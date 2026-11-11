#!/usr/bin/env python3
"""Backtest of the first-possession CHAIN model (Tim's idea, 11/5/26) vs the current first points model.

Walk-forward, no lookahead, actual starters and tip jumpers, games from 2025-12-01 plus all 2026-27 regular season
games (same game set and same "current" numbers as backtest_fix.py). Target = the game's first POINTS incl FT.
Chain model: chain_model.py. Data: chain_data.py (rebounds, turnovers, putbacks) + opening.py + first3.py caches.

Also scores pick rules per team on the team's own first points (2 teams per game):
  cur top 2     the team's two highest current-model chances
  chain top 2   the two highest chain chances
  two-slot      slot 1 = most likely to score on the team's first shot event; slot 2 = best second-chance scorer

  python3 analysis/nba/backtest_chain.py           # results table, writes out/backtest_chain.json
"""
import json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backtest_fix as bf  # noqa: E402
import chain_model as cm  # noqa: E402
from build_nba_tab import POS, JB, v1_share, jumper_split, shrink_top  # noqa: E402

CHF = ('mins', 'OR', 'PA', 'PM', 'trT', 'trS', 'cFGA')
bf.F = bf.F + CHF
TF = ('to', 'seg', 'mf', 'orb', 'dto', 'dseg', 'dmf', 'dorb')


def team_rates(TS, tm, opp, season, LC, c):
    def get(t, f):
        cur = TS['2026-27'][t][f] * 3 if season == '2026-27' else 0
        return cur + TS['2025-26'][t][f] if season == '2026-27' else TS['2025-26'][t][f]
    lto, lob = LC['to'], LC['ob']
    o_to = (get(tm, 'to') + c['k_to'] * lto) / (get(tm, 'seg') + c['k_to'])
    d_to = (get(opp, 'dto') + c['k_to'] * lto) / (get(opp, 'dseg') + c['k_to'])
    o_ob = (get(tm, 'orb') + c['k_ob'] * lob) / (get(tm, 'mf') + c['k_ob'])
    d_ob = (get(opp, 'dorb') + c['k_ob'] * lob) / (get(opp, 'dmf') + c['k_ob'])
    return lto * (o_to / lto) * (d_to / lto), min(0.6, max(0.1, o_ob + d_ob - lob))


