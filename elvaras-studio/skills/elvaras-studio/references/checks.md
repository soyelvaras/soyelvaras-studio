# Revisiones: el chequeo de toma, el recorte, la autorrevisión

Nada de este producto se ajustó para el clip del usuario. Estas revisiones son la red de seguridad. No te las saltes.

## Zona segura de Reels (1080 x 1920)
- arriba 220 libres, abajo 450 libres (nada bajo **y 1470**), 35 libres a cada lado,
- los 100 de la derecha libres desde **y 1155** hacia abajo (me gusta / comentar / compartir).
- Una excepción: la tarjeta de la persona en Tutorial Gráfico va pegada al borde inferior.
`build_reel.py --safe` pinta de rojo el área no segura para las instantáneas. Nunca renderices con eso puesto:
`build_reel.py` sin `--safe` justo antes de cada render.

## 1. Chequeo de toma (antes de cualquier efecto)
`PY "SK/scripts/footage_check.py" "<project>"` revisa cada efecto elegido contra lo que midió `layout.py`: encuadre,
movimiento de cámara, pared libre, cantidad de tomas y las partes del reel que permitió el usuario.
- `OK`: calza. Las líneas de abajo dicen qué tiene que estar listo antes (un recorte, un paquete, algo del usuario).
- `SKIP`: déjalo fuera. Dile al usuario la línea impresa, traducida. No fuerces la toma para que califique.
- `CHECK`: el script no pudo decidir. Mira `work/sheets.jpg` y `work/layout/check.jpg` y decide tú.
Las mediciones son primeras estimaciones (el encuadre sale del ancho de la cabeza, la cámara de cuánto cambia el
cuarto entre muestras). Cuando tus ojos y el script no coinciden, ganan tus ojos. Dilo en la nota de entrega.

Un efecto que pasa igual tiene que calzar con las PALABRAS: sin número dicho no hay Contador, sin lista no hay
Checklist.

La última línea bajo un `OK` dice de qué tipo es el efecto. `ready` (listo): crea un espacio con `fx_new.py`, llena el
bloque CLIP, ejecuta los comandos que imprime, agrégalo con `fx_add.py`. `recipe` (receta): adapta a mano el armado de
la demo. Ambos están paso a paso en `effects/INDEX.md`. Las partes que permitió el usuario se hacen cumplir tres veces
(`fx_new.py` se niega a crear el espacio, `fx_add.py` se niega a agregarlo, `build_reel.py` lo deja fuera): nunca le
saques la vuelta a una negativa, dile al usuario la línea que imprime.

## 2. El recorte: rápido o limpio
| | Rápido: `cutout.py` | Limpio: `rvm_cut.py` |
|---|---|---|
| Tiempo | unos 7 s por segundo de video en Apple Silicon, varias veces eso en otros equipos | unos 1,2 s por CUADRO en Apple Silicon (0,4 en este computador): un reel de 20 s son unos 12 minutos en Mac |
| Sirve para | medir (layout.py hace uno pequeño propio), Etiqueta Pegada | todo lo que va DETRÁS de la persona o sale de una tarjeta: Contundente, Tutorial Gráfico, la mayoría de los efectos. Todo efecto listo usa este |
| Punto débil | puede tomar una cara de un cuadro o póster como la persona; manos bruscas | lento; necesita `setup.py --matting` una vez. Ropa del mismo color que la silla o el sillón detrás se mezcla con ella |

Prefiere el limpio siempre que se vaya a ver un borde. Dile al usuario el tiempo ANTES de empezar, córrelo en segundo
plano, sigue trabajando. Un recorte a la vez. Solo los cuadros de un efecto necesitan recorte: `fx_new.py` lo hace para
un efecto listo (un espacio de 3 segundos son unos 2 minutos en Mac), `rvm_cut.py --src` para una receta.
Ambos escriben `assets/subject.webm` y se detienen con FRAME MISMATCH si no coincide cuadro por cuadro con el corte:
entonces vuelve a ejecutar `assemble.py` y recorta de nuevo.

## 3. Autorrevisión (después de armar cualquier cosa)
Antes del render, desde instantáneas con la guía roja (`build_reel.py --safe`, `HF snapshot --at ...`): composición,
legibilidad, zona segura. Elige 5 a 10 momentos: uno por cada cambio de look de subtítulos, cada título, cada efecto,
la última frase.

Después del render, desde el archivo FINAL:
`PY "SK/scripts/frames_check.py" "<project>" "renders/<file>.mp4" [--at 1.2,3.4]`
escribe una imagen, `work/check/<file>.jpg` (seis cuadros por fila), con la zona segura en rojo y la cara en verde.
La caja verde sale de `layout.json`: si no está sobre la cara, corrige primero el layout. Confirma las cuatro:

