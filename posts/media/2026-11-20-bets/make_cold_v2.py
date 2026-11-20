import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HANDLE = sys.argv[1] if len(sys.argv) > 1 else "@YOURHANDLE"
W,H = 1600,900
BLACK=(10,10,10); ORANGE=(204,85,0); ORANGE2=(255,122,26); DARK=(26,20,16); CREAM=(245,236,225); GREY=(150,140,130)
img = Image.new("RGB",(W,H),BLACK)
d = ImageDraw.Draw(img)
def f(sz,b=True):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
# spotlight glow behind player
glow = Image.new("RGB",(W,H),BLACK); g = ImageDraw.Draw(glow)
for r in range(520,0,-8):
    c = int(70*(1-r/520))
    g.ellipse([1180-r,470-r,1180+r,470+r], fill=(c, int(c*0.4), 0))
img = Image.blend(img, glow, 1.0); d = ImageDraw.Draw(img)
# court floor + 3pt arc
d.rectangle([0,760,W,H], fill=(30,18,8))
d.arc([620,640,1740,1180], 180, 360, fill=ORANGE, width=6)
d.line([(0,760),(W,760)], fill=ORANGE, width=4)
# diagonal speed slashes
for i in range(6):
    x = 760 + i*40
    d.polygon([(x,0),(x+14,0),(x-240,760),(x-254,760)], fill=(40,22,8))
# ---- player silhouette (hands on head), centered x=1180 ----
cx = 1180; S = (18,18,18)  # silhouette fill
J = ORANGE  # jersey
# legs
d.polygon([(cx-70,600),(cx-20,600),(cx-40,760),(cx-95,760)], fill=S)
d.polygon([(cx+20,600),(cx+70,600),(cx+95,760),(cx+40,760)], fill=S)
d.ellipse([cx-120,742,cx-30,772], fill=S); d.ellipse([cx+30,742,cx+120,772], fill=S)
# shorts
d.polygon([(cx-95,470),(cx+95,470),(cx+110,620),(cx+10,620),(cx,590),(cx-10,620),(cx-110,620)], fill=J)
d.line([(cx-100,560),(cx-108,615)], fill=BLACK, width=6); d.line([(cx+100,560),(cx+108,615)], fill=BLACK, width=6)
# torso / jersey
d.polygon([(cx-105,265),(cx+105,265),(cx+95,480),(cx-95,480)], fill=J)
d.polygon([(cx-40,265),(cx+40,265),(cx,310)], fill=BLACK)  # v-neck
num="0"; tw=d.textlength(num,font=f(130)); d.text((cx-tw/2,320),num,font=f(130),fill=BLACK)
# neck + head (tilted down)
d.rectangle([cx-24,225,cx+24,270], fill=S)
d.ellipse([cx-62,120,cx+62,250], fill=S)
# arms up, elbows out, hands on head
for sgn in (-1,1):
    sh=(cx+sgn*100,285); el=(cx+sgn*205,175); hd=(cx+sgn*45,140)
    d.line([sh,el], fill=S, width=46); d.line([el,hd], fill=S, width=40)
    d.ellipse([el[0]-23,el[1]-23,el[0]+23,el[1]+23], fill=S)
    d.ellipse([hd[0]-28,hd[1]-24,hd[0]+28,hd[1]+24], fill=S)
    d.ellipse([sh[0]-30,sh[1]-30,sh[0]+30,sh[1]+30], fill=S)
# frustration marks
for a in (-60,-30,30,60):
    r1,r2 = 120,165; t=math.radians(a-90)
    d.line([(cx+r1*math.cos(t),150+r1*math.sin(t)),(cx+r2*math.cos(t),150+r2*math.sin(t))], fill=ORANGE2, width=8)
# rolling-away ball
bx,by,br=1440,705,52
d.ellipse([bx-br,by-br,bx+br,by+br], fill=ORANGE)
d.arc([bx-br,by-br,bx+br,by+br],0,360,fill=BLACK,width=4)
d.line([(bx-br,by),(bx+br,by)],fill=BLACK,width=4); d.line([(bx,by-br),(bx,by+br)],fill=BLACK,width=4)
d.arc([bx-br-30,by-br,bx+br-60,by+br],-60,60,fill=BLACK,width=4); d.arc([bx-br+60,by-br,bx+br+30,by+br],120,240,fill=BLACK,width=4)
for i in range(3): d.line([(bx-br-30-i*28,by+20-i*10),(bx-br-10-i*28,by+20-i*10)],fill=GREY,width=4)
# ---- text block (left) ----
d.rectangle([70,72,78,190], fill=ORANGE)
d.text((96,70),"NBA FIRST BASKET",font=f(38),fill=ORANGE2)
d.text((96,118),"WATCH",font=f(38),fill=GREY)
d.text((70,205),"3 DAYS",font=f(150),fill=CREAM)
d.text((70,365),"COLD.",font=f(150),fill=ORANGE)
y=560
for day in ("TUE 11/17","WED 11/18","THU 11/19"):
    d.rounded_rectangle([70,y,560,y+52],radius=10,fill=DARK,outline=ORANGE,width=3)
    d.text((90,y+8),day,font=f(30),fill=CREAM)
    t="0 HITS"; tw=d.textlength(t,font=f(30)); d.text((540-tw,y+8),t,font=f(30),fill=ORANGE2)
    y+=64
d.text((70,770),"Play list 0 for 8. Expected about 3.",font=f(30),fill=CREAM)
d.text((70,812),"Same process. Smaller stakes. Bounce back loading.",font=f(26,False),fill=GREY)
# handle bottom right
tw=d.textlength(HANDLE,font=f(34)); d.rounded_rectangle([W-tw-110,H-82,W-40,H-30],radius=26,fill=ORANGE)
d.text((W-tw-75,H-78),HANDLE,font=f(34),fill=BLACK)
img.save("first-basket-3-days-cold-v2.png")
