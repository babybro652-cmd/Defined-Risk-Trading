#!/usr/bin/env python3
"""NFL Scorer Tracker builder.

Pulls ESPN box scores + play-by-play for 2025 (full season) and 2026 through
--week, then builds every tab of the "NFL Scorer Tracker 2026" Google Sheet as
plain values (out/tracker.json), CSV copies (out/*.csv) and the 2026-only
ranking tables (out/rank_2026.md).

Usage:
    python3 analysis/nfl/build_tracker.py --week 5            # full refresh
    python3 analysis/nfl/build_tracker.py --week 5 --injuries-only

Parsed games are cached in data/games_<season>.json (small, committed), so a
weekly rerun only downloads the new 2026 games. Raw ESPN JSON is not kept.
"""
import argparse, csv, json, os, re, statistics as S, sys, time, urllib.request
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
SITE = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'
WEB = 'https://site.web.api.espn.com/apis/common/v3/sports/football/nfl'
SKILL = ('RB', 'WR', 'TE', 'QB', 'FB')
MAXWK = 18
PENDING = []  # 2026 games inside --week that are not final yet

# Players named in the Week 4 consistency report (kept even without a 2026 TD).
REPORT_PLAYERS = [
    'Christian McCaffrey', 'Jahmyr Gibbs', 'Javonte Williams', 'Derrick Henry', 'Kyren Williams',
    'Jonathan Taylor', 'Omarion Hampton', 'Josh Allen', 'George Kittle', 'James Cook III', 'Puka Nacua',
    'Bijan Robinson', 'Jaxon Smith-Njigba', 'Trey McBride', 'Davante Adams', 'CeeDee Lamb', 'Chris Olave',
    'Amon-Ra St. Brown', "Ja'Marr Chase", 'Zay Flowers', 'Brock Bowers', "Wan'Dale Robinson",
    'George Pickens', 'Drake London', 'Tyler Warren', 'Sam LaPorta', 'Stefon Diggs', 'Garrett Wilson',
    'Christian Watson', 'Tee Higgins', 'Kenneth Walker III', 'Nico Collins', "D'Andre Swift",
    'Justin Jefferson', 'DeVonta Smith', 'Dallas Goedert', 'Keenan Allen', 'Rashee Rice',
]


# ---------------------------------------------------------------- fetching
def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, separators=(',', ':'))


def scoreboard(season, week):
    return get(f'{SITE}/scoreboard?week={week}&seasontype=2&dates={season}')


# ---------------------------------------------------------------- parsing
PASS = re.compile(r"pass(?: incomplete)?(?: (?:short|deep))?(?: (?:left|middle|right))? (?:to|intended for) ([A-Z][a-z]{0,2}\.\s?[A-Z][\w'\.\- ]*?)(?=[\s\.,]+(?:to |for |at |\(|is |pushed|ran|$|\[|INTERCEPTED|TOUCHDOWN|\.)|\.?$)")
RUSH = re.compile(r"^(?:\([^)]*\)\s*)*(?:[A-Z][\w\.\-' ]*? reported in as eligible\.\s+)*([A-Z][a-z]{0,2}\.\s?[A-Z][\w'\.\-]*(?: [A-Z][\w'\-]+)?) (?:up the middle|left end|left tackle|left guard|right end|right tackle|right guard|rushes|scrambles|to [A-Z]{2,3} \d|for )")
SKIP_TYPES = {'Penalty', 'Kickoff', 'Punt', 'Timeout', 'End Period', 'Field Goal Good', 'Field Goal Missed',
              'Extra Point Good', 'Two-point Conversion', 'Official Timeout', 'End of Half', 'End of Game'}
SUFFIX = re.compile(r' (Jr\.|Sr\.|II|III|IV|V)$')


def lastkey(abbr):
    return abbr.split('.', 1)[1].strip().lower().replace(' ', '') if '.' in abbr else abbr.lower()


