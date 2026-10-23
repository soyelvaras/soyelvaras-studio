# Los efectos

Una sola lista plana. Un efecto puede ir en cualquier parte de un reel. Nunca se los presentes al usuario en grupos.
Nómbralos siempre con su nombre en español (la columna "Efecto" de la lista de abajo).

Cada efecto es de uno de dos tipos (la columna "Tipo" de abajo, `status` en `index.json`):

- **ready (listo)**: empaquetado. `effects/<key>/` tiene la maquinaria terminada que mide el clip por sí misma, un
  bloque de ajustes para llenar (el bloque CLIP al inicio de `build.py`), un `effect.md` con el orden exacto de
  ejecución, y `slot.json` (qué necesita y cómo se comporta dentro de un reel). Creas un espacio, llenas el bloque
  CLIP, ejecutas los comandos listados, revisas, lo agregas al reel. No reescribes código.
- **recipe (receta)**: el armado terminado de un reel real. Su maquinaria se puede reutilizar, pero el bloque marcado
  CLIP-SPECIFIC al inicio (cuadros, palabras, posiciones, rutas) pertenece a esa demo y hay que reescribirlo para el
  clip del usuario.

Las carpetas de efectos no tienen imágenes de demo, recortes ni sonidos: un efecto solo corre sobre el clip propio
del usuario. Las únicas imágenes de demo de la skill son los clips cortos de muestra del selector de estilo
(`picker/previews/`, `captions/previews/`), que están ahí a propósito para que el usuario vea cada look antes de
elegirlo. Nunca se usan en un reel. Un `example/clip.md` en la carpeta de un efecto es un ejemplo trabajado en
palabras: los ajustes que usó un clip de demo, sin imágenes.

Casi todos los efectos necesitan el recorte limpio (`setup.py --matting`, una vez, unos 105 MB). Revelado y los cuatro
superpuestos no necesitan ninguno, y Comentario puede correr sin él (`fx_new.py --no-cutout` y `CHIN_Y` escrito a
mano). La columna Recorte de abajo dice qué necesita cada uno.

**Los superpuestos** (Caja de Prompt, Cifra Grande, Fila de Cápsulas, Puntos; `"layer": "overlay"` en su `slot.json`)
son solo gráficos transparentes: su render es un `.webm` que el reel pone ENCIMA de su propia imagen, así que la
imagen conserva su color, sus cortes y la cámara viva, el espacio puede cruzar cortes, y `frames_check.py` sigue
midiendo esos cuadros. Son rápidos (sin recorte) y funcionan en cualquier encuadre. Dos de ellos muestran logos reales
de apps (`engine/icons`, 46 apps; `get_icon.py "<app>"` baja otra con licencia libre): solo cuando la persona nombra
esa app.

**Vidrio Líquido** no es un efecto: es un look para las tarjetas. La tarjeta desenfoca EN VIVO lo que tiene detrás (las manos y el cuarto se siguen moviendo) y su borde dobla la imagen como el canto de un vidrio grueso (`engine/glass.py`). Es siempre la **versión 2** de los efectos que lo tienen: Checklist, Llamadas y Caja de Prompt (las tres que Cristobal aprobó; en Cifra Grande y Fila de Cápsulas no quedó a la altura). Un superpuesto en vidrio necesita su propia imagen debajo: su render pasa a ser un .mp4 normal (`slot.json` "layer": "glass", lo pone `vgfx.py` solo), así que la cámara viva se detiene en 1 mientras dura. Sobre una pared clara, el texto crema necesita más tinte (Llamadas usa .62 por defecto).

