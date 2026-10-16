# pull-back-reveal (Revelado)

**Qué hace:** el video en vivo se achica a una tarjeta dentro de una ventana de app simple sobre una página clara. Al
lado, un checklist de la edición real se va marcando, la tira de línea de tiempo de la ventana reproduce las tomas del
propio reel, y un contador sube a su número mientras todo pasa a "listo". Luego la tarjeta vuelve a crecer a cuadro
completo.
**Función:** prueba ("este video lo editó ...", "esto es lo que acaba de hacer", "tomó N pasos"). Funciona como frase
gancho o a mitad del reel.
**Frases que lo activan:** "aléjate y muestra este video editándose", "achícame en la ventana de la app y marca lo que
hizo", "muestra la edición pasando a mi alrededor".

## Primer paso: solo lo que es verdad de este reel
Todo lo que muestra la ventana es una afirmación sobre la edición propia del usuario. Escribe `STEPS` y `SHOTS` desde la
lista de edición del propio reel (`edl.json` / `plan.json`: cuántos clips se transcribieron, cuántas tomas se cortaron,
la duración de cada toma en cuadros, si se agregaron subtítulos y sonido). `COUNT_TO`, `COUNT_LABEL` y `COUNT_NAME` son
solo lo que la persona dice en este clip. Nunca inventes un paso, una cantidad, un número o un nombre. El total de
cuadros es la suma de `SHOTS`, calculado, nunca escrito. La ventana es simple a propósito: un título de texto, sin logo,
sin la interfaz de un producto real. Los valores por defecto ("Paso uno", sin tomas, sin contador) son de relleno y
`build.py` avisa mientras sigan ahí. Nada verdadero que mostrar = deja fuera este efecto.

## Toma que necesita
- **Plano:** abierto, medio o cercano. Toda la imagen entra en la tarjeta (al 62%), así que la persona nunca se corta.
- **Cámara:** quieta, con deriva o en movimiento. No se sigue nada.
- **Pared:** ninguna.
- **Recorte:** no hace falta (crea el espacio con `--no-cutout`). Por eso funciona bien aunque la silla oscura se mezcle
  con la ropa.
- **Lo rompe:** una cara en el cuarto izquierdo de la imagen a media altura (el checklist tapa unos 170 px del borde
  izquierdo de la tarjeta: pon `FACE` y el panel se aparta, o el armado avisa); una cabeza muy arriba en la imagen (la
  barra de título tapa los 68 px superiores del clip); algo importante en los 240 px inferiores del clip (la tira de
  línea de tiempo); un espacio de menos de unos 3,5 s; un espacio que corta a otra toma.
- **Bordes:** el cuadro 0 y el último son el clip sin tocar. Se achica en `F_IN`, la imagen vuelve en `F_OUT`. Sin color,
  atenuación ni acercamiento propios (`GRADE=0` se acepta y no cambia nada). Excepción: `F_OUT = 'cut'` mantiene la
  ventana hasta el último cuadro y el reel tiene que cortar a otra toma ahí.

**Entradas del espacio:** recorte no, `aroll_hi` no. Python: numpy para `onsets.py`, numpy y Pillow para `check.py`;
`build.py` no necesita nada. Sin arte, solo sonidos de stock.

