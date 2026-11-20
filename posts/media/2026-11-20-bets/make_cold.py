from PIL import Image, ImageDraw, ImageFont
W,H=1600,900
img=Image.new("RGB",(W,H),(13,17,28))
d=ImageDraw.Draw(img)
def f(sz,b=True):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,sz)
# ice gradient bar top
for x in range(W):
    c=int(120+100*x/W); d.line([(x,0),(x,14)],fill=(60,c,255))
d.text((80,70),"NBA FIRST BASKET",font=f(40),fill=(110,190,255))
d.text((80,125),"3 DAYS COLD",font=f(150),fill=(235,245,255))
d.text((84,300),"Every first basket bet missed. Tue, Wed, Thu.",font=f(40,False),fill=(170,185,210))
days=[("TUE 11/17","0 HITS"),("WED 11/18","0 HITS"),("THU 11/19","0 HITS")]
x0,y0,bw,bh,gap=80,410,450,230,45
for i,(day,res) in enumerate(days):
    x=x0+i*(bw+gap)
    d.rounded_rectangle([x,y0,x+bw,y0+bh],radius=26,fill=(24,34,56),outline=(70,140,230),width=4)
    tw=d.textlength(day,font=f(44)); d.text((x+(bw-tw)/2,y0+35),day,font=f(44),fill=(140,200,255))
    tw=d.textlength(res,font=f(78)); d.text((x+(bw-tw)/2,y0+110),res,font=f(78),fill=(255,95,95))
d.text((80,700),"Play list: 0 for 8. Expected about 3.",font=f(46),fill=(235,245,255))
d.text((80,770),"Model's still on track over the season. Variance bites. Smaller stakes, same process.",font=f(32,False),fill=(170,185,210))
img.save("first-basket-3-days-cold.png")
