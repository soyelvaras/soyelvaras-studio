# checklist (Checklist)

**Qué hace:** una tarjeta oscura de checklist se arma en pantalla; el texto de cada fila aparece cuando la persona
empieza la frase, su marca se dibuja y salta en la palabra que la termina, y luego la tarjeta se completa (cápsula
contador "3 de 3", barra llena, brillo, resplandor).
**Función:** explicar. Convierte "son solo N pasos / te pregunta N cosas" en algo que el espectador ve completarse.
**Frases que lo activan:** "pon un checklist en pantalla con estos pasos", "márcalos cuando los digo", "pon las tres
cosas en una tarjeta".

## Toma que necesita, y dónde falla
- Una lista dicha de 2 a 5 elementos cortos (1 a 4 palabras cada uno en pantalla), al menos ~8 cuadros entre marcas, y
  ~0,5 s después de la última para el momento de completarse.
- Lo mejor: un plano abierto o medio con pared libre sobre o al lado de la persona. La tarjeta va DETRÁS de la persona
  (entre el cuarto y el recorte) y la cabeza de la persona tapa su borde inferior.
- Selfie cercana: funciona, pero el espacio libre es una columna angosta al lado de la cara, así que la tarjeta sale a
  ~0,5 a 0,7 de escala (texto de fila de 30 a 43 px). build.py imprime la escala y avisa bajo 0,6. Filas más cortas
  dan una tarjeta más grande.
- Cámara en movimiento (en mano): el vidrio es una imagen fija desenfocada del cuarto, así que cambia sola a una
  tarjeta OPACA cuando prep.py mide más de 24 px de deriva del fondo. La tarjeta queda fija en pantalla, no sigue la
  pared.
- Falla: sin espacio libre (la persona llena el cuadro de borde a borde), listas de 6 o más, elementos dichos con
  menos de ~0,3 s entre ellos, una mano levantada junto a la cabeza durante todo el clip (se toma como lo alto de la
  cabeza).

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte: necesario para LAYER detrás y para la ubicación automática),
`words.json`, `clip.json`. Sin aroll_hi. Tipografías y sonidos de stock de la plantilla. Sin paquetes extra de Python
(prep.py usa numpy del Python de la skill; build.py, onsets.py, check.py son python3 simple).

## Bloque CLIP (inicio de build.py)
| Campo | Qué es | Cómo obtenerlo |
|---|---|---|
| `TITLE` | línea superior (se muestra en mayúsculas) | palabras que dice la persona; menos de ~22 caracteres |
| `ROWS` | `(texto, f_say, f_tick)` x 2 a 5; `*palabra*` = acento dorado; `a|b` = fila de dos líneas (también en `TITLE`), cambia a un relleno más justo para una columna angosta | `onsets.py`: `say` de la palabra que empieza la frase, `tick` de la palabra que la termina |
| `F_IN` | la tarjeta empieza a armarse | primer cuadro de voz, o ~20 cuadros antes del primer f_say |
| `F_DONE` | momento de completarse | una palabra acentuada 8+ cuadros después de la última marca, o `None` (= última marca + 10) |
| `F_OUT` | la tarjeta sale de golpe, o `None` = se queda | inicio de la oración siguiente; úsalo cuando el espacio sigue después de la lista |
| `CARD_BOX` | `'auto'` o `(x, y, w, h)` donde debe caber la tarjeta | auto lee work/prep.json; cámbialo después de mirar las instantáneas |
| `LAYER` | `'behind'` / `'front'` / `'auto'` | detrás siempre que haya espacio; adelante solo sobre el pecho o las piernas, nunca la cara |
| `OVERLAP` | px que la tarjeta se mete detrás de lo alto de la cabeza | 40; 0 para dejarla libre |
| `GLASS` | `'auto'` / `'glass'` / `'opaque'` | deja auto |
| `ACCENT` | color de la marca | dorado `#C9A15B` |
| `GRADE`, `VIGNETTE`, `PUSH` | look de la imagen en el espacio | `''`, `0`, `1.0` cuando el espacio va en un reel que tiene su propio color; valores de demo para un clip suelto |
| `KEEP_OUT` | rectángulos que usa el reel (cápsula de título, franja de subtítulos) | del plan del reel; la ubicación automática se mantiene fuera, una caja puesta a mano recibe un aviso |

