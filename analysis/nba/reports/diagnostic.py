#!/usr/bin/env python3
"""NBA first basket diagnostic (Tim, 11/19/26: "Then let's figure it out. What's missing?").

Two data sets:
  LIVE  what we actually published: the last fb_candidates.json / shortlist.md committed for each graded date
        (analysis/reports/source_scorecard.COMMITS), projected fives, Out players removed. 11/4 onward.
  BT    walk-forward backtest (backtest_chain.run): same chain model, ACTUAL starters and jumpers, no lookahead.
        2025-26 from 12/1 (933 games) + 2026-27 (all graded games). Separates model error from lineup error.

  python3 analysis/nba/reports/diagnostic.py            # all sections
  python3 analysis/nba/reports/diagnostic.py live       # live sections only (fast)
Results are written up in analysis/nba/reports/diagnostic-2026-11-19.md.
"""
import collections, csv, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(R, 'analysis', 'reports'))
sys.path.insert(0, os.path.join(R, 'analysis', 'nba'))
import source_scorecard as sc  # noqa: E402

norm = sc.norm
PLAY = {  # play-list games as placed (out/play_list_<date>.md); value = 'tip' (tip 70%+) or 'exc' (model-accuracy exception)
    '2026-11-14': {('DEN', 'NO'): 'tip', ('DAL', 'CLE'): 'tip', ('DET', 'MIA'): 'tip', ('CHI', 'MIN'): 'tip'},
    '2026-11-15': {('LAL', 'PHX'): 'tip', ('CHA', 'LAC'): 'tip', ('SA', 'UTAH'): 'tip', ('ATL', 'MIL'): 'exc'},
    '2026-11-16': {('CHI', 'CLE'): 'tip', ('HOU', 'MIA'): 'tip', ('PHX', 'DEN'): 'tip'},
    '2026-11-17': {('DET', 'SA'): 'tip', ('UTAH', 'LAC'): 'tip'},
    '2026-11-18': {('PHI', 'ORL'): 'tip', ('CHI', 'BKN'): 'tip', ('DET', 'NO'): 'tip'},
    '2026-11-19': {('GS', 'MEM'): 'tip', ('LAC', 'SA'): 'tip', ('NY', 'MIN'): 'exc'},
}
pct = lambda a, b: f"{a}/{b} ({100 * a / b:.0f}%)" if b else '-'


def week_of(d):
    return {'2026-11-0': 'wk 11/4-11/9'}.get(d[:9], None) or ('wk 11/11-11/15' if d <= '2026-11-15' else 'wk 11/16-11/19')


def live():
    games = json.load(open(R + '/analysis/nba/data/games_2026-27.json'))
    opening = json.load(open(R + '/analysis/nba/data/opening_2026-27.json'))
    fe = {(r['date'], r['game'].replace(' ', '')): r for r in csv.DictReader(open(R + '/analysis/first_events/log.csv'))
          if r['sport'] == 'NBA'}
    out = []
    for d, c in sc.COMMITS.items():
        cand = json.loads(sc.show(c, 'analysis/nba/out/fb_candidates.json'))
        sl = sc.show(c, 'analysis/nba/out/shortlist.md')
        tipline = {}
        for m in re.finditer(r'- (\S+) @ (\S+) [\d:]+ ET: (.+?) vs (.+?); away wins tip (\d+)%, away scores first (\d+)%', sl):
            tipline[(m.group(1), m.group(2))] = (m.group(3), m.group(4), int(m.group(5)) / 100, int(m.group(6)) / 100)
        for g in games.values():
            if g.get('date') != d or g['type'] != 2 or not g.get('fp') or not g.get('tip'):
                continue
            a, h = g['away'], g['home']
            if (a, h) not in tipline:
                continue
            nm = g['nm']
            starters = {tm: {norm(nm[p[0]]) for p in g['pl'] if p[1] == tm and p[2]} for tm in (a, h)}
            played = {norm(nm[p[0]]) for p in g['pl'] if p[0] in nm}
            C = {tm: sorted([r for r in cand if r['tm'] == tm and r.get('inj') != 'Out'], key=lambda r: -r['p_v2'])
                 for tm in (a, h)}
            if not C[a] or not C[h]:
                continue
            for tm in (a, h):   # team_share is logged from 11/8; before that use the share of the team's game chance
                z = sum(x['p_v2'] for x in C[tm])
                for x in C[tm]:
                    x.setdefault('team_share', x['p_v2'] / z)
            ja, jh, pa, pfa = tipline[(a, h)]
            tp = opening.get(g['id'], {}).get('tp', {})
            ev = fe.get((d, f'{a}@{h}'), {})
            act_j = {tm: norm(nm.get(pid, '?')) for pid, tm in g['tip']['j']}
            rec = dict(d=d, a=a, h=h, play=PLAY.get(d, {}).get((a, h)), tipfav=a if pa > .5 else h, ptip=max(pa, 1 - pa),
                       pfirst_fav=pfa if pa > .5 else 1 - pfa, tipw=g['tip']['w'],
                       fp=norm(nm[g['fp'][0]]), fpname=nm[g['fp'][0]], fpteam=g['fp'][1],
                       tp={tm: norm(nm.get(pid, '?')) for tm, pid in tp.items()},
                       pred_j={a: norm(ja), h: norm(jh)}, act_j=act_j, starters=starters, played=played, C=C,
                       first_shot_made=ev.get('first_shot_result') == 'made', fga_to_make=ev.get('fga_to_first_make'),
                       fp_method=ev.get('first_points_method'))
            out.append(rec)
    return out


