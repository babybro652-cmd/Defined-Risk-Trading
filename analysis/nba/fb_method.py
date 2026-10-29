#!/usr/bin/env python3
"""First basket METHOD (10/29/26): how the first points / first basket are scored.

Methods (from the ESPN play type text):
  rim = dunk or layup (also tip-ins, putbacks, finger rolls, alley-oops)
  j2  = any other 2-pointer (jump shots, floaters, hooks, fadeaways)
  3   = 3-pointer
  ft  = free throw (only in the "first points" market; FanDuel first basket is field goals only)
Book rules vary: some group hooks or floaters with layups. We count hooks and floaters as j2.

Data: one ESPN summary call per game, cached in data/methods_<season>.json (game id -> record):
  fpm  method of the game's first points (incl FT); fbm  method of the first made FG
  tpm  {team: method of that team's first points}; tfm {team: method of its first FG}
  tf   {team: pid of its first FG}; mk {pid: [rim, j2, 3] made FGs in the game}

Model (see README "First basket method"):
  Game market: P(method) = sum over teams of P(team scores first) x P(method | team's first score),
    where P(method | team) = league rate x offense ratio x opponent defense ratio, each team rate shrunk
    toward the league with K_TEAM pseudo games, then renormalized.
  Player prop: P(player first basket) x P(method | he scores first). P(method | he scores first) =
    his team-first FG methods (counts) shrunk with K_PLAYER pseudo games toward a prior = position
    first-FG method mix x (his made-FG mix / position made-FG mix), his made mix shrunk toward the
    position with K_MIX pseudo makes.

Usage:
  python3 analysis/nba/fb_method.py --backfill        # fill the cache for both seasons
  python3 analysis/nba/fb_method.py --base            # league base rates and the player-model check
"""
import argparse, json, math, os, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
sys.path.insert(0, HERE)
METHODS = ('rim', 'j2', '3')
METHODS_FT = ('rim', 'j2', '3', 'ft')
LABEL = {'rim': 'Dunk/layup', 'j2': 'Other 2 (jumper, floater, hook)', '3': '3-pointer', 'ft': 'Free throw'}
SHORT = {'rim': 'Dunk/layup', 'j2': '2pt jumper', '3': '3-pointer', 'ft': 'Free throw'}
# knobs fit with --base (fit on 25-26 before 2/1/26, scored on the rest plus 26-27; see README)
K_TEAM = 80      # team offense / defense method rates shrunk toward league with 80 pseudo games
K_PLAYER = 40    # player's own first-FG methods shrunk toward his prior with 40 pseudo first FGs
K_MIX = 10       # player's made-FG mix shrunk toward his position with 10 pseudo makes
RIM_WORDS = ('dunk', 'layup', 'tip', 'putback', 'finger roll', 'alley oop')


def classify(p):
    t = (p.get('type') or {}).get('text', '').lower()
    if 'free throw' in t:
        return 'ft'
    if p.get('scoreValue') == 3 or p.get('pointsAttempted') == 3 or 'three point' in p.get('text', '').lower():
        return '3'
    if any(w in t for w in RIM_WORDS):
        return 'rim'
    return 'j2'


def parse(gid):
    import build_nba_tab as bt
    s = bt.get(f'{bt.B}/summary?event={gid}')
    if not s or not s['header']['competitions'][0]['status']['type'].get('completed'):
        return None
    tm = {t['team']['id']: t['team']['abbreviation'] for t in s['boxscore'].get('players', [])}
    rec = {'fpm': None, 'fbm': None, 'tpm': {}, 'tfm': {}, 'tf': {}, 'mk': {}}
    for p in s.get('plays', []):
        t = tm.get((p.get('team') or {}).get('id'))
        parts = [q['athlete']['id'] for q in p.get('participants', [])]
        if not t or not parts or not p.get('scoringPlay') or not p.get('shootingPlay', True):
            continue
        m = classify(p)
        if rec['fpm'] is None:
            rec['fpm'] = m
        rec['tpm'].setdefault(t, m)
        if m != 'ft':
            if rec['fbm'] is None:
                rec['fbm'] = m
            if t not in rec['tfm']:
                rec['tfm'][t] = m; rec['tf'][t] = parts[0]
            mk = rec['mk'].setdefault(parts[0], [0, 0, 0])
            mk[METHODS.index(m)] += 1
    return rec


