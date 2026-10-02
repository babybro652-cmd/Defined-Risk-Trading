#!/usr/bin/env python3
"""Build the Calm Wings 90-day anxiety journal as a print-ready PDF.

    python3 build_journal.py                 # builds both editions
    python3 build_journal.py --edition personal --name Sekora
    python3 build_journal.py --edition generic

Everything you would change for a new edition lives in the CONFIG block below.
"""
import argparse
import math
import os
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import butterfly_art as art  # noqa: E402
import content  # noqa: E402
import designs  # noqa: E402

# ==========================================================================
# CONFIG: edit here for a new edition
# ==========================================================================
CONFIG = {
    "name": "Sekora",                                  # personal edition name
    "title": "Calm Wings",
    "subtitle_personal": "A 90-Day Journal for {name}",
    "subtitle_generic": "A 90-Day Anxiety Journal",
    "greeting_personal": "Dear {name},",
    "greeting_generic": "Dear friend,",
    "signoff": "made with care for you",
    "file_personal": "Calm_Wings_{name}.pdf",
    "file_generic": "Calm_Wings_90_Day_Anxiety_Journal.pdf",
    "days": 90,
    # page geometry (inches)
    "margin": 0.6,
    "binding_extra": 0.25,
    "duplex": True,       # True: binding edge alternates (double-sided print)
    "page_size": "letter",  # "letter" (US) or "a4" (UK, EU, AU)
    "year": 2026,           # copyright year on the "Before you begin" page
    "shop_name": None,      # e.g. "Calm Wings Journal"; None keeps the shop name off the pages
    "about_page": True,     # generic edition: page 2 = disclaimer + terms of use
}

PAGE_SIZES = {"letter": letter, "a4": A4}

PALETTE = {
    "ink": "#3E4050",      # body text
    "muted": "#8A8DA0",    # small labels
    "rule": "#C9CBD7",     # writing lines
    "art": "#4B4D60",      # line art
    "accent": "#7E6BB5",   # headings (soft violet)
    "accent2": "#5E9F98",  # kickers (sea green)
    "lavender": "#E7DFF5",
    "mint": "#D7EEEA",
    "peach": "#FBE2D3",
    "rose": "#F8DCE5",
    "butter": "#FBF0CF",
    "sage": "#E0EDD9",
    "tint": "#F6F3FB",     # faintest panel tint
}

# Fonts: drop Quicksand / Caveat TTFs in ./fonts to override these.
FONT_CANDIDATES = {
    "Sans": [f"{HERE}/fonts/Quicksand-Regular.ttf", f"{HERE}/fonts/Nunito-Regular.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "SansB": [f"{HERE}/fonts/Quicksand-Bold.ttf", f"{HERE}/fonts/Nunito-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "SansI": [f"{HERE}/fonts/Nunito-Italic.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"],
    "Accent": [f"{HERE}/fonts/Caveat-Regular.ttf",
               "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"],
    "AccentR": ["/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"],
}

# ==========================================================================

C = {k: HexColor(v) for k, v in PALETTE.items()}
PW, PH = letter


def set_page_size(name):
    """Switch every layout to US Letter or A4. Layouts read PW / PH at draw time."""
    global PW, PH
    PW, PH = PAGE_SIZES[name.lower()]
    return PW, PH


def register_fonts():
    for name, paths in FONT_CANDIDATES.items():
        for p in paths:
            if os.path.exists(p):
                pdfmetrics.registerFont(TTFont(name, p))
                break
        else:
            raise SystemExit(f"No font found for {name}")


def sw(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


# ==========================================================================
# page frame + drawing helpers
# ==========================================================================


class Frame:
    def __init__(self, pno, cfg):
        m = cfg["margin"] * inch
        b = cfg["binding_extra"] * inch
        recto = (pno % 2 == 1) or not cfg["duplex"]
        self.left = m + (b if recto else 0)
        self.right = PW - m - (0 if recto else b)
        self.top = PH - m
        self.bottom = m
        self.w = self.right - self.left
        self.cx = (self.left + self.right) / 2
        self.pno = pno


def text(c, x, y, s, font="Sans", size=10.5, color=None, align="left", space=0):
    c.setFont(font, size)
    c.setFillColor(color or C["ink"])
    if space:
        w = sw(s, font, size) + space * (len(s) - 1)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        t = c.beginText(x, y)
        t.setFont(font, size)
        t.setCharSpace(space)
        t.textOut(s)
        t.setCharSpace(0)
        c.drawText(t)
        return
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)


def wrap(s, font, size, width):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if sw(t, font, size) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(c, x, y, width, s, font="Sans", size=10.5, leading=None, color=None, align="left",
         after=6):
    leading = leading or size * 1.45
    for block in s.split("\n"):
        for ln in wrap(block, font, size, width):
            xx = x + width / 2 if align == "center" else x
            text(c, xx, y, ln, font, size, color, align)
            y -= leading
        y -= after
    return y + after


def kicker(c, F, s, color=None):
    text(c, F.left, F.top - 6, s.upper(), "SansB", 7.5, color or C["accent2"], space=1.6)


def title(c, F, s, size=26, y=None, sub=None, align="left"):
    y = F.top - 40 if y is None else y
    x = F.cx if align == "center" else F.left
    text(c, x, y, s, "Accent", size, C["accent"], align)
    if sub:
        text(c, x, y - 20, sub, "Sans", 10, C["muted"], align)
        return y - 44
    return y - 26


def rule_lines(c, x, y, w, n, gap=24, color=None):
    c.saveState()
    c.setStrokeColor(color or C["rule"])
    c.setLineWidth(0.6)
    for i in range(n):
        c.line(x, y - i * gap, x + w, y - i * gap)
    c.restoreState()
    return y - (n - 1) * gap


def label(c, x, y, s, size=10.5, color=None, font="SansB"):
    text(c, x, y, s, font, size, color or C["ink"])


def rbox(c, x, y, w, h, r=8, stroke=None, fill=None, lw=0.7, dash=None):
    """x, y = top-left corner."""
    c.saveState()
    c.setStrokeColor(stroke or C["rule"])
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    if fill is not None:
        c.setFillColor(fill)
    c.roundRect(x, y - h, w, h, r, stroke=1 if stroke is not False else 0,
                fill=1 if fill is not None else 0)
    c.restoreState()


def checkbox(c, x, y, s=10, color=None):
    c.saveState()
    c.setStrokeColor(color or C["muted"])
    c.setLineWidth(0.8)
    c.roundRect(x, y, s, s, 2, stroke=1, fill=0)
    c.restoreState()


def rating_row(c, x, y, w, lab, lo="", hi="", r=8.5, lab_w=120):
    """A 0-10 row of circles. y is the baseline of the label."""
    label(c, x, y, lab, 10.5, font="Sans")
    x0 = x + lab_w
    span = w - lab_w
    step = span / 11
    c.saveState()
    c.setStrokeColor(C["muted"])
    c.setLineWidth(0.8)
    for i in range(11):
        cx = x0 + step * (i + 0.5)
        c.circle(cx, y + 3.5, r, stroke=1, fill=0)
        text(c, cx, y + 0.8, str(i), "Sans", 7, C["muted"], "center")
    c.restoreState()
    if lo:
        text(c, x0 + step * 0.5, y - 14, lo, "Sans", 7, C["muted"], "center")
    if hi:
        text(c, x0 + step * 10.5, y - 14, hi, "Sans", 7, C["muted"], "center")


def small_fly(c, x, y, size, k=0, angle=0.0, style=None):
    """A small pastel accent butterfly."""
    pals = [("lavender", "mint", "peach"), ("mint", "peach", "lavender"),
            ("peach", "rose", "lavender"), ("rose", "lavender", "mint"),
            ("butter", "peach", "lavender"), ("sage", "mint", "peach")]
    a, b, d = pals[k % len(pals)]
    styles = ["simple", "round", "classic", "petal"]
    art.draw_butterfly(c, x, y, size, style or styles[k % len(styles)], angle=angle,
                       lw=0.55 if size < 30 else 0.75, ink=C["art"],
                       fills=(C[a], C[b], C[d]), body_fill=white,
                       segments=size > 25)


def arrow(c, x0, y0, x1, y1, color=None, lw=0.9, head=5):
    c.saveState()
    c.setStrokeColor(color or C["muted"])
    c.setFillColor(color or C["muted"])
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.line(x0, y0, x1, y1)
    a = math.atan2(y1 - y0, x1 - x0)
    p = c.beginPath()
    p.moveTo(x1, y1)
    p.lineTo(x1 - head * math.cos(a - 0.45), y1 - head * math.sin(a - 0.45))
    p.lineTo(x1 - head * math.cos(a + 0.45), y1 - head * math.sin(a + 0.45))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def badge(c, x, y, s, fill, r=11, size=10):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(fill)
    c.circle(x, y, r, stroke=0, fill=1)
    c.restoreState()
    text(c, x, y - size * 0.35, s, "SansB", size, C["ink"], "center")


# ==========================================================================
# journal
# ==========================================================================


class Journal:
    def __init__(self, cfg, generic):
        self.cfg = cfg
        self.generic = generic
        self.name = None if generic else cfg["name"]
        self.pages = []
        self.marks = {}

    # ---------------------------------------------------------------- plan
    def mark(self, key):
        self.marks[key] = len(self.pages) + 1

    def add(self, fn, *args, footer=True):
        self.pages.append((fn, args, footer))

    def plan(self):
        P = self
        P.add(cover, footer=False)
        if self.generic and self.cfg.get("about_page"):
            P.add(about_page, "journal")
        P.mark("start")
        for fn in (welcome, how_anxiety_works, starting_point, my_people, more_help, key_pages):
            P.add(fn)
        P.mark("sos")
        P.add(sos_flow)
        P.mark("box")
        P.add(box_breathing)
        P.mark("exhale")
        P.add(long_exhale)
        P.mark("ground")
        P.add(grounding)
        P.mark("pmr")
        P.add(pmr)
        P.mark("tree")
        P.add(worry_tree)
        P.mark("thought")
        P.add(thought_record)
        P.mark("color")
        P.add(coloring_page, "mandala")
        P.add(coloring_page, "geometric")
        P.mark("phrases")
        P.add(will_pass)
        P.mark("daily")
        days = self.cfg["days"]
        week = 0
        for d in range(1, days + 1):
            P.add(daily, d)
            if d % 7 == 0 or d == days:
                week += 1
                if week == 1:
                    P.mark("weekly")
                start = (week - 1) * 7 + 1
                P.add(weekly_review, week, start, d)
                P.add(handled_it, week, start, d)
                P.add(reward_coloring, week)
            if d % 30 == 0:
                m = d // 30
                if m == 1:
                    P.mark("monthly")
                P.add(mood_butterfly, m, d - 29, d)
                P.add(habit_tracker, m, d - 29, d)
                P.add(compassion_letter, m)
        P.mark("confidence")
        for fn in (fear_ladder, ladder_log, lift_menu, wind_down, values_page, worry_time):
            P.add(fn)
        P.add(expressive, 0)
        P.add(expressive, 1)
        P.mark("lookback")
        for fn in (ninety_check, what_worked, future_letter, keep_going):
            P.add(fn)
        P.add(back_page)

    # --------------------------------------------------------------- build
    def build(self, path):
        self.plan()
        set_page_size(self.cfg.get("page_size", "letter"))
        c = canvas.Canvas(path, pagesize=(PW, PH))
        title_txt = self.cfg["title"] + ": " + self.subtitle()
        c.setTitle(title_txt)
        c.setAuthor("Calm Wings")
        c.setSubject("90-day anxiety journal")
        for i, (fn, args, footer) in enumerate(self.pages, 1):
            F = Frame(i, self.cfg)
            fn(self, c, F, *args)
            if footer:
                text(c, F.cx, 0.32 * inch, str(i), "Sans", 7, C["muted"], "center")
            c.showPage()
        c.save()
        return len(self.pages)

    def subtitle(self):
        if self.generic:
            return self.cfg["subtitle_generic"]
        return self.cfg["subtitle_personal"].format(name=self.name)

    def pg(self, key):
        return self.marks.get(key, 0)


# ==========================================================================
# pages: cover + section 1
# ==========================================================================


def cover(J, c, F, opts=None):
    """opts (optional, for the stand-alone packs): title, subtitle, tagline, style, fills, lineart."""
    o = dict(title=J.cfg["title"], subtitle=J.subtitle(), tagline="breathe  \u00b7  notice  \u00b7  grow",
             style="classic", fills=("lavender", "mint", "peach"), lineart=False,
             belongs="This journal belongs to" if J.generic else None)
    o.update(opts or {})
    cx = PW / 2
    c.saveState()
    c.translate(0, (PH - letter[1]) / 2)   # A4 is taller: keep the design centered
    # soft halo
    c.saveState()
    c.setFillColor(C["tint"])
    c.circle(cx, 500, 188, stroke=0, fill=1)
    c.setStrokeColor(C["lavender"])
    c.setLineWidth(0.8)
    c.setDash(1, 4)
    c.circle(cx, 500, 206, stroke=1, fill=0)
    c.restoreState()
    fills = None if o["lineart"] else tuple(C[k] for k in o["fills"])
    art.draw_butterfly(c, cx, 505, 168, o["style"], lw=1.2 if o["lineart"] else 1.0, ink=C["art"],
                       fills=fills, body_fill=white)
    # little companions with dotted flight trails
    trail = art.bezier_pts((cx - 205, 300), (cx - 250, 360), (cx - 170, 400), (cx - 218, 452))
    art.dashed_path(c, trail, lw=0.6, ink=C["muted"], dash=(0.8, 3.5))
    small_fly(c, cx - 222, 462, 17, 3, angle=-30)
    trail2 = art.bezier_pts((cx + 160, 690), (cx + 190, 720), (cx + 230, 700), (cx + 214, 664))
    art.dashed_path(c, trail2, lw=0.6, ink=C["muted"], dash=(0.8, 3.5))
    small_fly(c, cx + 150, 698, 14, 1, angle=28)
    small_fly(c, cx + 208, 300, 12, 4, angle=-12)
    text(c, cx, 228, o["title"], "Accent", 58, C["accent"], "center")
    text(c, cx, 192, o["subtitle"], "Sans", 15, C["ink"], "center", space=0.6)
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.7)
    c.line(cx - 90, 170, cx - 12, 170)
    c.line(cx + 12, 170, cx + 90, 170)
    c.restoreState()
    c.setFillColor(C["accent"])
    c.circle(cx, 170, 2, stroke=0, fill=1)
    text(c, cx, 150, o["tagline"], "Sans", 9.5, C["muted"], "center", space=1.2)
    if o["belongs"]:
        bx = cx - 150
        text(c, bx, 82, o["belongs"], "Sans", 9.5, C["muted"])
        c.setStrokeColor(C["rule"])
        c.setLineWidth(0.6)
        c.line(bx + sw(o["belongs"], "Sans", 9.5) + 8, 80, cx + 150, 80)
    c.restoreState()


