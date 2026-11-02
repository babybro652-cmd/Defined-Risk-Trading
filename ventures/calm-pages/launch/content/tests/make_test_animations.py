#!/usr/bin/env python3
"""Two TEST reels for Peace by Page built from the real journal PDFs (no AI imagery).

  python3 make_test_animations.py coloring   -> coloring-test.mp4 (+ sheets)
  python3 make_test_animations.py pageflip   -> pageflip-test.mp4 (+ sheets)
  python3 make_test_animations.py all

Coloring: Calm Petals coloring pack page 1 ("Botanical mandala") rendered from the Letter PDF,
regions found by connected-component labeling and filled one by one with a colored-pencil
texture, a drawn pencil following the fill, paper grain, slow camera drift.
Page flip: Calm Wings journal pages (Day 1, Mood Butterfly Tracker January, Box breathing,
Butterfly mandala) on a desk, turned with a 3D page-curl model (perspective, shading, cast shadow).
Audio: music bed from drt/audio/add_audio.py (CC0 library), foley synthesized here with numpy
(pencil scratch = band-passed noise strokes + grain clicks, page turn = rustle + whoosh + soft slap).
No third-party samples. See LICENSES.md in this folder.
"""
import json, math, os, re, subprocess, sys, tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as nd
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../../.."))
ED = os.path.join(REPO, "ventures/calm-pages/editions")
ADD_AUDIO = os.path.join(REPO, "drt/audio/add_audio.py")
W, H, FPS, SR = 1080, 1920, 30, 48000
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TMP = tempfile.mkdtemp(prefix="pbp_test_")


def render_pdf_page(pdf, page, dpi):
    base = os.path.join(TMP, "p%d_%d" % (page, dpi) + os.path.basename(pdf)[:10])
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(page), "-l", str(page), "-singlefile", pdf, base], check=True)
    return np.asarray(Image.open(base + ".png").convert("RGB")).astype(np.float32) / 255.0


def smooth_noise(shape, sigma, seed):
    r = np.random.default_rng(seed).standard_normal(shape).astype(np.float32)
    r = nd.gaussian_filter(r, sigma)
    return r / (r.std() + 1e-6)


def paper_grain(shape, seed=1):
    g = 0.6 * smooth_noise(shape, 0.8, seed) + 0.4 * smooth_noise(shape, 3, seed + 1)
    return g.astype(np.float32)


def desk_texture(seed=3):
    """Light oak-like desk: stretched noise grain plus warm base."""
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((H // 4, W // 4)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
    n = nd.gaussian_filter(n, (1.5, 30))
    n = (n - n.min()) / (n.max() - n.min())
    stripes = 0.5 + 0.5 * np.sin(np.linspace(0, 60, W)[None, :] + 6 * n)
    base = np.array([0.80, 0.70, 0.58], np.float32)
    t = (0.85 + 0.08 * stripes + 0.07 * n)[..., None]
    img = base * t
    img += 0.012 * np.random.default_rng(seed + 1).standard_normal((H, W, 1)).astype(np.float32)
    return np.clip(img, 0, 1)


def light_falloff():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xx - W * 0.35) / W, (yy - H * 0.3) / H)
    v = 1.04 - 0.22 * d ** 1.6
    warm = np.stack([v * 1.0, v * 0.985, v * 0.955], -1)
    return warm.astype(np.float32)


