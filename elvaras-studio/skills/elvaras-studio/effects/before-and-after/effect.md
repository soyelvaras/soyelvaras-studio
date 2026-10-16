# before-after (Antes y Después)

**Qué hace:** corre el clip crudo, una línea de comparación con un tirador redondo asoma en la palabra de entrada, se
retira suave y espera al lado de la cabeza, luego barre la pantalla en la palabra de remate y deja la versión editada
de los mismos cuadros (color, sombra suave, palabras de subtítulo, acercamiento lento, palabra opcional detrás de la
cabeza). Dos etiquetas viajan con la línea.
**Función:** prueba. **Frases que lo activan:** "haz un barrido antes y después en esta frase", "muestra el clip crudo
convirtiéndose en la edición".

## Toma que necesita
- **Plano:** abierto, medio o cercano. **Cámara:** quieta, con deriva o en movimiento (ambos lados son los mismos
  cuadros, nada se puede correr). **Pared:** no hace falta.
- **Recorte:** solo se mide (la posición de la cabeza decide dónde espera la línea, el tirador y la altura de los
  subtítulos); se usa como capa solo cuando `PUNCH` tiene valor. Un espacio creado con `--no-cutout` (más barato)
  igual corre: dale a `REST` una x a ojo o hace un solo barrido directo, y `PUNCH` queda fuera.
- **Qué lo rompe:** la palabra de remate en los primeros 0,3 s del espacio; menos de 1,5 s de espacio después del
  barrido (el look "después" no alcanza a verse, build.py avisa); una cabeza tan ancha que no hay lugar donde espere la
  línea (vuelve a un solo barrido); una frase que no habla de un cambio (ahí es decoración, no prueba).

## De dónde sale el lado "después"
1. **Hecho aquí (por defecto, `AFTER = None`).** La misma toma con `AFTER_GRADE`, `AFTER_SHADE`, `CAPS`, `PUSH`, y
   opcionalmente `ACCENT` / `PUNCH`. Sin trabajo a mano, un render.
2. **Tu propia versión terminada.** Copia el archivo a `after/` en el espacio, pon `AFTER = 'after/<archivo>'`, ejecuta
   `prep_after.py`. Tienen que ser los MISMOS cuadros: la misma toma, 9:16, empezando en el primer cuadro del espacio,
   cubriendo todo el espacio, sin acercamiento, reencuadre ni cambio de velocidad (los subtítulos y gráficos encima
   están bien). Su sonido se ignora, la voz es la de la toma. `prep_after.py` imprime el desfase en cuadros (si no es
   0, te dice el `AFTER_SHIFT` a poner) y una coincidencia de silueta (bajo 0,33 no calza, usa el modo 1). `CAPS`,
   `PUNCH`, `AFTER_GRADE` y `PUSH` no hacen nada en este modo, y `OUT` desvanece tu archivo (los subtítulos quemados
   se desvanecen a mitad de palabra: mejor `OUT = None` y terminar en un corte).

## Entradas del espacio
`assets/aroll.mp4`, `words.json`, `clip.json`, `assets/subject.webm` (opcional, ver arriba). Sin `aroll_hi`. Las
tipografías y `whoosh-short.mp3` / `pop.mp3` vienen de la plantilla. Solo numpy y Pillow.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `COMMIT` | palabra de remate, la línea barre en ella | una palabra o frase de la lista de `measure.py`, `('palabra', 2)` para la 2.ª vez que la dice, o segundos |
| `PEEK` | palabra de entrada, la línea asoma y espera | una palabra 0,7 s o más antes de `COMMIT`; `None` = un solo barrido directo |
| `REST` | x donde espera la línea | `'auto'` (medido: 70 px fuera de la cabeza, fuera del subtítulo, etiquetas legibles); un número; `None` |
| `SWEEP` | segundos que dura el barrido | 0.5; 0.4 si la palabra siguiente llega rápido |
| `LABELS` | las dos etiquetas | `('antes', 'después')` o dos palabras propias de la persona; `None`. Nunca una afirmación o número que no dice |
| `LABEL_IN`, `LABEL_Y` | cuándo aparece la primera etiqueta, parte superior de las etiquetas | `'auto'`, 232; cambia solo si build.py avisa |
| `AFTER`, `AFTER_SHIFT` | modo con archivo propio | ver arriba |
| `AFTER_GRADE`, `AFTER_SHADE` | el look del lado "después" | un filtro CSS / `True`. Este color ES el efecto; se va con `OUT` |
| `PUSH` | acercamiento en el lado "después" tras el barrido | 1.045; 1 = apagado |
| `CAPS`, `CAP_Y` | líneas de subtítulo en el lado "después" | `'auto'` (desde words.json, minúsculas), o una lista de líneas con una entrada por palabra dicha en orden (corrige aquí la ortografía de Whisper); `None` |
| `ACCENT` | una palabra del subtítulo en dorado con subrayado y destellos | una palabra que dice la persona después del barrido; por defecto `None` |
| `PUNCH` | una palabra que dice la persona, grande detrás de su cabeza | la palabra de remate; necesita el recorte; por defecto `None` |
| `HANDLE_Y` | altura del tirador | `'auto'` |
| `OUT` | cuándo se suaviza el look "después" | `'auto'` (por defecto: últimos 0,6 s, el espacio termina en imagen simple); segundos; `None` = el espacio TERMINA EN UN CORTE con el look puesto (solo como lo último antes de un corte o del final del reel) |

