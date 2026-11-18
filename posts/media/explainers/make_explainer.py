"""DRT animated chart explainers (series started 11/18 on Tim's request: "create videos like this for content").

Original 9:16 explainers built from REAL ES bars: candles print, then the concept builds on the chart step by step
(profile, zones, call-outs), and on-screen text does the teaching. Music is added after with drt/audio/add_audio.py.
No voiceover, no indicator names, no AMD/CRT, no trade calls, no P&L, no dates on screen.

Usage
  python3 make_explainer.py --topic volume-profile [--out vp.mp4] [--stills DIR]
  python3 make_explainer.py --list
Then: python3 drt/audio/add_audio.py vp.mp4 -o vp-music.mp4 --music NAME --sheet sheet.png  (needs AUDIO QA: PASS)

Adding a topic: write a function that returns a list of Scene objects and register it in TOPICS. Reuse Chart
(real bars from data/*.csv: time_et,open,high,low,close,volume) and the drawing layers below. Keep the hook on
screen from frame 0 with the chart already moving, 45-75 s total, navy/teal palette unless the week's palette changes.
Bars: Yahoo ES=F 1m JSON (query1.finance.yahoo.com/v8/finance/chart/ES=F?interval=1m&range=7d), NY session only,
saved to data/ so the render is reproducible after Yahoo drops the bars.
"""
import argparse, csv, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_FONTS = {}
def font(p, s):
    if (p, s) not in _FONTS: _FONTS[(p, s)] = ImageFont.truetype(p, s)
    return _FONTS[(p, s)]

# Reset-week palette (navy/teal), same values as posts/media/2026-11-18-daily/make_reels.py
NAVY = dict(bg_top=(12, 30, 58), bg_bot=(6, 18, 38), grid=(24, 46, 78), text=(236, 244, 250), muted=(150, 178, 200),
            accent=(46, 196, 182), up=(46, 196, 182), down=(236, 98, 110), panel=(8, 22, 44, 215),
            heavy=(46, 196, 182), thin=(236, 98, 110), poc=(255, 206, 92), prof=(120, 160, 200))

# chart area (TikTok side icons sit right of x~960, captions low on the screen: keep content inside)
CX0, CX1, CY0, CY1 = 70, 930, 830, 1640