def parse_game(d, season, week):
    """Return compact parsed game: player rows + drive red-zone info."""
    comp = d['header']['competitions'][0]
    ids = {c['team']['id']: c['team']['abbreviation'] for c in comp['competitors']}
    abbrs = list(ids.values())
    pg, namemap, first = {}, {}, {}
    for t in d['boxscore'].get('players', []):
        ta = t['team']['abbreviation']
        opp = [a for a in abbrs if a != ta][0]
        for s in t['statistics']:
            for a in s['athletes']:
                aid = a['athlete']['id']; nm = a['athlete']['displayName']
                r = pg.setdefault(aid, dict(id=aid, name=nm, team=ta, opp=opp, rec=0, tgt=0, recyd=0, rectd=0, car=0,
                                            rushyd=0, rushtd=0, rz=0, rzt=0, rzc=0, i10=0))
                st = dict(zip(s['keys'], a['stats']))

                def f(k):
                    v = st.get(k)
                    try:
                        return int(float(v)) if v not in (None, '', '--') else 0
                    except ValueError:
                        return 0
                if s['name'] == 'receiving':
                    r.update(rec=f('receptions'), recyd=f('receivingYards'), rectd=f('receivingTouchdowns'), tgt=f('receivingTargets'))
                elif s['name'] == 'rushing':
                    r.update(car=f('rushingAttempts'), rushyd=f('rushingYards'), rushtd=f('rushingTouchdowns'))
                nm2 = SUFFIX.sub('', nm)
                last = nm2.split(' ', 1)[1].lower().replace(' ', '') if ' ' in nm2 else nm2.lower()
                lst = namemap.setdefault((ta, last), [])
                if aid not in lst:
                    lst.append(aid)
                first[aid] = nm2.split(' ')[0].replace('.', '')
    drives, unresolved = [], 0
    for dr in d.get('drives', {}).get('previous', []):
        ta = dr.get('team', {}).get('abbreviation')
        in_rz = False
        for p in dr.get('plays', []):
            tx = p.get('text', ''); ty = p.get('type', {}).get('text', '')
            if ty in SKIP_TYPES or 'No Play' in tx or 'NULLIFIED' in tx or 'TWO-POINT' in tx:
                continue
            pteam = ids.get(str(p.get('start', {}).get('team', {}).get('id')), ta)
            ytg = p.get('start', {}).get('yardsToEndzone')
            if ytg is None or ytg <= 0 or ytg > 20:
                continue
            if pteam == ta:
                in_rz = True
            if 'kneels' in tx:
                continue
            m = PASS.search(tx); kind = 't'
            if not m:
                m = RUSH.search(tx); kind = 'c'
                if not m or ' pass ' in tx or 'sacked' in tx:
                    continue
            nm = m.group(1).strip().rstrip('.')
            lk = lastkey(nm)
            cand = namemap.get((pteam, lk)) or namemap.get((pteam, lk.split('-')[0]))
            if not cand:
                continue
            if len(cand) == 1:
                aid = cand[0]
            else:  # e.g. "Bi.Robinson" vs "Br.Robinson": match the initials prefix to the first name
                pre = nm.split('.')[0].lower()
                c2 = [c for c in cand if first[c].lower().startswith(pre)]
                if len(c2) != 1:
                    unresolved += 1
                    continue
                aid = c2[0]
            r = pg[aid]
            r['rz'] += 1
            r['rzt' if kind == 't' else 'rzc'] += 1
            if ytg <= 10:
                r['i10'] += 1
        res = (dr.get('result') or '').upper()
        drives.append([ta, int(in_rz), int(res == 'TD')])
    rows = [r for r in pg.values() if r['rec'] or r['tgt'] or r['car'] or r['rectd'] or r['rushtd']]
    for r in rows:
        r.pop('rzt'); r.pop('rzc')
    home = [c['team']['abbreviation'] for c in comp['competitors'] if c.get('homeAway') == 'home']
    return dict(season=season, week=week, teams=abbrs, home=home[0] if home else '', rows=rows,
                drives=drives, unresolved=unresolved)


