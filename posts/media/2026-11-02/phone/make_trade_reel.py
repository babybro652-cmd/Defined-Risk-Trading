"""Trade reel from Tim's 11/2/2026 TradingView recording (Drive DRT Phone,
Screen_Recording_20261102_111923_TradingView.mp4, id 13JqH6RySchXvXm1w8M0qI1FH2iYEtjQR) plus the
follow-up screenshot Screenshot_20261102_121417_TradingView.jpg (id 1zc9G6yUCAWZcx2_BkcDd1U3LhGMFrf_Z).
Same approach as posts/media/2026-10-30/phone/make_trade_reel.py: speed-up, crop the phone status bar
(clock, recorder icon, app notification icons) and nav bar, and cut these (found with a full-frame-rate scan):
  43.5-47.0 s   landscape rotation + recorder toolbar
  79.0-84.5 s   text notification banner with a contact name + edge lighting (79.4-83.2)
  610.3-612.0 s recorder toolbar + rotation
  after 794.0 s swipe home (home screen with a family photo from 794.85)
Ends on the 12:14 screenshot ("it kept falling") and a result card.
--hide-times blurs the chart's time-of-day axis (day-job safety option).
Usage: python3 make_trade_reel.py SRC.mp4 SHOT.jpg OUT.mp4 [--hide-times]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
AXIS = (1762, 1848)  # time axis band in cropped coordinates
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); GREEN = (90, 200, 140)
BG = (14, 10, 9)
SEGMENTS = [(0, 43.5, 2.2), (47.0, 79.0, 1.6), (84.5, 610.3, 25.0), (612.0, 794.0, 9.2)]  # (start, end, out s)
ACCOUNT = "  |  paper"  # Tim 11/2: paper account
CARD = ("Closed manually", "ES short 2 @ 7,667.75", "Stop 7,671.75 (4 pts)  |  Out at 7,659.25",
        "+8.50 pts  |  2.1R" + ACCOUNT)


def frames(src, start, end, n):
    rate = n / (end - start)
    cmd = [FF, "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", src,
           "-vf", f"fps={rate:.5f},crop={W}:{H}:0:{TOP}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    sz = W * H * 3
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        yield np.frombuffer(b, dtype=np.uint8).reshape(H, W, 3)


def bad(a):
    """Notification shade or home screen: the TradingView chart is dark; those screens are not."""
    return a[200:1500].mean() > 45 or (a[0:120].mean(axis=2) > 150).mean() > 0.08


def hide(im, y0, y1):
    box = (0, y0, im.width, y1)
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box)
    return im


def shot_card(path, hide_times):
    s = Image.open(path).convert("RGB")
    s = s.crop((0, TOP, 1080, 1905))  # header to time axis; status bar + toolbars cut
    if hide_times:
        s = hide(s, 1770, s.height)
    sc = 0.86; s = s.resize((int(s.width * sc), int(s.height * sc)))
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((70, 90), "After I closed", font=ImageFont.truetype(B, 64), fill=GOLD)
    d.text((70, 180), "ES kept falling.", font=ImageFont.truetype(B, 52), fill=CREAM)
    x = (W - s.width) // 2; im.paste(s, (x, 300))
    d.rectangle([x - 2, 298, x + s.width + 1, 300 + s.height + 1], outline=(60, 50, 45), width=2)
    return np.array(im)


def card(lines):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([100, 640, 180, 648], fill=GOLD)
    d.text((100, 690), lines[0], font=ImageFont.truetype(B, 84), fill=GREEN)
    y = 830
    for t, f, c in [(lines[1], ImageFont.truetype(B, 56), CREAM), (lines[2], ImageFont.truetype(R, 42), MUTED),
                    (lines[3], ImageFont.truetype(B, 44), GOLD)]:
        d.text((100, y), t, font=f, fill=c); y += 110
    d.text((100, 1300), "Define your risk. Wait for your setup.", font=ImageFont.truetype(B, 44), fill=CREAM)
    f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    return np.array(im)


def main():
    src, shot, out = sys.argv[1], sys.argv[2], sys.argv[3]
    hide_times = "--hide-times" in sys.argv
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    kept = dropped = 0
    for s, e, secs in SEGMENTS:
        for a in frames(src, s, e, round(secs * FPS)):
            if bad(a):
                dropped += 1
                continue
            if hide_times:
                a = np.array(hide(Image.fromarray(a), *AXIS))
            p.stdin.write(a.tobytes()); kept += 1
    for img, secs in [(shot_card(shot, hide_times), 3.5), (card(CARD), 3.5)]:
        for _ in range(int(secs * FPS)):
            p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
