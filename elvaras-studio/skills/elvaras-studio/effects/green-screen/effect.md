# green-screen (Pantalla Verde)

**Qué hace:** la persona se recorta y se achica abajo del cuadro (a la izquierda, a la derecha o al centro) y todo el
cuadro detrás pasa a ser aquello de lo que habla: un video, una imagen, o una captura mostrada como tarjeta redondeada
sobre un fondo liso. El look de "reaccionar a algo".
**Función:** explicar / prueba (el espectador ve el tema a pantalla completa mientras la persona sigue hablando encima).
**Frases que lo activan:** "ponme delante de este clip", "ponme en pantalla verde sobre este video", "muestra esto
detrás de mí mientras hablo de eso".

## Primer paso: el fondo es material propio del usuario
Pídele los archivos y cópialos a `bg/` en el espacio: video (mp4 / mov / webm) o imagen (png / jpg), al menos uno. El
efecto no trae material. Sin material = sin Pantalla Verde: `prep.py` y `build.py` se detienen con un mensaje, deja
fuera el efecto. Sus propios reels editados sirven como fondo.
Cuando el fondo es material de otra persona, pon `credit` con su usuario (`'@nombre'`): una cápsula lo muestra arriba a
la izquierda. Nunca inventes un usuario. Solo material que el usuario puede mostrar.

## Toma que necesita
- **Plano:** medio es lo mejor (cabeza, hombros y pecho en cuadro). Abierto funciona: la persona se agranda al mismo
  tamaño de cabeza, y sobre 1,3x el recorte queda blando (`prep.py` avisa). Cercano falla cuando se ve menos de una
  altura de cabeza de cuerpo bajo la barbilla: el armado se detiene con "too tight".
- **Cámara:** quieta, con deriva o en movimiento. El cuarto desaparece mientras el efecto está arriba, así que el
  movimiento de cámara no se ve; una persona que cruza el cuadro también cruza el fondo.
- **Pared:** no hace falta.
- **Recorte:** como capa y medido. `assets/subject.webm` es la persona en pantalla, y lo alto de la cabeza, la barbilla,
  el ancho de la cabeza y la fila donde se corta el cuerpo (borde del escritorio, mesa, borde inferior del cuadro) se
  leen de su alfa. `aroll_hi` no se usa.
- **Lo rompe:** un recorte que pierde pelo o manos rápidas (el fondo nuevo muestra cada falla), un cuerpo que toca el
  borde izquierdo Y el derecho del cuadro (se ven bordes rectos), dos personas en la toma, espacios de menos de 36
  cuadros entre entrada y salida, un fondo con subtítulos propios quemados a la altura de la cabeza, una silla oscura
  que el recorte mezcla con la ropa (se ve un pedazo de silla sobre el fondo).
- **Bordes:** el cuadro 0 y el último son el clip sin tocar (se achica desde `IN_FRAME`, vuelve a crecer en
  `OUT_FRAME`), así que el espacio cae sobre la toma en cualquier parte. Excepción: `HARD_IN` / `HARD_OUT` abren o
  terminan el espacio EN la pantalla verde, para un espacio que empieza o termina en un corte del reel.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `BG_DIR`, `BG` | la carpeta, y un diccionario por cada elemento de fondo | `[]` = cada archivo en orden de nombre, repartidos parejo. Claves: `file`, `at`, `start`, `mode`, `side`, `size`, `reframe`, `focus`, `credit` |
| `BG[..]['at']` | cuadro o palabra dicha en que un elemento posterior entra con corte seco | `prep.py words`; `'esto#2'` = la segunda vez que se dice la palabra |
| `BG[..]['mode']` | `'fill'` (cubre el cuadro) o `'card'` (tarjeta redondeada sobre el fondo liso) | `'auto'`: el material vertical llena, el material ancho (capturas) pasa a tarjeta |
| `BG[..]['reframe']`, `['focus']`, `['start']` | `(escala, x, y)` desplazamiento de un elemento que llena; qué parte sobrevive al recorte 9:16; primer segundo de un video | mira `work/layout.jpg`: el tema no debe quedar detrás de la persona |
| `IN_FRAME`, `OUT_FRAME` | cuadro o palabra en que empieza el efecto / en que vuelve la imagen simple | por defecto 2 y `None` (2 cuadros antes del final) |
| `HARD_IN`, `HARD_OUT` | sin achicarse al entrar / sin crecer al volver | solo donde el propio reel corta |
| `SIDE`, `SIZE` | `'left'`, `'center'`, `'right'`, `'far-left'`, `'far-right'` o una x; `'normal'`, `'small'`, `'big'` | el lado donde NO está el tema del fondo; `'small'` le da más espacio |
| `CREDIT`, `WALLPAPER` | cápsula de usuario (por defecto `''` = apagada); fondo CSS detrás de una tarjeta | oscuro neutro por defecto (bosque de marca sirve) |
| `CAPS`, `CAP_KEY`, `CAP_FIX`, `CAP_WORDS`, `CAP_PLATE` | las palabras de subtítulo propias del efecto. SOLO para un reel sin estilo de subtítulos propio: en un reel el espacio se arma con `CAPTIONS=0` y los subtítulos del reel llevan las palabras | `'auto'` = las palabras de la persona desde words.json; corrige lo mal escuchado en `CAP_FIX`; palabras en dorado en `CAP_KEY` |
| `BODY_BOTTOM`, `FACE` | fila de corte del cuerpo a mano / caja de la cabeza en el cuadro de origen | `None` = medido; ponlos solo cuando `work/layout.jpg` los muestra mal |
| `TRANS`, `PUSH`, `SHADOW`, `GRADE`, `VOICE`, `SOUNDS` | duración de achicarse, acercamiento, sombra de la persona, filtro CSS en el recorte, audio de la persona, sonidos | por defecto; deja `GRADE='none'` |

