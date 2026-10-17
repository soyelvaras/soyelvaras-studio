#!/usr/bin/env python3
"""negative-words (Negativo): only the words that matter, huge and in negative, with zooms that follow the face.

Not a caption line: one or two words per idea ("tenemos un 15% de margen en todas nuestras ventas" -> "15%" + "margen"),
in Work Sans 900. Every letter shows the inverse of what is behind it, mapped between two brand colours: over a light
wall the letters go dark (bosque), over something dark they go light (dorado), over the speaker their colours turn over.
A card whose big word fits above the head goes BEHIND the head (the head covers its lower third); the rest go in front,
over the chest. Meanwhile the camera does what Zoom Digital does: creeps, snaps and pulls aimed at the face. The reel's
own captions are hidden while the slot plays.

How the negative is drawn (four copies of every card, each blended with what is under it):
  overlay white      pushes the picture under the letters to its extremes (a mid-tone wall would invert to grey)
  difference white   turns it over
  color  LIGHT       gives the result the hue of the light colour, keeping its brightness
  lighten DARK       lifts the blacks to the dark colour
With COLORS = None only the first two are drawn: a plain black-and-white negative.

Run order, from the slot folder (exact commands in effect.md):
  onsets.py -> edit the CLIP block -> track.py -> build.py -> bake.py -> hyperframes render -> post.py

  SAFE=1    draw the IG safe zone, the eye target and the chin line (snapshots only, never for the render)
  SFX=0     no whoosh
  GRADE=0   no grade / vignette / flash (the main reel grades the slot: use this when the slot sits inside a graded reel)
  HI=0      ignore assets/aroll_hi.mp4 and work from the 1080 a-roll (scale is capped lower)
"""
import hashlib
import html
import json
import math
import os
import shutil
import subprocess
import sys

FPS = 30


def F(n):
    """time of frame n (so the CLIP block can be written in frames)"""
    return n / FPS


def zoom(t_start, t_land, scale, kind, **kw):
    """One camera move, exactly as in Zoom Digital. Times in seconds (use F(frame)), scale relative to the full frame.
    kind 'creep': slow eased move that settles on t_land. 'snap': hard punch on t_land (gets the whoosh).
         'pull' : fast whip, usually back to 1.0. Optional: drift=, over=, sfx=False."""
    return dict(t0=t_start, t1=t_land, scale=scale, kind=kind, **kw)


# ==== CLIP (edit this) ====
# The zooms, in order, timed from onsets.py like Zoom Digital: a creep that lands 2 frames after a vowel, a snap that lands ON
# the stressed vowel (starts 3 frames before), a pull that leaves on a word onset and lands about 9 frames later. Keep them
# gentle (1.1 to 1.3 on a 1080 source): the bigger the zoom, the less room above the head for the words behind it.
ZOOMS = [
    zoom(F(1), F(40), 1.12, 'creep'),
    zoom(F(110), F(119), 1.0, 'pull'),
]
EYE = (540, 700)             # where the eyes sit on screen while the shot is tight
FOLLOW = 5                   # how tightly the camera follows the head (gaussian sigma, frames)
AIM = None                   # manual eye point (frame, x, y) only if work/track_check.jpg shows the cross off the eyes
MAX_UPSCALE = 1.5            # how far past the lossless zoom of the source a scale may go
# The words: only what matters, never the whole sentence. One card per tuple: (last frame on screen or None, words), word =
# (frame it is said, text, 'L' or 's'). One 'L' (the big word) per card; small words before it ride high on its left, small
# words after it sit low on its right. None = the card stays until the next card (or the end of the slot). Write the text in
# lowercase unless it is a name or a number. Frames come from onsets.py. A third value places that card on its own:
# (last, words, 'front') or (last, words, 'behind'); mixing both reads best.
WORDS = [
    (None, [(20, 'margen', 's'), (30, '15%', 'L')]),
]
PLACE = 'auto'               # 'auto' (behind the head when the big word fits above it, else in front), 'behind' or 'front'
COLORS = ('#13281F', '#C9A15B')   # (dark, light): the negative goes from bosque (over light things) to dorado (over dark
                                  # things). None = a plain black-and-white negative
