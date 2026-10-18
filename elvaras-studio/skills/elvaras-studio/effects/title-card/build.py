#!/usr/bin/env python3
"""title-card (Tarjeta de Título): a chapter card. The picture cuts to the brand's bosque screen with a running dorado
timecode, a big serif title lands word by word with a short dorado rule under it, then the speaker comes back inside a
phone frame with a play bar, settles, and grows until the frame is the picture again.

Everything on it is real: the title is words the speaker says, the timecode is the reel's own time, the play bar shows
the reel's own position and length. One video only: the full picture itself shrinks into the phone and grows back.

Run from the slot folder:
    PY build.py      writes index.html (SAFE=1 safe-zone guide, SFX=0 no sounds)
"""
import json
import os
import sys

# ==== CLIP (edit this) ====
T_IN = 50            # frame the picture cuts to the title screen
TITLE = [            # the title, one line per entry: (frame it lands, 'WORDS'). Words the speaker says, in their order
    (57, 'MÍRALO'),
    (65, 'AHORA'),
]
PHONE_AT = None      # frame the speaker comes back inside the phone. None = 12 frames after the last title line
FULL_AT = None       # frame the phone starts growing back to the full picture. None = 16 frames after PHONE_AT
TIMECODE = True      # the running dorado timecode over the title (the reel's own time)
PLAYBAR = True       # the play bar inside the phone (the reel's own position and length)
SFX_VOL = 1.0        # sound level (0 = silent)
# ==== END CLIP ====

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
BOSQUE, CREMA, DORADO = '#13281F', '#F2ECDF', '#C9A15B'
PHONE_SCALE, PHONE_Y = .62, 858     # phone size (of the full picture) and the y of its centre
GROW = 9                            # frames the phone takes to grow back to the full picture
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


def tc(sec):
    f = int(round(sec * FPS))
    return f'{f // (3600 * FPS):02d}:{f // (60 * FPS) % 60:02d}:{f // FPS % 60:02d}:{f % FPS:02d}'


def mmss(sec):
    s = int(sec)
    return f'{s // 60}:{s % 60:02d}'


def main():
    clip = json.load(open(os.path.join(HERE, 'clip.json')))
    nfr = int(clip['frames'])
    dur = nfr / FPS - .001
    t0_reel = float(clip.get('in') or 0)
    reel_len = None
    proj = clip.get('project')
    if proj:
        try:
            import subprocess, shutil
            fp = shutil.which('ffprobe') or 'ffprobe'
            reel_len = float(subprocess.run([fp, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                             os.path.join(proj, 'assets/aroll.mp4')], capture_output=True, text=True).stdout.strip())
        except (ValueError, OSError):
            reel_len = None
    reel_len = reel_len or (t0_reel + nfr / FPS)
    if not TITLE:
        sys.exit('TITLE is empty: one line or more, with words the speaker says')
    lines = sorted(TITLE)
    phone = PHONE_AT if PHONE_AT is not None else lines[-1][0] + 12
    full = FULL_AT if FULL_AT is not None else phone + 16
    if T_IN < 2 or lines[0][0] < T_IN or phone - lines[-1][0] < 6 or full - phone < 8:
        sys.exit(f'frames: T_IN {T_IN} (2 or later), title lines from T_IN on ({[l[0] for l in lines]}), the phone 6 frames or more '
                 f'after the last line ({phone}), and 8 frames or more before it grows ({full})')
    end = full + GROW
    if end > nfr - 2:
        sys.exit(f'the card ends on f{end}, the slot has {nfr} frames: make the slot longer or move the frames earlier '
                 f'(the last 2 frames must be the plain picture)')

    # the title block: biggest size that fits the widest line, lines centred a little above the middle
    longest = max(len(t) for _, t in lines)
    fs = int(min(210, 900 / max(1, .62 * longest)))
    lh = int(fs * .98)
    block_h = lh * len(lines) + 40
    top = int(820 - block_h / 2)
    rule_y = top + lh * len(lines) + 18
    title_html = ''.join(f'<div class="tl" id="tl{k}" style="top:{top + k * lh}px;font-size:{fs}px;line-height:{lh}px">{esc(t)}</div>'
                         for k, (_, t) in enumerate(lines))
    tc_html = f'<div id="tc">{tc(t0_reel + T_IN / FPS)}</div>' if TIMECODE else ''
    bar_html = ''
    if PLAYBAR:
        bar_html = (f'<div id="pbar"><div id="pcount">{mmss(t0_reel + phone / FPS)} / {mmss(reel_len)}</div>'
                    f'<div id="ptrack"><i id="pfill"></i><b id="pknob"></b></div></div>')
    css = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#panel{{position:absolute;inset:0;background:{BOSQUE};z-index:1}}
