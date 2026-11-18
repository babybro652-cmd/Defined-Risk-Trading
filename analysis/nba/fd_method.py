#!/usr/bin/env python3
"""FanDuel "Method of First Basket" categories from ESPN play text (11/18/26, Tim's correction).

FanDuel's market is PLAYER + METHOD only ("Bam Adebayo - Dunk"), five methods:
  Dunk, Free Throw, Layup, Other, Three Point Field Goal.
Mapping from the ESPN play type (first matching rule wins):
  ft    'free throw' in the type
  3     3-point attempt
  dunk  'dunk' in the type (incl. alley-oop dunk, putback/tip dunk)
  layup 'layup' or 'finger roll' in the type (incl. driving, cutting, reverse, alley-oop and putback layups)
  other every other made 2: jump shots, pullups, step-backs, fadeaways, floaters, hooks, bank shots, tip shots
Cache data/fdmethod_<season>.json, per game:
  fp  [team, method, pid] of the game's first points (FT counts, FanDuel settles on first points)
  mk  {pid: [dunk, layup, other, 3, ft_trips]} made baskets by method, ft_trips = trips with 1+ make
      (one per run of consecutive free-throw plays by the same shooter)
Usage: python3 analysis/nba/fd_method.py        # update both caches, print league rates
"""
import json, os, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FD = ('dunk', 'layup', 'other', '3', 'ft')
FD_LAB = {'dunk': 'Dunk', 'layup': 'Layup', 'other': 'Other', '3': 'Three Point Field Goal', 'ft': 'Free Throw'}


def fd_class(p):
    t = (p.get('type') or {}).get('text', '').lower()
    if 'free throw' in t:
        return 'ft'
    if p.get('scoreValue') == 3 or p.get('pointsAttempted') == 3 or 'three point' in p.get('text', '').lower():
        return '3'
    if 'dunk' in t:
        return 'dunk'
    if 'layup' in t or 'finger roll' in t:
        return 'layup'
    return 'other'


def parse(gid):
    import build_nba_tab as bt
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s:
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    rec = {'fp': None, 'mk': {}, 'types': {}}
    last_ft = None
    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        typ = (p.get('type') or {}).get('text', '')
        is_ft = 'free throw' in typ.lower()
        if not is_ft:
            if t and parts:
                last_ft = None
        if not t or not parts or not p.get('scoringPlay') or not p.get('shootingPlay', True):
            continue
        m = fd_class(p); pid = parts[0]
        if rec['fp'] is None:
            rec['fp'] = [t, m, pid]
        e = rec['mk'].setdefault(pid, [0, 0, 0, 0, 0])
        if m == 'ft':
            if last_ft != pid:
                e[4] += 1
            last_ft = pid
        else:
            e[FD.index(m)] += 1
            if m == 'other':
                rec['types'][typ] = rec['types'].get(typ, 0) + 1
    return rec


def load(season, fetch=True):
    path = os.path.join(HERE, 'data', f'fdmethod_{season}.json')
    c = json.load(open(path)) if os.path.exists(path) else {}
    if fetch:
        ids = [g for g, v in json.load(open(os.path.join(HERE, 'data', f'methods_{season}.json'))).items()
               if v and g not in c]
        def safe(g):
            try:
                return parse(g)
            except Exception as e:
                print(f'  {g}: {e!r}', file=sys.stderr)
                return None
        with ThreadPoolExecutor(10) as ex:
            for g, r in zip(ids, ex.map(safe, ids)):
                if r:
                    c[g] = r
        json.dump(c, open(path, 'w'))
    return c


if __name__ == '__main__':
    for season in ('2025-26', '2026-27'):
        c = load(season)
        f = Counter(r['fp'][1] for r in c.values() if r['fp']); n = sum(f.values())
        print(season, n, 'games; first points:', {FD_LAB[k]: f'{f[k] / n:.1%}' for k in FD})
        ty = Counter()
        for r in c.values():
            ty.update(r['types'])
        print('  "Other" made 2s by ESPN type:', ', '.join(f'{k} {v}' for k, v in ty.most_common(12)))
