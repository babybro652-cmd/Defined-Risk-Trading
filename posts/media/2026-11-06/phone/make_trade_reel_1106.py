"""Time-lapse eval-trade reel from Tim's 11/6/2026 TradingView recordings (Drive DRT Phone, uploaded 16:36 UTC,
note "Eval trade."), 1080x2340, ES1! 1m, silent audio track (-91 dB):
V1 Screen_Recording_20261106_111503_TradingView.mp4 (1TLu0TWaZvMIOvwNMuNB0tVzMzwErr8nA, 1:46.0, ~19 fps), ~11:13:17-11:15:03 ET.
  Short 2 @ 7,430.75 (filled before the recording, 11:13 bar). 4 pt mental stop (Tim: account type allows no TP/SL orders); price jumped before the close filled. Manual close (tap on the
  position's X at ~102.8 s), bought 2 @ 7,435.75: -5.00 pts x 2 = -$500.
V2 Screen_Recording_20261106_112200_TradingView.mp4 (11c_OcLaD-LYWNFtXoAMlPP6wQ-FH7mok, 6:01.0, ~13.5 fps), ~11:15:59-11:22:00 ET.
  Short 2 @ 7,436.25 (11:15 bar, before the recording). Target 7,406.25 (drawn line, Tim). Open P&L peaked +$1,275 at ~290 s
  (7,423.50). Manual close (tap on X at ~332.5 s, ~11:21:31 ET), bought 2 @ 7,433.75: +2.50 pts x 2 = +$250.
Cut (10 fps scan + 1 fps / 0.5 fps full-frame sheets): V1 14.7-27.2 s (OHLC legend, drawing toolbar, horizontal-line
menus incl. an alert item naming the indicator), V1 68.1-70.8 s (indicator legend expanded with indicator names);
V2 from 344.5 s (interval menu, 15m view with aggregated fills and indicator labels).
Covered: status bar cropped (top 98 px); everything below source y 1788 (time axis, order-ticket bar, indicator filter
table, toolbar, nav bar) covered with chart background; the volume table's Bias cell is repainted without the
indicator name (reads "Short" / "Long" from the cell colour).
Usage: python3 make_trade_reel_1106.py V1.mp4 V2.mp4 OUT.mp4 [--account eval|none]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, TOP = 1080, 1920, 30, 98
COVER = 1690  # crop row where the bottom cover starts (source y 1788)
BIAS = (302, 340, 632, 884)  # crop rows/cols of the volume table's Bias value cell
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (170, 150, 130); RED = (225, 95, 85); GREEN = (90, 200, 140)
BG = (14, 10, 9); CHART_BG = np.array((15, 15, 15), dtype=np.uint8)  # plain chart background
PLAN = [("v1", 0, 1.5, 1.5), ("v1", 1.5, 14.7, 1.5), ("v1", 27.2, 68.1, 5.0), ("v1", 70.8, 102.0, 5.0),
        ("v1", 102.0, 104.6, 2.6), ("v1", 104.6, 105.9, 1.0), ("hold", 0.8),
        ("v2", 0, 1.5, 1.5), ("v2", 1.5, 286.0, 18.0), ("v2", 286.0, 292.0, 2.0), ("v2", 292.0, 330.0, 4.0),
        ("v2", 330.0, 334.6, 4.6), ("v2", 334.6, 344.4, 1.5), ("hold", 1.0), ("card", 6.5)]
TITLES = {"v1": ("Trade 1", "Short 2 ES with the sell bias"),
          "v2": ("Trade 2", "Same idea, second entry")}
BAND = (420, 580)  # crop rows of the title band (empty chart area under the volume table)


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
    """Guard: bottom sheet / menu (bright panel), black frame, expanded indicator legend."""
    m = a[100:1690].mean()
    sheet = (a[900:1690].mean(axis=2) > 40).mean() > 0.25
    legend = (a[202:522, 0:420].mean(axis=2) > 90).mean() > 0.01
    return m > 40 or m < 8 or sheet or legend


def clean(a):
    a = a.copy()
    a[COVER:] = CHART_BG
    y0, y1, x0, x1 = BIAS
    cell = a[y0:y1, x0:x1].astype(int)
    if cell.mean() > 15:  # table is showing
        r, g = cell[..., 0], cell[..., 1]
        red = ((r > 150) & (g < 110)).sum(); green = ((g > 150) & (r < 120)).sum()
        bg = np.median(cell[2:6, 2:40].reshape(-1, 3), axis=0).astype(np.uint8)
        a[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = bg
        if red or green:
            im = Image.fromarray(a); d = ImageDraw.Draw(im)
            t = "Short" if red >= green else "Long"; f = ImageFont.truetype(R, 22)
            d.text(((x0 + x1 - d.textlength(t, font=f)) / 2, y0 + 7), t, font=f,
                   fill=(225, 70, 85) if t == "Short" else (40, 200, 120))
            a = np.array(im)
    return a


def title(a, key):
    im = Image.fromarray(a); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, BAND[0], W, BAND[1]], fill=(10, 8, 7, 225))
    small, big = TITLES[key]
    d.text((60, BAND[0] + 18), small, font=ImageFont.truetype(B, 38), fill=GOLD)
    d.text((60, BAND[0] + 72), big, font=ImageFont.truetype(B, 42), fill=CREAM)
    return np.array(im)


def card(account):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    lines = [("Sell bias day, two shorts", 54, True, CREAM, 300),
             ("Trade 1", 40, True, GOLD, 430),
             ("Short 2 ES @ 7,430.75", 38, False, CREAM, 490),
             ("Closed 7,435.75  |  -5.00 pts  |  -$500", 38, True, RED, 545),
             ("Trade 2", 40, True, GOLD, 650),
             ("Short 2 ES @ 7,436.25", 38, False, CREAM, 710),
             ("Open profit hit +$1,275", 38, False, MUTED, 765),
             ("Closed 7,433.75  |  +2.50 pts  |  +$250", 38, True, GREEN, 820),
             ("Day: -$250 gross", 46, True, CREAM, 940),
             ("Mental stop slipped. Kept what was left.", 38, False, MUTED, 1030)]
    if account == "eval":
        lines.append(("Evaluation account", 36, False, MUTED, 1180))
    lines.append(("Define your risk. Wait for your setup.", 42, True, CREAM, 1300))
    for t, size, bold, c, y in lines:
        d.text((90, y), t, font=ImageFont.truetype(B if bold else R, size), fill=c)
    f = ImageFont.truetype(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 260), t, font=f, fill=MUTED)
    return np.array(im)


def main():
    v1, v2, out = sys.argv[1], sys.argv[2], sys.argv[3]
    account = sys.argv[sys.argv.index("--account") + 1] if "--account" in sys.argv else "eval"
    src = {"v1": v1, "v2": v2}
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    kept = dropped = 0; last = None
    for seg in PLAN:
        if seg[0] in ("hold", "card"):
            img = last if seg[0] == "hold" else card(account)
            for _ in range(round(seg[-1] * FPS)):
                p.stdin.write(img.tobytes())
            continue
        v, s, e, secs = seg
        n = round(secs * FPS); got = 0
        for a in frames(src[v], s, e, n):
            if bad(a):
                dropped += 1; continue
            a = title(clean(a), v)
            p.stdin.write(a.tobytes()); kept += 1; got += 1; last = a
        for _ in range(n - got):  # keep segment timing if frames were dropped or the source ran short
            p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    print("kept", kept, "dropped", dropped)


if __name__ == "__main__":
    main()
