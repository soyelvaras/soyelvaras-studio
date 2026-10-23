#!/usr/bin/env python3
"""Trial reels: several versions of one approved reel, each different in ONE thing, plus its own light pass (speed,
framing and colour) so no two files are copies of each other. Instagram shows trial reels to non-followers first:
post them, keep the one that wins, and the winner says what worked. Guide: references/trials.md.

Usage (run with PY):
  PY trials.py plan   "<project>" --base renders/<slug>-vN.mp4 [--count 5] [--change hook,captions,colors,effects,pass]
                      [--fresh]         proposes the mix -> <project>/trials.json, and prints it
  PY trials.py make   "<project>"       builds each trial's composition (trials/NN-<id>.html). CHECK lines = do by hand
  PY trials.py render "<project>" [--only N] [--redo]     IN THE BACKGROUND: one after another, never two at once
  PY trials.py list   "<project>"       what each file changes
  PY trials.py posted "<project>" N [--undo]              trial N went out: it is never made or rendered again

What each change costs (the cheapest that still tests the thing):
  hook      a new opening headline over the first seconds. Only the opening is rendered (render_window.py -c) and
            spliced into the approved render: about a minute.
  captions  another caption style (built-in key). A whole render (about 15 min): the captions run all along.
  colors    the reel's accent colour swapped (the brand's gold #C9A15B -> another one) in the composition. A whole
            render. Effect slots are finished videos: they keep their own colours.
  effects   the reel with no effect slots (or only the ones in "effects"). A whole render.
  pass      nothing but the light pass: the approved render itself, sped, reframed and graded (ffmpeg only).
Every trial then gets its own pass, done on the finished file with ffmpeg: speed 0.965-1.035 (never 1.0, voice
pitch kept), 3-5% tighter around the face with a small side shift, and a light grade. Captions and graphics scale
with the picture (at most 5%, so they stay inside the safe zone). A trial can be strict: "unique": false.
hook and colors are made on the approved index.html itself, so they work on any reel, also one built with the
project's own scripts (Página y Tarjeta). captions and effects rebuild it with build_reel.py, so they need a reel
built by it (make says when today's engine would build it differently).
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
# the order a plan uses when it picks caption styles: the most different from the usual first
CAPTION_ORDER = ['karaoke', 'loud-lowercase', 'golden-hour', 'keyword', 'outline', 'anchor', 'arcade', 'low-key']
CAPTION_NAMES = {'karaoke': 'Karaoke', 'loud-lowercase': 'Minúscula Gigante', 'golden-hour': 'Hora Dorada',
                 'keyword': 'Palabra Clave', 'outline': 'Contorno', 'anchor': 'Noticiero', 'arcade': 'Arcade',
                 'low-key': 'Discreto'}
# accent colours a 'colors' trial may swap the gold for: on brand, never orange (effects/INDEX.md)
ACCENTS = [('#8FB9A8', 'salvia'), ('#F2ECDF', 'crema'), ('#B9C7E4', 'azul niebla'), ('#D8B4A0', 'arcilla')]
# the light pass: no two trials share a speed or a framing, and none is the reel itself (1.0x, unframed)
SPEEDS = [1.025, 0.975, 1.035, 0.965, 1.015, 0.985, 1.03, 0.97, 1.02, 0.98]
ZOOMS = [1.04, 1.03, 1.05, 1.035, 1.045, 1.032, 1.048, 1.038, 1.042, 1.034]
SHIFTS = [-18, 16, -8, 22, 10, -24, 4, -14, 20, -4]
LOOKS = {
    'calido': 'colorbalance=rm=.025:gm=.005:bm=-.025,eq=saturation=1.04',
    'frio': 'colorbalance=rm=-.02:bm=.025,eq=saturation=.98',
    'claro': 'eq=brightness=.018:contrast=1.02',
    'contraste': 'eq=contrast=1.05:saturation=1.03',
    'suave': 'eq=contrast=.97:brightness=.01:saturation=.97',
}
LOOK_ORDER = list(LOOKS)
KINDS = ['hook', 'captions', 'colors', 'effects', 'pass']


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


def engine_built(proj):
    """True when index.html came from build_reel.py (caption and effect trials rebuild it from plan.json)"""
    b, ix = os.path.join(proj, 'work', 'build.json'), os.path.join(proj, 'index.html')
    return os.path.isfile(b) and os.path.isfile(ix) and abs(os.path.getmtime(b) - os.path.getmtime(ix)) < 120


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
    b = read(os.path.join(proj, 'work', 'build.json'), {}) or {}
    return b.get('caption')


# ---------------------------------------------------------------- plan
def plan(proj, args):
    base = opt(args, '--base')
    old = read(os.path.join(proj, 'trials.json'), {}) or {}
    base = base or old.get('base')
    if not base or not os.path.isfile(os.path.join(proj, base)):
        sys.exit('STATUS trials FAILED: --base renders/<slug>-vN.mp4, the approved render (relative to the project)')
    count = int(opt(args, '--count', '5'))
    kinds = [k.strip() for k in (opt(args, '--change') or ','.join(KINDS)).split(',') if k.strip()]
    bad = [k for k in kinds if k not in KINDS]
    if bad:
        sys.exit(f'STATUS trials FAILED: unknown change {bad}. One of: {", ".join(KINDS)}')
    engine = engine_built(proj)
    if not engine:
        dropped = [k for k in kinds if k in ('captions', 'effects')]
        kinds = [k for k in kinds if k not in ('captions', 'effects')]
        if dropped:
            print(f'NOTE   index.html was not built by build_reel.py (a reel made with its own scripts): '
                  f'{", ".join(dropped)} left out. hook, colors and pass still work.')
        if not kinds:
            sys.exit('STATUS trials FAILED: nothing left to test on this reel')
    if old.get('trials') and '--fresh' not in args:
        sys.exit('STATUS trials FAILED: trials.json already has a plan. --fresh makes a new one (posted trials stay)')
    posted = [t for t in old.get('trials', []) if t.get('posted')]
    if '--fresh' in args and os.path.isdir(os.path.join(proj, 'trial-reels')):
        keep = {t['file'] for t in posted if t.get('file')}
        dst = os.path.join(proj, 'trial-reels', f'antes-{date.today().isoformat()}')
        for f in os.listdir(os.path.join(proj, 'trial-reels')):
            p = os.path.join(proj, 'trial-reels', f)
            if os.path.isfile(p) and f.endswith('.mp4') and f not in keep:
                os.makedirs(dst, exist_ok=True)
                shutil.move(p, os.path.join(dst, f))
    used_pass = {(t['unique'] or {}).get('speed') for t in posted if t.get('unique')}
    cur = current_caption(proj)
    caps = [c for c in CAPTION_ORDER if c != cur]
    hk = hook_end(proj)
    trials, n_of = list(posted), {k: 0 for k in KINDS}
    k_i = 0
    while len(trials) < count and k_i < count * len(KINDS):
        kind = kinds[k_i % len(kinds)]
        k_i += 1
        j = n_of[kind]
        n_of[kind] += 1
        t = {'change': kind}
        if kind == 'hook':
            t.update(id=f'gancho-{j + 1}', what='Gancho: abre con el titular «(escríbelo)»', headline=None, to=max(hk, 2.5))
        elif kind == 'captions':
            if j >= len(caps):
                continue
            t.update(id=f'subtitulos-{caps[j]}', what=f'Subtítulos: {CAPTION_NAMES.get(caps[j], caps[j])}', caption=caps[j])
        elif kind == 'colors':
            if j >= len(ACCENTS):
                continue
            hexc, name = ACCENTS[j]
            t.update(id=f'colores-{name.replace(" ", "-")}', what=f'Colores: el dorado pasa a {name} ({hexc})', accent=hexc)
        elif kind == 'effects':
            if j:
                continue
            t.update(id='sin-efectos', what='Efectos: el reel sin efectos', effects=[])
        elif kind == 'pass':
            if j:
                continue
            t.update(id='solo-pase', what='Nada más: el mismo reel con su pase propio (control)')
        trials.append(t)
    free = [i for i in range(len(SPEEDS)) if SPEEDS[i] not in used_pass]
    n = max([t['n'] for t in posted] or [0])
    for t in trials:
        if t.get('posted'):           # a posted trial keeps its number, its file and its pass
            continue
        n += 1
        t['n'] = n
        if t.get('unique', True) is not False:
            i = free.pop(0)
            t['unique'] = {'speed': SPEEDS[i], 'zoom': ZOOMS[i], 'shift': SHIFTS[i], 'look': LOOK_ORDER[i % len(LOOK_ORDER)]}
    data = {'base': base, 'planned': date.today().isoformat(), 'engine': engine, 'trials': trials}
    write(os.path.join(proj, 'trials.json'), data)
    show(proj, data)
    if any(t['change'] == 'hook' and not t.get('headline') for t in trials):
        print('CHECK  write each hook trial\'s "headline" in trials.json: 2 to 7 words, from what the reel says, '
              'never a promise it does not make. Show the options to the user first.')
    if len(trials) < count:
        print(f'SHORT  only {len(trials)} of {count}: add a hook trial by hand, or allow more kinds (--change)')
    print(f'STATUS trials PLANNED {len(trials)}')


def show(proj, data):
    for t in data['trials']:
        u = t.get('unique')
        extra = (f'  [{u["speed"]:.3f}x, {round((u["zoom"] - 1) * 100, 1)}% más cerca, {u["look"]}]' if u else '  [estricto]')
        print(f'{t["n"]:>2}. {t["id"]:<24} {t["what"]}{"  (PUBLICADO)" if t.get("posted") else ""}{extra}')


# ---------------------------------------------------------------- make
def html_name(t):
    return f'trials/{t["n"]:02d}-{t["id"]}.html'


def add_headline(html, t):
    """the approved composition plus one headline over the opening, and nothing else: outside the window every frame
    stays the approved reel's, so the window can be spliced into the approved render (works on any index.html)"""
    text = t['headline'].replace('<', '&lt;')
    size = 74 if len(text) <= 22 else 60
    t1 = max(.5, float(t['to']))
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


