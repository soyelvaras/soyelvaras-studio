# orbit (Órbita)

**Qué hace:** las portadas de los propios reels de la persona giran a su alrededor en un anillo. Del lado de atrás las
tarjetas pasan detrás de la persona, del lado de adelante pasan por delante a la altura del pecho, siempre bajo la
cara.
**Función:** gancho ("publico todos los días", "todos estos salieron de una sola skill", "necesitas ediciones así").
Funciona en cualquier parte: pon `F_IN` y `F_OUT` y los cuadros de antes y después son la toma sin tocar.
**Frases que lo activan:** "pon mis reels en órbita a mi alrededor", "haz que mis reels giren a mi alrededor",
"órbita".

## Primer paso: las portadas son del usuario
Pídele una carpeta con las imágenes de portada de sus reels (jpg / png / webp, al menos 4, 6 es el anillo por defecto;
9:16 es lo mejor, cualquier otra cosa se recorta a 9:16). Cópialas a `covers/` en el espacio. El efecto no trae
portadas. **Sin portadas del usuario = deja fuera el efecto**, no inventes ni tomes prestadas. Las tarjetas no llevan
números salvo que el usuario dé conteos de vistas reales para `COUNTS`: nunca estimes ni redondees hacia arriba un
conteo. Cuadros de sus propios reels editados sirven como portadas.

## Toma que necesita
- **Plano:** abierto o medio, persona centrada, con la barbilla sobre y 1000 aprox. para que quepa una tarjeta entre la
  barbilla e y 1470. Una toma continua mientras el anillo está arriba.
- **Cámara:** quieta o con deriva (el anillo sigue la cabeza una vez que se mueve más de 10 px). No para una cámara que
  se mueve o camina.
- **Pared:** no hace falta. El anillo flota en el cuarto; lo que está detrás de la persona queda como está.
- **Recorte:** como capa. Las tarjetas de atrás van bajo `assets/subject.webm`, las de adelante sobre él; el anillo se
  mide desde el alfa del recorte.
- **Qué lo rompe:** una selfie cercana (la cara llega muy abajo, `prep.py` se detiene y lo dice); una persona que llena
  el ancho del cuadro (las tarjetas pasan de atrás a adelante estando todavía sobre un brazo, `prep.py` avisa); una
  persona muy descentrada; una mano levantada sobre la cabeza (se lee como la cabeza); un recorte débil (pelo o dedos
  perdidos: las tarjetas de atrás se ven a través); una segunda persona en la toma.

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy y Pillow para `prep.py` y `onsets.py`; `build.py` no
necesita nada. Sin OpenCV.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `COVERS` | carpeta con las imágenes de portada del usuario | por defecto `covers` dentro del espacio; el orden de los nombres de archivo es el orden del anillo |
| `COUNTS` | conteos de vistas reales opcionales por archivo | de las estadísticas propias del usuario; `{}` = sin números, sin íconos de reproducción |
| `CARDS` | tarjetas en el anillo, 4 a 8 | 6 |
| `F_IN` | cuadro en que llega el anillo | `onsets.py`: inicio de la palabra (5 o más) |
| `F_OUT` | cuadro en que vuelve la imagen simple, o `None` | inicio de una palabra posterior, al menos 45 después de `F_IN`, como máximo frames - 2 |
| `CAPS`, `CAP_Y` | las palabras de subtítulo propias del efecto y su parte superior | palabras dichas, cuadros de `onsets.py`; `None` = medido, caja amarilla en `work/ring.jpg` |
| `CX`, `CY`, `RX` | centro del anillo y medio ancho | `None` = medido desde el recorte; escribe px solo para corregir lo que muestra `work/ring.jpg` |
| `TILT` | alto / ancho del anillo | ,33; más chico es más plano |
| `CARD_W`, `NEAR`, `FAR` | ancho de tarjeta adelante, tamaño adelante y atrás | 190, 1,0, ,6; `prep.py` achica la tarjeta solo si el anillo no cabe |
| `FACE_GAP` | px libres entre las tarjetas de adelante y la caja de la cara | 30 |
| `REV`, `DIR`, `PHASE` | segundos por vuelta, dirección, ángulo inicial | 5,2, 1, ,35 |
| `FOLLOW` | el anillo sigue la cabeza cuando la toma deriva | `True` |
| `CROP_Y`, `FAR_DIM` | qué parte de una portada no 9:16 se conserva, brillo de las tarjetas de atrás | ,5, ,75 |
| `GRADE` | look opcional mientras el anillo está arriba | `None` = apagado |
| `VOICE`, `REF`, `SOUNDS` | audio de la persona sí/no, cuadro en la imagen de revisión, sonidos | por defecto |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las palabras de
subtítulo propias del efecto. `SFX=0` saca sus sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: pídele al usuario una carpeta con las portadas de sus propios reels (sus portadas guardadas, o exportadas de su perfil) y cópialas a <slot>/covers/ (fx_new.py --buyer-files <carpeta> hace la copia). Sin portadas del usuario = sin Órbita: déjalo fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # copia las portadas del usuario a ./covers (crea la carpeta; 4 o más imágenes); 1. inicios de palabra como cuadros -> F_IN, F_OUT, CAPS en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. tarjetas + anillo medidos desde el recorte (segundos)
# editar: MIRA work/ring.jpg (caja roja de la cara sobre toda la cabeza, ninguna tarjeta amarilla de adelante sobre ella, ninguna tarjeta en el borde rojo), lee las líneas WARNING, corrige el bloque CLIP y ejecuta prep.py de nuevo hasta que esté bien.
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # 3. página con la guía de seguridad
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.0,1.5,2.0,2.5,3.0,3.5
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Cualquier Python con numpy y Pillow sirve en lugar de la ruta del entorno. Elige los tiempos de instantánea dentro del
tiempo en pantalla del anillo.

