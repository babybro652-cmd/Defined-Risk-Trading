#!/usr/bin/env python3
"""Backtest of three first basket fixes (Tim approved 11/5/26), walk-forward, no lookahead.

Target: the game's FIRST POINTS, free throws included (FanDuel settles first basket that way; Tim 11/4).
Every game from 2025-12-01 on (plus all 2026-27 regular season games) is priced from earlier dates only, with the
actual starters and tip jumpers, then the jumper split and the top-end shrink, as in build_nba_tab.py.

  current  model as built 11/2 (V2 + ramp + w3 0.5, team first FG counts, tip-winner-first rate on the first FG)
  fix 1    target = first points: shares fit on each team's first POINTS scorer (tp1), tip rate on first points
  fix 2    opening play: his share of his team's first FGA over his last N starts with this team, shrunk toward his
           season first-FGA share (k pseudo starts), x his FG% / league; blended in with weight w_open
  fix 3    shot type: event share x scoring chance per event. Event share = early FGA share (first shot and first 3
           FGA); chance = sum over rim / j2 / 3 of his FGA mix x his make rate (shrunk) + FT trips per FGA x trip
           scoring rate; normalized per team and blended in with weight w_shot3
  combined all three

  python3 analysis/nba/backtest_fix.py            # tuning grid + results table (needs data/opening_<season>.json)
Book assumption for the value sim: FanDuel's view = the plain season model (team first FG share x tip chance), with
a 30% overround on the starters (FanDuel first basket boards usually sum to about 125-140% implied).
"""
import json, math, os, sys
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nba_tab import V2, FP, POS, W_DEFAULT, JB, cur_weight, v1_share, v2_shares, jumper_split, shrink_top  # noqa: E402

START = '2025-12-01'
KINDS = ('rim', 'j2', '3')
F = ('gs', 't1', 'tp1', 'sh1', 'fgm', 'fga', 'f3', 'gs3', 'rA', 'rM', 'jA', 'jM', 'tA', 'tM', 'ftT', 'ftS')
OVERROUND, EDGE = 1.30, 1.20


def season_of(d):
    return '2026-27' if d >= '2026-07-01' else '2025-26'


def load(name, s):
    try:
        return json.load(open(os.path.join(HERE, 'data', f'{name}_{s}.json')))
    except FileNotFoundError:
        return {}


def counts(PS, pid, tm, season):
    c = PS[season][pid]
    l = PS['2025-26'][pid] if season == '2026-27' else {}
    w = cur_weight(W_DEFAULT, c.get(('gs', tm), 0), V2) if season == '2026-27' else 1
    out = {f: w * c.get(f, 0) + l.get(f, 0) for f in F}
    out['n_starts'] = c.get('gs', 0) + l.get('gs', 0)
    return out


