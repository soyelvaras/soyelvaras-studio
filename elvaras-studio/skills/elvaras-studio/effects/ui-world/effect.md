# ui-world (Mundo App)

**Qué hace:** una pantalla de app cae sobre la parte superior del cuadro y la persona queda delante de ella: el recorte
de la persona va sobre la pantalla, la unión cruza a la mitad del pecho, el cuarto real se ve en la franja de abajo, y
la pantalla acompaña las palabras de la persona (cosas que caen en una caja de mensaje, una línea que se escribe y se
envía, una respuesta y una tarjeta de pasos que se marcan, una tarjeta de resultado que aparece al lado de la cabeza).
**Función:** explicar ("solo haces X, después Y"). Funciona en cualquier parte de un video: como apertura, a mitad de
video en una frase de cómo funciona, o en el remate. Pon `F_OUT` y la pantalla se levanta de nuevo dentro de la toma.
**Frases que lo activan:** "ponme delante de la pantalla de la app", "ponme delante de la pantalla de Claude", "muestra
el chat detrás de mí mientras lo explico", "mundo app".

## Toma que necesita, y dónde falla
- UNA toma continua, 3 a 6 s, la persona de frente a cámara, cabeza y hombros en cuadro. Planos abiertos y medios
  funcionan: una cabeza pequeña se acerca hasta 1,25x y toda la toma baja para que la cabeza quede bajo la pantalla.
- Mejor cuando la cabeza de la persona mide 150 a 320 px de alto en el espacio de 1080x1920. Deja 1,5 s después de lo
  último que aparece.
- **Falla en:** una selfie justa (cabeza de más de ~360 px de alto: a la pantalla le queda una franja y no hay franja del
  cuarto para los subtítulos); una persona que se mueve mucho arriba y abajo o camina (la pantalla se compone para la
  posición más alta de la persona, no se sigue nada); manos levantadas sobre la cabeza (cortan la caja de mensaje); una
  toma que corta; dos personas en cuadro (solo se mide la silueta más grande); una cabeza que ya está cerca del borde
  inferior del cuadro.
- **La calidad del recorte decide este efecto.** Una pantalla clara muestra cada falla de la silueta. Ropa del mismo
  color que la silla o el sillón detrás es la falla clásica (hombro comido, o un pedazo de silla conservado). Mira la
  línea de los hombros antes de renderizar. En las tomas de Cristobal en la silla gamer pasa esto: usa las tomas del
  sillón azul.

**Entradas del espacio:** recorte sí (`assets/subject.webm`), `aroll_hi` no. Python: numpy, scipy, Pillow (el Python de
la skill los tiene). Sin paquetes extra, sin modelo propio.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `SCREEN` | `'chat'` (pantalla de chat incluida con tu texto) o la ruta de tu propia imagen / grabación de pantalla | solo tu propia app o página; vertical, 1080 px de ancho o más; ponla en `assets/` |
| `APP_NAME`, `APP_MARK` | chat: nombre en el encabezado, archivo de logo pequeño opcional | lo tuyo; `None` = sin logo |
| `GREETING`, `PLACEHOLDER` | chat: línea en la pantalla vacía, texto gris en la caja | `None` = ninguno. En español ("¿Qué hacemos hoy?", "Escribe aquí...") |
| `ATTACH` | `(cuadro, [1 a 5 etiquetas o rutas de imágenes])` cosas que vuelan a la caja | cuadro de la palabra ("suelto") desde `onsets.py` |
| `TYPE`, `SEND` | `(cuadro, texto)` escrito en la caja; cuadro en que se envía | texto de máximo ~30 caracteres |
| `REPLY` | `(cuadro, texto)` la respuesta, aparece palabra por palabra | necesita `SEND`; máximo ~34 caracteres |
| `STEPS` | `(título, [(cuadro, fila), ...])` 1 a 4 filas que aparecen y se marcan | necesita `SEND`; filas de máximo ~30 caracteres |
| `RESULT` | `(cuadro, título, imagen o None, insignia)` tarjeta al lado de la cabeza | la palabra de remate; una imagen 9:16 funciona mejor |
| `LABELS` | `(cuadro, TEXTO, dónde)` etiquetas de destacador | dónde = `'attach'`, `'text'` o `(x, y)` desde una instantánea con `SAFE=1` |
| `F_IN`, `F_OUT` | cuadro en que cae la pantalla; cuadro en que se levanta | `F_OUT = None` se queda hasta el final |
| `EDGE` | y del borde inferior de la pantalla (la línea del pecho) | `None` = medido; ponlo a ojo si la línea rosada de `work/measure.jpg` está corrida |
| `HEAD_Y`, `ZOOM` | y hasta donde se baja lo alto de la cabeza; acercamiento | 860 y `None` (medido). Un número `HEAD_Y` más bajo = más franja del cuarto, menos pantalla |
| `RESULT_SIDE` | `'L'` / `'R'` lado de la tarjeta de resultado | `None` = el lado con más espacio sobre el hombro |
| `ACCENT`, `HILITE` | color del botón / progreso; color de las etiquetas | tu color de marca; dorado |
| `CAPTION_FIX`, `CAP_Y` | corrige palabras de subtítulo mal escuchadas (`''` saca una); y de la línea de subtítulos | lee las palabras que imprime `onsets.py` |
| `SCREEN_ZOOM`, `SCREEN_X`, `SCREEN_Y`, `SCREEN_SCROLL` | material: tamaño, posición, desplazamiento lento de tu imagen | empieza en 1, 0, 0, 0 y ajusta en una instantánea |
| `SHADOW`, `FIX_EDGE`, `VOICE`, `SOUNDS` | la sombra de la persona sobre la pantalla, recorte limpiado, el audio de la persona, lista de sonidos | por defecto |

