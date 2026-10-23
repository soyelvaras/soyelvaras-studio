---
name: elvaras-studio
description: "Soy Elvaras Studio. Convierte clips verticales 9:16 de alguien hablando a cámara en un reel de Instagram terminado, con el look guardado en el selector de estilo: uno de 19 estilos de subtítulos o uno de 3 estilos completos, más los efectos y transiciones elegidos. Elige la toma más limpia de cada frase, corta los silencios, transcribe con tiempo por palabra, ubica los subtítulos según dónde está la persona en el cuadro y revisa todo dentro de la zona segura de Reels. Responde siempre en español. Úsala cuando el usuario diga 'edítalo', 'edita estos clips', 'dejé clips en descargas', 'arma un reel con esto', 'cambia mis subtítulos', 'cambia mis efectos', 'cambia mi estilo', 'abre el selector', 'actualiza el Studio', 'haz 5 trial reels', 'hazme versiones de prueba', o sus versiones en inglés ('edit it', 'open the picker', 'make trial reels'), o cuando ejecute /elvaras-studio."
---

# Soy Elvaras Studio (elvaras-studio)

Entran clips crudos, sale un reel terminado con el look que eligió el usuario. Se configura una vez, se elige en el
selector de estilo y desde ahí basta con dejar los clips y decir "edítalo". El usuario nunca abre un editor: mira una
copia para el celular y da notas. Puede cambiar su estilo de edición cuando quiera, con solo pedirlo.

Lee antes de la primera edición: `references/cutting.md` (tomas, silencios, corregir la transcripción),
`references/captions.md` (los 19 estilos de subtítulos, cómo marcar palabras, dónde van los subtítulos),
`references/checks.md` (chequeo de toma, autorrevisión, zona segura), `references/motion.md` (cómo se mueve todo lo
que dibujas: la regla de oro, entradas, salidas, cámara viva, entradas de movimiento). Lee `references/styles.md` cuando las
elecciones tengan un estilo completo, `effects/INDEX.md` cuando tengan efectos y `references/gotchas.md` cuando un
armado o render falle. Lee `references/replicate.md` apenas el usuario muestre un ejemplo o describa un look propio.
Lee `references/gifs.md` cuando pida GIFs (puedes buscarlos tú y ponerlos en las frases correctas).
Lee `references/sounds.md` antes de poner efectos de sonido. Ahí está cada sonido, dónde pega, su volumen bajo la voz y
cuál elegir entre las variantes parecidas.
Cuando nombra una app y un gráfico la muestra, usa su logo real: `engine/icons` trae 46, y
`PY "SK/scripts/get_icon.py" "<app>"` baja otra con licencia libre (si no hay, va su inicial y lo dices).

## Idioma: siempre en español

- **Responde siempre en español de Chile**, con palabras simples, aunque el usuario escriba en inglés o las
  instrucciones técnicas de algún archivo estén en inglés.
- Los efectos y estilos se nombran con su **nombre en español** (Palabra Clave, Zoom Digital, Cálido...).
  Cada entrada de los archivos de datos guarda su nombre original en inglés en el campo `en`: úsalo solo para
  cruzarlo con código o notas antiguas. Las claves (`key`) nunca cambiaron.
- Las frases de "Lo que escucha el usuario" (al final) son las que usas, tal cual o con el mismo tono.
- Lo que imprimen los scripts (líneas `STATUS`, `NOTE`, `CHECK`) está en inglés a propósito: es para ti. Nunca se lo
  muestres al usuario: tradúcelo a una frase simple.

## Soy Elvaras: marca (leer primero)

Esta es la copia personal de Cristobal Varas, para sus reels y los de sus clientes, en su propio computador. Nunca
se comparte, publica ni entrega a otra persona, y su repositorio de GitHub es privado.

- Marca: `brands/soyelvaras/brand.json`. Colores bosque #13281F, dorado #C9A15B, crema #F2ECDF, tinta #141615.
  Tipografías: Bebas Neue para el golpe, Instrument Serif itálica para el remate (la palabra clave), Work Sans para
  leer. Todo estilo de subtítulos y todo efecto usa estos colores y tipografías por defecto, salvo que él pida otra
  cosa. Donde un efecto usa amarillo, naranjo o rojo como acento, usa dorado. Donde usa negro o casi negro, usa
  bosque o tinta.
