#!/usr/bin/env python3
"""First 3 field-goal attempts per team (11/2/26 test of the @nbafirstbasket "# of 1st 3 shot attempts" idea).

For every final game: each team's first three FGA in order (shooter pid; free throws excluded, blocked shots count as
the shooter's attempt). Cache: data/first3_<season>.json, game id -> {team: [pid, pid, pid]}.

  python3 analysis/nba/first3.py --backfill     # fill the cache for every game in data/games_<season>.json
Backtest: python3 analysis/nba/backtest_fb.py --first3
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
sys.path.insert(0, HERE)


def parse(gid):
    import build_nba_tab as bt
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s or not s['header']['competitions'][0]['status']['type'].get('completed'):
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    out = {}
    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not t or not parts or not p.get('shootingPlay') or bt.is_ft(p):
            continue
        if len(out.setdefault(t, [])) < 3:
            out[t].append(parts[0])
        if len(out) == 2 and all(len(v) == 3 for v in out.values()):
            break
    return out


def cache(season, gids, log=lambda m: print(m, file=sys.stderr)):
    import build_nba_tab as bt
    path = os.path.join(DATA, f'first3_{season}.json')
    c = bt.load(path, {})
    todo = [g for g in gids if g not in c]
    if todo:
        def safe(g):
            try:
                return parse(g)
            except Exception as e:
                log(f'  first3 {g}: {e!r}')
                return None
        with ThreadPoolExecutor(10) as ex:
            for g, r in zip(todo, ex.map(safe, todo)):
                if r:
                    c[g] = r
        bt.save(path, c)
    log(f'{season}: first3 {len(c)} cached ({len(todo)} fetched)')
    return c


if __name__ == '__main__':
    if '--backfill' in sys.argv:
        for s in ('2025-26', '2026-27'):
            g = json.load(open(os.path.join(DATA, f'games_{s}.json')))
            cache(s, [k for k, v in g.items() if v['type'] == 2])
