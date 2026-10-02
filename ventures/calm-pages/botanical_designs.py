"""Calm Petals coloring pages and the mood flower.

Every design takes (canvas, box, ink) where box = (x0, y0, x1, y1) in points and fills that
box with clean, closed line art for coloring. Built on botanical_art.py.
"""
import math
import random

from reportlab.lib.colors import white

import botanical_art as b
from botanical_art import (Path, bell, bouquet, bud, cosmos, curve, eucalyptus, fern, fern_path, fiddlehead,
                           forget_me_not, lavender, leaf, leafy_sprig, ribbon_stem, rosette, setup, spline, stroke,
                           wild_rose)
from butterfly_art import bezier_pts, draw_daisy, draw_grass, draw_poly, petal_pts
from designs import banner, cloud

LW = 1.05


def fit(box):
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def ring(c, cx, cy, r, ink, lw=LW, fill=False):
    setup(c, ink, lw)
    c.circle(cx, cy, r, stroke=1, fill=1 if fill else 0)


def lotus_petal(cx, cy, r0, r1, half_w, angle, n=30):
    """A pointed petal from radius r0 to r1, widest a third of the way out."""
    a = math.radians(angle)
    pts = []
    for i in range(n + 1):
        t = i / n
        w = half_w * math.sin(math.pi * t ** 0.8) ** 0.75
        pts.append((r0 + (r1 - r0) * t, w))
    pts += [(x, -y) for x, y in reversed(pts)]
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


# --------------------------------------------------------------------------
# SOS pages
# --------------------------------------------------------------------------


def mandala(c, box, ink, n=8, simple=False):
    """Botanical mandala: lotus petals, leafy stems, a petal ring and a ranunculus heart."""
    cx, cy, W, H = fit(box)
    R = min(W, H) / 2 - 4
    c.saveState()
    # outer laurel ring
    ring(c, cx, cy, R, ink, LW * 1.15)
    ring(c, cx, cy, R * 0.88, ink, LW)
    m = 44 if not simple else 30
    for i in range(m):
        a = 360 * i / m
        x, y = cx + R * 0.94 * math.cos(math.radians(a)), cy + R * 0.94 * math.sin(math.radians(a))
        leaf(c, x, y, R * (0.075 if not simple else 0.09), a + 90 + 30, 0.34, "lance", 0, 0, LW * 0.85, ink)
    # big lotus petals
    for i in range(n):
        a = 360 * i / n
        setup(c, ink, LW)
        draw_poly(c, lotus_petal(cx, cy, R * 0.4, R * 0.86, R * (0.2 if n <= 8 else 0.15), a), fill=True)
        draw_poly(c, lotus_petal(cx, cy, R * 0.46, R * 0.78, R * (0.12 if n <= 8 else 0.09), a), fill=True)
        x, y = cx + R * 0.5 * math.cos(math.radians(a)), cy + R * 0.5 * math.sin(math.radians(a))
        leaf(c, x, y, R * 0.24, a, 0.18, "lance", 0, 2 if not simple else 0, LW * 0.85, ink)
    # leafy stems between the petals
    for i in range(n):
        a = 360 * (i + 0.5) / n
        x0, y0 = cx + R * 0.45 * math.cos(math.radians(a)), cy + R * 0.45 * math.sin(math.radians(a))
        x1, y1 = cx + R * 0.8 * math.cos(math.radians(a)), cy + R * 0.8 * math.sin(math.radians(a))
        pts = [(x0 + (x1 - x0) * t / 20, y0 + (y1 - y0) * t / 20) for t in range(21)]
        Pp = Path(pts)
        for t, s in ((0.3, 0.13), (0.62, 0.1)):
            px, py, ang = Pp.at(t)
            for sd in (1, -1):
                leaf(c, px, py, R * s, ang + 55 * sd, 0.44, "round", 0, 0, LW * 0.85, ink)
        stroke(c, pts, ink, LW)
        if not simple:
            bud(c, x1, y1, R * 0.07, a, ink, LW * 0.9)
        else:
            setup(c, ink, LW)
            c.circle(x1, y1, R * 0.03, stroke=1, fill=1)
    # petal ring
    ring(c, cx, cy, R * 0.42, ink, LW, fill=True)
    k = 16 if not simple else 12
    for i in range(k):
        a = 360 * i / k
        setup(c, ink, LW)
        draw_poly(c, petal_pts(cx, cy, R * 0.17, R * 0.045, a, base=R * 0.22), fill=True)
    for i in range(k):
        a = math.radians(360 * (i + 0.5) / k)
        c.circle(cx + R * 0.36 * math.cos(a), cy + R * 0.36 * math.sin(a), R * 0.018, stroke=1, fill=0)
    ring(c, cx, cy, R * 0.22, ink, LW, fill=True)
    rosette(c, cx, cy, R * 0.2, 3, 0, ink, LW)
    c.restoreState()


