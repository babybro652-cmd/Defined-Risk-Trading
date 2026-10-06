"""Payhip Store Builder images for Peace by Page (store design, 10/6).

Builds, into ../brand/store/:
  hero-art.png            1600 x 1200  homepage hero for an "Image with Text" section (no text in the art)
  hero-desktop.png        2400 x 1000  full-width hero for a Slideshow section (text baked in, left side)
  hero-mobile.png         1080 x 1350  phone version of hero-desktop (text on top, journals below)
  edition-calm-wings.png  1200 x 1200  collection cover, Calm Wings
  edition-calm-petals.png 1200 x 1200  collection cover, Calm Petals
  edition-calm-nights.png 1200 x 1200  collection cover, Calm Nights
  free-sampler.png        1200 x 1200  free 7-day sampler promo tile
  about.png               1200 x 1200  About section graphic (inside pages, no text)
  header-logo.png         1200 x 300   wide logo for the store header, transparent
  social-share.png        1200 x 630   social preview image for custom pages

Pages are rendered from the real product PDFs, so the images always match the files.
Run from anywhere: python3 launch/make_store_assets.py
"""
import os
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_brand_assets import (BRAND_COL, EDITIONS, INK, LAV, MINT, PEACH, ROOT, SANS, SERIF,  # noqa: E402
                               centered, gradient, ringed)

OUT = os.path.join(ROOT, "brand", "store")
SERIF_REG = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

J = {  # edition key -> journal PDF
    "wings": EDITIONS[0][1],
    "petals": EDITIONS[1][1],
    "nights": EDITIONS[2][1],
}
SAMPLER = "editions/sampler/PeaceByPage_7Day_Sampler_Letter.pdf"

ED = {  # key: (name, tagline, accent rgb, gradient stops)
    "wings": ("Calm Wings", "Soft butterflies", (126, 107, 181),
              [(231, 223, 245), (246, 243, 251), (215, 238, 234)]),
    "petals": ("Calm Petals", "Gentle botanicals", (84, 128, 104),
               [(222, 233, 213), (244, 247, 241), (245, 222, 218)]),
    "nights": ("Calm Nights", "Moon and stars, for evenings", (61, 65, 128),
               [(220, 227, 245), (245, 244, 251), (246, 234, 203)]),
}

_cache = {}


def page(pdf, idx, width):
    """Render one PDF page as an RGB image `width` px wide."""
    key = (pdf, idx, width)
    if key not in _cache:
        doc = pymupdf.open(os.path.join(ROOT, pdf))
        pg = doc[idx]
        zoom = width * 1.6 / pg.rect.width
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        h = round(width * pix.height / pix.width)
        _cache[key] = im.resize((width, h), Image.LANCZOS)
    return _cache[key]


