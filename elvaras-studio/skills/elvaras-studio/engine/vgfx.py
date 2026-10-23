"""Shared machinery for the overlay graphics (Caja de Prompt, Cifra Grande, Fila de Cápsulas, Puntos): transparent
graphics the reel lays over its own footage, so its grade, cuts and live camera stay underneath. Brought over from the
Creator Studio original's Viral Guy effects and rebuilt on Soy Elvaras' brand and the motion rules in
references/motion.md (entrances that overshoot a touch, quicker exits, staggered pieces, nothing ever stands still).
fx_new.py copies this file into every slot whose slot.json lists it in "libs", so a slot needs nothing else.

What it gives a build.py:
  Slot          the slot's facts: frames, seconds, words (slot seconds), where the face is and where graphics may go
  Page          collects html / css / timeline lines / sounds and writes index.html (the slot's own footage under it
                only in SAFE=1 / PREVIEW=1 builds). Motion helpers: enter, leave, drift, press, cursor. Logos: icon
  style_css()   the STYLE block as css rules (.vg-word, .vg-big, .vg-small, .vg-serif)
  Page.glass_css  Vidrio Líquido (engine/glass.py) for a card, when STYLE has glass on: the slot's own footage then goes
                under the graphics and the render is a normal opaque slot (slot.json "layer" becomes "glass")
  T(sec)        a time snapped onto the 30 fps frame grid, 2 ms early so a hard set lands ON that frame

No cutout, no extra Python packages. Placement comes from the reel's layout.json (scripts/layout.py) when the slot
was made inside a reel project; on a loose clip it falls back to the chest band and says so.
"""
import html
import json
import math
import os
import re
import sys

FPS = 30
SAFE_TOP, SAFE_BOTTOM, SAFE_SIDE, SAFE_RIGHT, SAFE_RIGHT_FROM = 220, 1470, 35, 100, 1155
SAFE_MARK = 'rgba(255,0,0,.28)'
SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')
# stock sounds the slot gets from setup: how long each one is worth playing, and how early its hit sits in the file
SFX_LEN = {'click-soft': .25, 'click': .3, 'pop': .4, 'key-press': .2, 'whoosh-short': .8, 'typing': 1.6}
SFX_LEAD = {'click-soft': .01, 'click': .01, 'pop': .118, 'key-press': .01, 'whoosh-short': .12, 'typing': 0}
# the motion rules (references/motion.md) as numbers: entrance, exit (60% of it), hold drift, click press
ENTER, ENTER_EASE = .28, 'back.out(1.6)'
LEAVE, LEAVE_EASE = .16, 'power2.in'
DRIFT = .02
PRESS = .067


def env(name, default='1'):
    return os.environ.get(name, default)


SAFE = env('SAFE', '0') == '1'
SFX_ON = env('SFX', '1') != '0'
# The final build is transparent graphics only: the reel lays it over its own footage (slot.json "layer": "overlay").
# SAFE=1 or PREVIEW=1 puts the slot's footage under it, to judge the snapshots.
PREVIEW = SAFE or env('PREVIEW', '0') == '1'


def T(t):
    return max(0.0, round(t * FPS) / FPS - .002)


def esc(s):
    return html.escape(str(s), quote=False).replace("'", '&rsquo;')


def cased(text, case):
    if case == 'lower':
        return text.lower()
    if case == 'upper':
        return text.upper()
    return text


def bare(s):
    return s.strip().rstrip(',.;:!?¡¿').lstrip('¡¿')


def die(msg):
    """a plain one-line reason the editing Claude can pass on to the user, then stop"""
    print('DECLINED: ' + msg)
    sys.exit(2)


