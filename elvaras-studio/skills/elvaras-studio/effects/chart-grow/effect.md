# chart-grow (Gráfico que Crece)

**Qué hace:** un gráfico de línea se dibuja solo en la pared DETRÁS de la persona: grilla, una línea plana con pequeñas
ondulaciones, y luego la línea se dispara en el color de acento en una palabra dicha. El cuarto se atenúa un poco
mientras está arriba.
**Función:** prueba (crecimiento, resultados, "despegó"). **Frases que lo activan:** "dibuja un gráfico de crecimiento
detrás de mí que se dispare cuando digo escalar", "pon un gráfico detrás de mí en esta frase", "haz que la línea suba
cuando digo X".

## El gráfico es una afirmación: solo la forma por defecto
Una línea que sube dice "esto creció". Por defecto dibuja una FORMA y nada más: sin números en los ejes, sin
etiquetas de valores, sin moneda, sin porcentaje, sin título. `FIGURES`, `X_LABELS` y `TAG` están apagados. Enciéndelos
solo con lo que te entrega la persona: sus propios números reales, los nombres reales de los períodos, una palabra que
dice. **Nunca inventes, estimes ni redondees hacia arriba un número.** Si no tiene cifras, la forma es todo el efecto.
Con `FIGURES` la línea se dibuja a escala desde cero, así que números que no se disparan no se verán como un disparo
(build.py avisa: entonces es el efecto equivocado, no tuerzas los números).

## Toma que necesita
- **Plano:** abierto o medio. **Cercano:** solo si un pedazo de pared de unos 330 x 280 px queda libre de la persona
  durante todo el espacio; si no, build.py se detiene con `NO OPEN WALL` y el efecto queda fuera de ese clip.
- **Cámara:** quieta (el gráfico queda fijo) o con deriva / en mano (el gráfico se pega a la pared con el seguimiento
  propio de measure.py, solo numpy). **En movimiento** (caminando, paneos, más de unos 16 px por cuadro) rompe el
  seguimiento.
- **Pared:** al lado, arriba o ambas. Lo mejor: pared libre arriba a la derecha de la cabeza, donde termina la línea.
  Sin pared = se detiene.
- **Recorte:** como capa (el gráfico va entre la imagen y el recorte) y medido (el gráfico se ubica desde él).
- **Qué lo rompe:** selfies cercanas; manos que cruzan arriba a la derecha durante el disparo (el gráfico se achica a
  la pared libre o se detiene); una pared sin textura con cámara en mano (nada que seguir: el gráfico flota); la
  palabra del disparo en el primer segundo del espacio (sin parte plana desde donde crecer); menos de 1,5 s de toma
  después de la palabra.
