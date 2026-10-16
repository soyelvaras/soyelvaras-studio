# phone-mockup (Teléfono 3D)

**Qué hace:** un teléfono 3D dibujado (marco metálico, brillo de vidrio, grosor en el borde, sombra suave, flotación
lenta) llega volando al lado de la persona y muestra una pantalla; un punto de toque presiona la pantalla en las
palabras de la persona (onda, anillos, el botón cambia, las filas se marcan), y luego el teléfono se va.
**Función:** explicar (mostrar la pantalla de la que habla la persona sin cortar fuera de ella).
**Frases que lo activan:** "pon un teléfono a mi lado mostrando la app, toca Aprobar cuando digo aprobar", "muestra esta
grabación de pantalla en un teléfono a mi lado", "teléfono con esta captura mientras hablo".

## Primer paso: qué va en el vidrio (pregunta antes de armar)
- **Su propia pantalla:** pídele al usuario la grabación (mp4 / mov / webm) o la imagen (png / jpg) y cópiala a
  `screen/` en el espacio (`screen/recording.mp4`). Solo una pantalla que pueda mostrar. Pon `SCREEN`.
- **Sin archivo:** la tarjeta incluida (`SCREEN = None`): nombre de app, etiqueta, título, hasta 4 filas, un botón, todo
  escrito a partir de lo que dice la persona en el clip, en español. Sin números, nombres ni afirmaciones que no dice.
  Los valores por defecto son de relleno: reemplaza cada uno.
- Ni archivo ni palabras que calcen en una tarjeta: deja fuera el efecto.

## Toma que necesita
- **Plano:** medio o abierto es lo mejor. Cercano funciona cuando hay 300 px o más de fondo al lado de la cabeza; un
  plano cercano que llena el cuadro recibe un teléfono más chico (hasta 250 px), y si ni eso cabe build.py se detiene
  con "no room for a phone" (usa otra toma o déjalo fuera).
- **Cámara:** quieta o con deriva. El teléfono va fijo a la pantalla, no a la pared, así que una cámara que se mueve
  mucho lo hace leer como capa (está bien) pero puede pasar a la persona por el vidrio (build.py imprime cuánto esconde
  la persona).
- **Pared:** no hace falta. Cualquier fondo; los recargados o claros reciben una atenuación suave detrás del teléfono.
- **Recorte:** como capa (`LAYER='behind'`: el teléfono va entre el fondo y la persona, la cabeza y las manos pasan por
  delante) y medido (el lado, el tamaño y la altura salen de él). `LAYER='front'` lo necesita solo para medir; con
  `--no-cutout` escribe `SIDE`, `PHONE_W`, `PHONE_TOP` a mano.
- **Lo rompe:** espacios de menos de 2 s (necesita 40 cuadros entre entrada y salida, mejor 75), una palabra de toque en
  los primeros 0,6 s o en los últimos 0,5 s, una mano detenida delante del punto de toque, la persona caminando por el
  cuadro. Sin `aroll_hi`.
- **Bordes:** el cuadro 0 y el último son el clip sin tocar (el teléfono entra en `IN_FRAME` y se fue 12 cuadros después
  de `OUT_FRAME`), así que el espacio cae sobre la toma en cualquier parte.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `SCREEN` | `None` (tarjeta incluida) o `'screen/<archivo>'` | el archivo del usuario, ver primer paso |