def refresh_games(season, last_week, log):
    path = os.path.join(DATA, f'games_{season}.json')
    games = load(path, {})
    todo = []
    for wk in range(1, last_week + 1):
        sb = scoreboard(season, wk)
        for e in sb.get('events', []):
            done = e['competitions'][0]['status']['type'].get('completed')
            if not done:
                PENDING.append(f'{e["shortName"]} (Wk{wk})')
                log(f'  {season} wk{wk} {e["shortName"]}: not final yet, skipped')
                continue
            if e['id'] not in games:
                todo.append((e['id'], wk))
    log(f'{season}: {len(games)} cached, {len(todo)} to download')

    def work(item):
        gid, wk = item
        return gid, parse_game(get(f'{SITE}/summary?event={gid}'), season, wk)
    with ThreadPoolExecutor(8) as ex:
        for gid, g in ex.map(work, todo):
            games[gid] = g
    save(path, games)
    return games


def refresh_positions(ids, log):
    path = os.path.join(DATA, 'pos.json')
    pos = load(path, {})
    missing = [i for i in ids if i not in pos]
    if missing:
        log(f'positions: {len(missing)} to look up')

        def work(aid):
            try:
                return aid, get(f'{WEB}/athletes/{aid}')['athlete']['position']['abbreviation']
            except Exception:
                return aid, '?'
        with ThreadPoolExecutor(12) as ex:
            for aid, p in ex.map(work, missing):
                pos[aid] = p
        save(path, pos)
    return pos


def fetch_injuries():
    d = get(f'{SITE}/injuries')
    out = {}
    for t in d.get('injuries', []):
        for i in t.get('injuries', []):
            a = i.get('athlete', {})
            aid = None
            for l in a.get('links', []):
                m = re.search(r'/id/(\d+)', l.get('href', ''))
                if m:
                    aid = m.group(1); break
            if not aid:
                continue
            det = i.get('details', {})
            inj = ' '.join(x for x in [det.get('side') if det.get('side') not in (None, 'Not Specified') else '',
                                         det.get('type', ''),
                                         det.get('detail') if det.get('detail') not in (None, 'Not Specified') else '']
                           if x).strip()
            prev = out.get(aid)
            if prev and prev['date'] >= i.get('date', ''):
                continue
            out[aid] = dict(status=i.get('status', ''), injury=inj or 'n/a', date=i.get('date', ''),
                            note=i.get('shortComment', ''), ret=det.get('returnDate', ''),
                            fantasy=det.get('fantasyStatus', {}).get('description', ''))
    return out, d.get('timestamp', '')


# ---------------------------------------------------------------- helpers
def rank_desc(vals):
    """{key: value} -> {key: rank}, 1 = highest value (ties share the best rank)."""
    order = sorted(vals.values(), reverse=True)
    return {k: order.index(v) + 1 for k, v in vals.items()}


def pct(a, b):
    return round(100 * a / b) if b else ''


def r1(x):
    return round(x, 1)


def short_status(s):
    return {'Injured Reserve': 'IR'}.get(s, s)


