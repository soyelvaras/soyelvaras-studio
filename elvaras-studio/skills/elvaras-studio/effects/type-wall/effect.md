# type-wall (Muro de Palabras)

**Qué hace:** el cuarto detrás de la persona se convierte en un muro oscuro de palabras gigantes. Filas de una palabra
repetida desfilan hacia los lados en direcciones alternadas, filas sólidas y de contorno se turnan, y cada fila cambia
de golpe a la palabra siguiente en el cuadro en que la persona la dice. La fila justo sobre la cabeza dice cada palabra
cuando la persona la dice; en la palabra que importa todo el muro salta a ella, se acerca, y esa fila pasa a dorado. La
persona queda delante del muro todo el tiempo.

**Función:** énfasis, en cualquier parte de un video: una frase gancho, la oración de la que cuelga una sección, un
remate, un llamado a la acción. Mejor en una frase corta (2 a 4 segundos) con una palabra que importa.

**Frases que lo activan:** "pon palabras gigantes detrás de mí que cambien mientras hablo", "muro de palabras en esta
frase", "convierte la pared detrás de mí en palabras".

**Toma que necesita:** una cámara quieta (trípode, o un celular apoyado en algo), la persona del pecho hacia arriba o
más abierta, con espacio libre sobre la cabeza: lo alto de la cabeza en y 250 o más abajo en el cuadro de 1080x1920. Un
recorte limpio de la persona (el creador del espacio recorta a la persona con el modelo de recorte bueno). 1 a 2
segundos de toma después de la última palabra para que el muro se alcance a leer.
**Dónde falla (dilo y ofrece otro efecto):**
- Selfie justa sin pared: cabeza cerca del borde superior, hombros de borde a borde. Las palabras no tienen dónde
  mostrarse. `prep.py` avisa ("no room above the speaker's head", "open wall under 40%").
- Cámara en movimiento o en mano: el muro está fijo, así que la persona tambalea encima como un sticker, y una forma
  `KEEP` se despega del mueble. `prep.py` avisa sobre 8 px de deriva. (Un solo asentamiento lento con `KEEP = []` está
  bien: el clip de demo tiene uno.)
- Una cara en un cuadro, póster o pantalla detrás de la persona puede terminar en el recorte y flotar en el muro.
  `prep.py` informa una segunda forma; mira esos cuadros. Un recorte que mezcla la ropa oscura con una silla oscura deja
  la silla flotando sobre el muro.
- Palabras largas: al tamaño por defecto una palabra de más de unas 7 letras es más ancha que el cuadro. Pártela o
  sáltala (en español conviene elegir palabras cortas).

**Entradas del espacio:** `assets/aroll.mp4`, recorte `assets/subject.webm` (obligatorio), `clip.json`, `words.json`.
Sin `aroll_hi`. Python: el Python de la skill para `prep.py` (numpy, scipy, Pillow); `build.py` y `onsets.py` corren en
python3 simple. Trae su propia tipografía y un sonido en `assets_fx/`.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo obtenerlo |
|---|---|---|
| `PHRASES` | lo que dice el muro: 1 a 3 palabras EN MAYÚSCULAS por frase, cada una `(cuadro, 'PALABRA')`; `'hit': True` en la frase que importa | palabras de `words.json`, cuadros de `python3 onsets.py` (columna "swap"). La primera palabra entra con el muro |
| `IN_FRAME`, `OUT_FRAME` | cuadro en que llega el muro (corte seco desde el cuarto, las filas entran de golpe) y cuadro en que vuelve el cuarto | `IN_FRAME` = cuadro de la primera palabra del muro (0 = arriba desde el inicio); `OUT_FRAME = None` = se queda hasta el final del espacio |
| `KEEP` | formas de la imagen real que quedan delante del muro (el sillón, escritorio o mesón donde se sienta la persona) | `[]` = el muro llena el cuadro. Si no, lee los puntos de las esquinas en `work/measure.jpg` (las etiquetas son px a tamaño completo), unos px dentro del borde del mueble |
| `FS` | tamaño de letra en px | 205; baja a 150 a 180 cuando hay poco espacio sobre la persona o una palabra es muy ancha |
| `ACCENT_Y`, `HEAD_GAP` | dónde terminan las letras de la fila dorada | `None` = medido, 14 px sobre el punto más alto de la cabeza |
| `XC` | `{fila: x}` para mover dónde se centra la palabra de una fila en un cambio | `{}` = medido (el hueco más ancho que deja la persona en esa fila); `build.py` imprime los números de fila |
| `GROUND`, `INK`, `ACCENT` | colores del muro, color de letra, color de la fila de acento (hex de 6 dígitos) | por defecto bosque, crema y dorado; mantén el muro oscuro |
| `VOL_IN`, `VOL_HIT`, `VOL_SWAP` | whoosh de entrada, golpe grave en la palabra que importa, whoosh suave en una frase nueva | 0 apaga uno |

