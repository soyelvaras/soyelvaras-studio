# stat-stack (Cifra Grande)

**Qué hace:** el número que la persona dice cae enorme sobre el pecho en Bebas Neue dorado y sube hasta su valor en
cerca de 0,8 s (un número menor a 10 solo cae), y una línea chica en mayúsculas debajo cambia con las palabras que
siguen ("100%" / LO EDITÓ CLAUDE).

**Función:** prueba. Resultados, precios, cantidades: el número que ES el punto de la frase.

**Frases que lo activan:** "pon el número gigante", "que la cifra suba en pantalla".

## Todo es real
Solo un número que la persona dice de verdad, escrito como lo dijo. Nunca un resultado inventado.

## Bloque CLIP
| Campo | Qué es |
|---|---|
| `NUMBER` | el número como se dijo ("3.000", "100%", "7 días"). None = la primera palabra con un dígito |
| `T_IN` | cuándo cae. None = cuando empieza esa palabra |
| `COUNT` | segundos que sube hasta su valor (0 = cae ya con su valor). Respeta separadores y símbolos |
| `SUBS` | `[(TEXTO, seg)]` líneas chicas debajo, cada una reemplaza a la anterior. None = las 1 o 2 palabras dichas justo después; `[]` = ninguna |
| `T_OUT` | cuándo se va. None = el final del espacio |
| `Y`, `SIZE` | lugar y tamaño (un número largo se achica solo) |

## Trampa
Whisper puede partir "3.000" en dos palabras: escribe `NUMBER` a mano cuando se ve mal.

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