def about_page(J, c, F, product="journal"):
    """Page 2 of every product: disclaimer, crisis lines, terms of use."""
    kicker(c, F, "Before you begin")
    y = title(c, F, "A few words first")
    small_fly(c, F.right - 26, F.top - 26, 22, 2, angle=14)
    y -= 4
    rbox(c, F.left, y + 14, F.w, 100, 14, stroke=C["accent"], fill=C["tint"], lw=1.0)
    label(c, F.left + 20, y - 8, f"About this {product}", 11.5, C["accent"])
    para(c, F.left + 20, y - 28, F.w - 40, content.DISCLAIMER.format(product=product), "Sans", 10.5, 15.5)
    y -= 122
    label(c, F.left, y, "If you need help now", 11.5, C["accent"])
    y -= 22
    for a, b in content.CRISIS_SHORT:
        text(c, F.left, y, a, "SansB", 10.5)
        y = para(c, F.left + 130, y, F.w - 130, b, "Sans", 10.5, 15) - 9
    y -= 14
    label(c, F.left, y, "Terms of use", 11.5, C["accent"])
    y = para(c, F.left, y - 22, F.w, content.TERMS.format(product=product), "Sans", 10.5, 15.5, after=8) - 14
    label(c, F.left, y, "Printing", 11.5, C["accent"])
    y = para(c, F.left, y - 22, F.w, content.PRINT_NOTE, "Sans", 10.5, 15.5) - 26
    shop = J.cfg.get("shop_name")
    owner = f"Calm Wings by {shop}" if shop else "Calm Wings"
    text(c, F.left, y, f"\u00a9 {J.cfg.get('year', 2026)} {owner}. All rights reserved.", "Sans", 9, C["muted"])
    text(c, F.left, y - 14, "Content and art created with AI assistance and reviewed by the maker.", "Sans", 9,
         C["muted"])


def welcome(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "Welcome")
    y -= 14
    greet = J.cfg["greeting_generic"] if J.generic else J.cfg["greeting_personal"].format(name=J.name)
    text(c, F.left, y, greet, "Accent", 17, C["ink"])
    y -= 30
    y = para(c, F.left, y, F.w - 40, content.WELCOME, "Sans", 11, 17.5, after=10)
    y -= 14
    text(c, F.right - 60, y, J.cfg["signoff"], "Accent", 17, C["accent"], "right")
    small_fly(c, F.right - 30, y + 6, 18, 0, angle=12)
    # what you need
    y -= 70
    bw = F.w
    rbox(c, F.left, y, bw, 108, 12, stroke=False, fill=C["tint"])
    text(c, F.left + 22, y - 26, "WHAT YOU'LL NEED", "SansB", 7.5, C["accent2"], space=1.6)
    items = [("A pen", "anything you like writing with"),
             ("Colored pencils", "or markers, for the coloring pages"),
             ("About 5 minutes", "most days, and no pressure on the others")]
    colw = (bw - 44) / 3
    for i, (a, b) in enumerate(items):
        x = F.left + 22 + i * colw
        text(c, x, y - 52, a, "SansB", 11, C["ink"])
        para(c, x, y - 70, colw - 16, b, "Sans", 9.5, 13, C["muted"])


