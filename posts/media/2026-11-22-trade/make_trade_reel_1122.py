#!/usr/bin/env python3
"""Build the 11/22 Sunday-open trade reel from DRT Phone Screenshot_20261122_185335_TradingView.jpg.
Usage: python3 make_trade_reel_1122.py SHOT.jpg OUTDIR
Crops out the status bar, the indicator legend / signal table (names an internal indicator), the app tab bar
and system nav. Keeps Tim's chart (bars, fill markers, price axis, time axis). Adds a header rendered here.
"""
import sys, subprocess
from PIL import Image, ImageDraw, ImageFont
shot, out = sys.argv[1], sys.argv[2]
im = Image.open(shot).convert("RGB")
assert im.size == (1080, 2340), im.size
chart = im.crop((0, 650, 1080, 1930))          # below the legend + collapse button, through the time axis
W, H = 1080, 1920
BG = (15, 15, 15)
canvas = Image.new("RGB", (W, H), BG)
CY = 360
canvas.paste(chart, (0, CY))
d = ImageDraw.Draw(canvas)
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
R = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
f1, f2, f3, f4 = ImageFont.truetype(R, 46), ImageFont.truetype(B, 92), ImageFont.truetype(R, 50), ImageFont.truetype(R, 38)
def ctext(y, s, f, fill):
    w = d.textlength(s, font=f); d.text(((W - w) / 2, y), s, font=f, fill=fill)
ctext(48, "Sunday night futures open", f1, (200, 200, 200))
ctext(112, "1 ES long  +14.5 pts", f2, (38, 166, 154))
ctext(240, "In 7,037.25   Out 7,051.75", f3, (235, 235, 235))
ctext(CY + 1280 + 70, "ES 1-minute chart", f4, (150, 150, 150))
canvas.save(f"{out}/still.png")
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
# slow push-in anchored right (price axis stays) and near the top (header stays), 9 s, 30 fps, moving from frame 0
N = 270
zp = (f"scale=2160:3840,zoompan=z='1+0.05*on/{N}':x='(iw-iw/zoom)*1.0':y='(ih-ih/zoom)*0.3':"
      f"d={N}:s=1080x1920:fps=30,setsar=1")
subprocess.run([FF, "-y", "-loop", "1", "-i", f"{out}/still.png", "-vf", zp, "-frames:v", str(N),
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", f"{out}/reel.mp4"], check=True)
