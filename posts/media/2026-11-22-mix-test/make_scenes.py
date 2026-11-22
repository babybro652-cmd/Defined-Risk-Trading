"""Mix explainer test (11/22): six textless-ish scene clips on REAL ES 1m bars (Tue 11/17 NY, date not shown),
fed to Blotato's "AI Video with AI Voice" template as uploadedMedia per scene (ElevenLabs voice + word captions on top).
Center captions sit around y 700-830, so our labels stay in y 140-620 and the chart sits in y 960-1640.
Usage: python3 make_scenes.py OUTDIR
"""
import os, sys, csv, importlib.util
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mx", os.path.join(HERE, "..", "explainers", "make_explainer.py"))
mx = importlib.util.module_from_spec(spec); spec.loader.exec_module(mx)
mx.CY0, mx.CY1 = 980, 1640          # chart lower so the center captions stay clear
P = mx.NAVY; W, H, FPS = mx.W, mx.H, mx.FPS
B, R = mx.B, mx.R; font = mx.font
DATA = os.path.join(HERE, "..", "explainers", "data", "es_1m_2026-11-17_ny.csv")
CLIP = 12.0                          # seconds per clip; Blotato trims to each voice line

def subset(a, b, out):
    rows = list(csv.DictReader(open(DATA)))
    w = [r for r in rows if a <= r["time_et"][11:] < b]
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=rows[0].keys()); wr.writeheader(); wr.writerows(w)
    return out

def base_bg():
    im = mx.background(P); d = ImageDraw.Draw(im)
    return im

def ctext(d, y, text, f, col):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)

def top_card(im, lines, alpha=1.0):
    """lines: [(text, size, colour, bold)] centred inside y 150-620 on a dark panel."""
    if alpha <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    hts = [int(s * 1.35) for _, s, _, _ in lines]; h = sum(hts) + 70
    y0 = 150 + max(0, (440 - h) // 2)
    d.rounded_rectangle([90, y0, W - 90, y0 + h], radius=28, fill=(8, 22, 44, int(215 * alpha)))
    y = y0 + 35
    for (t, s, c, b), hh in zip(lines, hts):
        ctext(d, y, t, font(B if b else R, s), c + (int(255 * alpha),)); y += hh
    im.alpha_composite(ov)

def chart_layer(im, C, minutes, chip_text, dim=False, bands=(), tags=()):
    d = ImageDraw.Draw(im); mx.chip(d, P, chip_text); mx.handle(d, P, top=True)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); mx.draw_bands(ov, C, P, list(bands)); im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    mx.draw_candles(d, C, P, C.candles(minutes), dim_after=-1 if dim else None)
    for tg in tags: mx.tag(d, P, *tg)

def render(out, fn):
    n = int(CLIP * FPS)
    def gen():
        for k in range(n):
            im = base_bg().convert("RGBA"); fn(im, k / FPS); yield np.asarray(im.convert("RGB"))
    mx.render(out, gen())

