import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='WED 11/25 (6:35 PM update)'; OUT='analysis/nba/out/charts/plan_2026-11-25.png'
fb=[('CHI @ CHA','7:00','CHI 72%',[('Nic Claxton  $0.30','+549 / +679'),('Buddy Hield  $0.20','+668 / +822'),('Naz Reid  $0.20','+767 / +940')],'Claxton vs Diabate. J. Smith out of the five. Place only if Claxton starts'),
    ('CLE @ NY','7:30','CLE 73%',[('Jarrett Allen  $0.50','+483 / +599'),('Donovan Mitchell  $0.30','+733 / +899'),('Karl-Anthony Towns (Prob)  $0.20','+735 / +903')],'Allen vs Towns (probable). Brunson downgraded to Q; Mobley OUT'),
    ('SAC @ GS','10:00','GS 90%',[('Charles Bassey  $0.50','+454 / +565'),('Brandin Podziemski  $0.30','+630 / +777'),('Yaxel Lendeborg (Q)  $0.20','+673 / +827')],'Bassey vs Sabonis. Bassey tip sample small. LaVine, Lendeborg Q; Curry OUT'),
    ('SA @ POR','10:00','SA 88%',[('Victor Wembanyama (Q)  $0.50','+318 / +401'),('Devin Vassell  $0.30','+705 / +865'),("De'Aaron Fox (Q)  $0.20",'+733 / +900')],'Wemby vs Clingan. Wemby (back), Fox Q: if Wemby sits, skip game')]
meth=[('Victor Wembanyama - Dunk','$0.50','+1,050','+1,280'),('Charles Bassey - Other','$0.20','+1,136','+1,383'),('Sam Merrill - Three Point Field Goal','$0.20','+1,403','+1,704'),('Jarrett Allen - Other','$0.10','+1,618','+1,961')]
fig=plt.figure(figsize=(7.2,12.3),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(35,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $4.70  •  12 straights ($0.50 / $0.30 / $0.20)  •  Method $1.00',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'Tip 70%+ only. Skip PHI 56, MIN 54, LAC 65, BKN 62, HOU 54.',color=MUTED,fontsize=8.4,va='center')
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
    ax.text(9,yy,n,color=TXT,fontsize=9.6,va='center'); ax.text(66,yy,st,color=GREEN,fontsize=9.2,va='center',ha='right')
    ax.text(93,yy,'fair '+f+' / take '+t,color=MUTED,fontsize=8.6,va='center',ha='right')
y=y-h-3.5
ax.text(5,y,'FanDuel Method of First Basket = player + method. Other = jumper, floater, hook, tip.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-4,'Preliminary. CLE@NY rechecked 7:10; west games ~9:30 PM. Place off the rerun.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Bet only at take-at or longer. First basket is mostly noise; small stakes.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