def how_anxiety_works(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "How anxiety works")
    y -= 6
    for head, body in content.HOW_ANXIETY[:2]:
        label(c, F.left, y, head, 11.5, C["accent"])
        y = para(c, F.left, y - 18, F.w, body, "Sans", 10.5, 15.5, after=4) - 16
    # wave diagram beside the third paragraph
    head, body = content.HOW_ANXIETY[2]
    label(c, F.left, y, head, 11.5, C["accent"])
    tw = F.w * 0.52
    y2 = para(c, F.left, y - 18, tw, body, "Sans", 10.5, 15.5, after=4)
    gx0, gx1 = F.left + tw + 24, F.right - 4
    gy = y - 112
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.7)
    c.line(gx0, gy, gx1, gy)
    c.line(gx0, gy, gx0, gy + 96)
    pts = []
    for i in range(101):
        t = i / 100
        v = math.exp(-((t - 0.38) / 0.17) ** 2) if t < 0.38 else math.exp(-((t - 0.38) / 0.3) ** 2)
        pts.append((gx0 + 6 + t * (gx1 - gx0 - 10), gy + 6 + 80 * v))
    c.setStrokeColor(C["accent"])
    c.setLineWidth(1.6)
    c.setLineCap(1)
    art.draw_poly(c, pts, close=False)
    c.restoreState()
    for t, s in ((0.16, "builds"), (0.38, "peaks"), (0.74, "settles")):
        i = int(t * 100)
        px, py = pts[i]
        if s == "builds":
            text(c, px - 8, py, s, "Accent", 11.5, C["ink"], "right")
        else:
            text(c, px + (0 if s == "peaks" else 6), py + 8 if s == "peaks" else py + 10, s,
                 "Accent", 11.5, C["ink"], "center" if s == "peaks" else "left")
    text(c, gx1, gy - 12, "time (often minutes)", "Sans", 7.5, C["muted"], "right")
    text(c, gx0 - 4, gy + 100, "how strong", "Sans", 7.5, C["muted"])
    y = min(y2, gy - 20) - 16
    head, body = content.HOW_ANXIETY[3]
    label(c, F.left, y, head, 11.5, C["accent"])
    y = para(c, F.left, y - 18, F.w, body, "Sans", 10.5, 15.5, after=4) - 10
    # life cycle strip
    lifecycle(c, F, y - 64)


def lifecycle(c, F, y):
    xs = [F.left + F.w * (i + 0.5) / 4 for i in range(4)]
    ink = C["art"]
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(0.9)
    # egg on a leaf
    art.draw_leaf(c, xs[0] - 26, y - 6, 52, 8, lw=0.9, ink=ink, fill=C["sage"])
    c.setFillColor(C["butter"])
    c.ellipse(xs[0] - 5, y + 6, xs[0] + 5, y + 20, stroke=1, fill=1)
    # caterpillar
    for i in range(6):
        cx = xs[1] - 26 + i * 10
        cy = y + 8 + 6 * math.sin(i * 1.1)
        c.setFillColor(C["mint"] if i % 2 else C["sage"])
        c.circle(cx, cy, 7 if i < 5 else 8, stroke=1, fill=1)
    c.setFillColor(ink)
    c.circle(xs[1] + 26, y + 8 + 6 * math.sin(5 * 1.1) + 2, 1.2, stroke=0, fill=1)
    # chrysalis hanging from a twig
    c.line(xs[2] - 24, y + 40, xs[2] + 24, y + 40)
    c.line(xs[2], y + 40, xs[2], y + 32)
    ch = art.bezier_pts((xs[2], y + 32), (xs[2] + 16, y + 26), (xs[2] + 10, y - 10), (xs[2], y - 16)) + \
        art.bezier_pts((xs[2], y - 16), (xs[2] - 10, y - 10), (xs[2] - 16, y + 26), (xs[2], y + 32))
    c.setFillColor(C["peach"])
    art.draw_poly(c, ch, fill=True)
    c.line(xs[2] - 8, y + 16, xs[2] + 8, y + 16)
    c.line(xs[2] - 6, y + 6, xs[2] + 6, y + 6)
    c.restoreState()
    small_fly(c, xs[3], y + 10, 26, 0)
    labels = ["begin", "grow", "rest and change", "fly"]
    for i, x in enumerate(xs):
        text(c, x, y - 34, labels[i], "Accent", 12, C["ink"], "center")
        if i < 3:
            arrow(c, x + 38, y + 10, xs[i + 1] - 38, y + 10, C["rule"], 0.9, 5)


def starting_point(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "My starting point")
    text(c, F.right - 170, F.top - 40, "Date", "Sans", 10, C["muted"])
    rule_lines(c, F.right - 140, F.top - 42, 140, 1)
    y -= 2
    y = para(c, F.left, y, F.w, "Rate how things feel right now, most days. No right answers. "
             "You'll come back to this page on Day 90 to see what has shifted.",
             "Sans", 10.5, 15.5, C["muted"]) - 24
    for lab, lo, hi in (("Anxiety", "calm", "very anxious"), ("Sleep", "poor", "great"),
                        ("Mood", "low", "great")):
        rating_row(c, F.left, y, F.w, lab, lo, hi, r=10, lab_w=100)
        y -= 50
    y -= 6
    prompts = [("What I want to feel more of", 4), ("What tends to set off my anxiety", 3),
               ("What already helps, even a little", 3), ("What I hope this journal helps with", 3)]
    for p, n in prompts:
        label(c, F.left, y, p, 11, C["accent"])
        y = rule_lines(c, F.left, y - 26, F.w, n, 24) - 36
    small_fly(c, F.right - 20, F.top - 2, 15, 2, angle=15)


