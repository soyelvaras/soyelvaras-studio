# the-stack ("La Pila")

**Qué hace:** la imagen baja de golpe a una ventana redondeada en la parte inferior de una página clara punteada y
tarjetas de datos se apilan sobre la persona: cada tarjeta cae en una palabra y empuja la ventana de la persona hacia
abajo, sus barras compiten con números que cuentan, y la barra ganadora llega en la palabra que elijas. Luego la
ventana vuelve a crecer a cuadro completo.
**Función:** explicar (comparar unas pocas cifras mientras la persona habla: costos, horas, resultados, antes y
después).
**Frases que lo activan:** "haz la composición de tarjetas de datos en esta frase", "apila los números sobre mí", "la
pila".

## Primer paso: las cifras son del usuario
Cada título, etiqueta, valor y unidad en `CARDS` sale de lo que se dice en el clip o de cifras que te da el usuario.
Pídeselas si la frase no las tiene. Nunca inventes, estimes ni redondees hacia arriba un número, un nombre, una
herramienta o un ranking: la fila ganadora es la que los números del usuario hacen ganadora. Sin cifras del usuario =
deja fuera este efecto. El paquete trae un relleno y `build.py` se detiene hasta que se reemplace.

## Toma que necesita, y dónde falla
- Plano: abierto, medio o cercano. Cámara: quieta, con deriva o en mano. Pared: no hace falta. Una persona con cabeza y
  hombros en cuadro, una toma continua, 3 a 6 s, al menos 1,5 s entre `F_IN` y `F_OUT`.
- Recorte: solo se mide, nunca como capa. `measure.py` lee el alfa de `assets/subject.webm` para encontrar la cabeza, así
  que el recorte de la ventana centra la cara con un poco de espacio arriba. Con `HEAD` escrito a mano el espacio no
  necesita recorte (`fx_new.py --no-cutout`). `aroll_hi`: no. Python: numpy, Pillow.
- Qué lo rompe: una selfie muy justa (la imagen no puede achicarse bajo el ancho de la ventana, así que la cabeza queda
  grande y la pila cabe unas 5 filas en total: `build.py` se detiene y dice cuántos px sacar); un plano abierto lejano
  (se agranda más de 2x, blando); manos sobre la cabeza, una capucha o dos personas (la caja de la cabeza queda mal:
  revisa `work/head.jpg`, escribe `HEAD`); una persona que sale del cuadro; una toma con un corte. Una persona en mano o
  que se balancea está bien: la ventana sigue su cabeza (`FOLLOW`).
- Subtítulos: la composición reemplaza todo el cuadro, así que el efecto dibuja sus propias palabras de subtítulo
  (`CAPS`) sobre el pecho dentro de la ventana. Con `CAPTIONS=0` esa franja queda vacía y `build.py` la imprime
  (`caption band: y .. to ..`): ahí va el subtítulo del reel para esos cuadros, en cualquier otro lugar cae sobre las
  tarjetas.
- Bordes: cada cuadro antes de `F_IN - 8` y desde `F_OUT` en adelante es la imagen sin tocar. `F_OUT = None` mantiene la
  composición hasta el último cuadro: el reel tiene que cortar en ese cuadro.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `TITLE` | línea en negrita sobre las tarjetas | las palabras del usuario, menos de 30 caracteres; `''` = ninguna |
