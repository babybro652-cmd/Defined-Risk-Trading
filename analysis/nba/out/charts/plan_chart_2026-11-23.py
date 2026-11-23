import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='MON 11/23 (6:05 PM, expected fives)'; OUT='analysis/nba/out/charts/plan_2026-11-23.png'
fb=[('MIL @ TOR','7:30','TOR 72%',[('Scottie Barnes  $0.30','+496 / +615'),('Collin Murray-Boyles (DTD)  $0.20','+549 / +679'),('Allen Graves  $0.20','+783 / +960')],'Turner vs Murray-Boyles. TipProj says MIL jumper Sims: if Sims jumps, recheck'),
    ('CLE @ CHI','8:00','CLE 83%',[('Jarrett Allen  $0.30','+412 / +514'),('Donovan Mitchell  $0.20','+632 / +778'),('Peyton Watson  $0.20','+679 / +835')],'Allen vs J. Smith (DTD). Tyson OUT (ESPN) though feed lists him; Mobley OUT'),
    ('PHX @ NO','8:00','PHX 75%',[('Devin Booker  $0.30','+659 / +811'),('Jalen Green  $0.20','+671 / +825'),('Dillon Brooks  $0.20','+679 / +835')],'Ighodaro vs Missi. Zion DTD (in five); M. Williams OUT'),
    ('UTAH @ LAL','10:00','LAL 92%',[('Luka Doncic  $0.30','+267 / +340'),('Walker Kessler  $0.20','+565 / +698'),('Ziaire Williams  $0.20','+1016 / +1239')],'Bamba vs Kessler. Hayes, Markkanen, JJJ, Nurkic OUT; Reaves OUT'),
    ('SA @ SAC','10:00','SA 94%',[('Victor Wembanyama (DTD)  $0.30','+297 / +376'),("De'Aaron Fox (DTD)  $0.20",'+698 / +858'),('Devin Vassell  $0.20','+709 / +871')],'Wemby vs Sabonis. Wemby, Fox DTD: if Wemby sits, tip edge gone, skip')]
meth=[('Luka Doncic - Other','$0.50','+671','+825'),('Victor Wembanyama - Dunk','$0.20','+990','+1,208'),('Scottie Barnes - Other','$0.20','+1,030','+1,256'),('Walker Kessler - Dunk','$0.10','+1,179','+1,435')]
fig=plt.figure(figsize=(7.2,13.6),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(18,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $4.50  •  15 straights ($0.30 / $0.20 / $0.20)  •  Method $1.00  •  balance ~$10.97',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'Tip 70%+ only. Skip MEM 62, PHI 60, IND 59, MIN 53, LAC 66.',color=MUTED,fontsize=8.4,va='center')
ax.text(5,182,'FIRST BASKET  (top 3; fair / take-at)',color=GOLD,fontsize=11,weight='bold',va='center')
y=178
for g,t,tip,picks,note in fb:
    h=22; card(4,y-h,92,h)
    ax.text(7,y-3.5,g,color=TXT,fontsize=12,weight='bold',va='center')
    ax.text(40,y-3.5,t+' PM',color=MUTED,fontsize=9.5,va='center')
    ax.text(93,y-3.5,'Tip '+tip,color=GREEN,fontsize=10,weight='bold',va='center',ha='right')
    for i,(n,o) in enumerate(picks):
        yy=y-9.5-i*3.6
        ax.text(9,yy,f'#{i+1}',color=GOLD if i==0 else BLUE,fontsize=9.5,weight='bold',va='center')
        ax.text(16,yy,n,color=TXT,fontsize=10,va='center')
        ax.text(93,yy,o,color=MUTED,fontsize=9.5,va='center',ha='right')
    ax.text(9,y-h+2.3,note,color=RED,fontsize=8.2,va='center',style='italic')
    y-=h+3
ax.text(5,y-1,'FIRST BASKET METHOD  (longshots, take-at or longer)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=len(meth)*4.3+3; card(4,y-h,92,h)
for i,(n,st,f,t) in enumerate(meth):
    yy=y-3.8-i*4.3
    ax.text(9,yy,n,color=TXT,fontsize=9.6,va='center'); ax.text(62,yy,st,color=GREEN,fontsize=9.2,va='center',ha='right')
    ax.text(93,yy,'fair '+f+' / take '+t,color=MUTED,fontsize=8.6,va='center',ha='right')
y=y-h-3.5
ax.text(5,y,'FanDuel Method of First Basket = player + method. Other = jumper, floater, hook, tip.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-4,'Preliminary. Rerun after official lineups (~7:00 / 7:30 / 9:30 PM). Place off the rerun.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Bet only at take-at or longer. First basket is mostly noise; small stakes.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
