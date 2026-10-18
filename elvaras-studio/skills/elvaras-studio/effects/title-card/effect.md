# title-card (Tarjeta de Título)

**Qué hace:** una tarjeta de capítulo. La imagen corta a la pantalla bosque de la marca con un código de tiempo dorado
que corre; un título grande en Instrument Serif aterriza palabra por palabra con una línea dorada corta debajo; después
la persona vuelve dentro de un marco de teléfono con barra de reproducción, se asienta y crece hasta que el marco vuelve
a ser la imagen completa.

**Función:** separar partes de un video ("primer paso", "el resultado"), presentar un tema o el remate.

**Frases que lo activan:** "pon una tarjeta de título en esta parte", "corta a un título y vuelve en un teléfono",
"separador de capítulo".

## Todo es real
El título son palabras que la persona dice. El código de tiempo es el tiempo del propio reel y la barra del teléfono
muestra su posición y su largo reales. No hay nada inventado ni material de otros. Un solo video: la imagen completa se
achica hasta ser el teléfono y vuelve a crecer.

## Toma que necesita
Cualquier toma; la persona solo tiene que estar en el cuadro cuando vuelve en el teléfono. Sin recorte. Mientras dura la
pantalla del título, los subtítulos del reel se ocultan solos (`work/reel_captions.json`, lo lee `fx_add.py`).

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `T_IN` | cuadro en que corta a la pantalla del título | 2 o más; una palabra antes del título |
| `TITLE` | `(cuadro, 'PALABRAS')` por línea | cuadros de `words.json` del espacio; las palabras que dice, en su orden |
| `PHONE_AT`, `FULL_AT` | cuándo vuelve en el teléfono y cuándo crece | `None` = 12 cuadros tras la última línea, y 16 después |
| `TIMECODE`, `PLAYBAR` | código de tiempo y barra del teléfono | `True` |
| `SFX_VOL` | volumen | 1 |

**Interruptores:** `SAFE=1` guía de zona segura, `SFX=0` sin sonidos.

## Orden de ejecución (PY y SK como en SKILL.md)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # imprime los cuadros y los tiempos para la instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <los tiempos que imprime>
PY "SK/scripts/fx_run.py" "<slot>" build.py
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
Último paso en un reel: `fx_add.py`.
