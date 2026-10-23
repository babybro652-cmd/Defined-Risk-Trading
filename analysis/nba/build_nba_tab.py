#!/usr/bin/env python3
"""Build the NBA tab of Tim's Bet Tracker sheet (first basket, tip-off, points and threes).

Usage:
  python3 analysis/nba/build_nba_tab.py                  # slate = next game day from today (ET)
  python3 analysis/nba/build_nba_tab.py --date 2026-10-20

Slate rule: the first date on or after --date with NBA games. Before the regular season starts,
preseason dates are skipped and the slate is opening night (preseason starters are not real).

Data (all ESPN, free, no key):
  - site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=YYYYMMDD (schedule)
  - .../summary?event=<id> (boxscore with starters, play-by-play with jump ball and every shot)
  - .../teams, .../teams/<id>/roster (current teams), .../injuries
  Parsed games are cached in data/games_<season>.json, so reruns only fetch new games.
  cdn.nba.com and stats.nba.com are blocked from here (403 / timeout) and are not used.

Output:
  out/sheet_values.json  {"NBA": [[...], ...], "meta": {...}}  ready for the Sheets connector
  out/nba_tab.csv        same grid as CSV
  out/shortlist.md       the slate's shortlist as text
"""
import argparse, csv, datetime as dt, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
ET = ZoneInfo('America/New_York')
B = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba'
LAST, CUR = '2025-26', '2026-27'
SEASONS = {LAST: (dt.date(2025, 10, 21), dt.date(2026, 4, 12)),
           CUR: (dt.date(2026, 10, 1), dt.date(2027, 4, 12))}
W_DEFAULT = 3       # one 2026-27 regular-season game counts as this many 2025-26 games
UA = {'User-Agent': 'Mozilla/5.0'}
PTS_LINES = (9.5, 14.5, 19.5, 24.5)
THREE_LINES = (0.5, 1.5, 2.5, 3.5)
POS = ('G', 'F', 'C')

# ---------- first-basket model v2 (10/21/26; see README "How numbers are computed") ----------
# Each knob was checked in backtest_fb.py (2025-26 walk-forward plus 10/20/26).
V2 = {'w_shot': 0.5,      # share = (1 - w) x first-FG share + w x first-shot share x (his FG% / league FG%)
      'fg_k': 150,        # FG% shrunk toward league with 150 pseudo attempts
      'def_k': 120,       # defense-by-position rate shrunk toward league with 120 pseudo games
      'def_cap': 0.15,    # defense multiplier kept within 0.85 to 1.15
      'norm': 1.0,        # 1 = the five starters' shares are rescaled to sum to the league starter rate (injury ripple)
      'starter_sum': 0.99,
      'ramp_n': 5,        # 26-27 weight ramps from 1x at 0 starts with his current team to the full B3 weight at 5
      'k_new': 10,        # extra pseudo starts for a player with few starts in the data (any team) ...
      'settle_n': 10}     # ... fading to 0 at 10 starts, both seasons (a team-only count hurt traded regulars)


def cur_weight(w, n_cur, prm=V2):
    """26-27 game weight for one player: full weight only after prm['ramp_n'] 26-27 starts with his current team."""
    return 1 + (w - 1) * min(n_cur, prm['ramp_n']) / prm['ramp_n']


def v1_share(t1, gs, k=10):
    return (t1 + k / 5) / (gs + k)   # shrink toward 1 in 5 with k pseudo starts (10 by default)


def v2_shares(players, allow, allow_n, lg, prm=V2):
    """players: list of dicts with weighted counts gs, t1, sh1, fgm, fga and pos ('G'/'F'/'C').
    allow / allow_n: the opponent's first FGs allowed by position and games counted. lg: {'fg': league FG%,
    'pos': {pos: league share of team first FGs}}. Returns (shares, defense multipliers, raw v1 shares)."""
    w, out, mults, raw = prm['w_shot'], [], [], []
    for p in players:
        kp = 10   # few starts in the data (new starter): shrink harder toward 1 in 5
        if 'n_starts' in p and prm.get('k_new'):
            kp += prm['k_new'] * max(0, 1 - p['n_starts'] / prm['settle_n'])
        p = {k: p.get(k, 0) for k in ('gs', 't1', 'sh1', 'fgm', 'fga')} | {'pos': p.get('pos', '')}
        s1 = v1_share(p['t1'], p['gs'], kp)
        s2 = v1_share(p['sh1'], p['gs'], kp)
        fg = (p['fgm'] + prm['fg_k'] * lg['fg']) / (p['fga'] + prm['fg_k'])
        a = (1 - w) * s1 + w * s2 * fg / lg['fg']
        r = lg['pos'].get(p['pos'])
        m = 1.0
        if r and prm['def_k'] is not None:
            m = ((allow.get(p['pos'], 0) + prm['def_k'] * r) / (allow_n + prm['def_k'])) / r
            m = min(1 + prm['def_cap'], max(1 - prm['def_cap'], m))
        raw.append(s1); mults.append(m); out.append(a * m)
    tot = sum(out)
    if tot and prm['norm']:
        f = (prm['starter_sum'] / tot) ** prm['norm']
        if prm.get('up_only'):
            f = max(f, 1.0)
        out = [x * f for x in out]
    return out, mults, raw


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


