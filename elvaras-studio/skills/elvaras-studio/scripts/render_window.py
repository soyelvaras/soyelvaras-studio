#!/usr/bin/env python3
"""Fix a few seconds of an approved render without rendering the whole reel again: render only that window and
splice it into the render you already have.

Usage (run with PY):
  PY render_window.py "<project>" <from> <to> "renders/<slug>-vN.mp4" -o "renders/<slug>-vN+1.mp4"
        the reel: renders <from>-<to> of <project>/index.html, puts those frames into the base render (exact frames,
        one CRF 16 encode of the picture) and copies the base render's audio untouched -> the new version
  PY render_window.py "<project>/fx/<slot>" <from> <to> --webm -o "renders/<name>.webm"
        a sub-composition (an fx slot, a graphics pass): renders only the window as a transparent WebM. Point the
        slot at it (src = that file, media = slot start - <from>) and then fix the reel window as above.

Rules (the standard way to apply notes since 2026-10-22):
  - A note about some seconds of an approved render -> this script. A full render only when the change runs across
    the whole reel (the cut, the timing, the caption style...).
  - Build the reel first as usual (build_reel.py and any project script that edits index.html): the window is read
    from the current index.html, so it carries the fix. Everything outside the window comes from the base render.
  - Give the window a few frames of margin before and after the change; times snap to the frame grid.
  - Check the result: same frame count as the base (printed), and look at frames across both seams.
How it works: <dir>/window.html is a copy of index.html whose timeline is driven through tweenFromTo(from, to) and
whose media (video/audio with data-start) is shifted onto the window; media that is never on screen inside it is
left out, or the renderer would wait for its frames. Asset paths do not change.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skillenv  # noqa: E402

FF, FP = skillenv.tool('ffmpeg'), skillenv.tool('ffprobe')
OPEN = re.compile(r'<(?:video|audio)\b[^>]*>')


def window_html(comp, t0, t1):
    s = open(os.path.join(comp, 'index.html'), encoding='utf-8').read()
    dur = t1 - t0

    def media(m):
        whole = m.group(0)
        tag = OPEN.match(whole).group(0)
        st = re.search(r'data-start="(-?[\d.]+)"', tag)
        du = re.search(r'data-duration="([\d.]+)"', tag)
        if not st or not du:
            return whole
        a, d = float(st.group(1)), float(du.group(1))
        ms = re.search(r'data-media-start="(-?[\d.]+)"', tag)
        m0 = max(0.0, float(ms.group(1))) if ms else 0.0
        if a + d <= t0 or a >= t1:
            return ''
        na, nd, nm = max(0.0, a - t0), min(a + d, t1) - max(a, t0), m0 + max(0.0, t0 - a)
        new = re.sub(r'data-start="-?[\d.]+"', f'data-start="{na:.3f}"', tag)
        new = re.sub(r'data-duration="[\d.]+"', f'data-duration="{nd:.3f}"', new)
        if ms:
            new = re.sub(r'data-media-start="-?[\d.]+"', f'data-media-start="{nm:.3f}"', new)
        else:
            new = new.replace('data-start=', f'data-media-start="{nm:.3f}" data-start=', 1)
        return whole.replace(tag, new, 1)

    s = re.sub(r'<(video|audio)\b[^>]*>.*?</\1>', media, s, flags=re.S)
    s = re.sub(r'(id="root"[^>]*data-duration=")[\d.]+(")', lambda m: f'{m.group(1)}{dur:.3f}{m.group(2)}', s, count=1)
    hook = 'window.__timelines["main"] = tl;'
    if hook not in s:
        sys.exit('STATUS window FAILED: no window.__timelines["main"] = tl; in index.html')
    s = s.replace(hook, f'const __wt = gsap.timeline({{ paused: true }}); __wt.add(tl.tweenFromTo({t0:.4f}, {t1:.4f}, {{ ease: "none" }}));\n'
                        f'window.__timelines["main"] = __wt;', 1)
    open(os.path.join(comp, 'window.html'), 'w', encoding='utf-8', newline='\n').write(s)
    return len(re.findall(r'<(?:video|audio)[ >]', s))


def probe(f):
    r = json.loads(subprocess.run([FP, '-v', 'error', '-count_frames', '-show_entries',
                                   'stream=codec_type,r_frame_rate,nb_read_frames', '-of', 'json', f], **skillenv.TEXT).stdout)
    v = next(x for x in r['streams'] if x['codec_type'] == 'video')
    n, d = v['r_frame_rate'].split('/')
    return float(n) / float(d), int(v.get('nb_read_frames') or 0), any(x['codec_type'] == 'audio' for x in r['streams'])


def main():
    skillenv.utf8_stdio()
    args = sys.argv[1:]
    webm = '--webm' in args
    args = [a for a in args if a != '--webm']
    out = None
    if '-o' in args:
        i = args.index('-o')
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) < (3 if webm else 4) or not out:
        sys.exit(__doc__)
    comp = os.path.abspath(args[0])
    fps = 30.0
    base = None
    if not webm:
        base = args[3] if os.path.isabs(args[3]) else os.path.join(comp, args[3])
        fps, base_frames, has_audio = probe(base)
    f0, f1 = round(float(args[1]) * fps), round(float(args[2]) * fps)
    t0, t1 = f0 / fps, f1 / fps
    kept = window_html(comp, t0, t1)
    print(f'STATUS window {t0:.3f}-{t1:.3f} frames {f0}-{f1} ({f1 - f0} frames), {kept} media kept')
    hf = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hf.py'), comp, 'render', '-c', 'window.html']
    part = out if webm else os.path.join('renders', '_window.mp4')
    cmd = hf + ['-o', part, '--quality', 'high'] + (['--format', 'webm'] if webm else [])
    if subprocess.run(cmd).returncode:
        sys.exit('STATUS window FAILED: the window render did not finish')
    if webm:
        print(f'STATUS window DONE {out}  (slot media = slot start - {t0:.3f})')
        return
    part = os.path.join(comp, part)
    dst = out if os.path.isabs(out) else os.path.join(comp, out)
    fc = (f'[0:v]trim=end_frame={f0},setpts=PTS-STARTPTS[a];[1:v]trim=end_frame={f1 - f0},setpts=PTS-STARTPTS[b];'
          f'[0:v]trim=start_frame={f1},setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps={fps:g}[v]')
    cmd = [FF, '-v', 'error', '-y', '-i', base, '-i', part, '-filter_complex', fc, '-map', '[v]']
    if has_audio:
        cmd += ['-map', '0:a', '-c:a', 'copy']            # the sound does not change: copied as it is
    cmd += ['-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709',
            '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', dst]
    subprocess.run(cmd, check=True)
    _, frames, _ = probe(dst)
    ok = 'same as the base' if frames == base_frames else f'BASE HAS {base_frames}: CHECK'
    print(f'STATUS window DONE {dst}  {frames} frames ({ok}). Look at frames across {t0:.2f}s and {t1:.2f}s.')


if __name__ == '__main__':
    main()
