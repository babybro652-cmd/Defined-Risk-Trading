import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
def bg():
    y=np.linspace(0,1,H)[:,None]
    top=np.array([34,24,18]); bot=np.array([12,9,8])
    g=(top*(1-y)+bot*y)[:,:,None].repeat(W,1) if False else None
    arr=np.zeros((H,W,3),dtype=np.uint8)
    col=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)
    arr[:]=col[:,None,:]
    return Image.fromarray(arr)
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def block(d,y,text,font,fill,gap=18):
    for ln in wrap(d,text,font,W-200):
        tw=d.textlength(ln,font=font); d.text(((W-tw)/2,y),ln,font=font,fill=fill); y+=font.size+gap
    return y
def card(label,head,label2=None,sub=None,foot=False):
    im=bg(); d=ImageDraw.Draw(im)
    d.rectangle([100,560,180,568],fill=GOLD)
    y=600
    if label:
        d.text((100,y),label,font=ImageFont.truetype(B,40),fill=RED if label.startswith("WHAT") else GOLD); y+=90
    for ln in wrap(d,head,ImageFont.truetype(B,76),W-200):
        d.text((100,y),ln,font=ImageFont.truetype(B,76),fill=CREAM); y+=96
    if label2:
        y+=70; d.text((100,y),label2,font=ImageFont.truetype(B,40),fill=GOLD); y+=90
        for ln in wrap(d,sub,ImageFont.truetype(B,64),W-200):
            d.text((100,y),ln,font=ImageFont.truetype(B,64),fill=GOLD); y+=84
    elif sub:
        y+=60
        for ln in wrap(d,sub,ImageFont.truetype(R,52),W-200):
            d.text((100,y),ln,font=ImageFont.truetype(R,52),fill=MUTED); y+=70
    f=ImageFont.truetype(B,36); t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-260),t,font=f,fill=MUTED)
    return np.array(im)
cards=[
 (card(None,"The first thing my son inherits from me won't be money."),4.0),
 (card("NOT THE BALANCE","It'll be how I handle it.",None,"Kids copy what they see long before they understand it."),4.5),
 (card("HABIT 1","Know the stop before the entry."),3.5),
 (card("HABIT 2","Know the most I'll lose in a day. Stop there."),3.5),
 (card("HABIT 3","1 or 2 good trades. Close the platform. Go pick him up."),4.0),
 (card(None,"An account can be drained in a week. A habit outlasts any balance."),4.5),
 (card(None,"The habits come first.",None,"Define your risk. Wait for your setup."),4.5),
]
for i,(c,_) in enumerate(cards): Image.fromarray(c).save(f"card_{i+1}.png")
fps=30; fade=12
p=subprocess.Popen([FF,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
 "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
 "-c:a","aac","-b:a","96k","-movflags","+faststart","fb-son-inherits.mp4"],stdin=subprocess.PIPE)
black=np.zeros((H,W,3),np.uint8)
for i,(c,dur) in enumerate(cards):
    n=int(dur*fps)
    for k in range(n):
        a=1.0
        if k<fade: a=k/fade
        if k>n-fade: a=(n-k)/fade
        p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
