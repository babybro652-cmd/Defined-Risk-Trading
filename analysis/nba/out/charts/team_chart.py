import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
d=json.load(open('analysis/nba/out/fb_candidates.json'))
games=[('MIL','PHI','1:00'),('POR','NY','7:30'),('LAC','DAL','8:00'),('MEM','MIN','8:00'),('NO','SA','8:00'),('BOS','SAC','10:00')]
play={'LAC@DAL','NO@SA'}  # 11/21 plan
def am(p):
    dec=1/p; return ('+%d'%round((dec-1)*100)) if dec>=2 else ('-%d'%round(100/(dec-1)))
def take(p):
    dec=1.2/p; return ('+%d'%round((dec-1)*100)) if dec>=2 else ('-%d'%round(100/(dec-1)))
by={}
for r in d: by.setdefault(r['tm'],[]).append(r)
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
fig=plt.figure(figsize=(7.2,9.8),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(170,306); ax.axis('off')
ax.text(5,301,'TEAM FIRST BASKET  •  SAT 11/21 (lineup rerun 7:27 PM)',color=TXT,fontsize=16,weight='bold',va='center')
ax.text(5,296.6,'Top 2 per team: chance to score his team\'s first points, fair odds, take-at (fair x1.2)',color=MUTED,fontsize=8,va='center')
ax.text(5,293,'Gold border = tip 70%+ games. Tracking only this week (log FanDuel price), no money',color=GOLD,fontsize=7.6,va='center')
y=289; h=18.2
for a,hm,t in games:
    key=f'{a}@{hm}'; on=key in play
    ax.add_patch(FancyBboxPatch((4,y-h),92,h,boxstyle='round,pad=0.3,rounding_size=1.4',fc=CARD,ec=GOLD if on else '#2c3850',lw=1.4 if on else 1))
    ax.text(7,y-3,f'{a} @ {hm}',color=TXT,fontsize=11,weight='bold',va='center')
    ax.text(93,y-3,t+' PM',color=MUTED,fontsize=9,va='center',ha='right')
    for col,tm in enumerate((a,hm)):
        x=7+col*45
        ax.text(x,y-7.3,tm,color=BLUE,fontsize=9.5,weight='bold',va='center')
        top=sorted(by.get(tm,[]),key=lambda r:-r['team_share'])[:2]
        for i,r in enumerate(top):
            yy=y-11.2-i*3.7; p=r['team_share']
            name=r['player'].split(' ',1)[-1] if len(r['player'])>17 else r['player']
            flag=' (DTD)' if r.get('inj') and r.get('inj')!='Out' else (' (Prob)' if r.get('inj')=='Out' else '')
            ax.text(x,yy,f"{name}{flag}",color=TXT if not flag else RED,fontsize=8.8,va='center')
            ax.text(x+21,yy,f"{p*100:.0f}%",color=GREEN,fontsize=8.8,va='center')
            ax.text(x+28,yy,f"{am(p)}  /  {take(p)}",color=MUTED,fontsize=8.3,va='center')
    y-=h+1.6
ax.text(5,y,'Read: chance  •  fair  /  take at. Bet only at the take-at price or longer.',color=MUTED,fontsize=8,va='center')
ax.text(5,y-4,'Team first basket = first made basket or FT points for that team (FanDuel rules).',color=MUTED,fontsize=8,va='center')
fig.savefig('analysis/nba/out/charts/team_fb_2026-11-21.png',facecolor=BG)
for a,hm,t in games:
    for tm in (a,hm):
        print(tm,[(r['player'],round(r['team_share'],3),r.get('inj')) for r in sorted(by.get(tm,[]),key=lambda r:-r['team_share'])[:2]])
