"""Trade reel (DRT + personal) from Tim's 11/3/2026 second TradingView recording (Drive DRT Phone,
Screen_Recording_20261103_114846_TradingView.mp4, id 1HcMknWt1AmbjHykQ5g22G3ARq1w-we7D, 31:02, 1080x2340, VFR ~11.9 fps).
ES short 2 @ 7,614.00 (filled just before the recording starts), stop 7,618.00, target 7,598.00; bought back 2 @ 7,597.75.
Cut (found with a full-frame-rate scan of all 22,192 frames):
  5.0-30.0 s      indicator legend expanded (indicator names, settings) + method panels (~8-29 s)
  804.0-810.0 s   text notification with a contact name + message preview, purple edge lighting (804.9-808.9)
  1194.0-1199.5 s second text notification, same contact (1194.5-1198.6)
  1556.5-1559.0 s screen-recorder toolbar + landscape rotation (1557.0-1558.2)
Status bar (clock, recorder icon, app icons) and nav bar cropped from every frame. The chart's time axis is
blurred by default (the recording is inside Tim's work hours); --show-times keeps it.
--breakdown: ~67 s time-lapse for Tim's own breakdown video (real speed on the entry and the target fill, no card).
Usage: python3 make_trade_reel_2.py SRC.mp4 OUT.mp4 [--account paper|live] [--show-times] [--breakdown]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
AXIS = (1762, 1848)  # time axis band in cropped coordinates
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (225, 95, 85); GREEN = (90, 200, 140)
BG = (14, 10, 9)
SEGMENTS = [(0, 5.0, 1.5), (30.0, 804.0, 20.0), (810.0, 1194.0, 11.0), (1199.5, 1556.5, 10.0), (1559.0, 1820.0, 6.0),
            (1820.0, 1861.5, 4.5)]
# breakdown: real speed 0-2 s (entry fill marker) and 1838.5-1840.5 s (target fill at 7,597.75)
BREAKDOWN = [(0, 2.0, 2.0), (2.0, 5.0, 0.3), (30.0, 804.0, 26.0), (810.0, 1194.0, 13.0), (1199.5, 1556.5, 12.0),
             (1559.0, 1838.5, 10.0), (1838.5, 1840.5, 2.0), (1840.5, 1861.5, 2.0)]  # (start, end, out s)


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
    d.text((100, 690), "Target filled", font=ImageFont.truetype(B, 80), fill=GREEN)
    y = 830
    for t, f, c in [("ES short 2 @ 7,614.00", ImageFont.truetype(B, 56), CREAM),
                    ("Stop 7,618.00 (4 pts)  |  Out at 7,597.75", ImageFont.truetype(R, 42), MUTED),
                    ("+16.25 pts  |  4.1R" + tag, ImageFont.truetype(B, 44), GOLD)]:
        d.text((100, y), t, font=f, fill=c); y += 110
    d.text((100, 1300), "Define your risk. Wait for your setup.", font=ImageFont.truetype(B, 44), fill=CREAM)
    f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
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
    breakdown = "--breakdown" in sys.argv
    for s, e, secs in (BREAKDOWN if breakdown else SEGMENTS):
        for a in frames(src, s, e, round(secs * FPS)):
            if bad(a):
                dropped += 1
                continue
            if not show_times:
                a = np.array(hide(Image.fromarray(a), *AXIS))
            p.stdin.write(a.tobytes()); kept += 1; last = a
    if breakdown:
        p.stdin.close(); p.wait(); print("kept", kept, "dropped", dropped); return
    for _ in range(int(1.0 * FPS)):  # hold the exit frame
        p.stdin.write(last.tobytes())
    img = card(account)
    for _ in range(int(3.5 * FPS)):
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
