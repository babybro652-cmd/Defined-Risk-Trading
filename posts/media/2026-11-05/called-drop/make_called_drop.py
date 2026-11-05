"""'I called today's drop' carousel + reel, Thu 11/5/2026 (0 Blotato credits).
python3 make_called_drop.py OUTDIR [--line "Tim's one line on the longs"]
Writes slide-1..7.png (1080x1350), reel-silent.mp4 and reel-yt-silent.mp4 (1080x1920).
Charts: Tim's phone screenshots, cropped (no status bar/clock, no time axis, no indicator
tables), fill labels/arrows/countdowns covered, targets drawn on."""
import argparse, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84); GREEN=(110,190,150)
LINE = "I don't take trades before 10 AM. That's a rule. The drop happened before then, so I missed it and waited for my next setup. It was a buy."
f = lambda p, s: ImageFont.truetype(p, s)

def bg(W, H):
    y = np.linspace(0, 1, H)[:, None]; top = np.array([34,24,18]); bot = np.array([12,9,8])
    a = np.zeros((H, W, 3), np.uint8); a[:] = (top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:, None, :]
    return Image.fromarray(a)

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur+" "+w).strip()
            if d.textlength(t, font=font) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

from scipy import ndimage
BG=(15,15,15); GRID=(28,28,28); AXIS_X=920

def thin(idx):
    """keep only runs of <=3 (gridlines), drop wide bands (session boxes)"""
    keep=[]; runs=np.split(idx, np.where(np.diff(idx)>1)[0]+1) if len(idx) else []
    for r in runs:
        if len(r)<=3: keep+=list(r)
    return np.array(keep, int)

def clean_plot(im, y0, y1, gridc, blanks=(), heal=()):
    """Keep only candle pixels in rows y0..y1 left of the price axis; everything else
    (session shading and lines, shelves, POC/EMA lines, labels, fills, arrows, panels) -> plain bg.
    Gridlines are redrawn where the original had them."""
    a = np.array(im).astype(int); P = a[y0:y1, :AXIS_X]
    for (bx0,by0,bx1,by1) in blanks:                 # red arrows / alert icons: never candles
        P[max(by0-y0,0):max(by1-y0,0), bx0:bx1] = BG
    R,G,Bc = P[...,0],P[...,1],P[...,2]
    red = (R>170)&(G<125)&(Bc<135)&(R-G>90)
    grn = (G>105)&(G-R>60)&(G-Bc>5)&(R<130)
    out = np.empty_like(P); out[:] = BG
    gm = np.all(np.abs(P-np.array(gridc))<=4, 2)
    rows = thin(np.where(gm.mean(1) > 0.25)[0]); cols = thin(np.where(gm.mean(0) > 0.25)[0])
    out[rows, :] = GRID; out[:, cols] = GRID
    for m, col in ((red,(242,54,69)), (grn,(7,154,128))):
        m = ndimage.binary_closing(m, structure=np.ones((9,1)))   # bridge gaps where lines crossed candles
        for (hx0,hy0,hx1,hy1) in heal:             # text drawn over a candle body: close it vertically
            sub = m[hy0-y0-30:hy1-y0+30, hx0:hx1]
            m[hy0-y0-30:hy1-y0+30, hx0:hx1] = ndimage.binary_closing(sub, structure=np.ones((61,1))) | sub
        lab, n = ndimage.label(m)
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            h, w = sl[0].stop-sl[0].start, sl[1].stop-sl[1].start
            if (lab[sl]==i).sum() < 40 or (h < 9 and w > 60): m[sl][lab[sl]==i] = False   # dots, horizontal lines
        out[m] = col
    a[y0:y1, :AXIS_X] = out
    return Image.fromarray(a.astype(np.uint8))