def ranked(rec):
    both = [r for tm in (rec['a'], rec['h']) for r in rec['C'][tm]]
    return sorted(both, key=lambda r: -r['p_v2'])


def top3_hit(rec):
    return any(norm(r['player']) == rec['fp'] for r in ranked(rec)[:3])


def section_drift(L):
    print('\n## 1. Drift: top 3 and tip by week / last 14 days')
    by = collections.defaultdict(list)
    for r in L:
        by[week_of(r['d'])].append(r)
        by['last 14 (11/6-11/19)' if r['d'] >= '2026-11-06' else 'before (11/4-11/5)'].append(r)
        by['last 7 (11/13-11/19)' if r['d'] >= '2026-11-13' else 'before 11/13 (11/4-11/12)'].append(r)
        by['ALL'].append(r)
    exp = lambda rs: sum(sum(x['p_v2'] for x in ranked(r)[:3]) for r in rs)
    print('| Span | Games | Top 3 hit | Top 3 expected | #1 hit | #1 expected | Tip right | Tip expected |')
    print('|---|---|---|---|---|---|---|---|')
    for k in ('wk 11/4-11/9', 'wk 11/11-11/15', 'wk 11/16-11/19', 'before 11/13 (11/4-11/12)', 'last 7 (11/13-11/19)', 'ALL'):
        rs = by[k]
        t3 = sum(top3_hit(r) for r in rs)
        n1 = sum(norm(ranked(r)[0]['player']) == r['fp'] for r in rs)
        tip = sum(r['tipfav'] == r['tipw'] for r in rs)
        print(f"| {k} | {len(rs)} | {pct(t3, len(rs))} | {exp(rs) / len(rs):.0%} | {pct(n1, len(rs))} | "
              f"{sum(ranked(r)[0]['p_v2'] for r in rs) / len(rs):.0%} | {pct(tip, len(rs))} | {sum(r['ptip'] for r in rs) / len(rs):.0%} |")
    # binomial: chance of <= observed top-3 hits if the model's own probabilities were right
    rs = by['last 7 (11/13-11/19)']
    ps = [sum(x['p_v2'] for x in ranked(r)[:3]) for r in rs]
    obs = sum(top3_hit(r) for r in rs)
    print(f"\nLast 7 days: observed {obs} of {len(rs)}, model expected {sum(ps):.1f}. P(<= observed | model right) = {poibin_cdf(ps, obs):.2f}")
    ps = [sum(x['p_v2'] for x in ranked(r)[:3]) for r in L]
    obs = sum(top3_hit(r) for r in L)
    print(f"Season live: observed {obs} of {len(L)}, model expected {sum(ps):.1f}. P(<= observed | model right) = {poibin_cdf(ps, obs):.3f}")
    PLx = [r for r in L if r['play']]
    for lo, hi, lab in (('2026-11-17', '2026-11-19', 'play list 11/17-11/19'),):
        rs = [r for r in PLx if lo <= r['d'] <= hi]
        ps = [sum(x['p_v2'] for x in ranked(r)[:3]) for r in rs]
        obs = sum(top3_hit(r) for r in rs)
        print(f"{lab}: observed {obs} of {len(rs)}, expected {sum(ps):.1f}; P(0 | model right) = {math.prod(1 - p for p in ps):.3f}")


