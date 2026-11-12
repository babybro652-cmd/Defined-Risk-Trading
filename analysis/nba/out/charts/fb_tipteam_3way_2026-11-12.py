import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
# cols: game, team, tip (ours / StarTool / @NBAFirstBasket tip sheet normalized), our top 2 (game chance, fair), StarTool top 2, fbsheet top 2 (1st Bsk / 1st Gm), agree flag, color
rows=[
["TOR @ PHI\n7:00","TOR","Ours TOR 68 | ST TOR 67\nTip sheet TOR 53 (Poeltl 2-1 Embiid)","Barnes (Q) 14% (+603)\nBarrett 14% (+621)","Barrett 13% (star)\nQuickley 12% (bomb)","Barrett 20/12\nQuickley 19/6","Agree (Barrett)","g"],
["","PHI","(other side)","Embiid (Q) 10% (+854)\nBrown 10% (+943)","Brown 13% (bomb)\nEmbiid, Maxey 13%","Embiid 36/20\nBrown 28/15","Agree (Embiid, Brown)","g"],
["DET @ WSH\n7:00","WSH","Ours WSH 74 | ST not loaded\nTip sheet WSH (Collins 0 tips)","Davis 18% (+443)\nSarr 12% (+707)","card not loaded","Dybantsa 25/12\nDavis 23/10","Partial (Davis)","y"],
["","DET","(other side)","Collins 12% (+747)\nCunningham 9% (+957)","card not loaded","Collins 29/15\nA. Thompson 20/7","Agree (Collins)","g"],
["DAL @ MIN\n8:00","MIN","Ours MIN 65 | ST MIN 64\nTip sheet MIN 60 (Gafford 2-3 Gobert)","LaMelo 13% (+652)\nKuminga 13% (+691)","LaMelo 15% (star)\nDosunmu 12% (bomb)","LaMelo 27/15\nGobert 21/9","Agree (LaMelo)","g"],
["","DAL","(other side)","Flagg 12% (+725)\nGafford 10% (+899)","Flagg 14% (bomb)\nIrving 14% (star)","Irving 22/0, Flagg 22/8\nGafford 20/15","Agree (Flagg)","g"],
["CHA @ PHX\n9:00","PHX","Ours PHX 56 | ST CHA 59\nTip sheet PHX 59 (Diabate 0-2 Ighodaro)","Booker 12% (+737)\nBrooks 12% (+769)","Booker 12% (star)\nBrooks 9% (bomb)","Booker 28/14\nJ. Green 28/12","Agree (Booker)","g"],
["","CHA","(other side)","Reid 12% (+730)\nG. Allen 11% (+796)","White 16% (bomb)\nG. Allen 16% (star)","G. Allen 31/17\nReid, Diabate 21","Agree on G. Allen","y"],
]
fig,ax=plt.subplots(figsize=(18,0.95*len(rows)+2.4)); ax.axis('off')
ax.set_title("Thu 11/12 First Basket: ours vs StarTool vs @NBAFirstBasket cheat sheets\nTip-winning team listed first. fbsheet = new First Basket Cheat Sheet (1st Bsk % of team / 1st Gm % of game)",fontsize=15,fontweight='bold',pad=12)
tb=ax.table(cellText=[r[:7] for r in rows],colLabels=["Game","Team","Tip favorite (3 sources)","Our top 2 (game chance, fair)","StarTool top 2","fbsheet top 2","Agree?"],
  colWidths=[0.08,0.05,0.22,0.18,0.15,0.15,0.14],loc='upper center',cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5)
col={'g':'#dff3e3','y':'#fff4cc','r':'#fbe1e1'}
for (r,c),cl in tb.get_celld().items():
    cl.set_height(0.085 if r>0 else 0.03)
    if r==0:
        cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
    else:
        if r%2==0: cl.set_facecolor('#eef2f7')
        if c==6: cl.set_facecolor(col[rows[r-1][7]])
plt.figtext(0.5,0.02,"Tip favorite: all sources agree in 3 of 4; CHA @ PHX splits (StarTool CHA 59, ours and the tip sheet PHX). DET @ WSH StarTool card did not load.\nQuestionable: Barnes, Embiid, LeBron. Diabate probable. StarTool lists Murray-Boyles for TOR and Kalkbrenner for CHA.",ha='center',fontsize=10.5)
plt.savefig('/home/user/Defined-Risk-Trading/analysis/nba/out/charts/fb_tipteam_3way_2026-11-12.png',dpi=110,bbox_inches='tight')
