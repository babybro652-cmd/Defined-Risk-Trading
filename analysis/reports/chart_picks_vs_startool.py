#!/usr/bin/env python3
"""Chart for the 10/30/26 picks vs StarTool report. Reads out/summary.json (from picks_vs_startool.py)."""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'out', 'summary.json')))
BLUE, ORANGE, INK, INK2, GRID, SURF = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
plt.rcParams.update({'font.size': 11, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK, 'axes.facecolor': SURF, 'figure.facecolor': SURF})
fig, axes = plt.subplots(3, 1, figsize=(10, 14), gridspec_kw={'height_ratios': [1.25, 0.8, 1.1]})

# 1. hit rate vs expected
c = D['cats']; sb = D['star_bomb']
rows = [('NBA first basket (ours)', c['NBA first basket']['w_p'], c['NBA first basket']['n_p'], c['NBA first basket']['exp']),
        ('StarTool stars (NBA FB)', sb['star']['hits'], sb['star']['n'], sb['star']['expected']),
        ('StarTool bombs (NBA FB)', sb['bomb']['hits'], sb['bomb']['n'], sb['bomb']['expected']),
        ('NBA points (ours)', c['NBA points']['w_p'], c['NBA points']['n_p'], c['NBA points']['exp']),
        ('NBA threes (ours)', c['NBA threes']['w_p'], c['NBA threes']['n_p'], c['NBA threes']['exp']),
        ('NHL anytime goal (ours)', c['NHL anytime goal']['w_p'], c['NHL anytime goal']['n_p'], c['NHL anytime goal']['exp']),
        ('NHL SOG 3+ (ours)', c['NHL SOG 3+']['w_p'], c['NHL SOG 3+']['n_p'], c['NHL SOG 3+']['exp'])]
ax = axes[0]
y = list(range(len(rows)))[::-1]
for yi, (lab, w, n, e) in zip(y, rows):
    ax.barh(yi, w / n, height=0.5, color=BLUE)
    ax.plot([e / n], [yi], marker='D', ms=9, color=ORANGE, mec=SURF, mew=2, ls='none')
    ax.text(max(w / n, e / n) + 0.02, yi, f'{w} of {n} ({w / n:.0%}) vs {e / n:.0%} expected', va='center', color=INK2, fontsize=10)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
ax.set_xlim(0, 1.25); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.grid(axis='x', color=GRID); ax.set_axisbelow(True)
ax.set_title('Hit rate (bar) vs the model\'s own expected rate (diamond), picks with a logged %', loc='left', color=INK, fontsize=12)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)

# 2. ours vs StarTool, 50 shared games
s = D['startool']
ax = axes[1]
labs = ['Top pick scored first', 'Scorer in top 2', 'Scorer in top 4']
ours = [s['our_top_hits_same_games'], s['our_in_top2'], s['our_in_top4']]
st = [s['st_top_hits_same_games'], s['st_in_top2'], s['st_in_top4']]
x = range(len(labs))
ax.bar([i - 0.2 for i in x], ours, width=0.38, color=BLUE, label='Our model')
ax.bar([i + 0.2 for i in x], st, width=0.38, color=ORANGE, label='StarTool')
for i in x:
    ax.text(i - 0.2, ours[i] + 0.5, str(ours[i]), ha='center', color=INK, fontsize=10)
    ax.text(i + 0.2, st[i] + 0.5, str(st[i]), ha='center', color=INK, fontsize=10)
ax.set_xticks(list(x)); ax.set_xticklabels(labs)
ax.set_ylabel('games (of 50)'); ax.set_ylim(0, 32)
ax.grid(axis='y', color=GRID); ax.set_axisbelow(True)
ax.legend(frameon=False, loc='upper left')
ax.set_title(f"NBA first basket, 50 games with both lists: mean rank of actual scorer ours {s['our_mean_rank_same']} vs StarTool {s['st_mean_rank_same']} (of 10)",
             loc='left', color=INK, fontsize=11)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)

# 3. ROI at $0.20, slip odds only (categories with 4+ slips)
ax = axes[2]
rr = []
for k, v in c.items():
    if v['n_slip'] >= 4:
        rr.append((k, v['pl_slip'] / (0.2 * v['n_slip']), v['n_slip']))
rr.sort(key=lambda t: t[1])
yy = range(len(rr))
ax.barh(list(yy), [t[1] for t in rr], height=0.5, color=BLUE)
for yi, (k, roi, n) in zip(yy, rr):
    ax.text(roi + (0.04 if roi >= 0 else -0.04), yi, f'{roi:+.0%} on {n}', va='center', ha='left' if roi >= 0 else 'right',
            color=INK2, fontsize=10)
ax.axvline(0, color=INK2, lw=1)
ax.set_yticks(list(yy)); ax.set_yticklabels([t[0] for t in rr])
lim = max(abs(t[1]) for t in rr) + 0.5
ax.set_xlim(-1.2, lim)
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.grid(axis='x', color=GRID); ax.set_axisbelow(True)
ax.set_title('ROI of our picks at FanDuel slip odds (only categories with 4+ priced slips)', loc='left', color=INK, fontsize=12)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)

fig.suptitle('Our picks vs StarTool, season to date (through 10/29/26)', x=0.02, ha='left', fontsize=15, color=INK, fontweight='bold')
fig.text(0.02, 0.005, 'Small samples. First basket picks that hit pay +500 to +1100, so one hit moves ROI a lot.', color=INK2, fontsize=9)
fig.tight_layout(rect=(0, 0.015, 1, 0.97))
fig.savefig(os.path.join(HERE, '2026-10-30-picks-vs-startool.png'), dpi=110)
