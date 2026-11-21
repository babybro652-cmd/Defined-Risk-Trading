#!/usr/bin/env python3
"""Download and clean FBS drive data for the first scoring play model (ESPN public API, no key).

Source: site.api.espn.com college-football scoreboard (game list, FBS group 80) and summary?event=<id>
(drives, scoring plays, pickcenter closing spread / total). Raw per-game extracts go to
analysis/ncaaf/raw/games/<season>/<id>.json (gitignored).

Writes analysis/ncaaf/data/:
  fs_games.csv   one row per FBS vs FBS game: date, teams, spread (home), total, first drive team,
                 first score (team side, type TD / FG / SAF, offensive or not)
  fs_drives.csv  one row per drive: game, team side, drive index, result class, start yards to goal

Usage: python3 analysis/ncaaf/first_score_data.py [--download] [--seasons 2023 2024 2025 2026]
"""
import argparse, csv, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw', 'games')
DATA = os.path.join(HERE, 'data')
API = 'https://site.api.espn.com/apis/site/v2/sports/football/college-football'
# FBS conference ids on ESPN: ACC, Big 12, Big Ten, Pac-12, CUSA, MAC, MWC, FBS Ind, Sun Belt, American, SEC
FBS_CONF = {'1', '4', '5', '9', '12', '15', '17', '18', '37', '151', '8'}


def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as r:
                return json.load(r)
        except Exception as e:  # noqa
            if k == tries - 1:
                print('fail', url, e, file=sys.stderr)
                return None
            time.sleep(1.5 * (k + 1))


def scoreboard(dates=None, season=None, stype=2, week=None):
    q = f'{API}/scoreboard?groups=80&limit=400'
    if dates:
        q += f'&dates={dates}'
    else:
        q += f'&dates={season}&seasontype={stype}&week={week}'
    return get(q) or {}


def event_rows(sb):
    out = []
    for e in sb.get('events', []):
        c = e['competitions'][0]
        side = {}
        for t in c['competitors']:
            side[t['homeAway']] = t
        if 'home' not in side or 'away' not in side:
            continue
        fbs = all(side[s]['team'].get('conferenceId') in FBS_CONF for s in ('home', 'away'))
        o = (c.get('odds') or [{}])[0]
        out.append({'id': e['id'], 'date': e['date'], 'status': c['status']['type']['name'], 'fbs': fbs,
                    'neutral': c.get('neutralSite', False),
                    'home': side['home']['team']['abbreviation'], 'away': side['away']['team']['abbreviation'],
                    'home_id': side['home']['team']['id'], 'away_id': side['away']['team']['id'],
                    'details': o.get('details'), 'total': o.get('overUnder')})
    return out


def extract(ev):
    d = get(f'{API}/summary?event={ev}')
    if not d:
        return None
    drives = []
    for x in (d.get('drives') or {}).get('previous', []):
        st, en = x.get('start') or {}, x.get('end') or {}
        drives.append({'team': (x.get('team') or {}).get('id'), 'result': x.get('result'),
                       'disp': x.get('displayResult'), 'score': x.get('isScore'),
                       'period': (st.get('period') or {}).get('number'), 'start_yl': st.get('yardLine'),
                       'start_text': st.get('text'), 'end_text': en.get('text'), 'yards': x.get('yards'),
                       'plays': x.get('offensivePlays')})
    sp = [{'type': (s.get('type') or {}).get('text'), 'team': (s.get('team') or {}).get('id'),
           'period': (s.get('period') or {}).get('number'), 'clock': (s.get('clock') or {}).get('displayValue'),
           'text': s.get('text', '')[:160]} for s in d.get('scoringPlays', [])[:4]]
    pc = [{'p': (p.get('provider') or {}).get('name'), 'details': p.get('details'), 'spread': p.get('spread'),
           'total': p.get('overUnder')} for p in d.get('pickcenter', [])]
    return {'drives': drives, 'scoring': sp, 'pickcenter': pc}


def download(seasons):
    for y in seasons:
        os.makedirs(os.path.join(RAW, str(y)), exist_ok=True)
        evs = []
        for stype, weeks in ((2, range(1, 17)), (3, range(1, 2))):
            for w in weeks:
                evs += [dict(r, season=y, week=w if stype == 2 else 20) for r in event_rows(scoreboard(season=y, stype=stype, week=w))]
        evs = [e for e in evs if e['fbs'] and e['status'] == 'STATUS_FINAL']
        seen, todo = set(), []
        for e in evs:
            if e['id'] in seen:
                continue
            seen.add(e['id'])
            p = os.path.join(RAW, str(y), f"{e['id']}.json")
            if not os.path.exists(p):
                todo.append((e, p))
        json.dump(evs, open(os.path.join(RAW, f'{y}_events.json'), 'w'))
        print(y, 'games', len(seen), 'to fetch', len(todo), file=sys.stderr)

        def job(a):
            e, p = a
            try:
                x = extract(e['id'])
            except Exception as err:  # noqa
                print('skip', e['id'], err, file=sys.stderr); return
            if x:
                x['event'] = e
                json.dump(x, open(p, 'w'))
        with ThreadPoolExecutor(12) as ex:
            list(ex.map(job, todo))


CORE = 'https://sports.core.api.espn.com/v2/sports/football/leagues/college-football'


