"""Method of First Basket chart, FanDuel format (player + method only, 11/18/26).
Per play-list game: each starter's chance to score the first points by Dunk / Layup / Other / 3PT / FT, fair odds;
gold = bet. Run from the repo root: python3 analysis/nba/out/charts/method_chart.py [DATE]
(reads analysis/nba/out/method_longshots_<DATE>.json from method_longshots.py)"""
import json, sys, datetime as dt, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['text.parse_math'] = False
D = sys.argv[1] if len(sys.argv) > 1 else '2026-11-18'
J = json.load(open(f'analysis/nba/out/method_longshots_{D}.json'))
OUT = f'analysis/nba/out/charts/method_{D}.png'
COLS = [('dunk', 'Dunk'), ('layup', 'Layup'), ('other', 'Other'), ('3', '3PT'), ('ft', 'Free Throw')]
BG = '#0f1420'; CARD = '#1a2233'; TXT = '#e8ecf3'; MUTED = '#9aa4b5'; GOLD = '#f5c542'; GREEN = '#4cd38a'
def am(p): d = 1 / p; return '+{:,}'.format(round((d - 1) * 100)) if d >= 2 else '-%d' % round(100 / (d - 1))
pk = {(k['player'], k['key']): k for k in J['picks']}
games = J['games']; nrows = sum(len(g['players']) + 1.6 for g in games)
H = 3.2 + nrows * 0.5 + 2.6 + len(J['picks']) * 0.5
fig = plt.figure(figsize=(8, H * 0.62), dpi=200); fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, H); ax.axis('off')
day = dt.date.fromisoformat(D).strftime('%a %m/%d').upper()
ax.text(3, H - 0.6, 'METHOD OF FIRST BASKET  •  ' + day, color=TXT, fontsize=15, weight='bold', va='center')
ax.text(3, H - 1.3, 'FanDuel format: player + method. Est % to score the game\'s first points that way (FT counts).',
        color=MUTED, fontsize=7.6, va='center')
ax.text(3, H - 1.85, 'Other = jumpers, floaters, hooks, tip shots. Gold = bet (take-at = fair x1.2 or longer).',
        color=MUTED, fontsize=7.6, va='center')
xs = [37, 50.5, 64, 77.5, 91]; y = H - 2.8
lg = J['league_first_points']
for (k, lab), x in zip(COLS, xs):
    ax.text(x, y, f'{lab}\n(lg {lg[k] * 100:.0f}%)', color=MUTED, fontsize=7.4, weight='bold', va='center', ha='center')
y -= 0.9
for g in games:
    ax.text(3, y, g['game'], color=GOLD, fontsize=9.5, weight='bold', va='center'); y -= 0.55
    for i, r in enumerate(g['players']):
        if i % 2 == 0: ax.add_patch(plt.Rectangle((2, y - 0.25), 96, 0.5, fc=CARD, ec='none'))
        ax.text(3, y, f"{r['player']} ({r['tm']})", color=TXT, fontsize=7.6, va='center')
        ax.text(29, y, f"{r['p_first'] * 100:.0f}%", color=MUTED, fontsize=7, va='center', ha='right')
        for (k, _), x in zip(COLS, xs):
            p = r['p'][k]; b = pk.get((r['player'], k))
            col = GOLD if b else (GREEN if p >= 0.04 else TXT)
            s = f"{p * 100:.1f}%  {am(p) if p > 0.002 else '-'}"
            ax.text(x, y, s + (f"  ${b['stake']:.2f}" if b else ''), color=col, fontsize=6.8,
                    weight='bold' if b else 'normal', va='center', ha='center')
        y -= 0.5
    y -= 0.55
ax.text(3, y, 'BETS ($1.00, ranked by likelihood)', color=GOLD, fontsize=9.5, weight='bold', va='center'); y -= 0.55
for k in J['picks']:
    ax.text(4, y, f"{k['player']} - {k['method']}  ${k['stake']:.2f}   est {k['p'] * 100:.1f}%, fair {k['fair']}, "
            f"take {k['take']}", color=TXT, fontsize=8, va='center'); y -= 0.5
ax.text(3, y - 0.1, 'Second column = his first basket chance. Green = 4%+. Longshots on a noisy market; small stakes.',
        color=MUTED, fontsize=7.2, va='center')
fig.savefig(OUT, facecolor=BG)
print(OUT)
