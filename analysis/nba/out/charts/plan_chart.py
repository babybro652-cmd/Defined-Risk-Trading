import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='WED 11/18 ($4 PLAN)'; OUT='analysis/nba/out/charts/plan_2026-11-18.png'
fb=[('PHI @ ORL','7:00','ORL 72%',[('Wendell Carter Jr.','+527'),('Franz Wagner','+636'),('Joel Embiid','+759')],'Banchero OUT; J. Brown OUT; Carter jumps vs Embiid'),
    ('CHI @ BKN','7:30','BKN 76%',[('Michael Porter Jr.','+573'),("Day'Ron Sharpe",'+616'),('Julius Randle','+622')],'Caleb Wilson OUT; Sharpe jumps vs Jalen Smith'),
    ('DET @ NO','8:00','DET 77%',[('John Collins','+506'),('Daniss Jenkins','+696'),('Ausar Thompson','+878')],'Cade Q (knee): swapped out for A. Thompson; Duren OUT')]
meth=[('Julius Randle - Other (CHI@BKN)','$0.50','+1,430','+1,736'),('Joel Embiid - Other (PHI@ORL)','$0.10','+1,525','+1,850'),('Daniss Jenkins - 3PT (DET@NO)','$0.10','+1,883','+2,280')]
pars=[('#1s: Carter + Porter Jr.','+4,122'),('#1s: Carter + Collins','+3,702'),('#1s: Porter Jr. + Collins','+3,984'),
      ('#2s: Wagner + Sharpe','+5,171'),('#2s: Wagner + Jenkins','+5,759'),('#2s: Sharpe + Jenkins','+5,603')]
fig=plt.figure(figsize=(7.2,14.4),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $4.00 of $4  •  Straights $2.70  •  2-leg $0.60  •  Method $0.70',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'Tip 70%+ games. First games listed 7:10 PM on FanDuel.',color=MUTED,fontsize=8.4,va='center')
ax.text(5,182,'FIRST BASKET  (top 3 straights, $0.30 each)',color=GOLD,fontsize=11,weight='bold',va='center')
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
ax.text(5,y-1,'2-LEG PARLAYS  (#1 with #1, #2 with #2, $0.10 each)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=len(pars)*3.9+2; card(4,y-h,92,h)
for i,(n,f) in enumerate(pars):
    yy=y-3.5-i*3.9
    ax.text(9,yy,n,color=TXT,fontsize=10.5,va='center'); ax.text(93,yy,'fair '+f,color=MUTED,fontsize=9.5,va='center',ha='right')
y=y-h-4
ax.text(5,y-1,'FIRST BASKET METHOD  (longshots, take-at or longer)',color=GOLD,fontsize=11,weight='bold',va='center')
y-=5; h=len(meth)*4.3+3; card(4,y-h,92,h)
for i,(n,st,f,t) in enumerate(meth):
    yy=y-3.8-i*4.3
    ax.text(9,yy,n,color=TXT,fontsize=9.6,va='center'); ax.text(62,yy,st,color=GREEN,fontsize=9.2,va='center',ha='right')
    ax.text(93,yy,'fair '+f+' / take '+t,color=MUTED,fontsize=8.6,va='center',ha='right')
y=y-h-3.5
ax.text(5,y,'FanDuel Method of First Basket = player + method. Other = jumper, floater, hook, tip.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-4,'Dropped ($4 balance): 6 other 2-legs, Sharpe - Layup, UTAH@LAL.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Wade (PHI) Q. Recheck 30 min before tip. Mostly noise.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
