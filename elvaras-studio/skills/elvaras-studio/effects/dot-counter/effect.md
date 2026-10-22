# dot-counter (Puntos)

**Qué hace:** una fila de puntos cae, uno tras otro, cuando la persona dice cuántas cosas vienen ("tres pasos").
Con `FILL_AT`, cada punto se llena de dorado en la palabra de su paso, y la fila muestra cuánto va de la lista.

**Función:** explicar. El "vienen N cosas" de una lista, y el avance paso a paso.

**Frases que lo activan:** "muestra con puntos cuántos pasos son", "que se marque cada paso".

## Todo es real
`COUNT` es el número que la persona dice (2 a 8). `FILL_AT` son los segundos en que nombra cada paso.

## Bloque CLIP
| Campo | Qué es |
|---|---|
| `COUNT` | cuántos puntos. None = el número dicho en el espacio (dígito o dos a ocho) |
| `FILLED` | cuántos caen ya llenos. None = todos (o ninguno con FILL_AT) |
| `FILL_AT` | `[seg, ...]` cada punto se llena en su paso, con un pop. `[]` = sin llenado |
| `T_IN`, `STEP` | cuándo cae el primero y la separación entre puntos |
| `T_OUT` | cuándo se va. None = 0,6 s después de la palabra contada (o del último FILL_AT) |
| `Y`, `DOT`, `SOUND` | lugar, tamaño del punto, volumen del click |

Para que vaya llenándose durante toda la lista, el espacio tiene que cubrir la lista entera (un efecto superpuesto
puede cruzar cortes).

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
