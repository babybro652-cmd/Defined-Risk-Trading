#!/usr/bin/env python3
"""FVG / IFVG tag test, 11/18/2026 (private; indicator names fine here, never in public copy).

Tim, 11/18: "On the indicators, can you say if there was an fvg or ifvg."
Tags every scored signal from indicator_analysis.py (CRT Pro, VMap, Forward Test BUY/SELL, Div labels,
CRT tags) for a Fair Value Gap or Inverse FVG at entry, on 1m bars (where cached, 10/20 on), 2m (10/13 on)
and 5m (9/10 on), then scores each tag group Tim's way.

Definitions (standard ICT, OHLC only):
  - Bullish FVG: 3 consecutive candles, candle 3 low > candle 1 high. Gap = c1 high .. c3 low.
  - Bearish FVG: candle 3 high < candle 1 low. Gap = c3 high .. c1 low.
  - Gap must be >= MIN_GAP (default 1 tick = 0.25; variant 1.00 pt). Candles must be consecutive bars.
  - Filled = price later trades through the whole gap (bull: a low <= c1 high; bear: a high >= c1 low).
  - IFVG = an FVG that a later bar CLOSES fully through (bull FVG: close < gap bottom; bear: close > gap
    top). It flips role: a bearish FVG closed above becomes bullish support (bull IFVG) and vice versa.
    It stays active until a close back through its far side, or AGE bars.
  - An FVG or IFVG is only known once its last bar has closed (no look-ahead), except tag a_out.

Tags per signal and view (R = view resolution, N = 10 bars):
  a_in   FVG in the trade's direction whose candle 3 closed within the N bars before the entry.
  a_out  FVG in the trade's direction formed in the first N bars after the entry. HINDSIGHT: it needs
         price to move the right way, so it is a label, never a filter.
  b      entry inside or at (0.25 pt) an unfilled FVG in the trade's direction formed in the last AGE bars.
  c      an active IFVG in the trade's direction within 1.5 pts of the entry.
  any    a_in or b or c (all knowable at entry). none = not any.
  conf   variant entry: wait for the first FVG in the trade's direction that completes in the N bars
         after the signal and enter at the close of its candle 3 (tradable confirmation).

Scoring (Tim's way): NY 10:00-16:00 by entry time, fixed 4 pt (and 3.5 pt) stop from entry, 8 pt target,
1 ES, $5 round trip, 120 min timeout; ambiguous coarse bars counted as the stop (conservative, same as
the day simulation in indicator_analysis.py). Plus "2 max a day" inside each group, and the signal's own
exits (CRT Pro, VMap, BUY/SELL logged results) for reference.
Usage: python3 fvg_tag.py   (uses data/es_bars_*.csv.gz and the sheet exports in data/)
"""
import os, sys, csv, bisect, datetime as dt
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicator_analysis as ia

N_BARS, AGE, NEAR_IFVG, AT_TOL = 10, {1: 240, 2: 150, 5: 96}, 1.5, 0.25
GAPS = (0.25, 1.0)
VIEWS = (1, 2, 5)
TIM = ia.TIM
TAG = '2026-11-18'
# brackets: Tim's rule (4/8, 3.5/8) and the 6 pt stop TEST (Tim, 11/18: "Test with a 6 point stop"), not his rule
BRK = (('b48', 4, 8), ('b358', 3.5, 8), ('b68', 6, 8), ('b612', 6, 12))
MIN = dt.timedelta(minutes=1)

