#!/usr/bin/env python3
"""10/24/26 check: does the model underrate the jumper (usually the starting center) when his team wins the tip?
Walk-forward with the current model (V2 + ramp), same games as backtest_fb.py --team. For each jumper and each other
starter, compares the model's chance of the first FG given the tip result (share x 64% or 36%) with what happened.

  python3 analysis/nba/center_check.py
"""
import os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_fb as bt  # noqa: E402
from build_nba_tab import V2  # noqa: E402

bt.run({'cur': dict(V2, ramp=True)}, team=True)
A = defaultdict(lambda: defaultdict(float))
for r in bt.REC:
    g, d = r['g'], r['d']
    seas = '26-27' if d >= '2026-07-01' else '25-26'
    tw, win, fbt = g['tip']['w'], g['fb'][0], g['fb'][1]
    jset = {pid for pid, tm in g['tip']['j']}
    for tm in (g['away'], g['home']):
        for p0 in r['st'][tm]:
            pid = p0[0]
            share = r['probs'][pid] / r['pt'][tm]
            role, c = ('jumper' if pid in jset else 'other'), ('won tip' if tm == tw else 'lost tip')
            for s in (seas, 'all'):
                a = A[(s, role, c)]
                a['n'] += 1; a['pred'] += share * (0.64 if c == 'won tip' else 0.36); a['act'] += win == pid
                if fbt == tm:
                    a['tn'] += 1; a['tsh'] += share; a['tact'] += win == pid
print(f"{'season':6} {'role':7} {'tip':9} {'n':>5} {'model':>6} {'actual':>6} | {'team 1st':>8} {'model sh':>8} {'actual sh':>9}")
for k in sorted(A):
    a = A[k]
    print(f"{k[0]:6} {k[1]:7} {k[2]:9} {int(a['n']):5d} {a['pred'] / a['n']:6.1%} {a['act'] / a['n']:6.1%} | "
          f"{int(a['tn']):8d} {a['tsh'] / a['tn']:8.1%} {a['tact'] / a['tn']:9.1%}")
