"""First shot / first score per game, NBA and NHL, for grading.

Usage: python3 analysis/first_events.py 2026-10-22 [nba|nhl|both]

Pulls finished games for the date (ET) and appends one row per game to
analysis/first_events/log.csv (re-running a date replaces that date's rows):

NBA (ESPN play-by-play): first field goal attempt of the game (shooter, made or
missed), each team's first FGA, first basket (first made FG, how books grade it)
and first points (any score, free throws count).
NHL (NHL API play-by-play): first shot on goal of the game, each team's first
SOG, first shot attempt of any kind (missed and blocked count), first goal.
"""
import csv
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'first_events', 'log.csv')
COLS = ['date', 'sport', 'game', 'first_shot', 'first_shot_result', 'away_first_shot',
        'home_first_shot', 'first_attempt_any', 'first_score', 'first_points_any', 'note']


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def nba(date):
    ymd = date.replace('-', '')
    sb = get(f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={ymd}')
    rows = []
    for ev in sb.get('events', []):
        if ev['status']['type']['name'] != 'STATUS_FINAL':
            continue
        g = get(f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={ev['id']}")
        comp = ev['competitions'][0]['competitors']
        team_abbr = {c['team']['id']: c['team']['abbreviation'] for c in comp}
        home = next(c['team']['id'] for c in comp if c['homeAway'] == 'home')
        away = next(c['team']['id'] for c in comp if c['homeAway'] == 'away')
        names = {}
        for t in g.get('boxscore', {}).get('players', []):
            for st in t.get('statistics', []):
                for a in st.get('athletes', []):
                    names[a['athlete']['id']] = a['athlete']['displayName']

        def who(p):
            parts = p.get('participants') or []
            pid = parts[0]['athlete']['id'] if parts else None
            return f"{names.get(pid, p['text'].split(' makes')[0].split(' misses')[0])} ({team_abbr.get(p['team']['id'], '?')})"

        fga = [p for p in g.get('plays', []) if p.get('shootingPlay') and 'Free Throw' not in p['type']['text']]
        pts = [p for p in g.get('plays', []) if p.get('scoringPlay')]
        first = fga[0] if fga else None
        team_first = {tid: next((p for p in fga if p['team']['id'] == tid), None) for tid in (away, home)}
        made = next((p for p in fga if p.get('scoringPlay')), None)
        rows.append({
            'date': date, 'sport': 'NBA', 'game': ev['shortName'],
            'first_shot': who(first) if first else '',
            'first_shot_result': ('made' if first.get('scoringPlay') else 'missed') if first else '',
            'away_first_shot': who(team_first[away]) + (' made' if team_first[away].get('scoringPlay') else ' missed') if team_first[away] else '',
            'home_first_shot': who(team_first[home]) + (' made' if team_first[home].get('scoringPlay') else ' missed') if team_first[home] else '',
            'first_attempt_any': '',
            'first_score': who(made) if made else '',
            'first_points_any': who(pts[0]) if pts else '',
            'note': 'first_score = first made FG (first basket)',
        })
    return rows


def nhl(date):
    sb = get(f'https://api-web.nhle.com/v1/score/{date}')
    rows = []
    for gm in sb.get('games', []):
        if gm.get('gameState') not in ('OFF', 'FINAL'):
            continue
        d = get(f"https://api-web.nhle.com/v1/gamecenter/{gm['id']}/play-by-play")
        abbr = {d['awayTeam']['id']: d['awayTeam']['abbrev'], d['homeTeam']['id']: d['homeTeam']['abbrev']}
        ppl = {r['playerId']: (f"{r['firstName']['default']} {r['lastName']['default']}", r['teamId'])
               for r in d.get('rosterSpots', [])}

        def who(pid):
            n, t = ppl.get(pid, (str(pid), None))
            return f'{n} ({abbr.get(t, "?")})'

        def shooter(p):
            x = p.get('details', {})
            return x.get('shootingPlayerId') or x.get('scoringPlayerId')

        def when(p):
            return f"P{p['periodDescriptor']['number']} {p.get('timeInPeriod', '')}"

        plays = [p for p in d['plays'] if p.get('periodDescriptor', {}).get('periodType') != 'SO']
        sog = [p for p in plays if p['typeDescKey'] in ('shot-on-goal', 'goal')]
        att = [p for p in plays if p['typeDescKey'] in ('shot-on-goal', 'goal', 'missed-shot', 'blocked-shot')]
        goals = [p for p in plays if p['typeDescKey'] == 'goal']

        def team_first(tid):
            p = next((p for p in sog if ppl.get(shooter(p), (0, None))[1] == tid), None)
            return f'{who(shooter(p))} {when(p)}' if p else ''

        f = sog[0] if sog else None
        rows.append({
            'date': date, 'sport': 'NHL', 'game': f"{abbr[d['awayTeam']['id']]} @ {abbr[d['homeTeam']['id']]}",
            'first_shot': f'{who(shooter(f))} {when(f)}' if f else '',
            'first_shot_result': ('goal' if f['typeDescKey'] == 'goal' else 'saved') if f else '',
            'away_first_shot': team_first(d['awayTeam']['id']),
            'home_first_shot': team_first(d['homeTeam']['id']),
            'first_attempt_any': f"{who(shooter(att[0]))} {when(att[0])} ({att[0]['typeDescKey']})" if att else '',
            'first_score': f'{who(shooter(goals[0]))} {when(goals[0])}' if goals else 'no goal',
            'first_points_any': '',
            'note': 'first_shot = first shot on goal; shootout excluded',
        })
    return rows


def main():
    date = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else 'both'
    new = []
    if which in ('nba', 'both'):
        new += nba(date)
    if which in ('nhl', 'both'):
        new += nhl(date)
    sports = {r['sport'] for r in new}
    old = []
    if os.path.exists(LOG):
        with open(LOG) as fh:
            old = [r for r in csv.DictReader(fh) if not (r['date'] == date and r['sport'] in sports)]
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(sorted(old + new, key=lambda r: (r['date'], r['sport'], r['game'])))
    for r in new:
        print(f"{r['sport']} {r['game']}: first shot {r['first_shot']} {r['first_shot_result']} | "
              f"{r['away_first_shot']} / {r['home_first_shot']} | first score {r['first_score']}")


if __name__ == '__main__':
    main()
