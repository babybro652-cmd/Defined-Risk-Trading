"""Amazon KDP paperback files for a Peace by Page journal (interior + wraparound cover).

Usage: python3 kdp/build_kdp.py --theme wings
Writes kdp/out/<slug>-kdp-interior.pdf and <slug>-kdp-cover.pdf.

KDP settings: 8.5 x 11 in trim, no bleed (interior), black & white interior on white paper,
matte cover. Interior keeps the duplex margins (0.85 in inside, 0.6 in outside); KDP's minimum
inside margin for 151-300 pages is 0.5 in. Cover: 0.125 in bleed, spine = pages x 0.002252 in.
"""
import argparse
import os
import sys

import pymupdf
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_journal as bj  # noqa: E402

TRIM_W, TRIM_H, BLEED = 8.5, 11.0, 0.125
PAPER = 0.002252  # in per page, white paper, black & white interior

BOOK_TERMS = (
    "This journal is for your own use. Please don't copy, scan, or share its pages beyond your household. "
    "If you'd like to use it with a group, class, or clients, contact us and we'll talk about it.\n"
    "Thank you for supporting a small, independent publisher."
)
BOOK_NOTE = "Pens and gel pens work on every page. Colored pencils work best on the coloring pages."

BACK_COPY = {
    "wings": (
        "One gentle page a day, about five minutes.",
        "Calm Wings is a 90-day journal for anyone who worries. Each day you check in with your mood, "
        "write three good things, name one worry and a more balanced thought, and pick one small step "
        "for tomorrow.",
        ["90 undated daily pages", "SOS toolkit for hard moments: box breathing, 5-4-3-2-1 grounding, a worry tree",
         "Weekly check-ins and monthly habit trackers", "A butterfly coloring page to end each week"],
    ),
}


def kdp_about_page(J, c, F, product="journal"):
    """Book version of page 2: disclaimer, crisis lines, terms, copyright. No print-at-home text."""
    T, C = bj.T, bj.C
    bj.kicker(c, F, "Before you begin")
    y = bj.title(c, F, "A few words first")
    bj.small_fly(c, F.right - 26, F.top - 26, 22, 2, angle=14)
    y -= 4
    bj.rbox(c, F.left, y + 14, F.w, 100, 14, stroke=C["accent"], fill=C["tint"], lw=1.0)
    bj.label(c, F.left + 20, y - 8, f"About this {product}", 11.5, C["accent"])
    bj.para(c, F.left + 20, y - 28, F.w - 40, bj.content.DISCLAIMER.format(product=product), "Sans", 10.5, 15.5)
    y -= 122
    bj.label(c, F.left, y, "If you need help now", 11.5, C["accent"])
    y -= 22
    for a, b in bj.content.CRISIS_SHORT:
        bj.text(c, F.left, y, a, "SansB", 10.5)
        y = bj.para(c, F.left + 130, y, F.w - 130, b, "Sans", 10.5, 15) - 9
    y -= 14
    bj.label(c, F.left, y, "Please keep it personal", 11.5, C["accent"])
    y = bj.para(c, F.left, y - 22, F.w, BOOK_TERMS, "Sans", 10.5, 15.5, after=8) - 14
    bj.label(c, F.left, y, "What to write with", 11.5, C["accent"])
    y = bj.para(c, F.left, y - 22, F.w, BOOK_NOTE, "Sans", 10.5, 15.5) - 26
    bj.text(c, F.left, y, f"© {J.cfg.get('year', 2026)} {T.title} by {T.brand}. All rights reserved.", "Sans", 9,
            C["muted"])
    bj.text(c, F.left, y - 14, "Content and art created with AI assistance and reviewed by the maker.", "Sans", 9,
            C["muted"])


SAFE_OUT, SAFE_IN = 0.3, 0.6   # in: KDP minimums are 0.25 outside/top/bottom and 0.5 inside (151-300 pages)


