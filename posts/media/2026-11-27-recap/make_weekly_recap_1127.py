"""Weekly recap reel, Mon 11/23 - Fri 11/27/2026 (0 Blotato credits). DRAFT for Tim's go.
Frame 0 = Tim's 11/24 NY chart at the +15 pt exit (no fade-in). Clips/stills only from the QA'd, Tim-approved trade
media of 11/23-11/25. Points only, no dollar amounts (Tim OK'd). Facts from posts/2026-11-23..25 trade files.
Music added after with drt/audio/add_audio.py.
Usage: python3 make_weekly_recap_1127.py OUT.mp4"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/bin/ffmpeg"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
M = os.path.join(REPO, "posts", "media")
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
NAVY = (16, 24, 40); CARD = (28, 40, 64); WHITE = (240, 242, 246); MUTED = (150, 165, 190)
GREEN = (72, 199, 116); RED = (232, 92, 92); TEAL = (88, 196, 214); AMBER = (240, 176, 72)
f = lambda p, s: ImageFont.truetype(p, s)
P = lambda *a: os.path.join(M, *a)


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout)


def base():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((W / 2, 1780), "DEFINED RISK TRADING", font=f(B, 38), fill=MUTED, anchor="mm")
    d.line((360, 1740, 720, 1740), fill=TEAL, width=3)
    return im, d


def c(d, y, t, font, fill=WHITE):
    d.text((W / 2, y), t, font=font, fill=fill, anchor="mm")


def overlay(label, pts, col, sub, top=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if top:
        h, l1, l2, c1 = top
        d.rectangle((0, 0, W, h), fill=NAVY + (255,))
        c(d, h * 0.38, l1, f(B, 66), c1); c(d, h * 0.74, l2, f(B, 46), WHITE)
    d.rectangle((0, 1500, W, H), fill=(10, 16, 28, 255))
    d.text((70, 1570), label, font=f(B, 50), fill=TEAL, anchor="lm")
    d.text((70, 1665), pts, font=f(B, 72), fill=col, anchor="lm")
    d.text((70, 1760), sub, font=f(R, 40), fill=MUTED, anchor="lm")
    return im


def read_clip(path, start, dur_s):
    raw = subprocess.run([FF, "-loglevel", "error", "-ss", str(start), "-i", path, "-t", str(dur_s), "-an",
                          "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def clip_tail(path, secs, ov):
    out = []
    for fr in read_clip(path, max(0.0, dur(path) - secs - 0.05), secs):
        im = Image.fromarray(fr).convert("RGBA"); im.alpha_composite(ov); out.append(np.array(im.convert("RGB")))
    return out


def hold_last(path, secs, ov):
    """Final frame (flat, after the exit fill: no USD order/position labels) held still."""
    fr = read_clip(path, max(0.0, dur(path) - 0.3), 0.3)[-1]
    im = Image.fromarray(fr).convert("RGBA"); im.alpha_composite(ov); return still(im, secs)


def still(im, secs):
    a = np.array(im.convert("RGB")); return [a] * int(round(secs * FPS))


def still_png(path, ov, secs):
    im = Image.open(path).convert("RGBA").resize((W, H)); im.alpha_composite(ov); return still(im, secs)


HOOK = (400, "MY ES WEEK", "5 trades: 4 wins, 1 loss", AMBER)


def seg_a():  # 11/24 NY pair, tail of reel A = the 7,172.50 exit (flat, no USD labels)
    return clip_tail(P("2026-11-24-trades", "reel-a.mp4"), 3.2,
                     overlay("TUE  2 shorts, 1 ES", "-4.5 / +15 pts", GREEN, "Stopped, then re-entered", top=HOOK))


def seg_b():
    return still_png(P("2026-11-24-trades", "still_b.png"),
                     overlay("TUE evening  Short 1 ES", "+38.75 pts", GREEN, "After the 6 PM reopen"), 3.0)


def seg_c():
    return hold_last(P("2026-11-25-trades", "reel-c.mp4"), 2.8,
                     overlay("WED 4:54 AM  Long 2 ES", "+2.25 pts each", GREEN, "Stop moved above entry"))


def seg_d():
    return still_png(P("2026-11-25-trades", "still_d.png"),
                     overlay("WED 9:45 AM  Long + add", "+10.75 pts", GREEN, "8.5 + 2.25 on 2 ES"), 3.0)


def seg_paper():
    return hold_last(P("2026-11-23-trade", "reel.mp4"), 2.6,
                     overlay("MON  PAPER  Long 1 ES", "+13.75 pts", GREEN, "Practice, kept in its own log",
                             top=(340, "PAPER ACCOUNT", "Practice, not real money", AMBER)))


def card_list():
    im, d = base()
    c(d, 230, "THE WEEK IN POINTS", f(B, 60), AMBER)
    rows = [("Tue", "Short 1 ES (stop)", "-4.5", RED), ("Tue", "Short 1 ES", "+15", GREEN),
            ("Tue", "Short 1 ES, evening", "+38.75", GREEN), ("Wed", "Long 2 ES", "+2.25 x2", GREEN),
            ("Wed", "Long 1 + add 1", "+8.5 / +2.25", GREEN)]
    y = 380
    for day, side, pts, col in rows:
        d.rounded_rectangle((70, y - 52, 1010, y + 52), radius=20, fill=CARD)
        d.text((105, y), day, font=f(B, 42), fill=MUTED, anchor="lm")
        d.text((215, y), side, font=f(B, 40), fill=WHITE, anchor="lm")
        d.text((975, y), pts, font=f(B, 44), fill=col, anchor="rm")
        y += 124
    d.text((100, y + 10), "PAPER (PRACTICE, SEPARATE)", font=f(B, 34), fill=MUTED, anchor="lm"); y += 90
    d.rounded_rectangle((70, y - 52, 1010, y + 52), radius=20, fill=CARD)
    d.text((105, y), "Mon", font=f(B, 42), fill=MUTED, anchor="lm")
    d.text((215, y), "Long 1 ES", font=f(B, 40), fill=WHITE, anchor="lm")
    d.text((975, y), "+13.75", font=f(B, 44), fill=GREEN, anchor="rm")
    c(d, y + 130, "ES points per contract, before fees", f(R, 38), MUTED)
    c(d, y + 190, "Thu: holiday.  Fri: sat out the early close.", f(R, 38), MUTED)
    return im


def card_net():
    im, d = base()
    c(d, 520, "REAL TRADES", f(B, 58), AMBER)
    c(d, 660, "+64.5 pts", f(B, 130), GREEN)
    c(d, 790, "added across all contracts", f(R, 42), MUTED)
    c(d, 890, "5 trades  |  4 wins, 1 loss", f(B, 50))
    d.line((360, 990, 720, 990), fill=TEAL, width=3)
    c(d, 1100, "PAPER", f(B, 58), AMBER)
    c(d, 1220, "+13.75 pts", f(B, 96), GREEN)
    c(d, 1330, "1 trade, kept separate", f(R, 42), MUTED)
    return im


def card_process():
    im, d = base()
    c(d, 540, "NY is my main session", f(B, 68))
    c(d, 640, "unless my setup shows.", f(B, 68))
    d.line((360, 770, 720, 770), fill=TEAL, width=3)
    c(d, 900, "The only loss:", f(B, 58), MUTED)
    c(d, 1010, "4 pt stop, filled at 4.5", f(B, 66), RED)
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
    seg_a,  # frame 0 = chart, no fade-in
    seg_b, seg_c, seg_d, seg_paper,
    lambda: still(card_list(), 5.0),
    lambda: still(card_net(), 3.5),
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
