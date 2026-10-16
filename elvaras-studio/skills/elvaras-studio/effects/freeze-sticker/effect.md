# sticker (Sticker Congelado)

**Qué hace:** en una palabra la imagen se congela y la persona se convierte en un sticker recortado (borde blanco
alrededor de su silueta, sombra suave, leve inclinación) pegado sobre una página de color, con notas a mano escritas
alrededor. La voz sigue bajo el congelado.
**Función:** llamado a la acción (también un momento de remate). Los cuadros antes de `F_FREEZE` son la toma sin tocar.
**Por defecto `F_OUT = None`: el espacio TERMINA EN EL STICKER, así que el reel termina o corta ahí.** Con un cuadro en
`F_OUT` el sticker sale volando y la imagen en vivo vuelve exactamente desde ese cuadro (un corte seco).
**Frases que lo activan:** "conviérteme en un sticker en esta frase", "congélame en un sticker", "sticker congelado".

## No se muestra nada que el usuario no haya dado
Las notas son las PROPIAS palabras del usuario: pídeselas (una o dos, de 2 a 5 palabras cada una). Los valores por
defecto son de relleno. Nunca escribas un número, un resultado, un usuario o una palabra para comentar que la persona
no dice en este clip. Sin notas del usuario = ejecútalo con `NOTES = []` (solo el sticker).

## Toma que necesita
- **Plano:** medio o abierto es lo mejor (cabeza y pecho con aire alrededor). Un plano cercano funciona, con un sticker
  grande y espacio para una o dos notas cortas.
- **Cámara:** quieta, con deriva o en movimiento funcionan (se congela un cuadro; no se sigue nada).
- **Pared:** no hace falta.
- **Recorte:** como capa y medido: el sticker ES el recorte del cuadro congelado (`assets/subject.webm`), y su silueta
  ubica todo.
- **Qué lo rompe:** un cuadro congelado con desenfoque de movimiento, ojos cerrados o una mano cruzando la cara (elige
  otro cuadro); un recorte que perdió pelo, dedos o una manga en ese cuadro (borde abollado: `bake.py` imprime
  "ragged"); una persona cortada por AMBOS lados del cuadro (el sticker no puede ser más chico que la pantalla, las
  notas tienen poco espacio); una cabeza cortada por el borde superior (parte de arriba plana); dos personas (solo se
  conserva la más grande); un plano muy cercano donde la cabeza mide más de 760 px de alto en pantalla (sin espacio
  para notas). Una silla oscura que el recorte mezcla con la ropa queda dentro del sticker.

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy, scipy y Pillow para `bake.py`, numpy y Pillow para
`onsets.py` y `check.py`; `build.py` no necesita nada.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `F_FREEZE` | cuadro en que se congela la imagen | `onsets.py`, "onset" de la palabra; luego MIRA `work/frames.jpg` y muévelo 1 a 3 cuadros al mejor cuadro |
| `F_OUT` | `None` (por defecto, termina en el sticker) o el cuadro en que vuelve la imagen en vivo | inicio de una palabra posterior, 24+ después de `F_FREEZE`, 2+ antes del último cuadro |
| `NOTES` | lista de `(texto, cuadro, lado)` | las palabras del usuario; cuadro = inicio de la palabra en que aparece la nota, `None` = justo después del congelado; lado `'auto'`, `'top'`, `'left'`, `'right'`; `*estrellas*` alrededor de una palabra = color de acento y subrayado |
| `STAMP` | una palabra corta en un sello enmarcado sobre la primera nota | la palabra del usuario; `''` = apagado |
| `ARROW`, `TICKS` | flecha de la primera nota al cuerpo, tres rayitas junto a la cabeza | encendidos por defecto; la flecha se omite cuando no tiene un camino libre |
| `BACKDROP`, `PAGE` | `'page'` = página de color en `PAGE`; `'footage'` = la imagen congelada desenfocada y atenuada | un color que haga resaltar a la persona (bosque o crema de marca); nunca naranjo, nunca gris |
| `INK`, `ACCENT` | color de la letra a mano, color de las palabras con estrellas | crema y dorado |
| `SIZE`, `PLACE`, `TILT` | escala del sticker, ajuste en px, grados | `'auto'`; cámbialo solo después de mirar `work/check.jpg` |
| `BORDER`, `CHOKE` | px del borde en pantalla; px que se rebajan del borde del recorte | 20 y 2; `CHOKE` 3 o 4 si se ve un borde del cuarto |
| `CUT_Y` | corte recto a través del cuerpo en esta y de la toma: el sticker flota completo | `None` = el cuerpo sigue hacia abajo fuera de la pantalla |
| `HEAD` | `(top_y, chin_y)` en px de la toma | solo cuando la caja verde de `work/check.jpg` no está sobre la cabeza |
| `GRADE`, `SOUNDS` | filtro css en los cuadros en vivo (`''` = apagado, por defecto), sonidos sí/no | por defecto |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las notas, el sello,
la flecha y las rayitas (solo el sticker). `SFX=0` saca los sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. inicios de palabra como cuadros
# editar: pon el inicio de la palabra en F_FREEZE (y los cuadros de las notas, F_OUT) en el bloque CLIP de build.py
PY "SK/scripts/fx_run.py" "<slot>" bake.py frames      # 2. MIRA work/frames.jpg: ojos abiertos, sin desenfoque de movimiento, buena expresión. Este cuadro es todo el efecto: mueve F_FREEZE si no
PY "SK/scripts/fx_run.py" "<slot>" bake.py      # 3. hornea el sticker y ubica las notas (5 s). Lee sus avisos, MIRA work/check.jpg: borde completo, caja verde en la cabeza, notas fuera del sticker
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # página con la guía de seguridad
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.0,1.4,1.5,1.8,2.4      # tus propios tiempos: justo antes del congelado, el congelado, ya pegado, cada nota escrita
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar en los cuadros finales
- El cuadro 0 y el cuadro antes de `F_FREEZE`: imagen simple. Con `F_OUT`: ese cuadro y el último también (`check.py`
  lo imprime).
