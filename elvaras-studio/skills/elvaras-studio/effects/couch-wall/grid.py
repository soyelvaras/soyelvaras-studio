#!/usr/bin/env python3
"""couch-wall, version 2 "Grilla en movimiento": your reels drop in from the top one by one, PLAYING, into a grid around
and behind your head, then fly away.

build.py hands over to this file when VARIANT = 2. The cards come from the same folder as the covers (COVERS): a video
clip of one of your reels plays in its card (a piece from its middle, cut and scaled here into assets/grid/), an image
stays still. No wall matte and no prep.py: only the speaker's cutout (assets/subject.webm) sits in front of the cards,
so they pass behind the head and never over the face.
"""
import json
import os
import random
import shutil
import subprocess
import sys

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FF = shutil.which('ffmpeg') or 'ffmpeg'
FP = shutil.which('ffprobe') or 'ffprobe'
VIDEO_EXT = ('.mp4', '.mov', '.m4v', '.webm')
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.webp')
TOP = 240                      # top of the grid (Reels safe zone 220, plus air)
GAP = 26                       # px between cards
FALL, SETTLE = 7, 6            # frames a card falls, frames it settles after it hits
OUT = 9                        # frames the cards take to fly away
SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def F(n):
    return max(0.0, n / FPS - .002)


def probe_dur(path):
    out = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout
    try:
        return float(out.strip())
    except ValueError:
        return 0.0


def card_media(files, cw, ch, need):
    """one file per card in assets/grid/: a video piece (from the middle of the clip, `need` seconds long) or a still"""
    os.makedirs(os.path.join(HERE, 'assets/grid'), exist_ok=True)
    out = []
    w2, h2 = (int(cw * 1.5) // 2) * 2, (int(ch * 1.5) // 2) * 2       # a bit sharper than the card, still light to decode
    for k, src in enumerate(files):
        ext = os.path.splitext(src)[1].lower()
        if ext in VIDEO_EXT:
            dst = os.path.join(HERE, f'assets/grid/card{k}.mp4')
            stamp = f'{os.path.abspath(src)}|{os.path.getmtime(src)}|{w2}x{h2}|{need:.2f}'
            marker = dst + '.src'
            if not (os.path.exists(dst) and os.path.exists(marker) and open(marker, encoding='utf-8').read() == stamp):
                d = probe_dur(src)
                start = max(0.0, d / 2 - need / 2) if d > need + .5 else 0.0
                subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{start:.3f}', '-i', src, '-t', f'{need:.3f}', '-an', '-vf',
                                f'scale={w2}:{h2}:force_original_aspect_ratio=increase:flags=lanczos,crop={w2}:{h2},fps={FPS},setsar=1',
                                '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-g', '15',
                                '-movflags', '+faststart', dst], check=True)
                open(marker, 'w', encoding='utf-8').write(stamp)
            out.append(('video', f'assets/grid/card{k}.mp4', os.path.basename(src)))
        else:
            dst = os.path.join(HERE, f'assets/grid/card{k}.jpg')
            subprocess.run([FF, '-v', 'error', '-y', '-i', src, '-vf',
                            f'scale={w2}:{h2}:force_original_aspect_ratio=increase:flags=lanczos,crop={w2}:{h2}', '-q:v', '3', dst], check=True)
            out.append(('image', f'assets/grid/card{k}.jpg', os.path.basename(src)))
    return out


