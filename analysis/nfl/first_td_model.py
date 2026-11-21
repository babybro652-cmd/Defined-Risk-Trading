#!/usr/bin/env python3
"""NFL first touchdown scorer model (chain model, built 11/17/26).

Structured like the NBA first basket chain (analysis/nba/chain_model.py): play the game drive by drive until someone
scores a TD, then split the scoring team's first TD among its players.

1. Opening kickoff. The receiver is unknown pregame (coin toss). P(team receives) = 0.5 plus each team's shrunk
   receive tendency (some teams take the ball when they win the toss instead of deferring).
2. Drive chain. Drives alternate. Each drive ends in an offensive TD with a chance from a ridge logistic model:
   implied team total (spread + total), the team's shrunk offensive TD rate per drive, the opponent's shrunk TD rate
   allowed, the team's opening-drive TD rate and the opponent's opening-drive rate allowed (scripted drives), and
   dummies for team drive 1 and 2. Each drive also has a small league chance of a non-offensive TD (pick six, fumble
   return, kick or punt return), which voids / loses every player first TD bet. The second half starts with the
   other team receiving. Drive count comes from both teams' pace (drives per game).
   Output: P(A offense scores the game's first TD), P(B), P(non-offensive TD first), P(no TD).
3. Player share of the team's FIRST TD: conditional logit over the team's active skill players plus an "other"
   option, on decayed (recent games weigh more) shares of: team TDs, red-zone carries + targets, inside-5 carries +
   targets, opening-script touches (team's first 2 drives), 1st-quarter touches, snap share, team-first-TD share,
   with position terms (QB term carries QB rushing TDs). Shares shrink toward position priors.
4. Injuries / QB changes: out players drop from the candidate list. Their shares of each usage stat go to active
   teammates at the same position, in proportion. A new QB starts from his own history (or the QB prior).
   The line already moves for QB changes; that flows through the implied total.
5. Player first TD chance = P(team offense scores first) x share. Fair = 1 / chance. Take-at = fair decimal x 1.2.

Run:
  python3 analysis/nfl/first_td_data.py            # rebuild data/ftd_*.csv from raw/ (add --download to refresh)
  python3 analysis/nfl/first_td_model.py backtest  # walk-forward backtest, writes out/first_td_backtest.txt/.json
  python3 analysis/nfl/first_td_model.py week --week 11   # picks + chart out/charts/first_td_wk11.png
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict, Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
RAW = os.path.join(HERE, 'raw')
OUT = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)

DECAY_P = 0.92        # per player-game decay of usage sums (half-life about 8 games)
DECAY_T = 0.94        # per team-game decay of team drive rates
K_TEAM = 40.0         # pseudo-drives in team TD-rate shrink
K_OPEN = 10.0         # pseudo-games in opening-drive rate shrink
K_RECV = 16.0         # pseudo-games in receive-tendency shrink
K_SHARE = 3.0         # pseudo team-events in player share shrink toward the position prior
MAX_TEAM_DRIVE = 8    # drives used to fit the drive model
SKILL = ('RB', 'WR', 'TE', 'QB')
PFEATS = ['l_td', 'l_rz', 'l_gl', 'l_open', 'l_q1', 'l_snap', 'l_tfirst', 'new', 'QB', 'WR', 'TE']
DFEATS = ['d1', 'd2', 'ln_imp', 'off', 'dfn', 'open_off', 'open_def']
OFF_KINDS = ('rush', 'rec', 'off_other')


def f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def ridge_logit(X, y, lam=2.0, iters=40):
    n, d = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    w = np.zeros(d + 1)
    R = np.eye(d + 1) * lam; R[0, 0] = 0
    for _ in range(iters):
        p = sigmoid(Xb @ w)
        g = Xb.T @ (p - y) + R @ w
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb + R
        s = np.linalg.solve(H, g); w -= s
        if np.abs(s).max() < 1e-8:
            break
    return w


def clogit_fit(groups, lam=1.0, iters=50):
    """Conditional logit. groups: list of (X (n x d), chosen index or -1 for 'other'). Utility of 'other' = w0."""
    d = groups[0][0].shape[1]
    blocks, starts, chosen = [], [], []
    pos = 0
    for X, c in groups:
        Xa = np.vstack([np.eye(1, d + 1, 0), np.hstack([np.zeros((X.shape[0], 1)), X])])  # row 0 = other
        blocks.append(Xa); starts.append(pos); chosen.append(pos + (0 if c < 0 else c + 1)); pos += Xa.shape[0]
    A = np.vstack(blocks); starts = np.array(starts); chosen = np.array(chosen)
    gid = np.repeat(np.arange(len(groups)), np.diff(np.append(starts, pos)))
    w = np.zeros(d + 1)
    for _ in range(iters):
        u = A @ w
        mx = np.maximum.reduceat(u, starts)
        e = np.exp(u - mx[gid])
        den = np.add.reduceat(e, starts)
        p = e / den[gid]
        M = np.add.reduceat(A * p[:, None], starts)               # group means
        g = M.sum(0) - A[chosen].sum(0) + lam * w
        H = (A * p[:, None]).T @ A - M.T @ M + lam * np.eye(d + 1)
        s = np.linalg.solve(H, g); w -= s
        if np.abs(s).max() < 1e-8:
            break
    return w


def clogit_probs(w, X):
    d = X.shape[1]
    Xa = np.vstack([np.eye(1, d + 1, 0), np.hstack([np.zeros((X.shape[0], 1)), X])])
    u = Xa @ w; u -= u.max(); e = np.exp(u)
    p = e / e.sum()
    return p[1:], p[0]


def american(p):
    if p <= 0:
        return '-'
    if p >= 0.5:
        return f'-{round(100 * p / (1 - p))}'
    return f'+{round(100 * (1 - p) / p)}'


def take_at(p):
    dec = 1 / p * 1.2
    return f'+{round((dec - 1) * 100)}' if dec >= 2 else f'-{round(100 / (dec - 1))}'


# ------------------------------------------------------------------ data
def load_tables():
    G = list(csv.DictReader(open(os.path.join(DATA, 'ftd_games.csv'))))
    D = list(csv.DictReader(open(os.path.join(DATA, 'ftd_drives.csv'))))
    P = list(csv.DictReader(open(os.path.join(DATA, 'ftd_player_games.csv'))))
    for g in G:
        g['season'] = int(g['season']); g['week'] = int(g['week'])
    dg, pgm = defaultdict(list), defaultdict(list)
    for d in D:
        dg[d['game_id']].append(d)
    for p in P:
        for k in ('snaps', 'car', 'tgt', 'rz_car', 'rz_tgt', 'gl_car', 'gl_tgt', 'q1_car', 'q1_tgt', 'open_car', 'open_tgt',
                  'td', 'team_first_td', 'game_first_td'):
            p[k] = int(p[k])
        p['snap_pct'] = float(p['snap_pct'])
        p['pos'] = 'RB' if p['pos'] in ('FB', 'HB') else p['pos']
        pgm[p['game_id']].append(p)
    return G, dg, pgm


def implied(g, team):
    s, t = f(g.get('spread_line'), None), f(g.get('total_line'), None)
    if s is None or t is None:
        return None
    return t / 2 + s / 2 if team == g['home'] else t / 2 - s / 2


# ------------------------------------------------------------------ state
class State:
    def __init__(self):
        self.t = defaultdict(lambda: dict(od=0.0, otd=0.0, dd=0.0, dtd=0.0, og=0.0, oopen=0.0, dg=0.0, dopen=0.0,
                                           recv=0.0, games=0.0, drives=0.0))
        self.lg = dict(drives=0, td=0, open=0, opentd=0, non=0, alld=0, games=0, imp=0.0, impn=0)
        self.p = defaultdict(lambda: defaultdict(float))
        self.pinfo = {}
        self.posprior = defaultdict(lambda: [0.0, 0.0])   # (pos, stat) -> [player sum, team sum]
        self.team_recent = defaultdict(list)              # team -> list of {pid: snap_pct} for its games

    # league rates
    def lg_rate(self):
        return (self.lg['td'] + 25) / (self.lg['drives'] + 100)

    def lg_open(self):
        return (self.lg['opentd'] + 25) / (self.lg['open'] + 100)

    def lg_non(self):
        return (self.lg['non'] + 2) / (self.lg['alld'] + 200)

    def avg_imp(self):
        return self.lg['imp'] / self.lg['impn'] if self.lg['impn'] else 22.0

    def team_feats(self, team, opp, imp):
        a, b = self.t[team], self.t[opp]
        lr, lo = self.lg_rate(), self.lg_open()
        off = logit((a['otd'] + K_TEAM * lr) / (a['od'] + K_TEAM)) - logit(lr)
        dfn = logit((b['dtd'] + K_TEAM * lr) / (b['dd'] + K_TEAM)) - logit(lr)
        oo = logit((a['oopen'] + K_OPEN * lo) / (a['og'] + K_OPEN)) - logit(lo)
        od = logit((b['dopen'] + K_OPEN * lo) / (b['dg'] + K_OPEN)) - logit(lo)
        li = math.log(imp / self.avg_imp()) if imp else 0.0
        return dict(off=off, dfn=dfn, open_off=oo, open_def=od, ln_imp=li)

    def recv_tend(self, team):
        a = self.t[team]
        return (a['recv'] + K_RECV * 0.5) / (a['games'] + K_RECV) - 0.5

    def pace(self, team):
        a = self.t[team]
        return (a['drives'] + 4 * 10.75) / (a['games'] + 4)

    def share(self, pid, stat, tstat, pos):
        s = self.p[pid]
        pr = self.posprior[(pos, stat)]
        prior = pr[0] / pr[1] if pr[1] else 0.08
        return (s[stat] + K_SHARE * prior) / (s[tstat] + K_SHARE)

    def player_feats(self, pid, pos):
        s = self.p[pid]
        out = {}
        for stat, tstat, key in (('td', 't_td', 'l_td'), ('rz', 't_rz', 'l_rz'), ('gl', 't_gl', 'l_gl'),
                                 ('open', 't_open', 'l_open'), ('q1', 't_q1', 'l_q1'), ('tfirst', 't_tdg', 'l_tfirst')):
            out[key] = self.share(pid, stat, tstat, pos)
        out['snap'] = s['snap'] / s['gp'] if s['gp'] else 0.3
        out['new'] = 1.0 if s['gp'] < 1.5 else 0.0
        out['gp'] = s['gp']
        return out

    def regulars(self, team):
        """Players with a big role in the team's last 3 games (snap share >= 30% in any)."""
        reg = {}
        for gm in self.team_recent[team][-3:]:
            for pid, sp in gm.items():
                if sp >= 0.30:
                    reg[pid] = self.pinfo.get(pid, {}).get('pos')
        return reg

    def update(self, g, drives, pls):
        home, away = g['home'], g['away']
        # teams
        tn = defaultdict(lambda: dict(d=0, td=0, open=0, opentd=0, all=0))
        for d in drives:
            t = d['team']; n = int(d['team_drive'])
            x = tn[t]; x['all'] += 1
            if n <= MAX_TEAM_DRIVE:
                x['d'] += 1; x['td'] += int(d['off_td'])
            if n == 1:
                x['open'] = 1; x['opentd'] = int(d['off_td'])
            self.lg['non'] += int(d['non_td']); self.lg['alld'] += 1
        for t, o in ((home, away), (away, home)):
            a, b, x = self.t[t], self.t[o], tn[t]
            for k in a:
                a[k] *= DECAY_T
            a['od'] += x['d']; a['otd'] += x['td']; a['og'] += x['open']; a['oopen'] += x['opentd']
            a['recv'] += int(g['recv'] == t); a['games'] += 1; a['drives'] += x['all']
            self.lg['drives'] += x['d']; self.lg['td'] += x['td']; self.lg['open'] += x['open']; self.lg['opentd'] += x['opentd']
            imp = implied(g, t)
            if imp:
                self.lg['imp'] += imp; self.lg['impn'] += 1
        for t, o in ((home, away), (away, home)):
            b, x = self.t[o], tn[t]
            # defense of o faced x  (decay already applied above to b)
            b['dd'] += x['d']; b['dtd'] += x['td']; b['dg'] += x['open']; b['dopen'] += x['opentd']
        # players
        tot = defaultdict(lambda: defaultdict(int))
        for p in pls:
            t = tot[p['team']]
            t['td'] += p['td']; t['rz'] += p['rz_car'] + p['rz_tgt']; t['gl'] += p['gl_car'] + p['gl_tgt']
            t['open'] += p['open_car'] + p['open_tgt']; t['q1'] += p['q1_car'] + p['q1_tgt']
            t['tdg'] += p['team_first_td']
        recent = defaultdict(dict)
        for p in pls:
            if p['pos'] not in SKILL:
                continue
            s = self.p[p['pid']]
            t = tot[p['team']]
            vals = dict(td=p['td'], rz=p['rz_car'] + p['rz_tgt'], gl=p['gl_car'] + p['gl_tgt'], open=p['open_car'] + p['open_tgt'],
                        q1=p['q1_car'] + p['q1_tgt'], tfirst=p['team_first_td'])
            for stat, v in vals.items():
                tv = t['tdg'] if stat == 'tfirst' else t[stat]
                pr = self.posprior[(p['pos'], stat)]; pr[0] += v; pr[1] += tv
            for k in list(s):
                s[k] *= DECAY_P
            s['gp'] += 1; s['snap'] += p['snap_pct']
            for stat, v in vals.items():
                s[stat] += v
            s['t_td'] += t['td']; s['t_rz'] += t['rz']; s['t_gl'] += t['gl']; s['t_open'] += t['open']; s['t_q1'] += t['q1']
            s['t_tdg'] += t['tdg']
            self.pinfo[p['pid']] = dict(name=p['name'], pos=p['pos'], team=p['team'])
            recent[p['team']][p['pid']] = p['snap_pct']
        for t in (home, away):
            self.team_recent[t].append(recent.get(t, {}))


