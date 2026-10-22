# Movimiento: cómo se mueve todo lo que dibuja el Studio

Lee esto antes de escribir o adaptar cualquier gráfico: una capa, el estilo de subtítulos a medida, el bloque CLIP o el
css de la copia de un efecto, o un look sacado de un ejemplo. Son las reglas que un motion designer senior tiene en la
cabeza, pasadas a reels 9:16 a 30 cuadros por segundo (1 cuadro = 0,033 s). Vienen de la skill de motion para videos
de lanzamiento (launch-motion) y del sistema de movimiento del Creator Studio original.

Todo se anima con GSAP sobre la línea de tiempo única del reel. El render busca cuadro por cuadro, así que css
`@keyframes`, `animation` y `transition` NO se reproducen (el armado imprime una NOTE cuando los encuentra).

## 1. Las reglas

**La regla de oro: nada se detiene nunca.** Lo que está quieto en pantalla sigue respirando un poco hasta que se va:
crece de 1 a 1,02, o deriva unos 4 px. La imagen también: la cámara viva (sección 2) la empuja siempre.

| Qué | Cómo | Valores |
|---|---|---|
| Nada lineal | toda entrada, salida o movimiento de cámara frena y arranca suave | `ease: 'none'` solo para la deriva de cámara y para lo que va atado al reloj (un código de tiempo, una barra de reproducción) |
| Entradas | llegan rápido y se pasan un poco de su punto antes de asentarse | 0,25 a 0,5 s (8 a 15 cuadros), `back.out(1.5)` a `back.out(2)`. Rápida (0,25 s) en un corte justo, que es lo que él prefiere; 0,5 s cuando hay aire |
| Salidas | más rápidas que la entrada, acelerando | 60 % de la entrada, `power2.in`. Un gráfico que termina en un corte no tiene salida: el corte lo saca |
| Agrupar | lo que va junto se mueve junto: anima el contenedor, no cada pieza | una tarjeta con sus filas es UN elemento que entra; las filas solo hacen lo suyo después |
| Desfase | los elementos de un grupo nunca entran todos en el mismo cuadro | uno cada 1 a 2 cuadros (`stagger: 0.04` a `0.07`) |
| Traslape | el movimiento siguiente parte antes de que el anterior se asiente | en el último 20 % del anterior |
| Legible | lo importante (un titular, un número, el estado clave de una pantalla) se queda lo suficiente para leerlo | 1 s como mínimo, salvo que el corte justo lo saque antes: entonces que entre antes |
| Contadores | suben, nunca saltan al valor final | cerca de 1 s, `power2.out` (Contador ya lo hace) |
| Clic | todo botón que se aprieta se hunde un poco | escala 1 → 0,96 → 1 en 4 cuadros (0,13 s) |
| Cursor | nunca en línea recta: viaja en arco como una mano, frena y se pasa apenas | ver la receta "Cursor en arco" |
| Cámara | los paneos y zooms siempre con entrada y salida suaves | `power2.inOut` / `sine.inOut`; un paneo de lado a lado no dura menos de 0,8 s. El zoom de golpe en una palabra es la excepción: 0,1 a 0,2 s `power3.out`, y vuelve |
| Pantallas | interfaces en html o SVG, nunca una captura | así un zoom a un botón queda nítido |
| Tipografía | cargada antes del primer cuadro | las fuentes del proyecto ya van con `font-display:block`; una fuente de reemplazo en pantalla es un error |
| Espacio | un gráfico que deja medio cuadro vacío está a medio hacer | llena el espacio libre que mide el efecto o el layout, y que el gráfico crezca o derive mientras se queda |

Las mismas reglas valen al adaptar un efecto en la copia de su espacio (`<project>/fx/<slot>/build.py`): cambia sus
tiempos y curvas ahí, nunca en la skill.

## 2. La cámara viva

