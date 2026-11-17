#!/usr/bin/env python3
"""Build the cleaned first-TD tables from nflverse play-by-play (2024, 2025, 2026).

Raw files (gitignored) live in analysis/nfl/raw/. Download them with --download:
  pbp:      github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_<y>.csv.gz
  rosters:  .../weekly_rosters/roster_weekly_<y>.csv
  snaps:    .../snap_counts/snap_counts_<y>.csv
  schedule: cdn.jsdelivr.net/gh/nflverse/nfldata@master/data/games.csv (spread, total, upcoming games)
  depth:    .../depth_charts/depth_charts_2026.csv (live starters)

Writes analysis/nfl/data/:
  ftd_games.csv         one row per game: lines, opening kickoff receiver, the game's first TD (team, player, type)
  ftd_drives.csv        one row per drive: team, game drive index, team drive number, offensive TD, non-offense TD
  ftd_player_games.csv  one row per player-game (offense): snaps, carries, targets, RZ / inside-5 / opening-script usage,
                        TDs, scored team's first offensive TD, scored the game's first TD

Usage: python3 analysis/nfl/first_td_data.py [--download] [--seasons 2024 2025 2026]
"""
import argparse, csv, gzip, os, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
DATA = os.path.join(HERE, 'data')
REL = 'https://github.com/nflverse/nflverse-data/releases/download'
SKILL = {'RB', 'FB', 'WR', 'TE', 'QB'}


def download(seasons):
    os.makedirs(RAW, exist_ok=True)
    jobs = [(f'{REL}/depth_charts/depth_charts_{max(seasons)}.csv', f'depth_{max(seasons)}.csv'),
            ('https://cdn.jsdelivr.net/gh/nflverse/nfldata@master/data/games.csv', 'games.csv')]
    for y in seasons:
        jobs += [(f'{REL}/pbp/play_by_play_{y}.csv.gz', f'pbp_{y}.csv.gz'),
                 (f'{REL}/weekly_rosters/roster_weekly_{y}.csv', f'roster_{y}.csv'),
                 (f'{REL}/snap_counts/snap_counts_{y}.csv', f'snaps_{y}.csv')]
    for url, fn in jobs:
        print('get', fn, file=sys.stderr)
        subprocess.run(['curl', '-sSL', '-m', '600', '-o', os.path.join(RAW, fn), url], check=True)