def my_people(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "My people")
    y = para(c, F.left, y, F.w, "The people I can call, text, or sit with when things feel like a lot. "
             "Add anyone who makes you feel steadier.", "Sans", 10.5, 15.5, C["muted"]) - 18
    cw = (F.w - 16) / 2
    ch = 88
    for i in range(6):
        x = F.left + (i % 2) * (cw + 16)
        yy = y - (i // 2) * (ch + 12)
        rbox(c, x, yy, cw, ch, 10)
        for j, lab in enumerate(("Name", "Phone", "Good for")):
            ly = yy - 24 - j * 24
            text(c, x + 14, ly, lab, "Sans", 8.5, C["muted"])
            rule_lines(c, x + 64, ly - 2, cw - 80, 1)
    y -= 3 * (ch + 12) + 14
    label(c, F.left, y, "My care team", 11.5, C["accent"])
    y -= 26
    for lab in ("Therapist or counselor", "Doctor", "Other support"):
        text(c, F.left, y, lab, "Sans", 10)
        text(c, F.left + 160, y, "Name", "Sans", 8.5, C["muted"])
        rule_lines(c, F.left + 190, y - 2, 140, 1)
        text(c, F.left + 342, y, "Phone", "Sans", 8.5, C["muted"])
        rule_lines(c, F.left + 374, y - 2, F.w - 374, 1)
        y -= 30
    y -= 8
    rbox(c, F.left, y + 12, F.w, 40, 10, stroke=False, fill=C["tint"])
    text(c, F.left + 16, y - 9, "Any time, day or night:", "Sans", 10, C["muted"])
    text(c, F.left + 140, y - 9, "988  (call or text, US Suicide & Crisis Lifeline)", "SansB", 10.5)


def more_help(J, c, F, product="journal", kick="Start here"):
    kicker(c, F, kick)
    y = title(c, F, "When to get more help")
    intro = content.HELP_INTRO.replace("This journal", f"This {product}")
    y = para(c, F.left, y, F.w, intro, "Sans", 10.5, 15.5) - 12
    for b in content.HELP_SIGNS:
        c.setFillColor(C["accent"])
        c.circle(F.left + 5, y + 3.5, 2.2, stroke=0, fill=1)
        y = para(c, F.left + 18, y, F.w - 18, b, "Sans", 10.5, 15) - 6
    y -= 12
    label(c, F.left, y, "Get help right away if", 11.5, C["accent"])
    y -= 22
    for b in content.HELP_URGENT:
        c.setFillColor(C["accent"])
        c.circle(F.left + 5, y + 3.5, 2.2, stroke=0, fill=1)
        y = para(c, F.left + 18, y, F.w - 18, b, "Sans", 10.5, 15) - 6
    y -= 16
    bh = 112
    rbox(c, F.left, y, F.w, bh, 14, stroke=C["accent"], fill=C["tint"], lw=1.1)
    text(c, F.left + 28, y - 48, "988", "SansB", 34, C["accent"])
    text(c, F.left + 112, y - 30, "Call or text 988", "SansB", 13)
    text(c, F.left + 112, y - 47, "US Suicide & Crisis Lifeline", "Sans", 10.5)
    text(c, F.left + 112, y - 64, "Free, confidential, 24 hours a day. You can also chat at 988lifeline.org.",
         "Sans", 9, C["muted"])
    text(c, F.left + 28, y - 92, "If you or someone else is in immediate danger, call 911.", "SansB", 10)
    y -= bh + 30
    para(c, F.left, y, F.w, "Asking for help is a strong, sensible thing to do. It is not a failure, "
         "and you don't have to wait until things are at their worst.", "Accent", 13.5, 19, C["ink"])


def key_pages(J, c, F):
    kicker(c, F, "Start here")
    y = title(c, F, "Key to the pages")
    y = para(c, F.left, y, F.w, "Here's what you'll find and where. Use what helps; skip what doesn't.",
             "Sans", 10.5, 15.5, C["muted"]) - 14
    rows = [
        ("SOS Toolkit", f"page {J.pg('sos')}", "Turn here when anxiety spikes. Breathing, grounding, and calming tools.", "rose"),
        ("Daily pages", f"from page {J.pg('daily')}", "Rate your day, note three good things, untangle one worry, plan one small step. About 5 minutes.", "lavender"),
        ("Weekly check-in", "every 7 days", "Look back on the week, log what you handled, then color your reward butterfly.", "mint"),
        ("Monthly pages", "after days 30, 60, 90", "Color your mood butterfly, track habits, and write yourself a kind letter.", "peach"),
        ("Building Confidence", f"page {J.pg('confidence')}", "Tools for facing fears a little at a time, sleep, values, and worry time.", "butter"),
        ("Look Back", f"page {J.pg('lookback')}", "See how far you've come and plan what's next.", "sage"),
    ]
    for i, (a, where, b, col) in enumerate(rows):
        small_fly(c, F.left + 16, y - 6, 13, i)
        text(c, F.left + 44, y, a, "SansB", 11)
        text(c, F.right, y, where, "Sans", 9, C["accent2"], "right")
        y = para(c, F.left + 44, y - 16, F.w - 44, b, "Sans", 10, 14, C["ink"]) - 18
    y -= 4
    label(c, F.left, y, "How to fill things in", 11.5, C["accent"])
    y -= 30
    c.saveState()
    c.setStrokeColor(C["muted"])
    c.setLineWidth(0.8)
    for i in range(3):
        c.circle(F.left + 10 + i * 22, y + 3, 8, stroke=1, fill=0)
    c.setFillColor(C["lavender"])
    c.circle(F.left + 54, y + 3, 8, stroke=1, fill=1)
    c.restoreState()
    text(c, F.left + 80, y, "Rating circles: fill in or color the number that fits. 0 = none, 10 = the most.", "Sans", 10)
    y -= 28
    checkbox(c, F.left + 4, y - 2)
    text(c, F.left + 80, y, "Checkboxes: tick what you did. Blank boxes are not failures.", "Sans", 10)
    y -= 28
    rule_lines(c, F.left, y - 2, 60, 1)
    text(c, F.left + 80, y, "Lines: write as much or as little as you like. A word counts.", "Sans", 10)


# ==========================================================================
# section 2: SOS toolkit
# ==========================================================================


def sos_flow(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "When anxiety hits, start here")
    y = para(c, F.left, y, F.w, "Go one step at a time. You can stop as soon as you feel a little steadier.",
             "Sans", 10.5, 15.5, C["muted"]) - 10
    steps = content.SOS_STEPS
    bw, bh = F.w - 70, 98
    cols = ["rose", "lavender", "mint", "peach"]
    for i, (head, body, ref) in enumerate(steps):
        x = F.left + (0 if i % 2 == 0 else 70)
        yy = y - i * (bh + 30)
        rbox(c, x, yy, bw, bh, 16, stroke=False, fill=C["tint"])
        badge(c, x + 32, yy - 34, str(i + 1), C[cols[i]], 17, 14)
        text(c, x + 64, yy - 30, head, "Accent", 20, C["accent"])
        para(c, x + 64, yy - 52, bw - 90, body, "Sans", 10, 14)
        text(c, x + bw - 16, yy - 30, ref.format(**{k: J.pg(k) for k in J.marks}), "Sans", 8.5,
             C["accent2"], "right")
        if i < 3:
            if i % 2 == 0:
                arrow(c, x + bw - 60, yy - bh - 4, x + bw - 30, yy - bh - 26, C["muted"])
            else:
                arrow(c, x + 60, yy - bh - 4, x + 30, yy - bh - 26, C["muted"])
    y -= 4 * (bh + 30) + 2
    small_fly(c, F.cx, y - 8, 20, 0)
    y -= 46
    text(c, F.cx, y, "Feeling unsafe? Call or text 988, any time.", "SansB", 10.5, C["ink"], "center")


def box_breathing(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "Box breathing")
    y = para(c, F.left, y, F.w, "Trace the square with a finger or pen. Each side is four slow counts. "
             "Start at the dot and follow the arrows.", "Sans", 10.5, 15.5, C["muted"]) - 20
    s = 300
    x0 = F.cx - s / 2
    y0 = y - 40 - s
    c.saveState()
    c.setStrokeColor(C["lavender"])
    c.setLineWidth(14)
    c.setLineJoin(1)
    c.roundRect(x0, y0, s, s, 24, stroke=1, fill=0)
    c.setStrokeColor(C["accent"])
    c.setLineWidth(1.2)
    c.setDash(2, 4)
    c.roundRect(x0, y0, s, s, 24, stroke=1, fill=0)
    c.restoreState()
    # ticks with counts
    corners = [(x0, y0), (x0, y0 + s), (x0 + s, y0 + s), (x0 + s, y0)]
    sides = [("Breathe in", 0), ("Hold", 1), ("Breathe out", 2), ("Hold", 3)]
    for k in range(4):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % 4]
        for j in range(1, 5):
            t = 0.12 + 0.76 * (j - 0.5) / 4
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            c.setFillColor(white)
            c.setStrokeColor(C["accent"])
            c.setLineWidth(0.8)
            c.circle(px, py, 8, stroke=1, fill=1)
            text(c, px, py - 3, str(j), "SansB", 8, C["accent"], "center")
    text(c, x0 - 22, y0 + s / 2, "", "Sans", 8)
    # labels
    c.saveState()
    c.translate(x0 - 30, y0 + s / 2)
    c.rotate(90)
    text(c, 0, 0, "Breathe in", "Accent", 16, C["ink"], "center")
    c.restoreState()
    text(c, x0 + s / 2, y0 + s + 24, "Hold", "Accent", 16, C["ink"], "center")
    c.saveState()
    c.translate(x0 + s + 38, y0 + s / 2)
    c.rotate(-90)
    text(c, 0, 0, "Breathe out", "Accent", 16, C["ink"], "center")
    c.restoreState()
    text(c, x0 + s / 2, y0 - 34, "Hold", "Accent", 16, C["ink"], "center")
    # start dot + arrows at corners
    c.setFillColor(C["accent"])
    c.circle(x0, y0, 6, stroke=0, fill=1)
    text(c, x0 - 10, y0 - 18, "start", "Sans", 8, C["accent"], "right")
    arrow(c, x0 + 40, y0 + s + 12, x0 + 80, y0 + s + 12, C["accent"])
    arrow(c, x0 + s + 12, y0 + s - 40, x0 + s + 12, y0 + s - 80, C["accent"])
    arrow(c, x0 + s - 40, y0 - 12, x0 + s - 80, y0 - 12, C["accent"])
    arrow(c, x0 - 12, y0 + 40, x0 - 12, y0 + 80, C["accent"])
    small_fly(c, F.cx, y0 + s / 2 + 4, 44, 1)
    y = y0 - 70
    y = para(c, F.left, y, F.w, "Go around four times, or for as long as it feels good. If holding your breath "
             "feels uncomfortable, skip the holds and breathe in and out slowly instead.",
             "Sans", 10.5, 15.5) - 14
    text(c, F.left, y, "How I felt before", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 98, y - 2, 60, 1)
    text(c, F.left + 190, y, "after", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 222, y - 2, 60, 1)
    text(c, F.left + 300, y, "(0 to 10)", "Sans", 8.5, C["muted"])