class Slot:
    """Everything this slot knows: run from the slot folder."""

    def __init__(self):
        here = os.getcwd()
        self.clip = _json(os.path.join(here, 'clip.json'), {})
        n = int(self.clip.get('frames') or 0)
        if not n:
            die('clip.json is missing or has no frame count: make the slot with fx_new.py first')
        self.frames, self.dur = n, n / FPS
        ws = _json(os.path.join(here, 'words.json'), [])
        ws = ws.get('words', ws) if isinstance(ws, dict) else ws
        self.words = [dict(w, text=w.get('text', w.get('word', '')).strip()) for w in ws if w.get('text', w.get('word', '')).strip()]
        self.layout, self.layout_from = self._layout()
        head = (self.layout or {}).get('head') or {}
        bands = (self.layout or {}).get('bands') or {}
        self.chin = int(head.get('chin_max') or head.get('chin') or 760)
        self.head_top = int(head.get('top_min') or head.get('top') or 452)
        self.cx = int(head.get('cx') or 540)
        self.chest = int(bands.get('Y_CHEST') or 1170)       # top of a one-line caption over the chest
        self.shot = (self.layout or {}).get('shot') or 'unknown'
        self.t0 = float(self.clip.get('in') or 0)          # reel seconds of the slot's first frame
        # the face in THIS slot's shots: layout.json measures every segment of the reel (punch-ins move the head)
        segs = [g for g in (self.layout or {}).get('segments') or []
                if g.get('t1', 0) > self.t0 + .02 and g.get('t0', 0) < self.t0 + self.dur - .02 and g.get('chin')]
        if segs:
            self.chin = max(int(g['chin']) for g in segs)
            self.head_top = min(int(g.get('head_top') or self.head_top) for g in segs)
            self.cx = int(sum(int(g.get('cx') or self.cx) for g in segs) / len(segs))

    def hide_hint(self, wins):
        """The reel's captions are hidden only while this effect's own words are up: written to
        work/reel_captions.json (slot seconds), which fx_add.py reads by itself."""
        wins = [[round(max(0.0, a), 3), round(min(b, self.dur), 3)] for a, b in wins if b > a]
        os.makedirs('work', exist_ok=True)
        with open(os.path.join('work', 'reel_captions.json'), 'w', encoding='utf-8') as fh:
            json.dump({'hide': wins}, fh)
        print('in a reel: the reel\'s captions are hidden for ' + ', '.join(f'{self.t0 + a:.2f} to {self.t0 + b:.2f}s' for a, b in wins)
              + ' (work/reel_captions.json, fx_add.py applies it)')

    def _layout(self):
        proj = self.clip.get('project')
        for p in ([os.path.join(proj, 'layout.json')] if proj else []) + ['layout.json']:
            if os.path.isfile(p):
                return _json(p, None), p
        return None, None

    def where(self):
        if self.layout_from:
            return f'placement: from {os.path.relpath(self.layout_from)} ({self.shot} shot, chin at y {self.chin}, chest band y {self.chest})'
        return 'placement: no layout.json found, so the chest band default (y 1170) is used: check a SAFE=1 snapshot'

    def band(self, height, prefer=None):
        """centre y for a graphic `height` px tall: on the chest band, never over the chin, never past y 1470.
        A close-up with no room under the chin gets the space above the head instead; None = no room anywhere."""
        if prefer is not None:
            return int(prefer)
        y = max(self.chest + 40, self.chin + 60 + height / 2)
        if y + height / 2 > SAFE_BOTTOM - 6:
            y = SAFE_BOTTOM - 6 - height / 2
        if y - height / 2 >= self.chin + 20:
            return int(y)
        up = self.head_top - 50 - height / 2              # above the head, clear of the top of the safe zone
        if up - height / 2 >= SAFE_TOP + 10:
            print(f'placement: no room under the chin on this clip, so it sits above the head (y {int(up)})')
            return int(up)
        return None

    def word_list(self):
        return ' '.join(f"{w['text']}@{w['start']:.2f}" for w in self.words)

    def find(self, pattern, after=0.0):
        """first word (from `after` seconds on) whose text matches the regex"""
        rx = re.compile(pattern, re.I)
        return next((w for w in self.words if w['start'] >= after - .01 and rx.search(bare(w['text']))), None)


def _json(path, fallback):
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return fallback