def geometric_bloom(c, box, ink):
    """A faceted lotus inside a double hexagon, with a ray lattice behind it."""
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
    o, inn = hexes
    for i in range(6):
        a, bb = o[i], o[(i + 1) % 6]
        p, q = inn[i], inn[(i + 1) % 6]
        segs = 5
        for j in range(segs + 1):
            t = j / segs
            A = (a[0] + (bb[0] - a[0]) * t, a[1] + (bb[1] - a[1]) * t)
            M = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            c.line(A[0], A[1], M[0], M[1])
    # rays from the lotus base, clipped to the inner hexagon
    c.saveState()
    pth = c.beginPath()
    pth.moveTo(*inn[0])
    for q in inn[1:]:
        pth.lineTo(*q)
    pth.close()
    c.clipPath(pth, stroke=0, fill=0)
    bx, by = cx, cy - R * 0.3
    for i in range(19):
        a = math.radians(180 * i / 18)
        c.line(bx, by, bx + 2 * R * math.cos(a), by + 2 * R * math.sin(a))
    for k in (0.62, 0.8):
        c.circle(bx, by, R * k, stroke=1, fill=0)
    c.restoreState()
    # faceted lotus: back petals first
    lw = LW
    petals = [(-52, 0.6, 0.15), (52, 0.6, 0.15), (-26, 0.76, 0.16), (26, 0.76, 0.16), (0, 0.9, 0.17),
              (-74, 0.46, 0.13), (74, 0.46, 0.13)]
    for ang, L, hw in petals:
        a = math.radians(90 + ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        tip = (bx + ux * R * L, by + uy * R * L)
        mid = R * L * 0.48
        lft = (bx + ux * mid + nx * R * hw, by + uy * mid + ny * R * hw)
        rgt = (bx + ux * mid - nx * R * hw, by + uy * mid - ny * R * hw)
        setup(c, ink, lw)
        draw_poly(c, [(bx, by), lft, tip, rgt], fill=True)
        q = (bx + ux * R * L * 0.74, by + uy * R * L * 0.74)
        q0 = (bx + ux * R * L * 0.3, by + uy * R * L * 0.3)
        draw_poly(c, [q0, tip], close=False)
        draw_poly(c, [lft, q, rgt], close=False)
        draw_poly(c, [lft, q0, rgt], close=False)
    # faceted leaves below
    for sd in (1, -1):
        a = math.radians(-90 + sd * 68)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        L = R * 0.5
        tip = (bx + ux * L, by + uy * L)
        l1 = (bx + ux * L * 0.45 + nx * L * 0.2, by + uy * L * 0.45 + ny * L * 0.2)
        l2 = (bx + ux * L * 0.45 - nx * L * 0.2, by + uy * L * 0.45 - ny * L * 0.2)
        setup(c, ink, lw)
        draw_poly(c, [(bx, by), l1, tip, l2], fill=True)
        draw_poly(c, [(bx + ux * L * 0.12, by + uy * L * 0.12), tip], close=False)
        for t in (0.3, 0.55):
            m = (bx + ux * L * t, by + uy * L * t)
            m2 = (bx + ux * L * (t + 0.22), by + uy * L * (t + 0.22))
            for e in (l1, l2):
                f = 0.55 if t < 0.5 else 0.5
                draw_poly(c, [m, (m2[0] + (e[0] - m2[0]) * f, m2[1] + (e[1] - m2[1]) * f)], close=False)
    setup(c, ink, lw)
    c.circle(bx, by, R * 0.05, stroke=1, fill=1)
    c.restoreState()


# --------------------------------------------------------------------------
# 13 weekly reward designs
# --------------------------------------------------------------------------


def wk_wreath(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.36
    yc = cy + H * 0.04
    b.wreath(c, cx, yc, R, ink, (None,) * 5, LW, density=1.5, scale=1.45)
    blooms = [(270, "cosmos", 0.27), (215, "rose", 0.19), (325, "rose", 0.19), (155, "rosette", 0.16),
              (25, "rosette", 0.16), (90, "bud", 0.14), (185, "forget", 0.1), (355, "forget", 0.1)]
    for a, kind, s in blooms:
        x, y = cx + R * math.cos(math.radians(a)), yc + R * math.sin(math.radians(a))
        if kind == "cosmos":
            cosmos(c, x, y, R * s, 8, 10, ink, LW)
        elif kind == "rose":
            wild_rose(c, x, y, R * s, a, ink, LW)
        elif kind == "rosette":
            rosette(c, x, y, R * s, 3, a, ink, LW)
        elif kind == "forget":
            for k in range(3):
                aa = math.radians(a + 120 * k)
                forget_me_not(c, x + R * s * 0.7 * math.cos(aa), y + R * s * 0.7 * math.sin(aa), R * s * 0.6,
                              k * 20, ink, LW)
        else:
            bud(c, x - R * 0.07, y, R * s, 112, ink, LW)
            bud(c, x + R * 0.07, y, R * s, 68, ink, LW)
    # pressed stem in the middle
    pts = curve(cx - R * 0.04, yc - R * 0.52, R * 0.95, 86, 0.1, 50)
    Pp = Path(pts)
    for t, sd in ((0.26, 1), (0.44, -1), (0.6, 1)):
        px, py, a = Pp.at(t)
        leaf(c, px, py, R * 0.3, a + 46 * sd, 0.3, "lance", -0.06 * sd, 3, LW, ink)
    stroke(c, pts, ink, LW)
    px, py, a = Pp.at(0.5)
    side = curve(px, py, R * 0.36, a - 40, -0.2, 30)
    stroke(c, side, ink, LW)
    bud(c, side[-1][0], side[-1][1], R * 0.1, a - 50, ink, LW)
    ex, ey, a = Pp.at(1.0)
    wild_rose(c, ex, ey, R * 0.24, 14, ink, LW)


def wk_ferns(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    gy = y0 + H * 0.1
    # three big fronds fanned out, two small ones in front
    for dx, ln, ang, bd, n in ((-0.04, 0.78, 118, -0.22, 20), (0.04, 0.78, 62, 0.22, 20), (0.0, 0.86, 92, -0.06, 22)):
        fern(c, cx + W * dx, gy, H * ln, ang, bd, n, ink, LW, None, 0.2)
    for dx, ln, ang, bd in ((-0.22, 0.36, 104, -0.25), (0.22, 0.34, 76, 0.25)):
        fern(c, cx + W * dx, gy, H * ln, ang, bd, 12, ink, LW, None, 0.26)
    for dx, ln, ang, t in ((-0.36, 0.3, 98, 1.7), (0.37, 0.27, 82, 1.5), (-0.12, 0.2, 100, 1.5),
                           (0.13, 0.19, 80, 1.6)):
        fiddlehead(c, cx + W * dx, gy, H * ln, ang, ink, LW, t)
    # mossy mounds and pebbles along the ground
    setup(c, ink, LW)
    mounds = [(0.02, 0.14), (0.16, 0.12), (0.3, 0.1), (0.7, 0.1), (0.84, 0.12), (0.98, 0.14)]
    for fx, w in mounds:
        x = x0 + W * fx
        draw_poly(c, bezier_pts((x - W * w / 2, gy), (x - W * w / 3, gy + H * 0.05), (x + W * w / 3, gy + H * 0.05),
                                (x + W * w / 2, gy), 24), fill=True)
    for fx in (0.44, 0.5, 0.57):
        x = x0 + W * fx
        c.ellipse(x - 10, gy - 1, x + 10, gy + 9, stroke=1, fill=1)
    setup(c, ink, LW * 1.1)
    c.line(x0 + 6, gy, x1 - 6, gy)


def wk_peony(c, box, ink):
    """A round posy seen from above: a big peony, wild roses and buds over radiating foliage."""
    cx, cy, W, H = fit(box)
    yc = cy
    L = W * 0.5
    for k in range(8):
        a = 90 + 45 * k + 22.5
        kind = k % 3
        if kind == 0:
            fern_path(c, curve(cx, yc, L, a, 0.12, 120), 14, ink, LW, None, 0.3, start=0.42)
        elif kind == 1:
            eucalyptus(c, curve(cx, yc, L * 0.97, a, -0.12, 60), 6, W * 0.075, ink, LW, start=0.45)
        else:
            leafy_sprig(c, curve(cx, yc, L * 0.97, a, 0.1, 50), 7, W * 0.095, ink, LW, None, "willow", 0.2,
                        spread=34, veins=1, start=0.45)
    for k in range(4):
        a = 90 + 90 * k
        pts = curve(cx, yc, L * 0.86, a, 0.06, 40)
        Pp = Path(pts)
        for t, sd in ((0.6, 1), (0.74, -1)):
            px, py, aa = Pp.at(t)
            leaf(c, px, py, W * 0.07, aa + 45 * sd, 0.3, "lance", -0.06 * sd, 2, LW, ink)
        stroke(c, pts, ink, LW)
        bud(c, pts[-1][0], pts[-1][1], W * 0.06, a, ink, LW)
    for k in range(4):
        a = 45 + 90 * k
        x, y = cx + W * 0.29 * math.cos(math.radians(a)), yc + W * 0.29 * math.sin(math.radians(a))
        wild_rose(c, x, y, W * 0.105, a, ink, LW)
    rosette(c, cx, yc, W * 0.22, 5, 0, ink, LW)


def wk_meadow(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    gy = y0 + H * 0.12
    setup(c, ink, LW)
    hill = bezier_pts((x0, gy + H * 0.1), (x0 + W * 0.35, gy + H * 0.2), (x0 + W * 0.65, gy + H * 0.02),
                      (x1, gy + H * 0.12), 80)
    draw_poly(c, hill, close=False)
    cloud(c, x0 + W * 0.22, y1 - H * 0.12, W * 0.24, ink)
    cloud(c, x0 + W * 0.8, y1 - H * 0.2, W * 0.18, ink)
    plants = [(0.06, 0.42, "bell"), (0.15, 0.6, "cosmos"), (0.26, 0.38, "lav"), (0.34, 0.52, "rose"),
              (0.44, 0.7, "daisy"), (0.54, 0.44, "bud"), (0.63, 0.62, "cosmos"), (0.72, 0.4, "lav"),
              (0.8, 0.55, "rosette"), (0.9, 0.46, "daisy"), (0.97, 0.34, "bud")]
    rnd = random.Random(7)
    for fx, fh, kind in plants:
        x = x0 + W * fx
        h = H * fh
        if kind == "lav":
            lavender(c, curve(x, y0 + 4, h, 90 + rnd.uniform(-6, 6), rnd.uniform(-0.08, 0.08), 50), ink, LW,
                     None, size=W * 0.018, frac=0.4)
            lavender(c, curve(x + W * 0.025, y0 + 4, h * 0.85, 84, 0.05, 50), ink, LW, None, size=W * 0.017,
                     frac=0.4)
            continue
        if kind == "bell":
            pts = curve(x, y0 + 4, h, 88, -0.25, 50)
            stroke(c, pts, ink, LW)
            Pp = Path(pts)
            for t in (0.62, 0.8, 0.97):
                px, py, a = Pp.at(t)
                bell(c, px, py, W * 0.03, -90 + 20, ink, LW)
            continue
        b.flower_on_stem(c, x, y0 + 4, h, 90 + rnd.uniform(-5, 5),
                         {"cosmos": "cosmos", "rose": "rose", "daisy": "daisy", "bud": "bud",
                          "rosette": "rosette"}[kind], ink, LW, size=W * (0.065 if kind != "bud" else 0.05),
                         seed=int(fx * 100))
    draw_grass(c, x0 + 4, x1 - 4, y0 + 4, H * 0.07, LW * 0.9, ink, seed=5, density=0.22)


def wk_pressed(c, box, ink):
    """A pressed-flower specimen: taped stem, a label tag, corner sprigs."""
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    m = 40
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + m, y0 + m, W - 2 * m, H - 2 * m, 18, stroke=1, fill=0)
    setup(c, ink, LW * 0.8)
    c.roundRect(x0 + m + 10, y0 + m + 10, W - 2 * m - 20, H - 2 * m - 20, 12, stroke=1, fill=0)
    for (x, y, a) in ((x0 + m, y0 + m, 45), (x1 - m, y0 + m, 135), (x0 + m, y1 - m, -45), (x1 - m, y1 - m, -135)):
        leaf(c, x, y, W * 0.11, a + 30, 0.3, "lance", -0.06, 2, LW, ink)
        leaf(c, x, y, W * 0.11, a - 30, 0.3, "lance", 0.06, 2, LW, ink)
        forget_me_not(c, x, y, W * 0.035, a, ink, LW)
    # specimen
    sx, sy = cx - W * 0.06, y0 + m + H * 0.12
    pts = spline([(sx, sy), (sx + W * 0.03, sy + H * 0.18), (sx - W * 0.02, sy + H * 0.36), (sx + W * 0.04, sy + H * 0.5)],
                 20)
    Pp = Path(pts)
    for t, sd, s in ((0.18, 1, 0.2), (0.34, -1, 0.22), (0.52, 1, 0.17), (0.68, -1, 0.13)):
        px, py, a = Pp.at(t)
        leaf(c, px, py, W * s, a + 52 * sd, 0.3, "ovate", -0.08 * sd, 3, LW, ink)
    stroke(c, pts, ink, LW * 1.1)
    px, py, a = Pp.at(0.45)
    side = curve(px, py, H * 0.2, a - 38, -0.2, 30)
    stroke(c, side, ink, LW)
    ex, ey = side[-1]
    bud(c, ex, ey, W * 0.06, a - 50, ink, LW)
    ex, ey, a = Pp.at(1.0)
    wild_rose(c, ex, ey, W * 0.14, 12, ink, LW)
    # tape strips
    for (tx, ty, ang) in ((sx + W * 0.005, sy + H * 0.07, 18), (sx + W * 0.02, sy + H * 0.3, -14)):
        c.saveState()
        c.translate(tx, ty)
        c.rotate(ang)
        setup(c, ink, LW * 0.9)
        w, h = W * 0.12, W * 0.04
        pts = [(-w / 2, -h / 2)] + [(-w / 2 + w * i / 6, -h / 2 + (1.5 if i % 2 else -1.5)) for i in range(1, 6)] + \
            [(w / 2, -h / 2), (w / 2, h / 2)] + [(w / 2 - w * i / 6, h / 2 + (1.5 if i % 2 else -1.5))
                                                 for i in range(1, 6)] + [(-w / 2, h / 2)]
        draw_poly(c, pts, fill=True)
        c.restoreState()
    # label tag
    lx, ly, lw_, lh = cx + W * 0.1, y0 + m + 34, W * 0.28, 58
    setup(c, ink, LW)
    c.roundRect(lx, ly, lw_, lh, 6, stroke=1, fill=1)
    c.setLineWidth(LW * 0.7)
    for k in range(3):
        c.line(lx + 12, ly + 14 + k * 15, lx + lw_ - 12, ly + 14 + k * 15)


def wk_pattern(c, box, ink):
    """A repeating pattern of leafy sprigs and little flowers, inside a rounded frame."""
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    c.saveState()
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + 4, y0 + 4, W - 8, H - 8, 22, stroke=1, fill=0)
    p = c.beginPath()
    p.roundRect(x0 + 4, y0 + 4, W - 8, H - 8, 22)
    c.clipPath(p, stroke=0, fill=0)
    step = W / 3.0
    rows = int(H / (step * 0.62)) + 2
    for r in range(-1, rows):
        for k in range(-1, 4):
            x = x0 + k * step + (step / 2 if r % 2 else 0)
            y = y0 + r * step * 0.62
            ang = 40 if r % 2 == 0 else 140
            pts = curve(x - step * 0.12, y, step * 0.58, ang, 0.18 if ang < 90 else -0.18, 30)
            leafy_sprig(c, pts, 5, step * 0.24, ink, LW, None, "lance", 0.3, spread=46, veins=1, start=0.18,
                        taper=0.35)
            fx, fy = x + step * 0.36, y + step * 0.02
            if (r + k) % 2:
                wild_rose(c, fx, fy, step * 0.11, r * 20 + k * 7, ink, LW)
            else:
                forget_me_not(c, fx, fy, step * 0.09, r * 20 + k * 7, ink, LW)
            setup(c, ink, LW)
            for dx, dy in ((0.22, 0.28), (0.3, 0.22)):
                c.circle(x + step * dx, y + step * dy, step * 0.018, stroke=1, fill=0)
    c.restoreState()


def wk_dahlia(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.4
    # sunburst leaves behind
    for i in range(12):
        a = 360 * (i + 0.5) / 12
        x, y = cx + R * 0.75 * math.cos(math.radians(a)), cy + R * 0.75 * math.sin(math.radians(a))
        leaf(c, x, y, R * 0.42, a, 0.26, "lance", 0, 3, LW, ink)
    layers = [(1.0, 24, 0.075), (0.82, 20, 0.08), (0.64, 16, 0.08), (0.47, 12, 0.08), (0.32, 9, 0.075)]
    for k, (f, n, hw) in enumerate(layers):
        for i in range(n):
            a = 360 * (i + 0.5 * (k % 2)) / n
            setup(c, ink, LW)
            draw_poly(c, lotus_petal(cx, cy, R * 0.12, R * f * 0.78, R * hw * (1 + f * 0.6), a), fill=True)
            if f > 0.45:
                c.setLineWidth(LW * 0.7)
                p0 = (cx + R * f * 0.3 * math.cos(math.radians(a)), cy + R * f * 0.3 * math.sin(math.radians(a)))
                p1 = (cx + R * f * 0.66 * math.cos(math.radians(a)), cy + R * f * 0.66 * math.sin(math.radians(a)))
                draw_poly(c, [p0, p1], close=False)
    ring(c, cx, cy, R * 0.14, ink, LW, fill=True)
    setup(c, ink, LW * 0.8)
    for i in range(10):
        a = 2 * math.pi * i / 10
        c.circle(cx + R * 0.085 * math.cos(a), cy + R * 0.085 * math.sin(a), R * 0.022, stroke=1, fill=0)
    c.circle(cx, cy, R * 0.035, stroke=1, fill=0)


def wk_little_mandala(c, box, ink):
    mandala(c, box, ink, n=6, simple=True)


def wk_terrarium(c, box, ink):
    """A faceted glass terrarium with a fern, succulents and pebbles."""
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    s = min(W, H) * 0.46
    by = cy - s * 0.75
    # hanging ring
    setup(c, ink, LW)
    c.line(cx, y1 - 4, cx, cy + s * 1.08)
    c.circle(cx, cy + s * 1.04, s * 0.04, stroke=1, fill=0)
    # glass: faceted shape
    top = [(cx - s * 0.18, cy + s * 1.0), (cx + s * 0.18, cy + s * 1.0)]
    mid = [(cx - s * 0.95, cy + s * 0.05), (cx - s * 0.62, cy + s * 0.6), (cx + s * 0.62, cy + s * 0.6),
           (cx + s * 0.95, cy + s * 0.05)]
    bot = [(cx - s * 0.6, by), (cx + s * 0.6, by)]
    outline = [top[0], mid[1], mid[0], bot[0], bot[1], mid[3], mid[2], top[1]]
    setup(c, ink, LW * 1.2)
    draw_poly(c, outline, fill=True)
    setup(c, ink, LW * 0.8)
    for a, bb in ((top[0], mid[2]), (top[1], mid[1]), (mid[1], mid[2]), (mid[0], mid[3]), (mid[1], bot[0]),
                  (mid[2], bot[1]), (mid[0], (cx, by)), (mid[3], (cx, by)), ((cx, cy + s * 0.6), (cx, by))):
        pass
    for a, bb in ((mid[1], mid[2]), (mid[0], mid[3])):
        draw_poly(c, [a, bb], close=False)

    # soil and pebbles
    sy = by + s * 0.28
    setup(c, ink, LW)
    soil = [(cx - s * 0.72, sy)] + bezier_pts((cx - s * 0.72, sy), (cx - s * 0.3, sy + s * 0.08),
                                              (cx + s * 0.3, sy - s * 0.04), (cx + s * 0.72, sy), 30)
    draw_poly(c, soil, close=False)
    rnd = random.Random(3)
    for i in range(9):
        px = cx - s * 0.5 + s * 1.0 * i / 8 + rnd.uniform(-6, 6)
        py = by + s * 0.11 + rnd.uniform(-4, 4)
        c.ellipse(px - s * 0.06, py - s * 0.035, px + s * 0.06, py + s * 0.035, stroke=1, fill=1)
    # plants
    fern(c, cx - s * 0.25, sy, s * 0.95, 100, -0.2, 11, ink, LW, None, 0.3)
    for (px, r) in ((cx + s * 0.28, s * 0.22), (cx - s * 0.48, s * 0.13)):
        for k, n in ((1.0, 8), (0.7, 7), (0.42, 5)):
            for i in range(n):
                a = 180 * (i + 0.5) / n
                leaf(c, px, sy + 2, r * k, a, 0.34, "lance", 0, 0, LW, ink)
    for x in (cx + s * 0.05,):
        b.flower_on_stem(c, x, sy, s * 0.62, 84, "rose", ink, LW, size=s * 0.1, seed=3)


def wk_blossom_branch(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    main = bezier_pts((x0 - 2, cy - H * 0.22), (x0 + W * 0.3, cy - H * 0.12), (x0 + W * 0.55, cy + H * 0.12),
                      (x1 - W * 0.04, cy + H * 0.3), 80)
    twig1 = bezier_pts(main[34], (main[34][0] + W * 0.05, main[34][1] + H * 0.12),
                       (main[34][0] + W * 0.02, main[34][1] + H * 0.24), (main[34][0] - W * 0.06, main[34][1] + H * 0.34),
                       40)
    twig2 = bezier_pts(main[52], (main[52][0] + W * 0.08, main[52][1] - H * 0.06),
                       (main[52][0] + W * 0.16, main[52][1] - H * 0.14), (main[52][0] + W * 0.24, main[52][1] - H * 0.2),
                       40)
    for tw, w0 in ((twig1, 6), (twig2, 6)):
        ribbon_stem(c, tw, w0, 1.5, ink, LW)
    ribbon_stem(c, main, 16, 3, ink, LW)
    for (pts, ts) in ((main, (0.2, 0.45, 0.72, 0.9)), (twig1, (0.4, 0.8)), (twig2, (0.5, 0.9))):
        Pp = Path(pts)
        for i, t in enumerate(ts):
            px, py, a = Pp.at(t)
            leaf(c, px, py, W * 0.11, a + (60 if i % 2 else -60), 0.3, "ovate", 0.05, 3, LW, ink)
    blooms = [(twig1, 1.0, 0.075), (twig2, 1.0, 0.07), (main, 1.0, 0.08), (main, 0.58, 0.085), (main, 0.32, 0.07),
              (twig1, 0.6, 0.06), (twig2, 0.3, 0.06)]
    for k, (pts, t, s) in enumerate(blooms):
        px, py, a = Path(pts).at(t)
        off = 0 if t == 1.0 else W * 0.03
        wild_rose(c, px + off * math.cos(math.radians(a + 90)), py + off * math.sin(math.radians(a + 90)),
                  W * s, k * 23, ink, LW)
    for (pts, t, a) in ((main, 0.82, 110), (twig2, 0.72, 40), (main, 0.1, 80)):
        px, py, _ = Path(pts).at(t)
        bud(c, px, py, W * 0.04, a, ink, LW)


def wk_lavender(c, box, ink):
    cx, cy, W, H = fit(box)
    tie = (cx, cy - H * 0.18)
    rnd = random.Random(2)
    stems = []
    for i in range(9):
        ang = 62 + 56 * i / 8 + rnd.uniform(-3, 3)
        ln = H * (0.55 + 0.1 * math.sin(i * 1.3))
        head = (tie[0] + ln * math.cos(math.radians(ang)), tie[1] + ln * math.sin(math.radians(ang)))
        base = (cx + (i - 4) * W * 0.012, cy - H * 0.44)
        stems.append(spline([base, tie, ((tie[0] + head[0]) / 2, (tie[1] + head[1]) / 2 + 4), head], 20))
    for pts in stems[::2]:
        lavender(c, pts, ink, LW, None, size=W * 0.024, frac=0.42)
    leafy_sprig(c, b.stem_to((cx - W * 0.02, cy - H * 0.44), tie, (cx - W * 0.4, cy + H * 0.15), 0.1), 6, W * 0.1,
                ink, LW, None, "willow", 0.2, spread=34, veins=1, start=0.5)
    leafy_sprig(c, b.stem_to((cx + W * 0.02, cy - H * 0.44), tie, (cx + W * 0.42, cy + H * 0.12), -0.1), 6, W * 0.1,
                ink, LW, None, "willow", 0.2, spread=34, veins=1, start=0.5)
    for pts in stems[1::2]:
        lavender(c, pts, ink, LW, None, size=W * 0.024, frac=0.42)
    b.bow(c, tie[0], tie[1], W * 0.07, ink, LW)


def wk_arch(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    aw = W * 0.8
    ax0, ax1 = cx - aw / 2, cx + aw / 2
    top_c = y1 - aw / 2 - 10
    base = y0 + 30
    for k in (0, 14):
        pts = [(ax0 + k, base)]
        for i in range(61):
            a = math.pi - math.pi * i / 60
            pts.append((cx + (aw / 2 - k) * math.cos(a), top_c + (aw / 2 - k) * math.sin(a)))
        pts.append((ax1 - k, base))
        setup(c, ink, LW * (1.2 if k == 0 else 0.9))
        draw_poly(c, pts, close=False)
    # climbing vines up both posts and over the top
    for sd in (-1, 1):
        x = cx + sd * (aw / 2 - 7)
        vine = [(x, base)]
        for i in range(1, 50):
            yy = base + (top_c - base) * i / 49
            vine.append((x + 6 * math.sin(i * 0.5), yy))
        for i in range(1, 31):
            a = math.pi / 2 - sd * (math.pi / 2) * (1 - i / 30)
            vine.append((cx + (aw / 2 - 7) * math.cos(a), top_c + (aw / 2 - 7) * math.sin(a)))
        Pp = Path(vine)
        for i in range(18):
            t = 0.04 + 0.92 * i / 17
            px, py, a = Pp.at(t)
            leaf(c, px, py, W * 0.06, a + (55 if i % 2 else -55), 0.32, "ovate", 0, 1, LW, ink)
        stroke(c, vine, ink, LW)
        for t in (0.2, 0.45, 0.7, 0.92):
            px, py, a = Pp.at(t)
            wild_rose(c, px, py, W * 0.04, t * 100, ink, LW)
    # distant hills and little trees seen through the arch
    c.saveState()
    pth = c.beginPath()
    pth.moveTo(ax0 + 14, base)
    for i in range(61):
        a = math.pi - math.pi * i / 60
        pth.lineTo(cx + (aw / 2 - 14) * math.cos(a), top_c + (aw / 2 - 14) * math.sin(a))
    pth.lineTo(ax1 - 14, base)
    pth.close()
    c.clipPath(pth, stroke=0, fill=0)
    setup(c, ink, LW)
    hy = base + H * 0.36
    draw_poly(c, bezier_pts((ax0, hy), (cx - W * 0.2, hy + H * 0.08), (cx + W * 0.05, hy - H * 0.02), (ax1, hy + H * 0.06),
                            60), close=False)
    draw_poly(c, bezier_pts((ax0, hy - H * 0.06), (cx - W * 0.1, hy - H * 0.02), (cx + W * 0.2, hy - H * 0.1),
                            (ax1, hy - H * 0.04), 60), close=False)
    for fx, fy, s_ in ((-0.22, 0.37, 0.05), (-0.16, 0.38, 0.035), (0.2, 0.33, 0.045)):
        tx, ty = cx + W * fx, base + H * fy
        c.line(tx, ty, tx, ty + H * s_ * 0.6)
        c.ellipse(tx - W * s_ * 0.45, ty + H * s_ * 0.4, tx + W * s_ * 0.45, ty + H * s_ * 1.6, stroke=1, fill=1)
    sx_, sy_ = cx + W * 0.08, hy + H * 0.16
    c.circle(sx_, sy_, W * 0.05, stroke=1, fill=1)
    c.restoreState()
    # path and flowers
    setup(c, ink, LW)
    c.line(x0 + 6, base, x1 - 6, base)
    for i in range(5):
        yy = base + H * (0.03 + 0.055 * i)
        ww = W * (0.075 - 0.011 * i)
        xx = cx + W * 0.02 * math.sin(i * 1.4)
        c.ellipse(xx - ww, yy - ww * 0.32, xx + ww, yy + ww * 0.32, stroke=1, fill=1)
    for sd in (-1, 1):
        for k, (fx, fh, kind) in enumerate(((0.26, 0.26, "cosmos"), (0.18, 0.34, "bud"), (0.33, 0.18, "daisy"))):
            b.flower_on_stem(c, cx + sd * W * fx, base, H * fh, 90 - sd * 6, kind, ink, LW,
                             size=W * (0.05 if kind != "bud" else 0.04), seed=k + (5 if sd > 0 else 0))
    # hanging bells in the arch
    for sd in (-1, 1):
        x = cx + sd * W * 0.14
        ytop = top_c + (aw / 2 - 14) * math.sqrt(max(0, 1 - (sd * W * 0.14 / (aw / 2 - 14)) ** 2))
        stroke(c, [(x, ytop), (x, ytop - H * 0.12)], ink, LW)
        bell(c, x, ytop - H * 0.12, W * 0.04, -90, ink, LW)
    stroke(c, [(cx, top_c + aw / 2 - 14), (cx, top_c + aw / 2 - 14 - H * 0.08)], ink, LW)
    bell(c, cx, top_c + aw / 2 - 14 - H * 0.08, W * 0.045, -90, ink, LW)


def wk_finale(c, box, ink, days=90, label=None):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    s = min(W * 0.52, H * 0.45)
    bouquet(c, cx, cy + H * 0.08, s, ink, (None,) * 6, LW)
    banner(c, cx, y0 + H * 0.05, W * 0.36, 34, label or f"{days} days", ink)
    for (fx, fy) in ((0.1, 0.88), (0.9, 0.86), (0.1, 0.22), (0.9, 0.24)):
        forget_me_not(c, x0 + W * fx, y0 + H * fy, W * 0.03, fx * 90, ink, LW)


WEEKLY = [wk_wreath, wk_ferns, wk_peony, wk_meadow, wk_pressed, wk_pattern, wk_dahlia, wk_little_mandala,
          wk_terrarium, wk_blossom_branch, wk_lavender, wk_arch, wk_finale]

WEEKLY_TITLES = ["Wildflower wreath", "Fern garden", "Peony and eucalyptus", "Meadow day", "Pressed flower",
                 "Leaf and blossom pattern", "Dahlia sunburst", "Little mandala", "Terrarium", "Blossom branch",
                 "Lavender bunch", "Garden arch", "You made it"]


# --------------------------------------------------------------------------
# extra designs for the stand-alone coloring pack
# --------------------------------------------------------------------------


def sampler(c, box, ink):
    """Nine botanical specimens, each in its own frame."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    cw, ch = W / 3, H / 3
    for i in range(9):
        cx = x0 + cw * (i % 3 + 0.5)
        cy = y1 - ch * (i // 3 + 0.5)
        setup(c, ink, LW)
        c.roundRect(cx - cw / 2 + 5, cy - ch / 2 + 5, cw - 10, ch - 10, 14, stroke=1, fill=0)
        c.roundRect(cx - cw / 2 + 11, cy - ch / 2 + 11, cw - 22, ch - 22, 10, stroke=1, fill=0)
        s = min(cw, ch) * 0.36
        if i == 0:
            cosmos(c, cx, cy, s * 0.9, 8, 10, ink, LW)
        elif i == 1:
            fern(c, cx - s * 0.2, cy - s * 1.05, s * 2.1, 82, -0.15, 12, ink, LW, None, 0.3)
        elif i == 2:
            rosette(c, cx, cy, s * 0.9, 4, 0, ink, LW)
        elif i == 3:
            eucalyptus(c, curve(cx - s * 0.3, cy - s * 1.05, s * 2.1, 78, -0.15, 50), 6, s * 0.36, ink, LW)
        elif i == 4:
            wild_rose(c, cx, cy, s * 0.95, 0, ink, LW)
        elif i == 5:
            lavender(c, curve(cx - s * 0.25, cy - s * 1.05, s * 2.05, 86, 0.06, 40), ink, LW, None, size=s * 0.09)
            lavender(c, curve(cx + s * 0.25, cy - s * 1.05, s * 1.9, 94, -0.06, 40), ink, LW, None, size=s * 0.09)
        elif i == 6:
            pts = curve(cx - s * 0.4, cy - s * 1.0, s * 1.9, 70, -0.45, 50)
            stroke(c, pts, ink, LW)
            Pp = Path(pts)
            for t in (0.55, 0.75, 0.95):
                px, py, _ = Pp.at(t)
                bell(c, px, py, s * 0.3, -80, ink, LW)
            px, py, a = Pp.at(0.25)
            leaf(c, px, py, s * 0.8, a + 40, 0.26, "lance", -0.05, 3, LW, ink)
        elif i == 7:
            pts = curve(cx, cy - s * 1.05, s * 1.6, 90, 0.1, 40)
            Pp = Path(pts)
            for t, sd in ((0.25, 1), (0.45, -1)):
                px, py, a = Pp.at(t)
                leaf(c, px, py, s * 0.75, a + 45 * sd, 0.3, "lance", -0.06 * sd, 3, LW, ink)
            stroke(c, pts, ink, LW)
            ex, ey, a = Pp.at(1.0)
            bud(c, ex, ey, s * 0.55, a, ink, LW)
        else:
            leaf(c, cx - s * 0.1, cy - s * 0.95, s * 1.95, 78, 0.34, "ovate", 0.06, 5, LW, ink)


def heart_wreath(c, box, ink):
    """A heart-shaped wreath of leaves and small blooms, with a rosette at its point."""
    cx, cy, W, H = fit(box)
    s = min(W, H) * 0.03
    pts = []
    for i in range(241):
        t = 2 * math.pi * i / 240
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s * 1.05, cy + y * s * 1.05 + H * 0.04))
    Pp = Path(pts)
    n = 46
    for i in range(n):
        t = (i + 0.5) / n
        px, py, a = Pp.at(t)
        k = i % 3
        if k == 0:
            leaf(c, px, py, W * 0.08, a + 40, 0.3, "lance", -0.06, 2, LW, ink)
            leaf(c, px, py, W * 0.07, a - 40, 0.3, "lance", 0.06, 1, LW, ink)
        elif k == 1:
            leaf(c, px, py, W * 0.05, a + 70, 0.44, "round", 0, 0, LW, ink)
            leaf(c, px, py, W * 0.05, a - 70, 0.44, "round", 0, 0, LW, ink)
        else:
            leaf(c, px, py, W * 0.07, a + 150, 0.22, "willow", 0, 1, LW, ink)
    stroke(c, pts, ink, LW)
    for t, kind in ((0.0, "rosette"), (0.17, "rose"), (0.83, "rose"), (0.35, "forget"), (0.65, "forget"),
                    (0.5, "cosmos")):
        px, py, _ = Pp.at(t)
        if kind == "rosette":
            rosette(c, px, py, W * 0.08, 3, 0, ink, LW)
        elif kind == "rose":
            wild_rose(c, px, py, W * 0.06, t * 100, ink, LW)
        elif kind == "cosmos":
            cosmos(c, px, py, W * 0.075, 8, 0, ink, LW)
        else:
            forget_me_not(c, px, py, W * 0.035, 0, ink, LW)
    # little pressed sprig inside
    pts2 = curve(cx, cy - H * 0.14, H * 0.2, 90, 0.08, 30)
    P2 = Path(pts2)
    for t, sd in ((0.35, 1), (0.6, -1)):
        px, py, a = P2.at(t)
        leaf(c, px, py, W * 0.08, a + 45 * sd, 0.3, "lance", -0.06 * sd, 2, LW, ink)
    stroke(c, pts2, ink, LW)
    ex, ey, a = P2.at(1.0)
    bud(c, ex, ey, W * 0.05, a, ink, LW)


# --------------------------------------------------------------------------
# mood flower: 30 numbered petals (31st in the center)
# --------------------------------------------------------------------------


def _petal_cell(cx, cy, r0, r1, a_c, half_ang, n=40):
    """A rounded petal shape between radius r0 and r1 centered at angle a_c (deg)."""
    pts = []
    for j in range(n + 1):
        u = -1 + 2 * j / n
        a = math.radians(a_c + u * half_ang)
        rho = r0 + (r1 - r0) * (0.78 + 0.22 * math.cos(u * math.pi / 2) ** 0.7)
        pts.append((cx + rho * math.cos(a), cy + rho * math.sin(a)))
    pts.append((cx + r0 * math.cos(math.radians(a_c + half_ang * 0.5)),
                cy + r0 * math.sin(math.radians(a_c + half_ang * 0.5))))
    pts.append((cx + r0 * math.cos(math.radians(a_c - half_ang * 0.5)),
                cy + r0 * math.sin(math.radians(a_c - half_ang * 0.5))))
    return pts


def mood_cells(c, box, ink, muted, start_day=1, n_days=None):
    """30 petal cells: an outer ring of 16 and an inner ring of 14, numbered clockwise from the top.
    n_days (calendar months): cells past n_days stay blank; 31 adds the center as the 31st cell."""
    cx, cy, W, H = fit(box)
    R = min(H / 2 - 2, W / 2.3)
    yc = cy + 2
    c.saveState()
    # leaves and a short stem peeking out at the bottom
    for sd in (1, -1):
        leaf(c, cx + sd * R * 0.35, yc - R * 0.72, R * 0.62, -90 + sd * 62, 0.3, "lance", -0.08 * sd, 4,
             LW, ink)
    labels = []
    rings = [(16, R * 0.3, R, 0.82), (14, R * 0.16, R * 0.6, 0.46)]
    day = start_day
    for n, r0, r1, lab in rings:
        half = 360 / n / 2 * 1.04
        for i in range(n):
            a = 90 - 360 * i / n
            setup(c, ink, LW * 1.15)
            draw_poly(c, _petal_cell(cx, yc, r0, r1, a, half), fill=True)
            if r1 > R * 0.7:
                c.setLineWidth(LW * 0.6)
                for u in (-0.42, 0.42):
                    aa = math.radians(a + u * half)
                    draw_poly(c, [(cx + R * 0.88 * math.cos(aa), yc + R * 0.88 * math.sin(aa)),
                                  (cx + R * 0.93 * math.cos(aa), yc + R * 0.93 * math.sin(aa))], close=False)
            labels.append((cx + R * lab * math.cos(math.radians(a)), yc + R * lab * math.sin(math.radians(a)), day))
            day += 1
    rc = R * 0.2
    setup(c, ink, LW * 1.15)
    c.circle(cx, yc, rc, stroke=1, fill=1)
    last = start_day + n_days - 1 if n_days else None
    c.setFillColor(muted)
    c.setFont("Sans", 8)
    for x, y, num in labels:
        if last is not None and num > last:
            continue
        c.drawCentredString(x, y - 2.8, str(num))
    if n_days and n_days > 30:
        c.drawCentredString(cx, yc - 2.8, str(start_day + 30))
    else:
        setup(c, ink, LW * 0.8)
        for i in range(8):
            a = 2 * math.pi * i / 8
            c.circle(cx + rc * 0.55 * math.cos(a), yc + rc * 0.55 * math.sin(a), rc * 0.12, stroke=1, fill=0)
        c.circle(cx, yc, rc * 0.2, stroke=1, fill=0)
    c.restoreState()
