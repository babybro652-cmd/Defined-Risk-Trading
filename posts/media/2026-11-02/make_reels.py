"""Text-card reels for the Mon 11/2/2026 daily posts (0 Blotato credits).
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
SIGN=("Define your risk. Wait for your setup.","Let's have a disciplined day.")
REELS={
 "open-push":[
  card(None,"The first push after 9:30 isn't my entry."),
  card("THE TRAP","Price can run hard off the bell.","Late traders chase it.",red=True),
  card("WHAT I WATCH","Does it hold, or snap back through the open?","The reaction tells me more than the push."),
  card("MY RULE","No entry until my setup forms.","Stop set before I click."),
  card(None,*SIGN)],
 "lunch-stop":[
  card(None,"My lunch break is my hardest stop."),
  card("THE JOB","Full-time at a distribution center.","6 AM to 4:30 PM, Monday to Friday."),
  card("THE WINDOW","Some days I trade on my lunch break.","Around 10 AM."),
  card("THE HARD STOP","Break ends. Phone goes away.","Phones aren't allowed on the floor.",red=True),
  card("WHY IT HELPS","No hunting for one more trade.","The window decides when I'm done."),
  card(None,*SIGN)],
}
out=sys.argv[1]; fps=30; fade=12
dur=float(sys.argv[2]) if len(sys.argv)>2 else 4.0
only=sys.argv[3] if len(sys.argv)>3 else None
for name,cards in REELS.items():
    if only and name!=only: continue
    tag=name if dur==4.0 else f"{name}-{dur:g}s"
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,tag+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        n=int((dur+0.5 if i==len(cards)-1 else dur)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
