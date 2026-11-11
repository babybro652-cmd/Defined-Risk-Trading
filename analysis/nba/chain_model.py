#!/usr/bin/env python3
"""First-possession CHAIN model for first points (Tim's idea, 11/5/26; backtest: backtest_chain.py).

Tim: "Who takes the first shot is important only if they are hitting more than missing, and if they are missing
then the second pick should be next in line."

The opening is played out possession by possession until someone scores (exact Markov chain, no simulation):
  tip      P(team gets the ball first) = jumper vs jumper tip chance
  segment  a fresh possession (or a reset after an offensive rebound): turnover with the team's TO rate, else one
           player ends it with a shot event. Shooter shares: the team's FIRST segment uses his first-FGA share (shrunk
           to his usage); later segments use his first-3-FGA share (shrunk to usage). The tip jumper's first-segment
           share x jq when his team won the tip.
  event    FT trip with his trip share (trips / (trips + FGA)), scores with his trip rate; or an FGA that scores with
           his make rate (rim / j2 / 3 mix x make rates, as the 11/5 shot-type term)
  miss     offensive rebound with the team's rate (vs the opponent's allowed rate); the rebounder is split by OREB per
           minute (team rebounds -> reset segment). After his rebound he takes a putback with his putback rate and
           scores with his putback rate; otherwise a reset segment for the same team.
  else     the other team's possession.
Shrinkage constants live in CH. Outputs P(player scores the game's first points) and, per team, P(player scores
the team's first points), P(he scores on the team's first shot event) and the second-chance part (the rest).
"""
KINDS = 3
CH = {'k_sh1': 50, 'k_f3': 50, 'k_u': 150, 'k_mix': 30, 'k_fg': 40, 'k_tr': 100, 'k_trs': 20, 'k_or': 150,
      'k_pa': 15, 'k_pm': 15, 'k_to': 3000, 'k_ob': 1500, 'jq': 1.2, 'temp': 1.0, 'steps': 80,
      'w_tp': 0.0, 'k_tp': 20, 'tp_q2': False}
# w_tp (11/11 test, README "Test 11/11/26"): blend his past share of the TEAM's first points (tp1 / gs, shrunk to 1/5
# with k_tp pseudo starts) into the first-possession shooter share: q1 = (1 - w_tp) q1 + w_tp share. tp_q2 also
# blends it into the later-possession share. 0 = off.


def player_params(p, L, c=CH):
    """p: weighted counts (gs, sh1, f3, gs3, rA..tM, mins, OR, PA, PM, trT, trS, cFGA) + pos. Returns dict."""
    pos = p.get('pos') if p.get('pos') in ('G', 'F', 'C') else 'F'
    A, M = (p['rA'], p['jA'], p['tA']), (p['rM'], p['jM'], p['tM'])
    mix = [(A[i] + c['k_mix'] * L['pmix'][pos][i]) / (sum(A) + c['k_mix']) for i in range(3)]
    mk = [(M[i] + c['k_fg'] * L['kfg'][i]) / (A[i] + c['k_fg']) for i in range(3)]
    fg = sum(x * y for x, y in zip(mix, mk))
    ev = p['cFGA'] + p['trT']
    upm = (ev + c['k_u'] * L['upm'][pos]) / (p['mins'] + c['k_u'])
    tr = (p['trT'] + c['k_tr'] * L['tr']) / (ev + c['k_tr'])
    trs = (p['trS'] + c['k_trs'] * L['trs']) / (p['trT'] + c['k_trs'])
    orpm = (p['OR'] + c['k_or'] * L['orpm'][pos]) / (p['mins'] + c['k_or'])
    pa = (p['PA'] + c['k_pa'] * L['pa'][pos]) / (p['OR'] + c['k_pa'])
    pm = (p['PM'] + c['k_pm'] * L['pm'][pos]) / (p['PA'] + c['k_pm'])
    return {'pid': p['pid'], 'fg': fg, 'tr': tr, 'trs': trs, 'upm': upm, 'orpm': orpm, 'pa': pa, 'pm': pm,
            'sh1': p['sh1'], 'gs': p['gs'], 'f3': p['f3'], 'gs3': p['gs3'], 'tp1': p.get('tp1', 0)}


