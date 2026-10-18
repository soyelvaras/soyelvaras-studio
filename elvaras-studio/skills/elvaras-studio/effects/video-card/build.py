#!/usr/bin/env python3
"""video-card (Tarjeta de Video): a video card pops in with a title and chapters; its picture plays the clip of each
chapter ("01 La toma cruda", then "02 El reel terminado"), a segmented progress line runs under it, and it leaves.

The card is a brand panel (bosque, Instrument Serif title, a dorado label) over a 16:9 picture. Vertical clips are
cropped to the band with the face (CROP_Y). Where it goes is measured: ABOVE the head when the card fits there (it then
sits behind the speaker, the head may cover its lower edge), otherwise OVER THE CHEST, in front, and the reel's captions
step aside while it is up (work/reel_captions.json, read by fx_add.py). It never covers the face.

Run from the slot folder:
    PY build.py      writes index.html (SAFE=1 safe-zone guide, SFX=0 no sounds)
"""
import json
import os
import re
import shutil
import subprocess
import sys

# ==== CLIP (edit this) ====
TITLE = 'Así edito un reel'   # the card title: the speaker's words or the user's
LABEL = 'TUTORIAL'            # small dorado label before the chapter count ('' = no label)
# The chapters, in order: (frame its label shows and its clip starts, 'name', 'clip', seconds into the clip[, crop]). The
# clip is a path (absolute, or inside the slot) to the user's own footage: the raw take, the finished reel, a screen
# recording... The first chapter's clip already plays from CARD_IN, under the intro label. The optional fifth value is
# how that clip fills the card: 'fit' or 'crop' (or a number = crop at that CROP_Y).
CHAPTERS = [
    (30, 'La toma cruda', 'card/raw.mp4', 0.0),
    (60, 'El reel terminado', 'card/final.mp4', 0.0),
]
CARD_IN = 8          # frame the card pops in (3 or later)
CARD_OUT = None      # frame it leaves. None = 12 frames before the slot ends
PLACE = 'auto'       # 'auto', 'above' (above the head, behind the speaker) or 'below' (over the chest, in front)
SIZE = 1.0           # card size (1 = up to 900 px wide; it shrinks to fit the room it gets)
FIT = 'fit'          # how a VERTICAL clip fills the 16:9 picture: 'fit' = YouTube style, the whole clip centred over a
                     # blurred copy of itself; 'crop' = cut to the band with the face (CROP_Y). A horizontal clip (a real
                     # YouTube video of yours) always fills the picture as it is
CROP_Y = .30         # 'crop' only: which 16:9 band survives (0 = top, .5 = middle). .3 keeps a face that sits high
BADGE = 'youtube'    # small app icon in the corner of the picture: 'youtube' or '' (none). File in assets/icons
ZOOM = 1.06          # the whole frame pushes in toward the card while it is up, and back as it leaves (1 = off)
SFX_VOL = 1.0        # sound level (0 = silent)
# ==== END CLIP ====

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FF = shutil.which('ffmpeg') or 'ffmpeg'
FP = shutil.which('ffprobe') or 'ffprobe'
TOP_SAFE, BOTTOM_SAFE = 236, 1462
RATIO = .5625 + .215         # card height / width: the 16:9 picture plus the panel
SFX_GAIN = .75
BOSQUE, CREMA, DORADO = '#13281F', '#F2ECDF', '#C9A15B'
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


def probe(path, entries):
    out = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', entries, '-of', 'default=nw=1', path],
                         capture_output=True, text=True).stdout
    return dict(line.split('=', 1) for line in out.splitlines() if '=' in line)


