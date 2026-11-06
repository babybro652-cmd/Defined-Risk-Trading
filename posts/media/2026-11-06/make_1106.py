"""Fri 11/6/2026 drafts (0 Blotato credits).
python3 make_1106.py OUTDIR
Piece 1: Keaira testimonial reel, 15 s, 1080x1920 (keaira-silent.mp4 + keaira-yt-silent.mp4, no "link in bio").
Piece 2 (micro-contract bullet cut per Tim 11/6): "Paper to real money" carousel (paper-1..9.png, 1080x1350) + reel (paper-silent.mp4, paper-yt-silent.mp4).
Music is added afterwards with drt/audio/add_audio.py."""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERT = os.path.join(REPO, "posts/testimonials/media/keaira-certificate-redacted.png")
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
W = 1080
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

def emoji(ch, size):
    e = Image.new("RGBA", (160, 160)); ImageDraw.Draw(e).text((0, 0), ch, font=f(EMOJI, 109), embedded_color=True)
    e = e.crop(e.getbbox()); return e.resize((size, size), Image.LANCZOS)

STY = {  # font, size, color, line step, space before
  "label": (B, 40, GOLD, 70, 0), "head": (B, 76, CREAM, 94, 0), "big": (B, 84, CREAM, 102, 0),
  "sub": (R, 50, MUTED, 66, 30), "line": (B, 50, CREAM, 66, 26), "bul": (B, 48, CREAM, 62, 30),
  "small": (R, 34, MUTED, 44, 40), "gold": (B, 50, GOLD, 66, 26), "close": (B, 76, GOLD, 94, 56)}

def text_block(d, x, y, items, maxw, scale=1.0):
    for kind, txt in items:
        p, s, col, step, pre = STY[kind]; s = int(s*scale); step = int(step*scale)
        if isinstance(txt, tuple): txt, col = txt
        ft = f(p, s); y += int(pre*scale)
        if kind == "bul":
            d.rectangle([x, y+s*0.42, x+14, y+s*0.42+14], fill=GOLD)
            for ln in wrap(d, txt, ft, maxw-44): d.text((x+44, y), ln, font=ft, fill=col); y += step
        else:
            for ln in wrap(d, txt, ft, maxw): d.text((x, y), ln, font=ft, fill=col); y += step
    return y

def measure(items, maxw, scale=1.0):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10))); return text_block(d, 0, 0, items, maxw, scale)

