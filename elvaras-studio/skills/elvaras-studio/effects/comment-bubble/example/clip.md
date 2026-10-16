# Clip de demo

> El render y los cuadros de demo que menciona esta nota (`demo.mp4`, `stills/`) no son parte de la skill. Lo que sirve
> para un clip nuevo es el bloque CLIP y los números.

**Origen:** selfie cercana en mano, 3,5 s, 105 cuadros (los últimos 0,7 s son un congelado del último cuadro).
**Frase:** "So if you want it, just comment ads and I'll send you the link." ("Así que si lo quieres, solo comenta ads y
te mando el link.")
**Archivos:** `demo.mp4` (copia 720x1280 para celular del render), `stills/` (palabra tipeada, comentario publicado +
puntos de escritura, hilo final).

## Valores CLIP
Estos eran los valores por defecto del paquete original, así que un espacio nuevo de este clip reconstruye la demo sin
cambios. En Soy Elvaras Studio los textos por defecto están en español ("Te mandé el link", "Abrir link", "tú").

```
KEYWORD = 'ADS'        REPLY_TEXT = 'Sent you the link'   CHIP_TEXT = 'Open link'   USER_NAME = 'you'
T_IN = 0.50    T_FOCUS = 0.93   T_TYPE = 1.26   KEY_GAP = 0.09   T_SEND = 1.57
T_DOTS = 1.88  T_REPLY = 2.05   T_LINK = 2.39   T_OUT = None
SCALE = 1.3    CHIN_Y = None    CHIN_GAP = 20   DROP = 'auto'    X_CENTER = None   PUSH = 'auto'   PUSH_MAX = 1.12
AVATAR_FRAME = None    AVATAR_BOX = None    GRADE = 'none'    SEAT = 1.0
```

## Qué hace con eso el armado del paquete
`layout: scale 0.98  reply inline  thread x 48..863  y 1215..1456  chin 1270 -> 1195 after x1.116 lift`

- El plano cercano deja 186 px bajo la barbilla, así que el pedido de 1,3x se achica a 0,98 y la imagen sube 11,6%. La
  demo se ajustó a mano a 1,0 y una subida de 12%: la misma imagen.
- Los tiempos sugeridos por measure.py para este clip quedaron a menos de 0,06 s de los ajustados a mano de arriba
  (T_TYPE, T_SEND y T_LINK idénticos).

## Diferencias con el render de demo
- El hilo queda centrado bajo la cabeza (x 48..863); la demo se puso a mano en x 96..949.
- `GRADE` es `'none'`; la demo usó `contrast(1.05) saturate(.9) brightness(.98)`.
- Las letras de la palabra en el campo están 2 px más espaciadas.
- El avatar de la demo fue un cuadro elegido a mano (90); por defecto es el último cuadro.
