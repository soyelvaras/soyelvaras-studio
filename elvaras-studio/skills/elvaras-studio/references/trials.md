# Trial reels (versiones de prueba)

Instagram muestra un trial reel primero a gente que no sigue la cuenta. Sirve para probar versiones del mismo reel y
quedarse con la que gana. El usuario edita un reel como siempre, lo aprueba y dice **"haz 5 trial reels"** (o "hazme
versiones de prueba", "3 versiones para probar", "make trial reels"). El Studio arma esa cantidad de reels a partir del
render aprobado. Cada uno cambia **una sola cosa**, así el que gana dice qué funcionó.

Todo pasa por `scripts/trials.py`: `plan`, `make`, `render`, `list` y `posted`.

## Qué puede cambiar cada versión

| cambio | qué es | cómo se hace | costo |
|---|---|---|---|
| `hook` | otro titular sobre los primeros segundos | se agrega al `index.html` aprobado y se renderiza solo ese tramo, que se pega sobre el render aprobado (`render_window.py -c`) | ~1 min |
| `captions` | otro estilo de subtítulos | `build_reel.py --caption <key> --out` | render completo, ~15 min |
| `colors` | el dorado de la marca pasa a otro color (salvia, crema, azul niebla, arcilla; nunca naranjo) | cambio de color en el `index.html` aprobado | render completo |
| `effects` | el reel sin efectos | `build_reel.py` con los espacios apagados | render completo |
| `pass` | nada más que el pase propio (versión de control) | solo ffmpeg sobre el render aprobado | segundos |

Una versión con dos cambios se puede hacer si el usuario lo pide, pero entonces la ganadora no dice cuál de los dos
funcionó: díselo una vez.

`hook`, `colors` y `pass` sirven para cualquier reel, también los armados con los scripts del proyecto (Página y
Tarjeta). `captions` y `effects` rearman el reel con `build_reel.py`, así que necesitan un reel armado por él. Si el
motor cambió desde que se aprobó el reel, `make` lo avisa con una NOTE: esas versiones traen también los cambios del
motor (por ejemplo, la cámara viva). Díselo al usuario o déjalas fuera.

## Cada versión es su propio video

Las versiones se publican lado a lado desde una cuenta. Para que ningún archivo sea copia de otro, además de lo que
prueba, cada una lleva un **pase propio** (`"unique"` en `trials.json`), hecho con ffmpeg sobre el archivo terminado:

- **velocidad** de 0,965 a 1,035, distinta en cada versión y nunca 1,0. La voz conserva su tono (`atempo`).
- **encuadre** de 3 a 5% más cerca alrededor de la cara, con un leve corrimiento a un lado. Los subtítulos y gráficos
  se agrandan igual, como máximo un 5%, así que quedan dentro de la zona segura.
- **color**: un grado suave distinto (cálido, frío, claro, contraste o suave), nunca blanco y negro.

El pase es chico a propósito: quien mira solo nota lo que se prueba. Para una prueba estricta, sin pase, pon
`"unique": false` en esa versión.

Nunca le digas al usuario que las versiones "no van a ser detectadas": nadie fuera de Instagram sabe cómo compara
videos. Di lo que se hizo: cada una tiene su propia velocidad, encuadre y color, así que ninguna es copia de otra.

## Cómo se hace

```
1. el reel está editado y aprobado como siempre (render renders/<slug>-vN.mp4)
2. PY "SK/scripts/trials.py" plan "<project>" --base renders/<slug>-vN.mp4 --count 5 [--change hook,captions,colors,effects,pass]
       propone la mezcla -> <project>/trials.json, y la imprime
3. ¿el usuario dijo qué probar? Usa --change. ¿No dijo? Muéstrale la mezcla como una lista corta numerada y pregunta
   en UN mensaje: "Esta es la mezcla que probaría: 1 gancho nuevo, 1 con subtítulos Karaoke, 1 con colores salvia,
   1 sin efectos y 1 de control. ¿Te sirve, o prefieres que todas prueben el gancho?"
   Para cada versión de gancho, escribe en trials.json su "headline": de 2 a 7 palabras sacadas de lo que dice el reel,
   nunca una promesa que el reel no hace. Muéstrale las opciones antes de seguir.
4. PY "SK/scripts/trials.py" make "<project>"
       arma trials/NN-<id>.html por versión. Resuelve cada línea CHECK antes de renderizar
5. PY "SK/scripts/trials.py" render "<project>"        EN SEGUNDO PLANO
       una después de otra, nunca dos a la vez. La línea QUEUE dice cuánto demora: avísale al usuario.
       Mira cada versión al terminar (por lo menos el primer segundo y el corte del gancho).
6. entrega: la carpeta <project>/trial-reels/ con trial-01-<id>.mp4 ... y que-cambia.txt (o trials.py list)
```

- `render --only 3` hace solo una; `--redo` vuelve a hacer una que ya está en `trial-reels/`.
- Una versión que no sale con la misma cantidad de cuadros que el render aprobado falla antes del pase: revísala.
- La versión de subtítulos y la de colores llevan el audio del render aprobado tal cual (con todos sus arreglos). La de
  efectos lleva el suyo, porque sin efectos también se van sus sonidos.
- Un plan nuevo: `plan --fresh`. Las versiones anteriores pasan a `trial-reels/antes-<fecha>/`.

## Versiones publicadas

El usuario publicó la versión 3: `PY "SK/scripts/trials.py" posted "<project>" 3`. Esa versión conserva su archivo, su
número y su pase, nunca se vuelve a hacer, y un plan nuevo la mantiene y elige pases distintos para las demás.
`--undo` quita la marca.

## Qué escucha el usuario

- Al empezar: "Voy. Armo 5 versiones y las renderizo una por una para no ahogar el computador. Demora unos 45 minutos;
  te aviso cuando estén."
- Al entregar: "Tus 5 trial reels están en la carpeta trial-reels. Son los mismos clips, cada uno con una cosa distinta,
  y cada uno con su propia velocidad, encuadre y color, así que ninguno es copia de otro:" y luego una línea por
  archivo, por ejemplo:

```
trial-01-gancho-1.mp4              Gancho: abre con el titular «Claude le pone 12 efectos a mis videos»
trial-02-subtitulos-karaoke.mp4    Subtítulos: Karaoke
trial-03-colores-salvia.mp4        Colores: el dorado pasa a salvia
trial-04-sin-efectos.mp4           Efectos: el reel sin efectos
trial-05-solo-pase.mp4             Nada más: el mismo reel con su pase propio (control)
```

  Después: "Súbelos como trial reels y quédate con el que gane. Cuando sepas cuál ganó, dime y lo dejo como tu forma
  por defecto."
- Cuando dice cuál ganó: un gancho es una lección para los próximos guiones (dila en una línea). Unos subtítulos o
  colores pueden pasar a su estilo (`my-style.json`).

## Cómo enseñárselo a alguien

Basta con una frase: **"Edita el reel como siempre. Cuando esté aprobado, di: haz 5 trial reels."** Claude propone la
mezcla, pregunta qué probar, escribe los titulares del gancho, renderiza en segundo plano y entrega la carpeta con la
lista de qué cambia en cada una. Quien publica solo tiene que subirlas como trial reels y decir cuál ganó.