Todo reel sin estilo completo tiene la cámara viva, sin que haya que pedirla: cada toma se acerca despacio alrededor
de la cara (la cara queda quieta y la pieza se mueve a su alrededor), la toma siguiente se aleja, y el corte esconde
el cambio. Gana 1,5 % por segundo de toma, con un tope de 4,5 %. Los espacios de efecto quedan fuera de la cámara (sus
píxeles, su zona segura y su chequeo de cara quedan tal como se armaron): la cámara vuelve exacto a 1 cuando empieza
un efecto y parte de 1 cuando termina, así que nunca salta en el borde de un espacio. Los estilos completos no la usan:
sus tomas ya tienen su propio acercamiento.

```json
"camera": {"rate": 0.015, "max": 0.045, "alternate": true}
```
En `plan.json` (este reel) o en `my-style.json` (siempre). `"camera": false` deja la imagen quieta (dilo solo si el
usuario lo pide). `rate` más alto = más movimiento; `alternate: false` = todas las tomas se acercan. `build_reel.py`
imprime `camera=live (...)` con el acercamiento de las primeras tomas, y `frames_check.py` sigue a la cámara por su
cuenta: sus dos números siguen sirviendo.

## 3. Entradas de movimiento (motion)

Las entradas con nombre del motor (pop, fade, slide-up, type-on, word-by-word) son atajos, no el límite. Cuando un
ejemplo, una nota o estas reglas piden otro movimiento (letras que caen de a una, un desenfoque que entra, un rebote,
una palabra que tiembla, un golpe de zoom en cada palabra clave, un destello en cada corte, una deriva), escríbelo como
**entradas de movimiento**: tweens de GSAP sobre la línea de tiempo del reel, que el render dibuja exactos.

### Una entrada

```json
{"target": ".w", "tween": "from", "vars": {"yPercent": 60, "opacity": 0, "duration": 0.28, "ease": "power3.out", "stagger": 0.05}, "at": 0}
```

| Campo | Qué es |
|---|---|
| `target` | un selector css DENTRO del elemento al que pertenece la entrada, o `self` para el elemento mismo |
| `tween` | `from` (desde estos valores hasta cómo se ve), `to` (desde cómo se ve hasta estos), `fromTo` (con `from`), `set` (salto) |
| `vars` | cualquier variable de GSAP: `x`, `y`, `xPercent`, `yPercent`, `scale`, `scaleX`, `rotation`, `skewX`, `opacity`, `filter` ("blur(12px)"), `clipPath`, `color`, `backgroundColor`, `letterSpacing`, `transformOrigin`, `duration`, `ease`, `stagger` (un número o `{"each": 0.04, "from": "center"}`), `repeat`, `yoyo`, `delay` |
| `from` | los valores de partida, solo para `fromTo` |
| `at` | segundos después de que el elemento entra (por defecto 0) |
| `at_end` | en vez de `at`: segundos antes de que el elemento se vaya (una salida) |

Nunca valores al azar (`random(...)`, `"from": "random"`) ni código: el render puede cargar la página más de una vez y
dos renders del mismo cuadro tienen que ser iguales. Escribe los números (un temblor = una lista corta de valores x
fijos con `repeat`, o varias entradas `to`). El armado deja fuera la entrada y lo dice en una NOTE.

### Dónde van

| Dónde | Campo | Pertenece a | Los tiempos son |
|---|---|---|---|
| Subtítulos a medida | `caption.motion` | cada línea (`.cu`); apunta a `.ln` (una línea), `.w` (una palabra), `.w.m` (una marcada), `.ch` (una letra, con `entrance: "type-on"`) | después de que entra la línea / `at_end` antes de que se vaya |
| Subtítulos a medida | `caption.word_motion` | cada palabra, en el momento en que se dice | después de que empieza la palabra |
| Subtítulos a medida | `caption.mark_motion` | cada palabra marcada (num, key, emph, cta), al decirse | después de que empieza la palabra |
| Una capa | `layers[].motion` | esa capa (su html); escribe las letras como `<span class='ch'>` para animarlas de a una | después del `from` de la capa / `at_end` antes de su `to` |
| Todo el reel | `motion` (arriba en `plan.json` o en `my-style.json`) | la página; `target` es un selector, o `footage` (la imagen, el recorte y las palabras detrás de la cabeza, dentro de la cámara viva), `speaker` (el recorte), `captions`, `layers` | `at` = segundos del reel, o un patrón con `on` |