def _set_layer(layer):
    """slot.json in the slot folder says how the render goes into the reel: 'overlay' (transparent .webm over the reel's
    footage) or 'glass' (Vidrio Líquido needs the footage in the page, so an opaque .mp4 like any other slot)"""
    meta = _json('slot.json', None)
    if meta and meta.get('layer') in ('overlay', 'glass') and meta['layer'] != layer:
        meta['layer'] = layer
        with open('slot.json', 'w', encoding='utf-8') as fh:
            json.dump(meta, fh, indent=1, ensure_ascii=False)
            fh.write('\n')


def style_css(S):
    """the STYLE block as css: one place where the user's look goes in"""
    shadow = 'text-shadow:0 2px 18px rgba(0,0,0,.38);' if S.get('shadow', True) else ''
    ital = 'italic' if S.get('serif_italic', True) else 'normal'
    return f'''
.vg-word{{font-family:'{S["font"]}';font-weight:{S["weight"]};letter-spacing:{S["tracking"]}em;color:{S["ink"]};{shadow}line-height:1;white-space:nowrap}}
.vg-big{{font-family:'{S.get("big_font") or S["font"]}';font-weight:{S["big_weight"]};letter-spacing:{S["big_tracking"]}em;color:{S.get("accent") or S["ink"]};{shadow}line-height:.86;white-space:nowrap}}
.vg-small{{font-family:'{S["small_font"]}';font-weight:{S["small_weight"]};color:{S["ink"]};{shadow}line-height:1.1;white-space:nowrap}}
.vg-serif{{font-family:'{S["serif_font"]}';font-style:{ital};font-weight:400;color:{S["ink"]};{shadow}line-height:1;white-space:pre}}'''


# the pointer the cursor helper draws: cream with an ink edge, tip at the top left of the box
CURSOR_SVG = ("<svg width='{s}' height='{s}' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'>"
              "<path d='M4 2.5l15.5 9.2-6.7 1.5 3.9 7.1-2.9 1.6-3.9-7.1-4.8 4.9z' fill='{fill}' stroke='{edge}' "
              "stroke-width='1.4' stroke-linejoin='round'/></svg>")


