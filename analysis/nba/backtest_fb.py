#!/usr/bin/env python3
"""Backtest the first-basket model: v1 (old) vs v2 (accuracy blend, opponent defense by position,
injury ripple / team normalization). Walk-forward: every game from 2025-12-01 on (plus 2026-27 regular
season games) is predicted using only games played before its date. Starters and jumpers are the
actual ones (both models get the same), so this tests the share model, not lineup guessing.

  python3 analysis/nba/backtest_fb.py           # summary table
  python3 analysis/nba/backtest_fb.py --team    # 10/23 fix: 26-27 weight ramp + extra shrink for new-to-team starters
  python3 analysis/nba/backtest_fb.py --jumper  # 10/30 fix: jumper share x1.2 / x0.95 by tip, plus top-end shrink
Metrics: log loss of the actual first-FG scorer, probabilities renormalized over the 10 starters (games where a bench player
scored first are skipped for all models),
Brier over the 10 starters, and the hit rate of each game's top pick.
"""
import json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nba_tab import V2, POS, W_DEFAULT, JB, cur_weight, v1_share, v2_shares, jumper_split, shrink_top  # noqa: E402

START = '2025-12-01'
PREV = {'2026-27': '2025-26'}
REC = []   # per-game predictions (filled by run(); used by center_check.py)


def season_of(d):
    return '2026-27' if d >= '2026-07-01' else '2025-26'


def counts(PS, pid, tm, season, prm):
    """Counts as the build sees them: 26-27 games x W (flat, or ramped with prm['ramp']) plus 2025-26.
    In 2025-26 there is no earlier season, so W does not apply. n_starts = his starts for any team, both seasons
    (prm['team_only']: starts with tm only, the first try, which hurt traded regulars)."""
    c, l = PS[season][pid], PS[PREV[season]][pid] if season in PREV else {}
    w = 1
    if season in PREV:
        w = cur_weight(W_DEFAULT, c.get(('gs', tm), 0), prm) if prm.get('ramp') else prm.get('W', W_DEFAULT)
    out = {f: w * c.get(f, 0) + l.get(f, 0) for f in ('gs', 't1', 'sh1', 'fgm', 'fga')}
    if prm.get('k_new'):
        out['n_starts'] = (c.get(('gs', tm), 0) + l.get(('gs', tm), 0) if prm.get('team_only')
                           else c.get('gs', 0) + l.get('gs', 0))
    return out


