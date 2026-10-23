from PIL import Image, ImageDraw, ImageFont
import os
D=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1920
NAVY=(18,28,48); CARD=(28,42,70); WHITE=(240,242,246); MUTED=(150,165,190)
GREEN=(72,199,116); RED=(232,92,92); GOLD=(214,180,96)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s: ImageFont.truetype(p,s)
def base():
    im=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(im)
    d.text((W/2,1760),"DEFINED RISK TRADING",font=f(B,40),fill=MUTED,anchor="mm")
    d.line((340,1720,740,1720),fill=GOLD,width=3)
    return im,d
def c(d,y,t,font,fill=WHITE): d.text((W/2,y),t,font=font,fill=fill,anchor="mm")
slides=[]
# 1
im,d=base()
c(d,620,"WEEKLY RECAP",f(B,64),GOLD)
c(d,800,"6 ES trades",f(B,110))
c(d,930,"3 wins. 3 losses.",f(B,80))
c(d,1080,"2 contracts each, paper account",f(R,46),MUTED)
slides.append(im)
# 2 per trade
im,d=base()
c(d,330,"EVERY TRADE",f(B,64),GOLD)
rows=[("Tue","Long","+30.00",GREEN),("Tue","Short","-4.00",RED),("Tue","Short","+11.25",GREEN),
      ("Fri","Long","-3.50",RED),("Fri","Long","-4.25",RED),("Fri","Long","+22.50",GREEN)]
y=480
for day,side,pts,col in rows:
    d.rounded_rectangle((110,y-70,970,y+70),radius=24,fill=CARD)
    d.text((160,y),day,font=f(B,56),fill=MUTED,anchor="lm")
    d.text((330,y),side,font=f(B,56),fill=WHITE,anchor="lm")
    d.text((920,y),pts+" pts",font=f(B,56),fill=col,anchor="rm")
    y+=175
slides.append(im)
# 3 losses vs wins
im,d=base()
c(d,520,"LOSSES",f(B,64),RED)
c(d,650,"-11.75 pts total",f(B,84))
c(d,760,"Biggest loss: 4.25 pts",f(R,50),MUTED)
c(d,1000,"WINS",f(B,64),GREEN)
c(d,1130,"+63.75 pts total",f(B,84))
c(d,1240,"Biggest win: 30 pts",f(R,50),MUTED)
slides.append(im)
# 4 net
im,d=base()
c(d,560,"NET FOR THE WEEK",f(B,64),GOLD)
c(d,740,"+52 pts",f(B,140),GREEN)
c(d,910,"+$5,200",f(B,120),WHITE)
c(d,1060,"about +13R",f(B,72),WHITE)
c(d,1210,"2 ES, paper account, before commissions",f(R,42),MUTED)
slides.append(im)
# 5 lesson
im,d=base()
c(d,640,"The stops stayed small.",f(B,70))
c(d,760,"So 3 winners paid",f(B,70))
c(d,860,"for 3 losers",f(B,70))
c(d,960,"several times over.",f(B,70))
slides.append(im)
# 6 signoff
im,d=base()
c(d,760,"Define your risk.",f(B,84))
c(d,890,"Wait for your setup.",f(B,84))
slides.append(im)
for i,s in enumerate(slides,1): s.save(os.path.join(D,f"slide{i}.png"))
