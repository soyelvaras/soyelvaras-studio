#!/usr/bin/env python3
"""Trial reels: several clearly different versions of one approved reel for Instagram's trial reels (shown first to
people who don't follow the account). Each version gets its OWN opening hook, its own speed, its own zoom rhythm and
framing, its own light colour, and its own caption style when the reel was built by build_reel.py. Guide:
references/trials.md.

Usage (run with PY):
  PY trials.py plan   "<project>" --base renders/<slug>-vN.mp4 [--count 5] [--colors] [--fresh]
                      proposes the versions -> <project>/trials.json, and prints them
  PY trials.py make   "<project>"       builds what each version needs (its composition, its opener slot). CHECK = by hand
  PY trials.py render "<project>" [--only N] [--redo]     IN THE BACKGROUND: one after another, never two at once
  PY trials.py list   "<project>"       what each file changes
  PY trials.py posted "<project>" N [--undo]              version N went out: it is never made or rendered again

What a version changes, and what it costs:
  hook      always different from the reel and from every other version, by turns:
              titular  a headline over the opening, written for that version (2 to 7 words from what the reel says).
                       Only the opening is rendered (render_window.py -c) and spliced into the approved render
              led      the opening line lit up word by word on Pantalla LED (effects/led-screen), made from the reel's
                       own words and spliced over the opening of the approved render
  captions  another caption style (built-in key): the whole reel is rendered again (~15 min). Only on a reel built by
            build_reel.py; a reel built with the project's own scripts (Página y Tarjeta) keeps its captions
  colors    with --colors, every other version also swaps the brand's gold accent in the composition (whole render)
  speed     0.95 to 1.12, a different one per version, never 1.0 (voice pitch kept)
  zooms     a zoom rhythm on the reel's own cuts (golpes: a punch on each cut / empuje: a slow push through each shot /
            alterno: every other shot tighter, like a jump cut / respira: a slow in and out), over a framing 3-5% tighter
            with a small side shift. Captions and graphics move with the picture (at most ~10%, inside the safe zone)
  look      a light grade (cálido, frío, claro, contraste, suave)
speed, zooms and look are done with ffmpeg on the finished file, so they work on any reel.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skillenv  # noqa: E402
import fxlib  # noqa: E402

FF, FP = skillenv.tool('ffmpeg'), skillenv.tool('ffprobe')
PY = sys.executable
FPS = 30
BRAND_ACCENT = '#C9A15B'
CAPTION_ORDER = ['karaoke', 'loud-lowercase', 'golden-hour', 'keyword', 'outline', 'anchor', 'arcade', 'low-key']
CAPTION_NAMES = {'karaoke': 'Karaoke', 'loud-lowercase': 'Minúscula Gigante', 'golden-hour': 'Hora Dorada',
                 'keyword': 'Palabra Clave', 'outline': 'Contorno', 'anchor': 'Noticiero', 'arcade': 'Arcade',
                 'low-key': 'Discreto'}
ACCENTS = [('#8FB9A8', 'salvia'), ('#F2ECDF', 'crema'), ('#B9C7E4', 'azul niebla'), ('#D8B4A0', 'arcilla')]
HOOKS = ['titular', 'led']
# no two versions share a speed or a framing, and none is the reel itself
SPEEDS = [1.06, 1.10, 0.97, 1.03, 1.12, 0.95, 1.08, 1.04, 0.98, 1.05]
ZOOMS = [1.04, 1.03, 1.05, 1.035, 1.045, 1.032, 1.048, 1.038, 1.042, 1.034]
SHIFTS = [-18, 16, -8, 22, 10, -24, 4, -14, 20, -4]
RHYTHMS = ['golpes', 'empuje', 'alterno', 'respira']
RHYTHM_NAMES = {'golpes': 'un golpe de zoom en cada corte', 'empuje': 'empuje lento en cada toma',
                'alterno': 'una toma sí y otra no más cerca', 'respira': 'zoom que entra y sale lento'}
LOOKS = {
    'calido': 'colorbalance=rm=.025:gm=.005:bm=-.025,eq=saturation=1.04',
    'frio': 'colorbalance=rm=-.02:bm=.025,eq=saturation=.98',
    'claro': 'eq=brightness=.018:contrast=1.02',
    'contraste': 'eq=contrast=1.05:saturation=1.03',
    'suave': 'eq=contrast=.97:brightness=.01:saturation=.97',
}
LOOK_NAMES = {'calido': 'cálido', 'frio': 'frío', 'claro': 'claro', 'contraste': 'contraste', 'suave': 'suave'}
LOOK_ORDER = list(LOOKS)
ZOOM_MAX = 1.10          # framing x rhythm: past this the lowest captions would leave the safe zone


def read(p, fb=None):
    try:
        with open(p, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return fb


def write(p, data):
    with open(p, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write('\n')


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        return args[i + 1] if i + 1 < len(args) else default
    return default


def rebuild_check(proj):
    """Can a version with another caption style be rebuilt with build_reel.py without losing anything?
    -> ('same' | 'older' | 'custom', extra build_reel flags). It builds the reel again into trials/00-check.html, with
    the picks it was built with (work/build.json), with and without the user's own style:
      same    one of them gives back index.html exactly
      older   it differs only in what the engine does since (the live camera...): a rebuilt version carries that too
      custom  index.html has pieces build_reel.py does not make (a reel finished with the project's own scripts, like
              Página y Tarjeta): its captions are never rebuilt, they would lose the look"""
    built = read(os.path.join(proj, 'work', 'build.json'), None)
    ix = os.path.join(proj, 'index.html')
    if not built or not os.path.isfile(ix):
        return 'custom', []
    os.makedirs(os.path.join(proj, 'trials'), exist_ok=True)
    plan_slots = (read(os.path.join(proj, 'plan.json'), {}) or {}).get('slots') or []
    write(os.path.join(proj, 'trials', 'picks.json'),
          {'mode': 'preset' if built.get('style') else 'custom', 'style': built.get('style'),
           'captionStyle': built.get('caption') if built.get('caption') not in (None, 'custom') else 'none',
           'effects': sorted({s['key'] for s in plan_slots if s.get('key')}), 'effectSections': None})
    pk = ['--picks', os.path.join(proj, 'trials', 'picks.json')]
    cap = built.get('caption')
    capf = ['--caption', cap] if cap and cap != 'custom' else []
    approved = open(ix, encoding='utf-8').read()
    ids = set(re.findall(r'\bid="([^"]+)"', approved))
    best = None
    for extra in ([], ['--no-my-style']):
        r = subprocess.run([PY, os.path.join(HERE, 'build_reel.py'), proj, '--out', 'trials/00-check.html'] + pk + capf
                           + extra, **skillenv.TEXT)
        if r.returncode:
            continue
        got = open(os.path.join(proj, 'trials', '00-check.html'), encoding='utf-8').read()
        if got == approved:
            return 'same', pk + extra
        missing = len(ids - set(re.findall(r'\bid="([^"]+)"', got)))
        if best is None or missing < best[0]:
            best = (missing, pk + extra)
    if best is None or best[0] > 2:
        return 'custom', []
    return 'older', best[1]


def probe(f):
    r = json.loads(subprocess.run([FP, '-v', 'error', '-count_frames', '-show_entries', 'stream=codec_type,nb_read_frames',
                                   '-of', 'json', f], **skillenv.TEXT).stdout or '{}')
    v = next((x for x in r.get('streams', []) if x['codec_type'] == 'video'), {})
    return int(v.get('nb_read_frames') or 0)


def hook_end(proj):
    try:
        where, _ = fxlib.reel_parts(proj)
        return round(float(where['hook'][1]), 2)
    except Exception:          # no words.json or no parts: the first three seconds
        return 3.0


def current_caption(proj):
    return (read(os.path.join(proj, 'work', 'build.json'), {}) or {}).get('caption')


def describe(t):
    h = t['hook']
    parts = [f'Gancho: titular «{h.get("headline") or "(escríbelo)"}»' if h['kind'] == 'titular'
             else 'Gancho: la primera frase en Pantalla LED']
    if t.get('caption'):
        parts.append(f'subtítulos {CAPTION_NAMES.get(t["caption"], t["caption"])}')
    if t.get('accent'):
        parts.append(f'dorado → {t["accent"]}')
    parts.append(f'{t["speed"]:.2f}x · {RHYTHM_NAMES[t["zoom"]["rhythm"]]} · color {LOOK_NAMES[t["look"]]}')
    return ' · '.join(parts)


# ---------------------------------------------------------------- plan
def plan(proj, args):
    old = read(os.path.join(proj, 'trials.json'), {}) or {}
    base = opt(args, '--base') or old.get('base')
    if not base or not os.path.isfile(os.path.join(proj, base)):
        sys.exit('STATUS trials FAILED: --base renders/<slug>-vN.mp4, the approved render (relative to the project)')
    if old.get('trials') and '--fresh' not in args:
        sys.exit('STATUS trials FAILED: trials.json already has a plan. --fresh makes a new one (posted versions stay)')
    count = int(opt(args, '--count', '5'))
    engine, flags = rebuild_check(proj)
    posted = [t for t in old.get('trials', []) if t.get('posted') and old.get('version') == 2]
    if '--fresh' in args and os.path.isdir(os.path.join(proj, 'trial-reels')):
        keep = {t['file'] for t in posted if t.get('file')}
        dst = os.path.join(proj, 'trial-reels', f'antes-{date.today().isoformat()}')
        for f in os.listdir(os.path.join(proj, 'trial-reels')):
            p = os.path.join(proj, 'trial-reels', f)
            if os.path.isfile(p) and f.endswith('.mp4') and f not in keep:
                os.makedirs(dst, exist_ok=True)
                shutil.move(p, os.path.join(dst, f))
    used = {t.get('speed') for t in posted}
    free = [i for i in range(len(SPEEDS)) if SPEEDS[i] not in used]
    cur = current_caption(proj)
    caps = [c for c in CAPTION_ORDER if c != cur]
    hk = max(hook_end(proj), 2.0)
    trials = list(posted)
    n = max([t['n'] for t in posted] or [0])
    for k in range(count - len(posted)):
        i = free.pop(0)
        n += 1
        kind = HOOKS[k % len(HOOKS)]
        t = {'n': n, 'hook': {'kind': kind, 'to': hk}}
        if kind == 'titular':
            t['hook'].update(headline=None, to=max(hk, 2.5))
        else:
            t['hook'].update(case=['lower', 'upper'][(k // 2) % 2])
        if engine != 'custom' and k < len(caps):
            t['caption'] = caps[k]
        if '--colors' in args and k % 2 == 1:
            t['accent'] = ACCENTS[(k // 2) % len(ACCENTS)][0]
        t.update(speed=SPEEDS[i], look=LOOK_ORDER[i % len(LOOK_ORDER)],
                 zoom={'framing': ZOOMS[i], 'shift': SHIFTS[i], 'rhythm': RHYTHMS[k % len(RHYTHMS)]})
        t['id'] = f'v{n:02d}-{kind}'
        trials.append(t)
    for t in trials:
        t['what'] = describe(t)
    data = {'version': 2, 'base': base, 'planned': date.today().isoformat(), 'engine': engine, 'build_flags': flags,
            'trials': trials}
    write(os.path.join(proj, 'trials.json'), data)
    show(data)
    if engine == 'custom':
        print('NOTE   this reel was finished with its own scripts (Página y Tarjeta): the versions keep its captions. '
              'Hook, speed, zooms and colour change in every one.')
    elif engine == 'older':
        print('NOTE   today\'s engine builds this reel a little differently than when it was approved (the live camera, '
              'for one): the versions with another caption style carry that too. Tell the user.')
    if any(t['hook']['kind'] == 'titular' and not t['hook'].get('headline') for t in trials):
        print('CHECK  write each titular version\'s "headline" in trials.json ("hook"): 2 to 7 words from what the reel '
              'says, a different angle each (a question, a number, a "nobody tells you"), never a promise the reel does '
              'not make. Show them to the user first.')
    print(f'STATUS trials PLANNED {len(trials)}')


def show(data):
    for t in data['trials']:
        print(f'{t["n"]:>2}. {t["id"]:<14} {describe(t)}{"  (PUBLICADO)" if t.get("posted") else ""}')


# ---------------------------------------------------------------- make
def html_name(t):
    return f'trials/{t["n"]:02d}-{t["id"]}.html'


def add_headline(html, h):
    """the composition plus one headline over the opening, and nothing else, so outside the window every frame is the
    approved reel's and the window can be spliced into the approved render (works on any index.html)"""
    text = h['headline'].replace('<', '&lt;')
    size = 74 if len(text) <= 22 else 60
    t1 = max(.5, float(h['to']))
    # opaque and over the top band (y 214 to about 475): a reel that opens on its own title pill there gets it covered
    css = ("#tgh{position:absolute;left:50px;right:50px;top:214px;z-index:60;display:flex;justify-content:center;visibility:hidden}"
           "#tgh div{min-width:700px;min-height:260px;max-width:980px;padding:30px 40px;border-radius:32px;background:#13281F;"
           "display:flex;align-items:center;justify-content:center;color:#F2ECDF;"
           f"font:800 {size}px/1.04 'Inter Tight';letter-spacing:-.02em;text-align:center;box-shadow:0 14px 40px rgba(0,0,0,.3)}}")
    js = (f"tl.fromTo('#tgh',{{autoAlpha:0,y:-24}},{{autoAlpha:1,y:0,duration:.3,ease:'back.out(1.6)',immediateRender:false}},0.034);"
          f"tl.to('#tgh',{{autoAlpha:0,y:-12,duration:.16,ease:'power2.in'}},{t1 - .16:.3f});\n")
    hook = 'window.__timelines["main"] = tl;'
    if '</style>' not in html or hook not in html or not re.search(r'<div id="root"[^>]*>', html):
        return None
    html = html.replace('</style>', css + '\n</style>', 1)
    root = re.search(r'<div id="root"[^>]*>', html)
    html = html[:root.end()] + f'\n  <div id="tgh"><div>{text}</div></div>' + html[root.end():]
    return html.replace(hook, js + hook, 1)


