"""Calm Nights: the moon-and-stars edition, for anxious nights.

Printer-friendly: line art on white, deep indigo used sparingly for headings, soft lavender
and pale gold accents. Art and coloring pages from celestial_art.py. The copy leans toward
evenings: a night SOS page, a night brain dump next to the sleep wind-down, and night-flavored
lines of the day. Day pages still work any time.
"""
import math

import build_journal as bj
import celestial_art as ca
from themes import Theme, colors

PALETTE = {
    "ink": "#2F3350",      # body text (ink navy)
    "muted": "#868AA6",    # small labels
    "rule": "#CACCDD",     # writing lines
    "art": "#3A3F62",      # line art (soft navy)
    "accent": "#3D4180",   # headings (deep indigo, used sparingly)
    "accent2": "#A8853D",  # kickers (antique gold)
    # pastel slots
    "lavender": "#E6E0F4",  # lavender
    "mint": "#DCE3F5",      # periwinkle
    "peach": "#F6EACB",     # pale gold
    "rose": "#EEDDEE",      # mauve
    "butter": "#FAF2D8",    # moonlight
    "sage": "#E1E7F1",      # mist blue
    "tint": "#F5F4FB",      # faintest panel tint
}
C = colors(PALETTE)

IMG = {
    "bg_top": (247, 246, 252), "bg_bot": (228, 228, 245), "ink": (47, 51, 80), "muted": (120, 124, 152),
    "accent": (61, 65, 128), "accent2": (168, 133, 61), "lav": (230, 224, 244), "mint": (220, 227, 245),
    "peach": (246, 234, 203), "rose": (238, 221, 238), "butter": (250, 242, 216), "white": (255, 255, 255),
    "border": (222, 222, 238), "shadow": (40, 42, 90), "band": (46, 50, 102), "band_text": (214, 200, 160),
}

FILLS = (C["peach"], C["butter"], C["lavender"], C["mint"], C["sage"])   # moon, star, cloud, star2, sky


# --------------------------------------------------------------------------
# art hooks
# --------------------------------------------------------------------------


def accent(c, x, y, size, k=0, angle=0.0, style=None):
    """A small accent: crescent and star, sparkles, moon and cloud, full moon, star, constellation."""
    if style == "simple":
        k = 1
    ca.accent(c, x, y, size, k, angle, C["art"], FILLS)


def cover_art(c, cx, o):
    line = o["lineart"]
    F = (None,) * 5 if line else tuple(C[k] for k in o["fills"])
    c.saveState()
    c.setFillColor(C["tint"])
    c.circle(cx, 500, 188, stroke=0, fill=1)
    c.setStrokeColor(C["lavender"] if not line else C["rule"])
    c.setLineWidth(0.8)
    c.setDash(1, 4)
    c.circle(cx, 500, 206, stroke=1, fill=0)
    c.restoreState()
    ca.moon_scene(c, cx, 488 if o["style"] == "moon" else 500, 172, C["art"], F, 1.1 if line else 1.0, o["style"])
    if not line:
        accent(c, cx - 228, 330, 20, 1, 0)
        accent(c, cx + 226, 352, 18, 4, 12)


def lifecycle(c, F, y):
    text, arrow = bj.text, bj.arrow
    xs = [F.left + F.w * (i + 0.5) / 4 for i in range(4)]
    for x, p in zip(xs, (0.0, 0.12, 0.25, 0.5)):
        ca.phase(c, x, y + 10, 20, p, C["art"], 0.9, C["peach"], C["sage"])
    labels = ["dark", "a sliver", "halfway", "full"]
    for i, x in enumerate(xs):
        text(c, x, y - 34, labels[i], "Accent", 12, C["ink"], "center")
        if i < 3:
            arrow(c, x + 38, y + 10, xs[i + 1] - 38, y + 10, C["rule"], 0.9, 5)


def _exhale_geom(cx, cy, size):
    R = size * 0.9
    return ca.crescent_geom(cx + R * 0.28, cy - size * 0.02, R, rot=0.0, d=0.36, k=0.95, n=300)


def exhale(cx, cy, size):
    """Trace the moon: in up the inside curve, out around the outside edge."""
    inner, outer = _exhale_geom(cx, cy, size)
    pts = inner + outer[1:]
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
    split = L[len(inner) - 1]
    return [(pts, L, split)]