- Clientes: "edita esto para <cliente>" usa `brands/clientes/<cliente>/brand.json` (copia `_plantilla`). Cada
  cliente tiene además sus propios archivos de estilo: guárdalos como `ST/clients/<cliente>/my-style.{md,json}`.
- Formatos: el render principal es 9:16 para Instagram. Cuando pida la versión web, renderiza también en 16:9.
- Los 19 clips de `captions/previews` (y sus fotos en `picker/previews/posters/captions`) ya son de él: una sola
  escena de 1016(3), todo el texto abajo, armada en `~/reel-edits/subtitulos-base`. Los de `picker/previews/effects`
  (los 34) y `picker/previews/styles` (los 3) también son suyos. Los de `effects/*/example` siguen siendo de relleno
  hasta que él grabe los suyos: nunca los presentes como trabajo suyo.
- Lo que ya se aprendió con sus tomas (detalle en la memoria del proyecto): usa lentes, y la medición de la cabeza
  se corta en la nariz (la barbilla real queda unos 150 px más abajo); su silla oscura se mezcla con su polerón en
  los recortes; en los acercamientos usa `cy` cerca de 0.52; la palabra que pide comentar es "EDIT".

## Gana el estilo del usuario. Lee esto primero.

Es la regla más importante de la skill. Todo lo que trae la skill es un punto de partida. El estilo del usuario
manda sobre todo.

Orden de prioridad, de mayor a menor:
1. Lo que el usuario pide para este reel.
2. Un ejemplo que dio o un estilo que describió. Lo estudias y lo REPLICAS, y pasa a ser su propio estilo
   (`ST/my-style.md` + `ST/my-style.json`, ver "Cuando el usuario muestra un ejemplo o describe un estilo"). Una vez
   que existe, cada "edítalo" lo usa sin preguntar hasta que diga otra cosa, y los subtítulos y efectos que trae la
   skill solo se usan donde él los pida.
3. Sus elecciones guardadas: el estilo completo o el estilo de subtítulos en `ST/studio-picks.json`.
4. El look por defecto de un efecto. Siempre al final.

Lo que eso significa en cada edición:
- Un efecto nunca trae su propio look de subtítulos a un reel que ya tiene un estilo de subtítulos.
  - `effects/INDEX.md`, "Restyling an effect's own words" (Reestilizar las palabras de un efecto), dice qué hacer
    con cada efecto: apagar sus palabras o reestilizarlas al estilo del usuario antes de armar.
  - Vale para todos los efectos, también los que se agreguen después. Ninguno es excepción.
- **Todo en un efecto se puede cambiar.** Colores, tipografías, volumen del sonido, fuerza del movimiento, tiempos.
  Cámbialos para que calcen con el estilo o con las notas del usuario. Los valores por defecto de un efecto son el
  gusto de una demo, no una regla.
- **Los efectos son sugerencias.** Son una base para quien todavía no sabe lo que quiere. Usa un efecto elegido solo
  donde calza con el clip y con la frase. Mejor dejarlo fuera que forzarlo contra el estilo, y di por qué en una
  línea. Ajusta el look de los efectos para que tengan sentido con el clip: las palabras que se dicen, la persona que
  las dice, etc.
- **Una nota del usuario es una instrucción.** "Hazlo blanco", "menos zoom", "sin sonidos": hazlo en este reel. Si
  dice "siempre", escríbelo en `ST/my-style.md` para que todos los reels siguientes lo respeten.

Lee `ST/my-style.md` al inicio de cada edición cuando exista. Antes de entregar, revisa el reel terminado contra
esta regla: un solo look de subtítulos del primer al último cuadro, en el estilo del usuario.

## Paso 0: revisión de herramientas (cada vez)

`SK` es la carpeta de esta skill (la que tiene este archivo): `${CLAUDE_SKILL_DIR}`, o la carpeta base que te dio
Claude Code al cargar la skill. `SK` es de solo lectura: nunca escribas dentro.