## Las palabras son el efecto: bloque STYLE (inicio de build.py)
El checklist, el título de la ventana, la línea de estado, el contador, la etiqueta y el nombre son el efecto, no
subtítulos. Cuando el reel tiene un estilo de subtítulos o completo, ajusta el bloque `STYLE` ANTES de armar: `ui_font`,
`ui_weight`, `ui_case` (filas, títulos), `mono_font` (etiqueta, estado, conteo de cuadros), `num_font` (dígitos,
insignia, nombre), `label_font`, `label_italic`, `label_case`, los colores (`page`, `window`, `panel`, `ink`, `muted`,
`accent`, `done`, `highlight` ...), `radius`, y las entradas de ubicación `window_x` y `panel_y`. Las tipografías tienen
que estar en `assets/fonts/fonts.css`; `width_factor` amplía las revisiones de ajuste para una tipografía más ancha.
Los textos de la ventana van en español.
**Subtítulos:** los subtítulos propios del reel van al centro del cuadro completo, medio fuera de la tarjeta pequeña,
así que se ocultan mientras dura el espacio (`fx_add.py --captions hide`). En su lugar el efecto dibuja las palabras
dichas en la tarjeta, desde `words.json`, solo mientras la tarjeta está chica. Ajusta `cap_font`, `cap_weight`,
`cap_case`, `cap_size`, `cap_tracking`, `cap_color`, `cap_mark`, `cap_words` al estilo de subtítulos del reel para que el
reel mantenga un solo look de subtítulos. Límite: las palabras de la tarjeta toman tipografía, mayúsculas, tamaño y
color, no una placa detrás ni una palabra que se ilumina al decirse: avísale al usuario cuando su estilo tiene una de
esas. Interruptor: `CAPTIONS=0` no dibuja palabras de subtítulo (la tarjeta entonces no lleva subtítulos salvo que se
mantengan los del reel; esos van centrados en el cuadro, no en la tarjeta). Mantén cortos `F_IN` y la cola después de
`F_OUT`: las palabras dichas mientras la imagen está a cuadro completo no tienen subtítulo.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `STEPS` | 2 a 7 líneas de checklist, unos 22 caracteres cada una; `('texto', cuadro)` fija una marca | la lista de edición del reel; solo pasos verdaderos |
| `SHOTS` | la duración de cada toma en cuadros, en orden (`[]` = una barra simple, sin conteo de cuadros) | `edl.json`: segundos x 30 |
| `WINDOW_TITLE`, `WINDOW_FILE` | texto a la derecha de la barra de título; nombre de archivo pequeño al medio (`''` = ninguno) | las palabras del usuario; texto simple |
| `PANEL_TITLE`, `PANEL_TAG` | línea gris sobre la lista; cápsula al lado (`''` = ninguna) | lo que está haciendo el trabajo |
| `STATUS_RUN`, `STATUS_DONE` | palabra de estado en la tira, antes y después de `DONE_AT` | por defecto (ponlas en español: "editando", "listo") |
| `COUNT_TO`, `COUNT_UNIT` | número en que cae el contador (`None` = sin contador); 1 o 2 caracteres en la insignia | un número que dice la persona |
| `COUNT_LABEL`, `COUNT_NAME` | línea corta bajo el número; una palabra destacada bajo eso (`''` = ninguna) | las palabras de la persona |
| `F_IN` | cuadro en que empieza a achicarse (2 o más); llega 12 cuadros después | justo antes de la frase |
| `TICK_FROM`, `DONE_AT` | primera marca; última marca = línea de tiempo terminada = el contador cae | `onsets.py`: la palabra que dice que está listo |
| `COUNT_AT`, `LABEL_AT`, `NAME_AT` | los dígitos empiezan a girar; la etiqueta se escribe (un cuadro, o uno por palabra); el nombre aparece | inicios de esas palabras; `None` = repartidos después de `DONE_AT` |
| `F_OUT` | `'auto'` (3 cuadros antes del final), un cuadro, o `'cut'` | deja 12 cuadros para la vuelta |
| `FACE` | `(x0, y0, x1, y1)` alrededor de la cara en el clip, px; el panel se mantiene fuera | un cuadro de `assets/aroll.mp4` |
| `CAP_FIX`, `CAP_MARK` | palabras de subtítulo mal escuchadas `{'escuchado': 'dicho'}`; palabras en el color de acento | las líneas de subtítulo que imprime `build.py` |
| `SOUNDS`, `SEED` | `'auto'`, `[]`, o `(nombre, cuadro, volumen)` con nombres de stock; mezcla de barras | por defecto |

