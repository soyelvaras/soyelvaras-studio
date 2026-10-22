#!/usr/bin/env python3
"""prompt-box (Caja de Prompt): an input box rises over the chest, with the app's real logo and name notched into
its top border, and what the speaker says they tell the AI types itself in, caret and all. When the line is typed, a
cursor arcs in and clicks the send button. Transparent graphics over the reel's own footage (an overlay).

Run from the slot folder (effect.md has the full run order):
    python3 build.py      writes index.html   (SAFE=1 safe-zone guide, SFX=0 no sounds, CAPTIONS=0 accepted:
                                               the typed text IS the effect, so it always draws)
"""
import vgfx as V

# ==== STYLE (the reel's look wins: match this block to the reel's caption style before building) ====
# Fonts must be families that assets/fonts/fonts.css provides. The defaults are Soy Elvaras: Work Sans to read,
# Bebas Neue for the punch, Instrument Serif italic as the second voice, cream on bosque, dorado accent.
STYLE = dict(
    font='Work Sans',              # main words
    weight=600,
    tracking=-0.02,                # letter spacing of the main words, em
    big_font='Bebas Neue',         # the huge words (numbers, the word that matters)
    big_weight=400,
    big_tracking=0.01,
    case='as-said',                # 'as-said', 'lower' or 'upper'
    small_font='Work Sans',        # small labels, chips, sub lines
    small_weight=600,
    serif_font='Instrument Serif', # the second voice
    serif_italic=True,
    ink='#F2ECDF',                 # text colour (crema)
    accent='#C9A15B',              # dorado: the send button, the huge words
    card='#13281F',                # bosque: the box fill
    shadow=True,                   # soft shadow under words that sit on footage
)
# ==== END STYLE ====

# ==== CLIP (edit this) ====
TEXT = ''           # what types into the box: the speaker's own words, as they would type them. Required.
                    # Up to about 60 characters (two lines); longer text gets a smaller size by itself
APP = None          # the app the speaker names ("Claude", "ChatGPT", "Notion"): its real logo and name sit in the gap of
                    # the top border (assets/icons; get_icon.py fetches one that is missing). None = LABEL alone
LABEL = ''          # small label in the gap of the top border ("prompt", "paso dos"). '' with no APP = a plain border
T_TYPE = None       # when the first letter appears (slot seconds). None = when the first word of TEXT is said
T_DONE = None       # when the last letter appears. None = when the last word of TEXT ends (at least 0.03 s a letter)
SEND = True         # a send button that the cursor clicks once the line is typed. False = no button, no cursor
CURSOR = True       # the cursor that arcs in and clicks send (needs SEND)
T_OUT = None        # when the box leaves. None = 0.7 s after T_DONE (0.4 s without SEND), or the slot end
Y = None            # centre of the box, screen px. None = the chest band from layout.json
WIDTH = 760         # box width, px (kept inside the safe zone)
SIZE = 48           # text size, px
SOUND = 0.12        # volume of soft key clicks while it types. 0 = silent
# ==== END CLIP ====


