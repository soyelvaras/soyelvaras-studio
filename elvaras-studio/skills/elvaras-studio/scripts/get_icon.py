#!/usr/bin/env python3
"""Fetch the real logo of an app or brand the speaker names, under a free licence, for the graphics that show it
(Caja de Prompt, Fila de Cápsulas, a layer, a Mundo App screen).

Usage:  PY get_icon.py "<app name>" ["<app name>" ...] [--to <folder>] [--list]

  "<app name>"  as the speaker says it: "Claude", "Google Drive", "ChatGPT", "Premiere". One file per name.
  --list        only show the logos the skill already has (engine/icons + fetched), then stop
  --to <dir>    save somewhere else than <state folder>/icons (skill maintenance: --to engine/icons)
  --force       fetch again even when the logo is already there

Where it looks, in order:
  1. the logos already there (engine/icons, the starter set that ships with the skill, then <state folder>/icons)
  2. Simple Icons 16.35.0 (CC0): one-colour logos with the brand colour, matched by name, slug or alias
  3. Iconify, free collections only: logos (CC0, full colour), thesvg-color, devicon, skill-icons, thesvg,
     vscode-icons (all MIT)
Saves <slug>.svg plus a row in icons.json ({slug: {title, hex, mono, source, license}}) and LICENSES.md in that folder.
Prints  ICON <slug> <title> (<source>, <license>)  per name, or  MISSING <name>  when no free logo exists: then the
graphic uses the app's initial on a tile, and you say so. Never a logo from anywhere else (a website, a screenshot).

The logos are trademarks of their owners: they name the app in the user's own reels, never suggest the brand made,
sponsors or backs the video. fx_new.py copies engine/icons and the fetched ones into every slot that uses logos
(slot.json "icons": true), as <slot>/assets/icons. Needs the internet once per logo. Standard library only.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skillenv  # noqa: E402

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
SI_VERSION = '16.35.0'
SI_CDN = f'https://cdn.jsdelivr.net/npm/simple-icons@{SI_VERSION}'
ICONIFY = 'https://api.iconify.design'
FREE = {'logos': 'CC0 1.0', 'thesvg-color': 'MIT', 'devicon': 'MIT', 'skill-icons': 'MIT', 'thesvg': 'MIT',
        'vscode-icons': 'MIT'}     # the Iconify collections it may take from, and their licence
SHIPPED = os.path.join(skillenv.SKILL_DIR, 'engine', 'icons')
# names people say that are not the brand's own title in Simple Icons / Iconify
ALIASES = {'chatgpt': 'openai', 'gpt': 'openai', 'premiere': 'adobepremierepro', 'premiere pro': 'adobepremierepro',
           'photoshop': 'adobephotoshop', 'gemini': 'googlegemini', 'drive': 'googledrive', 'sheets': 'googlesheets',
           'calendar': 'googlecalendar', 'vscode': 'visualstudiocode', 'vs code': 'visualstudiocode',
           'davinci': 'davinciresolve', 'twitter': 'x', 'ig': 'instagram', 'yt': 'youtube'}


def opt(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def slugify(text):
    t = text.lower().replace('+', 'plus').replace('.', 'dot').replace('&', 'and')
    return re.sub(r'[^a-z0-9]', '', t)


def get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=timeout) as r:
        return r.read()


def clean_svg(data):
    """an svg that is only a drawing: no scripts, no event handlers, no links out"""
    s = data.decode('utf-8', 'replace').strip()
    s = re.sub(r'<\?xml[^>]*\?>', '', s).strip()
    if not s.startswith('<svg') or '<script' in s.lower() or re.search(r'\son\w+\s*=', s) \
            or re.search(r'(xlink:)?href\s*=\s*["\'](?!#)', s):
        return None
    return s


def index_of(folder):
    try:
        with open(os.path.join(folder, 'icons.json'), encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save(folder, slug, svg, meta):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, slug + '.svg'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(svg)
    idx = index_of(folder)
    idx[slug] = meta
    with open(os.path.join(folder, 'icons.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(dict(sorted(idx.items())), fh, ensure_ascii=False, indent=1)
    lic = os.path.join(folder, 'LICENSES.md')
    if not os.path.exists(lic):
        with open(lic, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('# Logos de apps\n\nCada archivo es un SVG plano (sin scripts ni enlaces externos). Los logos son marcas de '
                     'sus dueños: se usan para nombrar la app en los reels propios, nunca como si la marca auspiciara o '
                     'respaldara el video.\n\n| Archivo | Fuente | Licencia del SVG |\n|---|---|---|\n')
    with open(lic, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(f"| {slug} | {meta['source']} | {meta['license']} |\n")


def simple_icons(cache):
    path = os.path.join(cache, f'.simple-icons-{SI_VERSION}.json')
    if not os.path.isfile(path):
        os.makedirs(cache, exist_ok=True)
        with open(path, 'wb') as fh:
            fh.write(get(f'{SI_CDN}/data/simple-icons.json', 60))
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    out = {}
    for i in data:
        slug = i.get('slug') or slugify(i['title'])
        out.setdefault(slug, i)
        out.setdefault(slugify(i['title']), dict(i, slug=slug))
        for aka in ((i.get('aliases') or {}).get('aka') or []):
            out.setdefault(slugify(aka), dict(i, slug=slug))
    return out


def from_simple_icons(name, si):
    i = si.get(ALIASES.get(name.lower().strip(), slugify(name)))
    if not i:
        return None
    slug = i.get('slug') or slugify(i['title'])
    svg = clean_svg(get(f'{SI_CDN}/icons/{slug}.svg'))
    if not svg:
        return None
    return slug, svg, {'title': i['title'], 'hex': '#' + i['hex'], 'mono': True,
                       'source': f'Simple Icons {SI_VERSION} (cdn.jsdelivr.net/npm/simple-icons)', 'license': 'CC0 1.0'}


def from_iconify(name):
    slug = ALIASES.get(name.lower().strip(), slugify(name))
    queries = list(dict.fromkeys([name.strip(), name.replace(' ', '').strip()]))
    for prefix, lic in FREE.items():
        for q in queries:
            try:
                hits = json.loads(get(f'{ICONIFY}/search?query={urllib.parse.quote(q)}&prefix={prefix}&limit=16')).get('icons') or []
            except (urllib.error.URLError, ValueError, OSError):
                continue
            want = slugify(q)

            def bare(h):
                return slugify(h.split(':', 1)[1].replace('-icon', ''))
            # the brand's own mark: its name in the icon's name, no file or folder icon, the "-icon" mark before a
            # wordmark, the shortest name (closest to the plain brand)
            fits = [h for h in hits if want in bare(h) and not re.search(r'(^|-)(file|folder)-', h.split(':', 1)[1])
                    and 'wordmark' not in h]
            for h in sorted(fits, key=lambda h: (bare(h) != want, not h.endswith('-icon'), len(h))):
                svg = clean_svg(get(f'{ICONIFY}/{prefix}/{h.split(":", 1)[1]}.svg'))
                if svg:
                    return slug, svg, {'title': name.strip(), 'hex': None, 'mono': False,
                                       'source': f'Iconify {h} (api.iconify.design)', 'license': lic}
    return None


def main():
    skillenv.utf8_stdio()
    folder = skillenv.path_arg(opt('--to')) if opt('--to') else skillenv.icons_dir()
    if '--list' in sys.argv:
        for label, d in (('shipped', SHIPPED), ('fetched', skillenv.icons_dir())):
            for slug, m in sorted(index_of(d).items()):
                print(f'{label:8} {slug:22} {m.get("title")}  ({m.get("license")})')
        return
    names = [a for a in sys.argv[1:] if not a.startswith('--') and a != opt('--to')]
    if not names:
        sys.exit(__doc__)
    si = None
    for name in names:
        want = ALIASES.get(name.lower().strip(), slugify(name))
        had = next((d for d in (SHIPPED, skillenv.icons_dir(), folder) if os.path.isfile(os.path.join(d, want + '.svg'))), None)
        if had and '--force' not in sys.argv:
            m = index_of(had).get(want, {})
            print(f'ICON {want} {m.get("title", name)} (already there: {m.get("source", had)}, {m.get("license", "?")})')
            continue
        try:
            si = si if si is not None else simple_icons(skillenv.icons_dir())
            got = from_simple_icons(name, si) or from_iconify(name)
        except (urllib.error.URLError, OSError) as e:
            sys.exit(f'NO CONNECTION  could not reach the logo sources ({e}). Try again with internet.')
        if not got:
            print(f'MISSING {name}  (no free logo: the graphic uses its initial on a tile)')
            continue
        slug, svg, meta = got
        save(folder, slug, svg, meta)
        print(f'ICON {slug} {meta["title"]} ({meta["source"]}, {meta["license"]})')


if __name__ == '__main__':
    main()
