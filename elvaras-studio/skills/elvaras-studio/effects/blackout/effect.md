# blackout (Apagón)

**Qué hace:** el clip empieza con su look normal, el cuarto se atenúa durante una frase mientras la persona sigue
iluminada, la palabra de golpe cae detrás de la cabeza con un destello y un pequeño golpe de cámara, y las luces
vuelven de golpe en el corte siguiente (o en la frase siguiente).
**Función:** gancho (una frase que construye hasta una palabra, y luego un reinicio seco hacia la toma siguiente).
**Frases que lo activan:** "baja las luces cuando digo X y súbelas en la frase siguiente", "apaga el cuarto y pon X
detrás de mi cabeza", "luces abajo en esta frase, que vuelvan en el corte".
**Apagón o Foco:** Apagón solo atenúa el cuarto (nítido, a la mitad del brillo), hace caer UNA palabra con destello y
golpe, y devuelve las luces de golpe: elígelo para una palabra de golpe que lleva a un corte. Foco lleva el cuarto
casi a negro y desenfocado bajo un círculo de luz, hace caer hasta tres palabras y vuelve suave: elígelo para una
frase dentro de una toma continua.

## Toma que necesita
- **Plano:** abierto, medio o cercano, una persona, 3 a 6 s: una frase de 1 a 3 s que termina en la palabra de golpe,
  luego la frase siguiente o la toma siguiente. Mejor abierto o medio con espacio sobre la cabeza. En un plano cercano
  la palabra queda justo sobre la cabeza.
- **Cámara:** quieta, con deriva o en mano funcionan. El cuarto es la imagen en vivo con un filtro y la persona es el
  recorte en vivo, nada es una imagen fija. La palabra queda fija en pantalla.
- **Pared:** no hace falta. Unos 240 px de imagen entre el borde seguro superior (y 220) y lo alto de la cabeza le dan
  su lugar a la palabra.
- **Recorte:** como capa (dibujado iluminado sobre el cuarto atenuado, borde limpiado por `prep.py`) y medido (cabeza,
  cuello, cuarto libre).
- **Qué lo rompe:** un recorte que conserva fondo al lado de la cabeza o entre el brazo y el cuerpo (queda iluminado:
  elige otro tramo) o pierde pelo o dedos (se oscurecen con el cuarto); una mano sobre la cabeza o dos personas (la
  cabeza es lo más alto del recorte); una cabeza que llega al borde seguro superior (sin espacio: `WORD_PLACE`
  `'left'` / `'right'` / `'chest'`, o `CAPTIONS=0`); un cuarto que ya es oscuro (nada que atenuar); una frase de menos
  de 0,5 s antes del golpe.

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy, scipy, Pillow (`prep.py`, `check.py`, y `build.py`
para medir la palabra); numpy para `onsets.py`.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `F_DIM` | primer cuadro en que el cuarto empieza a atenuarse | `onsets.py`: inicio de la primera palabra de la frase. 3 o más |
| `DIM_FRAMES` | cuadros que dura la atenuación | 24 (0,8 s). Más corto en una frase corta: abajo antes de `F_PUNCH` |
| `F_PUNCH`, `PUNCH` | cuadro en que se dice la palabra de golpe, y la palabra | su inicio; escrita como la dice la persona, solo una palabra que dice. `''` = sin palabra |
| `F_SNAP` | cuadro en que vuelven las luces | `'auto'` = el primer corte después de `F_PUNCH` en `clip.json`. Sin corte: inicio de la frase siguiente. 12+ cuadros después de `F_PUNCH`, 14+ antes del último cuadro. `None` = atenuado hasta el último cuadro: el espacio debe TERMINAR EN UN CORTE |
| `DIM`, `COOL`, `EDGE_DARK` | brillo del cuarto, cuánto se enfría, oscuridad desde los bordes y el piso | 0.46, 1, 1. `DIM` 0.30 más oscuro, 0.60 más claro; los otros 0 = apagado |
| `PUSH`, `KICK` | acercamiento lento hasta el golpe; golpe de cámara en él | 1.055 (1 = nada); 1 (0.5 más suave, 0 = nada) |
| `FLASH`, `FLASH_COLOUR`, `SNAP_FLASH`, `SNAP_COLOUR` | el destello del golpe y el de cuando vuelven las luces | 0.28 blanco cálido, 0.5 blanco. 0 = nada |
| `EDGE_CHOKE`, `EDGE_SPILL` | px que se mete el borde del recorte; px recoloreados desde adentro | 1.5 y 3. Borde claro en `work/check_edge.jpg`: 2.5. Pelo fino comido: 0.8 |
| `GRADE`, `SOUNDS` | filtro css sobre todo el espacio (`''` = apagado, por defecto); sonidos sí / no | por defecto |

