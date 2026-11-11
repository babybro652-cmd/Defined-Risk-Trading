#!/usr/bin/env python3
"""Test 11/11/26 (Tim, 11/8): blend each starter's past share of his TEAM's first points (FT count, FanDuel rule)
into the chain model's first-possession shooter share (chain_model.py w_tp, shrunk to 1/5 with k_tp starts).

Same walk-forward games as backtest_chain.py (no lookahead). Out of sample: choose (w, k) on 2025-26, report 2026-27.
Scores vs the default chain (w 0):
  game LL   log loss of the game's first points scorer over the 10 starters
  team LL   log loss of each team's own first points scorer over its 5 starters (team_first, other team ignored)
  top 2     team first points scorer in the team's 2 highest team-first chances (random = 40%)
  two-slot  same with the two-slot pair

  python3 analysis/nba/backtest_tpshare.py      # table, writes out/backtest_tpshare.json
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest_chain as bc  # noqa: E402
import backtest_fix as bf  # noqa: E402

W = (0.15, 0.3, 0.5, 0.7)
K = (10, 20, 40)


def team_scores(recs, k):
    ll, top2, slot = [], [0, 0], [0, 0]
    for r in recs:
        pr = r['team'][k]
        for tm in (r['g']['away'], r['g']['home']):
            tgt = r['tp'].get(tm)
            if not tgt or tgt not in pr:
                continue
            ll.append(-math.log(max(pr[tgt], 1e-6)))
            mine = sorted((p for p in pr if r['tmof'][p] == tm), key=pr.get, reverse=True)[:2]
            top2[0] += tgt in mine; top2[1] += 1
            if k in r.get('slotsv', {}):
                slot[0] += tgt in r['slotsv'][k][tm]; slot[1] += 1
    return ll, top2, slot


def se(a, b):
    d = [x - y for x, y in zip(a, b)]
    m = sum(d) / len(d)
    return m, math.sqrt(sum((x - m) ** 2 for x in d) / (len(d) - 1) / len(d))


def main():
    v = {'chain': {}}
    for k in K:
        for w in W:
            v[f'w{w} k{k}'] = dict(w_tp=w, k_tp=k)
    for w in (0.3, 0.5):
        v[f'w{w} k20 q2'] = dict(w_tp=w, k_tp=20, tp_q2=True)
    recs = bc.run(v)
    parts = {'2025-26': [r for r in recs if r['d'] < '2026-07-01'], '2026-27': [r for r in recs if r['d'] >= '2026-07-01']}
    out = {}
    print(f"games {', '.join(f'{p} {len(rs)}' for p, rs in parts.items())}")
    print(f"{'model':16}" + ''.join(f" | {p}: gameLL (d, SE)       teamLL (d, SE)      top2   2slot" for p in parts))
    base = {}
    for name in ['current', 'chain'] + [x for x in v if x != 'chain']:
        row = f'{name:16}'
        out[name] = {}
        for p, rs in parts.items():
            g = bf.score(rs, name)
            tl, t2, sl = team_scores(rs, name)
            if name == 'chain':
                base[p] = (g['llg'], tl)
            dg, sg = se(g['llg'], base[p][0]) if name != 'current' and p in base else (0, 0)
            dt, st_ = se(tl, base[p][1]) if name != 'current' and p in base else (0, 0)
            tll = sum(tl) / len(tl)
            out[name][p] = dict(game_ll=g['ll'], team_ll=tll, d_game=dg, se_game=sg, d_team=dt, se_team=st_,
                                top2=t2, two_slot=sl, n_games=g['n'])
            s2 = f"{sl[0] / sl[1]:.1%}" if sl[1] else '  -  '
            row += (f" | {g['ll']:.4f} ({dg:+.4f}, {sg:.4f})  {tll:.4f} ({dt:+.4f}, {st_:.4f})  "
                    f"{t2[0] / t2[1]:.1%}  {s2}")
        print(row)
    json.dump(out, open(os.path.join(HERE, 'out', 'backtest_tpshare.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
