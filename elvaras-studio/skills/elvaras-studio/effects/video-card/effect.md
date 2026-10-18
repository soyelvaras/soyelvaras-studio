# video-card (Tarjeta de Video)

**Qué hace:** aparece una tarjeta de video con título y capítulos. Arriba corre el clip del capítulo actual con un
botón de play que aparece y se va; abajo, en un panel bosque, va el título en Instrument Serif y una línea que cambia
con cada capítulo ("TUTORIAL 2 capítulos", luego "01 La toma cruda", luego "02 El reel terminado"). Una línea de
progreso por segmentos avanza con un punto dorado. Después la tarjeta se va.

**Función:** explicar / prueba. Mostrar un antes y después dentro del reel ("esta era la toma, y así quedó"), un
tutorial por pasos o un video largo resumido en capítulos.

**Frases que lo activan:** "muestra la toma cruda y después el reel terminado en una tarjeta", "pon una tarjeta de video
con capítulos", "tarjeta tipo tutorial".

## Lo que necesita del usuario
Los clips de cada capítulo son material propio del usuario: su toma cruda, su reel terminado, una grabación de pantalla.
Van en `card/` dentro del espacio (`fx_new.py --buyer-files <carpeta>`) o con su ruta completa en `CHAPTERS`. El título
y los nombres de capítulo van con sus palabras; nunca un número o una afirmación que no dio.

## Toma que necesita, y dónde va la tarjeta
- Cualquier plano con la persona; cámara quieta o con deriva.
- `build.py` mide la cabeza (de `layout.json` del proyecto, o del recorte). Si la tarjeta cabe SOBRE la cabeza (unos
  520 px de ancho o más), va ahí, detrás de la persona: la cabeza puede tapar su borde inferior. Si no, va SOBRE EL
  PECHO, adelante, desde 46 px bajo la barbilla, y los subtítulos del reel se ocultan mientras está arriba
  (`work/reel_captions.json`, lo lee `fx_add.py`). Nunca tapa la cara.
- La imagen es formato YouTube (16:9). Un clip horizontal (un video de YouTube propio) la llena tal cual. Un clip vertical
  se muestra entero al centro sobre una copia desenfocada de sí mismo, como YouTube muestra un video vertical (`FIT =
  'fit'`), o recortado a la franja de la cara (`FIT = 'crop'`, `CROP_Y`). Arriba a la izquierda va el ícono de YouTube
  (`BADGE`).
- Mientras la tarjeta está arriba, todo el cuadro se acerca suave hacia ella (`ZOOM`, 1,06) y vuelve cuando se va.
- Nunca se descargan videos de otras personas (de YouTube ni de ningún lado): los clips son siempre del usuario.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `TITLE` | título de la tarjeta | las palabras del usuario |
| `LABEL` | etiqueta dorada antes del número de capítulos | `'TUTORIAL'`, `'PASO A PASO'`; `''` = sin etiqueta |
| `CHAPTERS` | `(cuadro, 'nombre', 'clip', segundo del clip[, 'fit' / 'crop' / número])` por capítulo | cuadros de las palabras (`words.json` del espacio); el primer clip ya corre desde `CARD_IN` |
| `CARD_IN`, `CARD_OUT` | cuándo entra y sale la tarjeta | 3 o más; `None` = 12 cuadros antes del final |
| `PLACE` | `'auto'`, `'above'`, `'below'` | `auto` mide |
| `FIT`, `CROP_Y` | cómo llena la imagen un clip vertical: `'fit'` (entero, estilo YouTube) o `'crop'` (franja de la cara en `CROP_Y`) | `'fit'`, .30 |
| `BADGE` | ícono en la esquina de la imagen | `'youtube'`, o `''` sin ícono |
| `ZOOM` | acercamiento suave de todo el cuadro hacia la tarjeta | 1,06; 1 = apagado |
| `SIZE`, `SFX_VOL` | tamaño máximo, volumen | 1, 1 |

**Interruptores:** `SAFE=1` guía de zona segura, `SFX=0` sin sonidos.

## Orden de ejecución (PY y SK como en SKILL.md)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # dice dónde va la tarjeta, su tamaño y los tiempos para la instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <los tiempos que imprime>
PY "SK/scripts/fx_run.py" "<slot>" build.py
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
Último paso en un reel: `fx_add.py` (los subtítulos del reel se ocultan solos cuando la tarjeta va sobre el pecho).

## Qué mirar
- La tarjeta nunca sobre la cara; sobre la cabeza, la persona queda adelante.
- El título y la línea de capítulo se leen a tamaño de teléfono; el clip cambia justo cuando cambia el capítulo.
- Nada bajo y 1470 ni sobre y 220.
