#!/usr/bin/env python3
"""Backtest half of the 11/19/26 first basket diagnostic (see diagnostic.py).

Walk-forward chain backtest (backtest_chain.run, actual starters and jumpers). A wrapper on chain_model.game_probs
records, per game, the tip chance pt and the chain's player chances for each tip outcome, so tip, team and player
fixes can be fit on early games and scored on held-out games without rerunning the chain.

  python3 analysis/nba/reports/diagnostic_bt.py          # all sections
  python3 analysis/nba/reports/diagnostic_bt.py --w 6    # 26-27 game weight 6 instead of 3 (recency test)
  python3 analysis/nba/reports/diagnostic_bt.py --ch '{"k_sh1": 20}'   # chain settings (opening tendencies)
"""
import collections, math, os, pickle, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NBA = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, NBA)
import backtest_chain as bc  # noqa: E402
import backtest_fix as bf  # noqa: E402
import chain_model as cm  # noqa: E402

TEST_FROM = '2026-11-01'   # held out: 2026-27 games on or after this date
CACHE = os.environ.get('DIAG_CACHE')   # optional pickle path for the records
_orig = cm.game_probs
LOG = []


def _wrap(teams, ptip_a, c=cm.CH):
    A = cm.play(teams, 0, c)
    B = cm.play(teams, 1, c)
    LOG.append(dict(pt=ptip_a, A=A, B=B, pids=[[x['pid'] for x in t.P] for t in teams]))
    return [[ptip_a * x + (1 - ptip_a) * y for x, y in zip(A[t], B[t])] for t in (0, 1)]


def load(variants=None, w=None, tag=''):
    key = f"{CACHE}.{w}{tag}" if CACHE else None
    if key and os.path.exists(key):
        return pickle.load(open(key, 'rb'))
    if w:
        bf.W_DEFAULT = w
    cm.game_probs = _wrap
    LOG.clear()
    recs = bc.run(variants or {'chain': {}})
    cm.game_probs = _orig
    assert len(LOG) == len(recs), (len(LOG), len(recs))
    for r, x in zip(recs, LOG):
        g = r['g']
        r.update(pt=x['pt'], A=x['A'], B=x['B'], pids=x['pids'], away=g['away'], home=g['home'],
                 tipw=g['tip']['w'], fpteam=g['fp'][1])
        r.pop('book', None)
    if key:
        pickle.dump(recs, open(key, 'wb'))
    return recs


def predict(r, s=1.0, t=1.0, u=1.0):
    """Player chances after the fixes:
    u  tip shrink: pt' = 0.5 + u (pt - 0.5)
    s  tip-winner edge: P(team with the ball first scores first) moved to 0.5 + s (X - 0.5)
    t  within-team temperature: shares inside each team ~ p ** t (t < 1 flattens)"""
    pt = 0.5 + u * (r['pt'] - 0.5)
    out = {}
    for first, w in ((r['A'], pt), (r['B'], 1 - pt)):
        tot = [sum(first[0]), sum(first[1])]
        z = tot[0] + tot[1]
        tot = [v / z for v in tot]
        lead = 0 if first is r['A'] else 1
        x = 0.5 + s * (tot[lead] - 0.5)
        newtot = [x, 1 - x] if lead == 0 else [1 - x, x]
        for k in (0, 1):
            q = [max(v, 1e-9) ** t for v in first[k]]
            zq = sum(q)
            for pid, v in zip(r['pids'][k], q):
                out[pid] = out.get(pid, 0) + w * newtot[k] * v / zq
    return out


def ll(recs, **kw):
    n = tot = 0
    for r in recs:
        p = predict(r, **kw)
        if r['win'] in p:
            n += 1; tot -= math.log(max(p[r['win']], 1e-9))
    return tot / n


def topk(recs, k=3, **kw):
    h = 0
    for r in recs:
        p = predict(r, **kw)
        h += r['win'] in sorted(p, key=p.get, reverse=True)[:k]
    return h


def split(recs):
    tr = [r for r in recs if r['d'] < TEST_FROM]
    te = [r for r in recs if r['d'] >= TEST_FROM]
    tr26 = [r for r in tr if r['d'] >= '2026-07-01']
    return tr, tr26, te