def hook_layer(text, y=150, size=64, sub=None):
    """RGBA overlay with a soft white card and serif italic text."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) > W - 200 and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    lines.append(cur)
    lh = int(size * 1.22)
    bh = lh * len(lines) + 60
    bw = int(max(d.textlength(l, font=f) for l in lines)) + 90
    x0 = (W - bw) // 2
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([x0, y, x0 + bw, y + bh], 34, fill=(255, 252, 247, 225))
    shadow = card.filter(ImageFilter.GaussianBlur(14))
    sh = np.asarray(shadow).copy(); sh[..., :3] = 40; sh[..., 3] = (sh[..., 3] * 0.25).astype(np.uint8)
    im = Image.alpha_composite(Image.fromarray(sh), card)
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, y + 28 + i * lh), l, font=f, fill=(62, 74, 66, 255))
    if sub:
        fs = ImageFont.truetype(FONT_SANS, 26)
        tw = d.textlength(sub, font=fs)
        d.text(((W - tw) / 2, H - 120), sub, font=fs, fill=(255, 255, 255, 200))
    a = np.asarray(im).astype(np.float32) / 255.0
    return a[..., :3], a[..., 3:4]


def drift_matrix(t, dur, amp=10, zoom=0.012, seed=0):
    """Loopable slow camera drift (periodic over dur)."""
    p = 2 * math.pi * t / dur
    tx = amp * math.sin(p + seed) + 3 * math.sin(3 * p + 1.3)
    ty = amp * 0.7 * math.sin(p * 2 + 0.7 + seed) + 2 * math.sin(5 * p)
    s = 1.03 + zoom * math.sin(p + 0.4)
    ang = 0.25 * math.sin(p + 2.0)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, s)
    M[0, 2] += tx; M[1, 2] += ty
    return M


class Writer:
    def __init__(self, path):
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                   "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)

    def add(self, f):
        self.p.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()


# ----------------------------------------------------------------- audio (numpy foley)

def bandpass(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lowpass(x, f, order=4):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def pencil_track(active, stroke_hz, seed=11):
    """active: per-video-frame bool (pencil touching paper). Strokes back and forth at stroke_hz."""
    rng = np.random.default_rng(seed)
    n = int(len(active) / FPS * SR)
    t = np.arange(n) / SR
    act = np.repeat(np.asarray(active, np.float32), SR // FPS)[:n]
    act = np.pad(act, (0, n - len(act)))
    act = nd.gaussian_filter1d(act, SR * 0.012)
    # stroke envelope: each half cycle is one stroke; louder mid-stroke, quiet at turnarounds
    jitter = np.cumsum(rng.normal(0, 0.004, n))
    ph = 2 * math.pi * stroke_hz * t + jitter
    stroke = np.abs(np.sin(ph)) ** 0.7
    stroke_gain = 0.75 + 0.25 * nd.gaussian_filter1d(rng.standard_normal(n), SR * 0.08) / 0.05
    stroke_gain = np.clip(stroke_gain, 0.4, 1.2)
    white = rng.standard_normal(n)
    hiss = bandpass(white, 1800, 7500) * 0.8 + bandpass(white, 600, 1800) * 0.35
    # paper tooth: sparse grain clicks
    clicks = (rng.random(n) < 0.012).astype(np.float64) * rng.normal(0, 1, n)
    clicks = bandpass(clicks, 2500, 9000) * 2.2
    # speed-dependent brightness: brighter mid-stroke
    sig = hiss * (0.6 + 0.4 * stroke) + clicks * stroke
    sig *= stroke * stroke_gain * act
    return sig.astype(np.float32)


def page_turn(seed, dur=1.1):
    """One page turn: lift crinkle, airy whoosh, soft slap on landing."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    white = rng.standard_normal(n)
    # lift / bend crinkle (0 to 0.35 s): bursts of band noise
    crink_env = np.exp(-((t - 0.12) / 0.11) ** 2)
    crinkle = bandpass(white, 1200, 6500) * crink_env
    crackle = (rng.random(n) < 0.03) * rng.normal(0, 1, n)
    crackle = bandpass(crackle, 2000, 8000) * np.exp(-((t - 0.15) / 0.12) ** 2) * 2.5
    # whoosh (0.2 to 0.8 s): low-passed noise swell
    wh_env = np.exp(-((t - 0.5) / 0.18) ** 2)
    whoosh = bandpass(white, 150, 1400) * wh_env * 0.9
    # landing slap (~0.85 s): short broadband transient + low thump
    land = 0.86
    slap_env = np.where(t >= land, np.exp(-(t - land) / 0.018), 0)
    slap = bandpass(rng.standard_normal(n), 400, 5000) * slap_env * 1.4
    thump = lowpass(rng.standard_normal(n), 220) * np.where(t >= land, np.exp(-(t - land) / 0.04), 0) * 2.0
    s = crinkle * 0.7 + crackle * 0.6 + whoosh + slap + thump
    return (s / (np.abs(s).max() + 1e-9)).astype(np.float32)


def room_tone(n, seed=5):
    r = np.random.default_rng(seed).standard_normal(n)
    return (lowpass(r, 400) * 0.02 + bandpass(r, 400, 3000) * 0.004).astype(np.float32)


def write_wav(path, x):
    x = np.asarray(x, np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                   input=x.astype(np.float32).tobytes(), check=True)


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


