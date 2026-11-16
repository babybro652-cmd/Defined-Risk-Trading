import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
fb=[('ORL @ BOS','7:00','ORL 76%',[('Carter','+502'),('Wagner','+599'),('Tatum','+803')],''),
    ('CHI @ CLE','7:00','CLE 87%',[('Allen','+364'),('Watson (Q)','+632'),('Mitchell','+658')],'Watson void if he sits'),
    ('HOU @ MIA','7:30','MIA 73%',[('Adebayo','+359'),('Giannis','+527'),('Sengun','+705')],''),
    ('PHX @ DEN','9:00','DEN 71%',[('Jokic','+376'),('Murray','+588'),('C. Johnson','+947')],'Softest tip: outside sources 56-72%')]
th=[('Podziemski','GS @ NO 8:00','47%','+113','+155'),('Tatum','ORL @ BOS 7:00','44%','+127','+173'),('Kyshawn George','MEM @ WSH 7:00','43%','+133','+179')]
fig=plt.figure(figsize=(7.2,12.8),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,178); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,173,'NBA PLAN  •  MON 11/16',color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,168.5,'Budget $100  •  First basket $88.80  •  3s parlay $1  •  Spare $10.20',color=MUTED,fontsize=8.6,va='center')
ax.text(5,162,'FIRST BASKET  (top 3 straights, $6 each)',color=GOLD,fontsize=11,weight='bold',va='center')
y=158
for g,t,tip,picks,note in fb:
    h=22 if note else 19; card(4,y-h,92,h)
    ax.text(7,y-3.5,g,color=TXT,fontsize=12,weight='bold',va='center')
    ax.text(40,y-3.5,t+' PM',color=MUTED,fontsize=9.5,va='center')
    ax.text(93,y-3.5,'Tip '+tip,color=GREEN,fontsize=10,weight='bold',va='center',ha='right')
    for i,(n,o) in enumerate(picks):
        yy=y-9.5-i*3.6
        ax.text(9,yy,f'#{i+1}',color=GOLD if i==0 else BLUE,fontsize=9.5,weight='bold',va='center')
        ax.text(16,yy,n,color=TXT,fontsize=10,va='center')
        ax.text(93,yy,'fair '+o,color=MUTED,fontsize=9.5,va='center',ha='right')
    if note: ax.text(9,y-h+2.3,note,color=RED,fontsize=8.2,va='center',style='italic')
    y-=h+3
ax.text(5,y-1,'Parlays: top 2 per game  •  24 two-leg $0.50  •  48 three/four-leg $0.10',color=MUTED,fontsize=8.4,va='center')
y-=7
ax.text(5,y,'3+ THREES LONGSHOT  (3 legs, $1)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=4; h=27; card(4,y-h,92,h)
ax.text(9,y-3,'Player',color=MUTED,fontsize=8.5,va='center'); ax.text(45,y-3,'Game',color=MUTED,fontsize=8.5,va='center')
ax.text(72,y-3,'Chance',color=MUTED,fontsize=8.5,va='center',ha='center'); ax.text(93,y-3,'Take at',color=MUTED,fontsize=8.5,va='center',ha='right')
for i,(n,g,p,f,tk) in enumerate(th):
    yy=y-8.5-i*4.4
    ax.text(9,yy,n,color=TXT,fontsize=10.5,weight='bold',va='center'); ax.text(45,yy,g,color=MUTED,fontsize=9,va='center')
    ax.text(72,yy,p,color=GREEN,fontsize=10,va='center',ha='center'); ax.text(93,yy,tk,color=TXT,fontsize=10,va='center',ha='right')
ax.text(9,y-h+3.5,'Parlay fair +1,024 (9%, about 1 in 11)  •  take +1,137 or longer',color=GOLD,fontsize=9,va='center',weight='bold')
ax.text(5,y-h-4,'Backups: Lillard 45% (take +164), Powell 49% (+145), Murray for a shorter parlay',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-h-8.5,'Lineup check 6:25 PM. Small stakes: first basket is mostly noise.',color=MUTED,fontsize=8.2,va='center')
fig.savefig('analysis/nba/out/charts/plan_2026-11-16.png',facecolor=BG)
