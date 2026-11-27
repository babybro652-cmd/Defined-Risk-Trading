import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
FF = "/usr/bin/ffmpeg"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = dict(bg_top=(12, 30, 58), bg_bot=(6, 18, 38), grid=(28, 52, 86), text=(236, 244, 250), muted=(150, 178, 200),
            accent=(46, 196, 182), up=(46, 196, 182), down=(236, 98, 110), panel=(8, 22, 44, 200))
LIGHT = dict(bg_top=(246, 248, 251), bg_bot=(226, 233, 242), grid=(205, 215, 228), text=(14, 32, 64), muted=(84, 104, 134),
             accent=(28, 92, 196), up=(22, 150, 110), down=(210, 70, 70), panel=(255, 255, 255, 215))

def font(p, s): return ImageFont.truetype(p, s)

def background(P):
    y = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(P["bg_top"]), np.array(P["bg_bot"])
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:] = (top[None, :] * (1 - y) + bot[None, :] * y).astype(np.uint8)[:, None, :]
    im = Image.fromarray(arr); d = ImageDraw.Draw(im)
    for x in range(60, W, 90): d.line([x, 820, x, 1640], fill=P["grid"], width=1)
    for yy in range(820, 1641, 82): d.line([60, yy, W - 60, yy], fill=P["grid"], width=1)
    return im

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_panel(im, P, label, head, sub=None, hs=74, ls=40):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    fh, fl, fs = font(B, hs), font(B, ls), font(R, 50)
    lines = wrap(d, head, fh, W - 220); sl = wrap(d, sub, fs, W - 220) if sub else []
    h = 70 + (int(ls * 2) if label else 0) + len(lines) * int(hs * 1.25) + (30 + len(sl) * 66 if sl else 0) + 40
    y0 = 200
    d.rounded_rectangle([70, y0, W - 70, y0 + h], radius=28, fill=P["panel"])
    d.rectangle([70, y0 + 28, 82, y0 + h - 28], fill=P["accent"])  # side accent bar
    y = y0 + 50
    if label: d.text((120, y), label, font=fl, fill=P["accent"]); y += int(ls * 2)
    for ln in lines: d.text((120, y), ln, font=fh, fill=P["text"]); y += int(hs * 1.25)
    if sl:
        y += 30
        for ln in sl: d.text((120, y), ln, font=fs, fill=P["muted"]); y += 66
    im.paste(ov, (0, 0), ov)

def handle(d, P):
    f = font(B, 36); t = "@definedrisktrading"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 190), t, font=f, fill=P["muted"])

def dashed(d, y, label, col, x0=60, x1=W - 60):
    for x in range(x0, x1, 40): d.line([x, y, x + 22, y], fill=col, width=4)
    f = font(B, 32); d.text((x1 - d.textlength(label, font=f), y + 12), label, font=f, fill=col)

def draw_candles(d, P, seq, prog, y_mid, unit, x0=110, cw=44, gap=22):
    """seq: (o,h,l,c) in units (positive = up). prog: candles shown, fractional = the current one printing."""
    n_full = int(prog); frac = prog - n_full
    for i, (o, h, l, c) in enumerate(seq):
        if i > n_full or (i == n_full and frac <= 0): break
        if i == n_full:  # printing: close walks from open toward close, wick grows with it
            cc = o + (c - o) * frac
            hh = max(o, cc) + (h - max(o, c)) * frac; ll = min(o, cc) - (min(o, c) - l) * frac
            o2, h2, l2, c2 = o, hh, ll, cc
        else: o2, h2, l2, c2 = o, h, l, c
        col = P["up"] if c2 >= o2 else P["down"]; x = x0 + i * (cw + gap); cx = x + cw // 2
        Y = lambda v: int(y_mid - v * unit)
        d.line([cx, Y(h2), cx, Y(l2)], fill=col, width=5)
        t, b = sorted([Y(o2), Y(c2)]); d.rectangle([x, t, x + cw, max(b, t + 4)], fill=col)

def walk(n, seed, start=0.0, drift=0.0):
    rng = np.random.default_rng(seed); out, p = [], start
    for _ in range(n):
        c = p + drift + rng.normal(0, 1.0); h = max(p, c) + abs(rng.normal(0, 0.45)); l = min(p, c) - abs(rng.normal(0, 0.45))
        out.append((p, h, l, c)); p = c
    return out

def scene(P, dur, seq, label, head, sub=None, line=None, start=4.0, tag=None, y_mid=1230, unit=55, hs=74, ls=40):
    """Frames for one scene: chart keeps printing (starts with `start` candles, already moving at frame 0)."""
    n = int(dur * FPS); end = len(seq)
    base = background(P)
    for k in range(n):
        prog = min(end, start + (end - start) * min(1.0, k / (n * 0.8)) + 0.35)
        im = base.copy(); d = ImageDraw.Draw(im)
        if line: dashed(d, int(y_mid - line[0] * unit), line[1], P["accent"])
        draw_candles(d, P, seq, prog, y_mid, unit)
        if tag and prog >= end - 0.05:
            f = font(B, 46)
            for i, ln in enumerate(tag[0].split("|")): d.text((110, 1680 + i * 58 - 120), ln, font=f, fill=tag[1](P))
        text_panel(im, P, label, head, sub, hs, ls)
        handle(ImageDraw.Draw(im), P)
        yield np.asarray(im)

def render(name, scenes):
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-an",
                          "-movflags", "+faststart", name], stdin=subprocess.PIPE)
    for fr in scenes:
        for f in fr: p.stdin.write(f.tobytes())  # scenes are generators: streamed, not held in memory
    p.stdin.close(); p.wait()

