"""Tim's phone chart: tip % + top 2 FB per team per game. Usage: python3 make_fb_chart.py DATE 'AWAY,HOME,TIME,AWAYTIP;...' [note]"""
import json,collections,sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
date=sys.argv[1]; games=[(a,h,t,int(p)) for a,h,t,p in (g.split(',') for g in sys.argv[2].split(';'))]
note=sys.argv[3] if len(sys.argv)>3 else ""
d=json.load(open('analysis/nba/out/fb_candidates.json'))
t=collections.defaultdict(list)
for r in d: t[r['tm']].append(r)
for v in t.values(): v.sort(key=lambda r:-r['p_v2'])
take=lambda f: f"+{round(((int(f)/100+1)*1.2-1)*100)}"
def cell(tm):
    return tm+"\n"+"\n".join(f"{r['player']}{' (Q)' if r['inj'] else ''}  {r['p_v2']*100:.0f}%  {r['fair_v2']} / take {take(r['fair_v2'].strip('+'))}" for r in t[tm][:2])
rows=[[f"{a} @ {h}\n{tm} PM",f"{a} {ap}%\n{h} {100-ap}%",cell(a),cell(h)] for a,h,tm,ap in games]
fig,ax=plt.subplots(figsize=(14,1.6*len(games)+1.6)); ax.axis('off')
ax.set_title(f"NBA First Basket, {date} (our chain model)\nTop 2 per team: chance, fair price / take-at (fair x1.2). (Q) = questionable",fontsize=15,fontweight='bold',pad=12)
tb=ax.table(cellText=rows,colLabels=["Game","Tip win","Away: top 2","Home: top 2"],colWidths=[0.11,0.1,0.395,0.395],loc='upper center',cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5)
for (r,c),cl in tb.get_celld().items():
    cl.set_height(0.098 if r>0 else 0.035)
    if r==0: cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
    elif r%2==0: cl.set_facecolor('#eef2f7')
    if r>0 and c in (2,3):
        ap=games[r-1][3]
        if (c==2 and ap>50) or (c==3 and ap<50): cl.set_facecolor('#dff3e3')
plt.figtext(0.5,0.035,"Green = team favored to win the tip. "+note,ha='center',fontsize=10.5)
plt.savefig(f'analysis/nba/out/charts/fb_{sys.argv[4] if len(sys.argv)>4 else "latest"}.png',dpi=110,bbox_inches='tight')
