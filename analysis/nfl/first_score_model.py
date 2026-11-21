#!/usr/bin/env python3
"""NFL first scoring play model (team + type), built 11/21/26.

FanDuel "First Scoring Play" market: "<Team> Touchdown", "<Team> Field Goal", "Safety" (any team), plus "No score".
A TD here is any TD by that team (offense, defense or special teams), as the market counts it.

Extends the first TD drive chain (first_td_model.py). Each drive ends in one of:
  own TD (offense, or own kick return), made FG, opponent TD (pick six, fumble or punt return), safety, no score.
- Offensive TD chance: the first TD ridge logistic (unchanged).
- FG chance given no TD on the drive: a second ridge logistic on implied team total, the team's shrunk FG rate per
  non-TD drive, the opponent's FG rate allowed, red-zone stall rates (FG share of red-zone trips that scored, offense
  and defense), team kicking over expected (makes minus distance-based expected makes), dome / closed roof, the team's
  TD-rate terms, and team drive 1 / 2 dummies.
- Opponent TD, own return TD and safety per drive: shrunk league rates.
Drives alternate from the opening kickoff (50/50 plus receive habit) and the second half flips, as in the TD chain.
Output per game: P(A TD, A FG, B TD, B FG, safety, no score). Fair = 1 / p, take-at = fair decimal x1.2.

Baselines in the backtest (walk-forward, same games):
  B1 "spread": P(home scores first) = logistic on the spread; type split = league TD / FG / safety rates.
  B2 "spread + total": same, plus the TD share of a team's first score from a logistic on its implied total.

Run:
  python3 analysis/nfl/first_score_model.py build      # data/fs_drives.csv, data/fs_games.csv from raw/pbp_*.csv.gz
  python3 analysis/nfl/first_score_model.py backtest   # out/first_score_backtest.txt / .json
  python3 analysis/nfl/first_score_week.py --week 11   # live prices + chart
"""
import argparse, csv, gzip, json, math, os, sys
from collections import defaultdict, Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import first_td_model as m  # noqa

DATA, RAW, OUT = m.DATA, m.RAW, m.OUT
OUTCOMES = ['home_td', 'home_fg', 'away_td', 'away_fg', 'safety', 'none']
FFEATS = ['d1', 'd2', 'ln_imp', 'fg_off', 'fg_def', 'stall_off', 'stall_def', 'kick_oe', 'dome', 'off', 'dfn']
K_FG = 40.0       # pseudo non-TD drives in FG-rate shrink
K_RZ = 15.0       # pseudo red-zone scoring trips in stall-rate shrink
K_KICK = 15.0     # pseudo attempts in kicking-over-expected shrink
DECAY = m.DECAY_T
OVERROUND = 1.18  # assumed FanDuel hold on the 6-way first scoring play market (no price history; see README)


# ------------------------------------------------------------------ data
def fg_expect(dist):
    """League make chance by kick distance (2024-26 NFL, smooth fit)."""
    return 1 / (1 + math.exp(-(6.3 - 0.105 * dist)))


