"""Trade reel from Tim's 10/30/2026 TradingView recording (Drive DRT Phone,
Screen_Recording_20261030_110252_TradingView.mp4, id 1gVJu7jkLbgwSBWWL_GqX-obaxLGvpH9f).
Same approach as posts/media/2026-10-28/make_trade_reels.py: speed-up, crop off the phone
status bar (clock, recorder icon, notification icons) and nav bar, drop bright frames
(notification shade / home screen), skip the landscape rotation + recorder toolbar (20.5-28 s)
and the final tap on the position (after 1140 s), then end on a result card.
Set CARD below once Tim confirms the outcome, then rerun.
Usage: python3 make_trade_reel.py SRC.mp4 OUT.mp4"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); GREEN = (90, 200, 140)
SEGMENTS = [(0, 20.5, 2), (28, 1140, 38)]  # (start s, end s, output seconds)
# Outcome not confirmed yet: the recording stops with the trade open at +1,850 USD (+18.5 pts).
CARD = ("Still running", "ES long 2 @ 7,635.25", "Stop 7,631.25 (4 pts)  |  Target 7,669.75",
        "+18.5 pts open, not closed yet")


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
    return a[200:1500].mean() > 70


def card(lines):
    im = Image.new("RGB", (W, H), (14, 10, 9)); d = ImageDraw.Draw(im)
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
    src, out = sys.argv[1], sys.argv[2]
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    kept = dropped = 0
    for s, e, secs in SEGMENTS:
        for a in frames(src, s, e, secs * FPS):
            if bad(a):
                dropped += 1
                continue
            p.stdin.write(a.tobytes()); kept += 1
    end = card(CARD)
    for _ in range(int(3.5 * FPS)):
        p.stdin.write(end.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