WHOOSH = 0.26                # whoosh volume on each snap (0 = none)
GRADE = 'contrast(1.06) saturate(.93) brightness(.98)'   # grade on the picture (dropped with GRADE=0)
# ==== END CLIP ====


# =====================================================================================================================
# MACHINERY (nothing clip-specific below)
# =====================================================================================================================
HERE = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.basename(HERE)
FP = shutil.which('ffprobe') or 'ffprobe'
ON = {k: os.environ.get(k, '1') != '0' for k in ('SFX', 'GRADE', 'HI')}
SAFE = bool(os.environ.get('SAFE')) and os.environ.get('SAFE') != '0'
SHUTTER = 0.62
BLUR_FROM, BLUR_FULL, BLUR_FLOOR = 28, 95, .1
NMAX = 48
CHIN_K = 0.80                # chin below the eye line, in head widths
EYE_K = 0.78                 # eye line below the top of the head, in head widths (track.py)
DRIFT = {'creep': .022, 'snap': .035, 'pull': 0}
WHOOSH_FILE, WHOOSH_CREST = 'whoosh-short', .16
SFX_GAIN = 0.75
TOP_SAFE = 236               # no glyph above this line (Reels safe zone, with a little air)
NG_FONT = 'WorkSans-100-900-normal.woff2'
NG_ASC, NG_DESC = .93, .243  # Work Sans ascent / descent (em): where the baseline sits in a line-height:1 box


def probe(path, entries):
    return subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', entries, '-of', 'csv=p=0',
                           os.path.join(HERE, path)], capture_output=True, text=True).stdout.strip()


CLIPJ = json.load(open(os.path.join(HERE, 'clip.json'))) if os.path.exists(os.path.join(HERE, 'clip.json')) else {}
NFR = int(CLIPJ.get('frames') or probe('assets/aroll.mp4', 'stream=nb_frames'))
DUR = NFR / FPS
if CLIPJ.get('cut_frames'):
    print(f"!! clip.json lists cuts at {CLIPJ['cut_frames']}: this effect wants one continuous shot (the face track resets at a cut)")
if not os.path.exists(os.path.join(HERE, 'assets/subject.webm')):
    sys.exit('Negativo needs the cutout (assets/subject.webm): make the slot without --no-cutout')
SRC = 'assets/aroll_hi.mp4' if ON['HI'] and os.path.exists(os.path.join(HERE, 'assets/aroll_hi.mp4')) else 'assets/aroll.mp4'
HW, HH = (int(v) for v in probe(SRC, 'stream=width,height').split(',')[:2])
COVER = max(1080 / HW, 1920 / HH)
LOSSLESS = 1 / COVER
OFFX, OFFY = (HW - 1080 / COVER) / 2, (HH - 1920 / COVER) / 2
MAXS = LOSSLESS * MAX_UPSCALE
NOTES = []

# ---------------------------------------------------------------- checks on the CLIP block
if not ZOOMS:
    sys.exit('ZOOMS is empty: add at least one zoom(...) (a slow creep is enough)')
for i, z in enumerate(ZOOMS):
    if z['kind'] not in DRIFT:
        sys.exit(f"zoom {i + 1}: kind must be creep, snap or pull (got {z['kind']!r})")
    if not z['t0'] < z['t1']:
        sys.exit(f'zoom {i + 1}: t_start must be before t_land')
    if i and z['t0'] < ZOOMS[i - 1]['t0']:
        sys.exit(f'zoom {i + 1} starts before zoom {i}: list them in order')
    if z['t1'] > DUR + 1e-6:
        sys.exit(f"zoom {i + 1} lands at frame {z['t1'] * FPS:.0f} but the clip has {NFR} frames: edit the CLIP block for this clip")
    if z['scale'] < 1:
        sys.exit(f'zoom {i + 1}: scale below 1.0 would show the edge of the picture')
    peak = z['scale'] * (1 + z.get('over', .04)) if z['kind'] == 'snap' else z['scale']
    if peak > MAXS + 1e-6:
        new = round(MAXS / (peak / z['scale']), 3)
        NOTES.append(f"zoom {i + 1}: {z['scale']}x capped to {new}x (source {HW}x{HH} is lossless to {LOSSLESS:.2f}x)")
        z['scale'] = max(1.0, new)