def run(chain_variants):
    games, F3, OP, CHN = [], {}, {}, {}
    for s in ('2025-26', '2026-27'):
        games += [x for x in bf.load('games', s).values() if x['type'] == 2]
        F3.update(bf.load('first3', s)); OP.update(bf.load('opening', s)); CHN.update(bf.load('chain', s))
    games.sort(key=lambda x: (x['date'], x['id']))
    PS = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    P = defaultdict(lambda: defaultdict(float))
    T = defaultdict(lambda: {'allow': defaultdict(float), 'n': 0})
    TS = {s: defaultdict(lambda: defaultdict(float)) for s in ('2025-26', '2026-27')}
    lg = defaultdict(float); lgpos = defaultdict(float); lgmix = defaultdict(lambda: [0.0, 0.0, 0.0])
    lp = defaultdict(lambda: defaultdict(float))   # chain league numbers by position
    by_date = defaultdict(list)
    for g in games:
        by_date[g['date']].append(g)
    recs = []
    cur_prm = dict(fp_fit=True, w_shot3=0.7)
    for d in sorted(by_date):
        day = by_date[d]
        if d >= bf.START and lg['posn']:
            L = {'fg': lg['fgm'] / lg['fga'], 'pos': {p: lgpos[p] / lg['posn'] for p in POS},
                 'kfg': [lg['M0'] / lg['A0'], lg['M1'] / lg['A1'], lg['M2'] / lg['A2']],
                 'pmix': {p: [x / sum(lgmix[p]) for x in lgmix[p]] for p in POS},
                 'ftr': lg['ftT'] / (lg['A0'] + lg['A1'] + lg['A2']), 'fts': lg['ftS'] / lg['ftT']}
            ev = sum(lp[p]['ev'] for p in POS)
            LC = {'upm': {p: lp[p]['ev'] / lp[p]['mins'] for p in POS},
                  'orpm': {p: lp[p]['OR'] / lp[p]['mins'] for p in POS},
                  'pa': {p: lp[p]['PA'] / lp[p]['OR'] for p in POS}, 'pm': {p: lp[p]['PM'] / lp[p]['PA'] for p in POS},
                  'tr': sum(lp[p]['trT'] for p in POS) / ev, 'trs': sum(lp[p]['trS'] for p in POS) / sum(lp[p]['trT'] for p in POS),
                  'to': lg['to'] / lg['seg'], 'ob': lg['orb'] / lg['mf'],
                  'cred': min(0.95, sum(lp[p]['OR'] for p in POS) / lg['orb_all'])}
            LL = dict(L, **LC)
            af_fp = lg['tipfirst_p'] / lg['tipn_p']
            for g in day:
                if not g['fp'] or not g['tip'] or g['id'] not in OP or g['id'] not in CHN:
                    continue
                st = {tm: [p for p in g['pl'] if p[1] == tm and p[2]] for tm in (g['away'], g['home'])}
                if any(len(v) != 5 for v in st.values()):
                    continue
                rate = {}
                for pid, tm in g['tip']['j']:
                    q = P[pid]; rate[tm] = (q['tipw'] + 3) / (q['tips'] + 6)
                ra, rh = rate.get(g['away'], .5), rate.get(g['home'], .5)
                pt = ra * (1 - rh) / (ra * (1 - rh) + rh * (1 - ra))
                ptip = {g['away']: pt, g['home']: 1 - pt}
                jm = {tm: pid for pid, tm in g['tip']['j']}
                win = g['fp'][0]
                if win not in {p[0] for v in st.values() for p in v}:
                    continue
                s = bf.season_of(d)
                feats = {tm: [dict(bf.counts(PS, p[0], tm, s), pos=p[6], pid=p[0]) for p in st[tm]] for tm in st}
                book = {}
                for tm in st:
                    for x in feats[tm]:
                        book[x['pid']] = (pt * af_fp + (1 - pt) * (1 - af_fp) if tm == g['away'] else
                                          (1 - pt) * af_fp + pt * (1 - af_fp)) * v1_share(x['t1'], x['gs'])
                bs = sum(book.values())
                book = {p: v / bs * bf.OVERROUND for p, v in book.items()}
                probs = {}
                cur = {}
                for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                    sh = bf.shares(feats[tm], T[opp]['allow'], T[opp]['n'], L, cur_prm, {})
                    cur.update(jumper_split({x['pid']: v for x, v in zip(feats[tm], sh)}, jm.get(tm), ptip[tm], af_fp, JB))
                probs['current'] = shrink_top(cur, 0.8)
                extra = {'team': {'current': {p: v / sum(u for q, u in cur.items() if q in {y[0] for y in st[tm]})
                                              for tm in st for p, v in cur.items() if p in {y[0] for y in st[tm]}}}}
                for k, c in chain_variants.items():
                    c = dict(cm.CH, **c)
                    TT = []
                    for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                        Pp = [cm.player_params(x, LL, c) for x in feats[tm]]
                        to, ob = team_rates(TS, tm, opp, s, LC, c)
                        ji = next((i for i, x in enumerate(Pp) if x['pid'] == jm.get(tm)), None)
                        TT.append(cm.Team(Pp, to, ob, LC['cred'], ji, c))
                    gp = cm.game_probs(TT, pt, c)
                    pr = {x['pid']: v for t in (0, 1) for x, v in zip(TT[t].P, gp[t])}
                    pr = shrink_top(pr, c['temp'])
                    if c.get('blend'):
                        tot = sum(probs['current'].values())
                        cs = sum(pr.values())
                        pr = {p: (1 - c['blend']) * probs['current'][p] + c['blend'] * v / cs * tot for p, v in pr.items()}
                    probs[k] = pr
                    tpr = {}
                    for t in (0, 1):
                        tf = cm.team_first(TT[t], c)[0]
                        z = sum(tf)
                        tpr.update({x['pid']: v / z for x, v in zip(TT[t].P, tf)})
                    extra.setdefault('team', {})[k] = tpr
                    slots = {}   # two-slot pick rule per variant (extra['slots'] = the default chain)
                    for t, tm in enumerate((g['away'], g['home'])):
                        s1, s2, tf, fe, sec = cm.two_slot(TT[t], c)
                        slots[tm] = (TT[t].P[s1]['pid'], TT[t].P[s2]['pid'])
                    extra.setdefault('slotsv', {})[k] = slots
                    if k == 'chain':
                        extra['slots'] = slots
                tmof = {p[0]: p[1] for v in st.values() for p in v}
                recs.append(dict(d=d, g=g, win=win, probs=probs, book=book, tmof=tmof,
                                 tp=OP[g['id']].get('tp', {}), **extra))
        for g in day:   # update with this day's results
            op = OP.get(g['id'], {})
            ch = CHN.get(g['id'], {})
            posof = {p[0]: p[6] for p in g['pl']}
            s = bf.season_of(d)
            for pid, tm, stt, mins, pts, tpm, pos, fgm, fga in g['pl']:
                z = PS[s][pid]; z['fgm'] += fgm; z['fga'] += fga; lg['fgm'] += fgm; lg['fga'] += fga
                z[('fgm', tm)] += fgm; z[('fga', tm)] += fga
                b = op.get('bx', {}).get(pid)
                if b:
                    for f, v in zip(('rA', 'rM', 'jA', 'jM', 'tA', 'tM', 'ftT', 'ftS'), b):
                        z[f] += v; z[(f, tm)] += v
                    for i in range(3):
                        lg[f'A{i}'] += b[2 * i]; lg[f'M{i}'] += b[2 * i + 1]
                        if pos in POS:
                            lgmix[pos][i] += b[2 * i]
                    lg['ftT'] += b[6]; lg['ftS'] += b[7]
                cb = ch.get('pb', {}).get(pid)
                if cb and mins:
                    vals = dict(mins=mins, OR=cb[0], PA=cb[3], PM=cb[4], trT=cb[5], trS=cb[6], cFGA=cb[7])
                    for f, v in vals.items():
                        z[f] += v; z[(f, tm)] += v
                    if pos in POS:
                        for f, v in vals.items():
                            lp[pos][f] += v
                        lp[pos]['ev'] += cb[7] + cb[5]
                if stt:
                    f3 = F3.get(g['id'], {}).get(tm)
                    took = g['ts'].get(tm) == pid
                    for f, v in (('gs', 1), ('t1', g['tf'].get(tm) == pid),
                                 ('tp1', op.get('tp', {}).get(tm) == pid), ('sh1', took),
                                 ('gs3', f3 is not None), ('f3', (f3 or []).count(pid))):
                        z[f] += v; z[(f, tm)] += v
            if ch:
                tms = list(ch['tm'])
                for tm in tms:
                    opp = [x for x in tms if x != tm][0]
                    mf, orb, to = ch['tm'][tm]
                    seg = to + sum(v[7] + v[5] for pid, v in ch['pb'].items() if any(p[0] == pid and p[1] == tm for p in g['pl']))
                    for f, v in (('to', to), ('seg', seg), ('mf', mf), ('orb', orb)):
                        TS[s][tm][f] += v; TS[s][opp]['d' + f] += v
                        lg[f] += v
                lg['orb_all'] += sum(ch['tm'][tm][1] for tm in tms)
            for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                ps = posof.get(g['tf'].get(opp))
                if ps in POS:
                    T[tm]['allow'][ps] += 1; T[tm]['n'] += 1; lgpos[ps] += 1; lg['posn'] += 1
            if g['tip']:
                for pid, tm in g['tip']['j']:
                    P[pid]['tips'] += 1; P[pid]['tipw'] += g['tip']['w'] == tm
                if g['fp']:
                    lg['tipn_p'] += 1; lg['tipfirst_p'] += g['tip']['w'] == g['fp'][1]
    return recs


