"""Calm Petals: the botanical edition.

Soft sage, eucalyptus and blush. Pressed-flower line art from botanical_art.py; coloring
pages and the mood flower from botanical_designs.py.
"""
import math

import botanical_art as ba
import botanical_designs as bd
import build_journal as bj
from themes import Theme, colors

PALETTE = {
    "ink": "#3B4641",      # body text (deep green-gray)
    "muted": "#87928B",    # small labels
    "rule": "#C9D2CB",     # writing lines
    "art": "#45514A",      # line art
    "accent": "#587D69",   # headings (deep sage)
    "accent2": "#B26F6C",  # kickers (dusty blush)
    # pastel slots
    "lavender": "#F5DEDA",  # blush
    "mint": "#D6E6E1",      # eucalyptus
    "peach": "#FAE3D3",     # apricot
    "rose": "#F2D7DC",      # rose
    "butter": "#F7EED3",    # cream
    "sage": "#DEE9D5",      # sage
    "tint": "#F4F7F1",      # faintest panel tint
}
C = colors(PALETTE)

IMG = {
    "bg_top": (250, 249, 244), "bg_bot": (232, 240, 230), "ink": (59, 70, 65), "muted": (118, 130, 122),
    "accent": (88, 125, 105), "accent2": (178, 111, 108), "lav": (245, 222, 218), "mint": (214, 230, 225),
    "peach": (250, 227, 211), "rose": (242, 215, 220), "butter": (247, 238, 211), "white": (255, 255, 255),
    "border": (221, 229, 220), "shadow": (45, 70, 55), "band": (88, 125, 105), "band_text": (214, 230, 220),
}

FILLS = (C["sage"], C["mint"], C["lavender"], C["peach"], C["butter"])


# --------------------------------------------------------------------------
# art hooks
# --------------------------------------------------------------------------


def accent(c, x, y, size, k=0, angle=0.0, style=None):
    """A small pastel botanical accent (sprig, bud, cosmos, eucalyptus...)."""
    if style == "simple":
        k = 4
    ba.accent(c, x, y, size, k, angle, C["art"], FILLS)


def cover_art(c, cx, o):
    line = o["lineart"]
    fl = (lambda k: None) if line else (lambda k: C[k])
    c.saveState()
    c.setFillColor(C["tint"])
    c.circle(cx, 500, 188, stroke=0, fill=1)
    c.setStrokeColor(C["sage"] if not line else C["rule"])
    c.setLineWidth(0.8)
    c.setDash(1, 4)
    c.circle(cx, 500, 206, stroke=1, fill=0)
    c.restoreState()
    f1, f2, f3 = o["fills"]
    lw = 1.1 if line else 1.0
    if o["style"] == "bouquet":
        ba.bouquet(c, cx, 505, 182, C["art"], (fl("sage"), fl("mint"), fl(f1), fl(f2), fl(f3), fl(f1)), lw)
    elif o["style"] == "wreath":
        ba.wreath(c, cx, 500, 150, C["art"], (fl("sage"), fl("mint"), None, None, None), lw, density=1.4,
                  scale=1.4)
        for a, kind in ((270, "cosmos"), (205, "rose"), (335, "rose"), (150, "rosette"), (30, "rosette"),
                        (90, "bud")):
            x, y = cx + 150 * math.cos(math.radians(a)), 500 + 150 * math.sin(math.radians(a))
            if kind == "cosmos":
                ba.cosmos(c, x, y, 40, 8, 10, C["art"], lw, fl(f1), fl(f3))
            elif kind == "rose":
                ba.wild_rose(c, x, y, 28, a, C["art"], lw, fl(f2), fl(f3))
            elif kind == "rosette":
                ba.rosette(c, x, y, 24, 3, a, C["art"], lw, fl(f1), fl(f2))
            else:
                ba.bud(c, x - 10, y, 22, 112, C["art"], lw, fl(f2), fl("sage"))
                ba.bud(c, x + 10, y, 22, 68, C["art"], lw, fl(f1), fl("sage"))
        pts = ba.curve(cx - 4, 400, 165, 88, 0.1, 50)
        P = ba.Path(pts)
        for t, sd in ((0.3, 1), (0.5, -1)):
            px, py, a = P.at(t)
            ba.leaf(c, px, py, 48, a + 46 * sd, 0.3, "lance", -0.06 * sd, 3, lw, C["art"], fl("sage"))
        ba.stroke(c, pts, C["art"], lw)
        ex, ey, a = P.at(1.0)
        ba.wild_rose(c, ex, ey, 40, 14, C["art"], lw, fl(f1), fl(f3))
    else:   # "bloom": one big flower with leaves (mood tracker)
        for sd in (1, -1):
            ba.leaf(c, cx + sd * 40, 430, 120, -90 + sd * 60, 0.3, "lance", -0.08 * sd, 4, lw, C["art"], fl("sage"))
            ba.leaf(c, cx + sd * 20, 470, 110, 90 + sd * 50, 0.28, "lance", 0.08 * sd, 4, lw, C["art"], fl("mint"))
        ba.cosmos(c, cx, 505, 128, 10, 0, C["art"], lw, fl(f1), fl(f3))
        for k in range(10):
            a = math.radians(90 - 36 * k)
            if k % 2:
                ba.forget_me_not(c, cx + 150 * math.cos(a), 505 + 150 * math.sin(a), 11, k * 15, C["art"], lw * 0.8,
                                 fl(f2), fl(f3))
    # a few pressed accents around the halo
    if not line:
        accent(c, cx - 224, 440, 30, 0, -14)
        accent(c, cx + 222, 330, 26, 3, 12)


