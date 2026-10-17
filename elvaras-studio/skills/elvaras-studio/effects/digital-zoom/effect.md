# digital-zoom (Zoom Digital)

**Qué hace:** zooms digitales sincronizados con las palabras en una toma continua, que apuntan a la cara de la persona,
no al centro del cuadro: un acercamiento lento, un golpe seco con desenfoque de zoom real, un regreso rápido. Cualquier
cantidad de movimientos, en cualquier orden.
**Función:** gancho / retención. Le da a una sola toma dos o tres "ángulos de cámara" sin cortar.
**Frases que lo activan:** "acércate a mi cara cuando digo X", "zoom lento hacia mí en esta frase", "agrega zooms
digitales en las palabras clave", "acércate, y luego vuelve de golpe cuando digo Y".

## Toma que necesita, y dónde falla
- Una toma continua (sin cortes internos) con la cara visible todo el tiempo. Plano abierto, medio y selfie cercana
  funcionan; trípode o en mano funcionan (el seguimiento de la cara sostiene a la persona, el cuarto se mueve en su
  lugar).
- Mejor con `assets/aroll_hi.mp4` (crea el espacio con `--hi`): 1728 de ancho no pierde calidad hasta 1,6x, 1440 de
  ancho hasta 1,33x. Con una fuente de 1080 todo zoom es una ampliación: build.py limita la escala a `MAX_UPSCALE`
  (1,5x) e imprime que lo hizo. En clips de 1080 mantén un acercamiento de unos 1,15 y un golpe de unos 1,35.
- Falla o se ve mal cuando: la cara sale del cuadro o se da vuelta por completo (el seguimiento vuelve al recorte y
  tiembla); una mano tapa los ojos más de unos pocos cuadros; la cabeza ya llena el cuadro (no queda nada donde
  acercarse); la toma tiene un corte.
- Un plano cercano deja poco espacio bajo la barbilla una vez acercado: usa `CAPTIONS=0` o una línea corta (ver el
  margen abajo). Para dejar la barbilla libre de los subtítulos del reel, sube `EYE` (por ejemplo `(540, 600)`).

## Entradas del espacio
recorte `assets/subject.webm`: sí (posición de la cabeza). `assets/aroll_hi.mp4`: opcional, muy recomendado.
`words.json`: solo como guía para `onsets.py`. Python: solo el Python de la skill (numpy, PIL), sin paquetes extra.

## Bloque CLIP (inicio de build.py, entre los marcadores CLIP)
| Campo | Qué es | Cómo encontrarlo para un clip nuevo |
|---|---|---|
| `ZOOMS` | lista de `zoom(t_inicio, t_llegada, escala, tipo)`, tipo `creep` / `snap` / `pull`, tiempos como `F(cuadro)` | cuadros de `onsets.py`. creep llega 2 cuadros después de la vocal; snap llega EN la vocal acentuada y empieza 3 cuadros antes; pull empieza en el inicio de la palabra, llega ~9 cuadros después. Opcional por zoom: `drift=` (0 = quieto), `over=`, `sfx=False` |
| `EYE` | dónde quedan los ojos en pantalla cuando está cerrado | (540, 640) planos abiertos y medios; cerca de (540, 620) en un plano cercano. build.py imprime "aim: ... fully framed from N x": empieza los golpes sobre N |
| `FOLLOW` | qué tan de cerca sigue la cámara a la cabeza (sigma, cuadros) | 5 por defecto; 3 en mano; 8 a 10 si el fondo de un trípode "nada" |
| `AIM` | punto de los ojos manual `(cuadro, x, y)`, por defecto `None` | solo si `work/track_check.jpg` muestra la cruz fuera de los ojos (con lentes puede quedar sobre un lente: pon el punto entre los ojos) |
| `MAX_UPSCALE` | cuánto puede pasar una escala del límite sin pérdida | deja 1,5 |
| `CAPS` | grupos de subtítulos `(último cuadro, [(top px, tamaño, [(cuadro, palabra, 'y' o '')])])`, tamaño `'sm'` / `'lg'` / `'big'` o px | cuadros de palabra de `onsets.py`; tops y tamaños desde el margen impreso (avisa: muy cerca de la barbilla, bajo 1470, muy ancho) |
| `WHOOSH` | volumen del whoosh en cada golpe (0 = ninguno) | 0,26 queda bajo la voz a un volumen normal de habla |
| `GRADE` | color CSS sobre la imagen | déjalo, o iguálalo al reel |
| `VARIANT` | 1 Golpes, 2 Medio rostro | lo escribe `fx_new.py` desde el selector |
| `HALF` | solo Medio rostro: (primer cuadro, último cuadro) del look | desde que aterriza el zoom de entrada hasta que empieza el regreso |
| `SIDE` | solo Medio rostro: lado donde queda la cara, `'left'` o `'right'` | el lado contrario a donde hay más aire en la toma. Un `EYE` centrado se mueve solo a x 150 / 930; para dejar media cara exacta baja a x 90 (o 990) |
| `HALF_WORDS` | solo Medio rostro: las palabras del lado vacío, `(último cuadro o None, líneas)`, línea = `(cuadro, texto, estilo)` | cuadros de `onsets.py`. Estilos: `'sm'` Work Sans (lectura), `'lg'` Bebas Neue (el golpe), `'it'` Instrument Serif cursiva en dorado (la palabra clave). Se achican solas para caber |
| `HALF_TOP` | solo Medio rostro: y donde empieza la pila de palabras | cerca de los ojos, 560 |
| `DIM`, `LINE` | solo Medio rostro: cómo queda el cuarto (filtro CSS) y el color del contorno y las líneas | gris oscuro y crema |

