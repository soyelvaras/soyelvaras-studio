# knockout-tiles (Fichas Fuera)

**Qué hace:** fichas con nombres caen de golpe en la pared detrás de la persona, una por palabra dicha; cada una se
tacha y sale volando (cae, se lanza o se rompe) cuando llega la siguiente. Segunda mitad opcional: se apilan recibos al
lado de la cabeza mientras un total los va sumando, y luego la pila se tacha y cae.
**Función:** explicar / prueba ("no necesitas X, Y ni Z", "deja de pagar por A, B y C", cualquier lista dicha que se va
tachando).
**Frases que lo activan:** "pon estos tres nombres en la pared detrás de mí y saca cada uno cuando lo digo",
"táchalos detrás de mí", "apila los recibos y muestra cuánto suman".

## Las cuatro versiones (`VARIANT`)
| n | nombre | cómo se ve |
|---|---|---|
| 1 | Etiqueta de precio | etiqueta de papel con hilo y agujero, nombre en mayúsculas; sale tachada |
| 2 | Post-it a mano | papel con cinta y nombre escrito a mano; sale con una X |
| 3 | Ventana que se cierra | ventana de programa con barra y botón de cerrar; se raja en dos y las mitades caen |
| 4 | Íconos | íconos de app en una fila (una baldosa de marca con la inicial y el nombre debajo, nunca un logo real); aparecen en su palabra, UNA línea dorada los tacha a todos, caen con gravedad detrás de la persona y en su lugar aterriza una palabra en serif cursiva |

Se elige en el Studio Picker con los puntitos bajo la tarjeta; `fx_new.py` escribe la versión guardada en la línea
`VARIANT`. Colores y letras salen del bloque `STYLE` (`paper`, `paper_ink`, `deep`, `strike`, `name_font`, `hand_font`,
`ui_font`), así que sirven para la marca de cualquier cliente.

### Versión 4, Íconos
- Todos los íconos quedan arriba juntos hasta `STRIKE_AT` (por defecto 12 cuadros después del último); la línea los cruza
  en 6 cuadros, de izquierda a derecha, y cada ícono se lleva su pedazo al caer (caen con 3 cuadros de diferencia).
- `prep.py` busca una fila libre de la persona: primero sobre la cabeza, si no al lado; achica los íconos antes de
  dejar que la persona los roce. 2 a 5 íconos.
- `WORD` (una palabra que la persona dice, como "programa.") aterriza donde estaban, en el espacio libre de ese lado de
  la cabeza mientras dura; con `word_color = 'auto'` sale verde bosque sobre una pared clara y crema sobre una oscura.
  `WORD_AT` / `WORD_OUT` la mueven; `WORD = ''` la apaga.
- La inicial sale del nombre (dos palabras = dos iniciales: "Adobe Premiere" = AP). Colores en `STYLE['icon_palette']`.
- Sin recibos ni total en esta versión. Sonidos: un pop por ícono y un whoosh en la línea.
- `check.py` puede marcar "something is over the face" cuando la persona se mueve mucho: el leve acercamiento (`ZOOM`)
  cambia la cara aunque nada la tape. Mira los cuadros de `work/check/sheet.jpg`; con `ZOOM = 1.0` la alerta se va.

## Primer paso: solo nombres y montos propios de la persona
Cada ficha es un nombre que la persona dice en este clip o que te dio el usuario. Cada monto en un recibo es uno que
dijo o entregó; el total lo suma el armado, nunca se escribe a mano. Nunca inventes un nombre, un precio o una
cantidad, y nunca dibujes un logo: las fichas son texto simple. Sin lista en la frase = deja fuera este efecto. Los
valores por defecto del CLIP ("Herramienta uno", "Recibo", 0) son de relleno; `build.py` avisa mientras sigan ahí.

## Toma que necesita
- **Plano:** abierto o medio, con pared alrededor de la cabeza. Cada ficha necesita unos 400 x 150 px de pared libre al
  lado o sobre la cabeza, dentro de la zona segura. Cercano falla: `prep.py` se detiene con "no clear wall".
- **Cámara:** quieta. Una deriva lenta está bien (una ficha está arriba menos de un segundo). Una cámara en movimiento
  lo rompe: las piezas no se siguen con el cuarto.
- **Pared:** al lado de la cabeza para fichas y recibos, arriba para la tercera ficha y el total. Sin pared arriba = las
  fichas alternan izquierda / derecha y el total necesita `TOTAL_POS` o queda apagado.
- **Recorte:** como capa y medido. `assets/subject.webm` va sobre las piezas, y la posición de la cabeza, su
  movimiento y la pared libre se leen de su alfa. `aroll_hi` no se usa.
- **Lo rompe:** un recorte que pierde pelo o conserva un pedazo de pared (la pieza se ve a través, o la corta un borde
  fantasma), dos personas en la toma, grandes movimientos de brazos a la altura de la cabeza mientras hay una ficha
  arriba, un espacio que corta a otra toma.
- **Bordes:** el cuadro 0 y el último son el clip sin tocar. El efecto se enciende en `F_IN` (5 cuadros antes de la
  primera ficha) y ya se fue en `F_OUT`; no tiene color, atenuación ni acercamiento.

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy, Pillow. Sin paquetes extra, sin arte, solo sonidos
de stock.

