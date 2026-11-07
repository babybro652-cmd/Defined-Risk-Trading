"""Text-card reels + carousel for the Sat 11/7/2026 daily posts (0 Blotato credits).
Slides: python3 make_reels.py slides
Usage: python3 make_reels.py OUTDIR [SECONDS or per-card list a,b,c] [NAME]
Short: python3 make_reels.py OUT 2.6,3.8,5.8,7.0,4.3 mental-stop"""
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
 "mental-stop":[
  card(None,"A mental stop isn't a stop."),
  card("THE MYTH","\"I'll get out when it hits my number.\"",red=True),
  card("THE PROBLEM","In a fast move, price can run past your number before you click.",red=True),
  card("THE FIX","Put a hard stop in the platform before you enter.","Even a stop order can fill a little worse in a fast market."),
  card("THE SIZING","Size for the slip, not the perfect fill.","Plan as if the exit comes in worse than your level."),
  card(None,*SIGN)],
 "size-slip":[
  card(None,"Size your trade for the slip, not the perfect fill."),
  card("THE PLAN","4-point stop on 1 ES = $200 of planned risk.","ES is $50 a point."),
  card("THE SLIP","A fast move fills you 2 points worse.","Now that loss is $300.",red=True),
  card("THE FIX","Leave room in your daily max for a worse fill.","Size so a bad fill still fits your plan."),
  card("THE SWAP","Can't fit the slip on ES? Trade MES.","$5 a point. Same stop, a tenth of the risk."),
  card(None,*SIGN)],
 "separate-logs":[
  card(None,"My paper trades and my eval trades never share a log."),
  card("THE PROBLEM","Mixed together, a strong paper week can hide a bad eval day.",red=True),
  card("PAPER","Where I test the plan with no money on the line."),
  card("EVAL","Real rules. Real drawdown limits. Real pressure."),
  card("THE CHECK","I grade each log on its own.","Did I follow the plan in both?"),
  card(None,*SIGN)],
 "before-ten":[
  card(None,"If the move happens before 10 AM, I miss it."),
  card("THE RULE","No trades before 10 AM ET."),
  card("THE COST","Some days the cleanest move is done before I can take it.",red=True),
  card("WHY I KEEP IT","I read the market better once the opening rush settles."),
  card("THE TRADE-OFF","I'd rather miss a move than chase one.","Another setup comes."),
  card(None,*SIGN)],
 "weekend":[
  card(None,"ES is closed right now. Here's the weekend map in ET."),
  card("FRIDAY","5:00 PM ET","The trading week ends."),
  card("SATURDAY","Closed all day.","No ES trading."),
  card("SUNDAY","6:00 PM ET","Trading reopens with the Asia session."),
  card("MY PLAN","I don't trade the Sunday open.","New York session only, after 10 AM ET."),
  card("WHY IT MATTERS","Price can open Sunday away from Friday's close.","Know where it closed before you plan Monday."),
  card(None,*SIGN)],
}
if len(sys.argv)>1 and sys.argv[1]=="slides":
    for i,c in enumerate(REELS["weekend"],1): Image.fromarray(c).save(f"weekend-{i}.png")
    sys.exit()
out=sys.argv[1]; fps=30; fade=12
arg=sys.argv[2] if len(sys.argv)>2 else "4"
durs=[float(x) for x in arg.split(",")]; dur=durs[0] if len(durs)==1 else 0
only=sys.argv[3] if len(sys.argv)>3 else None
for name,cards in REELS.items():
    if name=="weekend" or (only and name!=only): continue
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
