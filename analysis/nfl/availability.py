#!/usr/bin/env python3
"""Player availability for the NFL TD models (backup fix, 11/28/26).

Before a game is scored, a skill player is UNAVAILABLE if any of these are true (every hit is logged with its reason):
  1. Injury status (ESPN injuries feed) is Out, Doubtful, IR, PUP, Suspended / Suspension or Reserve.
  2. He is on the official inactives list: the ESPN game roster (core API competitor roster, posted about 90 min
     before kickoff) lists him as did-not-play, or the roster is posted and he is not on it.
  3. He is not in the top N at his position on the team's current ESPN depth chart (RB 3, WR 5, TE 3). Catches healthy
     scratches and demotions (RJ Harvey fell to RB5 on 11/27). Skipped for a team whose depth chart did not load.
  4. Roster status (nflverse weekly roster): suspended (R33), reserve / IR (RES), practice squad (DEV, unless he is in
     the depth-chart top N, i.e. elevated), cut / released / retired / traded / inactive. A Questionable or Probable tag on
     the injuries feed overrides a stale RES (he was activated); nothing overrides a suspension.
  5. The suspension list data/suspensions.csv (name, team, season, first_week, last_week, note). Add rows by hand
     when a suspension is announced; ESPN sometimes lists them late or not at all.

QBs keep the old rule (expected starter only; first_td_week.py / td_model.live_qb).
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TOPN = {'RB': 3, 'WR': 5, 'TE': 3}
BAD_INJ = ('Out', 'Doubtful', 'Injured Reserve', 'IR', 'Physically Unable to Perform', 'PUP', 'Suspended', 'Suspension',
           'Reserve', 'Non-Football Injury', 'NFI')
OK_INJ = ('Questionable', 'Probable')
ROSTER_OUT = {'CUT': 'cut', 'RLS': 'released', 'RET': 'retired', 'TRD': 'traded', 'INA': 'inactive (roster)', 'EXE': 'exempt list'}
DEPTH_KEYS = {'rb': 'RB', 'fb': 'RB', 'wr': 'WR', 'te': 'TE', 'qb': 'QB'}


def _get(url, tries=3):
    import build_tracker as bt
    return bt.get(url, tries=tries)


def fetch_depth(team_ids, season=2026):
    """{team: {espn_id: (pos, rank)}} from the live ESPN depth chart. Rank = order within the position across slots
    (all WR1s by slot, then the WR2s, ...); FB listed after the RBs. Teams that fail to load are left out."""
    import build_tracker as bt
    out = {}
    for t, tid in team_ids.items():
        try:
            dc = _get(f'{bt.CORE}/seasons/{season}/teams/{tid}/depthcharts')
        except Exception as e:  # noqa
            print(f'depth chart {t}: {e}', file=sys.stderr)
            continue
        item = next((it for it in dc.get('items', []) if 'qb' in it.get('positions', {})), None)
        if not item:
            continue
        lists = {}
        for k, pos in DEPTH_KEYS.items():
            if k not in item['positions']:
                continue
            ath = item['positions'][k]['athletes']
            slots = {}
            for i, a in enumerate(ath):
                slots.setdefault(a.get('slot', 0), []).append(re.search(r'/athletes/(\d+)', a['athlete']['$ref']).group(1))
            # depth order: rank 1 of every slot (slot order), then rank 2, ...
            order = []
            for r in range(max((len(v) for v in slots.values()), default=0)):
                for s in sorted(slots):
                    if r < len(slots[s]):
                        order.append(slots[s][r])
            lists.setdefault(pos, [])
            lists[pos] += [x for x in order if x not in lists[pos]]
        d = {}
        for pos, ids in lists.items():
            for i, a in enumerate(ids, 1):
                if a not in d:
                    d[a] = (pos, i)
        out[t] = d
    return out


def depth_from_nflverse(rows, last):
    """Same shape as fetch_depth, keyed by gsis id, from raw/depth_<season>.csv rows of the latest date."""
    tmp = {}
    for r in rows:
        if r['dt'][:10] != last or r['pos_abb'] not in ('QB', 'RB', 'WR', 'TE', 'FB'):
            continue
        pos = 'RB' if r['pos_abb'] == 'FB' else r['pos_abb']
        key = (int(r['pos_rank'] or 9), r['pos_abb'] == 'FB', r['pos_slot'])
        t = tmp.setdefault(r['team'], {}).setdefault(pos, {})
        if r['gsis_id'] not in t or key < t[r['gsis_id']]:
            t[r['gsis_id']] = key
    out = {}
    for team, bypos in tmp.items():
        d = {}
        for pos, ids in bypos.items():
            for i, g in enumerate(sorted(ids, key=lambda g: ids[g]), 1):
                d[g] = (pos, i)
        out[team] = d
    return out


def fetch_game_roster(event_id, team_id):
    """{espn_id: 'active' | 'inactive'} once ESPN posts the game roster (about 90 min before kickoff), else None."""
    import build_tracker as bt
    try:
        d = _get(f'{bt.CORE}/events/{event_id}/competitions/{event_id}/competitors/{team_id}/roster', tries=1)
    except Exception:  # noqa  (404 until posted)
        return None
    ent = d.get('entries', [])
    if len(ent) < 40:
        return None
    return {str(e['playerId']): ('inactive' if e.get('didNotPlay') else 'active') for e in ent}


def load_suspensions(season, week):
    """{(name lower, team): note} for suspensions covering this week, from data/suspensions.csv."""
    p = os.path.join(HERE, 'data', 'suspensions.csv')
    out = {}
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p)):
        try:
            if int(r['season']) == season and int(r['first_week']) <= week <= int(r['last_week'] or 99):
                out[(r['name'].strip().lower(), r['team'].strip())] = r.get('note', '') or 'suspended'
        except (KeyError, ValueError):
            continue
    return out


def check(name, team, pos, inj_status='', roster=None, depth=None, depth_loaded=False, game_roster=None, espn_id=None,
          suspensions=None):
    """Return a list of reasons he is unavailable (empty = available).
    roster: nflverse roster row (status, status_description_abbr) or None. depth: (pos on the chart, rank) or None if not
    listed; the chart's position wins when it differs from the roster's. game_roster: {espn_id: 'active'|'inactive'} or None."""
    if depth and depth[0] in TOPN:
        pos = depth[0]
    depth_rank = depth[1] if depth else None
    why = []
    s = inj_status or ''
    if s and not s.startswith(OK_INJ) and any(b.lower() in s.lower() for b in BAD_INJ):
        why.append(f'injury report: {s}')
    q_tag = any(s.startswith(x) for x in OK_INJ)
    g = game_roster.get(str(espn_id)) if (game_roster is not None and espn_id) else None
    if g == 'active':
        q_tag = True          # on the game-day active list: a stale reserve / practice-squad tag does not count
    if game_roster is not None and espn_id:
        if g == 'inactive':
            why.append('inactive (game-day list)')
        elif g is None:
            why.append('not on game-day roster')
    n = TOPN.get(pos)
    if n and depth_loaded:
        if depth_rank is None:
            why.append(f'not on {team} depth chart at {pos}')
        elif depth_rank > n:
            why.append(f'depth chart {pos}{depth_rank} (top {n} only)')
    if roster:
        st, ab = roster.get('status', ''), roster.get('status_description_abbr', '')
        if ab == 'R33':
            why.append('roster: suspended (R33)')
        elif st == 'RES' and ab == 'R48':
            pass              # IR return window: the injuries feed / game-day list decide (see first_td_week: marked Q)
        elif st == 'RES' and not q_tag:
            why.append(f'roster: reserve list ({ab or "RES"})')
        elif st == 'DEV' and not q_tag and not (depth_rank and n and depth_rank <= n):
            why.append(f'roster: practice squad ({ab or "DEV"})')
        elif st in ROSTER_OUT:
            why.append(f'roster: {ROSTER_OUT[st]}')
        if roster.get('team') and roster['team'] != team:
            why.append(f"roster: now on {roster['team']}")
    if suspensions and (name.lower(), team) in suspensions:
        why.append(f'suspension list: {suspensions[(name.lower(), team)]}')
    return why