def is_ft(play):
    return 'free throw' in play['type']['text'].lower()


# ---------- schedule ----------
def scoreboard(d):
    j = get(f'{B}/scoreboard?dates={d:%Y%m%d}') or {}
    out = []
    for e in j.get('events', []):
        c = e['competitions'][0]
        tm = {t['homeAway']: t['team']['abbreviation'] for t in c['competitors']}
        out.append({'id': e['id'], 'utc': e['date'], 'type': e['season'].get('type'), 'away': tm['away'],
                    'home': tm['home'], 'final': e['status']['type'].get('completed', False),
                    'state': e['status']['type']['name']})
    return out


def schedule(season, upto, log):
    """Every game of a season up to `upto` (inclusive). Past days of the last season are cached."""
    path = os.path.join(DATA, f'schedule_{season}.json')
    cache = load(path, {})
    a, b = SEASONS[season]
    days = [a + dt.timedelta(i) for i in range((min(b, upto) - a).days + 1)]
    todo = [d for d in days if d.isoformat() not in cache
            or (season == CUR and any(not e['final'] for e in cache[d.isoformat()]))]
    with ThreadPoolExecutor(10) as ex:
        for d, evs in zip(todo, ex.map(scoreboard, todo)):
            cache[d.isoformat()] = evs
    save(path, cache)
    log(f'{season}: schedule {len(days)} days ({len(todo)} fetched)')
    return cache


# ---------- one game ----------
def parse_game(ev):
    s = get(f"{B}/summary?event={ev['id']}")
    if not s:
        return None
    st = s['header']['competitions'][0]['status']['type']
    if not st.get('completed'):
        return None
    tm_by_id, team_of, nm, pl = {}, {}, {}, []
    for t in s['boxscore'].get('players', []):
        ab = t['team']['abbreviation']; tm_by_id[t['team']['id']] = ab
        stt = t['statistics'][0]; names = stt['names']
        for a in stt['athletes']:
            if not a.get('athlete', {}).get('id'):
                continue
            pid = a['athlete']['id']; team_of[pid] = ab; nm[pid] = a['athlete']['displayName']
            if a.get('didNotPlay') or not a.get('stats'):
                continue
            x = dict(zip(names, a['stats']))
            try:
                mins = int(x.get('MIN') or 0); pts = int(x.get('PTS') or 0)
                tpm = int((x.get('3PT') or '0-0').split('-')[0])
                fgm, fga = (int(v) for v in (x.get('FG') or '0-0').split('-'))
            except ValueError:
                continue
            pl.append([pid, ab, bool(a.get('starter')), mins, pts, tpm,
                       (a['athlete'].get('position') or {}).get('abbreviation', ''), fgm, fga])
    plays = s.get('plays', [])
    tip = None
    for p in plays:
        if p['period']['number'] == 1 and p['type']['text'].lower().startswith('jump'):
            parts = [q['athlete']['id'] for q in p.get('participants', [])]
            win = tm_by_id.get((p.get('team') or {}).get('id'))
            if len(parts) >= 2 and win:
                tip = {'j': [[parts[0], team_of.get(parts[0])], [parts[1], team_of.get(parts[1])]], 'w': win}
            break
    fb = fp = None; tfirst, tshot, tsm, tfd = {}, {}, {}, {}
    for p in plays:
        tid = tm_by_id.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not tid or not parts:
            continue
        if p.get('scoringPlay') and fp is None:
            fp = [parts[0], tid, p.get('scoreValue')]
        if p.get('shootingPlay') and not is_ft(p):
            if tid not in tshot:
                tshot[tid] = parts[0]; tsm[tid] = bool(p.get('scoringPlay'))
            if p.get('scoringPlay'):
                if tid not in tfirst:
                    tfirst[tid] = parts[0]
                    m = re.search(r'(\d+)-foot', p.get('text', ''))
                    tfd[tid] = int(m.group(1)) if m else 0   # shot distance in feet (0 = dunk / at the rim)
                if fb is None:
                    fb = [parts[0], tid, p.get('scoreValue')]
        if len(tfirst) == 2 and len(tshot) == 2 and fp:
            break
    hc = s['header']['competitions'][0]['competitors']
    sc = {c['homeAway']: (c['team']['abbreviation'], int(c.get('score') or 0)) for c in hc}
    return {'id': ev['id'], 'date': et(ev['utc']).date().isoformat(), 'type': ev['type'],
            'away': sc['away'][0], 'home': sc['home'][0], 'as': sc['away'][1], 'hs': sc['home'][1],
            'tip': tip, 'fb': fb, 'fp': fp, 'tf': tfirst, 'ts': tshot, 'tsm': tsm, 'tfd': tfd, 'pl': pl, 'v': 2,
            'nm': {p[0]: nm[p[0]] for p in pl} | ({j[0]: nm.get(j[0], '?') for j in tip['j']} if tip else {})}


def safe_parse_game(ev):
    try:
        return parse_game(ev)
    except Exception as e:
        print(f"  {ev['id']} parse error: {e!r}", file=sys.stderr)
        return None


