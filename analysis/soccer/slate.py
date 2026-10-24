#!/usr/bin/env python3
"""Soccer league slate model (EPL, La Liga, Serie A, Bundesliga, MLS) from free ESPN data.

Reuses the ESPN fetch/parse code in analysis/ucl/build_ucl_tab.py, with its own cache in
analysis/soccer/data. For each unplayed match on --date it prints:
  - expected goals per side (Poisson, attack x defence vs league average, home edge from league)
  - BTTS, over 2.5, match corners vs 8.5/9.5/10.5 (from team corners for/against)
  - top anytime goalscorer and 1+ shot-on-target candidates (per-start rates, shrunk,
    scaled by the game's expected goals) who started their club's latest league match.

Usage: python3 analysis/soccer/slate.py --date 2026-10-24 [--leagues eng.1,esp.1,ita.1,ger.1,usa.1]
"""
import argparse, datetime as dt, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ucl'))
import build_ucl_tab as b  # noqa: E402

b.DATA = os.path.join(HERE, 'data')
START = {'eng.1': dt.date(2026, 8, 1), 'esp.1': dt.date(2026, 8, 1), 'ita.1': dt.date(2026, 8, 1),
         'ger.1': dt.date(2026, 8, 1), 'usa.1': dt.date(2026, 2, 15)}