def exhale_center(c, cx, cy, size):
    inner, _ = _exhale_geom(cx, cy, size)
    R = size * 0.9
    hx = cx + R * 0.45
    ca.star(c, hx, cy + size * 0.12, size * 0.1, C["art"], 0.9, C["peach"], detail=True)
    ca.sparkle(c, hx + size * 0.12, cy - size * 0.2, size * 0.07, C["art"], 0.9, C["lavender"])
    ca.sparkle(c, hx - size * 0.1, cy - size * 0.05, size * 0.045, C["art"], 0.9, C["butter"])
    sx, sy = inner[0]
    c.setFillColor(C["accent"])
    c.circle(sx, sy, 5, stroke=0, fill=1)
    bj.text(c, sx + 10, sy - 14, "start", "Sans", 8, C["accent"])


def rating_icon(c, x, y):
    ca.star(c, x, y, 9, C["muted"], 0.5)


def image_art(c, style, fills, angle, lineart, px):
    F = (None,) * 5 if lineart else FILLS
    ca.accent(c, 200, 200, 150, style, angle, C["art"], F, lw=2.6 if px > 300 else 3.4)


COLORING = [
    ("Celestial mandala", ca.mandala, {}),
    ("Eight-point star", ca.geo_star, {}),
] + [(t, fn, {}) for t, fn in zip(ca.WEEKLY_TITLES[:12], ca.WEEKLY[:12])] + [
    ("Rest well", ca.wk_finale, {"label": "rest well"}),
    ("Night sampler", ca.sampler, {}),
    ("Shooting stars", ca.shooting_stars, {}),
    ("Twelve-petal mandala", ca.mandala, {"n": 12}),
]

TXT = {
    "tagline": "breathe  ·  unwind  ·  rest",
    "key_weekly": "Look back on the week, log what you handled, then color your reward page.",
    "key_monthly": "Color your mood stars, track habits, and write yourself a kind letter.",
    "key_confidence": "A night wind-down and brain dump, then tools for facing fears a little at a time, "
                      "values, and worry time.",
    "exhale_intro": "A longer out-breath tells your body it's safe to slow down. Breathe in for 4, out for 6. "
                    "Trace the moon from the dot: in as you travel up the inside curve, out as you glide around "
                    "the outside edge and back to the start.",
    "exhale_outro": "Go around the moon five times, or for as long as it feels good. If 4 and 6 feel too long, try "
                    "3 and 5. What matters is that the out-breath is longer than the in-breath.",
    "mood_title": "My mood stars",
    "worked_sub": "Color in the stars: one for okay, two for helpful, three for a keeper.",
    "coloring_name": "Celestial Coloring Pack",
    "coloring_tip_start": "Color one star or one cloud, then check in with how you feel.",
    "mood_name": "Mood Star Tracker",
    "mood_kicker": "Mood star tracker",
    "mood_month_kicker": "Mood stars",
    "mood_how": "One constellation a month, one star a night. By the end of the month you have a picture of "
                "how the weeks felt, which is often kinder than memory.",
    "mood_find": "Find tonight's number and color that star in the mood that fits the day best. Mixed day? "
                 "Split the star, or use two colors.",
    "mood_tagline": "12 months  ·  one star a night",
}


def _content():
    import content as base
    how = list(base.HOW_ANXIETY)
    how[3] = ("The moon part",
              "The moon doesn't go from dark to full in one night. It changes a sliver at a time, and it's still "
              "there on the nights you can't see it. Working on anxiety can feel like that. Some nights it will "
              "seem like nothing is changing. Keep going. Change is often quiet before it shows.")
    lines = list(base.DAILY_LINES)
    lines[12] = "Worries often look bigger at night than they do by day."
    lines[14] = "The moon takes its time. You can, too."
    lines[21] = "Tonight, rest is enough."
    lines[29] = "Night always gives way to morning."
    lines[15] = "Dim the lights. Slow your breath. Start there."
    wind = list(base.WIND_DOWN)
    wind[4] = "Write tomorrow's list on the night brain dump page ({dump})"
    return {
        "WELCOME": (
            "This journal is for the long nights and the lighter days. It's a place to set your thoughts down, "
            "notice what helps, and be a little kinder to yourself along the way.\n"
            "You only need about five minutes a day. Many people like to fill in the daily page in the evening, "
            "as part of winding down, but any time works. Color for a while, or turn to the SOS Toolkit when "
            "things feel like a lot. There's no right way to do this.\n"
            "Skipped days are fine. Missed a whole week? Also fine. Pick up wherever you are and keep going. "
            "Nothing in here is graded, and nobody is checking.\n"
            "The moon doesn't go from dark to full in one night. It changes a little at a time. You can, too."
        ),
        "HOW_ANXIETY": how,
        "DAILY_LINES": lines,
        "WIND_DOWN": wind,
        "DAILY_HABITS": ["drank water", "moved my body", "got outside", "went easy on caffeine",
                         "wound down before bed"],
        "HABIT_ROWS": ["Daily page", "Water", "Movement", "Time outside", "Easy on caffeine",
                       "Evening wind-down", "Screens off before bed", "Breathing practice", ""],
    }


