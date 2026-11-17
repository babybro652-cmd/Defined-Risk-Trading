#!/usr/bin/env python3
"""Dunk vs layup split for the first basket METHOD market (11/17/26, Tim's longshots).

FanDuel's "first basket method" market lists 3-pointer, layup, dunk, jump shot (2) and free throw.
fb_method.py groups dunks and layups as 'rim'. This script reads the ESPN play text for every 2026-27
game in data/methods_2026-27.json and stores, per game:
  fp   [team, method, sub] of the game's first points (sub = 'dunk' / 'layup' for rim, else method)
  tp   {team: sub of that team's first points}
  rk   {pid: [dunk makes, layup makes]} all rim makes in the game (for player dunk shares)
Cache: data/rimsplit_<season>.json (2025-26 and 2026-27) (only new games are fetched).

Usage: python3 analysis/nba/rim_split.py           # update the cache and print league / team rates
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_nba_tab as bt
from fb_method import classify



def sub(p, m):
    if m != 'rim':
        return m
    t = ((p.get('type') or {}).get('text', '') + ' ' + p.get('text', '')).lower()
    return 'dunk' if 'dunk' in t else 'layup'


def parse(gid):
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s:
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    rec = {'fp': None, 'tp': {}, 'rk': {}}
    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not t or not parts or not p.get('scoringPlay') or not p.get('shootingPlay', True):
            continue
        m = classify(p); x = sub(p, m)
        if rec['fp'] is None:
            rec['fp'] = [t, m, x, parts[0]]
        rec['tp'].setdefault(t, x)
        if m == 'rim':
            r = rec['rk'].setdefault(parts[0], [0, 0])
            r[0 if x == 'dunk' else 1] += 1
    return rec


def load(season='2026-27'):
    path = os.path.join(HERE, 'data', f'rimsplit_{season}.json')
    c = json.load(open(path)) if os.path.exists(path) else {}
    ids = [g for g, v in json.load(open(os.path.join(HERE, 'data', f'methods_{season}.json'))).items() if v and g not in c]
    with ThreadPoolExecutor(8) as ex:
        for g, r in zip(ids, ex.map(parse, ids)):
            if r:
                c[g] = r
    json.dump(c, open(path, 'w'))
    return c


if __name__ == '__main__':
  for season in ('2025-26', '2026-27'):
    c = load(season)
    print(season)
    from collections import Counter
    f = Counter(r['fp'][2] for r in c.values() if r['fp'])
    n = sum(f.values())
    print(f'{n} games; first points:', {k: f'{v} ({v / n:.0%})' for k, v in f.most_common()})
    rim = f['dunk'] + f['layup']
    print(f'dunk share of rim first points {f["dunk"]}/{rim} = {f["dunk"] / max(rim, 1):.0%}')
