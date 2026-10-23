"""Top-down engine bay and trunk layout guides for the Cutlass, Charger and Cruze.

Run: python3 personal/cars/layouts/make_layouts.py
Writes six 2400x1700 PNGs next to this script. Everything is drawn at 2x and
downsampled for clean edges. Coordinates below are in final (2400x1700) pixels.
Parts come from personal/cars/parts-lists.md (10/21/2026).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
S = 2
W, H = 2400, 1700
FD = "/usr/share/fonts/truetype/dejavu/"
_fc = {}


def font(sz, bold=False):
    k = (sz, bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), int(sz * S))
    return _fc[k]


BG = (10, 16, 25)
GRID = (17, 28, 42)
PANEL = (16, 24, 36)
PANEL_EDGE = (46, 62, 82)
TXT = (236, 240, 245)
SUB = (150, 164, 182)

# Line types: name -> (color, style, key label)
LINES = {
    "exhaust": ((255, 92, 40), "pipe", "Exhaust, hot side"),
    "charge": ((44, 128, 255), "pipe", "Charge air, cold side"),
    "intake": ((140, 210, 255), "pipe", "Intake air"),
    "coolant": ((60, 200, 110), "pipe", "Coolant hoses"),
    "oil": ((255, 178, 30), "pipe", "Oil feed / drain"),
    "fuel": ((182, 110, 255), "pipe", "Fuel lines"),
    "wire": ((245, 245, 245), "wire", "Main wiring / power"),
    "air": ((170, 178, 188), "braid", "Air ride lines"),
    "ac": ((255, 130, 200), "pipe", "A/C lines"),
    "vent": ((255, 178, 30), "thin", "Crankcase vent (PCV)"),
    "ic": ((40, 210, 200), "pipe", "Intercooler coolant loop"),
}


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def lighten(c, t):
    return mix(c, (255, 255, 255), t)


def darken(c, t):
    return mix(c, (0, 0, 0), t)


def spline(pts, n=14):
    """Catmull-Rom through the points."""
    if len(pts) < 3:
        return list(pts)
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def at(pts, f):
    """Point and unit tangent at fraction f along a polyline."""
    L = plen(pts) * f
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if d == 0:
            continue
        if L <= d or i == len(pts) - 2:
            t = min(1, L / d)
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            return (x, y), ((pts[i + 1][0] - pts[i][0]) / d, (pts[i + 1][1] - pts[i][1]) / d)
        L -= d
    return pts[-1], (1, 0)


def dashes(pts, on, off):
    """Split a polyline into dash pieces."""
    out, cur, pos, draw_on = [], [pts[0]], 0.0, True
    seg_left = on
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = math.dist(a, b)
        t0 = 0.0
        while d - t0 > 1e-6:
            step = min(seg_left, d - t0)
            t1 = t0 + step
            p = (a[0] + (b[0] - a[0]) * t1 / d, a[1] + (b[1] - a[1]) * t1 / d)
            if draw_on:
                cur.append(p)
            seg_left -= step
            t0 = t1
            if seg_left <= 1e-6:
                if draw_on and len(cur) > 1:
                    out.append(cur)
                draw_on = not draw_on
                seg_left = on if draw_on else off
                cur = [p]
    if draw_on and len(cur) > 1:
        out.append(cur)
    return out


class Cv:
    def __init__(self, car):
        self.car = car
        self.im = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.im)
        self.callouts = []
        self.used = []

    # ---------- primitives (design coordinates) ----------
    def P(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=2, r=0):
        b = [x0 * S, y0 * S, x1 * S, y1 * S]
        if r:
            self.d.rounded_rectangle(b, radius=r * S, fill=fill, outline=outline, width=int(w * S))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=int(w * S))

    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, w=2):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=outline, width=int(w * S))

    def poly(self, pts, fill=None, outline=None, w=2):
        self.d.polygon(self.P(pts), fill=fill)
        if outline:
            self.line(list(pts) + [pts[0]], outline, w)

    def line(self, pts, color, w=2):
        if len(pts) < 2:
            return
        self.d.line(self.P(pts), fill=color, width=max(1, int(w * S)), joint="curve")
        if w >= 4:
            for p in (pts[0], pts[-1]):
                self.ell(p[0], p[1], w / 2 - 0.3, fill=color)

    def text(self, x, y, s, sz=26, bold=False, fill=TXT, anchor="la"):
        self.d.text((x * S, y * S), s, font=font(sz, bold), fill=fill, anchor=anchor)

    def tlen(self, s, sz, bold=False):
        return self.d.textlength(s, font=font(sz, bold)) / S

    def grad(self, kind, geom, c1, c2, vertical=True, outline=None, w=2, r=0):
        if kind == "rect":
            x0, y0, x1, y1 = geom
            bb = (x0, y0, x1, y1)
        elif kind == "ell":
            cx, cy, rx, ry = geom
            bb = (cx - rx, cy - ry, cx + rx, cy + ry)
        else:
            xs = [p[0] for p in geom]
            ys = [p[1] for p in geom]
            bb = (min(xs), min(ys), max(xs), max(ys))
        X0, Y0 = int(bb[0] * S) - 2, int(bb[1] * S) - 2
        X1, Y1 = int(bb[2] * S) + 3, int(bb[3] * S) + 3
        mw, mh = max(1, X1 - X0), max(1, Y1 - Y0)
        m = Image.new("L", (mw, mh), 0)
        md = ImageDraw.Draw(m)
        if kind == "rect":
            b = [x0 * S - X0, y0 * S - Y0, x1 * S - X0, y1 * S - Y0]
            if r:
                md.rounded_rectangle(b, radius=r * S, fill=255)
            else:
                md.rectangle(b, fill=255)
        elif kind == "ell":
            md.ellipse([(cx - rx) * S - X0, (cy - ry) * S - Y0, (cx + rx) * S - X0, (cy + ry) * S - Y0], fill=255)
        else:
            md.polygon([(x * S - X0, y * S - Y0) for x, y in geom], fill=255)
        g = Image.linear_gradient("L")
        if not vertical:
            g = g.transpose(Image.Transpose.ROTATE_90).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        g = g.resize((mw, mh))
        tile = Image.composite(Image.new("RGB", (mw, mh), c2), Image.new("RGB", (mw, mh), c1), g)
        self.im.paste(tile, (X0, Y0), m)
        if outline:
            if kind == "rect":
                self.rect(x0, y0, x1, y1, outline=outline, w=w, r=r)
            elif kind == "ell":
                self.ell(cx, cy, rx, ry, outline=outline, w=w)
            else:
                self.line(list(geom) + [geom[0]], outline, w)

    # ---------- routing ----------
    def use(self, kind):
        if kind not in self.used:
            self.used.append(kind)

    def arrowhead(self, p, t, size, fill, edge):
        x, y = p
        tx, ty = t
        nx, ny = -ty, tx
        a = (x + tx * size * 0.7, y + ty * size * 0.7)
        b = (x - tx * size * 0.5 + nx * size * 0.55, y - ty * size * 0.5 + ny * size * 0.55)
        c = (x - tx * size * 0.5 - nx * size * 0.55, y - ty * size * 0.5 - ny * size * 0.55)
        self.poly([a, b, c], fill=fill)
        self.line([a, b, c, a], edge, 1.5)

    def route(self, kind, pts, w=None, arrows=(0.5,), smooth=True, hidden=False):
        """Draw a pipe, wire or air line along pts with flow arrows."""
        self.use(kind)
        color, style, _ = LINES[kind]
        p = spline(pts) if (smooth and len(pts) > 2) else list(pts)
        if style == "pipe":
            w = w or 14
            pieces = dashes(p, 26, 14) if hidden else [p]
            for q in pieces:
                self.line(q, darken(color, 0.55), w + 6)
            for q in pieces:
                self.line(q, color, w)
                self.line(q, lighten(color, 0.5), max(2, w * 0.22))
            for f in arrows:
                pt, t = at(p, f)
                self.arrowhead(pt, t, w * 1.25 + 10, lighten(color, 0.75), darken(color, 0.6))
        elif style == "thin":
            w = w or 5
            for q in dashes(p, 12, 7):
                self.line(q, darken(color, 0.5), w + 3)
                self.line(q, color, w)
            for f in arrows:
                pt, t = at(p, f)
                self.arrowhead(pt, t, 16, lighten(color, 0.6), darken(color, 0.6))
        elif style == "wire":
            w = w or 5
            for q in dashes(p, 16, 10):
                self.line(q, (20, 20, 24), w + 4)
                self.line(q, color, w)
            for f in arrows:
                pt, t = at(p, f)
                self.arrowhead(pt, t, 18, (255, 255, 255), (30, 30, 30))
        elif style == "braid":
            w = w or 9
            self.line(p, (40, 44, 50), w + 5)
            self.line(p, color, w)
            L = plen(p)
            s = 0
            while s < L:
                pt, t = at(p, s / L)
                nx, ny = -t[1], t[0]
                hw = w / 2
                a = (pt[0] + nx * hw - t[0] * 3, pt[1] + ny * hw - t[1] * 3)
                b = (pt[0] - nx * hw + t[0] * 3, pt[1] - ny * hw + t[1] * 3)
                self.line([a, b], (90, 96, 104), 1.6)
                s += 7
            for f in arrows:
                pt, t = at(p, f)
                self.arrowhead(pt, t, 20, (230, 232, 236), (40, 44, 50))
        return p

    # ---------- callouts ----------
    def call(self, n, m, anchor):
        self.callouts.append((n, m, anchor))

    def draw_callouts(self):
        mc = self.car["marker"]
        mt = self.car["marker_text"]
        for n, (mx, my), anchors in self.callouts:
            if anchors and not isinstance(anchors[0], (tuple, list)):
                anchors = [anchors]
            for ax, ay in anchors:
                dx, dy = ax - mx, ay - my
                d = math.hypot(dx, dy) or 1
                sx, sy = mx + dx / d * 22, my + dy / d * 22
                self.line([(sx, sy), (ax, ay)], (10, 12, 16), 6)
                self.line([(sx, sy), (ax, ay)], (235, 240, 246), 2.5)
                self.ell(ax, ay, 6, fill=(235, 240, 246), outline=(10, 12, 16), w=2)
        for n, (mx, my), anchors in self.callouts:
            self.ell(mx, my, 23, fill=(10, 12, 16))
            self.ell(mx, my, 21, fill=mc, outline=(255, 255, 255), w=2.5)
            self.text(mx, my + 1, str(n), 24 if n < 10 else 21, True, mt, "mm")

    # ---------- page furniture ----------
    def grid(self):
        for x in range(40, 1500, 40):
            self.line([(x, 150), (x, 1440)], GRID, 1)
        for y in range(150, 1445, 40):
            self.line([(40, y), (1490, y)], GRID, 1)
        self.rect(40, 150, 1490, 1440, outline=PANEL_EDGE, w=2, r=10)

    def header(self, title, sub):
        acc = self.car["accent"]
        self.grad("ell", (78, 78, 26, 26), lighten(acc, 0.35), darken(acc, 0.25), outline=(255, 255, 255), w=2)
        if "accent2" in self.car:
            self.ell(78, 78, 10, fill=self.car["accent2"])
        self.text(122, 40, title, 52, True)
        self.text(124, 104, sub, 27, False, SUB)
        self.line([(40, 140), (2360, 140)], acc, 3)

    def footer(self):
        self.text(40, 1652, "Layout guide, not to scale.", 28, True, SUB)
        self.text(470, 1655, "Top-down view. Driver side on the left. Numbers match the parts key.", 26, False, SUB)

    def key(self):
        kinds = self.used
        self.rect(40, 1455, 1490, 1625, fill=PANEL, outline=PANEL_EDGE, w=2, r=12)
        self.text(60, 1468, "LINE KEY", 24, True, SUB)
        cols = 3
        cw = (1450 - 40) / cols
        for i, k in enumerate(kinds):
            r, c = divmod(i, cols)
            x = 60 + c * cw
            y = 1514 + r * 42
            color, style, label = LINES[k]
            pts = [(x, y), (x + 70, y)]
            if style == "pipe":
                self.line(pts, darken(color, 0.55), 16)
                self.line(pts, color, 11)
                self.line(pts, lighten(color, 0.5), 3)
            elif style == "thin":
                for q in dashes(pts, 12, 7):
                    self.line(q, color, 5)
            elif style == "wire":
                for q in dashes(pts, 16, 10):
                    self.line(q, color, 5)
            else:
                self.line(pts, (40, 44, 50), 13)
                self.line(pts, color, 9)
                for j in range(0, 70, 7):
                    self.line([(x + j - 3, y + 4), (x + j + 3, y - 4)], (90, 96, 104), 1.6)
            self.text(x + 86, y, label, 26, False, TXT, "lm")

    def legend(self, items):
        x0, y0, x1, y1 = 1515, 150, 2360, 1625
        self.rect(x0, y0, x1, y1, fill=PANEL, outline=PANEL_EDGE, w=2, r=12)
        self.text(x0 + 24, y0 + 18, "PARTS KEY", 28, True, self.car["accent_text"])
        self.text(x1 - 24, y0 + 22, "brand / chosen part", 22, False, SUB, "ra")
        sz = 27
        while True:
            lay = self._legend_layout(items, x0, x1, sz)
            total = sum(h for _, h in lay) + 10 * (len(items) - 1)
            if total <= (y1 - y0 - 80) or sz <= 26:
                break
            sz -= 0.5
        gap = min(22, max(8, ((y1 - y0 - 80) - sum(h for _, h in lay)) / max(1, len(items) - 1)))
        y = y0 + 72
        for (n, lines), (_, h) in zip(((it[0], l) for it, (l, _) in zip(items, lay)), lay):
            self.ell(x0 + 44, y + sz * 0.62, 19, fill=self.car["marker"], outline=(255, 255, 255), w=2)
            self.text(x0 + 44, y + sz * 0.62 + 1, str(n), 21 if n < 10 else 18, True, self.car["marker_text"], "mm")
            ly = y
            for ln in lines:
                lx = x0 + 78
                for word, bold in ln:
                    self.text(lx, ly, word, sz, bold, TXT if bold else (200, 208, 218))
                    lx += self.tlen(word, sz, bold)
                ly += sz * 1.28
            y += h + gap
        assert y - gap <= y1, "legend overflow"

    def _legend_layout(self, items, x0, x1, sz):
        maxw = x1 - x0 - 78 - 22
        out = []
        for n, name, detail in items:
            toks = [(w + " ", True) for w in (name + ":").split(" ")] + [(w + " ", False) for w in detail.split(" ")]
            lines, cur, cw = [], [], 0
            for wd, b in toks:
                tw = self.tlen(wd, sz, b)
                if cur and cw + tw - self.tlen(" ", sz, b) > maxw:
                    lines.append(cur)
                    cur, cw = [], 0
                cur.append((wd, b))
                cw += tw
            if cur:
                lines.append(cur)
            out.append((lines, len(lines) * sz * 1.28))
        return out

    def save(self, name):
        self.draw_callouts()
        im = self.im.resize((W, H), Image.LANCZOS)
        im.save(os.path.join(OUT, name), optimize=True)
        print("wrote", name)


# ================= components =================
ALU = ((112, 122, 134), (214, 222, 230))
ALU_D = ((80, 88, 98), (170, 178, 188))
BLACK = ((22, 24, 28), (70, 74, 82))
IRON = ((48, 54, 62), (96, 104, 114))


def snail(cv, cx, cy, R, phi, cols, mirror=False, L=None):
    """Volute housing seen along its axis. phi = direction the tangential port points (radians,
    screen coords). Returns (center, port_end)."""
    L = L if L is not None else R * 0.9
    the = phi - math.pi / 2
    pts = []
    N = 60
    for i in range(N + 1):
        t = the - 2 * math.pi + 2 * math.pi * i / N
        r = R * (0.68 + 0.32 * i / N)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    tx, ty = math.cos(phi), math.sin(phi)
    po, pi_ = pts[-1], pts[0]
    pts += [(po[0] + tx * L, po[1] + ty * L), (pi_[0] + tx * L, pi_[1] + ty * L)]
    if mirror:
        pts = [(2 * cx - x, y) for x, y in pts]
        tx = -tx
        po = (2 * cx - po[0], po[1])
        pi_ = (2 * cx - pi_[0], pi_[1])
    cv.grad("poly", pts, cols[0], cols[1], vertical=False, outline=darken(cols[0], 0.5), w=2)
    # flange at port end
    e1 = (po[0] + tx * L, po[1] + ty * L)
    e2 = (pi_[0] + tx * L, pi_[1] + ty * L)
    nx, ny = tx * 7, ty * 7
    cv.poly([(e1[0] - nx, e1[1] - ny), (e2[0] - nx, e2[1] - ny), (e2[0] + nx * 0.3, e2[1] + ny * 0.3), (e1[0] + nx * 0.3, e1[1] + ny * 0.3)], fill=darken(cols[1], 0.25))
    port = ((e1[0] + e2[0]) / 2, (e1[1] + e2[1]) / 2)
    return port


def wheel_face(cv, cx, cy, r, col, blades=10, hub=(40, 44, 50)):
    cv.grad("ell", (cx, cy, r, r), darken(col, 0.35), lighten(col, 0.2), outline=darken(col, 0.6), w=2)
    for i in range(blades):
        a = 2 * math.pi * i / blades
        a2 = a + 0.5
        cv.line([(cx + r * 0.25 * math.cos(a), cy + r * 0.25 * math.sin(a)),
                 (cx + r * 0.6 * math.cos(a + 0.25), cy + r * 0.6 * math.sin(a + 0.25)),
                 (cx + r * 0.92 * math.cos(a2), cy + r * 0.92 * math.sin(a2))], darken(col, 0.5), 2)
    cv.ell(cx, cy, r * 0.22, fill=hub, outline=lighten(hub, 0.4), w=1.5)


def turbo(cv, cx, cy, comp_phi, turb_phi, mirror=False, R=46):
    """Compressor snail at (cx,cy); turbine snail offset toward the engine side."""
    dx = 92 if not mirror else -92
    tx, ty = cx + dx, cy + 34
    # center section
    cv.grad("poly", [(cx, cy - 16), (tx, ty - 16), (tx, ty + 16), (cx, cy + 16)], (60, 64, 72), (130, 136, 146), outline=(20, 22, 26))
    tp = snail(cv, tx, ty, R * 0.86, turb_phi, ((120, 44, 22), (214, 120, 60)), mirror)
    wheel_face(cv, tx, ty, R * 0.86 * 0.55, (150, 140, 130), 9)
    cp = snail(cv, cx, cy, R, comp_phi, ALU, mirror)
    cv.ell(cx, cy, R * 0.62, fill=(60, 66, 74), outline=(20, 22, 26), w=2)
    wheel_face(cv, cx, cy, R * 0.52, (190, 196, 204), 11)
    return {"c_in": (cx, cy), "c_out": cp, "t_in": tp, "t_out": (tx, ty), "chra": ((cx + tx) / 2, (cy + ty) / 2)}


def finned(cv, x0, y0, x1, y1, core, tank, vertical_fins=True, step=7, tanks="lr", tw=26):
    """Heat exchanger: tanks on the ends, finned core."""
    if tanks == "lr":
        cv.grad("rect", (x0, y0, x0 + tw, y1), tank[0], tank[1], vertical=False, outline=(20, 22, 26), r=6)
        cv.grad("rect", (x1 - tw, y0, x1, y1), tank[1], tank[0], vertical=False, outline=(20, 22, 26), r=6)
        cx0, cx1, cy0, cy1 = x0 + tw, x1 - tw, y0 + 3, y1 - 3
    else:
        cv.grad("rect", (x0, y0, x1, y0 + tw), tank[0], tank[1], outline=(20, 22, 26), r=6)
        cv.grad("rect", (x0, y1 - tw, x1, y1), tank[1], tank[0], outline=(20, 22, 26), r=6)
        cx0, cx1, cy0, cy1 = x0 + 3, x1 - 3, y0 + tw, y1 - tw
    cv.grad("rect", (cx0, cy0, cx1, cy1), core[0], core[1], outline=(20, 22, 26), w=1.5)
    if vertical_fins:
        x = cx0 + step
        while x < cx1 - 2:
            cv.line([(x, cy0 + 2), (x, cy1 - 2)], darken(core[0], 0.35), 1.6)
            x += step
    else:
        y = cy0 + step
        while y < cy1 - 2:
            cv.line([(cx0 + 2, y), (cx1 - 2, y)], darken(core[0], 0.35), 1.6)
            y += step


def fan(cv, cx, cy, r):
    cv.ell(cx, cy, r + 6, fill=(20, 22, 26), outline=(70, 76, 86), w=2)
    for i in range(7):
        a = 2 * math.pi * i / 7
        pts = [(cx + r * 0.2 * math.cos(a), cy + r * 0.2 * math.sin(a)),
               (cx + r * 0.95 * math.cos(a + 0.15), cy + r * 0.95 * math.sin(a + 0.15)),
               (cx + r * 0.95 * math.cos(a + 0.65), cy + r * 0.95 * math.sin(a + 0.65)),
               (cx + r * 0.25 * math.cos(a + 0.7), cy + r * 0.25 * math.sin(a + 0.7))]
        cv.grad("poly", pts, (60, 66, 76), (120, 128, 140), outline=(20, 22, 26), w=1)
    cv.grad("ell", (cx, cy, r * 0.22, r * 0.22), (90, 96, 106), (30, 34, 40), outline=(10, 10, 12))


def cyl_cap(cv, cx, cy, r, col=(230, 200, 60)):
    cv.ell(cx, cy, r, fill=darken(col, 0.4), outline=(10, 10, 12), w=1.5)
    cv.ell(cx, cy, r * 0.7, fill=col)


def battery(cv, x0, y0, x1, y1, label="AGM"):
    cv.grad("rect", (x0, y0, x1, y1), (24, 26, 30), (64, 68, 76), outline=(130, 136, 146), w=2, r=8)
    cv.rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10, outline=(90, 96, 104), w=1.5, r=6)
    pr = 13
    cv.ell(x0 + 30, y0 + 30, pr, fill=(200, 40, 40), outline=(255, 210, 210), w=2)
    cv.text(x0 + 30, y0 + 30, "+", 22, True, (255, 255, 255), "mm")
    cv.ell(x1 - 30, y0 + 30, pr, fill=(30, 30, 34), outline=(180, 180, 190), w=2)
    cv.text(x1 - 30, y0 + 29, "-", 24, True, (255, 255, 255), "mm")
    cv.text((x0 + x1) / 2, (y0 + y1) / 2 + 12, label, 22, True, (150, 156, 166), "mm")
    return (x0 + 30, y0 + 30), (x1 - 30, y0 + 30)


def reservoir(cv, x0, y0, x1, y1, fluid, cap=(30, 30, 34)):
    cv.grad("rect", (x0, y0, x1, y1), (200, 204, 196), (238, 238, 230), outline=(80, 84, 90), w=2, r=12)
    cv.rect(x0 + 6, (y0 + y1) / 2, x1 - 6, y1 - 6, fill=mix(fluid, (238, 238, 230), 0.45), r=8)
    cx, cy = (x0 + x1) / 2, y0 + 18
    cv.ell(cx, cy, 13, fill=cap, outline=(120, 120, 130), w=2)
    for i in range(8):
        a = i * math.pi / 4
        cv.line([(cx + 8 * math.cos(a), cy + 8 * math.sin(a)), (cx + 12 * math.cos(a), cy + 12 * math.sin(a))], (120, 120, 130), 1.5)


def booster_master(cv, cx, cy, r, mc_dir=-1, mirror=False):
    cv.grad("ell", (cx, cy, r, r), (20, 22, 26), (80, 84, 92), outline=(140, 146, 156), w=2)
    cv.ell(cx, cy, r * 0.75, outline=(60, 64, 72), w=2)
    cv.ell(cx, cy, r * 0.45, outline=(60, 64, 72), w=2)
    # master cylinder pointing forward
    mx0, mx1 = cx - 16, cx + 16
    my1 = cy - r * 0.6
    my0 = my1 - 90
    cv.grad("rect", (mx0, my0, mx1, my1), ALU[0], ALU[1], vertical=False, outline=(20, 22, 26), r=8)
    cv.grad("rect", (mx0 - 14, my0 + 12, mx1 + 14, my0 + 66), (200, 200, 196), (240, 240, 232), outline=(80, 84, 90), r=8)
    cyl_cap(cv, cx, my0 + 26, 9, (40, 40, 44))
    cyl_cap(cv, cx, my0 + 52, 9, (40, 40, 44))
    return (cx, my0)


def cone_filter(cv, cx, cy, length, rad, ang, col=(200, 40, 40)):
    """Cone filter: base at (cx,cy) pointing along ang."""
    tx, ty = math.cos(ang), math.sin(ang)
    nx, ny = -ty, tx
    b1 = (cx + nx * rad, cy + ny * rad)
    b2 = (cx - nx * rad, cy - ny * rad)
    e1 = (cx + tx * length + nx * rad * 0.72, cy + ty * length + ny * rad * 0.72)
    e2 = (cx + tx * length - nx * rad * 0.72, cy + ty * length - ny * rad * 0.72)
    cv.grad("poly", [b1, e1, e2, b2], darken(col, 0.3), lighten(col, 0.15), outline=(20, 22, 26))
    k = 1
    while k * 7 < length - 8:
        s = k * 7
        f = 1 - 0.28 * s / length
        cv.line([(cx + tx * s + nx * rad * f, cy + ty * s + ny * rad * f), (cx + tx * s - nx * rad * f, cy + ty * s - ny * rad * f)], darken(col, 0.55), 1.4)
        k += 1
    cv.line([e1, e2], (30, 30, 34), 7)
    cv.line([b1, b2], (160, 166, 176), 6)


def catch_can(cv, cx, cy, r=24):
    cv.grad("ell", (cx, cy, r, r), ALU[0], ALU[1], outline=(20, 22, 26), w=2)
    for i in range(16):
        a = 2 * math.pi * i / 16
        cv.line([(cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a)), (cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a))], (90, 96, 104), 1.5)
    cv.ell(cx, cy, r * 0.55, fill=(60, 66, 74), outline=(20, 22, 26), w=1.5)
    cv.ell(cx - r * 0.25, cy, 5, fill=(255, 178, 30))
    cv.ell(cx + r * 0.25, cy, 5, fill=(40, 120, 255))


def box_module(cv, x0, y0, x1, y1, base=(26, 28, 34), led=None, conn=True, fins=False, label=None, label_col=(160, 166, 176)):
    cv.grad("rect", (x0, y0, x1, y1), base, lighten(base, 0.18), outline=(130, 136, 146), w=2, r=7)
    if fins:
        y = y0 + 10
        while y < y1 - 8:
            cv.line([(x0 + 10, y), (x1 - 10, y)], lighten(base, 0.3), 2.2)
            cv.line([(x0 + 10, y + 2), (x1 - 10, y + 2)], darken(base, 0.4), 1.2)
            y += 9
    if conn:
        cv.rect(x0 + 8, y1 - 16, x0 + 8 + (x1 - x0) * 0.4, y1 - 5, fill=(14, 14, 16), outline=(90, 96, 104), w=1)
    if led:
        cv.ell(x1 - 14, y0 + 13, 6, fill=led, outline=lighten(led, 0.5), w=1)
    if label:
        cv.text((x0 + x1) / 2, (y0 + y1) / 2, label, 20, True, label_col, "mm")


def pulley(cv, cx, cy, r, col=ALU):
    cv.grad("ell", (cx, cy, r, r), col[0], col[1], outline=(20, 22, 26), w=2)
    cv.ell(cx, cy, r * 0.75, outline=darken(col[0], 0.3), w=1.5)
    cv.ell(cx, cy, r * 0.25, fill=(40, 44, 50))


def belt(cv, centers):
    """Belt around pulleys (convex hull of offset points)."""
    pts = []
    for cx, cy, r in centers:
        for i in range(36):
            a = 2 * math.pi * i / 36
            pts.append((cx + (r + 3) * math.cos(a), cy + (r + 3) * math.sin(a)))
    hull = convex_hull(pts)
    cv.line(hull + [hull[0]], (16, 16, 18), 6)
    cv.line(hull + [hull[0]], (70, 72, 78), 2)


def convex_hull(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def wastegate(cv, cx, cy, r=20):
    cv.grad("ell", (cx, cy, r + 6, r + 6), (90, 40, 24), (190, 110, 60), outline=(20, 22, 26), w=2)
    cv.grad("ell", (cx, cy, r, r), (150, 156, 166), (220, 226, 232), outline=(40, 44, 50), w=2)
    cv.ell(cx, cy, r * 0.45, fill=(220, 40, 40), outline=(60, 10, 10), w=1.5)
    for i in range(6):
        a = i * math.pi / 3
        cv.ell(cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a), 2.5, fill=(50, 54, 60))


def bov(cv, cx, cy, r=17):
    cv.grad("ell", (cx, cy, r, r), (50, 54, 60), (200, 206, 214), outline=(20, 22, 26), w=2)
    cv.ell(cx, cy, r * 0.5, fill=(40, 110, 230), outline=(10, 30, 70), w=1.5)


def tire_hidden(cv, x0, y0, x1, y1):
    for q in dashes([(x0 + 12, y0), (x1 - 12, y0), (x1, y0 + 12), (x1, y1 - 12), (x1 - 12, y1), (x0 + 12, y1), (x0, y1 - 12), (x0, y0 + 12), (x0 + 12, y0)], 12, 8):
        cv.line(q, (120, 128, 140), 2.5)


def v8(cv, cx, y0, y1, half=190, hemi=False, cover=((30, 32, 38), (84, 90, 100)), coil_col=(20, 20, 22)):
    """Longitudinal V8, front at y0. Returns port positions and key points."""
    x0, x1 = cx - half, cx + half
    cv.grad("rect", (x0, y0 + 20, x1, y1), IRON[0], IRON[1], vertical=False, outline=(20, 22, 26), w=2, r=16)
    bw = 92 if not hemi else 100
    cyl_y = [y0 + 85 + i * (y1 - y0 - 150) / 3 for i in range(4)]
    out = {"ports_l": [(x0, y) for y in cyl_y], "ports_r": [(x1, y + 22) for y in cyl_y]}
    # valve covers
    for side in (-1, 1):
        vx0 = x0 + 10 if side < 0 else x1 - 10 - bw
        vx1 = vx0 + bw
        cv.grad("rect", (vx0, y0 + 30, vx1, y1 - 14), cover[0], cover[1], vertical=False, outline=(150, 156, 166), w=2, r=20)
        cv.rect(vx0 + 10, y0 + 44, vx1 - 10, y1 - 28, outline=lighten(cover[0], 0.12), w=1.5, r=14)
        for yy in (y0 + 52, y1 - 34):
            for xx in (vx0 + 16, vx1 - 16):
                cv.ell(xx, yy, 3.5, fill=(170, 176, 186))
        for i, y in enumerate(cyl_y):
            yy = y + (0 if side < 0 else 22)
            if hemi:
                ccx = (vx0 + vx1) / 2
                cv.grad("rect", (ccx - 18, yy - 22, ccx + 18, yy + 22), coil_col, lighten(coil_col, 0.25), outline=(120, 120, 130), w=1.5, r=6)
                cv.rect(ccx - 8, yy - 30, ccx + 8, yy - 22, fill=(60, 60, 66))
            else:
                ox = vx0 + 8 if side < 0 else vx1 - 44
                cv.grad("rect", (ox, yy - 20, ox + 36, yy + 20), coil_col, lighten(coil_col, 0.25), outline=(120, 120, 130), w=1.5, r=4)
                cv.rect(ox + 10, yy - 26, ox + 26, yy - 20, fill=(60, 60, 66))
        out["cover_l" if side < 0 else "cover_r"] = (vx0, vx1)
    # intake: runners then plenum
    px0, px1 = cx - 72, cx + 72
    for i, y in enumerate(cyl_y):
        for side in (-1, 1):
            yy = y + (0 if side < 0 else 22)
            rx0 = (x0 + bw + 4) if side < 0 else px1 - 6
            rx1 = px0 + 6 if side < 0 else (x1 - bw - 4)
            cv.grad("rect", (rx0, yy - 16, rx1, yy + 16), (70, 76, 86), (150, 156, 166), outline=(20, 22, 26), w=1.5, r=8)
    cv.grad("rect", (px0, y0 + 40, px1, y1 - 30), (96, 104, 116), (190, 198, 208), vertical=False, outline=(20, 22, 26), w=2, r=30)
    cv.rect(px0 + 16, y0 + 70, px1 - 16, y1 - 60, outline=(110, 118, 130), w=1.5, r=22)
    out["plenum"] = (px0, px1)
    out["cyl_y"] = cyl_y
    out["x"] = (x0, x1)
    return out


def throttle_body(cv, cx, cy, r=30):
    cv.grad("ell", (cx, cy, r + 8, r + 8), (60, 66, 76), (170, 176, 186), outline=(20, 22, 26), w=2)
    cv.ell(cx, cy, r, fill=(18, 20, 24), outline=(120, 126, 136), w=2)
    cv.line([(cx - r * 0.9, cy + r * 0.3), (cx + r * 0.9, cy - r * 0.3)], (190, 196, 206), 3)
    cv.ell(cx, cy, 4, fill=(190, 196, 206))


def wheel_well_tire(cv, x0, y0, x1, y1):
    tire_hidden(cv, x0, y0, x1, y1)


# ================= bodies =================
def bay_body(cv, b):
    """b: dict with geometry. Front at top."""
    acc = cv.car["body"]
    L, R = b["L"], b["R"]
    top, cowl = b["top"], b["cowl"]
    cxm = (L + R) / 2
    # cabin / windshield
    cv.grad("poly", [(L + 30, cowl + 40), (R - 30, cowl + 40), (R - 10, 1438), (L + 10, 1438)], (20, 40, 60), (40, 70, 96), outline=(90, 110, 130))
    cv.text(cxm, 1408, "CABIN / WINDSHIELD", 24, True, (150, 175, 200), "mm")
    # outer body
    cv.grad("rect", (L, top, R, cowl + 40), acc[0], acc[1], vertical=False, outline=lighten(acc[1], 0.3), w=2.5, r=70)
    # bumper and nose
    cv.grad("rect", (L + 20, top - 18, R - 20, top + 26), darken(acc[0], 0.2), acc[1], outline=(20, 22, 26), w=2, r=20)
    # inner fender / apron
    ox0, oy0, ox1, oy1 = b["open"]
    cv.rect(ox0 - 34, oy0 - 18, ox1 + 34, oy1 + 30, fill=darken(acc[0], 0.55), r=26)
    # wheelhouse bulges
    for side in (-1, 1):
        wx = ox0 if side < 0 else ox1
        wy0, wy1 = b["wheel"]
        bulge = [(wx, wy0 - 30)]
        for i in range(21):
            a = math.pi * i / 20
            bulge.append((wx - side * (b["bulge"] * math.sin(a)), (wy0 + wy1) / 2 - (wy1 - wy0) / 2 * math.cos(a)))
        bulge.append((wx, wy1 + 30))
        b.setdefault("bulges", []).append(bulge)
    # opening floor
    cv.grad("rect", (ox0, oy0, ox1, oy1), (18, 26, 38), (26, 36, 52), outline=(70, 80, 96), w=2, r=18)
    for bulge in b["bulges"]:
        cv.poly(bulge, fill=darken(acc[0], 0.5))
        cv.line(bulge, (70, 80, 96), 2)
    # core support
    cv.grad("rect", (ox0 - 10, oy0 - 6, ox1 + 10, oy0 + 12), (40, 44, 52), (80, 86, 96), outline=(20, 22, 26), r=4)
    # firewall
    fw = b["firewall"]
    cv.grad("rect", (ox0, fw, ox1, oy1), darken(acc[0], 0.45), darken(acc[1], 0.35), outline=(70, 80, 96), w=2, r=8)
    tun = [(cxm - 80, oy1), (cxm - 60, fw - 30), (cxm + 60, fw - 30), (cxm + 80, oy1)]
    cv.poly(tun, fill=darken(acc[0], 0.62))
    cv.line(tun, (70, 80, 96), 2)
    cv.text(cxm, fw + (oy1 - fw) / 2 + 2, "FIREWALL", 22, True, lighten(acc[0], 0.25), "mm")
    # tires (hidden under fenders)
    wy0, wy1 = b["wheel"]
    tire_hidden(cv, L + 6, wy0, L + 6 + b["tire_w"], wy1)
    tire_hidden(cv, R - 6 - b["tire_w"], wy0, R - 6, wy1)
    # orientation labels
    cv.text(cxm, 160, "FRONT", 26, True, cv.car["accent_text"], "mm")
    cv.poly([(cxm - 66, 150), (cxm - 76, 168), (cxm - 56, 168)], fill=cv.car["accent_text"])
    cv.poly([(cxm + 66, 150), (cxm + 76, 168), (cxm + 56, 168)], fill=cv.car["accent_text"])
    cv.text(L - 8, 1290, "DRIVER", 24, True, SUB, "ra")
    cv.text(R + 8, 1290, "PASS.", 24, True, SUB, "la")


def trunk_body(cv, b):
    """Cabin side at top, rear bumper at bottom."""
    acc = cv.car["body"]
    L, R = b["L"], b["R"]
    cxm = (L + R) / 2
    # rear glass / package tray area at top
    cv.grad("poly", [(L + 20, 160), (R - 20, 160), (R - 40, b["seat"] - 24), (L + 40, b["seat"] - 24)], (20, 40, 60), (40, 70, 96), outline=(90, 110, 130))
    cv.text(cxm, 192, "CABIN (REAR SEAT)", 24, True, (150, 175, 200), "mm")
    cv.grad("rect", (L, b["seat"] - 30, R, b["bottom"]), acc[0], acc[1], vertical=False, outline=lighten(acc[1], 0.3), w=2.5, r=60)
    ox0, oy0, ox1, oy1 = b["open"]
    floor = b["floor"]
    cv.rect(ox0 - 24, oy0 - 14, ox1 + 24, oy1 + 14, fill=darken(acc[0], 0.55), r=30)
    cv.grad("rect", (ox0, oy0, ox1, oy1), floor[0], floor[1], outline=(70, 70, 80), w=2, r=24)
    # wheel tubs
    ty0, ty1 = b["tubs"]
    for side in (-1, 1):
        wx = ox0 if side < 0 else ox1
        pts = [(wx, ty0)]
        for i in range(21):
            a = math.pi * i / 20
            pts.append((wx - side * b["tub_depth"] * math.sin(a), (ty0 + ty1) / 2 - (ty1 - ty0) / 2 * math.cos(a)))
        pts.append((wx, ty1))
        cv.poly(pts, fill=darken(floor[1], 0.15) if b.get("tub_floor") else darken(acc[0], 0.5))
        cv.line(pts, (90, 90, 100), 2)
    # tires hidden
    tire_hidden(cv, L + 6, ty0 + 10, L + 6 + b["tire_w"], ty1 - 10)
    tire_hidden(cv, R - 6 - b["tire_w"], ty0 + 10, R - 6, ty1 - 10)
    # seat wall band
    cv.grad("rect", (ox0, oy0, ox1, oy0 + 46), darken(floor[0], 0.3), floor[1], outline=(80, 80, 90), w=2, r=12)
    cv.text(cxm, oy0 + 23, "REAR SEAT WALL", 22, True, lighten(floor[1], 0.45), "mm")
    cv.text(L - 8, 1250, "DRIVER", 24, True, SUB, "ra")
    cv.text(R + 8, 1250, "PASS.", 24, True, SUB, "la")
    cv.text(cxm, 1430, "REAR OF CAR", 24, True, cv.car["accent_text"], "mm")


# ================= cars =================
CUTLASS = dict(name="cutlass", accent=hexc("8d9298"), accent_text=hexc("c9ced5"), body=(hexc("4d5258"), hexc("8e949b")),
               marker=hexc("b8bec6"), marker_text=(14, 16, 20), accent2=hexc("7a1f2b"))
CHARGER = dict(name="charger", accent=hexc("efeadf"), accent_text=hexc("d2a86a"), body=(hexc("c9c3b6"), hexc("f6f3ec")),
               marker=hexc("b0874e"), marker_text=(255, 255, 255), accent2=hexc("b0874e"))
CRUZE = dict(name="cruze", accent=hexc("16171a"), accent_text=hexc("e8732a"), body=(hexc("060607"), hexc("34363c")),
             marker=hexc("cc5500"), marker_text=(255, 255, 255), accent2=hexc("cc5500"))


def cutlass_bay():
    cv = Cv(CUTLASS)
    cv.grid()
    cv.header("1979 Cutlass Supreme: engine bay", "6.0 iron LS, forged, twin turbo in the front corners. Dark pewter, smoothed bay, battery in the trunk.")
    b = dict(L=215, R=1315, top=200, cowl=1310, open=(310, 300, 1220, 1290), wheel=(600, 880), bulge=58, firewall=1240, tire_w=86)
    bay_body(cv, b)
    cx = 765
    # headlights, grille, parking lamps in the header panel
    for side in (-1, 1):
        hx = cx + side * 420
        cv.grad("rect", (hx - 62, 228, hx + 62, 276), (190, 210, 230), (250, 252, 255), outline=(40, 44, 50), w=2, r=6)
        cv.rect(hx - 50, 236, hx + 50, 268, outline=(150, 170, 190), w=1.5, r=4)
        px = cx + side * 300
        cv.grad("rect", (px - 34, 236, px + 34, 268), (200, 120, 20), (255, 190, 80), outline=(40, 44, 50), w=2, r=4)
    cv.grad("rect", (cx - 200, 226, cx + 200, 280), (20, 22, 26), (60, 64, 72), outline=(150, 156, 166), w=2, r=6)
    for x in range(cx - 190, cx + 191, 16):
        cv.line([(x, 232), (x, 274)], (110, 116, 126), 2)

    # intercooler, condenser, radiator, fans
    finned(cv, 520, 312, 1010, 362, ((120, 128, 138), (190, 198, 208)), ALU, step=6, tw=30)
    finned(cv, 540, 370, 990, 390, ((90, 70, 86), (150, 120, 140)), ((90, 90, 100), (150, 150, 160)), step=5, tw=14)
    finned(cv, 520, 398, 1010, 450, ((60, 70, 82), (120, 130, 144)), ((40, 44, 50), (90, 96, 106)), step=6, tw=30)
    cv.rect(560, 452, 970, 520, fill=(22, 24, 28), outline=(70, 76, 86), w=2, r=10)
    fan(cv, 660, 486, 30)
    fan(cv, 870, 486, 30)

    # engine
    e = v8(cv, cx, 600, 1150, half=190, cover=(hexc("3b3f45"), hexc("8a9097")))
    # accessory drive (front)
    belt(cv, [(cx, 600, 30), (cx, 548, 30), (622, 565, 30), (912, 565, 36), (cx - 70, 528, 13)])
    pulley(cv, cx, 600, 30)
    pulley(cv, cx, 548, 30)
    cv.grad("rect", (585, 540, 660, 600), (60, 64, 72), (150, 156, 166), vertical=False, outline=(20, 22, 26), r=14)
    pulley(cv, 622, 565, 22)
    cv.grad("rect", (868, 530, 990, 600), (40, 44, 50), (120, 126, 136), vertical=False, outline=(20, 22, 26), r=16)
    pulley(cv, 912, 565, 28, ((60, 64, 72), (150, 156, 166)))
    pulley(cv, cx - 70, 528, 12)
    throttle_body(cv, cx, 642, 28)

    # Holley 302-2 pan outline (under)
    for q in dashes([(cx - 175, 760), (cx + 175, 760), (cx + 175, 1120), (cx - 175, 1120), (cx - 175, 760)], 14, 9):
        cv.line(q, (255, 178, 30), 2.5)

    tp = {}
    for side in (-1, 1):
        mir = side > 0
        X = (lambda x: x) if not mir else (lambda x: 2 * cx - x)
        # header primaries forward to a collector, then hot pipe to the turbine
        ports = e["ports_l"] if not mir else e["ports_r"]
        col = (X(500), 690)
        for (px, py) in ports:
            cv.route("exhaust", [(px, py), (X(548), py - 20), (X(530), 760 if py > 760 else py - 40), col], w=10, arrows=(), smooth=True)
        t = turbo(cv, X(360), 395, comp_phi=-math.pi / 2 + (0.35 if not mir else 0.35), turb_phi=math.pi / 2, mirror=mir, R=46)
        tp[side] = t
        cv.route("exhaust", [col, (X(490), 620), t["t_in"]], w=20, arrows=(0.5,))
        wastegate(cv, X(462), 585, 18)
        # downpipe, below: to Doug's cutout behind the wheel, then back to the duals
        dp = cv.route("exhaust", [t["t_out"], (X(410), 520), (X(330), 560), (X(290), 700), (X(262), 960), (X(262), 1380)], w=16, arrows=(0.35, 0.82), hidden=True)
        # cutout box
        ccx = X(262)
        cv.grad("rect", (ccx - 22, 975, ccx + 22, 1035), (70, 76, 86), (170, 176, 186), outline=(20, 22, 26), r=6)
        cv.rect(ccx - 14, 985, ccx + 14, 1008, fill=(30, 30, 34))
        cv.route("exhaust", [(ccx - side * 24 if False else ccx + (-1 if not mir else 1) * 20, 1015), (ccx + (-1 if not mir else 1) * 48, 1040)], w=12, arrows=(0.7,), smooth=False)
        # filter to compressor inlet
        fcx = X(300)
        cone_filter(cv, fcx, 500, 70, 28, math.pi / 2 + (0.0), (60, 60, 66))
        cv.route("intake", [(fcx, 498), (X(330), 450), t["c_in"]], w=18, arrows=(0.45,))
        # compressor outlet to intercooler end tank
        cv.route("charge", [t["c_out"], (X(430), 318), (X(470), 330), (X(521), 336)], w=18, arrows=(0.6,))
        # oil feed (-4) and drain (-10)
        cv.route("oil", [(X(578), 800), (X(470), 770), (X(400), 640), (X(395), 520), t["chra"]], w=5, arrows=(0.5,))
        cv.route("oil", [t["chra"], (X(440), 490), (X(560), 620), (X(578), 700)], w=10, arrows=(0.7,))
        # catch can at the firewall, vents from the cover
        catch_can(cv, X(560), 1200, 24)
        cv.route("vent", [(X(620), 1130), (X(590), 1190), (X(584), 1200)], arrows=())
    # charge pipe IC center outlet -> TB, BOVs near TB
    cv.route("charge", [(cx, 362), (cx, 420), (cx, 520), (cx, 610)], w=22, arrows=(0.75,), smooth=False)
    for side in (-1, 1):
        bx = cx + side * 52
        cv.route("charge", [(cx, 560), (bx, 560)], w=10, arrows=(), smooth=False)
        bov(cv, bx, 560, 16)
    throttle_body(cv, cx, 642, 28)
    # coolant
    cv.route("coolant", [(cx + 20, 560), (840, 500), (960, 470), (996, 440)], w=14, arrows=(0.5,))
    cv.route("coolant", [(536, 440), (600, 520), (690, 540), (cx - 30, 556)], w=14, arrows=(0.5,))
    reservoir(cv, 1080, 960, 1170, 1080, (60, 200, 110))
    cv.route("coolant", [(996, 405), (1060, 420), (1110, 700), (1120, 960)], w=7, arrows=(0.5,))
    # A/C lines
    cv.route("ac", [(990, 560), (1040, 520), (1030, 420), (990, 380)], w=7, arrows=(0.5,))
    cv.route("ac", [(990, 580), (1080, 640), (1140, 900), (1180, 1100), (1150, 1240)], w=7, arrows=(0.6,))
    # oil cooler (passenger fender ahead of the wheel, ducted)
    cv.grad("rect", (1232, 420, 1296, 560), (120, 90, 30), (220, 170, 70), outline=(20, 22, 26), r=6)
    for y in range(428, 556, 6):
        cv.line([(1238, y), (1290, y)], (100, 70, 20), 1.5)
    cv.route("oil", [(950, 760), (1130, 700), (1200, 600), (1240, 540)], w=9, arrows=(0.5,))
    cv.route("oil", [(1270, 560), (1260, 700), (1150, 780), (950, 800)], w=9, arrows=(0.5,))
    # fuel: rails along the runners, feed from the rear, A1000 regulator at the firewall
    for side in (-1, 1):
        fx = cx + side * 88
        cv.route("fuel", [(fx, 690), (fx, 1100)], w=7, arrows=(), smooth=False)
    cv.route("fuel", [(700, 1290), (700, 1180), (cx - 88, 1100)], w=8, arrows=(0.4,))
    cv.route("fuel", [(cx - 88, 690), (cx, 680), (cx + 88, 690)], w=7, arrows=(), smooth=True)
    cv.route("fuel", [(cx + 88, 1100), (910, 1190)], w=7, arrows=(0.6,))
    cv.grad("ell", (910, 1200, 20, 20), (60, 20, 110), (190, 130, 255), outline=(20, 22, 26))
    cv.ell(910, 1200, 8, fill=(230, 230, 236))
    cv.route("fuel", [(925, 1215), (850, 1290)], w=7, arrows=(0.6,), smooth=False)
    # brake booster + master (driver firewall)
    booster_master(cv, 410, 1190, 56)
    # ECU on the passenger firewall
    box_module(cv, 1040, 1140, 1180, 1225, base=(30, 30, 36), led=(255, 60, 60), fins=True)
    cv.text(1110, 1182, "HOLLEY", 18, True, (220, 40, 40), "mm")
    # wiring
    cv.route("wire", [(1060, 1140), (1000, 1100), (965, 880), (950, 680)], arrows=(0.5,))
    cv.route("wire", [(1060, 1140), (1000, 1110), (560, 1110), (565, 680)], arrows=(0.7,))
    cv.route("wire", [(1180, 1225), (1200, 1290), (1250, 1420)], arrows=(0.5,))
    cv.route("wire", [(1110, 1140), (1150, 820), (1170, 520), (980, 480)], arrows=(0.6,))
    cv.text(1235, 1425, "1/0 cable from trunk battery", 22, True, (220, 224, 230), "ra")

    # callouts
    cv.call(1, (110, 330), [tp[-1]["c_in"]])
    cv.call(1, (1420, 330), [tp[1]["c_in"]])
    cv.call(2, (110, 600), [(462 - 18, 585)])
    cv.call(2, (1420, 600), [(1068 + 18, 585)])
    cv.call(3, (cx - 150, 560), [(cx - 52 - 14, 560)])
    cv.call(4, (cx + 300, 290), [(1000, 330)])
    cv.call(5, (cx - 330, 380), [(548, 380)])
    cv.call(6, (cx - 330, 440), [(550, 424)])
    cv.call(7, (cx + 300, 520), [(960, 548)])
    cv.call(8, (cx + 140, 640), [(cx + 30, 642)])
    cv.call(9, (cx, 1060), [(cx, 1030)])
    cv.call(10, (110, 760), [(520, 720)])
    cv.call(11, (110, 470), [(300, 540)])
    cv.call(12, (110, 1010), [(240, 1005)])
    cv.call(13, (110, 540), [(396, 535)])
    cv.call(14, (cx - 120, 1060), [(cx - 175, 1080)])
    cv.call(15, (1420, 480), [(1296, 490)])
    cv.call(16, (110, 1240), [(536, 1200)])
    cv.call(17, (1420, 1180), [(1180, 1182)])
    cv.call(18, (cx + 130, 1250), [(902, 1200)])
    cv.call(19, (110, 1130), [(380, 1110)])
    cv.call(20, (1420, 1020), [(1170, 1020)])
    cv.call(21, (110, 252), [(283, 252)])
    cv.key()
    cv.legend([
        (1, "Turbos x2", "Precision 6266 Gen2 or Speed Engineering 62 mm"),
        (2, "Wastegates x2", "Turbosmart GenV CompGate40"),
        (3, "Blow-off valves x2", "Turbosmart Race Port, by the throttle body"),
        (4, "Intercooler", "Treadstone or CX Racing, about 31x12x3.5"),
        (5, "A/C condenser", "RestoMod Air custom condenser kit"),
        (6, "Radiator + dual fans", "Champion or Griffin G-body LS, dual fans"),
        (7, "Accessory drive", "Holley mid-mount LS, alternator + A/C compressor"),
        (8, "Throttle body + intake", "Drive-by-wire (model not picked)"),
        (9, "Engine", "6.0 iron LS, forged; coil packs on the covers"),
        (10, "Headers + hot pipes", "Custom 321/304 stainless, ceramic coated"),
        (11, "Turbo inlet filters x2", "One per turbo, shielded (brand not picked)"),
        (12, "Downpipes + cutouts", "3 in stainless; Doug's DEC300A cutouts downstream"),
        (13, "Turbo oil lines", "Earl's or Russell -4 AN feeds, -10 AN drains"),
        (14, "Oil pan (under)", "Holley 302-2 LS retrofit pan, baffled"),
        (15, "Oil cooler", "Setrab or Earl's, sandwich adapter"),
        (16, "Catch cans x2", "Mighty Mouse"),
        (17, "ECU", "Holley Terminator X Max"),
        (18, "Fuel", "ID1050x injectors, Aeromotive A1000 regulator"),
        (19, "Brake booster + master", "Brand not picked"),
        (20, "Coolant overflow tank", "Brand not picked"),
        (21, "Headlights", "Holley RetroBright LFRB150 7x6 LED"),
    ])
    cv.footer()
    cv.save("cutlass-engine-bay-layout.png")


# ================= more components =================
def air_tank(cv, x0, y0, x1, y1):
    h = y1 - y0
    cv.grad("rect", (x0, y0, x1, y1), (110, 118, 128), (226, 232, 238), outline=(30, 32, 36), w=2, r=h / 2)
    cv.line([(x0 + h * 0.55, y0 + 4), (x0 + h * 0.55, y1 - 4)], (90, 96, 104), 2)
    cv.line([(x1 - h * 0.55, y0 + 4), (x1 - h * 0.55, y1 - 4)], (90, 96, 104), 2)
    cv.line([(x0 + h * 0.6, y0 + h * 0.28), (x1 - h * 0.6, y0 + h * 0.28)], (245, 248, 250), 3)
    ports = []
    for f in (0.3, 0.5, 0.7):
        px = x0 + (x1 - x0) * f
        cv.ell(px, y0 + 10, 7, fill=(200, 160, 40), outline=(60, 50, 10), w=1.5)
        ports.append((px, y0 + 10))
    return ports


def compressor(cv, x0, y0, x1, y1):
    """Motor can + finned head, long axis horizontal."""
    my = (y0 + y1) / 2
    cv.grad("rect", (x0, y0 + 8, x0 + (x1 - x0) * 0.62, y1 - 8), (20, 22, 26), (80, 86, 96), outline=(140, 146, 156), w=2, r=14)
    hx0 = x0 + (x1 - x0) * 0.6
    cv.grad("rect", (hx0, y0, x1, y1), ALU[0], ALU[1], outline=(30, 32, 36), w=2, r=10)
    x = hx0 + 7
    while x < x1 - 4:
        cv.line([(x, y0 + 4), (x, y1 - 4)], (90, 96, 104), 2)
        x += 7
    cv.rect(x0 + 10, y1 - 4, x0 + 40, y1 + 6, fill=(60, 60, 66))
    cv.rect(x1 - 30, y1 - 4, x1 - 6, y1 + 6, fill=(60, 60, 66))
    return (x1, my), (x0, my)


def water_trap(cv, cx, cy, r=20):
    cv.grad("ell", (cx, cy, r + 5, r + 5), (40, 44, 50), (120, 126, 136), outline=(20, 22, 26), w=2)
    cv.grad("ell", (cx, cy, r, r), (160, 200, 230), (230, 244, 252), outline=(60, 80, 100), w=1.5)
    cv.ell(cx, cy, r * 0.35, fill=(40, 120, 200))


def valve_manifold(cv, x0, y0, x1, y1):
    cv.grad("rect", (x0, y0, x1, y1), (120, 128, 138), (220, 226, 232), outline=(30, 32, 36), w=2, r=8)
    ports = []
    n = 4
    for i in range(n):
        px = x0 + (x1 - x0) * (i + 0.5) / n
        cv.grad("ell", (px, y0 + 22, 12, 12), (30, 32, 36), (90, 96, 104), outline=(200, 160, 40), w=2)
        ports.append((px, y0))
    cv.rect(x0 + 10, y1 - 20, x1 - 10, y1 - 8, fill=(20, 22, 26))
    return ports


def subwoofer(cv, cx, cy, r, ring=(176, 135, 78)):
    cv.ell(cx, cy, r + 10, fill=(14, 14, 16), outline=ring, w=3)
    for i in range(8):
        a = i * math.pi / 4
        cv.ell(cx + (r + 4) * math.cos(a), cy + (r + 4) * math.sin(a), 3, fill=(170, 170, 176))
    cv.grad("ell", (cx, cy, r, r), (30, 32, 36), (70, 74, 82), outline=(10, 10, 12), w=2)
    cv.ell(cx, cy, r * 0.86, outline=(90, 94, 100), w=2)
    cv.grad("ell", (cx, cy, r * 0.8, r * 0.8), (10, 10, 12), (44, 46, 52))
    cv.grad("ell", (cx, cy, r * 0.32, r * 0.32), (70, 74, 82), (16, 16, 18), outline=(110, 114, 120), w=1.5)


def amp(cv, x0, y0, x1, y1, base=(26, 26, 30), trim=(176, 135, 78), label="AMP"):
    cv.grad("rect", (x0, y0, x1, y1), base, lighten(base, 0.2), outline=trim, w=2.5, r=8)
    x = x0 + 12
    while x < x1 - 10:
        cv.line([(x, y0 + 10), (x, y1 - 26)], lighten(base, 0.3), 3)
        cv.line([(x + 3, y0 + 10), (x + 3, y1 - 26)], darken(base, 0.5), 1.5)
        x += 11
    for i in range(6):
        cv.ell(x0 + 18 + i * 16, y1 - 13, 5, fill=(200, 160, 40) if i < 2 else (150, 150, 156))
    cv.text(x1 - 12, y1 - 13, label, 18, True, trim, "rm")


def glow(cv, pts, col, w=6):
    for k, a in ((5, 0.85), (3, 0.6), (1.5, 0.3)):
        cv.line(pts, mix(col, BG, a), w * k)
    cv.line(pts, lighten(col, 0.2), w)


def headlight_pair(cv, cx, xoff, y0, y1, hw, halo=False):
    for side in (-1, 1):
        hx = cx + side * xoff
        cv.grad("rect", (hx - hw, y0, hx + hw, y1), (20, 22, 26), (70, 74, 82), outline=(150, 156, 166), w=2, r=12)
        cv.ell(hx - side * hw * 0.35, (y0 + y1) / 2, (y1 - y0) * 0.32, fill=(220, 232, 245), outline=(255, 140, 40) if halo else (120, 130, 140), w=3 if halo else 2)
        cv.ell(hx + side * hw * 0.4, (y0 + y1) / 2, (y1 - y0) * 0.22, fill=(180, 196, 214))


def diamond(cv, x0, y0, x1, y1, step, col):
    """Diamond-stitch lines clipped to a rectangle."""
    for sgn in (1, -1):
        k = -(x1 - x0) - (y1 - y0)
        while k < 2 * ((x1 - x0) + (y1 - y0)):
            pts = []
            # line: y - y0 = sgn * (x - x0) + k
            for x in (x0, x1):
                y = y0 + sgn * (x - x0) + k
                if y0 <= y <= y1:
                    pts.append((x, y))
            for y in (y0, y1):
                x = x0 + (y - y0 - k) * sgn
                if x0 <= x <= x1:
                    pts.append((x, y))
            pts = sorted(set(pts))
            if len(pts) >= 2:
                cv.line([pts[0], pts[-1]], col, 1)
            k += step


# ================= Cutlass trunk =================
def cutlass_trunk():
    cv = Cv(CUTLASS)
    cv.grid()
    cv.header("1979 Cutlass Supreme: trunk", "Burgundy carpet and trim panels hide the battery, fuel and security wiring. Pewter body, mini-tubs.")
    b = dict(L=215, R=1315, seat=300, bottom=1405, open=(300, 300, 1230, 1330), floor=(hexc("4a1820"), hexc("6a2430")),
             tubs=(360, 720), tub_depth=92, tire_w=86)
    trunk_body(cv, b)
    cx = 765
    # diamond stitch hint on the floor
    diamond(cv, 300, 346, 1230, 1330, 60, (110, 40, 52))
    # fuel tank under the floor (dashed)
    for q in dashes([(cx - 270, 420), (cx + 270, 420), (cx + 270, 690), (cx - 270, 690), (cx - 270, 420)], 16, 10):
        cv.line(q, (182, 110, 255), 3)
    cv.text(cx, 672, "TANK BELOW FLOOR", 22, True, (200, 160, 255), "mm")
    # fuel pump access panel
    cv.grad("rect", (cx - 120, 450, cx + 120, 610), (90, 30, 40), (130, 50, 62), outline=(200, 200, 206), w=2.5, r=10)
    for x, y in ((cx - 105, 465), (cx + 105, 465), (cx - 105, 595), (cx + 105, 595)):
        cv.ell(x, y, 5, fill=(200, 200, 206))
    cv.grad("ell", (cx, 530, 52, 52), (40, 44, 50), (150, 156, 166), outline=(20, 22, 26))
    cv.ell(cx, 530, 24, fill=(20, 22, 26), outline=(182, 110, 255), w=3)
    # fuel lines to the front
    cv.route("fuel", [(cx - 30, 478), (cx + 110, 400), (cx + 160, 300), (cx + 160, 170)], w=9, arrows=(0.7,))
    cv.route("fuel", [(cx + 205, 170), (cx + 205, 300), (cx + 150, 420), (cx + 30, 478)], w=9, arrows=(0.3,))
    # iKey module under the seat wall cover
    box_module(cv, 430, 370, 580, 440, base=(28, 28, 34), led=(60, 200, 255))
    cv.text(505, 398, "iKEY", 20, True, (160, 200, 230), "mm")
    # poppers in the doors (outside the trunk view)
    for side in (-1, 1):
        px = 120 if side < 0 else 1410
        cv.grad("rect", (px - 40, 230, px + 40, 280), (40, 44, 50), (150, 156, 166), vertical=False, outline=(20, 22, 26), r=10)
        cv.rect(px - 8 + side * 40, 245, px + 8 + side * 40, 265, fill=(200, 200, 206))
        cv.text(px, 312, "DOOR", 22, True, SUB, "mm")
    cv.route("wire", [(430, 380), (330, 330), (200, 270), (165, 255)], arrows=(0.6,))
    cv.route("wire", [(580, 395), (1000, 385), (1250, 300), (1365, 255)], arrows=(0.7,))
    # trunk release at the latch
    cv.grad("rect", (cx - 50, 1240, cx + 50, 1300), (50, 54, 60), (160, 166, 176), vertical=False, outline=(20, 22, 26), r=8)
    cv.ell(cx, 1270, 14, fill=(30, 30, 34), outline=(200, 200, 206), w=2)
    cv.route("wire", [(505, 440), (470, 800), (520, 1180), (cx - 50, 1270)], arrows=(0.5,))
    # spare well
    cv.grad("ell", (cx, 930, 200, 150), hexc("3a1219"), hexc("5a1e28"), outline=(150, 70, 80), w=3)
    cv.ell(cx, 930, 150, 108, outline=(120, 50, 60), w=2)
    cv.text(cx, 930, "SPARE WELL", 22, True, (220, 160, 170), "mm")
    # fuse and relay panel (driver side)
    box_module(cv, 330, 800, 490, 1000, base=(30, 30, 36), conn=False)
    for i in range(3):
        for j in range(2):
            cv.grad("rect", (345 + j * 72, 815 + i * 58, 405 + j * 72, 860 + i * 58), (20, 20, 24), (70, 74, 82), outline=(120, 126, 136), w=1.5, r=4)
    # battery box (passenger side)
    cv.grad("rect", (1000, 780, 1215, 980), (20, 20, 24), (54, 56, 62), outline=(200, 200, 206), w=2.5, r=14)
    pos, neg = battery(cv, 1020, 800, 1195, 960, "PC1200")
    cv.route("wire", [(1205, 870), (1240, 980), (1215, 1180)], arrows=(), w=4)
    cv.text(1120, 1000, "vent", 20, False, SUB, "mm")
    # cutoff + jump post
    cv.grad("ell", (1120, 1130, 30, 30), (150, 20, 20), (240, 70, 60), outline=(20, 22, 26), w=2)
    cv.rect(1104, 1124, 1136, 1136, fill=(240, 240, 240))
    cv.grad("ell", (1010, 1130, 18, 18), (150, 20, 20), (240, 70, 60), outline=(20, 22, 26), w=2)
    cv.ell(1010, 1130, 7, fill=(220, 190, 80))
    cv.route("wire", [pos, (985, 850), (985, 1060), (1092, 1118)], w=7, arrows=(0.5,))
    cv.route("wire", [(1150, 1130), (1215, 1100), (1225, 700), (1185, 330), (1185, 200)], w=7, arrows=(0.6,))
    cv.text(1175, 236, "1/0 to the bay", 22, True, (230, 232, 236), "ra")
    cv.route("wire", [(1090, 1130), (1028, 1130)], w=5, arrows=(), smooth=False)
    cv.route("wire", [(1000, 880), (700, 760), (490, 880)], arrows=(0.5,))
    cv.route("wire", [(490, 830), (620, 560), (cx - 52, 530)], arrows=(0.5,))
    cv.route("wire", [(330, 900), (300, 800), (260, 300), (260, 200)], arrows=(0.6,))
    cv.text(285, 236, "relays to the bay", 22, True, (230, 232, 236), "la")
    # tail panel
    glow(cv, [(260, 1372), (1270, 1372)], (255, 40, 40), 8)
    cv.call(1, (1420, 870), [(1215, 870)])
    cv.call(2, (1420, 1130), [(1150, 1130)])
    cv.call(3, (cx - 260, 1130), [(992, 1130)])
    cv.call(4, (cx + 380, 600), [(cx + 270, 600)])
    cv.call(5, (cx + 220, 520), [(cx + 120, 520)])
    cv.call(6, (cx - 140, 470), [(580, 420)])
    cv.call(7, (120, 400), [(120, 280)])
    cv.call(7, (1410, 400), [(1410, 280)])
    cv.call(8, (cx + 230, 1270), [(cx + 50, 1270)])
    cv.call(9, (110, 900), [(330, 900)])
    cv.call(10, (cx - 170, 1050), [(cx - 80, 1030)])
    cv.call(11, (110, 1372), [(260, 1372)])
    cv.call(12, (110, 560), [(280, 560)])
    cv.call(13, (cx - 250, 1240), [(cx - 200, 1180)])
    cv.key()
    cv.legend([
        (1, "Battery", "Odyssey PC1200 in a sealed, vented box"),
        (2, "Cutoff switch", "Painless relocation kit, 1/0 cable to the bay"),
        (3, "Jump post", "Remote positive post (brand not picked)"),
        (4, "Fuel tank (under floor)", "Tanks Inc G-body EFI tank or Holley Sniper tank"),
        (5, "Fuel pump access panel", "Aeromotive Phantom 340 (or dual pumps); feed and return run forward"),
        (6, "Security module", "Digital Guard Dawg iKey Premier IKEY-O, under the seat wall cover"),
        (7, "Door poppers x2 (in doors)", "AutoLoc AUTSL50 solenoids, fired by the iKey"),
        (8, "Trunk release", "Solenoid at the latch, fired by the iKey"),
        (9, "Fuse and relay panel", "Fuel pump relay, Doug's DEC300A cutout relays"),
        (10, "Spare well", "Carpeted to match"),
        (11, "Tail panel", "Custom full-width LED panel, smoked lens"),
        (12, "Mini-tubs", "Custom tubs plus frame notch kit"),
        (13, "Trim", "Burgundy ACC carpet and panels hide the wiring"),
    ])
    cv.footer()
    cv.save("cutlass-trunk-layout.png")


# ================= Charger =================
def charger_bay():
    cv = Cv(CHARGER)
    cv.grid()
    cv.header("2016 Charger Pursuit: engine bay", "Forged 392 HEMI, Whipple 3.0L twin-screw on top, 8HP90. White pearl, bronze accents.")
    b = dict(L=205, R=1325, top=200, cowl=1310, open=(305, 300, 1225, 1290), wheel=(600, 880), bulge=60, firewall=1240, tire_w=96)
    bay_body(cv, b)
    cx = 765
    cv.grad("rect", (cx - 230, 226, cx + 230, 280), (12, 12, 14), (44, 46, 52), outline=(176, 135, 78), w=2, r=8)
    for x in range(cx - 220, cx + 221, 14):
        cv.line([(x, 232), (x + 8, 274)], (60, 62, 68), 2)
    headlight_pair(cv, cx, 400, 226, 282, 110)
    # front heat exchanger (intercooler loop), radiator, fans
    finned(cv, 470, 300, 1060, 352, ((40, 120, 118), (110, 200, 196)), ALU, step=6, tw=30)
    finned(cv, 510, 368, 1020, 430, ((60, 70, 82), (120, 130, 144)), ((40, 44, 50), (90, 96, 106)), step=6, tw=30)
    cv.rect(550, 432, 980, 512, fill=(22, 24, 28), outline=(70, 76, 86), w=2, r=10)
    fan(cv, 655, 472, 33)
    fan(cv, 875, 472, 33)
    e = v8(cv, cx, 650, 1160, half=195, hemi=True, cover=(hexc("1a1a1c"), hexc("4a4a50")), coil_col=(30, 30, 34))
    for vx0, vx1 in (e["cover_l"], e["cover_r"]):
        cv.line([((vx0 + vx1) / 2, 690), ((vx0 + vx1) / 2, 720)], (176, 135, 78), 4)
    # exhaust manifolds to the rear
    for side in (-1, 1):
        ports = e["ports_l"] if side < 0 else e["ports_r"]
        mx = cx + side * 222
        for (px, py) in ports:
            cv.route("exhaust", [(px, py), (mx, py + 18)], w=12, arrows=(), smooth=False)
        cv.route("exhaust", [(mx, ports[0][1]), (mx, ports[-1][1] + 30), (mx + side * 10, 1300), (mx + side * 10, 1420)], w=20, arrows=(0.35, 0.85))
    cv.text(cx, 1372, "to 6.4 midpipes + cat-back", 22, True, (255, 180, 150), "mm")
    # Whipple blower: intake base, rotor case, intercooler lid
    cv.grad("rect", (cx - 118, 668, cx + 118, 1136), (60, 64, 72), (120, 126, 136), vertical=False, outline=(20, 22, 26), w=2, r=22)
    cv.grad("rect", (cx - 104, 690, cx + 104, 1112), ALU[0], (240, 244, 248), vertical=False, outline=(20, 22, 26), w=2, r=30)
    finned(cv, cx - 84, 740, cx + 84, 1060, ((40, 120, 118), (120, 205, 200)), ((150, 158, 168), (230, 234, 240)), vertical_fins=False, step=8, tanks="tb", tw=30)
    for xx in (cx - 86, cx - 30, cx + 30, cx + 86):
        cv.ell(xx, 712, 4, fill=(60, 64, 72))
    for xx in (cx - 86, cx + 86):
        cv.ell(xx, 1090, 4, fill=(60, 64, 72))
    cv.text(cx, 1086, "3.0L", 20, True, (60, 64, 72), "mm")
    # billet fuel rails with Hellcat injectors, drawn beside the blower
    for side in (-1, 1):
        fx = cx + side * 132
        cv.route("fuel", [(fx, 720), (fx, 1110)], w=9, arrows=(), smooth=False)
        for y in e["cyl_y"]:
            yy = y + (0 if side < 0 else 22)
            cv.ell(fx, yy, 7, fill=(30, 30, 34), outline=(182, 110, 255), w=2)
    cv.route("fuel", [(cx - 132, 1110), (cx, 1146), (cx + 132, 1110)], w=7, arrows=())
    cv.route("fuel", [(700, 1300), (680, 1200), (cx - 132, 1112)], w=8, arrows=(0.4,))
    # snout: inlet + throttle body (driver), drive pulley (passenger)
    cv.grad("rect", (cx - 118, 600, cx - 28, 690), (110, 118, 128), (226, 230, 236), vertical=False, outline=(20, 22, 26), r=14)
    cv.grad("rect", (cx + 40, 606, cx + 104, 690), (110, 118, 128), (226, 230, 236), vertical=False, outline=(20, 22, 26), r=12)
    belt(cv, [(cx, 640, 30), (cx + 72, 590, 26), (cx + 160, 616, 14), (cx - 2, 560, 22)])
    pulley(cv, cx - 2, 560, 22)
    pulley(cv, cx, 640, 30)
    pulley(cv, cx + 72, 590, 26)
    pulley(cv, cx + 160, 616, 14)
    throttle_body(cv, cx - 73, 598, 30)
    # inlet filter, driver front corner, into the throttle body
    cone_filter(cv, 430, 560, 90, 32, math.pi, (176, 135, 78))
    cv.route("intake", [(432, 560), (520, 590), (600, 600), (cx - 112, 600)], w=24, arrows=(0.5,))
    # intercooler coolant loop: heat exchanger -> reservoir -> pump -> lid -> back
    reservoir(cv, 1060, 540, 1140, 650, (40, 210, 200))
    cv.grad("rect", (1078, 690, 1122, 770), (30, 30, 34), (80, 84, 92), vertical=False, outline=(150, 156, 166), w=2, r=12)
    cv.ell(1100, 704, 8, fill=(40, 210, 200), outline=(20, 22, 26), w=1.5)
    cv.route("ic", [(1059, 326), (1110, 420), (1100, 540)], w=10, arrows=(0.5,))
    cv.route("ic", [(1100, 650), (1100, 690)], w=10, arrows=(), smooth=False)
    cv.route("ic", [(1100, 770), (1020, 810), (920, 820), (cx + 86, 900)], w=10, arrows=(0.5,))
    cv.route("ic", [(cx - 86, 800), (640, 760), (540, 640), (500, 450), (471, 330)], w=10, arrows=(0.3, 0.75))
    # engine coolant
    cv.route("coolant", [(cx + 22, 556), (900, 520), (990, 470), (1006, 430)], w=14, arrows=(0.5,))
    cv.route("coolant", [(524, 420), (590, 500), (690, 545), (cx - 22, 556)], w=14, arrows=(0.5,))
    reservoir(cv, 1080, 940, 1170, 1060, (255, 140, 180))
    cv.route("coolant", [(1006, 380), (1170, 560), (1180, 800), (1130, 940)], w=7, arrows=(0.5,))
    # oil cooler passenger front, braided lines
    cv.grad("rect", (1150, 300, 1210, 420), (120, 90, 30), (220, 170, 70), outline=(20, 22, 26), r=6)
    for y in range(306, 416, 6):
        cv.line([(1156, y), (1204, y)], (100, 70, 20), 1.5)
    cv.route("oil", [(960, 760), (1040, 700), (1190, 560), (1195, 422)], w=8, arrows=(0.5,))
    cv.route("oil", [(1165, 422), (1150, 520), (1000, 680), (960, 780)], w=8, arrows=(0.5,))
    # catch cans
    for side in (-1, 1):
        ccx = cx + side * 250
        catch_can(cv, ccx, 1210, 24)
        cv.route("vent", [(cx + side * 150, 1140), (cx + side * 200, 1200), (ccx - side * 22, 1208)], arrows=())
    # PCM driver side
    box_module(cv, 385, 900, 495, 1010, base=(34, 34, 40), led=(60, 220, 120), fins=True)
    cv.text(440, 940, "PCM", 18, True, (176, 135, 78), "mm")
    cv.route("wire", [(495, 950), (560, 1110), (980, 1110), (965, 720)], arrows=(0.7,))
    cv.route("wire", [(440, 900), (420, 760), (500, 680), (cx - 110, 640)], arrows=(0.5,))
    # power distribution center + jump post (battery in the trunk)
    box_module(cv, 1080, 1100, 1200, 1225, base=(26, 26, 30), conn=False)
    cv.rect(1095, 1115, 1185, 1160, outline=(90, 94, 100), w=1.5, r=4)
    cv.grad("ell", (1110, 1195, 14, 14), (150, 20, 20), (240, 70, 60), outline=(20, 22, 26))
    cv.route("wire", [(1200, 1190), (1215, 1290), (1250, 1420)], w=6, arrows=(0.5,))
    cv.text(1235, 1425, "power from trunk battery", 22, True, (230, 232, 236), "ra")
    cv.route("wire", [(1080, 760), (1060, 900), (1080, 1100)], w=4, arrows=(0.5,))
    booster_master(cv, 420, 1190, 56)
    cv.call(1, (110, 330), [(cx - 100, 720)])
    cv.call(2, (cx - 330, 880), [(cx - 40, 930)])
    cv.call(3, (cx + 330, 255), [(1040, 326)])
    cv.call(4, (1420, 600), [(1140, 600)])
    cv.call(4, (1420, 730), [(1122, 730)])
    cv.call(5, (110, 470), [(380, 560)])
    cv.call(6, (cx - 190, 520), [(cx - 90, 585)])
    cv.call(7, (1420, 470), [(cx + 168, 612)])
    cv.call(8, (1420, 870), [(905, 870)])
    cv.call(9, (cx + 150, 1250), [(cx + 132, 1100)])
    cv.call(10, (cx, 470), [(700, 410)])
    cv.call(11, (110, 1250), [(cx - 274, 1210)])
    cv.call(11, (1420, 1230), [(cx + 274, 1210)])
    cv.call(12, (1420, 330), [(1210, 360)])
    cv.call(13, (110, 760), [(cx - 222, 760)])
    cv.call(14, (110, 960), [(385, 955)])
    cv.call(15, (1420, 1160), [(1200, 1160)])
    cv.call(16, (110, 1110), [(404, 1110)])
    cv.call(17, (1420, 1000), [(1170, 1000)])
    cv.call(18, (cx - 230, 165), [(cx - 400, 226)])
    cv.key()
    cv.legend([
        (1, "Supercharger", "Whipple Gen 6 3.0L twin-screw, top-mount, kit WK-3021-30 (blower + intake, about 7 psi)"),
        (2, "Intercooler", "Dual-pass air-to-water core in the blower lid"),
        (3, "Heat exchanger", "Whipple kit, front bumper opening"),
        (4, "Intercooler pump + reservoir", "Whipple kit, passenger front"),
        (5, "Inlet filter", "Kit filter, driver front corner, into the throttle body"),
        (6, "Throttle body", "Whipple inlet, front of the blower"),
        (7, "Supercharger drive", "Whipple pulley and belt off the crank"),
        (8, "Engine", "Forged 6.4 / 392 HEMI; 8HP90 transmission behind it"),
        (9, "Fuel", "Hellcat injectors on billet rails (kit); upgraded pump in the tank"),
        (10, "Radiator + fans", "Factory heavy-duty Pursuit cooling"),
        (11, "Catch cans x2", "Mishimoto or UPR"),
        (12, "Oil cooler", "Braided lines"),
        (13, "Exhaust manifolds", "Into 6.4 midpipes and a Borla ATAK or Corsa Xtreme cat-back"),
        (14, "PCM", "6.4 calibration, HP Tuners custom tune"),
        (15, "Fuse box + jump post", "Factory; the H8 AGM battery is in the trunk"),
        (16, "Brake booster + master", "Factory; SRT/Hellcat Brembos at the wheels"),
        (17, "Coolant bottle", "Factory"),
        (18, "Headlights", "Morimoto XB LED or AlphaRex NOVA LED"),
    ])
    cv.footer()
    cv.save("charger-engine-bay-layout.png")


def charger_trunk():
    cv = Cv(CHARGER)
    cv.grid()
    cv.header("2016 Charger Pursuit: trunk", "Two subs behind plexiglass, raised amp panel, black suede with bronze stitching.")
    b = dict(L=205, R=1325, seat=300, bottom=1405, open=(295, 300, 1235, 1330), floor=(hexc("141416"), hexc("26262a")),
             tubs=(360, 700), tub_depth=80, tire_w=96)
    trunk_body(cv, b)
    cx = 765
    bronze = (176, 135, 78)
    diamond(cv, 295, 346, 1235, 1330, 70, (70, 56, 40))
    # sub enclosure against the seat wall
    cv.grad("rect", (400, 360, 1130, 580), (20, 20, 22), (44, 44, 48), outline=bronze, w=3, r=16)
    subwoofer(cv, 590, 470, 88)
    subwoofer(cv, 940, 470, 88)
    cv.rect(412, 372, 1118, 568, outline=(150, 170, 190), w=2, r=12)
    cv.line([(430, 380), (520, 380)], (200, 220, 240), 3)
    glow(cv, [(410, 588), (1120, 588)], bronze, 5)
    # raised amp panel
    cv.grad("rect", (420, 620, 1110, 800), (24, 24, 26), (50, 50, 54), outline=bronze, w=3, r=12)
    amp(cv, 450, 645, 755, 775, label="MONO")
    amp(cv, 785, 645, 1080, 775, label="4-CH")
    glow(cv, [(430, 810), (1100, 810)], bronze, 5)
    # remote start side panel (driver)
    cv.grad("rect", (320, 820, 470, 1150), (30, 30, 34), (52, 52, 58), outline=bronze, w=2, r=10)
    box_module(cv, 335, 840, 455, 930, base=(18, 18, 22), led=(60, 160, 255))
    cv.text(395, 880, "CS7900", 17, True, (150, 180, 220), "mm")
    box_module(cv, 335, 950, 455, 1020, base=(18, 18, 22), led=(60, 220, 120))
    cv.text(395, 982, "LTE", 18, True, (150, 220, 170), "mm")
    box_module(cv, 335, 1040, 455, 1120, base=(18, 18, 22), led=(255, 170, 40))
    cv.text(395, 1076, "BLADE", 17, True, (230, 190, 120), "mm")
    # battery hidden panel (passenger)
    for q in dashes([(1010, 880), (1215, 880), (1215, 1180), (1010, 1180), (1010, 880)], 16, 10):
        cv.line(q, bronze, 3)
    pos, neg = battery(cv, 1030, 920, 1195, 1080, "H8 AGM")
    cv.text(1112, 1150, "under floor", 20, True, (210, 180, 140), "mm")
    # distribution block
    cv.grad("rect", (cx - 70, 960, cx + 70, 1030), (120, 90, 40), (220, 180, 100), outline=(20, 22, 26), r=6)
    for i in range(4):
        cv.ell(cx - 45 + i * 30, 995, 8, fill=(40, 40, 44), outline=(240, 220, 160), w=1.5)
    cv.route("wire", [pos, (980, 900), (cx + 70, 995)], w=7, arrows=(0.5,))
    cv.route("wire", [(cx - 30, 960), (650, 860), (600, 775)], w=6, arrows=(0.6,))
    cv.route("wire", [(cx + 30, 960), (880, 860), (930, 775)], w=6, arrows=(0.6,))
    cv.route("wire", [(595, 645), (560, 600), (590, 560)], w=4, arrows=(0.5,))
    cv.route("wire", [(1195, 1000), (1230, 800), (1225, 400), (1215, 200)], w=6, arrows=(0.7,))
    cv.text(1195, 236, "to the bay", 22, True, (230, 232, 236), "ra")
    cv.route("wire", [(455, 885), (500, 1000), (cx - 70, 1000)], w=4, arrows=(0.5,))
    cv.route("wire", [(320, 900), (280, 700), (270, 300), (270, 200)], w=4, arrows=(0.7,))
    cv.text(290, 236, "to BCM / doors", 22, True, (230, 232, 236), "la")
    # racetrack tail light
    glow(cv, [(270, 1372), (1260, 1372)], (255, 40, 40), 9)
    cv.call(1, (cx, 680 - 280), [(cx - 120, 470), (cx + 120, 470)])
    cv.call(2, (110, 470), [(400, 470)])
    cv.call(3, (cx - 230, 860), [(600, 775)])
    cv.call(4, (cx + 230, 860), [(930, 775)])
    cv.call(5, (cx + 360, 600), [(1100, 588)])
    cv.call(6, (110, 885), [(335, 885)])
    cv.call(7, (110, 985), [(335, 985)])
    cv.call(8, (110, 1080), [(335, 1080)])
    cv.call(9, (1420, 1000), [(1195, 1000)])
    cv.call(10, (cx, 1110), [(cx, 1030)])
    cv.call(11, (110, 1372), [(270, 1372)])
    cv.call(12, (cx - 250, 1230), [(cx - 200, 1180)])
    cv.key()
    cv.legend([
        (1, "Subwoofers x2", "12 in, behind plexiglass (brand not picked)"),
        (2, "Sub enclosure", "Custom box against the rear seat wall, black suede"),
        (3, "Amp 1 (subs)", "Mono amp on the raised panel (brand not picked)"),
        (4, "Amp 2 (speakers)", "4-channel amp (brand not picked)"),
        (5, "Accent lighting", "Bronze LED strips under the box and panel"),
        (6, "Remote start + alarm", "Compustar CS7900-AS 2-way, FTI-SPTS-CH start kill"),
        (7, "Phone app module", "DroneMobile X2 LTE"),
        (8, "Bypass", "Blade-AL flashed for the car, push-to-start T-harness"),
        (9, "Battery (factory spot)", "H8 AGM, Odyssey or Mopar, under the floor"),
        (10, "Distribution block", "Fused amp power, fuse at the battery"),
        (11, "Taillight", "Stock racetrack LED (AlphaRex NOVA smoked optional)"),
        (12, "Floor", "Black suede with bronze stitching"),
    ])
    cv.footer()
    cv.save("charger-trunk-layout.png")


# ================= Cruze =================
def cruze_bay():
    cv = Cv(CRUZE)
    cv.grid()
    cv.header("2012 Cruze LT RS: engine bay", "1.4T, transverse, ZZP Z04 turbo once the engine tests healthy. Gloss black, burnt orange accents.")
    b = dict(L=230, R=1300, top=200, cowl=1310, open=(325, 300, 1205, 1290), wheel=(560, 840), bulge=56, firewall=1240, tire_w=86)
    bay_body(cv, b)
    cx = 765
    orange = (230, 110, 30)
    cv.grad("rect", (cx - 200, 226, cx + 200, 282), (8, 8, 10), (40, 42, 46), outline=(90, 94, 100), w=2, r=10)
    for x in range(cx - 190, cx + 191, 18):
        cv.line([(x, 232), (x, 276)], (50, 52, 58), 2)
    headlight_pair(cv, cx, 380, 226, 282, 130, halo=True)
    # intercooler, oil cooler, radiator
    finned(cv, 440, 300, 1090, 352, ((120, 128, 138), (190, 198, 208)), ALU, step=6, tw=30)
    finned(cv, 520, 370, 1010, 430, ((60, 70, 82), (120, 130, 144)), ((40, 44, 50), (90, 96, 106)), step=6, tw=26)
    cv.rect(580, 432, 950, 500, fill=(22, 24, 28), outline=(70, 76, 86), w=2, r=10)
    fan(cv, 765, 466, 30)
    cv.grad("rect", (1110, 370, 1180, 460), (120, 90, 30), (220, 170, 70), outline=(20, 22, 26), r=6)
    for y in range(376, 456, 6):
        cv.line([(1116, y), (1174, y)], (100, 70, 20), 1.5)
    # transaxle (driver side)
    cv.grad("rect", (360, 640, 520, 900), (60, 66, 74), (150, 156, 166), vertical=False, outline=(20, 22, 26), w=2, r=30)
    for y in range(660, 890, 22):
        cv.line([(372, y), (508, y)], (90, 96, 106), 1.5)
    # engine block, intake manifold (front), valve cover
    cv.grad("rect", (520, 600, 1080, 900), IRON[0], IRON[1], outline=(20, 22, 26), w=2, r=16)
    for i in range(4):
        x = 600 + i * 125
        cv.grad("rect", (x - 26, 560, x + 26, 680), (70, 76, 86), (150, 156, 166), vertical=False, outline=(20, 22, 26), r=10)
    cv.grad("rect", (560, 540, 1000, 600), (96, 104, 116), (190, 198, 208), outline=(20, 22, 26), w=2, r=24)
    cv.grad("rect", (545, 660, 1060, 860), (14, 14, 16), (60, 62, 68), outline=(150, 156, 166), w=2, r=24)
    cv.rect(560, 676, 1045, 844, outline=(40, 42, 46), w=1.5, r=18)
    cv.text(700, 820, "ECOTEC", 20, True, orange, "mm")
    for i in range(4):
        x = 600 + i * 125
        cv.grad("rect", (x - 24, 724, x + 24, 776), (24, 24, 28), (70, 74, 80), outline=(120, 120, 130), w=1.5, r=6)
    cv.grad("rect", (580, 742, 980, 758), (40, 40, 44), (90, 90, 96), outline=(20, 22, 26), r=6)
    # PCV area on the cover (passenger end)
    cv.grad("ell", (1015, 760, 22, 22), (40, 40, 44), (110, 110, 118), outline=orange, w=2.5)
    cv.ell(1015, 760, 8, fill=orange)
    # throttle body on the driver end of the intake
    throttle_body(cv, 535, 570, 26)
    # turbo on the firewall side
    t = turbo(cv, 760, 990, comp_phi=0.0, turb_phi=-math.pi / 2, R=48)
    cv.route("exhaust", [(840, 870), (860, 920), t["t_in"]], w=22, arrows=(0.5,), smooth=False)
    for i in range(4):
        x = 610 + i * 110
        cv.route("exhaust", [(x, 860), (x + 30, 880), (840, 880)], w=10, arrows=(), smooth=True)
    cv.route("exhaust", [t["t_out"], (900, 1100), (960, 1250), (990, 1420)], w=18, arrows=(0.4, 0.85), hidden=True)
    cv.text(930, 1338, "to single 4 in tip cat-back", 22, True, (255, 180, 150), "ra")
    # intake: filter in the driver fender to the compressor inlet
    cone_filter(cv, 420, 520, 80, 30, -math.pi / 2 - 0.3, orange)
    cv.route("intake", [(420, 524), (450, 600), (500, 960), (620, 1040), t["c_in"]], w=20, arrows=(0.3, 0.8))
    # charge: compressor out -> passenger side -> IC right tank; IC left tank -> TB
    cv.route("charge", [t["c_out"], (1000, 960), (1130, 900), (1150, 600), (1120, 360), (1089, 330)], w=18, arrows=(0.3, 0.7))
    cv.route("charge", [(441, 330), (400, 380), (440, 470), (500, 560), (509, 570)], w=18, arrows=(0.5,))
    bov(cv, 395, 430, 17)
    # PCV: cover -> CruzeKits check valve -> intake
    cv.route("vent", [(1015, 760), (1062, 660), (1058, 522)], arrows=(0.5,))
    cv.grad("rect", (1040, 462, 1076, 522), (20, 20, 22), (90, 90, 96), outline=orange, w=2, r=6)
    cv.route("vent", [(1058, 462), (1015, 470), (990, 545)], arrows=(0.5,))
    # catch can
    catch_can(cv, 1000, 1110, 26)
    cv.route("vent", [(980, 830), (1000, 950), (1000, 1084)], arrows=(0.5,))
    cv.route("vent", [(975, 1112), (700, 1100), (600, 1050)], arrows=(0.5,))
    # coolant
    cv.route("coolant", [(1006, 400), (1060, 520), (1070, 620)], w=12, arrows=(0.5,))
    cv.route("coolant", [(523, 420), (540, 470), (540, 540)], w=12, arrows=(0.5,))
    reservoir(cv, 1100, 1060, 1185, 1180, (255, 140, 60))
    cv.route("coolant", [(1080, 860), (1140, 960), (1142, 1060)], w=7, arrows=(0.5,))
    # oil cooler lines
    cv.route("oil", [(1060, 640), (1120, 520), (1130, 462)], w=8, arrows=(0.5,))
    cv.route("oil", [(1165, 462), (1170, 560), (1080, 700)], w=8, arrows=(0.5,))
    # turbo oil
    cv.route("oil", [(700, 900), (760, 940), t["chra"]], w=5, arrows=(0.5,))
    cv.route("oil", [t["chra"], (820, 960), (850, 900)], w=8, arrows=(0.5,))
    # fuel rail
    cv.route("fuel", [(580, 640), (1000, 640)], w=7, arrows=(), smooth=False)
    cv.route("fuel", [(640, 1300), (620, 1180), (560, 1000), (580, 640)], w=8, arrows=(0.5,))
    # battery + fuse box (driver rear) and booster
    battery(cv, 345, 960, 500, 1100, "BATT")
    box_module(cv, 345, 1120, 500, 1200, base=(20, 20, 24), conn=False)
    cv.text(422, 1160, "FUSES", 18, True, (150, 150, 160), "mm")
    cv.route("wire", [(470, 990), (520, 950), (560, 880), (600, 790)], arrows=(0.6,))
    cv.route("wire", [(380, 990), (330, 900), (330, 330)], arrows=(0.5,))
    booster_master(cv, 620, 1200, 48)
    cv.call(1, (cx + 50, 1180), [(t["c_in"][0] + 8, t["c_in"][1] + 12)])
    cv.call(2, (cx + 400, 285), [(1060, 320)])
    cv.call(3, (1150, 1372), [(985, 1360)])
    cv.call(4, (110, 470), [(400, 480)])
    cv.call(5, (cx + 60, 700), [(cx, 720)])
    cv.call(6, (1420, 500), [(1076, 492)])
    cv.call(7, (1420, 1110), [(1026, 1110)])
    cv.call(8, (cx - 140, 520), [(560, 560)])
    cv.call(9, (110, 380), [(378, 430)])
    cv.call(10, (cx - 300, 360), [(540, 410)])
    cv.call(11, (1420, 380), [(1180, 400)])
    cv.call(12, (cx + 120, 515), [(900, 640)])
    cv.call(13, (110, 1030), [(345, 1030)])
    cv.call(14, (110, 1160), [(345, 1160)])
    cv.call(15, (110, 760), [(360, 760)])
    cv.call(16, (cx - 250, 1260), [(650, 1210)])
    cv.call(17, (1420, 1200), [(1185, 1170)])
    cv.call(18, (110, 254), [(250, 254)])
    cv.key()
    cv.legend([
        (1, "Turbo", "ZZP Z04 bolt-on kit, only after the engine tests healthy"),
        (2, "Front mount intercooler", "ZZP"),
        (3, "Downpipe", "ZZP, to a single 4 in tip cat-back"),
        (4, "Cold air intake", "Driver fender (ZZP or similar)"),
        (5, "Valve cover", "GM/ACDelco 55573746 with built-in PCV"),
        (6, "PCV check valve", "CruzeKits 1.4T PCV fix kit (external)"),
        (7, "Catch can", "ZZP"),
        (8, "Throttle body", "Factory; BNR spacer if the PCV kit needs it"),
        (9, "Blow-off / diverter", "Not picked"),
        (10, "Radiator + fan", "Factory"),
        (11, "Oil cooler", "ZZP oil cooler kit, AN lines"),
        (12, "Fuel + tune", "Upgraded injectors, Trifecta or ZZP tune"),
        (13, "Battery", "Driver side (brand not picked)"),
        (14, "Fuse box", "Factory"),
        (15, "Transaxle", "Factory"),
        (16, "Brake booster + master", "Factory"),
        (17, "Coolant tank", "Factory, Dex-Cool"),
        (18, "Headlights", "Spyder Auto black LED halo projectors"),
    ])
    cv.footer()
    cv.save("cruze-engine-bay-layout.png")


def cruze_trunk():
    cv = Cv(CRUZE)
    cv.grid()
    cv.header("2012 Cruze LT RS: trunk", "Air Lift Performance 3P/3H air ride, burnt orange lighting, smoked LED taillights.")
    b = dict(L=230, R=1300, seat=300, bottom=1405, open=(310, 300, 1220, 1330), floor=(hexc("161618"), hexc("2a2a2e")),
             tubs=(360, 690), tub_depth=82, tire_w=86)
    trunk_body(cv, b)
    cx = 765
    orange = (230, 100, 20)
    # false floor panel with lighting
    cv.rect(400, 400, 1130, 1220, outline=(70, 70, 78), w=2, r=20)
    glow(cv, [(420, 1240), (1110, 1240)], orange, 5)
    glow(cv, [(390, 760), (390, 1200)], orange, 5)
    glow(cv, [(1140, 760), (1140, 1200)], orange, 5)
    # management ECU + manifold
    box_module(cv, 430, 400, 590, 480, base=(18, 18, 22), led=orange)
    cv.text(510, 433, "3P / 3H", 18, True, orange, "mm")
    ports = valve_manifold(cv, 680, 410, 860, 490)
    # tank
    tp = air_tank(cv, 440, 580, 1090, 720)
    cv.route("air", [tp[1], (cx, 490)], arrows=(0.5,), smooth=False)
    # air lines from the manifold to the bags
    cv.route("air", [ports[0], (680, 360), (400, 340), (360, 250), (360, 170)], arrows=(0.8,))
    cv.route("air", [ports[3], (870, 360), (1130, 340), (1170, 250), (1170, 170)], arrows=(0.8,))
    cv.route("air", [(700, 490), (640, 530), (500, 530), (410, 540)], arrows=(0.8,))
    cv.route("air", [(830, 490), (900, 530), (1030, 530), (1130, 540)], arrows=(0.8,))
    cv.text(380, 210, "to front bags", 22, True, (220, 222, 228), "la")
    cv.text(1150, 210, "to front bags", 22, True, (220, 222, 228), "ra")
    # rear bags in the wheel wells
    for x in (300, 1230):
        cv.grad("ell", (x, 540, 34, 34), (20, 20, 22), (70, 72, 78), outline=(170, 178, 188), w=2)
        for r in (24, 15):
            cv.ell(x, 540, r, outline=(110, 114, 120), w=2)
    # compressors, water traps
    c1o, c1i = compressor(cv, 430, 820, 640, 900)
    c2o, c2i = compressor(cv, 890, 820, 1100, 900)
    water_trap(cv, 560, 1010, 20)
    water_trap(cv, 970, 1010, 20)
    cv.route("air", [(640, 870), (650, 960), (580, 1010)], arrows=(0.5,))
    cv.route("air", [(1100, 870), (1110, 960), (990, 1010)], arrows=(0.5,))
    cv.route("air", [(540, 1010), (460, 960), (420, 760), (470, 712)], arrows=(0.6,))
    cv.route("air", [(950, 1010), (860, 960), (900, 780), (1000, 712)], arrows=(0.6,))
    # relays + fuse
    box_module(cv, cx - 70, 1080, cx + 70, 1170, base=(20, 20, 24), conn=False)
    for i in range(2):
        cv.grad("rect", (cx - 58 + i * 64, 1094, cx - 10 + i * 64, 1140), (20, 20, 24), (70, 74, 82), outline=(120, 126, 136), w=1.5, r=4)
    cv.route("wire", [(cx - 70, 1125), (520, 1060), (450, 900)], arrows=(0.6,))
    cv.route("wire", [(cx + 70, 1125), (1000, 1060), (1020, 900)], arrows=(0.6,))
    cv.route("wire", [(cx, 1170), (cx - 200, 1270), (300, 1250), (270, 760), (275, 170)], w=6, arrows=(0.75,))
    cv.route("wire", [(590, 440), (680, 470)], arrows=(), smooth=False)
    cv.route("wire", [(575, 400), (565, 300), (560, 170)], arrows=(0.7,))
    # smoked taillights
    for side in (-1, 1):
        x0 = 250 if side < 0 else 1060
        cv.grad("rect", (x0, 1340, x0 + 220, 1395), (30, 6, 6), (110, 20, 20), outline=(60, 60, 66), w=2, r=14)
        glow(cv, [(x0 + 20, 1367), (x0 + 200, 1367)], (255, 50, 40), 4)
    cv.call(1, (110, 440), [(430, 440)])
    cv.call(2, (cx + 230, 470), [(860, 465)])
    cv.call(3, (cx, 790), [(cx, 720)])
    cv.call(4, (cx - 210, 960), [(560, 900)])
    cv.call(4, (cx + 210, 960), [(1000, 900)])
    cv.call(5, (110, 1010), [(536, 1010)])
    cv.call(5, (1420, 1010), [(994, 1010)])
    cv.call(6, (1420, 540), [(1264, 540)])
    cv.call(6, (110, 540), [(266, 540)])
    cv.call(7, (1010, 400), [(905, 352)])
    cv.call(12, (cx - 90, 235), [(561, 225)])
    cv.call(13, (110, 760), [(272, 760)])
    cv.call(8, (cx + 230, 1160), [(cx + 70, 1140)])
    cv.call(9, (1420, 1240), [(1110, 1240)])
    cv.call(10, (110, 1367), [(250, 1367)])
    cv.call(11, (1420, 300), [(1170, 240)])
    cv.key()
    cv.legend([
        (1, "Management ECU", "Air Lift Performance 3P (or 3H with height sensors)"),
        (2, "Valve manifold", "Air Lift 3P/3H, built-in pressure sensors"),
        (3, "Air tank", "5 gal aluminum, centered"),
        (4, "Compressors x2", "Brand not picked"),
        (5, "Water traps x2", "One per compressor, before the tank"),
        (6, "Rear bags", "UAS bags on Ksport struts, or AirREX struts"),
        (7, "Air lines", "Braided lines from the manifold to all four bags"),
        (8, "Relays + fuse", "Compressor relays, fused feed from the battery"),
        (9, "Lighting", "Burnt orange app-controlled RGB LED strips"),
        (10, "Taillights", "Smoked LED, part SW-0126A-BRB"),
        (11, "Front bag lines", "Run under the car to the front struts"),
        (12, "Controller (in the cabin)", "Air Lift 3P/3H controller, wired from the ECU"),
        (13, "Power feed", "Fused 8 AWG run from the battery up front"),
    ])
    cv.footer()
    cv.save("cruze-trunk-layout.png")



if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["all"]
    fns = {"cutlass_bay": cutlass_bay, "cutlass_trunk": cutlass_trunk, "charger_bay": charger_bay,
           "charger_trunk": charger_trunk, "cruze_bay": cruze_bay, "cruze_trunk": cruze_trunk}
    for k, f in fns.items():
        if "all" in which or k in which:
            f()