def swap_accent(html, hexc):
    """the brand gold -> another accent, in every form the composition writes it"""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    out = re.sub(re.escape(BRAND_ACCENT), hexc, html, flags=re.I)
    return re.sub(r'201\s*,\s*161\s*,\s*91', f'{r},{g},{b}', out)


def bare(s):
    return re.sub(r'^[¡¿"“«(]+|[.,;:!?"”»)…]+$', '', s.strip()).lower()


def make_led(proj, t):
    """the opener: the hook's own words on Pantalla LED, a slot of the project (fx/trial-NN-led)"""
    name = f'trial-{t["n"]:02d}-led'
    slot = os.path.join(proj, 'fx', name)
    picks = os.path.join(proj, 'trials', 'picks-led.json')
    write(picks, {'mode': 'custom', 'style': None, 'captionStyle': 'none', 'effects': ['led-screen'], 'effectSections': None})
    r = subprocess.run([PY, os.path.join(HERE, 'fx_new.py'), 'led-screen', '--project', proj, '--from', '0',
                        '--to', f'{float(t["hook"]["to"]):.3f}', '--name', name, '--picks', picks, '--force'], **skillenv.TEXT)
    clip = read(os.path.join(slot, 'clip.json'), {}) or {}
    if r.returncode or not clip.get('frames'):
        return None, (r.stdout or '')[-300:] + (r.stderr or '')[-300:]
    frames = int(clip['frames'])
    words = read(os.path.join(proj, 'words.json'), []) or []
    words = words.get('words', words) if isinstance(words, dict) else words
    accent = sorted({bare(w.get('text', '')) for w in words if w.get('e') and float(w['start']) < float(t['hook']['to'])})
    p = os.path.join(slot, 'build.py')
    src = open(p, encoding='utf-8').read()
    src = re.sub(r'^T_OUT = None', f'T_OUT = {frames - 2}', src, count=1, flags=re.M)
    src = re.sub(r'^ACCENT = \[\]', f'ACCENT = {json.dumps(accent, ensure_ascii=False)}', src, count=1, flags=re.M)
    src = re.sub(r"^CASE = '[a-z-]+'", f"CASE = '{t['hook'].get('case', 'lower')}'", src, count=1, flags=re.M)
    open(p, 'w', encoding='utf-8', newline='\n').write(src)
    r = subprocess.run([PY, os.path.join(HERE, 'fx_run.py'), slot, 'build.py'], **skillenv.TEXT)
    if r.returncode:
        return None, (r.stdout or '')[-300:] + (r.stderr or '')[-300:]
    t['hook'].update(slot=os.path.relpath(slot, proj).replace('\\', '/'), led_in=3, led_out=frames - 2)
    lines = [l for l in (r.stdout or '').splitlines() if 'wrote index.html' in l]
    return slot, lines[0].strip() if lines else ''


