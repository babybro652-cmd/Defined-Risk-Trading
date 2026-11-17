import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='TUE 11/17'; OUT='analysis/nba/out/charts/plan_2026-11-17.png'
fb=[('DET @ SA','8:00','SA 85%',[('Wembanyama','+323'),('Fox','+714'),('Castle','+888')],'Duren, D. Robinson OUT; Collins jumps'),
    ('UTAH @ LAC','10:30','LAC 77%',[('Garland','+554'),('Lopez','+563'),('Bamba','+771')],'Hayes, Markkanen OUT; Bamba jumps')]
pars=[('Wembanyama + Garland','+2,665'),('Wembanyama + Lopez','+2,704'),('Fox + Garland','+5,222'),('Fox + Lopez','+5,296')]
fig=plt.figure(figsize=(7.2,12.8),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,178); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,173,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,168.5,'Budget $100  •  Straights $96  •  2-leg parlays $2  •  Spare $2',color=MUTED,fontsize=8.6,va='center')
ax.text(5,164.8,'2 games at 70%+ tip. Skipped: NY@TOR 51%, POR@MIN 56%, CHA@LAL 52%',color=MUTED,fontsize=8.4,va='center')
ax.text(5,160,'FIRST BASKET  (top 3 straights, $16 each)',color=GOLD,fontsize=11,weight='bold',va='center')
y=156
for g,t,tip,picks,note in fb:
    h=22; card(4,y-h,92,h)
    ax.text(7,y-3.5,g,color=TXT,fontsize=12,weight='bold',va='center')
    ax.text(40,y-3.5,t+' PM',color=MUTED,fontsize=9.5,va='center')
    ax.text(93,y-3.5,'Tip '+tip,color=GREEN,fontsize=10,weight='bold',va='center',ha='right')
    for i,(n,o) in enumerate(picks):
        yy=y-9.5-i*3.6
        ax.text(9,yy,f'#{i+1}',color=GOLD if i==0 else BLUE,fontsize=9.5,weight='bold',va='center')
        ax.text(16,yy,n,color=TXT,fontsize=10,va='center')
        ax.text(93,yy,'fair '+o,color=MUTED,fontsize=9.5,va='center',ha='right')
    ax.text(9,y-h+2.3,note,color=RED,fontsize=8.2,va='center',style='italic')
    y-=h+3
ax.text(5,y-1,'2-LEG PARLAYS  (top 2 per game, $0.50 each)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=21; card(4,y-h,92,h)
for i,(n,f) in enumerate(pars):
    yy=y-4-i*4.4
    ax.text(9,yy,n,color=TXT,fontsize=10.5,va='center'); ax.text(93,yy,'fair '+f,color=MUTED,fontsize=9.5,va='center',ha='right')
ax.text(5,y-h-4,'Stake check: FanDuel was $63.21 last night. If short, scale all six straights evenly.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-h-8.5,'Recheck lineups 30 min before tip. First basket is mostly noise.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
