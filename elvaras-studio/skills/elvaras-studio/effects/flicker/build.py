#!/usr/bin/env python3
"""flicker (transition): a hard cut between two shots becomes a burst of flashing light that lands on the next shot.

Two looks (VARIANT):
  1 Por capas  the main one. The speaker of shot B flickers in OVER shot A first (cut out, flashing white), settles,
               then the room behind flickers between the two shots and white, and shot B takes the frame
  2 Completo   the whole frame flickers: white flashes, shot A, shot B, faster and faster, landing on shot B

Nothing is baked: every frame of the transition just shows or hides a few layers (the live slot video, the last frame
of shot A, the first frame of shot B, the cutout of shot B, white). The cutout of shot B before the cut is its first
frame (a still): the flashing hides that it does not move. After the cut the live cutout takes over.

Run from the slot folder (full run order in effect.md):
    PY build.py      writes index.html (SAFE=1 safe-zone guide, SFX=0 no sound)
"""
import json
import math
import os
import shutil
import subprocess
import sys

# ==== CLIP (edit this) ====
CUT = None            # first frame of shot B. None = clip.json "cut_frames"[0] (fx_new.py writes it)
VARIANT = 1           # look: 1 = Por capas (shot B's speaker flickers in over shot A, then the room behind flickers,
                      # then shot B; needs assets/subject.webm, the cutout), 2 = Completo (the whole frame flickers)
LENGTH = 24           # frames the flicker takes (24 = 0.8 s). The patterns below are stretched or squeezed to it
FLASH = '#FFFFFF'     # colour of the flashes. White reads as light; the brand cream '#F2ECDF' is softer
FLASH_OPACITY = .95   # how solid a flash frame is (1 = a pure white frame)
PUNCH = 1.035         # zoom kick on the frame right after a flash, settling back (1 = none)
GLOW = 1.35           # brightness of the frame right after a flash (1 = none): the picture "comes back" overexposed
SFX_VOL = .26         # template volume of the flicker crackle (x0.75 is applied)
# ==== END CLIP ====

# ---- the look (not clip-specific) -----------------------------------------------------------------------------------
# One letter per frame, and the index of the letter that falls on the cut (the first frame of shot B):
#   A  shot A          B  shot B          W  a flash (FLASH colour, no picture)
#   p  shot A with shot B's speaker on top        P  shot A with shot B's speaker as a white silhouette
#   x  a flash with shot B's speaker on top
# Before the cut "shot B" is its first frame held; after the cut "shot A" is its last frame held.
PATTERNS = {
    1: ('PaPpaPPpPpxBpxBxxBpBBBBB', 16),
    2: ('WAWWAWBWAWWBWBWBBWBBBBBB', 12),
}
VARIANT_NAMES = {1: 'Por capas', 2: 'Completo'}
FPS = 30
SFX_GAIN = 0.75
SFX = ('glitch-2', 0.0)            # stock crackle under the burst: file, seconds of air before its first hit

FF = shutil.which('ffmpeg') or 'ffmpeg'
CLIPJ = json.load(open('clip.json'))
N = int(CLIPJ['frames'])
DUR = N / float(FPS)
SLOT = os.path.basename(os.getcwd())
if CUT is None:
    CUT = (CLIPJ.get('cut_frames') or [None])[0]
if CUT is None:
    sys.exit('no cut frame: make the slot across a cut of the reel (fx_new.py --from / --to around it), or set CUT')
if VARIANT not in PATTERNS:
    sys.exit('VARIANT must be one of %s' % ', '.join('%d (%s)' % (k, v) for k, v in VARIANT_NAMES.items()))


def pattern():
    """the version's letters stretched to LENGTH frames, and where the cut falls in them"""
    src, at = PATTERNS[VARIANT]
    n = max(8, int(LENGTH))
    out = ''.join(src[min(len(src) - 1, int(i * len(src) / n))] for i in range(n))
    k = int(round(at * n / len(src)))
    return out, k


PAT, AT = pattern()
F0 = CUT - AT                      # first frame of the flicker
if F0 < 2 or F0 + len(PAT) > N - 2:
    sys.exit('the flicker does not fit: it needs %d frames before the cut and %d after it (plus 2 on each side), the slot has '
             '%d before and %d after. Widen --from / --to, or lower LENGTH' % (AT, len(PAT) - AT, CUT, N - CUT))
HAS_CUT = os.path.exists('assets/subject.webm')
if VARIANT == 1 and not HAS_CUT:
    sys.exit('Por capas (version 1) needs the cutout (assets/subject.webm): make the slot without --no-cutout, '
             'or set VARIANT = 2 (Completo)')


def stills():
    """last frame of shot A, first frame of shot B, and shot B's cutout on that frame (with its alpha)"""
    os.makedirs('assets/flicker', exist_ok=True)
    for name, f in (('a_last.jpg', CUT - 1), ('b_first.jpg', CUT)):
        subprocess.run([FF, '-v', 'error', '-y', '-i', 'assets/aroll.mp4', '-vf', 'select=eq(n\\,%d)' % f,
                        '-frames:v', '1', '-q:v', '2', 'assets/flicker/' + name], check=True)
    if HAS_CUT:
        subprocess.run([FF, '-v', 'error', '-y', '-c:v', 'libvpx-vp9', '-i', 'assets/subject.webm', '-vf',
                        'select=eq(n\\,%d)' % CUT, '-frames:v', '1', 'assets/flicker/b_cut.png'], check=True)


