"""Payhip store branding for Peace by Page (launch step 22).

Builds, into ../brand/:
  payhip-logo.png          1000 x 1000  square logo (same style as facebook-profile.png)
  payhip-favicon.png        512 x 512   butterfly circle only, for the browser tab
  payhip-banner.png        2400 x 800   store banner (3:1), three edition art circles
  payhip-banner-slim.png   2400 x 600   slimmer 4:1 version if the theme crops tall banners

Art circles are cut from page 1 of each edition's Letter journal PDF, so they always match
the products. Run from anywhere: python3 launch/make_brand_assets.py
"""
import os

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "brand")

SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

EDITIONS = [  # (label, pdf, label color)
    ("Calm Wings", "editions/calm-wings/files/1-journal/CalmWings_90Day_Journal_Letter.pdf", (126, 107, 181)),
    ("Calm Petals", "editions/calm-petals/files/1-journal/CalmPetals_90Day_Journal_Letter.pdf", (84, 128, 104)),
    ("Calm Nights", "editions/calm-nights/files/1-journal/CalmNights_90Day_Journal_Letter.pdf", (52, 56, 110)),
]
BRAND_COL = (126, 107, 181)
INK = (62, 64, 80)
LAV, MINT, PEACH = (232, 223, 245), (216, 236, 232), (250, 226, 214)


def art_circle(pdf, px):
    """Cut the cover-art halo (center 306,500 pt; radius 188 pt) out of the cover, as RGBA px wide."""
    doc = pymupdf.open(os.path.join(ROOT, pdf))
    page = doc[0]
    r = 188
    cx, cy = page.rect.width / 2, page.rect.height - 500
    clip = pymupdf.Rect(cx - r, cy - r, cx + r, cy + r)
    zoom = px * 1.5 / (2 * r)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).resize((px, px), Image.LANCZOS)
    mask = Image.new("L", (px * 4, px * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, px * 4 - 1, px * 4 - 1], fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask.resize((px, px), Image.LANCZOS))
    return out


def ringed(pdf, px, ring):
    """Art circle inside a white ring with a faint shadow, as RGBA (px + 2*ring + pad)."""
    pad = ring
    size = px + 2 * ring + 2 * pad
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad, pad + ring // 4, size - pad, size - pad + ring // 4], fill=(90, 70, 130, 38))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(ring // 2)))
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse([pad, pad, size - pad, size - pad], fill=(255, 255, 255, 255))
    base = Image.alpha_composite(base, disc)
    base.alpha_composite(art_circle(pdf, px), (pad + ring, pad + ring))
    return base


def gradient(w, h, stops):
    """Diagonal gradient (top-left to bottom-right) through the given RGB stops."""
    small = Image.new("RGB", (64, 64))
    pxl = small.load()
    n = len(stops) - 1
    for y in range(64):
        for x in range(64):
            t = (x / 63 * 0.6 + y / 63 * 0.4)
            i = min(int(t * n), n - 1)
            f = t * n - i
            a, b = stops[i], stops[i + 1]
            pxl[x, y] = tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))
    return small.resize((w, h), Image.BICUBIC)


def centered(d, text, font, cx, y, fill):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def logo():
    S = 1000
    im = gradient(S, S, [LAV, (243, 232, 243), PEACH]).convert("RGBA")
    c = ringed(EDITIONS[0][1], 500, 44)
    im.alpha_composite(c, ((S - c.width) // 2, 70))
    d = ImageDraw.Draw(im)
    centered(d, "Peace by Page", ImageFont.truetype(SERIF, 118), S / 2, 735, BRAND_COL)
    im.convert("RGB").save(os.path.join(OUT, "payhip-logo.png"), optimize=True)


def favicon():
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = ringed(EDITIONS[0][1], 440, 18)
    c = c.resize((S, S), Image.LANCZOS)
    im.alpha_composite(c)
    im.save(os.path.join(OUT, "payhip-favicon.png"), optimize=True)


def banner(w, h, name):
    im = gradient(w, h, [LAV, MINT, (236, 236, 228), PEACH]).convert("RGBA")
    d = ImageDraw.Draw(im)
    slim = h / w < 0.3
    title_size = round(h * (0.16 if slim else 0.14))
    title_y = round(h * 0.04)
    centered(d, "Peace by Page", ImageFont.truetype(SERIF, title_size), w / 2, title_y, BRAND_COL)
    art_px = round(h * (0.42 if slim else 0.44))
    ring = round(art_px * 0.09)
    gap = round(w * 0.245)
    top = round(h * (0.27 if slim else 0.25))
    label_f = ImageFont.truetype(SANS, round(h * (0.05 if slim else 0.045)))
    for i, (label, pdf, col) in enumerate(EDITIONS):
        c = ringed(pdf, art_px, ring)
        cx = w / 2 + (i - 1) * gap
        im.alpha_composite(c, (round(cx - c.width / 2), top - ring))
        centered(d, label, label_f, cx, top - ring + c.width - ring * 0.6, col)
    tag_f = ImageFont.truetype(SERIF, round(h * (0.06 if slim else 0.05)))
    centered(d, "Calming printable journals. One page at a time.", tag_f, w / 2, round(h * (0.875 if slim else 0.885)), INK)
    im.convert("RGB").save(os.path.join(OUT, name), optimize=True)


if __name__ == "__main__":
    logo()
    favicon()
    banner(2400, 800, "payhip-banner.png")
    banner(2400, 600, "payhip-banner-slim.png")
    print("done:", OUT)
