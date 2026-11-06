"""DRT TikTok LIVE overlays (0 credits, PIL only).

python3 drt/live/make_overlays.py                 # writes drt/live/overlays/ + contact sheet
python3 drt/live/make_overlays.py --code TIM10    # fills the affiliate code slot
python3 drt/live/make_overlays.py --bias BULLISH  # also writes a filled bias card

Every overlay is a full-canvas transparent PNG (1080x1920 portrait for TikTok LIVE
Studio, 1920x1080 landscape for OBS). Add it as an Image source and stretch it to the
canvas; each element already sits in its spot. Brand styling matches the post scripts
in posts/media/ (dark brown panels, gold accent, cream text, DejaVu Sans).
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "overlays")
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 178, 92); CREAM = (245, 236, 220); MUTED = (190, 170, 150)
PANEL = (22, 16, 12); PANEL2 = (40, 28, 20)
f = lambda p, s: ImageFont.truetype(p, s)

CANVAS = {"portrait": (1080, 1920), "landscape": (1920, 1080)}


def canvas(kind):
    return Image.new("RGBA", CANVAS[kind], (0, 0, 0, 0))


def panel(im, box, alpha=225, radius=22, edge=True):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, radius=radius, fill=PANEL + (alpha,))
    if edge:
        d.rounded_rectangle(box, radius=radius, outline=GOLD + (255,), width=3)
    im.alpha_composite(lay)
    return ImageDraw.Draw(im)


def ctext(d, cx, y, t, font, fill):
    d.text((cx - d.textlength(t, font=font) / 2, y), t, font=font, fill=fill)


def fit(d, t, path, size, maxw):
    while d.textlength(t, font=f(path, size)) > maxw and size > 10:
        size -= 2
    return f(path, size)


# ---------- elements ----------
def banner(kind, code=None, cta=True):
    im = canvas(kind); W, H = im.size
    if kind == "portrait":
        x0, y0, x1, y1 = 60, 150, W - 60, 330   # clear of TikTok's top host bar
    else:
        x0, y0, x1, y1 = 40, 28, 1060, 168
    d = panel(im, (x0, y0, x1, y1))
    split = code is not None
    right = 0
    if split:   # code slot on the right
        right = 300 if kind == "portrait" else 290
        sx = x1 - right
        d.line([(sx, y0 + 24), (sx, y1 - 24)], fill=GOLD, width=3)
        cx = sx + right / 2
        ctext(d, cx, y0 + 34, "CODE", f(B, 30), GOLD)
        val = code if code else "______"
        ft = fit(d, val, B, 54, right - 40)
        ctext(d, cx, y0 + 82, val, ft, CREAM)
    ix0, ix1 = x0 + 34, x1 - right - 30
    cx = (ix0 + ix1) / 2
    title = "DEFINED RISK TRADING"
    ft = fit(d, title, B, 64 if kind == "portrait" else 60, ix1 - ix0)
    ty = y0 + (30 if cta else (y1 - y0) / 2 - 38)
    ctext(d, cx, ty, title, ft, CREAM)
    rule_y = d.textbbox((cx, ty), title, font=ft)[3] + 14
    d.rectangle([cx - 70, rule_y, cx + 70, rule_y + 6], fill=GOLD)
    if cta:
        ctext(d, cx, rule_y + 20, "Skool link in bio", f(B, 40 if kind == "portrait" else 38), GOLD)
    return im


def disclaimer(kind):
    im = canvas(kind); W, H = im.size
    t = "EDUCATION ONLY  |  NOT FINANCIAL ADVICE"
    if kind == "portrait":   # sits on the seam between webcam (top 40%) and chart
        box = (0, 740, W, 800); fs = 34
    else:
        box = (0, H - 54, W, H); fs = 30
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle(box, fill=PANEL + (235,))
    d.rectangle([box[0], box[1], box[2], box[1] + 4], fill=GOLD + (255,))
    im.alpha_composite(lay); d = ImageDraw.Draw(im)
    ft = fit(d, t, B, fs, W - 60)
    ctext(d, W / 2, box[1] + (box[3] - box[1] - ft.size) / 2 + 1, t, ft, CREAM)
    return im


def lower_third(kind, label, value=None, sub=None):
    im = canvas(kind); W, H = im.size
    if kind == "portrait":   # bottom of the webcam zone, above TikTok's comment area
        x0, y0, x1, y1 = 40, 548, W - 40, 724
    else:
        x0, y0, x1, y1 = 40, 836, 1080, 1004
    d = panel(im, (x0, y0, x1, y1), edge=False)
    d.rounded_rectangle([x0, y0, x0 + 18, y1], radius=8, fill=GOLD)
    tx = x0 + 52
    if value is None:   # title card only
        ft = fit(d, label, B, 74, x1 - tx - 30)
        d.text((tx, y0 + 30), label, font=ft, fill=CREAM)
        d.text((tx, y0 + 30 + ft.size + 18), sub or "", font=f(R, 36), fill=MUTED)
    else:
        lf = f(B, 64)
        d.text((tx, y0 + 26), label, font=lf, fill=CREAM)
        vx = tx + d.textlength(label + " ", font=lf)
        if value == "":   # blank slot to type into
            d.line([(vx, y0 + 26 + 66), (x1 - 40, y0 + 26 + 66)], fill=GOLD, width=5)
        else:
            d.text((vx, y0 + 26), value, font=fit(d, value, B, 64, x1 - vx - 30), fill=GOLD)
        d.text((tx, y0 + 112), sub or "", font=f(R, 34), fill=MUTED)
    return im


def tagline(kind):
    im = canvas(kind); W, H = im.size
    t = "Define your risk, wait for your setup."
    if kind == "portrait":
        box = (60, 1812, W - 60, 1880); fs = 38
    else:
        box = (1110, 940, W - 40, 1004); fs = 30
    d = panel(im, box, alpha=210, radius=34, edge=False)
    ft = fit(d, t, B, fs, box[2] - box[0] - 50)
    ctext(d, (box[0] + box[2]) / 2, box[1] + (box[3] - box[1] - ft.size) / 2 - 2, t, ft, GOLD)
    return im


def guide(kind):
    """Not for streaming: shows where the webcam, chart and overlays go."""
    W, H = CANVAS[kind]
    im = Image.new("RGBA", (W, H), (14, 10, 8, 255)); d = ImageDraw.Draw(im)
    def zone(box, fill, label, sub, fs=56, cy=None):
        d.rectangle(box, fill=fill, outline=GOLD, width=4)
        cx = (box[0] + box[2]) / 2; cy = cy or (box[1] + box[3]) / 2
        ctext(d, cx, cy - fs, label, f(B, fs), CREAM)
        ctext(d, cx, cy + 14, sub, f(R, int(fs * 0.55)), MUTED)
    def note(box, label, col=(120, 160, 220)):
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle(box, fill=col + (70,), outline=col + (255,), width=3)
        im.alpha_composite(lay)
        dd = ImageDraw.Draw(im)
        dd.text((box[0] + 14, box[1] + 8), label, font=f(B, 26), fill=CREAM)
    if kind == "portrait":
        zone((0, 0, W, 768), (60, 44, 32, 255), "WEBCAM", "top 40%  |  0 to 768 px", 64)
        zone((0, 768, W, H), (30, 38, 34, 255), "TRADINGVIEW CHART", "bottom 60%  |  768 to 1920 px", 60, cy=1000)
        note((60, 150, W - 60, 330), "BANNER  y 150-330")
        note((40, 548, W - 40, 724), "BIAS / PLAN CARD  y 548-724")
        note((0, 740, W, 800), "DISCLAIMER BAR  y 740-800 (seam)", (232, 178, 92))
        note((60, 1812, W - 60, 1880), "TAGLINE  y 1812-1880")
        note((0, 0, W, 140), "TikTok host bar + viewer count (keep clear)", (220, 90, 90))
        note((0, 1200, 760, 1800), "Comments float here on phones\n(approx.). Keep key chart\nlevels in the upper chart area\nor on the right side.", (220, 90, 90))
        note((960, 820, W, 1700), "Gift /\nbutton\nrail", (220, 90, 90))
    else:
        zone((0, 0, 1380, 1080), (30, 38, 34, 255), "TRADINGVIEW CHART", "left 72%  |  0 to 1380 px", 64, cy=430)
        zone((1380, 190, W, 900), (60, 44, 32, 255), "WEBCAM", "right column  |  540 x 710", 54)
        note((40, 28, 1060, 168), "BANNER  y 28-168")
        note((40, 836, 1080, 1004), "BIAS / PLAN CARD  y 836-1004")
        note((1110, 940, W - 40, 1004), "TAGLINE")
        note((0, H - 54, W, H), "DISCLAIMER BAR  bottom 54 px", (232, 178, 92))
    gx, gy = (690, 620) if kind == "landscape" else (W / 2, 1110)
    ctext(d, gx, gy, "LAYOUT GUIDE (do not stream this)", f(B, 34), GOLD)
    return im


def build(code=None, bias=None):
    os.makedirs(OUT, exist_ok=True)
    made = []
    for kind in ("portrait", "landscape"):
        sets = {
            "banner": banner(kind),
            "banner-code": banner(kind, code=code or ""),
            "banner-plain": banner(kind, cta=False),
            "disclaimer": disclaimer(kind),
            "bias": lower_third(kind, "TODAY'S BIAS:", "", "Higher timeframe read. Not a signal."),
            "tomorrow-plan": lower_third(kind, "TOMORROW'S PLAN", None, "Levels, bias, and what I wait for"),
            "tagline": tagline(kind),
            "layout-guide": guide(kind),
        }
        for b in (["BULLISH", "BEARISH", "NEUTRAL"] + ([bias.upper()] if bias else [])):
            sets["bias-" + b.lower()] = lower_third(kind, "TODAY'S BIAS:", b, "Higher timeframe read. Not a signal.")
        for name, im in sets.items():
            p = os.path.join(OUT, f"{kind}-{name}.png"); im.save(p); made.append(p)
    return made


def contact_sheet(paths, out):
    tw = 360; pad = 24; lab = 40
    tiles = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        th = int(im.height * tw / im.width)
        bg = Image.new("RGBA", (tw, th), (0, 0, 0, 255)); dd = ImageDraw.Draw(bg)
        for yy in range(0, th, 20):   # checkerboard shows transparency
            for xx in range(0, tw, 20):
                c = (95, 95, 95) if (xx // 20 + yy // 20) % 2 else (65, 65, 65)
                dd.rectangle([xx, yy, xx + 19, yy + 19], fill=c)
        bg.alpha_composite(im.resize((tw, th), Image.LANCZOS))
        tiles.append((os.path.basename(p), bg))
    cols = 6
    rows = []
    for i in range(0, len(tiles), cols):
        rows.append(tiles[i:i + cols])
    heights = [max(t.height for _, t in r) + lab + pad for r in rows]
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, sum(heights) + pad), (18, 14, 12))
    d = ImageDraw.Draw(sheet); y = pad
    for r, h in zip(rows, heights):
        x = pad
        for name, t in r:
            d.text((x, y), name.replace(".png", ""), font=f(B, 18), fill=GOLD)
            sheet.paste(t.convert("RGB"), (x, y + lab - 10)); x += tw + pad
        y += h
    sheet.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", help="affiliate code for the banner-code version")
    ap.add_argument("--bias", help="extra filled bias card, e.g. RANGE")
    a = ap.parse_args()
    made = build(a.code, a.bias)
    port = [p for p in made if "/portrait-" in p]; land = [p for p in made if "/landscape-" in p]
    print(contact_sheet(port + land, os.path.join(HERE, "overlays-contact-sheet.png")))
    print(len(made), "overlays")
