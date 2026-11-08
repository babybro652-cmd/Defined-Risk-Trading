"""Text-card reels + carousel for the Sun 11/8/2026 daily posts (0 Blotato credits).
Slides: python3 make_reels.py slides (red-week carousel)
Usage: python3 make_reels.py OUTDIR [SECONDS or per-card list a,b,c] [NAME]
Short: python3 make_reels.py OUT T1,T2,... weekly-prep"""
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
 "weekly-levels":[
  card(None,"Before Monday, mark 3 levels on your ES chart."),
  card("LEVEL 1","Last week's high.","The top of the whole week's range."),
  card("LEVEL 2","Last week's low.","The bottom of the week's range."),
  card("LEVEL 3","Friday's close.","Where the week ended. Monday can open away from it."),
  card("THE CHECK","When price reaches one, does it hold past it or snap back?","Let price show you before you act."),
  card(None,*SIGN)],
 "weekly-prep":[
  card(None,"4 things to do before the trading week starts."),
  card("STEP 1","Check the calendar for scheduled news.","Big reports can move ES fast. Know the day and time."),
  card("STEP 2","Write your risk limits for the week.","Stop size. Max loss per day. Max trades per day."),
  card("STEP 3","Read last week's journal.","The rule you broke most is this week's focus."),
  card("STEP 4","Pick your trading window.","Decide your session and hours before Monday."),
  card(None,*SIGN)],
 "loss-limit":[
  card(None,"Set your loss limit before the week starts, not after a red day."),
  card("THE MATH","4-point stop on 1 ES = $200.","ES is $50 a point."),
  card("THE LIMIT","Pick a daily max loss. Count how many full stops fit.","Example: a $600 daily max = 3 full stops on 1 ES."),
  card("THE RULE","Hit the max and you're done for the day.","Tomorrow starts fresh. The limit doesn't move.",red=True),
  card("WHY BEFORE","A limit set mid-week gets set by emotion.","Write it down while you're calm."),
  card(None,*SIGN)],
 "my-week":[
  card(None,"Full-time job. New dad. Here's how trading fits my week."),
  card("MON TO FRI","A full-time job, 6:00 AM to 4:30 PM."),
  card("LUNCH","Some days I trade my break, around 10 AM ET.","When it ends, the phone goes away. No phones on the floor."),
  card("NIGHT","I review my trades after work, once my son is asleep."),
  card("THE RULES","New York session only. Hard stop 3.5 to 4 points.","1 or 2 good trades, then done."),
  card(None,*SIGN)],
 "red-week":[
  card(None,"Red week? Don't change your strategy yet."),
  card("THE MYTH","\"A losing week means my strategy is broken.\"",red=True),
  card("THE CHECK","Grade the week on your rules first.","Hard stop on every trade? Only your setups? Inside your daily max?"),
  card("RULES FOLLOWED","A red week can still be a good week.","Losing weeks happen to a sound plan."),
  card("RULES BROKEN","Fix the habit, not the system.","A new indicator won't stop a moved stop.",red=True),
  card("THE WEEK AHEAD","Pick 1 rule to tighten.","Track it on every trade."),
  card(None,*SIGN)],
}
if len(sys.argv)>1 and sys.argv[1]=="slides":
    for i,c in enumerate(REELS["red-week"],1): Image.fromarray(c).save(f"redweek-{i}.png")
    sys.exit()
out=sys.argv[1]; fps=30; fade=12
arg=sys.argv[2] if len(sys.argv)>2 else "4"
durs=[float(x) for x in arg.split(",")]; dur=durs[0] if len(durs)==1 else 0
only=sys.argv[3] if len(sys.argv)>3 else None
for name,cards in REELS.items():
    if name=="red-week" or (only and name!=only): continue
    tag=name if arg in ("4","4.0") else f"{name}-timed"
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-r","30","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",os.path.join(out,tag+".mp4")],stdin=subprocess.PIPE)
    for i,c in enumerate(cards):
        d_=durs[i] if len(durs)>1 else dur
        n=int((d_+0.5 if i==len(cards)-1 else d_)*fps)
        for k in range(n):
            a=1.0
            if k<fade: a=k/fade
            if k>n-fade: a=(n-k)/fade
            p.stdin.write((c.astype(np.float32)*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
