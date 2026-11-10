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
render("skipped.mp4",[
 (card(None,"Sometimes the best trade is the one you skip."),4.5),
 (card("THE SETUP","Price does exactly what you expected.","Outside your trading window."),4.5),
 (card("THE RULE","No window, no trade.","Even when it works without you."),4.5),
 (card("WHY","One rule bent for a winner gets bent again for a loser."),5),
 (card(None,"Missing a move costs nothing.","Define your risk. Wait for your setup."),4.5)])
render("entryfee.mp4",[
 (card(None,"Your stop is the price of the ticket."),4),
 (card("BEFORE THE CLICK","Know the exact dollar amount you can lose."),4.5),
 (card("ON 2 ES","4 points is $400. That's the whole cost of the idea."),5),
 (card("IF IT HITS","You paid the fee. The idea was wrong. Move on."),4.5),
 (card(None,"Pay the fee, not the tuition.","Define your risk. Wait for your setup."),4.5)])
render("exitfirst.mp4",[
 (card(None,"Write the exit before the entry."),4),
 (card("STEP 1","Where am I wrong? That's the stop."),4),
 (card("STEP 2","Where is the next level? That's the target."),4.5),
 (card("STEP 3","Is the target at least 2x the stop?","If not, skip it."),5),
 (card(None,"Exits decided in calm beat exits decided in panic.","Education only."),5)])