def pois(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def grid(la, lh, n=10):
    return [[pois(i, la) * pois(j, lh) for j in range(n)] for i in range(n)]


def fair(p):
    if p <= 0 or p >= 1:
        return 'n/a'
    return f'{-round(100 * p / (1 - p))}' if p >= 0.5 else f'+{round(100 * (1 - p) / p)}'


def run(lg, day, log):
    a = START[lg]
    sched = b.schedule(lg, lg, a, day + dt.timedelta(400), day, log)
    evs = [e for d, es in sched.items() for e in es if d < day.isoformat()]
    games = {k: g for k, g in b.refresh(lg, evs, log).items() if g['date'] < day.isoformat()}
    T = b.team_stats(games)
    P = b.player_stats(games)
    n = sum(t['gp'] for t in T.values()) / 2
    hg = sum(g['hs'] for g in games.values()) / max(n, 1)
    ag = sum(g['as'] for g in games.values()) / max(n, 1)
    avg = (hg + ag) / 2
    cg = [g for g in games.values() if all(g['corners'].get(x) is not None for x in (g['home'], g['away']))]
    cavg = sum(g['corners'][g['home']] + g['corners'][g['away']] for g in cg) / max(len(cg), 1) / 2
    last = {}
    for g in sorted(games.values(), key=lambda x: x['date']):
        for tm in (g['home'], g['away']):
            last[tm] = g
    K = 4  # pseudo games of league average
    def att(tm): t = T[tm]; return (t['gf'] + K * avg) / (t['gp'] + K) / avg
    def dfn(tm): t = T[tm]; return (t['ga'] + K * avg) / (t['gp'] + K) / avg
    def cf(tm): t = T[tm]; return (t['cf'] + K * cavg) / (t['cg'] + K) / cavg
    def ca(tm): t = T[tm]; return (t['ca'] + K * cavg) / (t['cg'] + K) / cavg
    out = []
    for e in sched.get(day.isoformat(), []):
        if e['final'] or e['state'] != 'STATUS_SCHEDULED':
            continue
        A, H = e['away'], e['home']
        if A not in T or H not in T:
            log(f'skip {A}@{H}: no data'); continue
        la = ag * att(A) * dfn(H); lh = hg * att(H) * dfn(A)
        G = grid(la, lh)
        btts = sum(G[i][j] for i in range(1, 10) for j in range(1, 10))
        o25 = sum(G[i][j] for i in range(10) for j in range(10) if i + j > 2)
        hw = sum(G[i][j] for i in range(10) for j in range(10) if j > i)
        aw = sum(G[i][j] for i in range(10) for j in range(10) if i > j)
        ec = cavg * cf(A) * ca(H) + cavg * cf(H) * ca(A)
        cp = {k: 1 - sum(pois(x, ec) for x in range(int(k) + 1)) for k in (8.5, 9.5, 10.5)}
        # Poisson understates corner variance; report raw team history as well
        hist = {k: (T[A]['mo'][k] + T[H]['mo'][k]) / max(T[A]['cg'] + T[H]['cg'], 1) for k in (8.5, 9.5, 10.5)}
        players = []
        for tm, lam, tav in ((A, la, avg if lg else 0), (H, lh, avg)):
            team_avg = T[tm]['gf'] / T[tm]['gp']
            starters = {p[0] for p in last[tm]['pl'] if p[1] == tm and p[2]}
            for pid, s in P.items():
                if s.get('tm') != tm or pid not in starters or s['st'] < 3:
                    continue
                gps = (s['g'] + 0.10 * 3) / (s['st'] + 3)          # goals per start, shrunk
                lamp = gps * lam / max(team_avg, 0.3)
                pg = 1 - math.exp(-lamp * 0.92)                     # ~92% of goals from starters' minutes
                sot1 = (s['sot1'] + 0.35 * 3) / (s['st'] + 3)
                sot1 = min(0.95, sot1 * (lam / max(team_avg, 0.3)) ** 0.5)
                players.append({'nm': s['nm'], 'tm': tm, 'pos': s['pos'], 'st': s['st'], 'g': s['g'], 'sh': s['sh'],
                                'sot': s['sot'], 'pg': pg, 'sot1': sot1, 'raw_sot1': s['sot1'] / s['st'],
                                'gwg': s['gwg'] / s['st'], 'sh2': s['sh2'] / s['st']})
        players.sort(key=lambda x: -x['pg'])
        out.append({'lg': lg, 'ko': b.et(e['utc']).strftime('%I:%M %p').lstrip('0'), 'away': e['away_name'],
                    'home': e['home_name'], 'A': A, 'H': H, 'la': la, 'lh': lh, 'btts': btts, 'o25': o25,
                    'hw': hw, 'aw': aw, 'dr': 1 - hw - aw, 'ec': ec, 'cp': cp, 'chist': hist,
                    'form': {tm: ''.join(r for _, r in sorted(T[tm]['res'])[-5:]) for tm in (A, H)},
                    'rec': {tm: (T[tm]['gp'], T[tm]['gf'], T[tm]['ga'], T[tm]['btts'], T[tm]['o25'],
                                 round(T[tm]['cf'] / max(T[tm]['cg'], 1), 1), round(T[tm]['ca'] / max(T[tm]['cg'], 1), 1))
                            for tm in (A, H)},
                    'players': players[:8], 'sotlist': sorted(players, key=lambda x: -x['sot1'])[:5]})
    return out, {'hg': hg, 'ag': ag, 'cavg2': cavg * 2, 'n': n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', default=dt.datetime.now(b.ET).date().isoformat())
    ap.add_argument('--leagues', default='eng.1,esp.1,ita.1,ger.1,usa.1')
    a = ap.parse_args()
    day = dt.date.fromisoformat(a.date)
    log = lambda m: print(m, file=sys.stderr)
    res = {}
    for lg in a.leagues.split(','):
        res[lg] = run(lg, day, log)
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, 'out', f'slate-{day}.json'), 'w'), indent=1, default=str)
    for lg, (games, L) in res.items():
        print(f"\n=== {lg}  league: {L['n']:.0f} games, home {L['hg']:.2f} away {L['ag']:.2f} goals, corners {L['cavg2']:.1f}")
        for g in games:
            print(f"\n{g['ko']} {g['away']} @ {g['home']}  xG {g['la']:.2f}-{g['lh']:.2f}  "
                  f"A/D/H {g['aw']:.0%}/{g['dr']:.0%}/{g['hw']:.0%}  BTTS {g['btts']:.0%} ({fair(g['btts'])})  "
                  f"O2.5 {g['o25']:.0%} ({fair(g['o25'])})")
            for tm in (g['A'], g['H']):
                gp, gf, ga, bt, o, c1, c2 = g['rec'][tm]
                print(f"   {tm}: {gp}gp GF {gf} GA {ga} BTTS {bt}/{gp} O2.5 {o}/{gp} corners {c1} for {c2} ag  form {g['form'][tm]}")
            print(f"   corners exp {g['ec']:.1f}  model o8.5 {g['cp'][8.5]:.0%} o9.5 {g['cp'][9.5]:.0%} o10.5 {g['cp'][10.5]:.0%}"
                  f" | hist o8.5 {g['chist'][8.5]:.0%} o9.5 {g['chist'][9.5]:.0%} o10.5 {g['chist'][10.5]:.0%}")
            for p in g['players'][:6]:
                print(f"   AGS {p['nm']:<24}{p['tm']:<4}{p['pos']:<3} {p['g']}g/{p['st']}st sh {p['sh']} sot {p['sot']}"
                      f"  P(goal) {p['pg']:.0%} ({fair(p['pg'])})  1+SOT {p['sot1']:.0%} (raw {p['raw_sot1']:.0%})")
            for p in g['sotlist'][:3]:
                print(f"   SOT {p['nm']:<24}{p['tm']:<4} 1+SOT {p['sot1']:.0%} ({fair(p['sot1'])}) raw {p['raw_sot1']:.0%} {p['sot']}sot/{p['st']}st")


if __name__ == '__main__':
    main()
