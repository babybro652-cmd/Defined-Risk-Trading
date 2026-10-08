#!/usr/bin/env python3
"""Build the NHL tab of Tim's Bet Tracker sheet (anytime goal, first goal, shots on goal).

Usage:
  python3 analysis/nhl/build_nhl_tab.py                 # slate = today (ET)
  python3 analysis/nhl/build_nhl_tab.py --date 2026-10-15

Data:
  - NHL API (api-web.nhle.com): every 2025-26 and 2026-27 regular-season boxscore
    (goals, PP goals, SOG, TOI, starting goalie) and game landing (goal order -> first goal).
    Parsed games are cached in data/games_<season>.json, so reruns only fetch new games.
  - NHL stats API (api.nhle.com/stats/rest): team GA/G, SA/G, PK%; skater PP TOI; goalie SV%.
  - Daily Faceoff starting goalies page (probable goalies with Confirmed / Likely).
  - ESPN NHL injuries feed.

Output:
  out/sheet_values.json  {"NHL": [[...], ...], "meta": {...}}  ready for the Sheets connector
  out/nhl_tab.csv        same grid as CSV
  out/shortlist.md       tonight's shortlist as text
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
CUR, LAST = '20262027', '20252026'
CUR_START = dt.date(2026, 9, 20)
W_DEFAULT = 3          # one 2026-27 game counts as this many 2025-26 games in the blend
N_FWD, N_D = 34, 6     # players in the main tables
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url, tries=4, raw=False):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read()
                return b.decode('utf-8', 'replace') if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code == 404:
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


def secs(t):
    if not t:
        return 0
    m, s = t.split(':')
    return int(m) * 60 + int(s)


def norm(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z ]', '', s.replace('-', ' '))
    return ' '.join(s.split())


def slug(name):
    return norm(name).replace(' ', '-')


# ---------- games ----------
def parse_game(gid):
    bx = get(f'https://api-web.nhle.com/v1/gamecenter/{gid}/boxscore')
    if not bx or bx.get('gameState') not in ('OFF', 'FINAL'):
        return None
    ld = get(f'https://api-web.nhle.com/v1/gamecenter/{gid}/landing')
    fg = None
    for per in (ld or {}).get('summary', {}).get('scoring', []):
        if per['periodDescriptor'].get('periodType') == 'SO':
            continue
        if per['goals']:
            g = per['goals'][0]
            fg = [g['playerId'], g['teamAbbrev']['default'] if isinstance(g['teamAbbrev'], dict) else g['teamAbbrev'],
                  g.get('strength', '')]
            break
    rec = {'id': gid, 'date': bx['gameDate'], 'away': bx['awayTeam']['abbrev'], 'home': bx['homeTeam']['abbrev'],
           'as': bx['awayTeam'].get('score'), 'hs': bx['homeTeam'].get('score'), 'fg': fg, 'sk': [], 'gl': [], 'nm': {}}
    for side in ('awayTeam', 'homeTeam'):
        tm = bx[side]['abbrev']
        ps = bx['playerByGameStats'][side]
        for grp in ('forwards', 'defense'):
            for p in ps.get(grp, []):
                rec['sk'].append([p['playerId'], tm, p['position'], p.get('goals', 0), p.get('powerPlayGoals', 0),
                                  p.get('sog', 0), secs(p.get('toi'))])
                rec['nm'][str(p['playerId'])] = p['name']['default']
        for p in ps.get('goalies', []):
            rec['gl'].append([p['playerId'], tm, bool(p.get('starter')), p.get('shotsAgainst', 0),
                              p.get('goalsAgainst', 0), secs(p.get('toi'))])
            rec['nm'][str(p['playerId'])] = p['name']['default']
    return rec


def season_ids(season, today):
    if season == LAST:
        return [int(f'2025020{n:03d}') if n < 1000 else int(f'202502{n:04d}') for n in range(1, 1313)]
    ids, d = [], CUR_START
    while d <= today:
        s = get(f'https://api-web.nhle.com/v1/schedule/{d.isoformat()}')
        for w in s.get('gameWeek', []):
            for g in w['games']:
                if g['gameType'] == 2 and w['date'] < today.isoformat():
                    ids.append(g['id'])
        d += dt.timedelta(days=7)
    return sorted(set(ids))


def refresh(season, today, log):
    path = os.path.join(DATA, f'games_{season}.json')
    games = load(path, {})
    todo = [g for g in season_ids(season, today) if str(g) not in games]
    log(f'{season}: {len(games)} cached, {len(todo)} to fetch')
    with ThreadPoolExecutor(10) as ex:
        for gid, rec in zip(todo, ex.map(parse_game, todo)):
            if rec:
                games[str(gid)] = rec
            else:
                log(f'  {gid} not final, skipped')
    save(path, games)
    return games


# ---------- aggregates ----------
def player_stats(games):
    P = {}
    for g in sorted(games.values(), key=lambda x: (x['date'], x['id'])):
        fgp = g['fg'][0] if g['fg'] else None
        for pid, tm, pos, gl, ppg, sog, toi in g['sk']:
            s = P.setdefault(pid, {'gp': 0, 'g': 0, 'gwg': 0, 'ppg': 0, 'sog': 0, 'toi': 0, 'fg': 0, 'log': [],
                                   'tm': tm, 'pos': pos, 'nm': g['nm'][str(pid)]})
            s['gp'] += 1; s['g'] += gl; s['gwg'] += 1 if gl else 0; s['ppg'] += ppg; s['sog'] += sog
            s['toi'] += toi; s['fg'] += 1 if fgp == pid else 0
            s['log'].append((g['date'], sog)); s['tm'] = tm; s['pos'] = pos
    return P


def team_stats(games):
    T = {}
    for g in games.values():
        for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
            t = T.setdefault(tm, {'gp': 0, 'first': 0, 'allow_first': 0, 'starts': {}, 'last': ''})
            t['gp'] += 1
            if g['fg']:
                t['first'] += g['fg'][1] == tm
                t['allow_first'] += g['fg'][1] == opp
            for pid, gtm, st, *_ in g['gl']:
                if gtm == tm and st:
                    t['starts'][pid] = t['starts'].get(pid, 0) + 1
            t['last'] = max(t['last'], g['date'])
    return T


def stats_api(path, season):
    u = f'https://api.nhle.com/stats/rest/en/{path}?limit=-1&cayenneExp=seasonId={season}%20and%20gameTypeId=2'
    return (get(u) or {}).get('data', [])


def pct(x):
    return None if x is None else round(x, 3)


def blend(hc, gc, hl, gl, w):
    den = w * gc + gl
    return (w * hc + hl) / den if den else None


def build(slate, log):
    os.makedirs(DATA, exist_ok=True)
    today = slate
    gl_last = refresh(LAST, today, log)
    gl_cur = refresh(CUR, today, log)
    PL, PC = player_stats(gl_last), player_stats(gl_cur)
    TL, TC = team_stats(gl_last), team_stats(gl_cur)

    # names, current teams (rosters)
    stand = get('https://api-web.nhle.com/v1/standings/now')['standings']
    abbr_by_name = {s['teamName']['default']: s['teamAbbrev']['default'] for s in stand}
    abbr_by_slug = {slug(k): v for k, v in abbr_by_name.items()}
    teams = sorted(abbr_by_name.values())
    roster = {}
    with ThreadPoolExecutor(8) as ex:
        for tm, r in zip(teams, ex.map(lambda t: get(f'https://api-web.nhle.com/v1/roster/{t}/current'), teams)):
            for grp in ('forwards', 'defensemen', 'goalies'):
                for p in (r or {}).get(grp, []):
                    roster[p['id']] = {'name': f"{p['firstName']['default']} {p['lastName']['default']}",
                                       'tm': tm, 'pos': p['positionCode']}
    save(os.path.join(DATA, 'rosters.json'), {str(k): v for k, v in roster.items()})

    # stats API
    tsum = {s: {abbr_by_name.get(t['teamFullName'], t['teamFullName']): t for t in stats_api('team/summary', s)}
            for s in (LAST, CUR)}
    pptoi = {s: {t['playerId']: t['ppTimeOnIcePerGame'] for t in stats_api('skater/timeonice', s)} for s in (LAST, CUR)}
    gsum = {s: {g['playerId']: g for g in stats_api('goalie/summary', s)} for s in (LAST, CUR)}
    save(os.path.join(DATA, 'stats_api.json'), {'team': tsum, 'pptoi': pptoi, 'goalie': gsum})

    # injuries (ESPN)
    inj = {}
    for t in (get('https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries') or {}).get('injuries', []):
        for i in t.get('injuries', []):
            inj[norm(i['athlete']['displayName'])] = {'status': i.get('status', ''), 'note': i.get('shortComment', '')}
    save(os.path.join(DATA, 'injuries.json'), inj)

    # tonight: schedule + Daily Faceoff goalies
    sch = get(f'https://api-web.nhle.com/v1/schedule/{today.isoformat()}')
    slate_games = []
    for w in sch.get('gameWeek', []):
        if w['date'] == today.isoformat():
            for g in w['games']:
                if g['gameType'] == 2:
                    t = dt.datetime.fromisoformat(g['startTimeUTC'].replace('Z', '+00:00')) - dt.timedelta(hours=4)
                    slate_games.append({'away': g['awayTeam']['abbrev'], 'home': g['homeTeam']['abbrev'],
                                        'time': t.strftime('%-I:%M')})
    dfo = {}
    try:
        h = get(f'https://www.dailyfaceoff.com/starting-goalies/{today.isoformat()}', raw=True)
        nd = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S).group(1))
        for x in nd['props']['pageProps']['data']:
            for side in ('home', 'away'):
                ab = abbr_by_slug.get(x[f'{side}TeamSlug'])
                if ab:
                    dfo[ab] = (x.get(f'{side}GoalieName') or '?', x.get(f'{side}NewsStrengthName') or 'Unconfirmed')
    except Exception as e:
        log(f'Daily Faceoff not read: {e}')
    save(os.path.join(DATA, f'goalies_{today.isoformat()}.json'), dfo)
    opp_of = {}
    for g in slate_games:
        opp_of[g['away']] = (g['home'], '@'); opp_of[g['home']] = (g['away'], 'vs')

    W = W_DEFAULT
    name_to_gid = {}
    for s in (LAST, CUR):
        for pid, g in gsum[s].items():
            name_to_gid[norm(g['goalieFullName'])] = pid

    def sv(pid, s):
        g = gsum[s].get(pid)
        return (g['savePct'], g['gamesPlayed']) if g else (None, 0)

    def team_row(tm):
        c, l = tsum[CUR].get(tm, {}), tsum[LAST].get(tm, {})
        tc, tl = TC.get(tm, {'gp': 0, 'first': 0, 'allow_first': 0, 'starts': {}}), TL.get(tm, {'gp': 0, 'first': 0, 'allow_first': 0, 'starts': {}})
        return c, l, tc, tl

    # ---------- player universe ----------
    def P(pid):
        c, l = PC.get(pid), PL.get(pid)
        z = {'gp': 0, 'g': 0, 'gwg': 0, 'ppg': 0, 'sog': 0, 'toi': 0, 'fg': 0, 'log': []}
        c, l = c or z, l or z
        r = roster.get(pid)
        tm = r['tm'] if r else (PC.get(pid) or PL.get(pid))['tm']
        pos = r['pos'] if r else (PC.get(pid) or PL.get(pid))['pos']
        name = r['name'] if r else (PC.get(pid) or PL.get(pid))['nm']
        logs = sorted(l['log'] + c['log'], reverse=True)
        sogs = [s for _, s in l['log']], [s for _, s in c['log']]
        def over(k):
            return blend(sum(x > k for x in sogs[1]), len(sogs[1]), sum(x > k for x in sogs[0]), len(sogs[0]), W)
        return {'pid': pid, 'name': name, 'tm': tm, 'pos': pos, 'c': c, 'l': l, 'onroster': bool(r),
                'hit': blend(c['gwg'], c['gp'], l['gwg'], l['gp'], W),
                'fgr': blend(c['fg'], c['gp'], l['fg'], l['gp'], W),
                'sogpg': blend(c['sog'], c['gp'], l['sog'], l['gp'], W),
                'gpg': blend(c['g'], c['gp'], l['g'], l['gp'], W),
                'over': {k: over(k) for k in (1.5, 2.5, 3.5, 4.5)},
                'l5': [s for _, s in logs[:5]], 'l5cur': min(5, len(c['log'])),
                'toipg': blend(c['toi'], c['gp'], l['toi'], l['gp'], W) or 0,
                'pp': pptoi[CUR].get(pid) if c['gp'] else pptoi[LAST].get(pid),
                'inj': inj.get(norm(name))}

    cand = [P(pid) for pid in set(PC) | set(PL) if pid in roster and roster[pid]['pos'] != 'G']
    cand = [p for p in cand if (p['c']['gp'] * W + p['l']['gp']) >= 30]

    # role: TOI rank among team F / D, PP TOI rank among team skaters (current season if played)
    by_team = {}
    for p in cand:
        by_team.setdefault(p['tm'], []).append(p)
    for tm, ps in by_team.items():
        act = [p for p in ps if p['c']['gp'] or not TC.get(tm)]
        fw = sorted([p for p in act if p['pos'] != 'D'], key=lambda p: -p['toipg'])
        de = sorted([p for p in act if p['pos'] == 'D'], key=lambda p: -p['toipg'])
        pp = sorted([p for p in act if p['pp']], key=lambda p: -p['pp'])
        for p in ps:
            parts = []
            if p in fw:
                i = fw.index(p); parts.append('Top 6' if i < 6 else ('Mid 6' if i < 9 else 'Bottom'))
            elif p in de:
                i = de.index(p); parts.append('Top pair' if i < 2 else ('2nd pair' if i < 4 else '3rd pair'))
            else:
                parts.append('No 26-27 GP')
            if p in pp:
                i = pp.index(p); parts.append('PP1' if i < 5 else ('PP2' if i < 10 else ''))
            p['role'] = ' '.join(x for x in parts if x)

    fwd = sorted([p for p in cand if p['pos'] != 'D'], key=lambda p: -(p['hit'] or 0))[:N_FWD]
    dmen = sorted([p for p in cand if p['pos'] == 'D'], key=lambda p: -(p['sogpg'] or 0))[:N_D]

    # ---------- tonight's shortlist ----------
    def opp_info(tm):
        if tm not in opp_of:
            return None
        o, at = opp_of[tm]
        c, l, tc, tl = team_row(o)
        ga = blend(c.get('goalsAgainst', 0), c.get('gamesPlayed', 0), l.get('goalsAgainst', 0), l.get('gamesPlayed', 0), W)
        sa = blend(c.get('shotsAgainstPerGame', 0) * c.get('gamesPlayed', 0), c.get('gamesPlayed', 0),
                   l.get('shotsAgainstPerGame', 0) * l.get('gamesPlayed', 0), l.get('gamesPlayed', 0), W)
        gname, gstat = dfo.get(o, ('?', 'Unconfirmed'))
        gid = name_to_gid.get(norm(gname))
        gsv = None
        if gid:
            (s1, n1), (s2, n2) = sv(gid, CUR), sv(gid, LAST)
            num = (s1 or 0) * n1 + (s2 or 0) * n2; den = n1 + n2   # games-weighted, no 26-27 boost
            gsv = num / den if den else None
        return {'opp': o, 'at': at, 'ga': ga, 'sa': sa, 'g': gname, 'gstat': gstat, 'gsv': gsv}

    lg = [t for t in tsum[LAST].values()]
    lg_ga = sum(t['goalsAgainst'] for t in lg) / sum(t['gamesPlayed'] for t in lg)
    lg_sa = sum(t['shotsAgainstPerGame'] for t in lg) / len(lg)

    tonight = []
    for p in cand:
        if p['tm'] not in opp_of or not p['c']['gp']:
            continue   # skip anyone without a 2026-27 game (scratch, injured, or not yet in lineup)
        st = (p['inj'] or {}).get('status', '')
        if st and st.lower() not in ('day-to-day',):
            continue
        p['opp'] = opp_info(p['tm'])
        tonight.append(p)

    def gfac(p):
        o = p['opp']; f = o['ga'] / lg_ga
        if o['gsv']:
            f *= max(0.9, min(1.1, 1 + (0.900 - o['gsv']) * 5))   # .010 of SV% under .900 = +5%, capped at 10%
        return f

    def fmt_pct(x):
        return f'{round(100 * x)}%' if x is not None else '-'

    def gl_txt(p):
        o = p['opp']
        return f"{o['g']} ({o['gstat'].lower()}, SV {('%.3f' % o['gsv']).lstrip('0') if o['gsv'] else 'n/a'})"

    picks = []
    goal = sorted(tonight, key=lambda p: -(p['hit'] * gfac(p)))[:4]
    for p in goal:
        o = p['opp']
        picks.append(['Anytime goal', p['name'], f"{p['tm']} {o['at']} {o['opp']}",
                      f"Scored in {fmt_pct(p['hit'])} of games (blend); 26-27: {p['c']['g']} G in {p['c']['gp']} GP; "
                      f"{o['opp']} allows {o['ga']:.1f} GA/G; faces {gl_txt(p)}", 'Anytime goal'])
    def tfirst(tm):
        c, l, tc, tl = team_row(tm)
        return blend(tc['first'], tc['gp'], tl['first'], tl['gp'], W) or 0.5
    # first goal is rare (about 1 in 10 games for a top scorer), so rank by goals per game, which is a
    # steadier estimate of the same thing, times how often the team scores first
    fgs = sorted([p for p in tonight if p['pid'] not in {x['pid'] for x in goal}],
                 key=lambda p: -((p['gpg'] or 0) * tfirst(p['tm']) * gfac(p)))[:3]
    for p in fgs:
        tf = tfirst(p['tm'])
        picks.append(['First goal', p['name'], f"{p['tm']} {p['opp']['at']} {p['opp']['opp']}",
                      f"Scored first in {p['l']['fg']}/{p['l']['gp']} games in 25-26, {p['c']['fg']}/{p['c']['gp']} in 26-27; "
                      f"{p['gpg']:.2f} goals/G (blend); {p['tm']} scores first {fmt_pct(tf)}; {p['role']}", 'First goal (long odds)'])
    sogs = []
    for p in tonight:
        for k in (3.5, 2.5, 1.5):
            r = p['over'][k]
            if r and r >= 0.70:
                sogs.append((r * (p['opp']['sa'] / lg_sa), k, p)); break
    sogs.sort(key=lambda x: (-x[1], -x[0]))   # highest line first, then rate x opponent shots allowed
    seen = set()
    for sc, k, p in sogs:
        if p['pid'] in seen or len(seen) >= 5:
            continue
        seen.add(p['pid'])
        picks.append([f'SOG over {k}', p['name'], f"{p['tm']} {p['opp']['at']} {p['opp']['opp']}",
                      f"Over {k} in {fmt_pct(p['over'][k])} of games (blend); {p['sogpg']:.1f} SOG/G; L5: "
                      f"{' '.join(map(str, p['l5']))}; {p['opp']['opp']} allows {p['opp']['sa']:.1f} SA/G", f'Over {k} SOG'])

    # make sure shortlist players are in the tables
    ids = {p['pid'] for p in fwd + dmen}
    extra = [p for p in tonight if p['name'] in {x[1] for x in picks} and p['pid'] not in ids]
    table = sorted(fwd + extra, key=lambda p: -(p['hit'] or 0)) + dmen

    # ---------- grid ----------
    nc, nl = len(gl_cur), len(gl_last)
    rows = []
    R = lambda *a: rows.append(list(a))
    R(f'NHL props: goals, first goal, SOG (as of {today.strftime("%-m/%-d")})')
    R('Legend', '26 = 2026-27 season so far, 25 = 2025-26 season. Hit% = games with a goal / games played. '
      'Blend = both seasons, each 26-27 game counts as many 25-26 games as the weight in B3. '
      f'Sample: {nc} 2026-27 games played so far (2-4 per team), so 25-26 drives most numbers until about November. '
      'Nothing here is guaranteed. Small stakes.')
    R('26-27 game weight', W, 'Input. Change it and the Blend columns update.')
    R()
    hdr_short = len(rows) + 1
    R(f'Tonight {today.strftime("%-m/%-d")}: shortlist (not guaranteed)')
    R('Bet', 'Player', 'Game', 'Why', 'Look for')
    for p in picks:
        R(*p)
    R('How picked', 'Goal = blended goal hit% x opponent GA/G x goalie SV%. First goal = blended goals per game x team scores-first '
      'rate (first-goal counts are too small to rank on). SOG = highest line with a 70%+ blended hit rate, then rate x opponent '
      'shots allowed. Players with no 2026-27 game or listed Out/IR are skipped. Recheck lines and goalies before puck drop.')
    R()
    R('Tonight: probable goalies and key injuries (Daily Faceoff, ESPN)')
    R('Game (ET)', 'Away goalie', 'Home goalie', 'Out / IR (ESPN)')
    for g in slate_games:
        def gtxt(tm):
            n, s = dfo.get(tm, ('?', 'Unconfirmed'))
            return f'{n} ({s})'
        outs = []
        for tm in (g['away'], g['home']):
            names = [roster[pid]['name'] for pid in roster if roster[pid]['tm'] == tm and
                     (inj.get(norm(roster[pid]['name'])) or {}).get('status', '').lower() in ('out', 'injured reserve')
                     and ((PC.get(pid) or {}).get('gp', 0) + (PL.get(pid) or {}).get('gp', 0) >= 40)]
            if names:
                outs.append(f"{tm}: {', '.join(names[:4])}")
        R(f"{g['away']} @ {g['home']} {g['time']}", gtxt(g['away']), gtxt(g['home']), '; '.join(outs) or 'none of note')
    R()

    def onhdr(title, cols):
        R(title); R(*cols); return len(rows) + 1   # first data row (1-based)

    # A: anytime goal
    s = onhdr('Anytime goal (top 34 forwards by blended goal hit%, plus top 6 D by shots)',
              ['Player', 'Tm', 'Pos', 'Role', 'GP 26', 'G 26', 'Games w/ G 26', 'Hit% 26', 'GP 25', 'G 25',
               'Games w/ G 25', 'Hit% 25', 'Blend hit%', 'PPG 26', 'PPG 25', 'SOG/G', 'Injury'])
    for i, p in enumerate(table):
        r = s + i
        R(p['name'], p['tm'], p['pos'], p['role'], p['c']['gp'], p['c']['g'], p['c']['gwg'],
          f'=IF(E{r}=0,"-",G{r}/E{r})', p['l']['gp'], p['l']['g'], p['l']['gwg'], f'=IF(I{r}=0,"-",K{r}/I{r})',
          f'=IF($B$3*E{r}+I{r}=0,"-",($B$3*G{r}+K{r})/($B$3*E{r}+I{r}))', p['c']['ppg'], p['l']['ppg'],
          round(p['sogpg'] or 0, 2), (p['inj'] or {}).get('status', ''))
    a_rng = (s, s + len(table) - 1)
    R()
    # B: first goal
    s = onhdr('First goal of the game (shootout goals not counted)',
              ['Player', 'Tm', 'Role', 'GP 26', 'FG 26', 'FG% 26', 'GP 25', 'FG 25', 'FG% 25', 'Blend FG%',
               'Team 1st% 26', 'Team 1st% 25'])
    for i, p in enumerate(sorted(table, key=lambda p: -(p['fgr'] or 0))):
        r = s + i
        c, l, tc, tl = team_row(p['tm'])
        R(p['name'], p['tm'], p['role'], p['c']['gp'], p['c']['fg'], f'=IF(D{r}=0,"-",E{r}/D{r})',
          p['l']['gp'], p['l']['fg'], f'=IF(G{r}=0,"-",H{r}/G{r})',
          f'=IF($B$3*D{r}+G{r}=0,"-",($B$3*E{r}+H{r})/($B$3*D{r}+G{r}))',
          pct(tc['first'] / tc['gp']) if tc['gp'] else '-', pct(tl['first'] / tl['gp']) if tl['gp'] else '-')
    b_rng = (s, s + len(table) - 1)
    R()
    # C: shots on goal
    s = onhdr('Shots on goal (share of games over each line, blended)',
              ['Player', 'Tm', 'SOG/G 26', 'SOG/G 25', 'Over 1.5', 'Over 2.5', 'Over 3.5', 'Over 4.5',
               'Last 5 (newest first)', 'L5 from 26'])
    for p in sorted(table, key=lambda p: -(p['sogpg'] or 0)):
        R(p['name'], p['tm'], round(p['c']['sog'] / p['c']['gp'], 2) if p['c']['gp'] else '-',
          round(p['l']['sog'] / p['l']['gp'], 2) if p['l']['gp'] else '-',
          *[pct(p['over'][k]) for k in (1.5, 2.5, 3.5, 4.5)], "'" + ' '.join(map(str, p['l5'])), p['l5cur'])
    c_rng = (s, len(rows))
    R()
    # D: opponents
    s = onhdr('Opponent weakness (all 32 teams, sorted by 26-27 goals allowed per game)',
              ['Team', 'GP 26', 'GA/G 26', 'SA/G 26', 'PK% 26', 'GA/G 25', 'SA/G 25', 'PK% 25', 'Main starter 26',
               'SV% 26', 'SV% 25', 'Opp scores 1st 26', 'Tonight'])
    trs = []
    for tm in teams:
        c, l, tc, tl = team_row(tm)
        st = max(tc['starts'].items(), key=lambda x: x[1])[0] if tc['starts'] else (
            max(tl['starts'].items(), key=lambda x: x[1])[0] if tl['starts'] else None)
        gn = roster.get(st, {}).get('name') or (gsum[CUR].get(st) or gsum[LAST].get(st) or {}).get('goalieFullName', '?')
        tn = ''
        if tm in opp_of:
            n, stt = dfo.get(tm, ('?', 'Unconfirmed'))
            tn = f"{opp_of[tm][1]} {opp_of[tm][0]}; G: {n} ({stt})"
        trs.append([tm, c.get('gamesPlayed', 0), round(c.get('goalsAgainstPerGame', 0), 2), round(c.get('shotsAgainstPerGame', 0), 1),
                    pct(c.get('penaltyKillPct')), round(l.get('goalsAgainstPerGame', 0), 2), round(l.get('shotsAgainstPerGame', 0), 1),
                    pct(l.get('penaltyKillPct')), gn, pct(sv(st, CUR)[0]) if sv(st, CUR)[0] is not None else '-',
                    pct(sv(st, LAST)[0]) if sv(st, LAST)[0] is not None else '-',
                    pct(tc['allow_first'] / tc['gp']) if tc['gp'] else '-', tn])
    for t in sorted(trs, key=lambda t: -t[2]):
        R(*t)
    d_rng = (s, len(rows))
    R()
    R('Sources', f'NHL API boxscores and game summaries (api-web.nhle.com), {nl} 2025-26 and {nc} 2026-27 regular-season games; '
      'NHL stats API (api.nhle.com) for GA/G, SA/G, PK%, SV%, PP time on ice; Daily Faceoff starting goalies; ESPN injuries. '
      f'Pulled {(dt.datetime.utcnow() - dt.timedelta(hours=4)).strftime("%-m/%-d %-I:%M %p")} ET. Role = TOI rank on team (Top 6 F, Top pair D) and PP time rank '
      '(PP1 = top 5 on team), a proxy for line charts, not the official lines. Rebuilt weekly by analysis/nhl/build_nhl_tab.py.')

    width = max(len(r) for r in rows)
    rows = [r + [''] * (width - len(r)) for r in rows]
    meta = {'short': hdr_short, 'n_picks': len(picks), 'a': a_rng, 'b': b_rng, 'c': c_rng, 'd': d_rng,
            'goalie_hdr': hdr_short + 2 + len(picks) + 3, 'width': width, 'rows': len(rows)}
    os.makedirs(OUT, exist_ok=True)
    json.dump({'NHL': rows, 'meta': meta}, open(os.path.join(OUT, 'sheet_values.json'), 'w'))
    with open(os.path.join(OUT, 'nhl_tab.csv'), 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    with open(os.path.join(OUT, 'shortlist.md'), 'w') as f:
        f.write(f'# NHL shortlist {today.isoformat()} (not guaranteed)\n\n')
        for p in picks:
            f.write(f'- **{p[0]}: {p[1]}** ({p[2]}). {p[3]}\n')
        f.write('\n## Goalies\n\n')
        for g in slate_games:
            f.write(f"- {g['away']} @ {g['home']} {g['time']} ET: {dfo.get(g['away'], ('?', '?'))} / {dfo.get(g['home'], ('?', '?'))}\n")
    log(f'wrote {len(rows)} rows x {width} cols; picks {len(picks)}; meta {meta}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--date', help='slate date YYYY-MM-DD (default today ET)')
    a = ap.parse_args()
    d = dt.date.fromisoformat(a.date) if a.date else (dt.datetime.utcnow() - dt.timedelta(hours=4)).date()
    build(d, lambda m: print(m, file=sys.stderr))


if __name__ == '__main__':
    main()