def sec_links(recs):
    print('\n## BT: chain links by season (actual starters and jumpers)')
    print('| Season | Games | Tip fav won (pred) | Tip 70%+ games: won (pred) | Tip winner scored first (model X) | Team-first scorer in chain team top 2 | Game top 3 (pred) |')
    print('|---|---|---|---|---|---|---|')
    for lab, rs in (('2025-26', [r for r in recs if r['d'] < '2026-07-01']),
                    ('2026-27 to 10/31', [r for r in recs if '2026-07-01' <= r['d'] < TEST_FROM]),
                    ('2026-27 11/1 on', [r for r in recs if r['d'] >= TEST_FROM])):
        n = len(rs)
        fav = sum((r['pt'] > .5) == (r['tipw'] == r['away']) for r in rs if r['pt'] != .5)
        pf = sum(max(r['pt'], 1 - r['pt']) for r in rs) / n
        hi = [r for r in rs if max(r['pt'], 1 - r['pt']) >= .70]
        hiw = sum((r['pt'] > .5) == (r['tipw'] == r['away']) for r in hi)
        hip = sum(max(r['pt'], 1 - r['pt']) for r in hi) / max(1, len(hi))
        tw = sum(r['tipw'] == r['fpteam'] for r in rs)
        X = []
        for r in rs:
            for first, lead in ((r['A'], 0), (r['B'], 1)):
                z = sum(first[0]) + sum(first[1])
                X.append(sum(first[lead]) / z)
        t2 = tn = 0
        for r in rs:
            for k, tm in enumerate((r['away'], r['home'])):
                tgt = r['tp'].get(tm)
                if not tgt:
                    continue
                tpr = r['team']['chain']
                mine = sorted(r['pids'][k], key=lambda p: -tpr.get(p, 0))[:2]
                tn += 1; t2 += tgt in mine
        p = [predict(r) for r in rs]
        t3 = sum(r['win'] in sorted(q, key=q.get, reverse=True)[:3] for r, q in zip(rs, p))
        e3 = sum(sum(sorted(q.values(), reverse=True)[:3]) for q in p)
        print(f"| {lab} | {n} | {fav}/{n} {fav / n:.0%} ({pf:.0%}) | {hiw}/{len(hi)} {hiw / max(1, len(hi)):.0%} ({hip:.0%}) | "
              f"{tw}/{n} {tw / n:.0%} ({sum(X) / len(X):.0%}) | {t2}/{tn} {t2 / tn:.0%} | {t3}/{n} {t3 / n:.0%} ({e3 / n:.0%}) |")


def sec_calib(recs):
    print('\n## BT: calibration, 2026-27 (actual starters)')
    rs = [r for r in recs if r['d'] >= '2026-07-01']
    B = ((0, .05), (.05, .08), (.08, .11), (.11, .14), (.14, .18), (.18, .22), (.22, 1))
    rows = collections.defaultdict(lambda: [0, 0.0, 0])
    rk = collections.defaultdict(lambda: [0, 0.0, 0])
    trk = collections.defaultdict(lambda: [0, 0.0, 0])
    for r in rs:
        p = predict(r)
        for i, (pid, v) in enumerate(sorted(p.items(), key=lambda x: -x[1])):
            b = next(j for j, (lo, hi) in enumerate(B) if lo <= v < hi)
            rows[b][0] += 1; rows[b][1] += v; rows[b][2] += pid == r['win']
            rk[i][0] += 1; rk[i][1] += v; rk[i][2] += pid == r['win']
        for k, tm in enumerate((r['away'], r['home'])):
            tgt = r['tp'].get(tm)
            if not tgt:
                continue
            tpr = r['team']['chain']
            for i, pid in enumerate(sorted(r['pids'][k], key=lambda q: -tpr.get(q, 0))):
                trk[i][0] += 1; trk[i][1] += tpr.get(pid, 0); trk[i][2] += pid == tgt
    print('| Predicted | Players | Avg pred | Hit rate | Hits | Expected |')
    print('|---|---|---|---|---|---|')
    for j, (lo, hi) in enumerate(B):
        n, s, h = rows[j]
        if n:
            print(f"| {lo:.0%}-{hi:.0%} | {n} | {s / n:.1%} | {h / n:.1%} | {h} | {s:.1f} |")
    print('Game rank: ' + '; '.join(f"#{i + 1} {rk[i][1] / rk[i][0]:.1%} / {rk[i][2] / rk[i][0]:.1%}" for i in range(6)))
    print('Team rank (share of team first points): ' + '; '.join(f"#{i + 1} {trk[i][1] / trk[i][0]:.1%} / {trk[i][2] / trk[i][0]:.1%}" for i in range(5)))


