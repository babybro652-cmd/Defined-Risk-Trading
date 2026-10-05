#!/usr/bin/env python3
"""Free 7-day sampler (lead magnet) for the Peace by Page store, Letter + A4 (launch step 34).

    python3 launch/build_sampler.py      # -> editions/sampler/PeaceByPage_7Day_Sampler_{Letter,A4}.pdf

Pages come from the shared engine (Calm Wings theme, the brand's butterfly): cover, before-you-begin
(disclaimer, crisis lines, terms), how to use it, days 1 to 7, the week 1 review, one reward coloring
page, a cut-out SOS card, and a closing page with the three editions and the store link.
"""
import io
import os
import sys

from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import build_journal as bj  # noqa: E402
from build_journal import C, content, kicker, label, para, rbox, small_fly, text, title, badge  # noqa: E402
import make_brand_assets as mba  # noqa: E402

STORE = "payhip.com/PeaceByPage"
OUT = os.path.join(ROOT, "editions", "sampler")
SIZES = {"letter": "Letter", "a4": "A4"}


class Sampler(bj.Journal):
    def __init__(self, cfg):
        super().__init__(cfg, generic=True)

    def subtitle(self):
        return "A free 7-day taste of the 90-Day Anxiety Journal"

    def plan(self):
        P = self
        P.add(bj.cover, dict(title="7-Day Sampler", belongs="This sampler belongs to"), footer=False)
        P.add(bj.about_page, "sampler")
        P.add(how_to)
        for d in range(1, 8):
            P.add(bj.daily, d)
        P.add(bj.weekly_review, 1, 1, 7)
        P.add(bj.reward_coloring, 1)
        P.add(sos_card)
        P.add(full_journal, footer=False)


def how_to(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "Welcome to your sampler")
    small_fly(c, F.right - 26, F.top - 26, 22, 1, angle=12)
    y -= 8
    y = para(c, F.left, y, F.w,
             "These pages come from the Peace by Page 90-Day Anxiety Journal. Try them for one week, about five "
             "minutes a day, and see how a small daily habit feels. Nothing here is dated, so start any day you like.",
             "Sans", 11, 17, after=10) - 16
    steps = [
        ("Fill in one daily page", "Rate how today felt, write three good things, catch one worry and try a "
         "more balanced thought, then pick one small step for tomorrow."),
        ("Look back after day 7", "The week 1 review helps you notice what helped and what was hard."),
        ("Color your reward", "Finished the week? The coloring page is yours. No rules, stop whenever you like."),
        ("Keep the SOS card close", "Cut it out and keep it in your wallet, bag or by your bed for the hard moments."),
    ]
    cols = ["lavender", "mint", "peach", "rose"]
    for i, (h, b) in enumerate(steps):
        badge(c, F.left + 16, y - 2, str(i + 1), C[cols[i]], 15, 12)
        label(c, F.left + 44, y + 2, h, 11.5, C["ink"])
        y = para(c, F.left + 44, y - 16, F.w - 44, b, "Sans", 10.5, 15) - 22
    y -= 6
    rbox(c, F.left, y + 10, F.w, 92, 14, stroke=False, fill=C["tint"])
    label(c, F.left + 20, y - 14, "Printing", 11, C["accent"])
    para(c, F.left + 20, y - 34, F.w - 40,
         "Print at \"Actual size\" on plain or 24 lb (90 gsm) paper. Colored pencils work best on the coloring "
         "page. Print the daily page as many times as you need for yourself.", "Sans", 10, 14.5)
    y -= 128
    text(c, F.cx, y, "Want all 90 days? The full journals are at " + STORE, "SansB", 10.5, C["accent2"], "center")


def card(c, x, y, w, h, back=False):
    """One wallet card (x, y = top-left), dashed cut line."""
    rbox(c, x, y, w, h, 12, stroke=C["muted"], fill=None, lw=0.8, dash=(3, 3))
    pad = 16
    if not back:
        text(c, x + pad, y - 26, "When anxiety hits", "Accent", 17, C["accent"])
        small_fly(c, x + w - 26, y - 22, 16, 2, angle=12)
        lines = [("1", "Breathe", "in for 4, out for 6. Five rounds."),
                 ("2", "Ground", "5 see, 4 feel, 3 hear, 2 smell, 1 taste."),
                 ("3", "Move or color", "walk, stretch, or color."),
                 ("4", "Write", "name the worry, then a kinder thought.")]
        cols = ["rose", "lavender", "mint", "peach"]
        yy = y - 52
        for i, (n, hd, b) in enumerate(lines):
            badge(c, x + pad + 9, yy + 3, n, C[cols[i]], 9, 9)
            text(c, x + pad + 24, yy, hd, "SansB", 9.5, C["ink"])
            text(c, x + pad + 24 + bj.sw(hd + "  ", "SansB", 9.5), yy, b, "Sans", 9, C["ink"])
            yy -= 21
        text(c, x + w / 2, y - h + 14, "This feeling is a wave. It will pass.", "Accent", 12, C["muted"], "center")
    else:
        text(c, x + pad, y - 26, "If you need help now", "Accent", 17, C["accent"])
        yy = y - 50
        for a, b in (("US:", "call or text 988, 24/7"), ("", "or text HOME to 741741"),
                     ("Emergency:", "call 911 or your local number"),
                     ("Outside the US:", "findahelpline.com")):
            if a:
                text(c, x + pad, yy, a, "SansB", 9.5, C["ink"])
            text(c, x + pad + 92, yy, b, "Sans", 9.5, C["ink"])
            yy -= 18
        text(c, x + pad, yy - 4, "My person to call:", "Sans", 9, C["muted"])
        c.saveState()
        c.setStrokeColor(C["rule"])
        c.setLineWidth(0.6)
        c.line(x + pad + 92, yy - 6, x + w - pad, yy - 6)
        c.restoreState()
        text(c, x + w / 2, y - h + 14, "Peace by Page  ·  " + STORE, "Sans", 8, C["muted"], "center")


