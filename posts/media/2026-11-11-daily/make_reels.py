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
render("chase.mp4",[
 (card(None,"The candle already moved. Chasing it costs you."),4),
 (card("THE ENTRY","Buy after a big push and you get the worst price of the move."),5.5),
 (card("THE STOP","Under the whole candle is wide. Inside it is noise."),5.5),
 (card("THE FIX","Let price come back to a level you marked."),5),
 (card(None,"If it never comes back, the trade wasn't yours.","Define your risk. Wait for your setup."),5)])
render("poc.mp4",[
 (card(None,"The busiest price on yesterday's chart matters today."),4.5),
 (card("VOLUME PROFILE","How much traded at each price, not each bar."),5),
 (card("POINT OF CONTROL","The single price where the most volume traded."),5),
 (card("HOW I READ IT","Holding away from it: one side is in control.","Drifting back to it: balance, expect chop."),5.5),
 (card(None,"Mark it before the open. Watch what price does there.","Education only."),5)])
render("news.mp4",[
 (card(None,"Some of the fastest ES moves are on the calendar."),4.5),
 (card("THE RISK","A scheduled report can move ES several points in seconds."),5),
 (card("THE SLIP","Liquidity thins. A stop can fill past your price."),5),
 (card("THE CHECK","Read the economic calendar before your session.","Decide before the release: flat, or protected."),5.5),
 (card(None,"The calendar is part of your risk plan.","Define your risk. Wait for your setup."),4.5)])
