#!/usr/bin/env python3
"""Possession data for the first-possession CHAIN model (Tim's idea, 11/5/26).

One ESPN summary per final game, cached in data/chain_<season>.json, game id -> record:
  pb   {pid: [OR, DR, TO, PA, PM, trips, tripsScored, FGA]} whole game. OR / DR = credited offensive / defensive
       rebounds; TO = turnovers; PA = putback tries (his team's next shot event after his offensive rebound is his:
       an FGA or a free throw trip); PM = putback tries that scored; trips = FT trips WITHOUT and-ones (a 1-of-1 right
       after his own make is skipped), tripsScored = trips with a make. FGA incl. blocked shots.
  tm   {team: [missedFG, OREB after a missed FG (team rebounds incl.), TO]} whole game
  seq  the game's opening events until its first points (incl. FT), at most 40: [code, team, pid, kind, made]
       code S = FGA (kind rim / j2 / 3), F = FT trip, O = off. rebound, D = def. rebound, T = turnover
Technical / flagrant free throws skipped. Used by backtest_chain.py and build_nba_tab.py (chain report slots).

  python3 analysis/nba/chain_data.py --backfill     # fill the cache for every regular season game
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
sys.path.insert(0, HERE)


def parse(gid):
    import build_nba_tab as bt
    from fb_method import classify
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s or not s['header']['competitions'][0]['status']['type'].get('completed'):
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    rec = {'pb': {}, 'tm': {t: [0, 0, 0] for t in tm.values()}, 'seq': []}
    scored = False
    last_shot = None      # (team, pid, made, kind) of the last shooting event, to spot and-ones and rebounds
    pending_pb = {}       # team -> pid who just got an offensive rebound (next shot event of that team decides PA)
    open_trip = None      # [pid, scored?] for the current FT trip

    def P(pid):
        return rec['pb'].setdefault(pid, [0] * 8)

    def push(ev):
        if not scored and len(rec['seq']) < 40:
            rec['seq'].append(ev)

    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        ty = (p.get('type') or {}).get('text', '')
        tl = ty.lower()
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not t:
            continue
        pid = parts[0] if parts else None
        if p.get('shootingPlay'):
            if not pid:
                continue
            k = classify(p)
            made = bool(p.get('scoringPlay'))
            if k == 'ft':
                if 'technical' in tl or 'flagrant' in tl:
                    continue
                m = re.search(r'(\d) of (\d)', ty)
                first = not m or m.group(1) == '1'
                and1 = bool(m and m.group(2) == '1' and last_shot and last_shot[1] == pid and last_shot[2]
                            and last_shot[3] != 'ft')
                if first:
                    if and1:
                        open_trip = None
                    else:
                        open_trip = [pid, False]
                        P(pid)[5] += 1
                        if pending_pb.get(t):
                            r = pending_pb.pop(t)
                            if r == pid:
                                P(pid)[3] += 1
                                open_trip.append('pb')
                        pending_pb.pop(t, None)
                        push(['F', t, pid, 'ft', False])
                if made and open_trip and open_trip[0] == pid and not open_trip[1]:
                    open_trip[1] = True
                    P(pid)[6] += 1
                    if len(open_trip) > 2:
                        P(pid)[4] += 1
                    if not scored and rec['seq'] and rec['seq'][-1][0] == 'F':
                        rec['seq'][-1][4] = True
                if made:
                    scored = True
                last_shot = (t, pid, made, 'ft')
            else:
                P(pid)[7] += 1
                r = pending_pb.pop(t, None)
                if r == pid:
                    P(pid)[3] += 1
                    P(pid)[4] += made
                if not made:
                    rec['tm'][t][0] += 1
                push(['S', t, pid, k, made])
                if made:
                    scored = True
                last_shot = (t, pid, made, k)
            continue
        if 'rebound' in tl:
            off = 'offensive' in tl
            if off:
                if pid:
                    P(pid)[0] += 1
                    pending_pb[t] = pid
                else:
                    pending_pb.pop(t, None)
                if last_shot and last_shot[0] == t and not last_shot[2] and last_shot[3] != 'ft':
                    rec['tm'][t][1] += 1
                push(['O', t, pid, '', False])
            else:
                if pid:
                    P(pid)[1] += 1
                pending_pb.clear()
                push(['D', t, pid, '', False])
            continue
        if 'turnover' in tl:
            rec['tm'][t][2] += 1
            if pid:
                P(pid)[2] += 1
            pending_pb.clear()
            push(['T', t, pid, '', False])
    return rec


def cache(season, gids, log=lambda m: print(m, file=sys.stderr)):
    import build_nba_tab as bt
    path = os.path.join(DATA, f'chain_{season}.json')
    c = bt.load(path, {})
    todo = [g for g in gids if g not in c]
    if todo:
        def safe(g):
            try:
                return parse(g)
            except Exception as e:
                log(f'  chain {g}: {e!r}')
                return None
        with ThreadPoolExecutor(10) as ex:
            for g, r in zip(todo, ex.map(safe, todo)):
                if r:
                    c[g] = r
        bt.save(path, c)
    log(f'{season}: chain {len(c)} cached ({len(todo)} fetched)')
    return c


if __name__ == '__main__':
    if '--backfill' in sys.argv:
        for s in ('2025-26', '2026-27'):
            g = json.load(open(os.path.join(DATA, f'games_{s}.json')))
            cache(s, [k for k, v in g.items() if v['type'] == 2])
    elif len(sys.argv) > 1:
        print(json.dumps(parse(sys.argv[1]), indent=0)[:3000])
