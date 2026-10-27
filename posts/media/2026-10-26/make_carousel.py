"""Monday IG education carousel 10/26/2026 (4:5, 0 Blotato credits). Usage: python3 make_carousel.py OUTDIR"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1350
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
def bg():
    y=np.linspace(0,1,H)[:,None]; top=np.array([34,24,18]); bot=np.array([12,9,8])
    a=np.zeros((H,W,3),dtype=np.uint8); a[:]=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:,None,:]
    return Image.fromarray(a)
def wrap(d,t,f,mw):
    out=[];cur=""
    for w in t.split():
        s=(cur+" "+w).strip()
        if d.textlength(s,font=f)<=mw: cur=s
        else: out.append(cur);cur=w
    out.append(cur);return out
def card(n,label,head,sub=None,red=False):
    im=bg();d=ImageDraw.Draw(im)
    d.text((100,120),f"{n}/4",font=ImageFont.truetype(B,34),fill=MUTED)
    d.rectangle([100,380,180,388],fill=GOLD);y=420
    if label: d.text((100,y),label,font=ImageFont.truetype(B,40),fill=RED if red else GOLD);y+=90
    fh=ImageFont.truetype(B,72)
    for ln in wrap(d,head,fh,W-200): d.text((100,y),ln,font=fh,fill=CREAM);y+=92
    if sub:
        y+=50;fs=ImageFont.truetype(R,50)
        for ln in wrap(d,sub,fs,W-200): d.text((100,y),ln,font=fs,fill=MUTED);y+=68
    f=ImageFont.truetype(B,34);t="@definedrisktrading";d.text(((W-d.textlength(t,font=f))/2,H-130),t,font=f,fill=MUTED)
    return im
SLIDES=[
 card(1,None,"Not every ES session trades the same.","Volume changes how price moves."),
 card(2,"THIN DAYS","Holidays, half-days and the days around them.","Fewer contracts trading.",red=True),
 card(3,"WHAT I SEE","More fake breaks. Less follow-through.","Levels I trust on a normal day get sloppy."),
 card(4,"MY RULE","Thin day: smaller size or no trade.","Same 3.5 to 4 point stop either way."),
]
for i,s in enumerate(SLIDES,1): s.save(os.path.join(sys.argv[1],f"slide{i}.png"))