Ejecuta la revisión. El usuario no necesita Python, Node ni ffmpeg en el computador: el Studio consigue su propia
copia de lo que falte, dentro de `ST`, sin contraseña y sin instalar nada en el sistema.
- Mac y Linux: `sh "SK/scripts/start.sh"`. Siempre este. Nunca ejecutes `python3` solo en un Mac: sin las
  herramientas de desarrollo de Apple abre una ventana de "instalar herramientas de desarrollo".
- Windows: prueba en orden hasta que uno imprima líneas STATUS: `python3 "SK/scripts/setup.py"`, luego
  `python "SK/scripts/setup.py"`, luego `py -3 "SK/scripts/setup.py"`. (`python3` suele ser un acceso directo de la
  Tienda que imprime "Python was not found": prueba el siguiente.) Si ninguno funciona, no hay Python: ejecuta
  `powershell -NoProfile -ExecutionPolicy Bypass -File "SK/scripts/start.ps1"`. Consigue un Python propio para el
  Studio y luego hace la revisión.

Toma unos segundos, y unos minutos la primera vez mientras descarga lo que falta y arma su propio entorno de Python
(avísalo). Solo cuando imprima `STATUS python MISSING`, o `start.ps1` falle de otra forma: da la solución y detente
(Windows: pegar `winget install --id Python.Python.3.12 -e` en PowerShell, luego cerrar Claude Code por completo y
abrirlo de nuevo. Mac: descargar Python 3.12 de
https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg y abrirlo. Linux:
`sudo apt install python3 python3-venv`).

Nunca instales un Python por tu cuenta para pasar la revisión, y nunca el más nuevo: el motor de transcripción solo
se instala en Python 3.9 a 3.13. Un Python más nuevo en el computador puede quedarse ahí, el Studio lo salta.

Cómo leer las líneas STATUS:
- `STATUS state <folder>` es `ST`, la carpeta propia del Studio del usuario. Todo lo que guarda la skill vive ahí
  (su Python, `.platform.json`, `config.json`, `studio-picks.json`, efectos de sonido). Está fuera de la skill a
  propósito, para que una actualización nunca borre sus elecciones.
- node, python o ffmpeg `MISSING` (solo cuando el Studio no pudo conseguir su copia: sin internet, o un sistema sin
  versión disponible): la línea termina con los pasos para ESTE computador, escritos para alguien que nunca usó una
  terminal. Pásalos palabra por palabra, traducidos, y detente hasta que el script imprima `READY`. En Windows se
  pega la línea de winget en su propia ventana de PowerShell y luego se cierra Claude Code por completo y se abre de
  nuevo.
- `STATUS python TOO NEW`: el Python que corrió la revisión es más nuevo de lo que soporta el motor de transcripción.
  Ejecuta el comando del final de la línea (el script de arranque). Consigue un Python 3.12 propio. Nada que
  instalar.
- `the download did not finish, trying again (attempt 2 of 3)`: una descarga se trabó y el Studio la reinició solo.
  Nada que hacer. Solo cuenta la línea `OK` o `MISSING` que viene después.
- Efectos de sonido `MISSING` (sin conexión) está bien: el reel queda sin efectos de sonido hasta que estén.
- `STATUS update AVAILABLE`: hay una versión más nueva del Studio. Va primero, antes de las preguntas de
  configuración, el selector o cualquier edición. Pregúntalo solo: "Hay una actualización del Studio con arreglos.
  ¿La instalo? Toma un minuto."
  - Sí, o cada vez que diga "actualiza el Studio": ejecuta `PY "SK/scripts/update.py"` de inmediato, transmite lo
    que imprime, dile que abra un chat nuevo y detente. Nada más en este chat: el chat nuevo sigue donde quedó, con
    la versión nueva.
  - No: sigue, y no vuelvas a preguntar en este chat.
  - La fuente de actualizaciones es el repositorio público de Soy Elvaras Studio en GitHub (`SOURCE` en
    `scripts/update.py`): lo que está en su rama main es la versión más nueva.