def axis_label(im, y_center, text):
    d = ImageDraw.Draw(im); size = 20
    while d.textlength(text, font=f(R, size+1)) <= 117: size += 1
    ft = f(R, size); bb = d.textbbox((0,0), text, font=ft)
    d.text((936-bb[0], y_center-(bb[1]+bb[3])//2), text, font=ft, fill=(185,185,185))

def stack(parts):
    gap = 6; H = sum(p.height for p in parts) + gap*(len(parts)-1)
    out = Image.new("RGB", (1080, H), (60,50,42)); y = 0
    for p in parts: out.paste(p, (0, y)); y += p.height + gap
    return out

def dashed(d, y, x0, x1, col, w=4, dash=18, gap=12):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x+dash, x1), y)], fill=col, width=w); x += dash+gap

def pill(d, x, y, text, col, fg=(15,12,10), size=30):
    ft = f(B, size); tw = d.textlength(text, font=ft); h = size+16
    d.rounded_rectangle([x, y-h//2, x+tw+28, y+h//2], radius=10, fill=col)
    d.text((x+14, y-size//2-3), text, font=ft, fill=fg)

def bias_chart(marked=True):
    im = Image.open(os.path.join(SRC, "skool-bias-chart.jpg")).convert("RGB")
    top, bot = 520, 1582                               # ~7,750 down to ~7,684
    im = clean_plot(im, top, bot, (30,34,46))
    d = ImageDraw.Draw(im)
    for box in [(906, 885, 1072, 938), (906, 1087, 1072, 1141)]:   # EMA and POC price tags
        d.rectangle(box, fill=BG)
    axis_label(im, 906, "7,725.00")
    plot = im.crop((0, top, 1080, bot)); d = ImageDraw.Draw(plot)
    if marked:
        y = lambda p: 1112.7 + (7712.5 - p) * 16.47 - top
        dashed(d, y(7738), 0, 900, RED, 5)
        pill(d, 24, int(y(7738)) - 46, "Idea dead above 7,738", RED)
        for p, lab in [(7712, "Target 1  7,712"), (7704, "Target 2  7,704"), (7690, "Target 3  7,690")]:
            dashed(d, y(p), 0, 900, GOLD, 4); pill(d, 630, int(y(p)), lab, GOLD)
    return stack([im.crop((0, 0, 1080, 88)), plot, im.crop((0, 1862, 1080, 1925))])

def result_chart():
    im = Image.open(os.path.join(SRC, "skool-trade-chart.jpg")).convert("RGB")
    top, bot = 392, 1560                               # ~7,745 down to ~7,404
    im = clean_plot(im, top, bot, (28,28,28), blanks=[(545,1200,596,1280)],   # red sell arrows
                    heal=[(440,1146,540,1198)])                                   # "6 @ ..." label over a candle
    hd = np.array(im.crop((0, 185, 1080, 236))).astype(int)                       # day change row, text only
    hd[(hd[...,0]-hd[...,1]) < 40] = BG
    return stack([im.crop((0, 0, 1080, 88)), Image.fromarray(hd.astype(np.uint8)), im.crop((0, top, 1080, bot)),
                  im.crop((0, 1862, 1080, 1925))])

def text_block(d, x, y, items, maxw):
    for kind, txt in items:
        ft = {"label": f(B,40), "head": f(B,74), "chead": f(B,60), "sub": f(R,50), "line": f(B,48), "ph": f(B,40)}[kind]
        col = {"label": GOLD, "head": CREAM, "chead": CREAM, "sub": MUTED, "line": CREAM, "ph": RED}[kind]
        if isinstance(txt, tuple): txt, col = txt
        step = {"label": 88, "head": 92, "chead": 74, "sub": 66, "line": 64, "ph": 54}[kind]
        if kind in ("sub", "ph") : y += 30
        if kind == "line": y += 22
        for ln in wrap(d, txt, ft, maxw): d.text((x, y), ln, font=ft, fill=col); y += step
    return y

def text_card(W, H, items, y0):
    im = bg(W, H); d = ImageDraw.Draw(im)
    d.rectangle([90, y0-40, 170, y0-32], fill=GOLD)
    text_block(d, 90, y0, items, W-180)
    hf = f(B, 34); t = "@definedrisktrading"; d.text(((W-d.textlength(t, font=hf))/2, H-110), t, font=hf, fill=MUTED)
    return im

def chart_card(W, H, label, head, chart, cap_h):
    im = bg(W, H); d = ImageDraw.Draw(im)
    y = text_block(d, 60, 60 if H < 1500 else 150, [("label", label), ("chead", head)], W-120)
    room_h = H - y - (120 if H < 1500 else 290); s = min((W-60)/chart.width, room_h/chart.height)
    c = chart.resize((int(chart.width*s), int(chart.height*s)), Image.LANCZOS)
    cx = (W-c.width)//2; cy = y + 20 + (room_h - c.height)//2
    d.rectangle([cx-3, cy-3, cx+c.width+2, cy+c.height+2], outline=(70,58,48), width=3)
    im.paste(c, (cx, cy))
    hf = f(B, 34); t = "@definedrisktrading"; d.text(((W-d.textlength(t, font=hf))/2, H-(70 if H < 1500 else 200)), t, font=hf, fill=MUTED)
    return im

def build(W, H, line, yt=False):
    big = H > 1500; y0 = 640 if big else 380
    bc, rc = bias_chart(), result_chart()
    lesson_extra = [("sub", (line or LINE, CREAM))]
    cards = [
      text_card(W, H, [("head", "I called Thursday's drop before the open."),
                       ("sub", "Here's the plan, and what New York did with it.")], y0),
      text_card(W, H, [("label", "THE READ"), ("head", "Sells only."),
                       ("sub", "London swept above the Asia high, up to about 7,738. The Asia low near 7,690 was still untouched.")], y0),
      text_card(W, H, [("label", "THE PLAN"),
                       ("line", "Target 1: about 7,712, where most overnight volume traded"),
                       ("line", "Target 2: the London low near 7,704"),
                       ("line", "Target 3: the Asia low near 7,690"),
                       ("line", ("Wrong if price breaks and holds above 7,738.", RED))], y0 - (40 if big else 60)),
      chart_card(W, H, "BEFORE THE OPEN", "The plan on the chart.", bc, 0),
      chart_card(W, H, "AFTER THE OPEN", "All 3 targets were hit by the end of the first New York candle.", rc, 0),
      text_card(W, H, [("label", "THE LESSON"), ("head", "Bias tells you the side. The setup tells you when.")] + lesson_extra, y0),
      text_card(W, H, [("head", "Follow for the plan before the open.")] +
                ([] if yt else [("sub", "Full breakdowns are in Skool.\nLink in bio.")]), y0),
    ]
    return cards

def video(cards, durs, path, fps=30, fade=10):
    p = subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r",str(fps),"-i","-",
        "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-preset","medium",
        "-crf","18","-c:a","aac","-b:a","96k","-movflags","+faststart",path], stdin=subprocess.PIPE)
    arrs = [np.asarray(c, dtype=np.float32) for c in cards]
    for i, (a, dur) in enumerate(zip(arrs, durs)):
        n = int(dur*fps)
        for k in range(n):
            if i+1 < len(arrs) and k >= n-fade:
                t = (k-(n-fade)+1)/(fade+1); fr = a*(1-t)+arrs[i+1]*t
            else: fr = a
            p.stdin.write(fr.astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--line"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for i, c in enumerate(build(1080, 1350, a.line), 1): c.save(os.path.join(a.out, f"slide-{i}.png"))
    durs = [2.6, 3.6, 4.6, 4.4, 4.6, 5.6, 2.6]           # 28.0 s
    video(build(1080, 1920, a.line), durs, os.path.join(a.out, "reel-silent.mp4"))
    video(build(1080, 1920, a.line, yt=True), durs, os.path.join(a.out, "reel-yt-silent.mp4"))
