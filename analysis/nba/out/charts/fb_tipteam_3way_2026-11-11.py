import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
# cols: game, team, tip (ours / StarTool / sheet last-season normalized / Tip-off Projections), our top 2, StarTool top 2, agree flag, color
rows=[
["WSH @ IND\n7:00","IND","Ours IND 60 | ST IND 54\nSheet WSH 56 (Davis) | TipProj IND 56","Zubac 16% (+531)\nNembhard 11%","Siakam 23%\nNembhard 16%","Split (Zubac vs Siakam)","y"],
["","WSH","(other side)","Davis 13% (+661)\nSarr 12% (+757)","Davis 8%\nDybantsa 6%","Agree (Davis)","g"],
["CLE @ NY\n7:00","CLE","Ours 73 | ST 77\nSheet 60 | TipProj 73","Allen 18% (+458)\nMobley 14% (+611)","Mitchell 15%\nHarden 13%","Split (Allen vs Mitchell)","y"],
["BOS @ TOR\n7:00","TOR","Ours 72 | ST 61\nSheet 59 | TipProj 66","Barrett 15% (+574)\nMurray-Boyles 14%","Barrett 17%\nPoeltl 9%","Agree (Barrett)","g"],
["SA @ CHI\n8:00","SA","Ours 95 | ST 76\nSheet 78 | TipProj 96","Wembanyama 27% (+267)\nFox 13% (+685)","Wembanyama 19%\nFox 12%","Agree (Wembanyama, Fox)","g"],
["DEN @ MEM\n8:00","MEM","Ours MEM 59 | ST 54\nSheet 58 | TipProj 68","Edey 14% (+639)\nJerome 13% (+648)","Jerome 15%\nBoozer 10%","Agree on Jerome","y"],
["","DEN","(other side)","Jokic 17% (+490)\nMurray 12% (+716)","Jokic 16%\nMurray 15%","Agree (Jokic, Murray)","g"],
["LAL @ MIL\n8:00","LAL","Ours 82 | ST 58\nSheet 72 | TipProj 87","Doncic 25% (+307)\nReaves 13% (+682)","Doncic 18%\nReaves 12%","Agree (Doncic, Reaves)","g"],
["BKN @ NO\n8:00","BKN","Ours 64 | ST 59\nSheet 61 | TipProj 66","Porter Jr. 14% (+609)\nSharpe 11% (+773)","Porter Jr. 15%\nRandle 13%","Agree (Porter Jr.)","g"],
["ORL @ UTAH\n9:00","ORL","Ours 81 | ST 79\nSheet 63 | TipProj 69","Carter 18% (+461)\nWagner 15% (+567)","Bane 14%\nWagner 14%","Split (Carter vs Bane)","y"],
["GS @ HOU\n9:30","HOU","Ours 66 | ST 64\nSheet 59 | TipProj 69","Sengun 18% (+445)\nDurant 13% (+655)","Durant 15%\nSengun 12%","Agree (Sengun, Durant)","g"],
["OKC @ POR\n10:00","POR","Ours 65 | ST 66\nSheet 52 | TipProj 54","Clingan 14% (+638)\nLillard 12% (+743)","Avdija 14%\nLillard 12%","Agree on Lillard","y"],
["","OKC","(other side)","A. Mitchell 10% (+878)\nSGA 10% (+883)","SGA 23%\nA. Mitchell 10%","Agree (SGA, Mitchell)","g"],
]
fig,ax=plt.subplots(figsize=(16,0.95*len(rows)+2.4)); ax.axis('off')
ax.set_title("Wed 11/11 First Basket: Tip-Winning Team's Top 2\nTip %: ours vs StarTool vs @NBAFirstBasket (last season, normalized) vs Tip-off Projections (new)",fontsize=15,fontweight='bold',pad=12)
tb=ax.table(cellText=[r[:6] for r in rows],colLabels=["Game","Team","Tip favorite (4 sources)","Our top 2 (game chance, fair)","StarTool top 2","Agree?"],
  colWidths=[0.1,0.05,0.27,0.2,0.14,0.18],loc='upper center',cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5)
col={'g':'#dff3e3','y':'#fff4cc','r':'#fbe1e1'}
for (r,c),cl in tb.get_celld().items():
    cl.set_height(0.075 if r>0 else 0.03)
    if r==0:
        cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
    else:
        if r%2==0: cl.set_facecolor('#eef2f7')
        if c==5: cl.set_facecolor(col[rows[r-1][6]])
plt.figtext(0.5,0.02,"All 4 tip sources pick the same team in 9 of 10 games; only the cheat sheet flips WSH @ IND (it lists Davis as the jumper, the other three use Sarr).\nThe cheat sheet sent today had tip rates only (no first basket card). Toss-ups: Markkanen, Herro, Quickley, Murray-Boyles, Vassell, Powell, Hart.",ha='center',fontsize=10.5)
plt.savefig('/home/user/Defined-Risk-Trading/analysis/nba/out/charts/fb_tipteam_3way_2026-11-11.png',dpi=110,bbox_inches='tight')
