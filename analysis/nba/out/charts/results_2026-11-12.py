"""11/12/26 NBA results charts (game first basket, team first basket). Styled like make_fb_chart.py.
Run from repo root: python3 analysis/nba/out/charts/results_2026-11-12.py"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

G, R, N, HEAD, ALT = '#cdebd3', '#f6cccc', '#ffffff', '#1f3a5f', '#eef2f7'
OUT = 'analysis/nba/out/charts/results_2026-11-12_'


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


# ---------- Chart 1: game first basket ----------
cols = ["Game", "Tip (winner first)", "Tip calls", "First shot", "First points", "Our #1 pick", "Longshot (#3)",
        "Scorer in top picks?"]
rows = [
    ["TOR @ PHI\n123-112 TOR",
     "PHI won\nEmbiid beat Poeltl\n(Maxey ball)\nPHI no 1st score",
     "Ours TOR  X\nStarTool TOR  X\nTip sheet TOR  X\nTipProj TOR  X",
     "Jaylen Brown\n(PHI) 18 ft\nstep-back, MISSED",
     "Jakob Poeltl\n(TOR) layup\n11:07",
     "RJ Barrett: MISS\nBrown missed, Poeltl missed\na layup, Wade missed a 3,\nthen Poeltl layup (Quickley ast)",
     "Embiid: MISS",
     "Ours top 3: no (Poeltl #5, 11%)\nStarTool TOR top 2: no\nCheat Gm #1 Embiid / TOR Bsk\ntop Barrett: no"],
    ["DET @ WSH\n144-140 WSH",
     "DET won\nCollins beat Davis\n(Cunningham ball)\nDET scored 1st",
     "Ours WSH  X\nStarTool: no card\nTip sheet WSH  X\nTipProj DET  OK",
     "Daniss Jenkins\n(DET) 27 ft 3\nMADE",
     "Daniss Jenkins\n(DET) 3-pointer\n11:52",
     "Anthony Davis: MISS\nDET won the tip, Jenkins hit\na 3 on DET's 1st shot. Davis\nthen scored WSH's 1st (fadeaway)",
     "Collins: MISS",
     "Ours top 3: no\nStarTool: no card\nCheat Gm #1 Collins / DET Bsk\ntop Collins: no (Jenkins 12%)"],
    ["DAL @ MIN\n133-94 DAL",
     "MIN won\nGobert beat Gafford\n(McDaniels ball)\nMIN scored 1st",
     "Ours MIN  OK\nStarTool MIN  OK\nTip sheet MIN  OK\nTipProj MIN  OK",
     "Jonathan Kuminga\n(MIN) driving\nlayup, MADE",
     "Jonathan Kuminga\n(MIN) layup\n11:45",
     "LaMelo Ball: MISS\nLaMelo assisted Kuminga's\nlayup on MIN's 1st shot",
     "Flagg: MISS",
     "Ours top 3: YES (Kuminga #2, 13%)\nStarTool MIN top 2: no\nCheat Gm #1 Gafford/LaMelo,\nMIN Bsk top LaMelo: no\n(Kuminga 4%)"],
    ["CHA @ PHX\n101-96 CHA",
     "CHA won\nDiabate beat\nIghodaro\n(White ball)\nCHA no 1st score",
     "Ours PHX  X\nStarTool CHA  OK\nTip sheet PHX  X\nTipProj PHX  X",
     "Grayson Allen\n(CHA) 30 ft 3\nMISSED",
     "Jalen Green\n(PHX) 3 ft shot\n11:02",
     "Naz Reid: MISS\nAllen missed a 3, Diabate\nboard then TO (Green steal),\nBridges missed a 3, CHA TO,\nGreen 3 ft shot",
     "Brooks: MISS",
     "Ours top 3: no (Green #4, 11%)\nStarTool PHX top 2: no\nCheat PHX Bsk top: YES (Booker/\nGreen tied 28%); Gm #1 Allen: no"],
]
shades = [
    ['', '', 'r', 'r', '', 'r', 'r', 'r'],
    ['', '', 'r', 'g', '', 'r', 'r', 'r'],
    ['', '', 'g', 'g', '', 'r', 'r', 'g'],
    ['', '', 'r', 'r', '', 'r', 'r', 'g'],
]
draw("NBA First Basket Results, Thu 11/12/26 (4 games)\nOur #1 picks 0-4, longshots 0-4. Tips: ours 1-3, StarTool 2-1, tip sheet 1-3, TipProj 2-2",
     cols, [0.075, 0.11, 0.12, 0.115, 0.105, 0.19, 0.075, 0.21], rows, shades,
     "Green = hit / right, red = miss / wrong. Tip calls cell colored by our call. First points count free throws (FanDuel rule). "
     "Expected jumpers jumped in all 4. Tip winner scored first 2 of 4.",
     'game', 1.75, fs=10, fy=0.09)

# ---------- Chart 2: team first basket ----------
cols = ["Team", "Team's first scorer", "Our top 2", "StarTool top 2", "Cheat sheet top 2 (1st Bsk)"]
rows = [
    ["TOR", "Jakob Poeltl, layup", "Murray-Boyles / Barrett: MISS", "Barrett / Quickley: MISS", "Barrett / Quickley: MISS"],
    ["PHI", "Jaylen Brown, free throw", "Embiid / Brown: HIT", "Brown / Embiid: HIT", "Embiid / Brown: HIT"],
    ["DET", "Daniss Jenkins, 3", "Collins / Cunningham: MISS", "no card", "Collins / A. Thompson: MISS"],
    ["WSH", "Anthony Davis, fadeaway", "Davis / Sarr: HIT (#1)", "no card", "Dybantsa / Davis: HIT"],
    ["DAL", "Daniel Gafford, free throw", "Flagg / Gafford: HIT", "Flagg / Irving: MISS", "Irving / Flagg: MISS"],
    ["MIN", "Jonathan Kuminga, layup", "LaMelo / Kuminga: HIT", "LaMelo / Dosunmu: MISS", "LaMelo / Gobert: MISS"],
    ["CHA", "Coby White, driving layup", "Reid / G. Allen: MISS", "White / G. Allen: HIT (#1 tie)", "G. Allen / Diabate: MISS"],
    ["PHX", "Jalen Green, 3 ft shot", "Booker / Brooks: MISS", "Booker / Brooks: MISS", "Booker / Green: HIT (#1 tie)"],
]
sh = lambda t: 'g' if 'HIT' in t else 'r' if 'MISS' in t else ''
shades = [[''] * 2 + [sh(x) for x in r[2:]] for r in rows]
draw("NBA Team First Basket Results, Thu 11/12/26\nTop 2 hit: ours 4 of 8, StarTool 2 of 6, cheat sheet 3 of 8 (random about 40%)",
     cols, [0.07, 0.22, 0.24, 0.235, 0.235], rows, shades,
     "Green = scorer in that source's top 2, red = not. Free throws count. StarTool DET @ WSH card did not load. "
     "Season to date top 2: ours 50%, StarTool 42%, cheat sheet 43%.",
     'team', 0.62, fs=12, fy=0.12)
