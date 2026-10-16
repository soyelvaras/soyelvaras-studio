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

## Primera prueba: cierre del Comentario

Maquetas en `~/reel-edits/efectos-cta/fx/alt-cierre/`:
- `actual.jpg`: el hilo de app de siempre.
- `alt-a.png`: Nota a mano ("comenta" en serif itálica, EDIT en Bebas dorado con círculo a mano, "y te lo comparto"
  manuscrito con flecha).
- `alt-b.png`: Sello Soy Elvaras (boleto crema con COMENTA LA PALABRA / EDIT / "y te lo comparto", y el sello V de la
  marca).

Cuando elija, la elegida pasa a `effects/comment-bubble/build.py` como estilo por defecto y las otras quedan como
opción.
