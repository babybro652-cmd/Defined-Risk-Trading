#!/usr/bin/env python3
"""Build the 5 sell-ready products for one Calm Pages edition, plus the listing images.

    python3 build_products.py --theme petals      # -> editions/calm-petals/
    python3 build_products.py --theme nights
    python3 build_products.py --theme wings       # rebuilds Calm Wings exactly as before
    python3 build_products.py --all               # all three
    python3 build_products.py --theme petals --no-images

Products (generic edition only, no personal names), each in Letter + A4:
  1. 90-Day Anxiety Journal
  2. Bundle                  journal + coloring pack + mood tracker, one zip per paper size
  3. Coloring Pack           18 designs + cover
  4. SOS Calm-Down Kit       the SOS toolkit + cover
  5. Mood Tracker            12 undated months + year-in-color page
Each product also gets <Prefix>_How_To_Print.pdf (1 page).

Output: editions/<slug>/files/<n-product>/ (upload these) and editions/<slug>/images/<n-product>/
(5 listing images, 2000 x 2000). Listing copy is hand-written in editions/<slug>/listings.md.
"""
import argparse
import calendar
import os
import shutil
import sys
import zipfile

from reportlab.lib.colors import white
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_journal as bj  # noqa: E402
import themes  # noqa: E402
from build_journal import (C, content, label, kicker, para, rbox, rule_lines, small_fly, text, title,  # noqa: E402
                           badge, checkbox, tx)

SIZES = {"letter": "Letter", "a4": "A4"}

FOLDERS = {"journal": "1-journal", "bundle": "2-bundle", "coloring": "3-coloring-pack", "sos": "4-sos-kit",
           "mood": "5-mood-tracker"}


def products():
    """folder, file stem and listing name for each product of the active theme."""
    P = bj.T.file_prefix
    cn, mn = tx("coloring_name"), tx("mood_name")
    return {
        "journal": dict(folder=FOLDERS["journal"], stem=f"{P}_90Day_Journal", name="90-Day Anxiety Journal"),
        "bundle": dict(folder=FOLDERS["bundle"], stem=f"{P}_Bundle", name="Complete Bundle"),
        "coloring": dict(folder=FOLDERS["coloring"], stem=f"{P}_" + cn.replace(" ", "_"), name=cn),
        "sos": dict(folder=FOLDERS["sos"], stem=f"{P}_SOS_Calm_Down_Kit", name="SOS Calm-Down Kit"),
        "mood": dict(folder=FOLDERS["mood"], stem=f"{P}_" + mn.replace(" ", "_"), name=mn),
    }


def howto_name():
    return f"{bj.T.file_prefix}_How_To_Print.pdf"


MONTH_DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   # undated year: February keeps a leap day


# ==========================================================================
# shared pages for the stand-alone packs
# ==========================================================================


class Pack(bj.Journal):
    """A stand-alone printable built from a page list instead of the 90-day plan."""

    def __init__(self, cfg, subtitle, planner):
        super().__init__(cfg, generic=True)
        self._subtitle = subtitle
        self._planner = planner

    def plan(self):
        self._planner(self)

    def subtitle(self):
        return self._subtitle


def pack_back(J, c, F, product):
    small_fly(c, F.cx, bj.PH / 2 + 40, 34, 1)
    text(c, F.cx, bj.PH / 2 - 18, bj.T.title, "Accent", 22, C["accent"], "center")
    text(c, F.cx, bj.PH / 2 - 50, f"This {product} supports, not replaces, care from a professional.",
         "Sans", 9.5, C["ink"], "center")
    text(c, F.cx, bj.PH / 2 - 66, "In a crisis, call or text 988 (US). In an emergency, call 911.",
         "Sans", 8.5, C["muted"], "center")
    text(c, F.cx, bj.PH / 2 - 80, "Outside the US, call your local emergency number or visit findahelpline.com.",
         "Sans", 8.5, C["muted"], "center")


# ---------------------------------------------------------------- coloring

def pack_coloring(J, c, F, i, name, fn, kw):
    kicker(c, F, f"{bj.T.title} coloring  ·  {i} of {len(bj.T.coloring_pack)}")
    text(c, F.right, F.top - 6, name, "Accent", 13, C["accent"], "right")
    box = (F.left, F.bottom + 22, F.right, F.top - 28)
    fn(c, box, C["art"], **kw)
    text(c, F.cx, F.bottom + 4, "No rules. Any colors, any order, stop whenever you like.", "Sans", 8,
         C["muted"], "center")