def cache(season, gids, log=lambda m: print(m, file=sys.stderr)):
    import build_nba_tab as bt
    path = os.path.join(DATA, f'methods_{season}.json')
    c = bt.load(path, {})
    todo = [g for g in gids if g not in c]
    if todo:
        def safe(g):
            try:
                return parse(g)
            except Exception as e:
                log(f'  method {g}: {e!r}')
                return None
        with ThreadPoolExecutor(10) as ex:
            for g, r in zip(todo, ex.map(safe, todo)):
                if r:
                    c[g] = r
        bt.save(path, c)
    log(f'{season}: methods {len(c)} cached ({len(todo)} fetched)')
    return c


def norm(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()} if s else d


class Model:
    """Built from the main game caches (for positions and 26-27 weight) plus the method caches."""

    def __init__(self, seasons, W=3):
        # seasons: list of (games dict, methods dict, weight)
        self.lg = {m: 0.0 for m in METHODS_FT}          # team first points (incl FT)
        self.lgfb = {m: 0.0 for m in METHODS}           # team first FG
        self.off, self.dfn = {}, {}                     # team -> {m: weighted count, 'n': games}
        self.off_fg, self.dfn_fg = {}, {}
        self.pfirst, self.pmix = {}, {}                 # pid -> {m: count}
        self.posfirst = {p: {m: 0.0 for m in METHODS} for p in 'GFC'}
        self.posmix = {p: {m: 0.0 for m in METHODS} for p in 'GFC'}
        self.game_fp = {m: 0 for m in METHODS_FT}; self.game_fb = {m: 0 for m in METHODS}; self.n_games = 0
        self.raw = {}                                   # season label -> counts for the report
        for label, games, meth, w in seasons:
            r = self.raw.setdefault(label, {'fp': {m: 0 for m in METHODS_FT}, 'fb': {m: 0 for m in METHODS},
                                            'tp': {m: 0 for m in METHODS_FT}, 'n': 0})
            for gid, g in games.items():
                x = meth.get(gid)
                if not x or not x['fpm']:
                    continue
                pos = {p[0]: p[6] for p in g['pl']}
                r['n'] += 1; r['fp'][x['fpm']] += 1
                if x['fbm']:
                    r['fb'][x['fbm']] += 1
                for t, o in ((g['away'], g['home']), (g['home'], g['away'])):
                    if t in x['tpm']:
                        m = x['tpm'][t]; r['tp'][m] += 1
                        self.lg[m] += w
                        for D, k in ((self.off, t), (self.dfn, o)):
                            e = D.setdefault(k, {mm: 0.0 for mm in METHODS_FT} | {'n': 0.0})
                            e[m] += w; e['n'] += w
                    if t in x['tfm']:
                        m = x['tfm'][t]; self.lgfb[m] += w
                        for D, k in ((self.off_fg, t), (self.dfn_fg, o)):
                            e = D.setdefault(k, {mm: 0.0 for mm in METHODS} | {'n': 0.0})
                            e[m] += w; e['n'] += w
                        pid = x['tf'][t]
                        self.pfirst.setdefault(pid, {mm: 0.0 for mm in METHODS})[m] += w
                        ps = pos.get(pid, '')[:1]
                        if ps in self.posfirst:
                            self.posfirst[ps][m] += w
                for pid, mk in x['mk'].items():
                    e = self.pmix.setdefault(pid, {mm: 0.0 for mm in METHODS})
                    ps = pos.get(pid, '')[:1]
                    for i, m in enumerate(METHODS):
                        e[m] += w * mk[i]
                        if ps in self.posmix:
                            self.posmix[ps][m] += w * mk[i]
        self.lg, self.lgfb = norm(self.lg), norm(self.lgfb)
        self.posfirst = {p: norm(v) for p, v in self.posfirst.items()}
        self.posmix = {p: norm(v) for p, v in self.posmix.items()}

    def team_split(self, tm, opp, fg_only=False):
        lg = self.lgfb if fg_only else self.lg
        O, D = (self.off_fg, self.dfn_fg) if fg_only else (self.off, self.dfn)
        o, d = O.get(tm, {'n': 0}), D.get(opp, {'n': 0})
        out = {}
        for m, r in lg.items():
            ro = (o.get(m, 0) + K_TEAM * r) / (o['n'] + K_TEAM)
            rd = (d.get(m, 0) + K_TEAM * r) / (d['n'] + K_TEAM)
            out[m] = r * (ro / r) * (rd / r)
        return norm(out)

    def game_split(self, away, home, p_away_first, fg_only=False):
        a, h = self.team_split(away, home, fg_only), self.team_split(home, away, fg_only)
        return {m: p_away_first * a[m] + (1 - p_away_first) * h[m] for m in a}

    def player_split(self, pid, pos):
        ps = (pos or 'F')[:1]
        ps = ps if ps in self.posfirst else 'F'
        mix = self.pmix.get(pid, {m: 0 for m in METHODS}); n_mix = sum(mix.values())
        sm = {m: (mix[m] + K_MIX * self.posmix[ps][m]) / (n_mix + K_MIX) for m in METHODS}
        prior = norm({m: self.posfirst[ps][m] * sm[m] / self.posmix[ps][m] for m in METHODS})
        f = self.pfirst.get(pid, {m: 0 for m in METHODS}); n = sum(f.values())
        post = {m: (f[m] + K_PLAYER * prior[m]) / (n + K_PLAYER) for m in METHODS}
        return post, n, n_mix, sm


