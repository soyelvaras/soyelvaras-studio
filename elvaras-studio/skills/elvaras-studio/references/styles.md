# Los 8 estilos completos y el plan de cada reel

Un estilo completo = lo que le pasa a la imagen (color, composición, cortes, acercamientos) + los subtítulos que trae.
`build_reel.py` lo arma cuando las elecciones dicen `"mode": "preset"`. Motor: `SK/engine/styles.py`. Nunca editas el
motor para un reel. Todo lo que un estilo escribe en pantalla sale de `<project>/plan.json`, que escribes TÚ a partir
de las palabras del reel.

Los cuatro "para ella" funcionan con o sin cara. Nunca digas que son solo sin cara.

| Clave | Nombre | Qué le hace a la imagen | Sus subtítulos | Necesita |
|---|---|---|---|---|
| `soft-hours` | Horas Suaves | Color cálido y tenue, un acercamiento lento en cada toma, viñeta suave | Moodboard (tercio superior cuando no hay nadie en cámara, si no, bajo la barbilla) | |
| `glam-cam` | Glam Cam | Color limpio y luminoso, un salto de zoom en cada idea nueva, pivotando en la barbilla | Tocador | funciona mejor en plano medio o cercano |
| `color-block` | Bloques de Color | Las tomas se cortan con tarjetas de color plano en el primer golpe de cada oración nueva | Minúscula Gigante | más de una oración |
| `camera-shy` | Tímido de Cámara | Cortes rápidos (un acercamiento cada frase más o menos), color cálido y tenue | Una lista escrita desde el plan; sin ella, Moodboard | una lista en el plan |
| `chalk-talk` | Pizarra | La persona recortada sobre un fondo de estudio oscuro, títulos a plumón, una tarjeta redondeada de b-roll opcional | Ninguno: los títulos a plumón llevan las palabras | un recorte limpio hecho con `rvm_cut.py --hard` |
| `fireside` | Junto al Fuego | Una sola toma, color cálido de lámpara, viñeta, un acercamiento lento a la cara | Serif dorada pequeña, dos palabras a la vez | |
| `raw-tape` | Cinta Cruda | Una imagen 4:3 dentro del reel sobre negro, color de película verde gastada, acercamiento lento | Subtítulos dorados simples y pequeños dentro de la imagen | |
| `show-and-tell` | Muestra y Cuenta | La persona en una tarjeta redondeada pegada al borde INFERIOR del video, con la cabeza asomando sobre ella, un lienzo claro arriba | Ninguno: el lienzo lleva las palabras | un recorte limpio (`rvm_cut.py`) |

Cambio de subtítulos: cuando el `captionStyle` de las elecciones no es el que trae el estilo, el tratamiento de la
imagen se queda y ese estilo de subtítulos va encima. Dos límites, ambos avisados con una `NOTE` que hay que
transmitir: Muestra y Cuenta no acepta cambio (los subtítulos claros no se leen en su lienzo claro), y Contundente no
puede ir sobre ningún estilo completo (sus palabras van detrás de la cabeza de una imagen sin tocar).

Todo estilo se arma con un plan VACÍO. En ese caso usa el título fijo, la primera palabra `num` con lo que cuenta, y
la palabra `cta`. Escribe el plan cuando eso no basta, que en Pizarra, Muestra y Cuenta y Tímido de Cámara es casi
siempre.

## plan.json

```json
{
  "title": ["7 efectos de video", "que Claude hizo para mí"],
  "swash": ["7 Efectos", "De Video"],
  "parts": {"hook": [0, 2.9], "end": [21.4, 25.0]},
  "style": { "<clave del estilo>": { ... } },
  "slots": [{"src": "fx/checklist/renders/slot.mp4", "from": 6.2, "to": 9.8}]
}
```
Todos los tiempos son segundos en el corte terminado (léelos de `words.json`). El texto es lo que dijo la persona,
acortado. Nunca agregues una afirmación, un número o un nombre que no dijo. `parts` reemplaza las partes calculadas
(gancho = la primera oración, final = la oración con la palabra para comentar): úsalo cuando la primera oración es
muy larga, por ejemplo una lista.

