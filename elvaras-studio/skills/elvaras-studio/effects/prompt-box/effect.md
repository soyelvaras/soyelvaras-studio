# prompt-box (Caja de Prompt)

**Qué hace:** una caja de texto sube sobre el pecho con el logo real y el nombre de la app en el hueco de su borde
superior, y lo que la persona dice que le pide a la IA se escribe solo, con cursor de texto. Cuando la frase termina,
un cursor de mouse llega en arco y aprieta el botón de enviar.

**Función:** explicar. "Le digo a Claude: edítalo", "escribo un prompt", el momento en que se le pide algo a una app.

**Frases que lo activan:** "pon mi prompt en pantalla", "que se escriba lo que le pido a Claude".

## Todo es real
`TEXT` son palabras que la persona dice, como las escribiría. `APP` solo cuando nombra la app: su logo real sale de
`assets/icons` (`engine/icons` trae 46 apps; `get_icon.py "<app>"` baja otra con licencia libre). Es una caja propia
con el logo en la etiqueta, nunca una copia de la pantalla de una app.

## Bloque CLIP
| Campo | Qué es |
|---|---|
| `TEXT` | lo que se escribe (hasta unos 60 caracteres; más largo se achica solo). Obligatorio |
| `APP`, `LABEL` | la app que nombra (logo + nombre en el borde) y/o una etiqueta corta ("paso dos") |
| `T_TYPE`, `T_DONE` | cuándo empieza y termina de escribirse. None = cuando dice la primera y la última palabra de TEXT |
| `SEND`, `CURSOR` | el botón de enviar y el cursor que lo aprieta 0,25 s después de escribir. False = sin ellos |
| `T_OUT` | cuándo se va. None = 0,7 s después de escribir (o el final del espacio) |
| `Y`, `WIDTH`, `SIZE` | lugar (None = franja del pecho desde layout.json), ancho y tamaño del texto |
| `SOUND` | volumen de las teclas (0 = sin teclas) |

Los subtítulos del reel se ocultan solo mientras la caja está arriba (build.py escribe esa ventana y fx_add.py la usa).

## Dónde falla
Sin espacio bajo la barbilla ni sobre la cabeza se detiene con DECLINED. Una frase muy larga queda chica: acórtala
(palabras que dijo). Deja unos 0,5 s de espacio después de la última palabra para que el cursor alcance a enviar.

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

## Versiones (`VARIANT` en el bloque CLIP)
1. **Caja**: la caja bosque (el original), superpuesta.
2. **Vidrio**: la caja en Vidrio Líquido (`engine/glass.py`): lo de atrás se ve desenfocado y en movimiento. Necesita
   la imagen debajo, así que el render es un `.mp4` normal (`slot.json` "layer" pasa a "glass" solo) y la cámara
   viva del reel se queda quieta mientras dura el espacio.

## El estilo del usuario manda
El bloque STYLE al inicio de `build.py` trae Soy Elvaras (Work Sans, Bebas Neue, Instrument Serif itálica, crema,
dorado, bosque). Antes del primer armado, ajústalo al estilo de subtítulos del reel (`effects/INDEX.md`, "Reestilizar
las palabras de un efecto").
