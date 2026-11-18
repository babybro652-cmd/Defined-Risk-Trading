"""Method longshots chart: how each game's first points are scored (est % and fair), bet picks highlighted.
Run from the repo root: python3 analysis/nba/out/charts/method_chart.py  (edit DATE / JSON / PICKS per slate)"""
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
DATE='WED 11/18'; JSON='analysis/nba/out/method_longshots_2026-11-18.json'; OUT='analysis/nba/out/charts/method_2026-11-18.png'
PICKS={('DET @ NO','ft'):'$0.50',('DET @ NO','dunk'):'$0.20',('PHI @ ORL','ft'):'$0.20'}
COMBO='Wendell Carter Jr. first basket by dunk: 4.7%, fair +2,015, take +2,437 ($0.10)'
PLAY={'PHI @ ORL','CHI @ BKN','DET @ NO'}
LEAGUE={'3':27.6,'layup':25.0,'dunk':10.4,'j2':28.0,'ft':8.9}
COLS=[('3','3-pointer'),('layup','Layup'),('dunk','Dunk'),('j2','Jump shot (2)'),('ft','Free throw')]
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; GREEN='#4cd38a'
def am(p): d=1/p; return '+{:,}'.format(round((d-1)*100)) if d>=2 else '-%d'%round(100/(d-1))
g=json.load(open(JSON))['games']
n=len(g)+4; lo=n-1.9-0.95-len(g)*0.62-1.0
fig=plt.figure(figsize=(8,0.75*(n-lo)),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(lo,n); ax.axis('off')
ax.text(3,n-0.55,'FIRST BASKET METHOD  •  '+DATE,color=TXT,fontsize=15,weight='bold',va='center')
ax.text(3,n-1.15,'How the game\'s first points are scored (FT counts). Est % and fair. Gold = bet (take-at = fair x1.2 or longer)',color=MUTED,fontsize=7.4,va='center')
xs=[33,47,61,75,89]; y=n-1.9
ax.text(3,y,'Game',color=MUTED,fontsize=8.5,weight='bold',va='center')
for (k,lab),x in zip(COLS,xs): ax.text(x,y,f'{lab}\n(lg {LEAGUE[k]:.0f}%)',color=MUTED,fontsize=7.6,weight='bold',va='center',ha='center')
for i,r in enumerate(g):
    yy=y-0.95-i*0.62
    if i%2==0: ax.add_patch(plt.Rectangle((2,yy-0.3),96,0.6,fc=CARD,ec='none'))
    on=r['game'] in PLAY
    ax.text(3,yy,r['game']+(' *' if on else ''),color=GOLD if on else TXT,fontsize=9,weight='bold' if on else 'normal',va='center')
    for (k,_),x in zip(COLS,xs):
        p=r['methods'][k]; pick=PICKS.get((r['game'],k))
        col=GOLD if pick else (GREEN if p*100>LEAGUE[k]+1.5 else TXT)
        ax.text(x,yy,f"{p*100:.0f}%  {am(p)}"+(f"  {pick}" if pick else ''),color=col,fontsize=7.6,weight='bold' if pick else 'normal',va='center',ha='center')
yb=y-0.95-len(g)*0.62
ax.text(3,yb,'Combo: '+COMBO,color=GOLD,fontsize=8,va='center')
ax.text(3,yb-0.5,'* = play-list game. Green = 1.5+ pts above league. Longshots on a noisy market; small stakes.',color=MUTED,fontsize=7.6,va='center')
fig.savefig(OUT,facecolor=BG)