def long_exhale(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "Long-exhale breathing")
    y = para(c, F.left, y, F.w, "A longer out-breath tells your body it's safe to slow down. Breathe in for 4, "
             "out for 6. Trace each wing: in as you travel up and out, out as you glide back around to the body.",
             "Sans", 10.5, 15.5, C["muted"]) - 8
    cx, cy = F.cx, y - 250
    size = 225
    w = art.Wing((0.0, 0.0), 86, -96, [0, 0.72, 0.98, 1.0, 0.82, 0.62, 0.7, 0.72, 0.6, 0.0])
    pts = w.outline(n=600)
    # arc length
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
    tot = L[-1]
    split = 0.4 * tot
    for mirror in (False, True):
        tf = art.Tf(cx, cy, size, 0, mirror)
        P = [tf(p) for p in pts]
        c.saveState()
        c.setLineCap(1)
        c.setLineJoin(1)
        c.setLineWidth(15)
        c.setStrokeColor(C["mint"])
        idx = next(i for i, l in enumerate(L) if l >= split)
        art.draw_poly(c, P[:idx + 1], close=False)
        c.setStrokeColor(C["lavender"])
        art.draw_poly(c, P[idx:], close=False)
        c.setLineWidth(1)
        c.setDash(2, 4)
        c.setStrokeColor(C["accent"])
        art.draw_poly(c, P, close=False)
        c.restoreState()
        # numbered counts
        for j in range(4):
            target = split * (j + 1) / 4.15
            i = next(i for i, l in enumerate(L) if l >= target)
            px, py = P[i]
            c.setFillColor(white)
            c.setStrokeColor(C["accent2"])
            c.setLineWidth(0.8)
            c.circle(px, py, 8, stroke=1, fill=1)
            text(c, px, py - 3, str(j + 1), "SansB", 8, C["accent2"], "center")
        for j in range(6):
            target = split + (tot - split) * (j + 1) / 6.6
            i = next(i for i, l in enumerate(L) if l >= target)
            px, py = P[i]
            c.setFillColor(white)
            c.setStrokeColor(C["accent"])
            c.setLineWidth(0.8)
            c.circle(px, py, 8, stroke=1, fill=1)
            text(c, px, py - 3, str(j + 1), "SansB", 8, C["accent"], "center")
    art.draw_body(c, art.Tf(cx, cy + 4, size * 0.42), 0.9, C["art"], antennae=0.7)
    c.setFillColor(C["accent"])
    c.circle(cx, cy + 1, 4, stroke=0, fill=1)
    # legend
    ly = cy - size * 0.95 - 10
    for i, (col, s) in enumerate(((C["mint"], "Breathe in: 1, 2, 3, 4"),
                                  (C["lavender"], "Breathe out: 1, 2, 3, 4, 5, 6"))):
        x = F.cx - 200 + i * 210
        c.setFillColor(col)
        c.roundRect(x, ly - 2, 26, 10, 5, stroke=0, fill=1)
        text(c, x + 34, ly, s, "Sans", 10)
    y = ly - 34
    para(c, F.left, y, F.w, "Do one wing, then the other. Five rounds is plenty. If 4 and 6 feel too long, "
         "try 3 and 5. What matters is that the out-breath is longer than the in-breath.",
         "Sans", 10.5, 15.5)


def grounding(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "5-4-3-2-1 grounding")
    y = para(c, F.left, y, F.w, "When your mind is racing ahead, bring it back to right here. Go slowly and "
             "notice the small details: colors, textures, quiet sounds.", "Sans", 10.5, 15.5, C["muted"]) - 16
    rows = [("5", "things I can see", "lavender", 3), ("4", "things I can feel or touch", "mint", 2),
            ("3", "things I can hear", "peach", 2), ("2", "things I can smell", "rose", 2),
            ("1", "thing I can taste, or one slow breath", "butter", 1)]
    for n, lab, col, lines in rows:
        badge(c, F.left + 18, y - 2, n, C[col], 18, 17)
        text(c, F.left + 48, y - 8, lab, "Accent", 17, C["ink"])
        y = rule_lines(c, F.left + 48, y - 36, F.w - 48, lines, 25) - 34
    y -= 4
    text(c, F.left, y, "Now I feel", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 62, y - 2, F.w - 62, 1)


def pmr(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "Progressive muscle relaxation")
    y = para(c, F.left, y, F.w, "Tense each part of your body for about 5 seconds, then let it go for about "
             "10 seconds and notice the difference. Tense gently. It should never hurt. Sitting or lying down "
             "both work.", "Sans", 10.5, 15.5, C["muted"]) - 12
    # write-in for the reader's own calming audio (replaces the old QR placeholder)
    rbox(c, F.left, y + 4, F.w, 62, 12, stroke=False, fill=C["tint"])
    text(c, F.left + 16, y - 16, "My favorite calming audio", "SansB", 10.5, C["accent"])
    text(c, F.left + 16 + sw("My favorite calming audio", "SansB", 10.5) + 8, y - 16,
         "a song, playlist, podcast, or guided recording that helps me relax", "Sans", 8.5, C["muted"])
    rule_lines(c, F.left + 16, y - 42, F.w - 32, 1)
    y -= 84
    for i, (part, how) in enumerate(content.PMR_STEPS, 1):
        badge(c, F.left + 11, y + 3.5, str(i), C["lavender"], 10, 9)
        text(c, F.left + 30, y, part, "SansB", 10.5)
        y = para(c, F.left + 30 + 92, y, F.w - 122, how, "Sans", 10.5, 15) - 19
    y -= 2
    y = para(c, F.left, y, F.w, content.PMR_END, "Accent", 13.5, 19, C["ink"]) - 16
    text(c, F.left, y, "How I felt before", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 98, y - 2, 60, 1)
    text(c, F.left + 190, y, "after", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 222, y - 2, 60, 1)
    text(c, F.left + 300, y, "(0 to 10)", "Sans", 8.5, C["muted"])


def node(c, x, y, w, h, head, body=None, fill=None, lines=0, center=True):
    rbox(c, x, y, w, h, 12, stroke=C["rule"] if fill is None else False, fill=fill)
    if center:
        yy = para(c, x + 12, y - 20, w - 24, head, "SansB", 10.5, 14, C["ink"], "center")
    else:
        yy = para(c, x + 14, y - 20, w - 28, head, "SansB", 10.5, 14, C["ink"])
    if body:
        yy = para(c, x + 12, yy - 2, w - 24, body, "Sans", 9.5, 13, C["ink"], "center" if center else "left")
    if lines:
        rule_lines(c, x + 14, yy - 10, w - 28, lines, 22)


def worry_tree(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "The worry tree")
    y = para(c, F.left, y, F.w, "Worries feel urgent, but they're not all the same kind. This helps you sort "
             "them so you know what to do next.", "Sans", 10.5, 15.5, C["muted"]) - 12
    node(c, F.left, y, F.w, 84, "What am I worried about?", fill=C["tint"], lines=2, center=False)
    y -= 84
    arrow(c, F.cx, y - 2, F.cx, y - 20)
    y -= 22
    node(c, F.cx - 170, y, 340, 58, "Is this a real problem I can do something about?",
         "(Not a 'what if' or something out of my hands)", fill=C["lavender"])
    y -= 58
    lw = (F.w - 30) / 2
    lx, rx = F.left, F.left + lw + 30
    arrow(c, F.cx - 60, y - 2, lx + lw / 2, y - 30)
    arrow(c, F.cx + 60, y - 2, rx + lw / 2, y - 30)
    text(c, F.cx - 100, y - 16, "Yes", "Accent", 14, C["accent2"], "right")
    text(c, F.cx + 100, y - 16, "No", "Accent", 14, C["accent2"])
    y -= 34
    node(c, lx, y, lw, 100, "What's one thing I can do?", lines=3, center=False)
    node(c, rx, y, lw, 100, "Name it and let it pass",
         "Say to yourself: \"There's a what-if.\" You don't have to argue with it or solve it.")
    y -= 100
    arrow(c, lx + lw / 2, y - 2, lx + lw / 2, y - 20)
    arrow(c, rx + lw / 2, y - 2, rx + lw / 2, y - 20)
    y -= 22
    node(c, lx, y, lw, 96, "When will I do it?", "Do it now, or pick a time. Then let the rest go until then.",
         fill=C["mint"])
    node(c, rx, y, lw, 96, "Shift your attention",
         "Breathe, color, take a walk, or call someone. If it keeps coming back, save it for worry time.",
         fill=C["peach"])
    y -= 96
    arrow(c, lx + lw / 2, y - 2, F.cx - 30, y - 22)
    arrow(c, rx + lw / 2, y - 2, F.cx + 30, y - 22)
    y -= 24
    node(c, F.cx - 150, y, 300, 44, "Then do one kind thing for yourself.", fill=C["tint"])


