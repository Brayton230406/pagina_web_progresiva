import {accessFor} from '../model/resources.js';
// Pagina texto literal, sin interpretar HTML procedente del libro.
export function paginate(text,size=6500){const pages=[];let offset=0;while(offset<text.length){let end=Math.min(offset+size,text.length);if(end<text.length){const newline=text.indexOf('\n',end);if(newline!==-1&&newline<end+1000)end=newline+1;}pages.push(text.slice(offset,end));offset=end;}return pages.length?pages:[''];}
export class Reader {
 constructor(storage,onProgress,onClose){
  this.storage=storage;this.onProgress=onProgress;this.onClose=onClose;this.page=0;this.pages=[];this.font=19;this.busy=false;
  $('#reader-prev').on('click',()=>this.turn(-1));$('#reader-next').on('click',()=>this.turn(1));
  $('#reader-close').on('click',()=>document.querySelector('#reader-dialog').close());
  document.querySelector('#reader-dialog').addEventListener('close',()=>{this.onClose?.(this.book);});
  $('#font-smaller').on('click',()=>this.resize(-1));$('#font-larger').on('click',()=>this.resize(1));
  $('#reader-dark').on('change',e=>{$('#reader-dialog').toggleClass('night',e.target.checked);this.preferences();});
 }
 async open(book){
  const access=accessFor(book);if(!access.textUrl)return;
  this.book=book;this.pages=[];this.busy=true;
  $('#reader-title').text(book.title);$('#reader-text').text('');$('#reader-position').text('');$('#reader-prev,#reader-next').prop('disabled',true);$('#reader-status').text('Abriendo el libro completo…');
  document.querySelector('#book-dialog').close();document.querySelector('#reader-dialog').showModal();
  try{
   const response=await fetch(access.textUrl);if(!response.ok)throw new Error('No se pudo abrir el archivo del libro.');
   const text=await response.text();if(text.length<1000)throw new Error('El archivo del libro está incompleto.');
   this.pages=paginate(text);
   const previous=await this.storage.get('settings','reader:'+book.id);
   const preferences=await this.storage.get('settings','reader-preferences');
   this.font=Math.max(15,Math.min(27,preferences?.font||19));$('#reader-text').css('--reader-font',this.font+'px');$('#reader-dark').prop('checked',!!preferences?.night);$('#reader-dialog').toggleClass('night',!!preferences?.night);
   this.page=Math.min(this.pages.length-1,Math.max(0,previous?.page||0));
   this.render();await this.save();
  }catch(error){$('#reader-status').text(error.message||'No se pudo cargar el libro. Cierra la lectura y vuelve a intentarlo.');}finally{this.busy=false;}
 }
 render(){
  $('#reader-text').text(this.pages[this.page]);$('#reader-status').text('Texto íntegro · Project Gutenberg · Tu posición se guarda automáticamente');
  $('#reader-position').text(`Página ${this.page+1} de ${this.pages.length}`);$('#reader-prev').prop('disabled',this.page===0);$('#reader-next').prop('disabled',this.page===this.pages.length-1);
  document.querySelector('#reader-dialog').scrollTop=0;
 }
 async save(){await this.storage.put('settings',{id:'reader:'+this.book.id,page:this.page});const progress=this.pages.length===1?100:Math.round(this.page/(this.pages.length-1)*100);await this.onProgress(this.book,progress);}
 async turn(delta){if(this.busy||!this.pages.length)return;const next=this.page+delta;if(next<0||next>=this.pages.length)return;this.busy=true;this.page=next;this.render();try{await this.save();}catch{$('#reader-status').text('No se pudo guardar tu posición. Puedes continuar leyendo.');}finally{this.busy=false;}}
 resize(delta){this.font=Math.max(15,Math.min(27,this.font+delta));$('#reader-text').css('--reader-font',this.font+'px');this.preferences();}
 async preferences(){try{await this.storage.put('settings',{id:'reader-preferences',font:this.font,night:$('#reader-dark').prop('checked')});}catch{$('#reader-status').text('No se pudieron guardar tus preferencias.');}}
}
