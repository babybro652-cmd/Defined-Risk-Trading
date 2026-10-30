"""Text-card reel for the Fri 10/30/2026 daily posts (0 Blotato credits).
Usage: python3 make_commentary_reel.py OUTDIR"""
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
 "gap-fill":[
  card(None,"Gaps don't have to fill."),
  card("THE MYTH","Every gap on ES gets filled.","Some fill. Some run and never look back.",red=True),
  card("WHAT I MARK","Yesterday's 4 PM price.","The space between it and the 9:30 open is the gap."),
  card("WHAT I WAIT FOR","New York shows its hand first.","Fill or run, my stop is set before entry."),
  card(None,*SIGN)],
 "one-session":[
  card(None,"More hours on the chart isn't more opportunity."),
  card("THE MYTH","Trade every session and you catch more moves.","More hours, more chances to break your rules.",red=True),
  card("MY WINDOW","New York session only.","Asia and London are levels on my chart, not entries."),
  card("THE EDGE","Same window. Same rules. Risk set first."),
  card(None,*SIGN)],
 "grade-process":[
  card(None,"I grade trades on process, not P&L."),
  card("GRADE A","Followed every rule. Took the stop.","Still an A. The process worked."),
  card("GRADE F","Broke a rule. Made money.","Still an F. Luck isn't repeatable.",red=True),
  card("WHY","Rules you can repeat build the account.","One trade's outcome doesn't."),
  card(None,*SIGN)],
 "daily-limit":[
  card(None,"1 bad trade used to turn into 4."),
  card("THE FIX","One max loss number for the day.","Set before the open. Never changed during it."),
  card("THE RULE","Hit it and the platform closes.","No matter how good the next setup looks.",red=True),
  card("WHY IT WORKS","The limit makes the call, not my mood."),
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