# ---------------------------------------------------------------- build
def build(week, log, injuries_only=False):
    now = datetime.now(timezone.utc)
    g25 = load(os.path.join(DATA, 'games_2025.json'), {})
    if not injuries_only:
        if len(g25) < 272:
            g25 = refresh_games(2025, MAXWK, log)
        g26 = refresh_games(2026, week, log)
    else:
        g26 = load(os.path.join(DATA, 'games_2026.json'), {})
    games = {**g25, **g26}
    rows = []
    for gid, g in games.items():
        if g['season'] == 2026 and g['week'] > week:
            continue
        for r in g['rows']:
            rows.append(dict(r, season=g['season'], week=g['week'], gid=gid, td=r['rectd'] + r['rushtd']))
    pos = refresh_positions(sorted({r['id'] for r in rows}), log) if not injuries_only else load(os.path.join(DATA, 'pos.json'), {})
    for r in rows:
        r['pos'] = pos.get(r['id'], '?')

    # team totals per game
    tt = defaultdict(lambda: dict(td=0, rz=0, tgt=0))
    for r in rows:
        k = (r['gid'], r['team']); tt[k]['td'] += r['td']; tt[k]['rz'] += r['rz']; tt[k]['tgt'] += r['tgt']
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r['id']][r['season']].append(r)
    for d in by.values():
        for g in d.values():
            g.sort(key=lambda r: r['week'])

    # ---- player summaries
    P = {}
    for aid, d in by.items():
        g6, g5 = d.get(2026, []), d.get(2025, [])
        if not g6:
            continue
        last = g6[-1]
        x = dict(id=aid, name=last['name'], team=last['team'], pos=last['pos'], g6=g6, g5=g5,
                 gp6=len(g6), gp5=len(g5),
                 h6=sum(1 for r in g6 if r['td']), h5=sum(1 for r in g5 if r['td']),
                 t6=sum(r['td'] for r in g6), t5=sum(r['td'] for r in g5),
                 mx=max(r['td'] for r in g6 + g5),
                 rz6=sum(r['rz'] for r in g6), i106=sum(r['i10'] for r in g6),
                 rz5=sum(r['rz'] for r in g5), i105=sum(r['i10'] for r in g5),
                 trz6=sum(tt[(r['gid'], r['team'])]['rz'] for r in g6),
                 rec6=[r['rec'] for r in g6], tgt6=sum(r['tgt'] for r in g6),
                 ttgt6=sum(tt[(r['gid'], r['team'])]['tgt'] for r in g6))
        x['comb'] = (x['h5'] + x['h6']) / (x['gp5'] + x['gp6'])
        P[aid] = x
    names = {x['name']: aid for aid, x in P.items()}
    tracked = [aid for aid, x in P.items() if x['t6'] > 0 and x['pos'] in SKILL]
    for n in REPORT_PLAYERS:
        if n in names and names[n] not in tracked:
            tracked.append(names[n])
    tracked.sort(key=lambda a: (-P[a]['h6'], -P[a]['t6'], -P[a]['rz6'], P[a]['name']))

    # ---- injuries
    inj, inj_ts = fetch_injuries()

    def status(aid):
        i = inj.get(aid)
        if not i:
            return dict(status='Active', injury='', date='', note='', ret='')
        st = short_status(i['status'])
        if st == 'Out' and i['fantasy'] == 'INACTIVE' and i['injury'].startswith("Coach"):
            st = 'Out (inactive)'
        if st == 'Active':
            # Active entries are mostly game recaps; keep the note only when it names an injury, e.g. "Nacua (hip)"
            keep = re.search(r'\((?!on )[a-z][a-z ,/-]*\)', i['note'] or '')
            return dict(i, status=st, injury='', ret='', date=i['date'][:10] if keep else '', note=i['note'] if keep else '')
        return dict(i, status=st, date=i['date'][:10])

    tabs = {}
    wkhdr = [f'Wk{w}' for w in range(1, MAXWK + 1)]

    # ---- Scorers
    sc = [['Player', 'Team', 'Pos'] + wkhdr + ['Games played', 'Games w/ TD', '2026 hit %', '2025 hit %',
                                                '2025 games w/ TD', 'Total TDs 2026', 'Total TDs 2025', 'Max in one game (25+26)']]
    for aid in tracked:
        x = P[aid]; wk = {r['week']: r['td'] for r in x['g6']}
        sc.append([x['name'], x['team'], x['pos']] + [wk.get(w, '') for w in range(1, MAXWK + 1)] +
                  [x['gp6'], x['h6'], pct(x['h6'], x['gp6']), pct(x['h5'], x['gp5']) if x['gp5'] else 'n/a',
                   f"{x['h5']}/{x['gp5']}" if x['gp5'] else 'n/a', x['t6'], x['t5'] if x['gp5'] else 'n/a', x['mx']])
    tabs['Scorers'] = sc

    # ---- Red Zone
    rz = [['Player', 'Team', 'Pos'] + [f'Wk{w} RZ/i10' for w in range(1, MAXWK + 1)] +
          ['2026 RZ opps', '2026 i10 opps', 'RZ opps/g 2026', 'i10 opps/g 2026', 'Team RZ share 2026',
           'RZ opps/g 2025', 'i10 opps/g 2025']]
    for aid in tracked:
        x = P[aid]; wk = {r['week']: f"{r['rz']}/{r['i10']}" for r in x['g6']}
        rz.append([x['name'], x['team'], x['pos']] + [wk.get(w, '') for w in range(1, MAXWK + 1)] +
                  [x['rz6'], x['i106'], r1(x['rz6'] / x['gp6']), r1(x['i106'] / x['gp6']),
                   f"{pct(x['rz6'], x['trz6'])}%" if x['trz6'] else 'n/a',
                   r1(x['rz5'] / x['gp5']) if x['gp5'] else 'n/a', r1(x['i105'] / x['gp5']) if x['gp5'] else 'n/a'])
    tabs['Red Zone'] = rz

    # ---- Injuries
    ij = [['Player', 'Team', 'Pos', 'Status', 'Injury', 'Last updated', 'Est. return', 'Note']]
    for aid in sorted(tracked, key=lambda a: (status(a)['status'] == 'Active', P[a]['name'])):
        x = P[aid]; s = status(aid)
        ij.append([x['name'], x['team'], x['pos'], s['status'], s['injury'], s['date'], s.get('ret', ''), s['note'][:160]])
    tabs['Injuries'] = ij

    # ---- Defense
    def defense(season):
        D = defaultdict(lambda: defaultdict(float)); G = defaultdict(set)
        for r in rows:
            if r['season'] != season:
                continue
            G[r['opp']].add(r['gid'])
            p = 'RB' if r['pos'] == 'FB' else r['pos']
            if p in ('RB', 'WR', 'TE'):
                D[r['opp']][p + '_rush'] += r['rushtd']; D[r['opp']][p + '_rectd'] += r['rectd']
                D[r['opp']][p + '_td'] += r['td']; D[r['opp']][p + '_rec'] += r['rec']
            elif p == 'QB':
                D[r['opp']]['QB_rush'] += r['rushtd']
        RZ = defaultdict(lambda: [0, 0])
        for gid, g in games.items():
            if g['season'] != season or (season == 2026 and g['week'] > week):
                continue
            for team, inrz, td in g['drives']:
                if inrz:
                    opp = [t for t in g['teams'] if t != team][0]
                    RZ[opp][0] += 1; RZ[opp][1] += td
        out = {}
        for t in G:
            n = len(G[t]); x = {k: v for k, v in D[t].items()}; x['g'] = n
            x['rz_trips'], x['rz_td'] = RZ[t]
            x['rz_pct'] = x['rz_td'] / x['rz_trips'] if x['rz_trips'] else 0
            out[t] = x
        ranks = {}
        for k in ['RB_td', 'WR_td', 'TE_td', 'RB_rec', 'WR_rec', 'TE_rec', 'QB_rush']:
            ranks[k] = rank_desc({t: out[t].get(k, 0) / out[t]['g'] for t in out})
        ranks['rz_pct'] = rank_desc({t: out[t]['rz_pct'] for t in out})
        return out, ranks
    d26, k26 = defense(2026)
    d25, k25 = defense(2025)
    df = [['Team', 'G', 'RB rush TD', 'RB rec TD', 'RB TD/g', 'RB TD rank', 'WR TD', 'WR TD/g', 'WR TD rank',
           'TE TD', 'TE TD/g', 'TE TD rank', 'QB rush TD/g', 'QB rush rank',
           'RB rec/g', 'RB rec rank', 'WR rec/g', 'WR rec rank', 'TE rec/g', 'TE rec rank',
           'Opp RZ trips', 'Opp RZ TDs', 'RZ TD% allowed', 'RZ TD% rank',
           '2025 RB TD rank', '2025 WR TD rank', '2025 TE TD rank', '2025 RZ TD% rank']]
    for t in sorted(d26, key=lambda t: (k26['RB_td'][t] + k26['WR_td'][t] + k26['TE_td'][t], t)):
        x = d26[t]; n = x['g']; g = lambda k: x.get(k, 0)
        df.append([t, n, int(g('RB_rush')), int(g('RB_rectd')), r1(g('RB_td') / n), k26['RB_td'][t],
                   int(g('WR_td')), r1(g('WR_td') / n), k26['WR_td'][t], int(g('TE_td')), r1(g('TE_td') / n), k26['TE_td'][t],
                   r1(g('QB_rush') / n), k26['QB_rush'][t],
                   r1(g('RB_rec') / n), k26['RB_rec'][t], r1(g('WR_rec') / n), k26['WR_rec'][t], r1(g('TE_rec') / n), k26['TE_rec'][t],
                   x['rz_trips'], x['rz_td'], f"{pct(x['rz_td'], x['rz_trips'])}%" if x['rz_trips'] else 'n/a', k26['rz_pct'][t],
                   k25['RB_td'].get(t, 'n/a'), k25['WR_td'].get(t, 'n/a'), k25['TE_td'].get(t, 'n/a'), k25['rz_pct'].get(t, 'n/a')])
    tabs['Defense'] = df

    # ---- Week Shortlist
    nxt = week + 1
    opp_of, game_of = {}, {}
    try:
        sb = scoreboard(2026, nxt)
        for e in sb.get('events', []):
            c = e['competitions'][0]
            home = [x['team']['abbreviation'] for x in c['competitors'] if x['homeAway'] == 'home'][0]
            away = [x['team']['abbreviation'] for x in c['competitors'] if x['homeAway'] == 'away'][0]
            kt = datetime.fromisoformat(e['date'].replace('Z', '+00:00')).astimezone(ET)
            day = kt.strftime('%a %-I:%M %p ET')
            opp_of[home], opp_of[away] = away, home
            game_of[home] = game_of[away] = f"{e.get('shortName', away + ' @ ' + home)} ({day})"
    except Exception as ex:  # noqa
        log(f'Week {nxt} schedule unavailable: {ex}')
    key_of = {'RB': 'RB_td', 'FB': 'RB_td', 'WR': 'WR_td', 'TE': 'TE_td', 'QB': 'QB_rush'}
    ws = [['Player', 'Team', 'Pos', f'Week {nxt} game', 'Opponent', 'Opp rank vs pos (2026)', 'Opp rank vs pos (2025)',
           'Opp RZ TD% rank', 'Hit % 25+26', '2026 games w/ TD', 'RZ opps/g 2026', 'Injury status', 'Verdict', 'Why']]
    cands = [a for a in tracked if P[a]['h6'] >= 2 or P[a]['name'] in REPORT_PLAYERS[:15]]
    for aid in sorted(cands, key=lambda a: -P[a]['comb']):
        x = P[aid]; t = x['team']; opp = opp_of.get(t); s = status(aid)['status']
        k = key_of.get(x['pos'])
        rk = k26[k].get(opp) if (opp and k) else None
        rk25 = k25[k].get(opp, 'n/a') if (opp and k) else 'n/a'
        c = x['comb']
        if not opp:
            v, why = 'Skip', 'Bye week'
        elif s in ('Out', 'Out (inactive)', 'IR', 'Doubtful', 'Suspension'):
            v, why = 'Skip', f'Injury status: {s}'
        else:
            if c >= 0.55 and rk <= 16:
                v, why = 'Play', f'{round(c*100)}% hit rate, opp #{rk} softest'
            elif c >= 0.55:
                v, why = 'Small stake', f'{round(c*100)}% hit rate, tough opp (#{rk})'
            elif c >= 0.45 and rk <= 12:
                v, why = 'Small stake', f'{round(c*100)}% hit rate, soft opp (#{rk})'
            else:
                v, why = 'Skip', f'{round(c*100)}% hit rate, opp #{rk}'
            if x['gp6'] >= 4 and x['h6'] / x['gp6'] <= 0.25 and v != 'Skip':
                v = {'Play': 'Small stake', 'Small stake': 'Skip'}[v]
                why += f"; cold in 2026 ({x['h6']}/{x['gp6']})"
            if s == 'Questionable':
                v = {'Play': 'Small stake', 'Small stake': 'Skip'}.get(v, v)
                why += '; questionable, check Sat/Sun'
            if x['gp5'] + x['gp6'] < 8:
                v = 'Small stake' if v == 'Play' else v
                why += '; small sample'
        ws.append([x['name'], t, x['pos'], game_of.get(t, 'BYE'), opp or '-', rk if rk else '-', rk25,
                   k26['rz_pct'].get(opp, '-') if opp else '-', f"{round(c*100)}%", f"{x['h6']}/{x['gp6']}",
                   r1(x['rz6'] / x['gp6']), s, v, why])
    order = {'Play': 0, 'Small stake': 1, 'Skip': 2}
    ws[1:] = sorted(ws[1:], key=lambda r: (order[r[12]], -int(r[8].rstrip('%'))))
    tabs['Week Shortlist'] = ws

    # ---- Notes
    pending = PENDING if not injuries_only else []
    unresolved = sum(g.get('unresolved', 0) for g in g26.values())
    tabs['Notes'] = [
        ['Item', 'Detail'],
        ['Last update', now.astimezone(ET).strftime('%a %m/%d/%Y %I:%M %p ET') + f' (2026 games through Week {week}' + (f'; not final yet: {", ".join(pending)}' if pending else '') + f'; injuries feed {inj_ts[:16].replace("T", " ")} UTC)'],
        ['Data', 'ESPN game summaries (box score + play-by-play) for every 2025 regular-season game and 2026 games through this week. ESPN injuries feed. ESPN athlete pages for positions.'],
        ['Scorers', 'Wk columns = rushing + receiving TDs that week. Blank = no box-score line (bye, did not play, or played without a touch). 0 = played, no TD. Return and passing TDs not counted.'],
        ['Hit %', 'Games with a rushing or receiving TD / games played. 2025 numbers came with the 2025 team.'],
        ['Red Zone', 'Wk cell = RZ opps / inside-10 opps. RZ opp = target or carry on a play that started inside the opponent 20; i10 = inside the 10. Counted from ESPN play-by-play text; plays wiped out by penalty excluded. Estimates, not official counts.'],
        ['Team RZ share', "Player RZ opps / all RZ opps (targets + carries) by his team in the games he played."],
        ['Defense', 'TDs and catches allowed to each position, 2026 per game. Rank #1 = allows the most (softest), #32 = allows the least. Ties share a rank. RZ TD% allowed = opponent drives that ran a play inside the 20 and ended in a TD / those drives. 2025 ranks shown as a second look.'],
        ['Week Shortlist', 'Mechanical rule: Play = 55%+ hit rate (2025+2026) and opponent top 16 softest vs the position; Small stake = 55%+ vs a tough defense, or 45%+ vs a top 12 soft defense; Questionable, a cold 2026 (TD in 25% or fewer of 4+ games) and a small sample (under 8 games) each drop one level; Out/IR/Doubtful/bye = Skip. Small stakes only, for fun.'],
        ['Injuries', 'Status from the ESPN injuries feed. "Out (inactive)" = listed inactive as a coach decision. Not on the report = Active. "Out" with note "inactive" right after a Sunday means he sat that game; the status for the next game comes with the Wed-Fri practice reports, so recheck Saturday before betting.'],
        ['Not available', 'Routes run %, snap counts and official red-zone splits (Pro-Football-Reference blocks requests). Left out rather than guessed.'],
        ['Name matches', f'Play-by-play names are matched to the box score by team + last name + first initials. Unresolved RZ plays in 2026 so far: {unresolved}.'],
        ['Refresh', f'python3 analysis/nfl/build_tracker.py --week N (full) or --injuries-only. Repo: analysis/nfl/README.md'],
    ]

    # ---- 2026-only rankings (markdown)
    tdr = [x for x in P.values() if x['pos'] in SKILL and x['h6'] > 0]
    tdr.sort(key=lambda x: (-x['h6'], -x['rz6'] / x['gp6'], x['gp6']))
    md = ['### 2026 only: Anytime TD top 15', '',
          'Ranked by number of 2026 games with a TD, then red-zone opps per game. No 2025 data in the order.', '',
          '| # | Player | Tm | Pos | 2026 games w/ TD | TDs | RZ opps/g | Inside-10/g | Team RZ share | 2026 by game |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for i, x in enumerate(tdr[:15], 1):
        md.append(f"| {i} | {x['name']} | {x['team']} | {x['pos']} | {x['h6']}/{x['gp6']} | {x['t6']} | {x['rz6']/x['gp6']:.1f} | {x['i106']/x['gp6']:.1f} | {pct(x['rz6'], x['trz6'])}% | {' '.join(str(r['td']) for r in x['g6'])} |")
    rcr = [x for x in P.values() if x['pos'] in ('WR', 'TE', 'RB') and x['gp6'] >= 3]
    rcr.sort(key=lambda x: (-S.mean(x['rec6']), -min(x['rec6'])))
    md += ['', '### 2026 only: Receptions top 15', '',
           'Ranked by 2026 catches per game, then the lowest game (floor). Minimum 3 games played in 2026.', '',
           '| # | Player | Tm | Pos | Games | Avg | Floor | Over 4.5 | Over 5.5 | Tgt share | 2026 by game |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for i, x in enumerate(rcr[:15], 1):
        rc = x['rec6']
        md.append(f"| {i} | {x['name']} | {x['team']} | {x['pos']} | {len(rc)} | {S.mean(rc):.1f} | {min(rc)} | {sum(v > 4.5 for v in rc)}/{len(rc)} | {sum(v > 5.5 for v in rc)}/{len(rc)} | {pct(x['tgt6'], x['ttgt6'])}% | {' '.join(map(str, rc))} |")

    if injuries_only:
        prev = load(os.path.join(OUT, 'tracker.json'), {})
        prev.update({k: tabs[k] for k in ('Injuries', 'Week Shortlist', 'Notes')})
        tabs = prev
    os.makedirs(OUT, exist_ok=True)
    save(os.path.join(OUT, 'tracker.json'), tabs)
    # Sheet-safe copy: Sheets would turn "3/4" or "8/5" into dates, so keep them as text.
    safe = {k: [[("'" + c) if isinstance(c, str) and re.fullmatch(r'\d+/\d+', c) else c for c in row] for row in v]
            for k, v in tabs.items()}
    save(os.path.join(OUT, 'sheet_values.json'), safe)
    for name, vals in tabs.items():
        with open(os.path.join(OUT, name.lower().replace(' ', '_') + '.csv'), 'w', newline='') as f:
            csv.writer(f).writerows(vals)
    if not injuries_only:
        with open(os.path.join(OUT, 'rank_2026.md'), 'w') as f:
            f.write('\n'.join(md) + '\n')
    log('tabs: ' + ', '.join(f'{k} ({len(v)-1} rows)' for k, v in tabs.items()))
    return tabs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--week', type=int, required=True, help='last completed 2026 week to include')
    ap.add_argument('--injuries-only', action='store_true', help='only refresh Injuries + Week Shortlist + Notes')
    a = ap.parse_args()
    build(a.week, lambda m: print(m, file=sys.stderr), a.injuries_only)


if __name__ == '__main__':
    main()