### Imágenes extra, en cualquiera de los cuatro "para ella"
```json
"soft-hours": {"broll": [{"src": "assets/broll/cocina.mp4", "from": 0, "to": 3.4, "media": 0, "zoom": 1}]}
```
Con `broll` los clips listados son la imagen y el corte del reel solo se escucha (esa es la versión sin cara). Sin
eso se usan las tomas del propio reel. Pon los archivos en `<project>/assets/broll/` (1080x1920).

### Tímido de Cámara: la lista escrita
```json
"camera-shy": {"list": {"title": "3 cosas que ojalá hubiera sabido", "at": 0.4,
                        "sub": "antes de empezar a publicar", "subAt": 1.3,
                        "rows": [{"text": "1. junta tus ganchos", "at": 3.1}, {"text": "2. graba en una toma", "at": 5.6}]}}
```
`title` aparece en `at`, `sub` se escribe solo desde `subAt`, cada fila se escribe sola cuando se dice su punto. Con la
persona en cámara la lista va bajo la barbilla y tiene 3 filas como máximo.

### Bloques de Color
```json
"color-block": {"color": "#C9A15B", "cards": [[3.3, 4.45], [7.0, 8.35]]}
```
Ambos opcionales. `cards` = cuándo la tarjeta de color plano reemplaza la imagen (las palabras siguen encima).

### Glam Cam
```json
"glam-cam": {"zooms": [[1.2, 1.16], [2.4, 1.0], [3.1, 1.22]]}
```
Opcional: tiempo y nivel de zoom de cada salto. Por defecto: un salto en cada frase nueva.

### Pizarra: los títulos a plumón
```json
"chalk-talk": {
  "beats": [{"from": 0.0, "to": 2.1, "title": "¿QUIERES EL LINK?"},
            {"from": 2.1, "to": 4.6, "big": "21", "lines": ["EFECTOS", "DE VIDEO"], "lineAt": [2.4, 2.8]}],
  "broll": {"src": "assets/broll/demo.mp4", "from": 4.6, "to": 6.9, "media": 0.2, "label": "CLAUDE LOS HACE"}
}
```
Un momento es una línea a plumón (`title`, hasta unos 22 caracteres, las más largas se parten en dos) o un número
grande con las una o dos palabras que cuenta, cada una apareciendo cuando se dice. `broll` corta a una tarjeta
redondeada con una etiqueta a plumón. El llamado a la acción ("COMENTA" + la palabra, subrayada) se agrega solo desde
la marca `cta`.

### Muestra y Cuenta: el lienzo
```json
"show-and-tell": {
  "beats": [{"from": 0.0, "to": 2.1, "label": "Vas a necesitar", "card": "el link", "icon": "link"},
            {"from": 2.1, "to": 5.6, "label": "21 efectos de video",
             "thumbs": ["assets/thumbs/a.jpg", "assets/thumbs/b.jpg", "assets/thumbs/c.jpg", "assets/thumbs/d.jpg"],
             "note": "Claude los arma por ti", "noteAt": 4.0}]
}
```
Un momento es una etiqueta con una tarjeta blanca debajo, o una etiqueta con hasta cuatro miniaturas (imágenes
propias del usuario, 226x402) y una nota destacada opcional. El "Comenta" grande + la palabra se agrega solo desde la
marca `cta`. La tarjeta de la persona ignora la zona segura inferior a propósito. Todo lo demás del lienzo queda
dentro de ella.

## Acercamientos que ya vienen en el corte
Los estilos agregan su propio acercamiento lento encima de lo que hizo `edl.json`. Junto al Fuego y Cinta Cruda están
pensados para una sola toma continua: en un reel con muchos cortes igual funcionan, el acercamiento simplemente
atraviesa los cortes.
