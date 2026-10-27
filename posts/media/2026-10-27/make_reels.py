"""Text-card reels for 10/27/2026 daily DRT content (0 Blotato credits).
Usage: python3 make_reels.py OUTDIR"""
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
SIGN=("Define your risk. Wait for your setup.","Let's have a disciplined week.")
REELS={
 "equal-lows":[
  card(None,"Equal lows on ES aren't a floor to me."),
  card("WHY","Stops sit under them.","Price often runs there first."),
  card("THE TRAP","Buying the bounce right at the lows.",red=True),
  card("WHAT I DO","Wait for the reaction after the sweep.","Stop set before I click."),
  card(None,*SIGN)],
 "breakeven-myth":[
  card(None,"Moving your stop to breakeven fast doesn't protect you."),
  card("THE MYTH","Stop at entry = a free trade.",red=True),
  card("THE TRUTH","ES moves a few points back and forth all day.","Normal noise takes you out."),
  card("MY RULE","The stop stays put until price reaches my first marked level."),
  card(None,*SIGN)],
 "pre-open":[
  card(None,"My pre-open checklist on ES."),
  card("1","Overnight high and low marked."),
  card("2","Daily loss limit set."),
  card("3","2-trade cap."),
  card("THEN","I wait for my setup."),
  card(None,*SIGN)],
 "broke-cap":[
  card(None,"Last week I broke my own 2-trade cap twice."),
  card("THE PROBLEM","Both extra trades worked out.","A broken rule that pays gets broken again.",red=True),
  card("HOW I GRADE IT","Rules, not results.","Over the cap is a mark against me."),
  card("THIS WEEK","Cap stays at 2.","Hit it, platform closes."),
  card(None,*SIGN)],
 "write-the-reason":[
  card(None,"No written reason for the entry? You don't have a trade yet."),
  card("WHAT REVIEWS SHOW","The chart looked good. They clicked.","An hour later, the reason is a feeling.",red=True),
  card("THE FIX","1 line before the order:","Setup. Stop. What makes me wrong."),
  card("THE PAYOFF","A month of reasons shows which setups you trust for good reasons."),
  card(None,*SIGN)],
 "session-levels":[
  card(None,"I don't trade Asia or London. I still mark their highs and lows."),
  card("WHY","In how I read ES, New York often reaches for one of them first."),
  card("WHAT I DO","Mark them before the open.","Wait for my setup there."),
  card(None,*SIGN)],
}
out=sys.argv[1]; fps=30; fade=12; dur=4.0
for name,cards in REELS.items():
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,name+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        n=int((4.5 if i==len(cards)-1 else dur)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
