#!/usr/bin/env python3
"""10/30/26: calibrate the NHL anytime goal shrink factor (GOAL_F in build_nhl_tab.py).

Walk-forward on cached games: each night, every skater's blended goal hit% from earlier games only
(2025-26: season to date; 2026-27: W x 26-27 + 25-26, W = 3), the shortlist pick rule (top 4 of the night by
blended hit%, 20+ weighted GP), then actual / predicted. Also prints the logged Bets picks with a "% blend"
(9 of 25 scored vs 11.6 expected through 10/29, from the 10/30 report).

  python3 analysis/nhl/calibrate_goal.py
"""
import json, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
W = 3
LOGGED = (9, 25, 11.6)   # Bets rows with a logged blend %, through 10/29 (report 10/30)


def load(s):
    g = json.load(open(os.path.join(HERE, 'data', f'games_{s}.json')))
    return sorted(g.values(), key=lambda x: (x['date'], x['id']))


def walk(games, prior, start, top=4, min_gp=20):
    cur = defaultdict(lambda: [0, 0])
    res = {'top': [0, 0.0, 0], 'band35': [0, 0.0, 0], 'band45': [0, 0.0, 0]}
    by_d = defaultdict(list)
    for g in games:
        by_d[g['date']].append(g)
    for d in sorted(by_d):
        day = by_d[d]
        if d >= start:
            rows = []
            for g in day:
                for pid, tm, pos, gl, *_ in g['sk']:
                    c, l = cur[pid], (prior or {}).get(pid, [0, 0])
                    n = W * c[0] + l[0] if prior else c[0]
                    if n < min_gp:
                        continue
                    h = (W * c[1] + l[1]) / n if prior else c[1] / c[0]
                    rows.append((h, gl > 0))
            rows.sort(key=lambda x: -x[0])
            for h, y in rows[:top]:
                r = res['top']; r[0] += 1; r[1] += h; r[2] += y
            for h, y in rows:
                for k, lo, hi in (('band35', .35, .45), ('band45', .45, 1)):
                    if lo <= h < hi:
                        r = res[k]; r[0] += 1; r[1] += h; r[2] += y
        for g in day:
            for pid, tm, pos, gl, *_ in g['sk']:
                cur[pid][0] += 1; cur[pid][1] += gl > 0
    return res, {p: v[:] for p, v in cur.items()}


def main():
    g25, g26 = load('20252026'), load('20262027')
    r25, tot25 = walk(g25, None, '2025-11-15')
    r26, _ = walk(g26, tot25, '2026-10-01')
    print(f"{'sample':34} {'n':>5} {'pred':>6} {'actual':>6} {'factor':>6}")
    agg = [0, 0.0, 0]
    for lab, r in (('25-26 top 4 a night (from 11/15)', r25['top']), ('26-27 top 4 a night', r26['top']),
                   ('25-26 all with blend 35-45%', r25['band35']), ('25-26 all with blend 45%+', r25['band45']),
                   ('26-27 all with blend 35-45%', r26['band35']), ('26-27 all with blend 45%+', r26['band45'])):
        print(f"{lab:34} {r[0]:5d} {r[1] / r[0]:6.1%} {r[2] / r[0]:6.1%} {r[2] / r[1]:6.3f}")
    h, n, e = LOGGED
    print(f"{'logged Bets picks (through 10/29)':34} {n:5d} {e / n:6.1%} {h / n:6.1%} {h / e:6.3f}")
    for r in (r25['top'], r26['top']):
        agg = [a + b for a, b in zip(agg, r)]
    agg = [agg[0] + n, agg[1] + e, agg[2] + h]
    print(f"{'pooled: both top-4 samples + logged':34} {agg[0]:5d} {agg[1] / agg[0]:6.1%} {agg[2] / agg[0]:6.1%} {agg[2] / agg[1]:6.3f}")


if __name__ == '__main__':
    main()
