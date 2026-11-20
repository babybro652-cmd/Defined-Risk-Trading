import sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
random.seed(7)
HANDLE = sys.argv[1] if len(sys.argv) > 1 else "@YOURHANDLE"
W,H = 1600,900
BLACK=(8,9,8); G=(124,214,40); GL=(160,255,70); WHITE=(236,240,232); GREY=(140,146,138); DK=(22,24,22)
FI="/usr/share/fonts/opentype/inter/"
def f(sz,style="Black-Italic"):
    return ImageFont.truetype({"Black-Italic":FI+"Inter-BlackItalic.otf","Black":FI+"Inter-Black.otf","XB":FI+"Inter-ExtraBold.otf","XBI":FI+"Inter-ExtraBoldItalic.otf"}[style], sz)
img = Image.new("RGB",(W,H),BLACK); d = ImageDraw.Draw(img)
# grainy noise
noise = Image.effect_noise((W,H), 22).convert("RGB")
img = ImageChops.add(img, ImageChops.multiply(noise, Image.new("RGB",(W,H),(40,40,40))))
d = ImageDraw.Draw(img)
# stadium lights arc
for i in range(90):
    t = math.pi*(0.08+0.84*i/89); x = 800+760*math.cos(t)*1.05; y = 150-110*math.sin(t)
    d.ellipse([x-3,y-3,x+3,y+3], fill=(200,205,200))
lights = img.filter(ImageFilter.GaussianBlur(6)); img = ImageChops.lighter(img, lights); d = ImageDraw.Draw(img)
# green glow behind player
glow = Image.new("RGB",(W,H),(0,0,0)); g = ImageDraw.Draw(glow)
g.ellipse([880,170,1480,830], fill=(50,110,10)); glow = glow.filter(ImageFilter.GaussianBlur(120))
img = ImageChops.lighter(img, glow); d = ImageDraw.Draw(img)
# green splatter / smoke specks
spl = Image.new("RGB",(W,H),(0,0,0)); s = ImageDraw.Draw(spl)
for _ in range(900):
    side = random.choice([0,1,1,2])
    x = random.gauss(60 if side==0 else (1560 if side==2 else 1180), 120 if side!=1 else 260)
    y = random.uniform(0,H) if side!=1 else random.gauss(820,60)
    r = random.choice([1,1,2,2,3,5])
    s.ellipse([x-r,y-r,x+r,y+r], fill=random.choice([G,GL,(70,140,20)]))
for _ in range(14):
    x=random.choice([random.uniform(0,140),random.uniform(1460,1600)]); y=random.uniform(0,H)
    s.line([(x,y),(x+random.uniform(-90,90),y+random.uniform(-40,40))], fill=G, width=random.randint(6,16))