def sos_card(J, c, F):
    kicker(c, F, "SOS card")
    y = title(c, F, "Your pocket SOS card", sub="Cut along the dashed lines and fold in the middle, "
              "or glue the two sides back to back.")
    w, h = min(F.w, 7.0 * 72) / 2 - 8, 178
    x0 = F.cx - w - 8
    y -= 10
    card(c, x0, y, w, h)
    card(c, x0 + w + 16, y, w, h, back=True)
    y -= h + 30
    card(c, x0, y, w, h)
    card(c, x0 + w + 16, y, w, h, back=True)
    y -= h + 34
    label(c, F.left, y, "Practice on a calm day", 11, C["accent"])
    para(c, F.left, y - 20, F.w, "Try the breathing and grounding steps when you feel okay, so they feel familiar "
         "when you need them. Stop as soon as you feel a little steadier.", "Sans", 10.5, 15.5)


_circles = {}


def circle_img(i):
    if i not in _circles:
        im = mba.ringed(mba.EDITIONS[i][1], 360, 30)
        buf = io.BytesIO()
        im.save(buf, "PNG")
        buf.seek(0)
        _circles[i] = ImageReader(buf)
    return _circles[i]


def full_journal(J, c, F):
    kicker(c, F, "Keep going")
    y = title(c, F, "Ready for all 90 days?", align="center", y=F.top - 50)
    y = para(c, F.left + 30, y - 4, F.w - 60,
             "The full journal has 90 daily pages, an SOS Toolkit, weekly check-ins with reward coloring, "
             "monthly mood and habit pages, and tools for building confidence. Three editions, same gentle pages:",
             "Sans", 10.5, 15.5, C["ink"], "center") - 12
    d = 128
    gap = (F.w - 3 * d) / 2
    names = [("Calm Wings", "butterflies"), ("Calm Petals", "botanical"), ("Calm Nights", "moon and stars")]
    for i, (n, sub) in enumerate(names):
        x = F.left + i * (d + gap)
        c.drawImage(circle_img(i), x, y - d, d, d, mask="auto")
        text(c, x + d / 2, y - d - 20, n, "Accent", 16, C["accent"], "center")
        text(c, x + d / 2, y - d - 36, sub, "Sans", 9, C["muted"], "center")
    y -= d + 74
    rbox(c, F.left + 40, y + 16, F.w - 80, 64, 16, stroke=C["accent"], fill=C["tint"], lw=1.0)
    text(c, F.cx, y - 10, "Find them at " + STORE, "SansB", 14, C["accent"], "center")
    text(c, F.cx, y - 30, "Printable PDFs in US Letter and A4. Instant download.", "Sans", 9.5, C["muted"], "center")
    y -= 92
    label(c, F.left, y, "Please note", 11, C["accent"])
    y = para(c, F.left, y - 20, F.w, content.DISCLAIMER.format(product="sampler"), "Sans", 10, 14.5) - 10
    label(c, F.left, y, "If you need help now", 11, C["accent"])
    y -= 20
    for a, b in content.CRISIS_SHORT:
        text(c, F.left, y, a, "SansB", 10)
        y = para(c, F.left + 120, y, F.w - 120, b, "Sans", 10, 14) - 6
    text(c, F.cx, F.bottom + 4, "© 2026 Peace by Page. Free to print for personal use.", "Sans", 8,
         C["muted"], "center")


def main():
    bj.register_fonts()
    bj.set_theme("wings")
    bj.content.DISCLAIMER = (
        "This sampler is a self-reflection tool for general wellbeing. It is not medical advice, diagnosis, or "
        "treatment, and it supports, not replaces, care from a licensed professional. If something in here "
        "doesn't feel right for you, skip it.")
    bj.content.PRINT_NOTE = (
        "Print at \"Actual size\" on plain or 24 lb (90 gsm) paper. Print the daily page as often as you like "
        "for yourself. Colored pencils work best on the coloring page.")
    os.makedirs(OUT, exist_ok=True)
    for size, tag in SIZES.items():
        cfg = dict(bj.CONFIG, theme="wings", page_size=size, days=7, shop_name="Peace by Page")
        path = os.path.join(OUT, f"PeaceByPage_7Day_Sampler_{tag}.pdf")
        n = Sampler(cfg).build(path)
        print(f"{path}: {n} pages, {os.path.getsize(path) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
