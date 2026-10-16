# spotlight (Foco)

**Qué hace:** en una palabra clave el cuarto se oscurece y desenfoca, la persona queda iluminada y nítida en un círculo
de luz, las palabras clave caen grandes (la primera escondida detrás de la cabeza, la siguiente adelante sobre el
pecho), y luego las luces vuelven a subir.
**Función:** explicar (una frase que tiene que pegar, con una entrada y una salida claras).
**Frases que lo activan:** "ponme un foco cuando digo X", "apaga las luces en esta palabra", "luces abajo en X, arriba
en Y".

## Toma que necesita
- **Plano:** abierto, medio o cercano, UNA toma continua de una persona, 3 a 6 s. Mejor en un plano abierto o medio con
  pared sobre y al lado de la cabeza (el cuarto oscuro es lo que lo vende). En un plano cercano igual funciona: el
  círculo se cierra a un resplandor alrededor de la cabeza.
- **Cámara:** quieta, con deriva o en mano funcionan. El cuarto oscuro se hace desde la imagen en vivo cuadro a cuadro (la
  persona se borra de cada cuadro antes del desenfoque) y el círculo de luz sigue a la cabeza medida. Nada es una imagen
  fija.
- **Pared:** no hace falta. Algo de fondo sobre o al lado de la cabeza le da un lugar a la primera palabra.
- **Recorte:** como capa (`assets/subject.webm` se limpia para un cuarto oscuro y se dibuja encima) y medido (cabeza,
  cuello, espacio libre).
- **Qué lo rompe:** un recorte que pierde pelo, dedos o un objeto (la parte perdida se oscurece con el cuarto) o conserva
  un pedazo de fondo (queda iluminado: `GAP`, `FLECKS`, o elige otro tramo; una silla oscura mezclada con la ropa es
  este caso); una mano levantada sobre la cabeza o dos personas (la cabeza se toma como lo más alto del recorte); una
  capucha o pelo largo sobre los hombros (no hay cuello que encontrar, revisa la caja verde); una cabeza que llena el
  cuadro (sin espacio para palabras: `CAPTIONS=0` o deja fuera el efecto); una persona que se mueve mucho (las palabras
  quedan fijas en pantalla, así que la cabeza se desliza contra la palabra que tiene detrás).

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy, scipy, Pillow para `prep.py` y `check.py`; numpy
para `onsets.py`; `build.py` no necesita nada (Pillow si está, para anchos exactos de palabra).

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `F_IN` | primer cuadro en que se mueven las luces | `onsets.py`: inicio de la primera palabra clave menos 1. 3 o más |
| `F_OUT` | primer cuadro en que vuelven las luces, o `None` | inicio de la primera palabra dicha en el cuarto normal; 17+ después de `F_IN`, 14+ antes del último cuadro. `None` = oscuro hasta el último cuadro: el espacio debe TERMINAR EN UN CORTE |
| `KEYWORDS` | `(texto, cuadro, lugar, tamaño, color)` por palabra, solo palabras que dice la persona | cuadro = inicio de la palabra. lugar `'auto'` (la primera palabra `'above'`, el resto `'chest'`), `'above'`, `'left'`, `'right'`, `'chest'`, o `('back' o 'front', x central, y de la base)`. tamaño `'auto'` o px. Escribe el texto en las mayúsculas o minúsculas del estilo; color crema o dorado |
| `DARK` | qué tan oscuro queda el cuarto fuera del círculo | 0,16; 0,10 casi de noche, 0,30 atenuado. Mantiene su color, nunca gris |
| `BLUR` | px de desenfoque del cuarto | 11 |
| `POOL` | tamaño del círculo de luz | 1 = medido desde la cabeza; 0,8 = más cerrado, cuarto más oscuro |
| `EDGE_CHOKE` | px que se mete el borde del recorte | 1,5. Halo claro en `work/check_edge.jpg`: 2,5. Pelo fino comido: 0,8 |
| `EDGE_SPILL` | px del borde exterior recoloreados desde adentro | 4. Línea clara alrededor de la persona: 6. 0 = apagado |
| `PUSH` | acercamiento lento mientras las luces están abajo | 1,045; 1 = nada |
| `GAP` | polígono de fondo que conservó el recorte (entre las piernas) | solo cámara quieta; lee los puntos en un cuadro. `None` = apagado |
| `FLECKS` | `(primer cuadro, último cuadro, (x0, y0, x1, y1))`: punto brillante que asoma por un hoyo en la persona | solo si aparece uno en las imágenes de revisión. `[]` = apagado |
| `GRADE`, `SOUNDS` | filtro css sobre todo el espacio (`''` = apagado, por defecto); sonidos sí / no | por defecto |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las palabras clave
(solo luces; los subtítulos propios del reel llevan las palabras). `SFX=0` saca los sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. imprime los inicios de palabra como cuadros
# editar: el bloque CLIP en build.py: F_IN, F_OUT, KEYWORDS
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. mide y hornea (1 a 3 min). MIRA work/check_edge.jpg (tamaño completo) y work/check_sheet.jpg
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 3. ubica las palabras e imprime cada caja de tinta. Se detiene si una palabra queda sobre la cara o fuera de la zona segura
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.0,2.4,2.7,3.4,3.7      # tus propios tiempos: antes de F_IN, ambas palabras puestas, mitad de la pausa, mitad del regreso, después
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 4. la página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 5. cantidad de cuadros y cuadros simples en ambos extremos, escribe work/final_sheet.jpg y work/final_edge.jpg
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar en los cuadros finales
- `work/check_edge.jpg` y `work/final_edge.jpg` a tamaño completo, momento más oscuro: alrededor de la cabeza y el pelo
  sin halo claro ni línea pálida; la mano tiene todos sus dedos; nada de la persona queda oscuro y nada del cuarto
  queda iluminado dentro de la silueta.
