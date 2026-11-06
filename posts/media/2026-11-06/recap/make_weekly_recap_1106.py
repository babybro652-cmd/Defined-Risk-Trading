"""Weekly recap reel for Mon 11/2 - Fri 11/6/2026 (0 Blotato credits).
Paper Mon-Thu, eval Fri. Clips from Tim's own QA'd trade reels, silent; music added after with drt/audio/add_audio.py.
Text cards (PIL) + short clips of Tim's own QA'd trade reels, silent; music added after with drt/audio/add_audio.py.
Usage: python3 make_weekly_recap.py OUT.mp4"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
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
    c(d, 560, "THIS WEEK, 11/2-11/6", f(B, 64), GOLD)
    c(d, 740, "9 ES trades", f(B, 120))
    c(d, 880, "5 wins. 4 losses.", f(B, 84))
    c(d, 1030, "Paper Monday to Thursday", f(R, 50), MUTED)
    c(d, 1100, "Evaluation account Friday", f(R, 50), MUTED)
    return im


def card_wed():
    im, d = base()
    c(d, 720, "WEDNESDAY", f(B, 64), GOLD)
    c(d, 880, "No trades.", f(B, 120))
    return im


def card_list():
    im, d = base()
    c(d, 250, "EVERY TRADE, 2 ES EACH", f(B, 60), GOLD)
    rows = [("Mon", "Stopped out", "-$400", RED, "paper"), ("Mon", "Short", "+$850", GREEN, "paper"),
            ("Tue", "Long, stopped", "-$375", RED, "paper"), ("Tue", "Short, target", "+$1,625", GREEN, "paper"),
            ("Thu", "Long", "+$900", GREEN, "paper"), ("Thu", "Long, re-entry", "-$625", RED, "paper"),
            ("Thu", "Long, target", "+$2,850", GREEN, "paper"),
            ("Fri", "Short", "-$500", RED, "eval"), ("Fri", "Short", "+$250", GREEN, "eval")]
    y = 390
    for i, (day, side, usd, col, acct) in enumerate(rows):
        if i == 7:
            d.line((140, y - 70, 940, y - 70), fill=GOLD, width=3); y += 20
        d.rounded_rectangle((90, y - 52, 990, y + 52), radius=20, fill=CARD)
        d.text((130, y), day, font=f(B, 46), fill=MUTED, anchor="lm")
        d.text((265, y), side, font=f(B, 46), fill=WHITE, anchor="lm")
        d.text((950, y), usd, font=f(B, 50), fill=col, anchor="rm")
        y += 128
    c(d, y + 10, "Mon-Thu paper  |  Fri evaluation account", f(R, 40), MUTED)
    return im


def card_net():
    im, d = base()
    c(d, 470, "PAPER, MONDAY TO THURSDAY", f(B, 56), GOLD)
    c(d, 610, "+$4,825", f(B, 130), GREEN)
    c(d, 740, "7 trades  |  4 wins, 3 losses", f(B, 52))
    d.line((340, 860, 740, 860), fill=GOLD, width=3)
    c(d, 970, "EVALUATION ACCOUNT, FRIDAY", f(B, 56), GOLD)
    c(d, 1110, "-$250", f(B, 130), RED)
    c(d, 1240, "2 trades  |  1 win, 1 loss", f(B, 52))
    c(d, 1380, "2 ES each, before commissions", f(R, 42), MUTED)
    return im


def card_lesson():
    im, d = base()
    c(d, 560, "Best 2 trades:", f(B, 76), GREEN)
    c(d, 660, "stop set, target set, hands off.", f(B, 54))
    c(d, 880, "Worst 2 trades:", f(B, 76), RED)
    c(d, 980, "the stop slipped past 4 points.", f(B, 54))
    c(d, 1160, "Next week: size for the slip.", f(B, 60), GOLD)
    return im


def card_sign():
    im, d = base()
    c(d, 760, "Define your risk.", f(B, 84))
    c(d, 890, "Wait for your setup.", f(B, 84))
    return im


def banner(label, pts, usd, col, acct, cover=None):
    """Transparent overlay: bottom band with the numbers (also hides the time axis), optional top cover with the label."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if cover:
        d.rectangle(cover, fill=NAVY + (255,))
    d.rectangle((0, 1540, W, H), fill=(12, 18, 32, 255))
    d.text((80, 1620), label, font=f(B, 56), fill=GOLD, anchor="lm")
    d.text((1000, 1620), pts, font=f(B, 56), fill=col, anchor="rm")
    d.text((80, 1720), "2 ES, " + acct, font=f(R, 42), fill=MUTED, anchor="lm")
    d.text((1000, 1720), usd, font=f(B, 50), fill=WHITE, anchor="rm")
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



P = lambda *a: os.path.join(M, *a)
SEGMENTS = [
    lambda: still(card_hook(), 3.5),
    lambda: clip_frames(P("2026-11-02", "phone", "es-short-1102.mp4"), 10.0, 4.5, banner("MON  Short", "+8.50 pts", "+$850", GREEN, "paper")),
    lambda: clip_frames(P("2026-11-03", "phone", "es-short-1103.mp4"), 49.5, 4.5, banner("TUE  Short", "+16.25 pts", "+$1,625", GREEN, "paper")),
    lambda: still(card_wed(), 2.0),
    lambda: clip_frames(P("2026-11-05", "phone", "es-1105-combined.mp4"), 47.5, 4.5, banner("THU  Long", "+28.50 pts", "+$2,850", GREEN, "paper", cover=(0, 230, W, 410))),
    lambda: clip_frames(P("2026-11-06", "phone", "es-1106-eval.mp4"), 35.0, 4.5, banner("FRI  Short", "+2.50 pts", "+$250", GREEN, "eval", cover=(0, 0, W, 590))),
    lambda: still(card_list(), 5.5),
    lambda: still(card_net(), 4.5),
    lambda: still(card_lesson(), 4.0),
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
