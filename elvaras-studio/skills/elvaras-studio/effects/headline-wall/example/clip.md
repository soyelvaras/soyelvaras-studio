# Muro de Titulares: el clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Frase dicha:** "Everybody's talking about how Claude can edit your videos." ("Todos hablan de que Claude puede editar
tus videos.")
**Toma:** 1080x1920, plano medio, sentado en el piso contra una pared oscura, 92 cuadros (3,07 s), una toma continua.

## Valores del bloque CLIP (son los valores por defecto que trae build.py)
| campo | valor | por qué |
|---|---|---|
| `HEADLINES` | 20 versiones de "Claude ahora edita video", con `[Claude]` marcado en cada una | un mensaje, muchas voces |
| `HEROES` | 4 tarjetas en los cuadros 42, 56, 65, 71 | inicios de "Claude", "edit", "your", "videos" |
| `SEARCH` | `can [claude] edit videos` | la cápsula frente a la primera tarjeta grande |
| `F_START` / `F_PEAK` | 2 / 28 | primera sílaba; fin de "everybody's talking" |
| `F_ACCENT` | 42 | "Claude": destacador, golpe, impacto grave |
| `DENSITY` / `LEAD` | 1,8 / 4 | por defecto |
| `WALL` | `None` | pared desnuda hasta los codos de la persona |
| `HERO_FIRST_SIDE` | `'L'` | más pared libre a la izquierda |
| `PUSH` / `BUMP` / `DIM` | 1,06 / 1,032 / 1,0 | pared oscura, no hace falta atenuar más |
| `F_OUT`, `KEEP_OUT`, `FOREGROUND` | `None`, `[]`, `[]` | el muro se queda hasta el último cuadro |

## Lee esto antes de comparar un render nuevo con demo.mp4
- La demo se hizo a mano antes de empaquetar el efecto. Sus tarjetas lejanas pequeñas entran a los 220 px superiores del
  cuadro. El efecto empaquetado ya no hace eso: las tarjetas lejanas quedan bajo los 220 px superiores en cada cuadro,
  así que un render nuevo tiene una franja vacía arriba.
- El archivo de demo no se volvió a renderizar con el armado del paquete. La prueba en `test.md` es la prueba de los
  scripts empaquetados.
- En un reel de Soy Elvaras los titulares se escriben en español, genéricos, a partir de lo que dice Cristobal.