class Page:
    def __init__(self, slot):
        self.s = slot
        self.css, self.html, self.js, self.hidden, self.sfx = [], [], [], [], []
        self.n = 0
        self.icons = _json(os.path.join('assets', 'icons', 'icons.json'), {})
        self.glass = None

    def glass_css(self, key, w, h, radius, dark=True, edge=True):
        """css declarations that turn a w x h card into Vidrio Líquido. dark = tint alpha behind light text (True =
        the default, a number for a card over a bright wall). edge False = keep the card's own border"""
        if self.glass is None:
            sys.path.insert(0, os.getcwd())
            import glass
            self.glass = glass.Glass()
        css = self.glass.card(key, w, h, radius, dark=dark)
        if not edge:
            css = re.sub(r'border:[^;]*;', '', css)
        return css

    def nid(self, p='e'):
        self.n += 1
        return f'{p}{self.n}'

    def show(self, sel, t_in, t_out=None):
        """hard cut in (and out): for a piece inside something that already made its entrance"""
        self.hidden.append(sel)
        self.js.append(f"tl.set('{sel}',{{autoAlpha:1}},{T(t_in):.3f});")
        if t_out is not None and t_out < self.s.dur - .02:
            self.js.append(f"tl.set('{sel}',{{autoAlpha:0}},{T(t_out):.3f});")

    def enter(self, sel, t_in, frm, to, dur=ENTER, ease=ENTER_EASE, t_out=None):
        """an entrance with a touch of overshoot (references/motion.md); t_out = a hard cut out"""
        self.hidden.append(sel)
        self.js.append(f"tl.fromTo('{sel}',{json.dumps(dict(autoAlpha=0, **frm))},"
                       f"{json.dumps(dict(autoAlpha=1, duration=dur, ease=ease, immediateRender=False, **to))},{T(t_in):.3f});")
        if t_out is not None and t_out < self.s.dur - .02:
            self.js.append(f"tl.set('{sel}',{{autoAlpha:0}},{T(t_out):.3f});")

    def leave(self, sel, t_out, dur=LEAVE, y=-12):
        """an exit quicker than the entrance, gone exactly at t_out. An overlay's slot end is usually not a cut of the
        reel (the footage goes on under it), so it leaves there too instead of vanishing"""
        t = max(0.0, T(min(t_out, self.s.dur)) - dur)
        # absolute values only: a relative one renders differently depending on how the renderer seeks (hf lint)
        self.js.append(f"tl.to('{sel}',{{y:{y},autoAlpha:0,duration:{dur},ease:'{LEAVE_EASE}'}},{t:.3f});")

    def drift(self, sel, t0, t1, amount=DRIFT, origin='50% 50%'):
        """the golden rule: something that holds keeps growing a touch until it goes (scale only, so it never fights
        an entrance's y or a leave)"""
        if t1 - t0 < .3 or not amount:
            return
        self.js.append(f"tl.fromTo('{sel}',{{scale:1}},{{scale:{1 + amount:.4f},duration:{t1 - t0:.3f},ease:'sine.inOut',"
                       f"transformOrigin:'{origin}',immediateRender:false}},{T(t0):.3f});")

    def press(self, sel, at, depth=.96):
        """a button that gets clicked sinks a little: 1 -> 0.96 -> 1 in 4 frames"""
        self.js.append(f"tl.to('{sel}',{{scale:{depth},duration:{PRESS},yoyo:true,repeat:1,ease:'power1.inOut'}},{T(at):.3f});")

    def icon(self, name, size, color=None):
        """inline svg of an app's logo from assets/icons (engine/icons + get_icon.py). One-colour logos take `color`
        (None = the brand's own colour); full-colour ones keep theirs. No logo for that app: its initial on a round
        tile, and a line saying so"""
        slug = re.sub(r'[^a-z0-9]', '', (name or '').lower())
        path = os.path.join('assets', 'icons', slug + '.svg')
        meta = self.icons.get(slug, {})
        if not slug or not os.path.isfile(path):
            print(f'logo: none for "{name}" in assets/icons, so its initial stands in (get_icon.py "{name}" fetches a free one)')
            r = int(size * .24)
            return (f'<span style="display:inline-flex;flex:none;align-items:center;justify-content:center;width:{size}px;'
                    f"height:{size}px;border-radius:{r}px;background:{color or '#F2ECDF'};color:#141615;"
                    f"font:800 {int(size * .58)}px 'Work Sans'\">{esc((name or '?').strip()[:1].upper())}</span>")
        with open(path, encoding='utf-8') as fh:
            svg = fh.read()
        svg = re.sub(r'\s(width|height)="[^"]*"', '', svg, count=2)
        fill = f' fill="{color or meta.get("hex") or "#F2ECDF"}"' if meta.get('mono', True) else ''
        return svg.replace('<svg', f'<svg width="{size}" height="{size}"{fill} style="flex:none;display:block"', 1)

    def cursor(self, stops, size=58, fill='#F2ECDF', edge='#141615'):
        """a hand on a mouse: the pointer travels on an arc between stops (x and y on different eases, so the path
        bends), arrives with a small overshoot, holds with a slight drift, and clicks where a stop says so.
          stops  [(x, y, at, click), ...] screen px of the TIP and the slot second it arrives there; the first stop is
                 where it shows up (with a short fade), click True = a press on arrival
        Returns the cursor's id. Put the press of the button it clicks yourself (press()) on the same second."""
        i = self.nid('cur')
        self.css.append(f'\n#{i}{{position:absolute;left:0;top:0;z-index:9;filter:drop-shadow(0 4px 10px rgba(0,0,0,.35))}}')
        self.html.append(f"<div id='{i}'>{CURSOR_SVG.format(s=size, fill=fill, edge=edge)}</div>")
        off = size * 4 / 24                                # the tip sits 4/24 of the box in from its corner
        x0, y0, t0, _ = stops[0]
        self.enter(f'#{i}', t0, {'x': x0 - off, 'y': y0 - off + 18}, {'x': x0 - off, 'y': y0 - off}, .2, 'power2.out')
        for (xa, ya, ta, _), (xb, yb, tb, click) in zip(stops, stops[1:]):
            dist = math.hypot(xb - xa, yb - ya)
            move = min(max(.35, dist / 1300), .8, max(.12, tb - ta - .05))
            start = T(tb - move)
            settle = T(ta) + .2                            # after its entrance (or its last leg's overshoot)
            if start - settle > .3:                        # waiting: a slight hand drift, never frozen
                self.js.append(f"tl.fromTo('#{i}',{{x:{xa - off:.0f},y:{ya - off:.0f}}},{{x:{xa - off + 4:.0f},y:{ya - off + 3:.0f},"
                               f"duration:{start - settle:.3f},ease:'sine.inOut',immediateRender:false}},{settle:.3f});")
            self.js.append(f"tl.to('#{i}',{{x:{xb - off:.0f},duration:{move:.3f},ease:'power2.inOut'}},{start:.3f});")
            self.js.append(f"tl.to('#{i}',{{y:{yb - off:.0f},duration:{move:.3f},ease:'back.out(1.3)'}},{start:.3f});")
            if click:
                self.js.append(f"tl.to('#{i}',{{scale:.86,duration:{PRESS},yoyo:true,repeat:1,ease:'power1.inOut',"
                               f"transformOrigin:'{off:.0f}px {off:.0f}px'}},{T(tb):.3f});")
                self.sound('click-soft', tb, .2)
        return i

    def sound(self, name, at, vol=.35):
        if SFX_ON and os.path.exists(f'assets/sfx/{name}.mp3'):
            self.sfx.append((name, at, vol))

    def write(self, gain=1.0):
        dur = self.s.dur
        audio, lanes = [], []
        for k, (name, hit, vol) in enumerate(sorted(self.sfx, key=lambda x: x[1])):
            t = max(0.0, hit - SFX_LEAD.get(name, 0))
            d = min(SFX_LEN.get(name, .5), dur - t)
            if d < .08:
                continue
            lane = next((i for i, end in enumerate(lanes) if end <= t), None)
            if lane is None:
                lanes.append(0)
                lane = len(lanes) - 1
            lanes[lane] = t + d
            audio.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                         f'data-track-index="{10 + lane}" data-volume="{vol * gain:.3f}"></audio>')
        glassy = self.glass is not None
        _set_layer('glass' if glassy else 'overlay')
        footage = ('' if not (PREVIEW or glassy) else
                   f'<audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{dur:.4f}" data-track-index="2" data-volume="1"></audio>\n'
                   f'  <video id="bgv" class="full" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{dur:.4f}" data-track-index="0"></video>')
        hide = f"gsap.set({json.dumps(sorted(set(self.hidden)))}.join(','),{{autoAlpha:0}});" if self.hidden else ''
        page = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{'#000' if PREVIEW or glassy else 'transparent'}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden}}
.full{{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}}
#fx{{position:absolute;inset:0;z-index:5;pointer-events:none}}
{''.join(self.css)}
</style>
</head>
<body>
{self.glass.defs() if glassy else ''}
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.4f}" data-width="1080" data-height="1920">
  {footage}
  {chr(10).join(audio)}
  <div id="fx">
  {chr(10).join(self.html)}
  </div>
  {SAFE_GUIDE if SAFE else ''}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{hide}
{chr(10).join(self.js)}
tl.set({{}}, {{}}, {dur:.4f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
        with open('index.html', 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(page)
        print(f'index.html written: {self.s.frames} frames ({dur:.2f}s), {len(audio)} sound(s), '
              + ('footage under it, SAFE guide ON (snapshots only)' if SAFE else
                 'Vidrio Líquido: the slot footage under it, so hf render makes an opaque .mp4 (a normal slot, not an overlay)' if glassy else
                 'footage under it (PREVIEW=1, snapshots only)' if PREVIEW
                 else 'transparent graphics only (the final build: hf render makes a .webm the reel lays over its own footage)'))