def main(od):
    os.makedirs(od, exist_ok=True)
    full = mx.Chart(DATA, tf=5)
    zoom = mx.Chart(subset("12:45", "13:25", os.path.join(od, "zoom.csv")), tf=1)
    ease = mx.ease

    # 1 hook: full session printing fast from frame 0 (already 70 min of bars on screen)
    def s1(im, t):
        m = 70 + (full.n - 70) * ease(t / 6.0)
        chart_layer(im, full, m, "ES  ·  5m  ·  NY session")
        top_card(im, [("DAILY MAX MATH", 84, P["accent"], True), ("one contract, one rule", 44, P["muted"], False)])
    render(os.path.join(od, "s1.mp4"), s1)

    # 2 $50 a point: ruler of 4 points lights up one point at a time
    E = zoom.m[21][4]                 # a real bar close used only as a reference price
    def s2(im, t):
        m = 12 + 10 * ease(t / 3.0)
        chart_layer(im, zoom, m, "ES  ·  1m")
        k = int(np.clip((t - 0.6) / 0.8, 0, 4))
        d = ImageDraw.Draw(im); x = mx.CX1 - 120
        for i in range(4):
            y0, y1 = zoom.y(E - i), zoom.y(E - i - 1)
            col = P["poc"] if i < k else P["grid"]
            d.rectangle([x, y0 + 2, x + 60, y1 - 2], fill=col)
            if i < k: d.text((x - 110, (y0 + y1) / 2 - 18), "$50", font=font(B, 34), fill=P["poc"])
        top_card(im, [("1 point = $50", 76, P["text"], True),
                      (f"{k} pt{'s' if k > 1 else ''}  =  ${50 * k}" if k else "count the points", 64, P["poc"], True)])
    render(os.path.join(od, "s2.mp4"), s2)

    # 3 hard stop measured from entry: entry line, red band exactly 4 pts under it
    def s3(im, t):
        a = ease((t - 0.4) / 1.0); b = ease((t - 1.6) / 1.2)
        bands = [(E - 4 * b, E, P["down"], a * 1.0, "4 pts" if b > 0.95 else "")] if b > 0 else []
        tags = [((mx.CX0 + 10, zoom.y(E) - 80), "ENTRY", P["accent"], 36)] if a > 0.5 else []
        chart_layer(im, zoom, 22, "ES  ·  1m", bands=bands, tags=tags)
        d = ImageDraw.Draw(im)
        if a > 0:
            for x in range(mx.CX0, int(mx.CX0 + (mx.CX1 - mx.CX0) * a), 28):
                d.line([x, zoom.y(E), x + 16, zoom.y(E)], fill=P["accent"], width=4)
        top_card(im, [("HARD STOP", 80, P["down"], True), ("3.5 to 4 pts from ENTRY", 54, P["text"], True),
                      ("example, not a trade call", 34, P["muted"], False)])
    render(os.path.join(od, "s3.mp4"), s3)

    # 4 five stops fill the $1,000 day
    def meter(d, used, total=5, col_used=None, label=None):
        x0, x1, y0, y1 = 140, W - 140, 430, 530; gap = 14; sw = (x1 - x0 - gap * (total - 1)) / total
        for i in range(total):
            xa = x0 + i * (sw + gap); fill = (col_used or P["down"]) if i < used else (30, 52, 86)
            d.rounded_rectangle([xa, y0, xa + sw, y1], radius=14, fill=fill)
            d.text((xa + sw / 2 - d.textlength("$200", font=font(B, 34)) / 2, y0 + 30), "$200", font=font(B, 34),
                   fill=(255, 255, 255) if i < used else P["muted"])
    def s4(im, t):
        chart_layer(im, full, full.n, "ES  ·  5m  ·  NY session", dim=True)
        used = int(np.clip((t - 0.5) / 0.7 + 1, 0, 5)) if t > 0.5 else 0
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rounded_rectangle([90, 180, W - 90, 590], radius=28, fill=(8, 22, 44, 215))
        ctext(d, 220, "$1,000 daily max", font(B, 70), P["text"])
        ctext(d, 320, f"{used} of 5 full stops", font(B, 48), P["down"] if used == 5 else P["muted"])
        meter(d, used); im.alpha_composite(ov)
    render(os.path.join(od, "s4.mp4"), s4)

    # 5 the plan: wait for the label, one or two good trades, max stays far away
    def s5(im, t):
        chart_layer(im, full, full.n, "ES  ·  5m  ·  NY session")
        used = 1 if t < 1.6 else 2
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rounded_rectangle([90, 180, W - 90, 590], radius=28, fill=(8, 22, 44, 215))
        ctext(d, 215, "Wait for the label", font(B, 62), P["accent"])
        ctext(d, 305, "1 or 2 good trades", font(B, 52), P["text"])
        meter(d, used, col_used=P["accent"])
        ctext(d, 540, "$600 left as a buffer" if used == 2 else "", font(R, 34), P["muted"])
        im.alpha_composite(ov)
    render(os.path.join(od, "s5.mp4"), s5)

    # 6 close
    def s6(im, t):
        chart_layer(im, full, full.n, "ES  ·  5m  ·  NY session")
        top_card(im, [("Define your risk", 80, P["text"], True), ("before the trade", 56, P["accent"], True),
                      ("@definedrisktrading", 38, P["muted"], False)])
    render(os.path.join(od, "s6.mp4"), s6)

if __name__ == "__main__":
    main(sys.argv[1])
