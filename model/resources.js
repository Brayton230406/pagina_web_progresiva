// Solo estas ediciones completas están incluidas y disponibles sin conexión.
export const EDITIONS = {
 "don-quijote": {textUrl:'./books/don-quijote.txt',epubUrl:'./books/don-quijote.epub',infoUrl:'https://www.gutenberg.org/ebooks/2000',edition:'Project Gutenberg · edición en español'},
 "lazarillo": {textUrl:'./books/lazarillo.txt',epubUrl:'./books/lazarillo.epub',infoUrl:'https://www.gutenberg.org/ebooks/320',edition:'Project Gutenberg · edición en español'},
 "marianela": {textUrl:'./books/marianela.txt',epubUrl:'./books/marianela.epub',infoUrl:'https://www.gutenberg.org/ebooks/17340',edition:'Project Gutenberg · edición en español'},
 "novelas-ejemplares": {textUrl:'./books/novelas-ejemplares.txt',epubUrl:'./books/novelas-ejemplares.epub',infoUrl:'https://www.gutenberg.org/ebooks/61202',edition:'Project Gutenberg · edición en español'},
 "sombrero-tres-picos": {textUrl:'./books/sombrero-tres-picos.txt',epubUrl:'./books/sombrero-tres-picos.epub',infoUrl:'https://www.gutenberg.org/ebooks/29506',edition:'Project Gutenberg · edición en español'},
 "trafalgar": {textUrl:'./books/trafalgar.txt',epubUrl:'./books/trafalgar.epub',infoUrl:'https://www.gutenberg.org/ebooks/16961',edition:'Project Gutenberg · edición en español'},
 "la-regenta": {textUrl:'./books/la-regenta.txt',epubUrl:'./books/la-regenta.epub',infoUrl:'https://www.gutenberg.org/ebooks/17073',edition:'Project Gutenberg · edición en español'},
 "pepita-jimenez": {textUrl:'./books/pepita-jimenez.txt',epubUrl:'./books/pepita-jimenez.epub',infoUrl:'https://www.gutenberg.org/ebooks/17223',edition:'Project Gutenberg · edición en español'}
};
export const COVER_IDS = ["don-quijote", "lazarillo", "marianela", "novelas-ejemplares", "sombrero-tres-picos", "trafalgar", "la-regenta", "pepita-jimenez", "el-principito", "habitos", "clean-code", "cien-anos", "diseno", "breve"];
// Nunca permitir javascript:, data:, URLs con credenciales ni rutas aportadas por un respaldo.
export function safeLink(value){try{const url=new URL(String(value));if(!['https:','http:'].includes(url.protocol)||url.username||url.password)return '';url.protocol='https:';return url.href;}catch{return '';}}
export function coverFor(book){return COVER_IDS.includes(book.id)?`./assets/covers/${book.id}.svg`:safeLink(book.coverUrl);}
export function accessFor(book){const local=EDITIONS[book.id];if(local)return {...local,local:true};return {epubUrl:safeLink(book.epubUrl),pdfUrl:safeLink(book.pdfUrl),previewUrl:safeLink(book.previewUrl),infoUrl:safeLink(book.infoUrl)||`https://books.google.com/books?q=${encodeURIComponent(book.title+' '+book.author)}`,local:false};}
export function googleBook(volume){const info=volume.volumeInfo||{},access=volume.accessInfo||{};return {id:'google-'+volume.id,title:info.title,author:info.authors?.join(', '),category:info.categories?.[0]||'Otros',pages:info.pageCount,description:info.description,coverUrl:info.imageLinks?.thumbnail||info.imageLinks?.smallThumbnail,previewUrl:access.viewability&&access.viewability!=='NO_PAGES'?(access.webReaderLink||info.previewLink):'',infoUrl:info.infoLink||info.canonicalVolumeLink,epubUrl:access.epub?.isAvailable?access.epub.downloadLink:'',pdfUrl:access.pdf?.isAvailable?access.pdf.downloadLink:''};}