## Qué mirar en los cuadros finales
- El cuadro 0, el cuadro antes de `F_IN - 4`, el cuadro de `F_OUT` y el último cuadro: imagen simple, ninguna tarjeta,
  sin borde oscuro.
- El cuadro de `F_IN`: las primeras tarjetas están arriba y se ven claramente en la palabra.
- Seis cuadros repartidos durante el anillo: ninguna tarjeta de adelante sobre la cara (barbilla incluida), las de atrás
  realmente escondidas por la cabeza y los hombros, nunca dibujadas encima.
- A tamaño completo, un cuadro con una tarjeta de atrás junto al pelo o a una mano: borde de recorte limpio, ninguna
  tarjeta asomando. En los extremos izquierdo y derecho del anillo una tarjeta pasa de atrás a adelante al lado del
  cuerpo, no sobre un brazo.
- Todo dentro de la zona segura (arriba 220, abajo 1470, lados 35, derecha 100 desde y 1155). Números en las tarjetas
  solo si se llenó `COUNTS`. El render tiene exactamente los `frames` de `clip.json` (revísalo con ffprobe).

## Trampas
- La caja de la cara se mide desde la silueta, no con un detector de caras: va de lo alto de la cabeza (gorro, pelo) a
  la fila más angosta sobre los hombros. Un cuello alto, una capucha o una mano en la barbilla esconden el cuello;
  entonces la caja mide 1,35 anchos de cabeza de alto. Si la caja roja de `work/ring.jpg` termina sobre la barbilla, sube
  `FACE_GAP` o escribe `CY`.
- Las tarjetas de adelante cruzan el pecho, así que tapan las manos que gesticulan por un momento. Ese es el look; si un
  gesto de la mano lleva la frase, elige otro momento.
- `prep.py` tiene que correr de nuevo después de cualquier cambio en `F_IN`, `F_OUT`, `CARDS` o los campos del anillo:
  `build.py` rechaza un `work/ring.json` medido para otros cuadros.
- Con `CX`, `CY` o `RX` escritos a mano, no se corrige nada por ti: los avisos son la única protección. `F_OUT = None`
  mantiene el anillo hasta el último cuadro: solo cuando el reel corta ahí.
- Los sonidos son de la plantilla a 0,75x del volumen: un whoosh y un pop suave al entrar, un whoosh al salir.
