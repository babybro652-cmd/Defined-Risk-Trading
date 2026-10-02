"""Celestial line-art engine and coloring pages for Calm Nights.

Moons and moon phases, soft stars and sparkles, puffy clouds, constellations and planets,
all vector line art built from closed white-filled shapes so every region can be colored.
Each coloring design takes (canvas, box, ink) like the other editions.
"""
import math
import random

from reportlab.lib.colors import white

from butterfly_art import bezier_pts, draw_poly
from designs import banner

LW = 1.05


def setup(c, ink, lw=LW, fill=None):
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setFillColor(fill if fill is not None else white)


def fit(box):
    x0, y0, x1, y1 = box
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def arc(cx, cy, r, a0, a1, n=60):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------


def star_pts(x, y, r, rot=0.0, inner=0.47, points=5, soft=True):
    pts = []
    n = points * 2
    for i in range(n):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(90 + rot + 360 * i / n)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    if not soft:
        return pts
    # round the tips a little: bezier through each corner
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        k = 0.16 if i % 2 == 0 else 0.1
        a = (p1[0] + (p0[0] - p1[0]) * k, p1[1] + (p0[1] - p1[1]) * k)
        b = (p1[0] + (p2[0] - p1[0]) * k, p1[1] + (p2[1] - p1[1]) * k)
        out += bezier_pts(a, p1, p1, b, 6)
    return out


def star(c, x, y, r, ink, lw=LW, fill=None, rot=0.0, inner=0.47, points=5, detail=False):
    setup(c, ink, lw, fill)
    draw_poly(c, star_pts(x, y, r, rot, inner, points), fill=True)
    if detail and r > 16:
        c.setLineWidth(lw * 0.7)
        for i in range(points):
            a = math.radians(90 + rot + 360 * i / points)
            c.line(x, y, x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a))


def sparkle(c, x, y, r, ink, lw=LW, fill=None, rot=0.0, thin=0.22):
    """A four-point sparkle with curved sides."""
    pts = []
    for i in range(4):
        a = math.radians(rot + 90 * i)
        b = math.radians(rot + 90 * (i + 1))
        tip = (x + r * math.cos(a), y + r * math.sin(a))
        nxt = (x + r * math.cos(b), y + r * math.sin(b))
        mid = math.radians(rot + 90 * i + 45)
        ctrl = (x + r * thin * math.cos(mid), y + r * thin * math.sin(mid))
        pts += bezier_pts(tip, ctrl, ctrl, nxt, 12)[:-1]
    setup(c, ink, lw, fill)
    draw_poly(c, pts, fill=True)


def crescent_geom(x, y, R, rot=0.0, d=0.38, k=0.92, n=80):
    """Crescent outline as (inner arc tip->tip, outer arc tip->tip). Opens toward rot (degrees)."""
    R2 = k * R
    # intersection of |p| = R and |p - (d R, 0)| = R2
    dd = d * R
    xi = (R * R - R2 * R2 + dd * dd) / (2 * dd)
    yi = math.sqrt(max(R * R - xi * xi, 0.0))
    ao = math.degrees(math.atan2(yi, xi))           # outer circle angle of the top tip
    ai = math.degrees(math.atan2(yi, xi - dd))      # inner circle angle of the top tip
    outer = []
    for i in range(n + 1):
        t = ao + (360 - 2 * ao) * i / n             # top tip -> around the left -> bottom tip
        outer.append((R * math.cos(math.radians(t)), R * math.sin(math.radians(t))))
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)

    def tf(p):
        return (x + p[0] * ca - p[1] * sa, y + p[0] * sa + p[1] * ca)
    return [tf(p) for p in _inner_bottom_to_top(dd, R2, ai, n)], [tf(p) for p in outer]


def _inner_bottom_to_top(dd, R2, ai, n):
    pts = []
    for i in range(n + 1):
        t = -ai - (360 - 2 * ai) * i / n
        pts.append((dd + R2 * math.cos(math.radians(t)), R2 * math.sin(math.radians(t))))
    return pts


def crescent(c, x, y, R, ink, lw=LW, fill=None, rot=0.0, d=0.38, k=0.92, craters=False):
    inner, outer = crescent_geom(x, y, R, rot, d, k)
    setup(c, ink, lw, fill)
    draw_poly(c, outer + inner, fill=True)
    if craters and R > 30:
        c.setLineWidth(lw * 0.75)
        a = math.radians(rot)
        for (px, py, r) in ((-0.78, 0.2, 0.07), (-0.72, -0.32, 0.05), (-0.55, 0.62, 0.045), (-0.5, -0.66, 0.06)):
            qx, qy = px * R, py * R
            c.circle(x + qx * math.cos(a) - qy * math.sin(a), y + qx * math.sin(a) + qy * math.cos(a), r * R,
                     stroke=1, fill=0)


def moon(c, x, y, r, ink, lw=LW, fill=None, craters=True, seed=2):
    setup(c, ink, lw, fill)
    c.circle(x, y, r, stroke=1, fill=1)
    if craters and r > 12:
        rnd = random.Random(seed)
        c.setLineWidth(lw * 0.75)
        for (px, py, rr) in ((-0.35, 0.3, 0.17), (0.3, 0.42, 0.1), (0.2, -0.3, 0.2), (-0.4, -0.38, 0.09),
                             (0.55, 0.0, 0.08), (-0.05, 0.02, 0.07)):
            c.circle(x + px * r, y + py * r, rr * r * rnd.uniform(0.9, 1.1), stroke=1, fill=0)


def phase(c, x, y, r, p, ink, lw=LW, lit=None, dark=None):
    """Moon phase p in [0, 1): 0 new, 0.25 first quarter, 0.5 full, 0.75 last quarter."""
    setup(c, ink, lw, dark)
    c.circle(x, y, r, stroke=1, fill=1)
    if p in (0, 0.0):
        return
    if abs(p - 0.5) < 1e-6:
        setup(c, ink, lw, lit)
        c.circle(x, y, r, stroke=1, fill=1)
        return
    waxing = p < 0.5
    f = p * 2 if waxing else (1 - p) * 2           # lit fraction 0..1
    k = math.cos(math.pi * f)                         # terminator x-scale: 1 (new) .. -1 (full)
    side = 1 if waxing else -1
    pts = []
    for i in range(41):
        t = -90 + 180 * i / 40
        pts.append((x + side * r * math.cos(math.radians(t)), y + r * math.sin(math.radians(t))))
    for i in range(41):
        t = 90 - 180 * i / 40
        pts.append((x + side * r * k * math.cos(math.radians(t)), y + r * math.sin(math.radians(t))))
    setup(c, ink, lw, lit)
    draw_poly(c, pts, fill=True)


