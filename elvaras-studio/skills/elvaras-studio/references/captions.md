# Subtítulos: los 20 estilos, las marcas de palabras, dónde van

Un solo motor (`SK/engine/captions.py`), 20 estilos, todos manejados por el mismo `words.json`. `build_reel.py` elige
el estilo según las elecciones guardadas. Nunca editas el motor para un reel: limpias las palabras, las marcas y
escribes el título. Un usuario con estilo propio (un ejemplo que mostró, un look que describió) usa en cambio un
estilo de subtítulos a medida, una especificación que el mismo motor dibuja: `references/replicate.md`. Las marcas y
las franjas de abajo funcionan igual.

Todos los estilos usan por defecto los colores de Soy Elvaras: texto crema #F2ECDF y acento dorado #C9A15B donde el
original usaba blanco y amarillo.

## Los 20

| Clave | Nombre | El look | Usa las marcas | Dónde va | Necesita |
|---|---|---|---|---|---|
| `arcade` | Arcade | Letra pixelada crema, frases cortas, cortes secos | cta aparece al doble de tamaño entre comillas | pecho | |
| `low-key` | Discreto | Subtítulos pequeños y tranquilos que se arman palabra por palabra, bajo un título fijo en cápsula | | pecho + título arriba | un título |
| `field-notes` | Bitácora | Serif de libro tranquila, frases completas que aparecen suaves, cada una en un espacio libre distinto | | pared libre izquierda / pecho / pared libre derecha | pared libre al lado de la persona (si no, va al pecho) |
| `anchor` | Noticiero | Sans gruesa y limpia en un solo lugar, cortes secos | num y emph toman el cuadro con brillo, cta cae debajo en itálica | pecho | |
| `loud-lowercase` | Minúscula Gigante | Minúsculas enormes y apretadas, una palabra a la vez | num queda arriba a la izquierda con lo que cuenta, cta en mayúsculas | pecho + arriba a la izquierda | |
| `vanity` | Tocador | Serif alta en crema, una palabra a la vez | toda palabra marcada pasa a itálica dorada, key lleva un ícono pequeño, cta entre comillas | pecho | |
| `bubblegum` | Chicle | Una palabra brillante sobre la cabeza, título con trazo | key mantiene su mayúscula | sobre la cabeza + título | espacio sobre la cabeza (si no, va al pecho), un título con trazo |
| `moodboard` | Moodboard | Línea gruesa redondeada, línea itálica fina escrita debajo, destellos | key mantiene su mayúscula | pecho | |
| `golden-hour` | Hora Dorada | Subtítulos de cine en itálica dorada | cta entre comillas | tercio inferior | |
| `spec-sheet` | Ficha Técnica | Mayúsculas anchas y pequeñas al centro, etiquetas doradas inclinadas | num y cta pasan a etiquetas arriba a la izquierda | pecho + arriba a la izquierda | |
| `bold` | Contundente | Minúsculas gruesas, palabras grandes DETRÁS de la cabeza | num / emph / cta van gigantes detrás de la cabeza (emph y cta en dorado) | pecho + detrás de la cabeza | recorte limpio, espacio sobre la cabeza (si no, la palabra grande cae sobre el pecho) |
| `cool-girl` | Relajada | Minúsculas pequeñas y calmas, una línea grande en serif itálica dorada por idea | num / emph / cta son la línea grande | pecho (un bloque alto) | |
| `cool-dude` | Elegante | Mayúsculas diminutas y espaciadas sobre una palabra serif gruesa | num / emph / cta son la palabra serif | pecho (un bloque alto) | |
| `karaoke` | Karaoke | Mayúsculas anchas sobre placa bosque esmerilada, la palabra dicha se ilumina | | pecho | |
| `signature` | Firma | Mayúsculas anchas y limpias; una firma a mano sobre mayúsculas itálicas gruesas | num y cta tienen el momento de la firma | pecho | |
| `keyword` | Palabra Clave | Una línea limpia en minúsculas | toda palabra marcada va en dorado; una palabra marcada sola va más grande | pecho | |
| `weight-shift` | Contraste | Entrada fina, palabra de golpe gruesa | num / emph / cta son el golpe | pecho (un bloque alto) | |
| `terminal` | Terminal | Entrada en letra de código, una palabra grande en serif itálica | num / emph / cta son el golpe | pecho (un bloque alto) | |
| `outline` | Contorno | Mayúsculas altas y condensadas, la palabra de golpe dibujada hueca | num / emph / cta son el golpe | pecho (un bloque alto) | |
| `negativo` | Negativo | Minúsculas enormes en Work Sans 900 que muestran el negativo de lo que hay detrás (oscuras sobre una pared clara, claras sobre lo oscuro, colores invertidos sobre la persona); una palabra grande por frase y las chicas al lado | toda palabra marcada hace de palabra grande y va DETRÁS de la cabeza; en una frase sin marca, la palabra más larga es la grande y va adelante sobre el pecho | detrás de la cabeza + pecho | recorte limpio y espacio sobre la cabeza (si no, todo va al pecho). No va sobre un estilo completo. El color no es de marca: es el inverso de lo que hay detrás |

