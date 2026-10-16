# odometer (Contador)

**Qué hace:** el número que dice la persona sube dígito a dígito como un cuentakilómetros mecánico (cada dígito un
tambor, desenfoque vertical mientras gira, un pelito de rebote y un tic suave cuando se traba al final del número
dicho), en un panel de instrumentos oscuro que va DETRÁS de la persona, al lado de su cabeza. Una etiqueta se escribe
sola en las palabras de la persona.
**Función:** prueba (años, cantidad de clientes, ingresos, porcentajes). Solo números que la persona realmente dice en
el clip.
**Frases que lo activan:** "sube el número como un cuentakilómetros", "cuéntalo cuando digo 10 años", "contador en el
100%", "haz que la cifra gire".

## Toma que necesita, y dónde falla
- Cualquier encuadre con fondo libre al lado o sobre la cabeza: la selfie cercana (demo) y el plano abierto en trípode
  (prueba) funcionan. El panel queda fijo en pantalla, así que en un clip en mano la pared se mueve detrás (se lee como
  una interfaz, está bien); nunca se pega a la pared.
- Falla cuando la persona llena el cuadro de borde a borde durante todo el tramo (build.py se detiene con "no free
  spot"), y cuando el número se dice en los primeros 0,3 s del espacio (no hay tiempo para girar: empieza el espacio
  antes).
- El número tiene que decirse limpio una vez. Números murmurados o repetidos: pon `lock` a mano.
- Uno o dos contadores por espacio. Un tercero funciona, pero las fichas de esquina se amontonan.
- Necesita 1,5 s después del trabado para leerse; las palabras de la etiqueta necesitan sus propios momentos dichos o
  `None`.

## Entradas del espacio
`assets/aroll.mp4`, `assets/subject.webm` (recorte: OBLIGATORIO, los paneles van entre la imagen y el recorte),
`words.json`, `clip.json`. Sin `aroll_hi`. Las tipografías (Inter Tight 900, Montserrat 600) y `click-soft.mp3` /
`whoosh-short.mp3` vienen de la plantilla. Sin paquetes extra de Python (numpy + PIL del Python de la skill).

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `COUNTERS[i].text` | lo que queda trabado en pantalla: dígitos + prefijo/sufijo opcional (`10`, `$200K`, `87%`, `100s`, `1.250`) | el número que dice la persona, escrito como lo espera un espectador |
| `say` | las palabras dichas del número como las tiene words.json (`'cien por ciento'`, `'10'`, `'mil'`) | `measure.py` imprime las palabras; el trabado = fin medido de la última |
| `lock` | segundos, reemplaza `say` | solo si no se encuentra `say` o la columna "measured end" se ve mal |
| `label` | `[(PALABRA, cuándo), ...]`, línea dorada bajo los tambores; pasa a una segunda línea cuando es más ancha que los tambores | `cuándo` = una palabra dicha, segundos, o `None` (justo después del trabado). Las palabras de la persona, en mayúsculas, sin afirmaciones inventadas |
| `label2` | línea(s) extra opcional(es), por defecto `None`; cada lista interna gira sobre la anterior | solo cuando la persona enumera más cosas después del número |
| `sit` | `'auto'`, `'right'`, `'left'`, `'above'`, o `(x, y)` | deja `'auto'`; fuerza un lado si la instantánea se ve recargada |
| `size` | `'auto'` o una escala (1,0 = tambores de 150 px) | deja `'auto'` (lo más grande que deja dígitos y etiqueta libres de la persona, máximo 1,5) |
| `then` | qué hace este contador cuando llega el siguiente: `'dock'` (ficha en una esquina), `'stay'`, `'out'` | `'dock'` para dos pruebas seguidas |
| `ROLL` | segundos de giro antes del trabado | 0,44; 0,35 para un número dicho muy rápido |
| `OUT` | segundos en que salen todos los paneles, o `None` | `None` si el espacio termina en un corte, si no, unos 0,25 s antes de que termine |
| `DOCK_CORNER` | dónde va la ficha | `'auto'` |
| `GRADE` | filtro CSS sobre imagen + recorte | `'none'` cuando el reel da el color |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas). `CAPTIONS=0` paneles solo con números, sin palabras de etiqueta.
`SFX=0` sin tics / whoosh.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # palabras con inicio / fin medidos, dónde está la cabeza
# editar: el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # imprime el cuadro del trabado, posición del panel, tiempos de la etiqueta, avisos (!!)
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.2,1.0,2.0      # usa: giro, trabado+0,1, trabado+0,6, últimos 0,1 s
PY "SK/scripts/fx_run.py" "<slot>" build.py      # guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, prueba de texto detrás de la persona, tiempo de los tics, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 4 s toma unos 6 minutos de punta a punta (render cerca de 1 minuto).

## Qué mirar en los cuadros finales (work/check/sheet.jpg y lock_*.jpg)
- El cuadro de trabado que imprime build.py: último tambor nítido o a un cuadro de estarlo, destello dorado en los
  dígitos, sufijo apareciendo. Dos cuadros antes todavía tiene que ser un desenfoque.
- El cuadro 0 es una imagen limpia (el panel entra a los 0,02 s como mínimo), así que el espacio entra limpio.
- La cabeza de la persona solo tapa una esquina VACÍA del panel. Ningún dígito, sufijo ni palabra de la etiqueta detrás
  de la persona en ningún cuadro (check.py imprime el peor cuadro).
- Borde del recorte sobre el panel oscuro: sin borde claro, sin borde doble (un borde doble = desfase en la cantidad de
  cuadros del recorte).
- Nada legible sobre y 220, bajo y 1470, ni a menos de 35 px de los lados.

## Trampas
- Tiempos de palabra de Whisper: los inicios se corren hasta 0,35 s y parte las palabras rápidas en el lugar
  equivocado. Nunca los escribas; `measure.py` los ajusta al audio (la caída más cercana, no la más profunda: la caída
  más profunda alrededor de "diez" es la pausa dentro de la palabra).
- `click-soft.mp3` tiene 48 ms de silencio antes del golpe y es un doble clic: build.py lo empieza antes y lo recorta.
  Cualquier otro archivo de tic necesita su propio `SFX_LEAD` / `SFX_TRIM`.
- El volumen del tic sigue el nivel de voz medido de la persona (`VOICE_REF`); check.py imprime cuánto quedó bajo la
  voz (apunta a 12 dB o más).
- El desenfoque direccional es un SVG `feGaussianBlur stdDeviation="0 N"` puesto por cuadro según la velocidad de la
  tira. El `blur()` de CSS es igual en todas direcciones y se ve como desenfoque.
- El giro es un `tl.set` por cuadro (`frame/30 - 0.002`), no una curva de GSAP: resorte exacto, trabado en el cuadro.
- Cada tira lleva un número extra bajo el objetivo, o el rebote muestra un tambor vacío.
- "El panel crece una línea" es scaleY solo en el fondo. Nunca animes height ni letter-spacing (lint).
- Decodifica el recorte con `-c:v libvpx-vp9` ANTES de `-i` o se pierde el alfa (measure.py lo hace).
- Texto en pantalla: solo las palabras de la persona, sin guiones largos, nunca "gratis" ni "curso", ningún número que
  la persona no dijo.
