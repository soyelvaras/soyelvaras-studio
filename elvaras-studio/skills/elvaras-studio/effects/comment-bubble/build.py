#!/usr/bin/env python3
"""comment-bubble (CTA): a comment field slides up under their chin, the keyword types itself on the spoken word, the
send arrow is tapped, then one of five closings builds itself (VARIANT): the posted comment, the creator typing, the reply
and something attached. 1 Mensaje directo, 2 Notificaciones, 3 Fijado + video, 4 Papel + foto, 5 Link con vista previa.

Run from the slot folder (see effect.md for the full run order):
    PY measure.py        chin + onsets -> work/measure.json
    PY build.py          writes index.html (SAFE=1 draws the safe zone)
Switches: SAFE=1 safe-zone guide (snapshots only), SFX=0 no sounds, CAPTIONS=0 accepted (this effect has no captions).
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys

# ==== CLIP (edit this) ====
# -- on-screen text (no em dashes, never "free" / "course", nothing the speaker does not say or imply in the clip)
VARIANT = 1                        # the closing: 1 Mensaje directo, 2 Notificaciones, 3 Fijado + video, 4 Papel + foto,
                                   # 5 Link con vista previa. fx_new.py fills it from the Studio Picker
KEYWORD = 'ADS'                    # the word the speaker asks people to comment, in caps
REPLY_TEXT = 'Aquí te lo comparto' # creator reply, the speaker's own words; keep it under ~22 characters
USER_NAME = 'tú'                   # generic commenter name, never a real person
PLACEHOLDER = 'Comenta aquí...'    # grey text in the empty comment field
ATTACH_TITLE = 'Cómo lo hago'      # title on the attachment: what the speaker sends, in their words
ATTACH_SUB = 'Video · toca para verlo'   # second line on the attachment (closing 1)
LINK_DOMAIN = 'soyelvaras.cl'      # the brand's own site on the link preview (closing 5). '' = none. Never someone else's
BRAND_NAME = 'Soy Elvaras'         # who replies, as the notifications show it (closing 2). The buyer's or client's brand
BRAND_MARK = 'V'                   # one letter for the brand tile on the notifications (closing 2)
THUMB = 'auto'                     # picture on the attachment: 'auto' = a frame of the clip, or a file in the slot ('assets/x.jpg')
# -- times in seconds from the slot start. Run measure.py: it prints Whisper's start and the audio onset for every
#    word. Use the audio onset minus one frame (0.03) so the visual leads the voice by a frame.
T_IN = 0.50       # field slides up: about 0.4s before "comment" (on the words leading into it)
T_FOCUS = 0.93    # onset of "comment": field focuses, caret appears
T_TYPE = 1.26     # onset of the keyword minus 0.03: first letter
KEY_GAP = 0.09    # seconds per letter. (keyword end - T_TYPE - 0.1) / (letters - 1), between 0.05 and 0.11
T_SEND = 1.57     # send tap: the end of the keyword (first breath after it)
T_DOTS = 1.88     # onset of the next phrase ("I'll"): creator typing dots. At least 0.15s before T_REPLY
T_REPLY = 2.05    # onset of "send" (the s, not the vowel): reply bubble lands
T_LINK = 2.39     # onset of the thing the speaker sends ("link", "guide"...) minus 0.03: chip resolves
T_OUT = None      # None = thread holds to the last frame (slot ends on a cut). A time = thread leaves and the plate
                  # settles back so the slot's last frame matches the a-roll again (use when the reel keeps the shot)
# -- size and place. Everything is placed from the measured chin (work/measure.json), nothing is a fixed y.
SCALE = 1.3       # thread size, 1.0 = the original demo. Shrinks by itself if the band under the chin is too small
CHIN_Y = None     # None = measured from the cutout (95th percentile while the thread is up). Or a y in frame px:
                  # the lowest the speaker's chin gets in the slot, read off work/measure_check.jpg
CHIN_GAP = 20     # clear px between chin and thread, never less
DROP = 'auto'     # 'auto' = as low as the safe zone allows (bottom edge 1456): on wide shots the speaker's torso and hands stay
                  # visible, on close-ups this equals hugging the chin. A number = px from chin to the thread top
X_CENTER = None   # None = centred under the speaker's head (measured), clamped to the safe zone. Or an x in frame px
PUSH = 'auto'     # 'auto' = lift the plate (scale from the bottom edge) only as much as the thread needs, up to
PUSH_MAX = 1.12   # PUSH_MAX; 1 = never touch the plate (the thread shrinks instead). Close-ups need the lift.
# -- look
AVATAR_FRAME = None   # frame for the creator avatar crop: pick one from work/avatar_check.jpg (eyes open). None = last frame
AVATAR_BOX = None     # (x, y, size) square crop in frame px if the automatic head crop is off. None = measured
GRADE = 'none'        # css filter on the plate. Set it to the reel's own grade so the slot matches its neighbours
SEAT = 1.0            # strength of the soft dark gradient that seats the thread on the footage (0 = off)
# -- style. The buyer's style wins: in a reel, set these from the reel's caption style (SKILL.md "The buyer's style
#    wins", effects/INDEX.md "Restyling an effect's own words"). Each font is (css family, weight, file in
#    assets/fonts): the slot holds every font the caption styles use, assets/fonts/fonts.css lists them.
#    Karaoke, for example: WORD_FONT = TEXT_FONT = ('Archivo', 900, 'Archivo-900-normal.woff2'), UPPER = True.
#    A wider typeface makes the thread wider: build.py shrinks it to the safe zone, lower SCALE if it gets small.
WORD_FONT = ('Inter Tight', 800, 'InterTight-800-normal.woff2')   # the keyword (typed and posted) and the chip label
TEXT_FONT = ('Work Sans', 500, 'WorkSans-100-900-normal.woff2')   # the reply, names and every small line
UPPER = False         # True = reply line, chip label and name in capitals (the keyword is in capitals already)
ACCENT_COL, LIGHT_COL, DARK_COL = '#C9A15B', '#F2ECDF', '#141615'   # accent (ring, caret, highlights), light (paper, words), dark (words on light)
DEEP_COL = '#13281F'  # the brand's deep colour (pinned label, paper reply, brand tile)
PUNCH_FONT = ('Bebas Neue', 400, 'BebasNeue-400-normal.woff2')          # the posted keyword
SERIF_FONT = ('Instrument Serif', 400, 'InstrumentSerif-400-italic.woff2')   # the reply in closings 3 and 4 (italic)
# ==== END CLIP ====

FF = shutil.which('ffmpeg') or 'ffmpeg'
FP = shutil.which('ffprobe') or 'ffprobe'
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SLOT = os.path.basename(os.getcwd())
CLIPJ = json.load(open('clip.json')) if os.path.exists('clip.json') else {}
if CLIPJ.get('frames'):
    NFRAMES = int(CLIPJ['frames'])
else:
    NFRAMES = int(subprocess.run([FP, '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                  'stream=nb_read_frames', '-of', 'csv=p=0', 'assets/aroll.mp4'], capture_output=True, text=True).stdout.strip())
DUR = NFRAMES / 30
# the renderer makes ceil(duration * 30) frames: 212 frames written as 7.067 came out as 213. Stay a hair under.
DUR_ATTR = f'{NFRAMES / 30 - 0.0004:.4f}'
YEL, CREAM, INK = ACCENT_COL, LIGHT_COL, DARK_COL
WF, WW, TF, TW = WORD_FONT[0], WORD_FONT[1], TEXT_FONT[0], TEXT_FONT[1]
RESTYLED = (WORD_FONT[2], TEXT_FONT[2]) != ('InterTight-800-normal.woff2', 'Inter-600-normal.woff2')
CHIP_TEXT = ''          # (the old link chip, still used to size the field)
VARIANT = int(VARIANT) if str(VARIANT).isdigit() and 1 <= int(VARIANT) <= 5 else 1


def U(s):
    """the reply, chip and name text as it is shown (capitals when the style asks for them)"""
    return s.upper() if UPPER else s
SAFE_T, SAFE_B, SAFE_L, SAFE_R, SAFE_R_LOW, LOW_Y = 220, 1470, 35, 1045, 980, 1155   # Instagram safe zone
BOTTOM = SAFE_B - 14                     # thread bottom edge when DROP is 'auto'
MARGIN_L = 48
SFX_ON = os.environ.get('SFX', '1') != '0'

# ------------------------------------------------------------------ text widths (exact with PIL, estimated without)
try:
    from PIL import ImageFont
except ImportError:
    ImageFont = None
    print("note: PIL not found, text widths are estimated. Run build.py with the skill's Python (PY) for exact fits.")
FONT_FILES = {('Inter', 500): 'Inter-500-normal.woff2', ('Inter', 600): 'Inter-600-normal.woff2',
              ('Inter Tight', 800): 'InterTight-800-normal.woff2'}
FONT_FILES[(WF, WW)] = WORD_FONT[2]
FONT_FILES[(TF, TW)] = TEXT_FONT[2]
_fonts = {}


def _font(path, px, weight):
    f = ImageFont.truetype(path, px)
    if RESTYLED:               # a font from the buyer's style: measure it at its real weight (the files are variable)
        try:
            f.set_variation_by_axes([weight])
        except (OSError, AttributeError, ValueError):
            pass
    return f


def text_w(txt, family, weight, px, ls=0.0):
    """advance width of txt in design px (ls = css letter-spacing in px)"""
    path = os.path.join('assets', 'fonts', FONT_FILES[(family, weight)])
    if ImageFont and os.path.exists(path):
        try:
            if (path, px) not in _fonts:
                _fonts[(path, px)] = _font(path, px, weight)
            return _fonts[(path, px)].getlength(txt) + ls * len(txt)
        except OSError:
            pass
    em = .66 if txt.isupper() else .52
    return len(txt) * em * px + ls * len(txt)


# ------------------------------------------------------------------ design units (1.0 = the approved demo)
TYPE_PX, KW_PX, WHO_PX, RTXT_PX, CHIP_PX = 62, 70, 33, 42, 37
AV1, AVGAP, R1 = 86, 16, 114            # comment avatar, gap to the bubble, comment row height
BUB_PL, BUB_GAP, BUB_PR = 34, 18, 46    # comment bubble padding / gap between name and keyword
HEART_OUT = 24                          # heart badge overhang right of the bubble
ROW_GAP = 12                            # between comment row and reply row
INDENT, RAV, RB_X = 94, 78, 94          # reply row indent, creator avatar, reply bubble x inside the row
RB_PL, RB_GAP, RB_PR = 38, 24, 20       # reply bubble padding (inline: text + chip on one line)
CHIP_H, CHIP_PL, CHIP_ICON, CHIP_GAP, CHIP_PR = 80, 22, 36, 10, 30
R2_INLINE = 120
ST_PT, ST_LINE, ST_GAP, ST_PB, ST_PR = 20, 52, 12, 22, 38     # stacked reply: text above the chip
R2_STACK = ST_PT + ST_LINE + ST_GAP + CHIP_H + ST_PB
FIELD_H, FIELD_W, FIELD_TEXT_X, SEND = 116, 876, 120, 84


def key_w(ch):
    return round(text_w(ch, WF, WW, TYPE_PX)) + 5      # fixed boxes: the caret position is known without the browser


def widths():
    kw = text_w(KEYWORD, WF, WW, KW_PX, .01 * KW_PX)
    who = text_w(U(USER_NAME), TF, TW, WHO_PX, -.5)
    bub = BUB_PL + who + BUB_GAP + kw + BUB_PR
    rtxt = text_w(U(REPLY_TEXT), TF, TW, RTXT_PX, -.7)
    chip = CHIP_PL + CHIP_ICON + CHIP_GAP + text_w(U(CHIP_TEXT), WF, WW, CHIP_PX, -.2) + CHIP_PR
    typed = sum(key_w(c) for c in KEYWORD)
    return {'bub': bub, 'row1': AV1 + AVGAP + bub + HEART_OUT, 'chip': chip,
            'rb_inline': RB_PL + rtxt + RB_GAP + chip + RB_PR, 'rb_stack': RB_PL + max(rtxt + 8, chip) + ST_PR,
            'field_min': FIELD_TEXT_X + typed + 46 + SEND + 16}


# ------------------------------------------------------------------ measured head / chin
def measured():
    """(chin_y, head_cx, head_w, per-frame list or None) for the frames the thread is on screen"""
    per = None
    if os.path.exists('work/measure.json'):
        per = json.load(open('work/measure.json')).get('frames')
    if per:
        a = max(0, min(len(per) - 1, round(T_IN * 30)))
        win = [p for p in per[a:] if p.get('head_w', 0) > 0] or per
        chins = sorted(p['chin'] for p in win)
        chin = chins[min(len(chins) - 1, int(.95 * len(chins)))]
        cx = sorted(p['cx'] for p in win)[len(win) // 2]
        hw = sorted(p['head_w'] for p in win)[len(win) // 2]
    else:
        chin, cx, hw = None, 540, 0
    if CHIN_Y is not None:
        chin = CHIN_Y
    if chin is None:
        sys.exit('no chin position: run measure.py first (needs assets/subject.webm) or set CHIN_Y in the CLIP block')
    return chin, (X_CENTER if X_CENTER is not None else cx), hw, per


def layout():
    """pick the biggest scale <= SCALE (and inline before stacked reply) that fits between chin and safe line"""
    W = widths()
    chin, cx, head_w, per = measured()
    pmax = PUSH_MAX if PUSH == 'auto' else float(PUSH)
    s = SCALE
    while s >= .6:
        for mode in ('inline', 'stack'):
            r2 = R2_INLINE if mode == 'inline' else R2_STACK
            row2 = INDENT + RB_X + (W['rb_inline'] if mode == 'inline' else W['rb_stack'])
            tw, th = max(W['row1'], row2) * s, (R1 + ROW_GAP + r2) * s
            # where the top goes, and whether the plate has to lift for it
            if DROP == 'auto':          # bottom-anchored: the chin has to be at or above `need`, lift the plate if not
                top = BOTTOM - th
                need = top - CHIN_GAP
                push = 1.0 if chin <= need else (1920 - need) / (1920 - chin)
            else:                       # hung a fixed distance under the chin, plate untouched
                top = chin + max(float(DROP), CHIN_GAP)
                push = 1.0
            chin_eff = 1920 - (1920 - chin) * push
            bottom = top + th
            right = SAFE_R_LOW if bottom > LOW_Y else SAFE_R
            ok = (tw <= right - MARGIN_L and push <= pmax + 1e-6 and top >= chin_eff + CHIN_GAP - .5
                  and bottom <= BOTTOM + .5 and W['field_min'] * s <= right - MARGIN_L)
            if ok:
                x0 = min(max(cx - tw / 2, MARGIN_L), right - tw)
                fw = min(max(tw, W['field_min'] * s, min(FIELD_W * s, 640 * s)), right - MARGIN_L)
                fx = min(max(x0 + tw / 2 - fw / 2, MARGIN_L), right - fw)
                return dict(s=s, mode=mode, r2=r2, x0=x0, y0=top, tw=tw, th=th, push=push, chin=chin, chin_eff=chin_eff,
                            cx=cx, head_w=head_w, right=right, fx=fx, fw=fw, fy=bottom - FIELD_H * s, W=W, per=per)
        s = round(s - .02, 2)
    sys.exit('the thread does not fit under their chin even at 0.6 scale: raise PUSH_MAX, shorten the texts or pick another shot')


# ------------------------------------------------------------------ icons (generic, no platform marks)
def person(size, uid):
    """grey placeholder avatar: head + shoulders (unique ids: a hidden twin would blank the other one)"""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 80 80"><defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#D5D8DF"/><stop offset="1" stop-color="#9097A6"/></linearGradient>'
            f'<clipPath id="c{uid}"><circle cx="40" cy="40" r="40"/></clipPath></defs>'
            f'<g clip-path="url(#c{uid})"><rect width="80" height="80" fill="url(#g{uid})"/>'
            '<circle cx="40" cy="31" r="14" fill="#fff" fill-opacity=".94"/>'
            '<ellipse cx="40" cy="76" rx="27" ry="23" fill="#fff" fill-opacity=".94"/></g></svg>')


def arrow_up(color, size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M12 19.2V5.2M5.6 11.4L12 5l6.4 6.4"/></svg>')


def heart(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><path fill="#C9A15B" d="M12 21.2s-7.6-4.6-9.6-9.5C1 8.1 3 4.6 6.6 4.6c2 0 '
            '3.6 1 5.4 3.1 1.8-2.1 3.4-3.1 5.4-3.1 3.6 0 5.6 3.5 4.2 7.1-2 4.9-9.6 9.5-9.6 9.5z"/></svg>')


def link(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{INK}" stroke-width="2.7" stroke-linecap="round" '
            'stroke-linejoin="round" style="flex:none"><path d="M10.2 13.8a4.3 4.3 0 006.1 0l3-3a4.3 4.3 0 00-6.1-6.1l-1.3 1.3"/>'
            '<path d="M13.8 10.2a4.3 4.3 0 00-6.1 0l-3 3a4.3 4.3 0 006.1 6.1l1.3-1.3"/></svg>')


def reply_avatar(L):
    """square crop of their head from the clip -> assets/reply_avatar.jpg. Returns the img html, or a grey avatar."""
    f = AVATAR_FRAME if AVATAR_FRAME is not None else NFRAMES - 1
    f = max(0, min(NFRAMES - 1, int(f)))
    box = AVATAR_BOX
    if box is None and L['per']:
        p = L['per'][min(f, len(L['per']) - 1)]
        if p.get('head_w', 0) > 40:
            side = 1.5 * p['head_w']
            box = (p['cx'] - side / 2, p['top'] - .06 * side, side)
    if box is None:
        return person(round(RAV * L['s']), 'r')
    x, y, side = box
    side = int(min(side, 1080, 1920))
    x, y = int(min(max(0, x), 1080 - side)), int(min(max(0, y), 1920 - side))
    subprocess.run([FF, '-v', 'error', '-y', '-i', 'assets/aroll.mp4', '-vf',
                    f'select=eq(n\\,{f}),crop={side}:{side}:{x}:{y},eq=saturation=0.86:contrast=1.04,scale=240:240:flags=lanczos',
                    '-frames:v', '1', '-q:v', '2', 'assets/reply_avatar.jpg'], check=True)
    return '<img src="assets/reply_avatar.jpg" alt="" />'


# ------------------------------------------------------------------ the five closings (VARIANT 1..5)
# Every closing is a message sequence: the posted comment, then the creator's reply with something attached. Each one is
# drawn in a box of design px (VARIANTS[v]['box']) that is scaled to fit between the chin and the safe line. All colours
# and faces come from the CLIP block, so a client's brand only changes those lines.
VARIANT_NAMES = {1: 'Mensaje directo', 2: 'Notificaciones', 3: 'Fijado + video', 4: 'Papel + foto', 5: 'Link con vista previa'}
VBOX = {1: (960, 500), 2: (920, 370), 3: (640, 450), 4: (860, 470), 5: (700, 410)}


def vlayout():
    """box size, scale, place and plate lift for the chosen closing"""
    w, h = VBOX[VARIANT]
    chin, cx, head_w, per = measured()
    pmax = PUSH_MAX if PUSH == 'auto' else float(PUSH)
    s = min(1.0, (1080 - 2 * MARGIN_L) / w)
    while s >= .6:
        top = BOTTOM - h * s
        need = top - CHIN_GAP
        push = 1.0 if chin <= need else (1920 - need) / (1920 - chin)
        if push <= pmax + 1e-6:
            bx = min(max(cx - w * s / 2, MARGIN_L), 1080 - MARGIN_L - w * s)
            return dict(s=s, w=w, h=h, x0=bx, y0=top, tw=w * s, th=h * s, push=push, chin=chin,
                        chin_eff=1920 - (1920 - chin) * push, cx=cx, head_w=head_w, per=per)
        s = round(s - .02, 2)
    sys.exit('the closing does not fit under their chin even at 0.6 scale: raise PUSH_MAX or pick another shot')


def attach_thumb():
    """the attachment picture: THUMB, or a frame of the clip itself"""
    if THUMB != 'auto' and os.path.exists(THUMB):
        return THUMB
    f = max(0, NFRAMES - 8)
    subprocess.run([FF, '-v', 'error', '-y', '-i', 'assets/aroll.mp4', '-vf',
                    f'select=eq(n\\,{f}),scale=360:640:force_original_aspect_ratio=increase,crop=360:640',
                    '-frames:v', '1', '-q:v', '3', 'assets/attach.jpg'], check=True)
    return 'assets/attach.jpg'


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def variant_parts(av_html, thumb):
    """(html, css) for VARIANT, positions in design px inside the box"""
    kw, rp, who, nm = esc(KEYWORD), esc(U(REPLY_TEXT)), esc(U(USER_NAME)), esc(BRAND_NAME)
    at, sub, dom, mk = esc(ATTACH_TITLE), esc(ATTACH_SUB), esc(LINK_DOMAIN), esc(BRAND_MARK)
    gen = '<div class="vgen"></div>'
    play = '<i class="vplay"></i>'
    th = f'<div class="vthumb" style="background-image:url({thumb})">{play}</div>'
    if VARIANT == 1:      # direct message: your bubble right, reply + attached video left
        html = f'''
      <div id="vu1" class="v" style="right:60px;top:2px"><span class="vmuted">{who}</span></div>
      <div id="vu" class="v vpunch" style="right:50px;top:46px;background:var(--accent);color:var(--ink);font-size:100px;line-height:1;padding:20px 48px 12px;border-radius:52px 52px 14px 52px">{kw}</div>
      <div id="vu2" class="v" style="right:58px;top:178px"><span class="vmuted" style="font-size:24px">Visto</span></div>
      <div id="vav" class="v vav" style="left:2px;top:222px;width:84px;height:84px">{av_html}</div>
      <div id="vdots" class="v vdots" style="left:110px;top:220px"><i></i><i></i><i></i></div>
      <div id="vr" class="v vui" style="left:110px;top:216px;font-size:40px;font-weight:500;padding:22px 34px;border-radius:44px 44px 44px 12px;color:var(--paper)">{rp}</div>
      <div id="va" class="v vui" style="left:110px;top:312px;width:560px;height:180px;border-radius:28px;overflow:hidden;display:flex">
        <div style="width:140px;height:180px;flex:none;position:relative">{th}</div>
        <div style="padding:36px 28px"><b style="display:block;color:var(--paper);font-size:38px;font-weight:700">{at}</b>
          <span style="display:block;color:var(--accent);font-size:28px;margin-top:10px;font-weight:600">{sub}</span></div></div>'''
    elif VARIANT == 2:    # phone notifications: "you commented", then "they replied" with the video
        n = ('background:rgba(30,32,36,.92);border-radius:40px;padding:24px 30px;display:flex;gap:24px;align-items:center;'
             'box-shadow:0 26px 60px rgba(0,0,0,.5),0 6px 16px rgba(0,0,0,.3)')
        ic = f'<div class="vic">{mk}</div>'
        hd = f'<div class="vmuted" style="font-size:24px;letter-spacing:.08em;text-transform:uppercase">{nm} · ahora</div>'
        html = f'''
      <div id="vu" class="v" style="left:0;top:10px;width:920px;{n}">{ic}<div>{hd}
        <div style="color:var(--paper);font-size:36px;font-weight:500;margin-top:6px">Comentaste <b style="color:var(--accent);font-weight:800">{kw}</b></div></div></div>
      <div id="vr" class="v" style="left:0;top:176px;width:900px;{n}">{ic}<div>{hd}
        <div style="color:var(--paper);font-size:36px;font-weight:500;margin-top:6px">Te respondió:<br>{rp}</div></div>
        <div id="va" style="width:104px;height:136px;border-radius:16px;overflow:hidden;flex:none;margin-left:auto;position:relative">{th}</div></div>'''
    elif VARIANT == 3:    # pinned comment + video reply
        html = f'''
      <div id="vu" class="v" style="left:0;top:0;width:600px;background:var(--paper);border-radius:34px;padding:20px 30px 22px">
        <div style="color:var(--deep);font-size:24px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;display:flex;gap:10px;align-items:center">
          <svg width="22" height="30" viewBox="0 0 22 30"><path d="M4 2h14l-3 9 5 6H2l5-6z M11 17v12" fill="currentColor" stroke="currentColor" stroke-width="2"/></svg>Fijado</div>
        <div style="display:flex;align-items:center;gap:20px;margin-top:10px">{gen}<div>
          <div style="color:rgba(20,22,28,.55);font-size:28px;font-weight:600">{who}</div>
          <div class="vpunch" style="font-size:92px;line-height:.9;color:var(--ink)">{kw}</div></div></div></div>
      <svg id="vline" class="v" style="left:70px;top:170px" width="60" height="96"><path d="M8 0 V 56 Q 8 84 44 84" fill="none" stroke="rgba(242,236,223,.55)" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      <div id="vr" class="v" style="left:30px;top:254px;display:flex;align-items:center;gap:28px">
        <div id="va" style="width:190px;height:190px;border-radius:50%;padding:8px;background:conic-gradient(var(--accent) 0 72%,rgba(255,255,255,.25) 72%)">
          <div style="width:100%;height:100%;border-radius:50%;overflow:hidden;position:relative">{th}</div></div>
        <div><b class="vmuted" style="display:block;font-size:28px;letter-spacing:.06em;text-transform:uppercase">Respondió con video</b>
          <span class="vserif" style="display:block;color:var(--paper);font-size:62px;line-height:1.02;margin-top:6px;white-space:normal;width:330px">{rp}</span></div></div>'''
    elif VARIANT == 4:    # paper bubbles + a photo of the video
        html = f'''
      <div id="vu" class="v" style="left:430px;top:4px;background:var(--paper);color:var(--deep);border-radius:40px 40px 10px 40px;padding:16px 40px 8px;transform:rotate(-3deg)">
        <small style="display:block;font-size:24px;font-weight:700;letter-spacing:.2em;opacity:.8">{who.upper()} COMENTASTE</small>
        <b class="vpunch" style="display:block;font-size:112px;line-height:.95;font-weight:400">{kw}</b></div>
      <div id="vr" class="v vserif" style="left:0;top:210px;background:var(--deep);color:var(--paper);border-radius:40px 40px 40px 10px;padding:20px 34px;font-size:56px;transform:rotate(1.5deg);box-shadow:inset 0 0 0 2px var(--accent)">{rp}</div>
      <div id="va" class="v" style="left:530px;top:174px;background:#fff;padding:14px 14px 56px;transform:rotate(5deg);width:230px">
        <div style="width:202px;height:200px;position:relative">{th}</div>
        <div class="vhand" style="position:absolute;left:0;right:0;bottom:10px;text-align:center;font-size:38px;color:var(--ink)">{at.lower()}</div></div>'''
    else:                 # comment + reply with a link preview
        html = f'''
      <div id="vu" class="v" style="left:0;top:0;display:flex;align-items:center;gap:20px">{gen}
        <div style="background:rgba(255,255,255,.95);border-radius:40px;padding:12px 34px 8px">
          <small style="display:block;color:rgba(20,22,28,.55);font-size:24px;font-weight:600">{who}</small>
          <b class="vpunch" style="font-size:80px;line-height:1;color:var(--ink);font-weight:400">{kw}</b></div></div>
      <svg id="vline" class="v" style="left:36px;top:82px" width="70" height="120"><path d="M6 0 V 80 Q 6 106 60 106" fill="none" stroke="rgba(242,236,223,.55)" stroke-width="5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      <div id="vr" class="v vui" style="left:100px;top:154px;width:600px;border-radius:34px;overflow:hidden">
        <div style="padding:20px 26px 16px;color:var(--paper);font-size:38px;font-weight:500;display:flex;align-items:center;gap:18px">
          <div class="vav" style="width:60px;height:60px;flex:none">{av_html}</div>{rp}</div>
        <div id="va" style="display:flex;background:rgba(255,255,255,.06);border-top:1px solid rgba(255,255,255,.08)">
          <div style="width:170px;height:150px;flex:none;position:relative">{th}</div>
          <div style="padding:28px 24px"><b style="display:block;color:var(--paper);font-size:34px;font-weight:700">{at}</b>
            <span style="display:block;color:var(--accent);font-size:26px;font-weight:600;margin-top:8px">{dom}</span></div></div></div>'''
    css = f'''
#vbox{{position:absolute;transform-origin:0 0;z-index:11;font-family:'{TF}';
  --accent:{YEL};--paper:{CREAM};--ink:{INK};--deep:{DEEP_COL};--muted:rgba(242,236,223,.62)}}
#vbox .v{{position:absolute;white-space:nowrap}}
#vbox .vui{{background:rgba(17,19,23,.95)}}
#vbox .v,#vbox .vui{{box-shadow:0 26px 60px rgba(0,0,0,.5),0 6px 16px rgba(0,0,0,.3)}}
#vu1,#vu2,#vline,#vdots{{box-shadow:none!important}}
#vbox .vmuted{{color:var(--muted);font-size:28px;font-weight:600}}
#vbox .vpunch{{font-family:'{PUNCH_FONT[0]}';font-weight:{PUNCH_FONT[1]}}}
#vbox .vserif{{font-family:'{SERIF_FONT[0]}';font-style:italic;font-weight:{SERIF_FONT[1]}}}
#vbox .vhand{{font-family:'Caveat';font-weight:600}}
#vbox .vav{{border-radius:50%;overflow:hidden;box-shadow:0 0 0 4px var(--accent)}}
#vbox .vav img,#vbox .vav svg{{width:100%;height:100%;object-fit:cover;display:block}}
#vbox .vgen{{width:72px;height:72px;border-radius:50%;flex:none;background:#cfc9bd;position:relative;overflow:hidden}}
#vbox .vgen:after{{content:'';position:absolute;left:28%;top:20%;width:44%;height:44%;border-radius:50%;background:#f4f1ea}}
#vbox .vthumb{{position:absolute;inset:0;background-size:cover;background-position:center 30%}}
#vbox .vplay{{position:absolute;left:50%;top:50%;width:0;height:0;transform:translate(-35%,-50%);border-left:30px solid #fff;
  border-top:19px solid transparent;border-bottom:19px solid transparent;filter:drop-shadow(0 2px 6px rgba(0,0,0,.6))}}
#vbox .vic{{width:84px;height:84px;border-radius:22px;background:var(--deep);flex:none;display:flex;align-items:center;justify-content:center;
  color:var(--accent);font-family:'{SERIF_FONT[0]}';font-style:italic;font-size:58px;box-shadow:inset 0 0 0 3px var(--accent)}}
#vbox .vdots{{width:130px;height:72px;border-radius:36px 36px 36px 12px;background:rgba(20,22,28,.95);display:flex;align-items:center;justify-content:center;gap:11px}}
#vbox .vdots i{{width:14px;height:14px;border-radius:50%;background:rgba(255,248,239,.85)}}'''
    return html, css


def variant_tweens(T, sfx, tp):
    """the closing builds in four beats: comment (tp), typing (T_DOTS), reply (T_REPLY), attachment (T_LINK). When the
    speaker says them back to back the beats keep their order: each one waits for the one before to land."""
    TD = max(T_DOTS, tp + .18)
    TR = max(T_REPLY, TD + .16)
    TL = max(T_LINK, TR + .2)

    def pop(sel, t, frm, d=.42, ease='back.out(1.7)'):
        T(f"gsap.set('{sel}',{{autoAlpha:0}});")
        T(f"tl.fromTo('{sel}',{{autoAlpha:0,{frm}}},{{autoAlpha:1,x:0,y:0,scale:1,duration:{d},ease:'{ease}',immediateRender:false}},{t:.3f});")
    rot = {'#vu': -3 if VARIANT == 4 else 0, '#vr': 1.5 if VARIANT == 4 else 0, '#va': 5 if VARIANT == 4 else 0}
    def popr(sel, t, frm, extra_rot, d=.46):
        T(f"gsap.set('{sel}',{{autoAlpha:0}});")
        T(f"tl.fromTo('{sel}',{{autoAlpha:0,{frm},rotation:{rot[sel] + extra_rot}}},{{autoAlpha:1,x:0,y:0,scale:1,rotation:{rot[sel]},duration:{d},ease:'back.out(1.6)',immediateRender:false}},{t:.3f});")
    # 1. the comment
    if VARIANT == 2:
        pop('#vu', tp, "y:-40,scale:.96", .5, 'expo.out')
    elif VARIANT == 4:
        popr('#vu', tp, "y:40,scale:.6", -9)
    else:
        pop('#vu', tp, "y:40,scale:.7")
    if VARIANT == 1:
        pop('#vu1', tp + .05, "y:10", .3, 'power2.out')
        pop('#vu2', TD, "y:6", .3, 'power2.out')
    sfx.append(('pop', tp + .06, .20))
    # 2. typing / the thread line
    if VARIANT == 1:
        pop('#vav', TD, "scale:0", .32, 'back.out(2.2)')
        pop('#vdots', TD + .03, "scale:.4", .2, 'back.out(2)')
        for j in range(3):
            for rep in range(max(1, int((TR - TD - .1) / .42) + 1)):
                T(f"tl.to('#vdots i:nth-child({j + 1})',{{y:-10,duration:.09,ease:'power2.out',yoyo:true,repeat:1}},{TD + .07 + j * .05 + rep * .42:.3f});")
        T(f"tl.set('#vdots',{{autoAlpha:0}},{TR:.3f});")
    if VARIANT in (3, 5):
        T(f"tl.to('#vline path',{{strokeDashoffset:0,duration:.26,ease:'power2.out'}},{TD:.3f});")
    # 3. the reply
    if VARIANT == 2:
        pop('#vr', TR, "y:-40,scale:.96", .5, 'expo.out')
    elif VARIANT == 4:
        popr('#vr', TR, "x:-40,scale:.6", 6)
    else:
        pop('#vr', TR, "x:-30,scale:.6")
    sfx.append(('whoosh-short', TR + .04, .20))
    # 4. the attachment
    if VARIANT == 4:
        popr('#va', TL, "y:-90,scale:.8", 18, .55)
    elif VARIANT == 3:
        pop('#va', TL - .25 if TL - .25 > TR else TR, "scale:0", .46, 'back.out(2)')
    else:
        pop('#va', TL, "y:24,scale:.85", .42, 'back.out(2.2)')
    sfx.append(('click-soft', TL, .45))
    end = T_OUT if T_OUT is not None else DUR
    t = TL + .7
    k = 0
    while t + .5 < end and k < 3:      # a soft "tap me" on the play button while the closing holds
        T(f"tl.to('#vbox .vplay',{{scale:1.25,duration:.16,ease:'power2.out',yoyo:true,repeat:1}},{t:.3f});")
        t += 1.1
        k += 1
    if T_OUT is not None:
        T(f"tl.to('#vbox',{{autoAlpha:0,y:18,filter:'blur(6px)',duration:.22,ease:'power2.in'}},{T_OUT:.3f});")
        T(f"tl.to('#seat',{{autoAlpha:0,duration:.3,ease:'power1.in'}},{T_OUT:.3f});")


# ------------------------------------------------------------------ the effect
def comment_bubble(L, V):
    """returns (html, tweens, sfx). L = the field's layout, V = the closing's box. The field types the keyword, then the
    chosen closing (VARIANT) builds itself in four beats."""
    s = L['s']
    P = lambda v: round(v * s, 2)                  # design px -> frame px (the field)
    J, sfx = [], []
    T = J.append
    keys = ''.join(f'<span id="k{i}" class="k" style="width:{P(key_w(c))}px">{c}</span>' for i, c in enumerate(KEYWORD))
    send_cx = L['fw'] - P(16 + SEND / 2)           # send button centre, field-relative
    vhtml, vcss = variant_parts(reply_avatar(L), attach_thumb())
    html = f'''
  <div id="seat"></div>
  <div id="cbui">
    <div id="field" style="left:{L['fx']:.1f}px;top:{L['fy']:.1f}px;width:{L['fw']:.1f}px;height:{P(FIELD_H)}px">
      <div id="fring"></div>
      <div id="fav">{person(P(76), 'f')}</div>
      <div id="ph" style="left:{P(FIELD_TEXT_X + 14)}px">{esc(PLACEHOLDER)}</div>
      <div id="typed" style="left:{P(FIELD_TEXT_X)}px">{keys}</div>
      <div id="caret" style="left:{P(FIELD_TEXT_X - 1)}px"></div>
      <div id="send"><div id="sendoff">{arrow_up('rgba(255,255,255,.55)', P(42))}</div><div id="sendon">{arrow_up(INK, P(42))}</div></div>
      <div id="tapring" style="left:{send_cx:.1f}px;top:{P(FIELD_H / 2)}px"></div>
      <div id="tap" style="left:{send_cx:.1f}px;top:{P(FIELD_H / 2)}px"></div>
    </div>
  </div>
  <div id="vbox" style="left:{V['x0']:.1f}px;top:{V['y0']:.1f}px;width:{V['w']}px;height:{V['h']}px;transform:scale({V['s']:.4f})">{vhtml}
  </div>'''

    # ---- initial states
    T("gsap.set('#seat',{autoAlpha:0});")
    T(f"gsap.set('#field',{{autoAlpha:0,y:{P(84)},scale:.94,filter:'blur(10px)',transformOrigin:'50% 50%'}});")
    T("gsap.set(['#fav','#send'],{scale:.5,autoAlpha:0});")
    T("gsap.set(['#ph','#fring','#caret','#sendon','#tap','#tapring'],{autoAlpha:0});")
    T(f"gsap.set('.k',{{autoAlpha:0,scale:.4,y:{P(14)}}});")
    T(f"gsap.set('#tap',{{xPercent:-50,yPercent:-50,scale:1.25,x:{P(10)},y:{P(18)}}});gsap.set('#tapring',{{xPercent:-50,yPercent:-50}});")

    # ---- 1. field slides up
    T(f"tl.to('#seat',{{autoAlpha:1,duration:.6,ease:'power1.out'}},{T_IN:.3f});")
    T(f"tl.to('#field',{{autoAlpha:1,duration:.14,ease:'power1.out'}},{T_IN:.3f});")
    T(f"tl.to('#field',{{y:0,scale:1,filter:'blur(0px)',duration:.56,ease:'expo.out'}},{T_IN:.3f});")
    T(f"tl.to('#fav',{{scale:1,autoAlpha:1,duration:.34,ease:'back.out(2)'}},{T_IN + .10:.3f});")
    # the placeholder must finish fading in before the first letter hides it (a slot that opens right on
    # "comment" leaves little room): start no later than focus, end at least a frame before the first letter
    ph_t0 = min(T_IN + .14, T_FOCUS)
    ph_d = max(.03, min(.2, T_TYPE - ph_t0 - .04))
    T(f"tl.to('#ph',{{autoAlpha:1,duration:{ph_d:.3f},ease:'power1.out'}},{ph_t0:.3f});")
    T(f"tl.to('#send',{{scale:1,autoAlpha:1,duration:.34,ease:'back.out(2)'}},{T_IN + .17:.3f});")

    # ---- 2. "comment": focus ring + caret
    T(f"tl.to('#fring',{{autoAlpha:1,duration:.2,ease:'power2.out'}},{T_FOCUS:.3f});")
    T(f"tl.to('#ph',{{autoAlpha:.55,duration:{min(.2, max(.03, T_TYPE - max(T_FOCUS, ph_t0 + ph_d) - .04)):.3f}}},{max(T_FOCUS, ph_t0 + ph_d):.3f});")
    T(f"tl.set('#caret',{{autoAlpha:1}},{T_FOCUS:.3f});")
    if T_TYPE - T_FOCUS > .32:   # one blink while the speaker finishes the word
        T(f"tl.set('#caret',{{autoAlpha:0}},{T_FOCUS + .15:.3f});tl.set('#caret',{{autoAlpha:1}},{T_FOCUS + .25:.3f});")

    # ---- 3. keyword types itself, one key per tick
    cum = 0
    for i, c in enumerate(KEYWORD):
        t = T_TYPE + i * KEY_GAP
        cum += key_w(c)
        if i == 0:
            T(f"tl.set('#ph',{{autoAlpha:0}},{t:.3f});")
            T(f"tl.to('#sendon',{{autoAlpha:1,duration:.12}},{t:.3f});")
            T(f"tl.to('#send',{{scale:1.16,duration:.09,ease:'power2.out'}},{t:.3f});")
            T(f"tl.to('#send',{{scale:1,duration:{max(.05, min(.22, T_SEND - t - .1)):.3f},ease:'back.out(2.4)'}},{t + .093:.3f});")
        T(f"tl.to('#k{i}',{{autoAlpha:1,scale:1,y:0,duration:.16,ease:'back.out(2.6)'}},{t:.3f});")
        T(f"tl.set('#caret',{{x:{P(cum + 4)}}},{t:.3f});")
        bump = min(.034, KEY_GAP * .38)
        if t >= T_IN + .57:      # the field's own entrance still owns its scale before that
            T(f"tl.to('#field',{{scale:1.014,duration:{bump:.3f},ease:'power1.out'}},{t:.3f});")
            T(f"tl.to('#field',{{scale:1,duration:{bump * 1.3:.3f},ease:'power1.inOut'}},{t + bump + .001:.3f});")
        sfx.append(('click-soft', t, .60))

    # ---- 4. send arrow tapped (back-to-back tweens of one property leave a 6 ms gap: lint flags float-equal ends)
    T(f"tl.to('#tap',{{autoAlpha:1,scale:1,x:0,y:0,duration:.12,ease:'power3.out'}},{T_SEND - .13:.3f});")
    T(f"tl.to('#tap',{{scale:.8,duration:.044,ease:'power2.in'}},{T_SEND:.3f});")
    T(f"tl.to('#tap',{{autoAlpha:0,scale:1.2,duration:.16,ease:'power2.out'}},{T_SEND + .05:.3f});")
    T(f"tl.to('#send',{{scale:.82,duration:.044,ease:'power2.in'}},{T_SEND:.3f});")
    T(f"tl.to('#send',{{scale:1,duration:.16,ease:'back.out(3)'}},{T_SEND + .05:.3f});")
    T(f"tl.set('#tapring',{{autoAlpha:.9,scale:1}},{T_SEND + .03:.3f});")
    T(f"tl.to('#tapring',{{autoAlpha:0,scale:1.7,duration:.3,ease:'power2.out'}},{T_SEND + .03:.3f});")
    T(f"tl.set('#caret',{{autoAlpha:0}},{T_SEND:.3f});")
    sfx.append(('click', T_SEND, .70))

    # ---- 5. the field lets go, the closing takes over
    tp = T_SEND + .07
    T(f"tl.to('#field',{{y:{P(16)},scale:.96,autoAlpha:0,filter:'blur(8px)',duration:.12,ease:'power2.in'}},{tp:.3f});")
    T(f"tl.set('#field',{{autoAlpha:0}},{tp + .125:.3f});")
    variant_tweens(T, sfx, tp + .05)
    return html, J, sfx, vcss


def plate(L):
    """the footage lifts as the field opens (scale from the bottom edge) only when the thread needs the room"""
    tw = [f"gsap.set('#bgv',{{filter:'{GRADE}'}});"] if GRADE and GRADE != 'none' else []
    p = L['push']
    if p <= 1.001:
        return tw
    a = max(0, T_IN - .08)
    tw.append(f"tl.to('#stage',{{scale:{p:.4f},duration:.9,ease:'power3.inOut'}},{a:.3f});")
    if T_OUT is None:
        tw.append(f"tl.to('#stage',{{scale:{p + .022:.4f},duration:{max(.1, DUR - a - .9):.3f},ease:'sine.out'}},{a + .9:.3f});")
    else:
        d = max(.2, min(.6, DUR - T_OUT - .02))
        tw.append(f"tl.to('#stage',{{scale:1,duration:{d:.3f},ease:'power3.inOut'}},{max(a + .92, T_OUT + .04):.3f});")
    return tw


SFX_LEN = {'whoosh-short': .57, 'pop': .72, 'sparkle': 1.8, 'click': .3, 'click-soft': .36}
SFX_LEAD = {'whoosh-short': .118, 'pop': .117, 'sparkle': 0, 'click': .048, 'click-soft': .048}   # silence before the transient
SFX_GAIN = 0.75   # house level: all sounds 25% under the template base


def audio(sfx):
    out, lanes = [], []
    timed = sorted(((name, max(0, t - SFX_LEAD[name]), vol) for name, t, vol in sfx), key=lambda x: x[1])   # transient ON the beat
    for k, (name, t, vol) in enumerate(timed):
        d = min(SFX_LEN[name], DUR - t)
        if d <= .03:
            continue
        lane = next((i for i, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0)
            lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol * SFX_GAIN:.3f}"></audio>')
    return out


BASE_CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}
#stage{position:absolute;inset:0;transform-origin:50% 100%}
.full{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
#cbui{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:10}
#elbow{position:absolute;left:0;top:0}
'''

# design px: every px value below is multiplied by the layout scale (see scale_css)
UI_CSS = '''
/* ---- comment field */
#field{position:absolute;border-radius:58px;background:rgba(22,24,31,.96);
  box-shadow:0 30px 70px rgba(0,0,0,.52),0 6px 18px rgba(0,0,0,.32),inset 0 0 0 2px rgba(255,255,255,.15),inset 0 3px 0 rgba(255,255,255,.07)}
#fring{position:absolute;left:-3px;top:-3px;right:-3px;bottom:-3px;border-radius:61px;border:3px solid __YEL__;box-shadow:0 0 36px rgba(201,161,91,.30),inset 0 0 18px rgba(201,161,91,.10)}
#fav{position:absolute;left:20px;top:20px;width:76px;height:76px;border-radius:50%;overflow:hidden}
#fav svg,#cav svg,#rav svg{display:block}
#ph{position:absolute;top:0;height:116px;font:__PW__ 40px '__TF__';line-height:116px;color:rgba(255,248,239,.5);letter-spacing:-.6px;white-space:nowrap__UP__}
#typed{position:absolute;top:0;height:116px;display:flex;align-items:center}
.k{display:inline-block;text-align:center;font:__WW__ 62px '__WF__';line-height:116px;color:__CREAM__;transform-origin:50% 70%}
#caret{position:absolute;top:30px;width:5px;height:56px;border-radius:3px;background:__YEL__;box-shadow:0 0 14px rgba(201,161,91,.55)}
#send{position:absolute;right:16px;top:16px;width:84px;height:84px}
#sendoff,#sendon{position:absolute;left:0;top:0;width:84px;height:84px;border-radius:50%;display:flex;align-items:center;justify-content:center}
#sendoff{background:rgba(255,255,255,.11)}
#sendon{background:__YEL__;box-shadow:0 8px 26px rgba(201,161,91,.38)}
#tap{position:absolute;width:118px;height:118px;border-radius:50%;background:rgba(255,255,255,.46);border:3px solid rgba(255,255,255,.92);
  box-shadow:0 10px 28px rgba(0,0,0,.38),inset 0 0 22px rgba(255,255,255,.35)}
#tapring{position:absolute;width:84px;height:84px;border-radius:50%;border:4px solid __YEL__}

/* ---- posted comment */
#crow{position:absolute;display:flex;align-items:center;gap:16px}
#cav{width:86px;height:86px;border-radius:50%;overflow:hidden;flex:none;box-shadow:0 10px 26px rgba(0,0,0,.35)}
#cbub{position:relative;height:114px;padding:0 46px 0 34px;display:flex;align-items:center;gap:18px;background:__CREAM__;white-space:nowrap;
  border-radius:57px 57px 57px 16px;box-shadow:0 30px 70px rgba(0,0,0,.46),0 6px 18px rgba(0,0,0,.26),inset 0 -3px 0 rgba(20,22,28,.05)}
.who{font:__TW__ 33px '__TF__';color:rgba(20,22,28,.46);letter-spacing:-.5px;padding-top:6px__UP__}
.kw{font:__WW__ 70px '__WF__';color:__INK__;letter-spacing:.7px;line-height:114px}
#heart{position:absolute;right:-24px;top:-22px;width:60px;height:60px;border-radius:50%;background:#fff;display:flex;align-items:center;
  justify-content:center;box-shadow:0 10px 24px rgba(0,0,0,.30),0 2px 6px rgba(0,0,0,.18)}
#heartin{display:flex;padding-top:2px}
.hp{position:absolute;left:25px;top:25px;width:10px;height:10px;border-radius:50%;background:#FF4A6E}
.hp:nth-of-type(even){background:__YEL__;width:8px;height:8px}

/* ---- creator reply */
#rrow{position:absolute}
#rav{position:absolute;left:0;width:78px;height:78px;border-radius:50%;overflow:hidden;border:3px solid __YEL__;background:#222;
  box-shadow:0 10px 26px rgba(0,0,0,.4)}
#rav img{width:100%;height:100%;object-fit:cover;display:block}
#dots{position:absolute;left:94px;width:130px;height:72px;border-radius:36px 36px 36px 12px;background:rgba(20,22,28,.95);
  display:flex;align-items:center;justify-content:center;gap:11px;box-shadow:0 18px 44px rgba(0,0,0,.45),inset 0 0 0 2px rgba(255,255,255,.16)}
#dots i{width:14px;height:14px;border-radius:50%;background:rgba(255,248,239,.85)}
#rbub{position:absolute;left:94px;top:0;display:flex;white-space:nowrap;background:rgba(24,27,34,.97);
  box-shadow:0 30px 70px rgba(0,0,0,.55),0 6px 18px rgba(0,0,0,.34),inset 0 0 0 2px rgba(255,255,255,.16),inset 0 3px 0 rgba(255,255,255,.08)}
#rbub.inline{height:120px;padding:0 20px 0 38px;align-items:center;gap:24px;border-radius:60px 60px 60px 16px}
#rbub.stack{height:186px;padding:20px 38px 22px 38px;flex-direction:column;align-items:flex-start;gap:12px;border-radius:52px 52px 52px 16px}
#rtxt{font:__TW__ 42px '__TF__';color:__CREAM__;letter-spacing:-.7px;line-height:52px__UP__}
#rbub.stack #rtxt{padding-left:8px}
#chipwrap{position:relative;height:80px;flex:none}
#skel{position:absolute;left:0;top:0;width:100%;height:80px;border-radius:40px;background:rgba(255,255,255,.10);box-shadow:inset 0 0 0 2px rgba(255,255,255,.08)}
#chipring{position:absolute;left:0;top:0;width:100%;height:80px;border-radius:40px;border:3px solid __YEL__}
#chip{position:relative;height:80px;padding:0 30px 0 22px;border-radius:40px;background:__YEL__;display:flex;align-items:center;gap:10px;
  overflow:hidden;box-shadow:0 10px 30px rgba(201,161,91,.30)}
#chip span{font:__WW__ 37px '__WF__';color:__INK__;letter-spacing:-.2px__UP__}
#shine{position:absolute;left:0;top:0;width:100%;height:100%;background:linear-gradient(105deg,rgba(255,255,255,0) 36%,rgba(255,255,255,.85) 50%,rgba(255,255,255,0) 64%)}
'''.replace('__YEL__', YEL).replace('__CREAM__', CREAM).replace('__INK__', INK)
# typeface, weight and case come from the style lines of the CLIP block (the placeholder keeps its light weight in
# the default look and takes the text weight when the fonts were changed)
UI_CSS = (UI_CSS.replace('__WF__', WF).replace('__WW__', str(WW)).replace('__TF__', TF).replace('__TW__', str(TW))
          .replace('__PW__', str(TW if RESTYLED else 500)).replace('__UP__', ';text-transform:uppercase' if UPPER else ''))


def scale_css(css, s):
    """multiply every px length in the UI css by the layout scale (fonts, radii, paddings, shadows)"""
    return re.sub(r'(-?\d*\.?\d+)px', lambda m: f'{float(m.group(1)) * s:.2f}px', css)


def seat_css(L):
    a = max(0, L['y0'] - 230)
    k = max(0.0, min(1.5, SEAT))
    return ('#seat{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:5;pointer-events:none;'
            f'background:linear-gradient(180deg,rgba(8,9,12,0) {a:.0f}px,rgba(8,9,12,{.30 * k:.3f}) {L["y0"] + 60:.0f}px,'
            f'rgba(8,9,12,{.44 * k:.3f}) {min(1900, L["y0"] + L["th"] + 60):.0f}px,rgba(8,9,12,{.50 * k:.3f}) 1920px)}}')


# SAFE=1: Instagram safe zone in red + the chin line the layout used in cyan (snapshots only, never render this)
def safe_guide(L):
    return ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
            '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
            '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div>'
            f'<div style="position:absolute;left:0;right:0;top:{L["chin_eff"]:.0f}px;height:3px;background:rgba(0,255,255,.9)"></div></div>')


def sanity(L):
    last_key = T_TYPE + (len(KEYWORD) - 1) * KEY_GAP
    msgs = []
    if not (T_IN < T_FOCUS <= T_TYPE < T_SEND < T_DOTS < T_REPLY < T_LINK < DUR):
        msgs.append('times must run T_IN < T_FOCUS <= T_TYPE < T_SEND < T_DOTS < T_REPLY < T_LINK < slot end')
    if last_key > T_SEND - .06:
        msgs.append(f'the last letter lands at {last_key:.2f}, after the send tap ({T_SEND}): lower KEY_GAP or move T_SEND')
    if T_OUT is not None and not (T_LINK + .6 <= T_OUT <= DUR - .25):
        msgs.append('T_OUT must leave 0.6s after T_LINK and 0.25s before the slot ends')
    if DUR - T_LINK < 1.0:
        msgs.append(f'only {DUR - T_LINK:.2f}s of footage after the chip lands: give the slot at least 1.5s after T_LINK')
    if L['s'] < .8:
        msgs.append(f'the closing is drawn at {L["s"]:.2f} of its size: the band under their chin is {BOTTOM - L["chin_eff"]:.0f}px even after the lift')
    if L['push'] > 1.001 and T_OUT is None:
        msgs.append(f'plate is lifted x{L["push"]:.3f} and stays lifted on the last frame: end the slot on a cut, or set T_OUT')
    for m in msgs:
        print('  ! ' + m)


def build():
    L = layout()
    V = vlayout()
    html, tweens, sfx, vcss = comment_bubble(L, V)
    tweens = plate(V) + tweens
    nl = '\n'
    css = BASE_CSS + seat_css(V) + scale_css(UI_CSS, L['s']) + vcss
    doc = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR_ATTR}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR_ATTR}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio(sfx)) if SFX_ON else ''}
  <div id="stage">
    <video id="bgv" class="full" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR_ATTR}" data-track-index="0"></video>
  </div>
{html}
{safe_guide(V) if os.environ.get('SAFE') else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(tweens)}
tl.set({{}}, {{}}, {DUR_ATTR});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    open('index.html', 'w').write(doc)
    os.makedirs('work', exist_ok=True)
    json.dump({'frames': NFRAMES, 'variant': VARIANT, 'scale': V['s'], 'mode': VARIANT_NAMES[VARIANT], 'push': round(V['push'], 4),
               'chin': V['chin'], 'chin_eff': round(V['chin_eff'], 1), 'x0': round(V['x0'], 1), 'y0': round(V['y0'], 1),
               'tw': round(V['tw'], 1), 'th': round(V['th'], 1), 'field': [round(L['fx'], 1), round(L['fy'], 1), round(L['fw'], 1)],
               'beats': {'T_IN': T_IN, 'T_FOCUS': T_FOCUS, 'T_TYPE': T_TYPE, 'last_key': T_TYPE + (len(KEYWORD) - 1) * KEY_GAP,
                         'T_SEND': T_SEND, 'T_DOTS': T_DOTS, 'T_REPLY': T_REPLY, 'T_LINK': T_LINK, 'T_OUT': T_OUT}},
              open('work/layout.json', 'w'), indent=1)      # check.py reads this
    print(f'wrote index.html  {NFRAMES} frames ({DUR:.2f}s)  safe guide {"ON (do not render)" if os.environ.get("SAFE") else "off"}  sfx {"on" if SFX_ON else "off"}')
    print(f'closing {VARIANT} ({VARIANT_NAMES[VARIANT]}): scale {V["s"]:.2f}  x {V["x0"]:.0f}..{V["x0"] + V["tw"]:.0f}  y {V["y0"]:.0f}..{V["y0"] + V["th"]:.0f}'
          f'  chin {V["chin"]:.0f}' + (f' -> {V["chin_eff"]:.0f} after x{V["push"]:.3f} lift' if V['push'] > 1.001 else '  (plate untouched)'))
    sanity(V)
    print(f'render: npx --yes hyperframes@0.8.34 render -o renders/{SLOT}.mp4 --quality high')


build()
