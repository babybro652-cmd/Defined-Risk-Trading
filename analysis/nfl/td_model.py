#!/usr/bin/env python3
"""NFL anytime-TD model (v2, built 11/8/26).

Old method: a player's 2025+2026 hit rate (games with a rushing or receiving TD / games played).
New method (everything uses only games played before the game being scored):
  1. Shrink the hit rate toward a prior for players at the same position with similar usage
     (red-zone + inside-5 opportunities per game), weighted by games played: (hits + K*prior)/(gp + K).
  2. Vegas implied team total (from ESPN spread and total) vs the league average.
  3. Goal-line share: the player's share of his team's inside-5 carries + targets.
  4. Red-zone share (all) and red-zone TARGET share (WR/TE) of his team.
  5. A logistic regression (ridge) on those features, refit before each week on earlier games only, so the
     output is a calibrated chance.
  6. Automatic QB-change cut: when the team's starting QB is out and a backup / third-stringer starts, the
     chance is cut by a factor estimated from 2025-26 backup-QB games (team TDs vs the implied total).

Run `python3 analysis/nfl/td_model.py` for the backtest (writes out/td_backtest.json and prints the report).
build_tracker.py imports build_history / State / predict for the Week Shortlist.
"""
import json, math, os, sys
from collections import defaultdict, Counter, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'out')

K_SHRINK = 6.0            # pseudo-games in the shrink toward the usage prior
SHARE_PSEUDO = 8.0        # pseudo team opportunities added to every share denominator (shrinks small samples toward 0)
BACKUP_MAX_ATT = 150      # a starter with fewer prior pass attempts (2025-26) than this counts as a backup / third string
QB_WINDOW = 17            # team games used to name the team's primary QB
QB_PRIOR_GAMES = 10.0     # pseudo team-games at factor 1.0 in the QB-change factor
USAGE_BINS = [0.34, 1.0, 2.0, 3.5]
FEATS = ['logit_sh', 'ln_imp', 'gls', 'rzs', 'rzts', 'bqb', 'QB', 'WR', 'TE']
FEATS_NOQB = [f for f in FEATS if f != 'bqb']
ADOPT_NEW = True          # set from the backtest result (see README "TD model v2")


def pg(pos):
    return 'RB' if pos in ('RB', 'FB') else pos


def load_games():
    g = {}
    for y in (2025, 2026):
        p = os.path.join(DATA, f'games_{y}.json')
        if os.path.exists(p):
            g.update(json.load(open(p)))
    return g


def implied(odds, team, home):
    """Implied team total from the pregame spread (home perspective, negative = home favored) and total."""
    if not odds:
        return None
    t, s = odds['total'], odds['spread']
    return t / 2 - s / 2 if team == home else t / 2 + s / 2


def logit(p):
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def usage_bin(u):
    for i, e in enumerate(USAGE_BINS):
        if u < e:
            return i
    return len(USAGE_BINS)


