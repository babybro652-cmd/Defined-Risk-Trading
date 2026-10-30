#!/usr/bin/env python3
"""Daily parlay builder and StarTool "agree" flag (10/30/26, Tim approved; report
analysis/reports/2026-10-30-picks-vs-startool.md).

Parlays use ONLY the categories that beat their price season to date:
  NBA 3+ threes, NHL 3+ SOG, NFL receptions, UCL / soccer 1+ shot on target.
Never NBA points overs (singles only, at a higher alt line), never first basket / first goal / anytime goal.

Each sport's build writes its legs to analysis/<sport>/out/parlay_legs.json:
  {"date": "YYYY-MM-DD", "sport": "NBA", "legs": [{"player", "team", "game", "market", "p", "note"}]}
NBA and NHL builds write theirs automatically. NFL receptions have no model build: write the file by hand
(same format, market "4+ receptions" etc., p = the blended hit rate) and rerun this script. UCL writes its
1+ SOT legs from build_ucl_tab.py.

Then `write_sections(date)` (called at the end of the NBA and NHL builds, or run by hand)
rewrites one combined "## Parlays" section in analysis/nba/out/shortlist.md and analysis/nhl/out/shortlist.md.

  python3 analysis/parlays.py 2026-10-30

Rules: 2 or 3 legs, legs from different games when possible (a same-game pair is marked correlated and its fair
price is still the plain product, so it is optimistic), each leg used at most twice, leg chance 55% to 88%.
Fair odds = product of leg chances. Minimum FanDuel price = 10% cushion (fair chance / 1.1). Stake $0.10 to $0.20.
"""
import itertools, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SPORTS = ('nba', 'nhl', 'nfl', 'ucl')
ALLOWED = {'NBA': ('3+ threes',), 'NHL': ('3+ SOG',), 'NFL': ('receptions',), 'UCL': ('1+ shot on target',)}
P_MIN, P_MAX, CUSHION = 0.55, 0.88, 1.10
BEGIN, END = '<!-- parlays:begin -->', '<!-- parlays:end -->'
STARTOOL = {'nba': os.path.join(HERE, 'nba', 'out', 'startool', 'star_bomb.txt'),
            'nhl': os.path.join(HERE, 'nhl', 'out', 'startool', 'star_bomb.txt')}


def american(p):
    if not p or p <= 0 or p >= 1:
        return '-'
    return f'+{round((1 - p) / p * 100)}' if p < 0.5 else f'-{round(p / (1 - p) * 100)}'


def allowed(sport, market):
    return any(a in market for a in ALLOWED.get(sport, ())) and 'point' not in market.lower()


def write_legs(sport_dir, date, sport, legs):
    path = os.path.join(HERE, sport_dir, 'out', 'parlay_legs.json')
    legs = [x for x in legs if allowed(sport, x['market'])]
    json.dump({'date': date, 'sport': sport, 'legs': legs}, open(path, 'w'), indent=1)


def load_legs(date):
    out = {}
    for s in SPORTS:
        path = os.path.join(HERE, s, 'out', 'parlay_legs.json')
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        dates = d['date'] if isinstance(d['date'], list) else [d['date']]
        if date not in dates:
            continue
        legs = [x for x in d['legs'] if allowed(d['sport'], x['market']) and P_MIN <= x['p'] <= P_MAX]
        if legs:
            out[d['sport']] = sorted(legs, key=lambda x: -x['p'])[:8]
    return out


def build_parlays(legs, n2=3, n3=2):
    """Best 2-leg and 3-leg combos by fair chance, different games first, each leg used at most twice."""
    res, used = [], {}
    for size, cap in ((2, n2), (3, n3)):
        combos = []
        for c in itertools.combinations(legs, size):
            games = {x['game'] for x in c}
            if len({x['player'] for x in c}) < size:
                continue
            p = 1.0
            for x in c:
                p *= x['p']
            combos.append((len(games) < size, -p, c, p))
        combos.sort(key=lambda t: (t[0], t[1]))
        k = 0
        for same, _, c, p in combos:
            if k >= cap:
                break
            if any(used.get(x['player'], 0) >= 2 for x in c):
                continue
            for x in c:   # cross-game combos sort first, so a same-game one is used only when they run out
                used[x['player']] = used.get(x['player'], 0) + 1
            res.append({'legs': c, 'p': p, 'same_game': same})
            k += 1
    return res