def refresh(season, sched, today, log):
    path = os.path.join(DATA, f'games_{season}.json')
    games = load(path, {})
    evs = [e for d, es in sched.items() if d < today.isoformat() for e in es
           if e['type'] in (1, 2) and e['final'] and (e['id'] not in games or games[e['id']].get('v') != 2)]
    if season == LAST:
        evs = [e for e in evs if e['type'] == 2]
    log(f'{season}: {len(games)} cached, {len(evs)} to fetch')
    with ThreadPoolExecutor(10) as ex:
        for e, rec in zip(evs, ex.map(safe_parse_game, evs)):
            if rec:
                games[e['id']] = rec
            else:
                log(f"  {e['id']} not final or no summary, skipped")
    save(path, games)
    return games


# ---------- aggregates ----------
def zero():
    return {'gp': 0, 'gs': 0, 'fb': 0, 'fp': 0, 't1': 0, 'sh1': 0, 'sh1m': 0, 'tips': 0, 'tipw': 0, 'pts': 0, 'tpm': 0,
            'min': 0, 'fgm': 0, 'fga': 0, 'log': [], 'gs_by': {}}


def player_stats(games):
    P = {}
    for g in sorted(games.values(), key=lambda x: (x['date'], x['id'])):
        for pid, tm, st, mins, pts, tpm, pos, fgm, fga in g['pl']:
            s = P.setdefault(pid, zero() | {'tm': tm, 'pos': pos, 'nm': g['nm'].get(pid, '?')})
            s['gp'] += 1; s['pts'] += pts; s['tpm'] += tpm; s['min'] += mins; s['tm'] = tm; s['pos'] = pos or s['pos']
            s['fgm'] += fgm; s['fga'] += fga
            s['log'].append((g['date'], pts, tpm, st))
            if st:
                s['gs'] += 1; s['gs_by'][tm] = s['gs_by'].get(tm, 0) + 1
                s['fb'] += bool(g['fb'] and g['fb'][0] == pid)
                s['fp'] += bool(g['fp'] and g['fp'][0] == pid)
                s['t1'] += g['tf'].get(tm) == pid
                s['sh1'] += g['ts'].get(tm) == pid
                s['sh1m'] += g['ts'].get(tm) == pid and bool(g.get('tsm', {}).get(tm))
        if g['tip']:
            for pid, tm in g['tip']['j']:
                s = P.setdefault(pid, zero() | {'tm': tm, 'pos': '', 'nm': g['nm'].get(pid, '?')})
                s['tips'] += 1; s['tipw'] += g['tip']['w'] == tm
    return P


def team_stats(games):
    T = {}
    for g in games.values():
        first = g['fb'][1] if g['fb'] else None
        posof = {p[0]: p[6] for p in g['pl']}
        for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
            t = T.setdefault(tm, {'gp': 0, 'tips': 0, 'tipw': 0, 'first': 0, 'w_first': 0, 'jumpers': {}, 'last': '',
                                  'allow': {}, 'allow_n': 0})
            ps = posof.get(g['tf'].get(opp))   # position of the opponent who scored their first FG against tm
            if ps in POS:
                t['allow'][ps] = t['allow'].get(ps, 0) + 1; t['allow_n'] += 1
            t['gp'] += 1; t['first'] += first == tm; t['last'] = max(t['last'], g['date'])
            if g['tip']:
                t['tips'] += 1
                won = g['tip']['w'] == tm
                t['tipw'] += won; t['w_first'] += won and first == tm
                for pid, jt in g['tip']['j']:
                    if jt == tm:
                        t['jumpers'][pid] = t['jumpers'].get(pid, 0) + 1
    return T


def blend(hc, gc, hl, gl, w):
    den = w * gc + gl
    return (w * hc + hl) / den if den else None


def pct(x):
    return None if x is None else round(x, 3)


def american(p):
    if not p or p <= 0 or p >= 1:
        return '-'
    return f'+{round((1 - p) / p * 100)}' if p < 0.5 else f'-{round(p / (1 - p) * 100)}'