def load_all(W=3):
    import build_nba_tab as bt
    out = []
    for season, w in ((bt.LAST, 1), (bt.CUR, W)):
        games = {k: v for k, v in bt.load(os.path.join(DATA, f'games_{season}.json'), {}).items() if v['type'] == 2}
        out.append((season, games, cache(season, list(games)), w))
    return out


def check(seasons):
    """Player method check: fit on 25-26 games before 2/1/26, score team-first FG methods after (and 26-27)."""
    (l1, g1, m1, _), (l2, g2, m2, _) = seasons
    cut = '2026-02-01'
    tr = {k: v for k, v in g1.items() if v['date'] < cut}
    te = [(g, m1[k]) for k, g in g1.items() if g['date'] >= cut and k in m1] + [(g, m2[k]) for k, g in g2.items() if k in m2]
    M = Model([('train', tr, m1, 1)])
    res = {'league': 0.0, 'position': 0.0, 'mix prior': 0.0, 'model': 0.0}; n = 0
    for g, x in te:
        pos = {p[0]: p[6] for p in g['pl']}
        for t, m in x['tfm'].items():
            pid = x['tf'][t]; ps = (pos.get(pid) or 'F')[:1]; ps = ps if ps in M.posfirst else 'F'
            post, nf, nm_, sm = M.player_split(pid, ps)
            prior = norm({k: M.posfirst[ps][k] * sm[k] / M.posmix[ps][k] for k in METHODS})
            for key, d in (('league', M.lgfb), ('position', M.posfirst[ps]), ('mix prior', prior), ('model', post)):
                res[key] -= math.log(max(d[m], 1e-6))
            n += 1
    return {k: round(v / n, 4) for k, v in res.items()}, n


def check_team(seasons):
    """Team method check, same split: team first points (incl FT) and team first FG, model vs league rate."""
    (l1, g1, m1, _), (l2, g2, m2, _) = seasons
    cut = '2026-02-01'
    tr = {k: v for k, v in g1.items() if v['date'] < cut}
    te = [(g, m1[k]) for k, g in g1.items() if g['date'] >= cut and k in m1] + [(g, m2[k]) for k, g in g2.items() if k in m2]
    M = Model([('train', tr, m1, 1)])
    out = {}
    for fg in (False, True):
        ll = lgl = n = 0
        for g, x in te:
            D = x['tfm'] if fg else x['tpm']
            for t, o in ((g['away'], g['home']), (g['home'], g['away'])):
                if t in D:
                    ll -= math.log(M.team_split(t, o, fg)[D[t]]); lgl -= math.log((M.lgfb if fg else M.lg)[D[t]]); n += 1
        out['first FG' if fg else 'first points'] = {'league': round(lgl / n, 4), 'model': round(ll / n, 4), 'n': n}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backfill', action='store_true')
    ap.add_argument('--base', action='store_true')
    a = ap.parse_args()
    seasons = load_all()
    if a.base:
        M = Model(seasons)
        for label, r in M.raw.items():
            n = r['n']
            print(label, 'games', n)
            print('  first points (incl FT):', {m: f"{r['fp'][m]} ({100 * r['fp'][m] / n:.1f}%)" for m in METHODS_FT})
            nb = sum(r['fb'].values())
            print('  first basket (FG only):', {m: f"{r['fb'][m]} ({100 * r['fb'][m] / nb:.1f}%)" for m in METHODS})
            nt = sum(r['tp'].values())
            print('  team first points:', {m: f"{100 * r['tp'][m] / nt:.1f}%" for m in METHODS_FT}, nt)
        print('position first-FG mix', {p: {m: round(v, 3) for m, v in d.items()} for p, d in M.posfirst.items()})
        print('position made-FG mix', {p: {m: round(v, 3) for m, v in d.items()} for p, d in M.posmix.items()})
        print('player method check (log loss, lower is better):', check(seasons))
        print('team method check (log loss):', check_team(seasons))


if __name__ == '__main__':
    main()