Una frase de 1 palabra llena todas las filas. Una frase de 2 o 3 palabras se arma hacia abajo: todas las filas dicen la
palabra 1, luego una de cada 2 (o 3) filas pasa a la palabra 2, luego la palabra 3, así el muro terminado lee la frase
de arriba abajo.
**Interruptores:** `SAFE=1` dibuja la zona segura, la línea de lo alto de la cabeza (azul) y el contorno `KEEP` (verde).
`SFX=0` saca los sonidos. `CAPTIONS=0` no cambia nada: el muro es el subtítulo, así que el video principal no debe
poner subtítulos en estos cuadros.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # mide a la persona, luego MIRA work/measure.jpg (línea amarilla sobre lo alto de la cabeza, tinte azul = todo lo que ocupa la persona)
PY "SK/scripts/fx_run.py" "<slot>" onsets.py -v      # 3. cuadros de palabra desde el audio; lee la tira de volumen por cuadro para cada palabra del muro
# editar: el bloque CLIP en build.py: PHRASES siempre, KEEP cuando la persona está sentada sobre o detrás de algo.
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # arma con la guía puesta, lint, mira instantáneas (una por cambio, una al final); lee su tabla de filas y cualquier línea "!!"
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos en segundos, separados por coma>
PY "SK/scripts/fx_run.py" "<slot>" build.py      # render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
En el video principal: arma con `SFX=0` si tiene su propio diseño de sonido, pon el render sobre la toma exactamente en
estos cuadros, y no les pongas subtítulos.

## Qué mirar en los cuadros finales
- Cada cambio aparece en pantalla en el cuadro de su palabra (la fila dorada primero, el resto en unos pocos cuadros),
  nunca antes de que la persona lo diga.
- Toda la silueta de la persona queda limpia en cada cuadro: sin halo del cuarto anterior, sin dedos faltantes, nada
  extra flotando (cuadros, lámparas).
- La fila dorada queda libre sobre la cabeza y su palabra se lee completa en el cambio. La cara nunca queda tapada (las
  palabras están detrás de la persona por construcción).
- Con `KEEP`: ninguna astilla de la pared vieja sobre el mueble, y el borde no nada.
- El estado final se mantiene lo suficiente para leerse, y la cantidad de cuadros es igual a `frames` de `clip.json`.

## Trampas
- Todo lo que está detrás de la persona se reemplaza. Si la persona está en un sillón o escritorio y `KEEP` está vacío,
  la persona flota en el muro. Dibuja el borde superior del mueble como forma `KEEP`, 3 a 5 px dentro del mueble, cerrada
  a lo largo del borde inferior del cuadro. `KEEP` y la fila sobre la cabeza suponen que la persona y la cámara se
  quedan quietas: si la persona se levanta o se inclina mucho, acorta el espacio.
- Los inicios de palabra de Whisper se corren unos cuadros, y `onsets.py` es solo una primera estimación (en el clip de
  prueba puso "out" en la vocal de la palabra anterior). Ajusta cada palabra del muro en la tira `-v`. Un cuadro tarde
  está bien, un cuadro antes se ve como un error.
- Habla rápida: una fila que no terminó de esparcirse cuando toca la palabra siguiente salta la palabra anterior. Es a
  propósito; la fila dorada nunca salta.
- Las dos filas superiores van en los 220 px superiores donde viven los botones de la app. Eso está bien para las filas
  que desfilan; `build.py` avisa si la fila dorada en sí empieza sobre 220.
- Imágenes de luz de día brillante sobre el muro oscuro se ven recortadas a propósito. Ese es el look. No agregues grano
  ni pases a blanco y negro para esconderlo. Con el muro arriba, el cuarto que se conserva recibe el mismo color que la
  persona (cerca de 10% más oscuro) para que las uniones calcen.