if not WORDS:
    sys.exit('WORDS is empty: write the cards (only the words that matter)')
if PLACE not in ('auto', 'behind', 'front'):
    sys.exit("PLACE must be 'auto', 'behind' or 'front'")
T_LAST = F(NFR - 1)


# ---------------------------------------------------------------- scale curve (as in Zoom Digital)
def _creep(u, k=.74):
    u = min(1, max(0, u))
    return u * u / k if u < k else 1 - (1 - u) ** 2 / (1 - k)


def _snap(u):
    return min(1, max(0, u)) ** 1.5


def _pull(u):
    u = min(1, max(0, u)) ** 1.2
    return 1 - (1 - u) ** 3.6


def _smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def _drift(z, dt, tau=.25):
    rate = z.get('drift', DRIFT[z['kind']]) if z['scale'] > 1.001 else 0
    return rate * (dt - tau * (1 - math.exp(-dt / tau))) if dt > 0 else 0


def _seg(z, ls_from, t, last):
    t0, t1, tgt = z['t0'], z['t1'], math.log(z['scale'])
    u, dt = (t - t0) / (t1 - t0), t - t1
    way = 1 if tgt >= ls_from else -1
    if z['kind'] == 'creep':
        return ls_from + (tgt - ls_from) * _creep(u) + _drift(z, dt)
    if z['kind'] == 'snap':
        over = way * math.log(1 + z.get('over', .04))
        if u < 1:
            return ls_from + (tgt + over - ls_from) * _snap(u)
        return tgt + over * math.exp(-dt / (2.2 / FPS)) + _drift(z, dt)
    settle = -way * math.log(1 + z.get('over', .028))
    if u < 1:
        return ls_from + (tgt + settle - ls_from) * _pull(u)
    fade = 1 - _smooth(dt / max(1e-6, T_LAST - t1)) if last else 1
    return tgt + settle * math.exp(-dt / .22) * fade + _drift(z, dt)


def scale_at(t):
    ls = 0.0
    for i, z in enumerate(ZOOMS):
        if t < z['t0']:
            break
        nxt = ZOOMS[i + 1]['t0'] if i + 1 < len(ZOOMS) else None
        if nxt is not None and t >= nxt:
            ls = _seg(z, ls, nxt, False)
            continue
        ls = _seg(z, ls, t, nxt is None)
        break
    return min(MAXS, max(1.0, math.exp(ls)))


# ---------------------------------------------------------------- head track -> smooth face path
def _gauss(vals, sigma):
    r = max(1, int(3 * sigma))
    ker = [math.exp(-.5 * (k / max(sigma, 1e-3)) ** 2) for k in range(-r, r + 1)]
    out = []
    for i in range(len(vals)):
        acc = w = 0
        for k in range(-r, r + 1):
            j = min(len(vals) - 1, max(0, i + k))
            acc += ker[k + r] * vals[j]; w += ker[k + r]
        out.append(acc / w)
    return out


