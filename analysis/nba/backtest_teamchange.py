#!/usr/bin/env python3
"""Team-change rule backtest (11/5/26): starts with a player's OTHER teams (earlier this season or last season) count
`prior` x; optional ramp N fades that weight from 1 at 0 starts with his current team to `prior` at N starts.
Base = the 11/5 default (first points fit + shot type 0.7). Walk-forward, same harness as backtest_fix.py.
Scored on all games and on games with at least one team-changer starting.

  python3 analysis/nba/backtest_teamchange.py
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest_fix import run, score  # noqa: E402

BASE = {'fp_fit': True, 'w_shot3': 0.7}
V = {'base (prior 1)': dict(BASE)}
for q in (0.75, 0.5, 0.35, 0.25, 0.1):
    V[f'prior {q}'] = dict(BASE, prior=q)
for q, n in ((0.5, 10), (0.25, 10), (0.25, 20), (0.1, 20), (0.1, 40)):
    V[f'prior {q} ramp {n}'] = dict(BASE, prior=q, ramp=n)

recs = run(V)
parts = {'25-26': [r for r in recs if r['d'] < '2026-07-01'], '26-27': [r for r in recs if r['d'] >= '2026-07-01']}
parts |= {k + ' chg': [r for r in v if r['chg']] for k, v in list(parts.items())}
res = {k: {p: score(rs, k) for p, rs in parts.items()} for k in V}
print('games:', ', '.join(f'{p} {len(rs)}' for p, rs in parts.items()))
print(f"{'variant':22}" + ''.join(f"{p:>16}" for p in parts))
for k in V:
    row = ''
    for p in parts:
        dd = [x - y for x, y in zip(res[k][p]['llg'], res['base (prior 1)'][p]['llg'])]
        m = sum(dd) / len(dd)
        se = math.sqrt(sum((x - m) ** 2 for x in dd) / (len(dd) - 1) / len(dd)) if any(dd) else 0
        row += f"{res[k][p]['ll']:9.4f} ({se:.4f})"
    print(f"{k:22}{row}")