- `clean cutout NOT SET UP` está bien para subtítulos solos. Casi todos los efectos lo necesitan, igual que los looks
  que van detrás de la persona (subtítulos Contundente, Tutorial Gráfico). Consíguelo la primera vez que las
  elecciones tengan un efecto o uno de esos looks: `setup.py --matting`, una vez, unos 105 MB.
- El otro extra opcional, solo cuando un script lo pide: `setup.py --fx <effect key>` (paquetes de Python extra para
  ese efecto, en el Python propio de la skill).

Qué descarga un usuario nuevo y cuándo (una vez cada cosa; cuánto tarda depende de su conexión, así que di el
tamaño, no un tiempo):
- en la configuración: el entorno de Python de la skill, unos 0,25 GB. En un computador sin nada propio, además Python
  (unos 25 MB en Mac, 46 MB en Windows), Node (unos 50 MB) y ffmpeg (unos 45 a 75 MB).
- en la primera edición: el modelo de voz, unos 0,5 GB en el paso 1 y 1,4 GB más en el paso 4. HyperFrames (el motor
  de render), unos 0,4 GB, la primera vez que corren `HF` o `layout.py`, luego su navegador (unos 0,2 GB) en la
  primera instantánea o render, y su modelo de recorte rápido (unos 0,2 GB) en el paso 5.
- con el primer efecto: el recorte limpio, unos 105 MB.
Dilo una vez antes de la primera edición: "La primera edición descarga unos 3 GB de herramientas, una sola vez.
Después es rápido."

Luego lee `ST/.platform.json` (se reescribe en cada revisión). Tiene los comandos para este computador:
- `PY` = su valor `python`. Ejecuta TODOS los scripts de esta skill con él, nunca con `python3` solo.
- `HF` = `PY "SK/scripts/hf.py" "<project>"`: HyperFrames en la versión fijada, con el Node correcto en cualquier
  sistema. La carpeta del proyecto es su primer argumento y corre dentro de ella, así que no hay `cd` y
  `renders/...` es la del proyecto.
- `cutout`: `CoreML` (Apple Silicon, rápido) o `CPU` (todo lo demás: más lento, córrelo en segundo plano).

Un solo estilo de comando para zsh, bash, Git Bash y PowerShell: rutas completas entre comillas dobles y con barras
normales, un comando por llamada, sin `&&`, sin `cd`, sin `VAR=1 cmd`, sin `~` dentro de los argumentos. En PowerShell
pon `&` delante de un programa entre comillas: `& "PY" "SK/scripts/ingest.py" "<project>"`. La única ruta corta
permitida es un render con el nombre de la carpeta del proyecto (`"renders/<slug>-v1.mp4"`): `HF` y los dos scripts de
revisión la buscan dentro del proyecto.

### Solo la primera vez

`/elvaras-studio setup` (o "configura el Studio") es cómo empieza un usuario nuevo: haz el Paso 0, los pasos de primera
vez de abajo, y luego abre el selector de estilo. No pidas clips todavía. Cuando las elecciones estén guardadas, di
que está listo y que el siguiente paso es dejar los clips y decir "edítalo". Si se vuelve a ejecutar, solo repite lo
que todavía falta. El usuario puede saltarse el selector y mandarte uno o varios ejemplos de estilos de edición:
estudia esos videos o imágenes para poder replicar el estilo.

`STATUS config MISSING`:
1. Di: "Bienvenido a Soy Elvaras Studio. Dos preguntas rápidas y después eliges tu look. Esto pasa una sola vez."
2. Pregunta en un solo mensaje: dónde suelen quedar sus clips crudos (por defecto `~/Downloads`) y dónde deben vivir
   los proyectos de reels (por defecto `~/reel-edits`).
3. Guarda `ST/config.json`: `{"clipsDir": "~/Downloads", "projectsDir": "~/reel-edits", "setupDate": "YYYY-MM-DD"}`.

`STATUS picks MISSING` (o el usuario pide el selector): ábrelo, ver la sección siguiente.

## El selector de estilo