def run(variants, team=False):
    games = []
    for s in ('2025-26', '2026-27'):
        g = json.load(open(os.path.join(HERE, 'data', f'games_{s}.json')))
        games += [x for x in g.values() if x['type'] == 2]
    games.sort(key=lambda x: (x['date'], x['id']))
    P = defaultdict(lambda: defaultdict(float))
    T = defaultdict(lambda: {'allow': defaultdict(float), 'n': 0})
    lg = {'fgm': 0, 'fga': 0, 'pos': defaultdict(float), 'posn': 0, 'tipfirst': 0, 'tipn': 0}
    PS = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))   # season -> pid -> counts (team mode)
    res = {k: defaultdict(lambda: {'ll': 0, 'br': 0, 'hit': 0, 'n': 0}) for k in variants}
    tops = defaultdict(dict)   # game -> variant -> (top pick, winner)
    by_date = defaultdict(list)
    for g in games:
        by_date[g['date']].append(g)
    for d in sorted(by_date):
        day = by_date[d]
        if d >= START and lg['posn']:
            L = {'fg': lg['fgm'] / lg['fga'], 'pos': {p: lg['pos'][p] / lg['posn'] for p in POS}}
            af = lg['tipfirst'] / lg['tipn']
            for g in day:
                if not g['fb'] or not g['tip']:
                    continue
                st = {tm: [p for p in g['pl'] if p[1] == tm and p[2]] for tm in (g['away'], g['home'])}
                if any(len(v) != 5 for v in st.values()):
                    continue
                rate = {}
                for pid, tm in g['tip']['j']:
                    q = P[pid]; rate[tm] = (q['tipw'] + 3) / (q['tips'] + 6)
                ra, rh = rate.get(g['away'], .5), rate.get(g['home'], .5)
                pt = ra * (1 - rh) / (ra * (1 - rh) + rh * (1 - ra))
                pteam = {g['away']: pt * af + (1 - pt) * (1 - af)}
                pteam[g['home']] = 1 - pteam[g['away']]
                for k, prm in variants.items():
                    probs = {}
                    pt_k = pteam
                    if prm and prm.get('gamma'):
                        tot = {}
                        for tm in st:
                            pl = [dict(P[p[0]], pos=p[6]) for p in st[tm]]
                            tot[tm] = sum(v2_shares(pl, {}, 0, L, dict(prm, def_k=None, norm=0))[0])
                        a, h = g['away'], g['home']
                        lo = math.log(pteam[a] / pteam[h]) + prm['gamma'] * math.log(tot[a] / tot[h])
                        pt_k = {a: 1 / (1 + math.exp(-lo))}; pt_k[h] = 1 - pt_k[a]
                    for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                        if team:
                            pl = [dict(counts(PS, p[0], tm, season_of(d), prm), pos=p[6]) for p in st[tm]]
                        else:
                            pl = [dict(P[p[0]], pos=p[6]) for p in st[tm]]
                        for x in pl:
                            for f in ('gs', 't1', 'sh1', 'fgm', 'fga'):
                                x.setdefault(f, 0)
                        if prm is None:
                            sh = [v1_share(x['t1'], x['gs']) for x in pl]
                        else:
                            sh, _, _ = v2_shares(pl, T[opp]['allow'], T[opp]['n'], L, prm)
                        for p, s_ in zip(st[tm], sh):
                            probs[p[0]] = pt_k[tm] * s_
                    win = g['fb'][0]
                    if win not in probs:   # a bench player scored first (rare); skipped for every model alike
                        continue
                    REC.append(dict(k=k, d=d, g=g, probs=dict(probs), pt=dict(pt_k), st=st, af=af,
                                    ptip={g['away']: pt, g['home']: 1 - pt}))
                    pw = probs[win] / sum(probs.values())   # proper: renormalized over the 10 starters
                    tops[(d, g['away'], g['home'])][k] = (max(probs, key=probs.get), win, g['nm'])
                    for r in (res[k]['all'], res[k][season_of(d)]):
                        r['ll'] -= math.log(max(pw, 1e-6)); r['n'] += 1
                        r['br'] += sum((v - (p == win)) ** 2 for p, v in probs.items())
                        r['hit'] += max(probs, key=probs.get) == win
        for g in day:   # update with this day's results
            posof = {p[0]: p[6] for p in g['pl']}
            for pid, tm, stt, mins, pts, tpm, pos, fgm, fga in g['pl']:
                q = P[pid]; q['fgm'] += fgm; q['fga'] += fga
                PS[season_of(d)][pid]['fgm'] += fgm; PS[season_of(d)][pid]['fga'] += fga; lg['fgm'] += fgm; lg['fga'] += fga
                if stt:
                    z = PS[season_of(d)][pid]
                    for f, v in (('gs', 1), (('gs', tm), 1), ('t1', g['tf'].get(tm) == pid),
                                 ('sh1', g['ts'].get(tm) == pid)):
                        z[f] += v
                    q['gs'] += 1; q['t1'] += g['tf'].get(tm) == pid; q['sh1'] += g['ts'].get(tm) == pid
            for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                ps = posof.get(g['tf'].get(opp))
                if ps in POS:
                    T[tm]['allow'][ps] += 1; T[tm]['n'] += 1; lg['pos'][ps] += 1; lg['posn'] += 1
            if g['tip']:
                for pid, tm in g['tip']['j']:
                    P[pid]['tips'] += 1; P[pid]['tipw'] += g['tip']['w'] == tm
                if g['fb']:
                    lg['tipn'] += 1; lg['tipfirst'] += g['tip']['w'] == g['fb'][1]
    return res, tops


