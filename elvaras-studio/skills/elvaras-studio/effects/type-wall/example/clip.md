# Muro de Palabras: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Origen:** el clip de demo, 92 cuadros (3,07 s). Plano medio, la persona sentada en el piso apoyada en un baúl de
madera, pared libre sobre la cabeza (lo alto de la cabeza en y 328 a 340). La cámara no está fija: se asienta durante
los primeros 1,5 s (prep.py mide unos 97 px de movimiento del fondo en el espacio).

**Frase dicha:** "Everybody's talking about how Claude can edit your videos."

**Bloque CLIP de este clip** (son los valores que trae el `build.py` del paquete):

```python
PHRASES = [
    {'words': [(3, 'EVERY'), (11, 'BODY’S'), (21, 'TALKING')]},     # la voz empieza en f3; "body's" es la caída en f11; "talking" f21
    {'words': [(42, 'CLAUDE')], 'hit': True},                       # la "Cl" dura en f42: golpe del muro, fila de acento, impacto grave
    {'words': [(56, 'EDIT'), (65, 'YOUR'), (71, 'VIDEOS')]},        # el muro termina leyendo EDIT / YOUR / VIDEOS de arriba abajo
]
IN_FRAME = 0        # el clip abre con el muro
OUT_FRAME = None
KEEP = []
FS = 205
ACCENT_Y = None     # medido: letras de la fila de acento en y 165 a 314 (la demo a mano las tenía en 167 a 317)
HEAD_GAP = 14
XC = {}             # medido: filas 0 a 4 centradas en x 470, 536, 200, 940, 1016
GROUND = ('#22261A', '#14160F', '#0B0C09')
INK = '#EEEADF'
ACCENT = '#FAE67A'  # en Soy Elvaras el acento por defecto es dorado #C9A15B
VOL_IN, VOL_HIT, VOL_SWAP = .28, .08, .16
```

**Momentos:** las filas entran de golpe desde lados alternados en el primer cuadro; el muro arma EVERY / BODY'S /
TALKING mientras la persona lo dice; en "Claude" cada fila salta a CLAUDE esparciéndose desde la fila sobre la cabeza,
el muro se acerca de golpe y esa fila pasa al color de acento; luego EDIT, YOUR, VIDEOS se arman hacia abajo.

**En qué se diferencia `demo.mp4` de lo que arma el paquete sobre el mismo clip** (el render de demo se hizo antes de
empaquetar):
- En la demo el baúl y la alfombra quedan delante del muro. Eso fue una forma dibujada a mano y seguida con la cámara en
  movimiento cuadro a cuadro. El paquete no trae ese seguimiento: sus formas `KEEP` son fijas, para una cámara quieta. En
  este clip el paquete se correría con `KEEP = []` (muro hasta abajo) o sobre una toma nueva con cámara fija.
- En la demo las filas que dirán TALKING están vacías hasta que la persona lo dice. El paquete empieza cada fila en la
  primera palabra y pasa filas a la 2.ª y 3.ª palabra cuando la persona las dice (igual que la demo arma EDIT / YOUR /
  VIDEOS).
- Las alturas de fila y las posiciones de palabra se escribieron a mano en la demo y se miden desde el recorte en el
  paquete. Los números quedan a menos de 3 px para la fila de acento.
- Cuadros de palabra: la demo usó 56 / 65 / 71 para edit / your / videos. `onsets.py` oye esas palabras empezar en
  53 / 62 / 67. Ambos se leen en la palabra; los más tardíos son los que usa la demo.

**Archivos:** `demo.mp4` (vista previa 720x1280 con sonido), `stills/type-wall-1.jpg` a `-3.jpg` (tres momentos de la
demo en orden; `-2.jpg` es el golpe de CLAUDE).
