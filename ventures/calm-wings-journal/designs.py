"""Full-page coloring designs and the mood-butterfly cell layout.

Every design takes (canvas, box, ink) where box = (x0, y0, x1, y1) in points,
and fills that box with clean, closed line art suitable for coloring.
"""
import math
import random

from reportlab.lib.colors import white

import butterfly_art as art
from butterfly_art import (Tf, Wing, bezier_pts, dashed_path, draw_butterfly, draw_daisy, draw_geometric,
                           draw_leaf, draw_poly, draw_tulip, petal_pts)

LW = 1.05  # base line width for coloring pages (pt)


def fit(box):
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def setup(c, ink, lw=LW):
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setFillColor(white)


# --------------------------------------------------------------------------
# building blocks
# --------------------------------------------------------------------------


def laurel(c, cx, cy, R, a0, a1, n, leaf, ink, lw=LW, flip=False):
    """Leaves along an arc from angle a0 to a1 (degrees)."""
    setup(c, ink, lw)
    pts = [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / 60)),
            cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / 60))) for i in range(61)]
    draw_poly(c, pts, close=False)
    sgn = 1 if a1 > a0 else -1
    for i in range(n):
        t = (i + 0.6) / (n + 0.2)
        a = math.radians(a0 + (a1 - a0) * t)
        px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        tang = math.degrees(a) + 90 * sgn
        draw_leaf(c, px, py, leaf, tang + 38, lw, ink)
        draw_leaf(c, px, py, leaf, tang - 38, lw, ink)
    # berry at the tip
    ex, ey = pts[-1]
    c.circle(ex, ey, leaf * 0.12, stroke=1, fill=1)


def sprig(c, x, y, length, angle, n, leaf, ink, lw=LW, curve=0.25):
    """A curved stem with paired leaves."""
    setup(c, ink, lw)
    a = math.radians(angle)
    ex, ey = x + length * math.cos(a), y + length * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    mid1 = (x + (ex - x) * 0.33 + nx * length * curve, y + (ey - y) * 0.33 + ny * length * curve)
    mid2 = (x + (ex - x) * 0.66 + nx * length * curve, y + (ey - y) * 0.66 + ny * length * curve)
    pts = bezier_pts((x, y), mid1, mid2, (ex, ey), 60)
    draw_poly(c, pts, close=False)
    for i in range(n):
        j = int(10 + (len(pts) - 14) * i / max(n - 1, 1))
        px, py = pts[j]
        qx, qy = pts[j + 2]
        tang = math.degrees(math.atan2(qy - py, qx - px))
        side = 1 if i % 2 == 0 else -1
        draw_leaf(c, px, py, leaf * (0.75 + 0.25 * i / max(n - 1, 1)), tang + 42 * side, lw, ink)
    draw_leaf(c, ex, ey, leaf, math.degrees(a) + curve * 40, lw, ink)


def stem(c, pts, ink, lw=LW):
    setup(c, ink, lw)
    draw_poly(c, bezier_pts(*pts, 50), close=False)


