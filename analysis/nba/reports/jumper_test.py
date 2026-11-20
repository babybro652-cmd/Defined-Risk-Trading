#!/usr/bin/env python3
"""Jumper choice test (11/19/26 diagnostic). Given the ACTUAL starting five, who jumps the opening tip?

Walk-forward over 2026-27 regular season games, each predicted from earlier 2026-27 games (plus last season's tips):
  current  build_nba_tab.main_jumper: this season's tips for the team newest first (3, 2, 1.5, then 1; regular season
           x2) + 0.05 per tip last season; any player on the team (not limited to the five)
  in-five  the same weights, but only players in the five
  co-start in-five, and games where the candidate's rival big (the other in-five player with tips) also started count
           x4, so "Mara jumps when he starts next to Hartenstein" wins over Hartenstein's solo starts

  python3 analysis/nba/reports/jumper_test.py
"""
import collections, json, os

R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
G = {s: json.load(open(f'{R}/analysis/nba/data/games_{s}.json')) for s in ('2025-26', '2026-27')}


def pl(g):
    return g['pl'] if isinstance(g['pl'], list) else eval(g['pl'])


last = collections.Counter()
for g in G['2025-26'].values():
    for pid, tm in (g.get('tip') or {}).get('j', []):
        last[pid] += 1

games = sorted((g for g in G['2026-27'].values() if g.get('tip') and g['tip'].get('j')), key=lambda g: (g['date'], g['id']))
hist = collections.defaultdict(list)   # team -> [(date, type, jumper pid, set of starters)]
res = collections.Counter()
recent = collections.Counter()
for g in games:
    for pid, tm in g['tip']['j']:
        five = {p[0] for p in pl(g) if p[1] == tm and p[2]}
        H = sorted(hist[tm], key=lambda x: x[0], reverse=True)
        if g['type'] == 2 and len(H) >= 3 and pid in five:
            preds = {}
            for rule in ('current', 'in-five', 'co-start'):
                c = collections.defaultdict(float)
                rivals = {j for _, _, j, _ in H if j in five}
                for i, (d, ty, j, f5) in enumerate(H):
                    if rule != 'current' and j not in five:
                        continue
                    w = ((3, 2, 1.5)[i] if i < 3 else 1) * (2 if ty == 2 else 1)
                    if rule == 'co-start' and len(rivals) > 1 and all(r in f5 for r in rivals):
                        w *= 4
                    c[j] += w
                for p in (five if rule != 'current' else {j for _, _, j, _ in H}):
                    c[p] += 0.05 * last[p]
                preds[rule] = max(c, key=c.get) if c else None
            for rule, p in preds.items():
                res[rule, 'n'] += 1; res[rule, 'hit'] += p == pid
                if g['date'] >= '2026-11-01':
                    recent[rule, 'n'] += 1; recent[rule, 'hit'] += p == pid
        hist[tm].append((g['date'], g['type'], pid, five))

print('Jumper given the actual five, 2026-27 regular season (team-games with 3+ earlier tips):')
for rule in ('current', 'in-five', 'co-start'):
    print(f"  {rule:9} all {res[rule, 'hit']}/{res[rule, 'n']} ({res[rule, 'hit'] / res[rule, 'n']:.1%})   "
          f"11/1 on {recent[rule, 'hit']}/{recent[rule, 'n']} ({recent[rule, 'hit'] / recent[rule, 'n']:.1%})")