def coloring_tips(J, c, F):
    kicker(c, F, "Before you color")
    y = title(c, F, "Color to calm")
    y = para(c, F.left, y, F.w, "Coloring gives busy hands and a busy mind one small, gentle thing to do. "
             "There's no right way to do it and nothing to finish. These ideas can help you settle in.",
             "Sans", 10.5, 15.5, C["muted"]) - 14
    tips = [
        ("Pick a few colors first", "Three to five colors you like together. Fewer choices means less to decide."),
        ("Start small", tx("coloring_tip_start")),
        ("Breathe with it", "Slow strokes, slow breaths. Try breathing out a little longer than you breathe in."),
        ("Let go of perfect", "Going outside the lines is fine. So is leaving a page half done."),
        ("Make it a ritual", "The same time, a warm drink, a favorite playlist. Your body learns the cue."),
    ]
    cols = ["lavender", "mint", "peach", "rose", "butter"]
    for i, (h, b) in enumerate(tips):
        badge(c, F.left + 16, y - 2, str(i + 1), C[cols[i]], 15, 12)
        label(c, F.left + 44, y + 2, h, 11.5, C["ink"])
        y = para(c, F.left + 44, y - 16, F.w - 44, b, "Sans", 10.5, 15) - 20
    y -= 6
    label(c, F.left, y, "Paper and pencils", 11.5, C["accent"])
    y = para(c, F.left, y - 22, F.w, "Print the coloring pages on one side only, so color doesn't show "
             "through. Heavier paper (32 lb / 120 gsm or cardstock) feels nicer and takes more layers. Colored "
             "pencils work best; markers may bleed on thin paper, so slip a spare sheet underneath.",
             "Sans", 10.5, 15.5) - 20
    label(c, F.left, y, "My favorite color combinations", 11.5, C["accent"])
    y -= 30
    for r in range(3):
        for k in range(5):
            c.saveState()
            c.setStrokeColor(C["muted"])
            c.setLineWidth(0.8)
            c.circle(F.left + 14 + k * 30, y + 4, 11, stroke=1, fill=0)
            c.restoreState()
        rule_lines(c, F.left + 170, y, F.w - 170, 1)
        y -= 34
    small_fly(c, F.right - 26, F.top - 26, 22, 3, angle=14)


def plan_coloring(P):
    P.add(bj.cover, dict(subtitle=tx("coloring_name"), belongs=None, **bj.T.pack_covers["coloring"]),
          footer=False)
    P.add(bj.about_page, "coloring pack")
    P.add(coloring_tips)
    for i, (name, fn, kw) in enumerate(bj.T.coloring_pack, 1):
        P.add(pack_coloring, i, name, fn, kw)
    P.add(pack_back, "coloring pack")


# ---------------------------------------------------------------- SOS kit


def sos_count():
    return 10 + len(bj.T.extra_sos)


def plan_sos(P):
    P.add(bj.cover, dict(subtitle="SOS Calm-Down Kit", tagline=f"{sos_count()} pages for the hard moments",
                         belongs=None, **bj.T.pack_covers["sos"]), footer=False)
    P.add(bj.about_page, "toolkit")
    P.mark("sos")
    P.add(bj.sos_flow)
    for key, fn in (("box", bj.box_breathing), ("exhale", bj.long_exhale), ("ground", bj.grounding),
                    ("pmr", bj.pmr), ("tree", bj.worry_tree), ("thought", bj.thought_record)):
        P.mark(key)
        P.add(fn)
    P.mark("color")
    P.add(bj.coloring_page, "mandala")
    P.add(bj.coloring_page, "geometric")
    P.mark("phrases")
    P.add(bj.will_pass)
    for name in bj.T.extra_sos:
        P.mark(name)
        P.add(bj.PAGES[name])
    P.add(bj.more_help, "toolkit", "SOS toolkit")
    P.add(pack_back, "toolkit")


# ---------------------------------------------------------------- mood tracker

MOODS = ["calm", "happy", "okay", "worried", "low", "tired", "", ""]