`none` = sin subtítulos (solo títulos y efectos).

Negativo dibuja cada frase dos veces: una copia en modo *overlay* empuja la imagen bajo las letras a sus extremos y la
de encima, en modo *diferencia*, la da vuelta. Solo con diferencia, una pared de tono medio (como el crema de la pieza)
deja las letras grises y casi invisibles. Un efecto que mueve la capa de subtítulos (`caption_y`) la deja como letras
blancas mientras dura, sin el negativo.

## Marcar las palabras (en cada reel)

Cada palabra de `words.json` puede llevar una marca en su campo `e`. Las marcas son las que hacen que un estilo de
subtítulos se vea diseñado y no tipeado.

| Marca | Significado | Cuándo marcarla |
|---|---|---|
| `num` | un número que vale la pena mostrar grande | el número ES el punto de la frase: "7 efectos de video", "$500 al día", "10x". No para números de paso ("una de las cosas", un año, una hora). |
| `key` | un nombre o una marca | todo producto, app, empresa o persona dicha por su nombre: "Claude", "Instagram". Mantiene su mayúscula en los estilos en minúscula y va en dorado en Palabra Clave. |
| `emph` | la palabra en la que se apoya la frase | una oración sin número ni palabra para comentar, donde una palabra la carga ("nunca", "automáticamente", "todo"). La palabra que acentuarías en voz alta. |
| `cta` | la palabra para comentar | la palabra que pide comentar: "comenta EDIT". Exactamente una por reel. |

La regla:
1. Ejecuta `PY "SK/scripts/marks.py" "<project>"` DESPUÉS de corregir lo mal escuchado. Propone `num` (dígitos y
   números escritos, en español o inglés), `cta` (la palabra después de "comenta" / "comment") y `key` (palabras con
   mayúscula que no empiezan una oración). Nunca propone `emph`.
2. Luego recorre la transcripción oración por oración:
   - como máximo UNA de `num` / `emph` por oración (son el golpe; dos golpes pelean). Deja la que trata la oración y
     saca la otra. Una oración larga cuenta por partes: una coma, "y", "luego" o "entonces" empieza una parte nueva.
   - la palabra para comentar SIEMPRE mantiene su marca `cta`, aunque su oración ya tenga `num` o `emph` (un reel de
     una oración: "consigue los 21 efectos, y solo comenta VIDEO" mantiene `21` num y `VIDEO` cta).
   - `key` en cada nombre, todos los que haya. Revisa a mano las palabras que abren oración: el script no distingue un
     nombre que empieza una oración de una palabra normal (las lista).
   - agrega `emph` donde una oración todavía no tiene golpe y una palabra claramente lo carga. No toda oración lo
     necesita.
   - nunca marques relleno ("el", "la", "y", "que", "para", "the", "and").
3. Un reel corto (menos de 10 segundos) suele terminar con 2 a 5 marcas. Más de una marca cada 4 palabras es
   demasiado.

Ejemplo: "Todos hablan de que Claude edita videos, así que aquí van siete efectos de video que Claude creó para mí."
-> `Claude` key, `siete` num (escríbelo `7` si el estilo muestra los números grandes), segundo `Claude` key.

