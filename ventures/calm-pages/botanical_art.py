"""Botanical line-art engine for Calm Petals.

Pressed-flower style: leaves with a gently bent midrib and side veins, ferns, eucalyptus,
cosmos, wild roses, ranunculus, bellflowers, lavender and buds. Everything is vector and
built from closed shapes filled white, so pieces layer cleanly and every region can be
colored. All drawing goes straight to a reportlab canvas.
"""
import math
import random

from reportlab.lib.colors import white

from butterfly_art import bezier_pts, draw_poly

LW = 1.05


def setup(c, ink, lw=LW, fill=None):
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setFillColor(fill if fill is not None else white)


# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------


def spline(pts, n=18):
    """Catmull-Rom curve through pts (dense point list)."""
    if len(pts) < 3:
        return bezier_pts(pts[0], pts[0], pts[-1], pts[-1], n)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j])
                                    * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(tuple(pts[-1]))
    return out


class Path:
    """A dense polyline with arc-length lookups."""

    def __init__(self, pts):
        self.pts = pts
        self.L = [0.0]
        for i in range(1, len(pts)):
            self.L.append(self.L[-1] + math.dist(pts[i], pts[i - 1]))
        self.length = self.L[-1]

    def at(self, t):
        """(x, y, tangent angle in degrees) at fraction t of the length."""
        s = max(0.0, min(1.0, t)) * self.length
        lo, hi = 0, len(self.L) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.L[mid] < s:
                lo = mid
            else:
                hi = mid
        p, q = self.pts[lo], self.pts[hi]
        seg = self.L[hi] - self.L[lo] or 1.0
        f = (s - self.L[lo]) / seg
        x, y = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
        return x, y, math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def curve(x, y, length, angle, bend=0.2, n=60):
    """A gently bent stem from (x, y) in direction angle; bend > 0 curves to the left."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    p0 = (x, y)
    p1 = (x + ux * length * 0.35 + nx * length * bend * 0.35, y + uy * length * 0.35 + ny * length * bend * 0.35)
    p2 = (x + ux * length * 0.7 + nx * length * bend * 0.75, y + uy * length * 0.7 + ny * length * bend * 0.75)
    p3 = (x + ux * length + nx * length * bend * 0.7, y + uy * length + ny * length * bend * 0.7)
    return bezier_pts(p0, p1, p2, p3, n)


def stroke(c, pts, ink, lw=LW):
    setup(c, ink, lw)
    draw_poly(c, pts, close=False)


def ribbon_stem(c, pts, w0, w1, ink, lw=LW, fill=None):
    """A stem with real width (two lines), tapering w0 -> w1, so it can be colored."""
    left, right = [], []
    n = len(pts)
    for i, (px, py) in enumerate(pts):
        q = pts[min(i + 1, n - 1)]
        p0 = pts[max(i - 1, 0)]
        tx, ty = q[0] - p0[0], q[1] - p0[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((px + nx * w, py + ny * w))
        right.append((px - nx * w, py - ny * w))
    setup(c, ink, lw, fill)
    draw_poly(c, left + right[::-1], fill=True)


# --------------------------------------------------------------------------
# leaves
# --------------------------------------------------------------------------

SHAPES = {
    "lance": lambda t: math.sin(math.pi * t) ** 0.85 * (1 - 0.38 * t),
    "ovate": lambda t: math.sin(math.pi * t ** 0.72) ** 0.9,
    "round": lambda t: math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)),
    "willow": lambda t: math.sin(math.pi * t) ** 0.7 * (1 - 0.25 * t),
    "petal": lambda t: math.sin(math.pi * t ** 0.85) ** 0.6,
}


def leaf_geom(x, y, length, angle, width=0.3, shape="lance", bend=0.0, n=36):
    """Outline points and a midrib function for a leaf from (x, y) pointing at angle."""
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    f = SHAPES[shape]

    def mid(t):
        off = bend * length * t * t
        return (x + ux * length * t + nx * off, y + uy * length * t + ny * off)

    def half(t):
        return width * length * f(t)

    left, right = [], []
    for i in range(n + 1):
        t = i / n
        mx, my = mid(t)
        # normal of the bent midrib
        dx = ux * length + nx * 2 * bend * length * t
        dy = uy * length + ny * 2 * bend * length * t
        L = math.hypot(dx, dy) or 1
        mnx, mny = -dy / L, dx / L
        w = half(t)
        left.append((mx + mnx * w, my + mny * w))
        right.append((mx - mnx * w, my - mny * w))
    return left + right[::-1], mid, half, (ux, uy, nx, ny)


def leaf(c, x, y, length, angle, width=0.3, shape="lance", bend=0.0, veins=3, lw=LW, ink=None, fill=None,
         midrib=True):
    """A leaf with a midrib and `veins` pairs of side veins."""
    pts, mid, half, (ux, uy, nx, ny) = leaf_geom(x, y, length, angle, width, shape, bend)
    setup(c, ink, lw, fill)
    draw_poly(c, pts, fill=True)
    if length < 14:
        return
    c.setLineWidth(lw * 0.75)
    if midrib:
        draw_poly(c, [mid(i / 20 * 0.9) for i in range(21)], close=False)
    for k in range(veins):
        t0 = 0.18 + 0.62 * k / max(veins, 1)
        t1 = min(t0 + 0.16, 0.95)
        for s in (1, -1):
            p0 = mid(t0)
            m1 = mid(t1)
            # direction of the side vein: toward the edge, leaning to the tip
            w = half(t1) * 0.72
            dx = ux * length + nx * 2 * bend * length * t1
            dy = uy * length + ny * 2 * bend * length * t1
            L = math.hypot(dx, dy) or 1
            mnx, mny = -dy / L, dx / L
            p2 = (m1[0] + mnx * w * s, m1[1] + mny * w * s)
            pc = mid((t0 + t1) / 2)
            pc = (pc[0] + mnx * w * 0.55 * s, pc[1] + mny * w * 0.55 * s)
            draw_poly(c, bezier_pts(p0, pc, pc, p2, 10), close=False)


def leafy_sprig(c, pts, n, size, ink, lw=LW, fill=None, shape="lance", width=0.3, spread=48, tip=True,
                start=0.12, veins=2, alternate=True, taper=0.45, stem_lw=None):
    """Leaves along a path (alternate or opposite), shrinking toward the tip."""
    P = Path(pts)
    for i in range(n):
        t = start + (0.92 - start) * i / max(n - 1, 1)
        x, y, ang = P.at(t)
        s = size * (1 - taper * (t - start) / (1 - start))
        sides = ((1 if i % 2 == 0 else -1),) if alternate else (1, -1)
        for side in sides:
            leaf(c, x, y, s, ang + spread * side, width, shape, bend=-0.06 * side, veins=veins, lw=lw, ink=ink,
                 fill=fill)
    stroke(c, pts, ink, stem_lw or lw)
    if tip:
        x, y, ang = P.at(1.0)
        leaf(c, x, y, size * (1 - taper) * 0.95, ang, width, shape, veins=veins, lw=lw, ink=ink, fill=fill)


def eucalyptus(c, pts, n, size, ink, lw=LW, fill=None, start=0.1):
    """Round silver-dollar leaves in opposite pairs along a stem."""
    P = Path(pts)
    for i in range(n):
        t = start + (0.92 - start) * i / max(n - 1, 1)
        x, y, ang = P.at(t)
        s = size * (1 - 0.42 * (t - start) / (1 - start))
        off = 8 * (1 if i % 2 else -1)
        for side in (1, -1):
            leaf(c, x, y, s, ang + (64 + off) * side, 0.44, "round", bend=0.0, veins=0, lw=lw, ink=ink, fill=fill)
    stroke(c, pts, ink, lw)
    x, y, ang = P.at(1.0)
    leaf(c, x, y, size * 0.5, ang, 0.44, "round", veins=0, lw=lw, ink=ink, fill=fill)


def fern(c, x, y, length, angle, bend=0.25, n=13, ink=None, lw=LW, fill=None, pinna=0.26, curl=False):
    """A fern frond: a curved rachis with paired leaflets that shrink toward the tip."""
    fern_path(c, curve(x, y, length, angle, bend, 120), n, ink, lw, fill, pinna, curl, bend >= 0)


def fern_path(c, pts, n=13, ink=None, lw=LW, fill=None, pinna=0.26, curl=False, left=True, start=0.06):
    P = Path(pts)
    length = P.length * (1 - start) / 0.94
    for i in range(n):
        t = start + (0.92 - start) * i / (n - 1)
        tl = (t - start) / (1 - start)
        px, py, ang = P.at(t)
        s = length * pinna * (1 - tl) ** 0.75 * min(1.0, 0.55 + tl * 2.2)
        for side in (1, -1):
            leaf(c, px, py, max(s, 3), ang + 58 * side, 0.27, "lance", bend=0.1 * side, veins=1 if s > 22 else 0,
                 lw=lw * 0.9, ink=ink, fill=fill)
    stroke(c, pts, ink, lw)
    ex, ey, ang = P.at(1.0)
    if curl:
        a0 = math.radians(ang + 90 * (1 if left else -1))
        r = length * 0.035
        cx, cy = ex + r * math.cos(a0), ey + r * math.sin(a0)
        sp = []
        for i in range(40):
            th = a0 + math.pi + (2.2 * math.pi) * i / 39 * (1 if left else -1)
            rr = r * (1 - 0.6 * i / 39)
            sp.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
        stroke(c, sp, ink, lw)
    else:
        leaf(c, ex, ey, length * pinna * 0.35, ang, 0.27, "lance", veins=0, lw=lw * 0.9, ink=ink, fill=fill)


def fiddlehead(c, x, y, length, angle, ink, lw=LW, turns=1.6, fill=None):
    """An unfurling fern tip: a stem that winds into a spiral, with small leaflet nubs."""
    a = math.radians(angle)
    pts = curve(x, y, length * 0.6, angle, 0.2, 40)
    ex, ey = pts[-1]
    r0 = length * 0.2
    dirn = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    cx, cy = ex + r0 * math.cos(dirn + math.pi / 2), ey + r0 * math.sin(dirn + math.pi / 2)
    sp = []
    th0 = dirn - math.pi / 2
    for i in range(80):
        th = th0 + turns * 2 * math.pi * i / 79
        rr = r0 * (1 - 0.82 * i / 79)
        sp.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    ribbon_stem(c, pts + sp[1:], length * 0.075, length * 0.02, ink, lw, fill)
    del a


# --------------------------------------------------------------------------
# flowers
# --------------------------------------------------------------------------


def _rot(px, py, a, x, y):
    ca, sa = math.cos(a), math.sin(a)
    return (x + px * ca - py * sa, y + px * sa + py * ca)


def cosmos(c, x, y, r, n=8, rot=0.0, ink=None, lw=LW, fill=None, center=None, detail=True):
    """Cosmos: broad petals with a toothed tip around a dotted center."""
    r0 = r * 0.16
    for i in range(n):
        a = math.radians(rot + 360 * i / n)
        side = []
        m = 20
        for k in range(m + 1):
            t = k / m
            xx = r0 + (r * 0.9 - r0) * t
            w = r * 0.25 * (0.22 + 0.78 * math.sin(t * math.pi / 2) ** 0.8)
            side.append((xx, w))
        we = side[-1][1]
        teeth = []
        for j in range(1, 36):
            v = 1 - 2 * j / 36
            bump = abs(math.sin(1.5 * math.pi * (v + 1))) ** 0.7
            teeth.append((r * 0.9 + r * 0.1 * bump * (1 - 0.25 * abs(v)), v * we))
        pts = side + teeth + [(px, -py) for (px, py) in reversed(side)]
        setup(c, ink, lw, fill)
        draw_poly(c, [_rot(px, py, a, x, y) for px, py in pts], fill=True)
        if detail and r > 18:
            c.setLineWidth(lw * 0.7)
            for yy in (-0.32, 0.32):
                draw_poly(c, [_rot(r0 + r * 0.12, yy * we * 0.4, a, x, y), _rot(r * 0.62, yy * we, a, x, y)],
                          close=False)
    setup(c, ink, lw, center)
    c.circle(x, y, r * 0.24, stroke=1, fill=1)
    if r > 14:
        setup(c, ink, lw * 0.8)
        m = max(8, int(r * 0.45))
        for i in range(m):
            a = 2 * math.pi * i / m
            c.circle(x + r * 0.15 * math.cos(a), y + r * 0.15 * math.sin(a), r * 0.025, stroke=1, fill=0)
        c.circle(x, y, r * 0.07, stroke=1, fill=0)


def wild_rose(c, x, y, r, rot=0.0, ink=None, lw=LW, fill=None, center=None, n=5):
    """Five notched, overlapping petals with a ring of stamens."""
    step = 360 / n
    for i in range(n):
        ac = rot + step * i
        pts = [(x, y)]
        m = 40
        for k in range(m + 1):
            u = -1 + 2 * k / m
            a = math.radians(ac + u * step * 0.62)
            rho = r * (0.78 + 0.22 * math.cos(u * math.pi / 2) ** 0.6)
            rho -= r * 0.11 * math.exp(-(u / 0.16) ** 2)
            pts.append((x + rho * math.cos(a), y + rho * math.sin(a)))
        setup(c, ink, lw, fill)
        draw_poly(c, pts, fill=True)
        if r > 16:
            c.setLineWidth(lw * 0.7)
            for u in (-0.35, 0.0, 0.35):
                a = math.radians(ac + u * step * 0.62)
                draw_poly(c, [(x + r * 0.3 * math.cos(a), y + r * 0.3 * math.sin(a)),
                              (x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a))], close=False)
    setup(c, ink, lw, center)
    c.circle(x, y, r * 0.2, stroke=1, fill=1)
    setup(c, ink, lw * 0.75)
    m = 16
    for i in range(m):
        a = 2 * math.pi * (i + 0.5) / m
        x0, y0 = x + r * 0.2 * math.cos(a), y + r * 0.2 * math.sin(a)
        x1, y1 = x + r * 0.31 * math.cos(a), y + r * 0.31 * math.sin(a)
        c.line(x0, y0, x1, y1)
        c.circle(x1, y1, max(r * 0.022, 0.6), stroke=1, fill=1)


def rosette(c, x, y, r, rings=4, rot=0.0, ink=None, lw=LW, fill=None, fill2=None):
    """A ranunculus / peony seen from above: rings of cupped petals, outer to inner."""
    for k in range(rings):
        R = r * (1 - k * (0.78 / rings))
        n = max(5, 10 - k)
        base = R * 0.35
        for i in range(n):
            ac = rot + (360 / n) * (i + 0.5 * (k % 2))
            pts = []
            m = 30
            for j in range(m + 1):
                u = -1 + 2 * j / m
                a = math.radians(ac + u * (360 / n) * 0.62)
                rho = R * (0.8 + 0.2 * math.cos(u * math.pi / 2))
                pts.append((x + rho * math.cos(a), y + rho * math.sin(a)))
            for j in range(m, -1, -1):
                u = -1 + 2 * j / m
                a = math.radians(ac + u * (360 / n) * 0.45)
                pts.append((x + base * math.cos(a), y + base * math.sin(a)))
            setup(c, ink, lw, fill if k % 2 == 0 else (fill2 if fill2 is not None else fill))
            draw_poly(c, pts, fill=True)
            if R > 24 and k < rings - 1:
                c.setLineWidth(lw * 0.65)
                inner = []
                for j in range(m + 1):
                    u = -0.75 + 1.5 * j / m
                    a = math.radians(ac + u * (360 / n) * 0.62)
                    rho = R * (0.68 + 0.12 * math.cos(u * math.pi / 2))
                    inner.append((x + rho * math.cos(a), y + rho * math.sin(a)))
                draw_poly(c, inner, close=False)
    # spiral heart
    setup(c, ink, lw)
    sp = []
    rr = r * 0.2
    for i in range(60):
        th = math.radians(rot) + 3.2 * math.pi * i / 59
        q = rr * (1 - i / 66)
        sp.append((x + q * math.cos(th) * 0.9, y + q * math.sin(th) * 0.9))
    c.setFillColor(fill if fill is not None else white)
    c.circle(x, y, rr, stroke=1, fill=1)
    draw_poly(c, sp, close=False)


def forget_me_not(c, x, y, r, rot=0.0, ink=None, lw=LW, fill=None, center=None):
    setup(c, ink, lw, fill)
    for i in range(5):
        a = math.radians(rot + 72 * i)
        c.circle(x + r * 0.52 * math.cos(a), y + r * 0.52 * math.sin(a), r * 0.48, stroke=1, fill=1)
    setup(c, ink, lw, center)
    c.circle(x, y, r * 0.24, stroke=1, fill=1)


def bell(c, x, y, s, angle=-90.0, ink=None, lw=LW, fill=None):
    """A hanging bellflower: (x, y) is where it joins the stalk; it opens toward angle."""
    a = math.radians(angle + 90)
    L = [(-0.14, 0.0), (-0.3, -0.25), (-0.36, -0.62), (-0.52, -0.92)]
    left = bezier_pts(*[(px * s, py * s) for px, py in L], 24)
    rim = []
    lobes = 4
    for k in range(lobes):
        xa = -0.52 + 1.04 * k / lobes
        xb = -0.52 + 1.04 * (k + 1) / lobes
        rim += bezier_pts((xa * s, -0.92 * s), (xa * s, -1.08 * s), (xb * s, -1.08 * s), (xb * s, -0.92 * s), 10)[1:]
    right = [(-px, py) for px, py in reversed(left)]
    pts = left + rim + right
    setup(c, ink, lw, fill)
    draw_poly(c, [_rot(px, py, a, x, y) for px, py in pts], fill=True)
    c.setLineWidth(lw * 0.7)
    for xx in (-0.16, 0.16):
        draw_poly(c, [_rot(px * s, py * s, a, x, y) for px, py in
                      bezier_pts((xx * 0.5, -0.1), (xx, -0.4), (xx * 1.4, -0.7), (xx * 1.9, -0.92), 12)],
                  close=False)
    # sepals
    setup(c, ink, lw, fill)
    for sd in (1, -1):
        leaf(c, x, y, s * 0.28, math.degrees(a) - 90 + 150 * sd, 0.28, "lance", veins=0, lw=lw * 0.9, ink=ink,
             fill=fill)


def bud(c, x, y, s, angle=90.0, ink=None, lw=LW, fill=None, leaf_fill=None):
    """A closed flower bud with two sepals, its base at (x, y)."""
    a = math.radians(angle - 90)
    pts = bezier_pts((0, 0), (0.42 * s, 0.25 * s), (0.3 * s, 0.8 * s), (0, 1.0 * s), 20) + \
        bezier_pts((0, 1.0 * s), (-0.3 * s, 0.8 * s), (-0.42 * s, 0.25 * s), (0, 0), 20)
    setup(c, ink, lw, fill)
    draw_poly(c, [_rot(px, py, a, x, y) for px, py in pts], fill=True)
    c.setLineWidth(lw * 0.7)
    draw_poly(c, [_rot(px, py, a, x, y) for px, py in bezier_pts((0, 0.2 * s), (0.18 * s, 0.5 * s),
                                                                    (0.1 * s, 0.8 * s), (0, 1.0 * s), 14)],
              close=False)
    for sd in (1, -1):
        leaf(c, x, y, s * 0.55, angle + 28 * sd, 0.26, "lance", bend=-0.1 * sd, veins=0, lw=lw * 0.9, ink=ink,
             fill=leaf_fill)


def lavender(c, pts, ink, lw=LW, fill=None, size=6.0, frac=0.45):
    """A lavender stem: buds in whorls along the top part of the path."""
    P = Path(pts)
    stroke(c, pts, ink, lw)
    n = int(P.length * frac / (size * 1.25))
    for i in range(n):
        t = 1 - frac + frac * i / max(n - 1, 1)
        x, y, ang = P.at(t)
        s = size * (1 - 0.45 * (t - (1 - frac)) / frac)
        for side in (1, -1):
            leaf(c, x, y, s * 1.5, ang + 34 * side, 0.36, "ovate", veins=0, lw=lw * 0.85, ink=ink, fill=fill)
    x, y, ang = P.at(1.0)
    leaf(c, x, y, size * 1.1, ang, 0.36, "ovate", veins=0, lw=lw * 0.85, ink=ink, fill=fill)


def berries(c, x, y, r, n, angle, ink, lw=LW, fill=None, seed=1):
    rnd = random.Random(seed)
    setup(c, ink, lw, fill)
    a = math.radians(angle)
    for i in range(n):
        d = r * (2.2 + 1.6 * i)
        bx = x + d * math.cos(a + rnd.uniform(-0.5, 0.5))
        by = y + d * math.sin(a + rnd.uniform(-0.5, 0.5))
        c.line(x, y, bx, by)
        c.circle(bx, by, r, stroke=1, fill=1)


def flower_on_stem(c, x, y, h, angle, kind, ink, lw=LW, fills=None, size=None, seed=0):
    """A stem with one or two leaves and a flower head of `kind` at the top. fills: (head, leaf, center)."""
    hf, lf, cf = fills or (None, None, None)
    rnd = random.Random(seed)
    pts = curve(x, y, h, angle, rnd.uniform(-0.12, 0.12), 50)
    P = Path(pts)
    stroke(c, pts, ink, lw)
    ls = min(h * 0.26, (size or h * 0.22) * 1.5)
    for t, sd in ((0.3, 1), (0.52, -1)):
        px, py, ang = P.at(t)
        leaf(c, px, py, ls, ang + 42 * sd, 0.26, "lance", bend=-0.08 * sd, veins=2, lw=lw, ink=ink, fill=lf)
    ex, ey, ang = P.at(1.0)
    s = size or h * 0.22
    if kind == "cosmos":
        cosmos(c, ex, ey, s, 8, rnd.uniform(0, 45), ink, lw, hf, cf)
    elif kind == "rose":
        wild_rose(c, ex, ey, s, rnd.uniform(0, 72), ink, lw, hf, cf)
    elif kind == "rosette":
        rosette(c, ex, ey, s, 3, rnd.uniform(0, 40), ink, lw, hf)
    elif kind == "bud":
        bud(c, ex, ey, s * 1.2, ang, ink, lw, hf, lf)
    elif kind == "daisy":
        from butterfly_art import draw_daisy
        draw_daisy(c, ex, ey, s, 13, lw, ink, center_fill=cf, petal_fill=hf, rotate=rnd.uniform(0, 30))
    elif kind == "forget":
        for k in range(3):
            a = math.radians(ang + 120 * k)
            forget_me_not(c, ex + s * 0.6 * math.cos(a), ey + s * 0.6 * math.sin(a), s * 0.55, k * 20, ink, lw,
                          hf, cf)
    return ex, ey


def bow(c, x, y, s, ink, lw=LW, fill=None):
    """A ribbon bow tied around a bunch of stems at (x, y)."""
    setup(c, ink, lw, fill)
    for sd in (1, -1):
        tail = [(x + sd * s * 0.08, y - s * 0.05), (x + sd * s * 0.35, y - s * 0.75), (x + sd * s * 0.62, y - s * 1.45),
                (x + sd * s * 0.42, y - s * 1.3), (x + sd * s * 0.3, y - s * 1.52), (x + sd * s * 0.12, y - s * 0.8),
                (x - sd * s * 0.06, y - s * 0.1)]
        draw_poly(c, tail, fill=True)
    for sd in (1, -1):
        loop = spline([(x, y), (x + sd * s * 0.45, y + s * 0.58), (x + sd * s * 1.12, y + s * 0.62),
                       (x + sd * s * 1.28, y + s * 0.12), (x + sd * s * 0.95, y - s * 0.32), (x + sd * s * 0.4, y - s * 0.22),
                       (x, y)], 10)
        draw_poly(c, loop, fill=True)
        c.setLineWidth(lw * 0.7)
        draw_poly(c, spline([(x + sd * s * 0.3, y + s * 0.05), (x + sd * s * 0.7, y + s * 0.25),
                             (x + sd * s * 0.95, y + s * 0.2)], 8), close=False)
        c.setLineWidth(lw)
    c.roundRect(x - s * 0.18, y - s * 0.2, s * 0.36, s * 0.4, s * 0.12, stroke=1, fill=1)


# --------------------------------------------------------------------------
# compositions used by the theme (accents, covers)
# --------------------------------------------------------------------------


def accent(c, x, y, size, k, angle, ink, F, lw=None):
    """Small pastel accent. F = (leaf, leaf2, flower, flower2, center) fills. size ~ radius."""
    lf, lf2, fl, fl2, cf = F
    lw = lw or (0.55 if size < 30 else 0.75)
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    kind = k % 6
    s = size
    if kind == 0:   # wildflower sprig
        pts = curve(-s * 0.15, -s * 1.0, s * 1.55, 82, 0.15, 30)
        P = Path(pts)
        px, py, a = P.at(0.35)
        leaf(c, px, py, s * 0.62, a + 48, 0.3, "lance", -0.06, veins=1, lw=lw, ink=ink, fill=lf)
        px, py, a = P.at(0.55)
        leaf(c, px, py, s * 0.5, a - 50, 0.3, "lance", 0.06, veins=1, lw=lw, ink=ink, fill=lf2)
        stroke(c, pts, ink, lw)
        ex, ey, _ = P.at(1.0)
        wild_rose(c, ex, ey, s * 0.42, 10, ink, lw, fl, cf)
    elif kind == 1:   # eucalyptus
        eucalyptus(c, curve(-s * 0.3, -s * 1.0, s * 2.0, 75, -0.2, 40), 4, s * 0.48, ink, lw, lf2)
    elif kind == 2:   # fern
        fern(c, -s * 0.2, -s * 1.0, s * 2.0, 80, -0.25, 9, ink, lw, lf, pinna=0.3)
    elif kind == 3:   # bud and leaf
        pts = curve(0, -s, s * 1.4, 92, -0.1, 30)
        P = Path(pts)
        px, py, a = P.at(0.4)
        leaf(c, px, py, s * 0.7, a - 45, 0.32, "lance", 0.08, veins=2, lw=lw, ink=ink, fill=lf)
        stroke(c, pts, ink, lw)
        ex, ey, a = P.at(1.0)
        bud(c, ex, ey, s * 0.62, a, ink, lw, fl2, lf2)
    elif kind == 4:   # cosmos head
        cosmos(c, 0, s * 0.1, s * 0.78, 8, 12, ink, lw, fl, cf, detail=size > 20)
        leaf(c, s * 0.2, -s * 0.45, s * 0.7, -30, 0.3, "lance", 0.06, veins=1, lw=lw, ink=ink, fill=lf)
    else:   # lavender pair
        lavender(c, curve(-s * 0.15, -s, s * 2.0, 84, 0.06, 40), ink, lw, fl2, size=s * 0.12, frac=0.5)
        lavender(c, curve(s * 0.15, -s, s * 1.7, 100, -0.06, 40), ink, lw, fl, size=s * 0.11, frac=0.5)
    c.restoreState()


def stem_to(base, tie, head, bulge=0.0, n=24):
    """A stem from the cut end through the tie point to the head, with a sideways bulge."""
    mx, my = (tie[0] + head[0]) / 2, (tie[1] + head[1]) / 2
    dx, dy = head[0] - tie[0], head[1] - tie[1]
    L = math.hypot(dx, dy) or 1
    mid = (mx - dy / L * bulge * L, my + dx / L * bulge * L)
    return spline([base, tie, mid, head], n)


def bouquet(c, cx, cy, s, ink, F, lw=1.0, heads=True):
    """The cover bouquet: a hand-tied bunch, stems gathered under a bow. s ~ half the height."""
    lf, lf2, fl, fl2, cf, rib = F
    tie = (cx, cy - s * 0.55)

    def base(dx):
        return (cx + dx * s, cy - s * 0.98)

    def P(dx, dy):
        return (cx + dx * s, cy + dy * s)

    # back layer: foliage
    fern_path(c, stem_to(base(-0.05), tie, P(-0.92, 0.12), 0.12), 13, ink, lw * 0.9, lf, 0.3, start=0.42)
    fern_path(c, stem_to(base(-0.02), tie, P(-0.55, 0.88), -0.1), 12, ink, lw * 0.9, lf, 0.28, start=0.45)
    eucalyptus(c, stem_to(base(0.05), tie, P(0.95, 0.1), -0.15), 6, s * 0.15, ink, lw * 0.9, lf2, start=0.45)
    eucalyptus(c, stem_to(base(0.03), tie, P(0.62, 0.86), 0.12), 5, s * 0.13, ink, lw * 0.9, lf2, start=0.5)
    leafy_sprig(c, stem_to(base(0.0), tie, P(0.05, 1.08), 0.06), 8, s * 0.2, ink, lw * 0.9, lf, "willow", 0.2,
                spread=34, veins=1, start=0.5)
    lavender(c, stem_to(base(-0.03), tie, P(-0.4, 1.02), -0.05), ink, lw * 0.9, fl2, size=s * 0.04, frac=0.35)
    lavender(c, stem_to(base(0.03), tie, P(0.36, 1.0), 0.05), ink, lw * 0.9, fl2, size=s * 0.04, frac=0.35)
    if not heads:
        return
    items = [
        ("bud", P(-0.2, 0.86), 0.1), ("bud", P(0.68, 0.5), -0.1), ("bells", P(0.3, 0.68), -0.08),
        ("rose", P(-0.5, 0.08), 0.06), ("rosette", P(0.34, 0.2), -0.06), ("daisy", P(0.02, -0.12), 0.0),
        ("cosmos", P(-0.12, 0.42), 0.04),
    ]
    stems = [(kind, stem_to(base(0.0), tie, hd, bl)) for kind, hd, bl in items]
    for kind, pts in stems:
        stroke(c, pts, ink, lw)
    for kind, pts in stems:
        Pp = Path(pts)
        if kind in ("rose", "rosette"):
            px, py, a = Pp.at(0.78)
            leaf(c, px, py, s * 0.22, a + (44 if kind == "rose" else -44), 0.28, "lance", 0.0, 2, lw, ink, lf)
    for kind, pts in stems:
        ex, ey, a = Path(pts).at(1.0)
        if kind == "cosmos":
            cosmos(c, ex, ey, s * 0.31, 8, 8, ink, lw, fl, cf)
        elif kind == "rose":
            wild_rose(c, ex, ey, s * 0.21, 20, ink, lw, fl2, cf)
        elif kind == "rosette":
            rosette(c, ex, ey, s * 0.22, 3, 10, ink, lw, fl, fl2)
        elif kind == "daisy":
            from butterfly_art import draw_daisy
            draw_daisy(c, ex, ey, s * 0.13, 13, lw, ink, center_fill=cf, petal_fill=None, rotate=6)
        elif kind == "bud":
            bud(c, ex, ey, s * 0.14, a, ink, lw, fl2, lf2)
        elif kind == "bells":
            for k, (dx, dy, sz) in enumerate(((0.0, 0.0, 0.085), (-0.1, -0.1, 0.075), (0.11, -0.13, 0.07))):
                bx, by = ex + dx * s, ey + dy * s
                if k:
                    stroke(c, bezier_pts((ex, ey), (bx, ey + s * 0.02), (bx, by + s * 0.06), (bx, by), 12), ink, lw)
                bell(c, bx, by, s * sz, -90, ink, lw, fl2)
    # tie
    bow(c, tie[0], tie[1], s * 0.12, ink, lw, rib)


def wreath(c, cx, cy, R, ink, F, lw=1.0, open_top=False, density=1.0, scale=1.0):
    """A ring of mixed foliage with a few blooms. F = (leaf, leaf2, flower, flower2, center)."""
    lf, lf2, fl, fl2, cf = F
    a0, a1 = (110, 430) if open_top else (90, 450)
    n = int(26 * density)
    # vine
    vine = [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / 200)),
             cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / 200))) for i in range(201)]
    for i in range(n):
        t = (i + 0.5) / n
        a = a0 + (a1 - a0) * t
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        tang = a + 90
        kind = i % 4
        k = R * scale
        if kind == 0:
            leaf(c, x, y, k * 0.24, tang + 38, 0.28, "lance", -0.06, 2, lw, ink, lf)
            leaf(c, x, y, k * 0.2, tang - 34, 0.28, "lance", 0.06, 1, lw, ink, lf2)
        elif kind == 1:
            leaf(c, x, y, k * 0.13, tang + 70, 0.44, "round", 0, 0, lw, ink, lf2)
            leaf(c, x, y, k * 0.12, tang - 70, 0.44, "round", 0, 0, lw, ink, lf2)
        elif kind == 2:
            leaf(c, x, y, k * 0.2, tang + 26, 0.3, "ovate", -0.04, 2, lw, ink, lf)
        else:
            leaf(c, x, y, k * 0.18, tang - 30, 0.22, "willow", 0.06, 1, lw, ink, lf)
    stroke(c, vine, ink, lw)
    return vine