def paper(im, angle=0, shadow=0.06):
    """A page with a thin edge and a soft drop shadow, rotated by `angle` degrees. Returns RGBA."""
    w, h = im.size
    pad = round(w * 0.12)
    base = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    off = round(w * shadow * 0.35)
    ImageDraw.Draw(sh).rectangle([pad + off // 2, pad + off, pad + w + off // 2, pad + h + off], fill=(70, 60, 110, 70))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(round(w * shadow * 0.5))))
    pg = im.convert("RGBA")
    ImageDraw.Draw(pg).rectangle([0, 0, w - 1, h - 1], outline=(220, 218, 230, 255), width=max(1, w // 400))
    base.alpha_composite(pg, (pad, pad))
    if angle:
        base = base.rotate(angle, resample=Image.BICUBIC, expand=True)
    return base


def place(canvas, layer, cx, cy):
    canvas.alpha_composite(layer, (round(cx - layer.width / 2), round(cy - layer.height / 2)))


def fan_covers(canvas, cx, cy, width):
    """Three journal covers fanned out: Petals left, Nights right, Wings in front."""
    side = round(width * 0.86)
    place(canvas, paper(page(J["petals"], 0, side), 9), cx - width * 0.74, cy + width * 0.04)
    place(canvas, paper(page(J["nights"], 0, side), -9), cx + width * 0.74, cy + width * 0.04)
    place(canvas, paper(page(J["wings"], 0, width), 0), cx, cy)


def font(path, size):
    return ImageFont.truetype(path, round(size))


def save(im, name):
    im.convert("RGB").save(os.path.join(OUT, name), optimize=True)
    print("  ", name, im.size)


def soft_bg(w, h):
    return gradient(w, h, [LAV, MINT, (236, 236, 228), PEACH]).convert("RGBA")


def hero_art():
    W, H = 1600, 1200
    im = soft_bg(W, H)
    fan_covers(im, W / 2, H * 0.5, 560)
    save(im, "hero-art.png")


def hero_desktop():
    W, H = 2400, 1000
    im = soft_bg(W, H)
    fan_covers(im, W * 0.72, H * 0.5, 470)
    d = ImageDraw.Draw(im)
    x = W * 0.075
    d.text((x, H * 0.20), "Peace by Page", font=font(SERIF, 64), fill=BRAND_COL)
    d.text((x, H * 0.31), "Five calm minutes", font=font(SERIF_REG, 112), fill=INK)
    d.text((x, H * 0.44), "a day.", font=font(SERIF_REG, 112), fill=INK)
    sub = font(SANS, 44)
    d.text((x, H * 0.62), "Printable anxiety journals in three", font=sub, fill=INK)
    d.text((x, H * 0.68), "gentle editions. Print at home.", font=sub, fill=INK)
    save(im, "hero-desktop.png")


def hero_mobile():
    W, H = 1080, 1350
    im = soft_bg(W, H)
    d = ImageDraw.Draw(im)
    centered(d, "Peace by Page", font(SERIF, 64), W / 2, H * 0.06, BRAND_COL)
    centered(d, "Five calm minutes a day.", font(SERIF_REG, 84), W / 2, H * 0.13, INK)
    centered(d, "Printable anxiety journals in three", font(SANS, 40), W / 2, H * 0.225, INK)
    centered(d, "gentle editions. Print at home.", font(SANS, 40), W / 2, H * 0.26, INK)
    fan_covers(im, W / 2, H * 0.64, 400)
    save(im, "hero-mobile.png")


def edition_cover(key):
    name, tag, col, stops = ED[key]
    S = 1200
    im = gradient(S, S, stops).convert("RGBA")
    # a daily page peeks out behind the cover
    place(im, paper(page(J[key], 18, 440), -7), S * 0.60, S * 0.43)
    place(im, paper(page(J[key], 0, 460), 4), S * 0.42, S * 0.42)
    d = ImageDraw.Draw(im)
    band_top = S * 0.78
    d.rectangle([0, band_top, S, S], fill=(255, 255, 255, 235))
    centered(d, name, font(SERIF, 96), S / 2, band_top + 26, col)
    centered(d, tag, font(SANS, 42), S / 2, band_top + 152, INK)
    save(im, f"edition-calm-{key}.png")


def free_sampler():
    S = 1200
    im = gradient(S, S, [PEACH, (247, 238, 243), LAV]).convert("RGBA")
    place(im, paper(page(SAMPLER, 12, 400), 8), S * 0.70, S * 0.58)
    place(im, paper(page(SAMPLER, 3, 400), -6), S * 0.32, S * 0.58)
    place(im, paper(page(SAMPLER, 0, 440), 0), S * 0.51, S * 0.55)
    d = ImageDraw.Draw(im)
    centered(d, "Try a week, free", font(SERIF, 104), S / 2, S * 0.045, BRAND_COL)
    centered(d, "7-Day Sampler  |  Letter and A4", font(SANS, 44), S / 2, S * 0.155, INK)
    # FREE badge
    r = 105
    bx, by = S * 0.80, S * 0.30
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(107, 90, 166, 255), outline=(255, 255, 255, 255), width=8)
    f = font(SANS_BOLD, 62)
    tw = d.textlength("FREE", font=f)
    d.text((bx - tw / 2, by - 38), "FREE", font=f, fill=(255, 255, 255))
    save(im, "free-sampler.png")


def about():
    S = 1200
    im = gradient(S, S, [MINT, (246, 243, 251), PEACH]).convert("RGBA")
    place(im, paper(page(J["petals"], 27, 420), -9), S * 0.29, S * 0.52)   # reward coloring page
    place(im, paper(page(J["nights"], 9, 420), 9), S * 0.71, S * 0.52)    # box breathing
    place(im, paper(page(J["wings"], 18, 480), 0), S * 0.50, S * 0.50)    # daily page
    save(im, "about.png")


def header_logo():
    W, H = 1200, 300
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c = ringed(J["wings"], 210, 14).resize((262, 262), Image.LANCZOS)
    im.alpha_composite(c, (40, (H - c.height) // 2))
    d = ImageDraw.Draw(im)
    d.text((330, 62), "Peace by Page", font=font(SERIF, 140), fill=BRAND_COL)
    im.save(os.path.join(OUT, "header-logo.png"), optimize=True)
    print("   header-logo.png", im.size)


def social_share():
    W, H = 1200, 630
    im = soft_bg(W, H)
    fan_covers(im, W * 0.725, H * 0.52, 240)
    d = ImageDraw.Draw(im)
    d.text((70, 150), "Peace by Page", font=font(SERIF, 72), fill=BRAND_COL)
    d.text((72, 265), "Calming printable journals.", font=font(SANS, 34), fill=INK)
    d.text((72, 312), "One page at a time.", font=font(SANS, 34), fill=INK)
    d.text((72, 400), "Free 7-day sampler inside", font=font(SERIF, 34), fill=BRAND_COL)
    save(im, "social-share.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hero_art()
    hero_desktop()
    hero_mobile()
    for k in ("wings", "petals", "nights"):
        edition_cover(k)
    free_sampler()
    about()
    header_logo()
    social_share()
    print("done:", OUT)
