"""Butterfly line-art engine for the Calm Wings journal.

Everything here is vector: wings are smooth polar "lobes" built from a radius
profile, mirrored for perfect symmetry, then decorated with bands, veins, spots
and eyespots. All drawing goes straight to a reportlab canvas.
"""
import math
import random

from reportlab.lib.colors import HexColor, white

# --------------------------------------------------------------------------
# small math helpers
# --------------------------------------------------------------------------


def catmull(vals, u):
    """Catmull-Rom interpolation of evenly spaced values at u in [0, 1]."""
    n = len(vals) - 1
    t = min(max(u, 0.0), 1.0) * n
    i = min(int(t), n - 1)
    f = t - i
    p0 = vals[max(i - 1, 0)]
    p1 = vals[i]
    p2 = vals[i + 1]
    p3 = vals[min(i + 2, n)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def rot(pt, ang, about=(0, 0)):
    a = math.radians(ang)
    x, y = pt[0] - about[0], pt[1] - about[1]
    return (about[0] + x * math.cos(a) - y * math.sin(a),
            about[1] + x * math.sin(a) + y * math.cos(a))


class Tf:
    """Maps unit butterfly coordinates to page points."""

    def __init__(self, cx, cy, size, angle=0.0, mirror=False):
        self.cx, self.cy, self.s, self.a, self.m = cx, cy, size, angle, mirror

    def __call__(self, p):
        x, y = p
        if self.m:
            x = -x
        x, y = rot((x * self.s, y * self.s), self.a)
        return (self.cx + x, self.cy + y)


def poly_path(c, pts, close=True):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def draw_poly(c, pts, stroke=True, fill=False, close=True):
    c.drawPath(poly_path(c, pts, close), stroke=1 if stroke else 0, fill=1 if fill else 0)


def circle_pts(cx, cy, r, n=64):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


# --------------------------------------------------------------------------
# wings
# --------------------------------------------------------------------------


class Wing:
    """A wing on the right side of the body, in unit coordinates.

    root: attachment point. a0 -> a1: sweep of angles (degrees) from the
    root. prof: radius profile sampled evenly over the sweep (ends at 0).
    """

    def __init__(self, root, a0, a1, prof, scallop=0, sdepth=0.0, tail=None):
        self.root = root
        self.a0, self.a1 = a0, a1
        self.prof = prof
        self.scallop = scallop
        self.sdepth = sdepth
        self.tail = tail

    def r(self, u):
        r = max(catmull(self.prof, u), 0.0)
        if self.scallop:
            w = min(1.0, max(0.0, (u - 0.08) / 0.12)) * min(1.0, max(0.0, (0.92 - u) / 0.12))
            s = abs(math.sin(math.pi * self.scallop * u)) ** 0.45
            r *= 1 - self.sdepth * w * (1 - s)
        if self.tail:
            tu, tw, tl = self.tail
            r *= 1 + tl * math.exp(-((u - tu) / tw) ** 2)
        return r

    def phi(self, u):
        return math.radians(self.a0 + (self.a1 - self.a0) * u)

    def pt(self, u, k=1.0):
        r = self.r(u) * k
        ph = self.phi(u)
        return (self.root[0] + r * math.cos(ph), self.root[1] + r * math.sin(ph))

    def outline(self, k=1.0, n=280, u0=0.0, u1=1.0):
        return [self.pt(u0 + (u1 - u0) * i / n, k) for i in range(n + 1)]


# --------------------------------------------------------------------------
# butterfly styles
# --------------------------------------------------------------------------

# Each style: fore / hind wing specs plus pattern lists.
# Pattern items:
#   ("band", k)                    inner outline at fraction k
#   ("veins", n, k0, k1, bend)     radial veins
#   ("spots", n, k, size)          spots between veins
#   ("eye", u, k, size, rings)     eyespot
#   ("edge", n, k, size)           tiny dots along the margin
#   ("drops", n, k0, k1)           teardrop cells between veins

F_STD = dict(root=(0.03, 0.06), a0=82, a1=-8, prof=[0, 0.74, 0.96, 1.0, 0.93, 0.78, 0.6, 0.0])
H_STD = dict(root=(0.03, -0.02), a0=-12, a1=-98, prof=[0, 0.6, 0.74, 0.75, 0.68, 0.52, 0.0])


def _w(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


STYLES = {
    "classic": dict(
        fore=_w(F_STD),
        hind=_w(H_STD),
        fpat=[("band", 0.42), ("veins", 5, 0.42, 0.8, 0.04), ("band", 0.8), ("edge", 9, 0.9, 0.02)],
        hpat=[("band", 0.45), ("veins", 4, 0.45, 0.78, 0.04), ("band", 0.78), ("edge", 7, 0.89, 0.02)],
    ),
    "swallowtail": dict(
        fore=_w(F_STD, a0=80, a1=-2, prof=[0, 0.8, 1.02, 1.04, 0.92, 0.72, 0.5, 0.0]),
        hind=_w(H_STD, a0=-8, a1=-100, prof=[0, 0.52, 0.64, 0.68, 0.66, 0.56, 0.0],
                scallop=6, sdepth=0.06, tail=(0.6, 0.045, 0.62)),
        fpat=[("band", 0.36), ("band", 0.66), ("veins", 5, 0.36, 0.66, 0.0), ("spots", 5, 0.83, 0.06)],
        hpat=[("band", 0.5), ("veins", 3, 0.0, 0.5, 0.0), ("edge", 5, 0.8, 0.035)],
    ),
    "round": dict(
        fore=_w(F_STD, a0=86, a1=-4, prof=[0, 0.8, 0.95, 0.98, 0.92, 0.78, 0.0]),
        hind=_w(H_STD, a0=-10, a1=-100, prof=[0, 0.7, 0.8, 0.8, 0.7, 0.0]),
        fpat=[("band", 0.52), ("spots", 4, 0.77, 0.085), ("veins", 3, 0.0, 0.52, 0.05)],
        hpat=[("band", 0.52), ("spots", 3, 0.76, 0.085), ("veins", 2, 0.0, 0.52, 0.05)],
    ),
    "scallop": dict(
        fore=_w(F_STD, scallop=8, sdepth=0.09),
        hind=_w(H_STD, scallop=6, sdepth=0.13),
        fpat=[("band", 0.3), ("drops", 5, 0.36, 0.74), ("band", 0.82)],
        hpat=[("band", 0.3), ("drops", 4, 0.36, 0.72), ("band", 0.8)],
    ),
    "peacock": dict(
        fore=_w(F_STD, scallop=7, sdepth=0.06),
        hind=_w(H_STD, scallop=5, sdepth=0.1),
        fpat=[("eye", 0.4, 0.64, 0.14, 3), ("band", 0.9), ("veins", 2, 0.0, 0.38, 0.05)],
        hpat=[("eye", 0.5, 0.6, 0.13, 3), ("band", 0.9), ("veins", 2, 0.0, 0.33, 0.05)],
    ),
    "petal": dict(
        fore=_w(F_STD, a0=76, a1=6, prof=[0, 0.6, 0.92, 1.04, 0.98, 0.78, 0.0]),
        hind=_w(H_STD, a0=-14, a1=-92, prof=[0, 0.66, 0.84, 0.8, 0.6, 0.0]),
        fpat=[("veins", 5, 0.12, 0.9, 0.07), ("band", 0.9)],
        hpat=[("veins", 4, 0.12, 0.88, 0.07), ("band", 0.88)],
    ),
    "monarch": dict(
        fore=_w(F_STD, a0=80, a1=-10, prof=[0, 0.7, 0.96, 1.04, 0.98, 0.8, 0.6, 0.0]),
        hind=_w(H_STD),
        fpat=[("veins", 6, 0.08, 0.84, 0.09), ("band", 0.84), ("edge", 12, 0.92, 0.017)],
        hpat=[("veins", 5, 0.1, 0.82, 0.09), ("band", 0.82), ("edge", 9, 0.91, 0.017)],
    ),
    "simple": dict(
        fore=_w(F_STD, prof=[0, 0.76, 0.96, 1.0, 0.92, 0.74, 0.0]),
        hind=_w(H_STD, prof=[0, 0.66, 0.78, 0.76, 0.64, 0.0]),
        fpat=[("band", 0.6)],
        hpat=[("band", 0.6)],
    ),
    "mandala": dict(
        fore=_w(F_STD),
        hind=_w(H_STD),
        fpat=[("band", 0.55), ("veins", 3, 0.0, 0.55, 0.05)],
        hpat=[("band", 0.55), ("veins", 2, 0.0, 0.55, 0.05)],
    ),
    "lacy": dict(
        fore=_w(F_STD, scallop=10, sdepth=0.05),
        hind=_w(H_STD, scallop=7, sdepth=0.08),
        fpat=[("band", 0.34), ("veins", 4, 0.34, 0.62, 0.0), ("band", 0.62), ("edge", 10, 0.79, 0.04)],
        hpat=[("band", 0.36), ("veins", 3, 0.36, 0.62, 0.0), ("band", 0.62), ("edge", 7, 0.79, 0.045)],
    ),
}


def make_wings(style):
    st = STYLES[style] if isinstance(style, str) else style
    return Wing(**st["fore"]), Wing(**st["hind"]), st


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------


def _vein(w, u, k0, k1, bend, n=40):
    pts = []
    for i in range(n + 1):
        k = k0 + (k1 - k0) * i / n
        uu = u + bend * math.sin(math.pi * (k - k0) / max(k1 - k0, 1e-6)) * (0.5 - u) * 2
        pts.append(w.pt(uu, k))
    return pts


def _local_width(w, u, k):
    """Approximate available half-width around a point (for spot sizes)."""
    return w.r(u) * k


def draw_wing(c, w, pat, tf, lw, ink, fill=None, fill2=None, detail=1.0):
    outline = [tf(p) for p in w.outline()]
    c.setStrokeColor(ink)
    c.setFillColor(fill if fill is not None else white)
    c.setLineWidth(lw * 1.25)
    draw_poly(c, outline, stroke=True, fill=True)
    c.setLineWidth(lw)
    for item in pat:
        kind = item[0]
        if kind == "band":
            k = item[1]
            pts = [tf(p) for p in w.outline(k)]
            if fill2 is not None and k <= 0.65:
                c.setFillColor(fill2)
                draw_poly(c, pts, stroke=True, fill=True)
            else:
                draw_poly(c, pts)
        elif kind == "veins":
            _, n, k0, k1, bend = item
            for i in range(n):
                u = (i + 1) / (n + 1)
                draw_poly(c, [tf(p) for p in _vein(w, u, k0, k1, bend)], close=False)
        elif kind == "spots":
            _, n, k, size = item
            for i in range(n):
                u = 0.16 + 0.68 * (i + 0.5) / n
                cx, cy = tf(w.pt(u, k))
                r = size * tf.s * (0.6 + 0.4 * w.r(u) / max(w.prof))
                if fill2 is not None:
                    c.setFillColor(fill2)
                    c.circle(cx, cy, r, stroke=1, fill=1)
                else:
                    c.circle(cx, cy, r, stroke=1, fill=0)
        elif kind == "edge":
            _, n, k, size = item
            for i in range(n):
                u = 0.12 + 0.76 * (i + 0.5) / n
                cx, cy = tf(w.pt(u, k))
                c.circle(cx, cy, size * tf.s, stroke=1, fill=0)
        elif kind == "eye":
            _, u, k, size, rings = item
            cx, cy = tf(w.pt(u, k))
            for j in range(rings):
                r = size * tf.s * (1 - j / (rings + 0.3))
                if fill2 is not None and j == rings - 1:
                    c.setFillColor(fill2)
                    c.circle(cx, cy, r, stroke=1, fill=1)
                else:
                    c.circle(cx, cy, r, stroke=1, fill=0)
        elif kind == "drops":
            _, n, k0, k1 = item
            for i in range(n):
                ua = 0.06 + 0.88 * i / n + 0.02
                ub = 0.06 + 0.88 * (i + 1) / n - 0.02
                draw_poly(c, [tf(p) for p in _drop(w, ua, ub, k0, k1)])


def _drop(w, ua, ub, k0, k1, n=50):
    """Closed teardrop between angles ua..ub, pointing to the root."""
    um = (ua + ub) / 2
    hw = (ub - ua) / 2
    pts = []
    for i in range(n + 1):
        t = i / n  # 0..1 along one side, from tip to head
        ang = math.pi * t
        # width profile: 0 at tip, widest near the head, round cap
        kk = k0 + (k1 - k0) * (1 - math.cos(ang)) / 2
        wd = hw * math.sin(ang) ** 0.6 if t < 1 else 0
        pts.append(w.pt(um + wd, kk))
    for i in range(n, -1, -1):
        t = i / n
        ang = math.pi * t
        kk = k0 + (k1 - k0) * (1 - math.cos(ang)) / 2
        wd = hw * math.sin(ang) ** 0.6
        pts.append(w.pt(um - wd, kk))
    return pts


def draw_body(c, tf, lw, ink, fill=None, segments=True, antennae=1.0):
    c.setStrokeColor(ink)
    c.setLineWidth(lw * 1.2)
    c.setFillColor(fill if fill is not None else white)
    # abdomen
    ab = []
    n = 60
    for i in range(n + 1):
        t = i / n
        y = 0.0 - 0.5 * t
        x = 0.05 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7 * (1 - 0.35 * t)
        ab.append((x, y))
    abd = [tf(p) for p in ab] + [tf((-x, y)) for (x, y) in reversed(ab)]
    draw_poly(c, abd, fill=True)
    if segments:
        c.setLineWidth(lw * 0.8)
        for j in range(1, 6):
            y = -0.08 * j
            t = -y / 0.5
            x = 0.05 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7 * (1 - 0.35 * t)
            arc = [tf((x * math.cos(a), y - 0.012 * math.sin(a))) for a in
                   [math.pi * q / 16 for q in range(17)]]
            draw_poly(c, arc, close=False)
    # thorax
    c.setLineWidth(lw * 1.2)
    th = [tf((0.06 * math.cos(a), 0.06 + 0.1 * math.sin(a))) for a in
          [2 * math.pi * q / 48 for q in range(48)]]
    draw_poly(c, th, fill=True)
    # head
    hd = [tf((0.045 * math.cos(a), 0.2 + 0.045 * math.sin(a))) for a in
          [2 * math.pi * q / 40 for q in range(40)]]
    draw_poly(c, hd, fill=True)
    # antennae
    if antennae:
        for sgn in (1, -1):
            pts = []
            for i in range(31):
                t = i / 30
                x = sgn * (0.02 + 0.1 * t * antennae + 0.035 * math.sin(math.pi * t) * antennae)
                y = 0.23 + 0.34 * t * antennae - 0.02 * t * t * antennae
                pts.append(tf((x, y)))
            c.setLineWidth(lw)
            draw_poly(c, pts, close=False)
            ex, ey = pts[-1]
            c.setFillColor(fill if fill is not None else white)
            c.circle(ex, ey, max(0.022 * tf.s, 1.2), stroke=1, fill=1)


def draw_butterfly(c, cx, cy, size, style="classic", angle=0.0, lw=1.0, ink=None,
                   fills=None, body_fill=None, antennae=1.0, segments=True):
    """Draw a symmetric butterfly. size = distance from body to wing tip (pt).

    fills: None for pure line art, else (fore_fill, hind_fill, accent_fill).
    """
    ink = ink or HexColor("#4B4D60")
    fw, hw, st = make_wings(style)
    c.saveState()
    c.setLineJoin(1)
    c.setLineCap(1)
    ff = hf = acc = None
    if fills:
        ff, hf, acc = fills
    for mirror in (False, True):
        tf = Tf(cx, cy, size, angle, mirror)
        draw_wing(c, hw, st["hpat"], tf, lw, ink, hf, acc)
    for mirror in (False, True):
        tf = Tf(cx, cy, size, angle, mirror)
        draw_wing(c, fw, st["fpat"], tf, lw, ink, ff, acc)
    draw_body(c, Tf(cx, cy, size, angle), lw, ink, body_fill, segments, antennae)
    c.restoreState()


# --------------------------------------------------------------------------
# geometric (low-poly) butterfly
# --------------------------------------------------------------------------


def draw_geometric(c, cx, cy, size, lw=1.0, ink=None, variant=0, halo=0):
    ink = ink or HexColor("#4B4D60")
    if variant == 0:
        fore = Wing((0.03, 0.05), 98, 0, [0, 0.66, 0.94, 1.02, 0.98, 0.84, 0.62, 0.0])
        hind = Wing((0.03, -0.02), -6, -100, [0, 0.6, 0.76, 0.78, 0.7, 0.55, 0.0])
        nf, nh, rings = 7, 5, (0.38, 0.7)
    else:
        fore = Wing((0.03, 0.05), 104, 6, [0, 0.7, 0.95, 1.0, 0.92, 0.75, 0.0])
        hind = Wing((0.03, -0.02), -4, -104, [0, 0.66, 0.82, 0.8, 0.66, 0.0])
        nf, nh, rings = 6, 4, (0.4, 0.72)
    c.saveState()
    c.setLineJoin(1)
    c.setLineCap(1)
    c.setStrokeColor(ink)

    def facets(w, n, mirror):
        tf = Tf(cx, cy, size, 0, mirror)
        us = [0.04 + 0.92 * i / n for i in range(n + 1)]
        levels = list(rings) + [1.0]
        grid = [[w.pt(u, k) for u in us] for k in levels]
        outer = [w.root] + grid[-1] + [w.root]
        c.setFillColor(white)
        c.setLineWidth(lw * 1.3)
        draw_poly(c, [tf(p) for p in outer], fill=True)
        c.setLineWidth(lw)
        # inner fan: only every second vertex reaches the root
        draw_poly(c, [tf(p) for p in grid[0]], close=False)
        for i in range(0, n + 1, 2):
            draw_poly(c, [tf(w.root), tf(grid[0][i])], close=False)
        for li in range(1, len(levels)):
            for i in range(n):
                a, b = grid[li - 1][i], grid[li - 1][i + 1]
                d, e = grid[li][i], grid[li][i + 1]
                draw_poly(c, [tf(a), tf(b), tf(e), tf(d)])
                if (i + li + variant) % 2 == 0:
                    draw_poly(c, [tf(a), tf(e)], close=False)
                else:
                    draw_poly(c, [tf(b), tf(d)], close=False)

    if halo:
        c.setStrokeColor(white)
        c.setFillColor(white)
        c.setLineWidth(halo)
        for w in (hind, fore):
            for m in (False, True):
                tf = Tf(cx, cy, size, 0, m)
                draw_poly(c, [tf(p) for p in w.outline(n=60)], fill=True)
        c.setStrokeColor(ink)
    for m in (False, True):
        facets(hind, nh, m)
    for m in (False, True):
        facets(fore, nf, m)
    # diamond body
    tf = Tf(cx, cy, size)
    c.setFillColor(white)
    c.setLineWidth(lw * 1.2)
    body = [(0, 0.26), (0.075, 0.08), (0.06, -0.1), (0, -0.52), (-0.06, -0.1), (-0.075, 0.08)]
    draw_poly(c, [tf(p) for p in body], fill=True)
    c.setLineWidth(lw)
    draw_poly(c, [tf((0.075, 0.08)), tf((-0.075, 0.08))], close=False)
    draw_poly(c, [tf((0.06, -0.1)), tf((-0.06, -0.1))], close=False)
    draw_poly(c, [tf((0, 0.26)), tf((0, -0.5))], close=False)
    for s in (1, -1):
        draw_poly(c, [tf((0.0, 0.26)), tf((0.1 * s, 0.42)), tf((0.22 * s, 0.5))], close=False)
        d = [(0.22 * s, 0.54), (0.25 * s, 0.5), (0.22 * s, 0.46), (0.19 * s, 0.5)]
        draw_poly(c, [tf(p) for p in d], fill=True)
    c.restoreState()


# --------------------------------------------------------------------------
# flowers, leaves and other bits
# --------------------------------------------------------------------------


def petal_pts(cx, cy, length, width, angle, n=40, base=0.0):
    """A petal / leaf shape from (cx,cy) pointing at angle."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = base + length * t
        y = width * math.sin(math.pi * t) ** 0.9 * (1 - 0.25 * t)
        pts.append((x, y))
    for i in range(n, -1, -1):
        t = i / n
        x = base + length * t
        y = -width * math.sin(math.pi * t) ** 0.9 * (1 - 0.25 * t)
        pts.append((x, y))
    return [(cx + p[0] * math.cos(math.radians(angle)) - p[1] * math.sin(math.radians(angle)),
             cy + p[0] * math.sin(math.radians(angle)) + p[1] * math.cos(math.radians(angle)))
            for p in pts]


def draw_daisy(c, cx, cy, r, petals=12, lw=1.0, ink=None, center_fill=None, petal_fill=None,
               rotate=0.0, inner=True):
    ink = ink or HexColor("#4B4D60")
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineJoin(1)
    for i in range(petals):
        a = rotate + 360 * i / petals
        c.setFillColor(petal_fill if petal_fill is not None else white)
        draw_poly(c, petal_pts(cx, cy, r, r * 0.22, a, base=r * 0.18), fill=True)
        if inner:
            pts = petal_pts(cx, cy, r * 0.55, 0.0001, a, n=2, base=r * 0.38)
            draw_poly(c, pts[:2], close=False)
    c.setFillColor(center_fill if center_fill is not None else white)
    c.circle(cx, cy, r * 0.3, stroke=1, fill=1)
    c.circle(cx, cy, r * 0.17, stroke=1, fill=0)
    c.restoreState()


def draw_leaf(c, x, y, length, angle, lw=1.0, ink=None, vein=True, fill=None):
    ink = ink or HexColor("#4B4D60")
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setFillColor(fill if fill is not None else white)
    pts = petal_pts(x, y, length, length * 0.28, angle)
    draw_poly(c, pts, fill=True)
    if vein:
        a = math.radians(angle)
        draw_poly(c, [(x + 0.05 * length * math.cos(a), y + 0.05 * length * math.sin(a)),
                      (x + 0.85 * length * math.cos(a), y + 0.85 * length * math.sin(a))], close=False)
    c.restoreState()


def draw_stem(c, pts, lw=1.0, ink=None):
    ink = ink or HexColor("#4B4D60")
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(*pts[0])
    if len(pts) == 4:
        p.curveTo(*pts[1], *pts[2], *pts[3])
    else:
        for q in pts[1:]:
            p.lineTo(*q)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def bezier_pts(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        cc = 3 * (1 - t) * t * t
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + cc * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + cc * p2[1] + d * p3[1]))
    return out


def draw_tulip(c, x, y, h, lw=1.0, ink=None, fill=None):
    ink = ink or HexColor("#4B4D60")
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setFillColor(fill if fill is not None else white)
    w = h * 0.22
    top = y + h
    cup = (bezier_pts((x - w, top), (x - w * 1.1, top - h * 0.25), (x - w * 0.6, top - h * 0.36), (x, top - h * 0.36))
           + bezier_pts((x, top - h * 0.36), (x + w * 0.6, top - h * 0.36), (x + w * 1.1, top - h * 0.25), (x + w, top))
           + [(x + w * 0.5, top - h * 0.1), (x, top + h * 0.02), (x - w * 0.5, top - h * 0.1)])
    draw_poly(c, cup, fill=True)
    draw_poly(c, [(x, top + h * 0.02), (x, top - h * 0.36)], close=False)
    c.restoreState()


def draw_grass(c, x0, x1, y, h, lw=0.8, ink=None, seed=3, density=0.33):
    ink = ink or HexColor("#4B4D60")
    rnd = random.Random(seed)
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setLineCap(1)
    x = x0
    while x < x1:
        hh = h * (0.5 + 0.5 * rnd.random())
        lean = (rnd.random() - 0.5) * hh * 0.6
        p = c.beginPath()
        p.moveTo(x - 1.4, y)
        p.curveTo(x, y + hh * 0.5, x + lean * 0.4, y + hh * 0.8, x + lean, y + hh)
        p.curveTo(x + lean * 0.5 + 1, y + hh * 0.7, x + 1.5, y + hh * 0.4, x + 1.8, y)
        c.drawPath(p, stroke=1, fill=0)
        x += rnd.uniform(4, 9) / density * 0.33
    c.restoreState()


def dashed_path(c, pts, lw=0.8, ink=None, dash=(2, 3)):
    ink = ink or HexColor("#4B4D60")
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(lw)
    c.setDash(*dash)
    c.setLineCap(1)
    draw_poly(c, pts, close=False)
    c.restoreState()
