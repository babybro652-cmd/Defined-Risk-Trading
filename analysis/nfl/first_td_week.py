#!/usr/bin/env python3
"""Live first TD picks for one week, from the chain model (first_td_model.py).

Inputs: data/ftd_*.csv (all games so far), raw/games.csv (schedule + spread/total), raw/roster_<season>.csv (latest week),
raw/depth_<season>.csv (fallback depth chart), ESPN injuries feed, live ESPN depth charts and game-day rosters
(availability.py, backup fix 11/28/26). Exclusions: out/first_td_status_wk<N>.csv. Refresh raw first:
  python3 analysis/nfl/first_td_data.py --download --seasons 2024 2025 2026
Outputs: out/first_td_wk<N>.csv, out/first_td_wk<N>.json, out/charts/first_td_wk<N>.png,
  either-player pairs (11/27/26): out/first_td_either_wk<N>.csv, out/charts/first_td_either_wk<N>.png (also 'either' in the json)
"""
import csv, json, math, os, sys
from collections import defaultdict
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import first_td_model as m  # noqa
import availability as av  # noqa

RAW, OUT = m.RAW, m.OUT
BAD = ('Out', 'Injured Reserve', 'Doubtful', 'Suspended', 'Suspension', 'Physically Unable to Perform', 'PUP', 'IR', 'Reserve')


def schedule(season, week):
    out = []
    for r in csv.DictReader(open(os.path.join(RAW, 'games.csv'))):
        if int(r['season']) == season and int(r['week']) == week and r['game_type'] == 'REG':
            out.append(dict(game_id=r['game_id'], home=r['home_team'], away=r['away_team'], spread_line=r['spread_line'],
                            total_line=r['total_line'], day=r['weekday'], date=r['gameday'], time=r['gametime'],
                            home_qb=r['home_qb_id'], away_qb=r['away_qb_id'], season=season, week=week))
    return out


def roster_now(season):
    rows = list(csv.DictReader(open(os.path.join(RAW, f'roster_{season}.csv'))))
    last = max(int(r['week']) for r in rows)
    latest = {}
    for r in rows:
        w = int(r['week'])
        g = r['gsis_id']
        if g and (g not in latest or w >= int(latest[g]['week'])):
            latest[g] = r
    e2g = {r['espn_id']: r['gsis_id'] for r in rows if r['espn_id'] and r['gsis_id']}
    return latest, last, e2g


def depth_now(season):
    rows = list(csv.DictReader(open(os.path.join(RAW, f'depth_{season}.csv'))))
    if not rows:
        return {}, {}
    last = max(r['dt'][:10] for r in rows)
    dep = defaultdict(dict)   # team -> gsis -> (pos_abb, rank)
    e2g = {}
    for r in rows:
        if r['dt'][:10] != last:
            continue
        if r['espn_id'] and r['gsis_id']:
            e2g[r['espn_id']] = r['gsis_id']
        if r['pos_abb'] in ('QB', 'RB', 'WR', 'TE', 'FB'):
            rk = int(r['pos_rank'] or 9)
            old = dep[r['team']].get(r['gsis_id'])
            if not old or rk < old[1]:
                dep[r['team']][r['gsis_id']] = (r['pos_abb'], rk)
    return dep, e2g


def injuries(e2g):
    try:
        import build_tracker as bt
        inj, ts = bt.fetch_injuries()
    except Exception as e:  # noqa
        print('injuries feed failed:', e, file=sys.stderr)
        return {}, ''
    return {e2g[k]: v for k, v in inj.items() if k in e2g}, ts


def espn_events(season, week):
    """{(away, home): (event_id, {abbr: team_id})} from the ESPN scoreboard; {} if it fails."""
    try:
        import build_tracker as bt
        sb = bt.scoreboard(season, week)
    except Exception as e:  # noqa
        print('ESPN scoreboard failed:', e, file=sys.stderr)
        return {}
    out = {}
    for e in sb.get('events', []):
        c = e['competitions'][0]
        side = {x['homeAway']: x['team'] for x in c['competitors']}
        fix = lambda a: {'WSH': 'WAS', 'LAR': 'LA'}.get(a, a)
        out[(fix(side['away']['abbreviation']), fix(side['home']['abbreviation']))] = (
            e['id'], {fix(x['team']['abbreviation']): x['team']['id'] for x in c['competitors']})
    return out