# ---------------------------------------------------------------- data
class Chart:
    def __init__(self, path, tf=5, bin_pts=1.0):
        self.m = []  # 1m bars: (time, o, h, l, c, v)
        with open(path) as f:
            for r in csv.DictReader(f):
                self.m.append((r["time_et"], float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["volume"])))
        self.tf, self.bin = tf, bin_pts
        self.lo = min(b[3] for b in self.m); self.hi = max(b[2] for b in self.m)
        pad = (self.hi - self.lo) * 0.04
        self.plo, self.phi = self.lo - pad, self.hi + pad
        self.n = len(self.m); self.nc = (self.n + tf - 1) // tf
        self.edges = np.arange(np.floor(self.lo / bin_pts) * bin_pts, self.hi + bin_pts, bin_pts)
        # per-minute volume spread evenly over each bar's ticks, cumulative so a partial profile is a lookup
        per = np.zeros((self.n, len(self.edges)))
        for i, (_, o, h, l, c, v) in enumerate(self.m):
            ticks = np.arange(l, h + 0.001, 0.25); idx = ((ticks - self.edges[0]) // bin_pts).astype(int)
            np.add.at(per[i], idx, v / len(ticks))
        self.cum = np.cumsum(per, axis=0)
        self.full = self.cum[-1]; self.vmax = self.full.max()
        self.poc = self.edges[self.full.argmax()] + bin_pts / 2

    def y(self, p): return CY1 - (p - self.plo) / (self.phi - self.plo) * (CY1 - CY0)
    def x(self, i): return CX0 + (i + 0.5) * (CX1 - CX0) / self.nc
    def idx(self, hhmm):
        for i, b in enumerate(self.m):
            if b[0].endswith(hhmm): return i
        raise KeyError(hhmm)

    def candles(self, minutes):
        """Display candles from the first `minutes` 1m bars (the last one partial, built from its real minutes)."""
        out, k = [], int(minutes)
        for s in range(0, k, self.tf):
            g = self.m[s:min(s + self.tf, k)]
            out.append((g[0][1], max(b[2] for b in g), min(b[3] for b in g), g[-1][4]))
        return out

    def profile(self, minutes):
        k = int(np.clip(minutes, 0, self.n))
        return np.zeros(len(self.edges)) if k == 0 else self.cum[k - 1]

    def zone(self, lo_frac, start_price, below):
        """Contiguous bins around start_price where the smoothed profile is >= (or < when below) lo_frac * max."""
        sm = np.convolve(self.full, np.ones(3) / 3, mode="same"); thr = lo_frac * sm.max()
        i = int((start_price - self.edges[0]) // self.bin); ok = (lambda j: sm[j] < thr) if below else (lambda j: sm[j] >= thr)
        a = b = i
        while a - 1 >= 0 and ok(a - 1): a -= 1
        while b + 1 < len(sm) and ok(b + 1): b += 1
        return self.edges[a], self.edges[b] + self.bin


# ---------------------------------------------------------------- drawing
def background(P):
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(P["bg_top"]), np.array(P["bg_bot"])
    arr = (top[None, :] * (1 - y) + bot[None, :] * y).astype(np.uint8)[:, None, :].repeat(W, axis=1)
    im = Image.fromarray(np.ascontiguousarray(arr)); d = ImageDraw.Draw(im)
    for x in range(CX0, CX1 + 1, 86): d.line([x, CY0 - 20, x, CY1 + 10], fill=P["grid"], width=1)
    for yy in range(CY0 - 20, CY1 + 11, 82): d.line([CX0, yy, CX1, yy], fill=P["grid"], width=1)
    return im

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_panel(im, P, label, head, sub=None, reveal=1.0, hs=70, ls=40, ss=46):
    """Panel sized for the full text; words appear in order as `reveal` goes 0 -> 1 (builds on screen)."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    fh, fl, fs = font(B, hs), font(B, ls), font(R, ss)
    hl = wrap(d, head, fh, W - 230); sl = wrap(d, sub, fs, W - 230) if sub else []
    h = 60 + (int(ls * 1.9) if label else 0) + len(hl) * int(hs * 1.24) + (24 + len(sl) * int(ss * 1.32) if sl else 0) + 36
    y0 = 190
    d.rounded_rectangle([70, y0, W - 70, y0 + h], radius=28, fill=P["panel"])
    d.rectangle([70, y0 + 28, 82, y0 + h - 28], fill=P["accent"])
    total = sum(len(l.split()) for l in hl + sl); shown = int(np.ceil(reveal * total)) if reveal < 1 else total
    y = y0 + 46
    if label: d.text((120, y), label, font=fl, fill=P["accent"]); y += int(ls * 1.9)
    def put(lines, f, col, y, step, shown):
        for ln in lines:
            ws = ln.split(); k = max(0, min(len(ws), shown)); shown -= len(ws)
            if k: d.text((120, y), " ".join(ws[:k]), font=f, fill=col)
            y += step
        return y, shown
    y, shown = put(hl, fh, P["text"], y, int(hs * 1.24), shown)
    if sl: put(sl, fs, P["muted"], y + 24, int(ss * 1.32), shown)
    im.alpha_composite(ov)

def handle(d, P):
    f = font(B, 34); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 196), t, font=f, fill=P["muted"])

def chip(d, P, text):
    f = font(B, 30); w = d.textlength(text, font=f)
    d.rounded_rectangle([CX0, CY0 - 74, CX0 + w + 36, CY0 - 26], radius=14, fill=(16, 40, 72))
    d.text((CX0 + 18, CY0 - 68), text, font=f, fill=P["muted"])

def draw_bands(ov, C, P, bands):
    d = ImageDraw.Draw(ov)
    for lo, hi, col, a, label in bands:
        if a <= 0: continue
        y0, y1 = C.y(hi), C.y(lo)
        d.rectangle([CX0, y0, CX1, y1], fill=col + (int(60 * a),))
        d.line([CX0, y0, CX1, y0], fill=col + (int(200 * a),), width=2); d.line([CX0, y1, CX1, y1], fill=col + (int(200 * a),), width=2)
        if label:
            f = font(B, 30); tw = d.textlength(label, font=f); lx = CX1 - 14 - tw
            d.rounded_rectangle([lx - 10, y0 + 4, CX1 - 4, y0 + 46], radius=8, fill=(8, 22, 44, int(230 * a)))
            d.text((lx, y0 + 8), label, font=f, fill=col + (int(255 * a),))

def draw_profile(ov, C, P, vol, grow=1.0, heavy=None, thin=None, poc_a=0.0, alpha=1.0, maxw=330):
    d = ImageDraw.Draw(ov)
    if vol.max() <= 0 or alpha <= 0: return
    pocp = C.poc
    for j, v in enumerate(vol):
        if v <= 0: continue
        lo = C.edges[j]; mid = lo + C.bin / 2; w = v / C.vmax * maxw * grow
        col, a = P["prof"], 120
        if heavy and heavy[0] <= mid < heavy[1]: col, a = P["heavy"], int(120 + 100 * heavy[2])
        if thin and thin[0] <= mid < thin[1]: col, a = P["thin"], int(120 + 100 * thin[2])
        if poc_a > 0 and abs(mid - pocp) < C.bin / 2: col, a = P["poc"], int(120 + 135 * poc_a)
        y0, y1 = C.y(lo + C.bin), C.y(lo)
        d.rectangle([CX0, y0 + 1, CX0 + w, y1 - 1], fill=col + (int(a * alpha),))

def draw_candles(d, C, P, cs, hi_set=None, dim_after=None):
    bw = max(3, int((CX1 - CX0) / C.nc * 0.62))
    for i, (o, h, l, c) in enumerate(cs):
        col = P["up"] if c >= o else P["down"]
        if (hi_set is not None and i not in hi_set) or (dim_after is not None and i > dim_after):
            col = tuple(int(v * 0.35 + 20) for v in col)
        x = C.x(i); d.line([x, C.y(h), x, C.y(l)], fill=col, width=2)
        t, b = sorted([C.y(o), C.y(c)]); d.rectangle([x - bw / 2, t, x + bw / 2, max(b, t + 2)], fill=col)

def tag(d, P, xy, text, col, size=40):
    f = font(B, size); w = d.textlength(text, font=f); x, y = xy
    d.rounded_rectangle([x, y, x + w + 36, y + size + 26], radius=14, fill=(8, 22, 44), outline=col, width=3)
    d.text((x + 18, y + 11), text, font=f, fill=col)

def ease(t): t = float(np.clip(t, 0, 1)); return t * t * (3 - 2 * t)


class Scene:
    """dur seconds; text; state(t) -> dict for the frame (t = 0..1 inside the scene)."""
    def __init__(self, dur, label, head, sub=None, state=None, reveal=True):
        self.dur, self.label, self.head, self.sub, self.state, self.reveal = dur, label, head, sub, state or (lambda t: {}), reveal


def frames(C, P, scenes, chip_text):
    base = background(P); d0 = ImageDraw.Draw(base); chip(d0, P, chip_text)
    for sc in scenes:
        n = int(round(sc.dur * FPS))
        for k in range(n):
            t = k / max(1, n - 1); s = sc.state(t)
            im = base.copy().convert("RGBA")
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_bands(ov, C, P, s.get("bands", []))
            if s.get("prof_min", 0) > 0:
                draw_profile(ov, C, P, C.profile(s["prof_min"]), s.get("grow", 1.0), s.get("heavy"), s.get("thin"),
                             s.get("poc_a", 0.0), s.get("prof_alpha", 1.0))
            im.alpha_composite(ov); d = ImageDraw.Draw(im)
            if s.get("cursor") is not None:
                x = C.x(s["cursor"] / C.tf); d.line([x, CY0 - 10, x, CY1], fill=P["muted"], width=2)
            draw_candles(d, C, P, C.candles(s.get("minutes", C.n)), s.get("hi_set"),
                         None if s.get("cursor") is None else s["cursor"] / C.tf)
            if s.get("poc_a", 0) > 0:
                y = C.y(C.poc); a = s["poc_a"]
                for x in range(CX0, int(CX0 + (CX1 - CX0) * a), 30): d.line([x, y, x + 18, y], fill=P["poc"], width=4)
            for tg in s.get("tags", []): tag(d, P, *tg)
            rv = 1.0 if not sc.reveal else min(1.0, t * sc.dur / 0.9)  # words in over ~0.9 s
            text_panel(im, P, sc.label, sc.head, sc.sub, rv)
            handle(ImageDraw.Draw(im), P)
            yield np.asarray(im.convert("RGB"))


def render(out, gen):
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "21", "-an",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = 0
    for f in gen: p.stdin.write(f.tobytes()); n += 1
    p.stdin.close(); p.wait(); return n


# ---------------------------------------------------------------- topics
def topic_volume_profile():
    """Volume profile on ES: fast through thin, slow at heavy. Real NY session, Tue 11/17 (date not shown)."""
    C = Chart(os.path.join(HERE, "data", "es_1m_2026-11-17_ny.csv"), tf=5, bin_pts=1.0)
    P = NAVY
    heavy = C.zone(0.55, C.poc, below=False)                  # shelf around the POC
    thin = C.zone(0.15, 7392, below=True)                     # the gap between the opening shelf and the heavy shelf
    a, b = C.idx("10:30"), C.idx("10:43")
    drop_pts, drop_min = C.m[a][4] - C.m[b][4], b - a
    thin_closes = sum(1 for x in C.m if thin[0] <= x[4] < thin[1])
    heavy_closes = sum(1 for x in C.m if heavy[0] <= x[4] < heavy[1])
    print(f"POC {C.poc}  heavy {heavy}  thin {thin}  drop {drop_pts} pts / {drop_min} min  "
          f"thin closes {thin_closes}  heavy closes {heavy_closes}/{C.n}", file=sys.stderr)
    assert (drop_pts, drop_min) == (60.0, 13), "on-screen numbers no longer match the bars"
    drop_set = set(range(a // C.tf, b // C.tf + 1))
    chop_set = {i for i in range(C.idx("11:00") // C.tf, C.nc)}
    hb = lambda al: (heavy[0], heavy[1], P["heavy"], al, f"HEAVY {heavy[0]:.0f}-{heavy[1]:.0f}")
    tb = lambda al: (thin[0], thin[1], P["thin"], al, f"THIN {thin[0]:.0f}-{thin[1]:.0f}")
    full = dict(minutes=C.n, prof_min=C.n)
    pocp = f"{C.poc - C.bin / 2:.0f}"
    dx = C.x(b // C.tf) + 30
    S = []
    # 1 hook: on screen at frame 0 while the drop prints
    S.append(Scene(4.6, None, f"ES fell {drop_pts:.0f} points in {drop_min} minutes. Then it stalled for hours.",
                   "Here's what the volume was saying.", reveal=False,
                   state=lambda t: dict(minutes=48 + (C.idx("10:46") - 48) * t)))
    # 2 rest of the session prints
    S.append(Scene(6.0, "ONE REAL SESSION", "New York session on ES, 5-minute candles.",
                   "Watch where price raced and where it went sideways.",
                   state=lambda t: dict(minutes=C.idx("10:46") + (C.n - C.idx("10:46")) * ease(t / 0.85))))
    # 3 profile builds as a cursor replays the day
    S.append(Scene(7.5, "THE PROFILE", "Now count the contracts traded at every price.",
                   "Each bar on the left is one price. Longer bar, more volume.",
                   state=lambda t: dict(minutes=C.n, prof_min=1 + (C.n - 1) * ease(t / 0.85), cursor=(C.n - 1) * ease(t / 0.85))))
    # 4 heavy
    S.append(Scene(6.5, "HEAVY", "Long bars: heavy volume.", "Buyers and sellers both traded here, so price slowed down.",
                   state=lambda t: dict(full, heavy=(heavy[0], heavy[1], ease(t / 0.4)), bands=[hb(ease(t / 0.4))])))
    # 5 POC
    S.append(Scene(5.5, "POC", "The longest bar is the point of control.", f"The busiest price of that day: {pocp}.",
                   state=lambda t: dict(full, heavy=(heavy[0], heavy[1], 0.5), bands=[hb(0.5)], poc_a=ease(t / 0.5))))
    # 6 thin
    S.append(Scene(6.5, "THIN", "Short bars: thin volume.", "Few contracts changed hands. One side was in control.",
                   state=lambda t: dict(full, heavy=(heavy[0], heavy[1], 0.3), thin=(thin[0], thin[1], ease(t / 0.4)),
                                        bands=[hb(0.3), tb(ease(t / 0.4))], poc_a=0.6)))
    # 7 fast through thin
    S.append(Scene(7.5, "FAST THROUGH THIN", f"{drop_pts:.0f} points in {drop_min} minutes.",
                   f"Only {thin_closes} one-minute closes inside the thin zone all day.",
                   state=lambda t: dict(full, prof_alpha=0.45, thin=(thin[0], thin[1], 1.0), bands=[tb(1.0)], hi_set=drop_set,
                                        tags=[((dx, C.y(thin[0]) + 24), f"{drop_pts:.0f} pts / {drop_min} min", P["thin"])] if t > 0.15 else [])))
    # 8 slow at heavy
    S.append(Scene(7.0, "SLOW AT HEAVY", "Then the rest of the day chopped.",
                   f"{heavy_closes} of {C.n} minutes closed inside the heavy zone.",
                   state=lambda t: dict(full, prof_alpha=0.45, heavy=(heavy[0], heavy[1], 1.0), bands=[hb(1.0)], hi_set=chop_set,
                                        poc_a=0.6, tags=[((560, C.y(heavy[1]) - 150), f"{heavy_closes} of {C.n} min", P["heavy"])] if t > 0.15 else [])))
    # 9 map
    S.append(Scene(6.0, "THE MAP", "Next session, mark these zones before you trade.",
                   "Thin areas can move fast. Heavy areas can chop.",
                   state=lambda t: dict(full, heavy=(heavy[0], heavy[1], 0.6), thin=(thin[0], thin[1], 0.6),
                                        bands=[hb(0.6), tb(0.6)], poc_a=0.6)))
    # 10 risk
    S.append(Scene(6.5, "THE RISK", "A level helps you plan. It doesn't replace the stop.",
                   "Decide the stop before you enter. Mine is 3.5-4 points from entry.",
                   state=lambda t: dict(full, prof_alpha=0.5, bands=[hb(0.35), tb(0.35)])))
    # 11 close
    S.append(Scene(4.2, None, "Fast through thin. Slow at heavy.", "Define your risk. Wait for your setup.",
                   state=lambda t: dict(full, heavy=(heavy[0], heavy[1], 0.6), thin=(thin[0], thin[1], 0.6),
                                        bands=[hb(0.6), tb(0.6)], poc_a=0.6)))
    return C, P, S, "ES  ·  5m  ·  NY session"


TOPICS = {"volume-profile": topic_volume_profile}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topic", default="volume-profile"); ap.add_argument("--out"); ap.add_argument("--stills")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{k}: {v.__doc__}" for k, v in TOPICS.items())); return
    C, P, S, chip_text = TOPICS[a.topic]()
    out = a.out or f"{a.topic}.mp4"
    n = render(out, frames(C, P, S, chip_text))
    print(f"{out}: {n} frames, {n / FPS:.1f} s")
    if a.stills:  # frame 0 plus the middle of every scene
        os.makedirs(a.stills, exist_ok=True); t0 = 0.0
        marks = [0.0] + [None] * 0
        for sc in S: marks.append(t0 + sc.dur * 0.7); t0 += sc.dur
        for i, m in enumerate(marks):
            subprocess.run([FF, "-y", "-loglevel", "error", "-ss", f"{m:.2f}", "-i", out, "-frames:v", "1",
                            os.path.join(a.stills, f"{a.topic}_{i:02d}.png")], check=True)


if __name__ == "__main__":
    main()
