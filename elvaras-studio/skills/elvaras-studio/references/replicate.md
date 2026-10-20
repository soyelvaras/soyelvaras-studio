# Replicar un ejemplo: estudiarlo, reconstruirlo, hacerlo suyo

Cuando el usuario muestra un ejemplo (un reel que le gusta, un pin, una captura) o describe un look, ESO es el
encargo. Los subtítulos y efectos que trae la skill quedan a un lado. Estudias el ejemplo de principio a fin y
reconstruyes su look con los clips del usuario, para que calce con SUS palabras e imágenes. Luego lo guardas, y cada
"edítalo" siguiente lo usa.

## Qué se copia y qué nunca

Se copia: el LOOK y la ESTRUCTURA. Sensación de la tipografía, mayúsculas o minúsculas, colores, placas, composición,
dónde va cada cosa, ritmo de los subtítulos, movimiento, ritmo de cortes, el tipo de elementos gráficos, el carácter
del sonido.

Nunca se copia: las imágenes, música, voz, logo, usuario, nombre o palabras del ejemplo. Nunca se dice que el
resultado es de quien hizo el ejemplo, con esa persona o aprobado por ella. En pantalla solo hay palabras propias del
usuario, sus imágenes y material, y rellenos genéricos.

Tipografía: la más parecida que trae la skill, o una de licencia abierta descargada con `get_font.py`. Nunca
descargues, incrustes ni pidas un archivo de fuente pagada. Cuando la del ejemplo no está disponible, di cuál la
reemplaza.

El texto propio de la skill nunca nombra ni imita a un creador específico. La referencia del usuario es asunto suyo.

## 1. Estudiarlo (completo, no tres cuadros)

```
PY "SK/scripts/study.py" "<example file>"            un video o una imagen que dejó el usuario
```
Un link a una publicación (un reel, un short, un pin) pasa por Apify: usa tu herramienta de Apify para conseguir la
dirección directa del video de ese link, y luego `PY "SK/scripts/get_example.py" --direct "<address>"` de inmediato
(esas direcciones vencen en minutos) y ejecuta `study.py` sobre el archivo que imprime. Queda en
`ST/examples/downloads/`. Si no tienes herramienta de Apify, dile al usuario en una frase que para usar links hay que
conectar Apify, o que puede dejar el archivo del video.

Escribe `ST/examples/<name>/`: cada cuadro muestreado en hojas de cuadros (`sheet_01.jpg` ...), `cuts.jpg` (el cuadro
antes y después de cada corte), cuadros a tamaño completo en `frames/`, y `study.json` (tiempos de corte, duración de
cada toma, volumen en el tiempo, dónde salta el sonido, las palabras con sus tiempos). Imprime la mitad medida:
duración, cortes, ritmo, velocidad al hablar, saltos de sonido. El modelo de voz del estudio detecta el idioma solo,
así que sirve para ejemplos en inglés o en español.

Luego MIRA cada hoja, en orden, y dos o tres cuadros a tamaño completo para tipografía y color. Los subtítulos, los
gráficos y el encuadre cambian de momento a momento: un look leído de tres cuadros es una suposición.

Una imagen fija (un pin, una captura) muestra tipografía, color, placa, ubicación y gráficos. No puede mostrar ritmo,
animación ni sonido: pregúntale al usuario en una sola pregunta, o elige valores tranquilos y dilo.

Solo una descripción ("subtítulos blancos gruesos con un resaltado amarillo, cortes rápidos, sin sonidos"): sáltate
el script, escribe las mismas notas desde sus palabras y haz una pregunta sobre lo que falte y defina el look.

## 2. Escribirlo (What to write down)

Escribe esto en `ST/my-style.md`, con palabras simples, una línea corta por área. No dejes nada como "igual que el
ejemplo".

| Área | Qué anotar |
|---|---|
| Tipografía | sensación (serif, sans limpia, condensada, mayúsculas anchas, monoespaciada, a mano), grosor, mayúsculas o minúsculas, tamaño respecto del ancho del cuadro, espaciado, la fuente que vas a usar y por qué |
| Color | texto, el acento, placa, contorno o sombra, color de fondo o página, el tratamiento de color (cálido, frío, plano, contrastado, gastado) |
| Subtítulos | dónde van (pecho, tercio inferior, sobre la cabeza, arriba, centro), cuántas palabras y líneas a la vez, con placa o sin, qué hace la palabra que se está diciendo, qué hace una palabra clave |
| Movimiento de subtítulos | cómo llega una línea (corte, salto, aparición suave, sube, se escribe, palabra por palabra) y cómo se va |
| Ritmo | cortes cada 10 segundos, duración típica de una toma, acercamientos (cada cuánto, qué tan fuertes), pausas que se dejan o se cortan |
| Encuadre | qué tan grande está la persona, dónde en el cuadro, qué hay detrás o alrededor (una página, un borde, una tarjeta) |
| Elementos gráficos | títulos, barras, bordes, tercios inferiores, stickers, tarjetas, insertos: qué, dónde, cuándo entran y salen |
| Sonido | golpes en cortes o palabras o ninguno, qué tan fuerte respecto de la voz, música o no |