- `work/final_edge.jpg` a tamaño completo: el borde blanco corre sin cortes alrededor del pelo, las orejas y los dedos,
  sin borde del cuarto adentro, sin abolladura donde el recorte perdió algo.
- Notas: legibles, escritas en su palabra, nunca sobre el sticker, nunca una sobre otra, dentro de la zona segura
  (arriba 220, nada bajo 1470, lados 35, derecha 100 desde y 1155). El cuerpo puede pasar bajo 1470, el texto no.
- Ningún borde recto de corte del cuerpo visible abajo o a los lados de la pantalla mientras el sticker está quieto.
- El render tiene exactamente los `frames` de `clip.json` y el audio de la persona (revísalo con ffprobe).

## Trampas
- Cualquier cambio en el bloque CLIP (incluso la redacción de una nota) necesita `bake.py` de nuevo: `build.py` se niega
  a correr hasta entonces.
- El tamaño se mide, no se escribe: una persona cortada por el cuadro en ambos lados obliga a un tamaño de 1,0 o más.
  `CUT_Y` sobre el punto donde los hombros salen del cuadro lo libera (sticker de cabeza y cuello que flota).
- Una mano levantada sobre la cabeza, una capucha o pelo largo pueden engañar al buscador de cabeza (caja verde): pon
  `HEAD`.
- Las partes del recorte que no están unidas al cuerpo en el cuadro congelado (una mano en el aire) quedan fuera, y
  `bake.py` lo dice.
- Con `F_OUT`, el sticker sale volando por arriba en 6 cuadros; un cuerpo que sigue fuera de la pantalla hacia abajo
  muestra su borde recto de corte en esos cuadros (desenfocado, a propósito).
- `GRADE` queda puesto en cada cuadro en vivo, incluidos los simples: déjalo apagado salvo que el reel tenga el mismo
  color. Los sonidos son los de la plantilla a 0,75x de volumen, bajo la voz.