**Interruptores:** `SAFE=1` guía de zona segura (solo instantáneas), `CAPTIONS=0` sin palabras de subtítulo en la
tarjeta, `SFX=0` sin sonidos, `GRADE=0` se acepta (no hay color que sacar).

## Orden de ejecución (PY y SK como en SKILL.md, <slot> = la carpeta del espacio; sin cd, sin variables de terminal)
```
# primero: lee la lista de edición propia del reel (edl.json / plan.json) y escribe STEPS y SHOTS desde ella: solo pasos que realmente se hicieron y la duración real de cada toma en cuadros. COUNT_TO, COUNT_LABEL y COUNT_NAME son solo lo que la persona dice en este clip. Nunca inventes un paso, una cantidad, un número o un nombre, nunca dibujes un logo. Nada verdadero que mostrar = deja fuera Revelado y dilo
PY "SK/scripts/fx_run.py" "<slot>" onsets.py      # 1. cada palabra con su cuadro
# editar: el bloque STYLE y el bloque CLIP en build.py (pasos verdaderos y duraciones de toma desde la lista de edición del reel)
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # 2. página con la guía; imprime cada momento, las líneas de subtítulo, los tiempos de instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint      # tiene que dar 0 errores
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <tiempos que imprimió build.py>
PY "SK/scripts/fx_run.py" "<slot>" build.py      # 3. guía apagada
PY "SK/scripts/fx_run.py" "<slot>" hf render
PY "SK/scripts/fx_run.py" "<slot>" check.py      # 4. cantidad de cuadros, bordes simples, work/check/sheet.jpg, copia para celular
```
`fx_new.py` imprime estos comandos con las rutas reales y los guarda como `RUN.txt` en el espacio. `hf render` nombra el
archivo solo, se niega a correr con la guía roja puesta y revisa la cantidad de cuadros. Último paso en un reel:
`PY "SK/scripts/fx_add.py" "<project>" "<slot>"`.

## Qué mirar (work/check/sheet.jpg)
- Todo el clip está en la tarjeta; la cara queda fuera del panel del checklist, la barra de título y la tira.
- En el cuadro DONE (no uno después): cada paso marcado, la línea de tiempo en el color de listo, el conteo de cuadros en
  su total, el contador en `COUNT_TO`. En el cuadro anterior, la última marca todavía está apareciendo y los dígitos
  siguen girando. Cada marca empieza dos cuadros antes de su cuadro, así que está completa EN su cuadro.
- Cada texto cabe en su caja (filas dentro del panel, título dentro de la barra, etiqueta y nombre a la izquierda de la
  ventana).
- Con `SAFE=1`: nada en las franjas rojas. `build.py` imprime las cajas de la ventana y del panel.
- "before", "back" y "last" son la imagen simple (`check.py` imprime la diferencia descontando el cambio general de tono
  del render); la cantidad de cuadros coincide con `clip.json`.

## Trampas
- El espacio necesita unos 105 cuadros con contador, etiqueta y nombre, más 15 para la vuelta: `build.py` dice cuántos
  cuando es corto. Las marcas están a 4 cuadros o más entre sí.
- Los anchos de texto se estiman al armar. Otra tipografía puede ser más ancha: mira una instantánea, sube
  `width_factor`.
- `window_x = 375` da una columna izquierda más ancha y dígitos más grandes, pero la esquina inferior derecha de la
  ventana queda bajo los botones de la app (ahí no hay texto).
- Los inicios de palabra de Whisper están 1 a 3 cuadros corridos y escucha mal los nombres: usa la columna de inicios,
  corrige la ortografía en `CAP_FIX`.
- Los sonidos son solo de stock a 0,75x del volumen de la plantilla (`whoosh-short`, `click-soft`, `impact-bass-1`,
  `pop`). Colores: nunca naranjo. `F_OUT = 'cut'` solo donde el reel realmente corta en el último cuadro del espacio;
  si no, la ventana sale de golpe. Un espacio de 5 s toma unos 5 minutos (no hay recorte que esperar).