```json
{"text": "7", "start": 3.18, "end": 3.52, "e": "num"}
```

## Los títulos salen del gancho (Titles come from the hook)

`plan.json` (lo empieza `init_project.py` con una primera propuesta; reescríbelo):
- `"title": ["línea uno", "línea dos"]`: el gancho del reel en dos líneas cortas, hasta unos 26 caracteres cada una,
  en minúsculas normales. Discreto lo deja fijo arriba todo el reel. Los estilos completos lo usan como titular de
  respaldo.
- `"swash": ["Línea Uno", "Línea Dos"]`: la misma idea, más corta (hasta unos 16 caracteres por línea), con mayúscula
  inicial en cada palabra. El título de Chicle.
Escribe lo que el reel promete, con las palabras de la persona: "7 efectos de video" / "que Claude hizo para mí". No
un resumen, ni un anzuelo que no dijo.

## Dónde van los subtítulos (se calcula por clip, nunca se escribe a mano)

`PY "SK/scripts/layout.py" "<project>"` toma muestras del reel, recorta a la persona solo en esos cuadros, lee la
cabeza desde la silueta y escribe `layout.json`. Mira `work/layout/check.jpg` una vez (hasta cuatro cuadros, a la
mitad del tamaño): la caja verde tiene que ir de lo alto de la cabeza a la barbilla, y sus números están impresos
debajo. Las líneas azules son las franjas, el rojo es la zona segura de Reels. Cuando el recorte limpio está
instalado (`setup.py --matting`) las muestras se recortan con él, lo que toma cerca de un minuto y no se confunde con
lo que cuelga detrás de la cabeza.

| Franja | En `bands` | Regla | Cuando no hay espacio |
|---|---|---|---|
| Sobre la cabeza | `Y_ABOVE_HEAD` | 104 px sobre la posición más alta de la cabeza, nunca sobre y 236 | `null`: la palabra de Chicle va sobre el pecho |
| Detrás de la cabeza | `HEAD_TOP` | la palabra grande de Contundente muestra el 72% de su alto sobre la cabeza, achicándose para caber bajo y 226 | menos de 110 px de letra: la palabra cae sobre el pecho, adelante |
| Pecho | `Y_CHEST` | y 1170, siempre que la barbilla esté al menos 100 px más arriba | la cara está baja o llena el cuadro: la imagen se sube (hasta 260 px, `lift`) y los subtítulos toman la franja del cuello bajo la barbilla. `fits.chest` dice `tight`: solo estilos de una línea |
| Tercio inferior | `Y_LOWER` | y 1376 (una línea termina en 1452) | el mismo lift |
| Pared libre | `WALL_LEFT`, `WALL_RIGHT` | al lado de la persona a la altura de la cara, al menos 240 px de ancho | `null`: Bitácora usa los lugares que existen |

Los acercamientos mueven la cabeza entre tramos: las franjas son las que quedan seguras en todos los tramos, y
Contundente lee la altura de la cabeza del tramo en que cae cada palabra.

El recorte rápido se puede confundir: un cuadro, póster o lámpara justo detrás de la cabeza se une a la silueta y la
caja parte unos 100 px más arriba y se detiene en la nariz. Los lentes producen el mismo error (la caja termina en la
nariz). `layout.py` imprime `CHECK THE HEAD BOX` cuando no encontró un cuello bajo la cabeza (la señal típica, también
normal con pelo largo o capucha), y `fx_new.py` / `fx_add.py` imprimen `CHECK layout.json` cuando el recorte limpio
de un efecto difiere en más de 60 px. En cualquier caso: si `check.jpg` muestra la caja verde fuera de la cara (muy
alta, un póster, una segunda persona, cortada en la nariz), ejecuta `setup.py --matting` una vez y `layout.py` de
nuevo, o corrige `head` y `bands` en `layout.json` a mano. Son números simples en el cuadro de 1080x1920. Contundente,
Chicle, Bitácora y la caja de la cara de la autorrevisión los leen.

Los estilos altos (Relajada, Elegante, Contraste, Terminal, Contorno) apilan tres líneas desde unos 70 px sobre
`Y_CHEST`. Con una franja de pecho `tight` avísale al usuario y usa un estilo de una línea para ese reel.
