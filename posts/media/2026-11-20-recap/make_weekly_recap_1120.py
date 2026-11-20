"""Weekly recap reel, Mon 11/16 - Fri 11/20/2026 (0 Blotato credits). DRAFT for Tim's go.
Frame 0 = Tim's 11/20 eval chart (no fade-in). Clips/stills from QA'd trade media only; music added after
with drt/audio/add_audio.py. Facts only from posts/2026-11-16..20 trade files.
Usage: python3 make_weekly_recap_1120.py OUT.mp4"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
M = os.path.join(REPO, "posts", "media")
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
NAVY = (16, 24, 40); CARD = (28, 40, 64); WHITE = (240, 242, 246); MUTED = (150, 165, 190)
GREEN = (72, 199, 116); RED = (232, 92, 92); TEAL = (88, 196, 214); AMBER = (240, 176, 72)
f = lambda p, s: ImageFont.truetype(p, s)
P = lambda *a: os.path.join(M, *a)


def base():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((W / 2, 1780), "DEFINED RISK TRADING", font=f(B, 38), fill=MUTED, anchor="mm")
    d.line((360, 1740, 720, 1740), fill=TEAL, width=3)
    return im, d


def c(d, y, t, font, fill=WHITE):
    d.text((W / 2, y), t, font=font, fill=fill, anchor="mm")


def overlay(label, pts, usd, col, sub, top=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if top:
        h, l1, l2, c1 = top
        d.rectangle((0, 0, W, h), fill=NAVY + (255,))
        c(d, h * 0.38, l1, f(B, 66), c1); c(d, h * 0.74, l2, f(B, 46), WHITE)
    d.rectangle((0, 1540, W, H), fill=(10, 16, 28, 255))
    d.text((70, 1620), label, font=f(B, 54), fill=TEAL, anchor="lm")
    d.text((1010, 1620), pts, font=f(B, 54), fill=col, anchor="rm")
    d.text((70, 1720), sub, font=f(R, 40), fill=MUTED, anchor="lm")
    d.text((1010, 1720), usd, font=f(B, 50), fill=WHITE, anchor="rm")
    return im


def read_clip(path, start, dur):
    raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(start), "-i", path, "-t", str(dur), "-an",
                          "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def clip(path, start, dur, ov):
    out = []
    for fr in read_clip(path, start, dur):
        im = Image.fromarray(fr).convert("RGBA"); im.alpha_composite(ov); out.append(np.array(im.convert("RGB")))
    return out


def still(im, secs):
    a = np.array(im.convert("RGB")); return [a] * int(round(secs * FPS))


HOOK = (400, "MY ES WEEK", "9 trades, 3 separate logs", AMBER)
EVAL_OV = overlay("FRI  Long 1 ES", "+12 pts", "+$600", GREEN, "25K eval, before fees", top=HOOK)


def eval_clip():
    r = P("2026-11-20-trade", "reel.mp4")
    return clip(r, 0.0, 2.0, EVAL_OV) + clip(r, 21.0, 2.5, EVAL_OV)


def paper_still(secs):
    im = Image.new("RGB", (W, H), NAVY)
    ch = Image.open(P("2026-11-20-trade", "paper-2-clean.jpg")).convert("RGB")
    s = 1540 / ch.height; ch = ch.resize((int(ch.width * s), 1540), Image.LANCZOS)
    im.paste(ch, ((W - ch.width) // 2, 0))
    im = im.convert("RGBA")
    im.alpha_composite(overlay("FRI  Long 2 ES", "+23 pts", "+$2,300", GREEN, "PAPER, practice only",
                               top=(340, "PAPER ACCOUNT", "Practice, not real money", AMBER)))
    return still(im, secs)


def funded_still(secs):
    im = Image.open(P("2026-11-17-trade", "screenshot_clean.jpg")).convert("RGBA").resize((W, H))
    im.alpha_composite(overlay("TUE  Funded, day 1", "4 trades", "+$100", GREEN, "1 ES, day result"))
    return still(im, secs)


def wed_clip():
    return clip(P("2026-11-18-trade", "reel-tt-music.mp4"), 64.7, 3.5,
                overlay("WED  Short 2 ES", "+10.25 pts", "+$1,025", GREEN, "PAPER, after a -$400 stop"))


def card_list():
    im, d = base()
    c(d, 210, "THIS WEEK, BY ACCOUNT", f(B, 58), AMBER)
    groups = [("25K EVAL", [("Fri", "Long 1 ES", "+$600", GREEN)]),
              ("FUNDED", [("Tue", "4 trades, 1 ES", "+$100", GREEN)]),
              ("PAPER (PRACTICE)", [("Mon", "Long 2 ES", "+$500", GREEN), ("Wed", "Short 2 ES", "-$400", RED),
                                    ("Wed", "Short 2 ES", "+$1,025", GREEN), ("Fri", "Long 2 ES", "+$2,300", GREEN)])]
    y = 330
    for title, rows in groups:
        d.text((100, y), title, font=f(B, 36), fill=MUTED, anchor="lm"); y += 72
        for day, side, usd, col in rows:
            d.rounded_rectangle((90, y - 48, 990, y + 48), radius=20, fill=CARD)
            d.text((130, y), day, font=f(B, 44), fill=MUTED, anchor="lm")
            d.text((260, y), side, font=f(B, 44), fill=WHITE, anchor="lm")
            d.text((950, y), usd, font=f(B, 48), fill=col, anchor="rm")
            y += 112
        y += 24
    c(d, y + 20, "ES, before fees", f(R, 40), MUTED)
    return im


def card_net():
    im, d = base()
    c(d, 400, "25K EVAL", f(B, 56), AMBER); c(d, 515, "+$600", f(B, 116), GREEN); c(d, 625, "1 trade  |  1 win", f(B, 46))
    d.line((360, 715, 720, 715), fill=TEAL, width=3)
    c(d, 810, "FUNDED", f(B, 56), AMBER); c(d, 925, "+$100", f(B, 116), GREEN); c(d, 1035, "4 trades  |  3 wins, 1 loss", f(B, 46))
    d.line((360, 1125, 720, 1125), fill=TEAL, width=3)
    c(d, 1220, "PAPER (PRACTICE)", f(B, 56), AMBER); c(d, 1335, "+$3,425", f(B, 116), GREEN)
    c(d, 1445, "4 trades  |  3 wins, 1 loss", f(B, 46))
    c(d, 1560, "Separate logs, never one total", f(R, 42), MUTED)
    return im


def card_process():
    im, d = base()
    c(d, 560, "Primarily New York.", f(B, 76))
    c(d, 670, "Always looking for my setup.", f(B, 60))
    d.line((360, 800, 720, 800), fill=TEAL, width=3)
    c(d, 930, "2 losses this week:", f(B, 60), MUTED)
    c(d, 1040, "3.5 and 4 points.", f(B, 76), RED)
    return im


def card_sign():
    im, d = base()
    c(d, 780, "Define your risk.", f(B, 84))
    c(d, 910, "Wait for your setup.", f(B, 84))
    return im


def fade(seq, n=6, fade_in=True):
    seq = list(seq); bg = np.array(NAVY, dtype=float)
    for i in range(min(n, len(seq))):
        k = (i + 1) / (n + 1)
        if fade_in:
            seq[i] = (seq[i] * k + bg * (1 - k)).astype(np.uint8)
        j = len(seq) - 1 - i
        seq[j] = (seq[j] * k + bg * (1 - k)).astype(np.uint8)
    return seq


SEGMENTS = [
    eval_clip,  # frame 0 = chart, no fade-in
    lambda: paper_still(3.5),
    wed_clip,
    lambda: funded_still(3.0),
    lambda: still(card_list(), 5.5),
    lambda: still(card_net(), 4.0),
    lambda: still(card_process(), 3.0),
    lambda: still(card_sign(), 2.0),
]

if __name__ == "__main__":
    out = sys.argv[1]
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264",
                          "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = 0
    for i, seg in enumerate(SEGMENTS):
        for fr in fade(seg(), fade_in=(i != 0)):
            p.stdin.write(fr.tobytes()); n += 1
    p.stdin.close(); p.wait()
    print("frames", n, "seconds", n / FPS)
