#!/usr/bin/env python3
"""Backtest the first-basket model: v1 (old) vs v2 (accuracy blend, opponent defense by position,
injury ripple / team normalization). Walk-forward: every game from 2025-12-01 on (plus 2026-27 regular
season games) is predicted using only games played before its date. Starters and jumpers are the
actual ones (both models get the same), so this tests the share model, not lineup guessing.

  python3 analysis/nba/backtest_fb.py           # summary table
Metrics: log loss of the actual first-FG scorer, probabilities renormalized over the 10 starters (games where a bench player
scored first are skipped for all models),
Brier over the 10 starters, and the hit rate of each game's top pick.
"""
import json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nba_tab import V2, POS, v1_share, v2_shares  # noqa: E402

START = '2025-12-01'


def run(variants):
    games = []
    for s in ('2025-26', '2026-27'):
        g = json.load(open(os.path.join(HERE, 'data', f'games_{s}.json')))
        games += [x for x in g.values() if x['type'] == 2]
    games.sort(key=lambda x: (x['date'], x['id']))
    P = defaultdict(lambda: defaultdict(float))
    T = defaultdict(lambda: {'allow': defaultdict(float), 'n': 0})
    lg = {'fgm': 0, 'fga': 0, 'pos': defaultdict(float), 'posn': 0, 'tipfirst': 0, 'tipn': 0}
    res = {k: {'ll': 0, 'br': 0, 'hit': 0, 'n': 0} for k in variants}
    by_date = defaultdict(list)
    for g in games:
        by_date[g['date']].append(g)
    for d in sorted(by_date):
        day = by_date[d]
        if d >= START and lg['posn']:
            L = {'fg': lg['fgm'] / lg['fga'], 'pos': {p: lg['pos'][p] / lg['posn'] for p in POS}}
            af = lg['tipfirst'] / lg['tipn']
            for g in day:
                if not g['fb'] or not g['tip']:
                    continue
                st = {tm: [p for p in g['pl'] if p[1] == tm and p[2]] for tm in (g['away'], g['home'])}
                if any(len(v) != 5 for v in st.values()):
                    continue
                rate = {}
                for pid, tm in g['tip']['j']:
                    q = P[pid]; rate[tm] = (q['tipw'] + 3) / (q['tips'] + 6)
                ra, rh = rate.get(g['away'], .5), rate.get(g['home'], .5)
                pt = ra * (1 - rh) / (ra * (1 - rh) + rh * (1 - ra))
                pteam = {g['away']: pt * af + (1 - pt) * (1 - af)}
                pteam[g['home']] = 1 - pteam[g['away']]
                for k, prm in variants.items():
                    probs = {}
                    pt_k = pteam
                    if prm and prm.get('gamma'):
                        tot = {}
                        for tm in st:
                            pl = [dict(P[p[0]], pos=p[6]) for p in st[tm]]
                            tot[tm] = sum(v2_shares(pl, {}, 0, L, dict(prm, def_k=None, norm=0))[0])
                        a, h = g['away'], g['home']
                        lo = math.log(pteam[a] / pteam[h]) + prm['gamma'] * math.log(tot[a] / tot[h])
                        pt_k = {a: 1 / (1 + math.exp(-lo))}; pt_k[h] = 1 - pt_k[a]
                    for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                        pl = [dict(P[p[0]], pos=p[6]) for p in st[tm]]
                        for x in pl:
                            for f in ('gs', 't1', 'sh1', 'fgm', 'fga'):
                                x.setdefault(f, 0)
                        if prm is None:
                            sh = [v1_share(x['t1'], x['gs']) for x in pl]
                        else:
                            sh, _, _ = v2_shares(pl, T[opp]['allow'], T[opp]['n'], L, prm)
                        for p, s_ in zip(st[tm], sh):
                            probs[p[0]] = pt_k[tm] * s_
                    win = g['fb'][0]
                    if win not in probs:   # a bench player scored first (rare); skipped for every model alike
                        continue
                    pw = probs[win] / sum(probs.values())   # proper: renormalized over the 10 starters
                    r = res[k]
                    r['ll'] -= math.log(max(pw, 1e-6)); r['n'] += 1
                    r['br'] += sum((v - (p == win)) ** 2 for p, v in probs.items())
                    r['hit'] += max(probs, key=probs.get) == win
        for g in day:   # update with this day's results
            posof = {p[0]: p[6] for p in g['pl']}
            for pid, tm, stt, mins, pts, tpm, pos, fgm, fga in g['pl']:
                q = P[pid]; q['fgm'] += fgm; q['fga'] += fga; lg['fgm'] += fgm; lg['fga'] += fga
                if stt:
                    q['gs'] += 1; q['t1'] += g['tf'].get(tm) == pid; q['sh1'] += g['ts'].get(tm) == pid
            for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                ps = posof.get(g['tf'].get(opp))
                if ps in POS:
                    T[tm]['allow'][ps] += 1; T[tm]['n'] += 1; lg['pos'][ps] += 1; lg['posn'] += 1
            if g['tip']:
                for pid, tm in g['tip']['j']:
                    P[pid]['tips'] += 1; P[pid]['tipw'] += g['tip']['w'] == tm
                if g['fb']:
                    lg['tipn'] += 1; lg['tipfirst'] += g['tip']['w'] == g['fb'][1]
    return res


def main():
    off = dict(V2, def_k=None)
    variants = {'v1 (old)': None,
                'v1 + ripple (normalize)': dict(off, w_shot=0),
                '+ accuracy': off,
                '+ defense (v2 full)': dict(V2),
                'v2 defense k=30': dict(V2, def_k=30),
                'v2 defense k=60': dict(V2, def_k=60),
                'v2 w_shot=0.25': dict(V2, w_shot=0.25),
                'v2 w_shot=0.75': dict(V2, w_shot=0.75),
                'v2 no ripple': dict(V2, norm=0),
                'v2 ripple up-only': dict(V2, up_only=True),
                'v2 ripple half': dict(V2, norm=0.5),
                'v2 nodef ripple up-only': dict(off, up_only=True),
                'v2 nodef no ripple': dict(off, norm=0),
                'v2 + team acc g=0.5': dict(V2, gamma=0.5),
                'v2 + team acc g=1': dict(V2, gamma=1),
                'v2 + team acc g=2': dict(V2, gamma=2),
                'v2 nodef + team acc g=1': dict(off, gamma=1)}
    res = run(variants)
    print(f"{'model':28} {'games':>5} {'logloss':>8} {'brier':>7} {'top hit':>8}")
    for k, r in res.items():
        print(f"{k:28} {r['n']:5d} {r['ll'] / r['n']:8.4f} {r['br'] / r['n']:7.4f} {r['hit'] / r['n']:8.3f}")


if __name__ == '__main__':
    main()
