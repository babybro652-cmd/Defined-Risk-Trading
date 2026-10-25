"""Text-card reels for 10/25/2026 daily DRT content (0 Blotato credits).
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
 "failed-breakout":[
  card(None,"A breakout that closes back inside the range isn't a breakout."),
  card("THE TRAP","Price pokes above the overnight high. You buy the break.","Then the candle closes back inside.",red=True),
  card("HOW I READ IT","A failed break above a high can be a stop run.","Not a new trend."),
  card("WHAT I DO","No chase. I wait for my setup to form, with a 3.5 to 4 point stop set first."),
  card(None,*SIGN)],
 "one-loss-myth":[
  card(None,"1 losing trade doesn't mean your strategy is broken."),
  card("THE MYTH","Stop hit, so the setup doesn't work.","Time for a new system.",red=True),
  card("THE TRUTH","Every setup loses some of the time.","That's what the stop is for."),
  card("HOW I JUDGE IT","A batch of trades, same checklist, risk set before entry.","Then I read the results together."),
  card(None,*SIGN)],
 "weekly-review":[
  card(None,"My Sunday review is 3 questions."),
  card("QUESTION 1","Was every stop set before I entered?"),
  card("QUESTION 2","Did I trade the New York session only?"),
  card("QUESTION 3","Did I stop after 1 or 2 good trades?"),
  card("WHY","Results tell me what happened.","These tell me if I followed the plan."),
  card(None,*SIGN)],
 "two-and-done":[
  card(None,"1 or 2 good trades. Then I close the chart."),
  card("THE TRAP","Trade 3. Trade 4. Trade 5.","Bored, forcing setups that aren't there.",red=True),
  card("MY RULE","A hard cap on trades per day.","No matter how much of the session is left."),
  card("WHY IT WORKS","Fewer clicks. Same stop every time.","A clear finish line."),
  card(None,*SIGN)],
 "sim-first-20":[
  card(None,"Your first 20 paper trades have 1 job."),
  card("THE JOB","Prove you can follow the process.","Without skipping a step."),
  card("THE RULES","Full checklist every trade. Risk set before entry. 1 or 2 trades a day, at least 2 weeks."),
  card("THE STAT TO TRACK","How many of the 20 followed every rule.","Not your win rate."),
  card(None,*SIGN)],
 "early-entry":[
  card(None,"I don't enter before my setup finishes forming."),
  card("THE TRAP","You see it coming and jump in early.","Then the candle closes the other way.",red=True),
  card("MY RULE","Wait for the closed candle that confirms it.","No confirmation, no trade."),
  card("WHAT IT COSTS","Sometimes I miss a few points.","I'm fine with that."),
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
