#!/usr/bin/env python3
"""Build the UCL tab of Tim's Bet Tracker sheet (goalscorers, shots, team goals, corners, fixtures).

Usage:
  python3 analysis/ucl/build_ucl_tab.py                  # slate = next UCL match day from today (ET)
  python3 analysis/ucl/build_ucl_tab.py --date 2026-10-20

Slate rule: the first date on or after --date with UCL matches, plus the next day when it is the
same matchday (Tue/Wed pairs). Matches already finished on that date are left out of the picks.

Data (all ESPN, free, no key):
  - site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard?dates=YYYYMMDD and /summary?event=<id>
    for 2025-26 and 2026-27 (player goals, shots, shots on target, starts; goal order; team corners;
    commentary for first-half corners)
  - the same for each club's domestic league this season (eng.1, esp.1, ita.1, ger.1, fra.1, por.1,
    ned.1, bel.1, tur.1, aut.1, gre.1, nor.1), only matches with a club that is in this UCL
  Parsed matches are cached in data/matches_<comp>.json, so reruns only fetch new matches.

Output:
  out/sheet_values.json  {"UCL": [[...], ...], "meta": {...}}  ready for the Sheets connector
  out/ucl_tab.csv        same grid as CSV
  out/shortlist.md       the slate's shortlist as text
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
ET = ZoneInfo('America/New_York')
S = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
UA = {'User-Agent': 'Mozilla/5.0'}
UCL = 'uefa.champions'
# competition key -> (league code, first day, last day)
COMPS = {'ucl25': (UCL, dt.date(2025, 9, 1), dt.date(2026, 5, 31)),
         'ucl26': (UCL, dt.date(2026, 9, 1), dt.date(2027, 6, 30))}
DOMESTIC = ['eng.1', 'esp.1', 'ita.1', 'ger.1', 'fra.1', 'por.1', 'ned.1', 'bel.1', 'tur.1', 'aut.1', 'gre.1', 'nor.1']
DOM_START = dt.date(2026, 8, 1)
W_DEFAULT = 3   # one UCL 2026-27 start counts as this many 2025-26 UCL or domestic starts in the blend
MATCH_CORNER_LINES = (8.5, 9.5, 10.5)
TEAM_CORNER_LINES = (4.5, 5.5)


def get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                return None
            time.sleep(1.5 * (i + 1))
        except Exception:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError('failed: ' + url)


def load(p, d):
    try:
        return json.load(open(p))
    except Exception:
        return d


def save(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(o, open(p, 'w'), separators=(',', ':'))


def et(iso):
    return dt.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(ET)


def norm(name):
    s = unicodedata.normalize('NFKD', name or '').encode('ascii', 'ignore').decode().lower()
    return ' '.join(re.sub(r'[^a-z ]', ' ', s).split())


# ---------- schedule ----------
def scoreboard(lg, d):
    j = get(f'{S}/{lg}/scoreboard?dates={d:%Y%m%d}') or {}
    out = []
    for e in j.get('events', []):
        c = e['competitions'][0]
        tm = {t['homeAway']: t['team'] for t in c['competitors']}
        sc = {t['homeAway']: t.get('score') for t in c['competitors']}
        out.append({'id': e['id'], 'utc': e['date'], 'lg': lg, 'stage': e['season'].get('slug', ''),
                    'away': tm['away']['abbreviation'], 'home': tm['home']['abbreviation'],
                    'away_id': tm['away']['id'], 'home_id': tm['home']['id'],
                    'away_name': tm['away'].get('displayName', ''), 'home_name': tm['home'].get('displayName', ''),
                    'as': sc['away'], 'hs': sc['home'], 'final': e['status']['type'].get('completed', False),
                    'state': e['status']['type']['name']})
    return out


def schedule(key, lg, a, b, upto, log):
    path = os.path.join(DATA, f'schedule_{key}.json')
    cache = load(path, {})
    days = [a + dt.timedelta(i) for i in range((min(b, upto) - a).days + 1)]
    recent = dt.datetime.now(ET).date() - dt.timedelta(3)
    today = dt.datetime.now(ET).date()
    stale = lambda d: any(not e.get('final') for e in cache.get(d.isoformat(), [])) and d < today
    todo = [d for d in days if d.isoformat() not in cache or d >= recent or stale(d)]
    with ThreadPoolExecutor(10) as ex:
        for d, evs in zip(todo, ex.map(lambda d: scoreboard(lg, d), todo)):
            cache[d.isoformat()] = evs
    save(path, cache)
    log(f'{key}: schedule {len(days)} days ({len(todo)} fetched)')
    return cache


# ---------- one match ----------
def stat(lst, name):
    for s in lst or []:
        if s.get('name') == name:
            try:
                return float(s.get('value', s.get('displayValue')))
            except (TypeError, ValueError):
                return None
    return None


def parse_match(ev):
    s = get(f"{S}/{ev['lg']}/summary?event={ev['id']}")
    if not s:
        return None
    if not s['header']['competitions'][0]['status']['type'].get('completed'):
        return None
    hc = {c['homeAway']: c for c in s['header']['competitions'][0]['competitors']}
    ids = {hc[k]['team']['id']: hc[k]['team']['abbreviation'] for k in hc}
    names = {}
    for k in hc:
        t = hc[k]['team']
        for n in (t.get('displayName'), t.get('shortDisplayName'), t.get('name')):
            if n:
                names[norm(n)] = t['abbreviation']
    rec = {'id': ev['id'], 'lg': ev['lg'], 'stage': ev['stage'], 'date': et(ev['utc']).date().isoformat(),
           'away': hc['away']['team']['abbreviation'], 'home': hc['home']['team']['abbreviation'],
           'away_id': hc['away']['team']['id'], 'home_id': hc['home']['team']['id'],
           'as': int(hc['away'].get('score') or 0), 'hs': int(hc['home'].get('score') or 0),
           'pl': [], 'nm': {}, 'fg': None, 'goals': [], 'corners': {}, 'c1h': None, 'shots': {}, 'sot': {}}
    player_team = {}
    for r in s.get('rosters', []):
        ab = ids.get(r['team']['id'], r['team'].get('abbreviation'))
        for p in r.get('roster', []):
            pid = p['athlete']['id']; nm = p['athlete']['displayName']
            player_team[norm(nm)] = ab
            rec['nm'][pid] = nm
            st = p.get('stats', [])
            started, sub_in = bool(p.get('starter')), bool(p.get('subbedIn'))
            if not (started or sub_in or (stat(st, 'appearances') or 0) > 0):
                continue
            rec['pl'].append([pid, ab, started, int(stat(st, 'totalGoals') or 0), int(stat(st, 'totalShots') or 0),
                              int(stat(st, 'shotsOnTarget') or 0), (p.get('position') or {}).get('abbreviation', '')])
    for t in s.get('boxscore', {}).get('teams', []):
        ab = ids.get(t['team']['id'], t['team'].get('abbreviation'))
        rec['corners'][ab] = stat(t.get('statistics'), 'wonCorners')
        rec['shots'][ab] = stat(t.get('statistics'), 'totalShots')
        rec['sot'][ab] = stat(t.get('statistics'), 'shotsOnTarget')
    for k in s.get('keyEvents', []):
        if not k.get('scoringPlay') or k.get('shootout'):
            continue
        typ = (k.get('type') or {}).get('text', '').lower()
        tm = ids.get((k.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in k.get('participants', [])]
        og = 'own' in typ
        g = [parts[0] if parts and not og else None, tm, 'OG' if og else ('P' if 'penalty' in typ else '')]
        rec['goals'].append(g)
    rec['fg'] = rec['goals'][0] if rec['goals'] else None
    # first-half corners from commentary
    com = sorted(s.get('commentary', []), key=lambda c: c.get('sequence', 0))
    if com:
        c1 = {rec['away']: 0, rec['home']: 0}; found = False
        for c in com:
            txt = c.get('text', '')
            if txt.lower().startswith('first half ends'):
                found = True; break
            if txt.startswith('Corner,'):
                per = ((c.get('play') or {}).get('period') or {}).get('number', 1)
                if per != 1:
                    continue
                m = re.match(r'Corner, (.*?)\. Conceded by (.*?)\.$', txt)
                ab = None
                if m:
                    ab = names.get(norm(m.group(1)))
                    if not ab and player_team.get(norm(m.group(2))):
                        cb = player_team[norm(m.group(2))]
                        ab = rec['home'] if cb == rec['away'] else rec['away']
                if ab in c1:
                    c1[ab] += 1
        if found:
            rec['c1h'] = c1
    return rec


def safe_parse_match(ev):
    try:
        return parse_match(ev)
    except Exception as e:
        print(f"  {ev['id']} parse error: {e!r}", file=sys.stderr)
        return None


def refresh(key, evs, log):
    path = os.path.join(DATA, f'matches_{key}.json')
    games = load(path, {})
    todo = [e for e in evs if e['final'] and e['id'] not in games]
    log(f'{key}: {len(games)} cached, {len(todo)} to fetch')
    with ThreadPoolExecutor(10) as ex:
        for e, rec in zip(todo, ex.map(safe_parse_match, todo)):
            if rec:
                games[e['id']] = rec
    save(path, games)
    return games


# ---------- aggregates ----------
def zero():
    return {'app': 0, 'st': 0, 'g': 0, 'gwg': 0, 'sh': 0, 'sot': 0, 'sot1': 0, 'sh2': 0, 'fg': 0, 'log': []}


def player_stats(games):
    P = {}
    for g in sorted(games.values(), key=lambda x: (x['date'], x['id'])):
        fgp = g['fg'][0] if g['fg'] else None
        for pid, tm, st, gl, sh, sot, pos in g['pl']:
            s = P.setdefault(pid, zero())
            s['app'] += 1; s['tm'] = tm; s['pos'] = pos or s.get('pos', ''); s['nm'] = g['nm'][pid]; s['last'] = g['date']
            if st:   # rates are per start
                s['st'] += 1; s['g'] += gl; s['gwg'] += gl > 0; s['sh'] += sh; s['sot'] += sot
                s['sot1'] += sot >= 1; s['sh2'] += sh >= 2; s['fg'] += fgp == pid
                s['log'].append((g['date'], gl, sh, sot))
    return P


def team_stats(games):
    T = {}
    for g in games.values():
        for tm, opp, gf, ga in ((g['away'], g['home'], g['as'], g['hs']), (g['home'], g['away'], g['hs'], g['as'])):
            t = T.setdefault(tm, {'gp': 0, 'gf': 0, 'ga': 0, 'btts': 0, 'o25': 0, 'first': 0, 'cg': 0, 'cf': 0, 'ca': 0,
                                  'mo': {k: 0 for k in MATCH_CORNER_LINES}, 'to': {k: 0 for k in TEAM_CORNER_LINES},
                                  'c1g': 0, 'c1': 0, 'c1o45': 0, 'res': []})
            t['gp'] += 1; t['gf'] += gf; t['ga'] += ga; t['btts'] += gf > 0 and ga > 0; t['o25'] += gf + ga > 2.5
            t['first'] += bool(g['fg']) and g['fg'][1] == tm
            t['res'].append((g['date'], 'W' if gf > ga else ('L' if gf < ga else 'D')))
            cf, ca = g['corners'].get(tm), g['corners'].get(opp)
            if cf is not None and ca is not None:
                t['cg'] += 1; t['cf'] += cf; t['ca'] += ca
                for k in MATCH_CORNER_LINES:
                    t['mo'][k] += cf + ca > k
                for k in TEAM_CORNER_LINES:
                    t['to'][k] += cf > k
            if g.get('c1h'):
                tot = sum(g['c1h'].values())
                t['c1g'] += 1; t['c1'] += tot; t['c1o45'] += tot > 4.5
    return T


def pct(x):
    return None if x is None else round(x, 3)


def div(a, b, nd=3):
    return round(a / b, nd) if b else '-'


def build(start, log):
    os.makedirs(DATA, exist_ok=True)
    today = dt.datetime.now(ET).date()
    horizon = max(start, today) + dt.timedelta(120)
    sch = {k: schedule(k, lg, a, b, horizon if k == 'ucl26' else min(b, today), log) for k, (lg, a, b) in COMPS.items()}
    ev26 = [e for es in sch['ucl26'].values() for e in es]
    ucl_ids = {e['away_id'] for e in ev26} | {e['home_id'] for e in ev26}
    g25 = refresh('ucl25', [e for es in sch['ucl25'].values() for e in es], log)
    g26 = refresh('ucl26', ev26, log)
    gdom = {}
    for lg in DOMESTIC:
        sc = schedule(f'dom_{lg}', lg, DOM_START, today, today, log)
        evs = [e for es in sc.values() for e in es if e['away_id'] in ucl_ids or e['home_id'] in ucl_ids]
        gdom.update(refresh(f'dom_{lg}', evs, log))
    # ESPN reuses abbreviations (SLB = Slovan and Benfica, SCP, MON, VAL...). Keep the abbreviation for
    # this season's UCL clubs and tag any other club that shares it with its ESPN id.
    ucl_code = {e['away_id']: e['away'] for e in ev26} | {e['home_id']: e['home'] for e in ev26}
    taken = set(ucl_code.values())

    def remap(games):
        for g in games.values():
            m = {}
            for side in ('away', 'home'):
                tid, ab = g[f'{side}_id'], g[side]
                new = ucl_code.get(tid) or (f'{ab}#{tid}' if ab in taken else ab)
                m[ab] = new; g[side] = new
            g['pl'] = [[p[0], m.get(p[1], p[1])] + p[2:] for p in g['pl']]
            for k in ('corners', 'c1h', 'shots', 'sot'):
                if g.get(k):
                    g[k] = {m.get(a, a): v for a, v in g[k].items()}
            g['goals'] = [[x[0], m.get(x[1], x[1]), x[2]] for x in g['goals']]
            g['fg'] = g['goals'][0] if g['goals'] else None
        return games
    for gs in (g25, g26, gdom):
        remap(gs)
    P25, P26, PD = player_stats(g25), player_stats(g26), player_stats(gdom)
    T25, T26, TD = team_stats(g25), team_stats(g26), team_stats(gdom)
    TA = team_stats({**g26, **gdom})            # this season, all comps we have
    W = W_DEFAULT

    team_name = {}
    for e in ev26:
        team_name[e['away']] = e['away_name']; team_name[e['home']] = e['home_name']
    ucl_abbr = set(team_name)

    # slate: next UCL match day on/after start, plus the next day if it has UCL matches too
    days = sorted(d for d, es in sch['ucl26'].items() if es and d >= start.isoformat()
                  and any(not e['final'] for e in es))
    slate_days = days[:1]
    if days and len(days) > 1 and (dt.date.fromisoformat(days[1]) - dt.date.fromisoformat(days[0])).days == 1:
        slate_days.append(days[1])
    slate_games = [dict(e, time=et(e['utc']).strftime('%a %-m/%-d %-I:%M %p')) for d in slate_days
                   for e in sorted(sch['ucl26'][d], key=lambda e: e['utc']) if not e['final']]
    opp_of = {}
    for g in slate_games:
        opp_of[g['away']] = (g['home'], '@', g); opp_of[g['home']] = (g['away'], 'vs', g)

    # current team = team in the player's latest match (UCL or domestic)
    cur_tm, last_date = {}, {}
    for src in (P25, PD, P26):
        for pid, s in src.items():
            if s.get('last', '') >= last_date.get(pid, ''):
                last_date[pid] = s['last']; cur_tm[pid] = s['tm']
    names = {pid: s['nm'] for src in (P25, PD, P26) for pid, s in src.items()}
    # who started each team's latest match (this season)
    latest = {}
    for g in sorted(list(g26.values()) + list(gdom.values()), key=lambda g: g['date']):
        for tm in (g['away'], g['home']):
            latest[tm] = (g['date'], [p[0] for p in g['pl'] if p[1] == tm and p[2]])

    def Z(src, pid):
        return src.get(pid) or zero()

    def bl(key, pid, den='st'):
        a, b, c = Z(P26, pid), Z(P25, pid), Z(PD, pid)
        d = W * a[den] + b[den] + c[den]
        return (W * a[key] + b[key] + c[key]) / d if d else None

    lg_ga = sum(t['ga'] for tm, t in TA.items() if tm in ucl_abbr) / max(1, sum(t['gp'] for tm, t in TA.items() if tm in ucl_abbr))

    def ga_rate(tm):   # shrunk toward the UCL-club average with 4 pseudo games
        t = TA.get(tm) or {'ga': 0, 'gp': 0}
        return (t['ga'] + 4 * lg_ga) / (t['gp'] + 4)

    PRIOR = {'gwg': 0.15, 'g': 0.17, 'sot1': 0.35}

    def shr(key, pid, k=6):
        # blended rate shrunk toward a typical starter (k pseudo starts) so 1-2 hot games don't top the list
        a, b, c = Z(P26, pid), Z(PD, pid), Z(P25, pid)
        d = W * a['st'] + b['st'] + c['st']
        return (W * a[key] + b[key] + c[key] + PRIOR[key] * k) / (d + k)

    # player universe: anyone on a UCL 26-27 team with 5+ starts across the three samples
    univ = [pid for pid in set(P26) | set(PD) | set(P25)
            if cur_tm.get(pid) in ucl_abbr and Z(P26, pid)['st'] + Z(P25, pid)['st'] + Z(PD, pid)['st'] >= 5
            and Z(P26, pid)['st'] + Z(PD, pid)['st'] >= 1 and Z(P26, pid).get('pos', Z(PD, pid).get('pos', '')) != 'G']
    ranked = sorted(univ, key=lambda p: -(bl('gwg', p) or 0))

    # ---------- picks ----------
    picks = []
    tonight = [p for p in univ if cur_tm[p] in opp_of and p in latest.get(cur_tm[p], ('', []))[1]
               and Z(P26, p)['st'] + Z(PD, p)['st'] + Z(P25, p)['st'] >= 6]

    def gfac(p):
        return max(0.75, min(1.35, ga_rate(opp_of[cur_tm[p]][0]) / lg_ga))

    def game_txt(p):
        o, at, _ = opp_of[cur_tm[p]]
        return f'{cur_tm[p]} {at} {o}'
    for p in sorted(tonight, key=lambda p: -(shr('gwg', p) * gfac(p)))[:5]:
        a, d = Z(P26, p), Z(PD, p)
        o = opp_of[cur_tm[p]][0]
        picks.append(['Anytime goal', names[p], game_txt(p),
                      f"Scored in {round(100 * bl('gwg', p))}% of starts (blend); this season UCL {a['g']} G in {a['st']} starts, "
                      f"league {d['g']} G in {d['st']} starts; {o} concede {TA[o]['ga'] / TA[o]['gp'] if TA.get(o) and TA[o]['gp'] else 0:.1f}/G this season", 'Anytime goal'])
    used = {x[1] for x in picks}

    def tfirst(tm):
        t = TA.get(tm)
        return (t['first'] + 1) / (t['gp'] + 2) if t else 0.5
    for p in sorted([p for p in tonight if names[p] not in used],
                    key=lambda p: -(shr('g', p) * tfirst(cur_tm[p]) * gfac(p)))[:3]:
        picks.append(['First goal', names[p], game_txt(p),
                      f"{bl('g', p):.2f} goals per start (blend); first goal of the match in {Z(P26, p)['fg'] + Z(P25, p)['fg'] + Z(PD, p)['fg']} "
                      f"games; {cur_tm[p]} scored first in {round(100 * tfirst(cur_tm[p]))}% this season", 'First goal (long odds)'])
    sots = sorted([p for p in tonight if (bl('sot1', p) or 0) >= 0.6 and shr('sot1', p) >= 0.55],
                  key=lambda p: -(shr('sot1', p) * gfac(p)))[:4]
    for p in sots:
        picks.append(['1+ shot on target', names[p], game_txt(p),
                      f"1+ SOT in {round(100 * bl('sot1', p))}% of starts; {bl('sh', p):.1f} shots and {bl('sot', p):.1f} SOT per start",
                      'Over 0.5 SOT'])

    def corner_view(g):
        a, h = TA.get(g['away']), TA.get(g['home'])
        if not a or not h or not a['cg'] or not h['cg']:
            return None
        ea = (a['cf'] / a['cg'] + h['ca'] / h['cg']) / 2
        eh = (h['cf'] / h['cg'] + a['ca'] / a['cg']) / 2
        o = {k: (a['mo'][k] / a['cg'] + h['mo'][k] / h['cg']) / 2 for k in MATCH_CORNER_LINES}
        return {'ea': ea, 'eh': eh, 'tot': ea + eh, 'o': o}
    gm = []
    for g in slate_games:
        a, h = TA.get(g['away']), TA.get(g['home'])
        if not a or not h:
            continue
        btts = (a['btts'] / a['gp'] + h['btts'] / h['gp']) / 2
        o25 = (a['o25'] / a['gp'] + h['o25'] / h['gp']) / 2
        gm.append((g, btts, o25, corner_view(g)))
    for g, btts, o25, cv in sorted(gm, key=lambda x: -x[2])[:2]:
        if o25 >= 0.6:
            picks.append(['Over 2.5 goals', f"{g['away']} @ {g['home']}", g['time'],
                          f"Over 2.5 in {round(100 * o25)}% of both teams' games this season (avg); BTTS {round(100 * btts)}%", 'Over 2.5'])
    for g, btts, o25, cv in sorted(gm, key=lambda x: -x[1])[:2]:
        if btts >= 0.6:
            picks.append(['BTTS', f"{g['away']} @ {g['home']}", g['time'],
                          f"Both scored in {round(100 * btts)}% of both teams' games this season (avg)", 'BTTS yes'])
    cvs = [(g, cv) for g, _, _, cv in gm if cv]
    for g, cv in sorted(cvs, key=lambda x: -x[1]['o'][9.5])[:2]:
        picks.append(['Match corners', f"{g['away']} @ {g['home']}", g['time'],
                      f"Expected {cv['tot']:.1f} corners ({g['away']} {cv['ea']:.1f}, {g['home']} {cv['eh']:.1f}); over 9.5 in "
                      f"{round(100 * cv['o'][9.5])}% of their games, over 8.5 in {round(100 * cv['o'][8.5])}%", 'Over 8.5 / 9.5 corners'])
    tc = []
    for g, cv in cvs:
        for tm, opp, e in ((g['away'], g['home'], cv['ea']), (g['home'], g['away'], cv['eh'])):
            t = TA[tm]
            tc.append((e, tm, opp, g, t['to'][4.5] / t['cg']))
    for e, tm, opp, g, r in sorted(tc, key=lambda x: -x[0])[:2]:
        picks.append(['Team corners', tm, f"{g['away']} @ {g['home']}",
                      f"{tm} expected {e:.1f} corners ({TA[tm]['cf'] / TA[tm]['cg']:.1f} won per game, {opp} concede "
                      f"{TA[opp]['ca'] / TA[opp]['cg']:.1f}); {tm} over 4.5 in {round(100 * r)}% of games", f'{tm} over 4.5 corners'])

    # ---------- grid ----------
    rows = []
    R = lambda *a: rows.append(list(a))
    R(f'UCL props: goalscorers, shots, goals, corners (as of {today.strftime("%-m/%-d")})')
    R('Legend', 'UCL 26 = Champions League 2026-27 so far, UCL 25 = 2025-26, Lg 26 = domestic league this season '
      '(since 8/1). Player rates are per START (bench minutes ignored). Blend = all starts pooled, each UCL 26 start '
      'counts as many starts as the weight in B3. Team goals and corners use every 2026-27 match we have '
      f'(UCL + domestic). Sample: {len(g26)} UCL 2026-27 matches, {len(gdom)} domestic matches, {len(g25)} UCL 2025-26 '
      'matches. Own goals do not count for any player. Nothing here is guaranteed. Small stakes.')
    R('UCL 26 start weight', W, 'Input. Change it and the Blend columns update.')
    R()
    hdr_short = len(rows) + 1
    R(f"Next matchday {' and '.join(dt.date.fromisoformat(d).strftime('%a %-m/%-d') for d in slate_days)}: shortlist (not guaranteed)")
    R('Bet', 'Player / match', 'Game', 'Why', 'Look for')
    for p in picks:
        R(*p)
    R('How picked', 'Anytime goal = blended share of starts with a goal (shrunk toward a typical starter so 1-2 hot games do not '
      'top the list) x opponent goals conceded per game vs the UCL-club average (capped at +35%). First goal = goals per start x team scores-first rate x same opponent factor. SOT = 1+ shot on target in '
      '60%+ of starts. Goals and corners angles average the two teams\' 2026-27 rates. Only players who started their '
      'team\'s latest match are picked; check lineups an hour before kickoff (ESPN has no soccer injury feed).')
    R()
    R('Next matchday: games and angles')
    R('Kickoff (ET)', 'Match', 'Away GF/G', 'Away GA/G', 'Home GF/G', 'Home GA/G', 'BTTS% (avg)', 'O2.5% (avg)',
      'Exp corners', 'Match O9.5 corners%', 'Away form', 'Home form')
    for g in slate_games:
        a, h = TA.get(g['away']), TA.get(g['home'])
        cv = corner_view(g)
        frm = lambda t: "'" + ''.join(r for _, r in sorted(t['res'])[-5:]) if t else ''
        R(g['time'], f"{g['away']} @ {g['home']}", div(a['gf'], a['gp'], 2) if a else '-', div(a['ga'], a['gp'], 2) if a else '-',
          div(h['gf'], h['gp'], 2) if h else '-', div(h['ga'], h['gp'], 2) if h else '-',
          pct((a['btts'] / a['gp'] + h['btts'] / h['gp']) / 2) if a and h else '-',
          pct((a['o25'] / a['gp'] + h['o25'] / h['gp']) / 2) if a and h else '-',
          round(cv['tot'], 1) if cv else '-', pct(cv['o'][9.5]) if cv else '-', frm(a), frm(h))
    games_rng = (len(rows) - len(slate_games) + 1, len(rows))
    R()

    def onhdr(title, cols):
        R(title); R(*cols); return len(rows) + 1

    # A: anytime goal and shots
    top = ranked[:60]
    extra = [p for p in tonight if names[p] in {x[1] for x in picks} and p not in top]
    table = sorted(top + extra, key=lambda p: -(bl('gwg', p) or 0))
    s = onhdr('Goalscorers: top 60 by blended goal rate per start (UCL clubs only)',
              ['Player', 'Tm', 'Pos', 'Starts UCL 26', 'Games w/ G UCL 26', 'Starts UCL 25', 'Games w/ G UCL 25',
               'Starts Lg 26', 'Games w/ G Lg 26', 'Blend goal%', 'Goals/start', 'Shots/start', 'SOT/start',
               '1+ SOT%', '2+ shots%', 'First goals (all)', 'Next'])
    for i, p in enumerate(table):
        r = s + i
        a, b, c = Z(P26, p), Z(P25, p), Z(PD, p)
        nx = opp_of.get(cur_tm[p])
        R(names[p], cur_tm[p], a.get('pos') or c.get('pos') or b.get('pos', ''), a['st'], a['gwg'], b['st'], b['gwg'], c['st'], c['gwg'],
          f'=IF($B$3*D{r}+F{r}+H{r}=0,"-",($B$3*E{r}+G{r}+I{r})/($B$3*D{r}+F{r}+H{r}))',
          pct(bl('g', p)), round(bl('sh', p) or 0, 2), round(bl('sot', p) or 0, 2), pct(bl('sot1', p)), pct(bl('sh2', p)),
          a['fg'] + b['fg'] + c['fg'], f'{nx[1]} {nx[0]}' if nx else '')
    a_rng = (s, s + len(table) - 1)
    R()
    # B: teams, goals
    s = onhdr('Teams: goals (2026-27 all comps; UCL 25-26 for reference), sorted by goals conceded',
              ['Team', 'GP 26', 'GF/G 26', 'GA/G 26', 'BTTS% 26', 'O2.5% 26', 'Scores 1st% 26', 'UCL GP 26', 'UCL GF/G 26',
               'UCL GA/G 26', 'UCL GP 25', 'UCL GF/G 25', 'UCL GA/G 25', 'UCL BTTS% 25', 'UCL O2.5% 25', 'Form (last 5)', 'Next'])
    trs = []
    for tm in sorted(ucl_abbr):
        t, u, v = TA.get(tm), T26.get(tm), T25.get(tm)
        nx = opp_of.get(tm)
        trs.append([f'{tm} {team_name[tm]}', t['gp'] if t else 0, div(t['gf'], t['gp'], 2) if t else '-',
                    div(t['ga'], t['gp'], 2) if t else '-', div(t['btts'], t['gp']) if t else '-', div(t['o25'], t['gp']) if t else '-',
                    div(t['first'], t['gp']) if t else '-', u['gp'] if u else 0, div(u['gf'], u['gp'], 2) if u else '-',
                    div(u['ga'], u['gp'], 2) if u else '-', v['gp'] if v else 0, div(v['gf'], v['gp'], 2) if v else '-',
                    div(v['ga'], v['gp'], 2) if v else '-', div(v['btts'], v['gp']) if v else '-', div(v['o25'], v['gp']) if v else '-',
                    "'" + ''.join(r for _, r in sorted(t['res'])[-5:]) if t else '', f'{nx[1]} {nx[0]}' if nx else ''])
    for t in sorted(trs, key=lambda t: -(t[3] if isinstance(t[3], float) else 0)):
        R(*t)
    b_rng = (s, len(rows))
    R()
    # C: corners
    s = onhdr('Corners by team (2026-27 all comps; 1H from ESPN commentary)',
              ['Team', 'Games', 'Won/G', 'Conceded/G', 'Match total/G', 'Match O8.5%', 'Match O9.5%', 'Match O10.5%',
               'Team O4.5%', 'Team O5.5%', '1H total/G', '1H O4.5%', '1H games', 'UCL 25 won/G', 'UCL 25 total/G', 'Next'])
    crs = []
    for tm in sorted(ucl_abbr):
        t, v = TA.get(tm), T25.get(tm)
        nx = opp_of.get(tm)
        if not t or not t['cg']:
            crs.append([f'{tm} {team_name[tm]}', 0] + ['-'] * 13 + [f'{nx[1]} {nx[0]}' if nx else '']); continue
        n = t['cg']
        crs.append([f'{tm} {team_name[tm]}', n, round(t['cf'] / n, 2), round(t['ca'] / n, 2), round((t['cf'] + t['ca']) / n, 2),
                    *[round(t['mo'][k] / n, 3) for k in MATCH_CORNER_LINES], *[round(t['to'][k] / n, 3) for k in TEAM_CORNER_LINES],
                    div(t['c1'], t['c1g'], 2), div(t['c1o45'], t['c1g']), t['c1g'],
                    div(v['cf'], v['cg'], 2) if v and v['cg'] else '-', div(v['cf'] + v['ca'], v['cg'], 2) if v and v['cg'] else '-',
                    f'{nx[1]} {nx[0]}' if nx else ''])
    for t in sorted(crs, key=lambda t: -(t[4] if isinstance(t[4], float) else 0)):
        R(*t)
    c_rng = (s, len(rows))
    R()
    # D: fixtures
    s = onhdr('UCL 2026-27 fixtures (league phase)', ['Date', 'Kickoff (ET)', 'Match', 'Result', 'Corners (A-H)', 'First goal'])
    md = sorted({d for d, es in sch['ucl26'].items() if es})
    for d in md:
        for e in sorted(sch['ucl26'][d], key=lambda e: e['utc']):
            g = g26.get(e['id'])
            fg = ''
            if g and g['fg']:
                fg = 'Own goal' if g['fg'][2] == 'OG' else f"{g['nm'].get(g['fg'][0], '?')} ({g['fg'][1]})"
            corners = f"'{int(g['corners'].get(g['away']) or 0)}-{int(g['corners'].get(g['home']) or 0)}" if g and g['corners'] else ''
            R(dt.date.fromisoformat(d).strftime('%a %-m/%-d/%y'), et(e['utc']).strftime('%-I:%M %p'), f"{e['away']} @ {e['home']}",
              f"'{e['as']}-{e['hs']}" if e['final'] else '', corners, fg)
    d_rng = (s, len(rows))
    R()
    R('Matchdays', '; '.join(dt.date.fromisoformat(d).strftime('%-m/%-d') for d in md))
    R('Sources', f'ESPN soccer scoreboard and match summaries (uefa.champions, plus {", ".join(DOMESTIC)} for UCL clubs). '
      'Domestic data is missing for clubs whose league ESPN does not carry (Shakhtar, Slavia, Slovan, Sabah). '
      f'Pulled {dt.datetime.now(ET).strftime("%-m/%-d %-I:%M %p")} ET. Rebuilt by analysis/ucl/build_ucl_tab.py.')

    width = max(len(r) for r in rows)
    rows = [[('' if v is None else v) for v in r] + [''] * (width - len(r)) for r in rows]
    meta = {'short': hdr_short, 'n_picks': len(picks), 'games': games_rng, 'a': a_rng, 'b': b_rng, 'c': c_rng, 'd': d_rng,
            'width': width, 'rows': len(rows), 'slate': slate_days}
    os.makedirs(OUT, exist_ok=True)
    json.dump({'UCL': rows, 'meta': meta}, open(os.path.join(OUT, 'sheet_values.json'), 'w'))
    with open(os.path.join(OUT, 'ucl_tab.csv'), 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    with open(os.path.join(OUT, 'shortlist.md'), 'w') as f:
        f.write(f"# UCL shortlist {', '.join(slate_days)} (not guaranteed)\n\n")
        for p in picks:
            f.write(f'- **{p[0]}: {p[1]}** ({p[2]}). {p[3]}\n')
        f.write('\n## Matches\n\n')
        for g in slate_games:
            f.write(f"- {g['time']} ET: {g['away_name']} @ {g['home_name']}\n")
    # parlay legs (10/30; analysis/parlays.py): 1+ shot on target only, starters with a 60%+ blended rate
    sys.path.insert(0, os.path.dirname(HERE))
    import parlays as PAR
    PAR.write_legs('ucl', slate_days, 'UCL', [
        {'player': names[p], 'team': cur_tm[p], 'market': '1+ shot on target', 'p': round(bl('sot1', p), 3),
         'game': (f"{cur_tm[p]} @ {opp_of[cur_tm[p]][0]}" if opp_of[cur_tm[p]][1] == '@'
                  else f"{opp_of[cur_tm[p]][0]} @ {cur_tm[p]}"), 'note': f"{bl('sot', p):.1f} SOT per start"}
        for p in tonight if (bl('sot1', p) or 0) >= 0.6 and shr('sot1', p) >= 0.55])
    PAR.write_sections(slate_days[0], targets=('ucl',))
    log(f'wrote {len(rows)} rows x {width} cols; picks {len(picks)}; meta {meta}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--date', help='start looking for the slate on this date, YYYY-MM-DD (default today ET)')
    a = ap.parse_args()
    d = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ET).date()
    build(d, lambda m: print(m, file=sys.stderr))


if __name__ == '__main__':
    main()
