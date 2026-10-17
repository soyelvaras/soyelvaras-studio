# Crear un efecto o una transición nueva

Cada efecto nuevo se construye con la misma forma que los 26 que ya existen, y cada transición nueva toma como base
Corte en Zoom (la única transición que hay hoy). Se hace uno por vez: referencia, lectura, construcción, showcase,
validación, deploy.

## 1. Lo que me pasas tú

1. **La referencia.** El clip de video (mp4 o mov) en `reel-edits/_referencias/transiciones/` o
   `reel-edits/_referencias/efectos/`. Lo ideal es recortado al momento, con un segundo antes y uno después. Si es un
   reel entero, dime en qué segundo está. Un link no sirve sin Apify conectado: necesito el archivo.
2. **Una línea sobre qué te gusta.** El movimiento, la velocidad, el sonido, el look. Y lo que no quieres copiar.
3. **El material para el showcase.** Por defecto uso 1016(3), el polerón café. Para una transición necesito dos tomas
   distintas seguidas (un corte real). Para un efecto, la frase donde cae.

## 2. Lo que hago yo

1. **Leo la referencia cuadro a cuadro** (`scripts/study.py`): cuánto dura en cuadros, cómo acelera y frena, qué
   desenfoque usa, dónde suena. Te devuelvo esa lectura en palabras simples, con lo que se puede igualar y lo que no,
   antes de construir nada.
2. **Lo construyo con la forma de siempre:** una carpeta `effects/<clave>/` con
   - `effect.md`: qué hace, qué toma necesita, dónde falla y la tabla del bloque CLIP (lo que Claude lee);
   - `slot.json`: cómo se comporta dentro de un reel (recorte, subtítulos, sonidos, pasos);
   - `build.py`: el bloque CLIP arriba (textos, colores, tiempos, versión) y el código que dibuja y anima;
   - los scripts que miden tu toma, preparan y revisan (`prep.py`, `check.py` y los que haga falta).

   Las transiciones viven sobre un corte, como Corte en Zoom: el espacio cruza el corte y conoce su cuadro.
3. **Lo registro** en `effects/index.json`, `effects/INDEX.md` y `picker/data/effects.json`. Las transiciones llevan
   `"category": "transition"` y aparecen solas en la pestaña y el carril de Transiciones.
4. **Hago el showcase:** edito un trozo corto con tu material, con el efecto durando lo más posible para que se note,
   y te paso el clip.

## 3. Lo que haces tú

Lo miras y me das notas. Corrijo (una o dos vueltas) hasta que lo apruebes.

## 4. Deploy

1. El clip aprobado pasa a ser la vista previa del selector (clip y foto).
2. Commit en el repo.
3. Subo la versión del plugin (`elvaras-studio/.claude-plugin/plugin.json`) y se actualiza el Studio instalado en
   Claude Code, que es una copia: sin este paso, Claude sigue usando la versión anterior.

## Qué se puede y qué no

- **Sí:** zooms y empujes, giros, barridos y paneos rápidos, desenfoque de movimiento, máscaras con tu recorte (pasar
  por delante o por detrás de ti), cortinas y formas, glitch, destellos y fugas de luz, pantallas divididas,
  congelados, textos y gráficos animados.
- **Difícil o no:** un movimiento de cámara 3D real (ver la escena desde otro ángulo), transformar una cara en otra,
  cosas generadas con IA, o lo que depende de cómo se grabó (por ejemplo, tapar el lente con la mano: eso hay que
  grabarlo). Si una referencia cae aquí, te lo digo antes de construir y te propongo lo más cercano.
