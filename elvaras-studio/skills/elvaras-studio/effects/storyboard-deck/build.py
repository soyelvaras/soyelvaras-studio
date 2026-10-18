#!/usr/bin/env python3
"""storyboard-deck (Mazo de Storyboard): a row of storyboard cards is dealt over the chest one by one, like playing
cards: first the script card (the line being said), then frames of your own reel, each with its shot number, its time
and the words said in it. One card lifts to stand out, then the whole row is swept off to the side.

Everything on the cards is real: frames taken from your own footage at the times you give, the words said at those
times (from the clip's words.json, or written by you), the line of the script card. The row sits under the chin, in
front of the body, never over the face; the reel's own captions step aside while it is up (work/reel_captions.json).

Run from the slot folder:
    PY build.py      writes index.html (SAFE=1 safe-zone guide, SFX=0 no sounds)
"""
import json
import os
import random
import shutil
import subprocess
import sys

# ==== CLIP (edit this) ====
F_IN = 12            # frame the first card is dealt
F_OUT = None         # frame the row lifts away. None = 14 frames before the slot ends
SCRIPT = None        # text of the script card. None = the words said in the slot (words.json), cut to fit
# The frame cards, in order: (clip, second, 'quote' or None). clip = 'aroll' (this slot's own footage) or a path to one
# of your reels; second = where in that clip; quote = the words said there (None = read from that clip's words.json
# when it has one). [] = four frames spread over this slot's own footage.
FRAMES = []
HIGHLIGHT = 1        # which frame card lifts to stand out (1 = the first frame card; 0 = none)
DEAL_EVERY = 4       # frames between one card and the next
SFX_VOL = 1.0
# ==== END CLIP ====

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FF = shutil.which('ffmpeg') or 'ffmpeg'
FP = shutil.which('ffprobe') or 'ffprobe'
BOSQUE, CREMA, DORADO, TINTA = '#13281F', '#F2ECDF', '#C9A15B', '#141615'
DEAL, LIFT = 8, 9            # frames a card takes to land, frames the row takes to lift away
SFX_GAIN = .75
SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def F(n):
    return max(0.0, n / FPS - .002)


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def mmss(sec):
    s = int(sec)
    return f'{s // 60}:{s % 60:02d}'


def words_of(path):
    """the words.json that belongs to a clip: this slot's own, or the project's of a render (renders/x.mp4 -> words.json)"""
    for cand in (os.path.join(os.path.dirname(path), 'words.json'), os.path.join(os.path.dirname(os.path.dirname(path)), 'words.json')):
        if os.path.exists(cand):
            try:
                return json.load(open(cand, encoding='utf-8'))
            except ValueError:
                pass
    return []


def said_at(words, t, span=1.8):
    """the words spoken around second t (a short window, so the quote is the moment, not the sentence)"""
    near = [w['text'] for w in words if t - span / 2 <= float(w['start']) <= t + span / 2]
    return ' '.join(near).strip(' ,.') or None


def head_chin():
    clipj = json.load(open(os.path.join(HERE, 'clip.json')))
    lay_p = os.path.join(clipj.get('project') or '', 'layout.json')
    if clipj.get('project') and os.path.exists(lay_p):
        h = json.load(open(lay_p, encoding='utf-8')).get('head') or {}
        if h.get('chin_max') or h.get('chin'):
            return float(h.get('chin_max') or h['chin'])
    return 980.0