def run(season, week, extra_out=(), extra_q=(), use_depth=True, use_inactives=True):
    G, dg, pgm = m.load_tables()
    preds, st, wd, wp, drows, prows = m.walk(G, dg, pgm, eval_from=(9999, 0))
    wd = m.ridge_logit(np.array([r[1] for r in drows]), np.array([r[2] for r in drows], float), lam=2.0)
    wp = m.clogit_fit([(r[1], r[2]) for r in prows], lam=1.0)
    games = schedule(season, week)
    latest, last_wk, e2g = roster_now(season)
    dep_nv, e2g2 = depth_now(season)
    e2g.update(e2g2)
    g2e = {g: e for e, g in e2g.items()}
    inj, ts = injuries(e2g)
    ev = espn_events(season, week)
    tids = {}
    for _, (eid, tm) in ev.items():
        tids.update(tm)
    # depth chart: live ESPN (backup fix 11/28/26); nflverse daily file as fallback
    dep_live = {}
    if use_depth:
        for t, d in av.fetch_depth({t: tids[t] for g in games for t in (g['home'], g['away']) if t in tids}, season).items():
            dep_live[t] = {e2g[e]: v for e, v in d.items() if e in e2g}
    dep_rank = av.depth_from_nflverse(*_nv_depth_rows(season))
    susp = av.load_suspensions(season, week)
    res, excl, notes = [], [], []
    for g in games:
        out = dict(game=g, teams={}, excluded=[])
        fe, cand = {}, {}
        eid, _ = ev.get((g['away'], g['home']), (None, {}))
        for t, o, qb in ((g['home'], g['away'], g['home_qb']), (g['away'], g['home'], g['away_qb'])):
            fe[t] = st.team_feats(t, o, m.implied(g, t))
            src = 'ESPN live' if t in dep_live else 'nflverse file'
            dmap = dep_live.get(t) or dep_rank.get(t, {})
            depth_loaded = use_depth and bool(dmap)
            groster = av.fetch_game_roster(eid, tids[t]) if (use_inactives and eid and t in tids) else None
            act, status = [], {}
            pool = {gid for gid, r in latest.items() if r['team'] == t} | set(dmap) | set(dep_nv.get(t, {}))
            for gid in pool:
                r = latest.get(gid)
                pos = r['position'] if r else (dmap.get(gid) or dep_nv.get(t, {}).get(gid))[0]
                pos = 'RB' if pos in ('FB', 'HB') else pos
                if pos not in m.SKILL:
                    continue
                name = (r['full_name'] if r else st.pinfo.get(gid, {}).get('name', gid))
                i = inj.get(gid)
                stt = i['status'] if i and i['status'] != 'Active' else ''
                if name in extra_q:
                    stt = 'Questionable'
                if r and r.get('status_description_abbr') == 'R48' and not stt:
                    stt = 'Questionable (IR return window)'
                d = dmap.get(gid)
                hist_ok = st.p[gid]['gp'] >= 1 and st.p[gid]['snap'] / max(st.p[gid]['gp'], 1) >= 0.08 and st.pinfo.get(gid, {}).get('team') == t
                dep_ok = d is not None and d[1] <= (1 if pos == 'QB' else av.TOPN.get(pos, 3))
                if not (hist_ok or dep_ok or name in extra_out):
                    continue
                if pos == 'QB':
                    if (stt and not stt.startswith(av.OK_INJ) and any(b.lower() in stt.lower() for b in av.BAD_INJ)) or name in extra_out:
                        continue
                    if not dep_ok and gid != qb:
                        continue
                    act.append((gid, pos)); status[gid] = (stt, name)
                    continue
                why = av.check(name, t, pos, stt, roster=r, depth=d, depth_loaded=depth_loaded and (t not in dep_live or gid in g2e), game_roster=groster,
                               espn_id=g2e.get(gid), suspensions=susp)
                if name in extra_out:
                    why.append('manual --out')
                if why:
                    if hist_ok or name in extra_out:   # log only players who had a role
                        snap = st.p[gid]['snap'] / max(st.p[gid]['gp'], 1)
                        soft = len(why) == 1 and why[0].startswith(('depth chart', 'not on ', 'roster: reserve'))
                        x = dict(game=f"{g['away']} @ {g['home']}", team=t, player=name, pos=pos, reason='; '.join(why),
                                 depth_source=src if depth_loaded else 'none', game_roster='posted' if groster else 'not posted',
                                 snap=snap, check='yes' if soft and snap >= 0.30 else '')
                        excl.append(x); out['excluded'].append(x)
                    continue
                act.append((gid, pos)); status[gid] = (stt, name)
            starter = qb if qb in status else next((gid for gid, (p, rk) in dmap.items() if p == 'QB' and rk == 1 and gid in status), None)
            # lead RB out: the top active RB on the depth chart inherits most of his role (11/21/26)
            reg = st.regulars(t)
            rbs_reg = [pid for pid, pos in reg.items() if pos == 'RB']
            top_reg = max(rbs_reg, key=lambda pid: st.player_feats(pid, 'RB')['snap'], default=None)
            lead_rb = None
            if top_reg and top_reg not in status:
                ranked = sorted((rk, gid) for gid, (p, rk) in dmap.items() if p == 'RB' and gid in status)
                lead_rb = ranked[0][1] if ranked else None
            drank = {gid: rk for gid, (p, rk) in dmap.items()} if depth_loaded else None
            vlog = []
            rows = m.candidates(st, t, act, starter, lead_rb=lead_rb, depth=drank, log=vlog)
            notes += vlog
            for s in vlog:
                print(s, file=sys.stderr)
            sh, oth = m.clogit_probs(wp, m.pmat(rows)) if rows else ([], 1)
            out['teams'][t] = dict(rows=rows, share=list(sh), other=float(oth), status=status, starter=starter, vacancy=vlog)
        pa = min(0.85, max(0.15, 0.5 + st.recv_tend(g['home']) - st.recv_tend(g['away'])))
        ch = m.chain(wd, fe[g['home']], fe[g['away']], st.lg_non(), pa, st.pace(g['home']) + st.pace(g['away']))
        out.update(p_home=ch[0], p_away=ch[1], p_non=ch[2], p_none=ch[3], p_home_recv=pa)
        players = []
        for t, pt in ((g['home'], ch[0]), (g['away'], ch[1])):
            T = out['teams'][t]
            for r, s in zip(T['rows'], T['share']):
                stt, name = T['status'][r['pid']]
                players.append(dict(name=name, team=t, pos=r['pos'], pid=r['pid'], share=float(s), p=float(pt * s), status=stt))
        players.sort(key=lambda x: -x['p'])
        out['players'] = players
        res.append(out)
    write_status(week, excl, notes, ts)
    write(season, week, res, ts)
    return res


