# Pendiente: revisar lo que se ve "de plantilla"

Cristobal (16-10-2026): si todos usan los mismos gráficos, el video se vuelve un commodity. Antes de usar el Studio en
serio, revisar cada elemento gráfico fijo y hacer versiones propias de Soy Elvaras.

## Dónde viven las plantillas

Todo está en `elvaras-studio/skills/elvaras-studio/`. Ningún gráfico es una imagen PNG o JPG: cada uno se dibuja con
código (HTML y CSS) dentro del `build.py` de su efecto. Cambiar el look es cambiar ese archivo.

| Qué se ve | Archivo |
|---|---|
| Hilo de comentario ("tú EDIT", respuesta, botón, corazón, barra "Comenta aquí...") | `effects/comment-bubble/build.py` |
| Tarjetas de titulares, buscador, chats, etiquetas genéricas | `effects/headline-wall/build.py` |
| Tarjetas de Llamadas (íconos, líneas, barras) | `effects/pointer-callout/build.py` |
| Tarjeta del teléfono (barra de app, botón) | `effects/phone-mockup/build.py` |
| Ventana de app, checklist y línea de tiempo de Revelado | `effects/pull-back-reveal/build.py` |
| Tarjeta tipo publicación (íconos de me gusta, comentar, compartir) | `effects/frame-break/build.py` |
| Tarjeta de vidrio del Checklist y su contador | `effects/checklist/build.py` |
| Pantalla de chat de Mundo App | `effects/ui-world/build.py` |
| Página con rayos, sello y notas a mano del Sticker | `effects/freeze-sticker/build.py` |
| Fichas de Congela y Señala | `effects/freeze-and-label/build.py` |
| Línea de tiempo de Línea en Llamas | `effects/timeline-burn/build.py` |
| Panel de tambores del Contador | `effects/odometer/build.py` |
| Los 19 estilos de subtítulos | `engine/captions.py` |
| Página base de cada reel | `engine/template/` |
| Colores y tipografías de marca | `brands/soyelvaras/brand.json` |

## Resuelto: cierre del Comentario (16-10-2026)

El hilo de app genérico se reemplazó por cinco versiones propias, todas como secuencia de mensajes con adjunto:
1 Mensaje directo, 2 Notificaciones, 3 Fijado + video, 4 Papel + foto, 5 Link con vista previa. Se eligen en el Studio
Picker con cinco puntitos bajo la tarjeta y se guardan en `effectVariants`. Colores, letras, nombre de marca, inicial y
sitio son variables en `effects/comment-bubble/build.py`, así que sirven para cualquier marca de cliente.

## Pendiente

Repetir lo mismo (alternativas propias y elegibles) con el resto de la tabla, empezando por titulares, llamadas y
tarjeta del teléfono.
