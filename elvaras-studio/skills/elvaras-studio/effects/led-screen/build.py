#!/usr/bin/env python3
"""led-screen (Pantalla LED): the picture cuts to a dark LED screen. The words the speaker says light up one at a time
on its grid of red, green and blue dots, with a short flicker as each one comes on, while the camera keeps pushing in
toward the screen until the single sub-pixels fill the frame. Then it cuts back to the speaker, who settles in from a
slightly closer framing, as if the camera came out through the other side.

Drawn frame by frame on a canvas from the reel's one timeline (the renderer seeks it like everything else), so every
frame is exact. Everything on it is real: the words are the speaker's own, on the frame each one is said.

Run from the slot folder (effect.md has the full run order):
    PY build.py      writes index.html   (SAFE=1 safe-zone guide, SFX=0 no sounds)
"""
import json
import os
import re
import sys

# ==== CLIP (edit this) ====
T_IN = 3            # frame the picture cuts to the screen. 2 or later: the slot starts on the plain picture
WORDS = None        # [(frame, 'word'), ...] each lights up on its frame and stays until the next one. None = every word
                    # said between T_IN and T_OUT (words.json of the slot), one at a time. Words the speaker says only
T_OUT = None        # frame it cuts back to the speaker. None = 8 frames before the slot ends
ACCENT = []         # words drawn in dorado instead of the warm white (['claude']). Compared without case or punctuation
CASE = 'lower'      # 'lower' (like the reference), 'upper' or 'as-said'
ZOOM_END = 6.0      # how far the camera has pushed in by T_OUT (1 = no push), most of it on the last word. 5 or
                    # more shows the single sub-pixels. Best with a short last word ("todo", "100%")
PITCH = 9           # px between two LEDs at the start (smaller = finer screen)
SFX_VOL = 1.0
# ==== END CLIP ====

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
LIGHT, DORADO, INK = '#F4EEE2', '#FFAF32', '#0B0C0B'   # dorado on LEDs: pushed warmer so it reads as gold
SETTLE = 7          # frames the speaker takes to settle back from the closer framing
SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')


def F(n):
    return max(0.0, n / FPS - .002)


def bare(s):
    return re.sub(r'^[¡¿"“«(]+|[.,;:!?"”»)…]+$', '', s.strip())


def rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def main():
    clip = json.load(open(os.path.join(HERE, 'clip.json'), encoding='utf-8'))
    nfr = int(clip['frames'])
    dur = nfr / FPS - .001
    t_out = T_OUT if T_OUT is not None else nfr - 8
    words = WORDS
    if words is None:
        try:
            ws = json.load(open(os.path.join(HERE, 'words.json'), encoding='utf-8'))
        except (OSError, ValueError):
            sys.exit('words.json is missing: write WORDS by hand, [(frame, "word"), ...]')
        ws = ws.get('words', ws) if isinstance(ws, dict) else ws
        words = [(int(round(float(w['start']) * FPS)), bare(w.get('text', w.get('word', '')))) for w in ws]
        words = [(f, t) for f, t in words if t and T_IN - 3 <= f < t_out - 2]
        if words and words[0][0] < T_IN:
            words[0] = (T_IN, words[0][1])
    words = sorted((max(int(f), T_IN), str(t)) for f, t in words)
    if T_IN < 2 or t_out > nfr - 2 or t_out - T_IN < 12:
        sys.exit(f'frames: T_IN {T_IN} (2 or later), T_OUT {t_out} (at most {nfr - 2}), and 12 frames or more between them')
    if not words:
        sys.exit('no words between T_IN and T_OUT: set WORDS, or move T_IN / T_OUT')
    shown = [{'f': f, 'text': (t.lower() if CASE == 'lower' else t.upper() if CASE == 'upper' else t),
              'gold': bare(t).lower() in {a.lower() for a in ACCENT}} for f, t in words]

    cfg = {'fps': FPS, 'tin': T_IN, 'tout': t_out, 'zoom': ZOOM_END, 'pitch': PITCH, 'words': shown,
           'light': rgb(LIGHT), 'gold': rgb(DORADO)}
    css = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#vw{{position:absolute;inset:0;transform-origin:540px 760px}}
