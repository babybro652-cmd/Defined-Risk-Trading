import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
NS="not sent yet"
rows=[
["PHI @ CHI\n3:30","PHI","Ours: PHI 68%\nStarTool: PHI (63 vs 25)\nSheet: PHI (54 vs Smith* 28)","Embiid 15% (+551)\nBrown 14% (+638)","Brown 12%\nEmbiid 12%","Embiid 36%\nBrown 29%","Ours+Sheet\n(StarTool ties Embiid)","y"],
["LAL @ DET\n6:00","LAL","Ours: LAL 80%\nStarTool: LAL (63 vs 25)\nSheet: LAL (Kessler 80 vs 38)","Doncic 22% (+346)\nKessler 15% (+586)","Doncic 19%\nReaves 13%","Doncic 36%\nReaves 20%","All 3 (Doncic)","g"],
["UTAH @ MIN\n7:00","MIN","Ours: MIN 67%\nStarTool: MIN (50 vs 25)\nSheet: MIN (Gobert 53 vs 40)","Kuminga 14% (+641)\nLaMelo 13% (+677)","LaMelo 14%\nDosunmu 11%","LaMelo 26%\nGobert 22%","StarTool+Sheet\n(LaMelo; ours Kuminga)","y"],
["BKN @ DAL\n7:30","BKN","Ours: 50/50 (BKN 51%)\nStarTool: DAL (50 vs 38)\nSheet: DAL (Gafford 37 vs 31)","Porter Jr. 13% (+668)\nRandle 12% (+740)","Porter Jr. 16%\nRandle 14%","Porter Jr. 38%\nSharpe 31%","All 3 (Porter Jr.)","g"],
["","DAL","(other side)","Flagg 12% (+710)\nGafford 11% (+778)","Flagg 14%\nIrving 14%","Flagg 23%\nChristie 23%","All 3 (Flagg; ties)","g"],
["BOS @ MIL\n8:00","BOS","Ours: BOS 59%\nStarTool: BOS (50 vs 25)\nSheet: BOS (Queta 40 vs 28)","Tatum 16% (+544)\nQueta 13% (+677)","Tatum 17%\nP. George 12%","Queta 29%\nP. George 26%","Ours+StarTool\n(Tatum; sheet Queta)","y"],
["NO @ LAC\n9:00","LAC","Ours: LAC 64%\nStarTool: NO (25 vs 13)\nSheet: LAC (Lopez 56 vs 29)","Lopez 14% (+632)\nGarland 13% (+687)","Garland 17%\nHachimura 10%","Lopez 26%\nHachimura 25%","Ours+Sheet\n(Lopez; StarTool Garland)","y"],
["MIA @ SAC\n9:00","MIA","Ours: MIA 83%\nStarTool: MIA (100 vs 38)\nSheet: MIA (Bam 73 vs 38)","Adebayo 22% (+362)\nGiannis 15% (+546)","Giannis 16%\nAdebayo 12%","Giannis 33%\nAdebayo 31%","StarTool+Sheet\n(Giannis; ours Bam)","y"],
]
fig,ax=plt.subplots(figsize=(16,1.1*len(rows)+2.4)); ax.axis('off')
ax.set_title("Sun 11/8 First Basket: Tip-Winning Team's Top 2\nOurs (chance + fair) vs StarTool (their %) vs @NBAFirstBasket sheet (share of team first baskets)",fontsize=15,fontweight='bold',pad=12)
tb=ax.table(cellText=[r[:7] for r in rows],colLabels=["Game","Team","Tip favorite","Our top 2","StarTool top 2","Cheat sheet top 2","#1 agrees"],
  colWidths=[0.12,0.05,0.19,0.16,0.11,0.12,0.17],loc='upper center',cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5)
col={'g':'#dff3e3','y':'#fff4cc','r':'#fbe1e1'}
for (r,c),cl in tb.get_celld().items():
    cl.set_height(0.105 if r>0 else 0.035)
    if r==0:
        cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold'); cl.get_text().set_ha('center')
    else:
        if r%2==0: cl.set_facecolor('#eef2f7')
        if c==6: cl.set_facecolor(col[rows[r-1][7]])
plt.figtext(0.5,0.03,"BKN @ DAL is a 50/50 tip in our model, so both teams are shown. Sheet top 2 skips players who are out; * = injury tag (Smith CHI, probable).\nQ: Doncic, Markkanen, Embiid (probable). Out: Duren (DET), Claxton (CHI), Edwards (MIN), Lively (DAL), Ingram and Beal (LAC).",ha='center',fontsize=10.5)
plt.savefig('/home/user/Defined-Risk-Trading/analysis/nba/out/charts/fb_tipteam_3way_2026-11-08.png',dpi=110,bbox_inches='tight')
