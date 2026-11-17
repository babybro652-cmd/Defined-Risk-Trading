import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math']=False
from matplotlib.patches import FancyBboxPatch
d=json.load(open('analysis/nba/out/fb_candidates.json'))
games=[('NY','TOR','7:30'),('POR','MIN','8:00'),('DET','SA','8:00'),('UTAH','LAC','10:30'),('CHA','LAL','11:00')]
play={'DET@SA','UTAH@LAC'}  # 4:50 PM rerun: unchanged
def am(p):
    dec=1/p; return ('+%d'%round((dec-1)*100)) if dec>=2 else ('-%d'%round(100/(dec-1)))
def take(p):
    dec=1.2/p; return ('+%d'%round((dec-1)*100)) if dec>=2 else ('-%d'%round(100/(dec-1)))
by={}
for r in d: by.setdefault(r['tm'],[]).append(r)
BG='#0f1420'; CARD='#1a2233'; TXT='#e8ecf3'; MUTED='#9aa4b5'; GOLD='#f5c542'; BLUE='#5aa9ff'; GREEN='#4cd38a'; RED='#ff6b6b'
fig=plt.figure(figsize=(7.2,12.8),dpi=200); fig.patch.set_facecolor(BG)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,178); ax.axis('off')
ax.text(5,173,'TEAM FIRST BASKET  •  TUE 11/17 (4:50 PM)',color=TXT,fontsize=16,weight='bold',va='center')
ax.text(5,168.6,'Top 2 per team: chance to score his team\'s first points, fair odds, take-at (fair x1.2)',color=MUTED,fontsize=8,va='center')
ax.text(5,165,'Gold border = on tonight\'s play list (tip 70%+)',color=GOLD,fontsize=8,va='center')
y=161; h=18.2
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
            flag=' (DTD)' if r.get('inj') else ''
            ax.text(x,yy,f"{name}{flag}",color=TXT if not flag else RED,fontsize=8.8,va='center')
            ax.text(x+21,yy,f"{p*100:.0f}%",color=GREEN,fontsize=8.8,va='center')
            ax.text(x+28,yy,f"{am(p)}  /  {take(p)}",color=MUTED,fontsize=8.3,va='center')
    y-=h+1.6
ax.text(5,y,'Read: chance  •  fair  /  take at. Bet only at the take-at price or longer.',color=MUTED,fontsize=8,va='center')
ax.text(5,y-4,'Team first basket = first made basket or FT points for that team (FanDuel rules).',color=MUTED,fontsize=8,va='center')
fig.savefig('analysis/nba/out/charts/team_fb_2026-11-17.png',facecolor=BG)
for a,hm,t in games:
    for tm in (a,hm):
        print(tm,[(r['player'],round(r['team_share'],3),r.get('inj')) for r in sorted(by.get(tm,[]),key=lambda r:-r['team_share'])[:2]])
