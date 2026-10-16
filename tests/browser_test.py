"""Pruebas de integración. Requiere playwright y Chromium de pruebas.
Inicia un servidor temporal bajo la subruta de GitHub Pages, o usa BASE_URL.
"""
from pathlib import Path
import json, os, tempfile, zipfile, functools, shutil, subprocess, sys, threading, hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]

def run(base_url):
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  context=browser.new_context(viewport={'width':1440,'height':1100},accept_downloads=True)
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base_url);expect(page.locator('#catalog .book-card')).to_have_count(14)
  page.wait_for_function("navigator.serviceWorker.controller !== null")
  expect(page.locator('#pwa-status')).to_contain_text('Lista')
  page.wait_for_function("[...document.querySelectorAll('#catalog .cover-image')].every(i=>i.complete&&i.naturalWidth>0)")
  page.screenshot(path='/tmp/lectora-desktop.png',full_page=True)
  page.locator('#download-only').check();expect(page.locator('#catalog .book-card')).to_have_count(8)
  page.locator('[data-id="don-quijote"] .cover-open').click()
  expect(page.locator('#access-status')).to_contain_text('Libro completo')
  page.locator('#book-notes').fill('Una historia para volver a leer.')
  page.get_by_role('button',name='Guardar en mi biblioteca',exact=True).click()
  expect(page.locator('#book-dialog')).not_to_be_visible();expect(page.locator('#stat-saved')).to_have_text('1')
  page.reload();expect(page.locator('#catalog .book-card')).to_have_count(14)
  page.locator('[data-id="don-quijote"] .cover-open').first.click()
  expect(page.locator('#book-notes')).to_have_value('Una historia para volver a leer.')
  for label,suffix in [('↓ Descargar EPUB','.epub'),('↓ Descargar TXT','.txt')]:
   with page.expect_download() as download_info:page.get_by_role('link',name=label,exact=True).click()
   download=download_info.value;assert download.failure() is None
   assert download.suggested_filename.endswith(suffix)
   assert Path(download.path()).stat().st_size>100000
   if suffix=='.epub':
    with zipfile.ZipFile(download.path()) as z:assert z.read('mimetype')==b'application/epub+zip'
  page.locator('#read-book').click();expect(page.locator('#reader-text')).not_to_be_empty()
  expect(page.locator('#reader-position')).to_contain_text('Página 1 de')
  page.locator('#reader-next').click();expect(page.locator('#reader-position')).to_contain_text('Página 2 de')
  page.locator('#reader-dark').check();page.locator('#font-larger').click();page.locator('#reader-close').click()
  expect(page.locator('#book-dialog')).to_be_visible();page.locator('#close-dialog').click()
  page.reload();expect(page.locator('#catalog .book-card')).to_have_count(14)
  page.locator('[data-id="don-quijote"] .cover-open').first.click();page.locator('#read-book').click()
  expect(page.locator('#reader-position')).to_contain_text('Página 2 de');expect(page.locator('#reader-dark')).to_be_checked()
  page.locator('#reader-close').click();page.locator('#close-dialog').click()
  page.locator('[data-tab="sources"]').click()
  for source in ['csv','xml','sqlite','json']:
   page.locator('#data-source').select_option(source);page.locator('#load-source').click()
   expect(page.locator('#source-status')).to_have_text(f'Fuente activa: {source} · 14 libros leídos',timeout=20000)
  # Respuestas controladas: prueban la integración sin depender de cuotas ni credenciales.
  page.route('https://www.googleapis.com/books/v1/volumes?*',lambda route:route.fulfill(json={'items':[{'id':'test-volume','volumeInfo':{'title':'Libro de prueba','authors':['Autora de prueba'],'imageLinks':{'thumbnail':'http://books.google.com/cover.jpg'}},'accessInfo':{'viewability':'ALL_PAGES','epub':{'isAvailable':True,'downloadLink':'https://books.google.com/test.epub'},'pdf':{'isAvailable':False},'webReaderLink':'https://books.google.com/reader'}}]}))
  page.locator('[data-tab="explore"]').click();page.locator('#search-source').select_option('google');page.locator('#search').fill('prueba');page.locator('#search-form').get_by_role('button').click()
  expect(page.locator('#catalog .book-card')).to_have_count(1);page.locator('.cover-open').first.click()
  expect(page.get_by_role('link',name='↓ Descargar EPUB',exact=True)).to_have_attribute('href','https://books.google.com/test.epub')
  expect(page.get_by_role('link',name='↓ Descargar PDF',exact=True)).to_have_count(0)
  page.get_by_role('button',name='Guardar en mi biblioteca',exact=True).click();expect(page.locator('#book-dialog')).not_to_be_visible();page.reload()
  expect(page.locator('#stat-saved')).to_have_text('2')
  page.locator('[data-tab="library"]').click();page.locator('[data-id="google-test-volume"] .cover-open').click()
  expect(page.get_by_role('link',name='↓ Descargar EPUB',exact=True)).to_have_attribute('href','https://books.google.com/test.epub');page.locator('#close-dialog').click()
  # Exportación real y restauración sin perder los enlaces de descarga.
  with page.expect_download() as backup_info:page.locator('#export').click()
  backup=backup_info.value;backup_data=json.loads(Path(backup.path()).read_text())
  assert len(backup_data['books'])==2
  page.locator('#import').set_input_files({'name':'respaldo.json','mimeType':'application/json','buffer':json.dumps(backup_data).encode()})
  expect(page.locator('#toast')).to_contain_text('Respaldo restaurado')
  assert page.evaluate(r"""async()=>{const {safeLink,googleBook}=await import('./model/resources.js');const {paginate}=await import('./controller/reader.js');const input='texto íntegro\n'.repeat(2000);return safeLink('javascript:alert(1)')===''&&safeLink('https://user:pass@example.org')===''&&!googleBook({id:'x',accessInfo:{epub:{isAvailable:true,acsTokenLink:'https://example.org/drm'}}}).epubUrl&&paginate(input).join('')===input;}""")
  page.unroute('https://www.googleapis.com/books/v1/volumes?*')
  # Los textos íntegros, las portadas, IndexedDB y SQLite funcionan sin Internet.
  context.set_offline(True);page.reload();expect(page.locator('#catalog .book-card')).to_have_count(14)
  editions=json.loads((ROOT/'books/editions.json').read_text())
  offline_files=[record['path'] for book in editions for record in book['files'].values()]+['assets/covers/'+book['id']+'.svg' for book in editions]
  assert page.evaluate("async paths=>{for(const path of paths){if(!await caches.match(new URL(path,location.href).href))return false;}return true;}",offline_files), 'Falta un libro o portada en Cache Storage.'
  page.wait_for_function("[...document.querySelectorAll('#catalog .cover-image')].every(i=>i.complete&&i.naturalWidth>0)")
  expect(page.locator('#stat-saved')).to_have_text('2')
  page.locator('[data-id="lazarillo"] .cover-open').first.click()
  with page.expect_download() as offline_download:page.get_by_role('link',name='↓ Descargar EPUB',exact=True).click()
  assert Path(offline_download.value.path()).stat().st_size>100000
  page.locator('#read-book').click();expect(page.locator('#reader-text')).not_to_be_empty()
  page.locator('#reader-close').click();page.locator('#close-dialog').click()
  # Abrir, descargar, anotar y reanudar todos los títulos nuevos sin conexión.
  editions=json.loads((ROOT/'books/editions.json').read_text())
  for edition in editions:
   if edition['id'] in ['don-quijote','lazarillo']:continue
   book_id=edition['id']
   page.locator(f'#catalog [data-id="{book_id}"] .cover-open').click()
   expect(page.locator('#access-status')).to_contain_text('Libro completo')
   for label,ext in [('↓ Descargar EPUB','epub'),('↓ Descargar TXT','txt')]:
    with page.expect_download() as result:page.get_by_role('link',name=label,exact=True).click()
    download=result.value;assert download.failure() is None
    assert hashlib.sha256(Path(download.path()).read_bytes()).hexdigest()==edition['files'][ext]['sha256']
   page.locator('#read-book').click();expect(page.locator('#reader-status')).to_contain_text('Texto íntegro')
   expect(page.locator('#reader-text')).not_to_be_empty()
   expect(page.locator('#reader-position')).to_contain_text('Página 1 de')
   page.locator('#reader-next').click();expect(page.locator('#reader-position')).to_contain_text('Página 2 de')
   page.locator('#reader-close').click();expect(page.locator('#book-dialog')).to_be_visible()
   page.locator('#book-notes').fill('Nota offline: '+edition['title'])
   page.get_by_role('button',name='Guardar en mi biblioteca',exact=True).click();expect(page.locator('#book-dialog')).not_to_be_visible()
   page.reload();expect(page.locator('#catalog .book-card')).to_have_count(14)
   page.locator(f'#catalog [data-id="{book_id}"] .cover-open').click()
   expect(page.locator('#book-notes')).to_have_value('Nota offline: '+edition['title'])
   page.locator('#read-book').click();expect(page.locator('#reader-position')).to_contain_text('Página 2 de')
   if book_id=='marianela':page.screenshot(path='/tmp/lectora-marianela-reader.png')
   page.locator('#reader-close').click();expect(page.locator('#book-dialog')).to_be_visible();page.locator('#close-dialog').click()
  print('OK: seis libros nuevos leídos y descargados completos offline; notas y posición conservadas.',flush=True)
  page.locator('[data-tab="sources"]').click();page.locator('#data-source').select_option('sqlite');page.locator('#load-source').click()
  expect(page.locator('#source-status')).to_have_text('Fuente activa: sqlite · 14 libros leídos')
  page.locator('[data-tab="explore"]').click();page.locator('#search-source').select_option('google');page.locator('#search').fill('prueba');page.locator('#search-form').get_by_role('button').click()
  expect(page.locator('#catalog .book-card')).to_have_count(1)
  context.set_offline(False);page.reload();expect(page.locator('#catalog .book-card')).to_have_count(14)
  # Móviles, tabletas, MacBook Pro y escritorios grandes.
  for width,height in [(320,740),(375,812),(768,1024),(820,1180),(1024,768),(1440,1100),(1512,982),(1728,1117),(1920,1080),(2560,1440),(3024,1964)]:
   page.set_viewport_size({'width':width,'height':height})
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Desbordamiento horizontal a {width}px'
   assert page.locator('main').evaluate('(main)=>Math.abs(main.getBoundingClientRect().right-document.documentElement.clientWidth)<=1'),f'Franja vacía a la derecha a {width}px'
   page.locator('[data-tab="sources"]').click()
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Fuentes desbordadas a {width}px'
   page.locator('[data-tab="library"]').click()
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Biblioteca desbordada a {width}px'
   page.locator('[data-tab="explore"]').click()
   if width in [1728,2560]:page.screenshot(path=f'/tmp/lectora-desktop-{width}.png',full_page=True)
   page.locator('[data-id="don-quijote"] .cover-open').first.click()
   box=page.locator('#book-dialog').bounding_box();assert box['x']>=0 and box['x']+box['width']<=width+1
   page.locator('#read-book').click();expect(page.locator('#reader-text')).not_to_be_empty()
   assert page.locator('#reader-dialog').evaluate('(d)=>d.scrollWidth<=d.clientWidth+1'),f'Lector desbordado a {width}px'
   page.locator('#reader-close').click();expect(page.locator('#book-dialog')).to_be_visible();page.keyboard.press('Escape');expect(page.locator('#book-dialog')).not_to_be_visible()
  page.set_viewport_size({'width':375,'height':812});page.screenshot(path='/tmp/lectora-mobile.png',full_page=True)
  page.locator('[data-id="don-quijote"] .cover-open').first.click();page.screenshot(path='/tmp/lectora-dialog.png')
  page.keyboard.press('Escape')
  assert not errors,errors
  print('OK: portadas, 14 libros y 8 ediciones completas offline, filtros, IndexedDB, EPUB/TXT, lector y posición, SQLite/CSV/XML, Google simulado, offline y móvil. Sin errores JS.')
  browser.close()
if __name__=='__main__':
 if os.environ.get('BASE_URL'):
  run(os.environ['BASE_URL'])
 else:
  # Reproduce la ruta de GitHub Pages, no solo la raíz de localhost.
  subprocess.run([sys.executable,str(ROOT/'scripts/build_site.py')],check=True)
  with tempfile.TemporaryDirectory(prefix='lectora-pages-') as folder:
   shutil.copytree(ROOT/'dist',Path(folder)/'pagina_web_progresiva')
   class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
   server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=folder))
   worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
   try:run(f'http://127.0.0.1:{server.server_port}/pagina_web_progresiva/')
   finally:server.shutdown();server.server_close();worker.join()
