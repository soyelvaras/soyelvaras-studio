# Checklist: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Origen:** el clip de demo (del creador original, en inglés), 128 cuadros (4,25 s). Plano abierto, la persona sentada
en el piso, pared libre sobre la cabeza. Descrito como cámara estática; prep.py mide 15 px de deriva del fondo (se
balancea durante el primer segundo), todavía dentro del límite del vidrio de 24 px.

**Frase dicha:** "All you need to do is drop your clips, trigger the skill, and Claude takes care of it all for you."
("Solo tienes que soltar tus clips, activar la skill, y Claude se encarga de todo por ti.")

**Bloque CLIP que hizo `demo.mp4`** (el `build.py` del paquete trae estos TITLE / ROWS / cuadros pero con
`CARD_BOX = 'auto'`, `LAYER = 'auto'`, `GRADE = ''`, `VIGNETTE = 0`, `PUSH = 1.0` como valores para un clip nuevo; con
el bloque de abajo reconstruye la línea de tiempo de la demo línea por línea, revisado contra el index.html):

```python
TITLE = 'All you need to do'
ROWS = [
    ('Drop your clips',        28, 39),    # vocal de "drop" f30 -> say 28; vocal de "clips" f40 -> tick 39
    ('Trigger the skill',      55, 69),    # vocal de "trigger" f58 (dicho 55, onsets.py sugiere 56); vocal de "skill" f70 -> tick 69
    ('*Claude* does the rest', 83, 97),    # vocal de "Claude" f84 (onsets.py sugiere 82); vocal de "care" f98 -> tick 97
]
F_IN = 2            # la voz empieza en el cuadro 2
F_DONE = 108        # "(takes care of it) ALL"
F_OUT = None        # el clip termina en la tarjeta terminada
CARD_BOX = (100, 256, 880, 649)    # puesto a mano; CARD_BOX = 'auto' da (104, 256, 873, 644), escala 0.99
LAYER = 'behind'
OVERLAP = 40        # lo alto del gorro de la persona va de y 855 a 870, el borde inferior de la tarjeta en y 905
GLASS = 'auto'      # -> vidrio
ACCENT = '#FAE67A'  # en Soy Elvaras el acento por defecto es dorado #C9A15B
GRADE = 'contrast(1.05) saturate(.95) brightness(.99)'
VIGNETTE = .30
PUSH = 1.03
```

**Momentos:** la tarjeta entra inclinada en "All" (f2), encabezado + tres círculos vacíos hacia f22; el texto de las filas
cae en "drop" / "trigger" / "Claude"; las marcas saltan en "clips" / "skill" / "care"; en "all" la cápsula salta a
"3 de 3" en el color de acento, brillo, resplandor en el borde, la tarjeta se asienta plana.

**Archivos:** `demo.mp4` (vista previa 720x1280 con sonido), `stills/checklist-1.jpg` (primera marca a mitad del salto),
`-2.jpg` (tercera marca), `-3.jpg` (tarjeta terminada).
