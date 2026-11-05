"""Text-card reels + carousel for the Thu 11/5/2026 daily posts (0 Blotato credits).
Slides: python3 make_reels.py slides
Usage: python3 make_reels.py OUTDIR [SECONDS or per-card list a,b,c] [NAME]
Short: python3 make_reels.py OUT 2.6,3.8,5.8,7.0,4.3 close-short"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
def bg():
    y=np.linspace(0,1,H)[:,None]; top=np.array([34,24,18]); bot=np.array([12,9,8])
    arr=np.zeros((H,W,3),dtype=np.uint8); arr[:]=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:,None,:]
    return Image.fromarray(arr)
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def card(label,head,sub=None,red=False):
    im=bg(); d=ImageDraw.Draw(im)
    d.rectangle([100,560,180,568],fill=GOLD); y=600
    if label:
        d.text((100,y),label,font=ImageFont.truetype(B,40),fill=RED if red else GOLD); y+=90
    fh=ImageFont.truetype(B,76)
    for ln in wrap(d,head,fh,W-200): d.text((100,y),ln,font=fh,fill=CREAM); y+=96
    if sub:
        y+=60; fs=ImageFont.truetype(R,52)
        for ln in wrap(d,sub,fs,W-200): d.text((100,y),ln,font=fs,fill=MUTED); y+=70
    f=ImageFont.truetype(B,36); t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-260),t,font=f,fill=MUTED)
    return np.array(im)
SIGN=("Define your risk. Wait for your setup.","Let's have a disciplined day.")
REELS={
 "prior-day":[
  card(None,"2 levels to mark before the New York open."),
  card("LEVEL 1","Yesterday's high.","The top of the prior day's range."),
  card("LEVEL 2","Yesterday's low.","The bottom of the prior day's range."),
  card("WHAT TO WATCH","Does price hold past the level, or snap back inside?"),
  card("THE POINT","Levels don't predict. They give you a plan.","Above, below, or back inside. Decide what each one means before the open."),
  card(None,*SIGN)],
 "moved-stop":[
  card(None,"A stop you move isn't a stop."),
  card("THE HABIT","Price gets close, so you give it a little more room.",red=True),
  card("WHAT HAPPENS","A planned 4-point loss turns into 8, then 12.",red=True),
  card("THE FIX","Set the stop before the entry. Then hands off.","If it gets hit, the idea was wrong. That's its job."),
  card("THE LESSON","Small losses are the cost of trading.","Big ones come from moving the line."),
  card(None,*SIGN)],
 "win-rate":[
  card(None,"A 40% win rate can still come out ahead."),
  card("THE MYTH","\"I need to win most of my trades.\"",red=True),
  card("THE MATH","10 trades. 4 wins at 2R. 6 losses at 1R.","+8R minus 6R = +2R, not counting fees."),
  card("WHAT 1R MEANS","1R is what you risk on the trade.","With a 4-point stop, 1R is 4 points."),
  card("THE LESSON","Keep your losses the size you planned.","Your wins carry the rest."),
  card(None,*SIGN)],
}
SLIDES=[
  card(None,"3 things to log after every ES trade."),
  card("1. THE SCREENSHOT","Entry, stop and target on the chart.","Memory rewrites trades. Pictures don't."),
  card("2. THE RULE CHECK","Did I follow every rule? Yes or no."),
  card("3. THE FEELING","Calm, rushed, or chasing?","Patterns show up here first."),
  card("WHY","After 20 trades, the log shows you what to fix."),
  card(None,*SIGN)]
if len(sys.argv)>1 and sys.argv[1]=="slides":
    for i,c in enumerate(SLIDES,1): Image.fromarray(c).save(f"journal-{i}.png")
    sys.exit()
out=sys.argv[1]; fps=30; fade=12
arg=sys.argv[2] if len(sys.argv)>2 else "4"
durs=[float(x) for x in arg.split(",")]; dur=durs[0] if len(durs)==1 else 0
only=sys.argv[3] if len(sys.argv)>3 else None
for name,cards in REELS.items():
    if only and name!=only: continue
    tag=name if arg in ("4","4.0") else f"{name}-timed"
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,tag+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        d_=durs[i] if len(durs)>1 else dur
        n=int((d_+0.5 if i==len(cards)-1 else d_)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