Una entrada de todo el reel con **`on`** se repite en cada momento de un tipo, así que sirve en cualquier reel:
- `"on": "marks"` cada palabra marcada (`"kinds": ["key", "num"]` para solo algunas), `"on": "words"`,
  `"on": "cuts"`, `"on": "start"`
- `"every": 2` una de cada dos, `"offset": -0.05` un poco antes

`my-style.json` guarda solo las entradas con `on` (los tiempos fijos pertenecen a un solo reel). Un efecto tapa la
imagen mientras dura su espacio: un golpe de zoom sobre `footage` no se ve dentro de un efecto.

### La deriva de una capa

Una capa en una franja (`top`, `above-head`, `center`, `chest`, `lower-third`) crece 2 % mientras se queda, sola, para
cumplir la regla de oro. `"drift": 0.03` la cambia, `"drift": 0` la apaga. Las capas `full` y `behind` no derivan
(un borde o un fondo se saldría de sus bordes), salvo que les pongas `drift`. Una capa cuyo propio `motion` mueve a
`self` no deriva: su movimiento ya manda.

## 4. Recetas (parte de aquí y luego iguala el ejemplo)

Línea de subtítulos que entra desenfocada:
```json
"motion": [{"target": "self", "tween": "from", "vars": {"filter": "blur(14px)", "opacity": 0, "duration": 0.12, "ease": "power1.out"}}]
```
Palabras que suben una tras otra, la línea se va hacia arriba al final:
```json
"motion": [{"target": ".w", "tween": "from", "vars": {"yPercent": 70, "opacity": 0, "duration": 0.25, "ease": "power3.out", "stagger": 0.05}},
           {"target": "self", "tween": "to", "at_end": 0.12, "vars": {"y": -24, "opacity": 0, "duration": 0.12, "ease": "power2.in"}}]
```
La palabra clave cae de golpe:
```json
"mark_motion": {"tween": "fromTo", "from": {"scale": 1.6, "rotation": -6}, "vars": {"scale": 1, "rotation": 0, "duration": 0.22, "ease": "back.out(3)"}}
```
La palabra dicha da un saltito:
```json
"word_motion": {"tween": "fromTo", "from": {"scale": 1.12}, "vars": {"scale": 1, "duration": 0.18}}
```
Golpe de zoom en cada palabra clave y un destello en cada corte:
```json
"motion": [{"on": "marks", "kinds": ["key", "num"], "target": "footage", "tween": "to", "vars": {"scale": 1.07, "duration": 0.1, "yoyo": true, "repeat": 1, "transformOrigin": "50% 35%"}},
           {"on": "cuts", "target": "#root", "tween": "fromTo", "from": {"filter": "brightness(1.7)"}, "vars": {"filter": "brightness(1)", "duration": 0.18}}]
```
Un sticker que salta y se mueve una vez:
```json
"motion": [{"target": "self", "tween": "from", "vars": {"scale": 0, "rotation": 14, "duration": 0.45, "ease": "elastic.out(1, 0.5)"}},
           {"target": "self", "tween": "to", "at": 0.6, "vars": {"rotation": -4, "duration": 0.08, "yoyo": true, "repeat": 3}}]
```
Una tarjeta con filas (agrupar, desfasar, traslapar): la tarjeta entra entera, las filas entran de a una antes de que
la tarjeta termine de asentarse, y la tarjeta sigue derivando sola:
```json
"motion": [{"target": "self", "tween": "from", "vars": {"y": 60, "scale": 0.92, "opacity": 0, "duration": 0.32, "ease": "back.out(1.6)"}},
           {"target": ".row", "tween": "from", "at": 0.24, "vars": {"x": -28, "opacity": 0, "duration": 0.22, "ease": "power3.out", "stagger": 0.06}},
           {"target": "self", "tween": "to", "at": 0.32, "vars": {"scale": 1.02, "duration": 2.0, "ease": "sine.inOut"}}]
```
Clic en un botón (dentro de una capa con `<div class='btn'>`), a los 0,8 s de la capa:
```json
"motion": [{"target": ".btn", "tween": "to", "at": 0.8, "vars": {"scale": 0.96, "duration": 0.067, "yoyo": true, "repeat": 1, "ease": "power1.inOut"}}]
```
Cursor en arco (un `<div class='cur'>` con el puntero en SVG, dentro de una capa `full`, con css
`.cur{position:absolute;left:0;top:0}`: su lugar sale solo de `x` / `y`, y el de partida va en `from`; el primer viaje parte con la capa, en `at` 0, para que nunca se vea en la esquina). x e y viajan
con curvas distintas, así que el camino se curva; llega con un pequeño exceso y aprieta:
```json
"motion": [{"target": ".cur", "tween": "fromTo", "at": 0, "from": {"x": 180}, "vars": {"x": 620, "duration": 0.7, "ease": "power2.inOut"}},
           {"target": ".cur", "tween": "fromTo", "at": 0, "from": {"y": 1300}, "vars": {"y": 980, "duration": 0.7, "ease": "back.out(1.4)"}},
           {"target": ".cur", "tween": "to", "at": 0.72, "vars": {"scale": 0.85, "duration": 0.067, "yoyo": true, "repeat": 1}}]
```
Para que el cursor dude entre dos lugares (una persona que se pierde), deja 0,4 a 1 s quieto con una deriva de 3 a 6
px antes del siguiente viaje.