Todos los efectos usan por defecto los colores de Soy Elvaras (dorado #C9A15B como acento, crema #F2ECDF como texto
claro, tinta #141615 y bosque #13281F como oscuros) y sus textos en pantalla por defecto están en español.

## Antes de usar uno (cada vez)

1. **Chequeo de toma.** `PY "SK/scripts/footage_check.py" "<project>"` revisa los efectos elegidos contra lo que se
   midió en este clip. `SKIP` significa déjalo fuera y dile al usuario la línea que imprime, traducida. `CHECK`
   significa mira los cuadros tú mismo. Nunca fuerces un efecto sobre una toma que falla. Las líneas bajo un `OK` dicen
   qué tiene que estar listo antes: `setup.py --matting` (el recorte limpio, una vez, unos 105 MB), `setup.py --fx
   <key>` (paquetes de Python extra para ese efecto, una vez), o algo del usuario.
2. **Partes.** Cuando las elecciones traen `effectSections`, un efecto solo puede ir en las partes que permitió el
   usuario (hook = la frase de apertura, end = el llamado a la acción, middle = el resto). El chequeo de toma imprime
   la ventana de tiempo de cada parte. `fx_new.py`, `fx_add.py` y `build_reel.py` lo hacen cumplir: un espacio fuera de
   sus partes se rechaza o se deja fuera, con el motivo. Si el gancho calculado es demasiado largo (una lista dicha en
   una sola oración), corrige las partes en `plan.json` (`"parts"`, ver `references/styles.md`).
3. **Solo donde calza con las palabras.** Un efecto cae en una frase que lo pide (un número para Contador, una lista
   para Checklist, la palabra para comentar para Comentario). Sin frase que calce no hay efecto, aunque esté elegido.
   Uno o dos efectos en un reel corto es suficiente, salvo que el usuario pida más.

## Un efecto listo (A ready effect)

Un espacio de efecto es un pequeño proyecto propio: toma N cuadros del reel y devuelve los mismos N cuadros con el
efecto aplicado (1080x1920, 30 fps). El armado del reel pone ese render sobre el reel exactamente en esos cuadros.

```
1. PY "SK/scripts/fx_new.py" <key> --project "<project>" --from <seg> --to <seg> [--hi]
       Segundos del reel. Empieza unos 0,1 s antes de la primera palabra a la que reacciona el efecto, termina unos
       1,5 s después de que cae (o en un corte). Crea <project>/fx/<key>/ con los scripts del efecto, los cuadros del
       espacio, las palabras del reel recortadas al espacio, tipografías, sonidos y el recorte de la persona (cortado
       del recorte del reel cuando existe, si no, recorta solo los cuadros del espacio: unos 1,2 s por cuadro en Mac,
       0,4 en este computador; avísale al usuario antes).
       Imprime los comandos para este efecto con las rutas reales, y los guarda como RUN.txt en el espacio.
       Los tiempos de instantánea de ejemplo que se pasarían del final del espacio se reparten dentro del espacio.
       Una línea que empieza con CHECK layout.json significa que el recorte limpio del espacio y layout.json no
       coinciden en dónde está la cabeza por más de 60 px: mira work/layout/check.jpg y vuelve a correr layout.py
       antes de seguir (con lentes, revisa también la barbilla a mano).
2. Lee <slot>/effect.md. Llena el bloque CLIP al inicio de <slot>/build.py con la herramienta Edit. Sigue las líneas
   "in a reel" que imprimió fx_new.py (sin color propio, irse antes de que termine el espacio, etc.).
3. Ejecuta los comandos impresos en orden. Todos se ven así:
       PY "SK/scripts/fx_run.py" "<slot>" measure.py              uno de los scripts propios del efecto
       PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1         los interruptores son palabras simples NOMBRE=valor
       PY "SK/scripts/fx_run.py" "<slot>" hf lint
       PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.4,1.2,2.0     MIRA <slot>/work/snap/contact-sheet.jpg
       PY "SK/scripts/fx_run.py" "<slot>" build.py                guía apagada: siempre el último armado antes de un render
       PY "SK/scripts/fx_run.py" "<slot>" hf render               -> <slot>/renders/<carpeta del espacio>.mp4
   El render se niega a empezar con la guía roja puesta, y revisa la cantidad de cuadros al final.
4. PY "SK/scripts/fx_add.py" "<project>" "<slot>"
       Revisa el render, lo copia a <project>/assets/fx/, y escribe el espacio en plan.json: sus cuadros, qué pasa con
       los subtítulos del reel, un pequeño ajuste de brillo para que el espacio calce con sus vecinos, y los sonidos
       propios del efecto.
5. PY "SK/scripts/build_reel.py" "<project>", lint, render, y luego la autorrevisión en los momentos del espacio y en
   sus dos bordes: PY "SK/scripts/frames_check.py" "<project>" "renders/<file>.mp4" --at <los tiempos que imprimió
   fx_add.py>. Nada sobre la cara, nada en el área roja, borde del recorte limpio, texto legible, ningún salto al
   entrar o salir del espacio. Corrígelo (una pasada) o sácalo: fx_add.py "<project>" "<slot>" --remove, y dile al
   usuario por qué.
```

Un segundo espacio del mismo efecto: agrega `--name <carpeta>` a `fx_new.py`. `--hi` además corta el espacio desde el
clip original a su propio tamaño (así Zoom Digital queda nítido). Dos espacios nunca pueden compartir cuadros.

Un efecto que vive SOBRE un corte (Corte en Zoom): dale a `fx_new.py` un tramo QUE CRUCE un corte del reel, unos 0,5 s
a cada lado (el chequeo de toma imprime dónde están los cortes). El espacio entonces tiene ambas tomas y conoce el
cuadro del corte. Todos los demás efectos necesitan una sola toma continua: `fx_new.py` rechaza un tramo que cruza un
corte.

Una misma toma puede servir para varios efectos distintos en espacios separados que no se pisan, o para demos
distintas del mismo tramo en proyectos separados (por ejemplo, para grabar los videos de muestra del selector).

## Una receta (A recipe)

1. Copia `SK/effects/<key>/` (y `SK/engine/fonts` como `assets/fonts`, más los dos archivos de `SK/engine/template/`)
   a `<project>/fx/<key>/`. Corta los cuadros que cubre el efecto a `fx/<key>/assets/aroll.mp4` con ffmpeg
   (exactamente N cuadros, 1080x1920, 30 fps, desde `<project>/assets/aroll.mp4`), y sus palabras a `words.json`
   (tiempos contados desde el inicio del espacio).
2. Reescribe el bloque CLIP-SPECIFIC a partir de la toma del usuario. Donde un armado lee una herramienta por una ruta
   fija, usa `ffmpeg` / `ffprobe` del PATH y `PY` para Python. Las rutas que empiezan con `FXLAB/`, `WORKSPACE/` o
   `HOME/` son archivos propios de la demo: reemplaza cada una. Los scripts auxiliares que terminan en `.sh` son notas
   de terminal de la demo: ejecuta directo los mismos comandos de ffmpeg / HyperFrames (funcionan igual en Windows),
   no ejecutes el archivo `.sh`.
3. Arma, lint, instantánea y render del espacio con `PY "SK/scripts/hf.py" "<project>/fx/<key>" <comando>` (la
   carpeta va primero, corre dentro de ella): el espacio es un render de cuadro completo 1080x1920 con exactamente la
   misma cantidad de cuadros que recibió.
4. Agrégalo a `<project>/plan.json` a mano y vuelve a correr `build_reel.py`:
   `"slots": [{"key": "<key>", "src": "fx/<key>/renders/slot.mp4", "from": 3.2, "to": 6.4, "captions": "hide"}]`
5. Autorrevisa el espacio desde el render final, igual que un efecto listo.

## Subtítulos, sonido y partes alrededor de un espacio

- **Subtítulos.** Cada efecto listo dice qué hacen los subtítulos del reel mientras se reproduce (`reel_captions` en
  su `slot.json`): `hide` cuando el efecto lleva las palabras él mismo o está donde van los subtítulos, `keep` cuando
  no se cruza con ellos. `fx_add.py --captions keep|hide` lo cambia para un espacio. Cuando las palabras propias de un
  efecto cubren solo parte del espacio, oculta los subtítulos solo en esa ventana: `fx_add.py ... --hide-captions
  3.9-4.9`. Antes y Después, cuando se arma con sus palabras propias encendidas (un reel sin subtítulos), calcula su
  propia ventana y `fx_add.py` la aplica sin opción. `fx_add.py --caption-y N` mantiene los subtítulos del reel pero
  mueve la parte superior de su línea a la y N de la pantalla mientras dura el espacio. Un efecto que necesita el
  pecho para él imprime el valor en su armado. El mismo valor sirve para todos los estilos de subtítulos, y el cambio
  ocurre en un cambio de subtítulo, nunca en medio de uno.
  Revisa en las instantáneas del espacio que ninguna palabra dicha quede sin subtítulo.
- **Gana el estilo de subtítulos del usuario.** Ver "Reestilizar las palabras de un efecto" abajo. Ningún efecto trae
  su propio look de subtítulos a un reel que tiene un estilo.
- **Sonido.** La voz siempre sale del propio corte del reel, así que no hay costura de audio. Los sonidos propios del
  efecto se leen del espacio y se reproducen en el reel. `--no-sfx` los deja fuera.
- **Un estilo completo.** Un espacio puesto sobre un estilo completo toma el color del estilo pero no sus
  acercamientos ni su reencuadre. Mira los dos bordes del espacio. Si salta, deja fuera el efecto en ese reel.
- **Recortes.** "clean" (limpio) significa `rvm_cut.py` (unos 1,2 segundos por cuadro en Mac; `fx_new.py` recorta
  solo los cuadros del espacio). "quick" (rápido) significa que basta con `cutout.py`. El limpio necesita
  `setup.py --matting` una vez. Ropa oscura sobre una silla oscura se mezcla en el recorte: los efectos que muestran
  el borde de la persona sobre algo claro (Mundo App, Foco, Apagón, Contundente) se ven mal ahí.
- Todo lo que se muestra en pantalla es real (los números y reels propios del usuario) o un relleno genérico. Nunca
  una persona real, nunca una prueba inventada, ningún conteo de me gusta o vistas que no se haya entregado.

## Reestilizar las palabras de un efecto (Restyling an effect's own words)

La regla está al inicio de SKILL.md. Los efectos de la tabla de abajo pueden poner palabras en pantalla. En un reel
que tiene un estilo de subtítulos (o un estilo que el usuario mostró o describió) nunca mantienen su propio look de
subtítulos. Un efecto que dibuja palabras y todavía no tiene fila aquí sigue la misma regla: lee su `effect.md`,
decide de cuál de los dos tipos son sus palabras, y agrega lo que encuentres al espacio.

- **Palabras que solo repiten lo que se dice: apágalas.** Los subtítulos del reel llevan las palabras en el estilo del
  usuario. `fx_new.py` ya imprime los comandos de armado con `CAPTIONS=0` para esos efectos.
- **Palabras que son el efecto: reestilízalas** al estilo del usuario antes del primer armado. Tipografía, mayúsculas
  o minúsculas, grosor, colores, placa o sin placa. El espacio es la copia propia del usuario del efecto, así que edita
  su `build.py` libremente. Los textos en pantalla van en español.
- Todo lo demás en un efecto también se puede cambiar: volumen del sonido (`SFX_GAIN`, `SOUNDS`, `SFX=0`), fuerza del
  movimiento (`PUSH`, las escalas en `ZOOMS`), tiempos (los valores de cuadro y segundo del bloque CLIP), colores
  (`ACCENT`, `GRADE`).
- Al adaptar el movimiento de un efecto en la copia de su espacio, sigue `references/motion.md`: entradas con un
  pequeño exceso, salidas más rápidas, nada lineal, nada que entre todo en el mismo cuadro, y lo que se queda sigue
  derivando. Los espacios quedan fuera de la cámara viva del reel (ella vuelve a 1 en sus bordes), así que un efecto
  que deja la imagen quieta más de 1 s necesita su propio empuje lento.

| Efecto | Sus palabras | Interruptor que las apaga | Dónde se define el look en el `build.py` del espacio |
|---|---|---|---|
| Antes y Después | repiten lo dicho (los subtítulos del lado "después"). Las dos etiquetas son el efecto | `CAPTIONS=0` (por defecto en un reel; las etiquetas se quedan) | Etiquetas: `LABELS`, `LABEL_Y`. Subtítulos propios, solo para un reel sin subtítulos: `CAPS`, `CAP_Y`, `CAP_FS`, `ACCENT`, `PUNCH`; tipografía en las reglas `font-family:'Inter Tight'` al final de la plantilla de la página |
| Órbita | repiten lo dicho | `CAPTIONS=0` (por defecto en un reel), luego `fx_add.py --caption-y <valor impreso>` | Subtítulos propios, solo para un reel sin subtítulos: `CAPS`, `CAP_Y`, `CAP_LINE` (tamaños); tipografía en las reglas css `.cap` |
| La Pila | las palabras de subtítulo repiten lo dicho. El título y las tarjetas son el efecto | `CAPTIONS=0` para las palabras de subtítulo (por defecto en un reel), luego `fx_add.py --caption-y <valor impreso>` | Título y tarjetas: `TITLE`, `CARDS`, `ACCENT`, y las reglas `font-family:'Inter Tight'` en `PAGE`. Franja de subtítulos: `CAP_Y`, `CAP_H` |
| Mundo App | la línea de subtítulo repite lo dicho. La pantalla y las etiquetas son el efecto | `CAPTIONS=0` para la línea de subtítulo (por defecto en un reel), luego `fx_add.py --caption-y <valor impreso>` | Etiquetas: `LABELS`, `HILITE`. Pantalla: `ACCENT`, `INK`, y las reglas de fuente del css de la pantalla. Línea de subtítulo: la regla css `.cap`, `CAP_Y` |
| Checklist | el efecto (un título y filas) | ninguno | `TITLE` (dibujado en mayúsculas por `.upper()` en la línea superior), `ROWS` (`*palabra*` = palabra de acento), `ACCENT`, `GLASS`, tamaño de fila `FS`, ubicación `CARD_BOX`. Tipografía: `font:600 26px ... Montserrat` (línea superior) y las dos reglas `font:800 ... 'Inter Tight'` (filas, cápsula) |
| Comentario | el efecto (la palabra tipeada, el comentario, la respuesta, el botón) | ninguno | Las líneas de estilo al final del bloque CLIP: `WORD_FONT`, `TEXT_FONT` (familia css, grosor, archivo de fuente), `UPPER`, `ACCENT_COL`, `LIGHT_COL`, `DARK_COL`. Tamaño y lugar: `SCALE`, `DROP`, `X_CENTER` |
| Sticker Congelado | el efecto (notas a mano, un sello) | `CAPTIONS=0` = sin notas ni dibujos | `NOTES`, `STAMP`, `INK`, `ACCENT`, `PAGE`, `SIZE`, `PLACE`. Tipografía: `.note{font-family:'Caveat'}` y la regla del sello (`'Inter Tight'`, `text-transform:uppercase`) |
| Foco | el efecto (las palabras clave) | `CAPTIONS=0` = solo luces: entonces agrega el espacio con `--captions keep` y los subtítulos del reel llevan las palabras | `KEYWORDS` (cada fila tiene su texto y color: escribe el texto en las mayúsculas o minúsculas del estilo), `FONT` (el archivo con que se miden las palabras) junto con la regla css `.kw{font-family ...;font-weight ...}` |
| Pantalla Verde | repiten lo dicho. La persona se achica abajo, así que la línea normal de subtítulos del reel caería sobre la cara | `CAPTIONS=0` (por defecto en un reel), luego `fx_add.py --caption-y <valor impreso>`: los subtítulos del reel suben a la línea sobre la cabeza | Subtítulos propios, solo para un reel sin subtítulos: `CAPS`, `CAP_KEY`, `CAP_WORDS`, `CAP_PLATE`, `CAP_PX`, `CAP_GAP` (minúsculas, tipografía en la regla css `.cap`). Más espacio sobre la cabeza: `SIZE = 'small'` |
| Apagón | el efecto: una palabra de golpe detrás de la cabeza, una palabra que dice la persona | `CAPTIONS=0` = sin palabra (la atenuación, el destello, el golpe y el regreso se quedan, los subtítulos del reel dicen la palabra). Con la palabra encendida, oculta el subtítulo del reel de esa palabra (`--hide-captions a-b`) | el bloque `WORD STYLE` bajo el bloque CLIP en `build.py`: `WORD_FONT`, `WORD_FONT_FILE`, `WORD_WEIGHT`, `WORD_ITALIC`, `WORD_CASE`, `WORD_TRACK`, `WORD_COLOUR`, `WORD_GLOW`, `WORD_PLACE`, `WORD_SIZE` |
| Fichas Fuera | el efecto (fichas con nombres, recibos, total; en la versión 4, íconos con nombre y una palabra). Los subtítulos del reel siguen | no hace falta: nada tapa los subtítulos | el bloque `STYLE` al inicio de `build.py`: `name_*` y `small_*` (tipografía, grosor, mayúsculas, espaciado), `tile_bg`, `tile_text`, `label_color`, `strike`, `paper`, `paper_ink`, `radius`, `order`; versión 4: `icon_palette`, `word_font`, `word_color`. Otra tipografía puede necesitar `width_factor` |
| Revelado | el efecto (título de ventana, checklist, contador, etiqueta). También dibuja las palabras dichas en la tarjeta pequeña, porque los subtítulos del reel se ocultan mientras dura el espacio | `CAPTIONS=0` = sin palabras dichas en la tarjeta | el bloque `STYLE` al inicio de `build.py`: `ui_font`, `ui_weight`, `ui_case`, `label_font`, `label_case`, los colores (`page`, `window`, `panel`, `ink`, `accent`, `done`, `highlight`), y para las palabras dichas `cap_font`, `cap_weight`, `cap_case`, `cap_size`, `cap_color`, `cap_mark`: ponlos según el estilo de subtítulos del usuario. Límite: las palabras de la tarjeta toman tipografía, mayúsculas, tamaño y color, no una placa detrás ni una palabra que se ilumina al decirse. Avísale al usuario cuando su estilo tiene una de esas |
| Línea en Llamas | el efecto (nombres de pistas, códigos de tiempo). Los subtítulos del reel siguen | no hace falta. La línea de tiempo va en la franja del pecho: agrega el espacio con el valor `--caption-y` que imprime `build.py`, o `--captions hide` cuando dice que no hay espacio | el bloque `STYLE` al inicio de `build.py`: `FONT`, `WEIGHT`, `CASE`, `TEXT`, `LABEL_PX`, `NAME_PX`, `ACCENT`, `PANEL`, `PANEL_EDGE`, `PALETTE`. Pon `DIM = 0` cuando el estilo del usuario ya es oscuro o no quiere oscurecer el cuarto |
| Zoom Digital, versión 2 (Medio rostro) | el efecto (la pila de palabras del lado vacío). Los subtítulos del reel se ocultan solo mientras dura `HALF` | ninguno: `CAPTIONS=0` no las apaga (solo apaga `CAPS`) | `HALF_WORDS` (escribe el texto en las mayúsculas o minúsculas del estilo; `'lg'` es Bebas Neue, solo mayúsculas), `LINE`, `HALF_TOP`, y las reglas css `.hl.sm`, `.hl.lg`, `.hl.it` (tipografía, grosor) que build.py agrega a `CSS` cuando `VARIANT == 2`. Color de la palabra clave: `YEL` |
| Negativo | el efecto (solo las palabras que importan, en negativo). Los subtítulos del reel se ocultan mientras dura | ninguno | `WORDS` (escribe el texto en las mayúsculas o minúsculas del estilo), `COLORS` (los dos colores del negativo), y las reglas css `.ng` (tipografía `'Work Sans'` 900; otra tipografía necesita su archivo en `NG_FONT` para medir) |
| Muro de Palabras | el efecto (el muro de palabras) | ninguno | `PHRASES`, `FS`, `INK`, `ACCENT`, `GROUND`, `ACCENT_Y`. Tipografía: su propio `@font-face` (`'Inter Tight Wall'`) y la regla `.wd`. El muro se dibuja en mayúsculas |
| Caja de Prompt, Cifra Grande, Fila de Cápsulas, Puntos | el efecto (lo que se escribe, el número y su línea, las cápsulas). Caja de Prompt, Cifra Grande y Puntos ocultan los subtítulos del reel solo mientras están arriba; Fila de Cápsulas los deja correr | ninguno (`CAPTIONS=0` se acepta y no cambia nada) | el bloque `STYLE` al inicio de `build.py`, igual en los cuatro: `font`, `weight`, `tracking`, `big_font`, `big_weight`, `big_tracking`, `case`, `small_font`, `small_weight`, `serif_font`, `ink`, `accent`, `card`, `shadow` |
| Pantalla LED | el efecto (las palabras dichas, una por una en la pantalla). Los subtítulos del reel se ocultan mientras dura | ninguno | `CASE`, `ACCENT` (palabras en dorado) en el bloque CLIP; los colores `LIGHT` / `DORADO` bajo él; la tipografía es `800 "Inter Tight"` en el canvas (`mask()` en el js de `build.py`) |

Comentario es el que tiene un bloque de estilo listo. En los otros efectos hechos de palabras la tipografía está en
reglas css dentro de `build.py`: cambia la familia y el grosor ahí, mantén las variables de tamaño, y mira la
instantánea del espacio, porque los anchos de texto se ajustaron para la tipografía por defecto (baja `FS` o el valor
de tamaño cuando una palabra ya no cabe). Todas las tipografías que usan los estilos de subtítulos ya están en el
espacio: `<slot>/assets/fonts/`, con nombres `<Familia>-<grosor>-<normal o italic>.woff2`, declaradas en
`assets/fonts/fonts.css`.

Los datos tipográficos de los estilos de subtítulos, para igualarlos (colores de Soy Elvaras):

| Estilo de subtítulos | Palabras principales | Segunda voz (palabras marcadas, títulos) | Mayúsculas | Colores | Placa |
|---|---|---|---|---|---|
| Arcade | Pixelify Sans 600 / 700 | | como se dice | crema #F2ECDF | ninguna |
| Discreto | Figtree 500 / 600, pequeña | cápsula de título: Barlow Condensed 500 | como se dice | crema; texto de la cápsula tinta #141615 sobre crema | solo la cápsula de título |
| Bitácora | Newsreader 400 | | como se dice | crema | ninguna |
| Noticiero | Inter Tight 800 | Playfair Display itálica | como se dice | crema | ninguna |
| Minúscula Gigante | Arimo 700 | | minúsculas | crema | ninguna |
| Tocador | Instrument Serif 400 | la misma, itálica | como se dice | crema #F2ECDF, palabras marcadas dorado #C9A15B | ninguna |
| Chicle | Arimo | título: Elsie Swash Caps 900 | minúsculas | crema con brillo dorado; título crema con trazo café #5B3F2C | ninguna |
| Moodboard | Poppins 700 | Instrument Serif itálica | minúsculas | crema | ninguna |
| Hora Dorada | Newsreader 500 itálica | | como se dice | dorado #C9A15B | ninguna |
| Ficha Técnica | Archivo 900, ancha (stretch 125%) | etiquetas, misma fuente | mayúsculas | crema, etiquetas dorado | ninguna |
| Contundente | Inter Tight 800 / 900 | la misma, gigante | minúsculas | crema, palabras grandes dorado | ninguna |
| Relajada | Inter 500 | Instrument Serif itálica | minúsculas | crema, línea grande dorado | ninguna |
| Elegante | Montserrat 500, pequeña y ancha | DM Serif Display | mayúsculas sobre una palabra serif | crema | ninguna |
| Karaoke | Archivo 900, ancha (stretch 125%) | | mayúsculas | crema, la palabra dicha dorado | placa bosque esmerilada, redondeada (rgba(19,40,31,.62), radio 26) |
| Firma | Archivo 900, ancha, itálica | Marck Script | mayúsculas | crema, firma crema | ninguna |
| Palabra Clave | Inter Tight 800 / 900 | | minúsculas | crema, palabras marcadas dorado | ninguna |
| Contraste | Inter 300 | Inter Tight 900 | como se dice | crema | ninguna |
| Terminal | JetBrains Mono 500 | Instrument Serif itálica | como se dice | crema | ninguna |
| Contorno | Bebas Neue | la misma, dibujada hueca | mayúsculas | crema | ninguna |

Cuando un detalle importa y esta tabla no basta, lee la función propia del estilo en `SK/engine/captions.py` (solo
lectura). Un estilo propio del usuario va por encima de esta tabla. Cuando tiene uno (`ST/my-style.json`, armado desde
un ejemplo o una descripción, `references/replicate.md`), los subtítulos del reel son su especificación a medida, no
uno de estos: reestiliza las palabras de un efecto a los valores de esa especificación (`font`, `weight`, `case`,
`color`, `accent`, `plate`).

## La lista

<!-- LIST:START (generated from index.json, do not edit by hand; traducida a mano en Soy Elvaras Studio) -->
34 listos, 0 recetas.

| # | Efecto | Clave | Tipo | Qué hace | El usuario dice | Encuadre | Cámara | Pared | Recorte | Seguimiento | Paquetes extra |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Órbita | `orbit` | listo | Tus propios reels giran a tu alrededor, pasando por detrás y por delante. | "pon mis reels en órbita a mi alrededor" | abierto o medio | quieta o con deriva | no hace falta | limpio | ninguno (prep.py mide el anillo desde el recorte; el anillo sigue la cabeza) | ninguno |
| 5 | Rompe Cuadro | `frame-break` | listo | El video se achica en una tarjeta y tu cabeza y manos salen de ella. | "achica el video en una tarjeta y déjame salir" | abierto o medio | cualquiera | no hace falta | limpio | ninguno (prep.py mide cabeza, cuerpo y manos desde el recorte) | ninguno |
| 6 | Muro de Palabras | `type-wall` | listo | Palabras gigantes desfilan detrás de ti y cambian en la palabra que dices. | "pon palabras gigantes detrás de mí que cambien mientras hablo" | abierto o medio | quieta | pared libre sobre la cabeza | limpio | ninguno (prep.py mide la cabeza; el muro está fijo) | scipy |
| 8 | Zoom Digital | `digital-zoom` | listo | Un acercamiento lento a tu cara, un golpe seco en una palabra clave, un regreso rápido (versión 2 "Medio rostro": un zoom extremo deja media cara a un lado, el cuarto queda gris oscuro, una línea rodea a la persona y las palabras se apilan en el lado vacío). | "acércate a mi cara cuando digo X" | cualquiera | cualquiera | no hace falta | limpio | cara (track.py) | ninguno |
| 16 | Muro de Titulares | `headline-wall` | listo | La pared detrás de ti se llena de titulares y publicaciones, con la palabra clave destacada. | "llena la pared detrás de mí con titulares sobre X" | abierto o medio | cualquiera | pared libre al lado de la persona | limpio | seguimiento del cuarto (prep.py) | scipy |
| 17 | Corte en Zoom | `zoom-through-cut` | listo | La cámara te atraviesa y sale en la toma siguiente. | "haz ese corte con zoom" | cualquiera, dos tomas seguidas | cualquiera | no hace falta | limpio | ninguno (prep.py encuentra los puntos de entrada) | scipy |
| 18 | Clon | `clone` | listo | Aparecen más de ti a tu lado en las palabras, y luego se sincronizan para el remate. | "clóname cuando digo así, así" | abierto | quieta | espacio libre a ambos lados | limpio | fijación de la deriva del cuarto (bake.py) | scipy |
| 2 | Muro de Portadas | `couch-wall` | listo | Las portadas de tus reels forman una grilla en la pared detrás de ti (versión 2 "Grilla en movimiento": tus reels caen uno por uno, reproduciéndose, a una grilla detrás de tu cabeza y salen volando). | "pon mis reels como grilla en la pared detrás de mí" | abierto o medio | quieta o con deriva | pared libre sobre la cabeza | limpio | seguimiento del cuarto, pared y muebles encontrados por color (prep.py) | scipy |
| 3 | Mundo App | `ui-world` | listo | Una pantalla de app llena el cuadro y tú quedas delante. | "ponme delante de la pantalla de Claude" | abierto o medio | quieta o con deriva | no hace falta | limpio | ninguno (se compone para la posición más alta de la persona) | scipy |
| 7 | La Pila | `the-stack` | listo | Tarjetas de datos con barras que corren se apilan sobre ti, tú vas en una ventana abajo. | "haz la composición de tarjetas de datos en esta frase" | cualquiera | cualquiera | no hace falta | limpio | ninguno (measure.py encuentra la cabeza desde el recorte; la ventana la sigue) | ninguno |
| 9 | Etiqueta Pegada | `sticky-text` | listo | Una etiqueta pegada a tu gorro o pecho que se mueve, inclina y escala contigo. | "pégame una etiqueta que diga X en el gorro" | cualquiera | cualquiera | no hace falta | limpio | cabeza y pecho seguidos cuadro a cuadro desde el recorte (track.py) | scipy |
| 11 | Foco | `spotlight` | listo | El cuarto se oscurece y desenfoca, tú quedas iluminado, las palabras clave caen grandes, las luces vuelven. | "ponme un foco cuando digo X" | cualquiera | cualquiera | no hace falta | limpio | ninguno (prep.py mide la cabeza en cada cuadro; la luz la sigue) | scipy |
| 13 | Congela y Señala | `freeze-and-label` | listo | La imagen se congela mientras sigues hablando, y líneas con etiquetas te apuntan. | "congela la imagen en X y ponme etiquetas: A, B" | cualquiera | cualquiera | no hace falta | limpio | ninguno (la imagen está congelada: todo se mide una vez en el cuadro detenido) | scipy |
| 14 | Teléfono 3D | `phone-mockup` | listo | Un teléfono 3D llega a tu lado mostrando una pantalla, con toques en tus palabras. | "pon un teléfono a mi lado mostrando la app" | cualquiera | quieta o con deriva | no hace falta | limpio | ninguno (build.py encuentra el lado con más espacio desde el recorte) | scipy |
| 15 | Checklist | `checklist` | listo | Una tarjeta se arma en la pared y cada paso se marca cuando lo dices. | "pon un checklist en pantalla con estos tres pasos" | cualquiera | cualquiera | no hace falta | limpio | ninguno (prep.py mide el clip) | ninguno |
| 21 | Llamadas | `pointer-callout` | listo | Tarjetas unidas a ti con líneas que se estiran y se balancean cuando te mueves. | "pon tarjetas en estas tres cosas y únelas a mí" | cualquiera | cualquiera | no hace falta | limpio | cabeza, pecho, hombros y manos seguidos cuadro a cuadro desde el recorte (track.py) | scipy |
| 10 | Contador | `odometer` | listo | Los números suben dígito por dígito como un cuentakilómetros. | "sube los números como un cuentakilómetros cuando digo X" | cualquiera | cualquiera | no hace falta | limpio | ninguno | ninguno |
| 19 | Antes y Después | `before-and-after` | listo | Una línea barre tu clip crudo y revela la versión editada (versión 2 "Tarjetas": un video de presentación del reel terminado, el corte crudo chico atrás y el reel grande adelante). | "haz un barrido antes y después en esta frase" | cualquiera | cualquiera | no hace falta | limpio | ninguno (measure.py encuentra la cabeza; ambos lados son los mismos cuadros) | ninguno |
| 20 | Gráfico que Crece | `chart-grow` | listo | Un gráfico de línea se dibuja en la pared detrás de ti y se dispara en tu palabra. | "dibuja un gráfico de crecimiento detrás de mí que se dispare cuando digo escalar" | abierto o medio | quieta o con deriva | espacio libre a ambos lados | limpio | seguimiento de la pared con cámara con deriva o en mano (measure.py); fijo con cámara quieta | scipy |
| 4 | Sticker Congelado | `freeze-sticker` | listo | Tu cuadro congelado se vuelve un sticker recortado con notas a mano. | "conviérteme en un sticker en esta frase" | cualquiera | cualquiera | no hace falta | limpio | ninguno (se congela un cuadro; bake.py mide su contorno) | scipy |
| 12 | Comentario | `comment-bubble` | listo | La palabra para comentar se escribe sola, se publica, y llega tu respuesta con el link. | "muestra el comentario escribiéndose y mi respuesta cuando digo comenta X" | cualquiera | cualquiera | no hace falta | limpio | ninguno | ninguno |
| 26 | Pantalla Verde | `green-screen` | listo | Quedas recortado y achicado abajo del cuadro, y toda la pantalla detrás pasa a ser aquello de lo que hablas. | "ponme en pantalla verde sobre este video" | abierto o medio | cualquiera | no hace falta | limpio | ninguno (prep.py lee lo alto de la cabeza, la barbilla, el ancho de la cabeza y la fila de corte del cuerpo desde el recorte) | scipy |
| 25 | Fichas Fuera | `knockout-tiles` | listo | Fichas con nombres caen en la pared detrás de ti, una por palabra, y cada una se tacha y sale volando; luego pueden apilarse recibos con un total (versión 4 "Íconos": íconos de app en fila con su nombre, el ícono real de la app cuando está en `assets/icons`, una línea los tacha a todos, caen con gravedad y aterriza una palabra en serif cursiva). | "pon estos nombres en la pared detrás de mí y saca cada uno cuando lo digo" | abierto o medio | quieta o con deriva | pared libre al lado de la persona | limpio | ninguno (prep.py lee la cabeza, su movimiento y la pared libre desde el recorte) | ninguno |
| 23 | Línea en Llamas | `timeline-burn` | listo | Una línea de tiempo de edición se arma frente a ti, se recalienta, se prende fuego en tu palabra y se deshace en brasas. | "pon una línea de tiempo de edición y quémala cuando digo X" | abierto o medio | cualquiera | no hace falta | limpio | ninguno (build.py lee la caja de la cabeza desde el recorte; la línea de tiempo es una capa de pantalla) | scipy |
| 22 | Apagón | `blackout` | listo | El cuarto se atenúa en tu frase mientras tú quedas iluminado, la palabra de golpe cae detrás de tu cabeza y las luces vuelven en la frase siguiente. | "baja las luces cuando digo X y súbelas en la frase siguiente" | cualquiera | cualquiera | no hace falta | limpio | ninguno (prep.py mide la cabeza mientras el cuarto está oscuro; la palabra queda fija en pantalla) | scipy |
| 24 | Revelado | `pull-back-reveal` | listo | El video en vivo se achica a una tarjeta dentro de una ventana de app: se marca un checklist con la edición real, corre la línea de tomas y un contador sube al número que dices. | "aléjate y muestra este video editándose" | cualquiera | cualquiera | no hace falta | ninguno | ninguno (toda la imagen entra en la tarjeta; no se mide nada) | ninguno |
| 30 | Mazo de Storyboard | `storyboard-deck` | listo | Una fila de tarjetas de storyboard se reparte sobre el pecho como naipes: la tarjeta de guion y cuadros de tus reels con su número, su tiempo y lo que se dice; una ola la recorre de izquierda a derecha, una se levanta y la fila sale hacia la derecha. | "reparte un storyboard sobre mi pecho" | abierto o medio | cualquiera | no hace falta | ninguno | ninguno (la barbilla sale de layout.json) | fotos de tu propio material |
| 31 | Caja de Prompt | `prompt-box` | listo | Una caja de texto sube sobre el pecho con el logo real de la app que nombras, lo que le pides a la IA se escribe solo y un cursor llega en arco y aprieta enviar. Superpuesto. | "pon mi prompt en pantalla" | cualquiera | cualquiera | no hace falta | ninguno | ninguno (fija en pantalla, ubicada desde layout.json) | ninguno |
| 32 | Cifra Grande | `stat-stack` | listo | El número que dices cae enorme en dorado y sube hasta su valor, con una línea chica debajo que cambia con lo que sigue. Superpuesto. | "pon el número gigante" | cualquiera | cualquiera | no hace falta | ninguno | ninguno (fija en pantalla, ubicada desde layout.json) | ninguno |
| 33 | Fila de Cápsulas | `chip-row` | listo | Una cápsula por cada cosa que nombras, en fila bajo los subtítulos, con el logo real cuando es una app. Superpuesto. | "pon lo que nombro en cápsulas" | cualquiera | cualquiera | no hace falta | ninguno | ninguno (fija en pantalla, bajo la línea de subtítulos) | ninguno |
| 34 | Puntos | `dot-counter` | listo | Una fila de puntos cae cuando dices cuántas cosas vienen, y cada punto se llena al nombrar su paso. Superpuesto. | "muestra con puntos cuántos pasos son" | cualquiera | cualquiera | no hace falta | ninguno | ninguno (fija en pantalla, ubicada desde layout.json) | ninguno |
| 29 | Tarjeta de Título | `title-card` | listo | Una tarjeta de capítulo: la imagen corta a la pantalla bosque con un código de tiempo que corre y un título grande en serif que aterriza palabra por palabra; la persona vuelve en un marco de teléfono con barra de reproducción y crece hasta la imagen completa. | "pon una tarjeta de título en esta parte" | cualquiera | cualquiera | no hace falta | ninguno | ninguno | ninguno |
| 28 | Negativo | `negative-words` | listo | Solo las palabras que importan, enormes y en negativo (verde bosque sobre lo claro, dorado sobre lo oscuro), la grande detrás de la cabeza cuando cabe, con zooms que siguen la cara. Los subtítulos del reel se ocultan mientras dura. | "pon esa cifra en negativo detrás de mi cabeza" | abierto o medio, con espacio sobre la cabeza | quieta o con deriva | no hace falta | limpio | cara (track.py, como Zoom Digital) | ninguno |
| 27 | Flicker | `flicker` | listo | El corte entre dos tomas se vuelve una ráfaga de destellos que aterriza en la toma siguiente (versión 1, la principal: primero parpadea la persona de la toma siguiente, después el fondo; versión 2: parpadea todo el cuadro). | "haz un flicker en ese corte" | cualquiera, dos tomas seguidas | cualquiera | no hace falta | limpio (solo la versión 1) | ninguno (no se mide nada: capas que aparecen y desaparecen por cuadro) | ninguno |
| 35 | Pantalla LED | `led-screen` | listo | La imagen corta a una pantalla LED oscura: tus palabras se encienden una por una en sus puntos rojos, verdes y azules, la cámara avanza y en la última palabra entra hasta ver los subpíxeles, y vuelve a ti desde un encuadre más cerrado. | "pon mis palabras en una pantalla LED" | cualquiera | cualquiera | no hace falta | ninguno | ninguno | ninguno |

## Por efecto: qué tiene que entregar el usuario, y qué vigilar

- **Órbita** (LISTO, `effects/orbit/`: build.py, effect.md, onsets.py, prep.py, slot.json). Necesita del usuario: una carpeta con las portadas de sus propios reels (al menos 4, 6 llenan el anillo por defecto). Conteos de vistas reales solo si el usuario los da. Persona centrada, plano abierto o medio, barbilla sobre y 1000 aprox. para que quepa una tarjeta bajo la cara. Falla en una selfie cercana, con una persona que llena el ancho del cuadro o está muy descentrada, con una mano sobre la cabeza, con un recorte débil y con una cámara que camina. Sin las portadas propias del usuario el efecto queda fuera.
- **Rompe Cuadro** (LISTO, `effects/frame-break/`: build.py, check.py, effect.md, onsets.py, prep.py, slot.json). No necesita nada del usuario. Una toma continua de 3 a 6 s, cabeza en la mitad superior con espacio sobre ella. Mejor con un gesto de la mano que se estira hacia el lado a la altura del pecho o más arriba; sin él igual funciona como la cabeza que sale. Débil en un plano muy cercano y cuando la cabeza toca el borde superior. Necesita un recorte que conserve pelo y dedos. Una capucha o pelo largo sobre los hombros necesita HEAD escrito a mano.
- **Muro de Palabras** (LISTO, `effects/type-wall/`: assets_fx, build.py, effect.md, example, onsets.py, prep.py, slot.json). No necesita nada del usuario. Solo cámara fija. Necesita espacio libre sobre la cabeza (lo alto de la cabeza en y 250 o más abajo). Reemplaza todo lo que hay detrás de la persona: el mueble donde se sienta hay que dibujarlo en KEEP. Mejor en una frase corta con una palabra que importa; una palabra de más de unas 7 letras no cabe.
- **Zoom Digital** (LISTO, `effects/digital-zoom/`: bake.py, build.py, clipblock.py, effect.md, example, onsets.py, post.py, slot.json, track.py). No necesita nada del usuario. Una toma continua con la cara visible todo el tiempo. Con --hi una fuente de 1728 px queda nítida hasta 1,6x; desde una fuente de 1080 todo zoom es una ampliación (limitada a 1,5x). Con lentes, el seguimiento puede quedar sobre un lente: usa AIM entre los ojos. Versión 2 "Medio rostro": un golpe de entrada y un regreso, `HALF` marca el tramo del look y `HALF_WORDS` lleva todas las palabras dichas en él (los subtítulos del reel se ocultan solo ahí); llega a 1,95x aunque la fuente sea de 1080, porque el cuarto oscuro esconde la ampliación.
- **Muro de Titulares** (LISTO, `effects/headline-wall/`: build.py, cards.py, effect.md, example, onsets.py, prep.py, slot.json). Necesita del usuario: el tema. El texto de las tarjetas se escribe para el reel: medios genéricos y nombres de relleno, nunca una publicación, persona o número real, ni una prueba inventada. Una toma continua de 3 a 6 s, con pared visible al lado o sobre la cabeza. Una cámara que se mueve se sigue. Una ventana, espejo o puerta abierta detrás de la persona rompe el seguimiento. Una selfie cercana no tiene espacio para las tarjetas grandes.
- **Corte en Zoom** (LISTO, `effects/zoom-through-cut/`: bake.py, build.py, effect.md, example, prep.py, slot.json, two_shot.py). En el selector aparece en la pestaña y el carril Transiciones (`"category": "transition"` en `picker/data/effects.json`); en las elecciones sigue siendo un efecto más. No necesita nada del usuario. Necesita dos tomas distintas seguidas (un corte real en la edición, no una toma continua), la persona en ambas, y algo oscuro y liso en la persona donde entrar. Un corte en medio de una palabra pelea con el movimiento.
- **Clon** (LISTO, `effects/clone/`: bake.py, build.py, check.py, effect.md, example, prep.py, slot.json). No necesita nada del usuario. Necesita espacio a ambos lados y el borde de un mueble (respaldo del sillón, escritorio, mesón) con pared encima para que los clones queden detrás. Sin planos cercanos, sin cámara en movimiento.
- **Muro de Portadas** (LISTO, `effects/couch-wall/`: build.py, effect.md, grid.py, onsets.py, prep.py, slot.json). Versión 2 "Grilla en movimiento": clips de sus propios reels (o portadas) en `covers/`, sin `prep.py` ni máscara de pared, solo el recorte adelante. Necesita del usuario: una carpeta con las portadas de sus propios reels (al menos 4, 9 o más se ve mejor). Conteos de vistas reales solo si el usuario los da. Necesita una pared lisa de un color en la parte superior del cuadro. Falla en una selfie cercana, una pared con diseño (papel mural, ladrillo, repisas, una ventana) y muebles o piso del mismo color que la pared (dibújalos en IN_FRONT). Sin las portadas propias del usuario el efecto queda fuera.
- **Mundo App** (LISTO, `effects/ui-world/`: build.py, effect.md, example, onsets.py, prep.py, slot.json). Necesita del usuario: lo que muestra la pantalla: sus palabras para la pantalla de chat incluida, o su propia imagen o grabación de pantalla. Todo nombre en ella es un relleno genérico. Persona quieta o casi, mirando a cámara, cabeza y hombros en cuadro, una toma continua. No se sigue nada: una persona que se mueve mucho arriba y abajo, camina o levanta las manos sobre la cabeza lo rompe. Necesita un recorte limpio con ambos hombros completos. Una selfie cercana no deja espacio (cabeza de más de unos 360 px de alto).
- **La Pila** (LISTO, `effects/the-stack/`: build.py, effect.md, measure.py, onsets.py, slot.json). Necesita del usuario: sus propias cifras: títulos, etiquetas, valores y unidades para una a tres tarjetas pequeñas. Una persona, cabeza y hombros en cuadro, una toma continua de 3 a 6 s. Una selfie muy cercana cabe unas 5 filas en total (build.py se detiene y dice cuánto sacar). Un plano abierto lejano se agranda y queda blando. Manos sobre la cabeza, una capucha o dos personas dan una caja de cabeza equivocada: escribe HEAD. Sin las cifras propias del usuario el efecto queda fuera.
- **Etiqueta Pegada** (LISTO, `effects/sticky-text/`: build.py, check.py, effect.md, slot.json, track.py). No necesita nada del usuario. Funciona con cámara en mano. 'cap' y 'chest' piden un plano medio o cercano, 'head' (al lado de la cabeza) pide espacio al lado. Se rompe con una mano sobre o encima de la cabeza, una capucha o pelo largo que tapa el cuello, una segunda persona, un giro de cabeza de más de unos 40 grados. Cuando el gorro está dentro de los 220 px superiores, 'cap' y 'head' se rechazan: usa 'chest'.
- **Foco** (LISTO, `effects/spotlight/`: build.py, check.py, effect.md, onsets.py, prep.py, slot.json). No necesita nada del usuario. Una toma continua de una persona, 3 a 6 s. Mejor en plano abierto o medio con pared sobre y al lado de la cabeza; en un plano cercano la luz se cierra a un resplandor. Necesita un recorte limpio: el pelo o los dedos perdidos se oscurecen con el cuarto. Se rompe con una mano sobre la cabeza, dos personas, una capucha o pelo largo sobre los hombros, y una cabeza que llena el cuadro (sin espacio para las palabras).
- **Congela y Señala** (LISTO, `effects/freeze-and-label/`: bake_freeze.py, build.py, check.py, effect.md, slot.json). Necesita del usuario: las etiquetas. Mejor en plano abierto o medio con espacio al lado o sobre la persona. La pausa necesita cerca de 1 s por etiqueta. Una selfie cercana cabe 1 o 2 etiquetas cortas (build.py se detiene y dice cuántas caben). Se rompe con un parpadeo o desenfoque de movimiento en la palabra congelada, una capucha o pelo largo sobre el cuello, una mano en la cabeza, una segunda persona. Los puntos de las manos se encuentran por color de piel y pueden fallar con una mano delante del pecho.
- **Teléfono 3D** (LISTO, `effects/phone-mockup/`: build.py, check.py, effect.md, measure.py, prep.py, slot.json). Necesita del usuario: su propia grabación de pantalla o imagen para el teléfono, o las palabras para la tarjeta incluida. Mejor en plano medio o abierto; un plano cercano funciona con 300 px o más de fondo al lado de la cabeza, y un plano cercano que llena el cuadro se detiene con 'no room for a phone'. Necesita un espacio de 2 s o más, la palabra del toque fuera de los primeros 0,6 s y los últimos 0,5 s, y ninguna mano detenida sobre el punto del toque. No para una persona que camina cruzando el cuadro.
- **Checklist** (LISTO, `effects/checklist/`: build.py, check.py, effect.md, example, onsets.py, prep.py, slot.json). Necesita del usuario: 2 a 4 pasos, con sus propias palabras. Necesita espacio libre sobre o al lado de la persona. Un plano cercano da una tarjeta pequeña. Con cámara en movimiento cambia sola a una tarjeta opaca.
- **Llamadas** (LISTO, `effects/pointer-callout/`: build.py, check.py, effect.md, slot.json, track.py). Necesita del usuario: los textos de las tarjetas. Mejor en plano abierto o medio con fondo libre al lado o sobre la persona, y una persona que se mueve o apunta. Una selfie cercana cabe 1 o 2 tarjetas cortas (build.py se detiene y dice cuántas caben). Se rompe con una capucha o pelo largo que tapa el cuello, una mano en la cabeza, una segunda persona. Los anclajes en las manos fallan con guantes, brazos descubiertos o ropa color piel: une esas tarjetas a la cabeza, el pecho o el hombro.
- **Contador** (LISTO, `effects/odometer/`: build.py, check.py, effect.md, example, measure.py, slot.json). Necesita del usuario: el número real, entregado por él. El panel va detrás de la persona, en fondo libre al lado o sobre la cabeza. Se detiene con un mensaje claro cuando la persona llena el cuadro. Solo un número que la persona realmente dice.
- **Antes y Después** (LISTO, `effects/before-and-after/`: build.py, check.py, effect.md, measure.py, prep_after.py, slot.json). Necesita del usuario: nada. Opcional: su propia versión terminada de los mismos cuadros. Cualquier toma, cualquier cámara. Necesita una frase que hable de un cambio. Débil cuando la palabra de remate cae en los primeros 0,3 s o cuando quedan menos de 1,5 s de espacio después del barrido. En una toma que ya es oscura el color por defecto puede quedar muy suave: sube AFTER_GRADE. El archivo "después" del usuario tiene que ser la misma toma sin acercamiento, reencuadre ni cambio de velocidad. Versión 2 "Tarjetas": NO es un espacio del reel, es su propio video y se arma después del render final, sobre todo el reel (`fx_new.py ... --from 0 --to <largo> --no-cutout --no-transcribe --variant 2`, puede cruzar cortes). Se entrega aparte como `<proyecto>-antes-despues.mp4`; `fx_add.py` se niega a ponerlo en el reel.
- **Gráfico que Crece** (LISTO, `effects/chart-grow/`: build.py, check.py, effect.md, measure.py, slot.json). Necesita del usuario: nada. Opcional: sus propias cifras y etiquetas reales para el gráfico. Necesita pared libre al lado o sobre la cabeza, mejor arriba a la derecha donde termina la línea. Una selfie cercana se detiene con NO OPEN WALL. Se rompe con una cámara que camina o hace paneo, una pared sin textura con cámara en mano, manos que cruzan la esquina superior derecha durante el golpe, y una palabra de golpe en el primer segundo del espacio.
- **Sticker Congelado** (LISTO, `effects/freeze-sticker/`: bake.py, build.py, check.py, effect.md, onsets.py, slot.json). Necesita del usuario: las notas. Mejor en plano medio o abierto (cabeza y pecho con aire alrededor); un plano cercano da un sticker grande con espacio para una o dos notas cortas. Se rompe con un cuadro congelado con desenfoque de movimiento, ojos cerrados o una mano cruzando la cara, un recorte que perdió pelo o dedos en ese cuadro, una persona cortada por ambos lados del cuadro, y una cabeza cortada por el borde superior.
- **Comentario** (LISTO, `effects/comment-bubble/`: build.py, check.py, effect.md, example, measure.py, slot.json). Necesita del usuario: la palabra para comentar (la marca cta en words.json). Quien comenta es un relleno genérico, nunca una persona real. El recorte solo se usa para medir la barbilla y el recorte del avatar (fx_new.py --no-cutout y CHIN_Y a mano lo evita). Necesita lo alto de la cabeza en cuadro y cerca de 1,5 s de la misma toma después de la frase. Si el recorte mezcla a la persona con la silla, escribe a mano CHIN_Y, X_CENTER y AVATAR_BOX.
- **Pantalla Verde** (LISTO, `effects/green-screen/`: build.py, check.py, effect.md, prep.py, slot.json). Necesita del usuario: su propio video o imagen de aquello de lo que habla (al menos un archivo en bg/). Mejor en plano medio (cabeza, hombros y pecho). Un plano abierto funciona, pero la persona se agranda y queda blanda sobre 1,3x. Un plano cercano con menos de una altura de cabeza de cuerpo bajo la barbilla se detiene con 'too tight'. Necesita un recorte limpio (el fondo nuevo muestra cada falla del recorte), una persona, un espacio de 36 cuadros o más. Solo se probó con cámara quieta.
- **Fichas Fuera** (LISTO, `effects/knockout-tiles/`: build.py, check.py, effect.md, prep.py, slot.json). Necesita del usuario: los nombres que enumera la persona; para los recibos, los montos que dice. Plano abierto o medio con unos 400 x 150 px de pared libre al lado de la cabeza, dentro de la zona segura. Cámara quieta: las piezas no se siguen con el cuarto. Necesita el recorte limpio. El total necesita unos 150 px de pared sobre la cabeza. Un plano cercano se detiene con 'no clear wall'. Solo se probó con un plano abierto y cámara quieta. Versión 4 "Íconos": 2 a 5 nombres en una fila (sobre la cabeza o al lado), una línea que los tacha a todos (`STRIKE_AT`) y una palabra que la persona dice (`WORD`); los íconos son el ícono real de la app cuando está en `assets/icons` (18 apps, licencias libres) o la inicial, siempre con el nombre debajo.
- **Línea en Llamas** (LISTO, `effects/timeline-burn/`: build.py, check.py, effect.md, slot.json). No necesita nada del usuario. Plano abierto o medio con la barbilla sobre y 980 aprox. (y 1100 sin línea de subtítulos): la línea de tiempo va bajo la barbilla en el tercio inferior. Una selfie cercana se detiene con 'No room for the timeline'. Necesita 1 s o más de espacio antes de la palabra del fuego y 1 s después. Se lee mejor sobre una imagen oscura u oscurecida (DIM). Solo se probó en plano abierto con cámara quieta.
- **Apagón** (LISTO, `effects/blackout/`: build.py, check.py, effect.md, onsets.py, prep.py, slot.json). No necesita nada del usuario. Una persona, una frase de 1 a 3 s que termina en una palabra de golpe, y luego un corte o la frase siguiente. Mejor en plano abierto o medio con espacio sobre la cabeza; en un plano cercano la palabra queda justo sobre la cabeza. Necesita un recorte limpio: el fondo que conserva el recorte queda iluminado, el pelo o los dedos perdidos se oscurecen con el cuarto. Se rompe con una mano sobre la cabeza, dos personas, una cabeza que llega al borde de la zona segura (sin espacio para la palabra: muévela o apágala) y un cuarto que ya es oscuro.
- **Revelado** (LISTO, `effects/pull-back-reveal/`: build.py, check.py, effect.md, onsets.py, slot.json). Necesita del usuario: la lista de edición propia del reel (pasos realmente hechos, la duración de cada toma en cuadros) y, para el contador, un número que dice la persona. Cualquier toma, cualquier cámara, sin recorte. El checklist cubre hasta 170 px del borde izquierdo de la tarjeta: una cara en el cuarto izquierdo de la imagen a media altura necesita FACE o pasos más cortos. La barra de título cubre los 68 px superiores del clip, la tira de línea de tiempo los 240 px inferiores. Necesita un espacio de unos 3,5 s o más. Solo se probó con un plano cercano en mano.
- **Flicker** (LISTO, `effects/flicker/`: build.py, effect.md, slot.json). Transición: en el selector va en la pestaña y el carril Transiciones; en las elecciones es un efecto más. No necesita nada del usuario. Necesita dos tomas distintas seguidas (un corte real) con la persona en ambas: la versión 1 (Por capas, la principal) pide 16 cuadros antes y 8 después, más el recorte limpio; la versión 2 (Completo) pide 12 a cada lado del corte. Destellos blancos: úsalo como acento, no en cada corte.
- **Negativo** (LISTO, `effects/negative-words/`: bake.py, build.py, clipblock.py, effect.md, onsets.py, post.py, slot.json, track.py). No necesita nada del usuario. Una toma continua con espacio sobre la cabeza. `WORDS` lleva solo lo que carga la frase (una cifra, un nombre, el remate), nunca la frase entera: "tenemos un 15% de margen en todas nuestras ventas" queda `15%` + `margen`. Zooms suaves (1,1 a 1,3): uno fuerte sube la cabeza y las tarjetas bajan al pecho; en un plano cercano baja `EYE` (y más alto) para dejar aire sobre el pelo. Cada tarjeta puede ir detrás o adelante (tercer valor); mezclar las dos se lee mejor. Los subtítulos del reel se ocultan todo el espacio (slot.json).
- **Tarjeta de Título** (LISTO, `effects/title-card/`: build.py, effect.md, slot.json). No necesita nada del usuario ni recorte. El título son palabras que la persona dice (`TITLE`, una línea por entrada con su cuadro); el código de tiempo y la barra del teléfono son el tiempo y el largo reales del reel. Los subtítulos del reel se ocultan mientras dura la pantalla del título.
- **Mazo de Storyboard** (LISTO, `effects/storyboard-deck/`: build.py, effect.md, slot.json). Los cuadros son fotos de su propio material (`'aroll'` o la ruta de un reel suyo) y las citas salen del `words.json` de ese clip o se escriben a mano. Necesita espacio bajo la barbilla; va adelante sobre el cuerpo, nunca sobre la cara, y sale hacia un lado. Los subtítulos del reel se ocultan mientras está arriba.
- **Caja de Prompt** (LISTO, superpuesto, `effects/prompt-box/`: build.py, check.py, effect.md, slot.json; `vgfx.py` lo copia fx_new.py). Necesita del usuario: nada; `TEXT` son palabras que dice, `APP` solo si nombra la app (logo real). Cualquier encuadre y corte. Deja unos 0,5 s después de la última palabra para que el cursor alcance a enviar. Sin espacio bajo la barbilla ni sobre la cabeza se detiene con DECLINED.
- **Cifra Grande** (LISTO, superpuesto, `effects/stat-stack/`). Necesita del usuario: nada; solo un número que dice de verdad. Sube como contador cuando vale 10 o más (respeta separadores y %). Whisper puede partir "3.000": escribe `NUMBER` a mano.
- **Fila de Cápsulas** (LISTO, superpuesto, `effects/chip-row/`). Necesita del usuario: nada; las cápsulas son lo que enumera (2 a 4, de 1 a 3 palabras), con logo solo para una app que nombra. Los subtítulos del reel siguen arriba: revisa que no se toquen.
- **Puntos** (LISTO, superpuesto, `effects/dot-counter/`). Necesita del usuario: nada; un número dicho de 2 a 8. Con `FILL_AT` el espacio cubre la lista entera (puede cruzar cortes) y cada punto se llena en su paso.
- **Pantalla LED** (LISTO, `effects/led-screen/`: build.py, effect.md, slot.json). No necesita nada del usuario ni recorte. Las palabras son las que dice, cada una en su cuadro (`WORDS = None` las lee de `words.json`). Mejor con una frase corta y una última palabra corta: ahí entra el empujón fuerte. Los subtítulos del reel se ocultan mientras dura la pantalla.
<!-- LIST:END -->
