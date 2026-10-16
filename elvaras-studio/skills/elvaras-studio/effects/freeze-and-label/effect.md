# freeze-label (Congela y Señala)

**Qué hace:** la imagen se congela en una palabra mientras la voz sigue, el cuarto se suaviza y atenúa detrás de la
persona, y etiquetas con líneas guía apuntan a partes de la persona congelada. Luego un corte seco de vuelta al video
en vivo.
**Función:** explicar (también un gancho: "esta es la persona" en dos etiquetas).
**Frases que lo activan:** "congela la imagen en X y ponme etiquetas: A, B", "congela en esa palabra y etiquétame",
"pausa la imagen y señala A y B".

## Toma que necesita
- **Plano:** abierto o medio es lo mejor (espacio al lado o sobre la persona para las etiquetas). Cercano funciona con
  1 o 2 etiquetas cortas y `ZOOM = 1.0`.
- **Cámara:** quieta, con deriva o en movimiento: la imagen está congelada, no se sigue nada. Una cámara en movimiento
  solo hace más grande el salto de vuelta al video en vivo, y más probable que el cuadro detenido esté movido.
- **Pared:** al lado o arriba ayuda (las etiquetas van primero sobre fondo libre). Sin pared, van sobre el cuerpo,
  nunca sobre la cabeza.
- **Recorte:** como capa y medido. La persona queda nítida sobre el cuarto suavizado (horneado en la imagen congelada),
  y la cabeza, los puntos de anclaje y el espacio libre se miden UNA vez en el cuadro detenido. `LOOK = 'off'`: solo
  medido.
- **Qué lo rompe:** un parpadeo o desenfoque de movimiento en la palabra del congelado (elige otro cuadro u otra
  palabra), una capucha / pelo largo sobre el cuello / una mano en la cabeza / una cabeza que no es lo más alto del
  recorte (sin silueta de cabeza: escribe `HEAD`), una segunda persona en el recorte, una selfie cercana con 3
  etiquetas (build.py se detiene y dice cuántas caben). Las manos se encuentran por el color de piel tomado de la cara:
  guantes, brazos descubiertos, ropa color piel o una mano delante del pecho se pierden o quedan mal ubicadas (usa
  pecho / hombro / un punto en fracción).
- La pausa necesita cerca de 1 s por etiqueta, y 13 cuadros de imagen en vivo después de soltar.

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte: OBLIGATORIO), `words.json`, `clip.json`. Sin `aroll_hi`. Las
tipografías (Inter Tight 800, JetBrains Mono 500) y `click.mp3`, `pop.mp3`, `whoosh-short.mp3` vienen de la plantilla.
Python: numpy, scipy, Pillow. El efecto no trae imágenes ni sonidos y no necesita ninguno del usuario: solo sus propias
palabras para las etiquetas.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `FREEZE` | palabra dicha en que se congela la imagen | como la imprime `bake_freeze.py` (ortografía de Whisper); `'esto#2'` = el segundo "esto"; o un número de cuadro |
| `HOLD` | qué cuadro se detiene | `'auto'` = el más nítido de los 6 cuadros desde la palabra; o 0 a 5 cuadros después de ella. SIEMPRE revisa `work/freeze_pick.jpg` |
| `RELEASE` | palabra en que vuelve el video en vivo | una palabra o cuadro al menos 13 cuadros antes de que termine el espacio. `None` = congelado hasta el último cuadro |
| `LABELS[i]` | `(texto, palabra en que aparece, a qué apunta)` más `'left'` / `'right'` opcional para el lado de la etiqueta | texto: palabras propias de la persona, 1 a 3 palabras, nunca un número, resultado o afirmación que no dice. palabra `''` = una después de otra. apunta a: `head`, `cap`, `chest`, `shoulder`, `hand` (o `head_left`, `hand_right` ... como se ve en pantalla), o `(fx, fy)` = un punto como fracción de la caja de la persona |
| `ZOOM`, `DRIFT` | acercamiento de la imagen congelada, avance lento durante la pausa | 1.12 y 0.03. Abierto: hasta 1,2. Cercano: 1,0 a 1,06 |
| `LOOK` | el cuarto congelado: `'subtle'`, `'strong'`, `'off'` | `'subtle'`. Solo desenfoque y atenuación: la imagen congelada siempre queda a todo color |
| `NUMBERS` | la pestaña pequeña 01 / 02 de cada etiqueta | `True`; `False` = solo texto |
| `ACCENT`, `CHIP`, `INK` | punto y pestaña, etiqueta y línea, texto | colores de marca (dorado, crema, tinta), nunca naranjo |
| `HEAD` | caja de la cabeza escrita a mano `(x0, y0, x1, y1)`, de lo alto a la barbilla | `None`. Solo cuando build.py no encuentra la cabeza: léela en `work/hold.jpg` |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas, nunca la renderices). `SFX=0` sin sonidos. `GRADE=0` sin look de
congelado (igual que `LOOK = 'off'`; la imagen en vivo nunca recibe color). `CAPTIONS=0` se acepta y no cambia nada (no
hay palabras de subtítulo). `COLTEST=1` armado de control de color: el cuadro detenido sin tratar a 1:1.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" bake_freeze.py      # imprime las palabras con sus cuadros de inicio y revisa que el recorte esté terminado
# editar: llena el bloque CLIP en build.py, luego arma (cerca de 12 s); una línea que empieza con !! es un alto o un aviso que hay que atender
PY "SK/scripts/fx_run.py" "<slot>" build.py
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf render      # render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # números, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 5 s toma unos 3 minutos de punta a punta una vez que existe el recorte (armado 12 s, render 30 s,
revisión 5 s).

