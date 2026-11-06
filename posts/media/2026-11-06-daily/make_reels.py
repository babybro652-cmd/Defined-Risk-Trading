"""Text-card reels + carousel for the Fri 11/6/2026 daily posts (0 Blotato credits).
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
 "micros":[
  card(None,"Small account? Keep the stop. Shrink the contract."),
  card("THE MYTH","\"A small account needs a tight stop.\"",red=True),
  card("THE PROBLEM","Too tight, and normal ES noise takes you out before the idea plays out.",red=True),
  card("THE MATH","A 4-point stop: $200 on 1 ES. $20 on 1 MES.","ES is $50 a point. MES is $5 a point."),
  card("THE FIX","Put the stop where the idea is wrong. Then size the trade to fit it."),
  card(None,*SIGN)],
 "two-trades":[
  card(None,"1 or 2 good trades. Then I'm done for the day."),
  card("THE RULE","A good trade or two, then the platform closes."),
  card("THE TRAP","Every extra trade is one more chance to break a rule.",red=True),
  card("THE PAYOFF","Stopping early keeps the good trades good."),
  card("THE LESSON","Decide your stopping point before the session starts."),
  card(None,*SIGN)],
 "night-review":[
  card(None,"My trade review happens at night."),
  card("WHEN","After work. After my son's bedtime."),
  card("WHY NIGHT","My session is long over. No pull to make it back."),
  card("WHAT I ASK","Was the plan right? Did I follow it?"),
  card("THE POINT","Calm eyes grade the process, not the P&L."),
  card(None,*SIGN)],
 "sessions":[
  card(None,"ES trades nearly 24 hours. Here's the map in ET.","Session times are approximate."),
  card("ASIA","6:00 PM to 3:00 AM ET","The trading day opens at 6 PM."),
  card("LONDON","3:00 AM to 9:30 AM ET"),
  card("NEW YORK","9:30 AM to 4:00 PM ET","Regular trading hours. My focus."),
  card("THE BREAK","5:00 to 6:00 PM ET, every day.","The week runs Sunday 6 PM to Friday 5 PM."),
  card("WHY IT MATTERS","Each session can set its own high and low.","Know which one you're trading in."),
  card(None,*SIGN)],
}
SLIDES=REELS["sessions"]
if len(sys.argv)>1 and sys.argv[1]=="slides":
    for i,c in enumerate(SLIDES,1): Image.fromarray(c).save(f"sessions-{i}.png")
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