## Interruptores
`SAFE=1` guía de zona segura (solo instantáneas). `CAPTIONS=0` sin palabras de subtítulo, acento ni palabra de golpe
(las etiquetas se quedan). `SFX=0` sin whooshes / pop.

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
PY "SK/scripts/fx_run.py" "<slot>" measure.py      # palabras con inicios medidos y dónde está la cabeza; luego edita el bloque CLIP en build.py
PY "SK/scripts/fx_run.py" "<slot>" prep_after.py      # SOLO cuando AFTER nombra tu propio archivo (si no, sáltalo): crea assets/after.mp4 y revisa que calce
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1 CAPTIONS=0      # imprime la posición de espera, tiempos del barrido, líneas de subtítulo y cada aviso (!!)
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at 0.1,2.0,3.0      # usa tus propios tiempos: etiqueta entra, línea esperando, mitad del barrido, look después
PY "SK/scripts/fx_run.py" "<slot>" build.py CAPTIONS=0      # guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # cantidad de cuadros, bordes simples, ambos lados mientras espera la línea, hoja, cuadros, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.
Un espacio de 5,5 s toma unos 4 minutos una vez que existe (render en menos de 1 minuto); crear el espacio con recorte
suma el recorte, `--no-cutout` no suma nada.

## Qué mirar en los cuadros finales (work/check/sheet.jpg)
- El cuadro 0 es la imagen simple. Con `OUT` puesto, los últimos cuadros también lo son (check.py imprime el primer y
  el último cuadro tocado).
- Mientras la línea espera está al lado de la cabeza, nunca sobre la cara; ninguna letra de subtítulo cortada por la
  mitad en la línea; ambas etiquetas completamente legibles.
- A mitad del barrido: un borde limpio, la imagen no salta en la línea (un salto = los dos lados no son los mismos
  cuadros).
- Después del barrido la diferencia tiene que leerse en tamaño celular. Si no, usa un `AFTER_GRADE` más fuerte o
  agrega `PUNCH`.
- Los subtítulos van bajo la barbilla, nada legible sobre y 220, bajo y 1470, ni a menos de 35 px de los lados.

## Trampas
- `mask-image` / `clip-path` no se renderizan de forma confiable: el lado "después" es una caja `overflow:hidden`
  movida a la línea con su contenido devuelto la misma cantidad.
- Cada capa que sigue a la línea se muestrea por cuadro en Python y se escribe como fotogramas clave lineales. Las
  animaciones suavizadas por separado se corren uno o dos píxeles y el borde se rasga.
- La caja se detiene en x 0 mientras la línea sigue fuera de pantalla, o los 80 px de la derecha vuelven a mostrar el
  ANTES.
- El acercamiento empieza solo cuando terminó el barrido: la imagen "después" no debe moverse mientras la línea está
  en pantalla.
- Dos etiquetas `<video>` sobre un mismo archivo las une el motor de render (lint: `duplicate_media_discovery_risk`):
  build.py copia la toma a `assets/aroll_b.mp4` para el lado "después". Cada video necesita un `z-index` explícito.
- Nunca animes la opacidad de `#aclip` (lleva la x con fotogramas clave): todo el lado "después" desaparece desde el
  cuadro 0. El suavizado final desvanece `#afade` dentro de él.
- `data-duration` se redondea hacia abajo al milisegundo (5.167 renderiza un cuadro de más).
- Los inicios de palabra de Whisper están 0,1 a 0,3 s corridos: nombra la palabra y deja que `measure.py` la ajuste;
  escribe segundos solo si una instantánea muestra que está mal.
- El texto en pantalla son palabras propias de la persona, escritas a su manera: ni números, resultados ni
  afirmaciones que no dijo.