## 5. Leer el movimiento de un ejemplo

En las hojas de `study.py`, mira los cuadros alrededor de cada momento en que algo aparece o se mueve, y anota: qué se
mueve (la línea, cada palabra, cada letra, la imagen), desde dónde (abajo, el lado, más grande, desenfocado,
invisible), cuánto dura (cuenta cuadros: 3 cuadros = 0,1 s), si se pasa y se asienta (`back.out`, `elastic.out`) y qué
más se mueve con eso. Cuando haga falta más detalle, saca los cuadros seguidos de ese momento con ffmpeg. Luego
escribe las entradas, arma, toma instantáneas en los mismos momentos y compara (`side_by_side.py`). Una pasada de
pulido.

## 6. Revisión

El movimiento pasa por las mismas revisiones que todo lo demás (`references/checks.md`, "Revisión del movimiento"):
`hf lint` con 0 errores, instantáneas en la MITAD de cada movimiento (no solo cuando se asienta) y los cuadros del
render final. Algo que se mueve no puede cruzar la cara ni salir de la zona segura en ningún cuadro del movimiento.

Movimiento sobre la imagen (`footage`, `speaker`, `#root`): los subtítulos y la caja de la cara están ubicados para la
imagen sin mover. Haz que un golpe de zoom vuelva (`"yoyo": true, "repeat": 1`, o un `to` después con `scale: 1`) salvo
que el ejemplo de verdad lo mantenga, déjalo chico (1,03 a 1,08) y que crezca desde la cara (`transformOrigin` en la
cabeza). La autorrevisión automática no puede comparar una imagen movida así con la toma, así que `build_reel.py` lo
avisa y `frames_check.py` deja de marcar esos cuadros: mira tú su hoja. La cámara viva es distinta: esa sí la sigue
`frames_check.py`.
