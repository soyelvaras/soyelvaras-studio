# clone (Clon)

**Qué hace:** copias de la persona aparecen desde detrás del mueble, una por cada golpe dicho, cada una unas décimas
de segundo atrasada respecto de la persona (un canon). Remate opcional: todas se sincronizan con la persona en una
palabra. Salida opcional: vuelven a bajar.
**Función:** gancho. También una lista dicha ("esto, esto, o aquello").
**Frases que lo activan:** "clóname cuando digo así, así" / "pon dos más de mí detrás del sillón en estas palabras" /
"multiplícame en esta frase".

## Toma que necesita, y dónde falla
- **Cámara quieta** (trípode, mesa, piso). Un avance lento de gimbal se sigue y se elimina (hasta ~40 px). Una toma en
  mano o caminando falla: los clones se deslizan en la pared.
- **Plano abierto con un mueble detrás o al lado de la persona** cuyo borde superior tenga pared encima: respaldo de
  sillón, cabecera de cama, mesón, escritorio. Los clones quedan DETRÁS de ese borde, que esconde sus piernas. Pared
  libre al lado de la cabeza, más o menos un ancho de cabeza por clon.
- **NO funciona en:** selfies cercanas en mano (la persona llena el cuadro, sin espacio, sin borde); tomas en sillón
  individual o banqueta donde el único mueble es el asiento bajo la persona (un clon al lado mostraría piernas sin
  nada donde pararse); una toma donde la persona está de pie de cuerpo entero en un piso abierto; una cámara que se
  mueve o hace zoom; una pared recargada u oscura justo detrás de los clones (igual se componen, pero la limpieza del
  desenfoque de movimiento solo conoce una pared lisa y clara).
- **No puede sentar una copia del mismo tamaño al lado de la persona.** Una persona sentada ocupa ~70% del ancho de un
  cuadro 9:16 con las manos abiertas: una copia de tamaño completo se corta en el borde y una copia achicada en el
  mismo asiento flota. No prometas "tres de mí en el sillón".
- Los gestos de la persona deciden la composición: la pose más ancha de todo el espacio fija qué tan cerca del borde
  puede estar un clon.

## Entradas del espacio
Recorte: **sí** (`assets/subject.webm`, hecho por `fx_new.py`). `aroll_hi`: no. `words.json`: lo usa `prep.py` para
los golpes de palabra.
Python: solo el Python de la skill (numpy, scipy, PIL). Sin OpenCV.

## Bloque CLIP (inicio de `build.py`)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `CLONES[].word_f` | cuadro en que cae la vocal de la palabra que lo activa | filas "HIT" de `work/onsets.txt`; compáralo con las barras de volumen |
| `CLONES[].x`, `.top` | x del centro de la cabeza del clon e y de lo alto de su cabeza, px | `work/prep/grid_*.jpg`: pared sin tinte rojo; top = lo alto de la cabeza de la persona + 60 a 120 |
| `CLONES[].scale` | tamaño respecto de la persona, 0,5 a 0,7 | el borde del mueble debe cruzar al clon entre el pecho y las caderas |
| `CLONES[].lag` | cuadros de atraso respecto de la persona (6 = 0,2 s) | distinto en cada clon |
| `SYNC_F` | cuadro del remate, o `None` | vocal de la palabra de remate |
| `EXIT_F` | cuadro en que los clones bajan, o `None` | espacio en un reel: ~14 cuadros antes del final; clip suelto: `None` |
| `OCCLUDER_LINE` | puntos aproximados del borde superior del mueble, a todo el ancho del cuadro | leídos de `grid_000.jpg`, ~10 px de precisión; sigue derecho a través de la persona |
| `LIGHT_FROM` | `'left'` / `'right'` | lado más iluminado de la cara de la persona |
| `CAP_X`, `CAPS`, `PUNCH` | palabras de subtítulo con cuadros, palabra grande de acento | franja del pecho, bajo la barbilla, sobre y 1470 |
| `ACCENT`, `VIGNETTE` | color de acento (dorado); viñeta (0 en un espacio de reel) | |

