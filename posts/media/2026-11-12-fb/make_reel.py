import subprocess
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130)
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
def card(label,head,sub=None,subgold=False):
    im=bg(); d=ImageDraw.Draw(im)
    d.rectangle([100,560,180,568],fill=GOLD); y=600
    if label: d.text((100,y),label,font=ImageFont.truetype(B,40),fill=GOLD); y+=90
    fh=ImageFont.truetype(B,76)
    for ln in wrap(d,head,fh,W-200): d.text((100,y),ln,font=fh,fill=CREAM); y+=96
    if sub:
        y+=60; fs=ImageFont.truetype(B if subgold else R,56 if subgold else 52)
        for ln in wrap(d,sub,fs,W-200): d.text((100,y),ln,font=fs,fill=GOLD if subgold else MUTED); y+=74
    f=ImageFont.truetype(B,36); t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-260),t,font=f,fill=MUTED)
    return np.array(im)
cards=[
 (card(None,"A steady paycheck is the best tool I have in the market."),4.0),
 (card("THE JOB","Full time at a distribution center.","6 AM to 4:30 PM, Monday to Friday. I train order picker skills."),4.5),
 (card("ONLINE","The day job gets treated like a cage.","Every other video sells the day you quit."),4.0),
 (card("WHAT IT GIVES ME","Bills covered first.","No single day in the market has to pay the rent."),4.0),
 (card("A HARD STOP","No phones on the warehouse floor.","Lunch break over, I'm off my phone."),4.0),
 (card("AT HOME","Baby boy at home. Chart time comes after he falls asleep."),4.0),
 (card(None,"Slow on solid footing beats fast under pressure.","Define your risk. Wait for your setup.",True),4.5),
]
for i,(c,_) in enumerate(cards): Image.fromarray(c).save(f"card_{i+1}.png")
fps=30; fade=12
p=subprocess.Popen([FF,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
 "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
 "-c:a","aac","-b:a","96k","-movflags","+faststart","fb-w2-base.mp4"],stdin=subprocess.PIPE)
for c,dur in cards:
    n=int(dur*fps)
    for k in range(n):
        a=1.0
        if k<fade: a=k/fade
        if k>n-fade: a=(n-k)/fade
        p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
