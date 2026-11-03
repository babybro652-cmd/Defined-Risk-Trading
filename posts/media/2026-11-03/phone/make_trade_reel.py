"""Personal trade reel from Tim's 11/3/2026 TradingView recording (Drive DRT Phone,
Screen_Recording_20261103_074907_TradingView.mp4, id 1HZd9Nsr0uyVjbb1x7act3U-rlEhzqUob, 16:03, 1080x2340, VFR ~10.5 fps).
ES long 2 @ 7,571.00 (filled before the recording starts), stop 7,567.00, target 7,581.00; closed 2 @ 7,567.25 at the end.
Same approach as posts/media/2026-11-02/phone/make_trade_reel.py. Cut (found with a full-frame-rate scan):
  549.5-552.5 s  screen-recorder toolbar + landscape rotation (550.0-551.9)
  781.5-798.0 s  indicator legend expanded (indicator names and settings) + method panels (782.5-797.0)
Status bar (clock, recorder icon, app icons) and nav bar cropped from every frame. The chart's time axis is
blurred by default (the recording is inside Tim's work hours); --show-times keeps it.
Usage: python3 make_trade_reel.py SRC.mp4 OUT.mp4 [--account paper|live] [--show-times]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
AXIS = (1762, 1848)  # time axis band in cropped coordinates
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (225, 95, 85)
BG = (14, 10, 9)
SEGMENTS = [(0, 549.5, 21.0), (552.5, 781.5, 9.0), (798.0, 930.0, 5.0), (930.0, 963.5, 4.5)]  # (start, end, out s)


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
    """Notification shade, home screen, rotation (black) or expanded legend: the chart frame is none of these."""
    m = a[200:1500].mean()
    legend = (a[50:240, 0:560].mean(axis=2) > 90).mean() > 0.045
    return m > 45 or m < 10 or (a[0:120].mean(axis=2) > 150).mean() > 0.08 or legend


def hide(im, y0, y1):
    box = (0, y0, im.width, y1)
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(14)), box)
    return im


def card(account):
    tag = f"  |  {account}" if account else ""
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([100, 640, 180, 648], fill=GOLD)
    d.text((100, 690), "Closed for a loss", font=ImageFont.truetype(B, 80), fill=RED)
    y = 830
    for t, f, c in [("ES long 2 @ 7,571.00", ImageFont.truetype(B, 56), CREAM),
                    ("Stop 7,567.00 (4 pts)  |  Out at 7,567.25", ImageFont.truetype(R, 42), MUTED),
                    ("-3.75 pts  |  -$375" + tag, ImageFont.truetype(B, 44), GOLD)]:
        d.text((100, y), t, font=f, fill=c); y += 110
    d.text((100, 1300), "Define your risk. Wait for your setup.", font=ImageFont.truetype(B, 44), fill=CREAM)
    return np.array(im)


def main():
    src, out = sys.argv[1], sys.argv[2]
    show_times = "--show-times" in sys.argv
    account = sys.argv[sys.argv.index("--account") + 1] if "--account" in sys.argv else ""
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    kept = dropped = 0
    last = None
    for s, e, secs in SEGMENTS:
        for a in frames(src, s, e, round(secs * FPS)):
            if bad(a):
                dropped += 1
                continue
            if not show_times:
                a = np.array(hide(Image.fromarray(a), *AXIS))
            p.stdin.write(a.tobytes()); kept += 1; last = a
    for _ in range(int(1.0 * FPS)):  # hold the exit frame
        p.stdin.write(last.tobytes())
    img = card(account)
    for _ in range(int(3.5 * FPS)):
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
