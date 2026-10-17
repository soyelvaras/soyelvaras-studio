# pointer-callout (Llamadas)

**Qué hace:** tarjetas de llamada que se quedan en su lugar, cada una unida a un punto de la persona (cabeza, hombro,
mano, pecho) por una línea delgada que se estira y se balancea con ella en cada cuadro.
**Función:** explicar (nombrar las 2 a 4 cosas que enumera la persona, una tarjeta por cosa, cada una cayendo en su
palabra).
**Frases que lo activan:** "pon tarjetas en estas tres cosas y únelas a mí con una línea que me siga", "etiqueta las
cosas que enumero y conéctalas a mí", "llamadas en esta frase".

## Toma que necesita
- **Plano:** abierto o medio es lo mejor (fondo libre al lado o sobre la persona). Cercano funciona con 1 o 2 tarjetas
  cortas unidas a `head_left` / `head_right`.
- **Cámara:** quieta, con deriva o en movimiento. Las tarjetas se quedan en su lugar en pantalla, el extremo de la línea
  sigue a la persona. Una cámara que se balancea fuerte hace que la cabeza barra el cuadro y deja menos espacio.
- **Pared:** al lado o arriba ayuda (las tarjetas van primero sobre fondo libre). Sin pared, van sobre el cuerpo, nunca
  sobre la cabeza.
- **Recorte:** solo se mide (silueta de la cabeza, dónde está el cuerpo, las manos). Nada se pone como capa sobre la
  imagen.
- **Mejor cuando** la persona se mueve o apunta: una mano que viaja hace que la línea la siga a la vista. Una persona
  quieta da un diagrama estático.
- **Qué lo rompe:** una selfie cercana con la cámara balanceándose (la cabeza llena la zona segura: build.py se detiene y
  dice cuántas tarjetas caben, a menudo 1 o 2), una capucha o pelo largo que tapa el cuello o una mano en la cabeza
  (track.py se detiene: sin silueta de cabeza), una segunda persona en el recorte, la persona que sale del cuadro.
  Manos: guantes, brazos descubiertos del mismo color hasta el hombro, o ropa color piel confunden al buscador de manos
  (usa cabeza / hombro / pecho).
- Cada tarjeta necesita 1 s en pantalla. El espacio empieza y termina en la imagen simple: las tarjetas entran en `IN_F`
  como pronto y todo se fue 6 cuadros antes del final.

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte: OBLIGATORIO), `words.json`, `clip.json`. Sin `aroll_hi`. Las
tipografías (Inter Tight 800) y `pop.mp3`, `click-soft.mp3` vienen de la plantilla. Python: solo numpy, scipy, Pillow.
El efecto no trae imágenes y no necesita ninguna del usuario: solo sus propias palabras para las tarjetas.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `CARDS[i].text` | las palabras de la tarjeta | el nombre propio que la persona le da a la cosa, 1 a 3 palabras (un texto largo achica todas las tarjetas: ninguna es más ancha que la mitad del cuadro). Nunca un número, resultado o afirmación que no dice |
| `say` | la palabra dicha en que cae la tarjeta | como la imprime track.py; `'esto#2'` = el segundo "esto". `''` = una tras otra desde `IN_F` |
| `anchor` | a qué se une la línea: `head`, `head_left`, `head_right`, `chest`, `shoulder_left`, `shoulder_right`, `hand_left`, `hand_right` (como se ve en pantalla) | track.py lista los que existen, cuánto viajan en px y si se quedan en la zona segura. Elige los que se mueven |
| `side` | dónde va la tarjeta: `'left'`, `'right'`, `'auto'` | `auto` = el lugar más libre cerca de su ancla |
| `icon`, `sub` | ícono (`check`, `image`, `script`, `launch`, `spark`, `none`) y el detalle pequeño bajo el texto (`lines`, `thumbs`, `progress`, `none`) | lo que le calce a la cosa; `none` para una tarjeta simple |
| `at`, `pos` | opcional: segundos (reemplaza `say`), `(left, top)` px para ubicar una tarjeta a mano | solo después de mirar la instantánea |
| `IN_F`, `OUT_F` | primer cuadro en que puede aparecer una tarjeta, cuadro en que todo se fue | 4, `None` (6 cuadros antes del final) |
| `DONE_SAY` | palabra opcional en que todos los puntos laten y las barras `progress` se completan | `''` = apagado |
| `SIZE`, `FLOOR` | tamaño de tarjeta (`'auto'` = lo más grande que permite el espacio libre) y el tamaño legible mínimo | déjalos; un número en `SIZE` solo para igualar otro espacio |
| `ACCENT`, `CREAM`, `INK` | línea / puntos / ícono, texto, tarjeta | colores de marca (dorado, crema, tinta), nunca naranjo |
| `GRADE` | filtro CSS sobre la imagen | `'none'` (el reel da el color) |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas). `SFX=0` sin sonidos de pop. `CAPTIONS=0` se acepta y no cambia nada
(el efecto no tiene palabras de subtítulo). `DEBUG=1` imprime por qué una tarjeta no encontró lugar.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" track.py      # mide la cabeza, los puntos de anclaje, el espacio libre y los inicios de palabra (cerca de 30 s); lee lo que imprime
# editar: el bloque CLIP en build.py, luego arma con la guía puesta; una línea que empieza con !! es un alto o un aviso que hay que atender
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 3.6,4.5      # instantánea 0,6 s después de que cae la última tarjeta y 0,5 s antes del final (segundos; build.py imprime los cuadros de llegada)
PY "SK/scripts/fx_run.py" "<slot>" build.py      # arma sin la guía, luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # números, hoja, recortes de fijación, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 5 s toma unos 4 minutos de punta a punta una vez que existe el recorte (track 25 s, armado 2 s, render
25 s).

