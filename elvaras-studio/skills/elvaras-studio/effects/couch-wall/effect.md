# couch-wall (Muro de Portadas)

**Qué hace:** la pared detrás de la persona se convierte en una grilla con las portadas de sus propios reels. Las
columnas suben desde detrás de la persona (y del sillón, la silla o el piso), se deslizan hacia arriba como un feed,
luego bajan y vuelve el cuarto real.
**Función:** explicar / prueba ("mira todo lo que publiqué", "todos hacen lo mismo", "mis últimos 20 videos").
Funciona en cualquier parte de un video: pon `F_IN` y `F_OUT` y los cuadros de antes y después son la toma sin tocar.
**Frases que lo activan:** "pon mis reels como grilla en la pared detrás de mí", "convierte la pared en mi grilla de
perfil", "muro de portadas".

## Las portadas son del usuario
Pídele una carpeta con las imágenes de portada de sus reels (jpg / png / webp, al menos 4, 9 o más se ve mejor; las
portadas 9:16 se recortan a fichas 3:4). Cópialas a `covers/` en el espacio. El efecto no trae portadas. Las fichas no
llevan números salvo que el usuario dé conteos de vistas reales para `COUNTS`: nunca estimes ni redondees hacia
arriba un conteo.

## Toma que necesita, y dónde falla
- UNA toma continua (sin cortes internos), 3 a 6 s, plano abierto o medio, con una pared lisa ocupando buena parte de
  la zona superior. Cámara quieta o con movimiento suave (se sigue).
- Al menos 1,5 s entre `F_IN` y `F_OUT` para que la grilla se alcance a leer.
- Falla en: una selfie cercana (no hay pared que cubrir); muebles, piso o ropa de un color parecido a la pared (cojín
  blanco en pared blanca, sillón beige en pared beige: la grilla se mete en ellos hasta que los dibujes en `IN_FRONT`);
  papel mural con diseño, ladrillo, repisas o una ventana como "pared" (no es de un color, así que `auto` encuentra
  poco: usa `FURNITURE = 'off'` con un rectángulo `WALL`); una toma que corta; pelo o manos rápidas que el recorte
  pierde.
- Lo que cuelga en la pared (cuadros, lámparas, un reloj) queda tapado por la grilla a propósito. Todo lo que llega al
  borde inferior del cuadro (sillón, silla, piso, marco de puerta, lámpara de pie) queda adelante.

**Entradas del espacio:** recorte sí (`assets/subject.webm`, hecho por `fx_new.py` con `_shared/rvm_cut.py`),
`aroll_hi` no. Python: numpy, scipy, Pillow. Sin OpenCV, sin paquetes extra.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `COVERS` | carpeta con las imágenes de portada del usuario | por defecto `covers` dentro del espacio; el orden de los nombres de archivo es el orden de la grilla |
| `COUNTS` | conteos de vistas reales opcionales por archivo | de las estadísticas propias del usuario; `{}` = sin números, sin íconos de reproducción |
| `TOP_BY_COUNT` | las mejores portadas van en la fila de arriba | solo importa con `COUNTS` |
| `F_IN` | cuadro en que la grilla ya llegó | `onsets.py`: inicio de la palabra |
| `F_OUT` | cuadro en que el cuarto volvió del todo, o `None` | inicio de una palabra posterior; `None` = la grilla se queda hasta el final |
| `CAPS`, `CAP_Y` | las palabras de subtítulo propias del efecto y su altura | palabras que dice la persona, cuadros de `onsets.py`; `None` = medido, revisa la caja amarilla |
| `WALL` | rectángulo que puede usar la grilla | `None` = todo el cuadro; lee los px en `work/wall.jpg` (a la mitad del tamaño) |
| `FURNITURE` | `'auto'` u `'off'` | primero `auto`; `off` + `WALL` cuando la pared no es de un color liso |
| `IN_FRONT`, `BEHIND` | formas dibujadas a mano que quedan adelante / van forzadas detrás de la grilla | por defecto `[]`; puntos en px en el cuadro de referencia |
| `WALL_TOL`, `EDGE_CHOKE` | tolerancia de color de la pared; px que se mete el borde del mueble | 1.0 y 1; ver trampas |
| `COLS`, `SCROLL`, `CROP_Y` | fichas a lo ancho, px de deslizamiento por segundo, qué parte de una portada alta se conserva | 3, 190, 0.42 |
| `LOOK`, `SHADOW` | atenuación de las fichas, sombra de la persona y los muebles sobre la grilla | baja `LOOK[0]` en un cuarto oscuro |
| `VOICE`, `TRACK_YMAX`, `REF`, `SOUNDS` | audio de la persona sí/no, zona de seguimiento, cuadro de medición, sonidos | por defecto |

**Interruptores:** `SAFE=1` dibuja la guía de zona segura (solo instantáneas). `CAPTIONS=0` saca las palabras de
subtítulo propias del efecto. `SFX=0` saca sus sonidos.

## Versiones (`VARIANT` en el bloque CLIP)

El usuario la elige en el selector (puntitos bajo la tarjeta); `fx_new.py` la escribe sola (o `--variant 2`).