def i(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0


def pg(pos):
    return 'RB' if pos in ('RB', 'FB', 'HB') else pos


def load_rosters(seasons):
    """(season, week, gsis) -> position; pfr id -> gsis; gsis -> name."""
    pos, pfr, name, latest = {}, {}, {}, {}
    for y in seasons:
        p = os.path.join(RAW, f'roster_{y}.csv')
        for r in csv.DictReader(open(p)):
            g = r['gsis_id']
            if not g:
                continue
            pos[(y, i(r['week']), g)] = pg(r['position'])
            if r['pfr_id']:
                pfr[r['pfr_id']] = g
            name[g] = r['full_name']
            latest[g] = pg(r['position'])
    return pos, pfr, name, latest


def load_snaps(seasons, pfr):
    out = {}
    for y in seasons:
        for r in csv.DictReader(open(os.path.join(RAW, f'snaps_{y}.csv'))):
            g = pfr.get(r['pfr_player_id'])
            if not g or r['game_type'] != 'REG':
                continue
            out[(r['game_id'], g)] = (i(r['offense_snaps']), float(r['offense_pct'] or 0))
    return out


def td_kind(r):
    """Kind of TD on a scoring play: rush, rec, off_other (offense recovers own fumble), def, st."""
    st = r['special_teams_play'] == '1' or r['play_type'] in ('kickoff', 'punt', 'field_goal', 'extra_point')
    if st:
        return 'st'
    if r['td_team'] and r['posteam'] and r['td_team'] != r['posteam']:
        return 'def'
    if r['rush_touchdown'] == '1':
        return 'rush'
    if r['pass_touchdown'] == '1':
        return 'rec'
    return 'off_other'


def build(seasons):
    pos, pfr, name, latest = load_rosters(seasons)
    snaps = load_snaps(seasons, pfr)
    snaps_g = defaultdict(dict)
    for (sg, p), v in snaps.items():
        snaps_g[sg][p] = v
    games, drives, pgames = [], [], []
    for y in seasons:
        rows = defaultdict(list)
        with gzip.open(os.path.join(RAW, f'pbp_{y}.csv.gz'), 'rt') as f:
            for r in csv.DictReader(f):
                if r['season_type'] != 'REG':
                    continue
                rows[r['game_id']].append(r)
        for gid, plays in rows.items():
            g0 = plays[0]
            wk = i(g0['week'])
            home, away = g0['home_team'], g0['away_team']
            # opening kickoff receiver: posteam of the first kickoff (kickoff posteam = receiving team)
            recv = None
            for r in plays:
                if r['play_type'] == 'kickoff' and r['qtr'] == '1':
                    recv = r['posteam']; break
            if recv is None:
                recv = home if g0['home_opening_kickoff'] == '1' else away
            spread = float(g0['spread_line']) if g0['spread_line'] else None   # + = home favored
            total = float(g0['total_line']) if g0['total_line'] else None
            # drives
            dinfo = {}
            order = []
            for r in plays:
                d = r['fixed_drive']
                if not d or not r['posteam']:
                    continue
                key = i(d)
                if key not in dinfo:
                    dinfo[key] = dict(team=r['posteam'], qtr=i(r['qtr']), off_td=0, non_td=0, non_team='', kind='')
                    order.append(key)
                if r['touchdown'] == '1' and r['td_team']:
                    k = td_kind(r)
                    di = dinfo[key]
                    if di['off_td'] or di['non_td']:
                        continue
                    if k in ('rush', 'rec', 'off_other'):
                        di['off_td'] = 1
                    else:
                        di['non_td'] = 1; di['non_team'] = r['td_team']
                    di['kind'] = k
            tnum = defaultdict(int)
            tdn = {}
            for n, key in enumerate(order, 1):
                di = dinfo[key]
                tnum[di['team']] += 1
                tdn[key] = tnum[di['team']]
                drives.append(dict(game_id=gid, season=y, week=wk, team=di['team'], opp=home if di['team'] == away else away,
                                   game_drive=n, team_drive=tnum[di['team']], qtr=di['qtr'], off_td=di['off_td'],
                                   non_td=di['non_td'], non_td_team=di['non_team'], td_kind=di['kind']))
            # TDs in order
            first = None
            team_first = {}
            for r in plays:
                if r['touchdown'] == '1' and r['td_team']:
                    k = td_kind(r)
                    ev = dict(team=r['td_team'], pid=r['td_player_id'], name=r['td_player_name'], kind=k, qtr=i(r['qtr']),
                              drive=i(r['fixed_drive']))
                    if first is None:
                        first = ev
                    if k in ('rush', 'rec', 'off_other') and r['td_team'] not in team_first:
                        team_first[r['td_team']] = ev
            gd = dict(game_id=gid, season=y, week=wk, home=home, away=away, spread_line=spread, total_line=total,
                      recv=recv, home_score=g0.get('home_score', ''), away_score=g0.get('away_score', ''),
                      first_td_team=first['team'] if first else '', first_td_pid=first['pid'] if first else '',
                      first_td_name=first['name'] if first else '', first_td_kind=first['kind'] if first else 'none',
                      first_td_qtr=first['qtr'] if first else '', first_td_drive=first['drive'] if first else '')
            games.append(gd)
            # player usage
            pu = defaultdict(lambda: defaultdict(int))
            team_of = {}
            for r in plays:
                if r['play_type'] not in ('run', 'pass') or not r['posteam']:
                    continue
                t = r['posteam']
                tn = tdn.get(i(r['fixed_drive']))
                yl = i(r['yardline_100']) if r['yardline_100'] else 99
                for col, kind in (('rusher_player_id', 'car'), ('receiver_player_id', 'tgt')):
                    p = r[col]
                    if not p:
                        continue
                    team_of[p] = t
                    u = pu[p]
                    u[kind] += 1
                    if yl <= 20: u['rz_' + kind] += 1
                    if yl <= 5: u['gl_' + kind] += 1
                    if r['qtr'] == '1': u['q1_' + kind] += 1
                    if tn is not None and tn <= 2: u['open_' + kind] += 1
                if r['touchdown'] == '1' and r['td_team'] == t and r['td_player_id']:
                    pu[r['td_player_id']]['td'] += 1
                    team_of.setdefault(r['td_player_id'], t)
            for p, (sn, spct) in snaps_g.get(gid, {}).items():
                if sn > 0:
                    pp = pos.get((y, wk, p), latest.get(p, ''))
                    if pp in SKILL and p not in pu:
                        pu[p]
            # snap-only players need a team: take from roster
            for p in list(pu):
                if p not in team_of:
                    team_of[p] = None
            for p, u in pu.items():
                t = team_of[p]
                if t is None:
                    t = roster_team(y, wk, p)
                    if t not in (home, away):
                        continue
                sn, spct = snaps.get((gid, p), (0, 0.0))
                pgames.append(dict(game_id=gid, season=y, week=wk, team=t, opp=home if t == away else away, pid=p,
                                   name=name.get(p, p), pos=pos.get((y, wk, p), latest.get(p, '')), snaps=sn, snap_pct=spct,
                                   car=u['car'], tgt=u['tgt'], rz_car=u['rz_car'], rz_tgt=u['rz_tgt'], gl_car=u['gl_car'],
                                   gl_tgt=u['gl_tgt'], q1_car=u['q1_car'], q1_tgt=u['q1_tgt'], open_car=u['open_car'],
                                   open_tgt=u['open_tgt'], td=u['td'],
                                   team_first_td=int(team_first.get(t, {}).get('pid') == p),
                                   game_first_td=int(bool(first) and first['pid'] == p)))
    return games, drives, pgames


_RT = {}


def roster_team(y, wk, p):
    if not _RT:
        for yy in (2024, 2025, 2026):
            fp = os.path.join(RAW, f'roster_{yy}.csv')
            if os.path.exists(fp):
                for r in csv.DictReader(open(fp)):
                    _RT[(yy, i(r['week']), r['gsis_id'])] = r['team']
    return _RT.get((y, wk, p))


def write(fn, rows):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, fn), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print('wrote', fn, len(rows), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--seasons', type=int, nargs='+', default=[2024, 2025, 2026])
    a = ap.parse_args()
    if a.download:
        download(a.seasons)
    games, drives, pgames = build(a.seasons)
    games.sort(key=lambda g: (g['season'], g['week'], g['game_id']))
    write('ftd_games.csv', games)
    write('ftd_drives.csv', drives)
    write('ftd_player_games.csv', pgames)


if __name__ == '__main__':
    main()
