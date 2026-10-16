# timeline-burn (Línea en Llamas)

**Qué hace:** una línea de tiempo de edición de video se arma delante de la persona (tercio inferior, bajo la barbilla),
un cursor hace dos ediciones lentas, la línea de tiempo se recalienta, se prende fuego en una palabra dicha, se quema de
derecha a izquierda y se deshace en brasas. Luego vuelve la imagen simple.
**Función:** gancho (también un remate a mitad de video: "ya no necesitas X", "X se acabó").
**Frases que lo activan:** "pon una línea de tiempo de edición y quémala cuando digo X", "quema la línea de tiempo en
X", "línea en llamas".

## Toma que necesita
- **Plano:** abierto o medio. En el espacio de 1080x1920 la barbilla tiene que estar sobre y 980 aprox. para la línea de
  tiempo más una línea de subtítulos, sobre y 1100 aprox. para la línea de tiempo sola. Cercano falla: con la cara tan
  baja no hay espacio bajo ella dentro de la zona segura y `build.py` se detiene con "No room for the timeline".
- **Cámara:** quieta, con deriva o en movimiento. No se sigue nada: la línea de tiempo es una capa de pantalla y no se
  pega al cuarto.
- **Pared:** ninguna.
- **Recorte:** solo se mide (la caja de la cabeza se lee de `assets/subject.webm` para que nunca se dibuje nada sobre la
  cara). No va como capa: la línea de tiempo está delante de la persona y las manos que bajan tanto pasan por detrás.
  Escribe `FACE` y el espacio se puede crear con `--no-cutout` (útil si el recorte mezcla la ropa con la silla).
  `aroll_hi` no se usa.
- **Lo rompe:** un espacio con menos de 30 cuadros antes de la palabra del fuego o menos de 30 después; una cara que baja
  de y 1100 durante el espacio; una mano en la cara, una capucha, pelo largo o una rodilla levantada (la caja de la
  cabeza se vuelve una suposición: `build.py` lo dice, escribe `FACE`); una imagen clara y recargada con `DIM = 0` (el
  fuego se lee mejor en una toma oscura u oscurecida).
- **Bordes:** el cuadro 0 y el último son el clip sin tocar. El efecto empieza en `F_IN` y todo, atenuación incluida, se
  fue 28 cuadros después del fuego. No puede terminar en el fuego: el espacio tiene que seguir 30 cuadros después de la
  palabra del fuego.
- Python: numpy, scipy, Pillow. Sin paquetes extra, sin modelo propio, sin material incluido.

## Palabras, subtítulos y el estilo del reel
- Las palabras que dibuja (nombres de pistas, códigos de tiempo, nombres de clips opcionales) **son el efecto**, no
  habla. No dibuja palabras dichas, así que no hay interruptor de subtítulos que apagar: los subtítulos del reel
  **siguen corriendo** durante el espacio.
- La línea de tiempo va donde van los subtítulos del pecho. `build.py` imprime `fx_add.py --caption-y N`: los subtítulos
  del reel suben a la línea sobre la línea de tiempo durante el espacio. Cuando no hay espacio para esa línea lo dice:
  agrega el espacio con `--captions hide` en su lugar (el único caso en que los subtítulos se pausan).
- **Bloque `STYLE`** (inicio de `build.py`, sobre el bloque CLIP): `FONT`, `WEIGHT`, `CASE`, `TEXT`, `LABEL_PX`,
  `NAME_PX`, `ACCENT`, `PANEL`, `PANEL_EDGE`, `PALETTE`. Cuando el reel tiene un estilo de subtítulos o completo, pon
  aquí tipografía, mayúsculas, grosor y colores ANTES del primer armado (`ACCENT` = el color de acento del reel,
  dorado). El fuego sigue color fuego. La ubicación es `PANEL_W` / `PANEL_X` / `PANEL_Y` en el bloque CLIP.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `BURN_AT` | la palabra dicha en que se prende fuego (`'palabra'`, `'palabra#2'` = la segunda vez), o un cuadro | `build.py words`. Obligatorio: el armado se detiene hasta que se pone |
