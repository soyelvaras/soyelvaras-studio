"""Vidrio Líquido: the shared glass for every effect that shows a floating card (Checklist, Llamadas, La Pila, Caja de
Prompt, Cifra Grande, Fila de Cápsulas, Puntos...). Not an effect of its own: a look a card can take.

What makes it liquid and not just frosted: the footage behind the card is blurred LIVE, frame by frame (the hands and
the room keep moving behind it), and a band along the card's edge bends the picture like the rim of a thick lens.
That bend is an SVG displacement map, drawn once per card size, used through css backdrop-filter. The renderer is
Chrome, which supports url() filters in backdrop-filter.

It only works over footage that is in the same page: a card in an effect that has its own footage under it (a
normal slot), or an overlay effect built with GLASS=1 (vgfx.Page then puts the slot's footage under the graphics and
the render is a normal opaque slot instead of a transparent .webm).

    import glass
    G = glass.Glass()                        # one per page
    css_rule = G.card('chk', w, h, radius)   # css declarations for a card that is w x h px (its own size, before
                                             # any transform) -> put them on the card's element
    page_html += G.defs()                    # the <svg> with the filters, once, anywhere in the body
"""
import base64
import io

import numpy as np
from PIL import Image

# the look, in one place: how clear the glass is, how strong the rim bends, the light on its edge
BLUR = 7            # px of live blur behind the card (the reference is fairly clear: hands still read through it)
SATURATE = 1.55
BRIGHT = 1.07
RIM = .16           # width of the bending band, as a share of the card's short side
BEND = 46           # px the picture shifts at the very rim
TINT = 'rgba(255,255,255,.06)'
DARK = .22          # tint for a card that carries light text, so cream words stay readable. A card over a bright wall
                    # needs more (.4 to .5): pass dark=<alpha>


def _map(w, h, r):
    """displacement map for a rounded rect: R/G hold the inward push (128 = none), strongest at the rim"""
    s = 0.5                                   # half resolution is plenty: the filter scales it back up
    W, H = max(8, int(w * s)), max(8, int(h * s))
    R = r * s
    y, x = np.mgrid[0:H, 0:W].astype(np.float32) + .5
    qx = np.abs(x - W / 2) - (W / 2 - R)
    qy = np.abs(y - H / 2) - (H / 2 - R)
    out = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - R
    depth = -out                              # px inside the edge
    gy, gx = np.gradient(depth)
    n = np.hypot(gx, gy) + 1e-6
    band = max(2.0, min(W, H) * RIM)
    m = np.clip(1 - depth / band, 0, 1) ** 2  # 1 at the rim, 0 past the band
    m[depth < 0] = 0
    dx, dy = gx / n * m, gy / n * m           # points inward: the rim shows the picture from a little further in
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[..., 0] = np.clip(128 + dx * 127, 0, 255)
    rgb[..., 1] = np.clip(128 + dy * 127, 0, 255)
    rgb[..., 2] = 128
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


class Glass:
    def __init__(self):
        self.filters = []

    def card(self, key, w, h, radius, dark=False, blur=BLUR, bend=BEND):
        """css declarations for a glass card w x h px with this corner radius"""
        fid = f'lg-{key}'
        self.filters.append(
            f'<filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feImage href="{_map(w, h, radius)}" x="0" y="0" width="{w:.0f}" height="{h:.0f}" preserveAspectRatio="none" result="m"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="m" scale="{bend * 2}" xChannelSelector="R" yChannelSelector="G"/>'
            '</filter>')
        tint = TINT if not dark else f'rgba(14,16,15,{DARK if dark is True else float(dark):.2f})'
        fx = f'url(#{fid}) blur({blur}px) saturate({SATURATE}) brightness({BRIGHT})'
        return (f'background:linear-gradient(160deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,.03) 38%,{tint} 100%);'
                f'backdrop-filter:{fx};-webkit-backdrop-filter:{fx};'
                'border:1.5px solid rgba(255,255,255,.34);'
                'box-shadow:inset 0 1.5px 0 rgba(255,255,255,.55),inset 0 -1px 0 rgba(255,255,255,.18),'
                'inset 0 0 28px rgba(255,255,255,.07),0 18px 44px rgba(0,0,0,.28);')

    def defs(self):
        if not self.filters:
            return ''
        return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
                + ''.join(self.filters) + '</defs></svg>')
