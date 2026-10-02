"""Listing images (2000 x 2000 PNG) for every product of the active Calm Pages edition.

Called by build_products.py. Pages are rendered straight from the built PDFs, so the images
always match the files. Five images per product:
  01_cover      the cover on a soft background
  02_spread     a fan of inside pages
  03_inside     4-page "inside look" collage
  04_included   what's included, with page counts
  05_download   instant download + how it works
"""
import io
import math
import os
import random

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.colors import white
from reportlab.pdfgen import canvas

import build_journal as bj

S = 2000
COL = {}   # filled from the active theme's IMG colors by build_images()


def use_theme():
    COL.clear()
    COL.update(bj.T.img)
    _fly_cache.clear()
FONTS = {
    "display": "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
    "sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
}
_fc = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONTS[kind], size)
    return _fc[key]


# --------------------------------------------------------------------------
# building blocks
# --------------------------------------------------------------------------


def page_img(pdf, pno, height):
    """Render page pno (1-based) of pdf to an RGB image `height` px tall."""
    doc = pymupdf.open(pdf)
    p = doc[pno - 1]
    zoom = height / p.rect.height
    pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom * 1.5, zoom * 1.5))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    w = round(im.width * height / im.height)
    return im.resize((w, height), Image.LANCZOS)


def find_page(pdf, needle, start=1):
    doc = pymupdf.open(pdf)
    for i in range(start - 1, len(doc)):
        if "".join(needle.upper().split()) in "".join(doc[i].get_text().upper().split()):
            return i + 1
    raise ValueError(f"{needle!r} not found in {pdf}")


def with_shadow(im, angle=0.0, blur=28, offset=(0, 18), alpha=70, border=True):
    """Return an RGBA image of `im` with a soft drop shadow, rotated by angle (deg)."""
    pad = blur * 3
    w, h = im.size
    if border:
        im = im.copy()
        ImageDraw.Draw(im).rectangle([0, 0, w - 1, h - 1], outline=COL["border"], width=2)
    base = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + offset[0], pad + offset[1], pad + offset[0] + w, pad + offset[1] + h],
                                 fill=COL["shadow"] + (alpha,))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh)
    base.paste(im, (pad, pad))
    if angle:
        base = base.rotate(angle, resample=Image.BICUBIC, expand=True)
    return base


def paste_c(dst, im, cx, cy):
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


_fly_cache = {}


def fly(px, style="classic", fills=("lavender", "mint", "peach"), angle=0.0, lineart=False):
    """A theme accent (butterfly, sprig, moon...) drawn by the same vector art as the journal,
    as an RGBA image px wide. style / fills are passed to the theme's image_art()."""
    key = (px, style, fills, angle, lineart)
    if key in _fly_cache:
        return _fly_cache[key]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(400, 400))
    bj.T.image_art(c, style, fills, angle, lineart, px)
    c.showPage()
    c.save()
    doc = pymupdf.open("pdf", buf.getvalue())
    zoom = px / 400
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    _fly_cache[key] = im
    return im


def background(seed=1, flies=True):
    im = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(im)
    a, b = COL["bg_top"], COL["bg_bot"]
    for y in range(S):
        t = y / (S - 1)
        d.line([(0, y), (S, y)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,))
    # soft pastel blobs: drawn on an opaque copy and blurred, so edges never go gray
    base = im.convert("RGB")
    blob = base.copy()
    bd = ImageDraw.Draw(blob)
    rnd = random.Random(seed)
    for colr, (x, y, r) in zip(("mint", "peach", "lav", "rose"),
                               ((-120, 1500, 520), (1850, 260, 440), (1700, 1750, 420), (200, 120, 360))):
        bd.ellipse([x - r, y - r, x + r, y + r], fill=COL[colr])
    blob = blob.filter(ImageFilter.GaussianBlur(110))
    im = Image.blend(base, blob, 0.75).convert("RGBA")
    if flies:
        spots = [(150, 300, 110, -24), (1860, 1180, 95, 20), (1780, 120, 80, 15)]
        acc = bj.T.mock["accents"]
        for k, (x, y, s, ang) in enumerate(spots):
            st, fl = acc[k % 3]
            f = fly(s, st, fl, ang)
            paste_c(im, f, x + rnd.randint(-10, 10), y + rnd.randint(-10, 10))
    return im