def make(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    if not data or data.get('version') != 2:
        sys.exit('STATUS trials FAILED: no trials.json of this version. Run plan (with --fresh over an old one)')
    os.makedirs(os.path.join(proj, 'trials'), exist_ok=True)
    checks = 0
    approved = open(os.path.join(proj, 'index.html'), encoding='utf-8').read()
    pk = data.get('build_flags') or []          # how plan found this reel rebuilds (rebuild_check)
    for t in data['trials']:
        if t.get('posted'):
            continue
        h = t['hook']
        html = None
        if t.get('caption'):
            out = html_name(t)
            r = subprocess.run([PY, os.path.join(HERE, 'build_reel.py'), proj, '--out', out, '--caption', t['caption']] + pk,
                               **skillenv.TEXT)
            if r.returncode:
                print(f'CHECK  {t["n"]}. {t["id"]}: build_reel.py failed: {(r.stderr or r.stdout).strip()[-300:]}')
                checks += 1
                continue
            html = open(os.path.join(proj, out), encoding='utf-8').read()
        if t.get('accent'):
            html = swap_accent(html or approved, t['accent'])
        if h['kind'] == 'titular':
            if not h.get('headline'):
                print(f'CHECK  {t["n"]}. {t["id"]}: no "headline" yet in trials.json')
                checks += 1
                continue
            html = add_headline(html or approved, h)
            if html is None:
                print(f'CHECK  {t["n"]}. {t["id"]}: index.html has no </style>, root div or timeline hook for the headline. '
                      f'Write {html_name(t)} by hand: index.html with the headline over 0 to {h["to"]}s')
                checks += 1
                continue
        if html is not None:
            with open(os.path.join(proj, html_name(t)), 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(html)
            t['html'] = html_name(t)
        if h['kind'] == 'led':
            slot, msg = make_led(proj, t)
            if not slot:
                print(f'CHECK  {t["n"]}. {t["id"]}: the Pantalla LED opener failed: {msg}')
                checks += 1
                continue
            print(f'       {t["n"]}. LED {msg}')
        print(f'MADE   {t["n"]}. {t["id"]}  {describe(t)}')
    write(os.path.join(proj, 'trials.json'), data)
    print('STATUS trials MADE' + (f' with {checks} CHECK line(s)' if checks else ''))


# ---------------------------------------------------------------- render
def face(proj):
    h = (read(os.path.join(proj, 'layout.json'), {}) or {}).get('head') or {}
    return int(h.get('cx') or 540), int(((h.get('top') or 452) + (h.get('chin') or 760)) / 2)


def cuts(proj, frames):
    """[(first frame, frames)] of every shot of the reel: segments.json, or 2-second pieces"""
    segs = read(os.path.join(proj, 'segments.json'), []) or []
    out = [(int(s['frame']), int(s['frames'])) for s in segs if 'frame' in s and 'frames' in s]
    return out or [(f, min(60, frames - f)) for f in range(0, frames, 60)]


def zoom_expr(rhythm, shots, framing):
    """the zoom for input frame `n`: the framing times the rhythm, piecewise over the shots"""
    amp = max(0.0, ZOOM_MAX / framing - 1)
    pieces = []
    for k, (f0, length) in enumerate(shots):
        if rhythm == 'golpes':           # a punch on the cut that eases out in about 8 frames
            r = f'(1+{min(.07, amp):.4f}*exp(-(n-{f0})/8))'
        elif rhythm == 'empuje':         # a slow push through the shot, back on the cut
            r = f'(1+{min(.05, amp):.4f}*(n-{f0})/{max(1, length)})'
        elif rhythm == 'alterno':        # every other shot tighter, like a jump cut
            r = f'{1 + min(.07, amp) * (k % 2):.4f}'
        else:                            # respira: a slow in and out
            r = f'(1+{min(.05, amp) / 2:.4f}*(1-cos(2*PI*n/90)))'
        pieces.append((f0, f0 + length - 1, r))
    expr = '1'
    for f0, f1, r in reversed(pieces):
        expr = f'if(between(n,{f0},{f1}),{r},{expr})'
    return f'{framing:.4f}*{expr}'


def light_pass(proj, src, dst, t, frames):
    """zoom rhythm and framing around the face, a light grade, then the speed (voice pitch kept). The zoom is a scale
    worked out again on every frame plus a crop that keeps the face where it was (zoompan multiplies the frames of a
    video: never use it here)"""
    cx, cy = face(proj)
    z = zoom_expr(t['zoom']['rhythm'], cuts(proj, frames), float(t['zoom']['framing']))
    dx = float(t['zoom']['shift'])
    zoom = (f"scale=w='trunc(1080*({z})/2)*2':h='trunc(1920*({z})/2)*2':eval=frame:flags=bicubic,"
            f"crop=1080:1920:x='min(max(0,{cx}*(in_w/1080-1)+{dx:.0f}),in_w-1080)':y='min(max(0,{cy}*(in_h/1920-1)),in_h-1920)'")
    s = float(t['speed'])
    vf = f'{zoom},{LOOKS[t["look"]]},setpts=PTS/{s},fps={FPS},format=yuv420p'
    cmd = [FF, '-v', 'error', '-y', '-i', src, '-vf', vf, '-af', f'atempo={s}', '-c:v', 'libx264', '-crf', '17',
           '-preset', 'medium', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', dst]
    subprocess.run(cmd, check=True)


def splice(base, part, f0, f1, dst):
    """base frames, with [f0, f1) taken from `part` (same frame numbering); base audio as it is"""
    fc = (f'[0:v]trim=end_frame={f0},setpts=PTS-STARTPTS[a];[1:v]trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS[b];'
          f'[0:v]trim=start_frame={f1},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps={FPS}[v]')
    subprocess.run([FF, '-v', 'error', '-y', '-i', base, '-i', part, '-filter_complex', fc, '-map', '[v]', '-map', '0:a?',
                    '-c:a', 'copy', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', dst], check=True)


def render(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    if not data or data.get('version') != 2:
        sys.exit('STATUS trials FAILED: no trials.json of this version. Run plan and make first')
    lock = os.path.join(proj, 'trials', '.busy')
    os.makedirs(os.path.join(proj, 'trials'), exist_ok=True)
    if os.path.exists(lock):
        sys.exit('STATUS trials BUSY: another trials render is running on this project (delete trials/.busy if not)')
    open(lock, 'w').close()
    base = os.path.join(proj, data['base'])
    frames = probe(base)
    only, redo = opt(args, '--only'), '--redo' in args
    outdir = os.path.join(proj, 'trial-reels')
    os.makedirs(outdir, exist_ok=True)
    todo = [t for t in data['trials'] if not t.get('posted') and (not only or str(t['n']) == only or t['id'] == only)]
    mins = sum((15 if t.get('caption') or t.get('accent') else 1) + 3 for t in todo)
    print(f'QUEUE  {len(todo)} version(s), about {mins} min')
    failed = []

    def tmp(n, s):
        return os.path.join(proj, 'trials', f'{n:02d}-{s}.mp4')
    try:
        for t in todo:
            name = f'trial-{t["n"]:02d}-{t["id"]}.mp4'
            dst = os.path.join(outdir, name)
            if os.path.isfile(dst) and not redo:
                print(f'KEPT   {name} (--redo renders it again)')
                continue
            h, n, src, ok = t['hook'], t['n'], base, True
            if t.get('html') and not os.path.isfile(os.path.join(proj, t['html'])):
                print(f'FAILED {n}. {t["id"]}: {t["html"]} is missing (make, and its CHECK lines)')
                ok = False
            elif t.get('caption') or t.get('accent'):
                # the whole reel again; the sound did not change, so the approved render's track goes on as it is
                full = tmp(n, 'full')
                ok = subprocess.run([PY, os.path.join(HERE, 'hf.py'), proj, 'render', '-c', t['html'], '-o',
                                     os.path.relpath(full, proj), '--quality', 'high']).returncode == 0
                if ok:
                    subprocess.run([FF, '-v', 'error', '-y', '-i', full, '-i', base, '-map', '0:v', '-map', '1:a', '-c', 'copy',
                                    '-shortest', tmp(n, 'a')], check=True)
                    src = tmp(n, 'a')
            elif t.get('html'):
                # only the headline window, spliced into the approved render
                end = min(float(h['to']) + .3, frames / FPS)
                ok = subprocess.run([PY, os.path.join(HERE, 'render_window.py'), proj, '0', f'{end:.3f}', data['base'],
                                     '-c', t['html'], '-o', os.path.relpath(tmp(n, 'a'), proj)]).returncode == 0
                src = tmp(n, 'a')
            if ok and h['kind'] == 'led':
                if not h.get('slot'):
                    print(f'FAILED {n}. {t["id"]}: no opener slot (make, and its CHECK lines)')
                    ok = False
                else:
                    slot = os.path.join(proj, h['slot'])
                    ok = subprocess.run([PY, os.path.join(HERE, 'fx_run.py'), slot, 'hf', 'render']).returncode == 0
                    led = os.path.join(slot, 'renders', os.path.basename(slot) + '.mp4')
                    if ok and os.path.isfile(led):
                        splice(src, led, int(h['led_in']), int(h['led_out']), tmp(n, 'b'))
                        src = tmp(n, 'b')
                    else:
                        ok = False
            if ok and probe(src) != frames:
                print(f'FAILED {n}. {t["id"]}: {probe(src)} frames, the approved render has {frames}')
                ok = False
            if not ok:
                failed.append(t['id'])
                continue
            light_pass(proj, src, dst, t, frames)
            for s in ('full', 'a', 'b'):                  # the in-between renders
                if os.path.isfile(tmp(n, s)):
                    os.remove(tmp(n, s))
            t['file'] = name
            print(f'DONE   {name}  {describe(t)}')
    finally:
        os.remove(lock)
    write(os.path.join(proj, 'trials.json'), data)
    with open(os.path.join(outdir, 'que-cambia.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(f'{t.get("file") or "(sin render)":<30} {describe(t)}' for t in data['trials']) + '\n')
    print('STATUS trials ' + (f'INCOMPLETE, failed: {", ".join(failed)}' if failed else f'DONE {outdir}'))


def posted(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    n = next((a for a in args if a.isdigit()), None)
    t = next((t for t in (data or {}).get('trials', []) if str(t['n']) == n), None)
    if not t:
        sys.exit('STATUS trials FAILED: no such version number')
    t['posted'] = '--undo' not in args
    write(os.path.join(proj, 'trials.json'), data)
    print(f'STATUS trials {"POSTED" if t["posted"] else "UNPOSTED"} {n}. {t["id"]}')


def main():
    skillenv.utf8_stdio()
    a = sys.argv[1:]
    if len(a) < 2 or a[0] not in ('plan', 'make', 'render', 'list', 'posted'):
        sys.exit(__doc__)
    proj = skillenv.path_arg(a[1])
    rest = a[2:]
    if a[0] == 'plan':
        plan(proj, rest)
    elif a[0] == 'make':
        make(proj, rest)
    elif a[0] == 'render':
        render(proj, rest)
    elif a[0] == 'list':
        show(read(os.path.join(proj, 'trials.json'), {'trials': []}))
    else:
        posted(proj, rest)


if __name__ == '__main__':
    main()