## Cómo termina (el salto de vuelta al video en vivo)
El cuadro congelado y la imagen en vivo nunca coinciden, así que el salto se hace a propósito: las etiquetas salen
hacia el lado, la imagen fija "inhala" 0,2 s, luego un CORTE SECO cae en la palabra de `RELEASE` con un golpe de corte
(imagen en vivo de 1,07 a 1,0 en 10 cuadros) y un destello corto de luz. Del cuadro 0 a la palabra del congelado es
imagen en vivo simple, y también todo desde 11 cuadros después de soltar. `RELEASE = None`: sin salida, las etiquetas
se quedan y el espacio TERMINA congelado, en un corte. Úsalo solo cuando el reel corta a otra cosa justo después del
espacio.

## Qué mirar (work/check/)
- Los números de check.py: cantidad de cuadros, primeros / últimos cuadros simples, la pausa realmente congelada,
  RESULT: ok.
- `sheet.jpg`: ninguna etiqueta ni línea sobre la caja azul de la cabeza, nada pasado las líneas rojas, cada etiqueta
  arriba en su palabra, último cuadro simple.
- Los primeros cuadros congelados contra los últimos en vivo: sin salto de color (solo el destello y la atenuación). El
  texto se lee en tamaño celular (`renders/<slot>-phone.mp4`; build.py imprime la altura del texto, menos de 40 px es
  pequeño).

## Trampas
- `HOLD = 'auto'` toma el cuadro más nítido, y el cuadro más nítido suele ser un parpadeo (lo fue en el clip de
  prueba). Aquí no se pueden medir los ojos: abre `work/freeze_pick.jpg` cada vez. "held frame is soft" = aviso de
  desenfoque de movimiento: prueba un cuadro vecino u otra palabra. Con lentes, revisa también los reflejos.
- Las imágenes congeladas son VIDEOS hechos de los propios píxeles YUV de la toma, con sus etiquetas de color del lado
  de entrada de ffmpeg. Una imagen fija PNG o JPG, o etiquetas dadas como opciones de salida, corren el color 3 a 4
  niveles en el congelado y al soltar. No las cambies por imágenes fijas.
- Una etiqueta en la propia palabra del congelado no puede empezar antes del congelado: se lee unos 8 cuadros después
  del golpe. Las etiquetas siguientes se abren en su palabra.
- Que no haya espacio es un resultado, no un error: saca una etiqueta, acorta el texto o baja `ZOOM`. `!! over the body`
  = no hay fondo libre, mira primero el plan.
- Un `head` / `shoulder` / `hand` sin lado toma el lado con más espacio; un punto `_left` siempre lleva su etiqueta a la
  izquierda, así ninguna línea cruza la cabeza.
- Los anchos de etiqueta en el plan son estimaciones (5% más anchos). La etiqueta real se ajusta a su texto y queda
  fijada por el lado donde llega su línea.
- Los inicios de palabra de Whisper se ajustan al audio, precisos a unos 3 cuadros. Si congela antes o después en el
  render: pasa un número de cuadro.
- En pantalla: solo las palabras de la persona, sin nombres ni números inventados, sin guiones largos, sin naranjo. Los
  sonidos son los tres de stock a 0,75x.
