#!/usr/bin/env python3
"""chip-row (Fila de Cápsulas): as the speaker lists things, an outlined pill pops in for each one in a row under the
captions, with the app's real logo inside when the thing is an app. Transparent graphics over the reel's own footage
(an overlay); the reel's captions keep running above it.

Run from the slot folder (effect.md has the full run order):
    python3 build.py      writes index.html   (SAFE=1 safe-zone guide, SFX=0 no sounds, CAPTIONS=0 accepted and ignored)
"""
import vgfx as V

# ==== STYLE (the reel's look wins: match this block to the reel's caption style before building) ====
STYLE = dict(
    font='Work Sans',
    weight=700,
    tracking=-0.02,
    big_font='Bebas Neue',
    big_weight=400,
    big_tracking=0.01,
    case='as-said',                # 'as-said', 'lower' or 'upper'
    small_font='Work Sans',        # the chip text
    small_weight=600,
    serif_font='Instrument Serif',
    serif_italic=True,
    ink='#F2ECDF',                 # crema: text and outline
    accent='#C9A15B',              # dorado: the last chip's outline (the one the list lands on)
    card='#13281F',                # bosque: the chip fill
    shadow=True,
    glass=False,                   # Vidrio Líquido (engine/glass.py): True = the card turns to live glass over the footage
)
# ==== END STYLE ====

# ==== CLIP (edit this) ====
CHIPS = []          # [(text, seconds), ...] or [(text, seconds, app), ...]: one pill per thing listed, each popping in
                    # when it is said (slot seconds). The speaker's own words, shortened: 1 to 3 words each, 2 to 4
                    # pills. app = the app's name for its real logo in the pill ("Notion"; get_icon.py fetches a
                    # missing one). Required
T_OUT = None        # when the row leaves (slot seconds). None = the end of the slot
Y = None            # centre of the row, screen px. None = just under the reel's caption line (layout.json)
SIZE = 34           # chip text size, px; the row shrinks by itself when it is wider than the frame
LAST_ACCENT = True  # the last chip gets a dorado outline: the list lands on it
SOUND = 0.12        # volume of the soft click on each chip. 0 = silent
# ==== END CLIP ====


def main():
    s = V.Slot()
    print('words: ' + s.word_list())
    print(s.where())
    if not CHIPS:
        V.die('write CHIPS in the CLIP block: the things the speaker lists and when each is said')
    chips = [(c[0], float(c[1]), c[2] if len(c) > 2 else None) for c in CHIPS]
    t_out = T_OUT if T_OUT is not None else s.dur
    # under the reel's caption line, which keeps running: its top sits on the chest band
    y = Y if Y is not None else s.chest + 160
    y = min(y, V.SAFE_BOTTOM - 44)
    if y - 34 < s.chin + 20:
        y = s.band(68)
        if y is None:
            V.die('there is no room under or above the face on this clip for the chips')
    width = sum(len(t) * SIZE * .56 + 2 * SIZE * .9 + (SIZE * 1.4 if app else 0) for t, _, app in chips) + 16 * (len(chips) - 1)
    scale = min(1.0, (1080 - 2 * V.SAFE_SIDE - 2 * V.SAFE_RIGHT) / width)
    size = int(SIZE * scale)
    p = V.Page(s)
    ink, card, accent = STYLE['ink'], STYLE['card'], STYLE['accent']
    p.css.append(V.style_css(STYLE) + f'''
.crw{{position:absolute;left:{V.SAFE_SIDE}px;right:{V.SAFE_RIGHT}px;transform:translateY(-50%)}}
.cr{{display:flex;justify-content:center;gap:{int(16 * scale)}px}}
.cr .chip{{display:inline-flex;align-items:center;gap:{int(size * .4)}px;font-size:{size}px;padding:{int(size * .42)}px {int(size * .87)}px;
  border-radius:999px;border:2px solid {ink}B3;background:{card}B3;box-shadow:0 8px 22px rgba(0,0,0,.25)}}
.cr .chip.last{{border-color:{accent}}}''')
    i = p.nid('cr')
    pills = ''
    for k, (text, _, app) in enumerate(chips):
        logo = p.icon(app, int(size * 1.15)) if app else ''
        last = ' last' if LAST_ACCENT and k == len(chips) - 1 and len(chips) > 1 else ''
        cw = len(text) * size * .56 + 2 * size * .87 + (size * 1.55 if app else 0)
        ch = size * 1.08 + 2 * int(size * .42) + 4
        gl = (f' style="width:{cw:.0f}px;justify-content:center;' + p.glass_css(f'c{k}', cw, ch, ch / 2) + '"') if STYLE.get('glass') else ''
        pills += f'<span id="{i}c{k}" class="chip vg-small{last}"{gl}>{logo}{V.esc(V.cased(text, STYLE["case"]))}</span>'
    p.html.append(f'<div class="crw" style="top:{y}px"><div id="{i}" class="cr">{pills}</div></div>')
    for k, (text, at, app) in enumerate(chips):
        p.enter(f'#{i}c{k}', at, {'y': 16, 'scale': .86}, {'y': 0, 'scale': 1}, .24, 'back.out(2.2)', t_out=t_out)
        if SOUND:
            p.sound('click-soft', at, SOUND)
        print(f'  chip {text!r} at {at:.2f}s' + (f' with the {app} logo' if app else ''))
    first = min(at for _, at, _ in chips)
    p.drift(f'#{i}', first, t_out - V.LEAVE, .025)
    p.leave(f'#{i}', t_out)
    print(f'  row centre y {y}, {size}px text, out at {t_out:.2f}s')
    p.write()
    print('snapshot at: ' + ','.join(f'{at + .12:.2f}' for _, at, _ in chips) + f',{max(0, t_out - .08):.2f}')
    print('in a reel: the reel\'s captions stay on (slot.json says keep); check they do not touch the row')


if __name__ == '__main__':
    main()