def main():
    s = V.Slot()
    print('words: ' + s.word_list())
    print(s.where())
    if not TEXT.strip():
        V.die('write TEXT in the CLIP block: what the speaker says they type or tell the AI')
    first = V.bare(TEXT.split()[0]).lower()
    last = V.bare(TEXT.split()[-1]).lower()
    w0 = next((w for w in s.words if V.bare(w['text']).lower() == first), None)
    t_type = T_TYPE if T_TYPE is not None else (w0['start'] if w0 else .1)
    w1 = next((w for w in s.words if w['start'] >= t_type - .01 and V.bare(w['text']).lower() == last), None)
    t_done = T_DONE if T_DONE is not None else (w1['end'] if w1 else t_type + len(TEXT) * .05)
    t_done = max(t_done, t_type + len(TEXT) * .03)
    t_send = t_done + .25 if SEND else None
    t_out = T_OUT if T_OUT is not None else min(s.dur, t_done + (.7 if SEND else .4))
    if SEND and t_send > t_out - .15:
        print('  send: no time to click send before the box leaves, so the button stays but nobody clicks it')
        t_send = None
    size = SIZE if len(TEXT) <= 26 else max(34, int(SIZE * 26 / len(TEXT) ** .9))
    width = min(WIDTH, 1080 - 2 * V.SAFE_RIGHT)
    room = width - 80 - (88 if SEND else 0)
    lines = 1 if len(TEXT) * size * .52 < room else 2
    height = int(lines * size * 1.15 + 72)
    y = s.band(height, Y)
    if y is None:
        V.die('there is no room under or above the face on this clip for the box')
    left = int((1080 - width) / 2)
    p = V.Page(s)
    ink, card, accent = STYLE['ink'], STYLE['card'], STYLE['accent']
    notch = bool(APP or LABEL)
    p.css.append(V.style_css(STYLE) + f'''
.pbw{{position:absolute;left:{left}px;width:{width}px;transform:translateY(-50%)}}
.pb{{position:relative;border:2px solid {ink}A6;
  border-top-color:{'transparent' if notch else ink + 'A6'};border-radius:28px;background:{card}C7;
  box-shadow:0 18px 50px rgba(0,0,0,.32);padding:34px {40 + (88 if SEND else 0)}px 30px 40px}}
.pb .top{{position:absolute;left:26px;right:26px;top:-21px;height:40px;display:flex;align-items:center;gap:14px}}
.pb .top i{{flex:1;height:2px;background:{ink}A6}}
.pb .top .lb{{display:flex;align-items:center;gap:10px;font-size:28px}}
.pb .tx{{font-size:{size}px;line-height:1.15;white-space:pre-wrap;min-height:{int(size * 1.15)}px}}
.pb .ch{{display:none}}
.pb .caret{{display:inline-block;width:4px;height:{int(size * 1.04)}px;background:{accent};vertical-align:-{int(size * .16)}px;margin-left:4px}}
.pb .send{{position:absolute;right:22px;bottom:22px;width:66px;height:66px;border-radius:50%;background:{accent};
  display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,.3)}}''')
    i = p.nid('pb')
    chars = ''.join(f'<span id="{i}k{k}" class="ch">{V.esc(c)}</span>' for k, c in enumerate(TEXT))
    label = (p.icon(APP, 34) if APP else '') + (f'<span>{V.esc(LABEL or APP)}</span>' if (LABEL or APP) else '')
    top = f'<div class="top"><i></i><span class="lb vg-small">{label}</span><i></i></div>' if notch else ''
    send = (f'<div id="{i}sd" class="send"><svg width="30" height="30" viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7" '
            f'fill="none" stroke="{card}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>') if SEND else ''
    # the wrapper centres the box on y (a css translate), the box inside it is what moves: GSAP owns its transform
    p.html.append(f'<div class="pbw" style="top:{y}px"><div id="{i}" class="pb">{top}<div class="tx vg-word" '
                  f'style="letter-spacing:-.02em">{chars}<span id="{i}cr" class="caret"></span></div>{send}</div></div>')
    t_in = max(0.0, t_type - .3)
    p.enter(f'#{i}', t_in, {'y': 40, 'scale': .94}, {'y': 0, 'scale': 1})
    p.drift(f'#{i}', t_in + V.ENTER, t_out - V.LEAVE, .015)
    p.leave(f'#{i}', t_out)
    if t_out < s.dur - .02:
        p.js.append(f"tl.set('#{i}',{{autoAlpha:0}},{V.T(t_out):.3f});")
    p.sound('whoosh-short', t_in, .12)
    step = (t_done - t_type) / len(TEXT)
    for k in range(len(TEXT)):
        at = t_type + k * step
        p.js.append(f"tl.set('#{i}k{k}',{{display:'inline'}},{V.T(at):.3f});")
        if SOUND and TEXT[k] != ' ' and k % 3 == 0:
            p.sound('key-press', at, SOUND)
    t = t_done + .2
    while t < t_out - .2:                  # the caret blinks once the line is typed
        p.js.append(f"tl.set('#{i}cr',{{opacity:0}},{V.T(t):.3f}); tl.set('#{i}cr',{{opacity:1}},{V.T(t + .25):.3f});")
        t += .5
    if t_send is not None:
        p.press(f'#{i}sd', t_send, .9)
        if CURSOR:
            bx, by = left + width - 22 - 33, y + height / 2 - 22 - 33     # the centre of the send button
            # it shows up below and left of the button, inside the safe zone (clear of the app buttons on the right)
            p.cursor([(min(1080 - V.SAFE_RIGHT - 40, bx - 120), min(V.SAFE_BOTTOM - 40, by + 190), max(t_in + .2, t_send - 1.0), False),
                      (bx + 6, by + 8, t_send, True)])
        else:
            p.sound('click-soft', t_send, .2)
        print(f'  send clicked at {t_send:.2f}s')
    print(f'  box in at {t_in:.2f}s, types {len(TEXT)} letters {t_type:.2f}s to {t_done:.2f}s, out at {t_out:.2f}s, centre y {y}')
    p.write()
    print(f'snapshot at: {t_in + .1:.2f},{t_type + .05:.2f},{(t_type + t_done) / 2:.2f},{t_done + .1:.2f},'
          + (f'{t_send + .03:.2f},' if t_send is not None else '') + f'{max(0, t_out - .08):.2f}')
    s.hide_hint([(t_in, t_out)])


if __name__ == '__main__':
    main()