def build(start, log):
    os.makedirs(DATA, exist_ok=True)
    sched_cur = schedule(CUR, start + dt.timedelta(14), log)
    sched_last = schedule(LAST, SEASONS[LAST][1], log)
    reg_dates = sorted(d for d, es in sched_cur.items() if any(e['type'] == 2 for e in es))
    reg_started = bool(reg_dates) and reg_dates[0] <= start.isoformat()
    slate_day = None
    for d in sorted(sched_cur):
        if d >= start.isoformat() and any(e['type'] == 2 or (reg_started and e['type'] in (1, 2)) for e in sched_cur[d]):
            slate_day = d; break
    if not slate_day:
        slate_day = next((d for d in sorted(sched_cur) if d >= start.isoformat() and sched_cur[d]), start.isoformat())
    slate = dt.date.fromisoformat(slate_day)
    today = (dt.datetime.now(ET)).date()

    g_last = refresh(LAST, sched_last, today, log)
    g_cur_all = refresh(CUR, sched_cur, today, log)
    g_cur = {k: v for k, v in g_cur_all.items() if v['type'] == 2}
    g_pre = {k: v for k, v in g_cur_all.items() if v['type'] == 1}
    PL, PC, PP = player_stats(g_last), player_stats(g_cur), player_stats(g_pre)
    TL, TC, TP = team_stats(g_last), team_stats(g_cur), team_stats(g_pre)
    W = W_DEFAULT

    # current rosters and injuries
    teams = {t['team']['id']: t['team']['abbreviation'] for t in
             get(f'{B}/teams')['sports'][0]['leagues'][0]['teams']}
    roster = {}
    with ThreadPoolExecutor(8) as ex:
        for tid, r in zip(teams, ex.map(lambda i: get(f'{B}/teams/{i}/roster'), teams)):
            for a in (r or {}).get('athletes', []):
                roster[a['id']] = {'name': a['displayName'], 'tm': teams[tid],
                                   'pos': (a.get('position') or {}).get('abbreviation', '')}
    save(os.path.join(DATA, 'rosters.json'), roster)
    inj = {}
    for t in (get(f'{B}/injuries') or {}).get('injuries', []):
        for i in t.get('injuries', []):
            m = re.search(r'/id/(\d+)/', json.dumps(i['athlete'].get('links', [])))
            if m:
                inj[m.group(1)] = {'status': i.get('status', ''), 'note': i.get('shortComment', '')}
    save(os.path.join(DATA, 'injuries.json'), inj)

    def S(src, pid):
        return src.get(pid) or zero()

    # probable starters: regular-season starts this season (last 5 games) once it begins,
    # otherwise preseason starts plus each player's 2025-26 starter share
    def starter_score(pid):
        c, p, l = S(PC, pid), S(PP, pid), S(PL, pid)
        rc = sum(1 for x in c['log'][-5:] if x[3])
        return rc * 10 + sum(1 for x in p['log'] if x[3]) * 1.0 + (l['gs'] / max(l['gp'], 1)) * 3 + l['min'] / max(l['gp'], 1) / 12
    starters, healthy5 = {}, {}
    for pid, r in roster.items():
        healthy5.setdefault(r['tm'], []).append(pid)
        if (inj.get(pid) or {}).get('status', '').lower() in ('out', 'doubtful'):
            continue
        starters.setdefault(r['tm'], []).append(pid)
    for tm in starters:
        starters[tm] = sorted(starters[tm], key=lambda p: -starter_score(p))[:5]
    for tm in healthy5:   # who would start if everyone were healthy (for the injury ripple note)
        healthy5[tm] = sorted(healthy5[tm], key=lambda p: -starter_score(p))[:5]
    all_starters = [p for tm in sorted(starters) for p in starters[tm]]
    # players hurt (Out) who started a lot last season, listed but not in the probable five
    hurt = [pid for pid, r in roster.items() if (inj.get(pid) or {}).get('status', '').lower() == 'out'
            and S(PL, pid)['gs'] >= 30]

    # league rates
    tips = [g for g in g_last.values() if g['tip'] and g['fb']]
    a_first = sum(g['tip']['w'] == g['fb'][1] for g in tips) / len(tips)

    def jump_rate(pid):
        c, l = S(PC, pid), S(PL, pid)
        # shrink toward 50% with 6 pseudo tips
        return (W * c['tipw'] + l['tipw'] + 3) / (W * c['tips'] + l['tips'] + 6)

    def main_jumper(tm):
        # this season's games (preseason and regular) newest first: weights 3, 2, 1.5, then 1; regular season x2.
        # Last season's tips count 0.05 each for any team, so traded bigs carry over but current roles win.
        ok = lambda pid: (roster.get(pid, {}).get('tm') == tm
                          and (inj.get(pid) or {}).get('status', '').lower() not in ('out', 'doubtful'))
        cands = {}
        mine = sorted((g for g in g_cur_all.values() if g['tip'] and tm in (g['away'], g['home'])),
                      key=lambda g: g['date'], reverse=True)
        for i, g in enumerate(mine):
            for pid, jt in g['tip']['j']:
                if jt == tm and ok(pid):
                    wt = (3, 2, 1.5)[i] if i < 3 else 1
                    cands[pid] = cands.get(pid, 0) + wt * (2 if g['type'] == 2 else 1)
        for pid, r in roster.items():
            if r['tm'] == tm and ok(pid) and S(PL, pid)['tips']:
                cands[pid] = cands.get(pid, 0) + 0.05 * S(PL, pid)['tips']
        if not cands:   # tallest proxy: a starting center
            cs = [p for p in starters.get(tm, []) if roster[p]['pos'] == 'C'] or starters.get(tm, [])[:1]
            return cs[0] if cs else None
        return max(cands, key=cands.get)

    # the main jumper is almost always a starter: if the estimate left him out, he replaces the 5th man
    for tm in list(starters):
        j = main_jumper(tm)
        if j and j not in starters[tm]:
            starters[tm] = starters[tm][:4] + [j]
    all_starters = [p for tm in sorted(starters) for p in starters[tm]]

    def share(pid):   # v1 (old model): shrunk share of team first FGs
        c, l = S(PC, pid), S(PL, pid)
        return v1_share(W * c['t1'] + l['t1'], W * c['gs'] + l['gs'])

    def wcounts(pid):   # 26-27 weight ramps up with his starts for his current team (10/23 fix)
        c, l, tm = S(PC, pid), S(PL, pid), roster[pid]['tm']
        w = cur_weight(W, c['gs_by'].get(tm, 0))
        return ({k: w * c[k] + l[k] for k in ('gs', 't1', 'sh1', 'fgm', 'fga')}
                | {'pos': roster[pid]['pos'], 'n_starts': c['gs'] + l['gs']})

    lg_fgm = sum(x['fgm'] for x in PL.values()) + W * sum(x['fgm'] for x in PC.values())
    lg_fga = sum(x['fga'] for x in PL.values()) + W * sum(x['fga'] for x in PC.values())
    pos_n = {p: sum(t['allow'].get(p, 0) for t in TL.values()) + W * sum(t['allow'].get(p, 0) for t in TC.values())
             for p in POS}
    LG = {'fg': lg_fgm / lg_fga, 'pos': {p: pos_n[p] / sum(pos_n.values()) for p in POS}}

    def allow(tm):
        a, b = TL.get(tm, {}), TC.get(tm, {})
        return ({p: a.get('allow', {}).get(p, 0) + W * b.get('allow', {}).get(p, 0) for p in POS},
                a.get('allow_n', 0) + W * b.get('allow_n', 0))

    def fgpct(pid):
        x = wcounts(pid)
        return (x['fgm'] + V2['fg_k'] * LG['fg']) / (x['fga'] + V2['fg_k'])

    def team_v2(tm, opp):
        """v2 shares for tm's probable five against opp (opp=None: no defense term). pid -> (share, def mult)."""
        five = starters.get(tm, [])
        al, an = allow(opp) if opp else ({}, 0)
        sh, mu, _ = v2_shares([wcounts(p) for p in five], al, an, LG, V2 if opp else dict(V2, def_k=None))
        return {p: (a, m) for p, a, m in zip(five, sh, mu)}

    def ripple_note(tm):
        gone = [p for p in healthy5.get(tm, []) if p not in starters.get(tm, []) and share(p) >= 0.25
                and S(PL, p)['gs'] + S(PC, p)['gs'] >= 20]
        return ', '.join(f"{nm(p)} out ({round(100 * share(p))}% share spread to the rest)" for p in gone)

    # ---------- slate ----------
    slate_games = []
    for e in sched_cur.get(slate_day, []):
        if not reg_started and e['type'] != 2:
            continue
        ja, jh = main_jumper(e['away']), main_jumper(e['home'])
        ra, rh = (jump_rate(ja) if ja else .5), (jump_rate(jh) if jh else .5)
        p = ra * (1 - rh) / (ra * (1 - rh) + rh * (1 - ra))
        pf = p * a_first + (1 - p) * (1 - a_first)
        slate_games.append({**e, 'time': et(e['utc']).strftime('%-I:%M'), 'ja': ja, 'jh': jh, 'ptip': p, 'pfirst': pf})
    side = {}
    for g in slate_games:
        side[g['away']] = (g, '@', g['home'], g['pfirst'])
        side[g['home']] = (g, 'vs', g['away'], 1 - g['pfirst'])

    def nm(pid):
        return (roster.get(pid) or {}).get('name') or S(PL, pid).get('nm') or S(PP, pid).get('nm') or pid

    cands = []
    for tm, (g, at, opp, pteam) in side.items():
        tv = team_v2(tm, opp)
        for pid in starters.get(tm, []):
            st = (inj.get(pid) or {}).get('status', '')
            sh, mu = tv[pid]
            cands.append({'pid': pid, 'tm': tm, 'at': at, 'opp': opp, 'pteam': pteam, 'share': sh, 'p': pteam * sh,
                          'p1': pteam * share(pid), 'mult': mu, 'gid': g['id'], 'inj': st, 'rip': ripple_note(tm),
                          'time': g['time']})
    json.dump([{'player': nm(c['pid']), 'tm': c['tm'], 'opp': c['opp'], 'time': c['time'], 'p_v2': round(c['p'], 4),
                'p_v1': round(c['p1'], 4), 'fair_v2': american(c['p']), 'fair_v1': american(c['p1']),
                'def_mult': round(c['mult'], 3), 'ripple': c['rip'], 'inj': c['inj']}
               for c in sorted(cands, key=lambda c: (c['time'], c['gid'], -c['p']))],
              open(os.path.join(OUT, 'fb_candidates.json'), 'w'), indent=0)
    picks = []
    per_game = {}
    for c in sorted(cands, key=lambda c: -c['p']):
        if len([p for p in picks if p[0] == 'First basket']) >= 8:
            break
        if per_game.get(c['gid'], 0) >= 2:
            continue
        per_game[c['gid']] = per_game.get(c['gid'], 0) + 1
        l, cu = S(PL, c['pid']), S(PC, c['pid'])
        pos = roster[c['pid']]['pos']
        picks.append(['First basket', nm(c['pid']), f"{c['tm']} {c['at']} {c['opp']} {c['time']}",
                      f"Est {round(100 * c['p'])}% (fair {american(c['p'])}; old model {round(100 * c['p1'])}%): "
                      f"{c['tm']} scores first {round(100 * c['pteam'])}%; first FG {l['t1']}/{l['gs']} and first shot "
                      f"{l['sh1']}/{l['gs']} starts 25-26" + (f", {cu['t1']}/{cu['gs']} 26-27" if cu['gs'] else '')
                      + f", FG {round(100 * fgpct(c['pid']))}%; {c['opp']} vs {pos} x{c['mult']:.2f}"
                      + (f"; {c['rip']}" if c['rip'] else '') + (f"; {c['inj']}" if c['inj'] else ''),
                      f"Better than {american(c['p'])}"])
    for c in sorted(cands, key=lambda c: -c['share'])[:4]:
        l = S(PL, c['pid'])
        picks.append(['Team first basket', nm(c['pid']), f"{c['tm']} {c['at']} {c['opp']}",
                      f"Model share of {c['tm']}'s first FG {round(100 * c['share'])}% (old {round(100 * share(c['pid']))}%); "
                      f"raw 25-26 {l['t1']}/{l['gs']}, first shot {l['sh1']}/{l['gs']}, FG {round(100 * fgpct(c['pid']))}%"
                      + (f"; {c['rip']}" if c['rip'] else ''), f"Better than {american(c['share'])}"])

    def over_rate(pid, idx, k):
        lg = [x[idx] for x in S(PL, pid)['log'] if x[3]]
        cg = [x[idx] for x in S(PC, pid)['log'] if x[3]]
        return blend(sum(v > k for v in cg), len(cg), sum(v > k for v in lg), len(lg), W), len(lg) + len(cg)
    props = []
    for c in cands:
        for lab, idx, lines in (('points', 1, PTS_LINES), ('threes', 2, THREE_LINES)):
            for k in reversed(lines):
                r, n = over_rate(c['pid'], idx, k)
                if r and n >= 20 and r >= 0.70:
                    props.append((k / (5 if lab == 'points' else 0.4), r, lab, k, c)); break
    props.sort(key=lambda x: (-x[0], -x[1]))
    seen = set()
    for _, r, lab, k, c in props:
        if c['pid'] in seen or len(seen) >= 6:
            continue
        seen.add(c['pid'])
        lg = [x for x in S(PL, c['pid'])['log'] if x[3]][-5:]
        picks.append([f'Over {k} {lab}', nm(c['pid']), f"{c['tm']} {c['at']} {c['opp']}",
                      f"Over {k} in {round(100 * r)}% of starts (blend); last 5 starts 25-26: "
                      f"{' '.join(str(x[1 if lab == 'points' else 2]) for x in reversed(lg))}", f'Over {k}'])

    # ---------- grid ----------
    rows = []
    R = lambda *a: rows.append(list(a))
    nl, nc, npre = len(g_last), len(g_cur), len(g_pre)
    R(f'NBA props: first basket, tip-off, points, threes (as of {today.strftime("%-m/%-d")})')
    R('Legend', '26 = 2026-27 regular season so far, 25 = 2025-26 regular season, Pre = 2026-27 preseason (shown, not '
      'in the blend). First basket (FB) = first made field goal of the game (FanDuel rule; free throws do not count). '
      "Team 1st = scored his team's first FG. 1st shot = took his team's first FG attempt. Blend = each 26-27 game counts "
      'as many 25-26 games as the weight in B3. '
      + (f'Regular season starts {dt.date.fromisoformat(reg_dates[0]).strftime("%-m/%-d")}: until then this is 2025-26 data '
         f'plus {npre} preseason games, and players on new teams carry last season\'s numbers.' if not reg_started else
         f'{nc} 2026-27 games so far.') + ' Nothing here is guaranteed. Small stakes.')
    R('26-27 game weight', W, 'Input. Change it and the Blend columns update.')
    R()
    hdr_short = len(rows) + 1
    lab = 'Opening night' if (reg_dates and slate_day == reg_dates[0]) else 'Slate'
    R(f'{lab} {slate.strftime("%a %-m/%-d")}: shortlist (not guaranteed)')
    R('Bet', 'Player', 'Game', 'Why', 'Look for')
    for p in picks:
        R(*p)
    R('How picked', f'First basket = P(team scores first) x player share (model v2, 10/21). P(team scores first) comes from the '
      f'two main jumpers\' tip-win rates (log5) and the 25-26 league rate that the tip winner scores first ({round(100 * a_first)}%). '
      'Share = half his share of team first FGs + half his share of team first shots x (his FG% / league FG%), each shrunk '
      'toward 1 in 5; then x the opponent\'s rate of allowing the first FG to his position (G/F/C, shrunk hard, 0.85 to 1.15); '
      'then the probable five are rescaled to sum to 99%, so an Out starter\'s share goes to the rest in proportion. '
      'Backtest (936 games, Dec 25 to 10/20/26): log loss 2.283 vs 2.293 old, top pick 14.0% vs 13.9%; small but better. '
      'Fair odds are the break-even price; '
      'only bet when the book pays more. Points / threes = highest line with a 70%+ blended hit rate as a starter. '
      'Recheck starting lineups 30 minutes before tip. '
      'Opening night 10/20: the value longer shots hit (Collins +1000, Vassell +800) while the book favorites '
      '(Wembanyama, Embiid) missed, and Queta did not start. Lean to role starters priced well past fair, '
      'skip favorites priced under fair, and only bet a player once his start is confirmed.')
    R()
    R('Slate: tip-off matchups and injuries (ESPN)')
    R('Game (ET)', 'Away jumper (tip win%)', 'Home jumper (tip win%)', 'Away wins tip', 'Away scores first', 'Out / doubtful')
    for g in slate_games:
        def jt(pid):
            return f'{nm(pid)} ({round(100 * jump_rate(pid))}%)' if pid else '?'
        outs = []
        for tm in (g['away'], g['home']):
            ns = [nm(p) for p, r in roster.items() if r['tm'] == tm and (inj.get(p) or {}).get('status', '').lower() in ('out', 'doubtful')
                  and S(PL, p)['gp'] >= 30]
            if ns:
                outs.append(f"{tm}: {', '.join(ns[:4])}")
        R(f"{g['away']} @ {g['home']} {g['time']}", jt(g['ja']), jt(g['jh']), pct(g['ptip']), pct(g['pfirst']),
          '; '.join(outs) or 'none of note')
    tip_rng = (len(rows) - len(slate_games) + 1, len(rows))
    R()

    def onhdr(title, cols):
        R(title); R(*cols); return len(rows) + 1

    # A: first basket, probable starters
    s = onhdr('First basket: probable starters, all 30 teams (estimate from recent starts)',
              ['Player', 'Tm', 'Pos', 'GS 26', 'FB 26', 'Team 1st 26', '1st shot 26', 'GS 25', 'FB 25', 'Team 1st 25',
               '1st shot 25', 'Blend FB%', 'Blend team 1st%', 'Blend 1st shot%', 'Pre 26 (GS / FB / T1 / S1)',
               'First pts incl FT 25', 'Injury', 'FG% (blend, shrunk)', 'Model share v2 (no opp)'])
    rowsA = sorted(all_starters + hurt, key=lambda p: -share(p) * (TL.get(roster[p]['tm'], {}).get('first', 0) + 1))
    e = s + len(rowsA) - 1

    def arr(num):   # one ARRAYFORMULA per blend column, in the first data row (reads B3)
        return (f'=ARRAYFORMULA(IF($B$3*D{s}:D{e}+H{s}:H{e}=0,"-",($B$3*{num[0]}{s}:{num[0]}{e}+{num[1]}{s}:{num[1]}{e})'
                f'/($B$3*D{s}:D{e}+H{s}:H{e})))')
    v2_all = {}
    for tm in starters:
        v2_all.update({k: v[0] for k, v in team_v2(tm, None).items()})
    for i, pid in enumerate(rowsA):
        c, l, p = S(PC, pid), S(PL, pid), S(PP, pid)
        first = i == 0
        R(nm(pid), roster[pid]['tm'], roster[pid]['pos'], c['gs'], c['fb'], c['t1'], c['sh1'], l['gs'], l['fb'], l['t1'], l['sh1'],
          arr('EI') if first else None, arr('FJ') if first else None, arr('GK') if first else None,
          f"'{p['gs']} / {p['fb']} / {p['t1']} / {p['sh1']}", l['fp'], (inj.get(pid) or {}).get('status', ''),
          pct(fgpct(pid)), pct(v2_all.get(pid)) if pid in v2_all else '-')
    a_rng = (s, s + len(rowsA) - 1)
    R()
    # B: tip-off by team
    s = onhdr('Tip-off by team (opening jump ball only)',
              ['Team', 'Main jumper now', 'Jumper tips 26', 'Won 26', 'Jumper tips 25', 'Won 25', 'Jumper blend win%',
               'Team tips 25', 'Team won 25', 'Team tip% 25', 'Team scores 1st% 25', '1st when won tip 25',
               'Pre 26 tips won', 'Next game'])
    nxt = {}
    for d in sorted(sched_cur):
        if d >= slate_day:
            for e in sched_cur[d]:
                for tm, o, at in ((e['away'], e['home'], '@'), (e['home'], e['away'], 'vs')):
                    nxt.setdefault(tm, f"{dt.date.fromisoformat(d).strftime('%-m/%-d')} {at} {o}")
    trows = []
    for tm in sorted(set(teams.values())):
        j = main_jumper(tm); jc, jl = S(PC, j), S(PL, j)
        t, tp = TL.get(tm, {'tips': 0, 'tipw': 0, 'gp': 0, 'first': 0, 'w_first': 0}), TP.get(tm, {'tips': 0, 'tipw': 0})
        trows.append([tm, nm(j) if j else '?', jc['tips'], jc['tipw'], jl['tips'], jl['tipw'], None, t['tips'], t['tipw'],
                      pct(t['tipw'] / t['tips']) if t['tips'] else '-', pct(t['first'] / t['gp']) if t['gp'] else '-',
                      pct(t['w_first'] / t['tipw']) if t['tipw'] else '-', f"'{tp['tipw']} of {tp['tips']}", nxt.get(tm, '')])
    trows.sort(key=lambda x: -(x[9] if isinstance(x[9], float) else 0))
    e = s + len(trows) - 1
    for i, t in enumerate(trows):
        t[6] = (f'=ARRAYFORMULA(IF($B$3*C{s}:C{e}+E{s}:E{e}=0,"-",($B$3*D{s}:D{e}+F{s}:F{e})/($B$3*C{s}:C{e}+E{s}:E{e})))'
                if i == 0 else None)
        R(*t)
    b_rng = (s, s + len(trows) - 1)
    R()
    # C: points and threes
    s = onhdr('Points and threes as a starter (share of starts over each line, blended)',
              ['Player', 'Tm', 'PPG 26', 'PPG 25', 'Over 9.5', 'Over 14.5', 'Over 19.5', 'Over 24.5', '3PM/G 25',
               '3PM 1+', '3PM 2+', '3PM 3+', '3PM 4+', 'Last 5 pts (newest first)', 'Last 5 3PM', 'Injury'])
    crow = []
    for pid in all_starters:
        l, c = S(PL, pid), S(PC, pid)
        lg = [x for x in (l['log'] + c['log']) if x[3]]
        if len([x for x in l['log'] if x[3]]) + len([x for x in c['log'] if x[3]]) < 10:
            continue
        lg5 = sorted(lg, reverse=True)[:5]
        crow.append([nm(pid), roster[pid]['tm'], round(c['pts'] / c['gp'], 1) if c['gp'] else '-',
                     round(l['pts'] / l['gp'], 1) if l['gp'] else '-',
                     *[pct(over_rate(pid, 1, k)[0]) for k in PTS_LINES],
                     round(l['tpm'] / l['gp'], 1) if l['gp'] else '-',
                     *[pct(over_rate(pid, 2, k)[0]) for k in THREE_LINES],
                     "'" + ' '.join(str(x[1]) for x in lg5), "'" + ' '.join(str(x[2]) for x in lg5),
                     (inj.get(pid) or {}).get('status', '')])
    crow.sort(key=lambda x: -(x[3] if isinstance(x[3], float) else 0))
    for x in crow:
        R(*x)
    c_rng = (s, len(rows))
    R()
    # D: next games
    s = onhdr('Next NBA games (7 days from the slate)', ['Date', 'Time (ET)', 'Game', 'Type', 'Jumpers', 'Away wins tip (est)'])
    for d in sorted(sched_cur):
        if slate_day <= d <= (slate + dt.timedelta(6)).isoformat():
            for e in sched_cur[d]:
                ja, jh = main_jumper(e['away']), main_jumper(e['home'])
                ra, rh = (jump_rate(ja) if ja else .5), (jump_rate(jh) if jh else .5)
                R(dt.date.fromisoformat(d).strftime('%a %-m/%-d'), et(e['utc']).strftime('%-I:%M %p'),
                  f"{e['away']} @ {e['home']}", 'Regular' if e['type'] == 2 else 'Preseason',
                  f'{nm(ja) if ja else "?"} vs {nm(jh) if jh else "?"}', pct(ra * (1 - rh) / (ra * (1 - rh) + rh * (1 - ra))))
    d_rng = (s, len(rows))
    R()
    R('Sources', f'ESPN NBA scoreboard, game summaries (boxscore starters and play-by-play) for {nl} 2025-26 regular-season '
      f'games, {npre} 2026-27 preseason and {nc} 2026-27 regular-season games; ESPN rosters and injuries. '
      f'Pulled {dt.datetime.now(ET).strftime("%-m/%-d %-I:%M %p")} ET. Probable starters are an estimate from recent '
      'starts, not official lineups; the main jumper (most recent opening tips this season, weighted to the newest) is '
      'always put in the probable five. Rebuilt by analysis/nba/build_nba_tab.py; model check in analysis/nba/backtest_fb.py.')

    width = max(len(r) for r in rows)
    rows = [[('' if v is None else v) for v in r] + [''] * (width - len(r)) for r in rows]
    meta = {'short': hdr_short, 'n_picks': len(picks), 'tips': tip_rng, 'a': a_rng, 'b': b_rng, 'c': c_rng, 'd': d_rng,
            'width': width, 'rows': len(rows), 'slate': slate_day}
    os.makedirs(OUT, exist_ok=True)
    json.dump({'NBA': rows, 'meta': meta}, open(os.path.join(OUT, 'sheet_values.json'), 'w'))
    with open(os.path.join(OUT, 'nba_tab.csv'), 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    with open(os.path.join(OUT, 'shortlist.md'), 'w') as f:
        f.write(f'# NBA shortlist {slate_day} (not guaranteed)\n\nTip winner scores first {round(100 * a_first)}% (25-26).\n\n')
        for p in picks:
            f.write(f'- **{p[0]}: {p[1]}** ({p[2]}). {p[3]}\n')
        f.write('\n## Tip-off\n\n')
        for g in slate_games:
            f.write(f"- {g['away']} @ {g['home']} {g['time']} ET: {nm(g['ja'])} vs {nm(g['jh'])}; away wins tip "
                    f"{round(100 * g['ptip'])}%, away scores first {round(100 * g['pfirst'])}%\n")
    log(f'wrote {len(rows)} rows x {width} cols; picks {len(picks)}; meta {meta}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--date', help='start looking for the slate on this date, YYYY-MM-DD (default today ET)')
    a = ap.parse_args()
    d = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ET).date()
    build(d, lambda m: print(m, file=sys.stderr))


if __name__ == '__main__':
    main()