def candidates(st, team, active, starter_qb=None, lead_rb=None):
    """active: list of (pid, pos). Returns rows with shares adjusted for out regulars, by position.
    starter_qb: the expected starting QB (live); in the backtest the QB with the most snaps that game.
    lead_rb: live only (11/21/26). The next-up RB on the depth chart when the lead RB is out: his usage rises to 85% of
    the vacated RB usage (or stays at his own if higher), the rest is split pro rata. None keeps the old split (backtest)."""
    rows = []
    for pid, pos in active:
        if pos not in SKILL:
            continue
        r = st.player_feats(pid, pos); r.update(pid=pid, pos=pos)
        rows.append(r)
    act = {r['pid'] for r in rows}
    reg = st.regulars(team)
    out = [(pid, pos) for pid, pos in reg.items() if pid not in act and pos in SKILL]
    for key in ('l_td', 'l_rz', 'l_gl', 'l_open', 'l_q1', 'l_tfirst'):
        for pos in SKILL:
            grp = [r for r in rows if r['pos'] == pos]
            if not grp:
                continue
            vac = sum(st.player_feats(pid, pos)[key] for pid, pp in out if pp == pos)
            if pos == 'QB':
                # a new starting QB takes the whole QB role: give vacated share to the top-snap QB only
                top = next((r for r in grp if r['pid'] == starter_qb), None) or max(grp, key=lambda r: r['snap'])
                top[key] += vac
                continue
            lead = next((r for r in grp if r['pid'] == lead_rb), None) if pos == 'RB' else None
            if lead is not None and vac > 0 and lead[key] < 0.85 * vac:
                add = 0.85 * vac - lead[key]
                lead[key] += add
                s = sum(r[key] for r in grp if r is not lead)
                for r in grp:
                    if r is not lead and s > 0:
                        r[key] *= min(2.0, 1 + (vac - add) / s)
                continue
            s = sum(r[key] for r in grp)
            if s > 0 and vac > 0:
                k = min(2.0, 1 + vac / s)
                for r in grp:
                    r[key] *= k
    lead = next((r for r in rows if r['pid'] == lead_rb and r['pos'] == 'RB'), None)
    if lead is not None:
        vs = sum(st.player_feats(pid, pos)['snap'] for pid, pos in out if pos == 'RB')
        lead['snap'] = min(0.8, max(lead['snap'], 0.85 * vs))
    for r in rows:
        for key in ('l_td', 'l_rz', 'l_gl', 'l_open', 'l_q1', 'l_tfirst'):
            r[key] = math.log(r[key] + 0.01)
        r['l_snap'] = math.log(r['snap'] + 0.05)
        r['QB'] = float(r['pos'] == 'QB'); r['WR'] = float(r['pos'] == 'WR'); r['TE'] = float(r['pos'] == 'TE')
    # QB: only the expected starter is a real candidate (backups rarely score); keep top-snap QB
    qbs = [r for r in rows if r['pos'] == 'QB']
    if len(qbs) > 1:
        keep = next((r for r in qbs if r['pid'] == starter_qb), None) or max(qbs, key=lambda r: r['snap'])
        rows = [r for r in rows if r['pos'] != 'QB' or r is keep]
    return rows


