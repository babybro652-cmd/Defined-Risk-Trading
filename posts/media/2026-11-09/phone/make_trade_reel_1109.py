"""Two paper trades, Tim's TradingView recordings (Drive DRT Phone, uploaded 11/9):
B Screen_Recording_20261108_195111 (1gjsibeFO36x7V7ANRvCNkEdREvd02KqS, 2:36): Sun 11/8 ~7:58 PM ET, Asia open.
  Long 2 ES @ 7,398.50, sold 2 @ 7,409.75: +11.25 pts x 2 = +$1,125.
A Screen_Recording_20261109_114007 (1DMuyFHwBM2e6Ror1CtP_Wh-wTOwumzXo, 17:50): Mon 11/9, entry before 11:22 (Tim), ~11:22-11:40 ET.
  Short 2 ES @ 7,560.25 after the rally, stop 7,564.25 (4 pts), target 7,534.00. Open peaked about +$2,125.
  Covered 2 @ 7,544.50 at ~11:40 (lunch break over): +15.75 pts x 2 = +$1,575.  Day total +$2,700 gross. Paper (Tim).
Covers (source px): volume-map table (top right) and filter table (bottom right) in both; indicator legend (A, top left).
Phone and chart times kept as proof. Usage: python3 make_trade_reel_1109.py A.mp4 B.mp4 OUT.mp4 MUSIC.mp3"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); GREEN = (90, 200, 140); BG = (14, 10, 9)
W, H = 1080, 1920
TMP = os.path.dirname(os.path.abspath(sys.argv[3]))

def band(path, small, big):
    im = Image.new("RGBA", (W, 190), (10, 8, 7, 235)); d = ImageDraw.Draw(im)
    d.text((50, 22), small, font=ImageFont.truetype(B, 36), fill=GOLD)
    d.text((50, 80), big, font=ImageFont.truetype(B, 44), fill=CREAM)
    im.save(path)

def card(path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    L = [("Two trades, both green", 58, True, CREAM, 330),
         ("Sunday night", 40, True, GOLD, 480), ("Long 2 ES @ 7,398.50", 38, False, CREAM, 540),
         ("Out 7,409.75  |  +11.25 pts  |  +$1,125", 38, True, GREEN, 595),
         ("Monday", 40, True, GOLD, 710), ("Short 2 ES @ 7,560.25 after the rally", 38, False, CREAM, 770),
         ("Out 7,544.50  |  +15.75 pts  |  +$1,575", 38, True, GREEN, 825),
         ("Total: +$2,700 gross", 50, True, CREAM, 950), ("Paper account", 34, False, MUTED, 1030),
         ("Define your risk. Wait for your setup.", 42, True, CREAM, 1220)]
    for t, s, b, c, y in L:
        d.text((90, y), t, font=ImageFont.truetype(B if b else R, s), fill=c)
    f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    im.save(path)

COV = "0x0f0f0f"
def boxes(lst): return ",".join(f"drawbox=x={x}:y={y}:w={w}:h={h}:color={COV}:t=fill" for x, y, w, h in lst)
CB = boxes([(440, 95, 455, 400), (600, 1900, 300, 215)])            # Sunday clip
CA = boxes([(440, 105, 455, 395), (600, 1630, 300, 225), (0, 200, 820, 230)])  # Monday clip
FIT = f"scale=-2:{H},pad={W}:{H}:(ow-iw)/2:0:color={COV},setsar=1,fps=30"

def seg(src, ss, to, speed, cov, bandpng, out):
    vf = f"[0:v]trim={ss}:{to},setpts=(PTS-STARTPTS)/{speed},{cov},{FIT}[v];[v][1:v]overlay=0:{H-190}"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-i", bandpng, "-filter_complex", vf, "-an",
                    "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p", out], check=True)

def main():
    a, b, out, music = sys.argv[1:5]
    p = lambda n: os.path.join(TMP, n)
    band(p("b1.png"), "Sunday night", "Long 2 ES at the Asia open"); band(p("a1.png"), "Monday", "Short 2 ES after the rally")
    card(p("card.png"))
    seg(b, 0, 146, 8, CB, p("b1.png"), p("s1.mp4")); seg(b, 146, 155.5, 1, CB, p("b1.png"), p("s2.mp4"))
    seg(a, 0, 1058, 48, CA, p("a1.png"), p("s3.mp4")); seg(a, 1058, 1068.8, 1, CA, p("a1.png"), p("s4.mp4"))
    subprocess.run([FF, "-y", "-loglevel", "error", "-loop", "1", "-t", "5", "-i", p("card.png"), "-vf", "fps=30,format=yuv420p",
                    "-c:v", "libx264", "-crf", "21", p("s5.mp4")], check=True)
    with open(p("list.txt"), "w") as f:
        for n in ("s1", "s2", "s3", "s4", "s5"): f.write(f"file '{p(n + '.mp4')}'\n")
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", p("list.txt"), "-c", "copy", p("v.mp4")], check=True)
    dur = float(subprocess.run([FF.replace("ffmpeg", "ffprobe") if os.path.exists(FF.replace("ffmpeg", "ffprobe")) else "ffprobe",
                                "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p("v.mp4")],
                               capture_output=True, text=True).stdout)
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", p("v.mp4"), "-i", music, "-filter_complex",
                    f"[1:a]atrim=0:{dur},afade=t=in:d=0.5,afade=t=out:st={dur-1.2}:d=1.2,loudnorm=I=-18:TP=-1.5[m]",
                    "-map", "0:v", "-map", "[m]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    print("done", round(dur, 1), "s")

if __name__ == "__main__":
    main()
