# Corte en Zoom: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Orígenes (dos tomas, 1080x1920):** toma A, 67 cuadros (abierto, sentado en el piso junto al sillón individual). Toma B,
74 cuadros (abierto, en el sillón individual). 141 cuadros en total, corte en el cuadro 67.

**Frase dicha:** "And you can get the cool girl aesthetic like this. / Or you can get the cool dude aesthetic ..."

**Bloque CLIP que hizo `demo.mp4`:**

```python
CUT = 67                  # cut_frames de clip.json
HALF = 9                  # 18 cuadros de transición, del 58 al 75
POINT_A = (480, 1212)     # elegido a mano en la polera negra, último cuadro de la toma A
POINT_B = (516, 1200)     # elegido a mano en la polera, primer cuadro de la toma B
DEPTH = 80.0
SHARP = 2.4
ROLL = 5.0
CREEP_A = 1.03
CREEP_B = 1.04
GRADE_A = 'girl'          # cálido, suave
GRADE_B = 'dude'          # oscuro, frío
CAP_A = {'style': 'girl', 'top': 1126,
         'lead': [(0.42, 'you'), (0.52, 'can'), (0.64, 'get'), (0.80, 'the')],
         'punch': [(0.92, 'cool'), (1.10, 'girl')],
         'tail': [(1.32, 'aesthetic')]}
CAP_B = {'style': 'dude', 'top': 1150,
         'lead': [(2.29, 'or'), (2.55, 'you'), (2.67, 'can'), (2.79, 'get'), (2.95, 'the')],
         'lead_rides': True,
         'punch': [(3.11, 'cool'), (3.31, 'dude')],
         'tail': [(3.53, 'aesthetic')]}
WHOOSH_VOL = 0.30
```

El `build.py` del paquete trae las mismas palabras y tiempos de subtítulo, pero con `POINT_A`, `POINT_B`, ambos valores
`top` y ambos colores en `None` (medidos por prep.py, imagen sin color), que son los valores correctos para un clip
nuevo.

**Momentos:** el bloque "cool girl" se arma palabra por palabra sobre la toma A; en el cuadro 58 la cámara empieza a
entrar en la polera y el bloque pasa rápido por el lente; el cuadro 67 (el corte) es oscuro con la toma B como un
pequeño destello en el punto; la toma B se abre y frena en su lugar hacia el cuadro 76 con "or you can get the" entrando
con la imagen; "cool dude" sube en sus palabras.

**Qué difiere del efecto empaquetado:** `demo.mp4` es el render de antes de empaquetar. Alrededor de la toma B, mientras
era más chica que el cuadro, ese armado usaba copias espejadas del cuarto, oscurecidas. El `bake.py` del paquete las
reemplaza por los propios colores de borde de la imagen estirados hacia afuera a lo largo de los rayos del zoom y
desvaneciéndose a oscuro, así que una pasada nueva de este clip muestra rayos suaves ahí. Todo lo demás (curva de
cámara, desenfoque, portal, subtítulos, whoosh) es el mismo código.

**Cuadros:** `stills/zoom-through-1.jpg` toma A con su subtítulo, `-2.jpg` el paso a través, `-3.jpg` toma B llegada.
