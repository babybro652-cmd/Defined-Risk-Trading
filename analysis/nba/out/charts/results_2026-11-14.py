"""11/14/26 NBA results charts: who scored first, who won the tip, first shot vs first score.
Styled like results_2026-11-13.py. Run from repo root: python3 analysis/nba/out/charts/results_2026-11-14.py"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

G, R, N, HEAD, ALT = '#cdebd3', '#f6cccc', '#ffffff', '#1f3a5f', '#eef2f7'
OUT = 'analysis/nba/out/charts/results_2026-11-14_'


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
    plt.close(fig)


# ---------- Chart 1: who scored first ----------
cols = ["Game", "First points (game)", "Our #1", "Our #2", "Our #3", "Tim's play", "StarTool #1 / sheet #1"]
rows = [
    ["DEN @ NO\n116-108 DEN", "Jeremiah Fears (NO)\n26 ft 3, 11:01", "Jokic: MISS\n(scored DEN's 1st, FT)", "Murray: MISS",
     "Bey: MISS", "In set (DEN 75%)\nall legs lost", "Zion: no\nMurray: no"],
    ["DAL @ CLE\n117-127 CLE", "Meleek Thomas (CLE)\n25 ft 3, 11:43", "Bryant: MISS\n(assisted it)", "M. Thomas: HIT\nfair +675",
     "Flagg: MISS\n(scored DAL's 1st)", "In set (CLE 71%)\nM. Thomas straight W", "D. Mitchell (out)\nsheet: Gafford: no"],
    ["DET @ MIA\n117-137 MIA", "Ausar Thompson (DET)\ndunk, 11:55", "Adebayo: MISS", "Giannis: MISS",
     "Collins: MISS", "In set (MIA 70%)\nall legs lost", "Cunningham: no\nAdebayo: no"],
    ["BKN @ MEM\n110-129 MEM", "Julius Randle (BKN)\ntip-in, 11:17", "Edey: VOID (DNP)", "Coward: MISS",
     "Porter Jr.: VOID (DNP)", "Skipped (MEM 66%)", "Randle: YES\nsheet: no"],
    ["CHI @ MIN\n117-106 CHI", "LaMelo Ball (MIN)\nlayup, 11:10", "Kuminga: MISS", "LaMelo: HIT\nfair +591",
     "McDaniels: MISS", "In set (MIN 78%)\nLaMelo straight W", "LaMelo: YES\nLaMelo: YES"],
]
sh = lambda t: 'g' if ('HIT' in t or 'YES' in t or ' W' in t) else 'r' if ('MISS' in t or 'lost' in t or 'no' in t.split()[-1:]) else ''
shades = [['', '', sh(r[2]), sh(r[3]), sh(r[4]), sh(r[5]), 'g' if 'YES' in r[6] else 'r'] for r in rows]
draw("NBA First Basket Results, Sat 11/14/26 (5 games)\nOur top 3 held the scorer in 2 of 5 (both at #2: M. Thomas, LaMelo). Our #1 0 for 5",
     cols, [0.09, 0.15, 0.15, 0.13, 0.14, 0.15, 0.19], rows, shades,
     "Green = hit, red = miss. First points count free throws (FanDuel rule). Tim's set: tip edge 70%+ games, top 3 straights, top 2 in parlays. "
     "Straights 2-10; only parlay hit: M. Thomas + LaMelo 2-leg (fair +5,249).",
     'game', 1.0, fs=10.5, fy=0.05)

# ---------- Chart 2: who won the tip ----------
cols = ["Game", "Expected jumpers (ours)", "Actual jumpers", "Tip winner", "Ours", "StarTool", "Tip sheet", "TipProj", "Tip winner scored 1st?"]
rows = [
    ["DEN @ NO", "Jokic vs Missi", "Jokic vs Missi", "DEN (Gordon)", "DEN 75%  OK", "DEN 55  OK", "DEN  OK", "DEN 71  OK", "no (Fears, NO)"],
    ["DAL @ CLE", "Gafford vs Bryant", "Gafford vs Bryant", "CLE (Hezonja)", "CLE 71%  OK", "CLE 81  OK", "CLE  OK", "CLE 81  OK", "YES (M. Thomas)"],
    ["DET @ MIA", "Collins vs Adebayo", "Collins vs Adebayo", "DET (Cunningham)", "MIA 70%  X", "loading", "MIA  X", "MIA 71  X", "YES (A. Thompson)"],
    ["BKN @ MEM", "Sharpe vs Edey", "Sharpe vs Stewart\n(Edey out)", "BKN (Clowney)", "MEM 66%  X", "MEM 54  X", "MEM  X", "MEM 79  X", "YES (Randle)"],
    ["CHI @ MIN", "J. Smith vs Gobert", "Z. Collins vs Gobert\n(J. Smith out)", "MIN (Dosunmu)", "MIN 78%  OK", "MIN 69  OK", "MIN  OK", "MIN 79  OK", "YES (LaMelo)"],
]
ok = lambda t: 'g' if ('OK' in t or 'YES' in t) else 'r' if (' X' in t or t.startswith('no')) else ''
shades = [['', '', 'g' if r[1] == r[2] else 'r', '', ok(r[4]), ok(r[5]), ok(r[6]), ok(r[7]), ok(r[8])] for r in rows]
draw("Who won the tip, Sat 11/14/26\nOurs 3-2, StarTool 3-1, tip sheet 3-2, TipProj 3-2. Every source picked the same side in all 5",
     cols, [0.08, 0.13, 0.14, 0.11, 0.1, 0.09, 0.08, 0.09, 0.14], rows, shades,
     "Expected jumpers right 3 of 5 (Edey and J. Smith sat). DET won the tip at MIA 70% for us. Tip winner scored first 4 of 5. "
     "StarTool tip % is each team's own rate, not head to head.",
     'tip', 0.55, fs=11, fy=0.06)

# ---------- Chart 3: first shot vs first score, per team ----------
cols = ["Team", "Our 1st-shot pick", "Team's first shot", "What happened next", "Team's first points", "Our 2nd-chance pick", "Either pick scored?"]
rows = [
    ["DEN", "Jokic", "Gordon FTs 0 of 2\n(1st FGA C. Johnson 3 MISS)", "NO scored first; Jokic FT\nat 10:46", "Jokic (FT)", "Murray: MISS", "YES (1st-shot pick)"],
    ["NO", "Bey", "Fears, 26 ft 3 MADE", "- (Zion assist)", "Fears", "Zion: MISS", "no"],
    ["CLE", "M. Thomas", "M. Thomas, 25 ft 3 MADE", "- (Bryant assist)", "M. Thomas", "Bryant: MISS", "YES (1st-shot pick)"],
    ["DAL", "Flagg", "Flagg, 13 ft MADE", "- (Washington assist)", "Flagg", "Gafford: MISS", "YES (1st-shot pick)"],
    ["DET", "Collins", "A. Thompson, dunk MADE", "- (Cunningham assist)", "A. Thompson", "Cunningham: MISS", "no"],
    ["MIA", "Adebayo", "Gardner, 23 ft 3 MADE", "- (Giannis assist)", "Gardner", "Giannis: MISS", "no"],
    ["BKN", "Porter Jr. (DNP)", "Sharpe, 23 ft 3 MISS", "MEM TO, Wolf missed,\nRandle tip-in", "Randle", "Sharpe: MISS", "no"],
    ["MEM", "Edey (DNP)", "Stewart, 3 ft MADE", "- (Spencer assist)", "Stewart", "Coward: MISS", "no"],
    ["MIN", "Kuminga", "LaMelo, 26 ft 3 MISS", "Powell missed, Kuminga DREB,\nLaMelo layup", "LaMelo", "LaMelo: HIT", "YES (2nd-chance pick)"],
    ["CHI", "Powell", "Powell, floater MISS", "Collins blocked, Giddey\nmissed, Collins OREB, Giddey", "Giddey", "J. Smith (DNP)", "no"],
]
shades = [['', '', 'g' if r[2].split(',')[0].split(' FTs')[0] in r[1] else 'r', '', '', sh(r[5]), 'g' if r[6].startswith('YES') else 'r']
          for r in rows]
draw("First shot vs first score, Sat 11/14/26: did our two-slot picks score their team's first points?\n"
     "1st-shot pick took the team's first shot 3 of 8 (M. Thomas, Flagg, Powell). Either pick scored: 4 of 10",
     cols, [0.06, 0.12, 0.19, 0.22, 0.11, 0.14, 0.14], rows, shades,
     "Green in column 3 = our 1st-shot pick took the team's first shot. 6 of 10 teams made their first shot (11/13: 4 of 18). "
     "Role players again: Fears, A. Thompson, Gardner, Stewart, Giddey.",
     'firstshot', 0.55, fs=10.5, fy=0.05)
