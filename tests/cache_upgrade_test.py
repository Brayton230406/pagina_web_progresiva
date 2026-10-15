"""Comprueba una actualización real con estilos antiguos en la caché HTTP."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import re, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT/'scripts/build_site.py')], check=True)
with tempfile.TemporaryDirectory(prefix='lectora-upgrade-') as folder:
    old = Path(folder)/'old'
    shutil.copytree(ROOT/'dist', old)
    style = old/'view/styles.css'
    style.write_text(style.read_text().replace('main{margin-left:234px;padding:0 48px;min-width:0}', 'main{margin-left:234px;padding:0 48px;max-width:1640px}'))
    worker = old/'sw.js'
    current_worker = (ROOT/'dist/sw.js').read_text()
    cache_name=re.search(r"const CACHE='([^']+)';",current_worker).group(1)
    worker.write_text(current_worker.replace(cache_name, 'lectora-upgrade-old',1))
    state = {'root':str(old)}
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=state['root'],**kwargs)
        def log_message(self,*args):pass
        def do_GET(self):
            # Dos versiones con fechas de archivo distintas pueden compartir URL.
            # El endpoint del worker entrega su contenido vigente al revalidarlo.
            if self.path.split('?')[0].endswith('/sw.js') and 'If-Modified-Since' in self.headers:
                del self.headers['If-Modified-Since']
            super().do_GET()
        def end_headers(self):
            self.send_header('Cache-Control','public, max-age=3600')
            super().end_headers()
    server=ThreadingHTTPServer(('127.0.0.1',0), Handler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={'width':2560,'height':1440})
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            expect(page.locator('#catalog .book-card')).to_have_count(8)
            page.wait_for_function('navigator.serviceWorker.controller !== null')
            assert page.locator('main').evaluate('(m)=>m.getBoundingClientRect().right')==1874
            page.locator('[data-id="don-quijote"] .cover-open').first.click()
            page.locator('#book-notes').fill('Conservar mi biblioteca al actualizar.')
            page.get_by_role('button',name='Guardar en mi biblioteca',exact=True).click()
            expect(page.locator('#book-dialog')).not_to_be_visible()
            state['root']=str(ROOT/'dist')
            page.evaluate("""async()=>{
              const r=await navigator.serviceWorker.getRegistration();await r.update();
              const worker=r.installing||r.waiting;
              if(worker&&worker.state!=='activated')await new Promise(resolve=>worker.addEventListener('statechange',()=>{if(worker.state==='activated')resolve();}));
            }""")
            page.reload();expect(page.locator('#catalog .book-card')).to_have_count(8)
            assert page.locator('main').evaluate('(m)=>m.getBoundingClientRect().right===document.documentElement.clientWidth'), 'La actualización siguió usando los estilos antiguos de la caché HTTP.'
            page.locator('[data-id="don-quijote"] .cover-open').first.click()
            expect(page.locator('#book-notes')).to_have_value('Conservar mi biblioteca al actualizar.')
            assert page.evaluate("async()=>!(await caches.keys()).includes('lectora-upgrade-old')")
            browser.close()
            print('OK: estilos renovados a pesar de la caché HTTP; biblioteca y notas conservadas.')
    finally:server.shutdown();server.server_close();thread.join()