def main_team():
    """10/23 fix (Jaquez Jr. got 36% of MIL's first FG off one 26-27 start at weight 3)."""
    old = dict(V2, k_new=0)
    variants = {'v2 old (W=3 flat)': old,
                'v2 W=1 (no 26-27 boost)': dict(old, W=1),
                'v2 + ramp only': dict(old, ramp=True),
                'v2 + shrink only k_new=10': dict(V2, k_new=10),
                'v2 new: ramp + k_new=10': dict(V2, ramp=True),
                'ramp + k_new=5': dict(V2, ramp=True, k_new=5),
                'ramp + k_new=20': dict(V2, ramp=True, k_new=20),
                'ramp + k_new=10 settle 20': dict(V2, ramp=True, settle_n=20),
                'ramp + k10 team-only count': dict(V2, ramp=True, team_only=True),
                'ramp n=3': dict(old, ramp=True, ramp_n=3),
                'ramp n=10': dict(old, ramp=True, ramp_n=10)}
    res, tops = run(variants, team=True)
    for part in ('2025-26', '2026-27', 'all'):
        print(f"\n{part}\n{'model':28} {'games':>5} {'logloss':>8} {'brier':>7} {'top hit':>8}")
        for k, rr in res.items():
            r = rr[part]
            if r['n']:
                print(f"{k:28} {r['n']:5d} {r['ll'] / r['n']:8.4f} {r['br'] / r['n']:7.4f} {r['hit'] / r['n']:8.3f}")
    a, b = 'v2 old (W=3 flat)', 'v2 new: ramp + k_new=10'
    ch = [(gk, t[a], t[b]) for gk, t in sorted(tops.items()) if t[a][0] != t[b][0]]
    print(f"\nTop pick changed old -> new in {len(ch)} of {len(tops)} games "
          f"(old right {sum(x[1][0] == x[1][1] for x in ch)}, new right {sum(x[2][0] == x[2][1] for x in ch)})")
    for (d, aw, hm), o, n in ch:
        if d >= '2026-07-01':
            nmz = o[2]
            print(f"  {d} {aw}@{hm}: {nmz.get(o[0], o[0])} -> {nmz.get(n[0], n[0])}; first FG {nmz.get(o[1], o[1])}")


def main():
    off = dict(V2, def_k=None)
    variants = {'v1 (old)': None,
                'v1 + ripple (normalize)': dict(off, w_shot=0),
                '+ accuracy': off,
                '+ defense (v2 full)': dict(V2),
                'v2 defense k=30': dict(V2, def_k=30),
                'v2 defense k=60': dict(V2, def_k=60),
                'v2 w_shot=0.25': dict(V2, w_shot=0.25),
                'v2 w_shot=0.75': dict(V2, w_shot=0.75),
                'v2 no ripple': dict(V2, norm=0),
                'v2 ripple up-only': dict(V2, up_only=True),
                'v2 ripple half': dict(V2, norm=0.5),
                'v2 nodef ripple up-only': dict(off, up_only=True),
                'v2 nodef no ripple': dict(off, norm=0),
                'v2 + team acc g=0.5': dict(V2, gamma=0.5),
                'v2 + team acc g=1': dict(V2, gamma=1),
                'v2 + team acc g=2': dict(V2, gamma=2),
                'v2 nodef + team acc g=1': dict(off, gamma=1)}
    res, _ = run(variants)
    print(f"{'model':28} {'games':>5} {'logloss':>8} {'brier':>7} {'top hit':>8}")
    for k, rr in res.items():
        r = rr['all']
        print(f"{k:28} {r['n']:5d} {r['ll'] / r['n']:8.4f} {r['br'] / r['n']:7.4f} {r['hit'] / r['n']:8.3f}")


def adjust(r, jb=None, temp=1.0, knee=None):
    """Re-price one REC game: jumper split (jb = {'win','lose','cap'} or None), then a top-end shrink
    (temp: power on the 10 chances, same total; knee = (cut, c): chances above cut pulled to cut + c x excess)."""
    out = {}
    jm = {tm: pid for pid, tm in r['g']['tip']['j']}
    for tm, five in r['st'].items():
        sh = {p[0]: r['probs'][p[0]] / r['pt'][tm] for p in five}
        if jb:
            out.update(jumper_split(sh, jm.get(tm), r['ptip'][tm], r['af'], jb))
        else:
            out.update({p: v * r['pt'][tm] for p, v in sh.items()})
    out = shrink_top(out, temp)
    if knee:
        cut, c = knee
        tot = sum(out.values())
        out = {p: (cut + c * (v - cut) if v > cut else v) for p, v in out.items()}
        f = tot / sum(out.values())
        out = {p: v * f for p, v in out.items()}
    return out


