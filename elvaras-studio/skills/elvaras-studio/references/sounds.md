# Sonidos: cuál va dónde

Todos viven en `ST/sfx/<nombre>.mp3` (la ruta `sfx_dir` de `.platform.json`), y `init_project.py` los copia a
`<project>/assets/sfx/`. En `plan.json` van así: `{"src": "assets/sfx/<nombre>.mp3", "at": <s>, "vol": <0-1>, "dur": <s>,
"media": <s>}`. `at` es cuando se oye, `media` desde dónde del archivo y `dur` cuánto.

Reglas para todos:
- **Cada sonido va pegado a algo que se ve:** un gráfico que entra, un corte, un clic, una palabra fuerte. Sin animación
  no hay sonido.
- **Siempre bajo la voz:** el pico entre 15 y 20 dB bajo ella. El `vol` de las tablas ya lo cumple con una voz grabada
  normal (pico de la voz ~-1 dB, promedio ~-16 dB). Ajústalo si la voz quedó más baja.
- **No repitas el mismo archivo** tres veces seguidas en menos de 2 s: alterna entre las variantes de su familia.
- **Los sonidos que suben** (riser, `whoosh-grave-largo`) se ponen ANTES del momento. Se pone `at` = momento − tiempo del
  pico (columna "pega en").
- De dónde vienen:
  - Los 19 de stock los descarga setup.py.
  - Los propios de Soy Elvaras (desde `whoosh-aire`, 23-10-2026) son de Cristobal. Van dentro de la skill, en `sfx/`, y
    setup.py los copia a `ST/sfx` sin pisar nada.
  - Si alguno falta (un Studio antiguo, una carpeta de estado sin revisar), usa la columna "si falta" y vuelve a correr
    setup.py.
  - Un sonido nuevo de él va a `sfx/` con el mismo tratamiento: recortado donde empieza, pico en -1 dBFS, mp3 a 48 kHz.
    Lleva además su fila en esta guía.

## Golpes de aire (whoosh): la familia más grande

Elige por lo que **se mueve** en pantalla:

| Nombre | Dura | Pega en | vol | Úsalo cuando... | Si falta |
|---|---|---|---|---|---|
| `whoosh-short` | 0,57 | 0,16 | 0,12–0,16 | una página o una escena entra o sale, cambio de escena común. El comodín. | — |
| `whoosh-aire` | 0,76 | 0,15 | 0,16 | entra algo LIVIANO y claro: una tarjeta, una burbuja, una ventana. Más aireado que `whoosh-short`. | `whoosh-short` |
| `whoosh-brillo` | 0,68 | 0,13 | 0,14 | entra algo brillante o dorado (una palabra clave, el sello, un brillo). Agudo. | `whoosh-short` |
| `whoosh-medio-1` | 0,76 | 0,30 | 0,10 | una cámara 2D se desliza de lado (travelling), un panel que cruza. Cuerpo medio. | `whoosh-short` |
| `whoosh-medio-2` | 0,80 | 0,22 | 0,16 | igual que `medio-1`, para alternar en una serie de deslizamientos. | `whoosh-short` |
| `whoosh-medio-3` | 0,80 | 0,27 | 0,10 | el deslizamiento más fuerte del medio: un salto de sección (paso 1 → paso 2). | `whoosh-short` |
| `whoosh-medio-4` | 0,90 | 0,30 | 0,09 | algo grande gira o da vuelta (una carta que se voltea, una tarjeta en 3D). | `whoosh` |
| `whoosh-suave` | 1,02 | 0,26 | 0,14 | movimientos chicos bajo una frase importante, cuando el sonido no debe competir. | `whoosh-short` a 0,08 |
| `whoosh-latigo` | 0,70 | 0,10 | 0,12 | un giro BRUSCO de cámara (whip pan), algo que sale volando, un corte seco a otra escena. | `whoosh-short` |
| `whoosh-mini` | 0,31 | 0,07 | 0,11 | un cursor que cruza, un chip que se arrastra, el paso de tarjetas en un carrusel. | `swish-mini` |
| `swish-mini` | 0,24 | 0,05 | 0,17 | el más corto y agudo: cosas que pasan muy rápido en serie (cada carta de un abanico). | `whoosh-mini` |
| `whoosh-grave-1` | 1,08 | 0,58 | 0,11 | la cámara viaja en 3D (zoom al fondo, entrar a otro espacio). Grave, se siente más que se oye. | `whoosh-cinematic` |
| `whoosh-grave-2` | 1,24 | 0,29 | 0,10 | igual que `grave-1`, más corto en la entrada: el empuje de cámara arranca de inmediato. | `whoosh-cinematic` |
| `whoosh-grave-largo` | 2,80 | 1,00 | 0,10 | un movimiento de cámara largo y continuo (una toma continua de 2 s o más, una órbita). | `whoosh-cinematic` |
| `whoosh-cinematic` | 5,54 | 2,54 | 0,07–0,09 | apertura de un bloque grande, la entrada a un mundo 3D. Úsalo con `media` ~1,5 y `dur` ~1. | — |
| `whoosh` | 0,57 | 0,16 | 0,12 | es el mismo archivo que `whoosh-short`. | — |

Cómo elegir entre los graves: si la cámara **avanza o se aleja en profundidad**, usa `grave`. Si se **desliza de
lado**, usa `medio`. Si **gira de golpe**, usa `latigo`. Si lo que se mueve es un **objeto chico**, usa `mini` o `swish`.

## Golpes, subidas y tensión

