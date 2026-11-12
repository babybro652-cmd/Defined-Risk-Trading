"""Education cut of Tim's approved 11/9 short (Drive 1DMuyFHwBM2e6Ror1CtP_Wh-wTOwumzXo, already posted 11/9).
One concept: the stop goes above the high, 4 pts, set before the click. No P&L: the TradingView USD
order labels are covered and replaced with plain STOP / ENTRY / TARGET tags. Status bar (clock,
notifications), time axis and nav bar are cropped off. Stills from t=600 s (15m) and t=900 s (1m).
Usage: python3 make_footage_cut.py full_600.png full_900.png OUT.mp4"""
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (235, 90, 90); GRN = (90, 200, 140)
W, H = 1080, 1920; BG = (15, 15, 15)
CROP = (0, 120, 1080, 1860)   # drop status bar (0-120) and time axis/nav (1860+)

def chart(path):
    im = Image.open(path).convert("RGB"); d = ImageDraw.Draw(im)
    # cover USD order labels (stop/entry pair and target) on the chart body; price axis tags kept
    d.rectangle([355, 750, 830, 880], fill=BG)
    d.rectangle([370, 1155, 830, 1235], fill=BG)
    f = ImageFont.truetype(B, 34)
    d.text((420, 765), "STOP  4 pts above", font=f, fill=GOLD)
    d.text((420, 822), "ENTRY  short", font=f, fill=RED)
    d.text((420, 1172), "TARGET", font=f, fill=GRN)
    im = im.crop(CROP)
    can = Image.new("RGB", (W, H), BG); can.paste(im, (0, 90))
    return can

def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def cap(base, label, text, y=330):
    im = base.copy(); d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(B, 58); fl = ImageFont.truetype(B, 36)
    lines = wrap(d, text, f, W - 160)
    h = 40 + (50 if label else 0) + 72 * len(lines) + 20
    d.rounded_rectangle([50, y, W - 50, y + h], radius=24, fill=(8, 8, 8, 230), outline=GOLD, width=3)
    yy = y + 25
    if label: d.text((80, yy), label, font=fl, fill=GOLD); yy += 50
    for ln in lines: d.text((80, yy), ln, font=f, fill=CREAM); yy += 72
    ft = ImageFont.truetype(B, 34); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=ft)) / 2, H - 120), t, font=ft, fill=MUTED)
    return im

def end_card():
    im = Image.new("RGB", (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.rectangle([100, 620, 180, 628], fill=GOLD)
    f = ImageFont.truetype(B, 78); y = 670
    for ln in wrap(d, "Stop first. Then the click.", f, W - 200): d.text((100, y), ln, font=f, fill=CREAM); y += 100
    y += 50; f2 = ImageFont.truetype(R, 52)
    for ln in wrap(d, "Define your risk. Wait for your setup.", f2, W - 200): d.text((100, y), ln, font=f2, fill=MUTED); y += 70
    ft = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=ft)) / 2, H - 260), t, font=ft, fill=MUTED)
    return im

def render(out, cards, fps=30, fade=8):
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-an", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for im, dur in cards:
        a0 = np.asarray(im, dtype=np.float32); n = int(dur * fps)
        for k in range(n):
            a = min(1.0, k / fade, (n - k) / fade)
            p.stdin.write((a0 * a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    a, b, out = sys.argv[1:4]
    A, Bc = chart(a), chart(b)
    render(out, [
        (cap(A, None, "Short ES on a day up 140 points. The stop came first."), 4.5),
        (cap(A, "THE SPOT", "The push into the high stalled. That's where I sold."), 5),
        (cap(A, "THE STOP", "4 points above, at 7,564.25. Price there means I'm wrong."), 5.5),
        (cap(A, "THE ROOM", "Target 7,534: about 26 points of room for 4 points of risk."), 5.5),
        (cap(Bc, "THE WAIT", "Then it's patience. The stop stays where I put it."), 5),
        (end_card(), 4.5)])
