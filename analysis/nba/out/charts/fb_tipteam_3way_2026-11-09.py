import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[
["LAL @ ATL\n7:00","LAL","Ours: LAL 71%\nStarTool: 50/50\nSheet: not sent","Doncic 22% (+358)\nReaves 11% (+801)","Reaves 18%\nKessler 11%","Doncic 36%\nReaves 21%","Ours+Sheet\n(Doncic; StarTool Reaves)","y"],
["CLE @ CHA\n7:00","CLE","Ours: CLE 69%\nStarTool: CLE (88 vs 38)\nSheet: not sent","Allen 16% (+507)\nMobley 14% (+593)","Mitchell 13%\nHarden 12%","Allen 34%\nMobley 31%","Ours+Sheet\n(Allen; StarTool Mitchell)","y"],
["WSH @ DET\n7:00","DET","Ours: 51% DET (49 WSH)\nStarTool: WSH (63 vs 38)\nSheet: not sent","Collins 13% (+692)\nReed 13% (+658)","Cunningham 17%\nRobinson 10%","Reed 33%\nCollins 28%","Ours+Sheet\n(Reed; StarTool Cunningham)","y"],
["","WSH","(other side)","Davis 13% (+679)\nSarr 12% (+722)","Davis 13%\nYoung 10%","Dybantsa 33%\nDavis 25%","Ours+StarTool\n(Davis; sheet #2)","y"],
["MEM @ TOR\n7:30","MEM","Ours: MEM 53%\nStarTool: TOR (63 vs 50)\nSheet: not sent","Jerome 13% (+682)\nEdey 13% (+663)","Jerome 16%\nBoozer 10%","Boozer 33%\nJerome 26%","Ours+StarTool\n(Jerome; sheet Boozer)","y"],
["","TOR","(other side)","Barrett 13% (+663)\nBarnes 13% (+685)","Barrett 13%\nQuickley 12%","Quickley 19%\nBarrett 19%","Ours+StarTool\n(Barrett; sheet tie)","y"],
["IND @ DAL\n8:00","IND","Ours: IND 62%\nStarTool: DAL (50 vs 25)\nSheet: IND (44 vs 36)","Zubac 14% (+617)\nNembhard 12% (+750)","Siakam 16%\nNembhard 12%","Zubac 35%\nSiakam 28%","Ours+Sheet\n(Zubac; StarTool Siakam)","y"],
["","DAL","(other side)","Flagg 12% (+727)\nGafford 11% (+826)","Irving 14%\nFlagg 14%","Flagg 23%\nMartin 20%","Ours+Sheet\n(Flagg; StarTool ties)","g"],
["DEN @ HOU\n8:30","DEN","Ours: DEN 56%\nStarTool: HOU (63 vs 38)\nSheet: DEN (50 vs 40)","Jokic 18% (+451)\nMurray 14% (+640)","Jokic 15%\nMurray 14%","Murray 30%\nJokic 30%","All 3 (Jokic;\nsheet ties Murray)","g"],
["SA @ PHX\n9:00","SA","Ours: SA 90%\nStarTool: SA (88 vs 50)\nSheet: SA (90 vs 50)","Wembanyama 27% (+267)\nFox 13% (+679)","Wembanyama 15%\nFox 10%","Wembanyama 43%\nCastle 20%","All 3 (Wembanyama)","g"],
["NO @ GS\n10:00","NO","Ours: NO 61%\nStarTool: 25/25\nSheet: 25/25","Murphy 12% (+715)\nZion 11% (+773)","Murphy 14%\nZion 13%","Fears / Zion / Murphy\n20% each","Ours+StarTool\n(Murphy; sheet 3-way tie)","y"],
["","GS","(other side)","Curry 11% (+820)\nLendeborg 11% (+809)","Curry 17%\nLendeborg 13%","Curry 24%\nPodziemski 21%","All 3 (Curry)","g"],
]
fig,ax=plt.subplots(figsize=(16,0.95*len(rows)+2.4)); ax.axis('off')
ax.set_title("Mon 11/9 First Basket: Tip-Winning Team's Top 2\nOurs (chance + fair) vs StarTool (their %) vs @NBAFirstBasket sheet (share of team first baskets)",fontsize=15,fontweight='bold',pad=12)
tb=ax.table(cellText=[r[:7] for r in rows],colLabels=["Game","Team","Tip favorite","Our top 2","StarTool top 2","Cheat sheet top 2","#1 agrees"],
  colWidths=[0.11,0.05,0.2,0.17,0.11,0.13,0.18],loc='upper center',cellLoc='left')
tb.auto_set_font_size(False); tb.set_fontsize(10.5)
col={'g':'#dff3e3','y':'#fff4cc','r':'#fbe1e1'}
for (r,c),cl in tb.get_celld().items():
    cl.set_height(0.075 if r>0 else 0.03)
    if r==0:
        cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold'); cl.get_text().set_ha('center')
    else:
        if r%2==0: cl.set_facecolor('#eef2f7')
        if c==6: cl.set_facecolor(col[rows[r-1][7]])
plt.figtext(0.5,0.02,"Both sides shown where the tip is near 50/50 or sources split. Tip-off sheet card 1 of 2 not sent (LAL, CLE, WSH, MEM tips n/a).\nDay-to-day: Doncic/Reaves (LAL), Davis (WSH), Allen (CLE), Jokic (DEN). StarTool CHA star B. Miller is OUT.",ha='center',fontsize=10.5)
plt.savefig('/home/user/Defined-Risk-Trading/analysis/nba/out/charts/fb_tipteam_3way_2026-11-09.png',dpi=110,bbox_inches='tight')
