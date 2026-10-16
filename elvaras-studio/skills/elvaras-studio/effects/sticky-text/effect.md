# sticky-text (Etiqueta Pegada)

**Qué hace:** una etiqueta pegada al gorro de la persona, al lado de su cabeza, o a su pecho. Viaja, se inclina y escala
con la persona en cada cuadro, así que se lee como pegada a ella y no flotando en la pantalla.
**Función:** explicar (nombrar aquello de lo que habla la persona y fijarlo a ella).
**Frases que lo activan:** "pégame una etiqueta que diga X en el gorro", "pon una etiqueta en mi pecho que me siga", "pon
una etiqueta al lado de mi cabeza que se mueva conmigo".

## Toma que necesita
- **Plano:** medio o cercano para `cap` y `chest`. Abierto funciona con `head` (al lado de la persona); en un plano
  abierto una etiqueta `cap` es más ancha que el gorro (build.py avisa). Sin gorro, `cap` va sobre la frente, encima de
  las cejas (y de los lentes).
- **Cámara:** quieta, con deriva o en movimiento. En mano está bien: la etiqueta sigue a la persona, no a la pared.
- **Pared:** no hace falta para `cap` / `chest`. `head` necesita espacio vacío al lado de la cabeza dentro de la zona
  segura.
- **Recorte:** siempre se mide (silueta de la cabeza = posición y tamaño). Se usa como capa sobre la imagen solo para
  `head`, y solo mientras esa etiqueta está puesta.
- **Qué lo rompe:** una mano sobre o encima de la cabeza, una capucha o pelo largo que tapa el cuello (track.py se
  detiene: sin silueta de cabeza), una segunda persona en el recorte, la persona que sale del cuadro, un giro de cabeza
  de más de unos 40 grados (la coincidencia de giro se debilita, la etiqueta mantiene el último ángulo bueno), tela lisa
  con manos que la cruzan para `chest`.
- **Plano cercano (selfie justa):** `head` casi no tiene espacio al lado de la persona, así que sale pequeña o build.py
  la rechaza. Usa `cap`: va sobre el gorro y se dimensiona desde la cabeza. Si el gorro está dentro de los 220 px
  superiores, build.py baja la etiqueta hasta la línea de las cejas, luego la achica, y luego se detiene con un mensaje:
  usa `chest`.
