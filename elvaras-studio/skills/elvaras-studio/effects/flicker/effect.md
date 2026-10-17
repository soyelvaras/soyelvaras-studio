# flicker (Flicker)

**Qué hace:** convierte un corte seco entre dos tomas en una ráfaga de destellos de luz que aterriza en la toma
siguiente. Dura 24 cuadros (0,8 s) y el audio queda como un corte seco, con un crujido eléctrico debajo.

**Función:** transición, en cualquier parte de un video: cambio de tema, de lugar, de look, un "y ahora..." o la
entrada al llamado.

**Frases que lo activan:** "haz un flicker en ese corte", "pasa a la siguiente toma con destellos", "corte con luces
parpadeantes".

**Toma que necesita:** dos tomas con un corte seco y la persona en las dos. La versión 1 necesita el recorte limpio de
la toma siguiente. Cámara quieta o en mano funcionan.

**Dónde falla:**
- Hay muy poco espacio a un lado del corte. La versión 1 pide 16 cuadros antes y 8 después; la versión 2 pide 12
  antes y 8 después.
- En la versión 1, la persona de la toma siguiente está en otro lugar del cuadro: su recorte aparece donde va a estar,
  no donde estaba la persona anterior. Se ve bien igual, pero cuenta.
- Los destellos blancos pueden molestar a gente sensible a la luz. Úsalo como acento, no en cada corte.

**Entradas del espacio:**
- `assets/aroll.mp4` con AMBAS tomas.
- `clip.json` con `"cut_frames": [K]`.
- `assets/subject.webm`, el recorte, solo para la versión 1.

`build.py` saca solo el último cuadro de la toma A, el primero de la B y el recorte de la B en ese cuadro
(`assets/flicker/`). No se hornea nada.

## Bloque CLIP (inicio de build.py)
| campo | qué es | cómo obtenerlo |
|---|---|---|
| `CUT` | primer cuadro de la toma B | `None` = `cut_frames` de clip.json |
| `VARIANT` | 1 Por capas (la principal), 2 Completo | lo escribe `fx_new.py` desde el selector |
| `LENGTH` | cuadros de la ráfaga | 24 (0,8 s); bájalo solo si el corte no tiene espacio |
| `FLASH`, `FLASH_OPACITY` | color y fuerza de los destellos | blanco a 0,95; crema `#F2ECDF` si se quiere más suave |
| `PUNCH`, `GLOW` | golpe de zoom y sobreexposición del cuadro que vuelve después de un destello | 1,035 y 1,35 |
| `SFX_VOL` | volumen de plantilla del crujido | 0,26 (se aplica x0,75) |

**Interruptores:** `SAFE=1` guía de zona segura, `SFX=0` sin sonido.

## Versiones (`VARIANT` en el bloque CLIP)

El usuario la elige en el selector (puntitos bajo la tarjeta); `fx_new.py` la escribe sola en el espacio.

1. **Por capas (la principal):** la persona de la toma B aparece encima de la toma A, recortada y parpadeando (a ratos
   como silueta blanca). Cuando se asienta, parpadea el fondo entre la toma A, destellos y la toma B, y la toma B se
   queda. El corte cae en el cuadro 16 de 24.
2. **Completo:** parpadea todo el cuadro entre destellos, la toma A y la toma B, cada vez más rápido, y aterriza en la B.
   El corte cae en el cuadro 12 de 24.

Antes del corte, la persona de la toma B es su primer cuadro congelado; los destellos tapan que no se mueve. Después
del corte toma el relevo el recorte en movimiento.