def score(recs, fn):
    bins = [(0, .08), (.08, .11), (.11, .14), (.14, .17), (.17, 1), (.15, 1)]
    cal = {b: [0, 0.0, 0] for b in bins}
    o = {'n': len(recs), 'll': 0, 'br': 0, 'top': 0, 'jn': 0, 'jp': 0, 'ja': 0}
    for r in recs:
        pr = fn(r)
        w = r['g']['fb'][0]
        o['ll'] -= math.log(max(pr[w] / sum(pr.values()), 1e-6))
        o['br'] += sum((v - (p == w)) ** 2 for p, v in pr.items())
        o['top'] += max(pr, key=pr.get) == w
        jset = {pid for pid, tm in r['g']['tip']['j']}
        for p, v in pr.items():
            for b in bins:
                if b[0] <= v < b[1]:
                    c = cal[b]; c[0] += 1; c[1] += v; c[2] += p == w
            if p in jset:
                o['jn'] += 1; o['jp'] += v; o['ja'] += p == w
    o['ll'] /= o['n']; o['br'] /= o['n']; o['cal'] = cal
    return o


def main_jumper():
    """10/30 fix: jumper share boost by tip result, then a top-end shrink. Same records as --team (V2 + ramp)."""
    run({'cur': dict(V2, ramp=True)}, team=True)
    recs = [r for r in REC if r['k'] == 'cur']
    print('Under-8% bin, pred/hit: current', *(f"{x[1] / x[0]:.1%}/{x[2] / x[0]:.1%}" for x in
          [score(recs, lambda r: adjust(r))['cal'][(0, .08)]]), '| jumper + temp 0.8',
          *(f"{x[1] / x[0]:.1%}/{x[2] / x[0]:.1%}" for x in [score(recs, lambda r: adjust(r, jb=JB, temp=0.8))['cal'][(0, .08)]]))
    parts = {'2025-26': [r for r in recs if r['d'] < '2026-07-01'], '2026-27': [r for r in recs if r['d'] >= '2026-07-01']}
    J = dict(JB, win=1.2, lose=0.95)
    variants = {'current (no jumper fix)': {},
                'jumper 1.1 / 1.0': dict(jb=dict(J, win=1.1, lose=1.0)),
                'jumper 1.2 / 1.0': dict(jb=dict(J, lose=1.0)),
                'jumper 1.2 / 0.95': dict(jb=J),
                'jumper 1.3 / 1.0': dict(jb=dict(J, win=1.3, lose=1.0)),
                'j1.2/0.95 + temp 0.95': dict(jb=J, temp=0.95),
                'j1.2/0.95 + temp 0.9': dict(jb=J, temp=0.9),
                'j1.2/0.95 + temp 0.85': dict(jb=J, temp=0.85),
                'j1.2/0.95 + temp 0.8 (used)': dict(jb=J, temp=0.8),
                'j1.2/0.95 + temp 0.75': dict(jb=J, temp=0.75),
                'j1.2/0.95 + temp 0.7': dict(jb=J, temp=0.7),
                'j1.2/0.95 + knee 15% x0.75': dict(jb=J, knee=(.15, .75)),
                'j1.2/0.95 + knee 15% x0.5': dict(jb=J, knee=(.15, .5)),
                'j1.2/0.95 + knee 14% x0.5': dict(jb=J, knee=(.14, .5))}
    for part, rs in parts.items():
        print(f"\n{part} ({len(rs)} games)\n{'model':28} {'logloss':>8} {'brier':>7} {'top':>4} {'jumper exp/act':>15} "
              f"{'14-17% pred/hit':>16} {'17%+ pred/hit':>16} {'15%+ n pred/hit':>20}")
        for k, kw in variants.items():
            o = score(rs, lambda r: adjust(r, **kw))
            c = o['cal']
            f = lambda b: f"{c[b][1] / c[b][0]:.1%}/{c[b][2] / c[b][0]:.1%}" if c[b][0] else '-'
            print(f"{k:28} {o['ll']:8.4f} {o['br']:7.4f} {o['top']:4d} {o['jp']:7.1f}/{o['ja']:<7d} {f((.14, .17)):>16} "
                  f"{f((.17, 1)):>16} {c[(.15, 1)][0]:5d} {f((.15, 1)):>14}")


if __name__ == '__main__':
    if '--jumper' in sys.argv:
        main_jumper()
    elif '--team' in sys.argv:
        main_team()
    else:
        main()