def head_box(f0, f1):
    """(head top, chin) on screen while the card is up: from the project's layout.json when the slot belongs to a reel,
    else read off the cutout (the top of the silhouette, and a chin from its width)"""
    clipj = json.load(open(os.path.join(HERE, 'clip.json')))
    lay_p = os.path.join(clipj.get('project') or '', 'layout.json')
    if clipj.get('project') and os.path.exists(lay_p):
        h = json.load(open(lay_p, encoding='utf-8')).get('head') or {}
        if h.get('top') and (h.get('chin_max') or h.get('chin')):
            return float(h.get('top_min') or h['top']), float(h.get('chin_max') or h['chin'])
    raw = subprocess.run([FF, '-v', 'error', '-c:v', 'libvpx-vp9', '-i', os.path.join(HERE, 'assets/subject.webm'), '-vf',
                          'alphaextract,scale=270:480:flags=area,format=gray', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    tops, widths = [], []
    for f in range(max(0, f0), f1 + 1):
        fr = raw[f * 270 * 480:(f + 1) * 270 * 480]
        if len(fr) < 270 * 480:
            break
        top = next((r for r in range(480) if max(fr[r * 270:(r + 1) * 270]) > 128), None)
        if top is None:
            continue
        row = fr[(top + 12) * 270:(top + 13) * 270] if top + 13 < 480 else fr[top * 270:(top + 1) * 270]
        widths.append(sum(1 for v in row if v > 128) * 4)
        tops.append(top * 4)
    if not tops:
        sys.exit('could not find the speaker in assets/subject.webm while the card is up')
    w = sorted(widths)[len(widths) // 2]
    return float(min(tops)), float(min(tops) + max(360, 1.9 * w))


def chapter_media(ends, cw, mh):
    """each chapter's clip, cut from its start for as long as it is on screen, cropped to 16:9 and scaled: assets/card/"""
    os.makedirs(os.path.join(HERE, 'assets/card'), exist_ok=True)
    w2, h2 = (int(cw * 1.3) // 2) * 2, (int(mh * 1.3) // 2) * 2
    out = []
    for k, (ch, end) in enumerate(zip(CHAPTERS, ends)):
        fr, name, src, t0 = ch[:4]
        mode = ch[4] if len(ch) > 4 else FIT
        cy = mode if isinstance(mode, (int, float)) else CROP_Y
        mode = 'crop' if isinstance(mode, (int, float)) else mode
        if mode not in ('fit', 'crop'):
            sys.exit(f"chapter {k + 1}: the fifth value is 'fit', 'crop' or a number (got {mode!r})")
        p = src if os.path.isabs(src) else os.path.join(HERE, src)
        if not os.path.exists(p):
            sys.exit(f'chapter {k + 1} "{name}": {src} is not there. Put the user\'s own clip in the slot (card/) or give a full path')
        info = probe(p, 'stream=width,height')
        w, h = int(info['width']), int(info['height'])
        start = (CARD_IN if k == 0 else fr)
        need = (end - start) / FPS + .3
        if h * 16 > w * 9 and mode == 'fit':                 # vertical, YouTube style: whole clip over a blurred copy
            vf = (f'split[a][b];[a]scale={w2}:{h2}:force_original_aspect_ratio=increase,crop={w2}:{h2},boxblur=22:2,'
                  f'eq=brightness=-0.10:saturation=0.85[bg];[b]scale=-2:{h2}:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:0')
        elif h * 16 > w * 9:                                 # vertical, cropped to the band with the face
            vf = f'crop=iw:trunc(iw*9/16/2)*2:0:(ih-iw*9/16)*{cy:.3f},scale={w2}:{h2}:flags=lanczos'
        else:
            vf = f'scale={w2}:{h2}:force_original_aspect_ratio=increase:flags=lanczos,crop={w2}:{h2}'
        dst = os.path.join(HERE, f'assets/card/ch{k}.mp4')
        stamp = f'{os.path.abspath(p)}|{os.path.getmtime(p)}|{t0}|{need:.2f}|{vf}'
        if not (os.path.exists(dst) and os.path.exists(dst + '.src') and open(dst + '.src', encoding='utf-8').read() == stamp):
            subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{float(t0):.3f}', '-i', p, '-t', f'{need:.3f}', '-an', '-vf',
                            vf + f',fps={FPS},setsar=1', '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                            '-g', '15', '-movflags', '+faststart', dst], check=True)
            open(dst + '.src', 'w', encoding='utf-8').write(stamp)
        out.append((f'assets/card/ch{k}.mp4', start, end))
    return out


def main():
    clip = json.load(open(os.path.join(HERE, 'clip.json')))
    nfr = int(clip['frames'])
    dur = nfr / FPS - .001
    c_out = CARD_OUT if CARD_OUT is not None else nfr - 12
    starts = [c[0] for c in CHAPTERS]
    if not CHAPTERS:
        sys.exit('CHAPTERS is empty: give one chapter or more')
    if CARD_IN < 3 or starts[0] < CARD_IN + 8 or starts != sorted(starts) or any(b - a < 12 for a, b in zip(starts, starts[1:])):
        sys.exit(f'frames: CARD_IN {CARD_IN} (3 or later), first chapter 8 frames or more after it, chapters in order and 12 '
                 f'frames or more apart (got {starts})')
    if c_out - starts[-1] < 15 or c_out > nfr - 10:
        sys.exit(f'CARD_OUT {c_out}: the last chapter needs 15 frames or more, and the card has to be gone 2 frames before the '
                 f'slot ends (CARD_OUT <= {nfr - 10})')
    if not os.path.exists(os.path.join(HERE, 'assets/subject.webm')):
        sys.exit('Tarjeta de Video needs the cutout (assets/subject.webm): make the slot without --no-cutout')

    head_top, chin = head_box(CARD_IN, c_out)
    above_w = min(900 * SIZE, (head_top - 14 - TOP_SAFE) / RATIO, 960)
    below_w = min(900 * SIZE, (BOTTOM_SAFE - (chin + 46)) / RATIO, 960)
    place = PLACE if PLACE in ('above', 'below') else ('above' if above_w >= 520 else 'below')
    W = int(above_w if place == 'above' else below_w)
    if W < 420:
        sys.exit(f'no room for the card {place} the head (it would be {W} px wide): use a wider shot, PLACE = '
                 f'"{"below" if place == "above" else "above"}", or leave this effect out')
    mh, ph = round(W * .5625), round(W * .215)
    H = mh + ph
    x = round((1080 - W) / 2)
    y = round(head_top - 14 - H) if place == 'above' else round(chin + 46)
    y = max(TOP_SAFE, y)
    ends = starts[1:] + [c_out]
    # each clip runs a little past its chapter (under the next one's fade in), the last one until the card is gone
    media = chapter_media([e + 4 for e in starts[1:]] + [min(nfr - 1, c_out + 10)], W, mh)
    n = len(CHAPTERS)

    # ---- page
    pad = round(W * .05)
    tfs = round(min(W * .085, (W - 2 * pad) / max(1, .43 * len(TITLE))))
    sfs = round(W * .034)
    gapw = 8
    seg_w = (W - 2 * pad - (n - 1) * gapw) / n
    vids = ''.join(f'<video id="cv{k}" class="cv" src="{src}" muted playsinline data-start="{F(s0):.3f}" data-media-start="0" '
                   f'data-duration="{F(e0) - F(s0) + .1:.3f}" data-track-index="{3 + k}"></video>' for k, (src, s0, e0) in enumerate(media))
    segs = ''.join(f'<div class="seg" style="left:{pad + k * (seg_w + gapw):.1f}px;width:{seg_w:.1f}px"><i id="fill{k}"></i></div>'
                   for k in range(n))
    count = f'{n} capítulo{"s" if n != 1 else ""}'
    subs = [f'<div class="st" id="st0">' + (f'<b>{esc(LABEL)}</b>' if LABEL else '') + f'<span>{count}</span></div>']
    subs += [f'<div class="st" id="st{k + 1}"><b class="nm">{k + 1:02d}</b><span>{esc(c[1])}</span></div>' for k, c in enumerate(CHAPTERS)]
    pb = round(W * .15)
    badge = ''
    if BADGE:
        bp = os.path.join(HERE, 'assets/icons', BADGE + '.svg')
        if not os.path.exists(bp):
            sys.exit(f'BADGE = {BADGE!r}: assets/icons/{BADGE}.svg is not there ("" = no badge)')
        icon = open(bp, encoding='utf-8').read()
        icon = re.sub(r'<title>.*?</title>', '', icon).replace('<svg', '<svg style="width:100%;height:100%;display:block;fill:#FF0000"', 1)
        bs = round(W * .085)
        badge = (f'<div id="badge" style="left:{round(W * .03)}px;top:{round(W * .03)}px;width:{round(bs * 1.32)}px;height:{bs}px">'
                 f'<div style="position:absolute;inset:{round(bs * .2)}px {round(bs * .22)}px">{icon}</div></div>')
    card = (f'<div id="card" style="left:{x}px;top:{y}px;width:{W}px;height:{H}px">'
            f'<div class="media" style="height:{mh}px">{vids}'
            f'<div id="play" style="width:{pb}px;height:{pb}px;margin:{-pb / 2:.0f}px 0 0 {-pb / 2:.0f}px">'
            f'<svg viewBox="0 0 24 24" width="{round(pb * .42)}" height="{round(pb * .42)}"><path d="M8 5.5v13l10.5-6.5z" fill="{BOSQUE}"/></svg></div>'
            f'<div class="shade"></div>{badge}<div id="bar" style="bottom:{round(W * .028)}px">{segs}<div id="knob"></div></div></div>'
            f'<div class="panel" style="height:{ph}px;padding:{round(ph * .14)}px {pad}px 0">'
            f'<div class="title" style="font-size:{tfs}px;line-height:{round(tfs * 1.08)}px">{esc(TITLE)}</div>'
            f'<div class="sub" style="font-size:{sfs}px;height:{round(sfs * 1.5)}px;margin-top:{round(ph * .06)}px">{"".join(subs)}</div></div></div>')
    sets, tw = [], []
    t_in, t_out = F(CARD_IN), F(c_out)
    sets += ["gsap.set('#card',{autoAlpha:0,y:40,scale:.96,transformOrigin:'50% 50%'});",
             "gsap.set('#play',{autoAlpha:0,scale:.5});", "gsap.set('.st',{autoAlpha:0,y:10});", "gsap.set('#st0',{autoAlpha:1,y:0});",
             f"gsap.set('#knob',{{x:{pad - 9:.1f}}});"]
    sets += [f"gsap.set('#fill{k}',{{scaleX:0}});" for k in range(n)]
    sets += [f"gsap.set('#cv{k}',{{autoAlpha:0}});" for k in range(1, n)]
    tw += [f"tl.to('#card',{{autoAlpha:1,y:0,scale:1,duration:.36,ease:'power3.out'}},{t_in:.3f});",
           f"tl.to('#play',{{autoAlpha:1,scale:1,duration:.26,ease:'back.out(2.2)'}},{t_in + .18:.3f});",
           f"tl.to('#play',{{autoAlpha:0,scale:1.25,duration:.2,ease:'power2.in'}},{F(starts[0]) - .2:.3f});"]
    for k, (s0, e0) in enumerate(zip(starts, ends)):
        a, b = F(s0), F(e0) - .03
        tw += [f"tl.to('#st{k}',{{autoAlpha:0,y:-8,duration:.12,ease:'power2.in'}},{a - .12:.3f});",
               f"tl.to('#st{k + 1}',{{autoAlpha:1,y:0,duration:.2,ease:'power3.out'}},{a:.3f});",
               f"tl.to('#fill{k}',{{scaleX:1,duration:{b - a:.3f},ease:'none'}},{a:.3f});",
               f"tl.fromTo('#knob',{{x:{pad + k * (seg_w + gapw) - 9:.1f}}},{{x:{pad + k * (seg_w + gapw) + seg_w - 9:.1f},duration:{b - a:.3f},"
               f"ease:'none',immediateRender:false}},{a:.3f});"]
        if k:
            tw += [f"tl.to('#cv{k}',{{autoAlpha:1,duration:.12,ease:'power1.out'}},{a:.3f});"]
    tw += [f"tl.to('#card',{{autoAlpha:0,y:-30,scale:.97,duration:.26,ease:'power2.in'}},{t_out:.3f});"]
    if ZOOM > 1.001:              # the whole frame leans in toward the card, slowly, and eases back as it leaves
        sets.append(f"gsap.set('#stage',{{scale:1,transformOrigin:'{x + W / 2:.0f}px {y + H / 2:.0f}px'}});")
        tw += [f"tl.to('#stage',{{scale:{ZOOM},duration:{max(.4, t_out - t_in - .1):.3f},ease:'sine.inOut'}},{t_in:.3f});",
               f"tl.to('#stage',{{scale:1,duration:{min(.45, (nfr - 3) / FPS - t_out - .1):.3f},ease:'power2.inOut'}},{t_out + .05:.3f});"]

    snd = [('pop', CARD_IN, .10), ('click-soft', CARD_IN + 6, .12)] + [('click-soft', s, .08) for s in starts[1:]] + \
          [('whoosh-short', c_out, .08)]
    audio = []
    if SFX_VOL > 0 and os.environ.get('SFX') != '0':
        for j, (name, fr, vol) in enumerate(snd):
            p = f'assets/sfx/{name}.mp3'
            if not os.path.exists(os.path.join(HERE, p)):
                continue
            d = min(.8, dur - F(fr))
            audio.append(f'<audio id="sx{j}" src="{p}" data-start="{F(fr):.3f}" data-duration="{d:.3f}" '
                         f'data-track-index="{20 + j}" data-volume="{vol * SFX_VOL * SFX_GAIN:.3f}"></audio>')
    css = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#card{{position:absolute;border-radius:28px;overflow:hidden;background:{BOSQUE};border:1.5px solid rgba(242,236,223,.18);
  box-shadow:0 34px 70px -18px rgba(0,0,0,.6),0 8px 22px rgba(0,0,0,.3)}}
.media{{position:relative;overflow:hidden;background:#000}}
.cv{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.shade{{position:absolute;left:0;right:0;bottom:0;height:34%;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.45))}}
#badge{{position:absolute;z-index:3;border-radius:22%;background:#FFFFFF;box-shadow:0 4px 14px rgba(0,0,0,.35)}}
#stage{{position:absolute;inset:0}}
#play{{position:absolute;left:50%;top:50%;border-radius:50%;background:{CREMA};display:flex;align-items:center;justify-content:center;
  box-shadow:0 10px 30px rgba(0,0,0,.4);z-index:3;padding-left:.5%}}
#bar{{position:absolute;left:0;right:0;height:6px;z-index:2}}
.seg{{position:absolute;top:0;height:6px;border-radius:3px;background:rgba(242,236,223,.3);overflow:hidden}}
.seg i{{position:absolute;inset:0;background:{CREMA};transform-origin:0 50%}}
#knob{{position:absolute;left:0;top:-6px;width:18px;height:18px;border-radius:50%;background:{DORADO};box-shadow:0 2px 8px rgba(0,0,0,.45)}}
.panel{{position:relative}}
.title{{font-family:'Instrument Serif',serif;font-weight:400;color:{CREMA};white-space:nowrap;letter-spacing:-.005em}}
.sub{{position:relative}}
.st{{position:absolute;left:0;top:0;white-space:nowrap;font-family:'Work Sans',sans-serif;font-weight:500;color:{CREMA};display:flex;align-items:baseline;gap:.55em}}
.st b{{font-weight:700;color:{DORADO};letter-spacing:.14em;font-size:.86em}}
.st b.nm{{letter-spacing:.04em;font-size:.95em}}
'''
    back = place == 'above'
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
  <div id="stage">
  <video id="bgv" class="full" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
  {card if back else ''}
  <video id="fg" class="full" src="assets/subject.webm" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="1"></video>
  {'' if back else card}
  </div>
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
    rc = os.path.join(HERE, 'work/reel_captions.json')
    if place == 'below':          # over the chest: the reel's own captions step aside while the card is up
        json.dump({'hide': [[round(t_in, 3), round(t_out + .3, 3)]]}, open(rc, 'w'))
    elif os.path.exists(rc):
        os.remove(rc)
    print(f'wrote index.html  {nfr} frames  card {W}x{H}px {place} the head (head top {head_top:.0f}, chin {chin:.0f}) at y {y}..{y + H}')
    print(f'  in f{CARD_IN}, out f{c_out}; chapters: ' + ', '.join(f'{k + 1:02d} "{c[1]}" f{c[0]}' for k, c in enumerate(CHAPTERS)))
    print('  reel captions: ' + ('hidden while the card is up (work/reel_captions.json)' if place == 'below' else 'stay on'))
    snaps = sorted({CARD_IN - 1, CARD_IN + 10, *[s + 6 for s in starts], c_out - 4, c_out + 9})
    print('snapshot times: ' + ','.join(f'{(f + .5) / FPS:.3f}' for f in snaps if 0 <= f < nfr))
    print(f'render to renders/{os.path.basename(HERE)}.mp4')


if __name__ == '__main__':
    main()