**Interruptores:** `SAFE=1` guía de zona segura (solo instantáneas), `CAPTIONS=0` sin palabras de subtítulo propias
(SIEMPRE en un reel que tiene estilo de subtítulos: gana el estilo del usuario), `SFX=0` sin sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: pregúntale al usuario qué va detrás de él: su propio clip o imagen de aquello de lo que habla (cópialo a <slot>/bg/). Cuando es material de otra persona, pide su usuario y ponlo en credit; nunca inventes un usuario. Sin material del usuario = sin Pantalla Verde: déjalo fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" prep.py words      # copia los archivos del usuario a ./bg; 1. cada palabra con su cuadro -> edita el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. mide el recorte, corta los archivos de fondo, work/layout.json + work/layout.jpg (MÍRALO)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # 3. página con la guía; imprime cajas, el valor --caption-y, tiempos de instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos que imprimió build.py>
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # 4. guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 5. cantidad de cuadros, bordes simples, cuadros de corte, filas de cara / cuerpo, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Después de CUALQUIER cambio en el bloque CLIP ejecuta `prep.py` de nuevo antes de `build.py` (build.py rechaza una
composición vieja). Un espacio de 5 s toma unos 6 minutos después del recorte.

## Cuando el reel pone los subtítulos del espacio (CAPTIONS=0, el caso normal)
Gana el estilo del usuario: en un reel que tiene estilo de subtítulos el espacio se arma con `CAPTIONS=0` y los
subtítulos propios del reel se quedan, en el estilo del usuario. `build.py` imprime entonces `fx_add.py --caption-y
N`: agrega el espacio con eso y los subtítulos del reel suben a la línea sobre la cabeza de la persona mientras dura
el espacio (el cambio ocurre en un cambio de subtítulo, nunca a mitad de uno). Mira una instantánea del reel dentro del
espacio: un estilo de subtítulos alto puede necesitar `SIZE = 'small'` para tener más espacio sobre la cabeza. Las
palabras propias del efecto (`CAPS`, minúsculas) son solo para un reel sin subtítulos propios (estilo `none`): arma sin
`CAPTIONS=0` y agrega el espacio con `--captions hide`.

Los subtítulos normales del reel a la altura del pecho caerían sobre la cara de la persona achicada. `build.py`
imprime, y `work/layout.json` guarda por elemento, dónde pueden ir las palabras: `cap_top` .. `cap_bottom` (una línea
de 76 px, 42 px sobre la cabeza), dentro de `cap_box` (rango de x), nunca más abajo. `face` y `box` son la cara y el
cuerpo de la persona en el lienzo.

## Qué mirar (work/check/sheet.jpg)
- Primer y último cuadro, el cuadro antes de `IN_FRAME` y el cuadro de `OUT_FRAME`: el clip simple (check.py imprime la
  diferencia).
- Toda la cara sobre la línea roja (y 1470). Ningún borde recto de corte del cuerpo sobre el borde inferior del lienzo
  una vez terminado el achicarse.
- El tema del fondo no queda detrás de la persona; cada corte cae en su cuadro; una tarjeta termina sobre la línea de
  subtítulos.
- Palabras de subtítulo nunca sobre la cara; sobre un fondo claro van sobre una placa oscura. Cápsula de crédito
  presente cuando el material no es del usuario.

## Trampas
- Los primeros uno o dos cuadros del achicarse muestran el borde de corte del cuerpo (la persona todavía está casi a
  tamaño completo): normal, desaparece en el cuadro 3.
- La barbilla medida es la línea del cuello más el movimiento de la cabeza, así que la caja de la cara va un poco baja a
  propósito. Una capucha, pelo largo o una mano en la cara esconden el cuello: `prep.py` lo dice, entonces pon `FACE`.
- Un escritorio que corta el cuerpo en diagonal: se usa el punto más alto del corte. Si todavía se ve una cuña, baja
  `BODY_BOTTOM` 20 px.
- Un video más corto que su tiempo en pantalla mantiene su último cuadro (prep avisa). Un video de celular en HDR como
  fondo puede verse deslavado: expórtalo primero en SDR.
- Whisper escucha mal nombres y números: lee una vez las líneas automáticas de subtítulo, corrígelas en `CAP_FIX`, o
  escribe `CAPS` a mano.
- Palabras en pantalla: las de la persona, sin guiones largos, sin números, nombres ni usuarios inventados. El fondo
  liso queda neutro: sin colores de marca de un producto real.
- Sonidos: solo `whoosh-short` de stock, a 0,75x del volumen de la plantilla (al entrar, en cada corte, al salir).