# ---------------------------------------------------------------- FVG detection
def build_fvgs(r, min_gap):
    """All FVGs at resolution r. Each: dict(dir, bot, top, k3, known, fill, inv, inv_end)."""
    b = ia.BARS[r]; ks = sorted(b); out = []
    step = dt.timedelta(minutes=r)
    for i in range(2, len(ks)):
        k1, k2, k3 = ks[i-2], ks[i-1], ks[i]
        if k3 - k1 != 2*step: continue
        h1, l1 = b[k1][1], b[k1][2]; h3, l3 = b[k3][1], b[k3][2]
        if l3 - h1 >= min_gap - 1e-9: out.append(dict(dir='LONG', bot=h1, top=l3, i=i, k3=k3))
        elif l1 - h3 >= min_gap - 1e-9: out.append(dict(dir='SHORT', bot=h3, top=l1, i=i, k3=k3))
    for f in out:
        f['known'] = f['k3'] + step                    # usable from this minute on
        f['fill'] = f['inv'] = f['inv_end'] = None
        for j in range(f['i']+1, min(len(ks), f['i']+1+3*max(AGE.values()))):
            k = ks[j]; o, h, l, c = b[k]; done = k + step
            if f['inv'] is None:
                if f['dir'] == 'LONG':
                    if f['fill'] is None and l <= f['bot']: f['fill'] = done
                    if c < f['bot']: f['inv'] = done
                else:
                    if f['fill'] is None and h >= f['top']: f['fill'] = done
                    if c > f['top']: f['inv'] = done
            else:   # inverted: IFVG runs the other way until a close back through its far side
                if (f['dir'] == 'LONG' and c > f['top']) or (f['dir'] == 'SHORT' and c < f['bot']):
                    f['inv_end'] = done; break
            if f['inv'] is None and j - f['i'] > AGE[r]: break
    return out

class Index:
    def __init__(self, fvgs):
        self.f = sorted(fvgs, key=lambda x: x['known']); self.kn = [x['known'] for x in self.f]
    def known_between(self, t0, t1):
        """FVGs that became known in (t0, t1]."""
        i = bisect.bisect_right(self.kn, t0); j = bisect.bisect_right(self.kn, t1)
        return self.f[i:j]

def tag(x, side, start, entry, r, idx):
    """Tags for one signal on view r. start = first live minute; entry = price at start."""
    step = dt.timedelta(minutes=r)
    out = dict(a_in=False, a_out=False, b=False, c=False, conf=None)
    if entry is None or start is None: return None
    # needs bars of this view around the entry
    base = start - dt.timedelta(minutes=start.minute % r)
    if not any((base - m*step) in ia.BARS[r] for m in range(1, 4)): return None
    win_in = idx.known_between(start - N_BARS*step - MIN, start)            # candle 3 closed in last N bars
    out['a_in'] = any(f['dir'] == side for f in win_in)
    for f in idx.known_between(start - AGE[r]*step, start):
        if f['dir'] == side:
            unfilled = f['fill'] is None or f['fill'] > start
            if unfilled and f['bot'] - AT_TOL <= entry <= f['top'] + AT_TOL: out['b'] = True
    # IFVG in trade direction: a FVG of the OTHER direction that was inverted before entry, still active
    for f in idx.known_between(start - 3*AGE[r]*step, start):
        if f['dir'] == side or f['inv'] is None or f['inv'] > start: continue
        if f['inv_end'] is not None and f['inv_end'] <= start: continue
        d = 0.0 if f['bot'] <= entry <= f['top'] else min(abs(entry - f['bot']), abs(entry - f['top']))
        if d <= NEAR_IFVG + 1e-9: out['c'] = True
    post = [f for f in idx.known_between(start, start + N_BARS*step) if f['dir'] == side]
    out['a_out'] = bool(post)
    if post:
        f = post[0]; out['conf'] = (ia.BARS[r][f['k3']][3], f['known'])
    out['any'] = out['a_in'] or out['b'] or out['c']
    return out