Una página local donde el usuario elige un estilo completo, o arma el suyo en tres pestañas (Subtítulos, Efectos,
Transiciones), con un clip de muestra en cada tarjeta. Abajo, "Tu reel" muestra lo elegido en carriles: Cualquier
parte, Gancho, Medio, Final y Transiciones. Sobre cada efecto hay botones Gancho / Medio / Final / Cualquier parte, y
cada efecto en un carril abre un menú para cambiar dónde va, su versión o quitarlo (también se puede arrastrar).
Corre solo en su computador y se abre en su navegador.

```
PY "SK/scripts/picker.py" --until-saved                  primera vez, "abre el selector", "cambia mi estilo"
PY "SK/scripts/picker.py" --tab captions --until-saved   "cambia mis subtítulos"
PY "SK/scripts/picker.py" --tab effects --until-saved    "cambia mis efectos"
PY "SK/scripts/picker.py" --tab transitions --until-saved "cambia mis transiciones"
```
Córrelo en segundo plano y dile: "Abrí el selector de estilo en tu navegador. Elige un estilo completo, o arma el
tuyo con subtítulos, efectos y transiciones, y presiona Guardar." Espera la línea `STATUS picks SAVED ...`. Luego lee
`ST/studio-picks.json` y confirma en UNA frase simple, con los nombres en español, por ejemplo: "Guardado. Quedaste
con subtítulos Palabra Clave, Zoom Digital y Checklist. Deja tus clips y di edítalo."

Las elecciones: `{"mode": "preset"|"custom", "style": key|null, "captionStyle": key|"none", "effects": [keys],
"effectSections": null | {"hook": [...], "middle": [...], "end": [...]}}`. `mode: preset` = un estilo completo, con
sus propios subtítulos salvo que `captionStyle` sea distinto al que trae ese estilo (el usuario los cambió).
`effectSections` con valor = cada efecto solo puede usarse en las partes indicadas para él (hook = gancho, middle =
medio, end = final). `effectVariants` = la versión elegida de los efectos que vienen en versiones.
Las transiciones (en `picker/data/effects.json` con `"category": "transition"`, hoy Corte en Zoom y Flicker) van en
`effects` como cualquier efecto: el archivo no cambia. Nunca tienen parte propia: con `effectSections` aparecen en las tres.
Una versión que es su propio video (`whole_reel_variants` en `effects/index.json`, hoy Antes y Después 2 "Tarjetas") no
va dentro del reel: si está elegida, después del render final arma también esa presentación (su `effect.md` dice cómo) y
entrégala aparte, junto al reel.

Algo puntual ("prueba Karaoke en este") no cambia las elecciones guardadas: `build_reel.py --caption karaoke` o
`--style glam-cam`.

## Cuando el usuario muestra un ejemplo o describe un estilo

El selector es para quien todavía no sabe lo que quiere. Quien te pasa un reel que le gusta, un pin, una captura de
pantalla, o dice con sus palabras lo que quiere, ya te dio el encargo. Replícalo. Los subtítulos y efectos que trae
la skill quedan a un lado: no acomodas su ejemplo al más parecido, reconstruyes el look en sí.
`references/replicate.md` tiene cada campo y comando. El procedimiento:

1. **Estudia el ejemplo completo.** `PY "SK/scripts/study.py" "<example file>"` sobre el archivo que dejó. Despliega
   CADA momento en hojas de cuadros y mide los cortes, el ritmo, la velocidad al hablar y dónde salta el sonido.
   Mira cada hoja, de arriba abajo, no tres cuadros sueltos. Un cuadro muestra tipografía, color y composición, pero
   no ritmo ni sonido: haz una pregunta, o elige valores tranquilos y dilo.
   Un link a una publicación (un reel, un short, un pin): consigue la dirección directa del video con tu herramienta
   de Apify, ejecuta `PY "SK/scripts/get_example.py" --direct "<address>"` y estudia el archivo que imprime. Sin
   Apify: dile "Para usar links hay que conectar Apify. O deja el archivo del video aquí."
2. **Escríbelo** en `ST/my-style.md`, una línea simple por área: tipografía, color, subtítulos (lugar, palabras a la
   vez, placa, qué hacen la palabra dicha y la palabra clave), movimiento de subtítulos, ritmo, encuadre, elementos
   gráficos, sonido.