def thought_record(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "Quick thought record")
    y = para(c, F.left, y, F.w, "Thoughts aren't facts. They're quick guesses your brain makes, often when "
             "you're tired or stressed. Writing one down helps you look at it from a little further away.",
             "Sans", 10.5, 15.5, C["muted"]) - 10

    def field(x, y, w, head, n, hint=None):
        label(c, x, y, head, 10.5, C["accent"])
        if hint:
            text(c, x + sw(head, "SansB", 10.5) + 8, y, hint, "Sans", 8.5, C["muted"])
        return rule_lines(c, x, y - 22, w, n, 22) - 28

    y = field(F.left, y, F.w, "What happened?", 2, "where, when, who")
    y = field(F.left, y, F.w, "What went through my mind?", 2)
    text(c, F.left, y, "How much I believe it", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 124, y - 2, 40, 1)
    text(c, F.left + 170, y, "/10", "Sans", 9, C["muted"])
    text(c, F.left + 230, y, "Feelings and body", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 330, y - 2, F.w - 330, 1)
    y -= 34
    hw = (F.w - 24) / 2
    yl = field(F.left, y, hw, "What supports the thought?", 4)
    field(F.left + hw + 24, y, hw, "What doesn't fit it?", 4)
    y = yl
    y = field(F.left, y, F.w, "A more balanced thought", 2, "what would I tell a friend?")
    text(c, F.left, y, "How much I believe the balanced thought", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 216, y - 2, 40, 1)
    text(c, F.left + 262, y, "/10", "Sans", 9, C["muted"])
    y -= 26
    text(c, F.left, y, "How I feel now", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 84, y - 2, F.w - 84, 1)


def coloring_page(J, c, F, which):
    kicker(c, F, "SOS toolkit  ·  color to calm")
    names = {"mandala": "Butterfly mandala", "geometric": "Geometric butterfly"}
    text(c, F.right, F.top - 6, names[which], "Accent", 13, C["accent"], "right")
    box = (F.left, F.bottom + 20, F.right, F.top - 26)
    if which == "mandala":
        designs.mandala(c, box, C["art"])
    else:
        designs.geometric_page(c, box, C["art"])
    text(c, F.cx, F.bottom + 4, "No rules. Any colors, any order, stop whenever you like.", "Sans", 8,
         C["muted"], "center")


def will_pass(J, c, F):
    kicker(c, F, "SOS toolkit")
    y = title(c, F, "This will pass", align="center", y=F.top - 44) - 8
    y = para(c, F.left + 40, y, F.w - 80, "Gentle words for the hard moments. Read them slowly, out loud if you can. "
             "Circle the ones that fit.", "Sans", 10.5, 15.5, C["muted"], "center") - 18
    for i, ph in enumerate(content.PASS_PHRASES):
        text(c, F.cx, y, ph, "Accent", 15.5, C["ink"], "center")
        y -= 20
        if i < len(content.PASS_PHRASES) - 1:
            c.setFillColor(C["lavender"] if i % 2 else C["mint"])
            c.circle(F.cx, y + 2, 2, stroke=0, fill=1)
            y -= 14
    y -= 16
    label(c, F.left, y, "My own words", 11, C["accent"])
    rule_lines(c, F.left, y - 26, F.w, 3, 24)
    small_fly(c, F.left + 40, F.top - 46, 22, 2, angle=-18)
    small_fly(c, F.right - 40, F.top - 46, 22, 0, angle=18)


# ==========================================================================
# section 3/4/5: daily, weekly, monthly
# ==========================================================================


def daily(J, c, F, d):
    kicker(c, F, f"Day {d} of {J.cfg['days']}")
    text(c, F.left, F.top - 44, f"Day {d}", "Accent", 30, C["accent"])
    text(c, F.left + 120, F.top - 40, "Date", "Sans", 9.5, C["muted"])
    rule_lines(c, F.left + 148, F.top - 42, 150, 1)
    small_fly(c, F.right - 34, F.top - 28, 24, d, angle=[-14, 10, -6, 16, 0][d % 5])
    y = F.top - 92
    label(c, F.left, y, "Today I felt", 10.5, C["accent"])
    y -= 30
    for lab, lo, hi in (("Anxiety", "calm", "very anxious"), ("Mood", "low", "great"),
                        ("Sleep last night", "poor", "great")):
        rating_row(c, F.left, y, F.w, lab, lo, hi, r=9, lab_w=118)
        y -= 40
    y -= 4
    label(c, F.left, y, "Three good things", 10.5, C["accent"])
    text(c, F.left + 118, y, "big or small", "Sans", 8.5, C["muted"])
    y -= 26
    for i in range(3):
        text(c, F.left, y + 1, f"{i + 1}.", "Sans", 9.5, C["muted"])
        rule_lines(c, F.left + 16, y - 1, F.w - 16, 1)
        y -= 25
    y -= 14
    # worry -> balanced thought
    bw = (F.w - 36) / 2
    bh = 108
    rbox(c, F.left, y + 4, bw, bh, 12)
    rbox(c, F.left + bw + 36, y + 4, bw, bh, 12, stroke=False, fill=C["tint"])
    text(c, F.left + 14, y - 14, "One worry", "SansB", 10.5, C["accent"])
    text(c, F.left + bw + 50, y - 14, "A more balanced thought", "SansB", 10.5, C["accent"])
    rule_lines(c, F.left + 14, y - 42, bw - 28, 3, 22)
    rule_lines(c, F.left + bw + 50, y - 42, bw - 28, 3, 22)
    arrow(c, F.left + bw + 8, y - bh / 2 + 4, F.left + bw + 28, y - bh / 2 + 4, C["accent"], 1.0, 6)
    y -= bh + 22
    label(c, F.left, y, "One small step for tomorrow", 10.5, C["accent"])
    rule_lines(c, F.left, y - 26, F.w, 2, 25)
    y -= 26 + 25 + 36
    label(c, F.left, y, "Today I", 10.5, C["accent"])
    habits = ["drank water", "moved my body", "got outside", "went easy on caffeine", "screens off before bed"]
    x = F.left + 62
    gap = (F.right - x) / len(habits)
    for h in habits:
        checkbox(c, x, y - 1.5, 10)
        para(c, x + 15, y, gap - 18, h, "Sans", 8.5, 10.5, C["ink"])
        x += gap
    # line of the day
    ly = F.bottom + 40
    line = content.DAILY_LINES[(d - 1) % len(content.DAILY_LINES)]
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.6)
    tw = sw(line, "Accent", 14)
    c.line(F.cx - tw / 2 - 60, ly + 4, F.cx - tw / 2 - 16, ly + 4)
    c.line(F.cx + tw / 2 + 16, ly + 4, F.cx + tw / 2 + 60, ly + 4)
    c.restoreState()
    text(c, F.cx, ly, line, "Accent", 14, C["ink"], "center")


def weekly_review(J, c, F, w, a, b):
    kicker(c, F, f"Week {w} check-in")
    y = title(c, F, f"Week {w} review", sub=f"Days {a} to {b}")
    small_fly(c, F.right - 30, F.top - 30, 26, w + 2, angle=-12)
    y -= 4
    text(c, F.left, y, "This week in one word", "Sans", 10, C["muted"])
    rule_lines(c, F.left + 124, y - 2, 140, 1)
    y -= 34
    rating_row(c, F.left, y, F.w, "Anxiety, most days", "calm", "very anxious", r=9, lab_w=118)
    y -= 42
    for head, hint, n in (("What helped", "people, tools, places, moments", 4),
                          ("What was hard", "", 4),
                          ("Patterns I noticed", "times of day, places, people, thoughts, sleep", 4),
                          ("One thing to try next week", "keep it small", 2)):
        label(c, F.left, y, head, 11, C["accent"])
        if hint:
            text(c, F.left + sw(head, "SansB", 11) + 10, y, hint, "Sans", 8.5, C["muted"])
        y = rule_lines(c, F.left, y - 26, F.w, n, 24) - 36


def handled_it(J, c, F, w, a, b):
    kicker(c, F, f"Week {w} check-in")
    y = title(c, F, "I handled it", sub="Moments I got through this week, even small ones. This is your proof.")
    cols = [("Day", 0.1), ("What happened", 0.34), ("What I did", 0.3), ("How it went", 0.26)]
    x = F.left
    xs = []
    for head, fr in cols:
        xs.append(x)
        text(c, x + 6, y, head, "SansB", 9.5, C["accent"])
        x += F.w * fr
    xs.append(F.right)
    y -= 10
    rows = 8
    rh = 50
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.6)
    for r in range(rows + 1):
        c.line(F.left, y - r * rh, F.right, y - r * rh)
    for xx in xs[1:-1]:
        c.line(xx, y, xx, y - rows * rh)
    c.restoreState()
    y -= rows * rh + 34
    label(c, F.left, y, "Something I'm proud of this week", 11, C["accent"])
    rule_lines(c, F.left, y - 26, F.w, 2, 24)


def reward_coloring(J, c, F, w):
    kicker(c, F, f"Week {w} reward")
    text(c, F.right, F.top - 6, designs.WEEKLY_TITLES[(w - 1) % 13], "Accent", 13, C["accent"], "right")
    box = (F.left, F.bottom + 22, F.right, F.top - 28)
    designs.WEEKLY[(w - 1) % 13](c, box, C["art"])
    text(c, F.cx, F.bottom + 4, f"You finished week {w}. Take your time with this one.", "Sans", 8,
         C["muted"], "center")