def main():
    clip = json.load(open(os.path.join(HERE, 'clip.json')))
    nfr = int(clip['frames'])
    dur = nfr / FPS - .001
    f_out = F_OUT if F_OUT is not None else nfr - 14
    slot_words = json.load(open(os.path.join(HERE, 'words.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, 'words.json')) else []
    frames = list(FRAMES) or [('aroll', round((k + .5) * dur / 4, 2), None) for k in range(4)]
    if not 2 <= len(frames) <= 5:
        sys.exit('FRAMES: 2 to 5 frame cards (the row also holds the script card)')
    n = len(frames) + 1
    land = [F_IN + k * DEAL_EVERY for k in range(n)]
    if F_IN < DEAL + 2 or f_out - land[-1] < 18 or f_out + LIFT > nfr - 2:
        sys.exit(f'frames: F_IN {F_IN} (>= {DEAL + 2}), the full row up 18 frames or more before F_OUT ({f_out}; last card lands '
                 f'f{land[-1]}), and gone 2 frames before the slot ends (F_OUT <= {nfr - 2 - LIFT})')
    script = SCRIPT or ' '.join(w['text'] for w in slot_words).strip() or '...'

    # layout: one row under the chin, as wide as the safe zone allows
    chin = head_chin()
    gap = 16
    left, right = 55, 975                # the row ends left of the column Instagram's buttons cover (x 980, below y 1155)
    cw = int(min(178, (right - left - (n - 1) * gap) / n))
    ih = int(cw * 1.42)                 # picture height inside a frame card
    chh = ih + int(cw * .34)            # card height (picture + quote strip)
    top = int(chin + 60)
    if top + chh > 1450:
        scale = (1450 - top) / chh
        cw, ih, chh = int(cw * scale), int(ih * scale), int((1450 - top))
        if cw < 110:
            sys.exit(f'no room for the row under the chin (chin at y {chin:.0f}): use a wider shot or leave this effect out')
    W = n * cw + (n - 1) * gap
    x0 = left + (right - left - W) / 2
    os.makedirs(os.path.join(HERE, 'assets/deck'), exist_ok=True)

    cards, sets, tw = [], [], []
    rng = random.Random(4)
    # the script card
    sfs = max(13, round(cw * .105))
    words = script.split()
    shown = ''
    for wd in words:                      # cut the line so it fits about 9 lines of the card
        if len(shown) + len(wd) + 1 > int(9 * cw / (sfs * .48)):
            shown = shown.rstrip(' ,.') + '…'
            break
        shown += wd + ' '
    cards.append(f'<div class="cd sc" id="cd0" style="width:{cw}px;height:{chh}px"><div class="hd"><span>GUION</span><span>01</span></div>'
                 f'<div class="tx" style="font-size:{sfs}px;line-height:{round(sfs * 1.3)}px">&ldquo;{esc(shown.strip())}&rdquo;</div>'
                 f'<div class="ln"></div><div class="ln short"></div></div>')
    # the frame cards: a still from the user's own footage, its number and time, and the words said there
    for k, (src, sec, quote) in enumerate(frames):
        path = os.path.join(HERE, 'assets/aroll.mp4') if src == 'aroll' else (src if os.path.isabs(src) else os.path.join(HERE, src))
        if not os.path.exists(path):
            sys.exit(f'frame card {k + 1}: {src} is not there (use "aroll" for this slot, or a path to one of your own reels)')
        out = os.path.join(HERE, f'assets/deck/f{k}.jpg')
        w2, h2 = (cw * 2) // 2 * 2, (ih * 2) // 2 * 2
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{float(sec):.3f}', '-i', path, '-frames:v', '1', '-vf',
                        f'scale={w2}:{h2}:force_original_aspect_ratio=increase:flags=lanczos,crop={w2}:{h2}', '-q:v', '3', out], check=True)
        if quote is None:
            quote = said_at(slot_words if src == 'aroll' else words_of(path), float(sec)) or ''
        when = mmss(float(clip.get('in') or 0) + float(sec)) if src == 'aroll' else mmss(float(sec))
        qfs = max(11, round(cw * .082))
        cards.append(f'<div class="cd fr" id="cd{k + 1}" style="width:{cw}px;height:{chh}px">'
                     f'<div class="im" style="height:{ih}px;background-image:url(assets/deck/f{k}.jpg)">'
                     f'<div class="tag"><span>{k + 2:02d}</span><span>{when}</span></div></div>'
                     f'<div class="q" style="font-size:{qfs}px;line-height:{round(qfs * 1.25)}px">{("&ldquo;" + esc(quote) + "&rdquo;") if quote else ""}</div></div>')
    html = []
    for k, c in enumerate(cards):
        x = x0 + k * (cw + gap)
        rot = rng.uniform(-3.2, 3.2)
        html.append(f'<div class="slot" style="left:{x:.0f}px;top:{top}px">{c}</div>')
        t0 = F(land[k] - DEAL)
        sets.append(f"gsap.set('#cd{k}',{{autoAlpha:0,x:{1080 - x + 60:.0f},y:-40,rotation:24}});")
        tw += [f"tl.set('#cd{k}',{{autoAlpha:1}},{t0:.3f});",
               f"tl.to('#cd{k}',{{x:0,y:0,rotation:{rot:.2f},duration:{DEAL / FPS:.3f},ease:'power3.out'}},{t0:.3f});"]
        # they leave the way a hand sweeps a row off the table: to the left, at chest height, never up across the face
        tw.append(f"tl.to('#cd{k}',{{x:{-(x + cw + 160):.0f},y:60,rotation:{rot - 14:.1f},autoAlpha:0,duration:{(LIFT - 1) / FPS:.3f},"
                  f"ease:'power2.in'}},{F(f_out + (n - 1 - k)):.3f});")
    if HIGHLIGHT and 1 <= HIGHLIGHT <= len(frames):
        hk = HIGHLIGHT
        t_hi = F(land[-1] + 6)
        t_dn = F(f_out) - .26
        tw += [f"tl.to('#cd{hk}',{{scale:1.14,y:-28,duration:.24,ease:'back.out(2)'}},{t_hi:.3f});",
               f"tl.to('#cd{hk}',{{scale:1,y:0,duration:.2,ease:'power2.inOut'}},{t_dn:.3f});"]
        sets.append(f"gsap.set('#cd{hk}',{{zIndex:5}});")
    snd = [('click-soft', land[k] - 2, .07) for k in range(n)] + [('whoosh-short', f_out - 1, .10)]
    audio = []
    if SFX_VOL > 0 and os.environ.get('SFX') != '0':
        for j, (name, fr, vol) in enumerate(snd):
            p = f'assets/sfx/{name}.mp3'
            if not os.path.exists(os.path.join(HERE, p)) or fr < 0:
                continue
            audio.append(f'<audio id="sx{j}" src="{p}" data-start="{F(fr):.3f}" data-duration="{min(.6, dur - F(fr)):.3f}" '
                         f'data-track-index="{20 + j}" data-volume="{vol * SFX_VOL * SFX_GAIN:.3f}"></audio>')
    css = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.slot{{position:absolute;width:0;height:0}}
.cd{{position:absolute;left:0;top:0;border-radius:10px;background:{CREMA};overflow:hidden;transform-origin:50% 60%;
  box-shadow:0 18px 34px rgba(0,0,0,.42),0 3px 8px rgba(0,0,0,.28)}}
.sc{{padding:0 10px}}
.sc .hd{{margin:0 -10px 10px;height:24px;background:{BOSQUE};display:flex;justify-content:space-between;align-items:center;padding:0 9px;
  font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.14em;color:{DORADO}}}
.sc .tx{{font-family:'Instrument Serif',serif;font-style:italic;color:{TINTA}}}
.sc .ln{{height:2px;margin-top:12px;background:rgba(20,22,21,.14);border-radius:1px}}
.sc .ln.short{{width:60%;margin-top:8px}}
.fr{{padding:6px 6px 0}}
.fr .im{{position:relative;border-radius:6px;background-size:cover;background-position:50% 40%}}
.fr .tag{{position:absolute;left:0;right:0;top:0;height:20px;padding:0 6px;display:flex;justify-content:space-between;align-items:center;
  background:linear-gradient(180deg,rgba(19,40,31,.92),rgba(19,40,31,.7));border-radius:6px 6px 0 0;
  font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.1em;color:{CREMA}}}
.fr .tag span:first-child{{color:{DORADO}}}
.fr .q{{padding:6px 2px 0;font-family:'Instrument Serif',serif;font-style:italic;color:{TINTA};overflow:hidden;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}
'''
    nl = '\n'
    page = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio)}
  <video id="bgv" class="full" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
{nl.join(html)}
{SAFE_GUIDE if os.environ.get('SAFE') == '1' else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(sets)}
{nl.join(tw)}
tl.set({{}}, {{}}, {dur:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(page)
    os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)
    json.dump({'hide': [[round(F(land[0] - DEAL), 3), round(F(f_out + LIFT + n), 3)]]}, open(os.path.join(HERE, 'work/reel_captions.json'), 'w'))
    print(f'wrote index.html  {nfr} frames  row of {n} cards {cw}x{chh}px at y {top} (chin {chin:.0f}), dealt f{land[0]} to f{land[-1]}, '
          f'lifts f{f_out}' + (f', card {HIGHLIGHT + 1} stands out' if HIGHLIGHT else ''))
    print(f'  script: "{shown.strip()}"')
    for k, (src, sec, quote) in enumerate(frames):
        print(f'  frame {k + 1}: {os.path.basename(src) if src != "aroll" else "this slot"} at {float(sec):.2f}s')
    print('  reel captions: hidden while the row is up (work/reel_captions.json)')
    snaps = sorted({land[0] - DEAL - 1, land[1], land[-1] + 2, land[-1] + 14, f_out + 3, f_out + LIFT + n})
    print('snapshot times: ' + ','.join(f'{(f + .5) / FPS:.3f}' for f in snaps if 0 <= f < nfr))
    print(f'render to renders/{os.path.basename(HERE)}.mp4')


if __name__ == '__main__':
    main()