def main(covers, f_in, f_out, grid=(3, 2), drop_every=4, size=1.0, sounds=True, voice=True, seed=5):
    clip = json.load(open(os.path.join(HERE, 'clip.json')))
    nfr = int(clip['frames'])
    dur = nfr / FPS - .001
    if not os.path.exists(os.path.join(HERE, 'assets/subject.webm')):
        sys.exit('Grilla en movimiento needs the cutout (assets/subject.webm): make the slot without --no-cutout')
    folder = covers if os.path.isabs(covers) else os.path.join(HERE, covers)
    if not os.path.isdir(folder):
        sys.exit(f'{covers}: no such folder. Put clips of your own reels (mp4 / mov) or your covers in it')
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if os.path.splitext(f)[1].lower() in VIDEO_EXT + IMAGE_EXT]
    cols, rows = grid
    if not (2 <= cols <= 4 and 1 <= rows <= 3):
        sys.exit('GRID must be (2 to 4 columns, 1 to 3 rows)')
    count = cols * rows
    if len(files) < 2:
        sys.exit(f'{covers} holds {len(files)} usable files: give at least 2 (better {count}) clips or covers of your own reels')
    files = (files * count)[:count]
    land = [f_in + k * drop_every for k in range(count)]
    if land[0] - FALL < 2:
        sys.exit(f'F_IN {f_in} is too early: the first card needs {FALL} frames to fall in (F_IN >= {FALL + 2})')
    if f_out is not None:
        if f_out - land[-1] - SETTLE < 15:
            sys.exit(f'F_OUT {f_out}: the last card lands on f{land[-1]}; give the full grid 15 frames or more to be seen '
                     f'(F_OUT >= {land[-1] + SETTLE + 15}), or lower DROP_EVERY')
        if f_out + OUT > nfr - 2:
            sys.exit(f'F_OUT {f_out}: the cards need {OUT} frames to fly away and the last 2 frames must be the plain clip '
                     f'(F_OUT <= {nfr - 2 - OUT})')
    end = (f_out + OUT) if f_out is not None else nfr - 1

    # layout: cards in 9:16, as wide as the safe zone allows, centred
    cw = int(min(240 * size, (980 - (cols - 1) * GAP) / cols))
    ch = int(cw * 16 / 9)
    while TOP + rows * ch + (rows - 1) * GAP > 1440 and cw > 120:
        cw -= 8
        ch = int(cw * 16 / 9)
    W = cols * cw + (cols - 1) * GAP
    x0 = (1080 - W) / 2
    rng = random.Random(seed)
    slots = [(c, r) for r in range(rows) for c in range(cols)]
    order = slots[:1] + rng.sample(slots[1:], len(slots) - 1)            # top-left first, then scattered, like a feed filling up
    need = (end - (land[0] - FALL)) / FPS + .3
    media = card_media(files, cw, ch, need)

    html, sets, tw, snd = [], [], [], []
    for k, ((c, r), (kind, src, name)) in enumerate(zip(order, media)):
        x, y = x0 + c * (cw + GAP), TOP + r * (ch + GAP)
        rot = rng.uniform(-2.5, 2.5)
        tilt = rng.choice((-1, 1)) * rng.uniform(7, 13)
        t0, tl_ = F(land[k] - FALL), F(land[k])
        body = (f'<video id="cv{k}" src="{src}" muted playsinline data-start="{t0:.3f}" data-media-start="0" '
                f'data-duration="{F(end) - t0 + .05:.3f}" data-track-index="{3 + k}"></video>' if kind == 'video'
                else f'<img src="{src}" alt="" />')
        html.append(f'<div class="card" id="cd{k}" style="left:{x:.0f}px;top:{y:.0f}px;width:{cw}px;height:{ch}px">{body}</div>')
        sets.append(f"gsap.set('#cd{k}',{{autoAlpha:0,y:{-(y + ch + 140):.0f},rotation:{tilt:.1f}}});")
        tw += [f"tl.set('#cd{k}',{{autoAlpha:1}},{t0:.3f});",
               f"tl.to('#cd{k}',{{y:12,rotation:{rot * .4:.2f},duration:{FALL / FPS - .004:.3f},ease:'power2.in'}},{t0:.3f});",
               f"tl.to('#cd{k}',{{y:0,rotation:{rot:.2f},duration:{SETTLE / FPS:.3f},ease:'back.out(2.2)'}},{tl_:.3f});"]
        snd.append(('pop', land[k] - 1, .09))
        if f_out is not None:
            to = F(f_out + (k % cols))
            tw += [f"tl.to('#cd{k}',{{y:{-(y + ch + 220):.0f},rotation:{rot - tilt * .5:.1f},duration:{(OUT - 2) / FPS:.3f},ease:'power2.in'}},{to:.3f});",
                   f"tl.set('#cd{k}',{{autoAlpha:0}},{F(f_out + OUT):.3f});"]
    if f_out is not None:
        snd.append(('whoosh-short', f_out - 2, .14))
    audio = []
    if sounds and os.environ.get('SFX') != '0':
        for j, (name, frame, vol) in enumerate(snd):
            path = f'assets/sfx/{name}.mp3'
            if not os.path.exists(os.path.join(HERE, path)) or frame < 0:
                continue
            d = min(probe_dur(os.path.join(HERE, path)) or .5, dur - F(frame))
            audio.append(f'<audio id="sx{j}" src="{path}" data-start="{F(frame):.3f}" data-duration="{d:.3f}" '
                         f'data-track-index="{20 + j}" data-volume="{vol * .75:.3f}"></audio>')
    css = '''
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}
.full{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
#cards{position:absolute;inset:0}
.card{position:absolute;border-radius:18px;overflow:hidden;background:#13281F;border:3px solid #F2ECDF;
  box-shadow:0 22px 40px rgba(0,0,0,.42),0 4px 10px rgba(0,0,0,.3)}
.card video,.card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
'''
    voice_el = (f'<audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{dur:.3f}" '
                f'data-track-index="2" data-volume="1"></audio>') if voice else ''
    nl = '\n'
    page = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="1080" data-height="1920">
  {voice_el}
{nl.join(audio)}
  <video id="bgv" class="full" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
  <div id="cards">
{nl.join(html)}
  </div>
  <video id="fg" class="full" src="assets/subject.webm" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="1"></video>
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
    vids = sum(1 for m in media if m[0] == 'video')
    print(f'wrote index.html  {nfr} frames ({dur:.3f}s)  version 2 Grilla en movimiento  grid {cols}x{rows}, cards {cw}x{ch}px, '
          f'{vids} playing, {len(media) - vids} still')
    print(f'  cards land f{land[0]} to f{land[-1]} (every {drop_every} frames)' +
          (f', fly away f{f_out} to f{f_out + OUT}' if f_out is not None else ', stay to the end'))
    for k, ((c, r), m) in enumerate(zip(order, media)):
        print(f'  card {k + 1}: column {c + 1}, row {r + 1}  {m[2]}  ({m[0]})')
    snaps = sorted({land[0] - FALL - 1, land[0] + 2, land[count // 2], land[-1] + SETTLE + 2,
                    *([f_out + 3, f_out + OUT + 1] if f_out is not None else [nfr - 2])})
    print('snapshot times: ' + ','.join(f'{(f + .5) / FPS:.3f}' for f in snaps if 0 <= f < nfr))
    print(f'render to renders/{os.path.basename(HERE)}.mp4')
