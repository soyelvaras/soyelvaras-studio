# comment-bubble (Comentario)

**Qué hace:** un campo de comentario sube bajo la barbilla de la persona, la palabra se escribe sola en la palabra
dicha, se toca enviar y luego se arma uno de cinco cierres, siempre como secuencia de mensajes: el comentario
publicado, el creador escribiendo, la respuesta y algo adjunto.
**Función:** llamado a la acción. **Frases que lo activan:** "muestra el comentario escribiéndose cuando digo comenta
VIDEO", "burbuja de comentario en el llamado", "escribe la palabra y responde con el link".

## Las cinco versiones (`VARIANT`)
| n | nombre | cómo se ve |
|---|---|---|
| 1 | Mensaje directo | tu burbuja a la derecha con "Visto", la respuesta a la izquierda con un video adjunto |
| 2 | Notificaciones | dos avisos del celular: "Comentaste EDIT" y "Te respondió", con la miniatura del video |
| 3 | Fijado + video | el comentario fijado en papel y la respuesta en video en un círculo con anillo |
| 4 | Papel + foto | burbujas de papel ladeadas y una foto instantánea del video con nota a mano |
| 5 | Link con vista previa | el comentario, una línea de hilo y la respuesta con la vista previa del sitio de la marca |

Se elige en el Studio Picker con los cinco puntitos bajo la tarjeta (debajo de Gancho / Medio / Final). `fx_new.py`
escribe la versión guardada (`effectVariants` en las picks) en la línea `VARIANT`. Todos los colores y letras salen
de `ACCENT_COL`, `LIGHT_COL`, `DARK_COL`, `DEEP_COL`, `TEXT_FONT`, `PUNCH_FONT`, `SERIF_FONT`: para la marca de un
cliente se cambian esas líneas, más `BRAND_NAME`, `BRAND_MARK` y `LINK_DOMAIN`. `THUMB` es la imagen del adjunto
(`'auto'` = un cuadro del clip). Ningún texto dice algo que la persona no dijo: `REPLY_TEXT` y `ATTACH_TITLE` son sus
palabras.

## Toma que necesita, y dónde falla
- Una frase con la forma "(solo) comenta PALABRA y te mando COSA" (o "comment KEYWORD and I'll send you THING"), más
  al menos 1,5 s de la misma toma después de COSA.
- Persona de frente hablando a cámara con LO ALTO DE LA CABEZA en cuadro. Funciona en plano cercano y abierto; la
  cámara puede ir en mano.
- Selfie cercana (barbilla bajo y ~1050): no hay espacio para 1,3x. El hilo se achica a cerca de 1,0 y la imagen sube
  hasta 12% desde el borde inferior (como cuando se abre un teclado). La subida sigue en el último cuadro: termina el
  espacio en un corte, o pon `T_OUT`.
- Plano abierto: 1,3x completo en el tercio inferior, respuesta apilada (texto sobre el botón), imagen sin tocar. Tapa
  el regazo de la persona y lo que hagan sus manos bajo y ~1050.
- Falla o necesita `CHIN_Y` a mano: cabeza cortada por el borde superior, tomas de perfil, capucha / pelo largo (sin
  forma de cabeza), dos personas, una mano en la cara durante casi todo el espacio, o un recorte que mezcla a la persona
  con la silla (entonces también `X_CENTER` y `AVATAR_BOX` a mano). El hilo queda fijo en el cuadro: si la persona se
  levanta o camina, elige otra toma.
- Gente que habla rápido: menos de 0,3 s entre la palabra y "mando" amontona la publicación, el corazón, los puntos y la
  respuesta. Igual se lee, pero míralo.

## Entradas del espacio
`assets/aroll.mp4`, `words.json`, `clip.json`. `assets/subject.webm` lo usa SOLO measure.py (barbilla, centro de la
cabeza, recorte del avatar), nunca como capa: con `fx_new.py --no-cutout` pon `CHIN_Y`, `X_CENTER` y `AVATAR_BOX` a
mano. `aroll_hi`: no se usa. Sin paquetes extra de Python.

