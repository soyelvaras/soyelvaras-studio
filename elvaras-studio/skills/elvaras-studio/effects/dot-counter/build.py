#!/usr/bin/env python3
"""dot-counter (Puntos): a row of dots pops in, one after another, when the speaker says how many things are coming;
filled dots show how far along they are, and with FILL_AT each dot fills on the word of its step. Transparent graphics
over the reel's own footage (an overlay).

Run from the slot folder (effect.md has the full run order):
    python3 build.py      writes index.html   (SAFE=1 safe-zone guide, SFX=0 no sounds, CAPTIONS=0 accepted and ignored)
"""
import re

import vgfx as V

# ==== STYLE (the reel's look wins: match this block to the reel's caption style before building) ====
STYLE = dict(
    font='Work Sans',
    weight=700,
    tracking=-0.02,
    big_font='Bebas Neue',
    big_weight=400,
    big_tracking=0.01,
    case='as-said',
    small_font='Work Sans',
    small_weight=600,
    serif_font='Instrument Serif',
    serif_italic=True,
    ink='#F2ECDF',                 # crema: the ring of an open dot
    accent='#C9A15B',              # dorado: a filled dot
    card='#13281F',
    shadow=True,
)
# ==== END STYLE ====

# ==== CLIP (edit this) ====
COUNT = None        # how many dots (2 to 8). None = the number the speaker says in the slot (a digit or dos to ocho)
FILLED = None       # how many of them are filled when they pop in. None = all of them (the "here come N things" beat),
                    # or none when FILL_AT is set. Fewer = progress: step two of three is COUNT = 3, FILLED = 2
FILL_AT = []        # [seconds, ...]: the dots fill one by one on these words (each step as it is named). [] = no filling
T_IN = None         # when the first dot pops (slot seconds). None = when the number is said
STEP = 0.07         # seconds between dots
T_OUT = None        # when the row leaves (slot seconds). None = 0.6 s after the counted word ends (after the last
                    # FILL_AT with filling), or the slot end
Y = None            # centre of the row, screen px. None = the chest band from layout.json
DOT = 46            # dot size, px
SOUND = 0.15        # volume of the soft click on each dot. 0 = silent
# ==== END CLIP ====

WORDS = {'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8,
         'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8}


def main():
    s = V.Slot()
    print('words: ' + s.word_list())
    print(s.where())
    said = next((w for w in s.words if re.fullmatch(r'[2-8]', V.bare(w['text'])) or V.bare(w['text']).lower() in WORDS), None)
    count = COUNT
    if count is None:
        if said is None:
            V.die('nobody says how many things are coming in this slot (2 to 8), so Puntos has nothing to count')
        t = V.bare(said['text']).lower()
        count = int(t) if t.isdigit() else WORDS[t]
    count = max(2, min(8, int(count)))
    fills = sorted(float(x) for x in FILL_AT)[:count]
    filled = (0 if fills else count) if FILLED is None else max(0, min(count, int(FILLED)))
    t_in = T_IN if T_IN is not None else (said['start'] if said else .1)
    if T_OUT is not None:
        t_out = T_OUT
    elif fills:
        t_out = min(s.dur, fills[-1] + .6)
    else:
        k = s.words.index(said) if said in s.words else None
        end = s.words[k + 1]['end'] if k is not None and k + 1 < len(s.words) else t_in + .4
        t_out = min(s.dur, end + .6)
    y = s.band(DOT + 20, Y)
    if y is None:
        V.die('there is no room under or above the face on this clip for the dots')
    p = V.Page(s)
    ink, accent = STYLE['ink'], STYLE['accent']
    p.css.append(f'''
.dcw{{position:absolute;left:0;right:0;transform:translateY(-50%)}}
.dc{{display:flex;justify-content:center;gap:{int(DOT * .38)}px}}
.dc span{{position:relative;width:{DOT}px;height:{DOT}px;border-radius:50%;border:{max(3, DOT // 13)}px solid {ink};
  box-shadow:0 2px 14px rgba(0,0,0,.3)}}
.dc span b{{position:absolute;inset:-{max(3, DOT // 13)}px;border-radius:50%;background:{accent}}}''')
    i = p.nid('dc')
    p.html.append(f'<div class="dcw" style="top:{y}px"><div id="{i}" class="dc">' +
                  ''.join(f'<span id="{i}d{k}"><b id="{i}f{k}"></b></span>' for k in range(count)) + '</div></div>')
    for k in range(count):
        at = t_in + k * STEP
        p.enter(f'#{i}d{k}', at, {'scale': .2}, {'scale': 1}, .2, 'back.out(3)')
        if k >= filled:
            p.js.append(f"gsap.set('#{i}f{k}',{{scale:0}});")
        if SOUND:
            p.sound('click-soft', at, SOUND)
    for k, at in enumerate(fills):            # each step fills its dot as it is named
        if k < filled:
            continue
        p.js.append(f"tl.fromTo('#{i}f{k}',{{scale:0}},{{scale:1,duration:.22,ease:'back.out(2.4)',immediateRender:false}},{V.T(at):.3f});")
        p.press(f'#{i}d{k}', at + .18, .92)
        p.sound('pop', at, .14)
        print(f'  dot {k + 1} fills at {at:.2f}s')
    p.drift(f'#{i}', t_in + count * STEP + .2, t_out - V.LEAVE, .03)
    p.leave(f'#{i}', t_out)
    if t_out < s.dur - .02:
        p.js.append(f"tl.set('#{i}',{{autoAlpha:0}},{V.T(t_out):.3f});")
    print(f'  {count} dots ({filled} filled) from {t_in:.2f}s, centre y {y}, out at {t_out:.2f}s')
    p.write()
    print(f'snapshot at: {t_in + .05:.2f},{t_in + count * STEP + .2:.2f},' + ''.join(f'{at + .25:.2f},' for at in fills)
          + f'{max(0, t_out - .08):.2f}')
    s.hide_hint([(t_in, t_out)])


if __name__ == '__main__':
    main()