## 3. Reconstruirlo con los clips del usuario

Edita los clips del usuario como siempre (`references/cutting.md`): sus mejores tomas, sus palabras. Los tiempos del
ejemplo no se copian. Su RITMO sí: si corta cada 2 segundos y marca una palabra por línea, haz eso con sus palabras.

Todo lo de abajo va en `ST/my-style.json` (el estilo, usado en cada reel) o en `<project>/plan.json` (solo este reel,
gana sobre my-style). `build_reel.py` lee ambos. No se usa ningún estilo de subtítulos ni efecto de la skill salvo que
el usuario lo pida.

### El estilo de subtítulos a medida: `"caption": { ... }`

Una especificación, dibujada por el mismo motor que los estilos de la skill: mismas palabras, mismas marcas, misma
lógica de zona segura y de cara, y los espacios de efecto (`--caption-y`, ventanas ocultas) funcionan con ella. Cada
campo es opcional.

| Campo | Valores | Por defecto |
|---|---|---|
| `font` | una familia de `assets/fonts/fonts.css` (`PY "SK/scripts/get_font.py" --list`), o una descargada con `get_font.py` | Inter Tight |
| `file` | el nombre del archivo de la fuente descargada (en `ST/fonts/`), solo para una familia que la skill no trae | |
| `weight`, `italic`, `stretch` | 100 a 900; true / false; font-stretch en % (125 para la Archivo ancha) | 800, false, 100 |
| `case` | `as-typed`, `upper`, `lower`, `title` | as-typed |
| `size`, `tracking`, `line_height` | px sobre el cuadro de 1080 de ancho; em; múltiplo del tamaño | 64, 0, 1.12 |
| `color`, `accent` | color del texto; el color de las palabras marcadas e iluminadas | crema #F2ECDF, dorado #C9A15B |
| `shadow` | un text-shadow css, o false | una sombra oscura suave |
| `stroke` | `{"color": "#000", "width": 8}` un contorno alrededor de las letras | ninguno |
| `plate` | `{"color": "rgba(...)", "radius": 24, "pad": [18, 32], "blur": 0, "per": "line"}`; `"per": "word"` pone una detrás de cada palabra | ninguna |
| `lit`, `lit_text` | qué hace la palabra que se está diciendo: `none`, `color` (acento mientras se dice), `stay` (pasa a acento y se queda), `plate` (una placa de acento detrás, texto en `lit_text`), `pop` | none |
| `mark`, `mark_scale` | palabras marcadas (num, key, emph, cta en `words.json`): `accent` (color de acento), `highlight` (una caja de acento detrás de la palabra, texto en `lit_text`) o `none`; un factor de tamaño como 1.25 | accent, 1 |
| `words`, `chars`, `lines` | máximo de palabras y caracteres por línea; 1 o 2 líneas | 3, 18, 1 |
| `position`, `dy` | `chest`, `lower`, `above-head`, `top`, `center`, o una y en px; un ajuste en px | chest |
| `align`, `margin` | `center`, `left`, `right`; margen lateral en px | center, 70 |
| `entrance`, `exit` | `none`, `pop`, `fade`, `slide-up`, `type-on`, `word-by-word`; `none` o `fade` | none |
| `css` | css extra para este estilo. Clases: `.cu` el bloque, `.cu .ln` una línea, `.cu .pl` la placa, `.cu .w` una palabra, `.cu .w.m` una palabra marcada | |

El motor mantiene el bloque dentro de la zona segura, corta las líneas donde se acaba el ancho y mueve un bloque que
quedaría sobre la cara (imprime una `NOTE` cuando lo hace). `"caption": "karaoke"` (una clave en vez de una
especificación) simplemente hace suyo un estilo de la skill.

### Tus propias capas: `"layers": [ ... ]`

Para lo que tiene el ejemplo y ningún efecto de la skill cubre: una tarjeta de título, una barra de progreso, un
borde, un tercio inferior, una etiqueta en una esquina, un sticker, una página detrás de la persona. Html y css
simples que escribes tú, con un rango de tiempo y un ancla.

```json
{"id": "title", "anchor": "top", "from": 0.0, "to": 2.4, "in": "slide-up", "out": "fade",
 "html": "<div class='tt'>3 cosas que ojalá hubiera sabido</div>",
 "css": ".tt{display:inline-block;font:400 72px 'Bebas Neue';color:#141615;background:#F2ECDF;padding:14px 30px;border-radius:18px}"}
```
- `anchor`: una franja que el motor ubica para este clip, `top` (y 236), `above-head`, `center`, `chest`,
  `lower-third` (una caja centrada de 1080 de ancho cuyo borde superior queda en la franja; `dx` / `dy` la ajustan).
  O `full`: el cuadro completo, tu css ubica todo. O `behind`: el cuadro completo, DETRÁS de la persona, lo que
  necesita un recorte de la persona (`rvm_cut.py`).
- `from` / `to` en segundos del reel. Déjalos fuera para una capa que dura todo el reel. En `my-style.json` solo se
  usan esas capas fijas; las capas con tiempo van en el `plan.json` de un reel, escritas a partir de sus palabras.