def _median(vals, r=2):
    return [sorted(vals[max(0, i - r):i + r + 1])[len(vals[max(0, i - r):i + r + 1]) // 2] for i in range(len(vals))]


HT_PATH = os.path.join(HERE, 'work/headtrack.json')
if not os.path.exists(HT_PATH):
    sys.exit('work/headtrack.json is missing: run track.py first')
HT = json.load(open(HT_PATH))
if HT['frames'] != NFR:
    sys.exit(f"head track has {HT['frames']} frames, the clip has {NFR}: run track.py again")
if (HT.get('aim') or None) != (list(AIM) if AIM else None):
    sys.exit('AIM changed since the last track: run track.py again')
HEAD_W = HT['head_w']
FX = _gauss(_median([o['eye_x'] for o in HT['track']]), FOLLOW)
FY = _gauss(_median([o['eye_y'] for o in HT['track']]), FOLLOW)


def face_at(t):
    x = min(NFR - 1, max(0, t * FPS))
    i = min(NFR - 2, int(x)); a = x - i
    return FX[i] * (1 - a) + FX[i + 1] * a, FY[i] * (1 - a) + FY[i + 1] * a


def _reach(eye, face, size):
    return (size - eye) / max(1, size - face) if eye < face else eye / max(1, face)


_MX, _MY = sorted(FX)[len(FX) // 2], sorted(FY)[len(FY) // 2]
S_REACH = max(_reach(EYE[0], _MX, 1080), _reach(EYE[1], _MY, 1920))
AIM_RANGE = min(.35, max(.12, 1.25 * (S_REACH - 1)))


def camera_at(t):
    s = scale_at(t)
    fx, fy = face_at(t)
    w = _smooth((s - 1) / AIM_RANGE)
    ex, ey = fx + (EYE[0] - fx) * w, fy + (EYE[1] - fy) * w
    left = min(1080 - 1080 / s, max(0, fx - ex / s))
    top = min(1920 - 1920 / s, max(0, fy - ey / s))
    return s, left, top, (fx - left) * s, (fy - top) * s


def solve():
    frames = []
    for f in range(NFR):
        t = F(f)
        s, l, tp, ex, ey = camera_at(t)

        def travel(dt):
            s2, l2, t2, _, _ = camera_at(t + dt)
            return max(math.hypot((l + cx / s - l2) * s2 - cx, (tp + cy / s - t2) * s2 - cy)
                       for cx, cy in ((0, 0), (1080, 0), (0, 1920), (1080, 1920)))

        speed = travel(1 / FPS)
        shutter = SHUTTER * min(1, max(BLUR_FLOOR, (speed - BLUR_FROM) / (BLUR_FULL - BLUR_FROM)))
        d = travel(shutter / FPS)
        n = min(NMAX, max(1, math.ceil(d / 2.2)))
        boxes = []
        for j in range(n):
            sj, lj, tj, _, _ = camera_at(t + shutter / FPS * j / n)
            boxes.append([round(OFFX + lj / COVER, 3), round(OFFY + tj / COVER, 3),
                          round(OFFX + (lj + 1080 / sj) / COVER, 3), round(OFFY + (tj + 1920 / sj) / COVER, 3)])
        frames.append({'f': f, 'scale': round(s, 5), 'eye': [round(ex, 1), round(ey, 1)], 'blur_px': round(d, 1), 'boxes': boxes,
                       'chin': round(ey + CHIN_K * HEAD_W * s, 1), 'head': round(ey - EYE_K * HEAD_W * s, 1)})
    return frames


CAM = solve()
os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)


def alpha_tops():
    """the real top of the head (hair included) in every frame, read from the cutout inside a column around the eyes, then
    put through that frame's crop: the eye estimate alone misses tall or curly hair"""
    k, aw, ah = 4, 270, 480
    ff = shutil.which('ffmpeg') or 'ffmpeg'
    raw = subprocess.run([ff, '-v', 'error', '-c:v', 'libvpx-vp9', '-i', os.path.join(HERE, 'assets/subject.webm'), '-vf',
                          f'alphaextract,scale={aw}:{ah}:flags=area,format=gray', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                         capture_output=True).stdout
    n = len(raw) // (aw * ah)
    found = 0
    for f in range(min(n, NFR)):
        frame = raw[f * aw * ah:(f + 1) * aw * ah]
        ex = HT['track'][f]['eye_x']
        c0, c1 = max(0, int((ex - .35 * HEAD_W) / k)), min(aw, int((ex + .35 * HEAD_W) / k) + 1)
        top = next((r for r in range(ah) if max(frame[r * aw + c0:r * aw + c1] or bytes(1)) > 128), None)
        if top is None:
            continue
        c = CAM[f]
        crop_top = (c['boxes'][0][1] - OFFY) * COVER
        c['head'] = round((top * k - crop_top) * c['scale'], 1)
        found += 1
    return found


HEAD_FROM_ALPHA = alpha_tops()
CUT_WIN = [0, NFR - 1]           # bake.py makes assets/zoom_cut.webm (the speaker alone, through the same crop) for every frame
CUT_SIG = hashlib.md5(json.dumps([CUT_WIN, [c['boxes'] for c in CAM]]).encode()).hexdigest()[:12]
json.dump({'name': NAME, 'src': SRC, 'w': 1080, 'h': 1920, 'fps': FPS, 'lossless': LOSSLESS, 'cover': COVER, 'offx': OFFX,
           'offy': OFFY, 'half': CUT_WIN, 'half_sig': CUT_SIG, 'frames': CAM}, open(os.path.join(HERE, 'work/camera.json'), 'w'))


# ---------------------------------------------------------------- the words
_fonts = {}


def ng_font(weight, px):
    from PIL import ImageFont
    key = (weight, int(px))
    if key not in _fonts:
        f = ImageFont.truetype(os.path.join(HERE, 'assets/fonts', NG_FONT), int(px))
        f.set_variation_by_axes([weight])
        _fonts[key] = f
    return _fonts[key]


def ng_len(text, px, track):
    """px width of text in Work Sans 900 with this tracking (em); a rough table when the font cannot be read"""
    try:
        return ng_font(900, px).getlength(text) + track * px * len(text)
    except Exception:
        return (.58 + track) * px * len(text)


def ng_height(text):
    """height of the glyphs above the baseline, in em (an x-height word is low, a word with an l, d, digit or capital is tall)"""
    try:
        return -ng_font(900, 1000).getbbox(text, anchor='ls')[1] / 1000
    except Exception:
        return .72 if any(c in text for c in 'bdfhklt0123456789%') or text[:1].isupper() else .52


def T(frame, lead=1.4):
    """tween start so the word is already half formed ON its frame"""
    return max(0, (frame - lead) / FPS)


def cards():
    """-> list of dicts: the layout of every card (size, baseline, where it goes) and a report"""
    out, rep = [], []
    starts = [min(fr for fr, _, _ in item[1]) for item in WORDS]
    for n, item in enumerate(WORDS):
        last, ws = item[0], sorted(item[1], key=lambda w: w[0])
        place = item[2] if len(item) > 2 else PLACE
        if place not in ('auto', 'behind', 'front'):
            sys.exit(f"card {n + 1}: place must be 'auto', 'behind' or 'front' (got {place!r})")
        big = next((k for k, w in enumerate(ws) if w[2] == 'L'), 0)
        f0 = starts[n]
        f1 = (starts[n + 1] - 1 if n + 1 < len(WORDS) else NFR - 1) if last is None else min(int(last), NFR - 1)
        if f0 < 0 or f0 >= NFR or f1 <= f0:
            sys.exit(f'card {n + 1}: frames {f0}-{f1} are outside the slot (0 to {NFR - 1}) or end before they start')
        text = [w[1] for w in ws]
        gh = ng_height(text[big])
        span = CAM[f0:f1 + 1]
        head_hi = min(c['head'] for c in span)           # the highest the head gets while the card is up
        head_mid = sorted(c['head'] for c in span)[len(span) // 2]
        chin_lo = max(c['chin'] for c in span)

        def fit(cap):
            for px in range(int(cap), 59, -4):
                s = max(56, round(px * .34))
                w = ng_len(text[big], px, -.05) + sum(ng_len(t, s, -.03) + .52 * s for k, t in enumerate(text) if k != big)
                if w <= 960:
                    return px, s
            return 60, 56

        room = (head_hi - TOP_SAFE) / (.7 * gh)
        behind = place == 'behind' or (place == 'auto' and room >= 150)
        if behind:
            px, s = fit(max(60, min(340, room)))
            base = max(head_mid + .30 * gh * px, TOP_SAFE + gh * px)          # the head covers its lower third
            if big:                                                          # raised small words stay under the safe line
                base = max(base, TOP_SAFE + .58 * gh * px + .74 * s)
            where = 'behind'
        else:
            px, s = fit(230)
            base = chin_lo + 60 + max(gh * px, .58 * gh * px + .74 * s if big else 0)     # the whole card clears the chin
            where = 'front'
        low = base + NG_DESC * px * .6
        top = base - (1 - NG_ASC - NG_DESC) / 2 * px - NG_ASC * px
        line = (f'card {n + 1} (f{f0}-{f1}) {where:6} "{" ".join(text)}"  big {px}px, small {s}px, glyph top '
                f'{base - gh * px:.0f}, baseline {base:.0f}')
        if behind and room < 150:
            line += f'  !! little room above the head ({room:.0f}px of size): the word is small, try PLACE = "front" or less zoom'
        if not behind and low > 1450:
            line += f'  !! runs to y {low:.0f}, past the safe line: zoom in less, or fewer / shorter words'
        rep.append(line)
        out.append(dict(ws=ws, big=big, px=px, s=s, gh=gh, top=top, behind=behind, f0=f0, f1=f1))
    return out, rep


CARDS, CARD_REP = cards()
LAYERS = ('u', 'd', 'c', 'l') if COLORS else ('u', 'd')


def words_html():
    """-> (html behind the speaker, html in front, tweens)"""
    back, front, tw = [], [], []
    for n, c in enumerate(CARDS):
        gid = f'g{n}'
        parts = []
        for j, (fr, txt, _) in enumerate(c['ws']):
            wid = f'{gid}w{j}'
            sel = ','.join(f'#{wid}{x}' for x in LAYERS)
            if j == c['big']:
                parts.append((wid, 'L', f'font-size:{c["px"]}px', txt))
                tw += [f"gsap.set('{sel}',{{autoAlpha:0}});",
                       f"tl.fromTo('{sel}',{{autoAlpha:0,scale:1.2,filter:'blur(18px)'}},{{autoAlpha:1,scale:1,filter:'blur(0px)',"
                       f"duration:.2,ease:'power3.out',immediateRender:false}},{T(fr):.3f});"]
            else:
                dy = -.58 * c['gh'] * c['px'] if j < c['big'] else .1 * c['px']
                parts.append((wid, 's', f'font-size:{c["s"]}px;top:{dy:.0f}px', txt))
                tw += [f"gsap.set('{sel}',{{autoAlpha:0}});",
                       f"tl.fromTo('{sel}',{{autoAlpha:0,y:12,filter:'blur(10px)'}},{{autoAlpha:1,y:0,filter:'blur(0px)',"
                       f"duration:.16,ease:'power3.out',immediateRender:false}},{T(fr):.3f});"]
        for x in LAYERS:
            body = ''.join(f'<span id="{i}{x}" class="{k}" style="{st}">{html.escape(t)}</span>' for i, k, st, t in parts)
            (back if c['behind'] else front).append(f'<div id="{gid}{x}" class="ng {x}" style="top:{c["top"]:.0f}px">{body}</div>')
        gsel = ','.join(f'#{gid}{x}' for x in LAYERS)
        if c['f1'] < NFR - 1:
            tw += [f"tl.to('{gsel}',{{autoAlpha:0,duration:.1}},{max(0, F(c['f1']) - .1):.3f});",
                   f"tl.set('{gsel}',{{autoAlpha:0}},{F(c['f1']) - .002:.3f});"]
    return back, front, tw


# ---------------------------------------------------------------- look: vignette breathes with the zoom
def look():
    smax = max(1.02, max(c['scale'] for c in CAM))

    def vig(c):
        return .25 + .75 * math.log(c['scale']) / math.log(smax)

    kf = ','.join(f"{{opacity:{vig(c):.3f},duration:{1 / FPS:.5f},ease:'none'}}" for c in CAM[1:])
    tw = [f"gsap.set('#vigin',{{opacity:{vig(CAM[0]):.3f}}});", f"tl.to('#vigin',{{keyframes:[{kf}]}},0);", "gsap.set('#flash',{opacity:0});"]
    for z in ZOOMS:
        if z['kind'] == 'snap':
            tw += [f"tl.to('#flash',{{opacity:.16,duration:{1 / FPS - .003:.4f},ease:'none'}},{z['t1'] - 1 / FPS:.4f});",
                   f"tl.to('#flash',{{opacity:0,duration:.3,ease:'power2.out'}},{z['t1']:.4f});"]
    return tw


def audio():
    wav = os.path.join(HERE, f'assets/sfx/{WHOOSH_FILE}.mp3')
    if not (ON['SFX'] and WHOOSH and os.path.exists(wav)):
        return []
    length = float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav],
                                  capture_output=True, text=True).stdout)
    out = []
    for k, z in enumerate(z for z in ZOOMS if z['kind'] == 'snap' and z.get('sfx', True)):
        t = z['t1'] - .5 / FPS - WHOOSH_CREST
        skip = max(0, -t)
        t = max(0, t)
        d = min(length - skip, DUR - t)
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{WHOOSH_FILE}.mp3" data-start="{t:.3f}" data-media-start="{skip:.3f}" '
                   f'data-duration="{d:.3f}" data-track-index="{10 + k}" data-volume="{WHOOSH * SFX_GAIN:.3f}"></audio>')
    return out