def poibin_cdf(ps, k):
    dist = [1.0]
    for p in ps:
        nd = [0.0] * (len(dist) + 1)
        for i, v in enumerate(dist):
            nd[i] += v * (1 - p); nd[i + 1] += v * p
        dist = nd
    return sum(dist[:k + 1])


def section_selection(L):
    print('\n## 2. Selection: play-list games vs the rest (11/14-11/19, when the play list existed)')
    rs = [r for r in L if r['d'] >= '2026-11-14']
    print('| Group | Games | Tip right | Tip pred | Tip winner scored first | Fav team scored first (pred) | Top 3 hit (exp) | #1 hit (exp) |')
    print('|---|---|---|---|---|---|---|---|')
    groups = (('play list, tip 70%+', [r for r in rs if r['play'] == 'tip']), ('play list, exception', [r for r in rs if r['play'] == 'exc']),
              ('not played', [r for r in rs if not r['play']]),
              ('ALL season: tip fav 70%+', [r for r in L if r['ptip'] >= .70]), ('ALL season: tip fav < 70%', [r for r in L if r['ptip'] < .70]))
    for lab, g in groups:
        if not g:
            continue
        n = len(g)
        print(f"| {lab} | {n} | {pct(sum(r['tipfav'] == r['tipw'] for r in g), n)} | {sum(r['ptip'] for r in g) / n:.0%} | "
              f"{pct(sum(r['tipw'] == r['fpteam'] for r in g), n)} | {pct(sum(r['tipfav'] == r['fpteam'] for r in g), n)} ({sum(r['pfirst_fav'] for r in g) / n:.0%}) | "
              f"{pct(sum(top3_hit(r) for r in g), n)} ({sum(sum(x['p_v2'] for x in ranked(r)[:3]) for r in g) / n:.0%}) | "
              f"{pct(sum(norm(ranked(r)[0]['player']) == r['fp'] for r in g), n)} ({sum(ranked(r)[0]['p_v2'] for r in g) / n:.0%}) |")
    # where do top-3 picks sit: how many of the 3 on the tip favorite team
    print('\nTop 3 composition (season live): picks on the tip-favorite team')
    cnt = collections.Counter()
    hit = collections.Counter()
    for r in L:
        k = sum(x['tm'] == r['tipfav'] for x in ranked(r)[:3])
        cnt[k] += 1; hit[k] += top3_hit(r)
    for k in sorted(cnt):
        print(f"  {k} of 3 on the fav team: {cnt[k]} games, top 3 hit {pct(hit[k], cnt[k])}")


