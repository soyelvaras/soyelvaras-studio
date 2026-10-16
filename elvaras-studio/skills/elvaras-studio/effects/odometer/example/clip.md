# Contador: el clip de demo

**Toma:** selfie cercana en mano (la persona llena casi todo el cuadro, la pared deriva unos 120 px), 186 cuadros.
**Frase:** "with 10 years of experience running ads for hundreds of different offers, funnels, and all types of
budgets." ("con 10 años de experiencia haciendo anuncios para cientos de ofertas distintas, embudos y todo tipo de
presupuestos.")

## Bloque CLIP que la reconstruye (es lo que trae build.py, más el `label2` opcional en el segundo contador)
```python
COUNTERS = [
    dict(text='10', say='10', lock=None,
         label=[('YEARS', 'years'), ('RUNNING', 'running'), ('ADS', 'ads')],   # se parte: YEARS / RUNNING ADS
         label2=None, sit='auto', size='auto', then='dock'),
    dict(text='100s', say='hundreds', lock=None,
         label=[('OF', 'of'), ('OFFERS', 'offers')],
         label2=[[('FUNNELS', 'funnels')], [('FUNNELS', 'budgets'), ('+', None), ('BUDGETS', None)]],   # solo demo; por defecto None
         sit='auto', size='auto', then='dock'),
]
ROLL = 0.44
OUT = None
DOCK_CORNER = 'auto'
GRADE = 'contrast(1.05) saturate(.92) brightness(.99)'
```

En español, `say` toma las palabras como las escribe words.json ("diez", "10", "mil", "cien por ciento").

## Lo que midió la maquinaria en este clip (la demo los tenía escritos a mano)
| | puesto a mano en la demo | medido por el paquete |
|---|---|---|
| trabado de "10" | 0,56 s | 0,56 s (Whisper decía que la palabra iba de 0,24 a 0,58) |
| trabado de "100s" | 2,48 s | 2,51 s |
| YEARS / RUNNING / ADS | 0,60 / 1,62 / 1,82 | 0,60 / 1,61 / 1,84 (Whisper: 0,58 / 1,26 / 1,74) |
| OF / OFFERS | 2,55 / 3,05 | 2,56 / 3,17 |
| panel "10" | (610, 236) escala 1,25 | (595, 236) escala 1,25 |
| ficha | (45, 236) | (47, 236) |
| panel "100s" | (455, 236) escala 1,0, la cabeza cortaba la esquina de un tambor en 5 cuadros | (463, 236) escala 0,91, nada legible detrás de la persona |

Momentos: 0,02 el panel aparece arriba a la derecha, los tambores giran, "10" se traba a los 0,56 cuando termina "ten";
YEARS, RUNNING ADS en las palabras de la persona; 1,93 el panel se achica a una ficha arriba a la izquierda mientras el
panel "100s" entra desde la derecha y se traba en "hundreds" a los 2,51; OF OFFERS.
