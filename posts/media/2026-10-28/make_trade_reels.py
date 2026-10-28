"""Trade reels from Tim's TradingView screen recordings (10/27 and 10/28/2026).
Speeds the recording up, crops off the phone status bar and nav bar, drops frames where a
notification shade or the home screen shows, and ends on a result card.
Usage: python3 make_trade_reels.py SRC_DIR OUT_DIR"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); GREEN = (90, 200, 140)

CLIPS = {
    "es-short-1027": dict(src="12b7T2azcd8yYEpMIVXq_Ok4oQ2kYnTJW.mp4", start=420, end=3170, secs=42,
                          card=("Target filled", "ES short 2 @ 7,746.00", "Stop 7,750.00 (4 pts)  |  Target 7,718.00",
                                "+28 pts  |  7R  |  paper")),
    "es-short-1028": dict(src="1L7Ob2LpMXcDmMn8pqsvc9tqNvZrbq0Y5.mp4", start=0, end=634, secs=30,
                          card=("Target filled", "ES short 2 @ 7,772.25", "Stop 7,776.25 (4 pts)  |  Target 7,759.50",
                                "+12.75 pts  |  3.2R  |  paper")),
}


def frames(src, start, end, n):
    rate = n / (end - start)
    cmd = [FF, "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", src,
           "-vf", f"fps={rate:.5f},crop=1080:1920:0:70", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
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
                    (lines[3], ImageFont.truetype(B, 50), GOLD)]:
        d.text((100, y), t, font=f, fill=c); y += 110
    d.text((100, 1300), "Define your risk. Wait for your setup.", font=ImageFont.truetype(B, 44), fill=CREAM)
    f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    return np.array(im)


def main():
    src_dir, out = sys.argv[1], sys.argv[2]
    for name, c in CLIPS.items():
        p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                              "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                              "-movflags", "+faststart", os.path.join(out, name + ".mp4")], stdin=subprocess.PIPE)
        kept = dropped = 0
        for a in frames(os.path.join(src_dir, c["src"]), c["start"], c["end"], c["secs"] * FPS):
            if bad(a):
                dropped += 1
                continue
            p.stdin.write(a.tobytes()); kept += 1
        end = card(c["card"])
        for _ in range(int(3.5 * FPS)):
            p.stdin.write(end.tobytes())
        p.stdin.close(); p.wait()
        print(name, "kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