def pmat(rows):
    return np.array([[r[k] for k in PFEATS] for r in rows], float)


def drive_x(feats, n):
    return [float(n == 1), float(n == 2), feats['ln_imp'], feats['off'], feats['dfn'],
            feats['open_off'] * (n == 1), feats['open_def'] * (n == 1)]


def drive_prob(wd, feats, n):
    x = np.array(drive_x(feats, min(n, 3)))
    return float(sigmoid(wd[0] + x @ wd[1:]))


def chain(wd, fa, fb, q, pa_recv, n_drives):
    """P(A off first), P(B off first), P(non-off first), P(no TD)."""
    h1 = int(round(n_drives / 2)); h2 = int(round(n_drives)) - h1
    out = np.zeros(4)
    for recv_a, w in ((True, pa_recv), (False, 1 - pa_recv)):
        seq = []
        first = 'A' if recv_a else 'B'
        second = 'B' if recv_a else 'A'
        for k in range(h1):
            seq.append(first if k % 2 == 0 else second)
        for k in range(h2):
            seq.append(second if k % 2 == 0 else first)
        alive = 1.0
        cnt = Counter()
        res = np.zeros(4)
        for t in seq:
            cnt[t] += 1
            p = drive_prob(wd, fa if t == 'A' else fb, cnt[t])
            res[0 if t == 'A' else 1] += alive * p
            res[2] += alive * q
            alive *= (1 - p - q)
        res[3] = alive
        out += w * res
    return out


