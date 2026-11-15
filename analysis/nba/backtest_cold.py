#!/usr/bin/env python3
"""Cold-opening backtest (11/15/26): do this season's cold openings (first-shot make rate 37.7% vs 48.6% last season)
call for current-season league make rates in the chain model?

Walk-forward, no lookahead (backtest_chain.run: each day is priced with data through the day before). Variants
(cold_league() and mk_counts() in backtest_chain.py):
  kfg_w N         league make rate by shot type (the player shrink target) = last season + N x this season
  open_a A, w W   every player's make rate x (league opening make rate / league full-game make rate) ** A,
                  both = last season + W x this season; opening = each team's first 3 FGA
  mk_w N          player make rates (rim / j2 / 3) count this season's games N x (W_DEFAULT 3 elsewhere)
Settings are chosen on 2026-27 games through 10/31 (tune) and reported on 11/1 on (test).
Scores: log loss of the game's first points scorer, #1 pick predicted vs hit, top-3 coverage, mean chance by rank.

  python3 analysis/nba/backtest_cold.py            # grid, writes out/backtest_cold.json
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest_chain as bc  # noqa: E402

SPLIT = '2026-11-01'


def metrics(recs, k):
    o = dict(n=0, ll=0.0, p1=0.0, h1=0, h2=0, h3=0, p2=0.0, p3=0.0, top3=0)
    for r in recs:
        pr, w = r['probs'][k], r['win']
        if w not in pr:
            continue
        z = sum(pr.values())
        pr = {p: v / z for p, v in pr.items()}
        rk = sorted(pr, key=pr.get, reverse=True)
        o['n'] += 1
        o['ll'] += -math.log(max(pr[w], 1e-6))
        for i, key in enumerate(('1', '2', '3')):
            o['p' + key] += pr[rk[i]]; o['h' + key] += rk[i] == w
        o['top3'] += w in rk[:3]
    n = max(1, o['n'])
    return {'n': o['n'], 'll': o['ll'] / n, 'p1': o['p1'] / n, 'hit1': o['h1'] / n, 'p2': o['p2'] / n,
            'hit2': o['h2'] / n, 'p3': o['p3'] / n, 'hit3': o['h3'] / n, 'top3': o['top3'] / n,
            'exp3': (o['p1'] + o['p2'] + o['p3']) / n}


def main():
    V = {'chain': {}}
    for w in (3, 10, 1000):
        V[f'kfg_w {w}'] = dict(kfg_w=w)
    for a in (0.5, 1.0, 1.5):
        for w in (3, 10, 1000):
            V[f'open a{a} w{w}'] = dict(open_a=a, open_w=w)
    for w in (6, 10):
        V[f'mk_w {w}'] = dict(mk_w=w)
        V[f'mk_w {w} + open a1.0 w10'] = dict(mk_w=w, open_a=1.0, open_w=10)
    V['kfg_w 10 + open a1.0 w10'] = dict(kfg_w=10, open_a=1.0, open_w=10)
    if len(sys.argv) > 1 and sys.argv[1].startswith('{'):
        V = {'chain': {}} | json.loads(sys.argv[1])
    recs = [r for r in bc.run(V) if r['d'] >= '2026-07-01']
    parts = {'tune': [r for r in recs if r['d'] < SPLIT], 'test': [r for r in recs if r['d'] >= SPLIT],
             'all 26-27': recs}
    res = {k: {p: metrics(rs, k) for p, rs in parts.items()} for k in V}
    print('games ' + ', '.join(f'{p} {len(rs)}' for p, rs in parts.items()))
    for p in parts:
        print(f'\n{p}: {"model":28} {"LL":>7} {"#1 pred":>7} {"#1 hit":>6} {"#2 p/h":>11} {"#3 p/h":>11} {"top3":>5} {"exp3":>5}')
        for k in V:
            m = res[k][p]
            print(f'{"":6}{k:28} {m["ll"]:7.4f} {m["p1"]:7.1%} {m["hit1"]:6.1%} {m["p2"]:5.1%}/{m["hit2"]:5.1%} '
                  f'{m["p3"]:5.1%}/{m["hit3"]:5.1%} {m["top3"]:5.1%} {m["exp3"]:5.1%}')
    json.dump(res, open(os.path.join(HERE, 'out', 'backtest_cold.json'), 'w'), indent=1)
    return res


if __name__ == '__main__':
    main()