#vw video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
#scr{{position:absolute;inset:0;z-index:2;background:{INK}}}
#scr canvas{{position:absolute;inset:0;width:1080px;height:1920px}}
#scr:after{{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 80% at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}}
'''
    js = '''
(function(){
const C = %s;
const W = 1080, H = 1920;
const cv = document.getElementById('led'), ctx = cv.getContext('2d');
const glow = document.createElement('canvas'); glow.width = W / 4; glow.height = H / 4;
const gx = glow.getContext('2d');
const cols = Math.ceil(W / C.pitch), rows = Math.ceil(H / C.pitch);
const masks = {};
const last = C.words[C.words.length - 1].f, ZM = Math.min(C.zoom, 2.2);
function clamp(x){ return Math.min(1, Math.max(0, x)); }
function zoomAt(f){
  // a steady push while the words go by (each one still reads whole), then the last word takes the big push
  // through the screen until its single sub-pixels fill the frame
  if (f < last) return 1 + (ZM - 1) * clamp((f - C.tin) / Math.max(1, last - C.tin));
  return ZM * Math.pow(C.zoom / ZM, Math.pow(clamp((f - last) / Math.max(1, C.tout - last)), 1.6));
}
function mask(k){
  if (masks[k]) return masks[k];
  const w = C.words[k];
  const zk = zoomAt(Math.max(w.f, C.tin));                     // each word is drawn to fit the screen as it looks then
  const m = document.createElement('canvas'); m.width = cols; m.height = rows;
  const mc = m.getContext('2d');
  mc.fillStyle = '#fff'; mc.textAlign = 'center'; mc.textBaseline = 'middle';
  let fs = 40; mc.font = `800 ${fs}px "Inter Tight"`;
  const tw = mc.measureText(w.text).width || 1;
  fs = Math.min(40 * cols * 0.80 / zk / tw, rows * 0.17 / zk);
  mc.font = `800 ${fs}px "Inter Tight"`;
  mc.fillText(w.text, cols / 2, rows * 0.46);
  const d = mc.getImageData(0, 0, cols, rows).data, a = new Float32Array(cols * rows);
  for (let i = 0; i < a.length; i++) a[i] = d[i * 4] / 255;
  if (document.fonts && document.fonts.check(`800 20px "Inter Tight"`)) masks[k] = a;   // cache only once the font is in
  return a;
}
function hash(a, b){ let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
function draw(t){
  const f = Math.round(t * C.fps);
  ctx.fillStyle = '#0B0C0B'; ctx.fillRect(0, 0, W, H);
  if (f < C.tin || f >= C.tout) return;
  let k = 0;
  for (let i = 0; i < C.words.length; i++) if (C.words[i].f <= f) k = i;
  const w = C.words[k], since = f - w.f;
  // a short flicker as each word comes on, then steady
  const flick = [0.25, 1.0, 0.55, 1.0][since] ?? 1.0;
  const on = (f - C.tin < 3) ? [0.15, 0.6, 0.35][f - C.tin] : 1.0;
  const p = (f - C.tin) / Math.max(1, C.tout - C.tin);
  const z = zoomAt(f);
  const a = mask(k), col = w.gold ? C.gold : C.light;
  const cell = C.pitch * z, cx = W / 2, cy = H * 0.46;
  const c0 = Math.max(0, Math.floor(cols / 2 - (W / 2) / cell) - 1), c1 = Math.min(cols, Math.ceil(cols / 2 + (W / 2) / cell) + 1);
  const r0 = Math.max(0, Math.floor(rows * 0.46 - cy / cell) - 1), r1 = Math.min(rows, Math.ceil(rows * 0.46 + (H - cy) / cell) + 1);
  const sw = cell / 3 * 0.74, sh = cell * 0.82, gap = cell / 3;
  const R = [255, 60, 52], G = [64, 255, 96], B = [72, 112, 255];
  for (let r = r0; r < r1; r++) {
    const y = cy + (r - rows * 0.46) * cell + cell * 0.09;
    for (let c = c0; c < c1; c++) {
      const x = cx + (c - cols / 2) * cell;
      const v = a[r * cols + c] * flick * on;
      const n = 0.94 + 0.12 * hash(c + f * 7, r);
      const base = 0.075 * on;
      const lr = (base + (col[0] / 255) * v) * n, lg = (base + (col[1] / 255) * v) * n, lb = (base + (col[2] / 255) * v) * n;
      ctx.fillStyle = `rgb(${R[0] * lr | 0},${R[1] * lr | 0},${R[2] * lr | 0})`; ctx.fillRect(x + gap * 0.13, y, sw, sh);
      ctx.fillStyle = `rgb(${G[0] * lg | 0},${G[1] * lg | 0},${G[2] * lg | 0})`; ctx.fillRect(x + gap * 1.13, y, sw, sh);
      ctx.fillStyle = `rgb(${B[0] * lb | 0},${B[1] * lb | 0},${B[2] * lb | 0})`; ctx.fillRect(x + gap * 2.13, y, sw, sh);
    }
  }
  // bloom: the lit dots bleed a soft glow, stronger as the camera gets close
  gx.clearRect(0, 0, glow.width, glow.height);
  gx.filter = `blur(${4 + 6 * p}px)`; gx.drawImage(cv, 0, 0, glow.width, glow.height); gx.filter = 'none';
  ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.55 + 0.25 * p;
  ctx.drawImage(glow, 0, 0, W, H);
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
}
const o = { t: 0 };
tl.fromTo(o, { t: 0 }, { t: %.4f, duration: %.4f, ease: 'none', immediateRender: true, onUpdate: () => draw(o.t) }, 0);
})();
''' % (json.dumps(cfg, ensure_ascii=False), dur, dur)
    t_in, t_back = F(T_IN), F(t_out)
    tw = [f"tl.set('#scr',{{autoAlpha:1}},{t_in:.3f});",
          f"tl.set('#scr',{{autoAlpha:0}},{t_back:.3f});",
          # out through the other side: the speaker comes back a little closer and settles
          f"tl.fromTo('#vw',{{scale:1.12}},{{scale:1,duration:{SETTLE / FPS:.3f},ease:'power3.out',immediateRender:false}},{t_back:.3f});"]
    snd = [('whoosh-short', T_IN - 2, .10)] + [('click-soft', w['f'], .07) for w in shown] + [('whoosh-short', t_out - 3, .10)]
    audio = []
    if SFX_VOL > 0 and os.environ.get('SFX') != '0':
        for j, (name, fr, vol) in enumerate(snd):
            p = f'assets/sfx/{name}.mp3'
            if not os.path.exists(os.path.join(HERE, p)) or fr < 0:
                continue
            audio.append(f'<audio id="sx{j}" src="{p}" data-start="{F(fr):.3f}" data-duration="{min(.6, dur - F(fr)):.3f}" '
                         f'data-track-index="{20 + j}" data-volume="{vol * SFX_VOL * .75:.3f}"></audio>')
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
  <div id="vw"><video id="bgv" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.3f}" data-track-index="0"></video></div>
  <div id="scr"><canvas id="led" width="1080" height="1920"></canvas></div>
  <span style="position:absolute;left:-9999px;font:800 40px 'Inter Tight'">fuente</span>
{SAFE_GUIDE if os.environ.get('SAFE') == '1' else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
gsap.set('#scr', {{autoAlpha: 0}});
{js}
{nl.join(tw)}
tl.set({{}}, {{}}, {dur:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)
    # the screen covers the whole frame and carries the words: the reel's own captions step aside while it is up
    json.dump({'hide': [[round(t_in, 3), round(t_back + SETTLE / FPS, 3)]]}, open(os.path.join(HERE, 'work/reel_captions.json'), 'w'))
    print(f'wrote index.html  {nfr} frames  screen f{T_IN} to f{t_out}, push to {ZOOM_END}x, words: '
          + ', '.join(f'"{w["text"]}" f{w["f"]}' + (' (dorado)' if w['gold'] else '') for w in shown))
    print(f'  reel captions: hidden f{T_IN} to f{t_out + SETTLE} (work/reel_captions.json)')
    snaps = sorted({T_IN + 1, *[w['f'] + 4 for w in shown], t_out - 2, t_out + 2})
    print('snapshot times: ' + ','.join(f'{(f + .5) / FPS:.3f}' for f in snaps if 0 <= f < nfr))
    print(f'render to renders/{os.path.basename(HERE)}.mp4')


if __name__ == '__main__':
    main()