- La etiqueta necesita 1,5 s en pantalla. El espacio empieza y termina en la imagen simple (las etiquetas entran en
  `IN_F` como pronto y salen 9 cuadros antes del final).

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte: OBLIGATORIO), `words.json`, `clip.json`. Sin `aroll_hi`. Las
tipografías (Inter Tight 800 / 900, JetBrains Mono) y `pop.mp3`, `whoosh-short.mp3`, `click-soft.mp3` vienen de la
plantilla. Python: solo numpy, scipy, Pillow.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `TAGS[i].text` | las palabras de la etiqueta | mayúsculas, 1 a 3 palabras: lo que dice la persona o el nombre de la cosa. Sin afirmaciones inventadas |
| `say` | la palabra dicha en que cae | como la imprime track.py; el inicio se ajusta al audio. `''` = cae en `IN_F` |
| `anchor` | `'cap'` (en el gorro / la frente, sobre las cejas), `'head'` (al lado de la cabeza, escondida detrás de ella), `'chest'` (bajo la barbilla) | plano cercano: `cap`. Abierto: `head`. Pecho visible sobre y 1470: `chest` |
| `at` | segundos, reemplaza `say` | solo si el inicio impreso está mal |
| `small`, `sub`, `sub_say` | línea pequeña opcional sobre la palabra, segunda línea oscura opcional bajo la etiqueta y la palabra en que cae | por defecto ninguna. Solo cuando la persona dice una segunda cosa |
| `side` | solo `head`: `'left'`, `'right'`, `'auto'` | `auto` = el lado con más espacio |
| `offset`, `tilt`, `size` | ajuste fino en px, grados en el cuadro de llegada, factor de tamaño sobre el tamaño automático | déjalos fuera primero; ajústalos después de la instantánea |
| `out` / `OUT` | segundos en que sale una etiqueta / todas | `None` = 9 cuadros antes de que termine el espacio |
| `IN_F` | primer cuadro en que puede aparecer una etiqueta | 4 |
| `BROW`, `HEAD_H` | línea de las cejas (fracción del alto de la cabeza) y alto / ancho de la cabeza | por defecto; cámbialos solo si las líneas azules de sheet.jpg no calzan con las cejas / la barbilla |
| `TAG_COL`, `INK`, `CREAM` | colores de etiqueta, texto, subtexto | colores de marca (dorado, tinta, crema), nunca naranjo |
| `GRADE` | filtro CSS sobre la imagen | `'none'` (el reel da el color) |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las líneas `small` y `sub`, mantiene la etiqueta.
`SFX=0` sin pop / whoosh.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" track.py      # mide la cabeza, el pecho y los inicios de palabra (cerca de 30 s); lee lo que imprime
# editar: el bloque CLIP en build.py, luego arma con la guía puesta; corrige cada línea que empieza con !!
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.0,2.2,3.8      # instantánea en la llegada + 0,3 s, al medio, y 0,5 s antes del final (tiempos en segundos)
PY "SK/scripts/fx_run.py" "<slot>" build.py      # arma sin la guía, luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # números, hoja, recortes de fijación, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 4,5 s toma unos 5 minutos de punta a punta una vez que existe el recorte (track 40 s, render 20 s).

## Qué mirar (work/check/)
- `lock.jpg`: seis recortes centrados en aquello a lo que está pegada la etiqueta. La etiqueta queda en el mismo lugar
  de la persona en cada uno; una etiqueta que nada = seguimiento débil (calidad de coincidencia de track.py bajo 0,35).
- `sheet.jpg`: el cuadro con el mayor movimiento de cabeza está ahí. La etiqueta sobre la línea azul de las cejas
  (`cap`) o bajo la línea azul de la barbilla (`chest`); ojos, nariz y boca nunca tapados. Nada pasado las líneas rojas.
- check.py imprime qué cuadros difieren de la toma: el cuadro 0 y el último tienen que ser simples.
- `head`: el borde del recorte sobre la etiqueta está limpio, sin borde claro, sin borde doble (borde doble = desfase de
  cuadros del recorte).

## Trampas
- Los inicios de palabra de Whisper están 0,1 a 0,3 s corridos: usa `say` (track.py lo ajusta al audio, preciso a unos 3
  cuadros). Si la etiqueta cae antes o después en el render, pon `at=` en segundos.
- Una cámara que se balancea y lleva el gorro a los 220 px superiores por un momento descarta `cap` y `head` en todo el
  tramo (build.py lo dice). `chest` igual funciona, o acorta el espacio.
- El giro del pecho se amortigua a propósito (mediana, suavizado largo, dentro de 8 grados de la cabeza): los pliegues
  de la tela y una cámara baja simulan un giro.
- La posición sale de la silueta, el giro de una coincidencia de plantilla contra un cuadro de referencia. El flujo
  óptico sobre una cabeza deriva y falló en la demo; un punto de pose de cara se deslizó 40 px respecto del gorro.
- El suavizado es leve a propósito (posición 0,8 cuadros, giro y tamaño 1,6). Más y la etiqueta se atrasa respecto de la
  cabeza.
- El arreglo de zona segura es un desplazamiento constante, nunca un límite por cuadro (un límite por cuadro despega la
  etiqueta).
- Las instantáneas buscan de forma aproximada durante la entrada: juzga el tiempo de llegada en cuadros del render real.
- En pantalla: solo las palabras de la persona, sin nombres ni números inventados, sin guiones largos, sin naranjo.
