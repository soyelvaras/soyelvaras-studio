# storyboard-deck (Mazo de Storyboard)

**Qué hace:** una fila de tarjetas de storyboard se reparte sobre el pecho una por una, como naipes: primero la tarjeta
de guion (la frase que se está diciendo), después cuadros de sus propios reels, cada uno con su número, su tiempo y lo
que se dice en él. Todo el movimiento va de izquierda a derecha: entran desde la izquierda, una ola recorre la fila, una tarjeta se levanta para destacar y la fila sale hacia la derecha.

**Función:** explicar / prueba. Mostrar cómo se arma un video, un antes de grabar, "así lo planeé", un resumen de un reel.

**Frases que lo activan:** "reparte un storyboard sobre mi pecho", "muestra los cuadros del reel como tarjetas", "mazo de
storyboard".

## Todo es real
Los cuadros son fotos de su propio material (`'aroll'` = la toma del espacio, o la ruta de uno de sus reels) en los
segundos que se indiquen. Las citas bajo cada cuadro son las palabras dichas en ese momento: salen del `words.json` del
clip (el del espacio, o el del proyecto de ese reel) o se escriben a mano. Nunca una cita inventada.

## Toma que necesita
Cualquier plano con espacio bajo la barbilla (un plano cercano deja poco: la fila se achica o se niega). Sin recorte: la
fila va adelante, sobre el cuerpo, nunca sobre la cara. Los subtítulos del reel se ocultan mientras está arriba.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `F_IN`, `F_OUT` | cuando se reparte la primera tarjeta y cuando se va la fila | 10 o más; `None` = 14 cuadros antes del final |
| `SCRIPT` | texto de la tarjeta de guion | `None` = lo que se dice en el espacio |
| `FRAMES` | `(clip, segundo, 'cita' o None)` por tarjeta, 2 a 5 | `'aroll'` o la ruta de un reel propio; `None` lee la cita del `words.json` |
| `HIGHLIGHT` | qué tarjeta de cuadro se levanta | 1 = la primera; 0 = ninguna |
| `DEAL_EVERY`, `SFX_VOL` | cuadros entre tarjetas, volumen | 4, 1 |

**Interruptores:** `SAFE=1` guía de zona segura, `SFX=0` sin sonidos.

## Orden de ejecución (PY y SK como en SKILL.md)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # imprime la fila, los cuadros y los tiempos para la instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <los tiempos que imprime>
PY "SK/scripts/fx_run.py" "<slot>" build.py
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
Último paso en un reel: `fx_add.py`.
