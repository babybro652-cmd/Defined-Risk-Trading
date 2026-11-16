"""Mon 11/16 daily content: wait for confirmation (TT 7 AM, IG 12:30, YT Short), leave the stop alone (FB 5 PM), week 1 night-review question (TT 8 PM).
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
    render("wait-confirm-shortcut.mp4",[
     (card(None,"An ES entry before your setup confirms is a guess with a stop on it."),4.6),
     (card("THE EARLY ENTRY","You see it forming and you click before it's done."),3.6),
     (card("WHAT IT COSTS","If the setup never finishes, you're holding a trade your plan never gave you."),4.8),
     (card("WHAT I DO","I wait for the setup to confirm. Then I enter.","Hard stop 3.5-4 pts from entry."),6.4),
     (card("THE TRADE-OFF","Waiting can cost a few ticks of entry.","Guessing can cost a full stop."),4.4),
     (card(None,"Wait for the confirmation.","Define your risk. Wait for your setup."),3.4)])
    sys.exit()
render("wait-confirm.mp4",[
 (card(None,"An ES entry before your setup confirms is a guess with a stop on it."),5),
 (card("THE EARLY ENTRY","You see it forming and you click before it's done."),5),
 (card("WHAT IT COSTS","If the setup never finishes, you're holding a trade your plan never gave you."),6),
 (card("WHAT I DO","I wait for the setup to confirm. Then I enter.","Hard stop 3.5-4 pts from entry."),6),
 (card("THE TRADE-OFF","Waiting can cost a few ticks of entry.","Guessing can cost a full stop."),5.5),
 (card(None,"Wait for the confirmation.","Define your risk. Wait for your setup."),4.5)])
render("leave-stop.mp4",[
 (card(None,"Your ES trade goes your way first. Then price turns and heads back to your stop."),5),
 (card("THE STOP","3.5-4 pts from entry. Decided before you click.","That's my hard stop."),5.5),
 (card("THE TEST","Price climbs back toward it, and you want to give the trade more room."),6),
 (card("WHAT MOVING IT DOES","A planned loss turns into a bigger one you never agreed to."),6),
 (card("THE RULE","If it fills, it fills.","The next setup is a new trade."),5.5),
 (card(None,"Set the stop. Leave it alone.","Define your risk. Wait for your setup."),4.5)])
render("week1-question.mp4",[
 (card("ONE RULE, ONE WEEK","Day 1 of no early entries. One question for tonight's review."),5),
 (card("THE QUESTION","Did every entry today wait for my setup to confirm?"),5.5),
 (card("IF THE ANSWER IS NO","That trade goes in the journal as outside my rules, win or lose."),6),
 (card("NO TRADES TODAY?","Still a yes.","No setup, no entry."),5),
 (card(None,"4 more days. Friday I'll tell you how the week went.","Define your risk. Wait for your setup."),5)])
