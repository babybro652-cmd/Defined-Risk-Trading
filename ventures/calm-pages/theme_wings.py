"""Calm Wings: the butterfly edition (the original, 10/2).

Art: butterfly_art.py (vector butterfly engine) and designs.py (coloring pages).
This module must keep rebuilding the Calm Wings files exactly as they were, so the
values below are the original ones; change them only on purpose.
"""
import math

from reportlab.lib.colors import white

import build_journal as bj
import butterfly_art as art
import designs
from themes import Theme, colors

PALETTE = {
    "ink": "#3E4050",      # body text
    "muted": "#8A8DA0",    # small labels
    "rule": "#C9CBD7",     # writing lines
    "art": "#4B4D60",      # line art
    "accent": "#7E6BB5",   # headings (soft violet)
    "accent2": "#5E9F98",  # kickers (sea green)
    # pastel slots (every theme fills the same six names with its own soft colors)
    "lavender": "#E7DFF5",
    "mint": "#D7EEEA",
    "peach": "#FBE2D3",
    "rose": "#F8DCE5",
    "butter": "#FBF0CF",
    "sage": "#E0EDD9",
    "tint": "#F6F3FB",     # faintest panel tint
}
C = colors(PALETTE)

# listing-image colors (RGB)
IMG = {
    "bg_top": (248, 245, 252), "bg_bot": (236, 229, 247), "ink": (62, 64, 80), "muted": (122, 125, 146),
    "accent": (126, 107, 181), "accent2": (78, 140, 133), "lav": (231, 223, 245), "mint": (215, 238, 234),
    "peach": (251, 226, 211), "rose": (248, 220, 229), "butter": (251, 240, 207), "white": (255, 255, 255),
    "border": (226, 222, 236), "shadow": (70, 55, 110), "band": (126, 107, 181), "band_text": (231, 223, 245),
}


# --------------------------------------------------------------------------
# art hooks
# --------------------------------------------------------------------------


def accent(c, x, y, size, k=0, angle=0.0, style=None):
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


def cover_art(c, cx, o):
    small_fly = bj.small_fly
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


def lifecycle(c, F, y):
    text, arrow = bj.text, bj.arrow
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
    accent(c, xs[3], y + 10, 26, 0)
    labels = ["begin", "grow", "rest and change", "fly"]
    for i, x in enumerate(xs):
        text(c, x, y - 34, labels[i], "Accent", 12, C["ink"], "center")
        if i < 3:
            arrow(c, x + 38, y + 10, xs[i + 1] - 38, y + 10, C["rule"], 0.9, 5)


def exhale(cx, cy, size):
    """Two mirrored wings to trace. Returns [(page points, cumulative length, split length)]."""
    w = art.Wing((0.0, 0.0), 86, -96, [0, 0.72, 0.98, 1.0, 0.82, 0.62, 0.7, 0.72, 0.6, 0.0])
    pts = w.outline(n=600)
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
    split = 0.4 * L[-1]
    out = []
    for mirror in (False, True):
        tf = art.Tf(cx, cy, size, 0, mirror)
        out.append(([tf(p) for p in pts], L, split))
    return out


def exhale_center(c, cx, cy, size):
    art.draw_body(c, art.Tf(cx, cy + 4, size * 0.42), 0.9, C["art"], antennae=0.7)
    c.setFillColor(C["accent"])
    c.circle(cx, cy + 1, 4, stroke=0, fill=1)


def rating_icon(c, x, y):
    art.draw_butterfly(c, x, y, 10, "simple", lw=0.5, ink=C["muted"], antennae=0.8, segments=False)


def image_art(c, style, fills, angle, lineart, px):
    """One accent for the listing images, drawn at (200, 200) on a 400 pt canvas."""
    fl = None if lineart else tuple(C[k] for k in fills)
    art.draw_butterfly(c, 200, 200, 150, style, angle=angle, lw=2.2 if px > 300 else 3.0, ink=C["art"],
                       fills=fl, body_fill=white)


COLORING = [
    ("Butterfly mandala", designs.mandala, {}),
    ("Geometric butterfly", designs.geometric_page, {}),
] + [(t, fn, {}) for t, fn in zip(designs.WEEKLY_TITLES[:12], designs.WEEKLY[:12])] + [
    ("Free to fly", designs.wk_finale, {"label": "free to fly"}),
    ("Butterfly sampler", designs.sampler, {}),
    ("Monarch meadow", designs.monarch_meadow, {}),
    ("Ten-wing mandala", designs.mandala, {"n": 10}),
]

