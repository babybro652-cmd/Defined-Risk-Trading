"""Apex 25K eval pass reel, 11/12. Text cards + Tim's cleaned screenshots (run clean_sources.py first).
python3 make_reel.py [drt|personal]   -> apex-pass.mp4 / apex-pass-personal.mp4 (silent; music via add_audio.py)
Only facts Tim gave: fills, -$425 / +$1,025 / +$1,825, +$2,425 gross, $25,000 -> $27,394 equity, his rules.
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

VAR = sys.argv[1] if len(sys.argv) > 1 else "drt"
W, H, FPS = 1080, 1920, 30
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130)
REDC = (242, 84, 91); GREEN = (64, 200, 140)
HANDLE = "@definedrisktrading" if VAR == "drt" else None


def bg():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([20, 26, 38]); bot = np.array([8, 10, 15])
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:] = (top[None, :] * (1 - y) + bot[None, :] * y).astype(np.uint8)[:, None, :]
    return Image.fromarray(arr)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def handle(d):
    if HANDLE:
        f = ImageFont.truetype(B, 36)
        d.text(((W - d.textlength(HANDLE, font=f)) / 2, H - 260), HANDLE, font=f, fill=MUTED)


def card(label, head, sub=None, subcol=MUTED, y=560, hsize=84):
    im = bg(); d = ImageDraw.Draw(im)
    d.rectangle([100, y - 50, 180, y - 42], fill=GOLD)
    if label:
        d.text((100, y), label, font=ImageFont.truetype(B, 42), fill=GOLD); y += 95
    f = ImageFont.truetype(B, hsize)
    for ln in wrap(d, head, f, W - 200):
        d.text((100, y), ln, font=f, fill=CREAM); y += int(hsize * 1.22)
    if sub:
        y += 45
        for part, col in (sub if isinstance(sub, list) else [(sub, subcol)]):
            f2 = ImageFont.truetype(B if col != MUTED else R, 60 if col != MUTED else 50)
            for ln in wrap(d, part, f2, W - 200):
                d.text((100, y), ln, font=f2, fill=col); y += int(f2.size * 1.35)
    handle(d)
    return np.array(im)


def rules_card():
    im = bg(); d = ImageDraw.Draw(im)
    y = 430
    d.rectangle([100, y - 50, 180, y - 42], fill=GOLD)
    d.text((100, y), "THE RULES I FOLLOWED", font=ImageFont.truetype(B, 42), fill=GOLD); y += 110
    f = ImageFont.truetype(B, 47)
    for r in ["New York session only", "No trades before 10 AM", "Wait for the label",
              "Hard stop 3.5-4 pts from entry", "Max $1,000 loss in a day"]:
        d.ellipse([104, y + 22, 122, y + 40], fill=GOLD)
        d.text((150, y), r, font=f, fill=CREAM); y += 105
    y += 60
    d.text((100, y), "Define your risk. Wait for your setup.", font=ImageFont.truetype(R, 46), fill=MUTED)
    handle(d)
    return np.array(im)


def band(im, text, y0=150):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(B, 54)
    lines = wrap(d, text, f, W - 140)
    h = 40 + 72 * len(lines)
    d.rectangle([0, y0, W, y0 + h], fill=(8, 10, 15))
    d.rectangle([0, y0 + h, W, y0 + h + 6], fill=GOLD)
    yy = y0 + 20
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, yy), ln, font=f, fill=CREAM); yy += 72


def chart_frames(dur):
    ch = Image.open("chart_clean.png").convert("RGB")  # 1080 x 1045
    n = int(dur * FPS)
    for k in range(n):
        a = min(1.0, k / 9, (n - k) / 9)
        im = bg(); im.paste(ch, (0, 540))
        band(im, "1 minute ES: trade 2 add and cover, then all of trade 3", 260)
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(R, 44)
        t = "Red arrows = sells. Blue arrows = covers."
        d.text(((W - d.textlength(t, font=f)) / 2, 1598), t, font=f, fill=MUTED)
        handle(d)
        yield (np.array(im).astype(np.float32) * a).astype(np.uint8)


def orders_frames(hold, scroll):
    o = Image.open("orders_clean.png").convert("RGB")  # 1080 x 6838
    view_y, view_h = 330, H - 330
    n1, n2 = int(hold * FPS), int(scroll * FPS)
    maxoff = o.height - view_h
    for k in range(n1 + n2):
        t = 0 if k < n1 else (k - n1) / max(1, n2 - 1)
        t = t * t * (3 - 2 * t)  # ease
        off = int(maxoff * t)
        im = Image.new("RGB", (W, H), (0, 0, 0))
        im.paste(o.crop((0, off, W, off + view_h)), (0, view_y))
        band(im, "Every fill, from the order log", 120)
        yield np.array(im)


def faded(frame, dur, fade=9):
    n = int(dur * FPS)
    for k in range(n):
        a = 1.0
        if k < fade: a = k / fade
        if k > n - fade: a = (n - k) / fade
        yield (frame.astype(np.float32) * a).astype(np.uint8)


segs = [
    faded(card(None, "Trade 1 hit my stop for -$425.", [("Same day, I passed my Apex 25K eval.", GOLD)], y=640, hsize=92), 3.6),
    faded(card("TRADE 1", "Short 2 ES at 7,669.75. Stopped out at 7,674.00.",
               [("4 pt stop + 0.25 slippage", MUTED), ("-$425", REDC)]), 4.6),
    faded(card("THE RULE HELD", "I took the stop. Then I kept following the plan."), 3.6),
    faded(card("TRADE 2", "Short 2 at 7,670.75. Added 2 at 7,664.50. Covered 4 at 7,662.50.",
               [("+$1,025", GREEN)]), 4.4),
    faded(card("TRADE 3", "Short 2 at 7,663.75. Added 2 at 7,658.00. Covered 4 at 7,651.75.",
               [("+$1,825", GREEN)]), 4.4),
    chart_frames(6.5),
    orders_frames(2.5, 6.5),
    faded(card("EVAL PASSED", "Started at $25,000. Equity now $27,394.",
               [("Day: +$2,425 gross on ES", GREEN)]), 4.2),
    faded(rules_card(), 5.0),
]

out = "apex-pass.mp4" if VAR == "drt" else "apex-pass-personal.mp4"
p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
                      "-crf", "20", "-an", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for s in segs:
    for fr in s:
        p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
print("wrote", out)
