import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/fonts/'
W,H=1600,900; random.seed(7)
G=(124,255,72); GD=(70,170,40); WH=(236,236,236); GR=(150,150,150)
img=Image.new('RGB',(W,H),(8,10,9))
# noise texture
px=img.load()
for y in range(0,H,2):
    for x in range(0,W,2):
        v=random.randint(0,18); c=(8+v,10+v,9+v)
        for dy in (0,1):
            for dx in (0,1): px[x+dx,y+dy]=c
# stadium light glow
glow=Image.new('RGB',(W,H),(0,0,0)); gd=ImageDraw.Draw(glow)
for i in range(14):
    x=200+i*90; gd.ellipse((x-6,70-6,x+6,70+6),fill=(220,230,220))
gd.ellipse((300,-250,1300,330),fill=(28,38,30))
glow=glow.filter(ImageFilter.GaussianBlur(40)); img=Image.blend(img,Image.eval(glow,lambda v:v),0.0)
img=Image.composite(Image.new('RGB',(W,H),(0,0,0)),img,Image.new('L',(W,H),0))
from PIL import ImageChops
img=ImageChops.add(img,glow)
# green splatter
spl=Image.new('RGB',(W,H),(0,0,0)); sd=ImageDraw.Draw(spl)
for cx,cy in [(70,780),(1530,120),(1500,820),(120,90)]:
    for _ in range(260):
        r=random.expovariate(1/60); a=random.uniform(0,6.28); s=random.randint(1,9)
        x=cx+r*math.cos(a)*2.2; y=cy+r*math.sin(a)
        sd.ellipse((x-s,y-s,x+s,y+s),fill=(random.randint(40,110),random.randint(150,255),random.randint(20,60)))
img=ImageChops.add(img,spl.filter(ImageFilter.GaussianBlur(1.2)))
img=ImageChops.add(img,spl.filter(ImageFilter.GaussianBlur(28)))
d=ImageDraw.Draw(img)
def T(xy,s,font,size,fill,anchor='mm',glow_c=None):
    f=ImageFont.truetype(F+font,size)
    if glow_c:
        L=Image.new('RGB',(W,H),(0,0,0)); ImageDraw.Draw(L).text(xy,s,font=f,fill=glow_c,anchor=anchor)
        img.paste(ImageChops.add(img,L.filter(ImageFilter.GaussianBlur(14))))
    ImageDraw.Draw(img).text(xy,s,font=f,fill=fill,anchor=anchor)
T((800,120),'NOT A CAPPER.','permanent-marker.ttf',44,WH)
T((800,215),'I BET DIMES','permanent-marker.ttf',84,WH)
T((800,345),'5 OF 6','permanent-marker.ttf',150,G,glow_c=(60,140,30))
T((800,455),'FIRST BASKETS HIT','anton.ttf',62,WH)
d=ImageDraw.Draw(img); d.line((470,500,1130,494),fill=G,width=6)
T((800,545),'SUNDAY 11/15 • NBA','anton.ttf',30,GR)
picks=[('MAXEY','+700'),('DONCIC','+350'),('GARLAND','+490'),('WEMBY','+320'),('A. MITCHELL','+700')]
x0=210; step=295
for i,(n,o) in enumerate(picks):
    cx=x0+i*step; d=ImageDraw.Draw(img)
    d.rounded_rectangle((cx-125,600,cx+125,735),radius=16,fill=(16,22,17),outline=GD,width=3)
    T((cx,632),'✓ WIN' if False else 'WIN','anton.ttf',26,G)
    T((cx,672),n,'anton.ttf',34,WH)
    T((cx,712),o,'anton.ttf',30,G)
T((800,790),'TOP 1% ON PIKKIT  •  BANKROLL $78 TO $201','anton.ttf',40,G,glow_c=(30,90,20))
T((800,850),'DIME  •  SMART  •  REAL','anton.ttf',26,GR)
img.save('/home/user/Defined-Risk-Trading/posts/media/2026-11-16-x/x-first-basket-1115.png')
