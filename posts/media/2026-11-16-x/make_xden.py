import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
F='/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/fonts/'
W,H=1600,900; random.seed(11)
G=(124,255,72); GD=(70,170,40); WH=(236,236,236); GR=(150,150,150)
img=Image.new('RGB',(W,H),(8,10,9)); px=img.load()
for y in range(0,H,2):
    for x in range(0,W,2):
        v=random.randint(0,18); c=(8+v,10+v,9+v)
        for dy in (0,1):
            for dx in (0,1): px[x+dx,y+dy]=c
glow=Image.new('RGB',(W,H),(0,0,0)); gd=ImageDraw.Draw(glow)
for i in range(14):
    x=200+i*90; gd.ellipse((x-6,64,x+6,76),fill=(220,230,220))
gd.ellipse((300,-250,1300,330),fill=(28,38,30))
img=ImageChops.add(img,glow.filter(ImageFilter.GaussianBlur(40)))
spl=Image.new('RGB',(W,H),(0,0,0)); sd=ImageDraw.Draw(spl)
for cx,cy in [(70,780),(1530,120),(1500,820),(120,90)]:
    for _ in range(260):
        r=random.expovariate(1/60); a=random.uniform(0,6.28); s=random.randint(1,9)
        x=cx+r*math.cos(a)*2.2; y=cy+r*math.sin(a)
        sd.ellipse((x-s,y-s,x+s,y+s),fill=(random.randint(40,110),random.randint(150,255),random.randint(20,60)))
img=ImageChops.add(img,spl.filter(ImageFilter.GaussianBlur(1.2)))
img=ImageChops.add(img,spl.filter(ImageFilter.GaussianBlur(28)))
def T(xy,s,font,size,fill,anchor='mm',glow_c=None):
    global img
    f=ImageFont.truetype(F+font,size)
    if glow_c:
        L=Image.new('RGB',(W,H),(0,0,0)); ImageDraw.Draw(L).text(xy,s,font=f,fill=glow_c,anchor=anchor)
        img=ImageChops.add(img,L.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(img).text(xy,s,font=f,fill=fill,anchor=anchor)
T((800,115),'TONIGHT • 9:00 PM ET','anton.ttf',34,GR)
T((800,200),'PHX @ DEN','permanent-marker.ttf',110,WH)
T((800,320),'FIRST BASKET','permanent-marker.ttf',96,G,glow_c=(60,140,30))
d=ImageDraw.Draw(img); d.line((440,385,1160,379),fill=G,width=6)
T((800,425),'DEN WINS THE TIP 71% • JOKIC VS IGHODARO','anton.ttf',34,WH)
picks=[('#1','JOKIC','+376'),('#2','MURRAY','+588'),('#3','CAM JOHNSON','+947')]
for i,(r,n,o) in enumerate(picks):
    cx=360+i*440; d=ImageDraw.Draw(img)
    d.rounded_rectangle((cx-190,480,cx+190,700),radius=20,fill=(16,22,17),outline=G if i==0 else GD,width=4 if i==0 else 3)
    T((cx,520),r,'permanent-marker.ttf',40,G)
    T((cx,590),n,'anton.ttf',58,WH)
    T((cx,660),'FAIR '+o,'anton.ttf',36,G)
T((800,760),'MODEL PICKS • PLAYING DIMES, NOT HOPES','anton.ttf',36,G,glow_c=(30,90,20))
T((800,830),'NOT A CAPPER • SMALL STAKES • FIRST BASKET IS A LONG SHOT','anton.ttf',24,GR)
img.save('/home/user/Defined-Risk-Trading/posts/media/2026-11-16-x/x-den-fb-1116.png')
