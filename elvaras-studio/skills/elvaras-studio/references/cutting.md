# Cortes: mejores tomas, silencios, una transcripción limpia

## 1. Ingerir
`PY "SK/scripts/ingest.py" "<project>" <clips o una carpeta> [--newest N]` escribe:
- `sources.json` (c1, c2 ... del más antiguo al más nuevo), `work/sheets.jpg` (8 cuadros de cada clip: míralo para
  ver los planos y ángulos), `words_cN.json` y `transcript.txt` (por clip: frases con tiempos, cada palabra con su
  tiempo, y un mapa de voz donde `S12.40` = empieza un silencio y `E13.10` = termina un silencio).
Los originales se leen donde están. No se copia ni se cambia nada. La primera transcripción descarga el modelo de voz:
unos 0,5 GB aquí, luego 1,4 GB más en el paso 4 para la pasada final (una vez cada uno). Avísale al usuario antes de
empezar, una vez: "La primera edición descarga el modelo de voz, unos 2 GB. Pasa una sola vez."
Los modelos son multilingües y transcriben en el idioma de `brands/soyelvaras/brand.json` (español por defecto).

## 2. Elegir tomas -> `<project>/edl.json`
La gente repite una frase hasta que le sale. Reconstruye lo que quiso decir a partir de las tomas:
- Usa la ÚLTIMA toma completa y limpia de cada frase, salvo que el usuario diga otra cosa ("la buena empieza en
  0:47" significa una sola toma continua desde ahí).
- Punto de entrada: 0,05 a 0,07 s antes de la primera palabra. Punto de salida: donde empieza el silencio después de
  la última palabra (mapa de voz).
- Corta los silencios entre frases. Antes de recortar una pausa corta dentro de una frase, confírmala con
  silencedetect (`ffmpeg -i <clip> -af silencedetect=n=-40dB:d=0.08 -f null -`): los tiempos de Whisper pueden
  estar 0,1 a 0,3 s corridos y puede inventar una palabra en un corte.
- Whisper inventa frases en tramos de ruido cortos ("Subtítulos por la comunidad de Amara.org", "Gracias por ver el
  video"). Si una frase así aparece en un tramo de menos de un segundo, es ruido: no la uses.
- Dos tramos seguidos del mismo ángulo: acerca uno (zoom 1.2 a 1.9, `cx` / `cy` en el pecho). Nítido cuando la fuente
  es 4K, blando sobre 1,4 en una fuente 1080. Con `cy` bajo (0.4) el recorte parte desde arriba y empuja la cara
  hacia los subtítulos: usa `cy` cerca de 0.52.
- Si dudas de un nombre o de la palabra para comentar: vuelve a transcribir solo ese trozo con los nombres en el
  prompt (`WhisperModel('medium', device='cpu', compute_type='int8')` con `language='es'`; nunca dejes el device en
  'auto', ver gotchas.md).

```json
[{"id": "hook", "clip": "c1", "in": 12.66, "out": 15.72, "zoom": 1.0, "cx": 0.5, "cy": 0.5, "line": "Todos hablan de..."},
 {"id": "cta",  "clip": "c2", "in": 4.10,  "out": 7.02,  "zoom": 1.4, "cx": 0.5, "cy": 0.52, "line": "Comenta EDIT y..."}]
```
`id` es un nombre corto, solo con letras. Cuéntale el plan al usuario en dos líneas y sigue. No esperes un sí.

## 3. Armar
`PY "SK/scripts/assemble.py" "<project>"` corta directo desde los originales a `assets/aroll.mp4` (1080x1920,
30 fps limpios desde t=0) y escribe `segments.json` (primer cuadro y cantidad de cuadros de cada tramo, tamaño de la
fuente). La última línea debe decir que los totales de cuadros coinciden.

## 4. Palabras
`PY "SK/scripts/transcribe_cut.py" "<project>" "Claude, Claude Code, <otros nombres dichos>"` escribe `words.json`:
`[{"text": "Todos", "start": 0.08, "end": 0.52}, ...]`. Estos tiempos manejan todos los subtítulos, así que límpialos:
- Corrige a mano lo mal escuchado según lo que realmente se dijo. Los típicos: "Claude" -> "cloud" / "claws" /
  "Claud", "skill" -> "scale", nombres de productos partidos en dos ("GPT" "-6", "5" ".1": el script une los casos
  comunes, revisa).
- Deja la puntuación de Whisper honesta: una coma o un punto cierra una frase de subtítulos, así que saca la coma que
  no es pausa y agrega un punto donde de verdad termina una oración.
- Deja los números como deben LEERSE en pantalla ("7", no "siete", cuando un estilo muestra el número grande).
- Nunca cambies los tiempos, salvo que una palabra esté claramente atrasada o adelantada respecto del audio.
`work/words_raw.json` guarda la salida de Whisper sin tocar.

Luego marca las palabras: `PY "SK/scripts/marks.py" "<project>"` y la regla de `references/captions.md`.

## 5. Revisar los cortes (después del render)
`PY "SK/scripts/check_cuts.py" "<project>" "renders/<file>.mp4" --phone` escribe `work/cut_check.jpg` (el cuadro antes
y después de cada corte, lado a lado) y una copia 720p para el celular. Cada cuadro "después" debe mostrar la toma
nueva limpia. El render se puede escribir de la forma corta (`renders/<file>.mp4`): los dos scripts de revisión lo
buscan dentro del proyecto.

La última línea que imprime es el nivel de audio (pico y promedio). El reel mantiene el nivel con que se grabó el
clip: nada en la edición sube ni baja la voz. Un pico de -6 dB o más alto está bien. Un pico más bajo es una
grabación baja: dilo en la nota de entrega y ofrece una copia más fuerte. Para hacerla, súbela en lo que falta (pico
-8,6 dB -> `volume=5dB` la deja en unos -3,6) con el ffmpeg de `.platform.json`, sin tocar la imagen:
`"<ffmpeg>" -i "<project>/renders/<file>.mp4" -af volume=5dB -c:v copy -c:a aac -b:a 192k "<project>/renders/<file>-louder.mp4"`
Nunca la subas tanto que el pico pase de -1 dB.
