import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='SAT 11/21 (LINEUP RERUN 7:27 PM)'; OUT='analysis/nba/out/charts/plan_2026-11-21.png'
fb=[('LAC @ DAL','8:00','LAC 78%',[('Brook Lopez','+581 / +717'),('Darius Garland','+603 / +743'),('Cooper Flagg','+695 / +854')],'Lopez vs Gafford. Marshall starts for P.J. Washington'),
    ('NO @ SA','8:00','SA 97%',[('Victor Wembanyama','+289 / +366'),("De'Aaron Fox",'+670 / +824'),('Devin Vassell','+733 / +899')],'Harper, T. Harris OUT. Murray, Mathurin OUT. Wemby likely short: skip under +366')]
meth=[('Victor Wembanyama - Dunk','$0.50','+964','+1,176'),('Brook Lopez - Other','$0.20','+1,678','+2,034'),('Cooper Flagg - Other','$0.20','+1,706','+2,067'),("De'Aaron Fox - Other",'$0.10','+1,908','+2,310')]
fig=plt.figure(figsize=(7.2,9.0),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(80,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $3.40  •  6 straights $0.40 = $2.40  •  Method $1.00  •  balance $10.97',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'Tip 70%+ only. Skip POR@NY 74 (Bridges jumps; NY 67 if Drummond), MEM@MIN 51, BOS@SAC 53.',color=MUTED,fontsize=8.4,va='center')
ax.text(5,182,'FIRST BASKET  (top 3, $0.40 each; fair / take-at)',color=GOLD,fontsize=11,weight='bold',va='center')
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
ax.text(5,y-4,'7:27 PM rerun on NBA lineups (LAC, DAL, NO, SA still expected). Place off this list.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Bet only at take-at or longer. First basket is mostly noise; small stakes.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
