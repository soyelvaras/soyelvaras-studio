# Clip de demo

**Origen:** el clip de demo, 138 cuadros (4,6 s). Plano abierto, la persona recostada en el piso junto al sillón verde,
cámara quieta, original de 1728x3072 (`aroll_hi.mp4`, sin pérdida hasta 1,6x).
**Frase:** "and you don't need to be techy or know anything about video editing in order to use it." ("y no necesitas
ser técnico ni saber nada de edición de video para usarlo.")

## Inicios leídos del audio (onsets.py), no de Whisper
| palabra | Whisper | cuadro real |
|---|---|---|
| "and" (primera palabra) | 0,05 s | f1 |
| "techy" | 0,99 s (f30) | golpe de la t f32,5, vocal acentuada f35,5 |
| "video" | 2,77 s (f83) | "v" f83,5, vocal acentuada f86 |
| "editing" | 3,11 s (f93) | f95 |
| "in" (order to use it) | 3,47 s (f104) | f108,5 |

## Valores del bloque CLIP (siguen siendo los valores por defecto en build.py)
```python
ZOOMS = [
    zoom(F(1), F(37), 1.62, 'creep'),       # empieza en "and", el movimiento muere en la vocal de "TECH-y" (f35 + 2)
    zoom(F(83), F(86), 2.26, 'snap'),       # sale en la "v", el pico cae en la vocal de "VI-deo"
    zoom(F(108), F(117), 1.0, 'pull'),      # sale en "in", abierto de nuevo antes de que termine "order"
]
EYE = (540, 640)
FOLLOW = 5
AIM = None
MAX_UPSCALE = 1.5
CAPS = [
    (54, [(1000, 'sm', [(8, 'you', ''), (13, 'don’t', ''), (18, 'need', ''), (23, 'to', ''), (26, 'be', '')]),
          (1082, 'big', [(33, 'techy', 'y')])]),
    (83, [(1000, 'sm', [(56, 'or', ''), (59, 'know', ''), (65, 'anything', ''), (78, 'about', '')])]),
    (108, [(1062, 'lg', [(86, 'video', '')]), (1228, 'lg', [(95, 'editing', 'y')])]),
    (None, [(1000, 'sm', [(110, 'in', ''), (113, 'order', ''), (120, 'to', '')]),
            (1082, 'big', [(123, 'use', ''), (130, 'it.', '')])]),
]
WHOOSH = 0.26
GRADE = 'contrast(1.06) saturate(.93) brightness(.98)'
```

## Qué hace la cámara con eso
- f1 a f37: acercamiento de 1,0x a 1,62x, los ojos se desplazan desde donde estaban a (540, 640), nítido todo el tiempo.
- f83 a f86: golpe a un pico de 2,35x (2,26 + 4% de rebote), los cuadros 84 y 85 llevan hasta 136 px de desenfoque de
  zoom en las esquinas, f86 está nítido, vuelve a 2,26 hacia f90, luego un avance lento.
- f108 a f117: regreso, abierto y nítido hacia f114, exactamente 1,0x en los últimos cuadros.
- 2,35x sobre un original sin pérdida hasta 1,6x es una ampliación de 1,47x: dentro de `MAX_UPSCALE`, nada se limitó.
- Cuadros: 1 = el acercamiento llegó ("techy"), 2 = el cuadro en viaje del golpe (f85), 3 = el golpe sostenido ("video
  editing").

## En los reels de Soy Elvaras
Sobre las fuentes de 1080 del celular de Cristobal se usó un acercamiento a 1,10-1,17 y un golpe a 1,30-1,35, con
`EYE = (540, 600)` para dejar la barbilla libre de los subtítulos, y `AIM` entre los ojos cuando el seguimiento se quedó
en un lente.