def pairs(recs):
    """Team-level pick rules on the team's own first points. Returns {rule: (hits, n)} and game-level union."""
    o = defaultdict(lambda: [0, 0])
    for r in recs:
        g = r['g']
        gu = defaultdict(set)
        for tm in (g['away'], g['home']):
            tgt = r['tp'].get(tm)
            if not tgt:
                continue
            for rule, pr in (('cur top 2', r['probs']['current']), ('chain top 2', r['probs']['chain'])):
                mine = sorted((p for p in pr if r['tmof'][p] == tm), key=pr.get, reverse=True)[:2]
                o[rule][0] += tgt in mine; o[rule][1] += 1
                o[rule + ' top 1'][0] += tgt == mine[0]; o[rule + ' top 1'][1] += 1
                gu[rule] |= set(mine)
            sl = r['slots'][tm]
            o['two-slot'][0] += tgt in sl; o['two-slot'][1] += 1
            o['two-slot slot 1'][0] += tgt == sl[0]; o['two-slot slot 1'][1] += 1
            o['two-slot slot 2'][0] += tgt == sl[1]; o['two-slot slot 2'][1] += 1
            # hybrid: slot 1 = current top pick, slot 2 = chain second-chance pick (if different)
            gu['two-slot'] |= set(sl)
        for rule, S in gu.items():
            o['game ' + rule][0] += r['win'] in S; o['game ' + rule][1] += 1
    return {k: tuple(v) for k, v in o.items()}


