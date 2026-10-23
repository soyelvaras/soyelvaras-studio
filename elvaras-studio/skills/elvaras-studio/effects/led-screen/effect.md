# led-screen (Pantalla LED)

**Qué hace:** la imagen corta a una pantalla LED oscura. Las palabras que dice la persona se encienden una por una en
su grilla de puntos rojos, verdes y azules, con un parpadeo corto al entrar cada una, mientras la cámara avanza hacia
la pantalla: primero un avance parejo y, en la última palabra, un empujón fuerte hasta que se ven los subpíxeles
sueltos. Luego vuelve a la persona, que se asienta desde un encuadre un poco más cerrado, como si la cámara hubiera
salido por el otro lado.

**Función:** remate o frase clave corta ("todo hecho con un prompt"). **Frases que lo activan:** "pon mis palabras en
una pantalla LED", "el efecto de la pantalla de puntos", "screen push".

## Todo es real
Las palabras son las de la persona, cada una en el cuadro en que la dice. Se dibuja cuadro a cuadro en un canvas desde
la línea de tiempo del reel, así que cada cuadro es exacto.

## Toma que necesita
Cualquier toma: la pantalla cubre todo el cuadro. Sin recorte. Mientras está arriba, los subtítulos del reel se ocultan
solos (`work/reel_captions.json`, lo lee `fx_add.py`). Funciona mejor con una frase corta de 3 a 6 palabras y una
última palabra corta ("todo", "100%"): una frase larga se vuelve una presentación de diapositivas.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo encontrarlo |
|---|---|---|
| `T_IN` | cuadro en que corta a la pantalla | 2 o más; unos cuadros antes de la primera palabra |
| `WORDS` | `[(cuadro, 'palabra'), ...]` | `None` = todas las palabras dichas entre `T_IN` y `T_OUT` (`words.json` del espacio). A mano para saltar palabras chicas |
| `T_OUT` | cuadro en que vuelve a la persona | `None` = 8 cuadros antes del final del espacio; 2 cuadros o más antes del final |
| `ACCENT` | palabras en dorado | `['claude']`; sin mayúsculas ni puntuación |
| `CASE` | `'lower'`, `'upper'` o `'as-said'` | `'lower'`, como la referencia |
| `ZOOM_END` | cuánto entra la cámara al final | 6; 5 o más muestra los subpíxeles |
| `PITCH` | px entre dos LEDs al inicio | 9 |
| `SFX_VOL` | volumen de los sonidos | 1 |

**Interruptores:** `SAFE=1` guía de zona segura, `SFX=0` sin sonidos.

## Orden de ejecución (PY y SK como en SKILL.md)
```
PY "SK/scripts/fx_run.py" "<slot>" build.py SAFE=1      # imprime las palabras con su cuadro y los tiempos para la instantánea
PY "SK/scripts/fx_run.py" "<slot>" hf lint
PY "SK/scripts/fx_run.py" "<slot>" hf snapshot --at <los tiempos que imprime>     MIRA: cada palabra se lee entera
PY "SK/scripts/fx_run.py" "<slot>" build.py
PY "SK/scripts/fx_run.py" "<slot>" hf render
```
Último paso en un reel: `fx_add.py`.
