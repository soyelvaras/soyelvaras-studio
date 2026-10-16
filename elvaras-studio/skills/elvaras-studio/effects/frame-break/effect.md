# frame-break (Rompe Cuadro)

**Qué hace:** todo el video se achica en una tarjeta flotante que parece una publicación en el celular, sobre una copia
desenfocada del cuarto. La cabeza de la persona sobresale por el borde superior de la tarjeta y las manos pasan por sus
lados, luego la tarjeta vuelve a crecer a cuadro completo.
**Función:** gancho (también un momento de llamado: "sígueme", "comenta PALABRA"). Pon `F_IN` y `F_OUT`: los cuadros
antes de achicarse y desde `F_OUT` en adelante son la toma sin tocar. Con `F_OUT = None` la tarjeta se queda y el
efecto debe TERMINAR EN UN CORTE (la última toma de un reel, o el reel corta en el último cuadro del espacio).
**Frases que lo activan:** "achica el video en una tarjeta y déjame salir", "haz que salga del cuadro", "rompe cuadro".

## No se muestra nada que el usuario no haya dado
La tarjeta lleva solo íconos: nunca conteos de me gusta, comentarios ni compartidos. Sin fila de nombre, sin línea de
texto, sin botón Seguir salvo que el usuario dé su propio usuario (`NAME`) y el texto. Nunca inventes un usuario, un
conteo ni el autor de un comentario.

## Toma que necesita
- **Plano:** medio o abierto, UNA toma continua, 3 a 6 s, cabeza en la mitad superior con algo de espacio sobre ella.
  Mejor con un gesto de la mano que se estira hacia el lado a la altura del pecho o más arriba.
- **Cámara:** quieta, con deriva o en movimiento funcionan (imagen y recorte se mueven juntos; no se sigue nada).
- **Pared:** no hace falta.
- **Recorte:** como capa (`assets/subject.webm` se dibuja sobre la tarjeta) y medido (cabeza, silueta del cuerpo,
  manos).
- **Qué lo rompe:** un plano muy cercano (la cabeza llena el cuadro, así que la tarjeta queda bajo la barbilla y poco
  sobresale); una cabeza que toca el borde superior (nada que asome sobre el borde); un recorte que pierde pelo o dedos
  rápidos (la parte perdida se queda dentro de la tarjeta y el borde de lo que sale parpadea); dos personas; una
  capucha o pelo largo sobre los hombros (no hay cuello que encontrar: pon `HEAD`). Manos que nunca salen del cuerpo:
  igual funciona, solo como cabeza que sale, y `prep.py` lo imprime.