def cloud(c, x, y, w, ink, lw=LW, fill=None, bumps=(0.22, 0.3, 0.26, 0.18), flat=0.06):
    """A puffy cloud centered at (x, y), w wide. Built as the outline of overlapping circles."""
    n = len(bumps)
    circles = []
    span = w * 0.78
    for i, r in enumerate(bumps):
        cx = x - span / 2 + span * i / (n - 1)
        circles.append((cx, y + w * 0.02 + r * w * 0.35 * (1 if 0 < i < n - 1 else 0.2), r * w))
    base = y - w * 0.08
    pts = []
    m = 200
    x0 = x - w / 2
    x1 = x + w / 2
    for i in range(m + 1):
        xx = x0 + (x1 - x0) * i / m
        top = None
        for cx, cy, r in circles:
            if abs(xx - cx) < r:
                v = cy + math.sqrt(r * r - (xx - cx) ** 2)
                top = v if top is None else max(top, v)
        if top is not None and top > base:
            pts.append((xx, top))
    # rounded underside
    bl, br = pts[0], pts[-1]
    under = bezier_pts(br, (br[0] + w * 0.05, base - w * flat), (bl[0] - w * 0.05, base - w * flat), bl, 30)
    setup(c, ink, lw, fill)
    draw_poly(c, pts + under[1:-1], fill=True)
    # inner curls for detail
    if w > 80:
        c.setLineWidth(lw * 0.7)
        for cx, cy, r in circles[1:-1]:
            draw_poly(c, arc(cx, cy, r * 0.62, 110, 200, 20), close=False)


def constellation(c, pts, ink, lw=LW, fill=None, r=4.0, lines=None):
    setup(c, ink, lw * 0.7)
    c.setDash(1, 3)
    for i, j in (lines or [(k, k + 1) for k in range(len(pts) - 1)]):
        c.line(pts[i][0], pts[i][1], pts[j][0], pts[j][1])
    c.setDash()
    for i, (px, py) in enumerate(pts):
        star(c, px, py, r * (1.25 if i % 3 == 0 else 1.0), ink, lw, fill, rot=i * 13)


def planet(c, x, y, r, ink, lw=LW, fill=None, fill2=None, tilt=-18):
    """A planet with a ring; the back half of the ring is hidden behind the planet."""
    a = math.radians(tilt)
    ca, sa = math.cos(a), math.sin(a)

    def ell(rx, ry, t0, t1, n=60):
        out = []
        for i in range(n + 1):
            t = math.radians(t0 + (t1 - t0) * i / n)
            px, py = rx * math.cos(t), ry * math.sin(t)
            out.append((x + px * ca - py * sa, y + px * sa + py * ca))
        return out
    # ring band, back half
    setup(c, ink, lw, fill2)
    draw_poly(c, ell(r * 1.75, r * 0.42, 0, 180) + ell(r * 1.35, r * 0.28, 180, 0), fill=True)
    setup(c, ink, lw, fill)
    c.circle(x, y, r, stroke=1, fill=1)
    c.saveState()
    p = c.beginPath()
    p.circle(x, y, r)
    c.clipPath(p, stroke=0, fill=0)
    c.setLineWidth(lw * 0.75)
    for k in (-0.45, 0.1, 0.55):
        draw_poly(c, [(x - r * 1.2 * ca - k * r * (-sa), y - r * 1.2 * sa + k * r * ca),
                      (x + r * 1.2 * ca - k * r * (-sa), y + r * 1.2 * sa + k * r * ca)], close=False)
    c.restoreState()
    setup(c, ink, lw, fill2)
    draw_poly(c, ell(r * 1.75, r * 0.42, 180, 360) + ell(r * 1.35, r * 0.28, 360, 180), fill=True)


def shooting_star(c, x, y, r, angle, length, ink, lw=LW, fill=None):
    a = math.radians(angle + 180)
    setup(c, ink, lw)
    for k, off in enumerate((-0.45, 0.0, 0.45)):
        nx, ny = -math.sin(a), math.cos(a)
        sx, sy = x + nx * r * off, y + ny * r * off
        L = length * (0.75 if k != 1 else 1.0)
        c.line(sx + math.cos(a) * r * 0.6, sy + math.sin(a) * r * 0.6, sx + math.cos(a) * L, sy + math.sin(a) * L)
    star(c, x, y, r, ink, lw, fill, rot=angle)


