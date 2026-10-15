# Lectora

[![Validar y publicar Lectora](https://github.com/Brayton230406/pagina_web_progresiva/actions/workflows/pages.yml/badge.svg)](https://github.com/Brayton230406/pagina_web_progresiva/actions/workflows/pages.yml)

Biblioteca personal en español, adaptable e instalable como PWA. Proyecto de semana 6: jQuery y transición a MVC, ampliado con IndexedDB y APIs de Google.

## Ejecutar

No necesita npm ni compilación. Desde esta carpeta:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Abrir http://127.0.0.1:8080. No abrir index.html con file://: los módulos, AJAX y service workers requieren un servidor. El modo offline requiere una primera visita completa en HTTPS o localhost. El navegador puede ofrecer instalación desde su menú; iOS usa Compartir > Añadir a pantalla de inicio.

## Funciones

- Catálogo de ocho libros, búsqueda instantánea, filtros por categoría y filtro de descargas.
- Biblioteca personal: guardar, quitar, estado de lectura, progreso y notas.
- Persistencia real en IndexedDB: stores `books`, `settings`, `cache`. Las operaciones se confirman al terminar la transacción.
- Exportar/restaurar biblioteca JSON; la importación valida todos los registros antes de escribirlos en una sola transacción. Fusiona por ID.
- Google Books API: búsqueda remota por título, autor o tema, con resultados guardados en IndexedDB para consultas posteriores sin red.
- Fuentes intercambiables: JSON, CSV, XML, SQLite con sql.js y Firestore de solo lectura.
- PWA: manifiesto, iconos PNG y maskable, service worker y caché de todos los recursos locales, incluidas dependencias y WebAssembly.
- Diseño adaptable, etiquetas accesibles, modal nativo con Escape y reducción de movimiento.

Dos clásicos completos (Don Quijote y Lazarillo de Tormes) se incluyen en EPUB y TXT para descarga directa y lectura local con paginación, ajuste de letra, modo nocturno y posición guardada automáticamente. Los archivos conservan los créditos y términos de Project Gutenberg. Las otras seis fichas ofrecen acceso al proveedor; no incluyen un archivo del libro completo. Las búsquedas de Google utilizan sus portadas reales y solo muestran descargas cuando existe un `downloadLink` en `accessInfo`; no confunden un token DRM con un EPUB/PDF.

La biblioteca se conserva en el navegador y origen utilizados. No hay cuentas ni sincronización de notas entre dispositivos. Exportar un respaldo permite trasladarla; borrar los datos del sitio elimina la copia local. Las portadas locales son ilustraciones vectoriales originales con motivos específicos para cada título.

## APIs de Google

### Google Books

En **Fuentes de datos > Conectar servicios de Google**, guardar una API key de un proyecto con Books API habilitada. Configurar restricciones de API y de referentes HTTP para el dominio de producción y localhost. La app puede intentar consultas públicas sin clave, pero el servicio puede rechazar solicitudes o agotar la cuota compartida. Durante la comprobación, la consulta sin clave respondió HTTP 429 por cuota agotada. No se presenta contenido local como si fueran resultados de Google.

Documentación: https://developers.google.com/books/docs/v1/reference/volumes/list

### Firestore

El adaptador usa la API REST de Google Firestore, únicamente GET, para una colección pública de catálogo. No contiene credenciales, proyecto inventado ni escrituras remotas. Para conectarlo, indicar `projectId`, API key pública web y nombre de colección. Requiere una base `(default)` compatible con la API de documentos de Firestore y permisos de lectura de esa colección. El lector muestra hasta 100 documentos. No usar datos privados en una colección pública. No introducir tokens, claves privadas ni archivos de cuenta de servicio.

Cada documento usa los campos `title` (string, obligatorio), `author`, `category`, `pages` (integer) y `description`. El ID se obtiene del documento. Esta conexión queda pendiente de un proyecto real y sus reglas; no se ha aprovisionado una base ni modificado permisos. Para configurar infraestructura se debe identificar primero la edición de Firestore.

Documentación: https://firebase.google.com/docs/firestore/use-rest-api

## Correspondencia con semana 6

| Tema | Aplicación concreta |
| --- | --- |
| 6.1 jQuery y modularidad | Biblioteca jQuery local; módulos ES separados |
| 6.2 DOM y eventos | Render en `view/ui.js`, `.text()`, `.append()`, `.attr()`, `.prop()`, `.val()`, clases, recorrido `.closest()` y eventos delegados en tarjetas |
| 6.3 Efectos y animaciones | Notificaciones con `.stop().text().fadeIn().delay().fadeOut()`; `$.fx.off` respeta reduced motion |
| 6.4 MVC | Modelo en `model/`, vista HTML/CSS y `view/ui.js`, coordinación en `controller/app.js` |
| 6.5 JSON | `$.ajax` lee `data/books.json` |
| 6.5 CSV | Lector tabular con soporte de comillas y saltos de línea |
| 6.5 XML | Lectura con DOMParser y detección de errores |
| 6.5 SQLite | sql.js/WebAssembly crea una base en memoria, utiliza parámetros y ejecuta SELECT; no escribe archivos de base |
| 6.5 Firestore | Adaptador REST de Google solo lectura, pendiente de configuración real |
| Comparación relacional/NoSQL | SQLite usa tablas y SELECT; Firestore usa documentos; IndexedDB almacena objetos locales |
| Ampliaciones solicitadas | IndexedDB, Google Books, manifiesto y service worker |

El PDF se emplea como material teórico; su cuestionario no se interpreta como una instrucción para responder un examen. Los ejemplos de React, Angular, MongoDB o Express explican comparaciones arquitectónicas; esta implementación usa MVC con jQuery, sin incorporar servidores innecesarios.

## Estructura

- `index.html`: vista principal y formularios.
- `view/`: estilos y renderizado seguro (los datos externos se insertan como texto).
- `controller/app.js`: control de acciones, instalación y coordinación.
- `model/storage.js`: IndexedDB y transacciones.
- `model/catalog.js`: normalización, fuentes estáticas, SQLite y APIs.
- `data/`: el mismo catálogo en tres formatos.
- `vendor/`: jQuery 3.7.1 (MIT), sql.js 1.13.0 (MIT) y WebAssembly. Los encabezados de distribución se conservan. sql.js: https://github.com/sql-js/sql.js ; jQuery: https://jquery.com/license/
- `model/resources.js`: ediciones incluidas, validación de enlaces y adaptación de acceso a Google Books.
- `controller/reader.js`: lector local y persistencia de posición/preferencias.
- `books/`: archivos completos EPUB/TXT de los dos clásicos.
- `sw.js`, `manifest.webmanifest`, `assets/`: PWA y portadas ilustradas.
- `.github/workflows/pages.yml`: publicación en GitHub Pages desde main.

## Verificación

Ejecutar `python3 tests/check_static.py`: comprueba paridad JSON/CSV/XML, rutas de caché, referencias, iconos, integridad ZIP de EPUB y presencia de inicio/final en los textos completos.

Para pruebas reales de navegador instalar Playwright y Chromium en un entorno Python temporal, iniciar el servidor y ejecutar:

```sh
python -m pip install playwright
python -m playwright install chromium
python tests/browser_test.py
```

La prueba usa un perfil aislado. Comprueba renderizado de portadas, filtros, guardar/recargar notas en IndexedDB, descargas EPUB/TXT, lectura con posición recordada, preferencias, consultas SQLite y fuentes CSV/XML, modo offline y tamaño móvil. La respuesta de Google se simula para verificar portadas/enlaces/persistencia sin depender de cuotas; esta prueba no certifica una conexión real a Google ni a Firestore.

Resultado comprobado el 15 de octubre de 2026: pruebas estáticas e integración Chromium aprobadas, incluidos descarga EPUB/TXT real, descarga EPUB sin conexión, exportación/restauración, rechazo de enlaces inseguros, integridad del texto paginado, SQLite WebAssembly offline y persistencia tras recargar. Se revisaron capturas de escritorio, móvil a 375 px y ficha de libro; sin errores JavaScript ni desbordamiento horizontal. La instalación desde el menú sigue siendo una comprobación manual.

Lista manual para Chrome, Edge u Opera:

1. Abrir localhost, comprobar ocho tarjetas y ausencia de errores de consola.
2. Guardar un libro, escribir notas, cambiar progreso, recargar y verificar persistencia y contadores.
3. Editar a Terminado y comprobar progreso 100%; exportar y restaurar el respaldo.
4. Cargar JSON, CSV, XML y SQLite: deben mostrar los mismos ocho libros (SQLite ordena por título).
5. Abrir DevTools > Application y comprobar manifest, service worker activo, Cache Storage e IndexedDB.
6. Tras la primera carga, activar Network > Offline y recargar: catálogo, biblioteca, notas y SQLite deben funcionar. Las búsquedas remotas requieren conexión o una consulta anterior en caché.
7. Configurar una API key propia, buscar en Google Books, guardar un resultado y repetir la búsqueda sin conexión.
8. Conectar un proyecto real y consultar la colección Firestore de lectura.
9. Revisar a 375 px, navegar con teclado, cerrar el diálogo con Escape y probar reduced motion.
10. Instalar la PWA desde el menú del navegador.

## GitHub Actions y publicación

La aplicación usa rutas relativas y admite GitHub Pages bajo `/pagina_web_progresiva/`. El repositorio de publicación es https://github.com/Brayton230406/pagina_web_progresiva.

Dirección de GitHub Pages: https://brayton230406.github.io/pagina_web_progresiva/

El workflow `.github/workflows/pages.yml` se ejecuta con cada push/PR a `main` y permite ejecución manual. Primero valida las fuentes, los EPUB y la caché; después ejecuta Chromium con la aplicación empaquetada bajo la misma subruta de Pages. Comprueba las pantallas de 320, 375, 768, 820, 1024, 1440, 1512, 1728, 1920, 2560 y 3024 px, incluida la biblioteca, las fuentes, la ficha y el lector. También verifica que el contenido principal llegue al borde derecho del área visible, sin una franja vacía en pantallas anchas. Solo publica cuando todas las pruebas pasan; las PR se validan sin desplegar. Las respuestas de Google se simulan en CI para que las cuotas externas no produzcan fallos ajenos al código.

`python3 scripts/build_site.py` crea `dist/` con una lista explícita de recursos públicos. El artefacto de Pages excluye las pruebas, el historial Git, la configuración de CI y los archivos locales. Para reproducir las comprobaciones:

```sh
python3 tests/check_static.py
python3 -m pip install -r tests/requirements.txt
python3 -m playwright install chromium
python3 tests/browser_test.py
```

La prueba de navegador inicia y detiene su propio servidor temporal. Para probar una instancia ya servida se puede definir `BASE_URL` con su URL completa. En Settings > Pages la fuente debe ser **GitHub Actions**. Al modificar los recursos de la PWA en producción hay que cambiar la versión de caché en `sw.js`.

## Procedencia de las ediciones completas

- Don Quijote: https://www.gutenberg.org/ebooks/2000 — texto español de Miguel de Cervantes, con créditos a los voluntarios del proyecto.
- Lazarillo de Tormes: https://www.gutenberg.org/ebooks/320 — obra anónima en español.

Se descargaron de los enlaces oficiales TXT UTF-8 y EPUB3 el 15 de octubre de 2026. Los archivos conservan la licencia y los créditos originales. Las fichas de Gutenberg identifican ambas ediciones como dominio público en EE. UU.; sus términos incluyen indicaciones para otros países. No se incluyen archivos completos de los títulos contemporáneos del catálogo.
