"""Personal IG paper trading reels (posts #1 and #3), Fri 10/30/2026. 0 Blotato credits.
Same style as make_personal_reel.py. Tim posts these himself (not scheduled).
Usage: python3 make_paper_13_reels.py OUTDIR CHART_PNG"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H=1080,1920
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(232,178,92); CREAM=(245,236,220); MUTED=(170,150,130); RED=(214,104,84)
SAFE_BOTTOM=H-350; SAFE_RIGHT=W-150
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
    hl=wrap(d,head,fh,SAFE_RIGHT-100); sl=wrap(d,sub,fs,SAFE_RIGHT-100) if sub else []
    total=(80 if label else 0)+len(hl)*int(size*1.22)+(50+len(sl)*76 if sl else 0)
    y=(H-total)//2-40
    d.rectangle([100,y-50,180,y-42],fill=GOLD)
    if label: d.text((100,y),label,font=fl,fill=RED if red else GOLD); y+=80
    for ln in hl: d.text((100,y),ln,font=fh,fill=CREAM); y+=int(size*1.22)
    if sl:
        y+=50
        for ln in sl: d.text((100,y),ln,font=fs,fill=MUTED); y+=76
    assert y<=SAFE_BOTTOM, (head,y)
    return im
def chart_card(head,label=None,size=68):
    im=bg(); d=ImageDraw.Draw(im); fh=ImageFont.truetype(B,size)
    y=200
    if label: d.text((100,y),label,font=ImageFont.truetype(B,42),fill=GOLD); y+=64
    for ln in wrap(d,head,fh,SAFE_RIGHT-100): d.text((100,y),ln,font=fh,fill=CREAM); y+=int(size*1.2)
    y+=30
    ch=Image.open(chart).convert("RGB"); h=SAFE_BOTTOM-y; w=int(ch.width*h/ch.height)
    if w>720: w=720; h=int(ch.height*w/ch.width)
    ch=ch.resize((w,h),Image.LANCZOS); im.paste(ch,((W-w)//2,y)); return im
REELS={
 "paper-1":[
  (card("I'm tired of people clowning paper trading like it's for kids.",size=88),2.8),
  (chart_card("Yesterday the market didn't fit my setup."),3.2),
  (card("Not even close.","So I didn't trade it."),2.4),
  (card("You know what's embarrassing?"),1.8),
  (card("Blowing an account because you had to prove something to people who don't even pay your bills.",size=74),3.6),
  (card("I'll paper trade all day before I force a trade that isn't in my plan."),3.0),
  (card("Call it scared.","I call it still having an account next week."),3.0),
 ],
 "paper-3":[
  (card("Some of y'all look down on paper trading but can't sit through one choppy morning without clicking buttons.",size=74),3.8),
  (chart_card("One choppy morning.",label="NOTHING LINES UP"),2.8),
  (card("That's the whole point."),1.8),
  (card("Paper isn't only practice for the skill.","It's practice for the emotions."),2.8),
  (card("Sitting still when nothing lines up is a skill, and it takes reps."),2.8),
  (card("I'd rather paper trade a bad day than blow a good account trying to force it."),3.0),
  (card("Define your risk. Wait for your setup.","If it's not there, it's not there."),3.0),
 ],
}
fps=30; fade=8
for name,CARDS in REELS.items():
    for i,(c,_) in enumerate(CARDS): c.save(os.path.join(out_dir,f"{name}-card{i+1}.png"))
    CARDS[0][0].save(os.path.join(out_dir,f"{name}-cover.png"))
    out=os.path.join(out_dir,f"{name}-reel.mp4")
    p=subprocess.Popen([FF,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
     "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20",
     "-c:a","aac","-b:a","96k","-movflags","+faststart",out],stdin=subprocess.PIPE)
    for c,dur in CARDS:
        a0=np.array(c).astype(np.float32); n=int(dur*fps)
        for k in range(n):
            a=min(1.0,k/fade,(n-k)/fade); p.stdin.write((a0*a).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
