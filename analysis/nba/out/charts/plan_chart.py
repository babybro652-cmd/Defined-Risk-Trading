import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='TUE 11/17'; OUT='analysis/nba/out/charts/plan_2026-11-17.png'
fb=[('DET @ SA','8:00','SA 85%',[('Wembanyama','+323'),('Fox','+714'),('Castle','+888')],'Duren, D. Robinson, I. Joe OUT; Collins jumps'),
    ('UTAH @ LAC','10:30','LAC 77%',[('Garland','+554'),('Lopez','+563'),('Bamba','+771')],'Hayes, Markkanen OUT; Bamba jumps')]
meth=[('DET@SA: Dunk','$1','+577','+712'),('DET@SA: Free throw','$0.50','+600','+740'),('Wembanyama FB by dunk','$1','+1,146','+1,395'),('UTAH@LAC: Dunk','$0.50','+830','+1,016'),('Bamba FB by dunk','$0.50','+2,303','+2,784')]
pars=[('Wembanyama + Garland','+2,665'),('Wembanyama + Lopez','+2,704'),('Fox + Garland','+5,222'),('Fox + Lopez','+5,296')]
fig=plt.figure(figsize=(7.2,11.2),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(44,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $35.50 of $36  •  Straights $30  •  Method $3.50  •  2-leg $2',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'7 PM recheck: no changes. Skipped: NY@TOR 51%, POR@MIN 56%, CHA@LAL 52%',color=MUTED,fontsize=8.4,va='center')
ax.text(5,182,'FIRST BASKET  (top 3 straights, $5 each)',color=GOLD,fontsize=11,weight='bold',va='center')
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
        ax.text(93,yy,'fair '+o,color=MUTED,fontsize=9.5,va='center',ha='right')
    ax.text(9,y-h+2.3,note,color=RED,fontsize=8.2,va='center',style='italic')
    y-=h+3
ax.text(5,y-1,'2-LEG PARLAYS  (top 2 per game, $0.50 each)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=21; card(4,y-h,92,h)
for i,(n,f) in enumerate(pars):
    yy=y-4-i*4.4
    ax.text(9,yy,n,color=TXT,fontsize=10.5,va='center'); ax.text(93,yy,'fair '+f,color=MUTED,fontsize=9.5,va='center',ha='right')
y=y-h-4
ax.text(5,y-1,'FIRST BASKET METHOD  (longshots, take-at or longer)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=25; card(4,y-h,92,h)
for i,(n,st,f,t) in enumerate(meth):
    yy=y-3.8-i*4.3
    ax.text(9,yy,n,color=TXT,fontsize=9.6,va='center'); ax.text(62,yy,st,color=GREEN,fontsize=9.2,va='center',ha='right')
    ax.text(93,yy,'fair '+f+' / take '+t,color=MUTED,fontsize=8.6,va='center',ha='right')
y=y-h-3.5
ax.text(5,y,'Method est: DET@SA dunk 15%, FT 14% (league 10%, 9%); UTAH@LAC near league.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-4,'FanDuel $39.41 at 12:22 PM, $1 on Rutgers. Plan leaves $3.91.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Recheck lineups 30 min before tip. First basket is mostly noise.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