3. **Reconstrúyelo con SUS clips.** Sus palabras, sus tomas, su duración. Copia el ritmo, no los tiempos.
   - Reconstrúyelo con una especificación de subtítulos propia, tus propias capas y los ajustes de todo el reel
     (`references/replicate.md` tiene cada campo).
4. **Compáralo lado a lado.** `PY "SK/scripts/side_by_side.py" "<example file>" "<project>" "renders/<slug>-v1.mp4"`
   pone cuadros del ejemplo sobre cuadros del render final. Corrige lo que no calza, una vez. Luego dale la hoja y
   una lista simple: qué calza y qué no se pudo igualar.
5. **Pasa a ser suyo.** Guarda la especificación en `ST/my-style.json` (subtítulos, capas fijas, color, css) y las
   notas en `ST/my-style.md`. `build_reel.py` lo lee en cada armado desde ahí, por encima de las elecciones
   guardadas.

Qué se copia y qué nunca: se replican el LOOK y la ESTRUCTURA (sensación de la tipografía, colores, composición,
ritmo, movimiento). Nunca las imágenes, música, voz, logo, usuario, nombre ni palabras del ejemplo, y nunca se dice
que el resultado es de quien hizo el ejemplo o con esa persona. Tipografía: la más parecida que trae la skill o una de
licencia abierta que pueda descargar; nunca un archivo de fuente pagada, y dices cuál la reemplaza.

Sé directo con los límites (`references/replicate.md` los lista): no se agrega música, la persona no se mueve a un
panel ni a una página fuera de los estilos completos y efectos que lo hacen, y el movimiento de subtítulos y capas es
el conjunto de entradas que tiene el motor. Di lo que no se pudo igualar. Nunca lo finjas.

## Reglas fijas

1. Zona segura de Reels (1080x1920): arriba 220, abajo 450 (nada bajo y 1470), lados 35, derecha 100 desde y 1155
   hacia abajo. Una excepción: la tarjeta de la persona en Tutorial Gráfico va pegada al borde inferior a propósito.
   O si el usuario pide ignorar la zona segura.
2. Subtítulos y efectos nunca tapan la cara (de los ojos a la barbilla).
3. Los subtítulos dicen lo que realmente se dijo. Corrige lo que Whisper escucha mal ("Claude" sale como "cloud").
   Sin guiones largos (—) en el texto en pantalla.
4. Todo lo que aparece en pantalla es real o un relleno claramente genérico. Nunca una persona real que no sea el
   usuario, nunca números, comentarios o resultados inventados.
5. Efectos solo donde la toma sirve (chequeo de toma) y solo en las partes que el usuario permitió. Que un efecto
   quede fuera es normal: dile por qué en una línea.
6. La prueba sale de cuadros del render FINAL, no de instantáneas.
7. Nunca borres ni cambies los archivos del usuario. Los originales solo se leen.
8. Háblale con palabras simples. Nunca le muestres nombres de archivos de esta skill, líneas STATUS ni errores
   técnicos.
9. La voz y la imagen nunca pierden calidad. Si un paso solo cambia la imagen (copia para el celular, recorte, escala), el audio
   se copia tal cual (`-c:a copy`). Si hay que codificarlo, una sola vez y en AAC 320k a 48 kHz, nunca menos. No
   bajes la tasa de bits ni el muestreo para que un archivo pese menos. La imagen tampoco se aplasta: el render final
   sale con CRF 16 y la copia para el celular en 1080p con CRF 20.
10. Nada se detiene nunca. La imagen tiene la cámara viva (sale sola en todo reel sin estilo completo; no la apagues
   salvo que él lo pida), cada gráfico que se queda sigue derivando, nada entra lineal ni todo en el mismo cuadro.
   Las reglas y cómo escribir cualquier movimiento: `references/motion.md`.

## Flujo de trabajo ("edítalo")

`<project>` = `<projectsDir>/<short-slug>/`. Clips = los archivos que nombra el usuario, si no, los videos más nuevos
de `clipsDir`.

