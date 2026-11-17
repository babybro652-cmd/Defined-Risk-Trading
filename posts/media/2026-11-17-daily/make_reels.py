"""Tue 11/17 daily content: stop distance from entry (TT 7 AM, IG 12:30, YT Short), 4 rules to clear before a trade (FB 5 PM), week 1 day 2 (TT 8 PM).
Self-rendered text cards + drawn stop diagram (no prices, no dates). Usage: python3 make_reels.py [--short]"""
import subprocess, sys, numpy as np
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
def eqdiagram(label,head,seq,tag,tagcol,tagpos,stops=True):
    im=bg();d=ImageDraw.Draw(im); text_block(d,label,head,None,250,hs=66)
    yl=1100; dline(d,yl,"EQUAL HIGHS")
    if stops:
        f=ImageFont.truetype(B,30); t="buy stops"
        for i,x in enumerate(range(160,W-160,70)): d.ellipse([x,yl-62,x+16,yl-46],fill=MUTED)
        d.text((110,yl-120),t,font=f,fill=MUTED)
    candles(d,seq,110,yl,60)
    f=ImageFont.truetype(B,42)
    for i,ln in enumerate(tag.split("|")): d.text((tagpos[0],tagpos[1]+i*54),ln,font=f,fill=tagcol)
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


def stopdiagram(label,head,side="long"):
    im=bg();d=ImageDraw.Draw(im); text_block(d,label,head,None,250,hs=66)
    fb=ImageFont.truetype(B,34)
    ye=1060; unit=55; ys=ye+int(4*unit) if side=="long" else ye-int(4*unit)
    # entry line (cream solid), stop line (red dashed)
    d.line([80,ye,W-80,ye],fill=CREAM,width=4)
    d.text((W-80-d.textlength("ENTRY",font=fb),ye-48),"ENTRY",font=fb,fill=CREAM)
    for x in range(80,W-80,40): d.line([x,ys,x+22,ys],fill=RED,width=4)
    t="HARD STOP"; d.text((W-80-d.textlength(t,font=fb),ys+(12 if side=="long" else -48)),t,font=fb,fill=RED)
    # bracket
    bx=W-150; d.line([bx,ye,bx,ys],fill=GOLD,width=5); d.line([bx-18,ye,bx+18,ye],fill=GOLD,width=5); d.line([bx-18,ys,bx+18,ys],fill=GOLD,width=5)
    fg=ImageFont.truetype(B,44); t="3.5-4 PTS"; d.text((bx-30-d.textlength(t,font=fg),(ye+ys)//2-26),t,font=fg,fill=GOLD)
    if side=="long": seq=[(-1.5,-0.5,-2.6,-1.0),(-1.0,0.2,-1.6,-0.1),(-0.1,0.9,-0.6,0.6)]
    else: seq=[(1.5,2.6,0.5,1.0),(1.0,1.6,-0.2,0.1),(0.1,0.6,-0.9,-0.6)]
    candles(d,seq,140,ye,unit)
    f=ImageFont.truetype(B,40); t=("LONG" if side=="long" else "SHORT")+": stop "+("below" if side=="long" else "above")+" entry"
    d.text((100,1420 if side=="long" else 1420),t,font=f,fill=MUTED)
    handle(d); return np.array(im)

if "--short" in sys.argv:
    render("stop-distance-shortcut.mp4",[
     (card(None,"Where does my ES stop go? 3.5-4 points from my entry."),4.4),
     (stopdiagram("LONG OR SHORT","Same distance from entry, either side.","long"),4.6),
     (card("THE COST","On 1 ES, 4 points is $200.","3.5 points is $175."),5.0),
     (card("DECIDED FIRST","I know that number before I click."),3.4),
     (card("IF IT DOESN'T FIT","A setup that needs a wider stop than your max is a pass."),4.8),
     (card(None,"Measure the stop from entry.","Define your risk. Wait for your setup."),4.6)])
    sys.exit()
render("stop-distance.mp4",[
 (card(None,"Where does my ES stop go? 3.5-4 points from my entry."),5),
 (stopdiagram("LONG","The stop sits a fixed distance below entry.","long"),5.5),
 (stopdiagram("SHORT","Same distance, above entry.","short"),5),
 (card("THE COST","On 1 ES, 4 points is $200.","3.5 points is $175."),5.5),
 (card("DECIDED FIRST","I know the distance before I click, so every trade risks the same size."),6),
 (card("IF IT DOESN'T FIT","A setup that needs a wider stop than your max is a pass."),5.5),
 (card(None,"Measure the stop from entry.","Define your risk. Wait for your setup."),4.5)])
render("pass-check.mp4",[
 (card(None,"4 rules every ES setup has to clear before I take it."),5),
 (card("RULE 1","New York session only.","No London. No Asia."),5),
 (card("RULE 2","The setup has to confirm.","No early entries."),5),
 (card("RULE 3","It has to work with a hard stop 3.5-4 pts from entry."),5.5),
 (card("RULE 4","The day's risk stays inside my $1,000 daily max."),5.5),
 (card("ONE NO","It's a pass.","Passing costs nothing."),4.5),
 (card(None,"Clear the rules, then click.","Define your risk. Wait for your setup."),4.5)])
render("week1-day2.mp4",[
 (card("ONE RULE, ONE WEEK","Day 2 of no early entries."),4.5),
 (card("TONIGHT'S QUESTION","Did I wait, even when the setup looked almost done?"),5.5),
 (card("WHY THAT ONE","Almost done is where early entries start."),5),
 (card("EITHER ANSWER","It goes in the journal.","Win, loss or no trade."),5),
 (card(None,"3 more days. Friday I'll tell you how the week went.","Define your risk. Wait for your setup."),5)])