def shares(P, c=CH):
    U = sum(x['upm'] for x in P)
    q1 = [(x['sh1'] + c['k_sh1'] * x['upm'] / U) / (x['gs'] + c['k_sh1']) for x in P]
    q2 = [(x['f3'] / 3 + c['k_f3'] * x['upm'] / U) / (x['gs3'] + c['k_f3']) for x in P]
    s1, s2 = sum(q1), sum(q2)
    q1, q2 = [v / s1 for v in q1], [v / s2 for v in q2]
    w = c.get('w_tp', 0)
    if w:
        h = [(x['tp1'] + c['k_tp'] / 5) / (x['gs'] + c['k_tp']) for x in P]
        sh = sum(h)
        h = [v / sh for v in h]
        q1 = [(1 - w) * a + w * b for a, b in zip(q1, h)]
        if c.get('tp_q2'):
            q2 = [(1 - w) * a + w * b for a, b in zip(q2, h)]
    return q1, q2


def boosted(q, j, jq):
    if j is None or jq == 1:
        return q
    qj = min(q[j] * jq, 0.9)
    k = (1 - qj) / (1 - q[j])
    return [qj if i == j else v * k for i, v in enumerate(q)]


class Team:
    def __init__(self, P, to, ob, cred, jumper_idx=None, c=CH):
        self.P = P
        self.q1, self.q2 = shares(P, c)
        self.q1b = boosted(self.q1, jumper_idx, c['jq'])
        self.to, self.ob, self.cred = to, ob, cred
        R = sum(x['orpm'] for x in P)
        self.rho = [x['orpm'] / R * cred for x in P]   # rebounder split; 1 - cred = team rebound -> reset


def _segment(T, q, m, absorb, miss_to_opp, reb):
    """Spread mass m over one segment of team T with shooter shares q. absorb[i] += scoring mass; returns mass
    that goes to the other team and adds (rebounder index or None, mass) to reb."""
    out = m * T.to
    m2 = m * (1 - T.to)
    for i, x in enumerate(T.P):
        mi = m2 * q[i]
        trip = mi * x['tr']
        absorb[i] += trip * x['trs']
        out += trip * (1 - x['trs'])
        fga = mi - trip
        absorb[i] += fga * x['fg']
        miss = fga * (1 - x['fg'])
        out += miss * (1 - T.ob)
        _orebs(T, miss * T.ob, reb)
    return out


def _orebs(T, m, reb):
    for r, rr in enumerate(T.rho):
        reb.append((r, m * rr))
    reb.append((None, m * (1 - T.cred)))


def _putback(T, r, m, absorb, reb):
    """Rebounder r: putback try with pa (scores pm, miss -> rebound again), else returns reset mass."""
    x = T.P[r]
    t = m * x['pa']
    absorb[r] += t * x['pm']
    miss = t * (1 - x['pm'])
    _orebs(T, miss * T.ob, reb)
    return m - t, miss * (1 - T.ob)   # (reset mass, mass to the other team)


def _rebounds(T, reb, absorb, rounds=8):
    """Resolve offensive rebounds round by round (mass per rebounder). Returns (reset mass, mass to the other team)."""
    vec = [0.0] * (len(T.P) + 1)
    for r, mm in reb:
        vec[-1 if r is None else r] += mm
    reset = out = 0.0
    for _ in range(rounds):
        reset += vec[-1]
        nxt = []
        for r in range(len(T.P)):
            if vec[r] > 1e-14:
                rs, o2 = _putback(T, r, vec[r], absorb, nxt)
                reset += rs; out += o2
        vec = [0.0] * (len(T.P) + 1)
        for r, mm in nxt:
            vec[-1 if r is None else r] += mm
        if sum(vec) < 1e-12:
            break
    return reset + sum(vec), out


