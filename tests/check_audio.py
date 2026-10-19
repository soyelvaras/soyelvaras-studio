#!/usr/bin/env python3
"""The voice never loses quality (SKILL.md rule 9). Fails if a Studio script encodes audio below 320k, or if the
phone copy re-encodes the render's audio instead of copying it. Reads the scripts only; needs nothing installed.

Usage:  python tests/check_audio.py      (exits 1 and names the line when the rule is broken)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'elvaras-studio', 'skills', 'elvaras-studio', 'scripts')
MIN_KBPS = 320

problems = []
for name in sorted(os.listdir(SCRIPTS)):
    if not name.endswith('.py'):
        continue
    with open(os.path.join(SCRIPTS, name), encoding='utf-8') as fh:
        for n, line in enumerate(fh, 1):
            for kbps in re.findall(r"""['"]-b:a['"]\s*,\s*['"](\d+)k['"]""", line):
                if int(kbps) < MIN_KBPS:
                    problems.append(f'{name}:{n}: audio at {kbps}k (minimum {MIN_KBPS}k): {line.strip()}')

with open(os.path.join(SCRIPTS, 'check_cuts.py'), encoding='utf-8') as fh:
    phone = fh.read().split("'--phone' in sys.argv", 1)[-1]
if not re.search(r"""['"]-c:a['"]\s*,\s*['"]copy['"]""", phone):
    problems.append("check_cuts.py: the phone copy must keep the render's audio with '-c:a', 'copy'")

if problems:
    print('AUDIO RULE BROKEN (SKILL.md rule 9):\n' + '\n'.join(problems))
    sys.exit(1)
print(f'audio OK: no script encodes audio below {MIN_KBPS}k and the phone copy keeps the audio as it is')
