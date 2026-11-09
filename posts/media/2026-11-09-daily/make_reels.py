import subprocess
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130)
def bg():
    y=np.linspace(0,1,H)[:,None]
    top=np.array([20,26,38]); bot=np.array([8,10,15])
    arr=np.zeros((H,W,3),dtype=np.uint8)
    arr[:]=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:,None,:]
    return Image.fromarray(arr)
def wrap(d,text,font,maxw):
    lines=[];cur=""
    for w in text.split():
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur);cur=w
    lines.append(cur);return lines
def card(label,head,sub=None):
    im=bg();d=ImageDraw.Draw(im)
    d.rectangle([100,520,180,528],fill=GOLD)
    y=570
    if label: d.text((100,y),label,font=ImageFont.truetype(B,40),fill=GOLD);y+=90
    f=ImageFont.truetype(B,78)
    for ln in wrap(d,head,f,W-200): d.text((100,y),ln,font=f,fill=CREAM);y+=100
    if sub:
        y+=50;f2=ImageFont.truetype(R,52)
        for ln in wrap(d,sub,f2,W-200): d.text((100,y),ln,font=f2,fill=MUTED);y+=70
    f=ImageFont.truetype(B,36);t="@definedrisktrading"
    d.text(((W-d.textlength(t,font=f))/2,H-260),t,font=f,fill=MUTED)
    return np.array(im)
def render(name,cards):
    fps=30;fade=10
    p=subprocess.Popen([FF,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20","-an","-movflags","+faststart",name],stdin=subprocess.PIPE)
    for c,dur in cards:
        n=int(dur*fps)
        for k in range(n):
            a=1.0
            if k<fade:a=k/fade
            if k>n-fade:a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close();p.wait()
render("indicators.mp4",[
 (card(None,"A 5th indicator won't fix a broken habit."),4),
 (card("WHAT IS BROKEN","Most traders already have a setup that works.","The chart isn't the problem."),4.5),
 (card("WHAT BREAKS","The follow-through.","Moved stops. Early entries. One more trade after the plan said done."),5),
 (card("THE FIX","Grade your last 10 trades on one question.","Did I follow my own rules?"),5),
 (card(None,"Define your risk. Wait for your setup.","Fix the habit before the chart."),4.5)])
render("sweep.mp4",[
 (card(None,"Price poked above the high. Then it dropped."),5),
 (card("WHY","Obvious highs and lows hold stop orders."),5),
 (card("A SWEEP","Price pushes through, grabs them, then turns back."),5),
 (card("A REAL BREAK","Price closes beyond the level and stays there."),5),
 (card(None,"Wait for the close, then decide.","Education only."),5)])
render("cooldown.mp4",[
 (card(None,"Took a loss on ES?"),3.5),
 (card("WARNING","Your next click is probably emotion, not a setup."),4.5),
 (card("THE RULE","Close the platform for 15 minutes."),4),
 (card("DURING THE BREAK","Walk. Water. Reread your rules."),4),
 (card(None,"Re-enter only if the setup is still there.","Define your risk. Wait for your setup."),4.5)])
