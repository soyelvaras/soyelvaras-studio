# Mundo App: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Frase dicha:** "All you need to do is drop your clips, trigger the skill, and Claude takes care of it all for you."
**Toma:** 1080x1920, plano medio-abierto, sentado en el piso delante de un sillón individual, 126 cuadros (4,2 s), una
toma continua, cámara quieta.

## Valores del bloque CLIP (los valores por defecto de build.py siguen la misma frase)
| campo | valor | por qué |
|---|---|---|
| `SCREEN` | `'chat'` | la pantalla de chat incluida |
| `APP_NAME` | `'Claude'` | el nombre en el encabezado |
| `GREETING` / `PLACEHOLDER` | "What are we making today?" / "How can I help you today?" | pantalla vacía antes de la primera palabra (en Soy Elvaras: "¿Qué hacemos hoy?" / "Escribe aquí...") |
| `ATTACH` | cuadro 25, cinco clips | "drop" a los 0,84 s |
| `LABELS` | cuadro 39 `RAW CLIPS` en `'attach'`, cuadro 67 `ONE COMMAND` en `'text'` | "clips" a los 1,30 s; justo antes de enviar |
| `TYPE` | cuadro 54, un comando con barra | "trigger" a los 1,80 s |
| `SEND` | 74 | "skill" termina a los 2,46 s |
| `REPLY` | cuadro 79, "On it. Editing your reel." | "Claude" a los 2,62 s |
| `STEPS` | 4 filas en los cuadros 87, 93, 99, 105 | se marcan durante "takes care of it all" |
| `RESULT` | cuadro 112, `reel-final.mp4`, insignia `Ready` | "for you" a los 3,74 s |
| `EDGE` | 1188 en la demo (puesto a mano) | la línea del pecho; el paquete la mide |
| `HEAD_Y` / `ZOOM` | no se usaron en la demo (la cabeza ya estaba en y 864) | el paquete reencuadra otras tomas para igualarlo |

## Lee esto antes de comparar un render nuevo con demo.mp4
- La demo se hizo a mano antes de empaquetar el efecto, y no se volvió a renderizar con el armado del paquete. La prueba
  en `test.md` es la prueba de los scripts empaquetados.
- Look: la demo usa una serif para el encabezado y la respuesta, un pequeño logo de estrella y un acento arcilla en el
  botón y la barra de progreso. El paquete usa las tipografías que trae la plantilla, sin logo salvo que lo entregues
  (`APP_MARK`), y un `ACCENT` neutro que reemplazas con tu color de marca (dorado).
- Adjuntos y tarjeta de resultado: la demo muestra miniaturas de los clips de la persona. El paquete no trae material,
  así que por defecto son fichas simples con etiqueta. Da rutas de imágenes en `ATTACH` y `RESULT` para tener
  miniaturas.
- Recorte: la demo usó un modelo de recorte de retrato más pesado sobre un recorte del torso, más limpieza a mano en
  algunos cuadros. El paquete usa el recorte estándar del espacio y limpia su borde en `prep.py`. En tomas difíciles
  (ropa del color del mueble) la línea de hombros de la demo es mejor que la que da el paquete de entrada.
