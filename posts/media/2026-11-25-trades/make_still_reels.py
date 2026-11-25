#!/usr/bin/env python3
"""Still-image trade reels from DRT Phone screenshots (same method as 2026-11-22-trade/make_trade_reel_1122.py).
Usage: python3 make_still_reels.py  (needs src/shot1929.jpg = DRT Phone 1lGbXWDKBkfXfWQx7jepqByvXP3Vac8fZ and src/shot0948.jpg = 1C7nuyAOMIF40IsQEuoMmxIgA8my4wsyQ; raw files kept out of git)
Crop keeps Tim's chart only (bars, fill markers, price + time axes). Removed: status bar, indicator legend and
signal/volume tables (indicator names), app tab bar, system nav. The 9:48 shot's "CRT Filter" panel is covered.
Header text rendered here, facts from the fill markers only. No $ (not shown as a result on screen), no account.
"""
import subprocess
from PIL import Image, ImageDraw, ImageFont
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; R = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
W, H, BG = 1080, 1920, (15, 15, 15)
JOBS = {
  "b": dict(src="src/shot1929.jpg", box=(0, 400, 1080, 1930), covers=[],
            lines=["Tuesday evening session, ES 1-minute", "1 ES short  +38.75 pts", "In 7,221.50   Out 7,182.75"],
            color=(38, 166, 154)),
  "d": dict(src="src/shot0948.jpg", box=(0, 500, 1080, 1930), covers=[(612, 1646, 894, 1846)],
            lines=["Wednesday 9:45 AM, ES 1-minute", "2 ES long  +10.75 pts total", "In 7,000.00 + 7,006.25   Out 2 @ 7,008.50"],
            color=(38, 166, 154)),
}
for k, j in JOBS.items():
    im = Image.open(j["src"]).convert("RGB"); assert im.size == (1080, 2340)
    d0 = ImageDraw.Draw(im)
    for c in j["covers"]:
        d0.rectangle(c, fill=BG)
    chart = im.crop(j["box"])
    canvas = Image.new("RGB", (W, H), BG)
    CY = 330
    canvas.paste(chart, (0, CY))
    d = ImageDraw.Draw(canvas)
    f1, f2, f3 = ImageFont.truetype(R, 44), ImageFont.truetype(B, 84), ImageFont.truetype(R, 46)
    def ctext(y, s, f, fill):
        while d.textlength(s, font=f) > W - 70:
            f = ImageFont.truetype(f.path, f.size - 2)
        w = d.textlength(s, font=f); d.text(((W - w) / 2, y), s, font=f, fill=fill)
    ctext(40, j["lines"][0], f1, (200, 200, 200))
    ctext(100, j["lines"][1], f2, j["color"])
    ctext(222, j["lines"][2], f3, (235, 235, 235))
    canvas.save(f"still_{k}.png")
    N = 300  # 10 s, slow 5% push-in anchored right/top, moving from frame 0
    zp = (f"scale=2160:3840,zoompan=z='1+0.05*on/{N}':x='(iw-iw/zoom)*1.0':y='(ih-ih/zoom)*0.2':"
          f"d={N}:s=1080x1920:fps=30,setsar=1")
    subprocess.run([FF, "-loglevel", "error", "-y", "-loop", "1", "-i", f"still_{k}.png", "-vf", zp, "-frames:v", str(N),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", f"reel-{k}.mp4"], check=True)