# ------------------------------------------------------------------ walk-forward engine
def walk(G, dg, pgm, eval_from=(2025, 1), fit_from=(2024, 4)):
    """Walk weeks in order. Before each eval week, refit both models on earlier rows. Returns per-game predictions."""
    st = State()
    weeks = sorted({(g['season'], g['week']) for g in G})
    by_week = defaultdict(list)
    for g in G:
        by_week[(g['season'], g['week'])].append(g)
    drows, prows = [], []      # training rows: (key, x, y) / (key, X, chosen)
    preds = []
    wd = wp = None
    for wk in weeks:
        games = by_week[wk]
        if wk >= eval_from:
            tr_d = [r for r in drows if r[0] < wk]
            tr_p = [r for r in prows if r[0] < wk]
            wd = ridge_logit(np.array([r[1] for r in tr_d]), np.array([r[2] for r in tr_d], float), lam=2.0)
            wp = clogit_fit([(r[1], r[2]) for r in tr_p], lam=1.0)
        for g in games:
            home, away = g['home'], g['away']
            pls = pgm[g['game_id']]
            fe = {t: st.team_feats(t, o, implied(g, t)) for t, o in ((home, away), (away, home))}
            cand = {}
            for t in (home, away):
                act = [(p['pid'], p['pos']) for p in pls if p['team'] == t and (p['snaps'] > 0 or p['car'] + p['tgt'] > 0)]
                qbs = [p for p in pls if p['team'] == t and p['pos'] == 'QB']
                sq = max(qbs, key=lambda p: p['snaps'])['pid'] if qbs else None
                cand[t] = candidates(st, t, act, sq)
            # training rows from this game (features known before it)
            if wk >= fit_from:
                for d in dg[g['game_id']]:
                    n = int(d['team_drive'])
                    if n <= MAX_TEAM_DRIVE:
                        drows.append((wk, drive_x(fe[d['team']], min(n, 3)), int(d['off_td'])))
                for t in (home, away):
                    rows = cand[t]
                    if not rows:
                        continue
                    scorer = [p['pid'] for p in pls if p['team'] == t and p['team_first_td']]
                    if not scorer:
                        continue
                    idx = [i for i, r in enumerate(rows) if r['pid'] == scorer[0]]
                    prows.append((wk, pmat(rows), idx[0] if idx else -1))
            if wk >= eval_from and wd is not None:
                pa = min(0.85, max(0.15, 0.5 + st.recv_tend(home) - st.recv_tend(away)))
                nd = st.pace(home) + st.pace(away)
                q = st.lg_non()
                ch = chain(wd, fe[home], fe[away], q, pa, nd)
                pr = dict(game=g, key=wk, p_home=ch[0], p_away=ch[1], p_non=ch[2], p_none=ch[3], p_home_recv=pa,
                          imp_home=implied(g, home), imp_away=implied(g, away), players=[])
                for t, pt in ((home, ch[0]), (away, ch[1])):
                    rows = cand[t]
                    if not rows:
                        continue
                    sh, oth = clogit_probs(wp, pmat(rows))
                    for r, s in zip(rows, sh):
                        pr['players'].append(dict(pid=r['pid'], team=t, pos=r['pos'], share=float(s), p=float(pt * s)))
                    pr.setdefault('other', {})[t] = float(oth)
                preds.append(pr)
        for g in games:
            st.update(g, dg[g['game_id']], pgm[g['game_id']])
    return preds, st, wd, wp, drows, prows