def lifecycle(c, F, y):
    text, arrow = bj.text, bj.arrow
    xs = [F.left + F.w * (i + 0.5) / 4 for i in range(4)]
    ink = C["art"]
    lw = 0.9
    gy = y - 14
    for x in xs:
        ba.setup(c, ink, lw)
        c.line(x - 28, gy, x + 28, gy)
    # seed
    ba.setup(c, ink, lw, C["butter"])
    c.ellipse(xs[0] - 9, gy + 1, xs[0] + 9, gy + 13, stroke=1, fill=1)
    c.line(xs[0] - 4, gy + 7, xs[0] + 5, gy + 9)
    # sprout
    ba.stroke(c, ba.curve(xs[1], gy, 22, 90, 0.1, 20), ink, lw)
    ba.leaf(c, xs[1], gy + 20, 18, 140, 0.34, "ovate", 0.05, 0, lw, ink, C["sage"])
    ba.leaf(c, xs[1], gy + 20, 18, 40, 0.34, "ovate", -0.05, 0, lw, ink, C["mint"])
    # bud
    pts = ba.curve(xs[2], gy, 44, 90, -0.08, 20)
    P = ba.Path(pts)
    px, py, a = P.at(0.4)
    ba.leaf(c, px, py, 20, a + 45, 0.3, "lance", -0.06, 0, lw, ink, C["sage"])
    ba.stroke(c, pts, ink, lw)
    ba.bud(c, pts[-1][0], pts[-1][1], 16, 90, ink, lw, C["peach"], C["mint"])
    # bloom
    pts = ba.curve(xs[3], gy, 40, 90, 0.06, 20)
    P = ba.Path(pts)
    px, py, a = P.at(0.4)
    ba.leaf(c, px, py, 20, a - 45, 0.3, "lance", 0.06, 0, lw, ink, C["sage"])
    ba.stroke(c, pts, ink, lw)
    ba.wild_rose(c, pts[-1][0], pts[-1][1], 16, 10, ink, lw, C["lavender"], C["butter"])
    labels = ["plant", "grow", "rest and gather", "bloom"]
    for i, x in enumerate(xs):
        text(c, x, y - 34, labels[i], "Accent", 12, C["ink"], "center")
        if i < 3:
            arrow(c, x + 38, y + 10, xs[i + 1] - 38, y + 10, C["rule"], 0.9, 5)


def exhale(cx, cy, size):
    """Two leaves on a stem. Trace from the stem up one edge, around the tip and back down."""
    out = []
    for sd in (1, -1):
        pts, _, _, _ = ba.leaf_geom(cx, cy - size * 0.18, size * 1.06, 90 - sd * 42, 0.36, "lance", -0.05 * sd, 300)
        if sd < 0:
            pts = pts[::-1]
        L = [0.0]
        for i in range(1, len(pts)):
            L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
        out.append((pts, L, 0.4 * L[-1]))
    return out