PACK_COVERS = {
    "coloring": dict(tagline="18 calming designs to color", style="moon", lineart=True),
    "sos": dict(style="cloud", fills=("peach", "butter", "lavender", "mint", "sage")),
    "mood": dict(style="starfield", fills=("peach", "butter", "lavender", "mint", "sage")),
}

MOCK = {
    "accents": [(1, None), (2, None), (4, None)],
    "corner": (0, None),
    "list_icons": [(0, None), (4, None), (2, None), (1, None)],
    "journal_spread_sub": "Daily pages, night tools, weekly rewards",
    "journal_weekly": ("13 weekly check-ins", "Review, \"I handled it\" log, reward coloring page"),
    "journal_monthly": ("3 monthly sections", "Mood stars, habit tracker, kind letter"),
    "journal_sos": ("SOS Toolkit, 11 pages", "Breathing, grounding, a can't-sleep page, worry tree"),
    "journal_more": ("Night wind-down + brain dump", "Plus Start Here, Building Confidence and Look Back"),
    "bundle_coloring": "18 original moon and star designs plus coloring tips",
    "bundle_mood": "12 undated months plus a year-in-color page",
    "bundle_inside_mood": "Mood stars",
    "coloring_band": "18 moon and star designs to color and unwind",
    "coloring_spread_sub": "18 original celestial designs",
    "coloring_spread": [9, 12, 4, 20, 17],
    "coloring_inside": [(4, "Celestial mandala"), (6, "Moon in the clouds"), (9, "Night lake"), (17, "Night window")],
    "coloring_thumbs": [8, 15],
    "coloring_list": "Mandalas, moons, constellations, clouds and night scenes",
    "bundle_spread_cp": (12, 9),
    "bundle_inside_cp": 6,
    "sos_count": "11",
    "sos_spread_last": 13,
    "sos_included": [("Start-here SOS flow", "Breathe, ground, color or move, write"),
                     ("When your mind won't switch off", "A gentle 4-step page for wakeful nights"),
                     ("Two breathing guides", "Trace-along box breathing and a long-exhale moon"),
                     ("Grounding, muscle relaxation", "5-4-3-2-1 and an 8-step body scan"),
                     ("Worry tree, thought record, 2 coloring pages", "Plus calming phrases and 988 resources")],
    "mood_band": "Color one star a night. See your year in color.",
    "mood_inside": "Monthly stars",
    "mood_included": ("12 monthly star constellations", "January to December, undated, 28 to 31 stars"),
    "buy_step": "Check out securely. No physical item is shipped.",
    "dl_step": "Download your PDFs from the link on your order page or in your email.",
    "dl_step_bundle": "Download the zip for your paper size from your order link, then unzip it.",
}

THEME = Theme(
    key="nights", slug="calm-nights", title="Calm Nights",
    subtitle="A 90-Day Anxiety Journal for Anxious Nights",
    file_prefix="CalmNights", palette=PALETTE, img=IMG, brand_mark=True,
    cover_defaults=dict(style="moon", fills=("peach", "butter", "lavender", "mint", "sage")),
    extra_sos=["sleep_sos"],
    confidence=["wind_down", "brain_dump", "fear_ladder", "ladder_log", "lift_menu", "values_page", "worry_time"],
    accent=accent, cover_art=cover_art, lifecycle=lifecycle, exhale=exhale, exhale_center=exhale_center,
    sos_coloring={"mandala": ("Celestial mandala", ca.mandala), "geometric": ("Eight-point star", ca.geo_star)},
    weekly=ca.WEEKLY, weekly_titles=ca.WEEKLY_TITLES, mood_cells=ca.mood_cells,
    rating_icon=rating_icon, coloring_pack=COLORING, pack_covers=PACK_COVERS, image_art=image_art,
    txt=TXT, content=_content(), mock=MOCK,
)