def main():
    variants = {'chain': {}}
    if '--grid' in sys.argv:
        for t in (1.0, 0.9, 0.8):
            for jq in (1.0, 1.2, 1.4):
                variants[f'chain t{t} jq{jq}'] = dict(temp=t, jq=jq)
        for k in (4, 16, 30):
            variants[f'chain ksh1 {k}'] = dict(k_sh1=k, k_f3=k)
        for kb in (0.3, 0.5):
            variants[f'blend {kb}'] = dict(blend=kb)
    elif len(sys.argv) > 1 and sys.argv[1].startswith('{'):
        variants.update(json.loads(sys.argv[1]))
    recs = run(variants)
    parts = {'2025-26': [r for r in recs if r['d'] < '2026-07-01'], '2026-27': [r for r in recs if r['d'] >= '2026-07-01']}
    keys = ['current'] + list(variants)
    res = {k: {p: bf.score(rs, k) for p, rs in parts.items()} for k in keys}
    print(f"games {', '.join(f'{p} {len(rs)}' for p, rs in parts.items())}")
    print(f"{'model':22} {'LL 25-26':>8} {'SE':>6} {'LL 26-27':>8} {'SE':>6} {'Br 25':>7} {'Br 26':>7} {'top25':>5} {'top26':>5}")
    for k in keys:
        a, b = res[k]['2025-26'], res[k]['2026-27']
        se = []
        for p in parts:
            dd = [x - y for x, y in zip(res[k][p]['llg'], res['current'][p]['llg'])]
            m = sum(dd) / len(dd)
            se.append(math.sqrt(sum((x - m) ** 2 for x in dd) / (len(dd) - 1) / len(dd)) if any(dd) else 0)
        print(f"{k:22} {a['ll']:8.4f} {se[0]:6.4f} {b['ll']:8.4f} {se[1]:6.4f} {a['br']:7.4f} {b['br']:7.4f} "
              f"{a['top']:5d} {b['top']:5d}")
    for k in ('current', 'chain'):
        for p in parts:
            print(f"calibration {k} {p}:", ' '.join(f"{x:.1%}/{h:.1%}" for x, h in res[k][p]['dec']))
    pr = {p: pairs(rs) for p, rs in parts.items()}
    print('\npick rules (team first points; game = game first points in the 4 picks):')
    for rule in pr['2025-26']:
        print(f"{rule:24} " + '  '.join(f"{p} {h}/{n} {h / n:.1%}" for p, (h, n) in ((p, pr[p][rule]) for p in parts)))
    out = {'ll': {k: {p: {x: y for x, y in v.items() if x != 'llg'} for p, v in r.items()} for k, r in res.items()},
           'pairs': pr}
    json.dump(out, open(os.path.join(HERE, 'out', 'backtest_chain.json'), 'w'), indent=1)
    return res, pr


if __name__ == '__main__':
    main()