## Versiones (`VARIANT` en el bloque CLIP)

El usuario la elige en el selector (puntitos bajo la tarjeta); `fx_new.py` la escribe sola en el espacio.

1. **Golpes:** todo lo de arriba. Acercamientos, golpes y regresos a la cara, sincronizados con las palabras. Los
   subtítulos del reel siguen encima.
2. **Medio rostro:** un zoom extremo (hasta 1,95x de la fuente, con un tope propio más alto que `MAX_UPSCALE` porque el
   cuarto oscuro esconde la ampliación) deja media cara en un lado de la pantalla. Mientras dura `HALF`, el cuarto se
   oscurece y pasa a gris, el color y una línea fina crema bajan alrededor de la persona, y las palabras de ese momento
   se apilan en el lado vacío: entran desenfocadas y grises y se aclaran, con una línea horizontal que las sigue hacia
   abajo y una línea vertical al borde. `ZOOMS` es un golpe (o acercamiento) de entrada y un regreso.
   - `bake.py` hornea además `assets/zoom_cut.webm`: la persona sola, con el mismo encuadre, solo para los cuadros del
     look. Si cambias `ZOOMS`, `EYE`, `HALF` o `VARIANT`, vuelve a hornear (build.py avisa).
   - Sus palabras son el efecto: van siempre, también con `CAPTIONS=0`. Los subtítulos del reel se ocultan solo
     mientras dura `HALF` (build.py escribe `work/reel_captions.json` y `fx_add.py` lo lee), así que `HALF_WORDS` tiene
     que llevar todas las palabras dichas en ese tramo. `CAPS` solo para lo que se dice fuera de `HALF`.
   - Un golpe desde 1,0 hasta la cara en el borde desliza la imagen en sus cuadros de viaje: se lee como un golpe con
     desenfoque. Si molesta, entra con un acercamiento.

