"""11/13/26 NBA results charts (game first basket, team first basket). Styled like make_fb_chart.py.
Run from repo root: python3 analysis/nba/out/charts/results_2026-11-13.py"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

G, R, N, HEAD, ALT = '#cdebd3', '#f6cccc', '#ffffff', '#1f3a5f', '#eef2f7'
OUT = 'analysis/nba/out/charts/results_2026-11-13_'


def draw(title, cols, widths, rows, shades, foot, name, h_row, fs=10.5, fy=0.01):
    fig, ax = plt.subplots(figsize=(18, h_row * len(rows) + 1.8)); ax.axis('off')
    ax.set_title(title, fontsize=15, fontweight='bold', pad=12)
    tb = ax.table(cellText=rows, colLabels=cols, colWidths=widths, loc='upper center', cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(fs)
    for (r, c), cl in tb.get_celld().items():
        cl.set_height((0.86 / len(rows)) if r > 0 else 0.045)
        if r == 0:
            cl.set_facecolor(HEAD); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
        else:
            s = shades[r - 1][c]
            cl.set_facecolor(G if s == 'g' else R if s == 'r' else ALT if r % 2 == 0 else N)
    plt.figtext(0.5, fy, foot, ha='center', fontsize=10.5)
    plt.savefig(OUT + name + '.png', dpi=110, bbox_inches='tight')


# ---------- Chart 1: game first basket and tips ----------
cols = ["Game", "Tip (winner first?)", "Tip calls", "First shot", "First points", "Our #1 pick", "Longshot (#3)",
        "Scorer in top picks?"]
rows = [
    ["NY @ IND\n106-104 IND", "IND won\nBridges vs Oubre\n(not Towns/Zubac)\nIND scored 1st",
     "Ours IND  OK\nStarTool IND  OK\nTip sheet NY  X\nTipProj IND  OK", "Andrew Nembhard\n(IND) layup\nMADE",
     "Andrew Nembhard\n(IND) layup\n11:53", "Towns: MISS\n(Towns scored NY's 1st\nat 10:17)", "Zubac: MISS",
     "Ours top 3: no\nStarTool #1 Siakam: no"],
    ["MIL @ ORL\n107-99 ORL", "MIL won\nTurner vs Carter\nMIL no 1st score",
     "Ours ORL  X\nStarTool ORL  X\nTip sheet ORL  X\nTipProj ORL  X", "Tristan da Silva\n(ORL) 3\nMISSED",
     "Franz Wagner\n(ORL) 6 ft\n10:12", "W. Carter Jr.: MISS\n2 MIL turnovers, da Silva\nmissed, Dieng missed,\nWagner scored", "Bane: MISS",
     "Ours top 3: YES (Wagner #2)\nStarTool #1 Herro: no"],
    ["CLE @ MIA\n133-121 MIA", "CLE won\nAllen vs Adebayo\nCLE no 1st score",
     "Ours MIA  X\nStarTool CLE  OK\nTip sheet MIA  X\nTipProj MIA  X", "James Harden\n(CLE) layup\nMISSED",
     "Giannis\n(MIA) fadeaway\n11:07", "Adebayo: MISS\nGiannis missed 2 FTs first,\nthen hit the fadeaway", "Giannis: HIT",
     "Ours top 3: YES (Giannis #3)\nStarTool #1 Giannis: YES"],
    ["ATL @ CHI\n125-117 CHI OT", "ATL won\nOkongwu vs J. Smith\nATL scored 1st",
     "Ours ATL  OK\nStarTool ATL  OK\nTip sheet ATL  OK\nTipProj ATL  OK", "Jalen Smith\n(CHI) 3\nMISSED",
     "Jalen Johnson\n(ATL) layup\n10:58", "Okongwu: MISS\nFlemings TO, Smith missed,\nDaniels missed, CHI TO,\nJ. Johnson layup", "NAW: MISS",
     "Ours top 3: no\nStarTool #1 J. Johnson: YES"],
    ["MEM @ NO\n142-111 MEM", "NO won\nStewart vs D. Jordan\n(not Matkovic)\nNO scored 1st",
     "Ours NO  OK\nStarTool MEM  X\nTip sheet MEM  X\nTipProj MEM  X", "Cedric Coward\n(MEM) 3\nMISSED",
     "Zion Williamson\n(NO) 2 pt\n10:58", "Zion: HIT\nFears TO, Coward missed,\nFears missed, Jordan OREB\nand TO, Wells missed, Zion", "Stewart: MISS",
     "Ours top 3: YES (Zion #1)\nStarTool #1 Zion: YES"],
    ["UTAH @ HOU\n125-118 HOU", "UTAH won\nHayes vs Sengun\nUTAH scored 1st",
     "Ours HOU  X\nStarTool HOU  X\nTip sheet HOU  X\nTipProj even", "Josh Okogie\n(UTAH) 3\nMISSED",
     "Josh Okogie\n(UTAH) 3\n11:39", "Sengun: MISS\nOkogie missed, Hayes OREB,\nOkogie hit the 3", "Bailey: MISS",
     "Ours top 3: no (Okogie\nnot in our five)\nStarTool #1 George: no"],
    ["GS @ SA\n123-85 SA", "SA won\nWembanyama vs Green\nSA scored 1st",
     "Ours SA  OK\nStarTool SA  OK\nTip sheet SA  OK\nTipProj SA  OK", "Stephon Castle\n(SA) 3\nMADE",
     "Stephon Castle\n(SA) 3\n11:40", "Wembanyama: MISS\n(he assisted Castle's 3)", "Castle: HIT",
     "Ours top 3: YES (Castle #3)\nStarTool #1 Wemby: no"],
    ["POR @ SAC\n120-107 POR", "POR won\nClingan vs Sabonis\nPOR scored 1st",
     "Ours POR  OK\nStarTool POR  OK\nTip sheet POR  OK\nTipProj POR  OK", "Domantas Sabonis\n(SAC) 18 ft\nMISSED",
     "Sidy Cissoko\n(POR) 3\n10:28", "Clingan: MISS\n2 POR TOs, Sabonis missed\nthree times, SAC shot\nclock TO, Cissoko 3", "Lillard: MISS",
     "Ours top 3: no\nStarTool #1 Avdija: no"],
    ["OKC @ LAC\n113-112 LAC", "LAC won\nMara vs Lopez\n(not Hartenstein)\nLAC scored 1st",
     "Ours LAC  OK\nStarTool OKC  X\nTip sheet LAC  OK\nTipProj LAC  OK", "Darius Garland\n(LAC) 8 ft\nBLOCKED",
     "Darius Garland\n(LAC) 25 ft\n11:35", "Lopez: MISS\nGarland blocked, LAC\nkept it, Garland scored", "Hachimura: MISS",
     "Ours top 3: YES (Garland #2)\nStarTool #1 SGA: no"],
]
tipc = ['g', 'r', 'r', 'g', 'g', 'r', 'g', 'g', 'g']
fs_ = ['g', 'r', 'r', 'r', 'r', 'r', 'g', 'r', 'r']
one = ['r', 'r', 'r', 'r', 'g', 'r', 'r', 'r', 'r']
lng = ['r', 'r', 'g', 'r', 'r', 'r', 'g', 'r', 'r']
top = ['r', 'g', 'g', 'r', 'g', 'r', 'g', 'r', 'g']
shades = [['', '', tipc[i], fs_[i], '', one[i], lng[i], top[i]] for i in range(9)]
draw("NBA First Basket Results, Fri 11/13/26 (9 games)\nOur #1 picks 1-8 (Zion), longshots 2-7 (Giannis, Castle). Tips: ours 6-3, StarTool 5-4, tip sheet 4-5, TipProj 5-3",
     cols, [0.075, 0.11, 0.115, 0.105, 0.1, 0.2, 0.08, 0.215], rows, shades,
     "Green = hit / right, red = miss / wrong. First points count free throws (FanDuel rule). First shot green = made. "
     "Expected jumpers right in 6 of 9 (NY, IND, NO, OKC changed). Tip winner scored first 7 of 9. Our scorer in top 3: 5 of 9.",
     'game', 1.45, fs=9.5, fy=0.05)

sh = lambda t: 'g' if 'HIT' in t else 'r' if 'MISS' in t else ''

# ---------- Chart 2: team first basket ----------
cols = ["Team", "Team's first scorer", "Our top 2", "StarTool top 2 (model %)"]
rows = [
    ["NY", "Karl-Anthony Towns, layup", "Towns / Brunson: HIT (#1)", "Brunson / Towns: HIT"],
    ["IND", "Andrew Nembhard, layup", "Zubac / Siakam: MISS", "Siakam / Nembhard: HIT"],
    ["MIL", "Myles Turner, 3 (after 2 OREBs)", "Burries / Turner: HIT", "Herro / Jaquez: MISS"],
    ["ORL", "Franz Wagner, 6 ft", "Carter / F. Wagner: HIT", "Bane / F. Wagner: HIT"],
    ["CLE", "Donovan Mitchell, 3", "Allen / Watson: MISS", "D. Mitchell / Harden: HIT"],
    ["MIA", "Giannis, fadeaway", "Adebayo / Giannis: HIT", "Giannis / Adebayo: HIT"],
    ["ATL", "Jalen Johnson, layup", "Okongwu / Flemings: MISS", "J. Johnson / NAW: HIT"],
    ["CHI", "Josh Giddey, 1 ft", "Powell / J. Smith: MISS", "Buzelis / Giddey: HIT (Wilson out)"],
    ["MEM", "Cameron Boozer, 3", "Jerome / Stewart: MISS", "Jerome / Boozer: HIT"],
    ["NO", "Zion Williamson, 2 pt", "Zion / Fears: HIT (#1)", "Zion / Fears: HIT"],
    ["UTAH", "Josh Okogie, 3", "Bailey / K. George: MISS", "K. George / Peterson: MISS"],
    ["HOU", "Fred VanVleet, 18 ft", "Sengun / Durant: MISS", "Durant / Sengun: MISS"],
    ["GS", "Gui Santos (bench), layup", "Lendeborg / Podziemski: MISS", "Lendeborg / Podziemski: MISS"],
    ["SA", "Stephon Castle, 3", "Wembanyama / Fox: MISS", "Wembanyama / Fox: MISS"],
    ["POR", "Sidy Cissoko, 3", "Clingan / Avdija: MISS", "Avdija / Lillard: MISS"],
    ["SAC", "Keegan Murray, layup", "Sabonis / Achiuwa (DNP): MISS", "Acuff / LaVine: MISS"],
    ["OKC", "Kenrich Williams, tip-in", "A. Mitchell (DNP) / SGA: MISS", "SGA / McCain: MISS"],
    ["LAC", "Darius Garland, 25 ft", "Lopez / Garland: HIT", "Garland / Hachimura: HIT"],
]
shades = [[''] * 2 + [sh(x) for x in r[2:]] for r in rows]
draw("NBA Team First Basket Results, Fri 11/13/26\nTop 2 hit: ours 6 of 18, StarTool 10 of 18 (random about 40%)",
     cols, [0.07, 0.27, 0.32, 0.34], rows, shades,
     "Green = scorer in that source's top 2, red = not. Free throws count. StarTool top 2 = printed model %, Out players dropped. "
     "Season to date top 2: ours 48% (67 of 140), StarTool 44% (60 of 137).",
     'team', 0.42, fs=11.5, fy=0.06)

# ---------- Chart 3: after our 1st-shot pick ----------
cols = ["Team", "Our 1st-shot pick", "Who took the team's 1st shot", "What happened next",
        "Team's first points", "Our 2nd-chance pick", "Either pick scored?"]
rows = [
    ["NY", "Brunson", "Anunoby, 18 ft MISS", "NY shot clock TO, Towns missed 3,\nthen Towns layup", "Towns", "Towns: HIT", "YES (2nd)"],
    ["IND", "Zubac", "Nembhard, layup MADE", "-", "Nembhard", "Siakam: MISS", "no"],
    ["MIL", "Burries", "Dieng, 28 ft 3 MISS", "Burries missed, Turner 2 OREBs,\nTurner 3", "Turner", "Herro: MISS", "no"],
    ["ORL", "W. Carter Jr.", "da Silva, 3 MISS", "da Silva TO, then Wagner 6 ft", "F. Wagner", "F. Wagner: HIT", "YES (2nd)"],
    ["CLE", "Allen", "Harden, layup MISS", "Mitchell TO, then Mitchell 3", "D. Mitchell", "D. Mitchell: HIT", "YES (2nd)"],
    ["MIA", "Adebayo", "Giannis FTs, 0 of 2", "Bam DREB; Giannis fadeaway", "Giannis", "Giannis: HIT", "YES (2nd)"],
    ["ATL", "Flemings", "Daniels, 2 pt MISS\n(Flemings TO before)", "CHI TO, J. Johnson layup", "J. Johnson", "Okongwu: MISS", "no"],
    ["CHI", "Powell", "J. Smith, 3 MISS", "Smith TO, Giddey 1 ft", "Giddey", "J. Smith: MISS", "no"],
    ["MEM", "Jerome", "Coward, 3 MISS", "Wells missed 3, Boozer 3\n(Jerome assist)", "Boozer", "Stewart: MISS", "no"],
    ["NO", "Zion", "Fears, layup MISS", "Jordan OREB, TO, then Zion", "Zion", "Fears: MISS", "YES (1st)"],
    ["UTAH", "Bailey", "Okogie, 3 MISS", "Hayes OREB, Okogie 3", "Okogie", "K. George: MISS", "no"],
    ["HOU", "Sengun", "VanVleet, 18 ft MADE", "- (Sengun assist)", "VanVleet", "Durant: MISS", "no"],
    ["SA", "Wembanyama", "Castle, 3 MADE", "- (Wemby assist)", "Castle", "Fox: MISS", "no"],
    ["GS", "Lendeborg", "D. Green, 3 MISS", "GS missed or turned it over\nfor 4+ min; bench Santos scored", "Santos", "Podziemski: MISS", "no"],
    ["POR", "Avdija", "Cissoko, 3 MADE\n(after 2 POR TOs)", "-", "Cissoko", "Clingan: MISS", "no"],
    ["SAC", "Sabonis", "Sabonis, 18 ft MISS", "Sabonis OREB, off foul; 2 more\nmisses; K. Murray layup", "K. Murray", "Acuff: MISS", "no"],
    ["OKC", "A. Mitchell (DNP)", "Mara, 10 ft MISS", "K. Williams tip-in", "K. Williams", "SGA: MISS", "no"],
    ["LAC", "Garland", "Garland, 8 ft BLOCKED", "LAC kept it, Garland 25 ft", "Garland", "Lopez: MISS", "YES (1st)"],
]
shades = [['', '', 'g' if r[2].split(',')[0] in r[1] else 'r', '', '', sh(r[5]), 'g' if r[6].startswith('YES') else 'r'] for r in rows]
draw("After the first shot, Fri 11/13/26: did our two-slot picks score their team's first points?\n"
     "1st-shot pick took the team's 1st shot 2 of 17 (Sabonis, Garland). Either pick scored: 6 of 18 (4 by the 2nd-chance pick)",
     cols, [0.06, 0.12, 0.16, 0.25, 0.1, 0.15, 0.1], rows, shades,
     "Green in column 3 = our 1st-shot pick took the team's 1st shot. 14 of 18 teams missed their 1st shot (MIA FTs count as a miss). "
     "The 2nd-chance pick scored after a miss 4 times (Towns, Wagner, Mitchell, Giannis); role players took most first shots.",
     'firstshot', 0.48, fs=10.5, fy=0.05)
