# Problemas conocidos (cada uno costó un render)

## Tiempos / sincronía
- La concatenación de ffmpeg deja un desfase inicial de 0,033 s y huecos de cuadro disparejos, y un recorte hecho
  desde eso se corre. `assemble.py` recodifica a 30 fps limpios; `cutout.py` y `rvm_cut.py` se detienen cuando la
  cantidad de cuadros no coincide.
- `tl.set` en un tiempo redondeado se dispara un cuadro tarde: usa `frame/30 - 0.002` (la `T()` del motor lo hace).
- `HF snapshot` busca aproximado en los cortes y puede mostrar la toma siguiente un cuadro antes. Solo los cuadros del
  render final prueban un corte (`check_cuts.py`, `frames_check.py`).
- Los inicios de palabra de Whisper pueden estar 0,1 a 0,3 s corridos y puede inventar una palabra en un corte.
  Confirma las pausas con silencedetect.
- Whisper parte "GPT-6" y "5.1" en dos y escucha "Claude" como "cloud". Corrige `words.json` a mano.
- En tramos de ruido cortos Whisper inventa frases completas ("Subtítulos por la comunidad de Amara.org", "Gracias
  por ver el video"). Un tramo de menos de un segundo con una frase así es ruido.

## HyperFrames (fijado: hyperframes@0.8.34, Node 22+, siempre iniciado a través de `HF`)
- Lint: los estados ocultos al inicio usan `gsap.set` fuera de la línea de tiempo; cada salida necesita un `tl.set`
  duro; cada `<video>` y `<audio>` necesita un `id` (un video sin id se renderiza congelado); los clips que se tocan en
  el tiempo van en distintos valores de `data-track-index`; una composición por `index.html`.
- Nunca animes autoAlpha u opacity en un elemento que tiene `data-start`: envuélvelo en un div simple y anima ese.
- `fromTo` muestra su estado inicial de inmediato: pasa `immediateRender:false` para todo lo que debe estar oculto
  hasta su tiempo.
- `autoAlpha:1` pone la opacidad en 1 y pisa una opacidad CSS en el mismo elemento.
- Dos animaciones sobre la misma propiedad que se solapan: la que sigue corriendo pisa a un `tl.set` posterior. Por
  ejemplo, un texto que aparece (fade-in) y se oculta con un set antes de que termine de aparecer queda visible.
  Haz que la primera termine antes del set.
- Lint rechaza animar letterSpacing: simula el espaciado con scaleX.
- Los ids de elementos no pueden tener apóstrofos.
- Las máscaras CSS sobre video no sobreviven al motor de render. Hornea el canal alfa en un webm VP9. Una
  `mask-image` con PNG sobre HTML sí funciona (el editor que se quema, 22-10), pero el PNG tiene que traer canal
  ALFA: uno en escala de grises no recorta nada.
- Un `filter` (aunque sea `blur(0px)`) sobre un elemento `preserve-3d` lo aplana: la z de sus hijos se pierde y la
  cámara termina encima de todo. Desenfoca el contenedor con la perspectiva y deja `filter:'none'` al terminar.
- Nunca un `filter` sobre la placa del video del reel (`#plate`): el a-roll deja de pintarse más adelante en el render.
- La cámara viva del motor (`#cam` / `#punch`) envuelve la toma, no `#layers`. Algo que debe calzar con la toma (un
  recorte de la persona encima, la cabeza fuera de la tarjeta) necesita la cámara en reposo (`scale:1`) mientras se
  ve, o aparece un doble borde. Y nunca uses el id `cam` en un script de proyecto: ya es del motor.
- Leer un webm con alfa con ffmpeg: `-c:v libvpx-vp9` ANTES de `-i`, y `alphaextract` antes de `scale`.
- Mucho backdrop-filter o desenfoque en muchos elementos puede dejar las capturas en negro. Limítalo a unos pocos.
- HyperFrames corre levemente los colores del video respecto de imágenes fijas y colores CSS: un cuadro congelado al
  lado de video en vivo necesita igualar el color (ver `effects/freeze-and-label/effect.md`).

## Herramientas
- Los scripts de Python corren en el entorno propio de la skill: lee `python` de `ST/.platform.json` (`PY`). Su ruta
  cambia según el sistema.
- La transcripción muere con `unexpected keyword argument 'metadata_errors'`: ejecuta `setup.py` de nuevo, lo
  repara.
- La skill escribe solo en su carpeta de estado `ST` y en la carpeta del proyecto. Nunca en `SK`.
- Un filtro de seguridad de la terminal puede bloquear un comando que ejecuta un programa guardado en una variable, o
  un `python -c` largo en línea: pon esos pasos en un script pequeño en la carpeta `work/` del proyecto y ejecuta ese.
- Las subidas grandes al chat pueden fallar: nunca bajes la calidad para que entre. Dile dónde quedó el archivo en
  su disco (la copia para el celular y el render completo).
- Los efectos que siguen el cuarto o la cara necesitan paquetes extra (`effects/INDEX.md` los lista por efecto).
  Instálalos en el Python propio de la skill: `PY -m pip install opencv-python-headless`. mediapipe no tiene versión
  para todas las versiones de Python: si no se instala, salta ese efecto y dilo.

## Windows (la misma skill, otra terminal)
- Claude Code ejecuta los comandos en Git Bash cuando Git para Windows está instalado, si no, en PowerShell. Escribe
  comandos que funcionen en ambos: rutas completas entre comillas dobles con barras normales, un comando por llamada,
  sin `&&`, sin `VAR=1 cmd`, sin `~` en los argumentos. En PowerShell empieza un programa entre comillas con `&`.
- `python3` suele ser un acceso directo de la Tienda. Usa `PY` para todo; antes de que exista el entorno prueba
  `python`, luego `py -3`, luego `start.ps1` (consigue un Python propio para la skill cuando el computador no tiene).
- Un programa instalado con Claude Code abierto no se encuentra hasta cerrar Claude Code por completo y abrirlo de
  nuevo.
- El recorte rápido no tiene ruta de GPU en Windows: corre en el procesador. Córrelo en segundo plano.
- Windows abre los archivos de texto como cp1252 salvo que se indique otra cosa: cada `open()` que escribas necesita
  `encoding='utf-8'`. Python en Windows escribe saltos de línea CRLF en modo texto: usa `newline=''` o `'\n'` al
  reescribir archivos de la skill.
- Nunca pongas una ruta de archivo dentro de un filtro de ffmpeg (los dos puntos de la unidad lo rompen). Pasa los
  archivos con `-i`.
- Smart App Control o el antivirus pueden bloquear la librería de imágenes que carga HyperFrames, o hacer que ffmpeg
  falle una vez con `spawn EBUSY`. Reintenta una vez, y luego dile al usuario qué bloqueó Windows.
- La transcripción muere con `Library cublas64_12.dll is not found or cannot be loaded`: el PC tiene tarjeta NVIDIA,
  así que el device por defecto de Whisper ('auto') eligió CUDA, pero el kit de CUDA no está instalado. Los scripts
  pasan `device='cpu'`; haz lo mismo en cualquier llamada puntual a `WhisperModel(...)` (un trozo retranscrito, por
  ejemplo).
- Windows en ARM: el motor de transcripción no tiene versión ARM; `setup.py` pide el Python x64.
- Los archivos auxiliares terminados en `.sh` dentro de `effects/` son notas de los armados en Mac. No los ejecutes:
  ejecuta directamente los comandos de ffmpeg y HyperFrames que contienen.
