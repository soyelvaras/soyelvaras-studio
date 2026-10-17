# negative-words (Negativo)

**Qué hace:** en vez de subtítulos, solo las palabras que importan, enormes y en negativo, mientras la cámara se acerca
a la cara como en Zoom Digital. Cada letra muestra el inverso de lo que hay detrás, llevado a dos colores de marca: sobre
una pared clara las letras quedan verde bosque, sobre algo oscuro quedan dorado, sobre la persona sus colores se dan
vuelta. La palabra grande de una tarjeta va DETRÁS de la cabeza cuando cabe arriba (la cabeza tapa su tercio de abajo);
si no, va adelante, sobre el pecho. Los subtítulos del reel se ocultan mientras dura el espacio.

**Función:** gancho / retención. Le da peso a una cifra, un nombre o el remate de una frase.

**Frases que lo activan:** "pon esa cifra en negativo", "solo las palabras clave, grandes", "el 15% gigante detrás de mi
cabeza".

## Qué palabras van (lo más importante del efecto)
Solo lo que carga la frase, nunca la frase entera. "Tenemos un 15% de margen en todas nuestras ventas" queda como `15%`
(grande) y `margen` (chica). "Este video estaba lleno de errores" queda como `errores` (grande) y `lleno de` (chica). Una
cifra, un nombre o la palabra de remate es la grande; una o dos palabras chicas la acompañan. Todo lo demás no sale en
pantalla. Nunca una cifra o afirmación que la persona no dice.

## Toma que necesita, y dónde falla
- Una toma continua con la cara visible y espacio sobre la cabeza (plano medio o abierto). En un plano cercano no queda
  espacio arriba: las tarjetas bajan al pecho.
- Recorte limpio (`assets/subject.webm`): es la capa que tapa las palabras de atrás.
- El negativo se lee mejor sobre zonas claras u oscuras; sobre un tono medio la copia en *overlay* lo empuja a los
  extremos para que no quede gris.
- Falla con una mano sobre la cabeza (tapa la palabra), con dos personas o con un zoom fuerte (la cabeza sube y no deja
  espacio).

## Bloque CLIP (inicio de build.py)
| Campo | Qué es | Cómo encontrarlo |
|---|---|---|
| `ZOOMS` | los movimientos de cámara, igual que Zoom Digital: `zoom(t_inicio, t_llegada, escala, tipo)` | cuadros de `onsets.py`. Suaves: 1,1 a 1,3. Termina con un regreso a 1,0 salvo que el espacio termine en un corte |
| `EYE`, `FOLLOW`, `AIM`, `MAX_UPSCALE` | encuadre y seguimiento de la cara | como en Zoom Digital |
| `WORDS` | las tarjetas: `(último cuadro o None, palabras)`, palabra = `(cuadro, texto, 'L' o 's')` | una `'L'` (grande) por tarjeta; las chicas antes de ella van arriba a su izquierda, las de después abajo a su derecha. `None` = hasta la tarjeta siguiente |
| `PLACE` | dónde van | `'auto'` (detrás de la cabeza si cabe, si no adelante), `'behind'`, `'front'`. Una tarjeta puede llevar su propio lugar como tercer valor: `(último, palabras, 'front')`; mezclar las dos se lee mejor |
| `COLORS` | los dos colores del negativo `(oscuro, claro)` | bosque y dorado; `None` = negativo en blanco y negro |
| `WHOOSH`, `GRADE` | sonido de los golpes y color | como en Zoom Digital; en un reel `GRADE=0` |

**Interruptores:** `SAFE=1` guía de zona segura, ojos y barbilla. `SFX=0` sin whoosh. `GRADE=0` sin color. `HI=0`
ignora la toma grande.

## Cómo se dibuja
Cada tarjeta va cuatro veces, cada copia mezclada con lo que tiene debajo: *overlay* blanco (empuja la imagen bajo las
letras a sus extremos), *difference* blanco (la da vuelta), *color* con el color claro (le da su tono sin cambiar la luz)
y *lighten* con el color oscuro (levanta los negros a ese color). Nada que contenga las palabras puede tener `z-index` ni
`transform`, o las copias dejan de mezclarse con el video.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. cuadro de inicio de cada palabra; luego edita ZOOMS y WORDS
PY "SK/scripts/fx_run.py" "<slot>" track.py      # 2. seguimiento de los ojos. MIRA work/track_check.jpg
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0      # 3. lee las líneas de cada tarjeta (detrás o adelante, tamaños, avisos !!)
PY "SK/scripts/fx_run.py" "<slot>" bake.py      # 4. assets/zoom.mp4 y assets/zoom_cut.webm
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 GRADE=0
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <un tiempo justo después de cada palabra grande>
PY "SK/scripts/fx_run.py" "<slot>" build.py GRADE=0
PY "SK/scripts/fx_run.py" "<slot>" hf render --video-frame-format png
PY "SK/scripts/fx_run.py" "<slot>" post.py
```
Vuelve a hornear después de cualquier cambio en `ZOOMS`, `EYE`, `FOLLOW`, `AIM` o `HI` (build.py avisa); las palabras,
los colores y el lugar solo necesitan build.py y el render. Último paso en un reel: `fx_add.py` (los subtítulos del reel
se ocultan solos mientras dura).

## Qué mirar en los cuadros finales
- La palabra de atrás nunca tapa la cara: la cabeza la cubre por abajo. La de adelante va bajo la barbilla.
- Nada legible sobre y 236 ni bajo y 1470.
- La palabra grande se lee a tamaño de teléfono sobre la pared y sobre lo oscuro.