def _nv_depth_rows(season):
    rows = list(csv.DictReader(open(os.path.join(RAW, f'depth_{season}.csv'))))
    return rows, (max(r['dt'][:10] for r in rows) if rows else '')


def write_status(week, excl, notes, ts):
    """Exclusion log (backup fix 11/28/26): every player with a role who was dropped, and why."""
    p = os.path.join(OUT, f'first_td_status_wk{week}.csv')
    with open(p, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Game', 'Team', 'Player', 'Pos', 'Prior snap share', 'Reason', 'Hand check', 'Depth source', 'Game-day roster', 'Built'])
        built = datetime.now().isoformat(timespec='minutes')
        for x in sorted(excl, key=lambda x: (x['game'], x['team'], -x['snap'])):
            w.writerow([x['game'], x['team'], x['player'], x['pos'], f"{x['snap'] * 100:.0f}%", x['reason'], x['check'], x['depth_source'], x['game_roster'], built])
        for n in notes:
            w.writerow(['', n.split(':')[0], '', '', '', 'VACANCY ' + n, '', '', '', built])
    print(f'{len(excl)} players excluded -> {p}', file=sys.stderr)


def short(stt):
    return ' (Q)' if stt.startswith('Quest') else ''


def write(season, week, res, ts):
    os.makedirs(os.path.join(OUT, 'charts'), exist_ok=True)
    lines = []
    with open(os.path.join(OUT, f'first_td_wk{week}.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Game', 'Kickoff', 'Team first TD %', 'Player', 'Team', 'Pos', 'Share of team first TD', 'First TD chance', 'Fair', 'Take at', 'Status'])
        for o in res:
            g = o['game']
            gm = f"{g['away']} @ {g['home']}"
            for x in o['players'][:12]:
                tp = o['p_home'] if x['team'] == g['home'] else o['p_away']
                w.writerow([gm, f"{g['day']} {g['date']} {g['time']}", f'{tp * 100:.1f}%', x['name'], x['team'], x['pos'],
                            f"{x['share'] * 100:.1f}%", f"{x['p'] * 100:.1f}%", m.american(x['p']), m.take_at(x['p']), x['status']])
    slim = [dict(game=f"{o['game']['away']} @ {o['game']['home']}", kickoff=f"{o['game']['day']} {o['game']['date']} {o['game']['time']}",
                 spread_line=o['game']['spread_line'], total_line=o['game']['total_line'],
                 p_home=o['p_home'], p_away=o['p_away'], p_non=o['p_non'], p_none=o['p_none'], p_home_recv=o['p_home_recv'],
                 top=[{k: x[k] for k in ('name', 'team', 'pos', 'share', 'p', 'status')} for x in o['players'][:6]],
                 team_top={t: sorted([dict(name=o['teams'][t]['status'][r['pid']][1], share=float(s)) for r, s in
                                      zip(o['teams'][t]['rows'], o['teams'][t]['share'])], key=lambda x: -x['share'])[:3]
                           for t in o['teams']}, excluded=[{k: x[k] for k in ('team', 'player', 'pos', 'reason')} for x in o.get('excluded', [])],
                 vacancy=[v for t in o['teams'] for v in o['teams'][t].get('vacancy', [])]) for o in res]
    for o, sl in zip(res, slim):
        sl['either'] = either_summary(o)
    write_either(week, res)
    json.dump(dict(season=season, week=week, injuries_feed=ts, built=datetime.now().isoformat(timespec='minutes'), games=slim),
              open(os.path.join(OUT, f'first_td_wk{week}.json'), 'w'), indent=1)
    chart(week, res, ts)
    for o in res:
        g = o['game']
        print(f"{g['away']} @ {g['home']}  {g['day']} {g['time']}  home {o['p_home'] * 100:.0f}% away {o['p_away'] * 100:.0f}% non {o['p_non'] * 100:.1f}% none {o['p_none'] * 100:.1f}%")
        for x in o['players'][:5]:
            print(f"   {x['name']:24s} {x['team']:3s} {x['pos']:2s} {x['p'] * 100:5.1f}%  fair {m.american(x['p']):>6s}  take {m.take_at(x['p']):>6s} {x['status']}")


def pair_dict(q):
    return dict(pair=f"{q['a']['name']}{short(q['a']['status'])} or {q['b']['name']}{short(q['b']['status'])}",
                teams=f"{q['a']['team']}/{q['b']['team']}" if not q['same'] else q['a']['team'],
                p=float(q['p']), fair=m.american(q['p']), take_at=m.take_at(q['p']),
                status='Q' if 'Quest' in q['a']['status'] + q['b']['status'] else '')


def either_summary(o):
    pairs, same = m.either_pairs(o['players'])
    g = o['game']
    fav = g['home'] if o['p_home'] >= o['p_away'] else g['away']
    return dict(top_pairs=[pair_dict(q) for q in pairs[:3]],
                same_team={t: pair_dict(same[t]) for t in sorted(same, key=lambda t: t != fav)})


def write_either(week, res):
    with open(os.path.join(OUT, f'first_td_either_wk{week}.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Game', 'Kickoff', 'Slot', 'Pair', 'Teams', 'Combined chance', 'Fair', 'Take at', 'Status'])
        for o in res:
            g = o['game']
            e = either_summary(o)
            gm, ko = f"{g['away']} @ {g['home']}", f"{g['day']} {g['date']} {g['time']}"
            for i, q in enumerate(e['top_pairs']):
                w.writerow([gm, ko, 'Top-2 combo' if i == 0 else f'Pair #{i + 1}', q['pair'], q['teams'], f"{q['p'] * 100:.1f}%", q['fair'], q['take_at'], q['status']])
            for t, q in e['same_team'].items():
                w.writerow([gm, ko, f'Same team {t}', q['pair'], q['teams'], f"{q['p'] * 100:.1f}%", q['fair'], q['take_at'], q['status']])
    chart_either(week, res)


def chart_either(week, res):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['text.parse_math'] = False
    order = {'Wednesday': -1, 'Thursday': 0, 'Friday': 1, 'Saturday': 2, 'Sunday': 3, 'Monday': 4}
    today = datetime.now().strftime('%Y-%m-%d')
    res = [o for o in res if o['game']['date'] >= today] or res
    res = sorted(res, key=lambda o: (order.get(o['game']['day'], 5), o['game']['time'], o['game']['game_id']))
    rows = []
    for o in res:
        g = o['game']
        hr = '%s %s' % (g['day'][:3], datetime.strptime(g['time'], '%H:%M').strftime('%-I:%M %p'))
        e = either_summary(o)
        ab = lambda nm: ' '.join([nm.split(' ')[0][0] + '.'] + nm.split(' ')[1:]) if ' ' in nm else nm
        cell = lambda q, lab='': (f"{lab}{' or '.join(ab(x) for x in q['pair'].split(' or '))}\n"
                                  f"{q['p'] * 100:.1f}%   fair {q['fair']}   take {q['take_at']}")
        c = [f"{g['away']} @ {g['home']}\n{hr}"] + [cell(q) for q in e['top_pairs']]
        c += [cell(q, f'{t}: ') for t, q in list(e['same_team'].items())[:2]]
        while len(c) < 6:
            c.append('')
        rows.append(c)
    fig, ax = plt.subplots(figsize=(24, 0.75 * len(rows) + 1.6))
    ax.axis('off')
    ax.set_title(f"NFL Either Player - First Touchdown Scorer, Week {week} (our chain model)\n"
                 "Chance either player scores the game's first TD = pA + pB. Fair price / take-at (fair decimal x1.2). (Q) = questionable",
                 fontsize=15, fontweight='bold', pad=12)
    tb = ax.table(cellText=rows, colLabels=['Game', 'Top-2 combo', 'Pair #2', 'Pair #3', 'Best same-team (fav)', 'Best same-team (other)'],
                  colWidths=[0.08, 0.184, 0.184, 0.184, 0.184, 0.184], loc='upper center', cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(10)
    hgt = 0.86 / max(len(rows), 1)
    for (r, c), cl in tb.get_celld().items():
        cl.set_height(hgt if r > 0 else 0.03)
        if r == 0:
            cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
        elif c == 1:
            cl.set_facecolor('#dff3e3')
        elif r % 2 == 0:
            cl.set_facecolor('#eef2f7')
    plt.figtext(0.5, 0.02, "Back-test (2025 + 2026, walk-forward): top-2 combo hit about 27% (fair about +270); best same-team pair of the favored team about 24%.\n"
                "Straights only at take-at or longer, $0.20 to $0.50. Parlays of these legs are tracking only. First TD is mostly noise.",
                ha='center', fontsize=10)
    p = os.path.join(OUT, 'charts', f'first_td_either_wk{week}.png')
    plt.savefig(p, dpi=110, bbox_inches='tight')
    plt.close(fig)
    print(p)


def chart(week, res, ts):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['text.parse_math'] = False
    order = {'Thursday': 0, 'Friday': 1, 'Saturday': 2, 'Sunday': 3, 'Monday': 4}
    # drop games already played (date before today), so Saturday / Sunday reruns show only the games left
    today = datetime.now().strftime('%Y-%m-%d')
    res = [o for o in res if o['game']['date'] >= today] or res
    res = sorted(res, key=lambda o: (order.get(o['game']['day'], 5), o['game']['time'], o['game']['game_id']))
    rows, fav_col = [], []
    for o in res:
        g = o['game']
        h, a = g['home'], g['away']
        hr = '%s %s' % (g['day'][:3], datetime.strptime(g['time'], '%H:%M').strftime('%-I:%M %p'))
        fav = h if o['p_home'] >= o['p_away'] else a
        fp = max(o['p_home'], o['p_away'])
        sp = float(g['spread_line'])
        line = f"{h if sp >= 0 else a} -{abs(sp):g}, O/U {float(g['total_line']):g}"
        cells = [f"{a} @ {h}\n{hr}\n{line}",
                 f"{fav} {fp * 100:.0f}%\n{a if fav == h else h} {min(o['p_home'], o['p_away']) * 100:.0f}%\nNo off. TD {(o['p_non'] + o['p_none']) * 100:.0f}%"]
        for x in o['players'][:3]:
            cells.append(f"{x['name']}{short(x['status'])} ({x['team']} {x['pos']})\n{x['p'] * 100:.1f}%   fair {m.american(x['p'])}\ntake {m.take_at(x['p'])}")
        rows.append(cells)
    fig, ax = plt.subplots(figsize=(17, 1.0 * len(rows) + 1.6))
    ax.axis('off')
    ax.set_title(f"NFL First TD, Week {week} (our chain model)\nTop 3 per game: chance to score the game's first TD, fair price / take-at (fair decimal x1.2). "
                 f"(Q) = questionable; Out / IR / suspended / inactive / off the depth-chart top N removed", fontsize=15, fontweight='bold', pad=12)
    tb = ax.table(cellText=rows, colLabels=['Game', 'Team first TD', '#1', '#2', '#3'], colWidths=[0.13, 0.12, 0.25, 0.25, 0.25],
                  loc='upper center', cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(10.5)
    hgt = 0.86 / max(len(rows), 1)
    for (r, c), cl in tb.get_celld().items():
        cl.set_height(hgt if r > 0 else 0.03)
        if r == 0:
            cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
        elif r % 2 == 0:
            cl.set_facecolor('#eef2f7')
        if r > 0 and c >= 2:
            o = res[r - 1]
            fav = o['game']['home'] if o['p_home'] >= o['p_away'] else o['game']['away']
            if c - 2 < len(o['players']) and o['players'][c - 2]['team'] == fav:
                cl.set_facecolor('#dff3e3')
    plt.figtext(0.5, 0.02, "Green = player on the team favored to score first. Team % = chance that team's offense scores the game's first TD "
                "(kickoff 50/50 + receive habit, opening-drive and per-drive TD rates, implied totals).\n'No off. TD' = defense / "
                "special teams TD first or no TD: every player bet loses.\nFirst TD is mostly noise: small stakes, bet only at take-at or longer. "
                f"Injuries from ESPN feed {ts[:16]}. Rerun after inactives (about 90 min before kickoff; Sunday 11:30 AM ET for 1 PM games).", ha='center', fontsize=10)
    p = os.path.join(OUT, 'charts', f'first_td_wk{week}.png')
    plt.savefig(p, dpi=110, bbox_inches='tight')
    plt.close(fig)
    print(p)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--week', type=int, default=11)
    ap.add_argument('--season', type=int, default=2026)
    ap.add_argument('--out', nargs='*', default=[], help='extra player names to treat as Out')
    ap.add_argument('--q', nargs='*', default=[], help='extra player names to mark Questionable')
    ap.add_argument('--no-depth', action='store_true', help='skip the depth-chart top-N rule (if ESPN depth charts look wrong)')
    ap.add_argument('--no-inactives', action='store_true', help='skip the ESPN game-day roster check')
    a = ap.parse_args()
    run(a.season, a.week, set(a.out), set(a.q), use_depth=not a.no_depth, use_inactives=not a.no_inactives)