class State:
    """Running pre-game knowledge. update(game) after scoring a game; features(...) before it."""

    def __init__(self, pos):
        self.pos = pos
        self.p = defaultdict(lambda: dict(gp=0, hits=0, rz=0, i5=0, team=None, sg=0, ti5=0, trz=0, trzt=0, prz_t=0))
        self.tier = defaultdict(lambda: [0, 0])      # (posgroup, bin) -> [games, hit games]
        self.posrate = defaultdict(lambda: [0, 0])
        self.qbatt = Counter()                       # prior pass attempts, any team
        self.qbteam = defaultdict(lambda: deque(maxlen=QB_WINDOW))  # team -> deque of {qbid: att}
        self.tot_sum, self.tot_n = 0.0, 0            # league average implied team total
        self.qbrows = []                             # team-games for the QB-change factor: (key, backup, td, implied, pos-group tds)

    # ---- knowledge
    def avg_imp(self):
        return self.tot_sum / self.tot_n if self.tot_n else 22.5

    def prior(self, pos, u):
        n, h = self.tier[(pos, usage_bin(u))]
        pn, ph = self.posrate[pos]
        base = ph / pn if pn else 0.15
        return (h + 5 * base) / (n + 5)

    def primary_qb(self, team):
        c = Counter()
        for d in self.qbteam[team]:
            c.update(d)
        return c.most_common(1)[0][0] if c else None, len(self.qbteam[team])

    def backup_start(self, team, starter):
        prim, n = self.primary_qb(team)
        if prim is None or n < 3 or starter is None:
            return False
        return starter != prim and self.qbatt[starter] < BACKUP_MAX_ATT

    def features(self, aid, team, imp):
        s = self.p[aid]
        gp = s['gp']
        pos = pg(self.pos.get(aid, '?'))
        u = (s['rz'] + s['i5']) / gp if gp else 0.0
        psh = (s['hits'] + K_SHRINK * self.prior(pos, u)) / (gp + K_SHRINK)
        gls = s['i5'] / (s['ti5'] + SHARE_PSEUDO)
        rzs = s['rz'] / (s['trz'] + SHARE_PSEUDO)
        rzts = s['prz_t'] / (s['trzt'] + SHARE_PSEUDO) if pos in ('WR', 'TE') else 0.0
        ln_imp = math.log(imp / self.avg_imp()) if imp else 0.0
        return dict(gp=gp, pos=pos, old=s['hits'] / gp if gp else 0.0, p_sh=psh, logit_sh=logit(psh), ln_imp=ln_imp,
                    gls=gls, rzs=rzs, rzts=rzts, QB=int(pos == 'QB'), WR=int(pos == 'WR'), TE=int(pos == 'TE'), bqb=0,
                    imp=imp, usage=u, i5g=s['i5'] / gp if gp else 0.0, rzg=s['rz'] / gp if gp else 0.0)

    def update(self, g):
        teams = g['teams']
        tot = {t: dict(i5=0, rz=0, rzt=0, td=0, skill=defaultdict(int)) for t in teams}
        for r in g['rows']:
            t = tot.get(r['team'])
            if t is None:
                continue
            t['i5'] += r['i5']; t['rz'] += r['rz']; t['rzt'] += r.get('rzt', 0)
            t['td'] += r['rectd'] + r['rushtd']
            t['skill'][pg(self.pos.get(r['id'], '?'))] += r['rectd'] + r['rushtd']
        for r in g['rows']:
            if r['team'] not in tot:
                continue
            s = self.p[r['id']]
            pos = pg(self.pos.get(r['id'], '?'))
            if s['gp']:
                u = (s['rz'] + s['i5']) / s['gp']
                b = self.tier[(pos, usage_bin(u))]; b[0] += 1; b[1] += int(r['rectd'] + r['rushtd'] > 0)
                pr = self.posrate[pos]; pr[0] += 1; pr[1] += int(r['rectd'] + r['rushtd'] > 0)
            if s['team'] != r['team']:
                s.update(team=r['team'], sg=0, ti5=0, trz=0, trzt=0, i5=0, rz=0, prz_t=0)  # new team: share restarts
            t = tot[r['team']]
            s['gp'] += 1; s['hits'] += int(r['rectd'] + r['rushtd'] > 0)
            s['rz'] += r['rz']; s['i5'] += r['i5']; s['prz_t'] += r.get('rzt', 0)
            s['ti5'] += t['i5']; s['trz'] += t['rz']; s['trzt'] += t['rzt']
        odds = g.get('odds')
        for team in teams:
            qs = g.get('qbs', {}).get(team, [])
            starter = qs[0][0] if qs else None
            imp = implied(odds, team, g['home'])
            if imp:
                self.tot_sum += imp; self.tot_n += 1
            self.qbrows.append(dict(key=(g['season'], g['week']), backup=self.backup_start(team, starter), td=tot[team]['td'],
                                    imp=imp, skill=dict(tot[team]['skill']), team=team, starter=starter))
            self.qbteam[team].append({q[0]: q[2] for q in qs})
            for q in qs:
                self.qbatt[q[0]] += q[2]