def card(H, items, emoji_after=None, foot=None, swipe=False):
    im = bg(W, H); d = ImageDraw.Draw(im); maxw = W-180
    scale = 1.0
    room = H - 420 if H > 1500 else H - 300
    while measure(items, maxw, scale) > room: scale -= 0.04
    h = measure(items, maxw, scale); y0 = max(150, (H - h)//2 - (60 if H > 1500 else 20))
    d.rectangle([90, y0-40, 170, y0-32], fill=GOLD)
    y = text_block(d, 90, y0, items, maxw, scale)
    if emoji_after:   # emoji at the end of the last line of the first item
        kind, txt = items[0]; p, s, _, step, _ = STY[kind]; s = int(s*scale); step = int(step*scale)
        lines = wrap(d, txt, f(p, s), maxw); last = lines[-1]
        ex = 90 + d.textlength(last + " ", font=f(p, s)); ey = y0 + step*(len(lines)-1) + 2
        if ex + s > W - 60: ex, ey = 90, y0 + step*len(lines)
        e = emoji(emoji_after, s); im.paste(e, (int(ex), int(ey)), e)
    hf = f(B, 34); t = "@definedrisktrading"
    hy = H-(200 if H > 1500 else 100)
    d.text(((W-d.textlength(t, font=hf))/2, hy), t, font=hf, fill=MUTED)
    if foot:
        sf = f(R, 32); d.text(((W-d.textlength(foot, font=sf))/2, hy-62), foot, font=sf, fill=MUTED)
    if swipe:
        sf = f(B, 34); t = "Swipe  >"; d.text((W-90-d.textlength(t, font=sf), hy), t, font=sf, fill=GOLD)
    return im

# ---------- Piece 1: Keaira ----------
def cert_frames(H, n):
    """slow zoom (1.00 -> 1.14) on the certificate, drifting toward the name/account lines"""
    base = card(H, [("label", "MEMBER WIN"), ("big", "50K account. Third try.")])
    # move text up: rebuild with fixed position instead
    base = bg(W, H); d = ImageDraw.Draw(base)
    y0 = 430; d.rectangle([90, y0-40, 170, y0-32], fill=GOLD)
    text_block(d, 90, y0, [("label", "MEMBER WIN"), ("big", "50K account.\nThird try.")], W-180)
    hf = f(B, 34); t = "@definedrisktrading"; d.text(((W-d.textlength(t, font=hf))/2, H-200), t, font=hf, fill=MUTED)
    src = Image.open(CERT).convert("RGB"); sw, sh = src.size
    bw = W-80; bh = int(bw*sh/sw); bx = 40; by = 760
    d.rectangle([bx-4, by-4, bx+bw+3, by+bh+3], outline=GOLD, width=4)
    fx, fy = 700/sw, 705/sh   # zoom focus (name + account line)
    frames = []
    for k in range(n):
        t = k/(n-1); t = t*t*(3-2*t); z = 1.0 + 0.35*t
        cw, ch = sw/z, sh/z
        cx = min(max(fx*sw - cw/2*(1 if t else 1), 0), sw-cw); cy = min(max(fy*sh - ch/2, 0), sh-ch)
        cx = (sw-cw)/2*(1-t) + cx*t; cy = (sh-ch)/2*(1-t) + cy*t
        crop = src.resize((bw, bh), Image.LANCZOS, box=(cx, cy, cx+cw, cy+ch))
        fr = base.copy(); fr.paste(crop, (bx, by)); frames.append(np.asarray(fr))
    return frames

def keaira(yt):
    H = 1920
    hook = card(H, [("big", "My student passed her first funded eval")], emoji_after="\U0001F389")
    five = card(H, [("big", "Took me 5 tries to pass my first."), ("big", ("She did it in 3.", GOLD))])
    end_items = [("head", "Same strategy, same patience.")]
    end_items += [("sub", ("Learn it in the Skool.", CREAM))] if yt else [("sub", ("Learn it in the Skool.\nLink in bio.", CREAM))]
    end = card(H, end_items, foot="Results vary. Not typical.")
    return hook, five, end

# ---------- Piece 2: paper to real money ----------
PAPER = [
  [("big", "Your strategy didn't change."), ("big", ("You did.", GOLD)), ("sub", "Paper trading vs real money: what changes, and how to fix it.")],
  [("label", "PAPER VS REAL"), ("head", "On paper, a loss is a number."),
   ("sub", "With real money, it's a feeling. Then the feeling starts placing your trades.")],
  [("label", "WHAT CHANGES: FEAR"), ("head", "You stop trusting the plan."),
   ("bul", "You cut winners early to lock something in."), ("bul", "You hesitate on the entry, then chase it late.")],
  [("label", "WHAT CHANGES: A LOSS"), ("head", "One red trade turns into three."),
   ("bul", "You move your stop to dodge the hit."), ("bul", "You revenge trade to win it back."),
   ("bul", "You size up to get there faster.")],
  [("label", "WHAT CHANGES: THE ITCH"), ("head", "Sitting still starts to feel like losing."),
   ("bul", "You overtrade."), ("bul", "You take trades outside your time window.")],
  [("label", "MY STORY"), ("line", "It took me 5 evals to pass my first one, and 8 before my first payout."),
   ("line", "I lost 2 prop accounts trading London, outside my own rules."),
   ("gold", "That's why I trade New York only now, with hard rules.")],
  [("label", "THE FIX: BEFORE THE TRADE"), ("bul", "Same size and same routine on paper and live."),
   ("bul", "Define your risk before you enter."), ("bul", "My hard stop: 3.5 to 4 points on ES. It never moves."),
   ("bul", "Set the bracket, then hands off.")],
  [("label", "THE FIX: DURING THE DAY"), ("bul", "New York only. No trades before 10 AM."),
   ("bul", "Daily max loss, set before the open."), ("bul", "1 to 2 good trades, then done."),
   ("bul", "After a loss, walk away. No revenge re-entry."), ("bul", "Journal every trade.")],
]
def paper_close(yt):
    it = [("label", "GOING LIVE"), ("bul", "Treat the eval like your own money."),
          ("close", "Define your risk, wait for your setup.")]
    if not yt: it.append(("sub", ("Full lessons in Skool. Link in bio.", CREAM)))
    return it

def paper_cards(H, yt=False):
    items = PAPER + [paper_close(yt)]
    return [card(H, it, swipe=(H < 1500 and i == 0), foot="Education only. Not financial advice." if i == len(items)-1 else None)
            for i, it in enumerate(items)]

REEL = [
  ([("big", "Your strategy didn't change."), ("big", ("You did.", GOLD)), ("sub", "Paper vs real money.")], 3.4),
  ([("label", "PAPER VS REAL"), ("head", "On paper, a loss is a number."), ("head", ("With real money, it's a feeling.", GOLD))], 4.2),
  ([("label", "WHAT CHANGES"), ("bul", "You cut winners early."), ("bul", "You hesitate, then chase the entry.")], 4.0),
  ([("label", "AFTER A LOSS"), ("bul", "You move your stop."), ("bul", "You revenge trade."), ("bul", "You size up to win it back.")], 4.3),
  ([("label", "THE ITCH"), ("bul", "You overtrade."), ("bul", "You trade outside your time window.")], 3.6),
  ([("label", "MY STORY"), ("line", "5 evals to pass my first. 8 before my first payout."),
    ("line", "I lost 2 prop accounts trading London, outside my own rules."), ("gold", "Now: New York only, hard rules.")], 6.6),
  ([("label", "THE FIX"), ("bul", "Same size and routine on paper and live."), ("bul", "Risk defined before entry."),
    ("bul", "My hard stop: 3.5 to 4 points on ES. It never moves."), ("bul", "Bracket set, hands off.")], 6.0),
  ([("label", "THE FIX"), ("bul", "No trades before 10 AM."), ("bul", "Daily max loss. 1 to 2 good trades, then done."),
    ("bul", "After a loss, walk away."), ("bul", "Journal every trade.")], 5.6),
]
def reel_close(yt):
    it = [("label", "GOING LIVE"), ("bul", "Treat the eval like your own money."),
          ("close", "Define your risk, wait for your setup.")]
    if not yt: it.append(("sub", ("Full lessons in Skool. Link in bio.", CREAM)))
    return it
def reel_cards(yt):
    its = [i for i, _ in REEL] + [reel_close(yt)]
    return [card(1920, it, foot="Education only. Not financial advice." if k == len(its)-1 else None) for k, it in enumerate(its)]
REEL_DURS = [d for _, d in REEL] + [5.0]

def words(items): return sum(len((t[0] if isinstance(t, tuple) else t).split()) for _, t in items)

def video(segments, path, fps=30, fade=10):
    """segments: list of (frames_list_or_image, seconds)"""
    p = subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r",str(fps),"-i","-",
        "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-preset","medium",
        "-crf","18","-c:a","aac","-b:a","96k","-movflags","+faststart",path], stdin=subprocess.PIPE)
    seqs = []
    for src, dur in segments:
        n = int(round(dur*fps))
        if isinstance(src, list): fr = src[:n] + [src[-1]]*(n-len(src))
        else: a = np.asarray(src); fr = [a]*n
        seqs.append(fr)
    for i, fr in enumerate(seqs):
        n = len(fr)
        for k in range(n):
            a = fr[k]
            if i+1 < len(seqs) and k >= n-fade:
                t = (k-(n-fade)+1)/(fade+1); a = (a.astype(np.float32)*(1-t) + seqs[i+1][0].astype(np.float32)*t).astype(np.uint8)
            p.stdin.write(np.ascontiguousarray(a).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    cf = cert_frames(1920, 150)
    Image.fromarray(cf[0]).save(os.path.join(out, "keaira-cert-start.png")); Image.fromarray(cf[-1]).save(os.path.join(out, "keaira-cert-end.png"))
    for yt in (False, True):
        hook, five, end = keaira(yt); tag = "-yt" if yt else ""
        for nm, im in (("hook", hook), ("five", five), ("end", end)): im.save(os.path.join(out, f"keaira{tag}-{nm}.png"))
        video([(hook, 3), (cf, 5), (five, 4), (end, 3)], os.path.join(out, f"keaira{tag}-silent.mp4"))
    for i, c in enumerate(paper_cards(1350), 1): c.save(os.path.join(out, f"paper-{i}.png"))
    print("reel total", round(sum(REEL_DURS), 1))
    for yt in (False, True):
        cards = reel_cards(yt)
        for i, c in enumerate(cards, 1): c.save(os.path.join(out, f"paper{'-yt' if yt else ''}-card-{i}.png"))
        video(list(zip(cards, REEL_DURS)), os.path.join(out, f"paper{'-yt' if yt else ''}-silent.mp4"))