def dotted_trail(im, pts, color=None, r=4, gap=26):
    color = color or COL["muted"]
    d = ImageDraw.Draw(im)
    # sample a smooth catmull path through pts
    path = []
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for k in range(60):
            t = k / 60
            path.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j])
                                     * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    acc = gap
    for i in range(1, len(path)):
        acc += math.dist(path[i], path[i - 1])
        if acc >= gap:
            acc = 0
            x, y = path[i]
            d.ellipse([x - r, y - r, x + r, y + r], fill=color + (160,))


def ctext(d, cx, y, s, f, fill=None):
    fill = fill or COL["ink"]
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


def wrap(d, s, f, width):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def pill(d, cx, y, s, f, fill=None, color=None, padx=44, h=None):
    fill = fill or COL["accent"]
    color = color or COL["white"]
    w = d.textlength(s, font=f)
    h = h or int(f.size * 1.9)
    d.rounded_rectangle([cx - w / 2 - padx, y, cx + w / 2 + padx, y + h], radius=h // 2, fill=fill)
    bb = f.getbbox(s)
    d.text((cx - w / 2, y + (h - (bb[3] - bb[1])) / 2 - bb[1]), s, font=f, fill=color)
    return y + h


def header(im, title, sub=None, y=110):
    d = ImageDraw.Draw(im)
    ctext(d, S / 2, y, title, font("display", 150), COL["accent"])
    if sub:
        ctext(d, S / 2, y + 185, sub, font("sans", 58), COL["ink"])
        return y + 270
    return y + 200


def footer_band(im, s):
    d = ImageDraw.Draw(im)
    d.rectangle([0, S - 150, S, S], fill=COL["band"] + (255,))
    if bj.T.brand_mark:
        ctext(d, S / 2, S - 132, s, font("bold", 56), COL["white"])
        brand_tag(im, S - 54, COL["band_text"])
    else:
        ctext(d, S / 2, S - 112, s, font("bold", 58), COL["white"])


def brand_tag(im, y, color=None, size=30):
    """The umbrella brand as a small spaced wordmark, centered at height y (top of the letters)."""
    d = ImageDraw.Draw(im)
    color = color or COL["muted"]
    f = font("bold", size)
    s = bj.T.brand.upper()
    sp = size * 0.32
    w = sum(d.textlength(ch, font=f) for ch in s) + sp * (len(s) - 1)
    x = S / 2 - w / 2
    for ch in s:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + sp
    ly = y + size * 0.55
    for x0, x1 in ((S / 2 - w / 2 - 90, S / 2 - w / 2 - 26), (S / 2 + w / 2 + 26, S / 2 + w / 2 + 90)):
        d.line([(x0, ly), (x1, ly)], fill=color, width=3)


# --------------------------------------------------------------------------
# the five layouts
# --------------------------------------------------------------------------


def img_cover(P, out):
    im = background(seed=2)
    d = ImageDraw.Draw(im)
    covers = P["covers"]
    if len(covers) == 1:
        back = with_shadow(page_img(P["pdf"], P["peek"], 1380), angle=-7, alpha=45)
        paste_c(im, back, 1130, 1010)
        front = with_shadow(page_img(covers[0][0], covers[0][1], 1420), angle=3)
        paste_c(im, front, 880, 1000)
    else:
        for (pdf, pno), (cx, cy, h, a) in zip(covers, ((620, 1060, 1120, 7), (1380, 1060, 1120, -7),
                                                       (1000, 1000, 1250, 0))):
            paste_c(im, with_shadow(page_img(pdf, pno, h), angle=a), cx, cy)
    dotted_trail(im, [(1560, 520), (1700, 420), (1640, 300), (1760, 230)])
    st, fl = bj.T.mock["corner"]
    paste_c(im, fly(150, st, fl, 18), 1800, 210)
    pill(d, S / 2, 70, P["badge"], font("bold", 54))
    footer_band(im, P["band"])
    im.convert("RGB").save(out, optimize=True)


def img_spread(P, out):
    im = background(seed=3)
    y = header(im, "A peek inside", P["spread_sub"])
    pages = P["spread"]
    n = len(pages)
    pivot = (S / 2, 2750)
    for i, (pdf, pno) in enumerate(pages):
        a = (i - (n - 1) / 2) * (40 / max(n - 1, 1))
        pg = with_shadow(page_img(pdf, pno, 1180), angle=-a, alpha=55)
        r = pivot[1] - 1170
        cx = pivot[0] + r * math.sin(math.radians(a))
        cy = pivot[1] - r * math.cos(math.radians(a))
        paste_c(im, pg, cx, cy)
    footer_band(im, P["band"])
    im.convert("RGB").save(out, optimize=True)


def img_inside(P, out):
    im = background(seed=4, flies=False)
    d = ImageDraw.Draw(im)
    y0 = header(im, "Inside look", None, y=70) - 10
    cells = P["inside"]
    h = 720
    xs = (S / 2 - 470, S / 2 + 470)
    ys = (y0 + h / 2 + 20, y0 + h * 1.5 + 150)
    for i, (pdf, pno, cap) in enumerate(cells):
        cx, cy = xs[i % 2], ys[i // 2]
        pg = page_img(pdf, pno, h)
        paste_c(im, with_shadow(pg, alpha=55, blur=20, offset=(0, 12)), cx, cy)
        pill(ImageDraw.Draw(im), cx, cy + h / 2 + 22, cap, font("bold", 44), fill=COL["white"],
             color=COL["accent"], padx=36)
    acc = bj.T.mock["accents"]
    paste_c(im, fly(130, acc[1][0], acc[1][1], -15), S / 2, ys[0] + 40)
    paste_c(im, fly(110, acc[2][0], acc[2][1], 12), S / 2, ys[1] + 40)
    if bj.T.brand_mark:
        brand_tag(im, S - 70)
    im.convert("RGB").save(out, optimize=True)


def img_included(P, out):
    im = background(seed=5, flies=False)
    d = ImageDraw.Draw(im)
    y = header(im, "What's included", None, y=80)
    # left: list
    x0, x1 = 130, 1180
    items = P["included"]
    fb, fs = font("bold", 56), font("sans", 44)
    tw = x1 - x0 - 190
    box_h = sum(40 + 70 * len(wrap(d, head, fb, tw)) + 56 * len(wrap(d, sub, fs, tw)) for head, sub in items) + 80
    avail = (S - 150) - y - 40
    top = y + 10 + max(0, (avail - box_h) / 2)
    d.rounded_rectangle([x0 - 40, top, x1 + 40, top + box_h], radius=50, fill=COL["white"] + (235,))
    yy = top + 60
    flies = bj.T.mock["list_icons"]
    for k, (head, sub) in enumerate(items):
        st, fl = flies[k % 4]
        paste_c(im, fly(110, st, fl), x0 + 55, yy + 40)
        for ln in wrap(d, head, fb, tw):
            d.text((x0 + 140, yy), ln, font=fb, fill=COL["ink"])
            yy += 70
        for ln in wrap(d, sub, fs, x1 - x0 - 190):
            d.text((x0 + 140, yy), ln, font=fs, fill=COL["muted"])
            yy += 56
        yy += 40
    # right: stacked thumbnails
    thumbs = P["thumbs"]
    for i, (pdf, pno) in enumerate(thumbs):
        a = [8, -6, 3][i % 3]
        pg = with_shadow(page_img(pdf, pno, 760), angle=a, alpha=55, blur=20)
        paste_c(im, pg, 1580 + (i - 1) * 30, top + box_h / 2 - 300 + i * 300)
    footer_band(im, P["included_band"])
    im.convert("RGB").save(out, optimize=True)


def img_download(P, out):
    im = background(seed=6)
    d = ImageDraw.Draw(im)
    y = header(im, "Instant download", "How it works", y=90)
    steps = [
        ("1", "Buy", bj.T.mock["buy_step"], "lav"),
        ("2", "Download", P["dl_step"], "mint"),
        ("3", "Print", "Print at home or at a local print shop, as many times as you like for personal use.", "peach"),
    ]
    top = y + 40
    ch = 330
    for i, (n, head, body, colr) in enumerate(steps):
        yy = top + i * (ch + 50)
        d.rounded_rectangle([170, yy, S - 170, yy + ch], radius=60, fill=COL["white"] + (240,))
        d.ellipse([230, yy + ch / 2 - 95, 420, yy + ch / 2 + 95], fill=COL[colr])
        ctext(d, 325, yy + ch / 2 - 72, n, font("bold", 120), COL["accent"])
        d.text((490, yy + 52), head, font=font("display", 96), fill=COL["accent"])
        by = yy + 172
        for ln in wrap(d, body, font("sans", 48), S - 170 - 490 - 70)[:2]:
            d.text((490, by), ln, font=font("sans", 48), fill=COL["ink"])
            by += 62
        if i < 2:
            cx = S / 2
            for k in range(3):
                d.ellipse([cx - 7, yy + ch + 10 + k * 14, cx + 7, yy + ch + 24 + k * 14], fill=COL["muted"])
    yy = top + 3 * (ch + 50) + 10
    for ln in P["dl_notes"]:
        ctext(d, S / 2, yy, ln, font("bold", 50), COL["accent2"])
        yy += 74
    footer_band(im, "Instant download  ·  printable PDF")
    im.convert("RGB").save(out, optimize=True)


# --------------------------------------------------------------------------
# per-product settings
# --------------------------------------------------------------------------


def product_specs(built):
    T = bj.T
    M = T.mock
    tx = bj.tx
    J = built[("journal", "letter")][0]
    CP = built[("coloring", "letter")][0]
    SK = built[("sos", "letter")][0]
    MT = built[("mood", "letter")][0]
    nJ, nC, nS, nM = (built[(k, "letter")][1] for k in ("journal", "coloring", "sos", "mood"))
    day1 = find_page(J, "Day 1 of 90")
    sos = find_page(J, "When anxiety hits, start here")
    review = find_page(J, "Week 1 review")
    reward = find_page(J, "Week 1 reward")
    moodp = find_page(J, tx("mood_title"))
    habit = find_page(J, "Habit tracker")
    box = find_page(J, "Box breathing", sos + 1)
    sizes = "US Letter + A4"
    common_dl = ["Letter (US) and A4 (UK, EU, AU) included", "Personal use  \u00b7  print as often as you like"]
    cs = M["coloring_spread"]
    return {
        "journal": dict(
            pdf=J, covers=[(J, 1)], peek=day1, badge=f"Printable PDF  \u00b7  {nJ} pages  \u00b7  {sizes}",
            band="90 days of calm daily reflection",
            spread_sub=M["journal_spread_sub"],
            spread=[(J, box), (J, sos), (J, day1), (J, reward), (J, moodp)],
            inside=[(J, day1, "Daily page"), (J, sos, "SOS toolkit"), (J, review, "Weekly check-in"),
                    (J, reward, "Reward coloring")],
            included=[("90 daily pages", "Mood ratings, 3 good things, one worry, one small step"),
                      M["journal_sos"], M["journal_weekly"], M["journal_monthly"], M["journal_more"],
                      ("How-to-print guide", "Home, double-sided and print-shop tips")],
            thumbs=[(J, moodp), (J, habit), (J, 1)],
            included_band=f"{nJ} pages  \u00b7  {sizes} PDFs",
            dl_step=M["dl_step"],
            dl_notes=common_dl),
        "bundle": dict(
            pdf=J, covers=[(CP, 1), (MT, 1), (J, 1)], badge="Bundle  \u00b7  3 printables  \u00b7  " + sizes,
            band="Journal + coloring pack + mood tracker",
            spread_sub="Journal, coloring pack and mood tracker",
            spread=[(CP, M["bundle_spread_cp"][0]), (MT, 4), (J, day1), (J, sos), (CP, M["bundle_spread_cp"][1])],
            inside=[(J, day1, "Daily journal page"), (CP, M["bundle_inside_cp"], "Coloring page"),
                    (MT, 4, M["bundle_inside_mood"]), (J, sos, "SOS toolkit")],
            included=[(f"90-Day Anxiety Journal, {nJ} pages", "Daily pages, SOS toolkit, weekly and monthly "
                       "check-ins"),
                      (f"{tx('coloring_name')}, {nC} pages", M["bundle_coloring"]),
                      (f"{tx('mood_name')}, {nM} pages", M["bundle_mood"]),
                      ("How-to-print guide", "Home, double-sided and print-shop tips")],
            thumbs=[(MT, 1), (CP, 1), (J, 1)],
            included_band=f"{nJ + nC + nM} pages  \u00b7  Letter + A4 zips",
            dl_step=M["dl_step_bundle"],
            dl_notes=common_dl),
        "coloring": dict(
            pdf=CP, covers=[(CP, 1)], peek=4, badge=f"Printable PDF  \u00b7  18 designs  \u00b7  {sizes}",
            band=M["coloring_band"],
            spread_sub=M["coloring_spread_sub"],
            spread=[(CP, p) for p in cs],
            inside=[(CP, p, cap) for p, cap in M["coloring_inside"]],
            included=[("18 coloring designs", M["coloring_list"]),
                      ("Color to calm tips page", "Simple ideas to settle in, plus a color-combo log"),
                      ("Cover and about page", "Ready to bind into your own coloring book"),
                      ("How-to-print guide", "Paper, single-sided tips and print-shop tips")],
            thumbs=[(CP, M["coloring_thumbs"][0]), (CP, M["coloring_thumbs"][1]), (CP, 1)],
            included_band=f"{nC} pages  \u00b7  {sizes} PDFs",
            dl_step=M["dl_step"],
            dl_notes=common_dl),
        "sos": dict(
            pdf=SK, covers=[(SK, 1)], peek=3, badge=f"Printable PDF  \u00b7  {nS} pages  \u00b7  {sizes}",
            band="Calming tools for the hard moments",
            spread_sub=f"{M['sos_count']} tools to come back to again and again",
            spread=[(SK, 4), (SK, 6), (SK, 3), (SK, 8), (SK, M.get("sos_spread_last", 12))],
            inside=[(SK, 3, "Start here flow"), (SK, 4, "Box breathing"), (SK, 6, "5-4-3-2-1 grounding"),
                    (SK, 8, "Worry tree")],
            included=M["sos_included"],
            thumbs=[(SK, 7), (SK, 9), (SK, 1)],
            included_band=f"{nS} pages  \u00b7  {sizes} PDFs",
            dl_step=M["dl_step"],
            dl_notes=common_dl),
        "mood": dict(
            pdf=MT, covers=[(MT, 1)], peek=4, badge=f"Printable PDF  \u00b7  12 months  \u00b7  {sizes}",
            band=M["mood_band"],
            spread_sub="12 undated months, start any time",
            spread=[(MT, 5), (MT, 3), (MT, 4), (MT, 16), (MT, 6)],
            inside=[(MT, 4, M["mood_inside"]), (MT, 3, "How it works"), (MT, 16, "Year in color"),
                    (MT, 5, "February")],
            included=[M["mood_included"],
                      ("Year in color page", "See all 12 months at a glance"),
                      ("How it works + color key", "Pick your mood colors once, use them all year"),
                      ("How-to-print guide", "Home and print-shop tips")],
            thumbs=[(MT, 16), (MT, 3), (MT, 1)],
            included_band=f"{nM} pages  \u00b7  {sizes} PDFs",
            dl_step=M["dl_step"],
            dl_notes=common_dl),
    }


def build_images(out, built):
    from build_products import products
    use_theme()
    PRODUCTS = products()
    specs = product_specs(built)
    for key, P in specs.items():
        idir = os.path.join(out, "images", PRODUCTS[key]["folder"])
        os.makedirs(idir, exist_ok=True)
        for fn, name in ((img_cover, "01_cover"), (img_spread, "02_spread"), (img_inside, "03_inside"),
                         (img_included, "04_included"), (img_download, "05_download")):
            path = os.path.join(idir, f"{name}.png")
            fn(P, path)
            print(f"{os.path.relpath(path, out)}: {os.path.getsize(path) / 1e6:.2f} MB")
