# headline-wall (Muro de Titulares)

**Qué hace:** la pared detrás de la persona se llena de tarjetas de titulares, publicaciones, búsquedas y videos que
dicen todos lo mismo con distintas palabras, pegadas al cuarto detrás de la persona; en la palabra clave un
destacador dorado pasa sobre una frase en cada tarjeta y tarjetas grandes caen en las palabras siguientes.
**Función:** prueba / explicar ("todo el mundo habla de X", "todos dicen X"). Funciona como apertura e igual de bien a
mitad de video o sobre b-roll: pon `F_OUT` y el muro sale de golpe dentro de la toma.
**Frases que lo activan:** "llena la pared detrás de mí con titulares sobre X", "todos hablan de X, muestra los
recortes", "muro de titulares".

## Toma que necesita, y dónde falla
- UNA toma continua (sin cortes internos), 3 a 6 s, con pared visible al lado o sobre la cabeza. Funciona en plano
  abierto (sillón, silla, piso) y medio. La cámara puede estar quieta o moverse: una cámara en movimiento se sigue.
- Cada tarjeta grande necesita unos 280 x 220 px de pared libre al lado de la cabeza dentro de la zona segura. Una
  selfie cercana que llena el cuadro no tiene espacio: usa 1 o 2 tarjetas grandes, u otro efecto.
- Falla en: una pared que en realidad es ventana / espejo / puerta abierta (el seguimiento se desliza), grandes
  movimientos de brazos sobre la pared después de que caen las tarjetas grandes (quedan tapadas), una toma que corta.
  Una pared con monitores o pizarra detrás (como en el escritorio) no sirve.
- Deja 1,5 s después de la última tarjeta grande para que el muro se alcance a leer.

**Entradas del espacio:** recorte sí (`assets/subject.webm`), `aroll_hi` no. Python: numpy, scipy, Pillow (el Python de
la skill los tiene). Sin OpenCV, sin paquetes extra.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `HEADLINES` | lista simple de textos, uno por tarjeta, `[frase]` = destacada | escribe 12 a 20 versiones del mensaje de la persona, en español, de menos de ~40 caracteres; sin medios, personas ni números reales |
| `HEROES` | `(titular, cuadro)` tarjetas grandes que caen en una palabra, 2 a 4 | cuadros de `onsets.py`; en el orden en que se dicen |
| `SEARCH` | texto de la cápsula de búsqueda, o `None` | minúsculas, como una búsqueda tipeada |
| `F_START`, `F_PEAK` | primera tarjeta, última tarjeta del montón | primera sílaba; fin de la frase de apertura |
| `F_ACCENT` | destacador + golpe + impacto grave | inicio de la palabra clave (normalmente el cuadro de la primera tarjeta grande) |
| `F_OUT` | cuadro en que el muro sale de golpe, `None` = se queda hasta el final | uso a mitad de toma; necesita `PUSH = BUMP = 1` y `F_OUT <= frames - 12` |
| `DENSITY`, `LEAD` | aceleración del amontonamiento; ventaja de la tarjeta grande | deja 1.8 y 4 |
| `WALL` | `(x0, y0, x1, y1)` pared que pueden cubrir las tarjetas | primero `None`, luego léela en `work/layout.jpg`: detente sobre sillones, escritorios, ventanas |
| `KEEP_OUT`, `FOREGROUND` | cajas de pantalla donde no entra ninguna tarjeta; polígonos de muebles que las tarjetas pasan por detrás | por defecto `[]`; la cápsula de título del reel; un cojín o respaldo de sillón delante de la pared |
| `FACE`, `HERO_FIRST_SIDE` | objetivo del acercamiento; lado de la primera tarjeta grande | `None` = medido; el lado con más pared libre |
| `N_MID`, `N_FAR`, `FAR_BLEED_SIDES` | cantidad de tarjetas por profundidad, sangrado a los lados | `None` = según el área de pared |
| `PUSH`, `BUMP`, `DIM`, `ACCENT` | acercamiento, golpe, atenuación del cuarto, color del destacador | sube `DIM` a ~1,3 en una pared blanca; acento dorado |
| `OUTLETS`, `PEOPLE`, `CHAT_REPLIES`, `DARK_LABEL` | etiquetas de fuente de relleno | mantenlas genéricas, en español |
| `VOICE`, `FIX_MATTE`, `TRACK_YMAX`, `REF`, `SEED`, `SOUNDS` | audio de la persona sí/no, arreglo de máscara, zona de seguimiento, cuadro de composición, mezcla, sonidos | por defecto; ver trampas |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `SFX=0` saca los sonidos del efecto.
`GRADE=0` saca la viñeta del efecto (el reel da color una sola vez). `CAPTIONS=0` se acepta y no hace nada: este
efecto no tiene palabras de subtítulo.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. inicios de palabra como cuadros -> llena HEADLINES, HEROES, F_* en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. seguimiento + máscara + composición (1 a 2 min). MIRA work/layout.jpg (y work/trackcheck.jpg si la cámara se mueve). Pon WALL / HERO_FIRST_SIDE si hace falta, luego
PY "SK/scripts/fx_run.py" "<slot>" prep.py layout      # solo recompone (segundos). Repite hasta que la imagen esté bien
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 GRADE=0      # 3. página con la guía de seguridad
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.5,1.0,1.5,2.0,2.5,3.0
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Mover una tarjeta a mano: edita `x`, `y`, `rot` en `work/layout.json`, ejecuta `python3 build.py` (un `prep.py layout`
posterior lo sobrescribe).

