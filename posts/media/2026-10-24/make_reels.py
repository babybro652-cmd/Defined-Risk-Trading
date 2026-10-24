"""Text-card reels for 10/24/2026 daily DRT content (0 Blotato credits).
Usage: python3 make_reels.py OUTDIR"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
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
def card(label,head,sub=None,red=False):
    im=bg(); d=ImageDraw.Draw(im)
    d.rectangle([100,560,180,568],fill=GOLD); y=600
    if label:
        d.text((100,y),label,font=ImageFont.truetype(B,40),fill=RED if red else GOLD); y+=90
    fh=ImageFont.truetype(B,76)
    for ln in wrap(d,head,fh,W-200): d.text((100,y),ln,font=fh,fill=CREAM); y+=96
    if sub:
        y+=60; fs=ImageFont.truetype(R,52)
        for ln in wrap(d,sub,fs,W-200): d.text((100,y),ln,font=fs,fill=MUTED); y+=70
    f=ImageFont.truetype(B,36); t="@definedrisktrading"; d.text(((W-d.textlength(t,font=f))/2,H-260),t,font=f,fill=MUTED)
    return np.array(im)
SIGN=("Define your risk. Wait for your setup.","Let's have a disciplined week.")
REELS={
 "size-after-wins":[
  card(None,"A winning streak isn't a reason to size up."),
  card("THE TRAP","3 green days, so you double your contracts.","Your next normal loss now costs twice as much.",red=True),
  card("WHAT I DO","Same size. Same 3.5 to 4 point stop.","The streak doesn't change the math."),
  card("WHEN SIZE GOES UP","On a plan I wrote down in advance.","Never because I feel hot."),
  card(None,*SIGN)],
 "overnight-levels":[
  card(None,"2 lines I mark before the New York open."),
  card("LINE 1","The overnight high."),
  card("LINE 2","The overnight low."),
  card("WHY","I read them as places where stops are stacked.","Price likes to test them."),
  card("HOW I USE THEM","Near one, I slow down and wait for my setup.","I don't chase the move into it."),
  card(None,*SIGN)],
 "sim-rules":[
  card(None,"Paper trading only works if you'd take the trade with real money."),
  card("THE TRAP","Big size, no stop, 10 trades a day.","Sim money makes it feel free.",red=True),
  card("MY SIM RULES","Same size I'd trade live. Same 3.5 to 4 point stop. Same session."),
  card("THE FEEDBACK LOOP","Every sim trade goes in the journal.","Did I follow the plan?"),
  card(None,*SIGN)],
 "after-a-stop":[
  card(None,"After a stop-out, I stand up from the chart."),
  card("THE TRAP","Clicking again right away to win it back.","That's revenge, not a setup.",red=True),
  card("MY RULE","Stop hit. Walk away. Reset.","Then I check if the setup is still there."),
  card("WHY","A planned loss is the cost of the business.","An angry second trade isn't."),
  card(None,*SIGN)],
 "indicator-myth":[
  card(None,"A new indicator won't fix a rule you keep breaking."),
  card("THE MYTH","If I find the right tool, I'll stop losing.",red=True),
  card("WHAT BLOWS UP ACCOUNTS","Moved stops. Oversized trades. Revenge clicks."),
  card("WHAT FIXES IT","A stop set before entry, and a plan you follow on every trade."),
  card(None,*SIGN)],
}
out=sys.argv[1]; fps=30; fade=12; dur=4.0
for name,cards in REELS.items():
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,name+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        n=int((4.5 if i==len(cards)-1 else dur)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
