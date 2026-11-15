"""Sun 11/15 daily content: equal highs (TT 7 AM, IG 12:30, YT Short), night review (FB 5 PM), one rule one week (TT 8 PM).
Self-rendered text cards + drawn candle diagrams (no prices, no dates). Usage: python3 make_reels.py"""
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
# two tops at the line (0), pullbacks between
TWO=[(-4,-2.5,-4.6,-2.8),(-2.8,0,-3.2,-1.2),(-1.2,-0.8,-3.6,-3.2),(-3.2,-2.4,-4.4,-2.6),(-2.6,0,-3,-1.4),(-1.4,-1,-3.8,-3.4)]
SWEEP=TWO+[(-3.4,-1.2,-3.8,-1.4),(-1.4,1.8,-1.8,-0.9),(-0.9,-0.6,-3.6,-3.3)]
HOLD=TWO+[(-3.4,-1.2,-3.8,-1.4),(-1.4,1.6,-1.8,1.3),(1.3,2.8,0.6,2.5)]
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
if "--short" in sys.argv:
    # YouTube Short cut, card times matched to the AI narration (about 20 s of voice)
    render("equal-highs-shortcut.mp4",[
     (card(None,"Two ES highs at the same price, and price keeps coming back for them."),3.9),
     (eqdiagram("THE LEVEL","Price tops out twice at the same spot and pulls back both times.",TWO,"",GOLD,(0,0),stops=False),1.5),
     (eqdiagram("WHY I MARK IT","Traders who sold those tops often park buy stops right above them.",TWO,"",GOLD,(0,0)),5.4),
     (eqdiagram("THE SWEEP","Price runs through the line, then closes back under. The stops got hit and the push failed.",SWEEP,"Back under|= sweep",RED,(560,1430)),4.2),
     (eqdiagram("THE HOLD","Price clears the line and stays above it. That's a breakout, not a sweep.",HOLD,"Holding|above",GRN,(110,1430),stops=False),3.3),
     (card(None,"Mark equal highs before the open.","Define your risk. Wait for your setup."),4.2)])
    sys.exit()
render("equal-highs.mp4",[
 (card(None,"Two ES highs at the same price, and price keeps coming back for them."),5),
 (eqdiagram("THE LEVEL","Price tops out twice at the same spot and pulls back both times.",TWO,"",GOLD,(0,0),stops=False),6),
 (eqdiagram("WHY I MARK IT","Traders who sold those tops often park buy stops right above them.",TWO,"",GOLD,(0,0)),6),
 (eqdiagram("THE SWEEP","Price runs through the line, then closes back under. The stops got hit and the push failed.",SWEEP,"Back under|= sweep",RED,(560,1430)),7),
 (eqdiagram("THE HOLD","Price clears the line and stays above it. That's a breakout, not a sweep.",HOLD,"Holding|above",GRN,(110,1430),stops=False),6),
 (card(None,"Mark equal highs before the open.","Define your risk. Wait for your setup."),4.5)])
render("night-review.mp4",[
 (card(None,"My son's asleep. Now I open the day's ES chart."),4.5),
 (card("THE NIGHT REVIEW","I work a full-time job, so my review happens at night, after his bedtime."),5.5),
 (card("WHAT I LOOK AT","The levels I marked. The trades I took. The setups I skipped."),6),
 (card("ONE QUESTION","Did I follow my rules?","The result comes second."),5.5),
 (card(None,"Tomorrow's plan starts tonight.","Define your risk. Wait for your setup."),5)])
render("one-rule.mp4",[
 (card("ONE RULE, ONE WEEK","Week 1: no early entries."),4.5),
 (card("THE RULE","I wait for my setup to confirm before I click.","No guessing ahead of it."),5.5),
 (card("WHY THIS ONE","Early entries feel smart until the setup never shows up.","Then you're holding a trade you made up."),6),
 (card("THE WEEK","Monday to Friday, every entry waits for confirmation.","Friday I'll tell you how it went."),6),
 (card(None,"Pick 1 rule and run it all week.","Define your risk. Wait for your setup."),5)])