```
1. PY "SK/scripts/ingest.py" "<project>" <clips o carpeta> [--newest 5]
       mira work/sheets.jpg, lee transcript.txt
2. escribe <project>/edl.json                    la mejor toma de cada frase, sin silencios (references/cutting.md)
3. PY "SK/scripts/assemble.py" "<project>"       -> assets/aroll.mp4 (30 fps limpio) + segments.json
4. PY "SK/scripts/transcribe_cut.py" "<project>" "<nombres y palabras clave dichos en el reel>"
       corrige a mano lo mal escuchado en words.json, luego:
   PY "SK/scripts/marks.py" "<project>"          primera propuesta de marcas; luego aplica tú la regla de marcado
5. PY "SK/scripts/layout.py" "<project>"         dónde está la persona -> layout.json. MIRA work/layout/check.jpg:
       la caja verde debe ir de lo alto de la cabeza a la barbilla. Una línea "CHECK THE HEAD BOX" significa que es
       una estimación (un cuadro o póster detrás de la cabeza la puede subir): corrígela antes de seguir
       (references/captions.md). Con lentes la caja se corta en la nariz: corrige la barbilla a mano.
6. PY "SK/scripts/init_project.py" "<project>"   tipografías, archivos del proyecto, plan.json inicial
       escribe el título fijo (y cualquier texto en pantalla que pida un estilo completo) en plan.json
7. ¿hay efectos?  PY "SK/scripts/footage_check.py" "<project>"   luego, por cada uno que pase Y calce con una frase:
       si dice "ready":   PY "SK/scripts/fx_new.py" <key> --project "<project>" --from <seg> --to <seg>
                          llena el bloque CLIP del espacio, ejecuta los comandos que imprime, y luego
                          PY "SK/scripts/fx_add.py" "<project>" "<slot>"      (escribe el espacio en plan.json)
       paso a paso: effects/INDEX.md
8. PY "SK/scripts/build_reel.py" "<project>" --safe     lee las elecciones -> index.html, zona no segura en rojo
                                                        (su línea "camera=" debe decir live salvo en un estilo completo)
   PY "SK/scripts/hf.py" "<project>" lint               0 errores
   PY "SK/scripts/hf.py" "<project>" snapshot --at <5 a 10 momentos> --no-end --describe false
                                                        lee <project>/snapshots/contact-sheet.jpg, corrige. Incluye
                                                        momentos en la MITAD de cada entrada (references/checks.md, 4)
9. PY "SK/scripts/build_reel.py" "<project>"            el mismo armado SIN la guía roja
   PY "SK/scripts/hf.py" "<project>" render -o renders/<slug>-v1.mp4 --quality high
                                                        unos 20 a 45 s por cada 10 s de reel en Apple Silicon, hasta
                                                        unos 80 s por cada 10 s cuando el reel tiene efectos
   PY "SK/scripts/frames_check.py" "<project>" "renders/<slug>-v1.mp4"     la autorrevisión: MIRA la hoja
   PY "SK/scripts/check_cuts.py" "<project>" "renders/<slug>-v1.mp4" --phone   tira de cortes + copia 1080p para celular
                                                        su última línea es el nivel de audio (references/cutting.md)
10. entrega la copia para celular y el render completo. Di qué se hizo y qué quedó fuera, con palabras simples.
```

`build_reel.py` imprime líneas `NOTE` cuando algo no se pudo hacer como estaba elegido (sin espacio sobre la cabeza,
un look que necesita recorte, un cambio de subtítulos que no calza con un estilo): transmite cada una al usuario con
palabras simples, y arregla lo que se pueda.

Un look que va detrás de la persona o la saca del cuarto (subtítulos Contundente, Tutorial Gráfico) necesita
primero un recorte de la persona en todo el reel. Usa el limpio, `rvm_cut.py`, y dile cuánto tarda antes de empezar
(`references/checks.md`). Casi todos los efectos necesitan también el recorte limpio (`effects/INDEX.md` dice cuáles
no), pero solo de sus propios cuadros: `fx_new.py` lo hace (unos 1,2 a 1,8 segundos por cuadro en un Mac con Apple
Silicon, unos 0,4 en este computador, así que unos 2 minutos para un efecto de 3 segundos). Los dos necesitan
`setup.py --matting` una vez.

