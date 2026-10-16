# zoom-through (Corte en Zoom)

**Qué hace:** convierte un corte seco entre dos tomas en un solo movimiento de cámara continuo: la cámara entra en un
punto de la persona, la imagen se estira con un desenfoque radial real, pasa por lo oscuro de la ropa de la persona, y
la toma siguiente se abre desde el mismo punto y frena en su lugar. 18 cuadros centrados en el corte, el audio queda
como un corte seco.

**Función:** transición, en cualquier parte de un video (nuevo encuadre, nuevo look, nuevo lugar, un "así" que revela).
También funciona en el gancho.

**Frases que lo activan:** "atraviésame con zoom hacia la toma siguiente", "haz ese corte con zoom", "entra en mi polera
y sal en el clip siguiente".

**Toma que necesita:** dos tomas con un corte seco, la persona en cuadro en ambas. Cámara quieta o en mano funcionan.
Mejor cuando la persona usa algo oscuro y liso en el torso (el punto de entrada). Cada toma necesita al menos
`HALF + 2` cuadros (11 por defecto) y la frase después del corte debería durar 1,5 s o más para que la llegada respire.
**Dónde falla:** el punto de entrada cae en piel, una mano o un estampado recargado (el paso se vuelve rosado o ruidoso:
mueve el punto); una toma de menos de 11 cuadros; un corte a mitad de una palabra (el whoosh y el desenfoque pelean con
la palabra: mueve el corte al hueco).

**Entradas del espacio:** `assets/aroll.mp4` con AMBAS tomas, `clip.json` con `"cut_frames": [K]`, recorte
`assets/subject.webm` (solo para los puntos de entrada automáticos y la altura de los subtítulos; con valores puestos a
mano `--no-cutout` está bien). Sin `aroll_hi`. Python: solo el Python de la skill (numpy, Pillow, scipy), sin paquetes
extra.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo obtenerlo |
|---|---|---|
| `CUT` | primer cuadro de la toma B | `None` = `cut_frames` de clip.json (two_shot.py lo escribe) |
| `HALF` | cuadros de transición a cada lado del corte | 9 = 18 cuadros; se baja solo si una toma es muy corta |
| `POINT_A` / `POINT_B` | px donde entra la cámara (último cuadro de A) / desde donde se abre (primer cuadro de B) | `None` = prep.py elige el parche plano más oscuro del torso (para A: torso o regazo, oscuro alrededor, lejos de las manos); revisa `work/measure.jpg`, si no, lee x,y en esa imagen (está a la mitad del tamaño: duplícalos) |
| `DEPTH`, `SHARP`, `ROLL` | zoom recorrido, inclinación de la curva, giro de cámara en grados | los valores por defecto sirven para la mayoría de los cortes; `DEPTH 40` es más suave |
| `CREEP_A` / `CREEP_B` | acercamiento lento antes / después | 1 = apagado (usa 1 cuando el reel ya mueve la toma) |
| `GRADE_A` / `GRADE_B` | look horneado opcional por toma | `None` salvo que las dos tomas deban verse distintas |
| `CAP_A` / `CAP_B` | bloque de subtítulos por toma: `style`, `top`, `lead`, `punch`, `tail` como `(segundos, 'palabra')` | tiempos de words.json, confirmados en el audio; `None` = sin bloque; `top: None` = justo bajo la barbilla según prep.py |
| `WHOOSH_VOL` | volumen de plantilla del único whoosh | 0,30 (se aplica x0,75); su pico se pone en el corte |

**Interruptores:** `SAFE=1` guía de zona segura, `CAPTIONS=0` sin bloques de subtítulos (el reel principal los pone),
`SFX=0` sin whoosh, `BAKE_WORKERS=n` procesos de horneado (4 por defecto).

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # mide, luego MIRA work/measure.jpg (cruz amarilla sobre tela oscura y lisa, línea verde bajo la barbilla)
# editar: el bloque CLIP en build.py (palabras y tiempos de subtítulos desde words.json, puntos solo si la cruz está mal)
PY "SK/scripts/fx_run.py" "<slot>" bake.py sheet      # horneado: primero una hoja de cuadros a la mitad del tamaño (cerca de 30 s), el horneado completo cuando se vea bien (2 a 4 min); mira work/bake/sheet.jpg
PY "SK/scripts/fx_run.py" "<slot>" bake.py      # escribe assets/plate.mp4
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # compone, revisa, renderiza
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <6 a 8 tiempos incluyendo los cuadros alrededor del corte>
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
En el reel principal: agrega `CAPTIONS=0` (y `SFX=0` si el reel tiene su propio whoosh) a ambas llamadas de `build.py`, y
pon el render sobre la toma exactamente en estos cuadros. El audio del espacio son las dos tomas con un corte seco, cada
una a su propio nivel: dos grabaciones distintas pueden diferir en varios dB, así que usa el audio del reel principal (o
iguala los niveles) en vez del del espacio.

## Qué mirar en los cuadros finales
- La entrada va en la tela, y el cuadro del corte es oscuro con la toma B como un pequeño destello brillante en el punto.
  Ningún cuadro completo rosado o color piel.
- Alrededor de la toma B mientras es pequeña: rayos suaves de sus propios colores de borde que se desvanecen a oscuro.
  Nunca una copia espejada del cuarto, nunca un rectángulo duro.
- El primer cuadro después de la transición (`K + HALF`) es la toma limpia, mismo encuadre que la toma más el
  acercamiento lento. Sin salto, sin franja oscura en el borde.
- Subtítulos: el bloque A se fue en el corte, el bloque B llega con la imagen, ambos libres de la cara y dentro de la
  zona segura en reposo.
- La cantidad de cuadros es igual a `frames` de clip.json; el whoosh cae en el hueco entre las dos frases y bajo la voz.

## Trampas
- Apuntar al gorro, la cara o las manos pone piel en todo el cuadro durante 4 cuadros. Apunta a la polera, chaqueta, un
  polerón oscuro o pantalones oscuros. La persona gesticula: revisa la cruz contra el ÚLTIMO cuadro de la toma A, que es
  el de measure.jpg.
- No nubles la toma A antes (`FOG_FROM` bajo la escala de A en el cuadro del corte): el cuadro del corte se convierte en
  una tarjeta de color plano.
- prep.py lee la cabeza desde la silueta del recorte; una capucha, una mano en la barbilla o un brazo levantado delante
  del cuello pueden engañarlo. El jpg lo muestra de inmediato: pon `POINT_*` o `top` a mano.
- Si el bloque no tiene espacio bajo la barbilla (plano muy cercano) se omite con un mensaje. Deja que el reel principal
  ponga los subtítulos de esa toma.
- Un `fromTo(..., immediateRender:false)` escalonado muestra las letras tardías antes: las letras se dejan quietas con
  `gsap.set` y se animan con `tl.to`.
- La imagen horneada no tiene audio; la voz sale de `assets/aroll.mp4`. No recodifiques ni cambies los tiempos de la
  toma después de hornear.
- `hyperframes snapshot` puede mostrar la toma siguiente un cuadro antes en el corte. Solo la hoja del mp4 final prueba
  la transición.