def section(date):
    by_sport = load_legs(date)
    L = [BEGIN, f'## Parlays {date} (2-3 legs, $0.10 to $0.20)', '',
         'Only categories that beat their price season to date: NBA 3+ threes, NHL 3+ SOG, NFL receptions, '
         'soccer 1+ shot on target. No points overs, no first basket / first goal / anytime goal legs. '
         'Fair = product of the leg chances (no correlation boost). Take only at the minimum price or longer '
         '(fair with a 10% cushion). Legs from the same game are correlated and marked.', '']
    if not by_sport:
        L.append('- No qualifying legs today.')
    for sport, legs in by_sport.items():
        L.append(f'### {sport}')
        pars = build_parlays(legs)
        if not pars:
            L.append('- Not enough qualifying legs.')
        for i, par in enumerate(pars, 1):
            p = par['p']
            legs_txt = ' + '.join(f"{x['player']} {x['market']} ({round(100 * x['p'])}%, {x['game']})" for x in par['legs'])
            L.append(f"- **{len(par['legs'])}-leg #{i}:** {legs_txt}. Fair {american(p)} ({100 * p:.0f}%); "
                     f"take {american(p / CUSHION)} or longer"
                     + ('; same game, correlated, fair price is optimistic' if par['same_game'] else '') + '.')
        L.append('')
    L.append(END)
    return '\n'.join(L) + '\n'


def write_sections(date, targets=('nba', 'nhl')):
    sec = section(date)
    for t in targets:
        path = os.path.join(HERE, t, 'out', 'shortlist.md')
        if not os.path.exists(path):
            continue
        txt = open(path).read()
        txt = re.sub(re.escape(BEGIN) + '.*?' + re.escape(END) + r'\n?', '', txt, flags=re.S).rstrip('\n') + '\n\n'
        open(path, 'w').write(txt + sec)
    return sec


# ---------- StarTool agree flag (no blend: Tim rejected it 10/30) ----------
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|iii|ii)\b', '', s)
    return re.sub(r'[^a-z]', '', s)


def same_name(full, card):
    """Card names can be full ("Tyler Herro"), last only ("Stamkos") or initial + last ("B. Tkachuk")."""
    if norm(full) == norm(card):
        return True
    f, c = full.replace('.', ' ').split(), card.replace('.', ' ').split()
    if not f or not c:
        return False
    fl = [x for x in f if norm(x)]
    fl = fl[:-1] if len(fl) > 2 and norm(fl[-1]) == '' else fl
    last_f = norm(' '.join(fl[1:])) if len(fl) > 1 else norm(fl[0])
    last_c = norm(' '.join(c[1:])) if len(c) > 1 else norm(c[0])
    if len(c) == 1:
        return norm(c[0]) in (last_f, norm(fl[-1]))
    if len(c[0]) == 1:   # initial + last name
        return last_c in (last_f, norm(fl[-1])) and norm(fl[0])[:1] == c[0].lower()
    return False


def startool_lines(sport, date):
    """star_bomb.txt lines: date|AWAY @ HOME|star1,star2|bomb1,bomb2 (as printed on the card)."""
    path = STARTOOL[sport]
    if not os.path.exists(path):
        return {}
    out = {}
    for ln in open(path):
        parts = [x.strip() for x in ln.strip().split('|')]
        if len(parts) < 4 or parts[0] != date:
            continue
        teams = frozenset(t.strip().upper() for t in parts[1].split('@'))
        out[teams] = {'stars': [x for x in parts[2].split(',') if x], 'bombs': [x for x in parts[3].split(',') if x]}
    return out


def agree_flag(sport, date, away, home, our_top):
    """Returns a short text: 'agree (StarTool star)', 'agree (StarTool bomb)', 'differs (StarTool star X / Y)',
    or '' when no card is saved for the game."""
    st = startool_lines(sport, date).get(frozenset((away.upper(), home.upper())))
    if not st:
        return ''
    if any(same_name(our_top, x) for x in st['stars']):
        return 'agree (StarTool star)'
    if any(same_name(our_top, x) for x in st['bombs']):
        return 'agree (StarTool bomb)'
    return f"differs (StarTool stars {', '.join(st['stars'])}; bombs {', '.join(st['bombs'])})"


if __name__ == '__main__':
    print(write_sections(sys.argv[1]))