def star(c, x, y, r, ink, lw=LW, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(90 + rot + 36 * i)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    setup(c, ink, lw)
    draw_poly(c, pts, fill=True)


def cloud(c, x, y, w, ink, lw=LW):
    circles = [(x - w * 0.3, y, w * 0.2), (x - w * 0.05, y + w * 0.08, w * 0.27), (x + w * 0.25, y, w * 0.22)]
    pts = []
    n = 120
    x0, x1 = x - w * 0.5, x + w * 0.47
    for i in range(n + 1):
        xx = x0 + (x1 - x0) * i / n
        top = y - 0.0001
        for cx, cy, r in circles:
            if abs(xx - cx) < r:
                top = max(top, cy + math.sqrt(r * r - (xx - cx) ** 2))
        pts.append((xx, top))
    pts += [(x1, y), (x0, y)]
    setup(c, ink, lw)
    draw_poly(c, pts, fill=True)


def crescent(c, x, y, R, ink, lw=LW):
    d, R2 = 0.42 * R, 0.86 * R
    # intersection angle on outer circle
    lo, hi = 0.0, math.pi
    for _ in range(60):
        mid = (lo + hi) / 2
        px, py = R * math.cos(mid), R * math.sin(mid)
        if math.hypot(px - d, py) < R2:
            lo = mid
        else:
            hi = mid
    ao = lo
    bx, by = R * math.cos(ao), R * math.sin(ao)
    ai = math.atan2(by, bx - d)
    pts = [(x + R * math.cos(t), y + R * math.sin(t))
           for t in [ao + (2 * math.pi - 2 * ao) * i / 120 for i in range(121)]]
    pts += [(x + d + R2 * math.cos(t), y + R2 * math.sin(t))
            for t in [(2 * math.pi - ai) - (2 * math.pi - 2 * ai) * i / 120 for i in range(121)]]
    setup(c, ink, lw)
    draw_poly(c, pts, fill=True)


def branch(c, pts4, w0, w1, ink, lw=LW):
    """Tapered branch along a cubic bezier."""
    cl = bezier_pts(*pts4, 80)
    left, right = [], []
    for i, (px, py) in enumerate(cl):
        q = cl[min(i + 1, len(cl) - 1)]
        p0 = cl[max(i - 1, 0)]
        tx, ty = q[0] - p0[0], q[1] - p0[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        w = w0 + (w1 - w0) * i / (len(cl) - 1)
        left.append((px + nx * w, py + ny * w))
        right.append((px - nx * w, py - ny * w))
    setup(c, ink, lw)
    draw_poly(c, left + right[::-1], fill=True)
    return cl


def chrysalis(c, x, y, h, ink, lw=LW):
    setup(c, ink, lw)
    c.line(x, y, x, y - h * 0.08)
    top = y - h * 0.08
    pts = bezier_pts((x, top), (x + h * 0.32, top - h * 0.14), (x + h * 0.22, top - h * 0.8), (x, top - h)) + \
        bezier_pts((x, top - h), (x - h * 0.22, top - h * 0.8), (x - h * 0.32, top - h * 0.14), (x, top))
    draw_poly(c, pts, fill=True)
    for k in (0.3, 0.48, 0.66):
        yy = top - h * k
        wd = h * (0.2 - 0.12 * (k - 0.3))
        draw_poly(c, bezier_pts((x - wd, yy), (x - wd / 2, yy - h * 0.05), (x + wd / 2, yy - h * 0.05),
                                (x + wd, yy), 20), close=False)
    for dx in (-0.08, 0.08):
        c.circle(x + h * dx, top - h * 0.18, h * 0.025, stroke=1, fill=0)


def banner(c, cx, cy, w, h, txt, ink, lw=LW, font="Accent"):
    setup(c, ink, lw)
    tail = h * 0.9
    for s in (-1, 1):
        x_in = cx + s * (w / 2 - tail * 0.4)
        x_out = cx + s * (w / 2 + tail)
        pts = [(x_in, cy - h * 0.3), (x_out, cy - h * 0.3), (x_out - s * tail * 0.4, cy + h * 0.2),
               (x_out, cy + h * 0.7), (x_in, cy + h * 0.7)]
        draw_poly(c, pts, fill=True)
    draw_poly(c, [(cx - w / 2, cy), (cx + w / 2, cy), (cx + w / 2, cy + h), (cx - w / 2, cy + h)], fill=True)
    c.setFillColor(ink)
    c.setFont(font, h * 0.62)
    c.drawCentredString(cx, cy + h * 0.28, txt)
    c.setFillColor(white)


def ring_beads(c, cx, cy, r, n, br, ink, lw=LW):
    setup(c, ink, lw)
    for i in range(n):
        a = 2 * math.pi * i / n
        c.circle(cx + r * math.cos(a), cy + r * math.sin(a), br, stroke=1, fill=1)


# --------------------------------------------------------------------------
# SOS coloring pages
# --------------------------------------------------------------------------


def mandala(c, box, ink, n=8, simple=False):
    cx, cy, W, H = fit(box)
    R = min(W, H) / 2 - 4
    c.saveState()
    setup(c, ink, LW * 1.15)
    c.circle(cx, cy, R, stroke=1, fill=0)
    c.circle(cx, cy, R * 0.9, stroke=1, fill=0)
    ring_beads(c, cx, cy, R * 0.95, 40 if not simple else 28, R * 0.034, ink)
    setup(c, ink, LW)
    # big petals between butterflies
    for i in range(n):
        a = 360 * (i + 0.5) / n
        outer = petal_pts(cx, cy, R * 0.5, R * (0.1 if n == 8 else 0.13), a, base=R * 0.38)
        draw_poly(c, outer, fill=True)
        inner = petal_pts(cx, cy, R * 0.34, R * (0.055 if n == 8 else 0.07), a, base=R * 0.46)
        draw_poly(c, inner, fill=False)
    # butterflies facing outward
    style = "mandala" if not simple else "simple"
    for i in range(n):
        a = 360 * i / n
        bx = cx + R * 0.66 * math.cos(math.radians(a))
        by = cy + R * 0.66 * math.sin(math.radians(a))
        draw_butterfly(c, bx, by, R * (0.21 if n == 8 else 0.22), style, angle=a - 90, lw=LW * 0.85, ink=ink,
                       segments=False)
    # inner ring
    setup(c, ink, LW)
    c.circle(cx, cy, R * 0.4, stroke=1, fill=1)
    m = 16 if not simple else 12
    for i in range(m):
        a = 360 * i / m
        draw_poly(c, petal_pts(cx, cy, R * 0.17, R * 0.045, a, base=R * 0.22), fill=True)
    for i in range(m):
        a = math.radians(360 * (i + 0.5) / m)
        c.circle(cx + R * 0.35 * math.cos(a), cy + R * 0.35 * math.sin(a), R * 0.018, stroke=1, fill=0)
    c.circle(cx, cy, R * 0.21, stroke=1, fill=1)
    draw_daisy(c, cx, cy, R * 0.19, petals=10, lw=LW, ink=ink, inner=False)
    c.restoreState()


def geometric_page(c, box, ink):
    cx, cy, W, H = fit(box)
    R = min(W, H * 0.9) / 2
    c.saveState()
    setup(c, ink, LW)
    hexes = []
    for k in (1.0, 0.92):
        pts = [(cx + R * k * math.cos(math.radians(30 + 60 * i)), cy + R * k * math.sin(math.radians(30 + 60 * i)))
               for i in range(6)]
        hexes.append(pts)
        draw_poly(c, pts)
    # zigzag triangles between hexagons
    o, inn = hexes
    for i in range(6):
        a, b = o[i], o[(i + 1) % 6]
        p, q = inn[i], inn[(i + 1) % 6]
        segs = 6
        for j in range(segs):
            t0, t1 = j / segs, (j + 1) / segs
            tm = (t0 + t1) / 2
            A = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            B = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            M = (p[0] + (q[0] - p[0]) * tm, p[1] + (q[1] - p[1]) * tm)
            draw_poly(c, [A, M, B], close=False)
    # triangular lattice inside the inner hexagon
    p = c.beginPath()
    p.moveTo(*inn[0])
    for q in inn[1:]:
        p.lineTo(*q)
    p.close()
    c.clipPath(p, stroke=0, fill=0)
    step = R * 0.92 / 3
    for ang in (0, 60, 120):
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        for k in range(-8, 9):
            ox, oy = cx + nx * step * k * math.sin(math.radians(60)), cy + ny * step * k * math.sin(math.radians(60))
            c.line(ox - dx * R * 2, oy - dy * R * 2, ox + dx * R * 2, oy + dy * R * 2)
    c.restoreState()
    draw_geometric(c, cx, cy + R * 0.08, R * 0.62, lw=LW, ink=ink, variant=0, halo=14)


# --------------------------------------------------------------------------
# 13 weekly reward designs
# --------------------------------------------------------------------------


def wk_classic_laurel(c, box, ink):
    cx, cy, W, H = fit(box)
    s = W * 0.4
    by = cy + H * 0.1
    laurel(c, cx - 4, by - s * 0.15, s * 1.25, 250, 150, 7, s * 0.2, ink)
    laurel(c, cx + 4, by - s * 0.15, s * 1.25, 290, 390, 7, s * 0.2, ink)
    draw_butterfly(c, cx, by, s, "classic", lw=LW, ink=ink)
    draw_butterfly(c, cx - W * 0.36, by + s * 1.05, s * 0.22, "simple", angle=18, lw=LW * 0.9, ink=ink, segments=False)
    draw_butterfly(c, cx + W * 0.36, by + s * 0.95, s * 0.18, "simple", angle=-20, lw=LW * 0.9, ink=ink, segments=False)


def wk_swallowtail_flower(c, box, ink):
    cx, cy, W, H = fit(box)
    s = W * 0.3
    bx, by = cx + W * 0.08, cy + H * 0.22
    # flowers at the bottom
    base = box[1] + 10
    stem(c, ((cx - W * 0.05, base), (cx - W * 0.08, base + H * 0.15), (cx - W * 0.18, base + H * 0.25),
             (cx - W * 0.2, base + H * 0.36)), ink)
    stem(c, ((cx + W * 0.05, base), (cx + W * 0.1, base + H * 0.12), (cx + W * 0.24, base + H * 0.14),
             (cx + W * 0.28, base + H * 0.24)), ink)
    stem(c, ((cx, base), (cx, base + H * 0.06), (cx - W * 0.02, base + H * 0.1), (cx - W * 0.01, base + H * 0.14)),
         ink)
    draw_leaf(c, cx - W * 0.1, base + H * 0.17, W * 0.13, 160, LW, ink)
    draw_leaf(c, cx + W * 0.13, base + H * 0.12, W * 0.12, 30, LW, ink)
    draw_leaf(c, cx - W * 0.02, base + H * 0.05, W * 0.1, 120, LW, ink)
    draw_daisy(c, cx - W * 0.2, base + H * 0.36, W * 0.12, 14, LW, ink)
    draw_daisy(c, cx + W * 0.28, base + H * 0.24, W * 0.08, 11, LW, ink, rotate=10)
    draw_tulip(c, cx - W * 0.01, base + H * 0.1, W * 0.1, LW, ink)
    draw_butterfly(c, bx, by, s, "swallowtail", angle=-12, lw=LW, ink=ink)


def wk_wreath_peacock(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.42
    laurel(c, cx, cy, R, 268, 95, 10, R * 0.17, ink)
    laurel(c, cx, cy, R, 272, 445, 10, R * 0.17, ink)
    draw_butterfly(c, cx, cy + R * 0.08, R * 0.58, "peacock", lw=LW, ink=ink)
    for a in (270,):
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        draw_daisy(c, x, y, R * 0.12, 10, LW, ink)


def wk_meadow(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    gy = y0 + H * 0.2
    setup(c, ink, LW)
    # rolling hills
    hill1 = bezier_pts((x0, gy + H * 0.08), (x0 + W * 0.3, gy + H * 0.2), (x0 + W * 0.6, gy - H * 0.02),
                       (x1, gy + H * 0.1), 80)
    draw_poly(c, hill1, close=False)
    hill2 = bezier_pts((x0, gy - H * 0.04), (x0 + W * 0.4, gy + H * 0.06), (x0 + W * 0.7, gy - H * 0.1),
                       (x1, gy - H * 0.02), 80)
    draw_poly(c, hill2, close=False)
    art.draw_grass(c, x0 + 4, x1 - 4, y0 + 4, H * 0.07, LW * 0.9, ink, seed=5, density=0.22)
    flowers = [(0.12, 0.3, 0.07, "d"), (0.3, 0.22, 0.055, "t"), (0.52, 0.28, 0.08, "d"),
               (0.72, 0.2, 0.06, "t"), (0.88, 0.32, 0.065, "d")]
    for fx, fh, fr, kind in flowers:
        x = x0 + W * fx
        top = y0 + H * fh
        stem(c, ((x, y0 + 6), (x - 4, y0 + H * fh * 0.4), (x + 4, y0 + H * fh * 0.7), (x, top)), ink)
        draw_leaf(c, x, y0 + H * fh * 0.4, W * 0.05, 140 if fx < 0.5 else 40, LW, ink)
        if kind == "d":
            draw_daisy(c, x, top, W * fr, 11, LW, ink)
        else:
            draw_tulip(c, x, top - W * fr * 0.4, W * fr * 1.2, LW, ink)
    cloud(c, x0 + W * 0.2, y1 - H * 0.1, W * 0.22, ink)
    cloud(c, x0 + W * 0.82, y1 - H * 0.16, W * 0.16, ink)
    path = bezier_pts((x0 + W * 0.15, cy - H * 0.05), (x0 + W * 0.3, cy + H * 0.25), (x0 + W * 0.55, cy - H * 0.1),
                      (x0 + W * 0.66, cy + H * 0.12), 60)
    dashed_path(c, path, LW * 0.8, ink, (2, 4))
    draw_butterfly(c, x0 + W * 0.74, cy + H * 0.15, W * 0.17, "round", angle=-18, lw=LW, ink=ink)
    draw_butterfly(c, x0 + W * 0.28, cy + H * 0.2, W * 0.12, "petal", angle=14, lw=LW, ink=ink)
    draw_butterfly(c, x0 + W * 0.45, cy - H * 0.08, W * 0.075, "simple", angle=-8, lw=LW, ink=ink)


def wk_framed_round(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    m = 52
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + m, y0 + m, W - 2 * m, H - 2 * m, 26, stroke=1, fill=0)
    setup(c, ink, LW * 0.8)
    c.setDash(1, 5)
    c.roundRect(x0 + m + 12, y0 + m + 12, W - 2 * m - 24, H - 2 * m - 24, 18, stroke=1, fill=0)
    c.setDash()
    for (x, y, a) in ((x0 + m, y0 + m, 45), (x1 - m, y0 + m, 135), (x0 + m, y1 - m, -45), (x1 - m, y1 - m, -135)):
        draw_leaf(c, x, y, W * 0.1, a + 28, LW, ink)
        draw_leaf(c, x, y, W * 0.1, a - 28, LW, ink)
        draw_daisy(c, x, y, W * 0.06, 10, LW, ink)
    draw_butterfly(c, cx, cy + H * 0.04, W * 0.36, "round", lw=LW, ink=ink)
    for i in range(5):
        x = cx - W * 0.24 + i * W * 0.12
        draw_daisy(c, x, y0 + m + 60, W * 0.035, 8, LW, ink, inner=False)


def wk_two_dancing(c, box, ink):
    cx, cy, W, H = fit(box)
    loop = []
    for i in range(201):
        t = 2 * math.pi * i / 200
        loop.append((cx + W * 0.36 * math.sin(t), cy + H * 0.2 * math.sin(2 * t)))
    dashed_path(c, loop, LW * 0.8, ink, (2, 5))
    draw_butterfly(c, cx - W * 0.2, cy + H * 0.2, W * 0.24, "monarch", angle=18, lw=LW, ink=ink)
    draw_butterfly(c, cx + W * 0.2, cy - H * 0.17, W * 0.22, "petal", angle=-16, lw=LW, ink=ink)
    for (dx, dy, r) in ((0.35, 0.33, 0.035), (-0.38, -0.3, 0.03), (0.0, 0.42, 0.025), (0.05, -0.42, 0.028),
                        (-0.42, 0.05, 0.02), (0.42, 0.02, 0.022)):
        star(c, cx + W * dx, cy + H * dy, W * r, ink, LW * 0.9, rot=dx * 50)


def wk_sunburst_lacy(c, box, ink):
    cx, cy, W, H = fit(box)
    R0, R1, R2 = W * 0.37, W * 0.4, W * 0.49
    setup(c, ink, LW)
    n = 28
    for i in range(n):
        a = 360 * (i + 0.5) / n
        draw_poly(c, petal_pts(cx, cy, (R2 - R1) * 1.05, W * 0.032, a, base=R1 - 2), fill=True)
        draw_poly(c, petal_pts(cx, cy, (R2 - R1) * 0.55, W * 0.012, a, base=R1 + 6), fill=False)
    c.circle(cx, cy, R1, stroke=1, fill=0)
    c.circle(cx, cy, R0, stroke=1, fill=0)
    ring_beads(c, cx, cy, (R0 + R1) / 2, 48, (R1 - R0) * 0.32, ink)
    draw_butterfly(c, cx, cy + W * 0.035, W * 0.3, "lacy", lw=LW, ink=ink)


def wk_mini_mandala(c, box, ink):
    mandala(c, box, ink, n=6, simple=True)


def wk_geo_hex(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.47
    setup(c, ink, LW)
    hx = {}
    for k in (1.0, 0.88, 0.62):
        hx[k] = [(cx + R * k * math.cos(math.radians(60 * i)), cy + R * k * math.sin(math.radians(60 * i)))
                 for i in range(6)]
        draw_poly(c, hx[k])
    for i in range(6):
        draw_poly(c, [hx[0.62][i], hx[1.0][i]], close=False)
        j = (i + 1) % 6
        m_in = ((hx[0.62][i][0] + hx[0.62][j][0]) / 2, (hx[0.62][i][1] + hx[0.62][j][1]) / 2)
        m_mid = ((hx[0.88][i][0] + hx[0.88][j][0]) / 2, (hx[0.88][i][1] + hx[0.88][j][1]) / 2)
        draw_poly(c, [hx[0.62][i], m_mid, hx[0.62][j]], close=False)
        draw_poly(c, [m_in, m_mid], close=False)
        for t in (0.25, 0.75):
            p = (hx[0.88][i][0] + (hx[0.88][j][0] - hx[0.88][i][0]) * t,
                 hx[0.88][i][1] + (hx[0.88][j][1] - hx[0.88][i][1]) * t)
            q = (hx[1.0][i][0] + (hx[1.0][j][0] - hx[1.0][i][0]) * t,
                 hx[1.0][i][1] + (hx[1.0][j][1] - hx[1.0][i][1]) * t)
            draw_poly(c, [p, q], close=False)
    draw_geometric(c, cx, cy + R * 0.06, R * 0.5, lw=LW, ink=ink, variant=1, halo=10)


def wk_branch_scallop(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    cl = branch(c, ((x0 - 2, cy - H * 0.05), (x0 + W * 0.3, cy - H * 0.02), (x0 + W * 0.55, cy - H * 0.2),
                    (x1 - W * 0.05, cy - H * 0.26)), 9, 3, ink)
    for i, t in enumerate((0.15, 0.3, 0.45, 0.62, 0.78, 0.93)):
        px, py = cl[int(t * 80)]
        side = 1 if i % 2 == 0 else -1
        draw_leaf(c, px, py, W * 0.15, 90 * side + (-20 if side > 0 else 20) - 15 * t, LW, ink)
    # twig with blossom
    px, py = cl[38]
    stem(c, ((px, py), (px + 10, py - 30), (px + 30, py - 60), (px + 26, py - H * 0.15)), ink)
    draw_daisy(c, px + 26, py - H * 0.15, W * 0.07, 9, LW, ink)
    draw_butterfly(c, cx + W * 0.12, cy + H * 0.18, W * 0.3, "scallop", angle=-10, lw=LW, ink=ink)
    draw_butterfly(c, x0 + W * 0.18, y1 - H * 0.12, W * 0.08, "simple", angle=16, lw=LW, ink=ink, segments=False)


def wk_moon_petal(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    crescent(c, x0 + W * 0.22, y1 - H * 0.16, W * 0.13, ink)
    cloud(c, x0 + W * 0.3, y1 - H * 0.28, W * 0.22, ink)
    cloud(c, x1 - W * 0.22, y0 + H * 0.16, W * 0.26, ink)
    for (fx, fy, r) in ((0.62, 0.92, 0.03), (0.82, 0.84, 0.04), (0.9, 0.62, 0.025), (0.08, 0.55, 0.03),
                        (0.14, 0.3, 0.04), (0.42, 0.08, 0.03), (0.7, 0.32, 0.022), (0.5, 0.95, 0.02),
                        (0.06, 0.12, 0.022)):
        star(c, x0 + W * fx, y0 + H * fy, W * r, ink, LW * 0.9, rot=fx * 40)
    draw_butterfly(c, cx + W * 0.05, cy + H * 0.02, W * 0.34, "petal", angle=8, lw=LW, ink=ink)
    for (fx, fy) in ((0.3, 0.68), (0.75, 0.55), (0.3, 0.38), (0.6, 0.22)):
        c.circle(x0 + W * fx, y0 + H * fy, 2.2, stroke=1, fill=0)


DECO = dict(
    fore=dict(root=(0.03, 0.06), a0=82, a1=-8, prof=[0, 0.74, 0.96, 1.0, 0.93, 0.78, 0.6, 0.0]),
    hind=dict(root=(0.03, -0.02), a0=-12, a1=-98, prof=[0, 0.6, 0.74, 0.75, 0.68, 0.52, 0.0], scallop=5,
              sdepth=0.08),
    fpat=[("band", 0.3), ("band", 0.56), ("band", 0.8), ("veins", 4, 0.3, 0.56, 0.0),
          ("veins", 7, 0.56, 0.8, 0.0), ("edge", 9, 0.9, 0.022)],
    hpat=[("band", 0.32), ("band", 0.6), ("veins", 3, 0.32, 0.6, 0.0), ("spots", 4, 0.8, 0.05)],
)


def wk_deco_arch(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    aw = W * 0.86
    ax0, ax1 = cx - aw / 2, cx + aw / 2
    top_c = y1 - aw / 2 - 6
    for k, lw in ((0, LW * 1.2), (12, LW * 0.9)):
        pts = [(ax0 + k, y0 + 20 + k)]
        for i in range(61):
            a = math.pi - math.pi * i / 60
            pts.append((cx + (aw / 2 - k) * math.cos(a), top_c + (aw / 2 - k) * math.sin(a)))
        pts.append((ax1 - k, y0 + 20 + k))
        setup(c, ink, lw)
        draw_poly(c, pts)
    # zigzag floor
    setup(c, ink, LW)
    zy = y0 + 20 + 12
    n = 14
    for i in range(n):
        xa = ax0 + 12 + (aw - 24) * i / n
        xb = ax0 + 12 + (aw - 24) * (i + 1) / n
        draw_poly(c, [(xa, zy), ((xa + xb) / 2, zy + 22), (xb, zy)], close=False)
    c.line(ax0 + 12, zy + 22, ax1 - 12, zy + 22)
    fy = zy + 22
    for fx, h, kind in ((-0.27, 0.27, "d"), (-0.13, 0.2, "t"), (0.0, 0.3, "d"), (0.13, 0.2, "t"), (0.27, 0.25, "d")):
        x = cx + W * fx
        top = fy + H * h
        stem(c, ((x, fy), (x - 3, fy + H * h * 0.4), (x + 3, fy + H * h * 0.7), (x, top)), ink)
        draw_leaf(c, x, fy + H * h * 0.35, W * 0.06, 140 if fx < 0 else 40, LW, ink)
        if kind == "d":
            draw_daisy(c, x, top, W * 0.065, 11, LW, ink)
        else:
            draw_tulip(c, x, top - W * 0.03, W * 0.09, LW, ink)
    draw_butterfly(c, cx, cy + H * 0.2, W * 0.3, DECO, lw=LW, ink=ink)


def wk_finale(c, box, ink, days=90):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    cl = branch(c, ((x0 - 2, y1 - H * 0.08), (x0 + W * 0.2, y1 - H * 0.05), (x0 + W * 0.4, y1 - H * 0.12),
                    (x0 + W * 0.55, y1 - H * 0.1)), 7, 2.5, ink)
    for i, t in enumerate((0.25, 0.5, 0.8)):
        px, py = cl[int(t * 80)]
        draw_leaf(c, px, py, W * 0.1, 70 if i % 2 else -60, LW, ink)
    px, py = cl[26]
    chrysalis(c, px, py - 4, H * 0.14, ink)
    path = bezier_pts((px + 8, py - H * 0.18), (px + W * 0.1, py - H * 0.35), (cx, cy + H * 0.15),
                      (cx + W * 0.08, cy + H * 0.06), 50)
    dashed_path(c, path, LW * 0.8, ink, (2, 5))
    style = dict(
        fore=dict(root=(0.03, 0.06), a0=82, a1=-8, prof=[0, 0.74, 0.96, 1.02, 0.95, 0.8, 0.6, 0.0],
                  scallop=9, sdepth=0.05),
        hind=dict(root=(0.03, -0.02), a0=-12, a1=-98, prof=[0, 0.6, 0.74, 0.76, 0.7, 0.54, 0.0],
                  scallop=6, sdepth=0.09),
        fpat=[("band", 0.4), ("veins", 4, 0.0, 0.4, 0.05), ("eye", 0.45, 0.66, 0.1, 2), ("band", 0.86),
              ("edge", 9, 0.93, 0.016)],
        hpat=[("band", 0.42), ("veins", 3, 0.0, 0.42, 0.05), ("spots", 3, 0.68, 0.06), ("band", 0.86)],
    )
    draw_butterfly(c, cx + W * 0.1, cy - H * 0.04, W * 0.32, style, lw=LW, ink=ink)
    banner(c, cx, y0 + H * 0.06, W * 0.36, 34, f"{days} days", ink)
    for (fx, fy) in ((0.85, 0.85), (0.12, 0.35), (0.9, 0.3)):
        star(c, x0 + W * fx, y0 + H * fy, W * 0.03, ink, LW * 0.9)


WEEKLY = [wk_classic_laurel, wk_swallowtail_flower, wk_wreath_peacock, wk_meadow, wk_framed_round,
          wk_two_dancing, wk_sunburst_lacy, wk_mini_mandala, wk_geo_hex, wk_branch_scallop, wk_moon_petal,
          wk_deco_arch, wk_finale]

WEEKLY_TITLES = ["Laurel and wings", "Swallowtail garden", "Peacock wreath", "Meadow day", "Garden frame",
                 "Dancing pair", "Sunburst", "Little mandala", "Hexagon wings", "Resting on a branch",
                 "Night flight", "Garden arch", "You made it"]


# --------------------------------------------------------------------------
# mood butterfly: 30 numbered cells
# --------------------------------------------------------------------------


def _splits(w, n, k0, k1):
    """Split u in [0,1] into n parts of equal band area."""
    N = 400
    cum = [0.0]
    for i in range(1, N + 1):
        u = (i - 0.5) / N
        cum.append(cum[-1] + w.r(u) ** 2)
    tot = cum[-1]
    out = [0.0]
    j = 0
    for q in range(1, n):
        target = tot * q / n
        while cum[j] < target:
            j += 1
        out.append(j / N)
    out.append(1.0)
    return out


def mood_cells(c, box, ink, muted, start_day=1):
    cx, cy, W, H = fit(box)
    size = min(W / 2.15, H / 1.72)
    fore = Wing((0.03, 0.06), 82, -8, [0, 0.74, 0.96, 1.0, 0.93, 0.78, 0.6, 0.0])
    hind = Wing((0.03, -0.02), -12, -98, [0, 0.6, 0.74, 0.75, 0.68, 0.52, 0.0])
    plan = [(fore, [(0.5, 1.0, 5), (0.0, 0.5, 3)]), (hind, [(0.0, 0.5, 2), (0.5, 1.0, 5)])]
    cyy = cy + size * 0.06
    day = start_day
    c.saveState()
    c.setLineJoin(1)
    labels = []
    order = []
    for mirror in (True, False):
        for w, bands in plan:
            order.append((mirror, w, bands, day))
            day += sum(nb for _, _, nb in bands)
    draw_order = [o for o in order if o[1] is hind] + [o for o in order if o[1] is fore]
    for mirror, w, bands, d0 in draw_order:
        tf = Tf(cx, cyy, size, 0, mirror)
        setup(c, ink, LW * 1.3)
        draw_poly(c, [tf(p) for p in w.outline()], fill=True)
        dd = d0
        for k0, k1, n in bands:
            sp = _splits(w, n, k0, k1)
            for i in range(n):
                ua, ub = sp[i], sp[i + 1]
                outer = w.outline(k1, 60, ua, ub)
                inner = w.outline(k0, 60, ua, ub)[::-1] if k0 > 0 else [w.root]
                setup(c, ink, LW)
                draw_poly(c, [tf(p) for p in outer + inner])
                um = (ua + ub) / 2
                km = (k0 + k1) / 2 if k0 > 0 else 0.66 * k1
                labels.append((tf(w.pt(um, km)), dd, w is hind))
                dd += 1
    c.setFillColor(muted)
    c.setFont("Sans", 8)
    for (tx, ty), num, _ in labels:
        c.drawCentredString(tx, ty - 2.8, str(num))
    art.draw_body(c, Tf(cx, cyy, size), LW, ink)
    c.restoreState()
