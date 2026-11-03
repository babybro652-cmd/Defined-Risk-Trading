"""Captioned trade breakdown (no voiceover) for Tim's 11/3/2026 ES short (paper).
Base: the --breakdown time-lapse from make_trade_reel_2.py (67.7 s, already privacy-cleaned, no-music version
42d6691f-9d11-4ad3-8d97-d5024b6a131f.mp4). Captions burn into the empty chart band at y 215-418 (above the
"2 @ 7614.00" entry label at y 433+, below the symbol header), x 40-900 (clear of the price scale and the
right-edge app buttons), nothing in the bottom 20%. The last frame is held to END_S so the closing lines read.
Music is added afterwards with drt/audio/add_audio.py (--target -23).
Usage: python3 make_breakdown_captions.py BASE.mp4 OUT_SILENT.mp4"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BAND = (215, 418)       # caption box vertical limits
XL, XR = 40, 900        # caption box horizontal limits
END_S = 75.0
HANDLE_Y = 1440         # @definedrisktrading on the last card (above the bottom 20% = y 1536)

CAPS = [  # (start, end, lines)
    (0.0, 2.8, ["Four points of risk.", "Sixteen points of reward."]),
    (2.8, 5.6, ["Here's how I think", "about a trade like this."]),
    (6.0, 8.8, ["Before I enter,", "I want to know"]),
    (8.8, 11.6, ["where price sits", "in the bigger picture."]),
    (12.2, 15.0, ["Price pushed into", "an area I had marked"]),
    (15.0, 17.6, ["and started to stall."]),
    (18.4, 21.2, ["I don't short because", "price looks high."]),
    (21.2, 23.8, ["I wait for", "my confirmation."]),
    (24.4, 27.4, ["When I got it, I sold", "2 contracts at 7,614."]),
    (28.2, 30.4, ["Risk comes first."]),
    (30.4, 33.4, ["Stop 4 points above,", "where the idea is wrong."]),
    (33.4, 36.4, ["Target 16 points lower,", "the next area I expected."]),
    (37.2, 39.8, ["That's 1 to 4,", "risk to reward."]),
    (39.8, 42.6, ["I set the bracket", "and let it work."]),
    (44.0, 46.4, ["No moving the stop."]),
    (46.4, 49.2, ["No grabbing", "a few points early."]),
    (53.0, 56.0, ["The plan was set", "before the trade,"]),
    (56.0, 59.0, ["so there was", "nothing to decide."]),
    (65.1, 68.4, ["Target filled.", "+16.25 pts a contract. Paper."]),
    (68.4, 70.8, ["Pick your spot.", "Define your risk."]),
    (70.8, 72.4, ["Let it work."]),
    (72.4, END_S, ["Full process in the Skool.", "Link in bio."]),
]


def fit(lines, d, size=62, minsize=44):
    while size > minsize:
        f = ImageFont.truetype(B, size)
        if max(d.textlength(t, font=f) for t in lines) <= XR - XL - 56:
            return f, size
        size -= 2
    return ImageFont.truetype(B, minsize), minsize


def overlay(lines, handle=False):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f, size = fit(lines, d)
    lh = int(size * 1.25)
    h = lh * len(lines) + 40
    y0 = BAND[0] + (BAND[1] - BAND[0] - h) // 2
    tw = max(d.textlength(t, font=f) for t in lines)
    bw = tw + 56; x0 = XL + (XR - XL - bw) / 2
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + h], radius=22, fill=(10, 8, 8, 200), outline=(232, 178, 92, 255), width=3)
    for i, t in enumerate(lines):
        x = XL + (XR - XL - d.textlength(t, font=f)) / 2
        d.text((x, y0 + 20 + i * lh), t, font=f, fill=(255, 250, 240, 255))
    if handle:
        hf = ImageFont.truetype(B, 40); t = "@definedrisktrading"
        tw = d.textlength(t, font=hf); x = XL + (XR - XL - tw) / 2
        d.rounded_rectangle([x - 24, HANDLE_Y - 14, x + tw + 24, HANDLE_Y + 60], radius=18, fill=(10, 8, 8, 200))
        d.text((x, HANDLE_Y), t, font=hf, fill=(232, 178, 92, 255))
    return im


def main():
    src, out = sys.argv[1], sys.argv[2]
    ovs = [overlay(l, handle=(i == len(CAPS) - 1)) for i, (_, _, l) in enumerate(CAPS)]
    dec = subprocess.Popen([FF, "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    sz = W * H * 3; n = 0; last = None; cache = {}
    total = int(round(END_S * FPS))
    while n < total:
        b = dec.stdout.read(sz)
        if len(b) == sz:
            last = Image.fromarray(np.frombuffer(b, dtype=np.uint8).reshape(H, W, 3))
        t = n / FPS
        idx = next((i for i, (s, e, _) in enumerate(CAPS) if s <= t < e), None)
        key = (idx, len(b) == sz)
        if len(b) == sz or key not in cache:
            fr = last.convert("RGBA")
            if idx is not None:
                fr = Image.alpha_composite(fr, ovs[idx])
            fr = fr.convert("RGB").tobytes()
            if len(b) != sz:
                cache[key] = fr
        else:
            fr = cache[key]
        enc.stdin.write(fr); n += 1
    enc.stdin.close(); enc.wait(); dec.kill()
    print("frames", n, "seconds", n / FPS)


if __name__ == "__main__":
    main()