## Qué mirar (work/check/)
- Números de check.py: la cantidad de cuadros coincide, cuadro 0 y último cuadro simples, 0 píxeles cambiados fuera de
  la zona segura y dentro de la cara, cada tarjeta vista por primera vez dentro de 3 cuadros de su palabra.
- `sheet.jpg`: ninguna tarjeta ni línea sobre la caja azul de la cabeza desde las cejas hacia abajo, nada pasado las
  líneas rojas, las tarjetas no se tocan, las líneas no se cruzan.
- `lock.jpg`: una fila por tarjeta. El punto queda en el mismo lugar de la persona en cada recorte. Un punto que deambula
  = seguimiento débil: cambia esa tarjeta a `head` o a un hombro.
- El texto se lee en tamaño celular (`renders/<slot>-phone.mp4`). build.py imprime la altura del texto en px: menos de
  40 es pequeño.

## Trampas
- Que no haya espacio es un resultado, no un error. "no room for 3 cards: 2 fit" significa saca una tarjeta, acorta el
  texto o une las líneas a `head_left` / `head_right`. No bajes `FLOOR` para meterlas.
- `!! over the body` en la línea de composición: no hay fondo libre, las tarjetas tapan ropa o manos. Mira la instantánea
  antes de renderizar.
- Las manos se encuentran por el color de piel tomado de la propia cara de la persona. Cuando una mano está escondida o
  bajo y 1470, la línea descansa en ese hombro y vuelve cuando vuelve la mano. Menos de 50% encontrada (track.py lo
  dice): mejor un hombro.
- Una mano que barre el cuerpo deja su tarjeta lejos: la línea se alarga y cruza el torso (nunca la cara). Si se ve
  desordenado, une esa tarjeta a un hombro.
- Los inicios de palabra de Whisper están 0,1 a 0,3 s corridos: `say` usa el inicio ajustado al audio (preciso a unos 3
  cuadros). Tarjeta adelantada o atrasada en el render: pon `at=` en segundos.
- Un punto que sale de la zona segura recibe un ajuste constante (nunca un límite por cuadro, eso despega el punto).
  Demasiado afuera = build.py se detiene y lista los puntos que están adentro.
- El recorrido de la línea se calcula por cuadro en Python: un dibujo con `stroke-dashoffset` pasa de oculto a completo
  en el motor de render. El punto va exactamente sobre el seguimiento, el resorte está solo en la curva: un punto
  atrasado se lee como mal seguimiento.
- Las instantáneas buscan de forma aproximada durante una entrada: juzga el tiempo de llegada en cuadros del render
  real.
- En pantalla: solo las palabras de la persona, sin nombres ni números inventados, sin guiones largos, sin naranjo.

## Versiones (`VARIANT` en el bloque CLIP)

El usuario la elige en el selector (puntitos bajo la tarjeta); `fx_new.py` la escribe sola en el espacio. Las tres usan
el mismo seguimiento, las mismas líneas y el mismo reparto del espacio.

1. **Tarjetas**: tarjetas oscuras con ícono y líneas doradas (el original).
2. **Etiquetas de museo**: rótulos crema numerados (01, 02...), texto en Instrument Serif cursiva, línea crema fina y
   punto dorado. Sin ícono ni detalle (`icon` y `sub` se ignoran).
3. **Notas a mano**: sin tarjeta, palabras en Caveat crema con un subrayado dorado y una flecha dibujada que apunta al
   cuerpo.

En 2 y 3, `ACCENT_WORD` (por defecto 'Claude') va en el color de acento.