## Bloque CLIP (inicio de build.py)
| Campo | Qué es | Cómo obtenerlo |
|---|---|---|
| `KEYWORD` | palabra para comentar, en mayúsculas | de la frase; measure.py la imprime (reconoce "comenta" y "comment") |
| `REPLY_TEXT`, `CHIP_TEXT` | respuesta del creador y etiqueta del botón | menos de ~20 / ~14 caracteres; solo cosas que la persona dice o da a entender. Por defecto "Te mandé el link" / "Abrir link" |
| `USER_NAME` | quien comenta, genérico | deja `tú` |
| `T_IN` .. `T_LINK`, `KEY_GAP` | tiempos de cada momento en segundos desde el inicio del espacio | pega los "suggested CLIP times" de measure.py, luego revisa cada uno contra su tabla de inicios |
| `T_OUT` | el hilo se va y la imagen vuelve a su lugar | `None` si el espacio termina en un corte; si no, >= `T_LINK` + 0,6 y <= final - 0,25 |
| `SCALE` | tamaño del hilo (1,0 = demo original) | deja 1,3; build.py lo achica si la franja bajo la barbilla es muy pequeña y lo dice |
| `CHIN_Y`, `CHIN_GAP` | línea de la barbilla a mano, px libres bajo ella | `None` = medida; cámbiala si work/measure_check.jpg está mal |
| `DROP` | `'auto'` = lo más abajo que permite la zona segura; número = px bajo la barbilla | `'auto'` salvo que el usuario lo quiera pegado a la barbilla en un plano abierto |
| `X_CENTER` | x del centro del hilo | `None` = bajo la cabeza de la persona |
| `PUSH`, `PUSH_MAX` | subida de la imagen (`'auto'` hasta `PUSH_MAX`, o `1` = nunca) | `1` cuando el espacio debe calzar cuadro a cuadro con sus vecinos |
| `AVATAR_FRAME`, `AVATAR_BOX` | cuadro / recorte cuadrado para el avatar del creador | elige el cuadro en work/avatar_check.jpg (ojos abiertos); caja solo si el recorte automático falla |
| `GRADE`, `SEAT` | filtro css sobre la imagen; fuerza del degradado oscuro detrás del hilo | `GRADE` = el color del reel; `SEAT` 0 a 1,5 |
| `WORD_FONT`, `TEXT_FONT` | tipografía de la palabra y el botón / de la respuesta y el nombre: (familia css, grosor, archivo en assets/fonts) | del estilo de subtítulos del reel (la tabla tipográfica en effects/INDEX.md). Palabra Clave: `('Inter Tight', 800, ...)` y `('Inter Tight', 700, ...)` |
| `UPPER` | respuesta, botón y nombre en mayúsculas | `True` cuando los subtítulos del usuario van en mayúsculas |
| `ACCENT_COL`, `LIGHT_COL`, `DARK_COL` | acento (anillo, cursor, botón), claro (burbuja, palabras), oscuro (palabras sobre claro) | los colores de subtítulos del usuario (dorado, crema, tinta por defecto) |

Gana el estilo del usuario: en un reel las palabras del hilo siguen el estilo de subtítulos del reel. Pon las cuatro
filas de arriba antes del primer armado. Una tipografía más ancha ensancha el hilo; se escala a la zona segura, así que
baja `SCALE` solo si las palabras quedan pequeñas.

## Interruptores
`SAFE=1` zona segura en rojo + la línea de la barbilla en cian (solo instantáneas). `SFX=0` sin sonidos (3 teclas, el
clic del toque, pop, whoosh suave, todos a 0,75x de la plantilla). `CAPTIONS=0` se acepta y no hace nada: el efecto no
tiene subtítulos. Saca los subtítulos propios del reel en estos cuadros, el hilo va donde irían ellos.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # inicios + tiempos sugeridos; MIRA work/measure_check.jpg y work/avatar_check.jpg
# editar: el bloque CLIP en build.py (textos, los tiempos sugeridos, AVATAR_FRAME)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <T_IN+.3,T_TYPE+.1,T_SEND,T_SEND+.2,T_DOTS+.1,T_REPLY+.15,T_LINK+.2,final-.05>
PY "SK/scripts/fx_run.py" "<slot>" build.py      # tiene que imprimir 0
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros + work/check/full.jpg y band.jpg desde el mp4 FINAL
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
build.py imprime la composición que eligió (escala, respuesta en línea o apilada, caja del hilo, barbilla, subida) y
avisa cuando achicó el hilo, subió la imagen o un tiempo está fuera de orden. Unos 10 minutos por clip nuevo en Mac, la
mayor parte el recorte en fx_new.py.

## Qué mirar en los cuadros finales
- La primera letra aparece en el cuadro en que empieza la palabra (o uno antes); el toque cae en la respiración
  después de ella; la respuesta en "mando"; el botón en la cosa que se manda.
- Línea cian de la barbilla sobre o bajo la barbilla real en cada cuadro, el borde superior del hilo debajo de ella.
  La cara nunca tapada.
- Nada legible pasado las líneas rojas de seguridad (borde derecho de la burbuja de respuesta <= 980 bajo y 1155).
- Cuadro de "publicando": la palabra aparece una vez, no dos. Los puntos de escritura se van en cuanto aparece la
  respuesta.
- El texto de fondo del campo ("Agrega un comentario...") desaparece en la primera letra.
- Planos cercanos: la subida es suave, sin borde negro abajo, el recorte del avatar es la cara de la persona (no una
  mano ni la pared).

## Trampas
- Los inicios de palabra de Whisper estuvieron 0,1 a 0,6 s antes en los clips de prueba, y pone palabras dentro de
  silencios. Usa los inicios de audio de measure.py (`--env` imprime la envolvente); empieza cada imagen un cuadro
  antes del inicio.
- Los sonidos de stock tienen silencio inicial (click 48 ms, pop / whoosh ~118 ms): `SFX_LEAD` ya lo compensa,
  mantenlo si cambias los archivos.
- Barbilla = lo alto de la cabeza + 1,5 x ancho de la cabeza desde el recorte. Precisa a unos 35 px en una persona con
  gorro; otras personas, sombreros o pelo cambian la proporción (`CHIN_K` en measure.py). La hoja de revisión es la
  verdad.
- El texto de la respuesta y el botón se miden con PIL desde las tipografías del espacio. Ejecuta build.py con el
  Python del entorno, o los anchos son estimaciones y la burbuja puede cruzar la línea segura.
- Cambiar el largo de `REPLY_TEXT` / `CHIP_TEXT` puede pasar de en línea a apilada y mover todo el hilo: vuelve a armar
  con `SAFE=1` y mira de nuevo.
- Reglas de lint que molestaron: un elemento `inset:0` con una animación de opacidad posterior, dos animaciones de una
  misma propiedad que se tocan en el mismo tiempo, un `tl.set(autoAlpha:0)` bajo un `tl.to(autoAlpha:1)` que sigue
  corriendo (por eso el texto de fondo termina de aparecer antes de la primera letra).