- Ubicación: `'behind'` = todo el ancho seguro, la parte plana pasa detrás de la cabeza (esa es la señal de
  profundidad), la curva, el disparo y el punto final se mantienen fuera de la persona en cada cuadro (62 / 40 / 70 px
  si la pared lo permite, 34 / 26 / 70 px como mínimo). Si eso no cabe: `'beside'` = un gráfico más pequeño en el
  pedazo de pared más grande. Si eso tampoco cabe: se detiene.

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte OBLIGATORIO), `words.json`, `clip.json`. Sin `aroll_hi`. Las
tipografías (Inter Tight, Montserrat) y cuatro sonidos de stock (`whoosh-short`, `pop`, `impact-bass-1`, `sparkle`)
vienen de la plantilla. Python: solo numpy, scipy, Pillow.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `KICK` | la palabra en que despega la línea; `('palabra', 2)` = segunda vez; o un número de cuadro | measure.py imprime cada palabra con su cuadro de inicio medido; `-v` muestra la tira de volumen |
| `KICK_LEAD` | cuadros que el disparo empieza antes de la palabra | 2 (la línea ya se mueve cuando llega la palabra) |
| `SHAPE` | altura de cada punto, 0 a 1 | deja el valor por defecto; plano primero, el último punto el más alto, disparo al menos 2,5x la ondulación |
| `KICK_FROM` | índice del punto desde donde se dispara | 4 con los 7 puntos por defecto |
| `FIGURES` / `FIGURE_FMT` / `FIGURE_AT` | los números propios de la persona (uno por punto), cómo se leen, qué puntos muestran uno | APAGADO. Solo de la persona, exactamente como los dio |
| `X_LABELS` | nombre del período por punto | APAGADO. Solo reales |
| `TAG` | una palabra dicha en una cápsula sobre la curva | APAGADO. Nunca un resultado como "3X" |
| `SIT` | `'auto'`, `'behind'`, `'beside'` o `(x0, y_top, x1, y_floor)` | deja `'auto'`; a mano solo después de mirar la instantánea |
| `IN_FRAME` / `OUT_FRAME` | primer cuadro en que se ve algo / cuadro en que ya se fue todo | 3 y `'auto'` (4 antes del final). `None` = el espacio termina en un corte y el gráfico se queda hasta el último cuadro |
| `DRAW_START` | cuándo empieza la parte plana | `'auto'`, una palabra, o un cuadro |
| `ACCENT` / `LINE` | color del disparo / color de la línea, la grilla y las etiquetas | color de marca (dorado #C9A15B); nunca naranjo, nunca gris (build.py avisa) |
| `DIM` | cuánto retrocede el cuarto | `'auto'` desde el brillo medido de la pared (0.38 a 0.68) |
| `LOCK` | pegar a la pared | `'auto'` desde la deriva medida de la cámara |
| `PUNCH`, `GRADE`, `SFX_LEVEL` | acercamiento en el disparo, color CSS, volumen de los sonidos | 1.0, `'none'`, 1.0 (los dos primeros apagados: los hace el reel) |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas). `CAPTIONS=0` saca `TAG`. `SFX=0` saca los sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # palabras con cuadros de inicio medidos, dónde está la persona, cámara quieta o en movimiento (cerca de 1 minuto)
# editar: el bloque CLIP en build.py: KICK como mínimo. FIGURES, X_LABELS y TAG quedan apagados salvo que la persona dé unos reales
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # imprime el cuadro del disparo, dónde va el gráfico, márgenes; cada aviso empieza con !!
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 1.2,3.0,3.6      # usa tus propios tiempos: mitad del dibujo, disparo + 0,15 s, llegada + 0,3 s
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # guía apagada (tiene que imprimir "clean")
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, primer y último cuadro simples, cuadro del disparo contra la palabra, volumen del sonido, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 5 s: el recorte toma unos 8 minutos en Mac (unos 1-2 aquí), luego todo el orden de ejecución unos 4
(medir 1, render 1).

## Qué mirar (work/check/sheet.jpg, luego un cuadro a tamaño completo)
- El disparo: nada en el color de acento un cuadro antes del cuadro del disparo, subiendo claramente en la palabra,
  llegando unos 0,45 s después. check.py imprime el cuadro en que aparece el color por primera vez.
- El punto final y todo el disparo están sobre pared libre, nunca detrás de la cabeza o de una mano. La parte plana
  puede pasar detrás de la cabeza; tiene que volver a salir antes de la curva.
- El primer y el último cuadro son la imagen sin tocar (check.py imprime la diferencia; con `OUT_FRAME = None` solo el
  primero).
- Borde del recorte contra la pared atenuada: sin borde claro, pelo y dedos completos. Un borde en una pared clara:
  baja `DIM`.
- En pantalla no hay nada que leer salvo lo que dio la persona. Punto final, etiqueta y cifras dentro de la zona segura
  (arriba 220, abajo 1470, lados 35, derecha 100 desde y 1155): build.py lista cada uno.
- En mano: la grilla se queda en la pared (mira un cuadro o una esquina contra una línea de la grilla durante el
  espacio).

## Trampas
- Los inicios de palabra de Whisper llegan hasta 0,35 s antes. Nunca los escribas: measure.py los ajusta a la subida
  de la voz. Una palabra con "no clear rise" necesita la tira `-v`.
- La línea plana se esconde detrás de la cabeza a propósito, así que un cursor y un rastro punteado llevan el barrido.
  No lo "arregles" subiendo toda la línea sobre la cabeza: una franja delgada ahí arriba se lee como plana en un
  celular.
- Una pared clara necesita la atenuación o la línea desaparece; `'auto'` lo maneja. No pongas `DIM` bajo 0,3 en una
  pared blanca.
- La punta de la línea es un fotograma clave lineal por cuadro (`perFrame`), calculado en Python. No lo reemplaces con
  animaciones suavizadas: el desplazamiento del punteado y el punto se separan.
- Los sonidos siguen la voz medida: build.py los baja hasta que el más fuerte quede 8 dB bajo la palabra más fuerte de
  la persona (una voz baja en plano abierto recibe sonidos más bajos). Nadie ha escuchado la mezcla hasta que la
  reproduzcas.
- `NO OPEN WALL` es una respuesta, no un error: usa otro efecto en ese clip. `SIT` a mano es para una persona que
  acepta tapar parte de la línea.
- Texto en pantalla: solo las palabras y números propios de la persona, sin guiones largos, nunca las palabras
  "gratis" o "curso".