def mood_butterfly(J, c, F, m, a, b):
    kicker(c, F, f"Month {m}")
    y = title(c, F, "My mood butterfly", sub=f"Days {a} to {b}. Each evening, color the cell for that day "
              "in the color that matches your mood.")
    cells_box = (F.left, y - 410, F.right, y - 6)
    designs.mood_cells(c, cells_box, C["art"], C["muted"], a)
    y -= 440
    label(c, F.left, y, "My color key", 11, C["accent"])
    text(c, F.left + 92, y, "color each circle with the pencil you'll use for that mood", "Sans", 8.5, C["muted"])
    y -= 34
    moods = ["calm", "happy", "okay", "worried", "low", "tired", "", ""]
    cw = F.w / 4
    for i, md in enumerate(moods):
        x = F.left + (i % 4) * cw
        yy = y - (i // 4) * 40
        c.saveState()
        c.setStrokeColor(C["muted"])
        c.setLineWidth(0.8)
        c.circle(x + 12, yy + 4, 11, stroke=1, fill=0)
        c.restoreState()
        if md:
            text(c, x + 32, yy, md, "Accent", 14, C["ink"])
        else:
            rule_lines(c, x + 32, yy - 2, cw - 50, 1)


def habit_tracker(J, c, F, m, a, b):
    kicker(c, F, f"Month {m}")
    y = title(c, F, "Habit tracker", sub=f"Days {a} to {b}. Tick or color a square for each day you did it.")
    habits = ["Daily page", "Water", "Movement", "Time outside", "Easy on caffeine",
              "Screens off before bed", "Breathing practice", "", ""]
    lab_w = 112
    n = 30
    cell = (F.w - lab_w) / n
    y -= 4
    for i in range(n):
        text(c, F.left + lab_w + cell * (i + 0.5), y, str(a + i), "Sans", 5.8, C["muted"], "center")
    y -= 6
    rh = 24
    c.saveState()
    for r, h in enumerate(habits):
        yy = y - r * rh
        if h:
            text(c, F.left, yy - rh + 8, h, "Sans", 9.2)
        else:
            c.setStrokeColor(C["rule"])
            c.setLineWidth(0.6)
            c.line(F.left, yy - rh + 6, F.left + lab_w - 10, yy - rh + 6)
        for i in range(n):
            x = F.left + lab_w + i * cell
            c.setStrokeColor(C["rule"])
            c.setLineWidth(0.6)
            if r % 2 == 0:
                c.setFillColor(C["tint"])
                c.rect(x + 1, yy - rh + 3, cell - 2, rh - 6, stroke=1, fill=1)
            else:
                c.rect(x + 1, yy - rh + 3, cell - 2, rh - 6, stroke=1, fill=0)
    c.restoreState()
    y -= len(habits) * rh + 34
    for head, nl in (("What I noticed this month", 4), ("A habit I want to keep", 1), ("One to try next month", 1)):
        label(c, F.left, y, head, 11, C["accent"])
        y = rule_lines(c, F.left, y - 26, F.w, nl, 24) - 36


def compassion_letter(J, c, F, m):
    kicker(c, F, f"Month {m}")
    y = title(c, F, "A kind letter to myself")
    y = para(c, F.left, y, F.w - 60, content.COMPASSION_PROMPTS[(m - 1) % 3], "Sans", 10.5, 15.5, C["muted"]) - 12
    text(c, F.left, y - 8, "Dear me,", "Accent", 16, C["ink"])
    y = rule_lines(c, F.left, y - 40, F.w, 21, 26) - 34
    text(c, F.right, y, "With love,", "Accent", 15, C["ink"], "right")
    small_fly(c, F.right - 26, F.top - 26, 22, m + 3, angle=14)


# ==========================================================================
# section 6: building confidence
# ==========================================================================


def fear_ladder(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "My fear ladder")
    y = para(c, F.left, y, F.w, "Pick something anxiety makes you avoid. Break it into small steps, from "
             "a little uncomfortable at the bottom to the goal at the top. Then climb one rung at a time, "
             "staying with each step until it feels easier.", "Sans", 10.5, 15.5, C["muted"]) - 6
    para(c, F.left, y, F.w, "For bigger fears, work through this with a therapist.", "SansI", 10, 15, C["accent"])
    y -= 30
    text(c, F.left + 60, y, "My goal", "SansB", 11, C["accent"])
    rule_lines(c, F.left + 112, y - 2, F.w - 112, 1)
    y -= 20
    rungs = 8
    top = y - 10
    bottom = F.bottom + 40
    gap = (top - bottom) / rungs
    rx0, rx1 = F.left + 10, F.left + 46
    c.saveState()
    c.setStrokeColor(C["art"])
    c.setLineWidth(1.4)
    c.line(rx0, bottom - 10, rx0, top + 10)
    c.line(rx1, bottom - 10, rx1, top + 10)
    c.restoreState()
    text(c, F.right, top + 2, "Fear (0 to 10)", "Sans", 8, C["muted"], "right")
    for i in range(rungs):
        yy = top - gap * (i + 0.5)
        c.setStrokeColor(C["art"])
        c.setLineWidth(1.4)
        c.line(rx0, yy, rx1, yy)
        text(c, rx1 + 14, yy - 3.5, str(rungs - i), "SansB", 10, C["accent2"])
        rule_lines(c, rx1 + 34, yy - 5, F.w - 150, 1)
        c.setStrokeColor(C["muted"])
        c.setLineWidth(0.8)
        c.circle(F.right - 26, yy - 2, 12, stroke=1, fill=0)
    small_fly(c, (rx0 + rx1) / 2, top + 34, 16, 1)


def ladder_log(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "Fear ladder progress", sub="Each time you practice a step, jot it down. Fear usually drops the more you repeat it.")
    cols = [("Date", 0.12), ("Step I practiced", 0.36), ("Fear before", 0.13), ("Fear after", 0.13),
            ("What I noticed", 0.26)]
    x = F.left
    xs = []
    for head, fr in cols:
        xs.append(x)
        text(c, x + 5, y, head, "SansB", 9, C["accent"])
        x += F.w * fr
    xs.append(F.right)
    y -= 10
    rows, rh = 13, 42
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.6)
    for r in range(rows + 1):
        c.line(F.left, y - r * rh, F.right, y - r * rh)
    for xx in xs[1:-1]:
        c.line(xx, y, xx, y - rows * rh)
    c.restoreState()


def lift_menu(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "Things that lift me", align="center", y=F.top - 44)
    y = para(c, F.left + 40, y, F.w - 80, "A menu to order from when you're low or wound up. Fill it in on a good "
             "day, so it's ready on a hard one.", "Sans", 10.5, 15.5, C["muted"], "center") - 6
    rbox(c, F.left + 6, y, F.w - 12, y - F.bottom - 10, 16, stroke=C["lavender"], lw=1.2)
    y -= 30
    secs = [("Quick bites", "5 minutes or less", "e.g. a song I love, cold water on my face", 4),
            ("Mains", "15 to 30 minutes", "e.g. a walk, a shower, a show that makes me laugh", 4),
            ("Shared plates", "with other people", "e.g. call a friend, coffee with someone I love", 3),
            ("Specials", "when I have more time", "e.g. a day trip, a craft project", 3)]
    for i, (h, sub, ex, n) in enumerate(secs):
        text(c, F.cx, y, h, "Accent", 18, C["accent"], "center")
        text(c, F.cx, y - 15, sub + "  ·  " + ex, "Sans", 8.5, C["muted"], "center")
        y = rule_lines(c, F.left + 50, y - 40, F.w - 100, n, 22) - 30
        if i < 3:
            small_fly(c, F.cx, y + 12, 8, i, style="simple")
            y -= 12


def wind_down(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "Sleep wind-down")
    y = para(c, F.left, y, F.w, "A calm last hour helps your body get the message that it's time to rest. "
             "Tick the ones you want to try. You don't need all of them.", "Sans", 10.5, 15.5, C["muted"]) - 10
    items = content.WIND_DOWN
    half = (len(items) + 1) // 2
    cw = (F.w - 20) / 2
    y0 = y
    for i, it in enumerate(items):
        x = F.left + (0 if i < half else cw + 20)
        yy = y0 - (i % half) * 34
        checkbox(c, x, yy - 2, 11)
        para(c, x + 20, yy, cw - 24, it.format(pmr=J.pg('pmr')), "Sans", 10, 13)
    y = y0 - half * 34 - 14
    label(c, F.left, y, "Brain dump", 12, C["accent"])
    text(c, F.left + 82, y, "Empty your head onto the page so it doesn't keep you up. Lists, worries, "
         "reminders, anything.", "Sans", 8.5, C["muted"])
    rbox(c, F.left, y - 12, F.w, y - 12 - F.bottom - 10, 14, stroke=C["rule"])
    rule_lines(c, F.left + 18, y - 44, F.w - 36, int((y - 44 - F.bottom - 20) / 24) + 1, 24,
               color=HexColor("#E4E5EC"))