**Versión muda / rápida (b-roll):** dale a cada fila un `f_say` temprano (todo el texto de entrada) y marcas cada ~9
cuadros; la barra de foco sigue entonces a las marcas. Los cuadros antes de `F_IN` y después de `F_OUT + 8` son la toma
sin tocar (capa de recorte apagada).
**Interruptores:** `SAFE=1` guía roja de zona segura (solo instantáneas), `SFX=0` sin sonidos, `GRADE=0` sin color ni
viñeta diga lo que diga el bloque CLIP, `CAPTIONS=0` se acepta y se ignora (el texto de la tarjeta es el subtítulo; el
efecto no dibuja subtítulos).

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # agrega -v para la tira de volumen; cuadros para ROWS, F_IN, F_DONE
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # deriva de cámara, caja de la cabeza, espacio libre -> work/prep.json
# editar: el bloque CLIP en build.py (herramienta Edit)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 GRADE=0      # lee lo que imprime: capa, vidrio/opaca, escala, líneas WARNING
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <8+ tiempos: armado, cada say+0,1 s, cada tick+0,1 s, done+0,15 s, final>
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0      # sin SAFE
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, copia para celular, work/final/sheet.jpg + ticks.jpg + edge.jpg
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un clip nuevo toma unos 15 minutos de punta a punta en Mac (el recorte en fx_new.py es la mayor parte: ~1,3 s por
cuadro).

## Qué mirar en los cuadros finales
- `ticks.jpg`: en tick-1 el círculo está vacío, en tick+1 el disco es dorado, en tick+3 la marca está dibujada.
  Reproduce la copia para celular con sonido: el pop tiene que caer en la palabra.
- `sheet.jpg`: el cuadro 0 no tiene tarjeta; el texto de cada fila se lee 8+ cuadros antes de su marca; el último
  cuadro muestra todas las filas brillantes y la cápsula dorada.
- `edge.jpg`: donde la persona se cruza con la tarjeta no hay borde claro ni borde doble; la cara nunca queda bajo la
  tarjeta.
- Zona segura: ningún WARNING de build.py, y la tarjeta fuera de la guía roja en cada instantánea (lo más grande es en
  el pop de completarse).

## Trampas (cada una costó un render)
- Los inicios de palabra de Whisper llegan 1 a 4 cuadros antes. Usa onsets.py, y revisa una palabra suave después de
  una fuerte en la tira `-v`.
- `pop.mp3` tiene 118 ms de aire antes del golpe: build.py empieza cada sonido antes (`SFX_LEAD`), así que los tiempos
  de SFX significan "cuándo se escucha".
- La cápsula contador cambia de color con un set duro en el cuadro. Un fundido esconde los dígitos un cuadro.
- Sin `backdrop-filter` ni `mask-image` en el motor de render: el vidrio es una imagen fija desenfocada horneada
  (`assets/glass.jpg`).
- Una toma "estática" en trípode igual puede derivar: la demo aprobada deriva 17 px en su primer segundo. Está dentro
  del límite del vidrio; confía en prep.py, no en la descripción de la toma.
- ffmpeg: `-c:v libvpx-vp9` antes de `-i` y `alphaextract` antes de `scale`, o se pierde el alfa del recorte.
- La tarjeta salta a 1,02 y el escenario puede acercarse: la ubicación se revisa en su momento más grande, no en
  reposo. No la pongas a mano a menos de 36 px de la línea segura superior.
- Una tarjeta adelante sobre un plano cercano casi siempre cruza la cara: build.py avisa, créele.
- `LAYER = 'auto'` toma una tarjeta grande ADELANTE sobre el cuerpo cuando eso es mucho más grande. Si las manos
  importan (la persona cuenta con los dedos) pon `LAYER = 'behind'`.
- Nunca agregues `overwrite:'auto'` a una animación: el motor de render busca, y el overwrite mata la animación
  anterior para siempre (el contador decía "2 de 3" desde el cuadro 0). En cambio, las duraciones se acortan al hueco.
- Plano medio centrado (sillón): el único espacio libre es una columna de ~340 px al lado de la cabeza. Parte las filas
  con `|`; espera una escala ~0,6 (texto de fila de 37 a 39 px).