1. **Feed de portadas:** todo lo de arriba. La pared se vuelve una grilla de portadas que sube y se desliza como un feed.
2. **Grilla en movimiento:** sus reels caen desde arriba uno por uno, REPRODUCIÉNDOSE, a una grilla detrás de su cabeza
   (con una leve inclinación y un rebote al llegar), y salen volando hacia arriba en `F_OUT`.
   - La carpeta `COVERS` puede tener clips de sus propios reels (mp4 / mov: cada tarjeta reproduce un pedazo del medio,
     cortado y achicado solo en `assets/grid/`) y portadas (quedan quietas). Al menos 2 archivos; con menos que tarjetas
     se repiten. `fx_new.py --buyer-files <carpeta>` los copia.
   - Sin máscara de pared y sin `prep.py`: solo el recorte de la persona queda adelante, así que las tarjetas pasan detrás
     de la cabeza y nunca por la cara. Los muebles no quedan adelante (en esta versión las tarjetas van arriba, sobre la
     pared).
   - Campos propios: `GRID` (columnas x filas, 3 x 2), `DROP_EVERY` (cuadros entre una tarjeta y la siguiente),
     `CARD_SIZE` (1 = 240 px de ancho; se achica sola si la grilla no cabe en la zona segura). `F_IN` = cuando aterriza
     la primera, `F_OUT` = cuando salen (o `None`: se quedan hasta el final).
   - Orden: `build.py SAFE=1`, `hf lint`, `hf snapshot --at <los tiempos que imprime>`, `build.py`, `hf render`.
     `grid.py` arma la página; build.py le pasa el control.
   - Solo reels del usuario: nunca videos de otra persona.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: pídele al usuario una carpeta con las portadas de sus propios reels (sus portadas guardadas, o exportadas de su perfil) y cópialas a <slot>/covers/ (fx_new.py --buyer-files <carpeta> hace la copia). Sin portadas del usuario = sin Muro de Portadas: déjalo fuera y dilo
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # copia las portadas del usuario a ./covers (crea la carpeta; 4 o más imágenes); 1. inicios de palabra como cuadros -> F_IN, F_OUT, CAPS en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep.py      # 2. portadas, seguimiento de cámara, máscara de la pared, fg.webm (unos 3 min). MIRA work/wall.jpg. Si el área cian está mal, edita WALL / IN_FRONT / BEHIND / WALL_TOL, luego
PY "SK/scripts/fx_run.py" "<slot>" prep.py wall      # vuelve a medir solo eso (20 s); repite hasta que esté bien, luego ejecuta prep.py una vez más SIN "wall" para que fg.webm se hornee desde la máscara final
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # 3. página con la guía de seguridad
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.5,1.0,1.5,2.0,2.5,3.0
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # 4. página limpia (sin guía), luego render
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Cualquier Python con numpy, scipy y Pillow sirve en lugar de la ruta del entorno. `build.py` en sí no necesita
paquetes.

## Qué mirar en los cuadros finales
- El cuadro de `F_IN` y el anterior: las columnas están arriba y casi quietas en la palabra. El cuadro de `F_OUT`:
  cuarto simple, sin ninguna ficha.
- Borde del mueble a tamaño completo: ninguna ficha sobre el sillón, la silla o el piso, ninguna franja de pared real
  entre el mueble y la grilla, sin borde brillante.
- La silueta de la persona: sin color de pared asomando por el pelo, los dedos o una manga rápida; ninguna ficha dentro
  del cuerpo.
- Palabras de subtítulo en el pecho, nunca en la cara ni en las manos, dentro de la zona segura (arriba 220, abajo
  1470, lados 35). La grilla en sí es fondo y puede pasar bajo esas zonas.
- Los números de las fichas aparecen solo si se llenó `COUNTS`. El render tiene exactamente los `frames` de `clip.json`
  (revísalo con ffprobe).

## Trampas
- `auto` lee el color de la pared desde la mitad superior del cuadro, promediando a la persona. Necesita que la persona
  deje visible la mayor parte de la pared superior en algún momento del espacio.
- Pared desnuda sin cubrir al lado de un mueble (una franja de sombra oscura): sube `WALL_TOL` a 1,3. Grilla sobre un
  sillón claro o el piso: bájalo a 0,7, o dibuja la pieza en `IN_FRONT`. prep avisa cuando la grilla llega al borde
  inferior del cuadro.
- Una puerta hacia otra pieza no es pared: si la grilla debería parar en el marco de la puerta y no lo hace, ciérrala
  con `WALL` o `IN_FRONT`.
- Después de cualquier cambio en los campos de la máscara ejecuta `prep.py` (no solo `prep.py wall`) antes de
  `build.py`, o el render usa el `fg.webm` viejo.
- Menos portadas de las que necesita la pared se repiten en orden; con menos de 9 las repeticiones se notan. `F_IN`
  tiene que ser 8 o más (las columnas suben durante 8 cuadros antes de la palabra); `F_OUT` necesita 45 cuadros
  después de `F_IN` y 2 cuadros después de sí mismo. Con `F_OUT = None` el reel tiene que cortar en el último cuadro.
- Cámara en movimiento: la grilla se pega a la pared con un `matrix3d` por cuadro, puesto con una propiedad GSAP basada
  en función (segura al buscar). Si se desliza, baja `TRACK_YMAX` justo sobre el mueble y ejecuta `prep.py --force`.
- Los sonidos suenan a 0,75x del volumen de la plantilla: un whoosh al entrar, uno al salir, un pop suave cuando vuelve
  el cuarto.