def sec_fix(recs, label='W 3'):
    tr, tr26, te = split(recs)
    print(f'\n## BT fixes ({label}): fit on games before {TEST_FROM}, scored on {len(te)} held-out games from {TEST_FROM}')
    grid = [dict(s=s, t=t, u=u) for s in (0.5, 0.7, 0.85, 1.0, 1.15) for t in (0.6, 0.8, 1.0, 1.2) for u in (0.6, 0.8, 1.0)]
    for name, fit in (('fit on 2025-26 + 26-27 to 10/31', tr), ('fit on 26-27 to 10/31 only', tr26)):
        best = min(grid, key=lambda kw: ll(fit, **kw))
        print(f"{name} ({len(fit)} games): best {best}")
    print('| Variant | Held-out LL | Paired SE vs chain | Top 1 | Top 3 | Train LL (all) |')
    print('|---|---|---|---|---|---|')
    base = [-math.log(max(predict(r).get(r['win'], 1e-9), 1e-9)) for r in te]
    for lab, kw in (('chain (live model)', {}), ('uniform (1/10 each)', None),
                    ('tip shrink u 0.8', dict(u=0.8)), ('tip shrink u 0.6', dict(u=0.6)),
                    ('tip-winner edge s 0.7', dict(s=0.7)), ('tip-winner edge s 0.5', dict(s=0.5)),
                    ('flatten t 0.8', dict(t=0.8)), ('flatten t 0.6', dict(t=0.6)), ('sharpen t 1.2', dict(t=1.2)),
                    ('u 0.8 + s 0.7', dict(u=0.8, s=0.7)), ('u 0.8 + s 0.7 + t 0.8', dict(u=0.8, s=0.7, t=0.8))):
        if kw is None:
            v = math.log(10)
            print(f"| {lab} | {v:.4f} | | {len(te) / 10:.0f} exp | {len(te) * .3:.0f} exp | |")
            continue
        x = [-math.log(max(predict(r, **kw).get(r['win'], 1e-9), 1e-9)) for r in te]
        d = [a - b for a, b in zip(x, base)]
        m = sum(d) / len(d)
        se = math.sqrt(sum((y - m) ** 2 for y in d) / (len(d) - 1) / len(d)) if any(d) else 0
        print(f"| {lab} | {sum(x) / len(x):.4f} | {m:+.4f} ({se:.4f}) | {topk(te, 1, **kw)} | {topk(te, 3, **kw)} | {ll(tr, **kw):.4f} |")


def sec_team_market(recs):
    """Team first basket and 'tip winner team' angles on held-out games."""
    _, _, te = split(recs)
    print('\n## BT: team first basket vs game first basket (held-out)')
    t2 = tn = 0
    for r in te:
        for k, tm in enumerate((r['away'], r['home'])):
            tgt = r['tp'].get(tm)
            if tgt:
                tpr = r['team']['chain']
                mine = sorted(r['pids'][k], key=lambda p: -tpr.get(p, 0))
                tn += 1; t2 += tgt in mine[:2]
    print(f"team top 2 hit {t2}/{tn} ({t2 / tn:.0%}); random 40%")


def main():
    w = None
    if '--w' in sys.argv:
        w = int(sys.argv[sys.argv.index('--w') + 1])
    ch = {}
    if '--ch' in sys.argv:   # chain settings, e.g. --ch '{"k_sh1": 20, "k_f3": 20}' (opening-tendency test)
        import json
        ch = json.loads(sys.argv[sys.argv.index('--ch') + 1])
    recs = load({'chain': ch}, w=w, tag=str(sorted(ch.items())) if ch else '')
    print('BT records', len(recs), 'through', recs[-1]['d'])
    sec_links(recs)
    sec_calib(recs)
    sec_fix(recs, f'W {w or 3} {ch or ""}')
    sec_team_market(recs)
    sec_tip70(recs)
    sec_first_shot(recs)
    sec_exception(recs)
    if '--live' in sys.argv or __name__ != '__main__':
        import diagnostic as D
        sec_matched(recs, D.live(), D.top3_hit)
    return recs