| `CARDS[].title`, `sub` | encabezado de la tarjeta, línea gris pequeña bajo él | lo que se compara; la fuente o la unidad en palabras |
| `CARDS[].rows` | `(etiqueta, valor)`, 1 a 5 por tarjeta, 1 a 3 tarjetas | las cifras del usuario; un texto se muestra tal como está escrito (`'12.400'`) |
| `unit`, `full` | texto antes / después de cada valor; el valor de una barra llena | `('$', '')`, `('', '%')`; `full=100` para porcentajes |
| `win` | fila que toma el acento y llega al final | lo que dicen los números; `None` = todas las barras con acento, sin ganadora |
| `at`, `race`, `win_at` | cuadros: tarjeta llegada, barras empiezan, ganadora llega | `onsets.py`; la primera tarjeta siempre cae en `F_IN` |
| `F_IN`, `F_OUT` | cuadros: composición llegada, imagen simple de vuelta | `onsets.py`; `F_IN` 8 o más; `F_OUT` hasta frames - 1, o `None` |
| `CAPS` | palabras de subtítulo `(cuadro, 'PALABRAS')` o `(cuadro, 'PALABRA', 'acc')` | palabras que dice la persona, 22 caracteres o menos, cuadros de `onsets.py` |
| `ACCENT` | el único color (barra ganadora, número, marca, brillo, palabra de golpe) | el hex de marca del usuario (dorado #C9A15B); nunca naranjo |
| `HEAD`, `FOLLOW` | caja de cabeza escrita `(top, centre_x, width)`; la ventana sigue la cabeza | `None` = medido; lee los px en `work/head.jpg` (a la mitad del tamaño). `FOLLOW = False` = un recorte fijo |
| `ZOOM`, `HEADROOM` | tamaño de la persona en la ventana, px de imagen sobre la cabeza | 1,0 y 40 |
| `CAP_Y`, `SOUNDS` | parte superior de la franja de subtítulos; sonidos | `None` = justo bajo la barbilla; `'auto'` o una lista de sonidos de stock |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura y la franja de subtítulos (solo instantáneas). `CAPTIONS=0`
saca las palabras de subtítulo del efecto. `SFX=0` saca sus sonidos. `GRADE=1` pone un color suave en la imagen durante
todo el espacio, bordes incluidos: solo cuando el reel lleva el mismo color (apagado por defecto).

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: consigue las cifras del usuario: cada título, etiqueta, valor y unidad en CARDS sale de lo que se dice en el clip o de cifras que da el usuario. Nunca inventes, estimes ni redondees hacia arriba un número, un nombre, una herramienta o un ranking. Sin cifras del usuario = sin La Pila: déjalo fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. inicios de palabra como cuadros -> F_IN, F_OUT, at, win_at, CAPS en build.py
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # 2. cabeza desde el alfa del recorte -> work/head.json; MIRA work/head.jpg
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # 3. página con la guía de seguridad; lee lo que imprime
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.5,1.0,1.5,2.0,3.0,4.0
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Elige los tiempos de instantánea desde tus propios cuadros (cuadro / 30): justo después de `F_IN`, después del `at` de
cada tarjeta, cada `win_at`, justo antes de `F_OUT - 8`. `build.py` no necesita paquetes; cualquier Python con numpy y
Pillow corre los otros dos.

## Qué mirar en los cuadros finales
- Cuadro `F_IN - 8` y cuadro `F_OUT`: la imagen simple, sin página, sin tarjeta, sin sombra. Cuadro `F_IN`: título y
  primera tarjeta llegados, la cabeza completa dentro de la ventana.
- Cada `at`: la tarjeta queda en su lugar y la ventana bajó bajo ella, nada se solapa. Cada `win_at` + 2: el número
  ganador muestra la cifra exacta escrita, marca puesta, las otras filas ya detenidas.
- Cada cifra en pantalla contra las del usuario: mismos dígitos, misma unidad, misma etiqueta. Ninguna fila que el
  usuario no dio.
- La cara: centrada en la ventana, pelo o gorro sin cortar por el borde superior de la ventana, barbilla sobre las
  palabras de subtítulo, subtítulo dentro de la franja punteada de la instantánea con `SAFE=1`.
- Zona segura: título y tarjetas entre y 220 y la ventana, dentro de x 90 a 990; palabras de subtítulo sobre y 1470. La
  ventana en sí es imagen y llega hasta el borde inferior del cuadro.
- El render tiene exactamente los `frames` de `clip.json` (revísalo con ffprobe).

## Trampas
- Cada encabezado de tarjeta cuesta unos 100 px y cada fila 48: tres tarjetas solo caben con 2 filas cada una.
  `build.py` se detiene con la cantidad de px que hay que sacar.
- La ventana sigue un seguimiento suavizado de lo alto de la cabeza, así que el cuarto detrás se mueve un poco mientras
  la persona queda quieta. Con `HEAD` escrito o `FOLLOW = False` el recorte queda fijo y usa el punto más alto que
  alcanza la cabeza.
- La barbilla se toma como 1,5 anchos de cabeza bajo lo alto de la cabeza (un cuello alto suele tapar el cuello). Si el
  subtítulo cae sobre una barba larga o una mano levantada, pon `CAP_Y` a mano desde la franja punteada de la
  instantánea con `SAFE=1`.
- Las barras se dibujan a escala contra el valor más grande (o `full`). Un valor bajo el 3% de ese es un muñón: eso es
  honesto, no lo estires.
- `win_at` después de que la composición se fue (más tarde que `F_OUT - 8`) deja a la ganadora todavía corriendo en el
  cierre: `build.py` avisa.
- Las etiquetas largas se cortan con puntos suspensivos cerca de los 25 caracteres; los valores largos achican las
  barras. Acorta la etiqueta, nunca la cifra.
- Los sonidos son de la plantilla a 0,75x de volumen: un whoosh al entrar, un pop por tarjeta, un destello en la última
  ganadora, un whoosh al volver.
