# Clon: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Origen:** plano abierto, la persona sentada en el borde delantero del sillón verde, cámara en un gimbal sobre la mesa
delante de ella (avanzó 13 px de lado y 7 px hacia arriba durante el clip). 132 cuadros (4,4 s).
**Frase dicha:** "you need edits like this, like this, or like that." ("necesitas ediciones así, así, o así.")
**Qué pasa:** el clon I aparece detrás del sillón en el primer "like THIS" (vocal en f37), el clon D en el segundo (f69),
ambos se sincronizan con la persona y saltan con destello en "or like THAT" (f115). Se quedan hasta el último cuadro
(demo suelta, sin salida).

`demo.mp4` es la copia para celular del render, `stills/` son los cuadros 48, 80 y 122.

## Bloque CLIP de la demo (también es lo que trae al inicio `build.py`)
```python
CLONES = [
    dict(id='L', word_f=37, x=287, top=520, scale=.64, lag=6),
    dict(id='R', word_f=69, x=781, top=520, scale=.64, lag=9),
]
SYNC_F = 115
EXIT_F = None
OCCLUDER_LINE = [(0, 998), (42, 998), (52, 940), (240, 960), (880, 966), (1080, 968)]   # cojín, esquina del sillón, respaldo
LIGHT_FROM = 'right'
CAP_X = 540
CAPS = [
    (1078, [('you', 1, ''), ('need', 3, ''), ('edits', 13, '')], 24),
    (1078, [('like', 25, ''), ('this', 36, 'y')], 54),
    (1078, [('like', 57, ''), ('this', 68, 'y')], 88),
    (1052, [('or', 91, ''), ('like', 104, '')], None),
]
PUNCH = ('that', 115, 1118, None)
ACCENT = '#FAE67A'  # en Soy Elvaras el acento por defecto es dorado #C9A15B
VIGNETTE = 0.0      # la demo usó 0.22 (clip suelto)
```

## Números que dieron las herramientas en este clip
- `prep.py`: ancla de la cabeza (540, 442), cabeza de 172 x 294 px, recorte de x 128 a 1000 (lo más ancho en el cuadro
  67, ambas manos abiertas).
- Golpes de palabra: this=37, this=69, or=91, that=116 (Whisper tenía los dos primeros 0,2 s antes).
- `bake.py`: deriva de 13,2 px de lado / 6,9 px vertical, borde del mueble ajustado en 459 columnas (la persona cubre el
  resto), clon I visto de x 21 a 576, clon D de 515 a 1069.

## Por qué la composición se ve así
La persona mide 750 px de ancho con las manos abiertas, así que no hay espacio para una copia del mismo tamaño a su
lado. Los clones quedan detrás del respaldo del sillón a 0,64 (lo que mide una persona unos 70 cm más lejos de este
lente), con las cabezas al lado y un poco más abajo que la de la persona, y el borde del sillón esconde todo bajo sus
caderas. En "or" las manos levantadas de la persona tapan las caras de los clones unos 10 cuadros: profundidad
correcta, se deja así.

Volver a correr el efecto del paquete sobre este clip con el bloque de arriba reproduce la demo (revisado al
empaquetar).