# ---------------------------------------------------------------- load signals (same as indicator_analysis.main)
def load():
    ia.load_cache()
    pro, _ = ia.load_tracker('crt_pro_trades.csv')
    vm, _ = ia.load_tracker('crt_pro_vmap.csv')
    sig = ia.load_forward()
    for t in pro: t['src'] = 'crtpro'
    for t in vm: t['src'] = 'vmap'
    for t in pro + vm:
        t['st0'] = t['time']; t['pts_own'] = t['pnl']
    RES_R = {'STOPPED': -1, 'STOPPED (BE)': 0, 'TP1 HIT': 1, 'TP2 HIT': 2, 'TP3 HIT': 3, 'STOPPED (TRAIL)': 1}
    bs = [s for s in sig if s['typ'] in ('BUY', 'SELL')]
    for s in bs:
        s['src'] = 'fwd_bs'; s['side'] = 'LONG' if s['typ'] == 'BUY' else 'SHORT'
        s['risk'] = abs(s['entry'] - s['sl']); s['R'] = RES_R.get(s['res'])
        s['pts_own'] = s['R']*s['risk'] if s['R'] is not None else None; s['st0'] = s['time']
    divs = [s for s in sig if s['typ'] in ('Bull Div', 'Bear Div')]
    for s in divs:
        s['src'] = 'fwd_div'; s['side'] = 'LONG' if s['typ'] == 'Bull Div' else 'SHORT'
        s['lt'] = s['time'] + dt.timedelta(minutes=5)
        s['entry'], s['st0'] = ia.live_entry(s['lt'] + MIN); s['R'] = None
    crt = [s for s in sig if s['typ'].startswith('CRT')]
    for s in crt:
        s['src'] = 'fwd_crt'; s['side'] = 'LONG' if 'Bull' in s['typ'] else 'SHORT'
        s['entry'], s['st0'] = ia.live_entry(s['time']); s['R'] = None
    allx = pro + vm + bs + divs + crt
    for x in allx:
        x['sess'] = ia.session(x['st0']) if x.get('st0') else ia.session(x['time'])
        for k, st, tg in BRK:
            if x.get('st0') and x.get('entry') is not None:
                ia.br(x, k, x['side'], x['entry'], x['st0'], st, tg)
            else: x[k] = None
    return dict(pro=pro, vm=vm, bs=bs, divs=divs, crt=crt)

# ---------------------------------------------------------------- scoring
def grp_stats(xs, key='b48'):
    xs = [x for x in xs if x.get(key)]
    if not xs: return None
    s = ia.stats([x[key][0]/x[key][5] for x in xs], [x[key][0] for x in xs])
    s['amb'] = sum(1 for x in xs if x.get(key + '_amb'))
    return s

def own_stats(xs):
    xs = [x for x in xs if x.get('R') is not None and x.get('pts_own') is not None]
    if not xs: return None
    return ia.stats([x['R'] for x in xs], [x['pts_own'] for x in xs])

def sim2(xs, key='b48'):
    """Tim's day: NY 10-4, one position at a time, max 2 trades a day, $1,000 cap. Returns stats + days."""
    by = defaultdict(list)
    for x in sorted([x for x in xs if x.get(key)], key=lambda x: x['st0']):
        by[x['st0'].date()].append(x)
    took = []; days = {}
    for d, ys in sorted(by.items()):
        free = None; n = 0; pnl = 0.0
        for y in ys:
            if free and y['st0'] < free: continue
            if n >= 2: break
            if pnl - (y[key][5]*ia.PT + ia.COST) < -1000: break
            took.append(y); n += 1; pnl += y[key][0]*ia.PT - ia.COST
            free = y[key][4] + dt.timedelta(minutes=y[key][2])
        days[d] = pnl
    if not took: return None
    s = ia.stats([x[key][0]/x[key][5] for x in took], [x[key][0] for x in took])
    s['days'] = len(days); s['worst_day'] = min(days.values())
    return s

def conf_trades(xs, view, gap):
    """Confirmation-entry variant: new entry at the close of the first in-direction FVG after the signal."""
    out = []
    for x in xs:
        tg = x['tags'].get((view, gap))
        if not tg or not tg['conf']: continue
        px, t0 = tg['conf']
        y = dict(src=x['src'], side=x['side'], entry=px, st0=t0, sess=ia.session(t0))
        if y['sess'] not in TIM: continue
        for k, st, tg in BRK: ia.br(y, k, y['side'], px, t0, st, tg)
        if y.get('b48'): out.append(y)
    return out