def shares(pl, allow, allow_n, L, prm, recent):
    """pl: 5 dicts of counts + pos + pid. Returns team shares (sum 0.99) of the team's first score.
    Variants without fix 2 (and with FT) run through build_nba_tab.v2_shares, so the build and this backtest match."""
    if not prm.get('w_open') and prm.get('ft', True) and not prm.get('own'):
        q = dict(V2, ramp=True)
        if prm.get('fp_fit'):
            q['fit_fp'] = True
        if prm.get('w_shot3'):
            q |= {k: v for k, v in FP.items() if k.startswith('k_')} | {'w_shot3': prm['w_shot3']}
        return v2_shares(pl, allow, allow_n, L, q)[0]
    tgt = 'tp1' if prm.get('fp_fit') else 't1'
    a_list, m_list = [], []
    shot_w = []
    for p in pl:
        kp = 10 + V2['k_new'] * max(0, 1 - p['n_starts'] / V2['settle_n'])
        s1 = v1_share(p[tgt], p['gs'], kp)
        s2 = v1_share(p['sh1'], p['gs'], kp)
        fg = (p['fgm'] + V2['fg_k'] * L['fg']) / (p['fga'] + V2['fg_k'])
        a = 0.5 * s1 + 0.5 * s2 * fg / L['fg']
        s3 = v1_share(p['f3'] / 3, p['gs3'], kp)
        a = 0.5 * a + 0.5 * s3
        if prm.get('w_open'):
            rec = recent.get(p['pid'], [])
            n, k = len(rec), prm['k_open']
            o = (sum(rec) + k * s2) / (n + k)
            if prm.get('open_replace'):   # recent first-FGA share replaces the season first-shot share inside the blend
                a = 0.5 * (0.5 * s1 + 0.5 * ((1 - prm['w_open']) * s2 + prm['w_open'] * o) * fg / L['fg']) + 0.5 * s3
            else:
                a = (1 - prm['w_open']) * a + prm['w_open'] * o * fg / L['fg']
        if prm.get('w_shot3'):
            att = 0.5 * s2 + 0.5 * s3
            if prm.get('w_open'):
                att = 0.5 * o + 0.5 * s3
            pos = p['pos'] if p['pos'] in POS else 'F'
            A = [p['rA'], p['jA'], p['tA']]
            M = [p['rM'], p['jM'], p['tM']]
            tot = sum(A)
            km = prm.get('k_mix', 30)
            mix = [(A[i] + km * L['pmix'][pos][i]) / (tot + km) for i in range(3)]
            kf = prm.get('k_fg', 40)
            mk = [(M[i] + kf * L['kfg'][i]) / (A[i] + kf) for i in range(3)]
            r = (p['ftT'] + 100 * L['ftr']) / (tot + 100) if prm.get('ft', True) else 0
            pft = (p['ftS'] + 20 * L['fts']) / (p['ftT'] + 20)
            eff = sum(mix[i] * mk[i] for i in range(3)) + r * pft
            shot_w.append(att * eff)
        a_list.append(a)
        rr = L['pos'].get(p['pos'])
        m = 1.0
        if rr:
            m = ((allow.get(p['pos'], 0) + V2['def_k'] * rr) / (allow_n + V2['def_k'])) / rr
            m = min(1 + V2['def_cap'], max(1 - V2['def_cap'], m))
        m_list.append(m)
    if shot_w:
        sa, sw = sum(a_list), sum(shot_w)
        a_list = [(1 - prm['w_shot3']) * a + prm['w_shot3'] * w / sw * sa for a, w in zip(a_list, shot_w)]
    out = [a * m for a, m in zip(a_list, m_list)]
    f = V2['starter_sum'] / sum(out)
    return [x * f for x in out]