def finish_audio(silent_mp4, foley, out_mp4, music_name, music_db_under=9.0, target=-23.0):
    """Music bed via drt/audio/add_audio.py (CC0 library, its own QA), then foley on top."""
    bed_mp4 = os.path.join(TMP, "bed.mp4")
    r = subprocess.run([sys.executable, ADD_AUDIO, silent_mp4, "-o", bed_mp4, "--music", music_name, "--target", "-18"],
                       capture_output=True, text=True)
    print(r.stdout[-600:])
    if r.returncode != 0:
        sys.exit("add_audio.py failed:\n" + r.stderr[-1500:])
    music = decode(bed_mp4)
    n = len(music)
    fol = np.zeros((n, 2), np.float32)
    fol[: min(n, len(foley))] = foley[:n]
    fol = fol + room_tone(n)[:, None]
    # loudness relationship: foley leads, music sits music_db_under below it (measured where foley is active)
    act = np.abs(nd.uniform_filter1d(fol[:, 0] ** 2, SR // 10)) > 1e-5
    f_db = rms_db(fol[act]) if act.any() else rms_db(fol)
    m_db = rms_db(music)
    music *= 10 ** ((f_db - music_db_under - m_db) / 20)
    mix = fol + music
    raw = os.path.join(TMP, "mix.wav"); write_wav(raw, mix)
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=%s:TP=-2.0:LRA=11:print_format=json" % target,
                         "-f", "null", "-"], capture_output=True).stderr.decode(errors="ignore")
    js = json.loads(p1[p1.rfind("{"): p1.rfind("}") + 1])
    ln = ("loudnorm=I=%s:TP=-2.0:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
          % (target, js["input_i"], js["input_tp"], js["input_lra"], js["input_thresh"], js["target_offset"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent_mp4, "-i", raw, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-af", ln + ",aresample=48000", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", out_mp4], check=True)
    return {"music": music_name, "foley_rms_db_active": round(float(f_db), 1),
            "music_rms_db_after_gain": round(float(rms_db(music)), 1), "music_under_foley_db": music_db_under}


def qa(out_mp4, sheet_png, audio_png, extra):
    rep = dict(extra)
    eb = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out_mp4, "-af", "ebur128=peak=true", "-f", "null", "-"],
                        capture_output=True).stderr.decode(errors="ignore")
    summ = eb[eb.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summ).group(1))
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", out_mp4],
                                      capture_output=True, text=True).stdout)
    v = [s for s in probe["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    dur = float(probe["format"]["duration"])
    od = decode(out_mp4)
    clipped = int(np.sum(np.abs(od) >= 0.999))
    # silence check: share of 100 ms windows below -50 dBFS
    win = SR // 10
    seg = od[: len(od) // win * win, 0].reshape(-1, win)
    quiet = float(np.mean(20 * np.log10(np.sqrt((seg ** 2).mean(1)) + 1e-12) < -50))
    checks = [
        ("9:16 1080x1920", v["width"] == W and v["height"] == H, "%sx%s" % (v["width"], v["height"])),
        ("7-12 s", 7 <= dur <= 12, "%.2f s" % dur),
        ("audio stream present", bool(a), a[0]["codec_name"] if a else "none"),
        ("loudness -23 +/-1.5 LUFS", abs(I + 23) <= 1.5, "%.1f LUFS" % I),
        ("true peak <= -1 dBTP, no clipping", tp <= -1.0 and clipped == 0, "%.1f dBTP, %d clipped" % (tp, clipped)),
        ("no dead air (<10%% quiet windows)", quiet < 0.10, "%.0f%% quiet" % (quiet * 100)),
    ]
    rep.update({"file": out_mp4, "duration_s": round(dur, 2), "integrated_lufs": I, "true_peak_dbtp": tp,
                "checks": [{"check": c, "pass": bool(p), "detail": d} for c, p, d in checks]})
    cols = 6
    nfr = 12
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out_mp4, "-vf",
                    "fps=%f,scale=240:-1,tile=%dx%d:padding=6:color=white" % (nfr / dur, cols, nfr // cols),
                    "-frames:v", "1", sheet_png], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out_mp4, "-filter_complex",
                    "[0:a]showspectrumpic=s=1200x400:legend=0:scale=log,format=rgb24[s];"
                    "[0:a]showwavespic=s=1200x200:split_channels=0:colors=0x3E4A42[w];[w][s]vstack",
                    "-frames:v", "1", audio_png], check=True)
    rep["contact_sheet"] = sheet_png
    rep["audio_sheet"] = audio_png
    ok = all(c["pass"] for c in rep["checks"])
    rep["qa"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=2))
    with open(os.path.splitext(out_mp4)[0] + "-qa.json", "w") as fh:
        json.dump(rep, fh, indent=2)
    return ok