#panel:after{{content:"";position:absolute;inset:0;background:radial-gradient(90% 60% at 50% 42%,rgba(255,255,255,.05),rgba(0,0,0,.22) 100%)}}
#tc{{position:absolute;left:0;right:0;top:300px;text-align:center;font-family:'JetBrains Mono',monospace;font-weight:500;font-size:34px;
  letter-spacing:.22em;color:{DORADO};z-index:2}}
.tl{{position:absolute;left:0;right:0;text-align:center;font-family:'Instrument Serif',serif;font-weight:400;color:{CREMA};
  letter-spacing:.02em;white-space:nowrap;z-index:2}}
#rule{{position:absolute;left:50%;top:{rule_y}px;width:120px;height:3px;margin-left:-60px;background:{DORADO};z-index:2;transform-origin:50% 50%}}
#vw{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;z-index:3;transform-origin:540px {PHONE_Y}px}}
#vw video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#frame{{position:absolute;inset:0;border:16px solid {CREMA};border-radius:96px;z-index:4;box-shadow:inset 0 0 0 2px rgba(0,0,0,.25)}}
#pbar{{position:absolute;left:70px;right:70px;bottom:150px;z-index:5}}
#pcount{{font-family:'JetBrains Mono',monospace;font-weight:500;font-size:44px;color:{CREMA};letter-spacing:.04em;
  text-shadow:0 2px 10px rgba(0,0,0,.6);margin-bottom:18px}}
#ptrack{{position:relative;height:9px;border-radius:5px;background:rgba(242,236,223,.35)}}
#pfill{{position:absolute;left:0;top:0;bottom:0;width:100%;border-radius:5px;background:{CREMA};transform-origin:0 50%}}
#pknob{{position:absolute;top:-10px;left:0;width:29px;height:29px;margin-left:-14px;border-radius:50%;background:{DORADO};
  box-shadow:0 3px 10px rgba(0,0,0,.5)}}