def run(variants):
    games, F3, OP = [], {}, {}
    for s in ('2025-26', '2026-27'):
        games += [x for x in load('games', s).values() if x['type'] == 2]
        F3.update(load('first3', s)); OP.update(load('opening', s))
    games.sort(key=lambda x: (x['date'], x['id']))
    PS = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    P = defaultdict(lambda: defaultdict(float))     # tips
    T = defaultdict(lambda: {'allow': defaultdict(float), 'n': 0})
    RE = defaultdict(lambda: deque(maxlen=40))      # (pid) -> (team, took team first FGA) over his starts, newest last
    lg = defaultdict(float); lgpos = defaultdict(float); lgmix = defaultdict(lambda: [0.0, 0.0, 0.0])
    recs = []
    by_date = defaultdict(list)
    for g in games:
        by_date[g['date']].append(g)
    for d in sorted(by_date):
        day = by_date[d]
        if d >= START and lg['posn']:
            L = {'fg': lg['fgm'] / lg['fga'], 'pos': {p: lgpos[p] / lg['posn'] for p in POS},
                 'kfg': [lg['M0'] / lg['A0'], lg['M1'] / lg['A1'], lg['M2'] / lg['A2']],
                 'pmix': {p: [x / sum(lgmix[p]) for x in lgmix[p]] for p in POS},
                 'ftr': lg['ftT'] / (lg['A0'] + lg['A1'] + lg['A2']), 'fts': lg['ftS'] / lg['ftT']}
            af_fb, af_fp = lg['tipfirst'] / lg['tipn'], lg['tipfirst_p'] / lg['tipn_p']
            for g in day:
                if not g['fp'] or not g['tip'] or g['id'] not in OP:
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
                s = season_of(d)
                feats = {tm: [dict(counts(PS, p[0], tm, s), pos=p[6], pid=p[0]) for p in st[tm]] for tm in st}
                # book view (value sim): plain season team-first-FG share x tip chance
                book = {}
                for tm in st:
                    for x in feats[tm]:
                        book[x['pid']] = (pt * af_fb + (1 - pt) * (1 - af_fb) if tm == g['away'] else
                                          (1 - pt) * af_fb + pt * (1 - af_fb)) * v1_share(x['t1'], x['gs'])
                bs = sum(book.values())
                book = {p: v / bs * OVERROUND for p, v in book.items()}
                out = {}
                for k, prm in variants.items():
                    af = af_fp if prm.get('fp_fit') else af_fb
                    probs = {}
                    for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                        recent = {}
                        if prm.get('w_open'):
                            for x in feats[tm]:
                                recent[x['pid']] = [t for team, t in RE[x['pid']] if team == tm][-prm['n_open']:]
                        sh = shares(feats[tm], T[opp]['allow'], T[opp]['n'], L, prm, recent)
                        probs.update(jumper_split({x['pid']: v for x, v in zip(feats[tm], sh)}, jm.get(tm), ptip[tm], af, JB))
                    out[k] = shrink_top(probs, 0.8)
                tmof = {p[0]: p[1] for v in st.values() for p in v}
                recs.append(dict(d=d, g=g, win=win, fb=(g['fb'] or [None])[0], probs=out, book=book, tmof=tmof))
        for g in day:   # update with this day's results
            op = OP.get(g['id'], {})
            posof = {p[0]: p[6] for p in g['pl']}
            s = season_of(d)
            for pid, tm, stt, mins, pts, tpm, pos, fgm, fga in g['pl']:
                z = PS[s][pid]; z['fgm'] += fgm; z['fga'] += fga; lg['fgm'] += fgm; lg['fga'] += fga
                b = op.get('bx', {}).get(pid)
                if b:
                    for f, v in zip(('rA', 'rM', 'jA', 'jM', 'tA', 'tM', 'ftT', 'ftS'), b):
                        z[f] += v
                    for i in range(3):
                        lg[f'A{i}'] += b[2 * i]; lg[f'M{i}'] += b[2 * i + 1]
                        if pos in POS:
                            lgmix[pos][i] += b[2 * i]
                    lg['ftT'] += b[6]; lg['ftS'] += b[7]
                if stt:
                    f3 = F3.get(g['id'], {}).get(tm)
                    took = g['ts'].get(tm) == pid
                    for f, v in (('gs', 1), (('gs', tm), 1), ('t1', g['tf'].get(tm) == pid),
                                 ('tp1', op.get('tp', {}).get(tm) == pid), ('sh1', took),
                                 ('gs3', f3 is not None), ('f3', (f3 or []).count(pid))):
                        z[f] += v
                    RE[pid].append((tm, took))
            for tm, opp in ((g['away'], g['home']), (g['home'], g['away'])):
                ps = posof.get(g['tf'].get(opp))
                if ps in POS:
                    T[tm]['allow'][ps] += 1; T[tm]['n'] += 1; lgpos[ps] += 1; lg['posn'] += 1
            if g['tip']:
                for pid, tm in g['tip']['j']:
                    P[pid]['tips'] += 1; P[pid]['tipw'] += g['tip']['w'] == tm
                if g['fb']:
                    lg['tipn'] += 1; lg['tipfirst'] += g['tip']['w'] == g['fb'][1]
                if g['fp']:
                    lg['tipn_p'] += 1; lg['tipfirst_p'] += g['tip']['w'] == g['fp'][1]
    return recs


