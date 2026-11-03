"""Text-card reels for the Tue 11/3/2026 daily posts (0 Blotato credits).
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
SIGN=("Define your risk. Wait for your setup.","Let's have a disciplined day.")
REELS={
 "stop-dollars":[
  card(None,"Know your stop in dollars before you click."),
  card("ES MATH","1 point = $50 per contract.","1 tick (0.25) = $12.50."),
  card("A 4-POINT STOP","16 ticks = $200 per contract.","2 contracts = $400 on the line."),
  card("ON MES","The same 4 points = $20 per contract.","Same chart, one tenth the risk."),
  card("MY RULE","If the dollar number scares you, the size is wrong.","Fix the size. Keep the stop."),
  card(None,*SIGN)],
 "wide-stop":[
  card(None,"A wider stop isn't a safer trade."),
  card("THE MYTH","\"Give it room and it can't stop me out.\"",red=True),
  card("THE MATH","Same size, 12-point stop = 3x the risk","of a 4-point stop."),
  card("WHAT I DO","My stop is 3.5 to 4 points.","No setup inside that? No trade."),
  card(None,*SIGN)],
 "limited-time":[
  card(None,"Less screen time made me a pickier trader."),
  card("MY WEEK","Full-time job. New dad.","Trading fits around both."),
  card("SO I CAN'T","Sit and wait for every move.","Or take every setup I see."),
  card("SO I DO","1 or 2 good trades.","Then I'm done for the day."),
  card("THE LESSON","Fewer trades, picked on purpose,","beat a full day of forcing it."),
  card(None,*SIGN)],
}
out=sys.argv[1]; fps=30; fade=12
dur=float(sys.argv[2]) if len(sys.argv)>2 else 4.0
only=sys.argv[3] if len(sys.argv)>3 else None
for name,cards in REELS.items():
    if only and name!=only: continue
    tag=name if dur==4.0 else f"{name}-{dur:g}s"
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,tag+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        n=int((dur+0.5 if i==len(cards)-1 else dur)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