| Revisión | Falla cuando | Arreglo, o dejarlo fuera |
|---|---|---|
| Nada tapa la cara | cualquier subtítulo, tarjeta o título toca de los ojos a la barbilla | vuelve a correr `layout.py`, corrige `bands` en `layout.json`, o usa un estilo de una línea |
| Nada sale de la zona segura | algo dibujado en el área roja (salvo la tarjeta de Tutorial Gráfico) | acorta el texto, baja el tamaño en el plan, o deja fuera el elemento |
| El recorte está limpio | halo, una mano que falta, un póster recortado como segunda persona, el borde que tiembla, un pedazo de silla | haz el recorte limpio; si sigue mal, cambia a un look que no lo necesite |
| El texto se lee | texto claro sobre pared clara, texto detrás de la cabeza que tapa más de un tercio de una letra | un estilo con placa o sombra (Karaoke, Hora Dorada), o mueve la franja |

Un espacio de efecto suma una quinta revisión: **sus dos bordes**. Pásale a `--at` los tiempos que imprimió
`fx_add.py` (justo dentro del espacio en ambos extremos, al medio, justo después). La imagen no debe saltar en brillo
o color al entrar o salir, los subtítulos no deben repetir las palabras propias del efecto, ninguna palabra dicha
dentro del espacio puede quedar sin algún subtítulo (del efecto o del reel), y el efecto tiene que haberse ido antes
de que termine el espacio, salvo que el espacio termine en un corte. `fx_add.py` dice si pudo igualar el espacio con
el reel; cuando dice NOT matched, mira dos veces. Si se nota un borde, saca el espacio (`fx_add.py ... --remove`) y
dilo.

Para un estilo de subtítulos sin estilo completo, el script también imprime cuánto del área no segura y de la caja de
la cara cambió respecto del corte crudo. Sobre un 1,5% significa que hay algo dibujado ahí. La cámara viva no lo
confunde: el script mueve el cuadro crudo igual que ella antes de comparar. Se salta esos números cuando el look cambia
el color o mueve la imagen con entradas de movimiento, y en cada cuadro dentro de un espacio de efecto (el efecto
cambia la imagen a propósito): ahí la imagen es la única prueba.

## 4. Revisión del movimiento (antes del render y en el render final)

Las reglas están en `references/motion.md`. Antes de renderizar, toma instantáneas también en la MITAD de cada
entrada y de cada movimiento, no solo cuando todo se asentó. Confirma:

| Revisión | Falla cuando | Arreglo |
|---|---|---|
| Nada se detiene | un gráfico, tarjeta o título se queda congelado más de 1 s; un reel sin estilo completo armado con `"camera": false` sin que él lo pidiera | deja la deriva de la capa (`drift`), agrega un `to` lento de escala 1,02, vuelve a encender la cámara |
| Nada lineal | una entrada, salida, paneo o zoom con `ease: 'none'` | `back.out` en entradas, `power2.in` en salidas, `power2.inOut` en la cámara |
| Escalonado | filas, tarjetas, íconos o checks que aparecen todos en el mismo cuadro | `stagger` de 0,04 a 0,07 s |
| Contadores | un número que salta al valor final en un cuadro | que suba en cerca de 1 s, `power2.out` |
| Legible | un titular o número que se va antes de 1 s (salvo un corte justo) | que entre antes o dure hasta el corte |
| Ningún texto encima de otro | dos textos que se tapan en algún cuadro, sobre todo en los bordes de cada espacio y capa | mira los cuadros de cada borde y corrige tiempos o lugar |
| Movimiento dentro de lo seguro | algo que en la mitad de su movimiento cruza la cara o sale de la zona segura | menos recorrido, otro origen, o que entre desde otro lado |
| Nada sale del cuadro sin querer | un elemento que queda cortado por el borde y no está saliendo a propósito | muévelo hacia adentro o achícalo |
| Cámara | la línea `camera=` de `build_reel.py` dice `still` en un reel sin estilo completo | quita `"camera": false` del plan o del estilo |

## 5. Cortes y entrega

`check_cuts.py` cubre los cortes (cuadro antes / después de cada corte) y escribe la copia para el celular.

Una pasada de pulido y entrega. Si algo sigue fallando después de un arreglo, deja fuera ese elemento y dile al
usuario qué quedó fuera y por qué. Un reel limpio sin el efecto es mejor que un reel roto con él.