def ink_box(page):
    """Visible content box in points (rendered, so clipped art doesn't count)."""
    import numpy as np
    pix = page.get_pixmap(dpi=72, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
    ys, xs = np.where(a < 245)
    if not len(xs):
        return None
    return pymupdf.Rect(xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def fit_margins(path):
    """Shrink any page whose art reaches into KDP's no-print zone; returns the page numbers fixed."""
    src = pymupdf.open(path)
    out = pymupdf.open()
    fixed = []
    for i, pg in enumerate(src):
        W, H = pg.rect.width, pg.rect.height
        box = ink_box(pg)
        right_hand = i % 2 == 0                      # page 1 is a right-hand page: gutter on the left
        left_m, right_m = (SAFE_IN, SAFE_OUT) if right_hand else (SAFE_OUT, SAFE_IN)
        safe = pymupdf.Rect(left_m * 72, SAFE_OUT * 72, W - right_m * 72, H - SAFE_OUT * 72)
        if box is None or safe.contains(box):
            out.insert_pdf(src, from_page=i, to_page=i)
            continue
        k = min(1.0, safe.width / box.width, safe.height / box.height)
        cx = min(max((box.x0 + box.x1) / 2, safe.x0 + box.width * k / 2), safe.x1 - box.width * k / 2)
        cy = min(max((box.y0 + box.y1) / 2, safe.y0 + box.height * k / 2), safe.y1 - box.height * k / 2)
        # place the whole page scaled by k so the ink box lands centered at (cx, cy) inside the safe area
        x0 = cx - ((box.x0 + box.x1) / 2) * k
        y0 = cy - ((box.y0 + box.y1) / 2) * k
        np_ = out.new_page(width=W, height=H)
        np_.show_pdf_page(pymupdf.Rect(x0, y0, x0 + W * k, y0 + H * k), src, i)
        fixed.append(i + 1)
    out.save(path + ".tmp")
    os.replace(path + ".tmp", path)
    return fixed


def interior(theme, out):
    bj.register_fonts()
    bj.set_theme(theme)
    bj.set_page_size("letter")
    bj.about_page = kdp_about_page
    cfg = dict(bj.CONFIG, theme=theme, page_size="letter", duplex=True, shop_name=None)
    n = bj.Journal(cfg, True).build(out)
    if n % 2:                       # KDP needs an even count: add a blank last page
        d = pymupdf.open(out)
        r = d[0].rect
        d.new_page(width=r.width, height=r.height)
        d.save(out + ".tmp")
        os.replace(out + ".tmp", out)
        n += 1
    fixed = fit_margins(out)
    if fixed:
        print("shrunk to fit KDP margins: pages", fixed)
    return n


def cover(theme, interior_pdf, pages, out):
    T, C = bj.T, bj.C
    spine = pages * PAPER
    W = (2 * BLEED + 2 * TRIM_W + spine) * inch
    H = (2 * BLEED + TRIM_H) * inch
    back_x, spine_x = BLEED * inch, (BLEED + TRIM_W) * inch
    front_x = spine_x + spine * inch
    tmp = out + ".base.pdf"
    c = canvas.Canvas(tmp, pagesize=(W, H))
    c.setFillColor(C["tint"])
    c.rect(0, 0, W, H, stroke=0, fill=1)                      # soft tint over the whole wrap, into the bleed
    c.setFillColor(C["accent"])
    c.rect(spine_x, 0, spine * inch, H, stroke=0, fill=1)     # spine band
    # spine text (KDP: 79+ pages; keep 0.0625 in clear each side)
    c.saveState()
    c.translate(spine_x + spine * inch / 2, H / 2)
    c.rotate(-90)
    c.setFillColor((1, 1, 1))
    c.setFont("SansB", 11)
    c.drawCentredString(0, -4, f"{T.title}  ·  A 90-Day Anxiety Journal")
    c.setFont("Sans", 8.5)
    c.drawString(H / 2 - 1.6 * inch, -3.2, T.brand)
    c.restoreState()
    # back cover copy
    hook, body, bullets = BACK_COPY[theme]
    x, w = back_x + 0.9 * inch, TRIM_W * inch - 1.8 * inch
    y = H - 1.6 * inch
    c.setFillColor(C["accent"])
    c.setFont("Accent", 26)
    c.drawString(x, y, hook)
    y -= 0.6 * inch
    for ln in bj.wrap(body, "Sans", 13, w):
        c.setFillColor(C["ink"])
        c.setFont("Sans", 13)
        c.drawString(x, y, ln)
        y -= 20
    y -= 16
    for b in bullets:
        lines = bj.wrap(b, "Sans", 12.5, w - 22)
        c.setFillColor(C["accent"])
        c.circle(x + 5, y + 4, 3.2, stroke=0, fill=1)
        c.setFillColor(C["ink"])
        c.setFont("Sans", 12.5)
        for ln in lines:
            c.drawString(x + 20, y, ln)
            y -= 19
        y -= 7
    y -= 18
    for ln in bj.wrap("For self-reflection and general wellbeing. It supports, not replaces, care from a "
                      "licensed professional. In crisis in the US, call or text 988.", "Sans", 10, w):
        c.setFillColor(C["muted"])
        c.setFont("Sans", 10)
        c.drawString(x, y, ln)
        y -= 15
    c.setFillColor(C["accent"])
    c.setFont("SansB", 12)
    c.drawString(x, (BLEED + 0.9) * inch, T.brand)
    # KDP barcode area: 2 x 1.2 in, kept white, 0.25 in in from the back's bottom-right trim corner
    c.setFillColor((1, 1, 1))
    c.rect(back_x + (TRIM_W - 0.25 - 2.0) * inch, (BLEED + 0.25) * inch, 2.0 * inch, 1.2 * inch, stroke=0, fill=1)
    c.showPage()
    c.save()
    # front cover: page 1 of the interior (vector), on a white rounded card, minus the "belongs to" line
    doc = pymupdf.open(tmp)
    pg = doc[0]
    src = pymupdf.open(interior_pdf)
    sw, sh = src[0].rect.width, src[0].rect.height
    hit = src[0].search_for("This journal belongs")
    cut = hit[0].y0 - 12 if hit else sh - 1.5 * 72
    clip = pymupdf.Rect(0, 0, sw, cut)                         # drop the "This journal belongs to" line
    card = pymupdf.Rect(front_x + 0.45 * inch, BLEED * inch + 0.45 * inch,
                        front_x + (TRIM_W - 0.45) * inch, H - BLEED * inch - 0.45 * inch)
    pg.draw_rect(card, color=None, fill=(1, 1, 1), radius=0.04)
    inner = pymupdf.Rect(card.x0 + 10, card.y0 + 10, card.x1 - 10, card.y1 - 10)
    pg.show_pdf_page(inner, src, 0, clip=clip, keep_proportion=True)
    doc.save(out)
    os.remove(tmp)
    return spine, W / inch, H / inch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="wings")
    a = ap.parse_args()
    od = os.path.join(HERE, "out")
    os.makedirs(od, exist_ok=True)
    bj.register_fonts()
    bj.set_theme(a.theme)
    slug = bj.T.slug
    ip = os.path.join(od, f"{slug}-kdp-interior.pdf")
    n = interior(a.theme, ip)
    cp = os.path.join(od, f"{slug}-kdp-cover.pdf")
    spine, w, h = cover(a.theme, ip, n, cp)
    print(f"interior {ip}: {n} pages\ncover {cp}: {w:.4f} x {h:.4f} in, spine {spine:.4f} in")


if __name__ == "__main__":
    main()