- `in` / `out`: `none`, `fade`, `pop`, `slide-up`. Ese es todo el movimiento que tiene una capa: los `@keyframes` de
  css en una capa NO se reproducen en el motor de render. Cuando el ejemplo mueve un gráfico de otra forma, usa la
  más parecida de esas cuatro y dilo.
- Un GIF o un clip corto como capa: `gif_add.py` lo hace y escribe la capa por ti (`references/gifs.md`).
- El texto de una capa son palabras propias del usuario o un relleno genérico. Nunca un logo, un usuario ni una
  afirmación.
- Las capas pasan por las mismas revisiones que todo: `HF lint`, instantáneas con la guía roja de zona segura y
  `frames_check.py` sobre el render final (sus números marcan todo lo dibujado en el área no segura o sobre la cara).
  Mantén el texto dentro de x 35 a 1045 (980 desde y 1155 hacia abajo) e y 220 a 1470. Una página, franja o borde
  simple puede entrar al área no segura (los botones de la app quedan encima); `frames_check.py` marca entonces cada
  cuadro donde esté: mira una vez que no haya nada para LEER ahí, y sigue.

### Todo el reel

| Qué | Cómo | Límite |
|---|---|---|
| Tratamiento de color | `"grade": "contrast(1.08) saturate(.9) brightness(.98)"` (un filtro css sobre la imagen, el recorte y cada espacio de efecto) | solo filtros css: sin LUTs, sin grano de película, sin color selectivo |
| Ritmo de acercamientos | `edl.json`: parte una toma en tramos y alterna `zoom` (1.0, 1.25, 1.0 ...) con `cx` / `cy` en la cara, tan seguido como lo hace el ejemplo | cortes secos entre niveles de zoom; un zoom suave es el efecto Zoom Digital; blando sobre 1,4 en una fuente 1080 |
| Ritmo de cortes | `edl.json`: salidas más justas o más holgadas, pausas que se dejan o se cortan, según la duración típica de toma del ejemplo | las tomas del usuario deciden qué se puede cortar |
| Sonido | `"sounds": [{"src": "assets/sfx/pop.mp3", "at": 1.2, "vol": 0.2}]` en `plan.json` (los nombres disponibles están en `<project>/assets/sfx`); ninguno para un ejemplo tranquilo. Efectos: `SFX=0`, `--no-sfx`, `SFX_GAIN` | solo el set de sonidos incluido; no se agrega música |
| Cualquier otra cosa | `"css": "..."` css simple que va al final, en `plan.json` o `my-style.json` | puede reestilizar lo que hay en la página; no puede agregar movimiento |

Lo que hoy no se puede igualar, así que dilo directo cuando el ejemplo lo tenga: música, una composición que mueve a la
persona a un panel o a una página (usa el estilo completo Tutorial Gráfico cuando ese es el look, o
Pantalla Verde para un fondo), cambios de velocidad, transiciones entre tomas que no sean un corte o el efecto Corte en
Zoom, gráficos animados más allá de las cuatro entradas, movimiento de subtítulos más allá de las seis entradas, 3D, y
b-roll que el usuario no entregó.

## 4. Compararlo lado a lado

```
PY "SK/scripts/side_by_side.py" "<example file>" "<project>" "renders/<slug>-v1.mp4" --example-at 1.2,3.0,6.5 --at 0.8,2.4,5.0
```
Cuadros del ejemplo arriba, el reel del usuario abajo, en `work/compare/`. Elige pares que muestren el mismo TIPO de
momento (una línea de subtítulos, una palabra marcada, un título, un gráfico). Míralo y corrige lo que no calza:
tamaño respecto del cuadro, color, posición, grosor. Una pasada de pulido.

Luego dile al usuario, con palabras simples: "Estudié tu ejemplo. Esto es lo que logré igualar: ... Y las dos cosas que
no pude: ..." Una línea cada una. Manda la hoja junto con el reel.

## 5. Pasa a ser suyo

- `ST/my-style.md`: las notas del paso 2, la fuente que reemplaza a la suya, lo que no se pudo igualar, sus notas
  fijas ("siempre", "nunca") y dónde está el estudio del ejemplo.
- `ST/my-style.json`: `{"name": "...", "caption": {...}, "layers": [las fijas], "grade": "...", "css": "...",
  "pace": "...", "sound": "..."}`. `build_reel.py` lee `caption`, las `layers` fijas, `grade` y `css` en cada armado;
  `pace` y `sound` son notas para ti cuando escribes `edl.json` y `plan.json`.
- Desde ahí "edítalo" usa su estilo sin preguntar. Está por encima de las elecciones guardadas. Un estilo de
  subtítulos de la skill o un efecto solo se usa cuando el usuario lo pide, y ese efecto se reestiliza a su estilo
  (`effects/INDEX.md`, "Restyling an effect's own words").
- "Vuelve a mis elecciones": `build_reel.py --no-my-style` para un reel, o deja a un lado `my-style.json`
  (cámbiale el nombre, nunca lo borres) para siempre.