def color_key(c, F, y, size=14):
    cw = F.w / 4
    for i, md in enumerate(MOODS):
        x = F.left + (i % 4) * cw
        yy = y - (i // 4) * 40
        c.saveState()
        c.setStrokeColor(C["muted"])
        c.setLineWidth(0.8)
        c.circle(x + 12, yy + 4, 11, stroke=1, fill=0)
        c.restoreState()
        if md:
            text(c, x + 32, yy, md, "Accent", size, C["ink"])
        else:
            rule_lines(c, x + 32, yy - 2, cw - 50, 1)
    return y - 80


def mood_howto(J, c, F):
    kicker(c, F, tx("mood_kicker"))
    y = title(c, F, "How it works")
    y = para(c, F.left, y, F.w, tx("mood_how"),
             "Sans", 10.5, 15.5, C["muted"]) - 16
    steps = [
        ("Choose your colors", "Pick a pencil for each mood and color its circle in the key below. Use the "
         "same key all year, and add your own moods on the blank lines."),
        ("Color one cell each evening", tx("mood_find")),
        ("Write a line if you like", "The notes at the bottom of each month are for anything you noticed: "
         "sleep, people, busy weeks, good surprises."),
        ("Look back", "At the end of the month, and again on the Year in color page, look for patterns. "
         "No judging, just noticing."),
    ]
    cols = ["lavender", "mint", "peach", "rose"]
    for i, (h, b) in enumerate(steps):
        badge(c, F.left + 16, y - 2, str(i + 1), C[cols[i]], 15, 12)
        label(c, F.left + 44, y + 2, h, 11.5, C["ink"])
        y = para(c, F.left + 44, y - 16, F.w - 44, b, "Sans", 10.5, 15) - 20
    y -= 8
    label(c, F.left, y, "My color key", 11.5, C["accent"])
    y = color_key(c, F, y - 34) - 10
    para(c, F.left, y, F.w, "The months are undated, so you can start any month of any year. February has a "
         "29th cell for leap years; skip it in other years.", "Sans", 9.5, 14, C["muted"])
    small_fly(c, F.right - 26, F.top - 26, 22, 4, angle=14)


def mood_month(J, c, F, m):
    name = calendar.month_name[m]
    n = MONTH_DAYS[m - 1]
    kicker(c, F, f"{tx('mood_month_kicker')}  ·  month {m} of 12")
    text(c, F.left, F.top - 40, name, "Accent", 30, C["accent"])
    text(c, F.right - 150, F.top - 38, "Year", "Sans", 9.5, C["muted"])
    rule_lines(c, F.right - 122, F.top - 40, 122, 1)
    sub = "Each evening, color the cell for that day in the color that matches your mood."
    if m == 2:
        sub += " Cell 29 is for leap years."
    y = para(c, F.left, F.top - 64, F.w, sub, "Sans", 10, 14, C["muted"]) - 6
    extra = bj.PH - letter[1]          # A4 has a little more height: give it to the butterfly
    bh = 405 + extra * 0.8
    cells_box = (F.left, y - bh, F.right, y - 4)
    bj.T.mood_cells(c, cells_box, C["art"], C["muted"], 1, n)
    y -= bh + 36
    label(c, F.left, y, "Color key", 11, C["accent"])
    text(c, F.left + 66, y, "use the same pencils as your key page", "Sans", 8.5, C["muted"])
    y = color_key(c, F, y - 30, 13) + 4
    label(c, F.left, y, "This month I noticed", 11, C["accent"])
    rule_lines(c, F.left, y - 24, F.w, 2, 22)


def year_in_color(J, c, F):
    kicker(c, F, tx("mood_kicker"))
    y = title(c, F, "My year in color", sub="Copy each day's color here to see the whole year at a glance.")
    text(c, F.right - 150, F.top - 38, "Year", "Sans", 9.5, C["muted"])
    rule_lines(c, F.right - 122, F.top - 40, 122, 1)
    lab_w = 26
    cw = (F.w - lab_w) / 12
    bottom = F.bottom + 40
    rh = min(17.0, (y - 18 - bottom) / 31)
    for m in range(12):
        text(c, F.left + lab_w + cw * (m + 0.5), y, calendar.month_abbr[m + 1], "SansB", 8.5, C["accent"], "center")
    y -= 8
    c.saveState()
    c.setLineWidth(0.6)
    for d in range(31):
        yy = y - d * rh
        text(c, F.left + lab_w - 8, yy - rh + 5, str(d + 1), "Sans", 7.5, C["muted"], "right")
        for m in range(12):
            x = F.left + lab_w + m * cw
            c.setStrokeColor(C["rule"])
            if d + 1 > MONTH_DAYS[m]:
                c.setFillColor(C["tint"])
                c.rect(x + 1.5, yy - rh + 1.5, cw - 3, rh - 3, stroke=0, fill=1)
            else:
                c.rect(x + 1.5, yy - rh + 1.5, cw - 3, rh - 3, stroke=1, fill=0)
    c.restoreState()
    y -= 31 * rh + 22
    text(c, F.left, y, "Shaded squares are days that month doesn't have. Feb 29 is for leap years.",
         "Sans", 8.5, C["muted"])


def plan_mood(P):
    P.add(bj.cover, dict(subtitle=tx("mood_name"), tagline=tx("mood_tagline"), belongs="This tracker belongs to",
                         **bj.T.pack_covers["mood"]), footer=False)
    P.add(bj.about_page, "mood tracker")
    P.add(mood_howto)
    for m in range(1, 13):
        P.add(mood_month, m)
    P.add(year_in_color)
    P.add(pack_back, "tracker")


# ==========================================================================
# how to print (1 page)
# ==========================================================================

def howto_info(key):
    return {
        "journal": dict(what="90-Day Anxiety Journal", duplex=True,
                        extra=f"Print as you go: Start Here and the SOS Toolkit first (pages 1 to {8 + sos_count()}), "
                              "then a week or a month of daily pages at a time."),
        "bundle": dict(what="Complete Bundle", duplex=True,
                       extra="Unzip the download first (on a phone: tap the file; on a computer: double-click). "
                             "Print the journal double-sided, and the coloring pack and tracker on one side."),
        "coloring": dict(what=tx("coloring_name"), duplex=False,
                         extra="Print one side only so color doesn't show through. Cardstock or 32 lb / 120 gsm "
                               "paper takes layers of colored pencil best."),
        "sos": dict(what="SOS Calm-Down Kit", duplex=True,
                    extra="Keep a copy where hard moments happen: by your bed, in your bag, or in a desk drawer. "
                          "A clear sheet protector lets you trace the breathing pages again and again."),
        "mood": dict(what=tx("mood_name"), duplex=False,
                     extra="Print one month at a time, or all 12 at once and keep them in a folder or on the "
                           "fridge. Single-sided works best for coloring."),
    }[key]


def how_to_print(path, key):
    info = howto_info(key)
    T = bj.T
    bj.set_page_size("letter")
    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle(f"How to print: {T.title} {info['what']}")
    c.setAuthor(getattr(T, "author", T.title))
    F = bj.Frame(1, dict(bj.CONFIG, duplex=False))
    kicker(c, F, f"{T.title}  ·  {info['what']}")
    y = title(c, F, "How to print")
    small_fly(c, F.right - 26, F.top - 26, 24, 1, angle=14)
    y = para(c, F.left, y, F.w, "Thank you for your order. Here's how to get the best prints at home or at "
             "a print shop.", "Sans", 10.5, 15.5, C["muted"]) - 12

    def section(y, head, lines, fill):
        h = 22 + sum(len(bj.wrap(s, "Sans", 10, F.w - 52)) * 14 + 4 for s in lines) + 10
        rbox(c, F.left, y + 4, F.w, h, 12, stroke=False, fill=fill)
        label(c, F.left + 16, y - 14, head, 11, C["accent"])
        yy = y - 32
        for s in lines:
            c.setFillColor(C["accent"])
            c.circle(F.left + 22, yy + 3.5, 1.8, stroke=0, fill=1)
            yy = para(c, F.left + 32, yy, F.w - 52, s, "Sans", 10, 14) - 4
        return y - h - 10

    y = section(y, "1. Pick your file", [
        "Letter: US, Canada, Mexico.  A4: UK, Europe, Australia and most other countries.",
        "Open the PDF in Adobe Acrobat Reader (free) for the cleanest print. Browser previews can shrink pages.",
    ], C["tint"])
    y = section(y, "2. Print at home", [
        "Set Scale to \"Actual size\" or 100%. If your printer cuts off an edge, choose \"Fit\" instead.",
        "Paper: 24 lb / 90 gsm or heavier feels nicer to write on. Black-and-white printing works too; the "
        "pages are mostly line art and use little ink.",
        info["extra"],
    ], C["mint"])
    if info["duplex"]:
        dlines = [
            "Printer with two-sided printing: choose \"Print on both sides\" and \"Flip on long edge\".",
            "No two-sided option: print odd pages, put the stack back in (try 4 pages first to check which way "
            "it faces), then print even pages.",
            "The inner margin alternates left and right, so pages line up for a binder or spiral binding.",
        ]
    else:
        dlines = [
            "This set is made for one side of the paper, so color won't show through.",
            "Want to save paper? Print the instructions pages double-sided and the coloring pages single-sided.",
        ]
    y = section(y, "3. Double-sided printing", dlines, C["lavender"])
    y = section(y, "4. Print-shop tip", [
        "Email or bring the PDF to a local print or office shop, or your library. Ask for: \"Actual size, "
        + ("double-sided, " if info["duplex"] else "single-sided, ")
        + "24 or 32 lb paper, coil binding on the left edge.\" A printed copy of the license below answers any "
        "copyright questions.",
    ], C["peach"])
    y = section(y, "5. Personal-use license", [
        "You may print as many copies as you need for yourself and your household.",
        "Please don't share, resell, or upload the files, or sell printed copies. For a group, class, or "
        "clients, message the shop first.",
    ], C["rose"])
    y -= 6
    where = f"through {T.store}" if T.store else "through the shop"
    para(c, F.left, y, F.w, f"Trouble with a file? Message us {where} and we'll help. {T.title} supports, "
         "not replaces, professional care. In a crisis in the US, call or text 988.", "Sans", 9, 13, C["muted"],
         "center")
    if T.brand_mark:
        bj.brand_mark(c, F.cx, F.bottom - 14)
    c.showPage()
    c.save()


# ==========================================================================
# build all
# ==========================================================================


def build_pdf(kind, size, path):
    cfg = dict(bj.CONFIG, page_size=size)
    if kind == "journal":
        doc = bj.Journal(cfg, generic=True)
    elif kind == "coloring":
        doc = Pack(dict(cfg, duplex=False), tx("coloring_name"), plan_coloring)
    elif kind == "sos":
        doc = Pack(cfg, "SOS Calm-Down Kit", plan_sos)
    elif kind == "mood":
        doc = Pack(dict(cfg, duplex=False), tx("mood_name"), plan_mood)
    n = doc.build(path)
    return n


def build_all(theme, out=None, images=True):
    T = bj.set_theme(theme)
    out = out or os.path.join(HERE, "editions", T.slug)
    bj.register_fonts()
    PRODUCTS = products()
    HOWTO = howto_name()
    report = []
    built = {}
    for kind in ("journal", "coloring", "sos", "mood"):
        p = PRODUCTS[kind]
        fdir = os.path.join(out, "files", p["folder"])
        os.makedirs(fdir, exist_ok=True)
        for size, tag in SIZES.items():
            path = os.path.join(fdir, f"{p['stem']}_{tag}.pdf")
            n = build_pdf(kind, size, path)
            built[(kind, size)] = (path, n)
            report.append((path, n))
        how = os.path.join(fdir, HOWTO)
        how_to_print(how, kind)
        report.append((how, 1))
    # bundle: one zip per paper size
    p = PRODUCTS["bundle"]
    fdir = os.path.join(out, "files", p["folder"])
    os.makedirs(fdir, exist_ok=True)
    how = os.path.join(fdir, HOWTO)
    how_to_print(how, "bundle")
    for size, tag in SIZES.items():
        zpath = os.path.join(fdir, f"{p['stem']}_{tag}.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for kind in ("journal", "coloring", "mood"):
                src, _ = built[(kind, size)]
                z.write(src, os.path.basename(src))
            z.write(how, HOWTO)
        report.append((zpath, None))
    os.remove(how)   # it lives inside each zip
    for path, n in report:
        mb = os.path.getsize(path) / 1e6
        flag = "  OVER 20 MB!" if mb >= 20 else ""
        print(f"{os.path.relpath(path, out)}: {str(n) + ' pages, ' if n else ''}{mb:.2f} MB{flag}")
    if images:
        import mockups
        mockups.build_images(out, built)
    return built


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", choices=themes.KEYS, default=bj.CONFIG["theme"])
    ap.add_argument("--all", action="store_true", help="build every edition")
    ap.add_argument("--out", default=None, help="default: editions/<edition slug>/")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    for key in (themes.KEYS if a.all else [a.theme]):
        build_all(key, None if a.all else a.out, images=not a.no_images)


if __name__ == "__main__":
    main()