def values_page(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "What matters to me")
    y = para(c, F.left, y, F.w, "Anxiety tends to shrink life down to what feels safe. Values pull it back "
             "out toward what matters. Circle the words that feel true for you, and add your own.",
             "Sans", 10.5, 15.5, C["muted"]) - 16
    words = content.VALUES
    cols = 4
    cw = F.w / cols
    for i, wd in enumerate(words):
        x = F.left + (i % cols) * cw + cw / 2
        yy = y - (i // cols) * 34
        text(c, x, yy, wd, "Accent", 15, C["ink"], "center")
    y -= ((len(words) - 1) // cols) * 34 + 46
    label(c, F.left, y, "My top three", 11, C["accent"])
    y -= 30
    for i in range(3):
        badge(c, F.left + 10, y + 3, str(i + 1), C[["lavender", "mint", "peach"][i]], 10, 9)
        rule_lines(c, F.left + 30, y - 1, F.w * 0.5, 1)
        y -= 28
    y -= 16
    label(c, F.left, y, "One small way to live each of these this week", 11, C["accent"])
    y = rule_lines(c, F.left, y - 26, F.w, 3, 24) - 38
    label(c, F.left, y, "When anxiety says no, my values say", 11, C["accent"])
    rule_lines(c, F.left, y - 26, F.w, 2, 24)


def worry_time(J, c, F):
    kicker(c, F, "Building confidence")
    y = title(c, F, "Worry time")
    y = para(c, F.left, y, F.w, content.WORRY_TIME, "Sans", 10.5, 15.5, C["muted"]) - 8
    text(c, F.left, y, "My worry time", "SansB", 10.5, C["accent"])
    rule_lines(c, F.left + 92, y - 2, 120, 1)
    text(c, F.left + 230, y, "Where", "SansB", 10.5, C["accent"])
    rule_lines(c, F.left + 272, y - 2, F.w - 272, 1)
    y -= 30
    cols = [("Date", 0.12), ("The worry", 0.44), ("Saved for later?", 0.18), ("Did it still matter?", 0.26)]
    x = F.left
    xs = []
    for head, fr in cols:
        xs.append(x)
        text(c, x + 5, y, head, "SansB", 9, C["accent"])
        x += F.w * fr
    xs.append(F.right)
    y -= 10
    rh = 38
    rows = int((y - F.bottom - 10) / rh)
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.6)
    for r in range(rows + 1):
        c.line(F.left, y - r * rh, F.right, y - r * rh)
    for xx in xs[1:-1]:
        c.line(xx, y, xx, y - rows * rh)
    c.restoreState()


def expressive(J, c, F, k):
    kicker(c, F, "Building confidence  ·  open page")
    head, prompt = content.EXPRESSIVE[k]
    y = title(c, F, head)
    y = para(c, F.left, y, F.w - 40, prompt, "Sans", 10.5, 15.5, C["muted"]) - 18
    n = int((y - F.bottom - 10) / 26) + 1
    rule_lines(c, F.left, y, F.w, n, 26)
    small_fly(c, F.right - 24, F.top - 26, 20, k + 4, angle=12)


# ==========================================================================
# section 7: look back
# ==========================================================================


def ninety_check(J, c, F):
    kicker(c, F, "Look back")
    y = title(c, F, f"{J.cfg['days']}-day check")
    y = para(c, F.left, y, F.w, f"Rate how things feel now, then turn back to page {J.pg('start') + 2} and "
             "compare with where you started. Any change counts, even a small one.",
             "Sans", 10.5, 15.5, C["muted"]) - 26
    for lab, lo, hi in (("Anxiety", "calm", "very anxious"), ("Sleep", "poor", "great"), ("Mood", "low", "great")):
        rating_row(c, F.left, y, F.w, lab, lo, hi, r=10, lab_w=100)
        y -= 50
    y -= 4
    # compare table
    cols = ["", "Day 1", f"Day {J.cfg['days']}", "Change"]
    cw = [0.34, 0.22, 0.22, 0.22]
    x = F.left
    xs = []
    for h, fr in zip(cols, cw):
        xs.append(x)
        text(c, x + 6, y, h, "SansB", 9.5, C["accent"])
        x += F.w * fr
    y -= 8
    c.saveState()
    c.setStrokeColor(C["rule"])
    c.setLineWidth(0.6)
    for r, lab in enumerate(["Anxiety", "Sleep", "Mood"]):
        c.line(F.left, y - r * 28, F.right, y - r * 28)
        text(c, F.left + 6, y - r * 28 - 18, lab, "Sans", 10)
    c.line(F.left, y - 3 * 28, F.right, y - 3 * 28)
    c.restoreState()
    y -= 3 * 28 + 34
    for head, n in (("What feels different now", 3), ("What I can do now that felt hard before", 3),
                    ("What I'm still working on", 2)):
        label(c, F.left, y, head, 11, C["accent"])
        y = rule_lines(c, F.left, y - 26, F.w, n, 24) - 34


def what_worked(J, c, F):
    kicker(c, F, "Look back")
    y = title(c, F, "What worked best", sub="Color in the butterflies: one for okay, two for helpful, three for a keeper.")
    y -= 4
    for tool in content.TOOLS:
        text(c, F.left, y, tool, "Sans", 10.5)
        for k in range(3):
            c.saveState()
            c.setStrokeColor(C["muted"])
            art.draw_butterfly(c, F.left + 300 + k * 30, y + 4, 10, "simple", lw=0.5, ink=C["muted"],
                               antennae=0.8, segments=False)
            c.restoreState()
        rule_lines(c, F.left + 400, y - 2, F.w - 400, 1)
        y -= 30
    text(c, F.left + 400, y + 30 * len(content.TOOLS) + 14, "notes", "Sans", 8, C["muted"])
    y -= 10
    for head, n in (("My go-to plan for a hard moment", 3), ("Keep doing", 2)):
        label(c, F.left, y, head, 11, C["accent"])
        y = rule_lines(c, F.left, y - 26, F.w, n, 24) - 34


def future_letter(J, c, F):
    kicker(c, F, "Look back")
    y = title(c, F, "A letter to my future self")
    y = para(c, F.left, y, F.w - 40, "Write to yourself a year from now. What do you want to remember "
             "about these 90 days? What do you hope you're doing by then? What should future you keep "
             "in mind if anxiety gets loud again?", "Sans", 10.5, 15.5, C["muted"]) - 12
    text(c, F.left, y - 8, "Dear future me,", "Accent", 16, C["ink"])
    y = rule_lines(c, F.left, y - 40, F.w, 20, 26) - 34
    text(c, F.right - 150, y, "Date", "Sans", 9.5, C["muted"])
    rule_lines(c, F.right - 118, y - 2, 118, 1)
    small_fly(c, F.right - 26, F.top - 26, 22, 1, angle=14)


def keep_going(J, c, F):
    kicker(c, F, "Look back")
    y = title(c, F, "Keep going")
    y = para(c, F.left, y, F.w, content.KEEP_GOING, "Sans", 10.5, 16, after=10) - 18
    label(c, F.left, y, "Support and resources", 11.5, C["accent"])
    y -= 24
    for a, b in content.RESOURCES:
        text(c, F.left, y, a, "SansB", 10.5)
        y = para(c, F.left + 170, y, F.w - 170, b, "Sans", 10, 14) - 12
    y -= 10
    para(c, F.left, y, F.w, "Resources were checked when this journal was made. Numbers and websites can change.",
         "Sans", 8.5, 12, C["muted"])
    small_fly(c, F.cx, F.bottom + 40, 30, 0)


def back_page(J, c, F):
    small_fly(c, F.cx, PH / 2 + 40, 34, 1)
    text(c, F.cx, PH / 2 - 18, J.cfg["title"], "Accent", 22, C["accent"], "center")
    text(c, F.cx, PH / 2 - 50, "This journal supports, not replaces, care from a professional.",
         "Sans", 9.5, C["ink"], "center")
    text(c, F.cx, PH / 2 - 66, "In a crisis, call or text 988 (US). In an emergency, call 911.",
         "Sans", 8.5, C["muted"], "center")
    text(c, F.cx, PH / 2 - 80, "Outside the US, call your local emergency number or visit findahelpline.com.",
         "Sans", 8.5, C["muted"], "center")


# ==========================================================================


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--edition", choices=["personal", "generic", "both"], default="both")
    ap.add_argument("--name", default=CONFIG["name"])
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--size", choices=["letter", "a4"], default=CONFIG["page_size"])
    args = ap.parse_args()
    register_fonts()
    cfg = dict(CONFIG, name=args.name, page_size=args.size)
    eds = ["personal", "generic"] if args.edition == "both" else [args.edition]
    for ed in eds:
        generic = ed == "generic"
        fname = cfg["file_generic"] if generic else cfg["file_personal"].format(name=cfg["name"])
        path = os.path.join(args.out, fname)
        n = Journal(cfg, generic).build(path)
        print(f"{path}: {n} pages, {os.path.getsize(path) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
