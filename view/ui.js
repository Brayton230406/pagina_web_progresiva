import {coverFor,accessFor} from '../model/resources.js';
const colors=['#ba855c','#46624f','#385867','#a56e5d','#a89876','#65778a'];
export function bookCover(book){
 const hash=[...book.id].reduce((a,c)=>a+c.charCodeAt(0),0);
 const cover=$('<div>').addClass('cover').css('--cover',colors[hash%colors.length]);
 cover.append($('<small>').text(book.author),$('<strong>').text(book.title),$('<span>').addClass('ornament').attr('aria-hidden','true').text('✦'));
 const imageUrl=coverFor(book);
 if(imageUrl){const image=$('<img>').addClass('cover-image').attr({src:imageUrl,alt:'Portada de '+book.title,loading:imageUrl.startsWith('./')?'eager':'lazy',referrerpolicy:'no-referrer'});image.on('error',()=>image.remove());cover.append(image);}
 return cover;
}
export const UI={
 toast(message){$('#toast').stop(true,true).text(message).fadeIn(150).delay(3000).fadeOut(200);},
 cards(target,books,saved,library=false){
  const root=$(target).empty();
  if(!books.length){root.append($('<div>').addClass('empty').append($('<span>').addClass('empty-icon').attr('aria-hidden','true').text('▥'),$('<p>').text(library?'Tu estantería empieza aquí. Explora el catálogo y guarda tu primer libro.':'No encontramos libros. Prueba con otro título o categoría.')));return;}
  books.forEach(book=>{
   const stored=saved.find(b=>b.id===book.id),access=accessFor(book);
   const card=$('<article>').addClass('book-card').attr('data-id',book.id);
   const wrap=$('<div>').addClass('cover-wrap');
   wrap.append($('<button>').addClass('cover-open').attr({'aria-label':'Abrir '+book.title,'data-action':'open'}).append(bookCover(book)),$('<button>').addClass('save-button').attr({'aria-label':stored?'Editar '+book.title:'Guardar '+book.title,'data-action':'open'}).text(stored?'✓':'+'));
   if(access.epubUrl||access.pdfUrl)wrap.append($('<span>').addClass('download-badge').text(access.local?'↓ Libro completo · offline':'↓ Descarga disponible'));
   card.append(wrap,$('<h3>').append($('<button>').addClass('title-button').attr('data-action','open').text(book.title)),$('<p>').text(book.author));
   if(library)card.append($('<p>').addClass('reading-state').text(({pending:'Por leer',reading:'Leyendo',done:'Terminado'})[book.state]+' · '+book.progress+'%'),$('<progress>').attr({max:100,value:book.progress,'aria-label':'Progreso de '+book.title}));
   card.append($('<div>').addClass('card-bottom').append($('<span>').addClass('tag').text(book.category),$('<button>').addClass('text-button').attr('data-action','open').text(access.local?'Leer y descargar ↗':library?'Abrir libro ↗':'Ver libro ↗')));
   root.append(card);
  });
 },
 stats(books){$('#saved-count,#stat-saved').text(books.length);$('#stat-reading').text(books.filter(b=>b.state==='reading').length);$('#stat-done').text(books.filter(b=>b.state==='done').length);}
};
