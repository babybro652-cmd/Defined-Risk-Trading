"""Paper trading reel, Fri 10/30/2026 (0 Blotato credits). Tim's own ES 15m chart of 10/29.
Usage: python3 make_paper_reel.py DIR   (DIR holds es-2026-10-29-15m-original.jpg)"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
d0=sys.argv[1]
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
def handle(d):
    f=ImageFont.truetype(B,36); t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-200),t,font=f,fill=MUTED)
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
    handle(d); return im
def chart_card():
    src=Image.open(os.path.join(d0,"es-2026-10-29-15m-original.jpg")).convert("RGB")
    ch=src.crop((0,100,1080,1930))            # drop phone status bar and app nav
    ch.save(os.path.join(d0,"chart_crop.png"))
    h=1400; w=int(ch.width*h/ch.height); ch=ch.resize((w,h),Image.LANCZOS)
    im=bg(); d=ImageDraw.Draw(im)
    d.text((80,120),"YESTERDAY ON ES",font=ImageFont.truetype(B,40),fill=GOLD)
    d.text((80,180),"Chop. Not my setup.",font=ImageFont.truetype(B,72),fill=CREAM)
    im.paste(ch,((W-w)//2,300)); handle(d); return im
CARDS=[
 card(None,"Paper trading isn't only for beginners."),
 chart_card(),
 card("SO I PAPER TRADED","No live trades forced into chop.","Same rules, same stop, same patience. No real money at risk.",red=False),
 card("WHAT IT TRAINS","The skill and the emotions.","Sitting through chop without itching to click buy is a rep too."),
 card(None,"Define your risk. Wait for your setup.","Let's have a disciplined day."),
]
DUR=[3.5,6.0,4.5,4.5,4.0]
for i,c in enumerate(CARDS): c.save(os.path.join(d0,f"slide{i+1}.png"))
out=os.path.join(d0,"paper-trading.mp4"); fps=30; fade=10
p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
 "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
 "-c:a","aac","-b:a","96k","-movflags","+faststart",out],stdin=subprocess.PIPE)
for c,dur in zip(CARDS,DUR):
    a0=np.array(c).astype(np.float32); n=int(dur*fps)
    for k in range(n):
        a=min(1.0,k/fade,(n-k)/fade)
        p.stdin.write((a0*a).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
