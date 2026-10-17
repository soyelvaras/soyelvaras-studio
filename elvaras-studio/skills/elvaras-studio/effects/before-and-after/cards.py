#!/usr/bin/env python3
"""before-after, version 2 "Tarjetas": a presentation video of a finished reel, not a slot inside it.

On the brand's light page the raw cut plays in a small card behind, on the left ("Antes"), and the finished reel plays in a
big card in front, on the right ("Después"), both on the same frame the whole time, with the reel's own sound. A wordmark
sits under the cards. Made AFTER the final render, to show a client's job: the slot is never laid into the reel.

build.py hands over to this file when VARIANT = 2 (its CLIP block holds REEL, TITLES, NAME, CREDIT, PROGRESS). The slot is
made over the whole reel (or the part to show) with fx_new.py --no-cutout: its assets/aroll.mp4 is the "Antes" side, and
the finished reel is read from the same moment (clip.json "in"), so both cards always show the same frame.
"""
import glob
import json
import os
import shutil
import subprocess
import sys

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FF = shutil.which('ffmpeg') or 'ffmpeg'
FP = shutil.which('ffprobe') or 'ffprobe'
PAGE, INK, BOSQUE, DORADO, LINEA = '#F2ECDF', '#141615', '#13281F', '#C9A15B', '#DDD4C2'
# the layout (1080x1920, all inside the Reels safe zone: top 220, nothing below 1470)
AFTER_BOX = (400, 330, 562, 999)        # x, y, w, h of the big card (9:16)
BEFORE_BOX = (118, 528, 340, 604)       # the small card behind it, same centre line
AFTER_R, BEFORE_R = 28, 16
LABEL_TOP = 222                          # top of the "Después" title; "Antes" sits 22 px over its own card
NAME_Y = 1366                            # top of the wordmark


def frames_of(path):
    out = subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets,width,height',
                          '-of', 'default=nw=1', path], capture_output=True, text=True).stdout
    kv = dict(line.split('=', 1) for line in out.splitlines() if '=' in line)
    return int(kv['nb_read_packets']), int(kv['width']), int(kv['height'])


def find_reel(project, reel):
    """the finished reel: REEL as given (relative to the project), or the newest full render in <project>/renders"""
    if reel:
        p = reel if os.path.isabs(reel) else os.path.join(project, reel)
        if not os.path.exists(p):
            sys.exit(f'REEL = {reel!r}: no such file in the project. Render the reel first, or fix the name')
        return p
    cands = [p for p in glob.glob(os.path.join(project, 'renders', '*.mp4'))
             if not any(k in os.path.basename(p) for k in ('-phone', 'antes-despues', 'preview', '-web'))]
    if not cands:
        sys.exit('no finished reel in the project renders/: render the reel first (or set REEL)')
    return max(cands, key=os.path.getmtime)


def wordmark(name):
    """the name under the cards: 'auto' = the Soy Elvaras wordmark (SOY EL in Bebas Neue + Varas in Instrument Serif italic)"""
    if name is None:
        return ''
    if name == 'auto':
        return '<div class="wm"><span class="wm1">SOY EL</span><span class="wm2">Varas</span></div>'
    return f'<div class="wm"><span class="wm3">{name}</span></div>'


def main(reel=None, titles=('Antes', 'Después'), name='auto', credit=None, progress=True):
    clipj = json.load(open(os.path.join(HERE, 'clip.json'), encoding='utf-8'))
    n, t_in = int(clipj['frames']), float(clipj.get('in') or 0)
    dur = n / FPS
    project = clipj.get('project')
    if not project:
        sys.exit('clip.json has no project: make this slot with fx_new.py --project, over the finished reel')
    src = find_reel(project, reel)
    rn, rw, rh = frames_of(src)
    if abs(rw / rh - 9 / 16) > .01:
        sys.exit(f'{os.path.basename(src)} is {rw}x{rh}: Tarjetas wants the 9:16 reel')
    need = round(t_in * FPS) + n
    if rn < need - 1:
        sys.exit(f'{os.path.basename(src)} has {rn} frames, the slot needs frames up to {need}: is it the render of this project, '
                 'and does the slot fit inside the reel?')
    an = frames_of(os.path.join(HERE, 'assets/aroll.mp4'))[0]
    notes = []
    if t_in == 0 and abs(rn - an) > 1 and clipj.get('frames') == an:
        notes.append(f'the reel has {rn} frames and the raw cut {an}: if the reel was cut again after this slot was made, make the slot again')
    os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
    dst = os.path.join(HERE, 'assets/reel.mp4')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src) or os.path.getsize(dst) != os.path.getsize(src):
        shutil.copyfile(src, dst)
    ax, ay, aw, ah = AFTER_BOX
    bx, by, bw, bh = BEFORE_BOX
    vis_c = bx + (ax - bx) / 2                          # centre of the part of the small card you can see
    css = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{PAGE}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:{PAGE}}}