- El cuadro 0, el cuadro antes de `F_IN`, y (con `F_OUT`) desde 8 cuadros después de `F_OUT` hasta el último: imagen
  simple, `check.py` dice ok. Sin atenuación ni acercamiento que quede puesto.
- Cuadro más oscuro: el cuarto es azul oscuro y suave pero conserva color, la persona está a todo color, la piel no
  está roja ni quemada. Sin grano.
- Cada palabra clave aparece en su palabra, es una que dice la persona, nunca tapa la cara, y con `SAFE=1` queda dentro
  de la zona segura (arriba 220, nada bajo 1470, lados 35, derecha 100 desde y 1155).
- El render tiene exactamente los `frames` de `clip.json` y el audio de la persona.

## Trampas
- `prep.py` hornea `F_IN`, `F_OUT`, `DARK`, `BLUR`, `POOL`, los campos de borde, `GAP` y `FLECKS` en los dos videos: si
  cambias uno, `build.py` se niega a correr hasta que `prep.py` corra de nuevo. `KEYWORDS`, `PUSH`, `GRADE` y `SOUNDS`
  solo necesitan `build.py`.
- Una copia desenfocada de la imagen todavía contiene a la persona y brilla alrededor del recorte nítido. Por eso el
  cuarto se borra cuadro a cuadro; nunca cambies `room_dark.mp4` por un desenfoque css sobre la toma.
- El recorte se enciende de golpe en el primer cuadro en movimiento y se disuelve en los últimos 3 cuadros del regreso;
  la luz en sí se hornea por cuadro. Un fundido de entrada del recorte hace bombear el brillo de la persona.
- Una animación que empieza en el cuadro n todavía muestra su valor inicial en el cuadro n: `build.py` empieza todo un
  cuadro antes, así que el `frame` de una palabra clave es el primer cuadro en que se ve.
- La palabra detrás de la cabeza se esconde solo un poco cuando la cabeza se mueve mucho. Si la cabeza tapa demasiado,
  dala a mano: `('back', x, y de la base)` un poco más arriba, o `'left'` / `'right'`.
- Las palabras `'chest'` van delante de la persona y tapan una mano que gesticula ahí. Plano abierto: la palabra queda
  sobre el regazo. Plano cercano: a un tercio del pecho hacia abajo.
- `GAP` es un polígono fijo: con una cámara en movimiento déjalo en `None` y elige un tramo donde el recorte esté limpio.
- Sonidos: `assets_fx/impact-bass-short.mp3` cuando caen las luces, `whoosh-short` de stock cuando vuelven, ambos a
  0,75x y bajo la voz.
