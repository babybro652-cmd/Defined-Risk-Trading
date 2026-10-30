"""Weekly recap reel, week ending Fri 10/30/2026 (0 Blotato credits).
Text cards (PIL) + short clips of Tim's own QA'd trade reels, silent; music added after with drt/audio/add_audio.py.
Usage: python3 make_weekly_recap.py OUT.mp4"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
M = os.path.join(REPO, "posts", "media")
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
NAVY = (18, 28, 48); CARD = (28, 42, 70); WHITE = (240, 242, 246); MUTED = (150, 165, 190)
GREEN = (72, 199, 116); RED = (232, 92, 92); GOLD = (214, 180, 96)
f = lambda p, s: ImageFont.truetype(p, s)


def base():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((W / 2, 1760), "DEFINED RISK TRADING", font=f(B, 40), fill=MUTED, anchor="mm")
    d.line((340, 1720, 740, 1720), fill=GOLD, width=3)
    return im, d


def c(d, y, t, font, fill=WHITE):
    d.text((W / 2, y), t, font=font, fill=fill, anchor="mm")


def card_hook():
    im, d = base()
    c(d, 600, "WEEKLY RECAP", f(B, 64), GOLD)
    c(d, 780, "5 ES trades", f(B, 120))
    c(d, 920, "3 wins. 2 losses.", f(B, 84))
    c(d, 1060, "2 contracts each, paper account", f(R, 46), MUTED)
    return im


def card_thu():
    im, d = base()
    c(d, 700, "THURSDAY", f(B, 64), GOLD)
    c(d, 860, "Sat out.", f(B, 120))
    c(d, 1010, "Chop. Not my setup.", f(B, 64))
    return im


def card_fri():
    im, d = base()
    c(d, 620, "FRIDAY", f(B, 64), GOLD)
    c(d, 790, "2 stops first", f(B, 100), RED)
    c(d, 920, "-4 pts each, -$400 each", f(B, 56))
    c(d, 1080, "Same 4-point stop on the next one", f(R, 46), MUTED)
    return im


def card_list():
    im, d = base()
    c(d, 330, "EVERY TRADE", f(B, 64), GOLD)
    rows = [("Tue", "Short", "+28.00", GREEN), ("Wed", "Short", "+12.75", GREEN), ("Fri", "Long", "-4.00", RED),
            ("Fri", "Long", "-4.00", RED), ("Fri", "Long", "+13.75", GREEN)]
    y = 500
    for day, side, pts, col in rows:
        d.rounded_rectangle((110, y - 70, 970, y + 70), radius=24, fill=CARD)
        d.text((160, y), day, font=f(B, 56), fill=MUTED, anchor="lm")
        d.text((330, y), side, font=f(B, 56), fill=WHITE, anchor="lm")
        d.text((920, y), pts + " pts", font=f(B, 56), fill=col, anchor="rm")
        y += 175
    return im


def card_net():
    im, d = base()
    c(d, 560, "NET FOR THE WEEK", f(B, 64), GOLD)
    c(d, 740, "+46.50 pts", f(B, 130), GREEN)
    c(d, 910, "+$4,650", f(B, 120))
    c(d, 1060, "about +11.6R", f(B, 72))
    c(d, 1210, "2 ES, paper account, before commissions", f(R, 42), MUTED)
    return im


def card_lesson():
    im, d = base()
    c(d, 600, "Losses: -8 pts.", f(B, 80), RED)
    c(d, 720, "Wins: +54.50 pts.", f(B, 80), GREEN)
    c(d, 900, "Every stop was 4 points,", f(B, 62))
    c(d, 990, "set before the entry.", f(B, 62))
    return im


def card_sign():
    im, d = base()
    c(d, 760, "Define your risk.", f(B, 84))
    c(d, 890, "Wait for your setup.", f(B, 84))
    return im


def banner(label, pts, usd, col):
    """Transparent overlay band for a chart clip."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 1560, 1020, 1800), radius=28, fill=(12, 18, 32, 235))
    d.text((100, 1630), label, font=f(B, 56), fill=GOLD, anchor="lm")
    d.text((980, 1630), pts, font=f(B, 56), fill=col, anchor="rm")
    d.text((100, 1730), "2 ES, paper", font=f(R, 42), fill=MUTED, anchor="lm")
    d.text((980, 1730), usd, font=f(B, 50), fill=WHITE, anchor="rm")
    return im


def read_clip(path, start, dur):
    raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-vf", f"scale={W}:{H},fps={FPS}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def clip_frames(path, start, dur, ov):
    out = []
    for fr in read_clip(path, start, dur):
        im = Image.fromarray(fr).convert("RGBA"); im.alpha_composite(ov); out.append(np.array(im.convert("RGB")))
    return out


def still(im, secs):
    a = np.array(im); return [a] * int(secs * FPS)


def fade(seq, n=8):
    """Fade in/out from navy at each segment boundary."""
    seq = list(seq); bg = np.array(NAVY, dtype=float)
    for i in range(min(n, len(seq))):
        k = (i + 1) / (n + 1)
        seq[i] = (seq[i] * k + bg * (1 - k)).astype(np.uint8)
        j = len(seq) - 1 - i
        seq[j] = (seq[j] * k + bg * (1 - k)).astype(np.uint8)
    return seq


SEGMENTS = [
    lambda: still(card_hook(), 3.0),
    # clip windows chosen clear of the flash / notification frames found in QA 10/30
    lambda: clip_frames(os.path.join(M, "2026-10-28", "es-short-1027.mp4"), 30.5, 4.5, banner("TUE  Short", "+28.00 pts", "+$2,800", GREEN)),
    lambda: clip_frames(os.path.join(M, "2026-10-28", "es-short-1028.mp4"), 24.0, 4.5, banner("WED  Short", "+12.75 pts", "+$1,275", GREEN)),
    lambda: still(card_thu(), 2.5),
    lambda: still(card_fri(), 3.0),
    lambda: clip_frames(os.path.join(M, "2026-10-30", "phone", "es-long-1030-clean.mp4"), 20.0, 4.5, banner("FRI  Long", "+13.75 pts", "+$1,375", GREEN)),
    lambda: still(card_list(), 4.0),
    lambda: still(card_net(), 4.0),
    lambda: still(card_lesson(), 3.5),
    lambda: still(card_sign(), 2.5),
]

if __name__ == "__main__":
    out = sys.argv[1]
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = 0
    for seg in SEGMENTS:
        for fr in fade(seg()):
            p.stdin.write(fr.tobytes()); n += 1
    p.stdin.close(); p.wait()
    print("frames", n, "seconds", n / FPS)