**Entradas del espacio:** recorte sí, `aroll_hi` no. Python: numpy y Pillow para `prep.py` y `onsets.py`; `build.py`
no necesita nada.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `F_IN` | cuadro en que la tarjeta ya llegó | `onsets.py`, "onset" de la palabra; 23 o más (achicarse toma 21 cuadros) |
| `F_OUT` | cuadro en que la imagen vuelve a cuadro completo, o `None` | inicio de una palabra posterior, 45+ después de `F_IN`, 2+ antes del último cuadro |
| `HEAD_OUT` | cuánta cabeza sobresale del borde de la tarjeta, en alturas de cabeza | `'auto'` = 0,3 (plano medio) a 1,0 (plano abierto); 1,5 = cabeza y hombros |
| `CARD` | rectángulo de la tarjeta en px de la toma, o `None` = medido | léelo en `work/check.jpg` (a 1/3 del tamaño) solo si la caja cian está mal |
| `SCALE` | tamaño de la tarjeta en pantalla | `'auto'` llena la zona segura; un número solo la achica |
| `HEAD` | `(top_y, chin_y)` a mano | solo cuando la caja verde no está sobre la cabeza |
| `SIDE_POP` | las manos pueden pasar por los lados de la tarjeta | `False` = solo sale lo que está sobre el borde superior |
| `ICONS` | íconos de me gusta / comentario / compartir en la tarjeta | sin conteos en ningún caso |
| `NAME`, `CARD_LINE` | el usuario de la persona y una línea corta | pregúntale; `''` = no se dibuja |
| `FOLLOW_AT` | cuadro de "sígueme": se toca el botón Seguir | necesita `NAME`; `None` = apagado |
| `COMMENT` | `('PALABRA', cuadro)`: la palabra sale del ícono de comentario | la palabra que dice la persona, su inicio; `None` = apagado |
| `LIKE_AT` | cuadro en que se llena el corazón | `None` = apagado |
| `TILT`, `GRADE`, `SOUNDS` | inclinación de la tarjeta (0 = plana), filtro css (`''` = apagado, por defecto), sonidos sí/no | por defecto |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca el texto de la
tarjeta (`CARD_LINE` y la palabra de `COMMENT`). `SFX=0` saca los sonidos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. inicios de palabra como cuadros -> F_IN, F_OUT (y FOLLOW_AT ...)
# editar: el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. medir + hornear (cerca de 1 min). MIRA work/check.jpg: tarjeta cian bajo la cabeza, caja verde en la cabeza, rosado = lo que sale. ¿Mal? cambia HEAD_OUT / CARD / HEAD, prueba con prep.py y el argumento "measure" (5 s), luego ejecuta prep.py una vez más sin él
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 3. página con la guía de seguridad
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.0,1.5,2.0,3.0,4.0      # usa tus propios tiempos
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 5. cuadros simples en ambos extremos contra la toma + work/final_sheet.jpg
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar en los cuadros finales
- El cuadro 0, el cuadro antes de achicarse, y (con `F_OUT`) el cuadro de `F_OUT` y el último cuadro: imagen simple,
  igual a la toma, sin borde, sin orilla oscura.
- El cuadro de `F_IN`: tarjeta llegada y nítida, íconos llegando. La cara nunca queda tapada por un ícono, la fila del
  nombre o la palabra del comentario.
- Cabeza a tamaño completo: la parte sobre el borde de la tarjeta tiene una silueta limpia contra el cuarto oscuro y no
  se desliza respecto de la parte dentro de la tarjeta. Manos: los dedos que pasan por el borde lateral están
  completos, no cortados por una línea recta.
- Con `SAFE=1`: tarjeta, íconos y texto dentro de la zona segura (arriba 220, nada bajo 1470, lados 35, derecha 100
  desde y 1155). `build.py` imprime la caja de la tarjeta en pantalla.
- El render tiene exactamente los `frames` de `clip.json` y el audio de la persona (revísalo con ffprobe).

## Trampas
- Cambiar `F_IN` o `F_OUT` cambia qué cuadros se miden: `build.py` se niega a correr hasta que `prep.py` corra de nuevo.
- El recorte se conserva solo hasta una línea bajo los hombros (líneas amarillas en la hoja de revisión). Debajo, todo
  lo que está fuera de la tarjeta se oculta a propósito, así que una mano que gesticula a la altura del estómago queda
  cortada por la tarjeta como el resto de la imagen.
- Hombros más anchos que la tarjeta se desvanecen suavemente justo fuera de sus lados. Si se lee como un fantasma, da
  un `CARD` más ancho o pon `SIDE_POP = False`.
- Una mano levantada sobre la cabeza achica la tarjeta en pantalla (todo lo que sale tiene que caber bajo los 220 px
  superiores). Elige el tramo del espacio para que no tenga un movimiento alto suelto.
- `GRADE` queda puesto en todo el espacio, incluidos los cuadros simples de ambos extremos. Déjalo apagado salvo que el
  reel tenga el mismo color.
- Los sonidos son los de la plantilla a 0,75x de volumen: un whoosh al entrar, un whoosh al volver, un clic suave en el
  toque de seguir, un pop en la palabra del comentario.