img = ImageChops.lighter(img, spl); img = ImageChops.lighter(img, spl.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(img)
# ---- player silhouette, hands on head ----
cx=1180; S=(16,17,16)
def player(dr, fill, jersey, grow=0):
    e=grow
    dr.polygon([(cx-70-e,600),(cx-20+e,600),(cx-40+e,770),(cx-95-e,770)], fill=fill)
    dr.polygon([(cx+20-e,600),(cx+70+e,600),(cx+95+e,770),(cx+40-e,770)], fill=fill)
    dr.ellipse([cx-125-e,752-e,cx-30+e,782+e], fill=fill); dr.ellipse([cx+30-e,752-e,cx+125+e,782+e], fill=fill)
    dr.polygon([(cx-95-e,470),(cx+95+e,470),(cx+112+e,625+e),(cx+10,625+e),(cx,595),(cx-10,625+e),(cx-112-e,625+e)], fill=jersey)
    dr.polygon([(cx-105-e,262-e),(cx+105+e,262-e),(cx+95+e,482),(cx-95-e,482)], fill=jersey)
    dr.rectangle([cx-24-e,222,cx+24+e,272], fill=fill)
    dr.ellipse([cx-62-e,118-e,cx+62+e,250+e], fill=fill)
    for sg in (-1,1):
        sh=(cx+sg*100,285); el=(cx+sg*205,175); hd=(cx+sg*45,140)
        dr.line([sh,el], fill=fill, width=46+2*e); dr.line([el,hd], fill=fill, width=40+2*e)
        for (px,py),r in ((el,23),(hd,26),(sh,30)):
            dr.ellipse([px-r-e,py-r-e,px+r+e,py+r+e], fill=fill)
rim = Image.new("RGB",(W,H),(0,0,0)); player(ImageDraw.Draw(rim), GL, GL, grow=5)
img = ImageChops.lighter(img, rim.filter(ImageFilter.GaussianBlur(14)))
d = ImageDraw.Draw(img); player(d, GL, GL, grow=3); player(d, S, (28,30,28))
d.polygon([(cx-40,262),(cx+40,262),(cx,308)], fill=BLACK)
d.line([(cx-95,482),(cx+95,482)], fill=G, width=5)
num="0"; tw=d.textlength(num,font=f(140,"Black")); d.text((cx-tw/2,300),num,font=f(140,"Black"),fill=G)
for a in (-62,-32,32,62):
    t=math.radians(a-90); d.line([(cx+120*math.cos(t),150+120*math.sin(t)),(cx+170*math.cos(t),150+170*math.sin(t))], fill=GL, width=9)
# dark ball rolling away
bx,by,br=1440,725,50
d.ellipse([bx-br,by-br,bx+br,by+br], fill=(35,37,35), outline=G, width=3)
for a in (0,):
    d.line([(bx-br,by),(bx+br,by)],fill=BLACK,width=4); d.line([(bx,by-br),(bx,by+br)],fill=BLACK,width=4)
d.arc([bx-br-30,by-br,bx+br-60,by+br],-60,60,fill=BLACK,width=4); d.arc([bx-br+60,by-br,bx+br+30,by+br],120,240,fill=BLACK,width=4)
for i in range(3): d.line([(bx-br-25-i*28,by+18-i*10),(bx-br-5-i*28,by+18-i*10)],fill=GREY,width=4)
# ---- text ----
d.text((72,62),"NBA FIRST BASKET",font=f(40),fill=GREY)
d.text((66,110),"3 DAYS",font=f(168),fill=WHITE)
cold = Image.new("RGB",(W,H),(0,0,0)); cd=ImageDraw.Draw(cold); cd.text((60,290),"COLD.",font=f(190),fill=G)
img = ImageChops.lighter(img, cold.filter(ImageFilter.GaussianBlur(16))); d=ImageDraw.Draw(img)
d.text((60,290),"COLD.",font=f(190),fill=G)
# brush underline
for k in range(5):
    d.line([(70+k*3,525+k*2),(640-k*6,512+k*2)], fill=G, width=4)
y=566
for day in ("TUE 11/17","WED 11/18","THU 11/19"):
    d.rounded_rectangle([70,y,600,y+54],radius=10,fill=DK,outline=G,width=2)
    d.text((92,y+9),day,font=f(30,"XB"),fill=WHITE)
    t="0 HITS"; tw=d.textlength(t,font=f(30,"XBI")); d.text((578-tw,y+9),t,font=f(30,"XBI"),fill=GL)
    y+=66
d.text((70,776),"PLAY LIST 0 FOR 8. EXPECTED ABOUT 3.",font=f(28,"XBI"),fill=WHITE)
d.text((70,816),"Same process. Smaller stakes. Bounce back loading.",font=f(26,"XB"),fill=GREY)
# handle
hf=f(32,"XBI"); tw=d.textlength(HANDLE,font=hf)
d.rounded_rectangle([W-tw-100,H-80,W-40,H-30],radius=25,fill=G); d.text((W-tw-70,H-76),HANDLE,font=hf,fill=BLACK)
img.save("first-basket-3-days-cold-v3.png")