.card{{position:absolute;overflow:hidden;background:#000}}
.card video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#before{{left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px;border-radius:{BEFORE_R}px;
  box-shadow:0 18px 40px -14px rgba(19,40,31,.38),0 3px 10px rgba(19,40,31,.14)}}
#after{{left:{ax}px;top:{ay}px;width:{aw}px;height:{ah}px;border-radius:{AFTER_R}px;
  box-shadow:0 46px 90px -24px rgba(19,40,31,.55),0 10px 26px rgba(19,40,31,.2)}}
.t{{position:absolute;white-space:nowrap;transform:translateX(-50%)}}
#tb{{left:{vis_c:.0f}px;top:{by - 22 - 34}px;font:600 30px/34px 'Work Sans';letter-spacing:.16em;text-transform:uppercase;color:{INK};opacity:.62}}
#ta{{left:{ax + aw / 2:.0f}px;top:{LABEL_TOP}px;font:italic 400 92px/92px 'Instrument Serif';letter-spacing:-.01em;color:{BOSQUE}}}
#bar{{position:absolute;left:{ax + 24}px;top:{ay + ah + 16}px;width:{aw - 48}px;height:3px;border-radius:2px;background:{LINEA}}}
#prog{{position:absolute;inset:0;border-radius:2px;background:{DORADO};transform-origin:0 50%}}
.wm{{position:absolute;left:0;right:0;top:{NAME_Y}px;text-align:center;white-space:nowrap}}
.wm1{{font:400 66px/66px 'Bebas Neue';letter-spacing:.02em;color:{BOSQUE}}}
.wm2{{font:italic 400 74px/66px 'Instrument Serif';color:{DORADO};margin-left:.06em}}
.wm3{{font:600 44px/60px 'Work Sans';color:{BOSQUE}}}
#cr{{position:absolute;left:0;right:0;top:{NAME_Y + 72}px;text-align:center;font:500 24px/28px 'Work Sans';letter-spacing:.06em;color:{INK};opacity:.6}}
'''
    safe = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
            '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>'
            if os.environ.get('SAFE') and os.environ.get('SAFE') != '0' else '')
    tb, ta = (titles or ('', ''))
    tw = ["gsap.set('#prog',{scaleX:0});", f"tl.to('#prog',{{scaleX:1,duration:{dur:.3f},ease:'none'}},0);"] if progress else []
    html = f'''<!doctype html>
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
  <audio id="snd" src="assets/reel.mp4" data-start="0" data-media-start="{t_in:.3f}" data-duration="{dur:.3f}" data-track-index="2" data-volume="1"></audio>
  <div id="before" class="card"><video id="vb" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video></div>
  <div id="after" class="card"><video id="va" src="assets/reel.mp4" muted playsinline data-start="0" data-media-start="{t_in:.3f}" data-duration="{dur:.3f}" data-track-index="1"></video></div>
  {f'<div id="tb" class="t">{tb}</div>' if tb else ''}
  {f'<div id="ta" class="t">{ta}</div>' if ta else ''}
  {'<div id="bar"><div id="prog"></div></div>' if progress else ''}
  {wordmark(name)}
  {f'<div id="cr">{credit}</div>' if credit and name is not None else ''}
{safe}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
tl.set({{}}, {{}}, {dur:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(html)
    os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)
    slug = os.path.basename(os.path.normpath(project))
    json.dump({'kind': 'presentation', 'variant': 'Tarjetas', 'reel': src, 'deliver': os.path.join(project, 'renders', f'{slug}-antes-despues.mp4')},
              open(os.path.join(HERE, 'work/presentation.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    name_s = os.path.basename(HERE)
    print(f'wrote index.html  {name_s}  version 2 Tarjetas  {n} frames ({dur:.2f}s) from reel second {t_in:.2f}')
    print(f'  antes   : assets/aroll.mp4 (the raw cut of the slot)')
    print(f'  despues : {os.path.relpath(src, project)} ({rn} frames) -> assets/reel.mp4, read from {t_in:.2f}s; its sound is the sound of the video')
    for line in notes:
        print('  !! ' + line)
    print(f'  this is its own video, not a slot: do NOT run fx_add.py. After hf render, deliver renders/{name_s}.mp4 as '
          f'{slug}-antes-despues.mp4 (copy it to the project renders/)')
