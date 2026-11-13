"""Weekly recap reel, Sun 11/8 - Fri 11/13/2026 (0 Blotato credits). DRAFT for Tim's go.
Text cards (PIL) + short clips of Tim's own QA'd trade reels (silent); music after with drt/audio/add_audio.py.
Only facts from the approved trade posts: 11/9 paper, 11/12 loss, 11/12 Apex eval, 11/13 Apex funded.
Usage: python3 make_weekly_recap_1113.py OUT.mp4"""
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
P = lambda *a: os.path.join(M, *a)


def base():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((W / 2, 1760), "DEFINED RISK TRADING", font=f(B, 40), fill=MUTED, anchor="mm")
    d.line((340, 1720, 740, 1720), fill=GOLD, width=3)
    return im, d


def c(d, y, t, font, fill=WHITE):
    d.text((W / 2, y), t, font=font, fill=fill, anchor="mm")


def card_hook():
    im, d = base()
    c(d, 560, "MY ES WEEK", f(B, 64), GOLD)
    c(d, 720, "Eval passed.", f(B, 110))
    c(d, 850, "Funded day 1: +$450.", f(B, 80), GREEN)
    c(d, 1010, "7 posted trades. 5 wins, 2 losses.", f(R, 50), MUTED)
    return im


def card_list():
    im, d = base()
    c(d, 230, "THE TRADES I POSTED", f(B, 60), GOLD)
    groups = [("PAPER", [("Sun", "Long 2", "+$1,125", GREEN), ("Mon", "Short 2", "+$1,575", GREEN)]),
              ("SEPARATE ACCOUNT", [("Thu", "Short 2, stopped", "-$375", RED)]),
              ("APEX 25K EVAL", [("Thu", "Short 2, stopped", "-$425", RED), ("Thu", "Short 2, add 2", "+$1,025", GREEN),
                                 ("Thu", "Short 2, add 2", "+$1,825", GREEN)]),
              ("APEX 25K FUNDED", [("Fri", "Short 1", "+$450", GREEN)])]
    y = 340
    for title, rows in groups:
        d.text((100, y), title, font=f(B, 34), fill=MUTED, anchor="lm"); y += 70
        for day, side, usd, col in rows:
            d.rounded_rectangle((90, y - 48, 990, y + 48), radius=20, fill=CARD)
            d.text((130, y), day, font=f(B, 44), fill=MUTED, anchor="lm")
            d.text((260, y), side, font=f(B, 44), fill=WHITE, anchor="lm")
            d.text((950, y), usd, font=f(B, 48), fill=col, anchor="rm")
            y += 112
        y += 20
    c(d, y + 10, "ES, before fees", f(R, 40), MUTED)
    return im


def card_net():
    im, d = base()
    c(d, 420, "PAPER", f(B, 56), GOLD)
    c(d, 540, "+$2,700", f(B, 120), GREEN)
    c(d, 650, "2 trades  |  2 wins", f(B, 50))
    d.line((340, 750, 740, 750), fill=GOLD, width=3)
    c(d, 850, "APEX 25K, EVAL + FUNDED", f(B, 56), GOLD)
    c(d, 970, "+$2,875", f(B, 120), GREEN)
    c(d, 1080, "4 trades  |  3 wins, 1 loss", f(B, 50))
    d.line((340, 1180, 740, 1180), fill=GOLD, width=3)
    c(d, 1280, "SEPARATE ACCOUNT", f(B, 56), GOLD)
    c(d, 1390, "-$375", f(B, 110), RED)
    c(d, 1510, "Separate logs, never one total", f(R, 42), MUTED)
    return im


def card_honest():
    im, d = base()
    c(d, 520, "On the record:", f(B, 76), GOLD)
    c(d, 680, "Sunday's long was", f(B, 60)); c(d, 760, "outside the New York session.", f(B, 54))
    c(d, 930, "Friday's short came", f(B, 60)); c(d, 1010, "before my 10 AM rule.", f(B, 54))
    c(d, 1180, "Both won. Both still count", f(R, 50), MUTED); c(d, 1250, "as outside my rules.", f(R, 50), MUTED)
    return im


def card_lesson():
    im, d = base()
    c(d, 600, "Biggest loss: -$425.", f(B, 76), RED)
    c(d, 720, "4 pt stop + 0.25 slippage.", f(B, 54))
    c(d, 920, "I took the stop.", f(B, 70))
    c(d, 1020, "Then I kept following the plan.", f(B, 54))
    return im


def card_sign():
    im, d = base()
    c(d, 760, "Define your risk.", f(B, 84))
    c(d, 890, "Wait for your setup.", f(B, 84))
    return im


def banner(label, pts, usd, col, sub, cover=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for cv in (cover or []):
        d.rectangle(cv, fill=NAVY + (255,))
    d.rectangle((0, 1540, W, H), fill=(12, 18, 32, 255))
    d.text((80, 1620), label, font=f(B, 56), fill=GOLD, anchor="lm")
    d.text((1000, 1620), pts, font=f(B, 56), fill=col, anchor="rm")
    d.text((80, 1720), sub, font=f(R, 42), fill=MUTED, anchor="lm")
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


def chart_still(secs):
    im, d = base()
    d.rectangle((0, 1540, W, H), fill=(12, 18, 32))
    c(d, 300, "THURSDAY, APEX 25K EVAL", f(B, 56), GOLD)
    c(d, 380, "Trade 2 add and cover, then trade 3", f(R, 42), MUTED)
    ch = Image.open(P("2026-11-12-apex", "chart_clean.png")).convert("RGB")
    im.paste(ch, (0, 460))
    d = ImageDraw.Draw(im)
    d.text((80, 1620), "EVAL PASSED", font=f(B, 56), fill=GOLD, anchor="lm")
    d.text((1000, 1620), "+$2,425", font=f(B, 56), fill=GREEN, anchor="rm")
    d.text((80, 1720), "3 trades, gross", font=f(R, 42), fill=MUTED, anchor="lm")
    return still(im, secs)


def still(im, secs):
    a = np.array(im); return [a] * int(secs * FPS)


def fade(seq, n=8):
    seq = list(seq); bg = np.array(NAVY, dtype=float)
    for i in range(min(n, len(seq))):
        k = (i + 1) / (n + 1)
        seq[i] = (seq[i] * k + bg * (1 - k)).astype(np.uint8)
        j = len(seq) - 1 - i
        seq[j] = (seq[j] * k + bg * (1 - k)).astype(np.uint8)
    return seq


SEGMENTS = [
    lambda: still(card_hook(), 3.5),
    lambda: clip_frames(P("2026-11-09", "phone", "es-1109-trades.mp4"), 15.0, 4.5,
                        banner("SUN  Long", "+11.25 pts", "+$1,125", GREEN, "2 ES, paper")),
    lambda: clip_frames(P("2026-11-09", "phone", "es-1109-trades.mp4"), 47.0, 4.5,
                        banner("MON  Short", "+15.75 pts", "+$1,575", GREEN, "2 ES, paper", cover=[(0, 0, W, 180)])),
    lambda: clip_frames(P("2026-11-12-loss", "loss-trade.mp4"), 22.0, 4.5,
                        banner("THU  Short", "-3.75 pts", "-$375", RED, "2 ES, stopped", cover=[(0, 0, W, 420)])),
    lambda: chart_still(4.5),
    lambda: still(card_list(), 6.0),
    lambda: still(card_net(), 5.0),
    lambda: still(card_honest(), 4.5),
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