Mira una instantánea del reel dentro de cada espacio de efecto: un solo look de subtítulos, nada repetido, ninguna
palabra dicha sin subtítulo salvo que las palabras del propio efecto la lleven.

Ronda de notas: cambia `edl.json` / `words.json` / `plan.json`, vuelve a armar desde el paso que cambió y renderiza
`-v2`. Guarda cada versión en `renders/`.

### Correcciones puntuales: render por tramos (siempre que se pueda)

Cuando el reel ya está validado y la nota toca solo unos segundos, NO lo renderices entero. Arregla la fuente, vuelve a
armar (build y los scripts del proyecto que tocan `index.html`) y renderiza solo esa ventana. El script la pega en el
render aprobado, en los cuadros exactos, y copia el audio tal cual:
```
PY "SK/scripts/render_window.py" "<project>" <desde> <hasta> "renders/<slug>-vN.mp4" -o "renders/<slug>-vN+1.mp4"
PY "SK/scripts/render_window.py" "<project>/fx/<slot>" <desde> <hasta> --webm -o "renders/<nombre>.webm"
```
- La segunda forma es para un efecto o una pasada de gráficos: renderiza solo la ventana y apunta el espacio del efecto
  a ese archivo (`media` = inicio del espacio − `<desde>`). Después arregla la ventana del reel con la primera.
- Deja unos cuadros de margen antes y después del cambio. Revisa que el total de cuadros sea el mismo que el de la base
  (lo imprime) y mira cuadros a ambos lados de las dos uniones.
- Un tramo de 2 s toma menos de un minuto, en vez de 6 a 10 minutos del reel completo, y muchos menos tokens.
- Renderiza todo de nuevo solo si el cambio atraviesa el reel: el corte, los tiempos, el estilo de subtítulos, un
  efecto que se repite en todo el video.

### Trial reels: "haz 5 trial reels"

Con el reel aprobado, el usuario puede pedir versiones de prueba para Instagram. Cada versión cambia una sola cosa (el
gancho, los subtítulos, los colores o los efectos) y además lleva un pase propio de velocidad, encuadre y color, así
que ninguna es copia de otra. Lee `references/trials.md` antes de empezar. En corto:
```
PY "SK/scripts/trials.py" plan "<project>" --base renders/<slug>-vN.mp4 --count 5     propone la mezcla; pregúntale
PY "SK/scripts/trials.py" make "<project>"                                            arma cada versión
PY "SK/scripts/trials.py" render "<project>"                                          en segundo plano, una por una
```
El gancho se renderiza solo en su tramo y se pega sobre el render aprobado (~1 min). Subtítulos, colores y efectos
necesitan un render completo cada uno.

## Lo que escucha el usuario

- Al empezar una edición: "Voy. Estoy eligiendo tus mejores tomas y cortando los silencios."
- Un efecto que queda fuera: "Dejé fuera Clon en este: necesita un plano abierto con la cámara quieta y este clip es
  un plano cercano."
- Una alternativa: "Tu cara llena el cuadro en este clip, así que dejé los subtítulos en una sola línea bajo tu
  barbilla."
- Un paso lento: "Este look necesita un recorte limpio de ti. Toma unos 12 minutos para este reel. Sigo avanzando y
  te aviso cuando esté."
- Entrega: "Aquí está tu reel. Subtítulos: Palabra Clave. Efectos: Zoom Digital en el gancho. Dime qué cambio."
- Un efecto hecho de palabras: "Ajusté el Checklist a tus subtítulos Karaoke: misma tipografía, mismas mayúsculas,
  mismo dorado."
- Un ejemplo que te mostró, antes de empezar: "Voy. Estoy estudiando tu ejemplo de principio a fin, y después armo
  ese look con tu clip."
- Después de replicarlo: "Esto es lo que logré igualar y lo que no. Desde ahora todos tus reels usan este estilo."
- Una grabación baja: "Tu voz quedó grabada un poco baja en este clip. ¿Quieres una copia más fuerte?"

Cálido y Tímido funcionan con o sin cara. Dilo así. Los estilos no son "para él" ni "para ella".