## Bloque WORD STYLE (justo bajo el bloque CLIP)
La palabra de golpe repite una palabra que dice la persona; es el centro del look, pero el efecto funciona sin ella.
**Gana el estilo del reel:** cuando el reel tiene un estilo de subtítulos o un estilo completo, copia en este bloque su
tipografía, mayúsculas, grosor y color, o arma con `CAPTIONS=0` y deja que los subtítulos del reel digan la palabra. Los
valores por defecto son solo para un reel sin estilo propio. Una tipografía ancha en mayúsculas achica una palabra larga
(13 letras quedaron en 74 px): cuando `build.py` dice "very small", elige una palabra de golpe más corta que diga la
persona, o arma con `CAPTIONS=0`.
`WORD_FONT` + `WORD_FONT_FILE` (una fuente en `assets/fonts`), `WORD_WEIGHT`, `WORD_ITALIC`, `WORD_CASE` (`'lower'`,
`'upper'`, `'title'`, `'as-typed'`), `WORD_TRACK`, `WORD_COLOUR`, `WORD_GLOW` (`'auto'`, un color, `''`), `WORD_PLACE`
(`'auto'`, `'behind'`, `'left'`, `'right'`, `'chest'`, o `('back' o 'front', x central, y de la base)`), `WORD_SIZE`
(`'auto'` o px).

**Interruptores:** `SAFE=1` dibuja la guía de zona segura y la caja de tinta medida de la palabra (solo instantáneas).
`CAPTIONS=0` apaga la palabra propia del efecto: el cuarto igual se atenúa, destella, golpea y vuelve, y los
subtítulos del reel llevan las palabras. `SFX=0` saca los sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. imprime los inicios de palabra como cuadros
# editar: el bloque CLIP en build.py: F_DIM, F_PUNCH, PUNCH, F_SNAP. Luego el bloque WORD STYLE debajo: el estilo propio del reel cuando tiene uno
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. mide a la persona, limpia el borde del recorte (cerca de 1 min). MIRA work/check_edge.jpg (tamaño completo) y work/check_sheet.jpg
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 3. ubica la palabra e imprime su caja de tinta. Se detiene si la palabra queda sobre la cara o fuera de la zona segura
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.4,2.52,2.72,3.35,3.39,3.75      # tus propios tiempos: antes de F_DIM, el cuadro del golpe, palabra asentada, último cuadro atenuado, el cuadro del regreso, después
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 4. la página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 5. cantidad de cuadros, cuadros simples en ambos extremos, cuánto se atenuó el cuarto; escribe work/final_sheet.jpg y work/final_edge.jpg
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar en los cuadros finales
- El cuadro 0, el cuadro antes de `F_DIM`, y desde 11 cuadros después de `F_SNAP` hasta el último cuadro: imagen
  simple, `check.py` dice ok. Sin atenuación ni acercamiento que quede puesto.
- La atenuación empieza en `F_DIM` y está abajo antes del golpe; el cuarto mantiene su color (atenuado y frío, nunca
  gris ni negro), la persona está a todo color.
- En `F_PUNCH` la palabra está en pantalla, grande y suave, con el destello; 6 cuadros después está nítida, detrás de
  la cabeza, dentro de la zona segura (arriba 220, nada bajo 1470, lados 35, derecha 100 desde y 1155). Nunca tapa la
  cara.
- El último cuadro atenuado es `F_SNAP` menos 1; en `F_SNAP` el cuarto está iluminado con el destello encima y la
  palabra se fue.
- `work/final_edge.jpg` a tamaño completo: sin borde claro alrededor de la cabeza y el pelo, nada de la persona
  atenuado, nada del cuarto iluminado.
- El render tiene exactamente los `frames` de `clip.json` y el audio de la persona.

## Trampas
- `prep.py` hornea `F_DIM`, `F_PUNCH`, `F_SNAP`, `EDGE_CHOKE` y `EDGE_SPILL`: si cambias uno, `build.py` se niega a
  correr hasta que `prep.py` corra de nuevo. Todo lo demás solo necesita `build.py`.
- Ejecuta `build.py` con el mismo Python que `prep.py`: mide la palabra con Pillow. Sin Pillow usa valores aproximados
  de tabla y lo dice.
- En el cuadro del golpe la palabra está a 1,9x y desenfocada durante 2 o 3 cuadros y puede pasarse de la zona segura:
  ese es el golpe. Se juzga donde se asienta.
- La palabra queda fija en pantalla. Una persona que se mueve mucho se desliza detrás de ella; la cabeza solo se mide
  mientras la palabra está arriba, así que elige el lugar mirando `work/check_sheet.jpg` si queda mal.
- Una primera instantánea puede mostrar la imagen gris (el video todavía no se decodificó). Juzga el cuarto en las
  siguientes y en el render.
- En un reel, crea el espacio CRUZANDO el corte: desde antes de la frase hasta unos 0,5 s dentro de la toma siguiente,
  para que el regreso y sus 11 cuadros de asentamiento caigan en la toma nueva y el espacio termine simple.
- Sonidos: `assets_fx/impact-bass-short.mp3` en el golpe, los de stock `click` y `whoosh-short` en el regreso, todos
  a 0,75x y bajo la voz.