# ------------------------------------------------------------------ old (crude) method, for the backtest
def crude_preds():
    """td_charts.py method on top of the v2 anytime model (td_model.py), walk-forward. Keyed (season, week, gsis)."""
    import td_model as tm
    games = tm.load_games()
    pos = json.load(open(os.path.join(DATA, 'pos.json')))
    hist, st = tm.build_history(games, pos)
    keys = sorted({r['key'] for r in hist})
    keys = [k for k in keys if (int(k[0]), int(k[1])) >= (2025, 1)]
    pr = tm.fit_predict(hist, keys, tm.FEATS)
    # espn -> gsis
    e2g = {}
    for y in (2025, 2026):
        for r in csv.DictReader(open(os.path.join(RAW, f'roster_{y}.csv'))):
            if r['espn_id'] and r['gsis_id']:
                e2g[r['espn_id']] = r['gsis_id']
    team_rows = defaultdict(list)
    for r in hist:
        if id(r) not in pr or not r['imp']:
            continue
        p = pr[id(r)]
        if r['backup']:
            qf = tm.qb_factor(st.qbrows, before=r['key'])
            p = tm.apply_qb(p, r['pos'], qf)
        team_rows[(int(r['key'][0]), int(r['key'][1]), r['team'])].append(dict(gsis=e2g.get(r['id']), p=p, imp=r['imp']))
    # opponent implied from ESPN odds: find game
    out = {}
    for gid, g in games.items():
        s, w = int(g['season']), int(g['week'])
        odds = g.get('odds')
        if not odds:
            continue
        imps = {t: tm.implied(odds, t, g['home']) for t in g['teams']}
        for t in g['teams']:
            lst = team_rows.get((s, w, t))
            if not lst:
                continue
            o = [x for x in g['teams'] if x != t][0]
            lam = imps[t] * 0.11
            L = (imps[t] + imps[o]) * 0.11
            for x in lst:
                x['rate'] = -math.log(1 - min(x['p'], 0.95))
            ssum = sum(x['rate'] for x in lst)
            k = min(1.0, 0.85 * lam / ssum) if ssum else 1
            for x in lst:
                if x['gsis']:
                    out[(s, w, x['gsis'])] = x['rate'] * k / L * (1 - math.exp(-L))
            out[(s, w, 'TEAM', {'LAR': 'LA', 'WSH': 'WAS'}.get(t, t))] = imps[t] / (imps[t] + imps[o]) * (1 - math.exp(-L))
    return out


