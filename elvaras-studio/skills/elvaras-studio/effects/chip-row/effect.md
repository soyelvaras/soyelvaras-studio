# chip-row (Fila de Cápsulas)

**Qué hace:** mientras la persona enumera, aparece una cápsula con borde por cada cosa, en fila bajo los
subtítulos, cada una en la palabra en que se dice. Si la cosa es una app, lleva su logo real adentro. La última
cápsula lleva borde dorado: ahí aterriza la lista.

**Función:** explicar. Listas cortas: herramientas, pasos, cosas que se necesitan o no.

**Frases que lo activan:** "pon lo que nombro en cápsulas", "una fila con las apps que uso".

## Todo es real
Las cápsulas son lo que la persona nombra, con sus palabras (1 a 3 palabras cada una, 2 a 4 cápsulas). Un logo solo
para una app que nombra.

## Bloque CLIP
| Campo | Qué es |
|---|---|
| `CHIPS` | `[(texto, seg)]` o `[(texto, seg, app)]`: una cápsula por cosa, en el segundo en que se dice. Obligatorio |
| `T_OUT` | cuándo se va la fila. None = el final del espacio |
| `Y`, `SIZE` | lugar (None = justo bajo la línea de subtítulos) y tamaño; una fila muy ancha se achica sola |
| `LAST_ACCENT` | borde dorado en la última cápsula |
| `SOUND` | volumen del click de cada cápsula |

Los subtítulos del reel siguen corriendo arriba de la fila: revisa en la instantánea que no se toquen.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd ni variables)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # imprime tiempos, lugar, momentos para instantánea y la ventana de subtítulos
PY "SK/scripts/fx_run.py" "<slot>" hf lint             # 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <los tiempos que imprimió build.py>      # MIRA, también a mitad de la entrada
PY "SK/scripts/fx_run.py" "<slot>" build.py            # guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render           # -> renders/<slot>.webm con transparencia
PY "SK/scripts/fx_run.py" "<slot>" check.py            # cuadros, work/check/sheet.jpg (el gráfico sobre la toma), copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda en `RUN.txt`. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Un efecto superpuesto
`slot.json` dice `"layer": "overlay"`: el armado final son solo gráficos transparentes, `hf render` escribe un `.webm` y el
reel lo pone ENCIMA de su propia imagen, que conserva su color, sus cortes y la cámara viva. Por eso puede cruzar cortes,
no necesita recorte ni paquetes extra, y la autorrevisión (`frames_check.py`) sigue midiendo sus cuadros: marca el
gráfico si toca la cara o el área roja. Con `SAFE=1` la toma va debajo para juzgar las instantáneas.
El movimiento sigue `references/motion.md` (base común en `vgfx.py`): entrada con un pequeño exceso, salida más rápida,
piezas escalonadas, y mientras se queda sigue creciendo un poco.

## El estilo del usuario manda
El bloque STYLE al inicio de `build.py` trae Soy Elvaras (Work Sans, Bebas Neue, Instrument Serif itálica, crema,
dorado, bosque). Antes del primer armado, ajústalo al estilo de subtítulos del reel (`effects/INDEX.md`, "Reestilizar
las palabras de un efecto").