def exhale_center(c, cx, cy, size):
    ink = C["art"]
    top = cy - size * 0.18
    ba.ribbon_stem(c, ba.curve(cx, cy - size * 0.86, size * 0.7, 90, 0.04, 30), 7, 4, ink, 0.9, C["sage"])
    ba.leaf(c, cx, cy - size * 0.55, size * 0.3, 160, 0.32, "lance", 0.06, 2, 0.9, ink, C["sage"])
    ba.leaf(c, cx, cy - size * 0.66, size * 0.26, 20, 0.32, "lance", -0.06, 2, 0.9, ink, C["mint"])
    ba.bud(c, cx, top, size * 0.16, 90, ink, 0.9, C["peach"], C["sage"])
    c.setFillColor(C["accent"])
    c.circle(cx, top, 4, stroke=0, fill=1)


def rating_icon(c, x, y):
    ba.forget_me_not(c, x, y, 8.5, 18, C["muted"], 0.5)


def image_art(c, style, fills, angle, lineart, px):
    F = (None,) * 5 if lineart else FILLS
    ba.accent(c, 200, 200, 150, style, angle, C["art"], F, lw=2.6 if px > 300 else 3.4)


COLORING = [
    ("Botanical mandala", bd.mandala, {}),
    ("Geometric bloom", bd.geometric_bloom, {}),
] + [(t, fn, {}) for t, fn in zip(bd.WEEKLY_TITLES[:12], bd.WEEKLY[:12])] + [
    ("In full bloom", bd.wk_finale, {"label": "in full bloom"}),
    ("Botanical sampler", bd.sampler, {}),
    ("Heart wreath", bd.heart_wreath, {}),
    ("Ten-petal mandala", bd.mandala, {"n": 10}),
]

TXT = {
    "tagline": "breathe  ·  notice  ·  bloom",
    "key_weekly": "Look back on the week, log what you handled, then color your reward page.",
    "key_monthly": "Color your mood flower, track habits, and write yourself a kind letter.",
    "key_confidence": "Tools for facing fears a little at a time, sleep, values, and worry time.",
    "exhale_intro": "A longer out-breath tells your body it's safe to slow down. Breathe in for 4, out for 6. "
                    "Trace each leaf: in as you travel up toward the tip, out as you glide around it and back "
                    "down to the stem.",
    "exhale_outro": "Do one leaf, then the other. Five rounds is plenty. If 4 and 6 feel too long, try 3 and 5. "
                    "What matters is that the out-breath is longer than the in-breath.",
    "mood_title": "My mood flower",
    "worked_sub": "Color in the flowers: one for okay, two for helpful, three for a keeper.",
    "coloring_name": "Botanical Coloring Pack",
    "coloring_tip_start": "Color one petal or one leaf, then check in with how you feel.",
    "mood_name": "Mood Flower Tracker",
    "mood_kicker": "Mood flower tracker",
    "mood_month_kicker": "Mood flower",
    "mood_how": "One flower a month, one petal a day. By the end of the month you have a picture of how the "
                "weeks felt, which is often kinder than memory.",
    "mood_find": "Find today's number on the flower and color that petal in the mood that fits the day best. "
                 "Mixed day? Split the petal, or use two colors.",
    "mood_tagline": "12 months  ·  one petal a day",
}

CONTENT = {
    "WELCOME": (
        "This journal is for the heavy days and the lighter ones. It's a place to set your thoughts down, "
        "notice what helps, and be a little kinder to yourself along the way.\n"
        "You only need about five minutes a day. Fill in a daily page, color for a while, or turn to the SOS "
        "Toolkit when things feel like a lot. There's no right way to do this.\n"
        "Skipped days are fine. Missed a whole week? Also fine. Pick up wherever you are and keep going. "
        "Nothing in here is graded, and nobody is checking.\n"
        "Gardens don't bloom overnight. They grow a little at a time, in their own season. You can, too."
    ),
}


