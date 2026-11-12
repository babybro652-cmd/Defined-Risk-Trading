"""Loss trade reel, Thu 11/12 (separate account, NOT the Apex eval). Source: Drive DRT Phone
Screen_Recording_20261112_101629_TradingView.mp4 (1VUoior9etsLHIEwmZtUUGmZ6iBlEy_PI, 1:55.7, 1080x2340).
On screen only: short 2 ES (ESZ2026) @ 7,612.50 at the sell label (~10:13 ET), Buy STP 2 @ 7,616.25 (3.75 pts),
open P&L as good as +$350, stop filled 2 @ 7,616.25 (~10:16 ET). -3.75 pts x 2 x $50 = -$375 before fees (computed;
the realized number is not on screen).
Cuts: 0-1.8 s (home screen, wallpaper photo), 35-45 s (long-press menu naming the indicator).
Covers: status bar + chart header + volume-map table (top band), filter table bottom right; crop drops the nav bar.
Raw source not committed. Usage: python3 make_loss_reel.py SRC.mp4 OUT.mp4 [drt|personal]"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (242, 84, 91); BG = (14, 10, 9)
W, H, TOPH = 1080, 1920, 430
SRC, OUT = sys.argv[1], sys.argv[2]
VAR = sys.argv[3] if len(sys.argv) > 3 else "drt"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "build_" + VAR); os.makedirs(TMP, exist_ok=True)
p = lambda n: os.path.join(TMP, n)


def top(path, small, big, big2=None, col2=CREAM):
    im = Image.new("RGBA", (W, TOPH), (14, 10, 9, 255)); d = ImageDraw.Draw(im)
    d.rectangle([60, 70, 140, 78], fill=GOLD)
    d.text((60, 100), small, font=ImageFont.truetype(B, 40), fill=GOLD)
    d.text((60, 175), big, font=ImageFont.truetype(B, 62), fill=CREAM)
    if big2:
        d.text((60, 268), big2, font=ImageFont.truetype(B, 58), fill=col2)
    im.save(path)


def card(path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    L = [("A defined loss", 70, True, CREAM, 300),
         ("Short 2 ES @ 7,612.50", 46, False, CREAM, 450),
         ("Stop 7,616.25  |  3.75 pts from entry", 42, False, CREAM, 520),
         ("Stopped out: -$375 before fees", 48, True, RED, 600),
         ("THE RULES", 40, True, GOLD, 760),
         ("New York session, after 10 AM", 44, False, CREAM, 830),
         ("Hard stop 3.5-4 pts from entry", 44, False, CREAM, 900),
         ("Max $1,000 loss in a day", 44, False, CREAM, 970),
         ("This one cost $375.", 48, True, CREAM, 1080),
         ("Define your risk. Wait for your setup.", 42, True, GOLD, 1260)]
    for t, s, b, c, y in L:
        d.text((90, y), t, font=ImageFont.truetype(B if b else R, s), fill=c)
    if VAR == "drt":
        f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
        d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    im.save(path)


# source-pixel covers (before the crop): filter table bottom right (and the order tag beside it)
COV = "drawbox=x=600:y=1625:w=300:h=225:color=0x0f0f0f:t=fill"
CROP = "crop=1080:1920:0:100,setsar=1,fps=30"


def seg(ss, to, speed, toppng, out):
    vf = (f"[0:v]trim={ss}:{to},setpts=(PTS-STARTPTS)/{speed},{COV},{CROP}[v];"
          f"[v][1:v]overlay=0:0")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC, "-i", toppng, "-filter_complex", vf, "-an",
                    "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", out], check=True)


def main():
    top(p("t1.png"), "SHORT 2 ES @ 7,612.50", "Stopped for -$375.", "The stop did its job.")
    top(p("t2.png"), "THE STOP", "Buy stop at 7,616.25", "3.75 pts from entry")
    top(p("t3.png"), "IT WORKED FOR A WHILE", "Up +$350 at the best point", "Stop stayed where it was")
    top(p("t4.png"), "THEN PRICE CAME BACK", "Filled 2 @ 7,616.25", "-3.75 pts x 2 ES = -$375", RED)
    card(p("card.png"))
    seg(1.8, 4.8, 1, p("t1.png"), p("s1.mp4"))        # hook, real time, 3 s
    seg(4.8, 35, 5, p("t2.png"), p("s2.mp4"))         # ~6 s
    seg(45, 104, 6, p("t3.png"), p("s3.mp4"))         # ~9.8 s
    seg(104, 115.6, 1.5, p("t4.png"), p("s4.mp4"))    # ~7.7 s, the stop fills
    subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-t", "6", "-i", p("card.png"),
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", p("s5.mp4")], check=True)
    with open(p("list.txt"), "w") as f:
        for n in ("s1", "s2", "s3", "s4", "s5"):
            f.write(f"file '{p(n + '.mp4')}'\n")
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", p("list.txt"),
                    "-c", "copy", "-movflags", "+faststart", OUT], check=True)
    print("done", OUT)


if __name__ == "__main__":
    main()
