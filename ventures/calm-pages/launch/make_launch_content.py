"""Peace by Page launch content (10/16 launch, checklist rows 41, 44, 47).

Builds, into ../launch/content/:
  pins/<edition>-<n>-<kind>.png      15 Pinterest pins, 1000 x 1500 (5 per edition)
  carousel/launch-<n>.png            7-slide launch carousel, 1080 x 1350 (Instagram / Facebook)
  videos/<n>-<name>.mp4              5 vertical videos, 1080 x 1920, 30 fps, no audio, captions baked in
  videos/<n>-<name>-cover.png        a cover frame for each video

Every page shown is rendered from the real product PDFs, so the art always matches the files.
Run from anywhere: python3 launch/make_launch_content.py [pins|carousel|videos]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_brand_assets import BRAND_COL, INK, LAV, MINT, PEACH, ROOT, SANS, SERIF, centered, gradient  # noqa: E402
from make_store_assets import ED, SAMPLER, SANS_BOLD, SERIF_REG, fan_covers, font, page, paper, place  # noqa: E402

OUT = os.path.join(ROOT, "launch", "content")
FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

PDF = {
    "wings": {
        "journal": "editions/calm-wings/files/1-journal/CalmWings_90Day_Journal_Letter.pdf",
        "coloring": "editions/calm-wings/files/3-coloring-pack/CalmWings_Butterfly_Coloring_Pack_Letter.pdf",
        "mood": "editions/calm-wings/files/5-mood-tracker/CalmWings_Mood_Butterfly_Tracker_Letter.pdf",
        "sos": "editions/calm-wings/files/4-sos-kit/CalmWings_SOS_Calm_Down_Kit_Letter.pdf",
    },
    "petals": {
        "journal": "editions/calm-petals/files/1-journal/CalmPetals_90Day_Journal_Letter.pdf",
        "coloring": "editions/calm-petals/files/3-coloring-pack/CalmPetals_Botanical_Coloring_Pack_Letter.pdf",
        "mood": "editions/calm-petals/files/5-mood-tracker/CalmPetals_Mood_Flower_Tracker_Letter.pdf",
        "sos": "editions/calm-petals/files/4-sos-kit/CalmPetals_SOS_Calm_Down_Kit_Letter.pdf",
    },
    "nights": {
        "journal": "editions/calm-nights/files/1-journal/CalmNights_90Day_Journal_Letter.pdf",
        "coloring": "editions/calm-nights/files/3-coloring-pack/CalmNights_Celestial_Coloring_Pack_Letter.pdf",
        "mood": "editions/calm-nights/files/5-mood-tracker/CalmNights_Mood_Star_Tracker_Letter.pdf",
        "sos": "editions/calm-nights/files/4-sos-kit/CalmNights_SOS_Calm_Down_Kit_Letter.pdf",
    },
}
# journal page indices (0-based); Calm Nights has one extra SOS page, so its days start one later
PG = {
    "wings": dict(cover=0, sos=8, box=9, ground=11, thought=14, sos_color=15, day1=18, handled=26, reward=27,
                  winddown=159, worry=161),
    "petals": dict(cover=0, sos=8, box=9, ground=11, thought=14, sos_color=15, day1=18, handled=26, reward=27,
                   winddown=159, worry=161),
    "nights": dict(cover=0, sos=8, box=9, ground=11, thought=14, sos_color=15, sleep_sos=18, day1=19, handled=27,
                   reward=28, winddown=157, night=158, worry=163),
}
COLOR_PICK = {"wings": (6, 15), "petals": (5, 9), "nights": (8, 3)}   # coloring pack pages for pins / videos
WORD = {"wings": "butterfly", "petals": "botanical", "nights": "moon and stars"}
STORE = "payhip.com/PeaceByPage"
CARE = "Supports, not replaces, professional care."
CRISIS = "In crisis in the US? Call or text 988."


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def block(d, text, f, cx, y, maxw, fill, gap=1.18):
    """Centered, wrapped text. Returns the y below the block."""
    for line in wrap(d, text, f, maxw):
        centered(d, line, f, cx, y, fill)
        y += f.size * gap
    return y


def pill(d, text, f, cx, y, bg, fg, padx=34, pady=16):
    w = d.textlength(text, font=f)
    d.rounded_rectangle([cx - w / 2 - padx, y, cx + w / 2 + padx, y + f.size + 2 * pady], radius=(f.size + 2 * pady) / 2,
                        fill=bg)
    d.text((cx - w / 2, y + pady - f.size * 0.08), text, font=f, fill=fg)
    return y + f.size + 2 * pady


def bg(key, w, h):
    stops = ED[key][3] if key in ED else [PEACH, (247, 238, 243), LAV]
    return gradient(w, h, stops).convert("RGBA")


def save(im, sub, name):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    p = os.path.join(OUT, sub, name)
    im.convert("RGB").save(p, optimize=True)
    print("  ", os.path.relpath(p, ROOT), im.size)


# ---------------------------------------------------------------- pins (1000 x 1500)

def pin_frame(key, kicker, headline, sub, cta):
    W, H = 1000, 1500
    im = bg(key, W, H)
    d = ImageDraw.Draw(im)
    col = ED[key][2] if key in ED else BRAND_COL
    centered(d, kicker.upper(), font(SANS_BOLD, 30), W / 2, 62, col)
    y = block(d, headline, font(SERIF, 84), W / 2, 112, W - 120, INK, 1.08)
    if sub:
        y = block(d, sub, font(SANS, 36), W / 2, y + 14, W - 160, INK)
    # bottom band
    top = H - 190
    d.rectangle([0, top, W, H], fill=(255, 255, 255, 236))
    pill(d, cta, font(SANS_BOLD, 38), W / 2, top + 30, col, (255, 255, 255))
    centered(d, "Peace by Page  |  " + STORE, font(SANS, 28), W / 2, top + 128, INK)
    return im, d, y


def pins():
    for key in ("wings", "petals", "nights"):
        name = ED[key][0]
        j, c = PDF[key]["journal"], PDF[key]["coloring"]
        p = PG[key]
        a, b = COLOR_PICK[key]

        # 1. inside pages
        im, d, y = pin_frame(key, name + " | 90-day journal", "A peek inside the anxiety journal",
                             "Daily pages, an SOS toolkit and coloring breaks", "Printable PDF  |  Letter + A4")
        cy = (y + 1310) / 2 + 20
        place(im, paper(page(j, p["box"], 414), -8), 250, cy + 30)
        place(im, paper(page(j, p["reward"], 414), 8), 750, cy + 30)
        place(im, paper(page(j, p["day1"], 483), 0), 500, cy)
        save(im, "pins", f"{key}-1-inside.png")

        # 2. coloring page
        im, d, y = pin_frame(key, name + " | coloring pack", f"18 calming {WORD[key]} coloring pages",
                             "For adults. Print, pick three colors, start anywhere.", "Instant download  |  $4.99")
        cy = (y + 1310) / 2 + 20
        place(im, paper(page(c, b, 437), 7), 690, cy + 20)
        place(im, paper(page(c, a, 598), -3), 440, cy)
        save(im, "pins", f"{key}-2-coloring.png")

        # 3. Day 1 page
        im, d, y = pin_frame(key, name + " | Day 1 of 90", "What five minutes a day looks like",
                             "Rate your mood, three good things, one worry and a kinder thought, one small step",
                             "See the full journal")
        cy = (y + 1310) / 2 + 20
        place(im, paper(page(j, p["day1"], 630), 0), 500, cy)
        save(im, "pins", f"{key}-3-day1.png")

        # 4. gift angle
        im, d, y = pin_frame(key, "Gift idea", "A gift for someone who worries",
                             f"The {name} bundle: journal, coloring pack and mood tracker", "Bundle  |  $16.99")
        cy = (y + 1310) / 2 + 30
        place(im, paper(page(PDF[key]["mood"], 0, 379), 10), 760, cy + 40)
        place(im, paper(page(c, 0, 379), -10), 240, cy + 40)
        place(im, paper(page(j, 0, 506), 0), 500, cy)
        # small bow-free tag: printable gift note
        pill(d, "Print it, wrap it, or email the file", font(SANS, 30), 500, 1310 - 90, (255, 255, 255, 230), INK)
        save(im, "pins", f"{key}-4-gift.png")

        # 5. free sampler
        im, d, y = pin_frame(key, "Free download", "Try a week of the anxiety journal free",
                             "7 daily pages, a pocket SOS card and a page to color", "Get the free sampler")
        cy = (y + 1310) / 2 + 20
        place(im, paper(page(SAMPLER, 12, 379), 9), 760, cy + 40)
        place(im, paper(page(j, 0, 379), -9), 240, cy + 40)
        place(im, paper(page(SAMPLER, 0, 494), 0), 500, cy)
        r = 86
        bx, by = 868, y + 120
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(107, 90, 166, 255), outline=(255, 255, 255, 255), width=7)
        f = font(SANS_BOLD, 48)
        d.text((bx - d.textlength("FREE", font=f) / 2, by - 30), "FREE", font=f, fill=(255, 255, 255))
        save(im, "pins", f"{key}-5-sampler.png")


# ---------------------------------------------------------------- carousel (1080 x 1350)

def slide(key, kicker, headline, sub=None):
    W, H = 1080, 1350
    im = bg(key, W, H)
    d = ImageDraw.Draw(im)
    centered(d, kicker.upper(), font(SANS_BOLD, 30), W / 2, 70, BRAND_COL if key not in ED else ED[key][2])
    y = block(d, headline, font(SERIF, 80), W / 2, 122, W - 140, INK, 1.08)
    if sub:
        y = block(d, sub, font(SANS, 38), W / 2, y + 12, W - 180, INK)
    centered(d, "Peace by Page", font(SERIF, 34), W / 2, H - 70, BRAND_COL)
    return im, d, y


def carousel():
    W, H = 1080, 1350
    J = {k: PDF[k]["journal"] for k in PDF}
    # 1 cover
    im, d, y = slide("wings", "Now open  |  October 16", "Today we open the doors",
                     "Peace by Page: gentle printable journals for anyone who worries")
    fan_covers(im, W / 2, (y + H - 90) / 2 + 40, 400)
    save(im, "carousel", "launch-1.png")
    # 2 what it is
    im, d, y = slide("petals", "What it is", "A 90-day journal you print at home",
                     "One page a day. About five minutes. Start any day; the pages are undated.")
    place(im, paper(page(J["petals"], PG["petals"]["day1"], 520), 0), W / 2, (y + H - 90) / 2 + 20)
    save(im, "carousel", "launch-2.png")
    # 3 day page
    im, d, y = slide("wings", "Each day", "Notice. Write. Take one small step.",
                     "Mood check, three good things, one worry and a more balanced thought")
    place(im, paper(page(J["wings"], PG["wings"]["thought"], 380), -7), 300, (y + H - 90) / 2 + 40)
    place(im, paper(page(J["wings"], PG["wings"]["day1"], 440), 4), 720, (y + H - 90) / 2 + 20)
    save(im, "carousel", "launch-3.png")
    # 4 SOS
    im, d, y = slide("nights", "For hard moments", "An SOS toolkit in every journal",
                     "Box breathing, 5-4-3-2-1 grounding, a worry tree, calming phrases")
    cy = (y + H - 90) / 2 + 30
    place(im, paper(page(J["nights"], PG["nights"]["ground"], 330), -9), 260, cy + 30)
    place(im, paper(page(J["nights"], PG["nights"]["sos"], 330), 9), 820, cy + 30)
    place(im, paper(page(J["nights"], PG["nights"]["box"], 420), 0), W / 2, cy)
    save(im, "carousel", "launch-4.png")
    # 5 editions
    im = gradient(W, H, [LAV, MINT, (236, 236, 228), PEACH]).convert("RGBA")
    d = ImageDraw.Draw(im)
    centered(d, "THREE EDITIONS", font(SANS_BOLD, 30), W / 2, 70, BRAND_COL)
    block(d, "Same journal inside. Pick the art that feels like you.", font(SERIF, 70), W / 2, 122, W - 140, INK, 1.08)
    for i, k in enumerate(("wings", "petals", "nights")):
        cx = 190 + i * 350
        place(im, paper(page(J[k], 0, 310), 0), cx, 740)
        centered(d, ED[k][0], font(SERIF, 46), cx, 1010, ED[k][2])
        block(d, ED[k][1], font(SANS, 28), cx, 1068, 300, INK)
    centered(d, "Peace by Page", font(SERIF, 34), W / 2, H - 70, BRAND_COL)
    save(im, "carousel", "launch-5.png")
    # 6 sampler
    im, d, y = slide("sampler", "Free", "Try a week first",
                     "The free 7-day sampler: 7 daily pages, a pocket SOS card and a coloring page")
    cy = (y + H - 90) / 2 + 30
    place(im, paper(page(SAMPLER, 12, 330), 9), 820, cy + 30)
    place(im, paper(page(SAMPLER, 3, 330), -9), 260, cy + 30)
    place(im, paper(page(SAMPLER, 0, 420), 0), W / 2, cy)
    save(im, "carousel", "launch-6.png")
    # 7 care note
    im = gradient(W, H, [MINT, (246, 243, 251), PEACH]).convert("RGBA")
    d = ImageDraw.Draw(im)
    centered(d, "A NOTE OF CARE", font(SANS_BOLD, 30), W / 2, 150, BRAND_COL)
    y = block(d, "A journal can be a calm place to start. It is not the whole plan.", font(SERIF, 72), W / 2, 220,
              W - 160, INK, 1.1)
    y = block(d, "Peace by Page journals are for self-reflection and general wellbeing. They are not medical advice "
                 "or treatment, and they support, not replace, care from a licensed professional.",
              font(SANS, 38), W / 2, y + 40, W - 200, INK, 1.3)
    d.rounded_rectangle([110, y + 50, W - 110, y + 330], radius=36, fill=(255, 255, 255, 235))
    centered(d, "In crisis in the US?", font(SANS_BOLD, 44), W / 2, y + 90, INK)
    centered(d, "Call or text 988", font(SERIF, 84), W / 2, y + 150, BRAND_COL)
    centered(d, "Outside the US: findahelpline.com", font(SANS, 32), W / 2, y + 262, INK)
    centered(d, "Shop and free sampler: " + STORE, font(SANS, 34), W / 2, H - 150, INK)
    centered(d, "Peace by Page", font(SERIF, 34), W / 2, H - 70, BRAND_COL)
    save(im, "carousel", "launch-7.png")


# ---------------------------------------------------------------- videos (1080 x 1920)

VW, VH, FPS = 1080, 1920, 30


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Card:
    """One beat of a video: a page layer (RGBA, full frame), a caption, and how it enters."""

    def __init__(self, layer, caption, dur=2.4, enter="slide", reveal=False):
        self.layer, self.caption, self.dur, self.enter, self.reveal = layer, caption, dur, enter, reveal


def page_layer(pdf, idx, width=760, angle=0, cy=1060, extra=()):
    lay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    for (p2, i2, w2, a2, dx, dy) in extra:
        place(lay, paper(page(p2, i2, w2), a2), VW / 2 + dx, cy + dy)
    place(lay, paper(page(pdf, idx, width), angle), VW / 2, cy)
    return lay


def caption_layer(text, col):
    lay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font(SERIF, 72)
    lines = wrap(d, text, f, VW - 260)
    h = len(lines) * f.size * 1.12 + 70
    top = 260
    d.rounded_rectangle([90, top, VW - 90, top + h], radius=40, fill=(255, 255, 255, 236))
    y = top + 30
    for ln in lines:
        centered(d, ln, f, VW / 2, y, INK)
        y += f.size * 1.12
    return lay


def end_card(key, line1, line2):
    lay = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = ED[key][2] if key in ED else BRAND_COL
    fan_covers(lay, VW / 2, 760, 300) if key != "sampler" else place(lay, paper(page(SAMPLER, 0, 520), 0), VW / 2, 760)
    centered(d, "Peace by Page", font(SERIF, 96), VW / 2, 1130, col)
    centered(d, line1, font(SANS_BOLD, 50), VW / 2, 1270, INK)
    centered(d, line2, font(SANS, 42), VW / 2, 1345, INK)
    d.rounded_rectangle([110, 1450, VW - 110, 1600], radius=30, fill=(255, 255, 255, 225))
    centered(d, CARE, font(SANS, 34), VW / 2, 1478, INK)
    centered(d, CRISIS, font(SANS, 34), VW / 2, 1532, INK)
    return lay


def render_video(name, key, cards, end):
    os.makedirs(os.path.join(OUT, "videos"), exist_ok=True)
    path = os.path.join(OUT, "videos", name + ".mp4")
    base = bg(key, VW, VH)
    col = ED[key][2] if key in ED else BRAND_COL
    caps = [caption_layer(c.caption, col) if c.caption else None for c in cards]
    cards = cards + [Card(end, None, 3.6, "fade")]
    caps.append(None)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium",
           "-movflags", "+faststart", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    T = 0.45   # transition length
    prev = None
    cover_saved = False
    for ci, c in enumerate(cards):
        n = int(c.dur * FPS)
        for fi in range(n):
            t = fi / FPS
            fr = base.copy()
            k = ease(t / T)
            # slow drift so still pages feel alive
            drift = int(18 * (t / c.dur))
            lay = c.layer
            if c.reveal:
                rv = ease((t - 0.1) / 1.6)
                mask = Image.new("L", (VW, VH), 0)
                ImageDraw.Draw(mask).rectangle([0, 0, VW, int(VH * rv)], fill=255)
                blank = page_layer_blank(lay)
                fr.alpha_composite(blank)
                cut = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
                cut.paste(lay, (0, 0), mask)
                lay = cut
            if prev is not None and k < 1:
                if c.enter == "slide":
                    fr.alpha_composite(prev, (int(-VW * 0.35 * k), 0))
                else:
                    pv = prev.copy()
                    pv.putalpha(pv.getchannel("A").point(lambda a, kk=k: int(a * (1 - kk))))
                    fr.alpha_composite(pv)
            if c.enter == "slide" and k < 1:
                fr.alpha_composite(lay, (int(VW * (1 - k)), -drift))
            elif c.enter == "fade" and k < 1:
                ly = lay.copy()
                ly.putalpha(ly.getchannel("A").point(lambda a, kk=k: int(a * kk)))
                fr.alpha_composite(ly, (0, -drift))
            else:
                fr.alpha_composite(lay, (0, -drift))
            if caps[ci] is not None:
                ck = ease((t - 0.15) / 0.4)
                if ck > 0:
                    cl = caps[ci] if ck >= 1 else caps[ci].copy()
                    if ck < 1:
                        cl.putalpha(cl.getchannel("A").point(lambda a, kk=ck: int(a * kk)))
                    fr.alpha_composite(cl)
            if not cover_saved and ci == 0 and fi == n - 1:
                fr.convert("RGB").save(os.path.join(OUT, "videos", name + "-cover.png"), optimize=True)
                cover_saved = True
            proc.stdin.write(fr.convert("RGB").tobytes())
        prev = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        prev.alpha_composite(c.layer, (0, -18))
    proc.stdin.close()
    proc.wait()
    print("  ", os.path.relpath(path, ROOT), f"{sum(c.dur for c in cards):.1f}s")


def page_layer_blank(lay):
    """A faint white silhouette of the page area, so a wipe-reveal starts from a blank sheet."""
    a = lay.getchannel("A").point(lambda v: 255 if v > 200 else 0)
    blank = Image.new("RGBA", (VW, VH), (255, 255, 255, 0))
    blank.putalpha(a)
    return blank


def videos():
    J = {k: PDF[k]["journal"] for k in PDF}
    w, n, p = J["wings"], J["nights"], J["petals"]
    # 1. Calm Wings flip-through
    render_video("1-wings-flip-through", "wings", [
        Card(page_layer(w, 0), "A 90-day anxiety journal you print at home", enter="fade"),
        Card(page_layer(w, PG["wings"]["sos"]), "Hard moment? Start with the SOS pages"),
        Card(page_layer(w, PG["wings"]["box"]), "Trace the square. Breathe in for four."),
        Card(page_layer(w, PG["wings"]["day1"]), "One page a day. About five minutes."),
        Card(page_layer(w, PG["wings"]["reward"]), "Finish a week, color a page"),
    ], end_card("wings", "Calm Wings  |  link in bio", "Letter + A4  |  instant download"))
    # 2. Calm Nights, evenings
    pn = PG["nights"]
    render_video("2-nights-evening-pages", "nights", [
        Card(page_layer(n, 0), "For worries that get louder at night", enter="fade"),
        Card(page_layer(n, pn["sleep_sos"]), "When your mind won't switch off"),
        Card(page_layer(n, pn["winddown"]), "A wind-down list for bedtime"),
        Card(page_layer(n, pn["day1"]), "Five quiet minutes before bed"),
        Card(page_layer(PDF["nights"]["coloring"], 8), "Moon and stars to color"),
    ], end_card("nights", "Calm Nights  |  link in bio", "Letter + A4  |  instant download"))
    # 3. Calm Petals coloring reveal
    c = PDF["petals"]["coloring"]
    render_video("3-petals-coloring-reveal", "petals", [
        Card(page_layer(c, 0), "18 botanical pages to color", enter="fade"),
        Card(page_layer(c, 5), "No rules. Start with one leaf.", 2.8, reveal=True),
        Card(page_layer(c, 9), "Three colors is plenty", 2.8, reveal=True),
        Card(page_layer(c, 13), "Stop whenever you like", 2.8, reveal=True),
        Card(page_layer(PDF["petals"]["mood"], 3), "Or color one petal a day to track your mood"),
    ], end_card("petals", "Calm Petals  |  link in bio", "Coloring pack $4.99"))
    # 4. three editions
    render_video("4-three-editions", "wings", [
        Card(page_layer(w, 0), "Calm Wings: soft butterflies", enter="fade"),
        Card(page_layer(p, 0), "Calm Petals: gentle botanicals"),
        Card(page_layer(n, 0), "Calm Nights: moon and stars"),
        Card(page_layer(p, PG["petals"]["day1"]), "Same 90-day journal inside"),
        Card(page_layer(n, PG["nights"]["day1"], extra=((w, PG["wings"]["day1"], 600, -8, -150, 40),
                                                       (p, PG["petals"]["day1"], 600, 8, 150, 40))),
             "Pick the one that feels like you"),
    ], end_card("wings", "Three editions  |  link in bio", "Free 7-day sampler in the shop"))
    # 5. free sampler
    render_video("5-free-sampler", "sampler", [
        Card(page_layer(SAMPLER, 0), "Not sure yet? Try a week free", enter="fade"),
        Card(page_layer(SAMPLER, 3), "7 daily pages, about five minutes each"),
        Card(page_layer(SAMPLER, 12), "A pocket SOS card to cut out"),
        Card(page_layer(SAMPLER, 11), "And a page to color when you finish"),
    ], end_card("sampler", "Free sampler  |  link in bio", "Letter + A4  |  $0"))


if __name__ == "__main__":
    what = sys.argv[1:] or ["pins", "carousel", "videos"]
    if "pins" in what:
        pins()
    if "carousel" in what:
        carousel()
    if "videos" in what:
        videos()
    print("done:", OUT)