def section_chain(L):
    print('\n## 3. Chain breakdown (live, all graded games)')
    n = len(L)
    a = sum(r['tipfav'] == r['tipw'] for r in L)
    print(f"(a) tip favorite won the tip: {pct(a, n)}, predicted {sum(r['ptip'] for r in L) / n:.0%}")
    b = sum(r['tipw'] == r['fpteam'] for r in L)
    print(f"(b) tip winner scored first: {pct(b, n)} (model assumes about 64% via the chain; 2025-26 league 64%)")
    fav = sum(r['tipfav'] == r['fpteam'] for r in L)
    print(f"    tip favorite TEAM scored first: {pct(fav, n)}, predicted {sum(r['pfirst_fav'] for r in L) / n:.0%}")
    # (c) within team
    t2 = t1 = tn = 0; share_sum = 0
    for r in L:
        tm = r['fpteam']
        c = r['C'][tm]
        names = [norm(x['player']) for x in sorted(c, key=lambda x: -x['team_share'])]
        tn += 1; t1 += names[:1] == [r['fp']]; t2 += r['fp'] in names[:2]
        share_sum += sum(x['team_share'] for x in c[:2])
    in5 = sum(r['fp'] in {norm(x['player']) for x in r['C'][r['fpteam']]} for r in L)
    print(f"(c) scorer in OUR projected five of his team: {pct(in5, n)}; our team #1 {pct(t1, tn)}, team top 2 {pct(t2, tn)} "
          f"(predicted top 2 share {share_sum / tn:.0%})")
    fs = sum(r['first_shot_made'] for r in L)
    print(f"(d) game's first shot went in: {pct(fs, n)} (2025-26: 48.6%; model make rates are full-game, about 47-50%)")
    # combined: which link broke in each top-3 miss
    print('\nTop 3 misses, first broken link:')
    why = collections.Counter()
    for r in L:
        if top3_hit(r):
            why['hit'] += 1; continue
        top = ranked(r)[:3]
        if r['fp'] not in {norm(x['player']) for x in r['C'][r['fpteam']]}:
            why['scorer not in our projected five (lineup)'] += 1
        elif r['tipfav'] != r['tipw']:
            why['lost the tip'] += 1
        elif r['tipw'] != r['fpteam']:
            why['won tip, other team scored first'] += 1
        elif all(x['tm'] != r['fpteam'] for x in top):
            why['right team, but no top-3 pick on it'] += 1
        else:
            why['right team, wrong player'] += 1
    for k, v in why.most_common():
        print(f"  {k}: {v}")
    # first shot made vs missed and our picks
    print('\nFirst shot made vs missed, top 3 hit:')
    for flag in (True, False):
        g = [r for r in L if r['first_shot_made'] == flag]
        print(f"  first shot {'made' if flag else 'missed'}: {len(g)} games, top 3 {pct(sum(top3_hit(r) for r in g), len(g))}")


def section_calibration(L):
    print('\n## 4. Calibration (live, every projected starter, game first points chance)')
    B = ((0, .05), (.05, .08), (.08, .11), (.11, .14), (.14, .18), (.18, .22), (.22, 1))
    rows = collections.defaultdict(lambda: [0, 0.0, 0])
    for r in L:
        for x in ranked(r):
            if norm(x['player']) not in r['played']:
                continue
            p = x['p_v2']
            b = next(i for i, (lo, hi) in enumerate(B) if lo <= p < hi)
            rows[b][0] += 1; rows[b][1] += p; rows[b][2] += norm(x['player']) == r['fp']
    print('| Predicted | Players | Avg pred | Hit rate | Hits | Expected hits |')
    print('|---|---|---|---|---|---|')
    for i, (lo, hi) in enumerate(B):
        n, s, h = rows[i]
        if n:
            print(f"| {lo:.0%}-{hi:.0%} | {n} | {s / n:.1%} | {h / n:.1%} | {h} | {s:.1f} |")
    print('\nBy game rank:')
    for k in range(10):
        g = [(ranked(r)[k], r) for r in L if len(ranked(r)) > k]
        g = [(x, r) for x, r in g if norm(x['player']) in r['played']]
        if g:
            print(f"  #{k + 1}: pred {sum(x['p_v2'] for x, r in g) / len(g):.1%}, hit {pct(sum(norm(x['player']) == r['fp'] for x, r in g), len(g))}")
    print('\nBy rank within his team (team_share order): predicted share of team first points vs actual')
    for k in range(5):
        n = s = h = 0
        for r in L:
            for tm in (r['a'], r['h']):
                if tm not in r['tp']:
                    continue
                c = sorted(r['C'][tm], key=lambda x: -x['team_share'])
                if len(c) > k:
                    n += 1; s += c[k]['team_share']; h += norm(c[k]['player']) == r['tp'][tm]
        print(f"  team #{k + 1}: pred {s / n:.1%}, actual {pct(h, n)}")
    nonstart = sum(r['tp'].get(tm) not in {norm(x['player']) for x in r['C'][tm]} for r in L for tm in (r['a'], r['h']) if tm in r['tp'])
    print(f"  team first scorer not in our projected five: {nonstart} of {sum(len(r['tp']) for r in L)}")