# ------------------------------------------------------------------ backtest report
def ll(y, p, lo=0.002):
    p = np.clip(np.array(p, float), lo, 1 - lo); y = np.array(y, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def bucket_table(y, p, edges=(0, .03, .06, .09, .12, .15, .20, 1.01)):
    y, p = np.array(y, float), np.array(p, float)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (p >= a) & (p < b)
        if m.sum():
            out.append((f'{a * 100:.0f}-{b * 100:.0f}%' if b < 1 else f'{a * 100:.0f}%+', int(m.sum()), float(p[m].mean()), float(y[m].mean())))
    return out


def backtest():
    G, dg, pgm = load_tables()
    preds, st, wd, wp, _, _ = walk(G, dg, pgm)
    crude = crude_preds()
    L = []
    res = {}
    kinds = Counter(pr['game']['first_td_kind'] for pr in preds)
    n = len(preds)
    L.append(f'NFL first TD chain model backtest (walk-forward, 2025 Weeks 1-18 + 2026 Weeks 1-10, n={n} games)')
    L.append('Training: 2024 Week 4 on, refit before every week on earlier weeks only. Active players = played that game.')
    L.append('')
    L.append('First TD type: ' + ', '.join(f'{k} {v} ({v / n * 100:.1f}%)' for k, v in kinds.most_common()))
    non = sum(v for k, v in kinds.items() if k not in OFF_KINDS)
    L.append(f'Non-offensive or no TD first (every player bet loses): {non} ({non / n * 100:.1f}%). '
             f'Model average: {np.mean([p["p_non"] + p["p_none"] for p in preds]) * 100:.1f}%')
    recv_first = [pr for pr in preds if pr['game']['first_td_kind'] in OFF_KINDS]
    rf = sum(pr['game']['first_td_team'] == pr['game']['recv'] for pr in recv_first)
    L.append(f'Opening kickoff receiver scored the first offensive TD: {rf}/{len(recv_first)} ({rf / len(recv_first) * 100:.1f}%)')
    L.append('')

    def evaluate(sub, label, with_crude):
        out = {}
        # team level
        ty, tp, tc = [], [], []
        fav_hit = fav_n = cfav_hit = 0
        for pr in sub:
            g = pr['game']; ft = g['first_td_team'] if g['first_td_kind'] in OFF_KINDS else None
            probs = [pr['p_home'], pr['p_away'], pr['p_non'] + pr['p_none']]
            idx = 0 if ft == g['home'] else 1 if ft == g['away'] else 2
            ty.append(-math.log(max(probs[idx], 1e-3)))
            if ft:
                fav = g['home'] if pr['p_home'] >= pr['p_away'] else g['away']
                fav_n += 1; fav_hit += int(fav == ft)
                if with_crude:
                    ch = crude.get((g['season'], g['week'], 'TEAM', g['home'])); ca = crude.get((g['season'], g['week'], 'TEAM', g['away']))
                    cf = g['home'] if (ch or 0) >= (ca or 0) else g['away']
                    cfav_hit += int(cf == ft)
            if with_crude:
                ch = crude.get((g['season'], g['week'], 'TEAM', g['home'])); ca = crude.get((g['season'], g['week'], 'TEAM', g['away']))
                cp = [ch, ca, max(1e-3, 1 - ch - ca)]
                tc.append(-math.log(max(cp[idx], 1e-3)))
        out['team_ll'] = float(np.mean(ty)); out['fav'] = (fav_hit, fav_n)
        if with_crude:
            out['team_ll_crude'] = float(np.mean(tc)); out['fav_crude'] = (cfav_hit, fav_n)
        # player level
        yn, pn, yc, pc, yc_new = [], [], [], [], []
        top = {1: 0, 2: 0, 3: 0}; ctop = {1: 0, 2: 0, 3: 0}
        cat_new, cat_crude = [], []
        for pr in sub:
            g = pr['game']
            scorer = g['first_td_pid'] if g['first_td_kind'] in OFF_KINDS else None
            pl = sorted(pr['players'], key=lambda x: -x['p'])
            for x in pl:
                yn.append(int(x['pid'] == scorer)); pn.append(x['p'])
            got = [x['p'] for x in pl if x['pid'] == scorer]
            cat_new.append(-math.log(max(got[0] if got else 1 - sum(x['p'] for x in pl), 1e-3)))
            for k in top:
                top[k] += int(scorer in [x['pid'] for x in pl[:k]])
            if with_crude:
                cl = []
                for x in pl:
                    c = crude.get((g['season'], g['week'], x['pid']))
                    if c is not None:
                        yc.append(int(x['pid'] == scorer)); pc.append(c); yc_new.append(x['p']); cl.append((c, x['pid']))
                cl.sort(reverse=True)
                for k in ctop:
                    ctop[k] += int(scorer in [pid for _, pid in cl[:k]])
        out['n'] = len(sub)
        out['player_ll'] = ll(yn, pn); out['calib'] = bucket_table(yn, pn); out['top'] = top
        out['scorer_ll'] = float(np.mean(cat_new))
        if with_crude:
            out['common_n'] = len(yc)
            out['common_ll_new'] = ll(yc, yc_new); out['common_ll_crude'] = ll(yc, pc)
            out['common_brier_new'] = float(np.mean((np.array(yc_new) - np.array(yc)) ** 2))
            out['common_brier_crude'] = float(np.mean((np.array(pc) - np.array(yc)) ** 2))
            out['calib_crude'] = bucket_table(yc, pc); out['calib_new_common'] = bucket_table(yc, yc_new); out['ctop'] = ctop
        return out

    def section(label, sub, with_crude):
        ev = evaluate(sub, label, with_crude)
        n = ev['n']
        L.append(f'== {label} ({n} games) ==')
        L.append(f"Team that scores first (3 outcomes: home, away, non-offense/none), log loss: chain {ev['team_ll']:.4f}"
                 + (f"   old {ev['team_ll_crude']:.4f}" if with_crude else ''))
        fh, fn = ev['fav']
        L.append(f'Favored team scored the first offensive TD: {fh}/{fn} ({fh / fn * 100:.1f}%)'
                 + (f"   old: {ev['fav_crude'][0]}/{fn} ({ev['fav_crude'][0] / fn * 100:.1f}%)" if with_crude else ''))
        L.append(f"Top-1 / top-2 / top-3 per game contains the first TD scorer: "
                 + ' / '.join(f"{ev['top'][k]} ({ev['top'][k] / n * 100:.1f}%)" for k in (1, 2, 3))
                 + (('   old: ' + ' / '.join(f"{ev['ctop'][k]} ({ev['ctop'][k] / n * 100:.1f}%)" for k in (1, 2, 3))) if with_crude else ''))
        L.append(f"Player log loss (every active skill player): {ev['player_ll']:.4f}; scorer log loss per game: {ev['scorer_ll']:.3f}")
        if with_crude:
            L.append(f"Same players, both models (n={ev['common_n']}): log loss chain {ev['common_ll_new']:.4f} vs old {ev['common_ll_crude']:.4f}; "
                     f"Brier {ev['common_brier_new']:.5f} vs {ev['common_brier_crude']:.5f}")
        L.append('Calibration (predicted first TD chance vs actual):')
        L.append('  bucket     chain n  pred / act' + ('            old n  pred / act' if with_crude else ''))
        cn = ev['calib_new_common'] if with_crude else ev['calib']
        cc = {b[0]: b for b in ev.get('calib_crude', [])}
        for b in cn:
            line = f'  {b[0]:9s} {b[1]:7d}  {b[2] * 100:4.1f}% / {b[3] * 100:4.1f}%'
            if with_crude:
                c = cc.get(b[0])
                line += f'        {c[1]:7d}  {c[2] * 100:4.1f}% / {c[3] * 100:4.1f}%' if c else '        -'
            L.append(line)
        for b in cc:
            if b not in {x[0] for x in cn}:
                c = cc[b]; L.append(f'  {b:9s}       -                   {c[1]:7d}  {c[2] * 100:4.1f}% / {c[3] * 100:4.1f}%')
        L.append('')
        return ev

    s25 = [p for p in preds if p['key'][0] == 2025]
    s26 = [p for p in preds if p['key'][0] == 2026]
    res['all'] = section('All: 2025 + 2026 Weeks 1-10, chain model only', preds, False)
    res['2025'] = section('2025 Weeks 1-18, chain model only', s25, False)
    res['2026'] = section('2026 Weeks 1-10, chain model only', s26, False)
    common = [p for p in preds if (p['key'][0], p['key'][1], 'TEAM', p['game']['home']) in crude
              and (p['key'][0], p['key'][1], 'TEAM', p['game']['away']) in crude]
    wks = sorted({p['key'] for p in common})
    lab = f"Head to head vs old method (td_charts.py on TD model v2), games where both exist: {wks[0][0]} Wk {wks[0][1]} to {wks[-1][0]} Wk {wks[-1][1]}"
    res['h2h'] = section(lab, common, True)
    # calibration of the team model
    tb = bucket_table([int(pr['game']['first_td_team'] == pr['game']['home'] and pr['game']['first_td_kind'] in OFF_KINDS) for pr in preds] +
                      [int(pr['game']['first_td_team'] == pr['game']['away'] and pr['game']['first_td_kind'] in OFF_KINDS) for pr in preds],
                      [pr['p_home'] for pr in preds] + [pr['p_away'] for pr in preds], edges=(0, .35, .42, .48, .54, .60, .66, 1.01))
    L.append('Team first TD calibration (chain, all games): ' + '; '.join(f'{b[0]} n={b[1]} {b[2] * 100:.0f}%/{b[3] * 100:.0f}%' for b in tb))
    # team-first-TD scorer (share) top-2 hit
    th = tn = 0
    for pr in preds:
        g = pr['game']
        for t in (g['home'], g['away']):
            pl = sorted([x for x in pr['players'] if x['team'] == t], key=lambda x: -x['share'])
            sc = [p['pid'] for p in pgm[g['game_id']] if p['team'] == t and p['team_first_td']]
            if sc and pl:
                tn += 1; th += int(sc[0] in [x['pid'] for x in pl[:2]])
    L.append(f'Team first TD scorer (team market): our top 2 per team hit {th}/{tn} ({th / tn * 100:.1f}%)')
    L.append('')
    L.append('Drive model weights (last fit): ' + ', '.join(f'{k} {v:+.3f}' for k, v in zip(['const'] + DFEATS, wd)))
    L.append('Player share weights (last fit): ' + ', '.join(f'{k} {v:+.3f}' for k, v in zip(['other'] + PFEATS, wp)))
    txt = '\n'.join(L)
    print(txt)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'first_td_backtest.txt'), 'w').write(txt + '\n')
    slim = {k: {kk: vv for kk, vv in v.items()} for k, v in res.items()}
    json.dump(slim, open(os.path.join(OUT, 'first_td_backtest.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['backtest', 'week'])
    ap.add_argument('--week', type=int, default=11)
    ap.add_argument('--season', type=int, default=2026)
    a = ap.parse_args()
    if a.mode == 'backtest':
        backtest()
    else:
        import first_td_week
        first_td_week.run(a.season, a.week)
