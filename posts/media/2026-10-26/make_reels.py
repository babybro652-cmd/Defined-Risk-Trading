"""Text-card reels for 10/26/2026 daily DRT content (0 Blotato credits).
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
 "size-by-stop":[
  card(None,"Most bad trades in a review aren't bad entries. They're bad sizes."),
  card("THE MISTAKE","Valid setup. Good stop.","Position too big, so a normal loss ends the day.",red=True),
  card("THE MATH","ES: $50 per point per contract.","4 point stop on 1 ES = $200. On 1 MES = $20."),
  card("THE ORDER","Find the stop. Check what it costs.","Then pick the size that fits your daily limit."),
  card(None,*SIGN)],
 "point-of-control":[
  card(None,"Point of control: the price where the most volume traded."),
  card("HOW I USE IT","I watch how price reacts when it gets there.","Accepted or rejected?"),
  card("THE TRAP","Trusting a move before it gets through that level.",red=True),
  card("MY RULE","Level first. Reaction second. Entry last.","Stop set before I click."),
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
