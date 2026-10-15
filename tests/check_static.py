"""Verificación reproducible de recursos y datos sin dependencias externas."""
from pathlib import Path
import csv,json,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
books=json.loads((root/'data/books.json').read_text())
with (root/'data/books.csv').open(newline='') as f: csv_books=list(csv.DictReader(f))
xml_books=[{n.tag:n.text for n in b} for b in ET.parse(root/'data/books.xml').getroot()]
for rows in (csv_books,xml_books):
 for row in rows: row['pages']=int(row['pages'])
 assert rows==books,'Las fuentes no son equivalentes'
assert len({b['id'] for b in books})==len(books)==8
sw=(root/'sw.js').read_text()
files=re.findall(r"'([^']+)'",re.search(r'const FILES=\[(.*?)\];',sw,re.S).group(1))
for file in files: assert (root/file).exists(),f'Recurso offline ausente: {file}'
html=(root/'index.html').read_text()
for url in re.findall(r'(?:src|href)="(\./[^"]*)"',html): assert (root/url).exists(),url
manifest=json.loads((root/'manifest.webmanifest').read_text())
assert manifest['start_url']=='./' and manifest['scope']=='./'
for icon in manifest['icons']:
 path=root/icon['src']; assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
assert 'maskable' in {i['purpose'] for i in manifest['icons']}
import zipfile
for name in ['don-quijote','lazarillo']:
 text=(root/f'books/{name}.txt').read_text(encoding='utf-8-sig')
 assert 'START OF THE PROJECT GUTENBERG EBOOK' in text
 assert 'END OF THE PROJECT GUTENBERG EBOOK' in text
 assert len(text)>100000
 with zipfile.ZipFile(root/f'books/{name}.epub') as epub:
  assert epub.read('mimetype')==b'application/epub+zip'
  assert epub.testzip() is None
print(f'OK: {len(books)} libros equivalentes, {len(files)} recursos offline y manifiesto/iconos válidos.')