#shade{{position:absolute;left:0;right:0;bottom:0;height:420px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.5));z-index:4}}
'''
    sets, tw = [], []
    tIn, tPh, tFull, tEnd = F(T_IN), F(phone), F(full), F(end)
    # the title screen hides the picture, the phone brings it back small, then it grows back to the frame
    sets += ["gsap.set('#panel',{autoAlpha:0});", "gsap.set('.tl',{autoAlpha:0,y:24});", "gsap.set('#rule',{scaleX:0});",
             "gsap.set(['#frame','#pbar','#shade'],{autoAlpha:0});", "gsap.set('#vw',{scale:1,borderRadius:0});"]
    tw += [f"tl.set('#panel',{{autoAlpha:1}},{tIn:.3f});", f"tl.set('#vw',{{autoAlpha:0}},{tIn:.3f});"]
    for k, (fr, _) in enumerate(lines):
        tw.append(f"tl.to('#tl{k}',{{autoAlpha:1,y:0,duration:.22,ease:'power3.out'}},{F(fr) - .03:.3f});")
    tw.append(f"tl.to('#rule',{{scaleX:1,duration:.3,ease:'power2.out'}},{F(lines[-1][0]) + .08:.3f});")
    if TIMECODE:
        sets.append(f"gsap.set('#tc',{{autoAlpha:0}});")
        tw.append(f"tl.set('#tc',{{autoAlpha:1}},{tIn:.3f});")
        for f in range(T_IN, phone + 1):          # the timecode runs frame by frame: the reel's own time
            tw.append(f"tl.set('#tc',{{innerText:'{tc(t0_reel + f / FPS)}'}},{F(f):.3f});")
    # the phone: the whole picture, framed, big then settling small with a little overshoot
    tw += [f"tl.set('#vw',{{autoAlpha:1,scale:.9,borderRadius:96}},{tPh:.3f});",
           f"tl.set(['#frame','#shade'],{{autoAlpha:1}},{tPh:.3f});",
           f"tl.to('#vw',{{scale:{PHONE_SCALE},duration:.34,ease:'back.out(1.6)'}},{tPh:.3f});"]
    if PLAYBAR:
        p0, p1 = (t0_reel + phone / FPS) / reel_len, (t0_reel + full / FPS) / reel_len
        tw += [f"tl.set('#pbar',{{autoAlpha:1}},{tPh:.3f});",
               f"tl.fromTo('#pfill',{{scaleX:{p0:.4f}}},{{scaleX:{p1:.4f},duration:{tFull - tPh:.3f},ease:'none',immediateRender:false}},{tPh:.3f});",
               f"tl.fromTo('#pknob',{{x:{p0 * 940:.1f}}},{{x:{p1 * 940:.1f},duration:{tFull - tPh:.3f},ease:'none',immediateRender:false}},{tPh:.3f});",
               f"tl.to('#pbar',{{autoAlpha:0,duration:.12}},{tFull:.3f});"]
        sets += [f"gsap.set('#pfill',{{scaleX:{p0:.4f}}});", f"gsap.set('#pknob',{{x:{p0 * 940:.1f}}});"]
    tw += [f"tl.to('#vw',{{scale:1,borderRadius:0,duration:{GROW / FPS:.3f},ease:'power3.inOut'}},{tFull:.3f});",
           f"tl.to(['#frame','#shade'],{{autoAlpha:0,duration:{GROW / FPS * .8:.3f},ease:'power1.in'}},{tFull:.3f});",
           f"tl.set('#panel',{{autoAlpha:0}},{tEnd:.3f});",
           f"tl.set(['.tl','#rule','#tc'],{{autoAlpha:0}},{tEnd:.3f});"]
    snd = [('whoosh-short', T_IN - 2, .10)] + [('click-soft', fr, .10) for fr, _ in lines] + [('pop', phone, .12),
                                                                                            ('whoosh-short', full - 1, .08)]
    audio = []
    if SFX_VOL > 0 and os.environ.get('SFX') != '0':
        for j, (name, fr, vol) in enumerate(snd):
            p = f'assets/sfx/{name}.mp3'
            if not os.path.exists(os.path.join(HERE, p)) or fr < 0:
                continue
            audio.append(f'<audio id="sx{j}" src="{p}" data-start="{F(fr):.3f}" data-duration="{min(.8, dur - F(fr)):.3f}" '
                         f'data-track-index="{20 + j}" data-volume="{vol * SFX_VOL * SFX_GAIN:.3f}"></audio>')
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
  <div id="panel"></div>
  {tc_html}
  {title_html}
  <div id="rule"></div>
  <div id="vw"><video id="bgv" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
    <div id="shade"></div>{bar_html}<div id="frame"></div></div>
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
    # the title screen covers the whole frame: the reel's own captions step aside from the cut until the phone has grown back
    json.dump({'hide': [[round(tIn, 3), round(tEnd, 3)]]}, open(os.path.join(HERE, 'work/reel_captions.json'), 'w'))
    print(f'wrote index.html  {nfr} frames  title screen f{T_IN}, lines ' + ', '.join(f'"{t}" f{f}' for f, t in lines) +
          f', phone f{phone}, grows f{full} to f{end}  (title {fs}px)')
    print(f'  timecode from {tc(t0_reel + T_IN / FPS)}; play bar {mmss(t0_reel + phone / FPS)} / {mmss(reel_len)}')
    print(f'  reel captions: hidden f{T_IN} to f{end} (work/reel_captions.json)')
    snaps = sorted({T_IN - 1, T_IN + 2, *[f + 4 for f, _ in lines], phone + 3, phone + 12, full + 4, end + 1})
    print('snapshot times: ' + ','.join(f'{(f + .5) / FPS:.3f}' for f in snaps if 0 <= f < nfr))
    print(f'render to renders/{os.path.basename(HERE)}.mp4')


if __name__ == '__main__':
    main()