def fmt(s, money=True, extra=''):
    if not s: return '| 0 | | | | |'
    th = ' (thin)' if s['n'] < 20 else ''
    return (f"| {s['n']}{th} | {s['win']:.0f}% | {s['tot']:+.1f}R ({s['avg']:+.2f}) | ${s['net']:,.0f} |{extra}")

def se(n): return 1.45 / n**0.5 if n else 0

def main():
    S = load()
    IND = [('CRT Pro, all', S['pro']), ('CRT Pro longs', [x for x in S['pro'] if x['side'] == 'LONG']),
           ('CRT Pro shorts', [x for x in S['pro'] if x['side'] == 'SHORT']),
           ('Div label, all', S['divs']), ('Div Bull', [x for x in S['divs'] if x['side'] == 'LONG']),
           ('Div Bear', [x for x in S['divs'] if x['side'] == 'SHORT']),
           ('Fwd BUY/SELL', S['bs']), ('CRT tag', S['crt']), ('VMap', S['vm'])]
    allx = S['pro'] + S['vm'] + S['bs'] + S['divs'] + S['crt']
    for x in allx: x['tags'] = {}
    counts = {}
    for r in VIEWS:
        for g in GAPS:
            fv = build_fvgs(r, g); idx = Index(fv); counts[(r, g)] = len(fv)
            for x in allx:
                x['tags'][(r, g)] = tag(x, x['side'], x.get('st0'), x.get('entry'), r, idx)

    md = [f'<!-- generated by fvg_tag.py; FVG counts ' + ', '.join(f'{r}m gap>={g}: {n}' for (r, g), n in counts.items()) + ' -->',
          '# FVG / IFVG tag tables, 11/18/2026\n',
          'NY 10:00-16:00 by entry time. Bracket = fixed stop from entry, 8 pt target, 1 ES, $5 round trip, ambiguous '
          'coarse bars counted as the stop. R in stop units (4, 3.5 or 6 pts). 6 pt stop = TEST only, not Tim\'s rule. "(thin)" = n < 20. 1 standard error on a group of n is '
          'about 1.45R/sqrt(n) a trade (n=20: 0.32R, n=80: 0.16R).\n']
    GROUPS = [('a_in: FVG formed in the last 10 bars', lambda t: t['a_in']),
              ('b: entry in/at an unfilled FVG', lambda t: t['b']),
              ('c: IFVG within 1.5 pts', lambda t: t['c']),
              ('any (a_in or b or c)', lambda t: t['any']),
              ('d: none', lambda t: not t['any']),
              ('a_out: FVG in first 10 bars after entry (HINDSIGHT)', lambda t: t['a_out']),
              ('no FVG after entry (HINDSIGHT)', lambda t: not t['a_out'])]
    summary = {}
    for g in GAPS:
        for r in VIEWS:
            md.append(f'\n## {r}m chart, minimum gap {g:g} pt\n')
            for name, xs in IND:
                ny = [x for x in xs if x['sess'] in TIM and x['tags'].get((r, g)) is not None and x.get('b48')]
                if not ny: continue
                base = grp_stats(ny); bs2 = sim2(ny)
                md.append(f'\n**{name}** (NY 10-4 signals with {r}m bars: {len(ny)}; all of them at 4/8: '
                          f"{base['tot']:+.1f}R, ${base['net']:,.0f}; 2 max a day: "
                          + (f"{bs2['n']} trades {bs2['tot']:+.1f}R ${bs2['net']:,.0f}" if bs2 else 'none') + ')\n')
                md.append('| Tag group | n | 4/8: win, R, $ | 3.5/8: R, $ | 6/8 TEST: win, R, $ | 6/12 TEST: win, R, $ | 2 max/day 4/8 | 2 max/day 6/8 | 2 max/day 6/12 | Own exits: n, R, $ | 4-pt losers that win at 6/8 |')
                md.append('|---|---|---|---|---|---|---|---|---|---|---|')
                def cell(s_, win=True):
                    if not s_: return ''
                    return (f"{s_['win']:.0f}%, " if win else '') + f"{s_['tot']:+.1f}R, ${s_['net']:,.0f}"
                def simc(s_): return f"{s_['n']}, {s_['tot']:+.1f}R, ${s_['net']:,.0f}" if s_ else ''
                for gl, fn in GROUPS + [('conf: enter at close of first FVG after the signal', None)]:
                    if fn is None:
                        sub = conf_trades(xs, r, g)
                    else:
                        sub = [x for x in ny if fn(x['tags'][(r, g)])]
                    st = {k: grp_stats(sub, k) for k, _, _ in BRK}
                    sm = {k: sim2(sub, k) for k in ('b48', 'b68', 'b612')}
                    ow = own_stats(sub) if fn else None
                    s = st['b48']
                    summary[(g, r, name, gl)] = (st, sm, ow)
                    if not s:
                        md.append(f'| {gl} | 0 | | | | | | | | | |'); continue
                    flip = sum(1 for x in sub if x.get('b48') and x.get('b68') and x['b48'][1] == 'L' and x['b68'][1] == 'W')
                    los = sum(1 for x in sub if x.get('b48') and x['b48'][1] == 'L')
                    th = ' (thin)' if s['n'] < 20 else ''
                    md.append(f"| {gl} | {s['n']}{th} | {cell(s)} | {cell(st['b358'], False)} | {cell(st['b68'])} | {cell(st['b612'])} | "
                              f"{simc(sm['b48'])} | {simc(sm['b68'])} | {simc(sm['b612'])} | "
                              + (f"{ow['n']}, {ow['tot']:+.1f}R, ${ow['net']:,.0f}" if ow else 'n/a') + f" | {flip} of {los} |")
    # tag frequency
    md.append('\n## How often each tag fires (NY 10-4 signals, share of signals with bars)\n')
    md.append('| Indicator | View | Gap | n | a_in | b | c | any | a_out |\n|---|---|---|---|---|---|---|---|---|')
    for name, xs in IND:
        for r in VIEWS:
            for g in GAPS:
                ts = [x['tags'][(r, g)] for x in xs if x['sess'] in TIM and x['tags'].get((r, g)) and x.get('b48')]
                if not ts: continue
                p = lambda k: f"{100*sum(1 for t in ts if t[k])/len(ts):.0f}%"
                md.append(f'| {name} | {r}m | {g:g} | {len(ts)} | {p("a_in")} | {p("b")} | {p("c")} | {p("any")} | {p("a_out")} |')
    os.makedirs(ia.OUT, exist_ok=True)
    fn = os.path.join(ia.OUT, f'fvg-ifvg-tables-{TAG}.md')
    open(fn, 'w').write('\n'.join(md) + '\n')
    with open(os.path.join(ia.DATA, f'fvg_tags_{TAG}.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        cols = [f'{k}_{r}m_{g:g}' for r in VIEWS for g in GAPS for k in ('a_in', 'b', 'c', 'a_out')]
        w.writerow(['source', 'id', 'entry_time_et', 'session', 'side', 'entry', 'b48_pts', 'b48_out', 'R_own'] + cols)
        for x in allx:
            b = x.get('b48'); row = []
            for r in VIEWS:
                for g in GAPS:
                    t = x['tags'].get((r, g))
                    row += ([int(t[k]) for k in ('a_in', 'b', 'c', 'a_out')] if t else ['', '', '', ''])
            w.writerow([x['src'], x.get('id', x.get('n')), x['st0'].isoformat(timespec='minutes') if x.get('st0') else '',
                        x['sess'], x['side'], x.get('entry'), b[0] if b else '', b[1] if b else '', x.get('R')] + row)
    print(fn)
    return summary

if __name__ == '__main__':
    main()
