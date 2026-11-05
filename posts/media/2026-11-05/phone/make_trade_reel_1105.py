"""Time-lapse trade reels (DRT + personal), combined cut and breakdown clip from Tim's 11/5/2026 TradingView recordings
(Drive DRT Phone, second upload ~11:50 AM after "I think I gave you the wrong videos"), 1080x2340, ES1! 1m:
V1 Screen_Recording_20261105_110059_TradingView.mp4 (11M5MfoHF9KPWeHVggMSSNhWVZrLoEwgT, 4:49.5, ~16 fps), 10:56:10-11:00:59 ET.
  Long 2 @ 7,448.25 (filled before the recording, 10:55 bar). Stop 7,444.50, dragged to 7,444.25 at 21.6-30.6 s (1 tick wider,
  4.00 pts). Target 7,497.75. Manual exit: tap on the position's close X at ~285.0 s, sold 2 @ 7,457.25 (+9.00 pts, +$900).
V2 Screen_Recording_20261105_111010_TradingView.mp4 (1biHbRIrDb-FnYRYf2UKIruf_LVFG19AP, same bytes as the first upload
  1pdagl6atV6IkOBr9R4QcFSUu1SGVoIZE, 3:06.3). Long 2 @ 7,442.75, stop 7,438.75, target 7,471.25 filled at 182.4 s (+$2,850).
Cut (10 fps scan of every frame + 1 fps sheets): V1 21.6-30.8 s stop-order menu ("Sell 2 @7,444.50 Stop / Modify / Cancel")
while the stop is dragged; V2 61.8-74.9 s interval menu + 15m detour (aggregated fill labels), 95.0-106.6 s chart reload +
"Trading account / Paper Trading" sheet and "Failed to login" dialog. Status bar (clock, recorder, app icons) cropped (top 98 px);
everything below source y 1788 (time axis, toolbar, tab bar, nav bar, order-ticket bar) covered with chart background.
Two-part series (Tim 11/5): Part 1 "Why I don't move my stop to breakeven" (V1), Part 2 "Same setup, new entry,
target hit" (V2); title band burned in over the empty chart area, end card per part. --mode combined = both in one reel.
--mode breakdown = ~78 s time-lapse of both for Tim's own video (no title band, no card).
Middle trade (impatient re-entry, long 2 @ 7,452.00, out 7,445.75, -$625) is not in these two videos: combined and breakdown
show Tim's 1m screenshot of all three fills (--still, same crop/cover, ~3 s).
Usage: python3 make_trade_reel_1105.py V1.mp4 V2.mp4 OUT.mp4 --mode part1|part2|combined|breakdown --still SHOT.jpg
       [--account paper|live]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
COVER = 1690  # crop-coordinate row where the bottom cover starts (source y 1788)
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (225, 95, 85); GREEN = (90, 200, 140)
BG = (14, 10, 9)
# (video, start, end, output seconds); real speed on the opening fill marker and on each exit
PART1 = [("v1", 0, 2.0, 2.0), ("v1", 2.0, 21.6, 3.0), ("v1", 30.8, 283.5, 28.0), ("v1", 283.5, 285.8, 2.3),
         ("v1", 285.8, 289.4, 1.2), ("hold", 1.0), ("card", "p1", 5.5)]
PART2 = [("v2", 0, 2.0, 2.0), ("v2", 2.0, 61.8, 7.0), ("v2", 74.9, 95.0, 3.0), ("v2", 106.6, 181.4, 20.0),
         ("v2", 181.4, 183.4, 2.0), ("v2", 183.4, 186.2, 1.5), ("hold", 1.0), ("card", "p2", 5.5)]
COMBINED = [("v1", 0, 1.5, 1.5), ("v1", 1.5, 21.6, 1.5), ("v1", 30.8, 283.5, 14.0), ("v1", 283.5, 285.8, 2.3),
            ("hold", 0.5), ("card", "p1", 3.5), ("still", 3.0),
            ("v2", 0, 1.5, 1.5), ("v2", 1.5, 61.8, 6.0), ("v2", 74.9, 95.0, 2.0), ("v2", 106.6, 181.4, 13.0),
            ("v2", 181.4, 183.4, 2.0), ("v2", 183.4, 186.2, 1.0), ("hold", 1.0), ("card", "both", 5.5)]
BREAKDOWN = [("v1", 0, 2.0, 2.0), ("v1", 2.0, 21.6, 3.0), ("v1", 30.8, 283.5, 30.0), ("v1", 283.5, 285.8, 2.3),
             ("v1", 285.8, 289.4, 2.0), ("still", 3.0),
             ("v2", 0, 2.0, 2.0), ("v2", 2.0, 61.8, 10.0), ("v2", 74.9, 95.0, 4.0), ("v2", 106.6, 181.4, 22.0),
             ("v2", 181.4, 183.4, 2.0), ("v2", 183.4, 186.2, 2.8)]
TITLES = {"v1": ("Part 1", "Why I don't move my stop to breakeven"),
          "v2": ("Part 2", "Same setup, new entry, target hit"),
          "still": ("In between", "Impatient re-entry: -$625")}
BAND = (240, 400)  # crop rows of the title band (empty chart area above the price action)


def frames(src, start, end, n):
    rate = n / (end - start)
    cmd = [FF, "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", src,
           "-vf", f"fps={rate:.5f},crop={W}:{H}:0:{TOP}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    sz = W * H * 3; k = 0
    while k < n:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        k += 1
        yield np.frombuffer(b, dtype=np.uint8).reshape(H, W, 3)
    p.kill()


def bad(a):
    """Guard: bottom sheet / dialog (bright panel), home screen, black frame, expanded indicator legend."""
    m = a[100:1700].mean()
    sheet = (a[900:1700].mean(axis=2) > 40).mean() > 0.25
    legend = (a[50:240, 0:560].mean(axis=2) > 90).mean() > 0.045
    return m > 40 or m < 8 or sheet or legend


def clean(a):
    a = a.copy()
    a[COVER:] = np.median(a[1400:1600, 100:500].reshape(-1, 3), axis=0).astype(np.uint8)
    return a


def title(a, key):
    im = Image.fromarray(a); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, BAND[0], W, BAND[1]], fill=(10, 8, 7, 225))
    small, big = TITLES[key]
    d.text((60, BAND[0] + 18), small, font=ImageFont.truetype(B, 38), fill=GOLD)
    d.text((60, BAND[0] + 72), big, font=ImageFont.truetype(B, 42), fill=CREAM)
    return np.array(im)


def text_card(lines, footer=True):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for t, size, bold, c, y in lines:
        d.text((90, y), t, font=ImageFont.truetype(B if bold else R, size), fill=c)
    if footer:
        f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
        d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    return np.array(im)


P1 = [("Part 1", 44, True, GOLD, 330),
      ("Why I don't move my stop", 58, True, CREAM, 400),
      ("to breakeven", 58, True, CREAM, 470),
      ("A breakeven exit still pays round-trip", 38, False, MUTED, 600),
      ("commissions and fees. The account goes down.", 38, False, MUTED, 650),
      ("Long 2 ES @ 7,448.25  |  Stop 7,444.25 (4 pts)", 36, False, CREAM, 780),
      ("Manual exit 7,457.25  |  +9.00 pts  |  +$900", 36, True, GOLD, 840),
      ("I protect a trade by getting out.", 38, False, MUTED, 910)]
P2 = [("Part 2", 44, True, GOLD, 330),
      ("Same setup, new entry,", 58, True, CREAM, 400),
      ("target hit", 58, True, GREEN, 470),
      ("Long 2 ES @ 7,442.75  |  Stop 7,438.75 (4 pts)", 36, False, CREAM, 610),
      ("Target 7,471.25 filled  |  +28.50 pts", 40, True, GOLD, 670),
      ("+$2,850  |  7.1R  |  Stop never moved", 40, True, GOLD, 730)]


def card(kind, account):
    tag = [(account.capitalize() + " account", 36, False, MUTED, 1180)] if account else []
    end = [("Define your risk. Wait for your setup.", 42, True, CREAM, 1300)]
    if kind == "p1":
        return text_card(P1 + [("Next trade: an impatient re-entry, -$625.", 38, True, RED, 1000),
                               ("Part 2: same setup, new entry.", 42, True, CREAM, 1070)] + tag + end)
    if kind == "p2":
        return text_card(P2 + [("Before it: an impatient re-entry, -$625.", 38, True, RED, 860),
                               ("Waiting for the proper entry paid.", 38, False, MUTED, 920)] + tag + end)
    both = P2
    return text_card([("Part 1: manual exit at 7,457.25, +$900", 38, True, GOLD, 170),
                      ("Then impatient: 7,452.00 to 7,445.75, -$625", 38, True, RED, 230)] + both +
                     [("Patience paid. Impatience cost.", 40, False, MUTED, 880)] + tag + end)


def main():
    v1, v2, out = sys.argv[1], sys.argv[2], sys.argv[3]
    account = sys.argv[sys.argv.index("--account") + 1] if "--account" in sys.argv else ""
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "combined"
    plan = {"part1": PART1, "part2": PART2, "combined": COMBINED, "breakdown": BREAKDOWN}[mode]
    src = {"v1": v1, "v2": v2}
    still = sys.argv[sys.argv.index("--still") + 1] if "--still" in sys.argv else None
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    kept = dropped = 0; last = None
    for seg in plan:
        if seg[0] == "still":
            a = np.array(Image.open(still).convert("RGB").resize((W, 2340)))[TOP:TOP + H]
            a = clean(a)
            if mode != "breakdown":
                a = title(a, "still")
            for _ in range(round(seg[1] * FPS)):
                p.stdin.write(a.tobytes())
            last = a
            continue
        if seg[0] in ("hold", "card"):
            img = last if seg[0] == "hold" else card(seg[1], account)
            for _ in range(round(seg[-1] * FPS)):
                p.stdin.write(img.tobytes())
            continue
        v, s, e, secs = seg
        n = round(secs * FPS); got = 0
        for a in frames(src[v], s, e, n):
            if bad(a):
                dropped += 1; continue
            a = clean(a)
            if mode != "breakdown":
                a = title(a, v)
            p.stdin.write(a.tobytes()); kept += 1; got += 1; last = a
        for _ in range(n - got):  # keep segment timing if frames were dropped or the source ran short
            p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
