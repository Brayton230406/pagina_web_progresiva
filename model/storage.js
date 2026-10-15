// Modelo de persistencia: las promesas resuelven cuando la transacción confirma.
export class Storage {
 async open(){this.db=await new Promise((resolve,reject)=>{const r=indexedDB.open('lectora',1);r.onupgradeneeded=()=>{for(const name of ['books','settings','cache'])r.result.createObjectStore(name,{keyPath:'id'});};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>reject(new Error('Cierra otras pestañas de Lectora y vuelve a intentar.'));});this.db.onversionchange=()=>this.db.close();}
 run(store,mode,action){return new Promise((resolve,reject)=>{const tx=this.db.transaction(store,mode);let req;try{req=action(tx.objectStore(store));}catch(e){reject(e);return;}tx.oncomplete=()=>resolve(req?.result);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error||new Error('No se pudo guardar.'));});}
 all(store='books'){return this.run(store,'readonly',s=>s.getAll());}
 get(store,id){return this.run(store,'readonly',s=>s.get(id));}
 put(store,value){return this.run(store,'readwrite',s=>s.put(value));}
 remove(id){return this.run('books','readwrite',s=>s.delete(id));}
 restore(books){return this.run('books','readwrite',s=>{books.forEach(b=>s.put(b));});}
}
