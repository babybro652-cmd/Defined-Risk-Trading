#!/usr/bin/env python3
"""College football (FBS) FIRST SCORING PLAY model: team + type (TD / FG / safety). Built 11/21/26.

FanDuel market: "First Scoring Play - LSU Field Goal", "LSU Touchdown", ... Same idea as the NFL first TD chain
(analysis/nfl/first_td_model.py): play the game drive by drive until someone scores.

1. Opening possession. Coin toss: P(team receives) = 0.5 plus each team's shrunk receive habit (most CFB toss winners
   defer, a few teams take the ball).
2. Drive chain. Drives alternate; the second half starts with the other team receiving. Each drive ends in
   offense TD / offense FG / defense score (pick six, fumble return, punt or kick return TD, safety) / no score, from a
   ridge multinomial logit on: implied team total (spread + total), the offense's shrunk TD and FG rates per drive,
   the defense's shrunk TD and FG rates allowed, the offense's early-drive (team drives 1-3) TD and FG rates, and
   dummies for team drive 1 and 2. Drive count comes from both teams' pace.
3. Stage 2 calibration (fit on earlier games only, recent weeks weigh more): which team scores first = logistic on the
   chain's side logit + spread; TD vs FG given the team = logistic on the chain's TD-share logit, home flag, team spread.
4. Output per game: P(home TD first), P(home FG first), P(away TD first), P(away FG first), P(safety first),
   P(no score). A team's TD includes its defensive / return TDs (FanDuel's team TD option counts any TD by that team).
   Fair = 1 / chance. Take-at = fair decimal x 1.2.

Run:
  python3 analysis/ncaaf/first_score_data.py --download   # refresh raw + rebuild data/fs_*.csv
  python3 analysis/ncaaf/first_score.py backtest          # walk-forward, writes out/first_score_backtest.txt/.json
  python3 analysis/ncaaf/first_score.py week --date 2026-11-21   # prices that day's FBS vs FBS games + chart
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict, Counter

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)

DECAY = 0.93          # per team-game decay of drive counts
CARRY = 0.5           # weight kept on last season's counts at a new season
K_TEAM = 30.0         # pseudo-drives in team rate shrink
K_EARLY = 9.0         # pseudo-drives in early-drive rate shrink
K_RECV = 12.0         # pseudo-games in receive-habit shrink
CAL_HL = 15.0        # stage-2 calibration half-life in game weeks (about one season)
MAX_TEAM_DRIVE = 4    # team drives per game used to fit the drive model
FEATS = ['d1', 'd2', 'ln_imp', 'otd', 'ofg', 'dtd', 'dfg', 'etd', 'efg']
CLS = ['none', 'TD', 'FG', 'DEF']
OUTC = ['H_TD', 'H_FG', 'A_TD', 'A_FG', 'SAF', 'NONE']


def fl(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def american(p):
    if p <= 0:
        return '-'
    if p >= 0.5:
        return f'-{round(100 * p / (1 - p))}'
    return f'+{round(100 * (1 - p) / p)}'


def take_at(p):
    dec = 1 / p * 1.2
    return f'+{round((dec - 1) * 100)}' if dec >= 2 else f'-{round(100 / (dec - 1))}'


# ------------------------------------------------------------------ fitting
def mnl_fit(X, Y, lam=2.0):
    """Ridge multinomial logit. Class 0 = baseline. Class 3 (defense score) gets intercept only."""
    n, d = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    mask = np.ones((d + 1, 4)); mask[:, 0] = 0; mask[1:, 3] = 0
    idx = np.where(mask.ravel() > 0)[0]
    Yo = np.eye(4)[Y]
    pen = np.ones((d + 1, 4)) * lam; pen[0] = 0

    def fg(w):
        W = np.zeros((d + 1) * 4); W[idx] = w; W = W.reshape(d + 1, 4)
        U = Xb @ W; U -= U.max(1, keepdims=True)
        E = np.exp(U); P = E / E.sum(1, keepdims=True)
        loss = -(Yo * np.log(P + 1e-12)).sum() + 0.5 * (pen * W * W).sum()
        G = Xb.T @ (P - Yo) + pen * W
        return loss, G.ravel()[idx]
    r = minimize(fg, np.zeros(len(idx)), jac=True, method='L-BFGS-B')
    W = np.zeros((d + 1) * 4); W[idx] = r.x
    return W.reshape(d + 1, 4)


def mnl_probs(W, x):
    u = np.concatenate([[1.0], x]) @ W
    u -= u.max(); e = np.exp(u)
    return e / e.sum()


# ------------------------------------------------------------------ data
def load():
    G = list(csv.DictReader(open(os.path.join(DATA, 'fs_games.csv'))))
    D = list(csv.DictReader(open(os.path.join(DATA, 'fs_drives.csv'))))
    for g in G:
        g['season'] = int(g['season']); g['week'] = int(g['week'])
        g['spread'] = fl(g['spread']); g['total'] = fl(g['total'])
    dg = defaultdict(list)
    for d in D:
        dg[d['id']].append(d)
    return G, dg


def implied(spread, total, side):
    if spread is None or total is None:
        return None
    return total / 2 - spread / 2 if side == 'H' else total / 2 + spread / 2


def outcome(g):
    s, t = g['fs_side'], g['fs_type']
    if t == 'SAF':
        return 'SAF'
    if s in ('H', 'A') and t in ('TD', 'FG'):
        return f'{s}_{t}'
    return 'NONE'


# ------------------------------------------------------------------ state
class State:
    def __init__(self):
        z = lambda: dict(od=0.0, otd=0.0, ofg=0.0, dd=0.0, dtd=0.0, dfg=0.0, ed=0.0, etd=0.0, efg=0.0,
                         recv=0.0, games=0.0, drives=0.0)
        self.t = defaultdict(z)
        self.lg = Counter()
        self.season = None
        self.saf = [2.0, 400.0]     # safeties among defense scores (prior about 18%)

    def new_season(self, y):
        if self.season is not None and y != self.season:
            for a in self.t.values():
                for k in a:
                    a[k] *= CARRY
        self.season = y

    def lr(self, k):
        pri = {'td': 0.25, 'fg': 0.11, 'etd': 0.24, 'efg': 0.11}[k]
        base = 'drives' if k in ('td', 'fg') else 'edrives'
        return (self.lg[k] + 200 * pri) / (self.lg[base] + 200)

    def avg_imp(self):
        return self.lg['imp'] / self.lg['impn'] if self.lg['impn'] else 28.0

    def feats(self, team, opp, imp):
        a, b = self.t[team], self.t[opp]
        rt, rf, ret, ref = self.lr('td'), self.lr('fg'), self.lr('etd'), self.lr('efg')
        sh = lambda num, den, r, k: logit((num + k * r) / (den + k)) - logit(r)
        return dict(ln_imp=math.log(max(imp, 3) / self.avg_imp()) if imp else 0.0,
                    otd=sh(a['otd'], a['od'], rt, K_TEAM), ofg=sh(a['ofg'], a['od'], rf, K_TEAM),
                    dtd=sh(b['dtd'], b['dd'], rt, K_TEAM), dfg=sh(b['dfg'], b['dd'], rf, K_TEAM),
                    etd=sh(a['etd'], a['ed'], ret, K_EARLY), efg=sh(a['efg'], a['ed'], ref, K_EARLY))

    def recv_tend(self, team):
        a = self.t[team]
        return (a['recv'] + K_RECV * 0.5) / (a['games'] + K_RECV) - 0.5

    def pace(self, team):
        a = self.t[team]
        return (a['drives'] + 4 * 12.5) / (a['games'] + 4)

    def update(self, g, drives, teams):
        for a in (self.t[teams['H']], self.t[teams['A']]):
            for k in a:
                a[k] *= DECAY
        cnt = Counter()
        for d in drives:
            s = d['side']; o = 'A' if s == 'H' else 'H'
            cnt[s] += 1
            a, b = self.t[teams[s]], self.t[teams[o]]
            r = d['res']
            if r == 'END' and cnt[s] > 1:
                continue      # end-of-half kneel / clock drives
            td, fg = float(r == 'TD'), float(r == 'FG')
            a['od'] += 1; a['otd'] += td; a['ofg'] += fg
            b['dd'] += 1; b['dtd'] += td; b['dfg'] += fg
            a['drives'] += 1
            self.lg['drives'] += 1; self.lg['td'] += td; self.lg['fg'] += fg
            if cnt[s] <= 3:
                a['ed'] += 1; a['etd'] += td; a['efg'] += fg
                self.lg['edrives'] += 1; self.lg['etd'] += td; self.lg['efg'] += fg
            if r in ('DTD', 'SAF'):
                self.saf[1] += 1; self.saf[0] += float(r == 'SAF')
        for s in ('H', 'A'):
            self.t[teams[s]]['games'] += 1
            self.t[teams[s]]['recv'] += float(g['recv'] == s)
        for s in ('H', 'A'):
            imp = implied(g['spread'], g['total'], s)
            if imp:
                self.lg['imp'] += imp; self.lg['impn'] += 1


def drive_x(fe, n):
    return np.array([float(n == 1), float(n == 2), fe['ln_imp'], fe['otd'], fe['ofg'], fe['dtd'], fe['dfg'],
                     fe['etd'] * (n <= 3), fe['efg'] * (n <= 3)])


def chain(W, fh, fa, p_h_recv, n_drives, saf_share):
    """Distribution over OUTC for one game."""
    h1 = int(round(n_drives / 2)); h2 = int(round(n_drives)) - h1
    out = np.zeros(6)
    cache = {}

    def dp(side, n):
        k = (side, min(n, 4))
        if k not in cache:
            cache[k] = mnl_probs(W, drive_x(fh if side == 'H' else fa, min(n, 4)))
        return cache[k]
    for recv_h, w in ((True, p_h_recv), (False, 1 - p_h_recv)):
        f1, f2 = ('H', 'A') if recv_h else ('A', 'H')
        seq = [f1 if k % 2 == 0 else f2 for k in range(h1)] + [f2 if k % 2 == 0 else f1 for k in range(h2)]
        alive, cnt, res = 1.0, Counter(), np.zeros(6)
        for s in seq:
            cnt[s] += 1
            p = dp(s, cnt[s])
            off = 0 if s == 'H' else 2
            dfn = 2 if s == 'H' else 0
            res[off] += alive * p[1]
            res[off + 1] += alive * p[2]
            res[dfn] += alive * p[3] * (1 - saf_share)
            res[4] += alive * p[3] * saf_share
            alive *= p[0]
        res[5] = alive
        out += w * res
    return out / out.sum()


# ------------------------------------------------------------------ walk-forward engine
def walk(G, dg, eval_from=(2024, 1), fit_from=(2023, 3), raw_from=(2023, 6), live=None):
    """Weeks in order; refit before each week on earlier drives. Raw chain prices start at raw_from and feed the
    stage-2 calibration (fit on earlier games only). live: list of upcoming games to price at the end."""
    st = State()
    by_week = defaultdict(list)
    for g in G:
        by_week[(g['season'], g['week'])].append(g)
    rows_x, rows_y, rows_k, preds, raws = [], [], [], [], []
    base = []   # (key, spread_home, outcome) for the naive baseline
    W = cal = None
    for wk in sorted(by_week):
        st.new_season(wk[0])
        if wk >= raw_from:
            m = np.array([k < wk for k in rows_k])
            W = mnl_fit(np.array(rows_x)[m], np.array(rows_y)[m])
        if wk >= eval_from:
            bl = baseline_fit([b for b in base if b[0] < wk])
            cal = cal_fit([r for r in raws if r['key'] < wk])
        for g in by_week[wk]:
            teams = {'H': g['home'], 'A': g['away']}
            fe = {s: st.feats(teams[s], teams['A' if s == 'H' else 'H'], implied(g['spread'], g['total'], s))
                  for s in ('H', 'A')}
            if wk >= fit_from:
                cnt = Counter()
                for d in dg[g['id']]:
                    cnt[d['side']] += 1
                    n = cnt[d['side']]
                    if n <= MAX_TEAM_DRIVE and d['res'] != 'END':
                        rows_x.append(drive_x(fe[d['side']], n))
                        rows_y.append({'TD': 1, 'FG': 2, 'DTD': 3, 'SAF': 3}.get(d['res'], 0))
                        rows_k.append(wk)
                base.append((wk, g['spread'], outcome(g)))
            if wk >= raw_from and g['spread'] is not None:
                pr = price(st, W, g, fe); pr['fe'] = fe
                pr['y'] = outcome(g); pr['game'] = g; pr['key'] = wk
                raws.append(pr)
                if wk >= eval_from:
                    pr['raw'] = pr['p']
                    pr['p'] = cal_apply(cal, pr['raw'], g['spread'])
                    pr['base'] = baseline_probs(bl, g['spread'])
                    preds.append(pr)
        for g in by_week[wk]:
            st.update(g, dg[g['id']], {'H': g['home'], 'A': g['away']})
    if live is not None:
        st.new_season(live[0]['season'])
        W = mnl_fit(np.array(rows_x), np.array(rows_y))
        cal = cal_fit(raws)
        out = []
        for g in live:
            fe = {s: st.feats(g['home' if s == 'H' else 'away'], g['away' if s == 'H' else 'home'],
                              implied(g['spread'], g['total'], s)) for s in ('H', 'A')}
            pr = price(st, W, g, fe); pr['game'] = g
            pr['raw'] = pr['p']; pr['p'] = cal_apply(cal, pr['raw'], g['spread'])
            out.append(pr)
        return out, W, st
    return preds, W, st


def _lfit(X, y, lam=0.5, sw=None):
    Xb = np.hstack([np.ones((len(X), 1)), X])
    sw = np.ones(len(y)) if sw is None else sw

    def nll(w):
        z = Xb @ w; p = 1 / (1 + np.exp(-z))
        return -(sw * (y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))).sum() + lam * (w[1:] ** 2).sum()
    return minimize(nll, np.zeros(Xb.shape[1]), method='BFGS').x


def cal_fit(raws):
    """Stage 2 on earlier games: which team scores first (chain side logit + spread) and TD vs FG given the team
    (chain TD-share logit, home flag, team spread). Safety rate = league."""
    sc = [r for r in raws if r['y'] not in ('SAF', 'NONE')]
    side = lambda q: logit((q[0] + q[1]) / q[:4].sum())
    Xs = np.array([[side(r['raw'] if 'raw' in r else r['p']), r['game']['spread'] / 10] for r in sc])
    ys = np.array([float(r['y'].startswith('H')) for r in sc])
    Xt, yt = [], []
    for r in sc:
        q = r['raw'] if 'raw' in r else r['p']
        o = 0 if r['y'].startswith('H') else 2
        tsp = r['game']['spread'] if o == 0 else -r['game']['spread']
        Xt.append([logit(q[o] / (q[o] + q[o + 1])), float(o == 0), tsp / 10]); yt.append(float(r['y'].endswith('TD')))
    saf = (sum(r['y'] == 'SAF' for r in raws) + 1) / (len(raws) + 100)
    # recent games weigh more (half-life CAL_HL game weeks): the dog-TD-first rate fell each season 2023-2026
    order = sorted({r['key'] for r in sc})
    rank = {k: i for i, k in enumerate(order)}
    sw = np.array([0.5 ** ((len(order) - 1 - rank[r['key']]) / CAL_HL) for r in sc])
    return dict(ws=_lfit(Xs, ys, sw=sw), wt=_lfit(np.array(Xt), np.array(yt), sw=sw), saf=saf)


def cal_apply(c, q, spread):
    if c is None:
        return q
    sg = lambda z: 1 / (1 + math.exp(-z))
    ph = sg(c['ws'][0] + c['ws'][1] * logit((q[0] + q[1]) / q[:4].sum()) + c['ws'][2] * spread / 10)
    th = sg(c['wt'][0] + c['wt'][1] * logit(q[0] / (q[0] + q[1])) + c['wt'][2] + c['wt'][3] * spread / 10)
    ta = sg(c['wt'][0] + c['wt'][1] * logit(q[2] / (q[2] + q[3])) - c['wt'][3] * spread / 10)
    r = 1 - c['saf']
    return np.array([r * ph * th, r * ph * (1 - th), r * (1 - ph) * ta, r * (1 - ph) * (1 - ta), c['saf'], 0.0])


def price(st, W, g, fe):
    pa = min(0.8, max(0.2, 0.5 + st.recv_tend(g['home']) - st.recv_tend(g['away'])))
    nd = st.pace(g['home']) + st.pace(g['away'])
    ss = st.saf[0] / st.saf[1]
    p = chain(W, fe['H'], fe['A'], pa, nd, ss)
    return dict(p=p, p_h_recv=pa)


def baseline_fit(rows):
    """Naive: P(home scores first) = logistic(a + b x home spread); P(TD | team first) and P(safety / none) = league."""
    rows = [r for r in rows if r[1] is not None]
    y = np.array([1.0 if r[2].startswith('H') else 0.0 for r in rows if r[2] not in ('SAF', 'NONE')])
    x = np.array([r[1] for r in rows if r[2] not in ('SAF', 'NONE')])

    def nll(w):
        z = w[0] + w[1] * x; p = 1 / (1 + np.exp(-z))
        return -(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)).sum()
    w = minimize(nll, np.zeros(2), method='BFGS').x
    c = Counter(r[2] for r in rows)
    n = len(rows)
    td = (c['H_TD'] + c['A_TD']) / max(1, n - c['SAF'] - c['NONE'])
    return dict(w=w, td=td, saf=c['SAF'] / n, none=c['NONE'] / n)


def baseline_probs(b, spread):
    ph = 1 / (1 + math.exp(-(b['w'][0] + b['w'][1] * spread)))
    r = 1 - b['saf'] - b['none']
    return np.array([r * ph * b['td'], r * ph * (1 - b['td']), r * (1 - ph) * b['td'], r * (1 - ph) * (1 - b['td']),
                     b['saf'], b['none']])


# ------------------------------------------------------------------ backtest
def backtest():
    G, dg = load()
    preds, W, _ = walk(G, dg)
    lines = []
    P = lambda s: lines.append(s)
    yi = lambda pr: OUTC.index(pr['y'])

    def ll(sub, key):
        k = {'m': 'p', 'b': 'base', 'r': 'raw'}[key]
        return float(np.mean([-math.log(max(1e-4, pr[k][yi(pr)])) for pr in sub]))

    def side_ll(sub, key):
        v = []
        for pr in sub:
            if pr['y'] in ('SAF', 'NONE'):
                continue
            q = pr['p'] if key == 'm' else pr['base']
            ph = (q[0] + q[1]) / (q[0] + q[1] + q[2] + q[3])
            v.append(-math.log(ph if pr['y'].startswith('H') else 1 - ph))
        return float(np.mean(v))

    def type_ll(sub, key):
        v = []
        for pr in sub:
            if pr['y'] in ('SAF', 'NONE'):
                continue
            q = pr['p'] if key == 'm' else pr['base']
            o = 0 if pr['y'].startswith('H') else 2
            pt = q[o] / (q[o] + q[o + 1])
            v.append(-math.log(pt if pr['y'].endswith('TD') else 1 - pt))
        return float(np.mean(v))
    res = {}
    P('FBS first scoring play model: walk-forward backtest (refit before every week)')
    P('Outcomes: home TD / home FG / away TD / away FG / safety / no score. Lower log loss is better.')
    P('')
    seasons = sorted({pr['game']['season'] for pr in preds})
    for lab, sub in [(str(s), [pr for pr in preds if pr['game']['season'] == s]) for s in seasons] + [('All', preds)]:
        r = dict(n=len(sub), ll_m=ll(sub, 'm'), ll_b=ll(sub, 'b'), ll_raw=ll(sub, 'r'), side_m=side_ll(sub, 'm'), side_b=side_ll(sub, 'b'),
                 type_m=type_ll(sub, 'm'), type_b=type_ll(sub, 'b'))
        res[lab] = r
        P(f"{lab}: {r['n']} games | 6-way log loss model {r['ll_m']:.4f} (raw chain {r['ll_raw']:.4f}) vs naive {r['ll_b']:.4f} | "
          f"which team first {r['side_m']:.4f} vs {r['side_b']:.4f} | TD vs FG given team {r['type_m']:.4f} vs {r['type_b']:.4f}")
    # stronger naive for the TD vs FG split: logistic on the scoring team's implied total only (walk-forward)
    rows = []
    for pr in preds:
        if pr['y'] in ('SAF', 'NONE'):
            continue
        sd = pr['y'][0]; imp = implied(pr['game']['spread'], pr['game']['total'], sd)
        if imp is not None:
            o = 0 if sd == 'H' else 2
            rows.append((pr['key'], imp / 10, float(pr['y'].endswith('TD')), pr['p'][o] / (pr['p'][o] + pr['p'][o + 1])))
    v2, vm = [], []
    for wk in sorted({r[0] for r in rows}):
        tr = [r for r in rows if r[0] < wk]
        if len(tr) < 200:
            continue
        w = _lfit(np.array([[r[1]] for r in tr]), np.array([r[2] for r in tr]))
        for r in rows:
            if r[0] == wk:
                q = 1 / (1 + math.exp(-(w[0] + w[1] * r[1])))
                v2.append(-math.log(q if r[2] else 1 - q)); vm.append(-math.log(r[3] if r[2] else 1 - r[3]))
    P(f'TD vs FG vs a stronger naive (implied team total only), {len(vm)} games: model {np.mean(vm):.4f} vs {np.mean(v2):.4f}')
    res['td_fg_vs_implied'] = dict(n=len(vm), model=float(np.mean(vm)), implied_only=float(np.mean(v2)))
    c = Counter(pr['y'] for pr in preds)
    P('')
    P('Outcome mix (all eval games): ' + ', '.join(f'{k} {100 * c[k] / len(preds):.1f}%' for k in OUTC))
    fav = [pr for pr in preds if pr['y'] not in ('SAF', 'NONE') and pr['game']['spread'] != 0]
    fw = sum(1 for pr in fav if (pr['game']['spread'] < 0) == pr['y'].startswith('H'))
    P(f'Favorite scored first: {100 * fw / len(fav):.1f}% of {len(fav)} games')
    td = sum(1 for pr in preds if pr['y'].endswith('TD')); fg = sum(1 for pr in preds if pr['y'].endswith('FG'))
    P(f'First score was a TD {100 * td / (td + fg):.1f}% / FG {100 * fg / (td + fg):.1f}% (of TD + FG)')
    # calibration over every outcome cell
    P('')
    P('Calibration, every outcome option (team TD / team FG), predicted vs actual:')
    edges = (0, .05, .10, .15, .20, .25, .30, .35, .40, .50, 1.01)
    for key, lab in (('m', 'Model'), ('b', 'Naive')):
        P(f'  {lab}:')
        for lo, hi in zip(edges, edges[1:]):
            ps, ys = [], []
            for pr in preds:
                q = pr['p'] if key == 'm' else pr['base']
                for j in range(4):
                    if lo <= q[j] < hi:
                        ps.append(q[j]); ys.append(float(yi(pr) == j))
            if ps:
                P(f'    {int(lo * 100):>2}-{int(min(hi, 1) * 100):>3}%: n {len(ps):>4}  pred {100 * np.mean(ps):5.1f}%  '
                  f'actual {100 * np.mean(ys):5.1f}%')
    P('')
    P('By option, mean predicted vs actual:')
    for nm, fj in (('Favorite TD', lambda hf: 0 if hf else 2), ('Favorite FG', lambda hf: 1 if hf else 3),
                   ('Underdog TD', lambda hf: 2 if hf else 0), ('Underdog FG', lambda hf: 3 if hf else 1)):
        js = [(pr, fj(pr['game']['spread'] <= 0)) for pr in preds]
        P(f"  {nm}: model {100 * np.mean([pr['p'][j] for pr, j in js]):.1f}%  naive "
          f"{100 * np.mean([pr['base'][j] for pr, j in js]):.1f}%  actual {100 * np.mean([yi(pr) == j for pr, j in js]):.1f}%")
    # FG-specific check: the FG options are the market's long prices
    P('')
    P('Field goal options only (team FG first), by model chance:')
    for lo, hi in ((0, .10), (.10, .14), (.14, .18), (.18, .24), (.24, 1)):
        ps, ys, bs = [], [], []
        for pr in preds:
            for j in (1, 3):
                if lo <= pr['p'][j] < hi:
                    ps.append(pr['p'][j]); ys.append(float(yi(pr) == j)); bs.append(pr['base'][j])
        if ps:
            P(f'  {int(lo * 100)}-{int(min(hi, 1) * 100)}%: n {len(ps):>4}  model {100 * np.mean(ps):5.1f}%  naive '
              f'{100 * np.mean(bs):5.1f}%  actual {100 * np.mean(ys):5.1f}%')
    # ranking: does the model pick the best single option better than naive?
    P('')
    for key, lab in (('m', 'Model'), ('b', 'Naive')):
        hit = np.mean([float(int(np.argmax((pr['p'] if key == 'm' else pr['base'])[:4])) == yi(pr)) for pr in preds])
        P(f'{lab} top option hit: {100 * hit:.1f}%')
    P('')
    P('Drive model weights (final fit; columns none / TD / FG / defense score):')
    for nm, row in zip(['const'] + FEATS, W):
        P(f'  {nm:>7}: ' + ' '.join(f'{v:+.3f}' for v in row))
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'first_score_backtest.txt'), 'w').write('\n'.join(lines) + '\n')
    json.dump(res, open(os.path.join(OUT, 'first_score_backtest.json'), 'w'), indent=1)
    print('\n'.join(lines))


# ------------------------------------------------------------------ live week
def live_games(date):
    import first_score_data as fsd
    sb = fsd.scoreboard(dates=date.replace('-', ''))
    out = []
    for r in fsd.event_rows(sb):
        if not r['fbs'] or r['status'] != 'STATUS_SCHEDULED':
            continue
        sp = fsd.home_spread(r['details'], r['home'], r['away'])
        tot = fl(r['total'])
        if sp is None or tot is None:
            print('no line, skip', r['away'], '@', r['home'], file=sys.stderr)
            continue
        out.append(dict(season=int(date[:4]) if int(date[5:7]) > 2 else int(date[:4]) - 1, id=r['id'],
                        date=r['date'], home=r['home'], away=r['away'], spread=sp, total=tot,
                        neutral=r['neutral']))
    return out


def et_time(iso):
    from datetime import datetime, timedelta
    t = datetime.strptime(iso, '%Y-%m-%dT%H:%MZ') - timedelta(hours=5)
    return t.strftime('%-I:%M')


def week(date):
    G, dg = load()
    live = live_games(date)
    if not live:
        print('no FBS games with lines on', date); return
    G = [g for g in G if g['date'] < date or g['id'] not in {x['id'] for x in live}]
    preds, W, st = walk(G, dg, eval_from=(9999, 0), live=live)
    rows = []
    for pr in preds:
        g, p = pr['game'], pr['p']
        for j, (side, typ) in enumerate((('H', 'TD'), ('H', 'FG'), ('A', 'TD'), ('A', 'FG'))):
            team = g['home'] if side == 'H' else g['away']
            rows.append(dict(game=f"{g['away']} at {g['home']}", kick=et_time(g['date']), team=team, type=typ,
                             p=float(p[j]), fair=american(p[j]), take=take_at(p[j]),
                             line=f"{g['home']} {g['spread']:+g}, total {g['total']:g}"))
        pr['saf'] = float(p[4]); pr['none'] = float(p[5])
    os.makedirs(OUT, exist_ok=True)
    tag = date
    with open(os.path.join(OUT, f'first_score_{tag}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    games = []
    for pr in preds:
        g, p = pr['game'], pr['p']
        games.append(dict(game=f"{g['away']} at {g['home']}", kick=et_time(g['date']), spread_home=g['spread'],
                          total=g['total'], home_recv=round(pr['p_h_recv'], 3),
                          probs={k: round(float(v), 4) for k, v in zip(OUTC, p)}))
    json.dump(games, open(os.path.join(OUT, f'first_score_{tag}.json'), 'w'), indent=1)
    chart(date, preds)
    for gm in games:
        pz = gm['probs']
        print(f"{gm['kick']} {gm['game']:<14} H{gm['spread_home']:+5.1f} T{gm['total']:4.1f} | "
              + ' '.join(f"{k} {100 * v:4.1f}%({american(v)})" for k, v in pz.items()))


def chart(date, preds):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    preds = sorted(preds, key=lambda pr: pr['game']['date'])
    hdr = ['Kick ET', 'Game (line)', 'Fav TD', 'Fav FG', 'Dog TD', 'Dog FG', 'Safety']
    cells, fgcol = [], []
    for pr in preds:
        g, p = pr['game'], pr['p']
        hf = g['spread'] <= 0
        fav, dog = (g['home'], g['away']) if hf else (g['away'], g['home'])
        fi, di = (0, 2) if hf else (2, 0)
        c = lambda j, t: f'{t} {100 * p[j]:.0f}%  {american(p[j])}\ntake {take_at(p[j])}'
        cells.append([et_time(g['date']), f"{g['away']} at {g['home']}\n{fav} -{abs(g['spread']):g}, o/u {g['total']:g}",
                      c(fi, fav), c(fi + 1, fav), c(di, dog), c(di + 1, dog),
                      f'{100 * p[4]:.1f}%'])
    fig_h = 0.6 + 0.52 * (len(cells) + 1)
    fig, ax = plt.subplots(figsize=(13, fig_h))
    fig.patch.set_facecolor('black'); ax.set_facecolor('black'); ax.axis('off')
    tb = ax.table(cellText=cells, colLabels=hdr, cellLoc='center', bbox=[0, 0, 1, 1],
                  colWidths=[.07, .19, .16, .16, .16, .16, .10])
    tb.auto_set_font_size(False); tb.set_fontsize(9)
    for (r, cc), cl in tb.get_celld().items():
        cl.set_edgecolor('#1db954')
        if r == 0:
            cl.set_facecolor('#1db954'); cl.get_text().set_color('black'); cl.get_text().set_fontweight('bold')
        else:
            cl.set_facecolor('#0b0b0b'); cl.get_text().set_color('white')
            if cc in (3, 5):
                cl.get_text().set_color('#7CFC9A')
    ax.set_title(f'CFB first scoring play, {date} (our drive chain model; fair price, take-at = fair x1.2)',
                 color='#1db954', fontsize=12, fontweight='bold', loc='left')
    ax.text(0, -0.02, 'Team TD includes defense / return TDs. Backtest: as accurate as the spread + total, no edge beyond '
            'them. Value only where FanDuel pays take-at or longer. Small stakes.', color='#9a9a9a', fontsize=8,
            transform=ax.transAxes, va='top')
    p = os.path.join(OUT, f'first_score_{date}.png')
    plt.savefig(p, dpi=110, bbox_inches='tight', facecolor='black')
    print('chart', p)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['backtest', 'week'])
    ap.add_argument('--date', default=None)
    a = ap.parse_args()
    if a.mode == 'backtest':
        backtest()
    else:
        from datetime import date as _d
        week(a.date or _d.today().isoformat())