| Nombre | Dura | Pega en | vol | Úsalo cuando... | Si falta |
|---|---|---|---|---|---|
| `impact-bass-1` | 2,12 | 0,10 | 0,08–0,10 | una palabra fuerte, una explosión, algo grande que aterriza. | — |
| `impact-bass-2` | 2,59 | 2,06 | 0,07 | un golpe con entrada larga (el pico llega a los 2 s). | `impact-bass-1` |
| `bajo-cine` | 2,90 | 0,08 | 0,10 | la revelación más grande del reel (el gancho, el giro final). Más profundo y con más cola que `impact-bass-1`. Máximo uno o dos por reel. | `impact-bass-1` |
| `riser` | 10,0 | 3,47 | 0,06–0,09 | una tensión que sube antes de una palabra (`media` ~8,9 para la subida corta). | `riser-metal` |
| `riser-metal` | 1,97 | 1,64 | 0,16 | una subida metálica corta. Pon `at` = momento − 1,6. Ideal antes de un "¡listo!" o un clic que revela. | `riser` |
| `quemado` | 1,50 | 0,40 | 0,18–0,32 | algo se quema, se prende fuego o se deshace en brasas ("Línea en Llamas", el editor que se quema). | `glitch-3` |

## Interfaz: clics, pops y teclado

| Nombre | Dura | Pega en | vol | Úsalo cuando... | Si falta |
|---|---|---|---|---|---|
| `pop` | 0,72 | 0,01 | 0,10–0,14 | entra un gráfico chico (una etiqueta, un ícono, una burbuja). El pop de siempre. | — |
| `pop-ui` | 0,58 | 0,04 | 0,10 | aparece un elemento de INTERFAZ: un botón, un menú, un panel, una notificación propia. Más redondo y grave que `pop`. Alternalos en una serie. | `pop` |
| `click-soft` | 0,37 | 0,01 | 0,25–0,30 | el cursor hace clic, se apreta un botón o se presiona Enter. | — |
| `click` | 0,37 | 0,01 | 0,25 | es el mismo archivo que `click-soft`. | — |
| `key-press` | 0,40 | 0,00 | 0,13–0,16 | un tic: cada marca de una línea de tiempo, cada carril que se enciende. | — |
| `typing` | 1,50 | 0,02 | 0,30 | se escribe en un TECLADO (la caja de Claude, un chat). | — |
| `tipeo-letras` | 1,60 | 0,20 | 0,25 | las letras aparecen de a una, como en una MÁQUINA DE ESCRIBIR (un titular que se escribe solo). | `typing` |
| `ping` | 1,32 | 0,01 | 0,18–0,20 | llega una respuesta (Claude contesta, algo queda listo). | — |
| `notification` | 2,46 | 0,15 | 0,12 | una notificación de celular, un "+1 seguidor", un "Listo 100%". | `ping` |
| `chime` | 2,50 | 0,26 | 0,15 | un logro suave, un cierre amable. | `sparkle` |
| `sparkle` | 1,80 | 0,07 | 0,08–0,09 | un brillo: la palabra de comentar, un sello dorado, la mascota. | — |
| `error` | 1,62 | 0,05 | 0,20 | algo sale mal (un aviso de error, una toma mala). | `glitch-3` |
| `glitch-1`, `glitch-2`, `glitch-3` | 2,6–3,5 | — | 0,09 / 0,06 / 0,13–0,14 | un tachado, una interferencia, algo que se borra. Para un tachado, `glitch-3` con `dur` 0,3–0,35. | — |

## Cámara, escritura y censura

| Nombre | Dura | Pega en | vol | Úsalo cuando... | Si falta |
|---|---|---|---|---|---|
| `flash` | 0,57 | 0,11 | 0,16 | se toma UNA foto: un cuadro congelado, un antes y después, una captura que aparece. | `click-soft` |
| `flash-triple` | 0,87 | 0,11 | 0,16 | una RÁFAGA de fotos: varias capturas seguidas, un mosaico que se arma de golpe. | `flash` ×3 |
| `obturador` | 0,75 | 0,09 | 0,23 | obturador de cámara de verdad: "Congela y Señala", un cuadro que queda quieto. Más mecánico que `flash`. | `click-soft` |
| `obturador-motor` | 0,37 | 0,25 | 0,28 | obturador con motor (35 mm): pasar diapositivas, cuadros que cambian como en un rollo. | `obturador` |
| `captura` | 0,69 | 0,50 | 0,34 | la captura de pantalla del celular: una imagen de una app que se "saca" de la pantalla. | `obturador` |
| `boligrafo` | 2,25 | 0,02 | 0,26 | algo se escribe o se marca A MANO: una nota escrita, un check dibujado, una firma. Recorta `dur` al largo del trazo. | `key-press` |
| `rotulador` | 1,77 | 0,02 | 0,21 | se subraya o se encierra una palabra con marcador (la línea que se dibuja bajo la palabra clave). | `boligrafo` |
| `censura` | 1,28 | 0,10 | 0,08–0,11 | el pitido de censura sobre una palabra oculta o tachada ("ni pagarle a un ████"). Corta `dur` al largo de la palabra. | `error` |

## Combinaciones probadas (reels aprobados)
- **Una página entra:** `whoosh-short` (0,16). **Un gráfico aparece:** `pop` (0,12–0,14).
- **Tachado:** el `pop` del gráfico y luego `glitch-3` (0,14, `dur` 0,35) en el tachado.
- **Claude responde:** `typing` (0,3) mientras escribe, `click-soft` al enviar, `ping` (0,2) con la respuesta.
- **Explosión del gancho:** `impact-bass-1` (0,1) y `whoosh-short` (0,13) a la vez.
- **Toma continua en 3D:** `whoosh-cinematic` (0,08) al entrar, `whoosh-grave-*` en cada empuje, `click-soft` en cada
  clic del cursor, `whoosh-mini` cuando arrastra.
- **El editor se quema:** `quemado` (0,32) y un `whoosh-cinematic` muy bajo (0,07).
