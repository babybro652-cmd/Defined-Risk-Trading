"""Sat 11/14 daily content: prop firm math (TT 7 AM, IG 12:30, FB 5 PM, YT Short) and the
lunch-break close story (TT 8 PM). Self-rendered text cards, no dates, no prices. Usage: python3 make_reels.py"""
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
def card(label,head,sub=None,y=420):
    im=bg();d=ImageDraw.Draw(im); text_block(d,label,head,sub,y); handle(d); return np.array(im)
def math_card():
    im=bg();d=ImageDraw.Draw(im)
    y=text_block(d,"$2,000 DRAWDOWN, 4 PT STOP","How many full stops fit inside the limit?",None,200,hs=62)
    rows=[("2 ES","$400 a stop",5,RED),("1 ES","$200 a stop",10,GOLD),("1 MES","$20 a stop",100,GRN)]
    y+=60; fb=ImageFont.truetype(B,58); fr=ImageFont.truetype(R,44); fn=ImageFont.truetype(B,64)
    for name,cost,n,col in rows:
        d.text((100,y),name,font=fb,fill=CREAM); d.text((360,y+10),cost,font=fr,fill=MUTED)
        t=f"{n} stops"; d.text((W-100-d.textlength(t,font=fn),y),t,font=fn,fill=col)
        y+=100; maxw=W-200; boxes=min(n,10); bw=(maxw-9*10)/10
        for i in range(boxes):
            x=100+i*(bw+10); d.rectangle([x,y,x+bw,y+44],fill=col)
        if n>10:
            d.text((100,y+60),"(that row, 10 times over)",font=ImageFont.truetype(R,36),fill=MUTED); y+=60
        y+=110
    d.text((100,y),"Before fees and slippage.",font=ImageFont.truetype(R,40),fill=MUTED)
    handle(d); return np.array(im)
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
render("prop-math.mp4",[
 (card(None,"$2,000 of drawdown and a 4 point ES stop. How many losses can you take?"),5),
 (card("THE MATH","ES moves $50 a point. A 4 point stop costs $200 on 1 contract."),5.5),
 (math_card(),9),
 (card("THE POINT","Your size decides how many mistakes the account survives.","Pick it before you click, never after a red trade."),6.5),
 (card(None,"Check your firm's drawdown rules before the first trade.","Define your risk. Wait for your setup."),5)])
render("lunch-close.mp4",[
 (card(None,"My ES trade was still open when my lunch break ended."),4.5),
 (card("THE RULE AT WORK","Phones aren't allowed on the floor where I work.","So the trade gets closed, wherever price is."),5.5),
 (card("WHAT HAPPENED","Some days price runs to my target without me."),4.5),
 (card("THE LESSON","Your trading window is part of your plan.","Know when your window closes before you enter."),6.5),
 (card(None,"That one's about life, not the chart. I'm fine with it.","Define your risk. Wait for your setup."),5)])
