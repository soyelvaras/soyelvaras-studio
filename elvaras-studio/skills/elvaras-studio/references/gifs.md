# GIFs

Solo cuando el usuario los pide: "agrega un GIF cuando digo X", "ponle unos GIFs a este", o "siempre usa GIFs"
(entonces escríbelo en `ST/my-style.md` y hazlo en cada reel). Nunca por tu cuenta.

## Qué frases llevan uno

Un GIF es una reacción, así que va en una frase que tenga una: un chiste, una sorpresa, un número grande, un error,
un logro. Uno a tres por reel, cada uno de 1,5 a 3 segundos, nunca dos a la vez y nunca durante un espacio de efecto.
Si el usuario nombró la frase o el GIF: haz exactamente eso. "Agrega GIFs donde calcen": tú eliges las frases desde
`words.json`.

## Buscarlo, mirarlo, ubicarlo

```
PY "SK/scripts/gif_find.py" "<project>" "mind blown"      1 a 4 palabras: la reacción, no la frase (en inglés
       encuentra más resultados). GIFs de Giphy y Tenor en una hoja numerada. MÍRALA. Elige el que se entiende de
       un vistazo y calza con el tono del usuario.
PY "SK/scripts/gif_add.py" "<project>" "<link del que elegiste>" --from 3.2 --to 5.4
       luego build_reel.py --safe y mira una instantánea dentro de ese tiempo
```
- Nada bueno en la hoja: búscalo de nuevo con otras palabras. Usa GIFs reales, de los que la gente conoce de sus
  grupos de chat. `--stickers` (formas recortadas) solo cuando el usuario pide un sticker.
- El usuario dio un archivo GIF o un link (Giphy, Tenor, o uno que termina en .gif): sáltate la búsqueda y pásalo
  directo a `gif_add.py`.
- Dónde va: `gif_add.py` elige un lugar que deja la cara libre (sobre la cabeza, si no, la pared libre al lado de la
  persona). Muévelo con `--place above|left|right|top|chest` o `--at X,Y`, cambia el tamaño con `--width`. Ejecútalo
  de nuevo con el mismo `--id` para reemplazarlo, `--remove <id>` para sacarlo.
- En la instantánea: el GIF no está sobre la cara, ni sobre un subtítulo, ni bajo el título fijo. Sigue el estilo del
  usuario como todo lo demás: un estilo tranquilo lleva uno pequeño, no tres llamativos.
- `STATUS gifs NONE` (la búsqueda no dio nada o no hay conexión): di "No encontré un GIF para esa frase. Mándame uno,
  o un link, y lo pongo."

## De qué tipo

Los GIFs de reacción de series, películas y memes son lo que el usuario quiere decir, así que úsalos: pedir GIFs es la
única excepción a la regla fija 4 ("nunca una persona real que no sea el usuario"). La primera vez que agregues GIFs,
dilo una vez: "Estos GIFs vienen de Giphy y Tenor, los mismos que ves en los chats."

Dilo simple en la entrega: "GIFs: uno de cabeza explotando en la frase del precio."