def make(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    if not data:
        sys.exit('STATUS trials FAILED: no trials.json. Run plan first')
    os.makedirs(os.path.join(proj, 'trials'), exist_ok=True)
    checks = 0
    approved = open(os.path.join(proj, 'index.html'), encoding='utf-8').read()
    # a rebuild uses the picks the reel was built with, not today's saved ones (another style since would drop its
    # effect slots): its own style and caption style, and every effect it has a slot for, allowed anywhere
    built = read(os.path.join(proj, 'work', 'build.json'), {}) or {}
    plan_slots = (read(os.path.join(proj, 'plan.json'), {}) or {}).get('slots') or []
    picks = {'mode': 'preset' if built.get('style') else 'custom', 'style': built.get('style'),
             'captionStyle': built.get('caption') if built.get('caption') not in (None, 'custom') else 'none',
             'effects': sorted({s['key'] for s in plan_slots if s.get('key')}), 'effectSections': None}
    write(os.path.join(proj, 'trials', 'picks.json'), picks)
    pk = ['--picks', os.path.join(proj, 'trials', 'picks.json')]
    if any(t['change'] in ('captions', 'effects') and not t.get('posted') for t in data['trials']):
        # does today's engine still build this reel exactly as it was approved, with or without the user's own style
        # (my-style.json may be newer than the reel)? The first way that matches is used for the rebuilt trials. If
        # none does, a rebuilt trial also carries what changed since (the live camera...): say so, it is a second change
        cap = current_caption(proj)
        capf = ['--caption', cap] if cap and cap != 'custom' else []
        match = None
        for extra in ([], ['--no-my-style']):
            r = subprocess.run([PY, os.path.join(HERE, 'build_reel.py'), proj, '--out', 'trials/00-check.html'] + pk + capf
                               + extra, **skillenv.TEXT)
            if r.returncode == 0 and open(os.path.join(proj, 'trials', '00-check.html'), encoding='utf-8').read() == approved:
                match = extra
                break
        pk += match or []
        if match is None:
            print('NOTE   today\'s engine does not build this reel exactly as it was approved (it is older than the last '
                  'engine change, or than the user\'s own style). The captions and effects trials are rebuilt, so they '
                  'also carry those changes: tell the user, or leave those two out. hook, colors and pass are made on '
                  'the approved index.html.')
    for t in data['trials']:
        if t.get('posted') or t['change'] == 'pass':
            continue
        out = html_name(t)
        over, cmd = {}, None
        if t['change'] == 'hook':
            if not t.get('headline'):
                print(f'CHECK  {t["n"]}. {t["id"]}: no "headline" yet in trials.json')
                checks += 1
                continue
            src = add_headline(approved, t)
            if src is None:
                print(f'CHECK  {t["n"]}. {t["id"]}: index.html has no </style>, root div or timeline hook to add the '
                      f'headline to. Write {out} by hand: index.html with the headline over 0 to {t["to"]}s')
                checks += 1
                continue
        elif t['change'] == 'colors':
            src = approved
        elif t['change'] == 'captions':
            cmd = ['--caption', t['caption']]
        elif t['change'] == 'effects':
            plan = read(os.path.join(proj, 'plan.json'), {}) or {}
            keep = set(t.get('effects') or [])
            over['slots'] = [dict(s, off=True) if s.get('key') not in keep else s for s in plan.get('slots') or []]
            cap = current_caption(proj)
            cmd = ['--caption', cap] if cap and cap != 'custom' else None
        if t['change'] in ('hook', 'colors'):
            pass
        else:
            ov = os.path.join(proj, 'trials', f'{t["n"]:02d}-over.json')
            write(ov, over)
            r = subprocess.run([PY, os.path.join(HERE, 'build_reel.py'), proj, '--plan-over', ov, '--out', out] + pk + (cmd or []),
                               **skillenv.TEXT)
            print((r.stdout or '').strip().splitlines()[0] if r.stdout else '')
            if r.returncode:
                print(f'CHECK  {t["n"]}. {t["id"]}: build_reel.py failed: {(r.stderr or r.stdout).strip()[-300:]}')
                checks += 1
                continue
            src = open(os.path.join(proj, out), encoding='utf-8').read()
        if t['change'] == 'colors':
            new = swap_accent(src, t['accent'])
            if new == src:
                print(f'CHECK  {t["n"]}. {t["id"]}: the gold {BRAND_ACCENT} is not in the composition, so nothing changed. '
                      f'Write the colour swap by hand in {out}')
                checks += 1
            src = new
        with open(os.path.join(proj, out), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(src)
        print(f'MADE   {t["n"]}. {t["id"]} -> {out}')
    print(f'STATUS trials MADE' + (f' with {checks} CHECK line(s)' if checks else ''))


# ---------------------------------------------------------------- render
def face(proj):
    l = read(os.path.join(proj, 'layout.json'), {}) or {}
    h = l.get('head') or {}
    cx = int(h.get('cx') or 540)
    cy = int(((h.get('top') or 452) + (h.get('chin') or 760)) / 2)
    return cx, cy


def light_pass(proj, src, dst, u):
    """speed (voice pitch kept), a little tighter around the face with a side shift, a light grade"""
    if not u:
        shutil.copyfile(src, dst)
        return
    cx, cy = face(proj)
    z, s = float(u['zoom']), float(u['speed'])
    w, h = int(round(1080 * z / 2) * 2), int(round(1920 * z / 2) * 2)
    x = min(max(cx * z - cx + float(u['shift']), 0), w - 1080)
    y = min(max(cy * z - cy, 0), h - 1920)
    vf = (f'scale={w}:{h}:flags=lanczos,crop=1080:1920:{x:.0f}:{y:.0f},{LOOKS[u["look"]]},'
          f'setpts=PTS/{s},fps={FPS},format=yuv420p')
    cmd = [FF, '-v', 'error', '-y', '-i', src, '-vf', vf, '-af', f'atempo={s}', '-c:v', 'libx264', '-crf', '17',
           '-preset', 'medium', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', dst]
    subprocess.run(cmd, check=True)


def render(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    if not data:
        sys.exit('STATUS trials FAILED: no trials.json. Run plan and make first')
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
    mins = sum(15 if t['change'] in ('captions', 'colors', 'effects') else 1 for t in todo)
    print(f'QUEUE  {len(todo)} trial(s), about {mins} min')
    failed = []
    try:
        for t in todo:
            name = f'trial-{t["n"]:02d}-{t["id"]}.mp4'
            dst = os.path.join(outdir, name)
            if os.path.isfile(dst) and not redo:
                print(f'KEPT   {name} (--redo renders it again)')
                continue
            raw = os.path.join(proj, 'trials', f'{t["n"]:02d}-raw.mp4')
            h = html_name(t)
            ok = True
            if t['change'] == 'pass':
                raw = base
            elif not os.path.isfile(os.path.join(proj, h)):
                print(f'FAILED {t["n"]}. {t["id"]}: {h} is missing (make, and its CHECK lines)')
                ok = False
            elif t['change'] == 'hook':
                end = min(float(t['to']) + .3, frames / FPS)
                r = subprocess.run([PY, os.path.join(HERE, 'render_window.py'), proj, '0', f'{end:.3f}', data['base'],
                                    '-c', h, '-o', os.path.relpath(raw, proj)])
                ok = r.returncode == 0
            else:
                part = os.path.join(proj, 'trials', f'{t["n"]:02d}-full.mp4')
                r = subprocess.run([PY, os.path.join(HERE, 'hf.py'), proj, 'render', '-c', h, '-o',
                                    os.path.relpath(part, proj), '--quality', 'high'])
                ok = r.returncode == 0
                if ok and t['change'] != 'effects':
                    # the sound did not change: the approved render's track (with every fix it got) goes on it as it is
                    subprocess.run([FF, '-v', 'error', '-y', '-i', part, '-i', base, '-map', '0:v', '-map', '1:a', '-c', 'copy',
                                    '-shortest', raw], check=True)
                elif ok:
                    shutil.move(part, raw)
            if ok and probe(raw) != frames:
                print(f'FAILED {t["n"]}. {t["id"]}: {probe(raw)} frames, the approved render has {frames}')
                ok = False
            if not ok:
                failed.append(t['id'])
                continue
            light_pass(proj, raw, dst, t.get('unique'))
            for tmp in (raw, os.path.join(proj, 'trials', f'{t["n"]:02d}-full.mp4')):   # the in-between renders
                if tmp != base and os.path.isfile(tmp):
                    os.remove(tmp)
            t['file'] = name
            print(f'DONE   {name}  {t["what"]}')
    finally:
        os.remove(lock)
    write(os.path.join(proj, 'trials.json'), data)
    lines = [f'{t.get("file") or "(sin render)":<36} {t["what"]}' for t in data['trials']]
    with open(os.path.join(outdir, 'que-cambia.txt'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('STATUS trials ' + (f'INCOMPLETE, failed: {", ".join(failed)}' if failed else f'DONE {outdir}'))


def posted(proj, args):
    data = read(os.path.join(proj, 'trials.json'))
    n = next((a for a in args if a.isdigit()), None)
    t = next((t for t in (data or {}).get('trials', []) if str(t['n']) == n), None)
    if not t:
        sys.exit('STATUS trials FAILED: no such trial number')
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
        show(proj, read(os.path.join(proj, 'trials.json'), {'trials': []}))
    else:
        posted(proj, rest)


if __name__ == '__main__':
    main()
