"""Personal TikTok paper trading reel (post #2), Fri 10/30/2026. 0 Blotato credits.
Usage: python3 make_personal_reel.py OUTDIR CHART_PNG"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
out_dir, chart = sys.argv[1], sys.argv[2]
def bg():
    y=np.linspace(0,1,H)[:,None]; top=np.array([34,24,18]); bot=np.array([12,9,8])
    arr=np.zeros((H,W,3),dtype=np.uint8); arr[:]=(top[None,:]*(1-y)+bot[None,:]*y).astype(np.uint8)[:,None,:]
    return Image.fromarray(arr)
def wrap(d,text,font,maxw):
    lines=[]; cur=""
    for w in text.split():
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def card(head,sub=None,label=None,red=False,size=84):
    im=bg(); d=ImageDraw.Draw(im)
    fh=ImageFont.truetype(B,size); fs=ImageFont.truetype(R,56); fl=ImageFont.truetype(B,42)
    hl=wrap(d,head,fh,W-200); sl=wrap(d,sub,fs,W-200) if sub else []
    total=(80 if label else 0)+len(hl)*int(size*1.22)+(50+len(sl)*76 if sl else 0)
    y=(H-total)//2-40
    d.rectangle([100,y-50,180,y-42],fill=GOLD)
    if label: d.text((100,y),label,font=fl,fill=RED if red else GOLD); y+=80
    for ln in hl: d.text((100,y),ln,font=fh,fill=CREAM); y+=int(size*1.22)
    if sl:
        y+=50
        for ln in sl: d.text((100,y),ln,font=fs,fill=MUTED); y+=76
    return im
def chart_card():
    ch=Image.open(chart).convert("RGB"); h=1380; w=int(ch.width*h/ch.height); ch=ch.resize((w,h),Image.LANCZOS)
    im=bg(); d=ImageDraw.Draw(im)
    d.text((80,150),"YESTERDAY",font=ImageFont.truetype(B,42),fill=GOLD)
    d.text((80,210),"Not my market.",font=ImageFont.truetype(B,76),fill=CREAM)
    im.paste(ch,((W-w)//2,360)); return im
CARDS=[
 (card("“Paper trading isn't real trading.”",size=92),2.4),
 (card("Cool.","Neither is gambling your rent on a setup that isn't there."),2.8),
 (chart_card(),3.0),
 (card("Paper is where I get the reps when the market isn't mine."),2.4),
 (card("Same rules. Same stop. Same patience."),2.2),
 (card("The only thing missing is the damage.",label="THE DIFFERENCE",red=True),2.2),
 (card("Ego blows more accounts than bad charts ever will."),2.4),
 (card("Keep laughing.","I'll keep my capital."),2.4),
]
for i,(c,_) in enumerate(CARDS): c.save(os.path.join(out_dir,f"card{i+1}.png"))
out=os.path.join(out_dir,"paper-trading-personal.mp4"); fps=30; fade=8
p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
 "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20",
 "-c:a","aac","-b:a","96k","-movflags","+faststart",out],stdin=subprocess.PIPE)
for c,dur in CARDS:
    a0=np.array(c).astype(np.float32); n=int(dur*fps)
    for k in range(n):
        a=min(1.0,k/fade,(n-k)/fade); p.stdin.write((a0*a).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