def _content():
    import content as base
    how = list(base.HOW_ANXIETY)
    how[3] = ("The garden part",
              "A seed doesn't become a flower in one leap. For a long time, most of the growing happens under "
              "the soil, where no one can see it yet. Working on anxiety can feel like that. Some days it will "
              "seem like nothing is happening. Keep going. Growth is often quiet before it shows.")
    lines = list(base.DAILY_LINES)
    lines[14] = "Seeds don't rush. You don't have to either."
    lines[29] = "Roots grow quietly before anything blooms."
    d = dict(CONTENT)
    d["HOW_ANXIETY"] = how
    d["DAILY_LINES"] = lines
    return d


PACK_COVERS = {
    "coloring": dict(tagline="18 calming designs to color", style="bouquet", lineart=True),
    "sos": dict(style="wreath", fills=("rose", "peach", "butter")),
    "mood": dict(style="bloom", fills=("lavender", "peach", "butter")),
}

MOCK = {
    "accents": [(1, None), (4, None), (0, None)],
    "corner": (3, None),
    "list_icons": [(0, None), (4, None), (1, None), (3, None)],
    "journal_spread_sub": "Daily pages, SOS tools, weekly rewards",
    "journal_weekly": ("13 weekly check-ins", "Review, \"I handled it\" log, reward coloring page"),
    "journal_monthly": ("3 monthly sections", "Mood flower, habit tracker, kind letter"),
    "journal_sos": ("SOS Toolkit, 10 pages", "Breathing, grounding, worry tree, thought record"),
    "journal_more": ("Start Here + Look Back", "Plus Building Confidence tools: 18 more guided pages"),
    "bundle_coloring": "18 original botanical designs plus coloring tips",
    "bundle_mood": "12 undated months plus a year-in-color page",
    "bundle_inside_mood": "Mood flower",
    "coloring_band": "18 botanical designs to color and unwind",
    "coloring_spread_sub": "18 original botanical designs",
    "coloring_spread": [6, 12, 4, 20, 16],
    "coloring_inside": [(4, "Botanical mandala"), (8, "Peony posy"), (17, "Garden arch"), (12, "Dahlia sunburst")],
    "coloring_thumbs": [7, 15],
    "coloring_list": "Mandalas, wreaths, ferns, bouquets and garden scenes",
    "bundle_spread_cp": (12, 6),
    "bundle_inside_cp": 8,
    "sos_count": "10",
    "sos_included": [("Start-here SOS flow", "Breathe, ground, color or move, write"),
                     ("Two breathing guides", "Trace-along box breathing and long-exhale leaves"),
                     ("Grounding, muscle relaxation", "5-4-3-2-1 and an 8-step body scan"),
                     ("Worry tree and thought record", "Sort a worry and find a more balanced thought"),
                     ("2 coloring pages + calming phrases", "Plus a when-to-get-more-help page with 988")],
    "mood_band": "Color one petal a day. See your year in color.",
    "mood_inside": "Monthly flower",
    "mood_included": ("12 monthly mood flowers", "January to December, undated, 28 to 31 petals"),
    "buy_step": "Check out securely. No physical item is shipped.",
    "dl_step": "Download your PDFs from the link on your order page or in your email.",
    "dl_step_bundle": "Download the zip for your paper size from your order link, then unzip it.",
}

THEME = Theme(
    key="petals", slug="calm-petals", title="Calm Petals", subtitle="A 90-Day Anxiety Journal",
    file_prefix="CalmPetals", palette=PALETTE, img=IMG, brand_mark=True,
    cover_defaults=dict(style="bouquet", fills=("lavender", "peach", "butter")),
    accent=accent, cover_art=cover_art, lifecycle=lifecycle, exhale=exhale, exhale_center=exhale_center,
    sos_coloring={"mandala": ("Botanical mandala", bd.mandala),
                  "geometric": ("Geometric bloom", bd.geometric_bloom)},
    weekly=bd.WEEKLY, weekly_titles=bd.WEEKLY_TITLES, mood_cells=bd.mood_cells,
    rating_icon=rating_icon, coloring_pack=COLORING, pack_covers=PACK_COVERS, image_art=image_art,
    txt=TXT, content=_content(), mock=MOCK,
)