def F(f):
    return f / float(FPS) - .002          # nudged so a tl.set lands ON its frame


LAYERS = ['live', 'alast', 'bfirst', 'bcut', 'blive', 'flash']
WHITE = "brightness(0) invert(1) drop-shadow(0 0 26px rgba(255,255,255,.85))"   # the speaker as a white silhouette


def state(ch, f):
    """which layers show on frame f for letter ch, and whether shot B's speaker is a white silhouette"""
    before = f < CUT
    on = set()
    if ch in 'Aap P':
        on.add('live' if before else 'alast')
    elif ch == 'B':
        on.add('bfirst' if before else 'live')
    elif ch in 'Wx':
        on.add('flash')
    if ch in 'pxP':
        on.add('bcut' if before else 'blive')
    return on, ch == 'P'


def timeline():
    tw = ["gsap.set(%s,{autoAlpha:0});" % json.dumps(['#' + l for l in LAYERS if l != 'live']),
          "gsap.set('#pic',{scale:1,filter:'brightness(1)'});"]
    prev = 'A'
    for i, ch in enumerate(PAT):
        f = F0 + i
        on, white = state(ch, f)
        off_l, on_l = ['#' + l for l in LAYERS if l not in on], ['#' + l for l in LAYERS if l in on]
        if off_l:
            tw.append("tl.set(%s,{autoAlpha:0},%.4f);" % (json.dumps(off_l), F(f)))
        if on_l:
            tw.append("tl.set(%s,{autoAlpha:1},%.4f);" % (json.dumps(on_l), F(f)))
        if HAS_CUT and on & {'bcut', 'blive'}:
            tw.append("tl.set(['#bcut','#blive'],{filter:%s},%.4f);" % (json.dumps(WHITE if white else 'none'), F(f)))
        after_flash = prev in 'Wx' and ch not in 'Wx'
        tw.append("tl.set('#pic',{scale:%.4f,filter:'brightness(%.3f)'},%.4f);"
                  % (PUNCH if after_flash else 1.0, GLOW if after_flash else 1.0, F(f)))
        prev = ch
    # the burst is over: shot B alone, a short settle of the punch
    end = F0 + len(PAT)
    tw += ["tl.set(%s,{autoAlpha:0},%.4f);" % (json.dumps(['#' + l for l in LAYERS if l != 'live']), F(end)),
           "tl.set('#live',{autoAlpha:1},%.4f);" % F(end),
           "tl.set('#pic',{scale:1,filter:'brightness(1)'},%.4f);" % F(end)]
    return tw


def audio():
    if os.environ.get('SFX') == '0' or not os.path.exists('assets/sfx/%s.mp3' % SFX[0]):
        return ''
    t = max(0.0, F0 / float(FPS) - SFX[1])
    d = min(len(PAT) / float(FPS) + .25, DUR - t)
    return ('<audio id="sfx0" src="assets/sfx/%s.mp3" data-start="%.3f" data-duration="%.3f" data-track-index="10" '
            'data-volume="%.3f"></audio>' % (SFX[0], t, d, SFX_VOL * SFX_GAIN))


CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}
#pic{position:absolute;inset:0;transform-origin:50% 46%}
.full{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
#flash{position:absolute;inset:0;background:FLASH;opacity:OPAC}
'''.replace('FLASH', FLASH).replace('OPAC', '%.3f' % FLASH_OPACITY)

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def build():
    stills()
    v = 'muted playsinline data-start="0" data-media-start="0" data-duration="%.3f"' % DUR
    cut = ''
    if HAS_CUT:
        cut = ('<img id="bcut" class="full" src="assets/flicker/b_cut.png" />'
               '<video id="blive" class="full" src="assets/subject.webm" %s data-track-index="1"></video>' % v)
    else:
        cut = '<i id="bcut"></i><i id="blive"></i>'
    nl = '\n'
    return '''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>%(css)s</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%(dur).3f" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="%(dur).3f" data-track-index="2" data-volume="1"></audio>
  %(sfx)s
  <div id="pic">
    <video id="live" class="full" src="assets/aroll.mp4" %(v)s data-track-index="0"></video>
    <img id="alast" class="full" src="assets/flicker/a_last.jpg" />
    <img id="bfirst" class="full" src="assets/flicker/b_first.jpg" />
    <div id="flash"></div>
    %(cut)s
  </div>
%(safe)s
</div>
<script>
const tl = gsap.timeline({ paused: true });
%(tw)s
tl.set({}, {}, %(dur).3f);
window.__timelines["main"] = tl;
</script>
</body>
</html>
''' % {'css': CSS, 'dur': DUR, 'sfx': audio(), 'v': v, 'cut': cut, 'tw': nl.join(timeline()),
       'safe': SAFE_GUIDE if os.environ.get('SAFE') else ''}


if __name__ == '__main__':
    open('index.html', 'w').write(build())
    print('wrote index.html  %s  %d frames (%.3fs)  version %d %s  cut %d  flicker %d..%d (%d frames, %.2fs)  -> renders/%s.mp4'
          % (SLOT, N, DUR, VARIANT, VARIANT_NAMES[VARIANT], CUT, F0, F0 + len(PAT) - 1, len(PAT), len(PAT) / 30.0, SLOT))
    print('  pattern ' + PAT[:AT] + '|' + PAT[AT:] + '   (| = the cut)')
