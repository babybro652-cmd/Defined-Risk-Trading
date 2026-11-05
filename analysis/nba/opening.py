#!/usr/bin/env python3
"""Opening plays and shot-type box per game (11/5/26 backtest of three first basket fixes).

One ESPN summary per final game, cached in data/opening_<season>.json, game id -> record:
  tp   {team: pid of that team's first points, free throws included}
  ev   {team: [[pid, kind, made], ...]} the team's shooting events in order up to and including its first score,
       at most 12; kind rim / j2 / 3 (classify() in fb_method.py) or ft (one entry per free throw trip, made = any make)
  bx   {pid: [rimA, rimM, j2A, j2M, 3A, 3M, ftTrips, ftTripsScored]} for the whole game (from play-by-play)
Technical free throws are skipped. Blocked shots count as the shooter's attempt (participants[0]).

  python3 analysis/nba/opening.py --backfill      # fill the cache for both seasons
Used by: backtest_fb.py --fix (three-fix backtest) and build_nba_tab.py --fp-model.
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
sys.path.insert(0, HERE)
KINDS = ('rim', 'j2', '3')


def parse(gid):
    import build_nba_tab as bt
    from fb_method import classify
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s or not s['header']['competitions'][0]['status']['type'].get('completed'):
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    rec = {'tp': {}, 'ev': {}, 'bx': {}}
    trip = {}   # pid -> index into his team's ev list for the current FT trip (pre-score only)
    open_trip = {}   # pid -> bx trip currently open (to mark scored)
    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not t or not parts or not p.get('shootingPlay'):
            continue
        pid, ty = parts[0], (p.get('type') or {}).get('text', '')
        k = classify(p)
        made = bool(p.get('scoringPlay'))
        b = rec['bx'].setdefault(pid, [0] * 8)
        if k == 'ft':
            if 'technical' in ty.lower() or 'flagrant' in ty.lower():
                continue
            m = re.search(r'(\d) of (\d)', ty)
            first_of_trip = not m or m.group(1) == '1'
            if first_of_trip:
                b[6] += 1; open_trip[pid] = True
            if made and open_trip.get(pid):
                b[7] += 1; open_trip[pid] = False
            if t not in rec['tp']:
                ev = rec['ev'].setdefault(t, [])
                if first_of_trip or pid not in trip:
                    trip[pid] = len(ev); ev.append([pid, 'ft', False])
                if made:
                    ev[trip[pid]][2] = True
        else:
            i = KINDS.index(k)
            b[2 * i] += 1; b[2 * i + 1] += made
            if t not in rec['tp']:
                ev = rec['ev'].setdefault(t, [])
                if len(ev) < 12:
                    ev.append([pid, k, made])
        if made and t not in rec['tp']:
            rec['tp'][t] = pid
    return rec


def cache(season, gids, log=lambda m: print(m, file=sys.stderr)):
    import build_nba_tab as bt
    path = os.path.join(DATA, f'opening_{season}.json')
    c = bt.load(path, {})
    todo = [g for g in gids if g not in c]
    if todo:
        def safe(g):
            try:
                return parse(g)
            except Exception as e:
                log(f'  opening {g}: {e!r}')
                return None
        with ThreadPoolExecutor(10) as ex:
            for g, r in zip(todo, ex.map(safe, todo)):
                if r:
                    c[g] = r
        bt.save(path, c)
    log(f'{season}: opening {len(c)} cached ({len(todo)} fetched)')
    return c


if __name__ == '__main__':
    if '--backfill' in sys.argv:
        for s in ('2025-26', '2026-27'):
            g = json.load(open(os.path.join(DATA, f'games_{s}.json')))
            cache(s, [k for k, v in g.items() if v['type'] == 2])
