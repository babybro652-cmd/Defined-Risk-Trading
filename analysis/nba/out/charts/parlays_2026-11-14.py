"""Tim's 11/14 first basket plan chart (top 3 per game, cost, best combos, injuries, voids).
Run from repo root: python3 analysis/nba/out/charts/parlays_2026-11-14.py"""
import csv, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HEAD, G, R, ALT = '#1f3a5f', '#cdebd3', '#f6cccc', '#eef2f7'
VOID = set()
rows = [r for r in csv.DictReader(open('analysis/nba/out/parlays_2026-11-14.csv')) if not r.get('dropped')]
c = [r for r in json.load(open('analysis/nba/out/fb_candidates.json')) if r.get('inj') != 'Out']
games = [('DEN', 'NO', '7:00'), ('DAL', 'CLE', '7:30'), ('DET', 'MIA', '8:00'), ('CHI', 'MIN', '8:00')]
am = lambda d: f"+{round((d - 1) * 100):,}" if d >= 2 else f"-{round(100 / (d - 1))}"

fig = plt.figure(figsize=(16, 15))
fig.suptitle("Tim's NBA First Basket Plan, Sat 11/14/26 (tip edge 70%+ games only)", fontsize=17, fontweight='bold', y=0.985)


def table(ax, title, cols, data, widths, shades=None, fs=10.5):
    ax.axis('off'); ax.set_title(title, fontsize=13, fontweight='bold', loc='left')
    tb = ax.table(cellText=data, colLabels=cols, colWidths=widths, loc='upper center', cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(fs); tb.scale(1, 1.55)
    for (r, cc), cl in tb.get_celld().items():
        if r == 0:
            cl.set_facecolor(HEAD); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
        else:
            s = shades[r - 1][cc] if shades else ''
            cl.set_facecolor(G if s == 'g' else R if s == 'r' else ALT if r % 2 == 0 else 'white')


# 1. top 3 per game now
data, sh = [], []
logged = {'DEN @ NO': 'Jokic / Murray / Bey', 'DAL @ CLE': 'Bryant / M. Thomas / Flagg (swapped 6:45 PM)',
          'DET @ MIA': 'Adebayo / Giannis / Collins', 'CHI @ MIN': 'Kuminga / LaMelo / McDaniels'}
for a, h, t in games:
    v = sorted([r for r in c if r['tm'] in (a, h)], key=lambda r: -r['p_v2'])[:3]
    top = '   '.join(f"#{i} {r['player']} {r['p_v2'] * 100:.1f}% ({am(1 / r['p_v2'])})" for i, r in enumerate(v, 1))
    g = f"{a} @ {h}"
    data.append([f"{g} {t}", top, logged[g]]); sh.append(['', '', 'r' if 'VOID' in logged[g] else ''])
table(fig.add_axes([0.03, 0.75, 0.94, 0.19]), "Games with tip edge 70%+ (DEN 75, CLE 71, MIA 70, MIN 78): top 3 now and logged",
      ["Game", "Model top 3 now (6:30 PM)", "Logged straights (#1 / #2 / #3)"], data, [0.12, 0.55, 0.33], sh)

# 2. cost
cost = [["Straights #1 and #2", "8", "$1.00", "$8.00"], ["Straights #3", "4", "$1.00", "$4.00"],
        ["2-leg parlays", "24", "$0.50", "$12.00"], ["3-leg parlays", "32", "$0.10", "$3.20"],
        ["4-leg parlays", "16", "$0.10", "$1.60"], ["Total", "84", "", "$28.80"]]
table(fig.add_axes([0.03, 0.47, 0.42, 0.24]), "Cost", ["Bet", "Count", "Stake", "Total"], cost, [0.46, 0.16, 0.18, 0.2])

# 3. best combo at each size (highest hit chance, CLE legs void -> parlay plays without them)
best = []
for k in (1, 2, 3, 4):
    cand = []
    for r in rows:
        if int(r['legs']) != k:
            continue
        legs = r['picks'].split(' + ')
        live = [l for l in legs if l not in VOID]
        if not live:
            continue
        q = {**{rr['picks']: float(rr['p']) for rr in rows if rr['legs'] == '1'}}
        p = 1
        for l in live:
            p *= q[l]
        cand.append((p, legs, live))
    full = [x for x in cand if len(x[2]) == len(x[1])]
    p, legs, live = max(full or cand)
    note = '' if len(live) == len(legs) else f" (CLE leg void, plays as {len(live)})"
    best.append([f"{k}-leg" if k > 1 else "Straight", ' + '.join(live) + note, am(1 / p), f"{p * 100:.2f}%"])
table(fig.add_axes([0.5, 0.47, 0.47, 0.24]), "Best combo at each size (fully live where possible)", ["Size", "Legs", "Fair", "Hit chance"],
      best, [0.13, 0.55, 0.17, 0.15], fs=10)

# 4. injuries
inj = [["CLE", "Allen, Mitchell, Harden, Watson, Mobley OUT (rested). Starters: Porter Jr., M. Thomas, Tyson, Hezonja, Bryant", "r"],
       ["MEM", "Jerome OUT (Spencer starts); Edey Q (ankle), Grant Q", "y"],
       ["BKN", "Porter Jr. Q (RotoWire 6:30); Traore probable", "y"],
       ["CHI", "J. Smith Q (finger), Powell Q (back), Claxton Q", "y"],
       ["MIA", "Larsson OUT (Gardner starts); Klay and Giannis play", ""],
       ["NO / DEN", "Murphy OUT; Missi available and starts; Murray plays", ""]]
table(fig.add_axes([0.03, 0.2, 0.94, 0.23]), "Injury status (NBA report 6:30 PM, ESPN, RotoWire)", ["Team", "Status"],
      [r[:2] for r in inj], [0.1, 0.9], [['', 'r' if r[2] == 'r' else ''] for r in inj])

# 5. voids
nv = sum(1 for r in rows if int(r['legs']) > 1 and set(r['picks'].split(' + ')) & VOID)
vtxt = ("Dropped 11/14 (tip under 70%): BKN @ MEM (MEM 66%), so every Edey / Coward leg, all 5-leg parlays and the Edey, Coward, Porter Jr. straights.\n"
        "163 rows kept in Bets as Placed = Dropped, stake 0. Live set: 84 bets, $28.80. CLE swap 6:45 PM: Bryant, M. Thomas, Flagg.\n"
        "Earlier void pick rows: Allen and Watson CLE team first basket, Mitchell 25+ points. First basket is mostly noise.")
fig.text(0.03, 0.08, vtxt, fontsize=11, va='bottom', wrap=True)
plt.savefig('analysis/nba/out/charts/parlays_2026-11-14.png', dpi=100, bbox_inches='tight')