Interruptores: `SAFE=1` guía de zona segura (solo instantáneas), `CAPTIONS=0` sin palabras de subtítulo, `SFX=0` sin
sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 20 s: ancla de la cabeza, pose más ancha, golpes de palabra, cuadros con grilla en work/prep/
# editar: mira work/prep/grid_*.jpg y work/onsets.txt, llena el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" bake.py      # 2 a 4 min, pesado: fg.webm + clone_*.webm. Lee su informe (abajo)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.2,2.4,3.6
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, diferencia por cuadro contra la toma, hojas de cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Tiempos de instantánea: 0,15 s después de cada aparición, el remate, la salida. Si cambias `x`, `top`, `scale`, `lag`,
`SYNC_F` u `OCCLUDER_LINE` -> hornea de nuevo. Si cambias solo subtítulos, `word_f` en uno o dos cuadros, o `EXIT_F` ->
basta con `build.py` + render (hornea de nuevo si `word_f` se adelanta más de 1 o `EXIT_F` se atrasa más de 10).

## Leer el informe del horneado
- `camera drift`: unos pocos px es normal. Sobre 40 px avisa: toma equivocada.
- `occluder edge snapped on N of 1080 columns`: abre `work/bake_debug/occluder_overlay.jpg`, el área roja tiene que
  terminar exactamente en el borde del mueble. "large correction" = vuelve a leer los puntos.
- `clone X: seen x A to B`: tiene que quedar dentro de 6..1074 (si no, dice CLIPPED): mueve `x` hacia adentro o baja
  `scale`. Si la persona real está cortada por el mismo borde del cuadro (codo fuera de cuadro) un clon también puede
  salirse por ese borde: dice "acceptable, look at it".
- `the speaker's cutout is cut by the source frame edge and that straight cut is in view`: el clon muestra un codo
  cortado en el aire. Mueve `x` hasta que el corte quede fuera de cuadro o detrás de la persona.
- `head hidden by the real speaker`: sobre ~60% durante un tramo significa que el cuerpo de la persona tapa la cara de
  ese clon: aleja `x` de la persona.

## Qué mirar en los cuadros finales (`work/check/`)
- `sheet_pop_*`: la cabeza está libre del mueble en el cuadro de la vocal, ningún cuadro muestra un clon antes de su
  aparición.
- `crop_*` a 1:1: sin mancha clara donde la mano en movimiento de la persona pasa sobre un clon, sin halo en el clon, el
  clon termina limpio en el borde del mueble, la cara de la persona nunca queda tapada.
- `sheet_payoff`: un cuadro de destello suave, los tres en la misma pose después. `sheet_exit` y el último cuadro: toma
  limpia.
- La diferencia de check.py: ~0 antes de la primera aparición y después de la salida; "unexplained jump" = mira ese
  cuadro.

## Trampas
- Las tomas "estáticas" de gimbal avanzan. El seguimiento corre solo en la franja donde viven los clones, así que el
  borde de una mesa o alfombra junto al lente no lo sesga.
- RVM toma las manos con desenfoque de movimiento como opacas: bien sobre el fondo, una mancha clara sobre un clon.
  bake.py limita el alfa contra un fondo limpio, solo en píxeles descubiertos un cuadro antes o después (si no, una
  palma clara y quieta queda con hoyos).
- Las manos levantadas de la persona taparán la cara de un clon durante unos cuadros. Esa es la profundidad correcta.
  Arréglalo con `x`, no con el orden de capas.
- PIL trata RGBA de forma especial al filtrar y escalar: los cuadros premultiplicados se envuelven como `CMYK` (4
  canales simples).
- Haz saltar el envoltorio, destella el div interior, nunca el `<video>`. Las animaciones de filtro necesitan la misma
  lista de funciones en ambos extremos.
- El golpe del escenario (1,04) x la aparición del clon (1,1) en el remate necesita ~20 px de sobra en el borde del
  cuadro: la regla de 6..1074 lo cubre.
- En un espacio de reel deja `VIGNETTE = 0` y pon `EXIT_F`, o la vuelta a la toma salta.
