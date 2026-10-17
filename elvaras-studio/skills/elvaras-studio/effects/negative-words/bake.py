#!/usr/bin/env python3
"""Step 3. Bake the camera move: work/camera.json + the source picture -> assets/zoom.mp4 (1080x1920, same frame count).

Every output frame is one or more crops of the SAME source frame (Lanczos from the highest-resolution copy of the clip).
Slow frames get one crop. Fast frames get up to 48 crops spread across the open shutter, averaged in linear light:
that is a real zoom blur (sharp at the point the camera aims at, streaking towards the edges), which CSS cannot do.
Past the lossless range of the source a light unsharp mask keeps the upscale crisp.

It also writes assets/zoom_cut.webm: the speaker alone (colour from the same baked frame, alpha from assets/subject.webm
put through the same crop), for every frame, so the words behind the head stay behind it while the camera moves.

Usage (from the slot folder; 1 to 3 minutes of CPU, so put it behind the slot runner on a shared machine):
  PY bake.py                  full bake -> assets/zoom.mp4
  PY bake.py --frames 80-92   PNG previews of those frames -> work/bake/
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = shutil.which('ffprobe') or 'ffprobe'
ap = argparse.ArgumentParser()
ap.add_argument('--out', default='assets/zoom.mp4')
ap.add_argument('--frames', default='')          # "a-b": write PNGs of these frames to work/bake/ instead of a video
args = ap.parse_args()

cam_path = os.path.join(HERE, 'work/camera.json')
if not os.path.exists(cam_path):
    sys.exit('work/camera.json is missing: run build.py first')
cam = json.load(open(cam_path))
W, H, FPS, LOSSLESS = cam['w'], cam['h'], cam['fps'], cam['lossless']
src = os.path.join(HERE, cam['src'])
sw, sh = (int(v) for v in subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                          '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip().split(',')[:2])
# Colour: swscale's default YUV<->RGB path truncates instead of rounding and loses ~0.8 luma levels per conversion (two
# conversions = a render about 2% darker than the a-roll at 1.0x). accurate_rnd on both sides brings the mean back exactly.
SWS = 'flags=accurate_rnd+full_chroma_int+full_chroma_inp'
cspace, crange = (subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_space,color_range',
                                  '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip().split(',') + ['', ''])[:2]
in_matrix = 'bt601' if cspace in ('smpte170m', 'bt470bg') else 'bt709'
in_range = 'pc' if crange == 'pc' else 'tv'
dec = subprocess.Popen([FFMPEG, '-v', 'error', '-i', src, '-vf', f'scale={SWS}:in_color_matrix={in_matrix}:in_range={in_range}:out_range=pc,format=rgb24',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL if args.frames else None)     # a preview stops reading early: no pipe noise
only, enc = None, None
out_path = os.path.join(HERE, args.out)
if args.frames:
    a, b = (int(v) for v in args.frames.split('-'))
    only = range(a, b + 1)
    os.makedirs(os.path.join(HERE, 'work/bake'), exist_ok=True)
else:
    enc = subprocess.Popen([FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-vf', f'scale={SWS}:in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p,'
                                   'setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709', '-c:v', 'libx264', '-preset', 'slow',
                            '-crf', '11', '-g', '15', '-bf', '0', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                            '-color_range', 'tv', '-movflags', '+faststart', out_path], stdin=subprocess.PIPE)

TO_LIN = ((np.arange(256) / 255.0) ** 2.2).astype(np.float32)
HALF = cam.get('half')
mdec = menc = None
if HALF:
    sub = os.path.join(HERE, 'assets/subject.webm')
    if not os.path.exists(sub):
        sys.exit('Negativo needs assets/subject.webm (the cutout)')
    mdec = subprocess.Popen([FFMPEG, '-v', 'error', '-c:v', 'libvpx-vp9', '-i', sub, '-vf', 'alphaextract,format=gray', '-f', 'rawvideo',
                             '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL if args.frames else None)
    if not args.frames:
        menc = subprocess.Popen([FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                 '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '22', '-deadline', 'good', '-cpu-used', '4',
                                 '-row-mt', '1', '-auto-alt-ref', '0', os.path.join(HERE, 'assets/zoom_cut.webm')], stdin=subprocess.PIPE)


def cut_alpha(mbuf, c):
    """the cutout's alpha through this frame's crop (middle of the shutter), edge tightened after the upscale"""
    bx = c['boxes'][len(c['boxes']) // 2]
    cov, ox, oy = cam['cover'], cam['offx'], cam['offy']
    box = ((bx[0] - ox) * cov, (bx[1] - oy) * cov, (bx[2] - ox) * cov, (bx[3] - oy) * cov)
    a = np.asarray(Image.frombuffer('L', (1080, 1920), mbuf, 'raw', 'L', 0, 1).resize((W, H), Image.BICUBIC, box=box), np.float32) / 255
    a = np.clip((a - .3) / .4, 0, 1)
    return (a * a * (3 - 2 * a) * 255 + .5).astype(np.uint8)


done = 0
for c in cam['frames']:
    mbuf = mdec.stdout.read(1080 * 1920) if mdec else None
    buf = dec.stdout.read(sw * sh * 3)
    if len(buf) < sw * sh * 3:
        sys.exit(f"the source ended at frame {c['f']}: {cam['src']} has fewer frames than the clip ({len(cam['frames'])})")
    if only is not None and c['f'] not in only:
        if c['f'] > only[-1]:
            break
        continue
    im = Image.frombuffer('RGB', (sw, sh), buf, 'raw', 'RGB', 0, 1)
    boxes = c['boxes']
    if len(boxes) == 1:
        out = im.resize((W, H), Image.LANCZOS, box=tuple(boxes[0]))
        up = c['scale'] / LOSSLESS
        if up > 1.02:                                    # upscaling: bring the edges back, gently
            out = out.filter(ImageFilter.UnsharpMask(radius=1.1 * up, percent=int(min(85, 150 * (up - 1))), threshold=2))
    else:
        acc = np.zeros((H, W, 3), np.float32)
        kern = Image.LANCZOS if len(boxes) <= 4 else Image.BICUBIC     # barely-moving frames keep the sharp kernel
        for bx in boxes:
            acc += TO_LIN[np.asarray(im.resize((W, H), kern, box=tuple(bx)))]
        acc /= len(boxes)
        out = Image.fromarray((np.clip(acc, 0, 1) ** (1 / 2.2) * 255 + .5).astype(np.uint8))
    if enc:
        enc.stdin.write(out.tobytes())
    else:
        out.save(os.path.join(HERE, f"work/bake/f{c['f']:03d}.png"))
    if HALF and HALF[0] <= c['f'] <= HALF[1]:
        if not mbuf or len(mbuf) < 1080 * 1920:
            sys.exit(f"assets/subject.webm ended before frame {c['f']}: make the cutout again (fx_new.py)")
        rgba = np.dstack([np.asarray(out), cut_alpha(mbuf, c)])
        if menc:
            menc.stdin.write(rgba.tobytes())
        else:
            Image.fromarray(rgba, 'RGBA').save(os.path.join(HERE, f"work/bake/f{c['f']:03d}_cut.png"))
    done += 1
dec.stdout.close()
dec.terminate()
dec.wait()
if mdec:
    mdec.stdout.close()
    mdec.terminate()
    mdec.wait()
if menc:
    menc.stdin.close()
    menc.wait()
    open(os.path.join(HERE, 'work/zoom_cut.sig'), 'w').write(cam.get('half_sig', ''))
    print(f'wrote assets/zoom_cut.webm: frames {HALF[0]}-{HALF[1]} (the speaker alone, for the words behind the head)')
if enc:
    enc.stdin.close()
    enc.wait()
    n = int(subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries', 'stream=nb_read_frames',
                            '-of', 'csv=p=0', out_path], capture_output=True, text=True).stdout.strip() or 0)
    print(f"wrote {args.out}: {n} frames from {cam['src']} ({sw}x{sh})")
    if n != len(cam['frames']):
        sys.exit(f'!! {n} frames baked, {len(cam["frames"])} expected')
else:
    print(f'wrote {done} preview frames to work/bake/')
