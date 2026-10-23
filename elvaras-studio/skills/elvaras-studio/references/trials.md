# Trial reels (versiones de prueba)

Instagram muestra un trial reel primero a gente que no sigue la cuenta. Sirve para probar versiones del mismo reel y
quedarse con la que gana. El usuario edita un reel como siempre, lo aprueba y dice **"haz 5 trial reels"** (o "hazme
versiones de prueba", "make trial reels"). El Studio arma esa cantidad de versiones del render aprobado, y **cada una
es claramente distinta**: otro gancho, otra velocidad, otro ritmo de zoom, otro color y, cuando se puede, otros
subtítulos. Así cada una se siente como un video propio y la cuenta prueba varias aperturas a la vez.

Todo pasa por `scripts/trials.py`: `plan`, `make`, `render`, `list` y `posted`.

## Qué cambia en cada versión

| qué | cómo | dónde funciona | costo |
|---|---|---|---|
| **gancho** (siempre distinto) | por turnos: **titular** (un texto de gancho distinto en cada versión, sobre los primeros segundos) o **apertura LED** (la primera frase palabra por palabra en Pantalla LED) | cualquier reel | ~1 min |
| **velocidad** | 0,95 a 1,12, distinta en cada versión y nunca 1,0. La voz conserva su tono | cualquier reel | parte del pase |
| **zooms y ritmo** | sobre los cortes del propio reel: *golpes* (un golpe de zoom en cada corte), *empuje* (empuje lento en cada toma), *alterno* (una toma sí y otra no más cerca, como jump cut) o *respira* (entra y sale lento), sobre un encuadre 3 a 5% más cerrado y corrido hacia un lado | cualquier reel | parte del pase |
| **color** | un grado suave: cálido, frío, claro, contraste o suave | cualquier reel | parte del pase |
| **subtítulos** | otro estilo de subtítulos por versión | solo un reel armado por `build_reel.py` | render completo, ~15 min |
| **colores de marca** | con `--colors`, una versión sí y otra no cambia el dorado por salvia, crema, azul niebla o arcilla | cualquier reel con `index.html` | render completo |

La velocidad, los zooms y el color se hacen con ffmpeg sobre el archivo terminado (`light_pass`). Los subtítulos y los
gráficos se mueven con la imagen, como máximo un 10%, así que quedan dentro de la zona segura.

**Página y Tarjeta.** Un reel terminado con los scripts del proyecto no se puede volver a armar con `build_reel.py` sin
perder su look. `plan` lo detecta solo (`rebuild_check`: arma una copia y compara qué piezas tiene), y en esos reels
las versiones conservan sus subtítulos. El gancho, la velocidad, los zooms y el color cambian igual en todas. Para
cambiar también los subtítulos, primero hay que llevar Página y Tarjeta al motor (pendiente).

**Reel viejo.** Si el motor cambió desde que se aprobó el reel, `plan` lo avisa con una NOTE: las versiones con otros
subtítulos traen también lo nuevo del motor (por ejemplo, la cámara viva). Díselo al usuario.

## Los ganchos de texto

Para cada versión con titular, escribe en `trials.json` (`"hook": {"headline": ...}`) un texto de 2 a 7 palabras sacado
de lo que dice el reel, cada uno con un ángulo distinto: una pregunta, un número, un "nadie te dice", un antes y
después. Nunca prometas algo que el reel no hace. Muéstraselos al usuario antes de seguir. El titular va opaco en la
franja de arriba (y 214 a 475); si el reel abre con su propio título ahí, lo tapa.

La apertura LED usa las palabras del propio reel en su primera frase, con las palabras marcadas en dorado. Se arma
como un espacio del proyecto (`fx/trial-NN-led`) y se pega sobre los primeros segundos del render aprobado.

## Cómo se hace

```
1. el reel está editado y aprobado como siempre (render renders/<slug>-vN.mp4)
2. PY "SK/scripts/trials.py" plan "<project>" --base renders/<slug>-vN.mp4 --count 5 [--colors]
       propone las versiones -> <project>/trials.json, y las imprime
3. escribe los titulares (CHECK) y muéstrale al usuario la lista en UN mensaje, por ejemplo:
   "Estas son las 5 versiones: 1) titular «Dejé de editar mis reels», 1,06x, golpes de zoom, cálido; 2) apertura en
   pantalla LED, 1,10x, empuje lento, frío; ... ¿Te sirven, o cambio algún gancho?"
4. PY "SK/scripts/trials.py" make "<project>"       arma lo de cada versión. Resuelve cada línea CHECK
5. PY "SK/scripts/trials.py" render "<project>"     EN SEGUNDO PLANO, una tras otra, nunca dos a la vez.
       La línea QUEUE dice cuánto demora: avísale. Mira cada versión al terminar (el primer segundo y el corte del gancho)
6. entrega: la carpeta <project>/trial-reels/ con trial-01-<id>.mp4 ... y que-cambia.txt (o trials.py list)
```

- `render --only 3` hace solo una; `--redo` vuelve a hacer una que ya está.
- Una versión que no sale con la misma cantidad de cuadros que el render aprobado falla antes del pase: revísala.
- Las versiones llevan el audio del render aprobado (con todos sus arreglos), acelerado o frenado con su velocidad.
- Un plan nuevo: `plan --fresh`. Las versiones anteriores pasan a `trial-reels/antes-<fecha>/`.
- No hagas trial reels de prueba que nadie pidió: cada render completo son ~15 minutos.

## Versiones publicadas

El usuario publicó la versión 3: `PY "SK/scripts/trials.py" posted "<project>" 3`. Esa versión conserva su archivo, su
número y su velocidad, nunca se vuelve a hacer, y un plan nuevo la mantiene y elige velocidades distintas para las
demás. `--undo` quita la marca.

## Qué escucha el usuario

- Al empezar: "Voy. Armo 5 versiones, cada una con su propio gancho, velocidad, ritmo de zoom y color, y las renderizo
  una por una. Demora unos N minutos; te aviso cuando estén."
- Al entregar: "Tus 5 trial reels están en la carpeta trial-reels:" y una línea por archivo (`que-cambia.txt`).
  Después: "Súbelos como trial reels y dime cuál ganó."
- Cuando dice cuál ganó: el gancho ganador es una lección para los próximos guiones (dila en una línea), y su ritmo y
  su color pueden pasar a su estilo.
- Nunca digas que las versiones "no van a ser detectadas": nadie fuera de Instagram sabe cómo compara videos. Di lo que
  se hizo: cada una tiene su propio gancho, velocidad, zoom y color.

## Cómo enseñárselo a alguien

Basta con una frase: **"Edita el reel como siempre. Cuando esté aprobado, di: haz 5 trial reels."** Claude propone
las versiones con sus ganchos, pregunta, renderiza en segundo plano y entrega la carpeta con la lista de qué cambia en
cada una. Quien publica solo tiene que subirlas como trial reels y decir cuál ganó.