| `SCREEN_START`, `SCREEN_POS` | segundo de la grabación en el tiempo 0 del espacio; qué parte sobrevive al recorte al vidrio alto | recorre la grabación; `'top'` si la acción está arriba |
| `CARD` | `app, intro, label, title, rows, button, button_done, button_alt, done` | las palabras de la persona; `''` / `[]` esconde una parte |
| `CARD_AT` | cuándo sube la tarjeta | una palabra dicha, un cuadro, o `None` (0,5 s después del teléfono) |
| `TAPS` | `[(cuándo, dónde), ...]` | `cuándo`: una palabra de words.json (`'manda#2'` = la segunda vez) o un número de cuadro; `dónde`: `'button'`, `'row1'`.. o `(x, y)` en fracciones del vidrio (una instantánea con `GRID=1` las muestra) |
| `ROWS_FOLLOW_BUTTON` | las filas no tocadas se marcan solas después del botón | `False` para dejarlas vacías |
| `TURN` | palabra / cuadro en que el teléfono gira hacia el espectador | `None` = apagado |
| `IN_FRAME`, `OUT_FRAME` | inicio de la llegada, inicio de la salida | 3 y `None` (16 cuadros antes del final) |
| `SIDE`, `PHONE_W`, `PHONE_TOP` | `'auto'` o izquierda/derecha, px, px | deja `'auto'`: el lado con más espacio, lo más grande que cabe, a la altura de la cabeza |
| `LAYER` | `'behind'` o `'front'` | `'front'` cuando el recorte de la persona es tosco o no existe (por ejemplo, una silla oscura mezclada con la ropa) |
| `ROOM` | `'auto'`, `'off'` o `dict(scale, x, y)` | tomas justas: corre la imagen mientras el teléfono está arriba y la devuelve antes de que se vaya |
| `COVER_MAX` | cuánto del vidrio puede esconder la persona en promedio | 0,12; más bajo si la pantalla tiene que seguir legible |
| `HAND_FRAMES`, `MATTE_FIX` | arreglos opcionales del recorte, apagados por defecto | solo después de ver un borde de mano en bloques o un bloque oscuro en el vidrio; vuelve a ejecutar prep.py |
| `CAPS`, `CAP_PUNCH`, `CAP_FIX`, `CAP_Y` | las palabras de subtítulo propias del efecto | `[]` o `CAPTIONS=0` cuando el reel pone los subtítulos del espacio (el caso normal) |
| `ACCENT`, `GRADE` | color de acento (dorado); filtro CSS sobre la imagen | deja `GRADE='none'` o los bordes dejan de calzar |

**Interruptores:** `SAFE=1` guía de zona segura, `GRID=1` fracciones en el vidrio (ambos solo instantáneas),
`CAPTIONS=0`, `SFX=0`.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: pregúntale al usuario qué va en el teléfono: su propia grabación de pantalla o imagen (cópiala a <slot>/screen/ y pon SCREEN), o la tarjeta incluida escrita con lo que dice en el clip (SCREEN = None, reemplaza cada relleno). Solo una pantalla que pueda mostrar. Ni archivo ni palabras que calcen = sin Teléfono 3D: déjalo fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # cada palabra con el cuadro donde caería un toque, dónde está la persona
# editar: copia el archivo del usuario a screen/ (si hay), edita el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # recorte suave para el teléfono oscuro (+ el archivo de pantalla cortado al espacio), cerca de 1 min
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # imprime lado, tamaño, límites, cuadros de toque, avisos (!!) y tiempos de instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos que imprimió build.py>
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, primer / último cuadro simples, zona segura, puntos de toque, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Usa solo numpy, scipy, Pillow. Un espacio de 4 s toma unos 8 minutos de punta a punta.

## Qué mirar (work/check/sheet.jpg, tap_*.jpg)
- El cuadro del toque: punto presionado sobre el objetivo, color de acento en la pantalla dentro de 2 cuadros, en la
  palabra de la persona (no antes).
- La cara de la persona nunca queda detrás del teléfono; donde la cabeza o una mano lo cruzan, el borde está limpio
  (sin borde claro, sin bloque oscuro).
- Las palabras en el vidrio se leen en tamaño celular; el título no se sale de la tarjeta.
- Teléfono dentro de la zona segura: nada sobre y 220, borde derecho en x 1045 como máximo (980 bajo y 1155), borde
  inferior sobre los subtítulos (y 1240).
- Primer y último cuadro idénticos al clip (check.py imprime la diferencia).

## Trampas
- Whisper pone el inicio de una palabra hasta 0,3 s antes, y "aprobar" empieza en su sílaba débil: los toques usan el
  inicio de la sílaba más fuerte desde el audio. Si uno se ve corrido, da el número de cuadro.
- Nunca pongas `filter` u `opacity` bajo 1 en los nodos 3D del teléfono (aplana el borde): el desenfoque y los fundidos
  van en `#phouter`.
- El fondo y el recorte comparten la clase `.cam` para que `ROOM` mueva los dos; una transformación en uno solo da una
  imagen doble.
- Un borde doble en la persona sobre el teléfono = desfase en la cantidad de cuadros del recorte: vuelve a crear el
  espacio.
- Las fracciones de toque son del vidrio visible después del recorte, no de la grabación original.
- Palabras en pantalla: las de la persona, sin guiones largos, nunca "gratis" ni "curso", sin acento naranjo, sin
  números ni nombres inventados.