def qb_factor(qbrows, before=None):
    """Backup-QB TD factor from team games before `before` (a (season, week) key). Returns dict of factors + counts."""
    rows = [r for r in qbrows if r['imp'] and (before is None or r['key'] < before)]
    norm = [r for r in rows if not r['backup']]
    bk = [r for r in rows if r['backup']]
    out = dict(n_backup=len(bk), n_norm=len(norm))
    if not norm:
        return dict(out, raw=1.0, factor=1.0, WR=1.0, TE=1.0, RB=1.0, QB=1.0)
    for grp in ('ALL', 'RB', 'WR', 'TE', 'QB'):
        def td(r):
            return r['td'] if grp == 'ALL' else r['skill'].get(grp, 0)
        rate = sum(td(r) for r in norm) / sum(r['imp'] for r in norm)   # TDs per implied point in normal games
        if not bk:
            out[grp] = 1.0; out['raw' if grp == 'ALL' else grp + '_raw'] = 1.0
            continue
        exp_b = rate * sum(r['imp'] for r in bk)
        act_b = sum(td(r) for r in bk)
        pseudo = QB_PRIOR_GAMES * 22.5 * rate
        f = (act_b + pseudo) / (exp_b + pseudo)
        out[grp] = f
        out['raw' if grp == 'ALL' else grp + '_raw'] = act_b / exp_b if exp_b else 1.0
        out[grp + '_act' if grp != 'ALL' else 'act'] = act_b
        out[grp + '_exp' if grp != 'ALL' else 'exp'] = exp_b
    out['factor'] = out['ALL']
    return out


def ridge_fit(X, y, lam=2.0, iters=30):
    n, d = X.shape
    Xb = np.hstack([np.ones((n, 1)), X])
    w = np.zeros(d + 1)
    R = np.eye(d + 1) * lam; R[0, 0] = 0
    for _ in range(iters):
        z = Xb @ w; p = sigmoid(z)
        g = Xb.T @ (p - y) + R @ w
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb + R
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-7:
            break
    return w


def design(rows, feats):
    return np.array([[r[f] for f in feats] for r in rows], dtype=float)


def predict_w(w, rows, feats):
    X = design(rows, feats)
    return sigmoid(w[0] + X @ w[1:])


def build_history(games, pos):
    """Walk every game in time order. Returns (rows with features + outcome, final State)."""
    st = State(pos)
    slots = defaultdict(list)
    for gid, g in games.items():
        slots[(g['season'], g['week'])].append(g)
    hist = []
    for key in sorted(slots):
        for g in slots[key]:
            for r in g['rows']:
                team = r['team']
                if team not in g['teams']:
                    continue
                f = st.features(r['id'], team, implied(g.get('odds'), team, g['home']))
                if f['gp'] == 0:
                    continue
                qs = g.get('qbs', {}).get(team, [])
                bk = st.backup_start(team, qs[0][0] if qs else None)
                f.update(key=key, id=r['id'], name=r['name'], team=team, opp=r['opp'], y=int(r['rectd'] + r['rushtd'] > 0),
                         backup=bk, bqb=int(bk), gid=g.get('gid'))
                hist.append(f)
        for g in slots[key]:
            st.update(g)
    return hist, st


def log_loss(y, p, lo=0.03, hi=0.97):
    p = np.clip(p, lo, hi)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(y, p):
    return float(np.mean((p - y) ** 2))


def fit_predict(hist, eval_keys, feats, min_train=400, lam=2.0, min_gp=3):
    """Walk-forward: for each eval key fit on rows with earlier keys (gp>=min_gp) and predict that key's rows."""
    preds = {}
    for k in eval_keys:
        tr = [r for r in hist if r['key'] < k and r['gp'] >= min_gp]
        te = [r for r in hist if r['key'] == k and r['gp'] >= min_gp]
        if len(tr) < min_train or not te:
            continue
        w = ridge_fit(design(tr, feats), np.array([r['y'] for r in tr], float), lam)
        pp = predict_w(w, te, feats)
        for r, p in zip(te, pp):
            preds[id(r)] = float(p)
    return preds


def apply_qb(p, pos, qf):
    f = qf.get(pos, qf['factor'])
    return 1 - (1 - p) ** f


def bucket_table(y, p, edges=(0, .1, .2, .3, .4, .5, .6, 1.01)):
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (p >= a) & (p < b)
        if m.sum():
            out.append((f'{int(a*100)}-{min(int(b*100),100)}%', int(m.sum()), float(p[m].mean()), float(y[m].mean())))
    return out