def dots(c, box, n, ink, seed=3, r=1.6, avoid=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    setup(c, ink, LW * 0.8)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
            continue
        if rnd.random() < 0.6:
            c.circle(x, y, r, stroke=1, fill=0)
        else:
            sparkle(c, x, y, r * 3.2, ink, LW * 0.8, rot=rnd.uniform(0, 30))


# --------------------------------------------------------------------------
# accents and covers (used by theme_nights)
# --------------------------------------------------------------------------


def accent(c, x, y, size, k, angle, ink, F, lw=None):
    """F = (moon, star, cloud, star2, sky) fills."""
    mf, sf, cf, sf2, kf = F
    lw = lw or (0.55 if size < 30 else 0.75)
    s = size
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    kind = k % 6
    if kind == 0:
        crescent(c, -s * 0.1, 0, s * 0.8, ink, lw, mf, rot=25)
        star(c, s * 0.55, s * 0.5, s * 0.22, ink, lw, sf)
        sparkle(c, s * 0.62, -s * 0.35, s * 0.18, ink, lw, sf2)
    elif kind == 1:
        sparkle(c, -s * 0.2, s * 0.1, s * 0.62, ink, lw, sf)
        sparkle(c, s * 0.5, s * 0.5, s * 0.3, ink, lw, sf2)
        sparkle(c, s * 0.45, -s * 0.45, s * 0.22, ink, lw, sf)
    elif kind == 2:
        crescent(c, s * 0.2, s * 0.3, s * 0.6, ink, lw, mf, rot=30)
        cloud(c, -s * 0.05, -s * 0.25, s * 1.6, ink, lw, cf)
    elif kind == 3:
        moon(c, 0, 0, s * 0.62, ink, lw, mf, craters=True)
        sparkle(c, s * 0.75, s * 0.55, s * 0.22, ink, lw, sf)
    elif kind == 4:
        star(c, 0, 0, s * 0.7, ink, lw, sf, rot=-8, detail=s > 20)
        sparkle(c, -s * 0.75, s * 0.5, s * 0.2, ink, lw, sf2)
    else:
        pts = [(-s * 0.8, -s * 0.3), (-s * 0.3, s * 0.15), (s * 0.15, -s * 0.05), (s * 0.55, s * 0.55),
               (s * 0.8, -s * 0.4)]
        constellation(c, pts, ink, lw, sf, r=s * 0.16)
    c.restoreState()


def moon_scene(c, cx, cy, s, ink, F, lw=1.0, style="moon"):
    """Cover hero. s ~ radius of the scene."""
    mf, sf, cf, sf2, kf = F
    if style == "cloud":
        crescent(c, cx + s * 0.05, cy + s * 0.12, s * 0.62, ink, lw, mf, rot=-60, craters=True)
        cloud(c, cx, cy - s * 0.3, s * 1.45, ink, lw, cf, bumps=(0.16, 0.24, 0.3, 0.24, 0.17))
        for (dx, dy, r, kind) in ((-0.62, 0.42, 0.13, "star"), (0.6, 0.5, 0.1, "sparkle"), (0.7, -0.05, 0.07, "star"),
                                  (-0.7, -0.05, 0.08, "sparkle"), (-0.3, 0.78, 0.07, "sparkle"),
                                  (0.32, 0.8, 0.08, "star")):
            if kind == "star":
                star(c, cx + dx * s, cy + dy * s, r * s, ink, lw, sf, rot=dx * 30)
            else:
                sparkle(c, cx + dx * s, cy + dy * s, r * s, ink, lw, sf2)
        return
    if style == "starfield":
        pts = [(-0.7, -0.35), (-0.45, 0.1), (-0.1, -0.05), (0.2, 0.35), (0.62, 0.2), (0.75, -0.3)]
        constellation(c, [(cx + px * s, cy + py * s) for px, py in pts], ink, lw, sf, r=s * 0.06)
        star(c, cx, cy + s * 0.05, s * 0.42, ink, lw * 1.1, sf2, rot=0, detail=True)
        for i in range(8):
            p = i / 8
            a = math.radians(90 + 360 * i / 8)
            phase(c, cx + s * 0.8 * math.cos(a), cy + s * 0.8 * math.sin(a), s * 0.085, p, ink, lw, mf, kf)
        return
    # "moon": crescent with clouds, stars and a ring of phases
    crescent(c, cx - s * 0.06, cy + s * 0.08, s * 0.66, ink, lw * 1.1, mf, rot=20, craters=True)
    cloud(c, cx + s * 0.28, cy - s * 0.42, s * 0.95, ink, lw, cf, bumps=(0.17, 0.27, 0.3, 0.2))
    cloud(c, cx - s * 0.42, cy - s * 0.52, s * 0.7, ink, lw, cf, bumps=(0.2, 0.3, 0.22))
    star(c, cx + s * 0.42, cy + s * 0.38, s * 0.13, ink, lw, sf, rot=8, detail=True)
    sparkle(c, cx + s * 0.6, cy + s * 0.05, s * 0.09, ink, lw, sf2)
    star(c, cx + s * 0.15, cy + s * 0.68, s * 0.06, ink, lw, sf2, rot=-10)
    sparkle(c, cx - s * 0.5, cy + s * 0.62, s * 0.07, ink, lw, sf)
    for (dx, dy, r) in ((-0.62, -0.8, 0.06), (0.55, -0.82, 0.07), (0.02, -0.98, 0.05)):
        sparkle(c, cx + dx * s, cy + dy * s, r * s, ink, lw, sf2 if dx < 0 else sf)
    star(c, cx - s * 0.25, cy - s * 0.9, s * 0.045, ink, lw, sf)
    star(c, cx + s * 0.3, cy - s * 1.0, s * 0.04, ink, lw, sf2)
    for i in range(7):
        p = [0.08, 0.17, 0.25, 0.5, 0.75, 0.83, 0.92][i]
        a = math.radians(160 - 140 * i / 6)
        phase(c, cx + s * 1.12 * math.cos(a), cy + s * 1.12 * math.sin(a), s * 0.075, p, ink, lw * 0.9, mf, kf)


# --------------------------------------------------------------------------
# coloring pages
# --------------------------------------------------------------------------


def mandala(c, box, ink, n=8, simple=False):
    """Celestial mandala: a cratered full moon, petal rays, crescents and stars in rings."""
    cx, cy, W, H = fit(box)
    R = min(W, H) / 2 - 4
    setup(c, ink, LW * 1.15)
    c.circle(cx, cy, R, stroke=1, fill=0)
    c.circle(cx, cy, R * 0.9, stroke=1, fill=0)
    m = 32 if not simple else 24
    for i in range(m):
        a = 360 * i / m
        x, y = cx + R * 0.95 * math.cos(math.radians(a)), cy + R * 0.95 * math.sin(math.radians(a))
        if i % 2:
            setup(c, ink, LW)
            c.circle(x, y, R * 0.018, stroke=1, fill=0)
        else:
            star(c, x, y, R * 0.04, ink, LW * 0.9, rot=a - 90)
    from botanical_designs import lotus_petal
    # thin rays between the petals
    for i in range(n):
        a = 360 * (i + 0.5) / n
        ang = math.radians(a)
        ux, uy = math.cos(ang), math.sin(ang)
        nx, ny = -uy, ux
        hw = 0.05
        p0 = (cx + ux * R * 0.42 + nx * R * hw, cy + uy * R * 0.42 + ny * R * hw)
        p1 = (cx + ux * R * 0.86, cy + uy * R * 0.86)
        p2 = (cx + ux * R * 0.42 - nx * R * hw, cy + uy * R * 0.42 - ny * R * hw)
        setup(c, ink, LW)
        draw_poly(c, [p0, p1, p2], fill=True)
        star(c, cx + ux * R * 0.8, cy + uy * R * 0.8, R * 0.035, ink, LW * 0.9, rot=a - 90)
    # big rounded petals, each holding a crescent and a star
    for i in range(n):
        a = 360 * i / n
        setup(c, ink, LW)
        draw_poly(c, lotus_petal(cx, cy, R * 0.38, R * 0.86, R * (0.21 if n <= 8 else 0.16), a), fill=True)
        draw_poly(c, lotus_petal(cx, cy, R * 0.44, R * 0.8, R * (0.15 if n <= 8 else 0.11), a), fill=True)
        x, y = cx + R * 0.6 * math.cos(math.radians(a)), cy + R * 0.6 * math.sin(math.radians(a))
        crescent(c, x, y, R * (0.075 if n <= 8 else 0.06), ink, LW, rot=a + 180)
        if not simple:
            x2, y2 = cx + R * 0.72 * math.cos(math.radians(a)), cy + R * 0.72 * math.sin(math.radians(a))
            sparkle(c, x2, y2, R * 0.03, ink, LW * 0.8, rot=a)
    # inner ring of scallops
    setup(c, ink, LW)
    c.circle(cx, cy, R * 0.42, stroke=1, fill=1)
    k = 18 if not simple else 12
    for i in range(k):
        a0 = 360 * i / k
        a1 = 360 * (i + 1) / k
        pts = arc(cx, cy, R * 0.34, a0, a1, 10)
        mid = math.radians((a0 + a1) / 2)
        bump = bezier_pts(pts[-1], (cx + R * 0.42 * math.cos(mid + 0.12), cy + R * 0.42 * math.sin(mid + 0.12)),
                          (cx + R * 0.42 * math.cos(mid - 0.12), cy + R * 0.42 * math.sin(mid - 0.12)), pts[0], 12)
        draw_poly(c, pts + bump[1:-1], fill=True)
    for i in range(k):
        a = math.radians(360 * (i + 0.5) / k)
        c.circle(cx + R * 0.385 * math.cos(a), cy + R * 0.385 * math.sin(a), R * 0.012, stroke=1, fill=0)
    moon(c, cx, cy, R * 0.3, ink, LW, craters=True, seed=4)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        sparkle(c, cx + R * 0.18 * math.cos(a), cy + R * 0.18 * math.sin(a), R * 0.03, ink, LW * 0.8) if not simple \
            else None


def geo_star(c, box, ink):
    """An eight-point star of facets inside a double octagon with a star lattice."""
    cx, cy, W, H = fit(box)
    R = min(W, H * 0.9) / 2
    setup(c, ink, LW)
    for k in (1.0, 0.92):
        pts = [(cx + R * k * math.cos(math.radians(22.5 + 45 * i)), cy + R * k * math.sin(math.radians(22.5 + 45 * i)))
               for i in range(8)]
        draw_poly(c, pts)
    o = [(cx + R * math.cos(math.radians(22.5 + 45 * i)), cy + R * math.sin(math.radians(22.5 + 45 * i)))
         for i in range(8)]
    inn = [(cx + R * 0.92 * math.cos(math.radians(22.5 + 45 * i)), cy + R * 0.92 * math.sin(math.radians(22.5 + 45 * i)))
           for i in range(8)]
    for i in range(8):
        a, b = o[i], o[(i + 1) % 8]
        p, q = inn[i], inn[(i + 1) % 8]
        for j in range(1, 4):
            t = j / 4
            c.line(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    # star polygon lattice {8/3}
    c.saveState()
    pth = c.beginPath()
    pth.moveTo(*inn[0])
    for q in inn[1:]:
        pth.lineTo(*q)
    pth.close()
    c.clipPath(pth, stroke=0, fill=0)
    for i in range(8):
        c.line(inn[i][0], inn[i][1], inn[(i + 3) % 8][0], inn[(i + 3) % 8][1])
    c.restoreState()
    # eight-point faceted star on top
    Ro, Ri = R * 0.66, R * 0.27
    pts = []
    for i in range(16):
        rr = Ro if i % 2 == 0 else Ri
        a = math.radians(90 + 22.5 * i)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    setup(c, ink, LW * 1.1)
    draw_poly(c, pts, fill=True)
    c.setLineWidth(LW)
    for i in range(16):
        c.line(cx, cy, pts[i][0], pts[i][1])
    # small inner star
    pts2 = []
    for i in range(16):
        rr = Ro * 0.45 if i % 2 == 0 else Ri * 0.5
        a = math.radians(90 + 22.5 * i + 22.5)
        pts2.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw_poly(c, pts2, fill=True)
    c.circle(cx, cy, R * 0.06, stroke=1, fill=1)


def wk_moon_clouds(c, box, ink):
    cx, cy, W, H = fit(box)
    crescent(c, cx - W * 0.02, cy + H * 0.1, W * 0.32, ink, LW * 1.1, rot=25, craters=True)
    cloud(c, cx + W * 0.16, cy - H * 0.12, W * 0.62, ink, LW, bumps=(0.16, 0.26, 0.3, 0.2))
    cloud(c, cx - W * 0.24, cy - H * 0.2, W * 0.48, ink, LW, bumps=(0.2, 0.3, 0.22))
    cloud(c, cx + W * 0.2, cy + H * 0.36, W * 0.3, ink, LW, bumps=(0.22, 0.3, 0.2))
    for (fx, fy, r, kind) in ((0.3, 0.2, 0.06, "s"), (0.36, -0.36, 0.045, "p"), (-0.38, 0.34, 0.05, "s"),
                              (-0.4, 0.05, 0.035, "p"), (0.4, 0.05, 0.03, "s"), (-0.1, 0.42, 0.035, "p"),
                              (-0.32, -0.42, 0.04, "s"), (0.1, -0.44, 0.03, "p")):
        if kind == "s":
            star(c, cx + W * fx, cy + H * fy, W * r, ink, LW, rot=fx * 50, detail=True)
        else:
            sparkle(c, cx + W * fx, cy + H * fy, W * r, ink, LW)


def wk_constellations(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.46
    setup(c, ink, LW * 1.2)
    c.circle(cx, cy, R, stroke=1, fill=0)
    c.circle(cx, cy, R * 0.94, stroke=1, fill=0)
    for i in range(36):
        a = math.radians(10 * i)
        c.line(cx + R * 0.94 * math.cos(a), cy + R * 0.94 * math.sin(a), cx + R * math.cos(a), cy + R * math.sin(a))
    groups = [
        [(-0.62, 0.3), (-0.48, 0.42), (-0.32, 0.38), (-0.2, 0.46), (-0.18, 0.3), (-0.34, 0.24)],
        [(0.15, 0.55), (0.3, 0.68), (0.45, 0.58), (0.38, 0.4), (0.55, 0.32)],
        [(-0.55, -0.25), (-0.4, -0.1), (-0.25, -0.22), (-0.38, -0.4), (-0.55, -0.25)],
        [(0.2, -0.05), (0.35, 0.1), (0.5, 0.05), (0.62, -0.12), (0.45, -0.25), (0.3, -0.18)],
        [(-0.05, -0.55), (0.1, -0.45), (0.25, -0.62), (0.4, -0.5)],
    ]
    for g in groups:
        constellation(c, [(cx + px * R, cy + py * R) for px, py in g], ink, LW, r=R * 0.03)
    crescent(c, cx - R * 0.02, cy + R * 0.05, R * 0.14, ink, LW, rot=200, craters=False)
    dots(c, (cx - R * 0.8, cy - R * 0.8, cx + R * 0.8, cy + R * 0.8), 30, ink, seed=5, r=1.4,
         avoid=[(cx, cy, R * 0.2)] + [(cx + px * R, cy + py * R, R * 0.07) for g in groups for px, py in g])
    star(c, cx, cy - R * 1.0, R * 0.07, ink, LW, rot=0)


def wk_phase_wreath(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.38
    setup(c, ink, LW)
    c.circle(cx, cy, R, stroke=1, fill=0)
    n = 12
    for i in range(n):
        a = math.radians(90 - 360 * i / n)
        phase(c, cx + R * math.cos(a), cy + R * math.sin(a), R * 0.13, i / n, ink, LW)
    for i in range(n):
        a = math.radians(90 - 360 * (i + 0.5) / n)
        sparkle(c, cx + R * 1.17 * math.cos(a), cy + R * 1.17 * math.sin(a), R * 0.06, ink, LW)
        star(c, cx + R * 0.8 * math.cos(a), cy + R * 0.8 * math.sin(a), R * 0.045, ink, LW, rot=i * 9)
    moon(c, cx, cy, R * 0.42, ink, LW * 1.1, craters=True)
    setup(c, ink, LW)
    c.circle(cx, cy, R * 0.52, stroke=1, fill=0)
    c.setDash(1, 4)
    c.circle(cx, cy, R * 0.6, stroke=1, fill=0)
    c.setDash()


def pine(c, x, y, h, ink, lw=LW, tiers=4):
    w = h * 0.42
    setup(c, ink, lw)
    c.rect(x - h * 0.03, y, h * 0.06, h * 0.12, stroke=1, fill=1)
    for k in range(tiers):
        yb = y + h * 0.1 + h * 0.8 * k / tiers
        wb = w * (1 - 0.2 * k)
        yt = yb + h * 0.38
        pts = [(x - wb / 2, yb), (x, yt), (x + wb / 2, yb)]
        pts = [pts[0]] + bezier_pts(pts[0], (x - wb * 0.2, yb + h * 0.18), (x, yt - h * 0.05), pts[1], 10)[1:] + \
            bezier_pts(pts[1], (x, yt - h * 0.05), (x + wb * 0.2, yb + h * 0.18), pts[2], 10)[1:]
        sc = []
        for j in range(5):
            xa = x + wb / 2 - wb * j / 5
            xb = x + wb / 2 - wb * (j + 1) / 5
            sc += bezier_pts((xa, yb), (xa, yb - h * 0.04), (xb, yb - h * 0.04), (xb, yb), 6)[1:]
        draw_poly(c, pts + sc, fill=True)


def wk_landscape(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + 6, y0 + 6, W - 12, H - 12, 24, stroke=1, fill=0)
    c.saveState()
    p = c.beginPath()
    p.roundRect(x0 + 6, y0 + 6, W - 12, H - 12, 24)
    c.clipPath(p, stroke=0, fill=0)
    moon(c, cx + W * 0.18, y1 - H * 0.22, W * 0.12, ink, LW, craters=True)
    cloud(c, cx - W * 0.22, y1 - H * 0.18, W * 0.34, ink, LW)
    cloud(c, cx + W * 0.36, y1 - H * 0.36, W * 0.24, ink, LW)
    for (fx, fy, r) in ((0.1, 0.92, 0.02), (0.42, 0.88, 0.016), (0.62, 0.95, 0.018), (0.9, 0.9, 0.022),
                        (0.3, 0.72, 0.015), (0.05, 0.66, 0.02), (0.75, 0.68, 0.016)):
        sparkle(c, x0 + W * fx, y0 + H * fy, W * r * 1.4, ink, LW)
    hy = y0 + H * 0.4
    setup(c, ink, LW)
    draw_poly(c, [(x0, hy)] + bezier_pts((x0, hy), (x0 + W * 0.25, hy + H * 0.16), (x0 + W * 0.45, hy + H * 0.12),
                                        (x0 + W * 0.6, hy + H * 0.04), 40)[1:] +
              bezier_pts((x0 + W * 0.6, hy + H * 0.04), (x0 + W * 0.75, hy + H * 0.14), (x0 + W * 0.9, hy + H * 0.1),
                         (x1, hy + H * 0.06), 40)[1:] + [(x1, hy)], fill=True)
    draw_poly(c, [(x0, hy)] + bezier_pts((x0, hy), (x0 + W * 0.3, hy + H * 0.07), (x0 + W * 0.7, hy - H * 0.02),
                                        (x1, hy + H * 0.04), 40)[1:] + [(x1, hy)], fill=True)
    # lake with the moon's reflection
    ly = y0 + H * 0.24
    c.rect(x0, ly, W, hy - ly, stroke=1, fill=1)
    rx = cx + W * 0.18
    for k in range(6):
        yy = hy - (hy - ly) * (k + 0.6) / 6.5
        ww = W * (0.1 - 0.012 * k)
        c.line(rx - ww, yy, rx + ww, yy)
    for k in range(4):
        yy = hy - (hy - ly) * (k + 1) / 5
        c.line(x0 + W * 0.08, yy, x0 + W * 0.22, yy)
    # shore with pines
    draw_poly(c, [(x0, y0)] + [(x0, ly)] + bezier_pts((x0, ly), (x0 + W * 0.3, ly + H * 0.03), (x0 + W * 0.6, ly - H * 0.03),
                                                       (x1, ly + H * 0.01), 40)[1:] + [(x1, y0)], fill=True)
    for (fx, h) in ((0.06, 0.34), (0.14, 0.26), (0.22, 0.2), (0.82, 0.3), (0.9, 0.38), (0.96, 0.24)):
        pine(c, x0 + W * fx, ly - H * 0.08, H * h, ink)
    c.restoreState()


def wk_star_frame(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    m = 44
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + m, y0 + m, W - 2 * m, H - 2 * m, 26, stroke=1, fill=0)
    setup(c, ink, LW * 0.8)
    c.setDash(1, 5)
    c.roundRect(x0 + m + 12, y0 + m + 12, W - 2 * m - 24, H - 2 * m - 24, 18, stroke=1, fill=0)
    c.setDash()
    for (x, y) in ((x0 + m, y0 + m), (x1 - m, y0 + m), (x0 + m, y1 - m), (x1 - m, y1 - m)):
        sparkle(c, x, y, W * 0.07, ink, LW)
        star(c, x, y, W * 0.025, ink, LW)
    # hanging crescent with stars on strings
    top = y1 - m - 12
    crescent(c, cx + W * 0.03, cy - H * 0.06, W * 0.24, ink, LW * 1.1, rot=20, craters=True)
    for fx, ln, r in ((-0.3, 0.42, 0.045), (-0.1, 0.1, 0.035), (0.14, 0.16, 0.04), (0.3, 0.36, 0.035)):
        x = cx + W * fx
        setup(c, ink, LW * 0.8)
        c.line(x, top, x, top - H * ln)
        star(c, x, top - H * ln - W * r, W * r, ink, LW, rot=fx * 40, detail=True)
    for i in range(7):
        x = cx - W * 0.27 + W * 0.09 * i
        cloud(c, x, y0 + m + 46, W * 0.14, ink, LW, bumps=(0.22, 0.3, 0.2)) if i % 2 == 0 else \
            star(c, x, y0 + m + 46, W * 0.02, ink, LW)


def wk_dream_clouds(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    setup(c, ink, LW * 1.2)
    c.roundRect(x0 + 6, y0 + 6, W - 12, H - 12, 24, stroke=1, fill=0)
    c.saveState()
    p = c.beginPath()
    p.roundRect(x0 + 6, y0 + 6, W - 12, H - 12, 24)
    c.clipPath(p, stroke=0, fill=0)
    placed = []
    rows = [(0.84, (0.22, 0.72)), (0.62, (0.06, 0.5, 0.94)), (0.4, (0.28, 0.76)), (0.18, (0.04, 0.48, 0.92)),
            (0.0, (0.25, 0.75))]
    for k, (fy, xs) in enumerate(rows):
        for j, fx in enumerate(xs):
            w = W * (0.46 if (k + j) % 2 else 0.4)
            cloud(c, x0 + W * fx, y0 + H * fy + H * 0.04, w, ink, LW,
                  bumps=((0.17, 0.27, 0.3, 0.2) if (k + j) % 2 else (0.2, 0.3, 0.22)))
            placed.append((x0 + W * fx, y0 + H * fy + H * 0.06, w * 0.5))
    crescent(c, x0 + W * 0.5, y0 + H * 0.95, W * 0.06, ink, LW, rot=30, craters=False)
    rnd = random.Random(11)
    n = tries = 0
    while n < 18 and tries < 3000:
        tries += 1
        px, py = x0 + W * rnd.uniform(0.04, 0.96), y0 + H * rnd.uniform(0.1, 0.98)
        if any(math.hypot(px - qx, (py - qy) * 1.3) < r * 1.1 for qx, qy, r in placed):
            continue
        placed.append((px, py, W * 0.05))
        if n % 2:
            star(c, px, py, W * 0.022, ink, LW, rot=n * 17)
        else:
            sparkle(c, px, py, W * 0.026, ink, LW)
        n += 1
    c.restoreState()


def wk_moon_sunburst(c, box, ink):
    cx, cy, W, H = fit(box)
    R = W * 0.42
    from botanical_designs import lotus_petal
    for k, (n, L, hw, off) in enumerate(((24, 1.0, 0.075, 0.5), (24, 0.84, 0.085, 0.0), (12, 0.66, 0.13, 0.25))):
        for i in range(n):
            a = 360 * (i + off) / n
            setup(c, ink, LW)
            draw_poly(c, lotus_petal(cx, cy, R * 0.36, R * L, R * hw, a), fill=True)
            if k < 2:
                c.setLineWidth(LW * 0.7)
                ang = math.radians(a)
                c.line(cx + math.cos(ang) * R * 0.5, cy + math.sin(ang) * R * 0.5,
                       cx + math.cos(ang) * R * (L - 0.14), cy + math.sin(ang) * R * (L - 0.14))
    setup(c, ink, LW)
    c.circle(cx, cy, R * 0.42, stroke=1, fill=1)
    for i in range(20):
        a = math.radians(18 * i)
        c.circle(cx + R * 0.38 * math.cos(a), cy + R * 0.38 * math.sin(a), R * 0.015, stroke=1, fill=0)
    moon(c, cx, cy, R * 0.32, ink, LW, craters=True, seed=7)


def wk_little_mandala(c, box, ink):
    mandala(c, box, ink, n=6, simple=True)


def wk_mobile(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    top = y1 - 4
    setup(c, ink, LW)
    c.line(cx, top, cx, cy + H * 0.36)
    hx, hy = cx, cy + H * 0.36
    bar = W * 0.4
    draw_poly(c, bezier_pts((hx - bar, hy - 10), (hx - bar / 2, hy + 6), (hx + bar / 2, hy + 6), (hx + bar, hy - 10), 30),
              close=False)
    hang = [(-1.0, 0.3, "moon"), (-0.5, 0.48, "star"), (0.0, 0.62, "cres"), (0.5, 0.44, "star"), (1.0, 0.28, "cloud")]
    for fx, ln, kind in hang:
        x = hx + bar * fx
        yy = hy - 10 + (6 + 10) * (1 - abs(fx)) * 0.75
        end = yy - H * ln
        setup(c, ink, LW * 0.8)
        c.line(x, yy, x, end)
        if kind == "moon":
            moon(c, x, end - W * 0.1, W * 0.1, ink, LW, craters=True)
        elif kind == "star":
            star(c, x, end - W * 0.09, W * 0.09, ink, LW, detail=True)
        elif kind == "cres":
            crescent(c, x, end - W * 0.16, W * 0.16, ink, LW, rot=-30, craters=True)
        else:
            cloud(c, x, end - W * 0.05, W * 0.26, ink, LW, bumps=(0.22, 0.3, 0.2))
        for k in (0.35, 0.65):
            if kind != "cres":
                sparkle(c, x, yy - (yy - end) * k, W * 0.018, ink, LW * 0.8)
    for (fx, fy) in ((0.1, 0.12), (0.3, 0.05), (0.7, 0.08), (0.9, 0.15), (0.5, 0.1)):
        star(c, x0 + W * fx, y0 + H * fy, W * 0.025, ink, LW, rot=fx * 40)


def wk_planets(c, box, ink):
    cx, cy, W, H = fit(box)
    setup(c, ink, LW * 0.8)
    c.setDash(2, 5)
    for k in (0.28, 0.4):
        c.ellipse(cx - W * k, cy - W * k * 0.45, cx + W * k, cy + W * k * 0.45, stroke=1, fill=0)
    c.setDash()
    planet(c, cx, cy, W * 0.14, ink, LW)
    moon(c, cx + W * 0.28, cy - W * 0.03, W * 0.035, ink, LW, craters=False)
    moon(c, cx - W * 0.3, cy + W * 0.16, W * 0.045, ink, LW, craters=True)
    planet(c, cx - W * 0.28, cy + H * 0.33, W * 0.07, ink, LW, tilt=20)
    moon(c, cx + W * 0.3, cy + H * 0.34, W * 0.06, ink, LW, craters=True)
    shooting_star(c, cx + W * 0.3, cy - H * 0.3, W * 0.05, 200, W * 0.3, ink, LW)
    crescent(c, cx - W * 0.3, cy - H * 0.32, W * 0.07, ink, LW, rot=10)
    dots(c, (cx - W * 0.46, cy - H * 0.46, cx + W * 0.46, cy + H * 0.46), 40, ink, seed=9, r=1.6,
         avoid=[(cx, cy, W * 0.3), (cx - W * 0.28, cy + H * 0.33, W * 0.14), (cx + W * 0.3, cy + H * 0.34, W * 0.08),
                (cx + W * 0.2, cy - H * 0.25, W * 0.18), (cx - W * 0.3, cy - H * 0.32, W * 0.09)])


def wk_window(c, box, ink):
    """An arched window open to the night sky, with curtains and a plant on the sill."""
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    ww = W * 0.56
    wx0, wx1 = cx - ww / 2, cx + ww / 2
    sill = y0 + H * 0.2
    top_c = y1 - H * 0.08 - ww / 2
    outline = [(wx0, sill)] + arc(cx, top_c, ww / 2, 180, 0, 60) + [(wx1, sill)]
    setup(c, ink, LW * 1.2)
    draw_poly(c, outline, fill=True)
    # the view, clipped to the window
    c.saveState()
    p = c.beginPath()
    p.moveTo(*outline[0])
    for q in outline[1:]:
        p.lineTo(*q)
    p.close()
    c.clipPath(p, stroke=0, fill=0)
    crescent(c, cx + ww * 0.12, top_c + ww * 0.05, ww * 0.18, ink, LW, rot=25, craters=True)
    cloud(c, cx - ww * 0.18, top_c - ww * 0.3, ww * 0.5, ink, LW)
    for (fx, fy) in ((-0.3, 0.3), (0.3, 0.42), (-0.05, 0.38), (0.32, -0.2), (-0.36, -0.05)):
        star(c, cx + ww * fx, top_c + ww * fy, ww * 0.035, ink, LW, rot=fx * 50)
    setup(c, ink, LW)
    draw_poly(c, [(wx0, sill + H * 0.12)] + bezier_pts((wx0, sill + H * 0.12), (cx - ww * 0.2, sill + H * 0.2),
                                                     (cx + ww * 0.2, sill + H * 0.08), (wx1, sill + H * 0.15), 40)[1:] +
              [(wx1, sill), (wx0, sill)], fill=True)
    for fx, h in ((-0.35, 0.18), (-0.25, 0.14), (0.3, 0.16)):
        pine(c, cx + ww * fx, sill + H * 0.1, H * h, ink)
    c.restoreState()
    setup(c, ink, LW)
    c.line(cx, sill, cx, top_c + ww / 2)
    c.line(wx0, top_c, wx1, top_c)
    # curtains
    for sd in (-1, 1):
        xo = cx + sd * (ww / 2 + W * 0.12)
        xi = cx + sd * (ww / 2 - W * 0.06)
        ytop = y1 - H * 0.02
        pts = [(xo, ytop), (xi, ytop)] + bezier_pts((xi, ytop), (xi, sill + H * 0.5), (xo - sd * W * 0.02, sill + H * 0.32),
                                                    (xo - sd * W * 0.03, sill + H * 0.3), 30)[1:] + \
            bezier_pts((xo - sd * W * 0.03, sill + H * 0.3), (xo, sill + H * 0.2), (xo, sill + H * 0.05), (xo, y0 + 6),
                       20)[1:]
        setup(c, ink, LW)
        draw_poly(c, pts, fill=True)
        c.setLineWidth(LW * 0.7)
        for k in (0.33, 0.66):
            xx = xo + (xi - xo) * k
            c.line(xx, ytop - 4, xx + (xo - xx) * 0.3, sill + H * 0.45)
        # tie-back
        setup(c, ink, LW)
        c.roundRect(xo - sd * W * 0.035 - W * 0.025, sill + H * 0.28, W * 0.05, H * 0.035, 3, stroke=1, fill=1)
    setup(c, ink, LW * 1.2)
    c.roundRect(wx0 - W * 0.06, sill - H * 0.03, ww + W * 0.12, H * 0.03, 3, stroke=1, fill=1)
    c.line(cx - W * 0.46, ytop, cx + W * 0.46, ytop)
    # plant pot on the sill
    px, py = cx - ww * 0.22, sill
    pts = [(px - W * 0.05, py), (px + W * 0.05, py), (px + W * 0.065, py + H * 0.07), (px - W * 0.065, py + H * 0.07)]
    setup(c, ink, LW)
    from botanical_art import leaf
    for a, ln in ((60, 0.13), (90, 0.16), (120, 0.12), (75, 0.1), (105, 0.11)):
        leaf(c, px, py + H * 0.06, W * ln, a, 0.3, "lance", 0.0, 2, LW, ink)
    draw_poly(c, pts, fill=True)
    # candle on the other side
    qx = cx + ww * 0.25
    c.rect(qx - W * 0.02, py, W * 0.04, H * 0.08, stroke=1, fill=1)
    flame = bezier_pts((qx, py + H * 0.085), (qx + W * 0.018, py + H * 0.1), (qx + W * 0.004, py + H * 0.12),
                       (qx, py + H * 0.135), 10) + bezier_pts((qx, py + H * 0.135), (qx - W * 0.004, py + H * 0.12),
                                                              (qx - W * 0.018, py + H * 0.1), (qx, py + H * 0.085), 10)
    draw_poly(c, flame, fill=True)


def wk_finale(c, box, ink, days=90, label=None):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    moon(c, cx, cy + H * 0.08, W * 0.26, ink, LW * 1.1, craters=True)
    for i in range(16):
        a = math.radians(360 * i / 16)
        r0, r1 = W * 0.3, W * (0.4 if i % 2 == 0 else 0.35)
        sparkle(c, cx + (r0 + r1) / 2 * math.cos(a), cy + H * 0.08 + (r0 + r1) / 2 * math.sin(a), W * 0.03, ink, LW)
    cloud(c, cx - W * 0.22, cy - H * 0.12, W * 0.42, ink, LW, bumps=(0.16, 0.27, 0.3, 0.2))
    cloud(c, cx + W * 0.24, cy - H * 0.1, W * 0.36, ink, LW, bumps=(0.2, 0.3, 0.22))
    shooting_star(c, x0 + W * 0.78, y1 - H * 0.08, W * 0.04, 210, W * 0.24, ink, LW)
    banner(c, cx, y0 + H * 0.06, W * 0.36, 34, label or f"{days} days", ink)
    for (fx, fy) in ((0.1, 0.88), (0.12, 0.24), (0.9, 0.26), (0.2, 0.62), (0.85, 0.6)):
        star(c, x0 + W * fx, y0 + H * fy, W * 0.025, ink, LW, rot=fx * 30)


def wk_star_quilt(c, box, ink):
    """A quilt of twelve tiles, each with its own little night motif."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    cols, rows = 3, 4
    tw, th = (W - 8) / cols, (H - 8) / rows
    for r in range(rows):
        for k in range(cols):
            tx, ty = x0 + 4 + k * tw, y0 + 4 + r * th
            cx, cy = tx + tw / 2, ty + th / 2
            setup(c, ink, LW)
            c.rect(tx, ty, tw, th, stroke=1, fill=0)
            c.roundRect(tx + 8, ty + 8, tw - 16, th - 16, 10, stroke=1, fill=0)
            s = min(tw, th) * 0.32
            i = r * cols + k
            # corner triangles
            for (ax, ay, sx, sy) in ((tx, ty, 1, 1), (tx + tw, ty, -1, 1), (tx, ty + th, 1, -1), (tx + tw, ty + th, -1, -1)):
                draw_poly(c, [(ax, ay), (ax + sx * 22, ay), (ax, ay + sy * 22)], fill=False)
            m = i % 6
            if m == 0:
                star(c, cx, cy, s, ink, LW, detail=True)
            elif m == 1:
                crescent(c, cx, cy, s, ink, LW, rot=20 + i * 10, craters=True)
            elif m == 2:
                sparkle(c, cx, cy, s * 1.05, ink, LW)
                sparkle(c, cx, cy, s * 0.45, ink, LW, rot=45)
            elif m == 3:
                moon(c, cx, cy, s * 0.8, ink, LW, craters=True, seed=i)
            elif m == 4:
                cloud(c, cx, cy - s * 0.15, s * 2.2, ink, LW, bumps=(0.2, 0.3, 0.22))
                star(c, cx + s * 0.6, cy + s * 0.65, s * 0.22, ink, LW)
            else:
                for j in range(3):
                    phase(c, cx - s * 0.75 + s * 0.75 * j, cy, s * 0.32, [0.2, 0.5, 0.8][j], ink, LW)


WEEKLY = [wk_moon_clouds, wk_constellations, wk_phase_wreath, wk_landscape, wk_star_frame, wk_dream_clouds,
          wk_moon_sunburst, wk_little_mandala, wk_star_quilt, wk_mobile, wk_planets, wk_window, wk_finale]

WEEKLY_TITLES = ["Moon in the clouds", "Constellations", "Moon phase wreath", "Night lake", "Starry frame",
                 "Dreamy clouds", "Moon sunburst", "Little mandala", "Star quilt", "Night mobile",
                 "Planets", "Night window", "You made it"]


def sampler(c, box, ink):
    """Nine little night pieces, each in its own frame."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    cw, ch = W / 3, H / 3
    for i in range(9):
        cx = x0 + cw * (i % 3 + 0.5)
        cy = y1 - ch * (i // 3 + 0.5)
        setup(c, ink, LW)
        c.roundRect(cx - cw / 2 + 5, cy - ch / 2 + 5, cw - 10, ch - 10, 14, stroke=1, fill=0)
        c.roundRect(cx - cw / 2 + 11, cy - ch / 2 + 11, cw - 22, ch - 22, 10, stroke=1, fill=0)
        s = min(cw, ch) * 0.34
        if i == 0:
            crescent(c, cx, cy, s, ink, LW, rot=20, craters=True)
        elif i == 1:
            star(c, cx, cy, s, ink, LW, detail=True)
        elif i == 2:
            moon(c, cx, cy, s * 0.85, ink, LW, craters=True)
        elif i == 3:
            cloud(c, cx, cy - s * 0.2, s * 2.2, ink, LW)
        elif i == 4:
            planet(c, cx, cy, s * 0.5, ink, LW)
        elif i == 5:
            sparkle(c, cx, cy, s, ink, LW)
            sparkle(c, cx, cy, s * 0.45, ink, LW, rot=45)
        elif i == 6:
            for k in range(5):
                phase(c, cx - s * 0.9 + s * 0.45 * k, cy, s * 0.2, [0.1, 0.25, 0.5, 0.75, 0.9][k], ink, LW)
        elif i == 7:
            constellation(c, [(cx - s * 0.8, cy - s * 0.4), (cx - s * 0.3, cy + s * 0.3), (cx + s * 0.2, cy - s * 0.1),
                              (cx + s * 0.7, cy + s * 0.5), (cx + s * 0.8, cy - s * 0.5)], ink, LW, r=s * 0.12)
        else:
            shooting_star(c, cx + s * 0.4, cy + s * 0.3, s * 0.35, 215, s * 1.3, ink, LW)


def shooting_stars(c, box, ink):
    cx, cy, W, H = fit(box)
    x0, y0, x1, y1 = box
    for (fx, fy, r, L) in ((0.75, 0.85, 0.06, 0.4), (0.4, 0.62, 0.05, 0.3), (0.85, 0.45, 0.045, 0.3),
                           (0.3, 0.3, 0.055, 0.35), (0.65, 0.18, 0.04, 0.25)):
        shooting_star(c, x0 + W * fx, y0 + H * fy, W * r, 210, W * L, ink, LW)
    crescent(c, x0 + W * 0.18, y0 + H * 0.85, W * 0.1, ink, LW, rot=30, craters=True)
    cloud(c, x0 + W * 0.26, y0 + H * 0.78, W * 0.3, ink, LW)
    cloud(c, x0 + W * 0.72, y0 + H * 0.06, W * 0.4, ink, LW)
    dots(c, (x0 + 10, y0 + 10, x1 - 10, y1 - 10), 46, ink, seed=21, r=1.6,
         avoid=[(x0 + W * fx, y0 + H * fy, W * 0.1) for fx, fy in ((0.75, 0.85), (0.4, 0.62), (0.85, 0.45),
                                                                     (0.3, 0.3), (0.65, 0.18), (0.2, 0.83), (0.72, 0.06))])


# --------------------------------------------------------------------------
# mood stars: one star per day, joined into a constellation
# --------------------------------------------------------------------------


def mood_cells(c, box, ink, muted, start_day=1, n_days=None):
    """30 (or 31) numbered stars along a winding constellation path. Without n_days (the journal's
    30-day pages) the path ends at a small crescent; months draw 31 stars and leave extra ones unnumbered."""
    cx, cy, W, H = fit(box)
    rows = [7, 6, 7, 6, 5] if n_days else [7, 6, 7, 6, 4]
    total = sum(rows)
    rnd = random.Random(8)
    pts = []
    nr = len(rows)
    for r, k in enumerate(rows):
        y = cy + H * 0.4 - H * 0.8 * r / (nr - 1)
        xs = [cx + (i - (k - 1) / 2) * W * 0.135 for i in range(k)]
        if r % 2:
            xs = xs[::-1]
        for x in xs:
            pts.append((x + rnd.uniform(-W * 0.012, W * 0.012), y + rnd.uniform(-H * 0.035, H * 0.035)))
    rr = min(W / 7, H / 5) * 0.4
    setup(c, ink, LW * 0.8)
    c.setDash(1.5, 3.5)
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
    end = None
    if not n_days:
        lx, ly = pts[-1]
        end = (lx - W * 0.12, ly)
        c.line(lx, ly, end[0], end[1])
    c.setDash()
    last = start_day + n_days - 1 if n_days else None
    for i, (x, y) in enumerate(pts):
        r = rr * (1.0 + 0.08 * ((i * 7) % 3 - 1))
        star(c, x, y, r, ink, LW * 1.15, rot=rnd.uniform(-8, 8), inner=0.55)
        num = start_day + i
        if last is None or num <= last:
            c.setFillColor(muted)
            c.setFont("Sans", 8)
            c.drawCentredString(x, y - 3.4, str(num))
    if end:
        crescent(c, end[0], end[1], rr * 0.9, ink, LW, rot=30)
    del total
