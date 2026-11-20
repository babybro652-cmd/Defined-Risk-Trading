import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
DATE='THU 11/19 ($9.40 PLAN)'; OUT='analysis/nba/out/charts/plan_2026-11-19.png'
fb=[('GS @ MEM','8:00','GS 75%',[('Yaxel Lendeborg','+649'),('Brandin Podziemski','+670'),('Isaiah Stewart (Q)','+735')],'Curry, Green OUT; Edey OUT; Stewart Q illness (void if sits)'),
    ('NY @ MIN','8:00','MIN 57%*',[('Jalen Brunson','+626'),('Karl-Anthony Towns','+636'),('Jaden McDaniels','+718')],'*Exception: model team top-2 NY 4/6, MIN 5/7. Edwards OUT, Kuminga Q'),
    ('LAC @ SA','8:00','SA 83%',[('Victor Wembanyama','+314'),("De'Aaron Fox",'+710'),('Devin Vassell','+838')],'Ingram, Beal OUT; Harper, Harris OUT. StarTool SA 89%')]
meth=[('Victor Wembanyama - Dunk','$0.50','+1,054','+1,285'),('LJ Cryer - 3PT','$0.20','+1,211','+1,473'),('Jalen Brunson - Other','$0.20','+1,248','+1,518'),('LaMelo Ball - 3PT','$0.10','+1,420','+1,724')]
pars=[('Lendeborg + Brunson','+5,336'),('Lendeborg + Towns','+5,412'),('Podziemski + Brunson','+5,491'),('Podziemski + Towns','+5,569'),
      ('Lendeborg + Wembanyama','+3,002'),('Lendeborg + Fox','+5,965'),('Podziemski + Wembanyama','+3,090'),('Podziemski + Fox','+6,138'),
      ('Brunson + Wembanyama','+2,905'),('Brunson + Fox','+5,776'),('Towns + Wembanyama','+2,947'),('Towns + Fox','+5,858')]
fig=plt.figure(figsize=(7.2,16.6),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(-30,200); ax.axis('off')
def card(x,y,w,h): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.4,rounding_size=1.5',fc=CARD,ec='#2c3850',lw=1))
ax.text(5,195,'NBA PLAN  •  '+DATE,color=TXT,fontsize=17,weight='bold',va='center')
ax.text(5,190.5,'Plan $9.40  •  Straights $7.20  •  2-leg $1.20  •  Method $1.00',color=MUTED,fontsize=8.6,va='center')
ax.text(5,186.8,'Tip 70%+ games plus NY@MIN exception. All tip 8:00 (8:10 on FanDuel). Skip POR@MIL.',color=MUTED,fontsize=8.4,va='center')
ax.text(5,182,'FIRST BASKET  (top 3 straights, $0.80 each)',color=GOLD,fontsize=11,weight='bold',va='center')
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
ax.text(5,y-1,'2-LEG PARLAYS  (cross-game top 2, $0.10 each)',color=GOLD,fontsize=11,weight='bold',va='center')
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
ax.text(5,y-4,'StarTool has MEM 63% tip (old card: Bassey, Edey). Ours GS 75% with Horford.',color=MUTED,fontsize=8.2,va='center')
ax.text(5,y-8,'Recheck Stewart, Kuminga, Avdija at 7:30. Mostly noise; small stakes.',color=MUTED,fontsize=8.2,va='center')
fig.savefig(OUT,facecolor=BG)