def evaluate(hist, state, label, eval_keys, min_gp=3):
    res = {}
    models = {
        'shrink only': ['logit_sh', 'QB', 'WR', 'TE'],
        '+ implied total': ['logit_sh', 'ln_imp', 'QB', 'WR', 'TE'],
        '+ goal-line share': ['logit_sh', 'ln_imp', 'gls', 'QB', 'WR', 'TE'],
        '+ RZ shares': FEATS_NOQB,
        'full (v2, + QB cut)': FEATS,
    }
    preds = {n: fit_predict(hist, eval_keys, f, min_gp=min_gp) for n, f in models.items()}
    base_ids = set(preds['full (v2, + QB cut)'])
    rows = [r for r in hist if id(r) in base_ids]
    y = np.array([r['y'] for r in rows], float)
    old = np.array([r['old'] for r in rows])
    out = dict(label=label, n=len(rows), base_rate=float(y.mean()), old=dict(ll=log_loss(y, old), br=brier(y, old)))
    out['models'] = {}
    for n in models:
        p = np.array([preds[n][id(r)] for r in rows])
        out['models'][n] = dict(ll=log_loss(y, p), br=brier(y, p))
    pf = np.array([preds['full (v2, + QB cut)'][id(r)] for r in rows])
    pn = np.array([preds['+ RZ shares'][id(r)] for r in rows])
    bk = np.array([r['backup'] for r in rows])
    out['qb_effect'] = dict(n=int(bk.sum()), with_flag=float(pf[bk].mean()) if bk.any() else 0, without=float(pn[bk].mean()) if bk.any() else 0,
                            actual=float(y[bk].mean()) if bk.any() else 0)
    out['final_p'] = pf
    out['n_backup_rows'] = int(sum(r['backup'] for r in rows))
    out['rows'] = rows
    out['y'] = y
    out['old_p'] = old
    return out


def report(ev):
    y, pn, po, rows = ev['y'], ev['final_p'], ev['old_p'], ev['rows']
    lines = [f"{ev['label']}: {ev['n']} player-games, base TD rate {ev['base_rate']*100:.1f}%, backup-QB rows {ev['n_backup_rows']}",
             f"  log-loss  old hit rate {ev['old']['ll']:.4f}   " + '   '.join(f"{k} {v['ll']:.4f}" for k, v in ev['models'].items()),
             f"  Brier     old hit rate {ev['old']['br']:.4f}   " + '   '.join(f"{k} {v['br']:.4f}" for k, v in ev['models'].items())]
    lines.append('  calibration (new):')
    for b in bucket_table(y, pn):
        lines.append(f'    {b[0]:>8} n={b[1]:4d} predicted {b[2]*100:4.1f}% actual {b[3]*100:4.1f}%')
    lines.append('  calibration (old hit rate):')
    for b in bucket_table(y, po):
        lines.append(f'    {b[0]:>8} n={b[1]:4d} predicted {b[2]*100:4.1f}% actual {b[3]*100:4.1f}%')
    return lines


def pick_stats(ev, thr_new=0.40, thr_old=0.40, topn=None):
    """Hit rate of 'picks' by position: players whose chance is at/above the threshold."""
    rows, y = ev['rows'], ev['y']
    res = {}
    for name, p, thr in (('new', ev['final_p'], thr_new), ('old', ev['old_p'], thr_old)):
        d = {}
        for grp, sel in (('RB/QB', lambda r: r['pos'] in ('RB', 'QB')), ('WR/TE', lambda r: r['pos'] in ('WR', 'TE'))):
            idx = [i for i, r in enumerate(rows) if sel(r) and p[i] >= thr]
            d[grp] = (len(idx), int(sum(y[i] for i in idx)), float(np.mean([p[i] for i in idx])) if idx else 0.0)
        res[name] = d
    return res


def top_weekly(ev, n=10):
    """Each week's top-n by chance: hits and mean chance."""
    rows, y = ev['rows'], ev['y']
    out = {}
    for name, p in (('new', ev['final_p']), ('old', ev['old_p'])):
        h = tot = 0; ps = []
        for k in sorted({r['key'] for r in rows}):
            idx = [i for i, r in enumerate(rows) if r['key'] == k]
            idx.sort(key=lambda i: -p[i])
            for i in idx[:n]:
                h += int(y[i]); tot += 1; ps.append(p[i])
        out[name] = (h, tot, float(np.mean(ps)))
    return out


# ---------------------------------------------------------------- live (Week Shortlist) helpers
def fit_final(hist, min_gp=3, lam=2.0):
    tr = [r for r in hist if r['gp'] >= min_gp]
    return ridge_fit(design(tr, FEATS), np.array([r['y'] for r in tr], float), lam)


def chance(w, f):
    z = w[0] + sum(w[1 + i] * f[k] for i, k in enumerate(FEATS))
    return float(sigmoid(z))


def fair_american(p):
    p = min(max(p, 0.01), 0.99)
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def _to_dec(a):
    return 1 + a / 100 if a > 0 else 1 + 100 / -a