## Las palabras son el efecto: bloque STYLE (inicio de build.py)
Las fichas, recibos y total no son subtítulos, así que los subtítulos del reel siguen durante el espacio (las piezas
van a la altura de la cabeza y más arriba, los subtítulos más abajo). `CAPTIONS=0` se acepta y no cambia nada. Cuando
el reel tiene un estilo de subtítulos o un estilo completo, ajusta el bloque `STYLE` a ese estilo antes de armar:
`name_font`, `name_weight`, `name_case`, `name_tracking` (nombres, títulos de recibo, total), `small_font`,
`small_weight`, `small_case` (etiqueta, líneas de recibo, etiqueta del total), los colores (`tile_bg`, `tile_text`,
`label_color`, `strike`, `paper`, `paper_ink`), `radius`, y `order` (qué lugares de la pared se usan, por turno). Las
tipografías tienen que estar en `assets/fonts/fonts.css`. `width_factor` ensancha las fichas si otra tipografía toca el
borde.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `TILES` | un diccionario por ficha: `text`, `at` (palabra dicha, `'palabra#2'`, o cuadro); opcional `exit`, `spot`, `knock` | `prep.py words`; en el orden dicho; 2 a 5 fichas, cada una arriba 9 cuadros o más |
| `TILE_LABEL` | línea pequeña bajo cada nombre (`''` = ninguna) | qué son esas cosas, con las palabras de la persona |
| `STRIKE_AT`, `WORD`, `WORD_AT`, `WORD_OUT` | solo Íconos: cuándo pasa la línea, la palabra que aterriza y cuándo entra y sale | palabras o cuadros de `prep.py words`; `None` = por defecto |
| `RECEIPTS_ON` | interruptor de la segunda mitad | `False` = solo fichas |
| `RECEIPTS` | una entrada por recibo: una palabra / cuadro, o un diccionario con `at`, `title`, `item`, `amount` | después de la última ficha; hasta 8 |
| `RECEIPT_TITLE`, `RECEIPT_ITEM`, `RECEIPT_AMOUNT`, `CURRENCY` | valores por defecto de cada recibo; texto antes de cada monto | números enteros que dijo la persona |
| `TOTAL_AT`, `TOTAL_TAG`, `TOTAL_TAG_AT`, `TOTAL_POS` | cuándo cae el total (`None` = sin total), etiqueta bajo él, posición a mano | la palabra donde lo suma |
| `WIPE_AT`, `F_IN`, `F_OUT` | cuándo cae la pila; primer y último cuadro del efecto | `None` = medido; `F_OUT` como máximo frames - 2 |
| `WALL`, `SPOTS`, `PILES`, `SIZE` | caja de pared usable; posiciones a mano; tamaño general | solo cuando `work/layout.jpg` muestra una pieza sobre una ventana, repisa o mueble |
| `RECEIPT_FIRST_SIDE`, `VOICE`, `SOUNDS`, `SEED` | lado de la primera pila, audio del clip, sonidos, mezcla de inclinaciones | por defecto |

**Interruptores:** `SAFE=1` guía de zona segura (solo instantáneas), `SFX=0` sin sonidos. `CAPTIONS=0` y `GRADE=0` se
aceptan y no cambian nada.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: pregunta qué nombres van en las fichas y, para recibos, qué montos: solo nombres y montos que la persona dice en este clip o que te dio el usuario. Nunca inventes un nombre, un precio ni una cantidad, nunca dibujes un logo. Sin lista dicha = deja fuera Fichas Fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" prep.py words      # 1. cada palabra con su cuadro -> edita STYLE y CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. mide el recorte, ubica cada pieza -> work/layout.jpg (MÍRALO)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 3. página con la guía; imprime cada momento y los tiempos de instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos que imprimió build.py>
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 4. guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 5. cantidad de cuadros, bordes simples, cara, work/check/sheet.jpg, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Después de CUALQUIER cambio en el bloque CLIP ejecuta `prep.py` de nuevo (`build.py` rechaza una composición hecha
para otros valores). Un espacio de 6 s toma unos 5 minutos después del recorte.

## Qué mirar (work/check/sheet.jpg)
- En su cuadro LANDS cada ficha está plana en la pared a tamaño de reposo (el cuadro anterior todavía viene volando,
  más grande); el tachado se dibuja antes de que salga.
- Las piezas pasan detrás de la persona: pelo, orejas y manos quedan adelante, ninguna pieza cruza la cara.
- Los nombres caben dentro de sus fichas; los montos de los recibos y el total se leen en tamaño celular; el total
  final es la suma.
- Nada queda en reposo sobre y 220 ni bajo y 1470. El primer y el último cuadro son el clip simple (`check.py` lo
  imprime).

## Trampas
- Whisper está 1 a 3 cuadros corrido y escucha mal los nombres: `prep.py words` muestra el cuadro en que realmente
  empieza la voz. Usa esa palabra, o el cuadro.
- El espacio tiene que empezar 6 cuadros o más antes del primer nombre y seguir 12 cuadros después de la última pieza:
  `build.py` dice cuántos cuadros necesita.
- Una ficha lanzada por el costado del cuadro cruza el margen lateral durante 3 o 4 cuadros mientras se desvanece; las
  piezas en reposo siempre quedan dentro de la zona segura.
- `prep.py` imprime `shrunk to 0.xx`: acorta el nombre, saca `TILE_LABEL`, o cambia los lugares en `STYLE['order']`.
  Bajo 0,8 el nombre queda pequeño en un celular.
- Una mano que pasa por el lugar de una ficha está bien (pasa por delante). Una persona que se inclina sobre ella
  durante casi todo el tiempo de la ficha mueve la ficha: mira `work/layout.jpg`.
- Los sonidos son solo de stock (`pop`, `whoosh-short`, `impact-bass-1`) a 0,75x del volumen de la plantilla. Colores:
  nunca naranjo, nunca blanco y negro (usa bosque, crema y dorado).