def build(seasons=(2024, 2025, 2026)):
    drives, games = [], []
    for y in seasons:
        rows = defaultdict(list)
        with gzip.open(os.path.join(RAW, f'pbp_{y}.csv.gz'), 'rt') as fh:
            for r in csv.DictReader(fh):
                if r['season_type'] == 'REG':
                    rows[r['game_id']].append(r)
        for gid, plays in rows.items():
            g0 = plays[0]
            home, away = g0['home_team'], g0['away_team']
            first = None
            dinfo, order = {}, []
            for r in plays:
                # game first scoring play
                if first is None:
                    if r['touchdown'] == '1' and r['td_team']:
                        off = r['td_team'] == r['posteam'] and r['special_teams_play'] != '1' and r['play_type'] in ('run', 'pass', 'qb_kneel', 'qb_spike', '')
                        first = dict(team=r['td_team'], type='TD', off=int(off), qtr=r['qtr'])
                    elif r['field_goal_result'] == 'made':
                        first = dict(team=r['posteam'], type='FG', off=1, qtr=r['qtr'])
                    elif r['safety'] == '1':
                        first = dict(team=r['defteam'], type='SAF', off=0, qtr=r['qtr'])
                d = r['fixed_drive']
                if not d or not r['posteam']:
                    continue
                k = int(float(d))
                if k not in dinfo:
                    dinfo[k] = dict(team=r['posteam'], res=r['fixed_drive_result'], rz=int(r['drive_inside20'] == '1'),
                                    fga=0, fgm=0, fgexp=0.0)
                    order.append(k)
                if r['field_goal_result'] in ('made', 'missed', 'blocked') and r['posteam'] == dinfo[k]['team']:
                    di = dinfo[k]
                    di['fga'] += 1; di['fgm'] += int(r['field_goal_result'] == 'made')
                    di['fgexp'] += fg_expect(float(r['kick_distance'] or 40))
            tn = Counter()
            for n, k in enumerate(order, 1):
                di = dinfo[k]
                tn[di['team']] += 1
                res = di['res']
                out = {'Touchdown': 'td', 'Field goal': 'fg', 'Opp touchdown': 'opp_td', 'Safety': 'safety'}.get(res, 'none')
                drives.append(dict(game_id=gid, season=y, week=int(g0['week']), team=di['team'],
                                   opp=home if di['team'] == away else away, game_drive=n, team_drive=tn[di['team']],
                                   outcome=out, rz=di['rz'], fga=di['fga'], fgm=di['fgm'], fgexp=round(di['fgexp'], 4)))
            games.append(dict(game_id=gid, season=y, week=int(g0['week']), home=home, away=away,
                              roof=g0['roof'], first_team=first['team'] if first else '',
                              first_type=first['type'] if first else 'none', first_off=first['off'] if first else 0,
                              first_qtr=first['qtr'] if first else ''))
    for fn, rows in (('fs_drives.csv', drives), ('fs_games.csv', games)):
        with open(os.path.join(DATA, fn), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        print('wrote', fn, len(rows), file=sys.stderr)


def load_fs():
    D = defaultdict(list)
    for d in csv.DictReader(open(os.path.join(DATA, 'fs_drives.csv'))):
        for k in ('team_drive', 'rz', 'fga', 'fgm'):
            d[k] = int(d[k])
        d['fgexp'] = float(d['fgexp'])
        D[d['game_id']].append(d)
    Gs = {g['game_id']: g for g in csv.DictReader(open(os.path.join(DATA, 'fs_games.csv')))}
    return D, Gs


def outcome_index(g, fg):
    t, ty = fg['first_team'], fg['first_type']
    if ty == 'none':
        return 5
    if ty == 'SAF':
        return 4
    h = t == g['home']
    return (0 if h else 2) + (1 if ty == 'FG' else 0)


# ------------------------------------------------------------------ team state for FG / non-offense terms
class FSState:
    def __init__(self):
        z = lambda: dict(nd=0.0, fg=0.0, rzs=0.0, rzfg=0.0, dnd=0.0, dfg=0.0, drzs=0.0, drzfg=0.0, fga=0.0, fgm=0.0, fgexp=0.0)
        self.t = defaultdict(z)
        self.lg = Counter()

    def lg_fg(self):
        return (self.lg['fg'] + 30) / (self.lg['nd'] + 100)

    def lg_stall(self):
        return (self.lg['rzfg'] + 40) / (self.lg['rzs'] + 100)

    def q(self):
        """Per-drive league rates: opponent TD, own return TD is inside 'td' already, safety."""
        n = self.lg['drives'] + 500
        return (self.lg['opp_td'] + 5) / n, (self.lg['safety'] + 1) / n

    def feats(self, team, opp, roof):
        a, b = self.t[team], self.t[opp]
        lf, ls = self.lg_fg(), self.lg_stall()
        return dict(
            fg_off=m.logit((a['fg'] + K_FG * lf) / (a['nd'] + K_FG)) - m.logit(lf),
            fg_def=m.logit((b['dfg'] + K_FG * lf) / (b['dnd'] + K_FG)) - m.logit(lf),
            stall_off=m.logit((a['rzfg'] + K_RZ * ls) / (a['rzs'] + K_RZ)) - m.logit(ls),
            stall_def=m.logit((b['drzfg'] + K_RZ * ls) / (b['drzs'] + K_RZ)) - m.logit(ls),
            kick_oe=(a['fgm'] - a['fgexp']) / (a['fga'] + K_KICK),
            dome=float(roof in ('dome', 'closed')))

    def update(self, drives):
        per = defaultdict(Counter)
        for d in drives:
            x = per[d['team']]
            self.lg['drives'] += 1
            self.lg['opp_td'] += int(d['outcome'] == 'opp_td'); self.lg['safety'] += int(d['outcome'] == 'safety')
            if d['team_drive'] > m.MAX_TEAM_DRIVE:
                continue
            if d['outcome'] != 'td':
                x['nd'] += 1; x['fg'] += int(d['outcome'] == 'fg')
            if d['rz'] and d['outcome'] in ('td', 'fg'):
                x['rzs'] += 1; x['rzfg'] += int(d['outcome'] == 'fg')
        for d in drives:
            per[d['team']]['fga'] += d['fga']; per[d['team']]['fgm'] += d['fgm']; per[d['team']]['fgexp'] += d['fgexp']
        teams = {d['team'] for d in drives} | {d['opp'] for d in drives}
        for t in teams:
            for k in self.t[t]:
                self.t[t][k] *= DECAY
        for t in teams:
            x = per[t]
            o = next((d['opp'] for d in drives if d['team'] == t), None)
            a = self.t[t]
            a['nd'] += x['nd']; a['fg'] += x['fg']; a['rzs'] += x['rzs']; a['rzfg'] += x['rzfg']
            a['fga'] += x['fga']; a['fgm'] += x['fgm']; a['fgexp'] += x['fgexp']
            self.lg['nd'] += x['nd']; self.lg['fg'] += x['fg']; self.lg['rzs'] += x['rzs']; self.lg['rzfg'] += x['rzfg']
            if o:
                b = self.t[o]
                b['dnd'] += x['nd']; b['dfg'] += x['fg']; b['drzs'] += x['rzs']; b['drzfg'] += x['rzfg']


def fg_x(tf, ff, n):
    return [float(n == 1), float(n == 2), tf['ln_imp'], ff['fg_off'], ff['fg_def'], ff['stall_off'], ff['stall_def'],
            ff['kick_oe'] * 10, ff['dome'], tf['off'], tf['dfn']]


def fs_chain(wd, wf, tfa, tfb, ffa, ffb, q_opp, q_saf, pa_recv, n_drives):
    """Returns P(A TD, A FG, B TD, B FG, safety, none)."""
    h1 = int(round(n_drives / 2)); h2 = int(round(n_drives)) - h1
    out = np.zeros(6)
    for recv_a, w in ((True, pa_recv), (False, 1 - pa_recv)):
        first, second = ('A', 'B') if recv_a else ('B', 'A')
        seq = [first if k % 2 == 0 else second for k in range(h1)] + [second if k % 2 == 0 else first for k in range(h2)]
        alive, cnt, res = 1.0, Counter(), np.zeros(6)
        for t in seq:
            cnt[t] += 1
            n = min(cnt[t], 3)
            tf, ff = (tfa, ffa) if t == 'A' else (tfb, ffb)
            ptd = m.drive_prob(wd, tf, n)
            pfg = float(m.sigmoid(wf[0] + np.array(fg_x(tf, ff, n)) @ wf[1:])) * max(0.0, 1 - ptd - q_opp - q_saf)
            own, opp = (0, 2) if t == 'A' else (2, 0)
            res[own] += alive * ptd
            res[own + 1] += alive * pfg
            res[opp] += alive * q_opp
            res[4] += alive * q_saf
            alive *= max(0.0, 1 - ptd - pfg - q_opp - q_saf)
        res[5] = alive
        out += w * res
    return out


# ------------------------------------------------------------------ baselines
class Baseline:
    """B1: spread logistic for who scores first x league type split. B2: plus implied-total logistic for TD share."""
    def __init__(self):
        self.rows = []   # (spread, imp_home, imp_away, outcome index)

    def fit(self):
        R = [r for r in self.rows if r[0] is not None]
        sc = [r for r in R if r[3] < 4]
        X = np.array([[r[0] / 7] for r in sc]); y = np.array([float(r[3] < 2) for r in sc])
        self.ws = m.ridge_logit(X, y, lam=1.0)
        n = len(R) + 20
        self.p_saf = (sum(r[3] == 4 for r in R) + 1) / n
        self.p_none = (sum(r[3] == 5 for r in R) + 0.2) / n
        tds = [float(r[3] in (0, 2)) for r in sc]
        self.td_share = (sum(tds) + 10) / (len(tds) + 20)
        imp = np.array([[math.log(r[1] if r[3] < 2 else r[2]) - math.log(22)] for r in sc])
        self.wt = m.ridge_logit(imp, np.array(tds), lam=1.0)

    def predict(self, spread, ih, ia, total=True):
        ph = float(m.sigmoid(self.ws[0] + self.ws[1] * spread / 7))
        sc = 1 - self.p_saf - self.p_none
        if total:
            th = float(m.sigmoid(self.wt[0] + self.wt[1] * (math.log(ih) - math.log(22))))
            ta = float(m.sigmoid(self.wt[0] + self.wt[1] * (math.log(ia) - math.log(22))))
        else:
            th = ta = self.td_share
        return np.array([sc * ph * th, sc * ph * (1 - th), sc * (1 - ph) * ta, sc * (1 - ph) * (1 - ta), self.p_saf, self.p_none])


# ------------------------------------------------------------------ walk-forward
def walk(eval_from=(2024, 8), fit_from=(2024, 4), upto=None):
    G, dg, pgm = m.load_tables()
    FD, FG = load_fs()
    st, fs, bl = m.State(), FSState(), Baseline()
    weeks = sorted({(g['season'], g['week']) for g in G})
    by_week = defaultdict(list)
    for g in G:
        by_week[(g['season'], g['week'])].append(g)
    drows, frows, preds = [], [], []
    wd = wf = None
    for wk in weeks:
        if upto and wk > upto:
            break
        if wk >= eval_from:
            wd = m.ridge_logit(np.array([r[1] for r in drows if r[0] < wk]), np.array([r[2] for r in drows if r[0] < wk], float), lam=2.0)
            wf = m.ridge_logit(np.array([r[1] for r in frows if r[0] < wk]), np.array([r[2] for r in frows if r[0] < wk], float), lam=2.0)
            bl.fit()
        for g in by_week[wk]:
            fg = FG.get(g['game_id'])
            if fg is None:
                continue
            h, a = g['home'], g['away']
            tf = {t: st.team_feats(t, o, m.implied(g, t)) for t, o in ((h, a), (a, h))}
            ff = {t: fs.feats(t, o, fg['roof']) for t, o in ((h, a), (a, h))}
            if wk >= fit_from:
                for d in dg[g['game_id']]:
                    n = int(d['team_drive'])
                    if n <= m.MAX_TEAM_DRIVE:
                        drows.append((wk, m.drive_x(tf[d['team']], min(n, 3)), int(d['off_td'])))
                for d in FD[g['game_id']]:
                    n = d['team_drive']
                    if n <= m.MAX_TEAM_DRIVE and d['outcome'] in ('fg', 'none'):
                        frows.append((wk, fg_x(tf[d['team']], ff[d['team']], min(n, 3)), int(d['outcome'] == 'fg')))
            y = outcome_index(g, fg)
            ih, ia = m.implied(g, h), m.implied(g, a)
            if wk >= eval_from and wd is not None and ih:
                pa = min(0.85, max(0.15, 0.5 + st.recv_tend(h) - st.recv_tend(a)))
                qo, qs = fs.q()
                p = fs_chain(wd, wf, tf[h], tf[a], ff[h], ff[a], qo, qs, pa, st.pace(h) + st.pace(a))
                preds.append(dict(game=g, key=wk, p=p, y=y, b1=bl.predict(m.f(g['spread_line']), ih, ia, total=False),
                                  b2=bl.predict(m.f(g['spread_line']), ih, ia, total=True), roof=fg['roof']))
            bl.rows.append((m.f(g['spread_line'], None) if g['spread_line'] else None, ih or 22, ia or 22, y))
        for g in by_week[wk]:
            st.update(g, dg[g['game_id']], pgm[g['game_id']])
            fs.update(FD[g['game_id']])
    return preds, st, fs, wd, wf, frows, drows, bl


# ------------------------------------------------------------------ backtest
def mlogloss(P, Y):
    return float(np.mean([-math.log(max(p[y], 1e-4)) for p, y in zip(P, Y)]))


def brier(P, Y):
    return float(np.mean([np.sum((p - np.eye(6)[y]) ** 2) for p, y in zip(P, Y)]))


def calib(pairs, edges):
    out = []
    p = np.array([x[0] for x in pairs]); y = np.array([x[1] for x in pairs], float)
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (p >= lo) & (p < hi)
        if k.sum():
            out.append((f'{lo * 100:.0f}-{hi * 100:.0f}%' if hi < 1 else f'{lo * 100:.0f}%+', int(k.sum()), float(p[k].mean()), float(y[k].mean())))
    return out


def roi_sim(preds, src='p', book='b2', thr=1.2):
    """Simulated: book price = baseline B2 chance x OVERROUND (proportional hold). Bet $1 when our p x book decimal >= thr."""
    bets = Counter(); won = Counter(); pnl = Counter()
    for pr in preds:
        p, b = pr[src], pr[book]
        for i in range(4):
            dec = 1 / (b[i] * OVERROUND)
            if p[i] * dec >= thr:
                lab = 'TD' if i in (0, 2) else 'FG'
                for k in (lab, 'all'):
                    bets[k] += 1
                    hit = pr['y'] == i
                    won[k] += hit
                    pnl[k] += (dec - 1) if hit else -1
    return {k: (bets[k], won[k], pnl[k]) for k in bets}


def backtest():
    preds, st, fs, wd, wf, frows, drows, _ = walk()
    L, res = [], {}
    n = len(preds)
    ys = Counter(pr['y'] for pr in preds)
    first_wk, last_wk = preds[0]['key'], preds[-1]['key']
    L.append(f'NFL first scoring play model backtest (walk-forward, {first_wk[0]} Wk {first_wk[1]} to {last_wk[0]} Wk {last_wk[1]}, n={n} games)')
    L.append('Refit before every week on earlier weeks only (training from 2024 Week 4). Lines = nflverse closing spread / total.')
    L.append('')
    tdf = sum(ys[i] for i in (0, 2)) / n; fgf = sum(ys[i] for i in (1, 3)) / n
    L.append(f'First score type: TD {tdf * 100:.1f}%, FG {fgf * 100:.1f}%, safety {ys[4] / n * 100:.1f}%, no score {ys[5] / n * 100:.1f}%')
    fav_first = [pr for pr in preds if pr['y'] < 4 and m.f(pr['game']['spread_line']) != 0]
    ff = sum((m.f(pr['game']['spread_line']) > 0) == (pr['y'] < 2) for pr in fav_first)
    L.append(f'Spread favorite scored first: {ff}/{len(fav_first)} ({ff / len(fav_first) * 100:.1f}%)')
    L.append('')

    def sect(label, sub):
        P = [x['p'] for x in sub]; Y = [x['y'] for x in sub]
        B1 = [x['b1'] for x in sub]; B2 = [x['b2'] for x in sub]
        r = dict(n=len(sub), ll=mlogloss(P, Y), ll_b1=mlogloss(B1, Y), ll_b2=mlogloss(B2, Y),
                 br=brier(P, Y), br_b1=brier(B1, Y), br_b2=brier(B2, Y))
        L.append(f'== {label} ({len(sub)} games) ==')
        L.append(f"6-way log loss: model {r['ll']:.4f} | B1 spread {r['ll_b1']:.4f} | B2 spread+total {r['ll_b2']:.4f}  (lower is better)")
        L.append(f"6-way Brier:    model {r['br']:.4f} | B1 spread {r['br_b1']:.4f} | B2 spread+total {r['br_b2']:.4f}")
        # FG-first binary (either team)
        for lab, idx in (('Any FG first', (1, 3)), ('Any TD first', (0, 2))):
            yy = [int(y in idx) for y in Y]
            pm = [sum(p[i] for i in idx) for p in P]; p2 = [sum(p[i] for i in idx) for p in B2]
            L.append(f'{lab}: actual {np.mean(yy) * 100:.1f}%, model avg {np.mean(pm) * 100:.1f}%; binary log loss model '
                     f'{m.ll(yy, pm):.4f} vs B2 {m.ll(yy, p2):.4f}')
        # who scores first (home vs away), 2-way among games with a team score
        hh = [(p[0] + p[1]) / max(p[0] + p[1] + p[2] + p[3], 1e-6) for p in P]
        hb = [(p[0] + p[1]) / max(p[0] + p[1] + p[2] + p[3], 1e-6) for p in B2]
        yh = [int(y < 2) for y in Y]
        L.append(f'Home scores first: log loss model {m.ll(yh, hh):.4f} vs spread {m.ll(yh, hb):.4f}')
        top = sum(int(np.argmax(p[:4]) == y) for p, y in zip(P, Y)); topb = sum(int(np.argmax(p[:4]) == y) for p, y in zip(B2, Y))
        L.append(f'Top outcome hit: model {top}/{len(sub)} ({top / len(sub) * 100:.1f}%), B2 {topb} ({topb / len(sub) * 100:.1f}%)')
        L.append('')
        res[label] = r
        return r

    sect('All seasons', preds)
    for s in (2024, 2025, 2026):
        sub = [x for x in preds if x['key'][0] == s]
        if sub:
            sect(f'{s}', sub)
    # calibration, the 4 team outcomes pooled and FG / TD separately
    edges = (0, .10, .15, .20, .25, .30, .35, .40, .50, 1.01)
    for lab, idx in (('Team TD first', (0, 2)), ('Team FG first', (1, 3)), ('All 4 team outcomes', (0, 1, 2, 3))):
        pairs = [(x['p'][i], int(x['y'] == i)) for x in preds for i in idx]
        pb = [(x['b2'][i], int(x['y'] == i)) for x in preds for i in idx]
        L.append(f'Calibration, {lab} (predicted / actual):')
        L.append('  bucket       model n  pred / act        B2 n  pred / act')
        cb = {b[0]: b for b in calib(pb, edges)}
        for b in calib(pairs, edges):
            c = cb.get(b[0])
            L.append(f'  {b[0]:10s} {b[1]:7d}  {b[2] * 100:4.1f}% / {b[3] * 100:4.1f}%' +
                     (f'   {c[1]:7d}  {c[2] * 100:4.1f}% / {c[3] * 100:4.1f}%' if c else ''))
        res['calib_' + lab] = calib(pairs, edges)
        L.append('')
    sa = [(x['p'][4], int(x['y'] == 4)) for x in preds]
    L.append(f"Safety first: predicted avg {np.mean([a for a, _ in sa]) * 100:.2f}%, actual {np.mean([b for _, b in sa]) * 100:.2f}%")
    L.append('')
    L.append(f'Simulated ROI (NO historical first scoring play prices available). Book = B2 baseline chance with a {OVERROUND:.2f} '
             'overround (proportional hold), roughly how FanDuel prices this market. $1 per bet.')
    res['roi'] = {}
    for thr, lab in ((1.2, 'take-at (our p x price >= 1.2)'), (1.0, 'any edge (our p x price >= 1.0)')):
        r = roi_sim(preds, thr=thr)
        res['roi'][lab] = r
        L.append('  ' + lab + ': ' + '; '.join(f'{k} {b} bets, {w} won, {pn:+.1f} units ({pn / b * 100:+.1f}%)' for k, (b, w, pn) in sorted(r.items())))
    r0 = roi_sim(preds, src='b2', thr=0.0)
    b, w, pn = r0['all']
    L.append(f'  reference, bet every team outcome at that book: {b} bets, {pn / b * 100:+.1f}% (the hold)')
    for s in (2024, 2025, 2026):
        parts = []
        for thr in (1.0, 1.1, 1.2):
            r = roi_sim([x for x in preds if x['key'][0] == s], thr=thr)
            if 'all' in r:
                b, w, pn = r['all']
                parts.append(f'edge {thr:.1f}: {b} bets {pn / b * 100:+.1f}%' +
                             (f" (FG {r['FG'][0]} bets {r['FG'][2] / r['FG'][0] * 100:+.1f}%)" if 'FG' in r else ''))
            else:
                parts.append(f'edge {thr:.1f}: 0 bets')
        L.append(f'  {s}: ' + '; '.join(parts))
    L.append('')
    L.append('FG model weights (last fit): ' + ', '.join(f'{k} {v:+.3f}' for k, v in zip(['const'] + FFEATS, wf)))
    L.append('TD drive weights (last fit): ' + ', '.join(f'{k} {v:+.3f}' for k, v in zip(['const'] + m.DFEATS, wd)))
    qo, qs = fs.q()
    L.append(f'League per-drive rates: opponent TD {qo * 100:.2f}%, safety {qs * 100:.2f}%')
    txt = '\n'.join(L)
    print(txt)
    open(os.path.join(OUT, 'first_score_backtest.txt'), 'w').write(txt + '\n')
    json.dump(res, open(os.path.join(OUT, 'first_score_backtest.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['build', 'backtest'])
    a = ap.parse_args()
    if a.mode == 'build':
        build()
    else:
        backtest()