def take_at(p):
    """Fair price with the profit stretched 20% (Tim's take-at rule): +300 fair -> +360."""
    prof = (1 / min(max(p, 0.01), 0.99) - 1) * 1.2
    return round(prof * 100) if prof >= 1 else round(-100 / prof)


def fmt_price(a):
    return f'+{a}' if a > 0 else str(a)


OUT_STATUSES = ('Out', 'Out (inactive)', 'IR', 'Doubtful', 'Suspension')


def live_qb(st, team, depth_ids, qb_status, names):
    """Return (backup_flag, note). depth_ids = QB athlete ids in depth-chart order (may be empty);
    qb_status = {athlete id: status string} from the injuries feed."""
    prim, n = st.primary_qb(team)
    last = st.qbteam[team][-1] if st.qbteam[team] else {}
    last_starter = max(last, key=last.get) if last else None
    order = list(depth_ids) or [x for x in (prim, last_starter) if x]
    start = None
    for q in order:
        if qb_status.get(q, 'Active') not in OUT_STATUSES:
            start = q; break
    if start is None:
        return True, 'every listed QB is out'
    if prim is None or n < 3:
        return False, ''
    nm = names.get(start, start)
    if start != prim and st.qbatt[start] < BACKUP_MAX_ATT:
        pn = names.get(prim, prim)
        why = f'{pn} {qb_status.get(prim, "")}'.strip() if qb_status.get(prim, 'Active') in OUT_STATUSES else f'{pn} not the listed starter'
        return True, f'backup QB {nm} expected to start ({why})'
    if qb_status.get(prim, 'Active') == 'Questionable':
        return False, f'{names.get(prim, prim)} questionable (no cut applied; if he sits the chance drops about 9%)'
    return False, ''


def main():
    games = load_games()
    pos = json.load(open(os.path.join(DATA, 'pos.json')))
    hist, st = build_history(games, pos)
    keys26 = sorted({r['key'] for r in hist if r['key'][0] == 2026 and 2 <= r['key'][1] <= 9})
    keys25 = sorted({r['key'] for r in hist if r['key'][0] == 2025 and r['key'][1] >= 7})
    res = {}
    lines = []
    for label, keys, mt in (('2026 Weeks 2-9 (trained on 2025 + earlier 2026)', keys26, 400),
                            ('2025 Weeks 7-18 (trained on earlier 2025 only)', keys25, 400)):
        ev = evaluate(hist, st, label, keys)
        lines += report(ev)
        ps = pick_stats(ev)
        lines.append('  picks at 40%+ chance (n, hits, avg predicted):')
        for nm in ('new', 'old'):
            lines.append(f"    {nm}: RB/QB {ps[nm]['RB/QB'][0]} bets, {ps[nm]['RB/QB'][1]} hit ({ps[nm]['RB/QB'][2]*100:.0f}% avg est)   "
                         f"WR/TE {ps[nm]['WR/TE'][0]} bets, {ps[nm]['WR/TE'][1]} hit ({ps[nm]['WR/TE'][2]*100:.0f}% avg est)")
        tw = top_weekly(ev)
        lines.append('  weekly top 10 by chance: ' + '   '.join(f"{k}: {v[0]}/{v[1]} ({v[0]/v[1]*100:.0f}%, est {v[2]*100:.0f}%)" for k, v in tw.items()))
        lines.append('')
        lines.append('  backup-QB rows: n=%d, model with flag %.1f%%, without flag %.1f%%, actual %.1f%%' % (ev['qb_effect']['n'], ev['qb_effect']['with_flag']*100, ev['qb_effect']['without']*100, ev['qb_effect']['actual']*100))
        res[label] = dict(n=ev['n'], qb_effect=ev['qb_effect'], base=ev['base_rate'], old=ev['old'], models=ev['models'], picks=ps, top10=tw,
                          calib_new=bucket_table(ev['y'], ev['final_p']), calib_old=bucket_table(ev['y'], ev['old_p']))
    qf = qb_factor(st.qbrows)
    lines.append('QB-change factor (all 2025-26 backup-QB team games): ' + json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in qf.items()}))
    print('\n'.join(lines))
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(res=res, qb=qf), open(os.path.join(OUT, 'td_backtest.json'), 'w'), indent=1)
    open(os.path.join(OUT, 'td_backtest.txt'), 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