def fetch_lines(seasons):
    """Closing spread / total from the ESPN core odds feed for games whose summary has no pickcenter line."""
    todo = []
    for y in seasons:
        d = os.path.join(RAW, str(y))
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith('_odds.json'):
                continue
            ev = fn[:-5]
            op = os.path.join(d, f'{ev}_odds.json')
            if os.path.exists(op):
                continue
            x = json.load(open(os.path.join(d, fn)))
            if any(p.get('details') for p in x.get('pickcenter', [])):
                continue
            todo.append((ev, op))
    print('lines to fetch', len(todo), file=sys.stderr)

    def job(a):
        ev, op = a
        r = get(f'{CORE}/events/{ev}/competitions/{ev}/odds')
        if r is None:
            return
        items = [i for i in r.get('items', []) if i.get('details') and 'live' not in
                 ((i.get('provider') or {}).get('name') or '').lower()]
        items.sort(key=lambda i: (i.get('provider') or {}).get('priority', 9))
        out = [{'p': (i.get('provider') or {}).get('name'), 'details': i.get('details'), 'total': i.get('overUnder')}
               for i in items]
        json.dump(out, open(op, 'w'))
    with ThreadPoolExecutor(12) as ex:
        list(ex.map(job, todo))


# ------------------------------------------------------------------ cleaning
NONOFF = re.compile(r'(interception|fumble|punt|kickoff|blocked|defensive|return|missed field goal)', re.I)


def score_class(t):
    """ESPN scoring play type -> (TD / FG / SAF, offensive flag). 'Pass Reception' and 'Rush' are TDs."""
    t = (t or '').lower()
    if 'safety' in t:
        return 'SAF', 0
    if 'field goal' in t:
        return 'FG', 1
    if NONOFF.search(t):
        return 'TD', 0
    return 'TD', 1


def drive_class(r):
    r = (r or '').upper()
    if r in ('TD', 'TOUCHDOWN', 'PASSING TOUCHDOWN', 'RUSHING TOUCHDOWN'):
        return 'TD'
    if r in ('FG', 'FIELD GOAL', 'FIELD GOAL GOOD'):
        return 'FG'
    if 'SF' == r or 'SAFETY' in r:
        return 'SAF'
    if 'TD' in r or 'TOUCHDOWN' in r:
        return 'DTD'  # turnover or return touchdown for the defense
    if 'MISSED' in r or 'BLOCKED FG' in r or r == 'FG MISSED':
        return 'MFG'
    if 'HALF' in r or 'GAME' in r:
        return 'END'
    return 'NONE'


def home_spread(details, home, away):
    """Home spread from 'LSU -3.5' style text (negative = home favored)."""
    if not details:
        return None
    if details.upper() in ('EVEN', 'PK', 'PICK'):
        return 0.0
    m = re.match(r'^(\S.*?)\s+([-+]?\d+(?:\.\d+)?)$', details.strip())
    if not m:
        return None
    t, v = m.group(1), float(m.group(2))
    if t == home:
        return v
    if t == away:
        return -v
    return None


def ytg(text, team_abbr):
    """Yards to goal for the offense from ESPN 'LSU 25' text."""
    if not text:
        return None
    m = re.match(r'^(\S+)\s+(\d+)$', text.strip())
    if not m:
        return 50 if text.strip() == '50' else None
    side, yl = m.group(1), int(m.group(2))
    return 100 - yl if side == team_abbr else yl


def build(seasons):
    os.makedirs(DATA, exist_ok=True)
    games, drives = [], []
    for y in seasons:
        d = os.path.join(RAW, str(y))
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith('_odds.json'):
                continue
            x = json.load(open(os.path.join(d, fn)))
            op = os.path.join(d, fn[:-5] + '_odds.json')
            if os.path.exists(op):
                x['pickcenter'] = x.get('pickcenter', []) + json.load(open(op))
            e = x['event']
            side = {e['home_id']: 'H', e['away_id']: 'A'}
            abbr = {e['home_id']: e['home'], e['away_id']: e['away']}
            sp, tot = None, None
            for p in x.get('pickcenter', []):
                sp = home_spread(p.get('details'), e['home'], e['away'])
                tot = p.get('total')
                if sp is not None:
                    break
            if sp is None:
                sp, tot = home_spread(e.get('details'), e['home'], e['away']), e.get('total')
            dv = [r for r in x['drives'] if r.get('team') in side]
            if len(dv) < 6:
                continue
            first = x['scoring'][0] if x['scoring'] else None
            fs_side, fs_type, fs_off = 'N', 'NONE', 0
            if first and first.get('team') in side:
                fs_side = side[first['team']]
                fs_type, fs_off = score_class(first['type'])
            games.append({'season': y, 'week': e['week'], 'date': e['date'][:10], 'id': e['id'], 'home': e['home'],
                          'away': e['away'], 'neutral': int(bool(e.get('neutral'))), 'spread': sp,
                          'total': tot if tot is not None else '', 'recv': side[dv[0]['team']],
                          'fs_side': fs_side, 'fs_type': fs_type, 'fs_off': fs_off,
                          'fs_text': (first or {}).get('type', '')})
            for k, r in enumerate(dv):
                drives.append({'id': e['id'], 'season': y, 'week': e['week'], 'side': side[r['team']], 'k': k,
                               'period': r.get('period'), 'res': drive_class(r.get('result')),
                               'raw': r.get('result'), 'ytg': ytg(r.get('start_text'), abbr[r['team']])})
    games.sort(key=lambda g: (g['date'], g['id']))
    for fn, rows in (('fs_games.csv', games), ('fs_drives.csv', drives)):
        with open(os.path.join(DATA, fn), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print('games', len(games), 'drives', len(drives), file=sys.stderr)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--seasons', nargs='+', type=int, default=[2023, 2024, 2025, 2026])
    a = ap.parse_args()
    if a.download:
        download(a.seasons)
        fetch_lines(a.seasons)
    build(a.seasons)