def section_data(L):
    print('\n## 5. Data checks (live)')
    jm = jn = 0; badj = []
    five_wrong = 0; fp_unproj = 0
    for r in L:
        for tm in (r['a'], r['h']):
            if tm in r['act_j']:
                jn += 1
                if r['pred_j'][tm] == r['act_j'][tm]:
                    jm += 1
                else:
                    badj.append((r['d'], tm, r['pred_j'][tm], r['act_j'][tm]))
            proj = {norm(x['player']) for x in r['C'][tm]}
            if proj != r['starters'][tm]:
                five_wrong += 1
        if r['fp'] not in {norm(x['player']) for tm in (r['a'], r['h']) for x in r['C'][tm]}:
            fp_unproj += 1
    print(f"Jumper right: {pct(jm, jn)} team-games. Wrong jumpers ({len(badj)}):")
    for x in badj:
        print('  ', *x)
    print(f"Projected five not the actual five: {five_wrong} of {2 * len(L)} team-games")
    print(f"Game first scorer was not a projected starter: {fp_unproj} of {len(L)}")
    # tip right by whether jumpers were right
    for ok in (True, False):
        g = [r for r in L if all(r['pred_j'][t] == r['act_j'].get(t) for t in (r['a'], r['h'])) == ok]
        print(f"  both jumpers right={ok}: {len(g)} games, tip right {pct(sum(r['tipfav'] == r['tipw'] for r in g), len(g))}, "
              f"pred {sum(r['ptip'] for r in g) / max(1, len(g)):.0%}")


def section_sources(L):
    """Ours vs StarTool vs cheat sheet (@NBAFirstBasket 1st Gm %) vs simple blends, same games, game first points."""
    print('\n## 6. Sources on the same games (game first points; each source normalized over our projected ten)')
    srcs = {'StarTool': sc.ST, 'Cheat sheet': sc.SH}
    rows = []
    for r in L:
        ours = {norm(x['player']): x['p_v2'] for tm in (r['a'], r['h']) for x in r['C'][tm]}
        ext = {}
        for s, P in srcs.items():
            m = {}
            for tm in (r['a'], r['h']):
                for x in P.get((r['d'], tm), []):
                    v = x[2] if s == 'Cheat sheet' else x[1]
                    if v is not None:
                        m[norm(x[0])] = v / 100
            if len(m) >= 8:
                ext[s] = m
        rows.append((r, ours, ext))

    def dist(m, keys, floor):
        v = {k: max(m.get(k, floor), floor) for k in keys}
        z = sum(v.values())
        return {k: x / z for k, x in v.items()}

    for combo in (('StarTool',), ('Cheat sheet',), ('StarTool', 'Cheat sheet')):
        g = [(r, o, e) for r, o, e in rows if all(s in e for s in combo)]
        if not g:
            continue
        res = collections.defaultdict(lambda: [0, 0.0, 0])
        for r, o, e in g:
            keys = list(o)
            D = {'Ours': dist(o, keys, 0.03)}
            for s in combo:
                D[s] = dist(e[s], keys, 0.03)
            for s in combo:
                D[f'50/50 ours + {s}'] = {k: .5 * D['Ours'][k] + .5 * D[s][k] for k in keys}
            if len(combo) == 2:
                D['equal blend of 3'] = {k: sum(D[s][k] for s in ('Ours',) + combo) / 3 for k in keys}
            for name, p in D.items():
                top = sorted(p, key=p.get, reverse=True)[:3]
                a = res[name]
                a[0] += r['fp'] in top
                a[2] += sorted(p, key=p.get, reverse=True)[0] == r['fp']
                a[1] += -math.log(p[r['fp']]) if r['fp'] in p else math.log(10)
        print(f"\nGames where {' and '.join(combo)} printed % for 8+ starters: {len(g)}")
        print('| Source | Top 3 hit | #1 hit | Log loss (lower is better; uniform 2.303) |')
        print('|---|---|---|---|')
        for name, (h, l, t1) in res.items():
            print(f"| {name} | {pct(h, len(g))} | {pct(t1, len(g))} | {l / len(g):.3f} |")


if __name__ == '__main__':
    L = live()
    print('live games', len(L), 'dates', sorted({r['d'] for r in L})[0], '-', sorted({r['d'] for r in L})[-1])
    section_drift(L)
    section_selection(L)
    section_chain(L)
    section_calibration(L)
    section_data(L)
    section_sources(L)
    if 'live' not in sys.argv[1:]:
        import diagnostic_bt
        diagnostic_bt.main()
