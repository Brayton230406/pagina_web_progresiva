// Solo estas ediciones completas están incluidas y disponibles sin conexión.
export const EDITIONS = {
 'don-quijote': {textUrl:'./books/don-quijote.txt',epubUrl:'./books/don-quijote.epub',infoUrl:'https://www.gutenberg.org/ebooks/2000',edition:'Project Gutenberg · edición en español'},
 'lazarillo': {textUrl:'./books/lazarillo.txt',epubUrl:'./books/lazarillo.epub',infoUrl:'https://www.gutenberg.org/ebooks/320',edition:'Project Gutenberg · edición en español'}
};
export const COVER_IDS = ['el-principito','habitos','clean-code','cien-anos','diseno','breve','don-quijote','lazarillo'];
// Nunca permitir javascript:, data:, URLs con credenciales ni rutas aportadas por un respaldo.
export function safeLink(value){try{const url=new URL(String(value));if(!['https:','http:'].includes(url.protocol)||url.username||url.password)return '';url.protocol='https:';return url.href;}catch{return '';}}
export function coverFor(book){return COVER_IDS.includes(book.id)?`./assets/covers/${book.id}.svg`:safeLink(book.coverUrl);}
export function accessFor(book){const local=EDITIONS[book.id];if(local)return {...local,local:true};return {epubUrl:safeLink(book.epubUrl),pdfUrl:safeLink(book.pdfUrl),previewUrl:safeLink(book.previewUrl),infoUrl:safeLink(book.infoUrl)||`https://books.google.com/books?q=${encodeURIComponent(book.title+' '+book.author)}`,local:false};}
export function googleBook(volume){const info=volume.volumeInfo||{},access=volume.accessInfo||{};return {id:'google-'+volume.id,title:info.title,author:info.authors?.join(', '),category:info.categories?.[0]||'Otros',pages:info.pageCount,description:info.description,coverUrl:info.imageLinks?.thumbnail||info.imageLinks?.smallThumbnail,previewUrl:access.viewability&&access.viewability!=='NO_PAGES'?(access.webReaderLink||info.previewLink):'',infoUrl:info.infoLink||info.canonicalVolumeLink,epubUrl:access.epub?.isAvailable?access.epub.downloadLink:'',pdfUrl:access.pdf?.isAvailable?access.pdf.downloadLink:''};}