GRADE_CSS = f'filter:{GRADE};' if ON['GRADE'] and GRADE else ''
DARK, LIGHT = COLORS if COLORS else ('#000', '#fff')
# No z-index and no transform on anything that holds the words: each copy has to blend with the picture under it
CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
.vid{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;{GRADE_CSS}}}
.fx{{position:absolute;inset:0;pointer-events:none}}
#tone{{z-index:2;background:linear-gradient(180deg,rgba(20,55,75,.14),rgba(60,40,20,.07));mix-blend-mode:soft-light}}
#vig{{z-index:2;background:radial-gradient(95% 62% at 50% 44%,rgba(0,0,0,0) 58%,rgba(0,0,0,.26) 100%)}}
#vigin{{z-index:2;background:radial-gradient(80% 54% at 50% 36%,rgba(0,0,0,0) 50%,rgba(0,0,0,.30) 100%),
  linear-gradient(180deg,rgba(0,0,0,0) 52%,rgba(0,0,0,.16) 80%,rgba(0,0,0,.20) 100%)}}
#flash{{z-index:3;background:#F2ECDF;mix-blend-mode:soft-light}}
.ng{{position:absolute;left:0;width:1080px;text-align:center;white-space:nowrap;line-height:1;font-family:'Work Sans';font-weight:900}}
.ng span{{display:inline-block;position:relative;transform-origin:50% 75%}}
.ng .L{{letter-spacing:-.05em}}
.ng .s{{letter-spacing:-.03em;margin:0 .26em}}
.ng.u{{color:#FFFFFF;mix-blend-mode:overlay}}
.ng.d{{color:#FFFFFF;mix-blend-mode:difference}}
.ng.c{{color:{LIGHT};mix-blend-mode:color}}
.ng.l{{color:{DARK};mix-blend-mode:lighten}}
'''

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div>'
              '<div id="dbgeye" style="position:absolute;left:0;top:0;width:60px;height:2px;margin:-1px 0 0 -30px;background:#0ff"></div>'
              '<div id="dbgchin" style="position:absolute;left:340px;top:0;width:400px;height:2px;background:#0f0"></div></div>')


def debug_tw():
    kf_e = ','.join(f"{{x:{c['eye'][0]},y:{c['eye'][1]},duration:{1 / FPS:.5f},ease:'none'}}" for c in CAM[1:])
    kf_c = ','.join(f"{{y:{c['chin']},duration:{1 / FPS:.5f},ease:'none'}}" for c in CAM[1:])
    return [f"gsap.set('#dbgeye',{{x:{CAM[0]['eye'][0]},y:{CAM[0]['eye'][1]}}});", f"tl.to('#dbgeye',{{keyframes:[{kf_e}]}},0);",
            f"gsap.set('#dbgchin',{{y:{CAM[0]['chin']}}});", f"tl.to('#dbgchin',{{keyframes:[{kf_c}]}},0);"]


def build():
    back, front, w_tw = words_html()
    tweens = (look() if ON['GRADE'] else []) + w_tw + (debug_tw() if SAFE else [])
    grade = ('<div id="tone" class="fx"></div><div id="vig" class="fx"></div><div id="vigin" class="fx"></div>'
             '<div id="flash" class="fx"></div>') if ON['GRADE'] else ''
    v = f'muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}"'
    nl = '\n  '
    return f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="2" data-volume="1"></audio>
  {nl.join(audio())}
  <video id="bgv" class="vid" src="assets/zoom.mp4" {v} data-track-index="0"></video>
  {nl.join(back)}
  <video id="cutv" class="vid" src="assets/zoom_cut.webm" {v} data-track-index="1"></video>
  {nl.join(front)}
  {grade}
{SAFE_GUIDE if SAFE else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''


open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(build())

# frames worth looking at in the final render (post.py reads this)
marks, stills = {0, NFR - 1}, []
for z in ZOOMS:
    a, b = round(z['t0'] * FPS), round(z['t1'] * FPS)
    marks |= {max(0, a - 1), a, min(NFR - 1, b), min(NFR - 1, b + 1)}
for c in CARDS:
    marks |= {min(NFR - 1, fr + 3) for fr, _, _ in c['ws']}
    stills.append(min(NFR - 1, max(fr for fr, _, _ in c['ws']) + 6))
stills = list(dict.fromkeys(stills + sorted(marks)))
json.dump({'name': NAME, 'frames': NFR, 'marks': sorted(marks), 'stills': stills[:3]}, open(os.path.join(HERE, 'work/marks.json'), 'w'))

print(f'wrote index.html + work/camera.json   slot "{NAME}"  {NFR} frames  head width {HEAD_W:.0f}px')
print(f'  picture: {SRC} {HW}x{HH}  lossless to {LOSSLESS:.2f}x, scale capped at {MAXS:.2f}x'
      + ('' if SRC.endswith('_hi.mp4') else '   (no aroll_hi: 1080 source, every zoom is an upscale, keep them modest)'))
for nline in NOTES:
    print('  !! ' + nline)
print(f'  colours: ' + (f'negative from {DARK} (over light) to {LIGHT} (over dark)' if COLORS else 'plain black-and-white negative'))
print(f'  head top: read from the cutout in {HEAD_FROM_ALPHA} of {NFR} frames' + ('' if HEAD_FROM_ALPHA > NFR * .8 else
      '  !! the cutout lost the head in many frames: the eye estimate stands in, look hard at the words behind the head'))
for line in CARD_REP:
    print('  ' + line)
print("  reel captions: hidden for the whole slot (slot.json says hide): the cards carry the words that matter")
_sig = os.path.join(HERE, 'work/zoom_cut.sig')
if not os.path.exists(os.path.join(HERE, 'assets/zoom_cut.webm')) or not os.path.exists(_sig) or open(_sig).read().strip() != CUT_SIG:
    print('  !! assets/zoom.mp4 / zoom_cut.webm are missing or were baked for another camera: run bake.py')
print('next: bake.py (needed after any change to ZOOMS / EYE / FOLLOW / AIM / HI; not for WORDS, PLACE, COLORS, grade or sound)')