# ----------------------------------------------------------------- 1. coloring time-lapse

PALETTE = [(0.95, 0.72, 0.75), (0.66, 0.78, 0.63), (0.97, 0.80, 0.64), (0.79, 0.72, 0.89),
           (0.96, 0.89, 0.62), (0.69, 0.81, 0.88), (0.91, 0.62, 0.66), (0.75, 0.88, 0.81)]


def make_coloring(out):
    DUR = 10.0
    NF = int(DUR * FPS)
    pdf = os.path.join(ED, "calm-petals/files/3-coloring-pack/CalmPetals_Botanical_Coloring_Pack_Letter.pdf")
    page = render_pdf_page(pdf, 4, 200)  # page 4 = "Botanical mandala", 1 of 18
    ph, pw = page.shape[:2]
    gray = page.mean(2)
    line = nd.binary_dilation(gray < 0.67, iterations=1)
    lab, n = nd.label(~line)
    idx = np.arange(1, n + 1)
    sizes = nd.sum(np.ones_like(gray), lab, idx)
    com = np.array(nd.center_of_mass(np.ones_like(gray), lab, idx))
    ys, xs = np.nonzero(line[300:1850])
    C = ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2 + 300)
    bg = idx[np.argmax(sizes)]
    regions = []
    for i, s in zip(idx, sizes):
        if i == bg or s < 400:
            continue
        cy, cx = com[i - 1]
        if not (300 < cy < 1850):
            continue
        r = math.hypot(cx - C[0], cy - C[1])
        ang = math.atan2(cy - C[1], cx - C[0])
        big = s > 60000
        regions.append(dict(id=i, size=s, r=r, ang=ang, big=big, key=(int(round(r / 30)), int(round(math.log(s) * 2.5)))))
    keys = sorted({g["key"] for g in regions if not g["big"]})
    rng = np.random.default_rng(4)
    color_of = {k: PALETTE[(j * 3) % len(PALETTE)] for j, k in enumerate(keys)}
    # order: center outward; within a ring go around by angle, starting at the top
    small = sorted([g for g in regions if not g["big"]], key=lambda g: (g["key"][0], g["key"][1], (g["ang"] + math.pi / 2) % (2 * math.pi)))
    bigs = sorted([g for g in regions if g["big"]], key=lambda g: g["r"])
    order = small + bigs
    for g in small:
        g["col"] = color_of[g["key"]]; g["alpha"] = 0.78
    wash = [(0.97, 0.93, 0.80), (0.90, 0.95, 0.89), (0.98, 0.90, 0.88), (0.92, 0.90, 0.97)]
    for j, g in enumerate(bigs):
        g["col"] = wash[j % len(wash)]; g["alpha"] = 0.55

    # timing: fill window 0 .. 9.2 s, time per region ~ size^0.5, lift gap between regions
    T0, T1 = 0.0, 9.2
    w = np.array([g["size"] ** 0.5 for g in order])
    gap = 0.03
    avail = (T1 - T0) - gap * len(order)
    dur = w / w.sum() * avail
    t = T0
    for g, d in zip(order, dur):
        g["t0"], g["t1"] = t, t + d
        t += d + gap

    # per-region fill coordinate: hatch direction 35 deg with ragged edge
    ragged = smooth_noise((ph, pw), 6, 9) * 0.04
    dirx, diry = math.cos(math.radians(35)), math.sin(math.radians(35))
    objs = nd.find_objects(lab)
    for g in order:
        sl = objs[g["id"] - 1]
        m = lab[sl] == g["id"]
        yy, xx = np.nonzero(m)
        proj = xx * dirx + yy * diry
        perp = -xx * diry + yy * dirx
        p = (proj - proj.min()) / (np.ptp(proj) + 1e-6)
        p = np.clip(p + ragged[sl][m], 0, 1)
        g.update(sl=sl, m=m, yy=yy + sl[0].start, xx=xx + sl[1].start, p=p, perp=perp, proj=proj)

    # colored pencil texture: grain + hatch lines
    grain = paper_grain((ph, pw), 21)
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    hatch = 0.5 + 0.5 * np.sin((xx * -diry + yy * dirx) * 0.9 + 2 * smooth_noise((ph, pw), 2, 31))
    tooth = np.clip(0.72 + 0.18 * grain + 0.14 * hatch, 0.35, 1.0).astype(np.float32)
    paper = np.clip(page * (1 + 0.025 * paper_grain((ph, pw), 2)[..., None]), 0, 1)
    paper = paper * np.array([1.0, 0.985, 0.96], np.float32)  # warm printer paper

    alpha = np.zeros((ph, pw), np.float32)
    colmap = np.ones((ph, pw, 3), np.float32)

    # page placement: page width 1200 in frame, slight rotation
    sc = 1200 / pw
    Mp = cv2.getRotationMatrix2D((pw / 2, ph / 2), -1.2, sc)
    Mp[0, 2] += W / 2 - pw / 2; Mp[1, 2] += H / 2 - ph / 2 + 10 - (C[1] - ph / 2) * sc + 30
    desk = desk_texture()
    light = light_falloff()
    hook_rgb, hook_a = hook_layer("Color one petal for every feeling", y=150, size=66)
    pencil_img = make_pencil()

    active = []
    frames0 = None
    wr = Writer(out)
    cur_tip = None
    for f in range(NF):
        tt = f / FPS
        tip = None
        for g in order:
            if g["t0"] > tt:
                break
            prog = min(1.0, (tt - g["t0"]) / (g["t1"] - g["t0"]))
            if g.get("done"):
                continue
            sel = g["p"] <= prog
            a_ = g["alpha"] * tooth[g["yy"][sel], g["xx"][sel]]
            alpha[g["yy"][sel], g["xx"][sel]] = a_
            colmap[g["yy"][sel], g["xx"][sel]] = g["col"]
            if prog >= 1.0:
                g["done"] = True
            else:
                # tip on the fill frontier, sweeping across it (hatching back and forth)
                fr = np.nonzero(np.abs(g["p"] - prog) < 0.04)[0]
                if len(fr):
                    pv = g["perp"][fr]
                    osc = 0.5 + 0.5 * math.sin(2 * math.pi * 5.0 * tt)
                    target = pv.min() + osc * np.ptp(pv)
                    k = fr[np.argmin(np.abs(pv - target))]
                    tip = (g["xx"][k], g["yy"][k], g["col"])
        active.append(tip is not None)
        a3 = alpha[..., None]
        pg = paper * (1 - a3 + a3 * colmap)
        # page shadow on desk + page composite
        frame = desk.copy()
        pa = cv2.warpAffine(np.ones((ph, pw), np.float32), Mp, (W, H), flags=cv2.INTER_LINEAR)
        sh = cv2.GaussianBlur(cv2.warpAffine(pa, np.float32([[1, 0, 10], [0, 1, 16]]), (W, H)), (0, 0), 14)
        frame *= (1 - 0.28 * sh)[..., None]
        pw_img = cv2.warpAffine(pg, Mp, (W, H), flags=cv2.INTER_AREA)
        frame = frame * (1 - pa[..., None]) + pw_img * pa[..., None]
        if tip is not None:
            cur_tip = tip
        if tip is not None or (cur_tip is not None and tt < T1):
            x, y, col = cur_tip
            fx = Mp[0, 0] * x + Mp[0, 1] * y + Mp[0, 2]
            fy = Mp[1, 0] * x + Mp[1, 1] * y + Mp[1, 2]
            if tip is None:  # lifted between regions: hover slightly
                fx += 6; fy -= 8
            frame = draw_pencil(frame, pencil_img, fx, fy, col, lifted=tip is None)
        frame *= light
        frame = cv2.warpAffine(frame, drift_matrix(tt, DUR, seed=0.5), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        frame = frame * (1 - hook_a) + hook_rgb * hook_a
        if f == 0:
            frames0 = frame.copy()
        # loop: last 0.5 s blend back toward the opening frame
        lf = NF - int(0.5 * FPS)
        if f >= lf:
            k = (f - lf + 1) / (NF - lf)
            frame = frame * (1 - k) + frames0 * k
        wr.add(frame)
    wr.close()
    return active


def make_pencil():
    """Colored pencil drawn top-down: hexagonal body, shaved wood cone, colored lead."""
    L, Wd = 1300, 46
    im = np.zeros((Wd + 40, L, 4), np.float32)  # pencil along +x, tip at x=0, centered at y=(Wd+40)/2
    return dict(L=L, Wd=Wd)


def draw_pencil(frame, pen, fx, fy, col, lifted=False):
    L, Wd = pen["L"], pen["Wd"]
    ux, uy = 0.60, 0.80  # from the tip toward the hand: pencil comes in from lower right
    nx, ny = -uy, ux
    cone = 110

    def P(s, o):
        return (fx + ux * s + nx * o, fy + uy * s + ny * o)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c255 = tuple(int(255 * c) for c in col)
    dark = tuple(int(255 * c * 0.72) for c in col)
    # body faces (3 visible hex faces as stripes)
    d.polygon([P(cone, -Wd / 2), P(L, -Wd / 2), P(L, -Wd / 6), P(cone, -Wd / 6)], fill=dark + (255,))
    d.polygon([P(cone, -Wd / 6), P(L, -Wd / 6), P(L, Wd / 6), P(cone, Wd / 6)], fill=c255 + (255,))
    d.polygon([P(cone, Wd / 6), P(L, Wd / 6), P(L, Wd / 2), P(cone, Wd / 2)],
              fill=tuple(min(255, int(v * 1.12) + 12) for v in c255) + (255,))
    # shaved wood cone, scalloped edge
    d.polygon([P(22, -7), P(cone, -Wd / 2), P(cone + 6, -Wd / 4), P(cone, 0), P(cone + 6, Wd / 4), P(cone, Wd / 2), P(22, 7)],
              fill=(226, 190, 146, 255))
    d.polygon([P(22, 0), P(cone, -Wd / 6), P(cone, Wd / 6)], fill=(236, 204, 162, 255))
    # lead
    d.polygon([P(0, 0), P(24, -7.5), P(24, 7.5)], fill=dark + (255,))
    a = np.asarray(ov).astype(np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3:4]
    # soft AO shading along the body edge and a slight blur (focus)
    rgb = cv2.GaussianBlur(rgb, (0, 0), 0.8)
    al = cv2.GaussianBlur(al, (0, 0), 0.8)[..., None]
    # shadow: offset more when lifted
    off = (26, 30) if not lifted else (40, 48)
    sh = cv2.warpAffine(al[..., 0], np.float32([[1, 0, off[0]], [0, 1, off[1]]]), (W, H))
    sh = cv2.GaussianBlur(sh, (0, 0), 16 if not lifted else 22)
    frame = frame * (1 - 0.32 * sh)[..., None]
    return frame * (1 - al) + rgb * al


# ----------------------------------------------------------------- 2. page flip

def make_pageflip(out):
    pages = [
        (os.path.join(ED, "calm-wings/files/1-journal/CalmWings_90Day_Journal_Letter.pdf"), 19),   # Day 1
        (os.path.join(ED, "calm-wings/files/5-mood-tracker/CalmWings_Mood_Butterfly_Tracker_Letter.pdf"), 4),  # January
        (os.path.join(ED, "calm-wings/files/1-journal/CalmWings_90Day_Journal_Letter.pdf"), 10),   # Box breathing
        (os.path.join(ED, "calm-wings/files/1-journal/CalmWings_90Day_Journal_Letter.pdf"), 16),   # Butterfly mandala
    ]
    tex = []
    for i, (pdf, p) in enumerate(pages):
        im = render_pdf_page(pdf, p, 150)
        im = np.clip(im * (1 + 0.02 * paper_grain(im.shape[:2], 40 + i)[..., None]), 0, 1) * np.array([1.0, 0.985, 0.962], np.float32)
        tex.append(im.astype(np.float32))
    th, tw = tex[0].shape[:2]
    # back of a single-sided print: blank paper with faint mirrored show-through
    backs = [np.clip(1 - (1 - t[:, ::-1]) * 0.06, 0, 1) * np.array([0.985, 0.97, 0.945], np.float32) for t in tex]

    PW = 960
    PH = int(PW * th / tw)
    spine = 92
    top = (H - PH) // 2 + 70
    D = 2600.0  # camera height in px
    cxc, cyc = W / 2, H / 2
    desk = desk_texture(seed=8)
    light = light_falloff()
    hook_rgb, hook_a = hook_layer("What's inside a 90-day anxiety journal", y=110, size=62)

    DUR = 9.6
    NF = int(DUR * FPS)
    flips = [0.15, 3.0, 5.85]
    FL = 1.15

    def place(img):
        """Flat page texture -> frame (on the table, z=0)."""
        M = np.float32([[PW / tw, 0, spine], [0, PH / th, top]])
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA)

    flat_alpha = place(np.ones((th, tw), np.float32))
    # left page (back of the page before Day 1), mostly off-frame
    left_alpha = cv2.warpAffine(np.ones((th, tw), np.float32), np.float32([[PW / tw, 0, spine - PW], [0, PH / th, top]]), (W, H))
    left_img = cv2.warpAffine(backs[0], np.float32([[PW / tw, 0, spine - PW], [0, PH / th, top]]), (W, H))
    # stack edges under the right page (a few sheets peeking out)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    def base_scene(right_idx, left_back_idx):
        fr = desk.copy()
        # stack shadow on desk
        st = np.zeros((H, W), np.float32)
        st[top - 6: top + PH + 10, spine - PW: spine + PW + 8] = 1
        st = cv2.GaussianBlur(st, (0, 0), 18)
        fr *= (1 - 0.30 * st)[..., None]
        # sheets below (slightly offset edges)
        for k, (dx, dy, sh) in enumerate([(5, 4, 0.90), (3, 2, 0.94)]):
            a = np.roll(np.roll(flat_alpha, dy, 0), dx, 1)
            fr = fr * (1 - a[..., None]) + np.array([0.93, 0.915, 0.89], np.float32) * sh * a[..., None]
        fr = fr * (1 - flat_alpha[..., None]) + place(tex[right_idx]) * flat_alpha[..., None]
        li = cv2.warpAffine(backs[left_back_idx], np.float32([[PW / tw, 0, spine - PW], [0, PH / th, top]]), (W, H))
        fr = fr * (1 - left_alpha[..., None]) + li * left_alpha[..., None]
        # gutter shading both sides of the spine
        g = np.exp(-np.abs(xx - spine) / 38.0)
        fr *= (1 - 0.28 * g)[..., None]
        return fr

    def curl_frame(fr, t_, front, back):
        """Render one turning page at progress t_ (0..1) over the scene fr."""
        e = 0.5 - 0.5 * math.cos(math.pi * t_)            # eased angle progress
        theta = math.pi * e
        bend = 1.1 * math.sin(2 * math.pi * e)  # outer edge leads while lifting, lags while landing
        S = np.linspace(0, PW, PW * 3)
        phi = np.clip(theta + bend * (S / PW) ** 1.3, 0, math.pi)
        ds = S[1] - S[0]
        X = spine + np.concatenate([[0], np.cumsum(np.cos(phi[:-1]) * ds)])
        Z = np.concatenate([[0], np.cumsum(np.sin(phi[:-1]) * ds)])
        Z = np.minimum(Z, D * 0.7)
        sig = D / (D - Z)
        xp = cxc + (X - cxc) * sig
        # cast shadow (light from upper left): the page footprint shifted right/down by height
        shadow_x = X + 0.42 * Z
        col = np.zeros(W, np.float32)
        hit = (shadow_x >= 0) & (shadow_x < W)
        np.maximum.at(col, shadow_x[hit].astype(int), 1.0)
        col = nd.maximum_filter1d(col, 4)
        shm = np.zeros((H, W), np.float32)
        y0, y1 = top + 20, top + PH + 20
        shm[y0:y1] = col[None, :]
        blur = 8 + 30 * math.sin(math.pi * e)
        shm = cv2.GaussianBlur(shm, (0, 0), blur)
        strength = 0.38 * math.sin(math.pi * min(1, e * 1.4)) if e < 0.95 else 0.0
        fr = fr * (1 - strength * shm)[..., None]
        # painter: draw samples far to near
        u_of_col = np.full(W, -1.0, np.float32)
        sig_of_col = np.ones(W, np.float32)
        face_of_col = np.zeros(W, np.int8)
        shade_of_col = np.ones(W, np.float32)
        order_ = np.argsort(Z)
        dxp = np.gradient(xp)
        for idx_ in np.array_split(order_, 1):
            xi = np.round(xp[idx_]).astype(int)
            ok = (xi >= 0) & (xi < W)
            xi, ii = xi[ok], idx_[ok]
            u_of_col[xi] = S[ii] / PW * (tw - 1)
            sig_of_col[xi] = sig[ii]
            face_of_col[xi] = (dxp[ii] > 0).astype(np.int8)
            # lambert-ish: light from upper left and above; normal of the surface
            nxn = -np.sin(phi[ii]); nzn = np.cos(phi[ii])
            facing = np.where(dxp[ii] > 0, 1, -1)
            lam = (0.35 * nxn * facing * -1 + 0.9 * nzn * facing)
            shade_of_col[xi] = np.clip(0.80 + 0.22 * lam, 0.62, 1.05)
        # fill 1-px holes
        holes = u_of_col < 0
        if holes.any():
            good = ~holes
            near = nd.distance_transform_edt(holes, return_distances=False, return_indices=True)[0]
            fillable = holes & (np.abs(np.arange(W) - near) <= 2)
            for arr in (u_of_col, sig_of_col, shade_of_col):
                arr[fillable] = arr[near[fillable]]
            face_of_col[fillable] = face_of_col[near[fillable]]
        cols = u_of_col >= 0
        mapx = np.repeat(u_of_col[None, :], H, 0)
        ysrc = (cyc + (yy - cyc) / sig_of_col[None, :] - top) / PH * (th - 1)
        mapy = ysrc.astype(np.float32)
        frontA = np.dstack([front, np.ones((th, tw, 1), np.float32)])
        backA = np.dstack([back[:, ::-1], np.ones((th, tw, 1), np.float32)])
        rf = cv2.remap(frontA, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        rb = cv2.remap(backA, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        faceF = (face_of_col == 1)[None, :, None]
        r = np.where(faceF, rf, rb)
        a = r[..., 3:4] * cols[None, :, None]
        pg = r[..., :3] * shade_of_col[None, :, None]
        return fr * (1 - a) + pg * a

    # foley events
    wr = Writer(out)
    for f in range(NF):
        tt = f / FPS
        k = sum(1 for s in flips if tt >= s + FL)  # completed flips
        turning = None
        for j, s in enumerate(flips):
            if s <= tt < s + FL:
                turning = (j, (tt - s) / FL)
        if turning is None:
            fr = base_scene(k, k if k < len(tex) else 0) if k > 0 else base_scene(0, 0)
            if k > 0:
                fr = base_scene(k, k - 1)
        else:
            j, p = turning
            fr = base_scene(j + 1, j - 1 if j > 0 else 0) if j > 0 else base_scene(1, 0)
            fr = curl_frame(fr, p, tex[j], backs[j])
        fr *= light
        fr = cv2.warpAffine(fr, drift_matrix(tt, DUR, amp=8, seed=1.7), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        fr = fr * (1 - hook_a) + hook_rgb * hook_a
        wr.add(fr)
    wr.close()
    return flips, FL, DUR


# ----------------------------------------------------------------- main

def build(which):
    if which == "coloring":
        silent = os.path.join(TMP, "coloring-silent.mp4")
        active = make_coloring(silent)
        n = int(len(active) / FPS * SR)
        pen = pencil_track(active, 5.0)
        foley = np.stack([pen * 0.98, pen * 1.0], 1)
        out = os.path.join(HERE, "coloring-test.mp4")
        info = finish_audio(silent, foley, out, "soft_as_a_dry_pillow", music_db_under=-14.0)
        return qa(out, os.path.join(HERE, "coloring-test-sheet.png"), os.path.join(HERE, "coloring-test-audio.png"), info)
    if which == "pageflip":
        silent = os.path.join(TMP, "pageflip-silent.mp4")
        flips, FL, DUR = make_pageflip(silent)
        n = int(DUR * SR) + SR
        fol = np.zeros(n, np.float32)
        for j, s in enumerate(flips):
            pt = page_turn(100 + j, FL)
            i0 = int(s * SR)
            fol[i0: i0 + len(pt)] += pt * (0.9 + 0.1 * j % 2)
        # finger brushing the page edge before each lift
        rng = np.random.default_rng(77)
        for s in flips:
            i0 = int(max(0, s - 0.05) * SR); L = int(0.12 * SR)
            b = bandpass(rng.standard_normal(L), 2500, 8000) * np.hanning(L) * 0.25
            fol[i0: i0 + L] += b.astype(np.float32)
        foley = np.stack([fol * 0.95, fol], 1)
        out = os.path.join(HERE, "pageflip-test.mp4")
        info = finish_audio(silent, foley, out, "this_pain_is_soft", music_db_under=-9.0)
        return qa(out, os.path.join(HERE, "pageflip-test-sheet.png"), os.path.join(HERE, "pageflip-test-audio.png"), info)


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    ok = True
    for name in (["coloring", "pageflip"] if w == "all" else [w]):
        ok &= build(name)
    sys.exit(0 if ok else 1)