| `F_IN` | cuadro en que se arma la línea de tiempo | `None` = 72 cuadros antes del fuego. 30 como mínimo; bajo 69 se omiten las ediciones del cursor |
| `TRACKS` | un diccionario por pista, de arriba abajo (2 a 6): `label`, `kind` (`'video'`, `'title'`, `'audio'`), `color`, `clips`, `names` | `clips` = una cantidad (repartida desde `SEED`) o `(inicio, fin[, 'nombre'])` de 0 a 1 |
| `TRACKS[..]['names']` | palabras opcionales en los clips | palabras propias de la persona, cortas; `[]` = ninguna. Son pequeñas por naturaleza: decoración, no subtítulos |
| `RULER` | códigos de tiempo sobre las pistas | `'auto'`, tu propia lista de hasta 8, o `None` para solo rayitas |
| `EDIT` | el cursor que recorta un clip y arrastra otro | `False` = sin cursor |
| `DIM` | cuánto se oscurece la imagen mientras la línea de tiempo está arriba | 0 = apagado, 0,4 por defecto, 0,6 oscuro. Entra suave y vuelve antes de que termine el espacio. 0 cuando el look del reel ya es oscuro |
| `PANEL_W`, `PANEL_X`, `PANEL_Y` | ancho, x central, y superior de la línea de tiempo | 848 / 540 / `None` (medido: lo más abajo que permite la zona segura) |
| `CAPTION_ROOM` | px que se dejan entre la barbilla y la línea de tiempo para la línea de subtítulos del reel | 130; 0 = no se deja |
| `FACE` | `(x0, y0, x1, y1)` caja de la cabeza durante todo el efecto | `None` = medida; léela en `work/layout.jpg` cuando la caja roja está mal (con lentes, revisa la barbilla) |
| `SEED`, `VOICE`, `SOUNDS` | composición / grietas / brasas; el audio de la persona; lista de sonidos | por defecto |

**Interruptores:** `SAFE=1` guía de zona segura (solo instantáneas), `SFX=0` sin sonidos, `DIM=0` sin oscurecer.
`CAPTIONS=0` no cambia nada (no hay palabras de subtítulo que sacar). No tiene color propio.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py words      # 1. cada palabra con su cuadro -> BURN_AT en el bloque CLIP; el estilo del reel -> el bloque STYLE
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 2. mide la cara, ubica la línea de tiempo, página con la guía. Lee las líneas !!, MIRA work/layout.jpg
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores (un aviso de "file too large" es normal)
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos que imprimió build.py>
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 3. guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 4. cantidad de cuadros, bordes simples, cuadro del fuego, cara, zona segura, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 5 s toma unos 5 minutos después del recorte.

## Qué mirar (work/check/sheet.jpg)
- Primer y último cuadro, el cuadro antes de `F_IN` y el cuadro 28 después del fuego: el clip simple (`check.py`
  imprime la diferencia).
- El destello está en el cuadro del fuego y el cuadro anterior no tiene ninguno. Di la frase en voz alta contra la copia
  para celular: el fuego empieza en la palabra.
- La línea de tiempo y cada brasa quedan bajo la barbilla y dentro de la zona segura (línea roja = y 1470; nada a la
  derecha de x 980 bajo y 1155).
- En el reel: una instantánea dentro del espacio. Los subtítulos del reel van en la línea sobre la línea de tiempo, en
  el estilo del reel, nada repetido.

## Trampas
- El cuadro de la palabra: `build.py words` ajusta cada palabra a donde la voz sube desde una caída, e imprime al lado la
  estimación de la transcripción. En habla rápida los dos pueden diferir en 5 cuadros. Confírmalo con
  `PY build.py level <desde> <hasta>` (barras por cuadro) y escribe el cuadro en `BURN_AT` cuando la palabra está mal.
  Un cuadro antes es mejor que uno tarde.
- Con menos de 72 cuadros antes del fuego el calentamiento se aprieta, con menos de 69 se van las ediciones del cursor.
  El chiste completo necesita 2,4 s: empieza el espacio con suficiente anticipación.
- Las etiquetas largas se dibujan pequeñas (la columna de etiquetas mide 70 px): 4 caracteres o menos. Un nombre que no
  cabe en su clip se omite y se informa.
- Genérico a propósito: sin nombre de app, logo ni interfaz real. Las palabras en pantalla son de la persona: sin
  números, nombres ni usuarios inventados, sin guiones largos.
- Sonidos: solo `whoosh-short`, `click`, `impact-bass-1` de stock, a 0,75x del volumen de la plantilla. `SOUNDS = []`
  cuando el reel tiene su propio golpe en esa palabra.
- Después de cambiar `BURN_AT`, `F_IN`, `TRACKS` o `FACE`, ejecuta `build.py` de nuevo y lee el `--caption-y` impreso:
  se mueve con la composición.
