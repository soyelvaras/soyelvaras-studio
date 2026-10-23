#!/usr/bin/env python3
"""stat-stack (Cifra Grande): the number the speaker says lands huge over the chest in Bebas Neue dorado and counts
up to its value in about 0.8 s, and a small caps line under it swaps on the words that follow ("3 MIL" / DÓLARES /
EN 7 DÍAS). Transparent graphics over the reel's own footage (an overlay).

Run from the slot folder (effect.md has the full run order):
    python3 build.py      writes index.html   (SAFE=1 safe-zone guide, SFX=0 no sounds, CAPTIONS=0 accepted and ignored)
"""
import json
import re

import vgfx as V

# ==== STYLE (the reel's look wins: match this block to the reel's caption style before building) ====
STYLE = dict(
    font='Work Sans',              # main words (the sub line)
    weight=700,
    tracking=-0.02,
    big_font='Bebas Neue',         # the number
    big_weight=400,
    big_tracking=0.01,
    case='as-said',                # 'as-said', 'lower' or 'upper'
    small_font='Work Sans',
    small_weight=600,
    serif_font='Instrument Serif',
    serif_italic=True,
    ink='#F2ECDF',                 # crema: the sub line
    accent='#C9A15B',              # dorado: the number. None = same as ink
    card='#13281F',
    shadow=True,
)
# ==== END STYLE ====

# ==== CLIP (edit this) ====
NUMBER = None       # the big text, exactly as said ("3 mil", "$3.000", "100%", "7 días"). None = the first spoken word
                    # with a digit in it. Never a number the speaker did not say
T_IN = None         # when it lands (slot seconds). None = when that word starts
COUNT = 0.8         # seconds the number counts up to its value (0 = it lands already at its value). Only for a value
                    # of 10 or more: a small number just lands
SUBS = None         # the small caps lines under it: [(text, seconds), ...], each replaces the one before at its
                    # seconds. Words the speaker says, shortened ("DÓLARES", "EN 7 DÍAS"). None = the one or two
                    # words said right after the number. [] = no line
T_OUT = None        # when it leaves (slot seconds). None = the end of the slot
Y = None            # centre of the number, screen px. None = the chest band from layout.json, clear of the chin
SIZE = 230          # px of the number; long numbers shrink to fit the width by themselves
# ==== END CLIP ====

WEAK = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'y', 'o', 'que', 'en', 'a', 'al', 'con', 'por', 'para', 'es',
        'the', 'a', 'an', 'to', 'of', 'and', 'that', 'for', 'in', 'on', 'with', 'is'}


def count_parts(number):
    """'$3.000' -> ('$', 3000, '.', '') so the count shows the same separators; None when it is not one plain value"""
    m = re.fullmatch(r'(\D*?)(\d{1,3}(?:([.,])\d{3})+|\d+)(\D*)', number.strip())
    if not m:
        return None
    sep = m.group(3) or ''
    value = int(m.group(2).replace(sep, '') if sep else m.group(2))
    return m.group(1), value, sep, m.group(4)


def main():
    s = V.Slot()
    print('words: ' + s.word_list())
    print(s.where())
    num_word = None
    number = NUMBER
    if number is None:
        num_word = next((w for w in s.words if re.search(r'\d', w['text'])), None)
        if num_word is None:
            V.die('nobody says a number in this slot, so there is nothing for Cifra Grande to show')
        number = V.bare(num_word['text'])
    else:
        digits = re.search(r'\d+', number)
        num_word = s.find(re.escape(digits.group() if digits else number.split()[0]))
    t_in = T_IN if T_IN is not None else (num_word['start'] if num_word else .1)
    subs = SUBS
    if subs is None:
        subs = []
        if num_word:
            k = s.words.index(num_word)
            # what the number counts: up to two words said right after it, stopping at punctuation or a small word
            took = []
            for w in s.words[k + 1:k + 3]:
                if w['start'] - s.words[k]['end'] > 1.2 or V.bare(w['text']).lower() in WEAK:
                    break
                took.append(w)
                if w['text'][-1:] in ',.?!':
                    break
            if took:
                subs.append((' '.join(V.bare(w['text']) for w in took).upper(), took[0]['start']))
    t_out = T_OUT if T_OUT is not None else s.dur
    size = int(min(SIZE, 900 / max(len(number) * .42, 1)))
    y = s.band(size + 70, Y)
    if y is None:
        V.die('there is no room under or above the face on this clip for the number')
    p = V.Page(s)
    p.css.append(V.style_css(STYLE) + '''
.stw{position:absolute;left:0;right:0;text-align:center;transform:translateY(-50%)}
.st .sub{position:absolute;left:0;right:0;font-size:38px;letter-spacing:.04em}''')
    i = p.nid('st')
    sub_html = ''
    for k, (text, at) in enumerate(subs):
        sub_html += f'<div id="{i}s{k}" class="sub vg-word">{V.esc(text)}</div>'
    shown = V.cased(number, STYLE['case'])
    parts = count_parts(shown) if COUNT > 0 else None
    counting = bool(parts) and parts[1] >= 10 and t_out - t_in > COUNT + .3
    start = f'{parts[0]}0{parts[3]}' if counting else shown
    p.html.append(f'<div class="stw" style="top:{y}px"><div id="{i}" class="st"><div id="{i}n" class="vg-big" '
                  f'style="font-size:{size}px">{V.esc(start)}</div><div style="position:relative;height:48px;margin-top:10px">'
                  f'{sub_html}</div></div></div>')
    p.enter(f'#{i}', t_in, {'scale': 1.25, 'y': 10}, {'scale': 1, 'y': 0}, .3, 'back.out(2)')
    p.drift(f'#{i}', t_in + .3, t_out - V.LEAVE)
    p.leave(f'#{i}', t_out)
    p.sound('pop', t_in, .2)
    if counting:
        pre, value, sep, post = parts
        fmt = (f"(Math.round(o.v)+'').replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,{json.dumps(sep)})" if sep else 'Math.round(o.v)')
        # the count is a tween on the reel's one timeline: the renderer seeks it frame by frame like everything else
        p.js.append(f"(function(){{const o={{v:0}},el=document.getElementById('{i}n');"
                    f"tl.to(o,{{v:{value},duration:{COUNT},ease:'power2.out',onUpdate:()=>{{el.textContent="
                    f"{json.dumps(pre)}+{fmt}+{json.dumps(post)};}}}},{V.T(t_in):.3f});}})();")
    for k, (text, at) in enumerate(subs):
        end = subs[k + 1][1] if k + 1 < len(subs) else t_out
        p.enter(f'#{i}s{k}', max(at, t_in + .12), {'y': 16}, {'y': 0}, .22, 'power3.out', t_out=end)
        print(f'  sub line {text!r} at {at:.2f}s')
    print(f'  number {number!r} at {t_in:.2f}s, {size}px, centre y {y}'
          + (f', counts up in {COUNT:.1f}s' if counting else '') + f'; out at {t_out:.2f}s')
    p.write()
    print(f'snapshot at: {t_in + .1:.2f},{t_in + COUNT / 2:.2f},' + ','.join(f'{at + .15:.2f}' for _, at in subs)
          + f',{max(0, t_out - .08):.2f}')
    s.hide_hint([(t_in, t_out)])


if __name__ == '__main__':
    main()
