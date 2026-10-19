#!/usr/bin/env python3
"""The voice and the picture never lose quality (SKILL.md rule 9). Reads the Studio's scripts and fails when:
  - a script encodes audio below 320k;
  - the phone copy re-encodes the render's audio instead of copying it, shrinks the picture below 1080p, or uses a
    crf above 20;
  - the final render's crf (skillenv.RENDER_CRF) is above 16, or a render can skip it.
Needs nothing installed.

Usage:  python tests/check_quality.py      (exits 1 and names each broken rule)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'elvaras-studio', 'skills', 'elvaras-studio', 'scripts')
MIN_AUDIO_KBPS, MAX_PHONE_CRF, MAX_RENDER_CRF = 320, 20, 16
Q = r"""['"]"""                       # either quote


def read(name):
    with open(os.path.join(SCRIPTS, name), encoding='utf-8') as fh:
        return fh.read()


problems = []
for name in sorted(n for n in os.listdir(SCRIPTS) if n.endswith('.py')):
    for n, line in enumerate(read(name).splitlines(), 1):
        for kbps in re.findall(Q + r'-b:a' + Q + r'\s*,\s*' + Q + r'(\d+)k' + Q, line):
            if int(kbps) < MIN_AUDIO_KBPS:
                problems.append(f'{name}:{n}: audio at {kbps}k (minimum {MIN_AUDIO_KBPS}k)')

phone = read('check_cuts.py').split("'--phone' in sys.argv", 1)[-1].split('print(', 1)[0]
if not re.search(Q + r'-c:a' + Q + r'\s*,\s*' + Q + 'copy' + Q, phone):
    problems.append("check_cuts.py: the phone copy must keep the render's audio ('-c:a', 'copy')")
crf = re.search(Q + r'-crf' + Q + r'\s*,\s*' + Q + r'(\d+)' + Q, phone)
if not crf or int(crf.group(1)) > MAX_PHONE_CRF:
    problems.append(f'check_cuts.py: the phone copy needs a crf of {MAX_PHONE_CRF} or less (has {crf and crf.group(1)})')
for w in re.findall(r'scale=(\d+):', phone):
    if int(w) < 1080:
        problems.append(f'check_cuts.py: the phone copy shrinks the picture to {w} wide (keep 1080)')

env = read('skillenv.py')
rc = re.search(r'^RENDER_CRF\s*=\s*(\d+)', env, re.M)
if not rc or int(rc.group(1)) > MAX_RENDER_CRF:
    problems.append(f'skillenv.py: RENDER_CRF must be {MAX_RENDER_CRF} or less (has {rc and rc.group(1)})')
if 'hyperframes_command(render_quality(args))' not in env:
    problems.append('skillenv.py: run_hyperframes must pass every command through render_quality()')

if problems:
    print('QUALITY RULE BROKEN (SKILL.md rule 9):\n' + '\n'.join(problems))
    sys.exit(1)
print(f'quality OK: audio {MIN_AUDIO_KBPS}k or copied, phone copy 1080p crf <= {MAX_PHONE_CRF} with the audio copied, '
      f'renders crf <= {MAX_RENDER_CRF}')