def score(recs, k, target='win'):
    o = {'n': 0, 'll': 0.0, 'br': 0.0, 'top': 0, 'topfga': 0, 'bets': 0, 'bw': 0, 'pnl': 0.0}
    pts = []
    llg = []
    for r in recs:
        pr, w = r['probs'][k], r[target]
        if w not in pr:
            continue
        o['n'] += 1
        x = -math.log(max(pr[w] / sum(pr.values()), 1e-6)); o['ll'] += x; llg.append(x)
        o['br'] += sum((v - (p == w)) ** 2 for p, v in pr.items())
        top = max(pr, key=pr.get)
        o['top'] += top == w
        o['topfga'] += r['g']['ts'].get(r['tmof'][top]) == top
        for p, v in pr.items():
            pts.append((v, p == w))
            if v * (1 / r['book'][p]) >= EDGE:   # book price beats our fair by 20%+
                o['bets'] += 1; o['bw'] += p == w; o['pnl'] += (1 / r['book'][p] - 1) if p == w else -1
    pts.sort()
    dec = []
    for i in range(10):
        ch = pts[i * len(pts) // 10:(i + 1) * len(pts) // 10]
        dec.append((sum(v for v, _ in ch) / len(ch), sum(h for _, h in ch) / len(ch)))
    o['dec'] = dec; o['llg'] = llg
    o['ll'] /= o['n']; o['br'] /= o['n']
    return o


def main():
    f1 = {'fp_fit': True}
    variants = {'current': {}, 'fix1': f1, 'fix1+3 w0.7 own': dict(f1, w_shot3=0.7, own=True)}
    for n in (10, 15, 20):
        for w in (0.1, 0.25, 0.4, 0.55):
            variants[f'fix2 N{n} w{w}'] = dict(w_open=w, n_open=n, k_open=10)
            variants[f'fix2 N{n} w{w} repl'] = dict(w_open=w, n_open=n, k_open=10, open_replace=True)
    for w in (0.25, 0.4, 0.55, 0.7, 1.0):
        variants[f'fix3 w{w}'] = dict(w_shot3=w)
        variants[f'fix3 w{w} noFT'] = dict(w_shot3=w, ft=False)
        variants[f'fix1+3 w{w}'] = dict(f1, w_shot3=w)
    for n, wo in ((20, 0.1), (20, 0.25), (15, 0.25)):
        for ws in (0.55, 0.7):
            variants[f'all N{n} wo{wo} ws{ws}'] = dict(f1, w_open=wo, n_open=n, k_open=10, w_shot3=ws)
            variants[f'all N{n} wo{wo} ws{ws} repl'] = dict(f1, w_open=wo, n_open=n, k_open=10, w_shot3=ws, open_replace=True)
    recs = run(variants)
    parts = {'2025-26': [r for r in recs if r['d'] < '2026-07-01'], '2026-27': [r for r in recs if r['d'] >= '2026-07-01']}
    nights = {p: len({r['d'] for r in rs}) for p, rs in parts.items()}
    res = {k: {p: score(rs, k) for p, rs in parts.items()} for k in variants}
    print(f"games {', '.join(f'{p} {len(rs)} ({nights[p]} nights)' for p, rs in parts.items())}")
    print("current model on the FIRST FG target: " + ', '.join(
        f"{p} {score(rs, 'current', 'fb')['ll']:.4f}" for p, rs in parts.items()))
    print(f"\n{'variant':30} {'LL 25-26':>8} {'SE':>6} {'LL 26-27':>8} {'SE':>6} {'Br 25':>7} {'Br 26':>7} {'top25':>5} "
          f"{'top26':>5} {'tFGA25':>6} {'tFGA26':>6} {'bets/n25':>8} {'bets/n26':>8}")
    for k in variants:
        a, b = res[k]['2025-26'], res[k]['2026-27']
        se = []
        for p in parts:
            dd = [x - y for x, y in zip(res[k][p]['llg'], res['current'][p]['llg'])]
            m = sum(dd) / len(dd)
            se.append(math.sqrt(sum((x - m) ** 2 for x in dd) / (len(dd) - 1) / len(dd)) if any(dd) else 0)
        print(f"{k:30} {a['ll']:8.4f} {se[0]:6.4f} {b['ll']:8.4f} {se[1]:6.4f} {a['br']:7.4f} {b['br']:7.4f} {a['top']:5d} "
              f"{b['top']:5d} {a['topfga']:6d} {b['topfga']:6d} {a['bets'] / nights['2025-26']:8.1f} "
              f"{b['bets'] / nights['2026-27']:8.1f}")
    for k in [x for x in variants if x in sys.argv[1:]] or ['current', 'fix1']:
        for p in parts:
            print(f"\ncalibration by decile, {k}, {p} (pred / hit):",
                  ' '.join(f"{a_:.1%}/{h:.1%}" for a_, h in res[k][p]['dec']))
    json.dump({k: {p: {x: y for x, y in v.items() if x != 'llg'} for p, v in r.items()} for k, r in res.items()},
              open(os.path.join(HERE, 'out', 'backtest_fix.json'), 'w'), indent=1)
    return res, parts


if __name__ == '__main__':
    main()