Cualquier parte del chat puesta en `None` se omite. En modo material los campos del chat se ignoran; `LABELS` con
`(x, y)` y los subtítulos igual funcionan.
**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las palabras de
subtítulo de la franja del cuarto (el reel principal las pone en su lugar). `SFX=0` saca los sonidos del efecto.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. inicios de palabra como cuadros -> llena el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. mide a la persona + hornea el recorte limpio (1 a 2 min). MIRA work/measure.jpg: cian = lo alto de la cabeza, amarillo = cuello, rosado = línea del pecho. Rosado fuera del pecho -> pon EDGE
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # 3. página con la guía de seguridad; lee las líneas WARNING que imprime
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.2,1.0,2.0,3.0,4.0      # (elige los tiempos para que uno caiga justo después de cada uno de tus cuadros: cuadro / 30)
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar en los cuadros finales
- La silueta de la persona contra la pantalla a tamaño completo: ambos hombros completos, ningún pedazo de silla o pared
  conservado, sin borde oscuro o claro alrededor del pelo, el gorro y las manos.
- La unión: el borde de la pantalla cruza el pecho, y no hay costura ni salto de color en el cuerpo justo debajo.
- Cada cosa cae en su palabra (saca el cuadro de la palabra y el anterior): adjuntos en la caja, el clic de enviar, la
  tarjeta de resultado.
- Nada en la pantalla que haya que leer queda escondido detrás de la cabeza; la tarjeta de resultado libre de la cara; la
  cara nunca tapada (todo en la pantalla está detrás de la persona).
- Zona segura: encabezado bajo y 220, etiquetas y tarjetas dentro de los lados, subtítulos sobre y 1470. Primer y último
  cuadro: con `F_IN` > 0 o `F_OUT` puesto tienen que ser la toma sin tocar. La cantidad de cuadros es igual a `frames`
  de `clip.json` (revísalo con ffprobe).

## Trampas
- El recorte del espacio viene de `_shared/rvm_cut.py`. Si un hombro queda comido o se conserva un mueble, un recorte
  mejor le gana a cualquier ajuste aquí: rehaz el recorte y pásalo con `fx_new.py --cutout-from`, luego ejecuta
  `prep.py` de nuevo. Un número `EDGE` más bajo (unión más arriba en el pecho) esconde una mala línea de hombros.
- `prep.py` mide el cuello desde la silueta. Una mano junto a la cara, una capucha o pelo largo dan un cuello
  equivocado: imprime un aviso, pon `EDGE` tú mismo. Después de cambiar solo `EDGE`, `HEAD_Y` o `ZOOM` no hace falta
  correr prep de nuevo.
- El reencuadre mueve y escala la imagen y el recorte juntos, solo hacia abajo. `ZOOM` sobre 1,25 queda blando en un
  espacio de 1080.
- La pantalla necesita unos 12 cuadros para llegar: empieza el espacio (o pon `F_IN`) al menos 12 cuadros antes de que
  caiga lo primero, y saca `GREETING` cuando lo primero cae dentro del primer segundo.
- Los inicios de palabra de Whisper están 1 a 3 cuadros corridos: usa la columna de inicios. Los subtítulos usan
  `words.json` tal cual: corrige nombres en `CAPTION_FIX`. Un espacio que empieza a mitad de oración puede perder su
  primera palabra en `words.json`.
- `build.py` se detiene con un mensaje claro cuando un texto no cabe (demasiadas filas, sin espacio para la caja). Los
  anchos del texto tipeado se estiman, así que revisa en una instantánea una etiqueta puesta con `'text'`.
- Una grabación de pantalla tiene que cubrir todo el espacio y se reproduce desde su inicio en `F_IN`. No muestres una
  pantalla, publicación o página que no sea tuya. La demo en `example/` se hizo a mano (otras tipografías y acento): ver
  `example/clip.md`.