## Interruptores (variables de entorno de build.py)
`SAFE=1` guía de zona segura + objetivo de los ojos + línea de la barbilla (solo instantáneas). `CAPTIONS=0` sin palabras
de subtítulo: SIEMPRE en un reel, para que los subtítulos propios del reel sigan sobre el zoom en el estilo que eligió el
usuario (la lista `CAPS` es solo para un clip suelto). build.py imprime entonces una línea "reel captions": si la
barbilla queda libre de la franja de subtítulos del reel en el zoom más cerrado. `SFX=0` sin whoosh. `GRADE=0` sin
color, viñeta ni destello: úsalo cuando el espacio va dentro de un reel con color, si no, el look salta en los bordes del
espacio. `HI=0` ignora aroll_hi y trabaja desde la toma de 1080.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. cuadro de inicio de cada palabra; luego edita el bloque CLIP
PY "SK/scripts/fx_run.py" "<slot>" track.py      # 2. seguimiento de los ojos. MIRA work/track_check.jpg (cruz entre los ojos en cada recuadro)
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0 CAPTIONS=0      # 3. cámara + index.html. Lee lo que imprime: subtítulos, escala por cuadro, la línea de subtítulos del reel
PY "SK/scripts/fx_run.py" "<slot>" bake.py      # 4. assets/zoom.mp4, 1 a 3 min (PY bake.py --frames 80-90 previsualiza unos cuadros primero)
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # 5. tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 GRADE=0 CAPTIONS=0
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.2,2.9,3.6      # usa tus propios tiempos: uno justo después de cada llegada
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0 CAPTIONS=0      # 6. guía apagada de nuevo, los mismos interruptores que el render
PY "SK/scripts/fx_run.py" "<slot>" hf render --video-frame-format png
PY "SK/scripts/fx_run.py" "<slot>" post.py      # 7. cantidad de cuadros, renders/<slot>-phone.mp4, cuadros, work/qa/sheet_*.jpg
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Vuelve a hornear después de cualquier cambio en ZOOMS, EYE, FOLLOW, AIM o HI; subtítulos, color y sonido solo necesitan
build.py y el render.

## Qué mirar en los cuadros finales (work/qa/sheet_*.jpg)
- Cada golpe: dos cuadros desenfocados en viaje, luego un cuadro nítido EN la vocal acentuada. Cada acercamiento: el
  movimiento se detiene a uno o dos cuadros de su palabra. Cada regreso: abierto y nítido de nuevo antes de la frase
  siguiente.
- Los ojos en la línea `EYE` en cada cuadro cerrado, cara centrada. El desenfoque de zoom se estira alejándose de la
  cara, la cara queda como lo más nítido.
- Ningún subtítulo de los ojos a la barbilla, nada legible sobre y 220 ni bajo y 1470, columna derecha libre desde
  y 1155.
- El primer cuadro idéntico a la toma. El último cuadro exactamente a 1,0x si la lista termina con un regreso (si no, el
  reel corta de vuelta al plano abierto, lo que es una decisión: build.py imprime una nota; si el siguiente tramo ya
  viene acercado, el corte se ve natural).

## Trampas
- Los inicios de palabra de Whisper llegan 1 a 4 cuadros antes o después. Nunca tomes el tiempo de un zoom desde
  words.json: usa `onsets.py`.
- Lo alto de la cabeza según el recorte no es la línea de los ojos (se corre 20 a 30 px cuando la persona inclina la
  cabeza). La coincidencia de plantilla lo corrige; el recorte es solo la baranda. Confía en `track_check.jpg`, no en los
  números.
- Una salida suavizada "llega" 4 a 5 cuadros antes de su último fotograma clave. Por eso el `t_llegada` de un
  acercamiento va 2 cuadros después de la vocal.
- El desenfoque depende de la velocidad: los acercamientos quedan nítidos, los golpes se estiran. Un acercamiento que
  recorre más de unos 0,6x en menos de 15 cuadros empieza a desenfocarse; hazlo golpe o dale más cuadros.
- Las apariciones de subtítulos con más de 18 px de desenfoque se ven como una mancha gris un cuadro. Una animación que
  empieza en el cuadro de una palabra no muestra nada en ese cuadro (`T()` la empieza 1,4 cuadros antes).
- A 1,0x el recorte no se puede mover, así que la mira se mezcla a medida que la escala sale de 1,0. Un golpe que empieza
  bajo la escala "fully framed" también desliza la imagen y mancha la cara en sus dos cuadros de viaje (build.py imprime
  una nota). Arreglo: deja que un acercamiento llegue antes a esa escala, o acerca `EYE` a donde ya están los ojos. El
  mismo deslizamiento pasa al final de un regreso a 1,0 cuando la persona está descentrada; se esconde en el latigazo.
- El render del espacio deja el audio intacto más el whoosh. Si el reel agrega su propio diseño de sonido, renderiza con
  `SFX=0`.
- No implementado: hacer zoom también al recorte (para palabras detrás de la cabeza durante un zoom). Necesita una
  segunda pasada de horneado sobre subject.webm con el mismo camera.json.