TXT = {
    "tagline": "breathe  ·  notice  ·  grow",
    "key_weekly": "Look back on the week, log what you handled, then color your reward butterfly.",
    "key_monthly": "Color your mood butterfly, track habits, and write yourself a kind letter.",
    "key_confidence": "Tools for facing fears a little at a time, sleep, values, and worry time.",
    "exhale_intro": "A longer out-breath tells your body it's safe to slow down. Breathe in for 4, "
                    "out for 6. Trace each wing: in as you travel up and out, out as you glide back around "
                    "to the body.",
    "exhale_outro": "Do one wing, then the other. Five rounds is plenty. If 4 and 6 feel too long, "
                    "try 3 and 5. What matters is that the out-breath is longer than the in-breath.",
    "mood_title": "My mood butterfly",
    "worked_sub": "Color in the butterflies: one for okay, two for helpful, three for a keeper.",
    # stand-alone products
    "coloring_name": "Butterfly Coloring Pack",
    "coloring_tip_start": "Color one wing, or one section, then check in with how you feel.",
    "mood_name": "Mood Butterfly Tracker",
    "mood_kicker": "Mood butterfly tracker",
    "mood_month_kicker": "Mood butterfly",
    "mood_how": "One butterfly a month, one wing cell a day. By the end of the month you have "
                "a picture of how the weeks really felt, which is often kinder than memory.",
    "mood_find": "Find today's number on the butterfly and color it in the mood that "
                 "fits the day best. Mixed day? Split the cell, or use two colors.",
    "mood_tagline": "12 months  ·  one wing a day",
    "sos_extra_line": "",
}

PACK_COVERS = {
    "coloring": dict(tagline="18 calming designs to color", style="peacock", lineart=True),
    "sos": dict(style="round", fills=("rose", "lavender", "mint")),
    "mood": dict(style="petal", fills=("butter", "rose", "lavender")),
}

# listing-image wording and page picks (see mockups.product_specs)
MOCK = {
    "accents": [("simple", ("lavender", "mint", "peach")), ("round", ("rose", "lavender", "mint")),
                ("petal", ("butter", "peach", "lavender"))],
    "corner": ("classic", ("lavender", "mint", "peach")),
    "list_icons": [("classic", ("lavender", "mint", "peach")), ("round", ("rose", "lavender", "mint")),
                   ("petal", ("butter", "peach", "lavender")), ("simple", ("mint", "peach", "lavender"))],
    "journal_spread_sub": "Daily pages, SOS tools, weekly rewards",
    "journal_weekly": ("13 weekly check-ins", "Review, \"I handled it\" log, reward coloring page"),
    "journal_monthly": ("3 monthly sections", "Mood butterfly, habit tracker, kind letter"),
    "journal_sos": ("SOS Toolkit, 10 pages", "Breathing, grounding, worry tree, thought record"),
    "journal_more": ("Start Here + Look Back", "Plus Building Confidence tools: 18 more guided pages"),
    "bundle_coloring": "18 original designs plus coloring tips",
    "bundle_mood": "12 undated months plus a year-in-color page",
    "bundle_inside_mood": "Mood butterfly",
    "coloring_band": "18 butterfly designs to color and unwind",
    "coloring_spread_sub": "18 original butterfly designs",
    "coloring_spread": [8, 11, 4, 19, 16],
    "coloring_inside": [(4, "Butterfly mandala"), (10, "Garden frame"), (20, "Monarch meadow"), (16, "Night flight")],
    "coloring_thumbs": [13, 5],
    "coloring_list": "Mandalas, gardens, wreaths, geometric and night scenes",
    "bundle_spread_cp": (9, 4),
    "bundle_inside_cp": 6,
    "sos_count": "10",
    "sos_included": [("Start-here SOS flow", "Breathe, ground, color or move, write"),
                     ("Two breathing guides", "Trace-along box breathing and long-exhale wings"),
                     ("Grounding, muscle relaxation", "5-4-3-2-1 and an 8-step body scan"),
                     ("Worry tree and thought record", "Sort a worry and find a more balanced thought"),
                     ("2 coloring pages + calming phrases", "Plus a when-to-get-more-help page with 988")],
    "mood_band": "Color one wing a day. See your year in color.",
    "mood_inside": "Monthly butterfly",
    "mood_included": ("12 monthly mood butterflies", "January to December, undated, 28 to 31 day cells"),
    "buy_step": "Check out securely. No physical item is shipped.",
    "dl_step": "Download your PDFs from the link on your order page or in your email.",
    "dl_step_bundle": "Download the zip for your paper size from your order link, then unzip it.",
}

THEME = Theme(
    key="wings", slug="calm-wings", title="Calm Wings", subtitle="A 90-Day Anxiety Journal",
    file_prefix="CalmWings", file_generic="Calm_Wings_90_Day_Anxiety_Journal.pdf",
    file_personal="Calm_Wings_{name}.pdf", author="Calm Wings",
    palette=PALETTE, img=IMG, store=None, brand_mark=True,
    cover_defaults=dict(style="classic", fills=("lavender", "mint", "peach")),
    accent=accent, cover_art=cover_art, lifecycle=lifecycle, exhale=exhale, exhale_center=exhale_center,
    sos_coloring={"mandala": ("Butterfly mandala", designs.mandala),
                  "geometric": ("Geometric butterfly", designs.geometric_page)},
    weekly=designs.WEEKLY, weekly_titles=designs.WEEKLY_TITLES, mood_cells=designs.mood_cells,
    rating_icon=rating_icon, coloring_pack=COLORING, pack_covers=PACK_COVERS, image_art=image_art,
    txt=TXT, content={}, mock=MOCK,
)
