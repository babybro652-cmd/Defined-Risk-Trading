"""Fri 11/13 7 AM TikTok / IG reel / YouTube Short: the overnight high, sweep vs hold.
Self-rendered text cards + drawn candle diagrams (no prices, no dates). Usage: python3 make_reels.py"""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(225,85,85); GRN=(80,190,130)
def bg():
    y=np.linspace(0,1,H)[:,None]; top=np.array([20,26,38]); bot=np.array([8,10,15])
    arr=np.zeros((H,W,3),dtype=np.uint8); arr[:]=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:,None,:]
    return Image.fromarray(arr)
def wrap(d,text,font,maxw):
    lines=[];cur=""
    for w in text.split():
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur);cur=w
    lines.append(cur);return lines
def handle(d):
    f=ImageFont.truetype(B,36);t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-200),t,font=f,fill=MUTED)
def text_block(d,label,head,sub,y,hs=78):
    d.rectangle([100,y,180,y+8],fill=GOLD); y+=50
    if label: d.text((100,y),label,font=ImageFont.truetype(B,40),fill=GOLD);y+=80
    f=ImageFont.truetype(B,hs)
    for ln in wrap(d,head,f,W-200): d.text((100,y),ln,font=f,fill=CREAM);y+=int(hs*1.28)
    if sub:
        y+=40;f2=ImageFont.truetype(R,52)
        for ln in wrap(d,sub,f2,W-200): d.text((100,y),ln,font=f2,fill=MUTED);y+=70
    return y
def card(label,head,sub=None):
    im=bg();d=ImageDraw.Draw(im); text_block(d,label,head,sub,470); handle(d); return np.array(im)
def candles(d,seq,x0,y_line,unit,cw=46,gap=26):
    # seq: list of (open, high, low, close) in units relative to the line (positive = above)
    x=x0
    for o,h,l,c in seq:
        col=GRN if c>=o else RED; cx=x+cw//2
        Y=lambda v:int(y_line-v*unit)
        d.line([cx,Y(h),cx,Y(l)],fill=col,width=5)
        top,bot=sorted([Y(o),Y(c)]); d.rectangle([x,top,x+cw,max(bot,top+4)],fill=col)
        x+=cw+gap
def dline(d,y,label):
    for x in range(80,W-80,40): d.line([x,y,x+22,y],fill=GOLD,width=4)
    d.text((W-80-d.textlength(label,font=ImageFont.truetype(B,32)),y-46),label,font=ImageFont.truetype(B,32),fill=GOLD)
def diagram(label,head,seq,tag,tagcol,tagpos):
    im=bg();d=ImageDraw.Draw(im); text_block(d,label,head,None,250,hs=66)
    yl=1080; dline(d,yl,"OVERNIGHT HIGH"); candles(d,seq,110,yl,60)
    f=ImageFont.truetype(B,42)
    for i,ln in enumerate(tag.split("|")): d.text((tagpos[0],tagpos[1]+i*54),ln,font=f,fill=tagcol)
    handle(d); return np.array(im)
SWEEP=[(-4,-3,-5.5,-3.2),(-3.2,-1.8,-3.8,-2),(-2,-0.6,-2.6,-0.8),(-0.8,1.6,-1.2,-0.6),(-0.6,-0.3,-2.8,-2.5),(-2.5,-2,-4.2,-3.8),(-3.8,-3.2,-5.6,-5.2),(-5.2,-4.6,-6.4,-6)]
HOLD=[(-4,-3,-5.5,-3.2),(-3.2,-1.8,-3.8,-2),(-2,-0.6,-2.6,-0.8),(-0.8,1.4,-1.2,1.2),(1.2,2.0,0.4,1.8),(1.8,2.2,0.5,0.9),(0.9,2.6,0.6,2.4),(2.4,3.6,2.0,3.4)]
def render(name,cards):
    fps=30;fade=10
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20","-an","-movflags","+faststart",name],stdin=subprocess.PIPE)
    for c,dur in cards:
        n=int(dur*fps)
        for k in range(n):
            a=min(1.0,k/fade,(n-k)/fade)
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close();p.wait()
render("overnight-high.mp4",[
 (card(None,"ES pokes above the overnight high, then snaps back under it. That's a sweep."),5),
 (card("THE LEVEL","The overnight high is the top of everything ES traded from 6 PM to 9:30 AM ET."),6),
 (diagram("THE SWEEP","Price trades above the line, then closes back below it. Breakout buyers get trapped.",SWEEP,"Back below|= sweep",RED,(730,1120)),6.5),
 (diagram("THE HOLD","Price clears the line and stays above it. That's a breakout, not a sweep.",HOLD,"Holding|above",GRN,(110,900)),6),
 (card("MY RULE","No trades before 10 AM ET. An early sweep is one I watch, not one I take."),6),
 (card(None,"Mark the overnight high before the open.","Define your risk. Wait for your setup."),4.5)])