def sec_tip70(recs):
    print('\n## BT: tip 70%+ games vs the rest (actual starters and jumpers)')
    print('| Season | Group | Games | Fav won tip (pred) | Fav team scored first (pred) | Top 3 (pred) |')
    print('|---|---|---|---|---|---|')
    for lab, rs in (('2025-26', [r for r in recs if r['d'] < '2026-07-01']), ('2026-27', [r for r in recs if r['d'] >= '2026-07-01'])):
        for gl, f in (('tip 70%+', lambda r: max(r['pt'], 1 - r['pt']) >= .7), ('tip < 70%', lambda r: max(r['pt'], 1 - r['pt']) < .7)):
            g = [r for r in rs if f(r)]
            n = len(g)
            fw = sum((r['pt'] > .5) == (r['tipw'] == r['away']) for r in g)
            pf = sum(max(r['pt'], 1 - r['pt']) for r in g) / n
            fs = fp = 0
            t3 = e3 = 0
            for r in g:
                p = predict(r)
                fav = r['away'] if r['pt'] > .5 else r['home']
                k = 0 if fav == r['away'] else 1
                fp += sum(p.get(x, 0) for x in r['pids'][k]) / sum(p.values())
                fs += r['fpteam'] == fav
                top = sorted(p, key=p.get, reverse=True)[:3]
                t3 += r['win'] in top; e3 += sum(p[x] for x in top)
            print(f"| {lab} | {gl} | {n} | {fw / n:.0%} ({pf:.0%}) | {fs / n:.0%} ({fp / n:.0%}) | {t3 / n:.0%} ({e3 / n:.0%}) |")


def sec_first_shot(recs):
    print('\n## BT: first FGA of each team goes in (games data, tsm)')
    for lab, rs in (('2025-26', [r for r in recs if r['d'] < '2026-07-01']), ('2026-27 to 10/31', [r for r in recs if '2026-07-01' <= r['d'] < TEST_FROM]),
                    ('2026-27 11/1 on', [r for r in recs if r['d'] >= TEST_FROM])):
        m = n = 0
        for r in rs:
            for v in r['g'].get('tsm', {}).values():
                n += 1; m += bool(v)
        print(f"  {lab}: team first FGA made {m}/{n} ({m / n:.1%})")


def matched(recs, L):
    """Live published picks vs the same model with actual starters, same games."""
    import source_scorecard as sc
    by = {(r['d'], r['away'], r['home']): r for r in recs}
    rows = []
    for x in L:
        r = by.get((x['d'], x['a'], x['h']))
        if not r:
            continue
        p = predict(r)
        nm = r['g']['nm']
        top = [sc.norm(nm[q]) for q in sorted(p, key=p.get, reverse=True)[:3]]
        rows.append((x, top, -math.log(max(p.get(r['win'], 1e-9), 1e-9))))
    return rows


def sec_matched(recs, L, top3_hit):
    rows = matched(recs, L)
    n = len(rows)
    live = sum(top3_hit(x) for x, _, _ in rows)
    bt = sum(x['fp'] in top for x, top, _ in rows)
    print(f"\n## Live vs actual starters, same {n} games: live top 3 {live}/{n} ({live / n:.0%}), "
          f"same model with actual fives and jumpers {bt}/{n} ({bt / n:.0%})")
    for lab, f in (('play list 11/14+', lambda x: x['play']), ('11/17-11/19', lambda x: x['d'] >= '2026-11-17')):
        g = [(x, t) for x, t, _ in rows if f(x)]
        print(f"  {lab}: live {sum(top3_hit(x) for x, _ in g)}/{len(g)}, actual fives {sum(x['fp'] in t for x, t in g)}/{len(g)}")



def sec_exception(recs):
    """Does a team's past top-2 hit rate (model-accuracy exception, 11/15) predict its next game? 2026-27, walk-forward."""
    print('\n## BT: model-accuracy exception check (team past top-2 hit rate -> next game)')
    past = collections.defaultdict(list)
    buckets = collections.defaultdict(lambda: [0, 0])
    for r in sorted((r for r in recs if r['d'] >= '2026-07-01'), key=lambda r: r['d']):
        upd = []
        for k, tm in enumerate((r['away'], r['home'])):
            tgt = r['tp'].get(tm)
            if not tgt:
                continue
            tpr = r['team']['chain']
            hit = tgt in sorted(r['pids'][k], key=lambda p: -tpr.get(p, 0))[:2]
            h = past[tm]
            if len(h) >= 5:
                rate = sum(h) / len(h)
                b = '55%+' if rate >= .55 else ('45-55%' if rate >= .45 else 'under 45%')
                buckets[b][0] += hit; buckets[b][1] += 1
            upd.append((tm, hit))
        for tm, hit in upd:
            past[tm].append(hit)
    for b in ('55%+', '45-55%', 'under 45%'):
        h, n = buckets[b]
        print(f"  past rate {b}: next game top 2 hit {h}/{n} ({h / max(1, n):.0%})")


if __name__ == '__main__':
    main()
