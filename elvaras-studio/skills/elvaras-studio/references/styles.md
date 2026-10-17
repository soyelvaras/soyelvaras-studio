# Los 3 estilos completos y el plan de cada reel

Un estilo completo = lo que le pasa a la imagen (color, composición, cortes, acercamientos) + los subtítulos que trae.
`build_reel.py` lo arma cuando las elecciones dicen `"mode": "preset"`. Motor: `SK/engine/styles.py`. Nunca editas el
motor para un reel. Todo lo que un estilo escribe en pantalla sale de `<project>/plan.json`, que escribes TÚ a partir
de las palabras del reel.

Glam Cam y Tímido de Cámara funcionan con o sin cara (con `broll` el corte solo se escucha).

| Clave | Nombre | Qué le hace a la imagen | Sus subtítulos | Necesita |
|---|---|---|---|---|
| `glam-cam` | Glam Cam | Color limpio y luminoso, un salto de zoom en cada idea nueva, pivotando en la barbilla | Tocador | funciona mejor en plano medio o cercano |
| `camera-shy` | Tímido de Cámara | Cortes rápidos (un acercamiento cada frase más o menos), color cálido y tenue | Una lista escrita desde el plan; sin ella, Moodboard | una lista en el plan |
| `show-and-tell` | Muestra y Cuenta | La persona en una tarjeta redondeada pegada al borde INFERIOR del video, con la cabeza asomando sobre ella, un lienzo claro arriba | Ninguno: el lienzo lleva las palabras | un recorte limpio (`rvm_cut.py`) |

Cambio de subtítulos: cuando el `captionStyle` de las elecciones no es el que trae el estilo, el tratamiento de la
imagen se queda y ese estilo de subtítulos va encima. Dos límites, ambos avisados con una `NOTE` que hay que
transmitir: Muestra y Cuenta no acepta cambio (los subtítulos claros no se leen en su lienzo claro), y Contundente no
puede ir sobre ningún estilo completo (sus palabras van detrás de la cabeza de una imagen sin tocar).

Todo estilo se arma con un plan VACÍO. En ese caso usa el título fijo, la primera palabra `num` con lo que cuenta, y
la palabra `cta`. Escribe el plan cuando eso no basta, que en Muestra y Cuenta y Tímido de Cámara es casi siempre.

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

### Imágenes extra, en Glam Cam o Tímido de Cámara
```json
"camera-shy": {"broll": [{"src": "assets/broll/cocina.mp4", "from": 0, "to": 3.4, "media": 0, "zoom": 1}]}
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

### Glam Cam
```json
"glam-cam": {"zooms": [[1.2, 1.16], [2.4, 1.0], [3.1, 1.22]]}
```
Opcional: tiempo y nivel de zoom de cada salto. Por defecto: un salto en cada frase nueva.

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
Los estilos agregan su propio acercamiento lento encima de lo que hizo `edl.json`.