def play(teams, first, c=CH):
    """teams: (Team A, Team B). first: index of the team with the first possession (it won the tip).
    Returns per team a list of P(player scores the game's first points | that team has the ball first)."""
    absorb = [[0.0] * len(t.P) for t in teams]
    # phase 0: first team's opening possession, 1: other team's opening possession, 2: later
    fresh = {(first, 0): 1.0}
    resets = {}
    for _ in range(c['steps']):
        nf, nr = {}, {}
        tot = 0.0
        items = [('f', k, v) for k, v in fresh.items()] + [('r', k, v) for k, v in resets.items()]
        for kind, (ti, ph), m in items:
            if m < 1e-12:
                continue
            tot += m
            T = teams[ti]
            if kind == 'f' and ph in (0, 1):
                q = T.q1b if ph == 0 else T.q1
            else:
                q = T.q2
            reb = []
            out = _segment(T, q, m, absorb[ti], None, reb)
            rs, o2 = _rebounds(T, reb, absorb[ti])
            nr[(ti, ph)] = nr.get((ti, ph), 0) + rs
            out += o2
            nph = 1 if ph == 0 else 2
            nf[(1 - ti, nph)] = nf.get((1 - ti, nph), 0) + out
        fresh, resets = nf, nr
        if tot < 1e-9:
            break
    return absorb


def team_first(T, c=CH):
    """P(player scores HIS TEAM's first points) for one team alone (other team ignored), plus P(he scores on the
    team's first shot event of the game, no tip boost). Returns (team_fp, first_event)."""
    n = len(T.P)
    first_ev = [0.0] * n
    m2 = 1 - T.to
    for i, x in enumerate(T.P):
        first_ev[i] = T.q1[i] * (x['tr'] * x['trs'] + (1 - x['tr']) * x['fg'])   # if the first segment ends in a shot
    absorb = [0.0] * n
    fresh, resets = {0: 1.0}, {}
    for _ in range(c['steps']):
        nf, nr, tot = {}, {}, 0.0
        for kind, ph, m in [('f', k, v) for k, v in fresh.items()] + [('r', k, v) for k, v in resets.items()]:
            if m < 1e-12:
                continue
            tot += m
            q = T.q1 if (kind == 'f' and ph == 0) else T.q2
            reb = []
            out = _segment(T, q, m, absorb, None, reb)
            rs, o2 = _rebounds(T, reb, absorb)
            nr[ph] = nr.get(ph, 0) + rs
            out += o2
            nf[2] = nf.get(2, 0) + out
        fresh, resets = nf, nr
        if tot < 1e-9:
            break
    return absorb, [v * m2 for v in first_ev]


def game_probs(teams, ptip_a, c=CH):
    """P(each player scores the game's first points). ptip_a: chance team A gets the first possession."""
    a = play(teams, 0, c)
    b = play(teams, 1, c)
    out = [[ptip_a * x + (1 - ptip_a) * y for x, y in zip(a[t], b[t])] for t in (0, 1)]
    return out


def two_slot(T, c=CH):
    """Tim's two-slot pick for one team: slot 1 = most likely to score on the team's first shot event (takes it and
    makes it); slot 2 = best second-chance scorer = most likely to score the team's first points AFTER a miss,
    turnover or rebound (team first points chance minus the first-event part), other than slot 1."""
    tf, fe = team_first(T, c)
    s1 = max(range(len(fe)), key=lambda i: fe[i])
    sec = [tf[i] - fe[i] for i in range(len(tf))]
    s2 = max((i for i in range(len(tf)) if i != s1), key=lambda i: sec[i])
    return s1, s2, tf, fe, sec