## Qué mirar en los cuadros finales
- La primera tarjeta grande ya llegó del todo en el cuadro de su palabra y el destacador empieza en ese cuadro (saca el
  cuadro de la palabra y el anterior).
- Las tarjetas quedan pegadas a la pared mientras la cámara se mueve (compara un detalle de la pared junto a una
  tarjeta en dos cuadros a 10 de distancia).
- Cada línea de tarjeta grande se lee completa, ninguna escondida detrás de la cabeza o el hombro; nada tapa la cara
  (las tarjetas están detrás de la persona).
- Nada en los 220 px superiores; tarjetas grandes y medianas dentro de la zona segura en el último cuadro. Las
  tarjetas lejanas pueden salirse por los lados.
- La silueta de la persona: sin crema asomando por una mano o manga rápida, sin borde claro alrededor del gorro o el
  pelo. El render tiene exactamente los `frames` de `clip.json` (revísalo con ffprobe).

## Trampas
- `WALL = None` baja hasta la altura de los codos: bien en una pared desnuda, mal cuando hay un respaldo de sillón o un
  escritorio en esa franja. Revisa siempre la caja cian en `work/layout.jpg`.
- prep imprime `shrunk to 0.xx` / `dropped` cuando una tarjeta grande no tiene espacio: acorta el titular, cambia
  `HERO_FIRST_SIDE`, o usa menos tarjetas grandes. Bajo 0,8 el texto queda pequeño en un celular.
- Pon la `[frase]` al principio de un titular: los saltos de línea se equilibran, y la primera línea es la que
  sobrevive a una tarjeta escondida detrás de la persona.
- Inicios de palabra: Whisper está 1 a 3 cuadros corrido y escucha mal los nombres. `onsets.py` muestra el nivel por
  cuadro; una tarjeta grande con `LEAD` 4 cae en la palabra, menos de 3 se lee tarde.
- Una tarjeta grande solo tiene que quedar libre de donde está la persona desde su propio cuadro de llegada, las
  medianas y lejanas desde el acento: si la persona se inclina hacia una tarjeta más tarde en el espacio, acorta el
  espacio o baja esa tarjeta.
- El seguimiento se ajusta en los píxeles de pared sobre `TRACK_YMAX` (1100). Si `work/trackcheck.jpg` muestra una
  pared duplicada, bájalo justo sobre los muebles y ejecuta `prep.py --force`. Después de editar `FOREGROUND` ejecuta
  `prep.py matte`.
- `matrix3d` no se le pasa a GSAP: una propiedad basada en función (`cam.frame`) lo pone por cuadro. Déjalo así, es
  seguro al buscar.
- `click-soft` es un archivo muy bajo (necesita ~,34 de volumen base); `impact-bass-short` viene en `assets_fx/`. Las
  tarjetas lejanas nunca entran a los 220 px superiores (revisado en cada cuadro); el sangrado lateral está encendido
  por defecto, `FAR_BLEED_SIDES = False` las mantiene completas dentro del cuadro.
