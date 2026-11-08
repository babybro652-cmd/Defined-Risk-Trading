#!/usr/bin/env python3
"""CRT Pro VMap analysis, 11/8/2026 (private; indicator names fine here).

Inputs (read-only exports, data/): crt_pro_vmap.csv (CRT Pro VMap tab), crt_pro_trades.csv
(CRT Pro Trades = the unfiltered CRT Pro signals), forward_test_log.csv (column H check).
Bars: Yahoo ES=F 1m JSON files in a folder (argv[1]); Yahoo keeps 30 days, so bars start
10/9 20:00 ET. Bar-based tests therefore cover 10/12-10/23 only; logged results cover 10/2-10/23.
Output: markdown tables to stdout, charts to out/.
"""
import csv, json, glob, os, sys, datetime as dt, statistics as st
from collections import defaultdict
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data'); OUT = os.path.join(HERE, 'out')
ET = ZoneInfo('America/New_York')
PT, COST = 100.0, 10.0          # 2 ES, $ per point; $ round trip

# ------------------------------------------------------------ bars
BARS = {}
def load_bars(folder):
    for f in sorted(glob.glob(os.path.join(folder, '*.json'))):
        d = json.load(open(f))['chart']['result']
        if not d: continue
        d = d[0]; q = d['indicators']['quote'][0]
        for i, t in enumerate(d.get('timestamp') or []):
            v = (q['open'][i], q['high'][i], q['low'][i], q['close'][i])
            if None in v: continue
            BARS[dt.datetime.fromtimestamp(t, ET).replace(tzinfo=None, second=0)] = v
    ks = sorted(BARS); return ks[0], ks[-1]

def path(start, minutes):
    out = []
    for m in range(minutes):
        k = start + dt.timedelta(minutes=m)
        if k in BARS: out.append((k, BARS[k]))
    return out

def ema_at(t, n=20):
    """EMA20 of 1m closes up to and including bar t (warm-up = all bars before)."""
    ks = [k for k in sorted(BARS) if k <= t]
    if len(ks) < 60: return None
    a = 2/(n+1); e = BARS[ks[0]][3]
    for k in ks[1:]: e = BARS[k][3]*a + e*(1-a)
    return e
_EMA = None
def ema_series():
    global _EMA
    if _EMA is None:
        ks = sorted(BARS); a = 2/21; e = BARS[ks[0]][3]; _EMA = {}
        for i, k in enumerate(ks):
            e = BARS[k][3]*a + e*(1-a) if i else e; _EMA[k] = e if i >= 60 else None
    return _EMA

# ------------------------------------------------------------ load
def tparse(d, t):
    h, m = t.split(':'); return dt.datetime.fromisoformat(d) + dt.timedelta(hours=int(h), minutes=int(m))

def load(fn, prefix):
    rows = []
    for r in csv.reader(open(os.path.join(DATA, fn))):
        if not r or not r[0].startswith(prefix): continue
        if r[19] not in ('Win', 'Loss', 'Breakeven'): continue          # skip OPEN
        entry, sl = float(r[6]), float(r[7])
        rows.append(dict(id=r[0], date=r[1], time=tparse(r[1], r[2]), session=r[3], side=r[4],
                         entry=entry, sl=sl, tp=[float(r[8]), float(r[9]), float(r[10])],
                         risk=float(r[11]), tpr=int(r[12]), reason=r[15], pts=float(r[16]), R=float(r[17]),
                         setup=r[24] if len(r) > 24 else ''))
    return rows

VM = load('crt_pro_vmap.csv', 'VM-'); CP = load('crt_pro_trades.csv', 'CRTPRO-')

def ses(t):
    m = t.hour*60 + t.minute
    if m >= 18*60 or m < 180: return 'Asia'
    if m < 570: return 'London'
    if m < 600: return 'NY open 9:30-10'
    if m < 720: return 'NY 10-12'
    if m < 960: return 'NY PM 12-4'
    return 'After hours'

def stats(rs, pts=None):
    n = len(rs)
    if not n: return None
    w = sum(r > 1e-9 for r in rs); cum = peak = dd = 0.0; cw = cl = bw = bl = 0
    for r in rs:
        cum += r; peak = max(peak, cum); dd = max(dd, peak-cum)
        if r > 1e-9: cw += 1; cl = 0
        elif r < -1e-9: cl += 1; cw = 0
        else: cw = cl = 0
        bw = max(bw, cw); bl = max(bl, cl)
    out = dict(n=n, win=100*w/n, tot=cum, avg=cum/n, dd=dd, bw=bw, bl=bl)
    if pts is not None: out['usd'] = sum(p*PT - COST for p in pts)
    return out

def fmt(s):
    if not s: return '| 0 | | | | | |'
    return f"| {s['n']} | {s['win']:.0f}% | {s['avg']:+.3f} | {s['tot']:+.1f}R | {s['dd']:.1f}R | {s['bl']} |"
H = '| n | Win | Avg R | Total R | Max DD | Worst streak |'
HS = '|---|---|---|---|---|---|'

def tbl(title, groups, key=None):
    print(f'\n**{title}**\n\n| Group {H[1:]}\n|---{HS}')
    for g, rows in groups:
        rs = [x['R'] for x in sorted(rows, key=lambda x: x['time'])]
        print(f'| {g} {fmt(stats(rs))}')

# ------------------------------------------------------------ bar replays
def bracket(side, entry, start, stop, tgt, minutes=60):
    p = path(start, minutes)
    if not p: return None
    sg = 1 if side == 'LONG' else -1
    sl, tp = entry - sg*stop, entry + sg*tgt
    for k, (o, h, l, c) in p:
        if (l <= sl) if sg > 0 else (h >= sl): return -stop, 'L'
        if (h >= tp) if sg > 0 else (l <= tp): return tgt, 'W'
    return sg*(p[-1][1][3]-entry), 'T'

def mae_before(side, entry, start, work, minutes=60):
    """(outcome, max adverse excursion before `work` pts in favor)"""
    p = path(start, minutes)
    if not p: return None
    sg = 1 if side == 'LONG' else -1; mae = 0.0
    for k, (o, h, l, c) in p:
        mae = max(mae, (entry-l) if sg > 0 else (h-entry))
        if ((h-entry) if sg > 0 else (entry-l)) >= work: return 'worked', mae
    return 'never', mae

def vm_sim(t, stop, tgt, minutes=240):
    """VMap trade replayed from the bar after entry with a fixed stop/target; holds up to `minutes`."""
    return bracket(t['side'], t['entry'], t['time'] + dt.timedelta(minutes=1), stop, tgt, minutes)

def main(folder):
    lo, hi = load_bars(folder)
    print(f'<!-- bars {lo} to {hi}, {len(BARS)} -->')
    print(f'VMap closed: {len(VM)}  CRT Pro closed: {len(CP)}')
    OLD = [t for t in VM if t['date'] <= '2026-10-21']; NEW = [t for t in VM if t['date'] >= '2026-10-22']
    # note: the 10/22 comparison used rows to 10/21 + early 10/22; "new" here is after the earlier export
    EX = {t['id'] for t in VM[:116]}
    new = [t for t in VM if t['id'] not in EX]

    print('\n## 1 filtered vs unfiltered')
    for name, rows in [('VMap all (actual)', VM), ('VMap Setup A', [t for t in VM if t['setup'] == 'A']),
                       ('VMap Setup B', [t for t in VM if t['setup'] == 'B']),
                       ('VMap first 116 (10/22 report)', VM[:116]), (f'VMap new ({len(new)})', new),
                       ('CRT Pro unfiltered all', CP),
                       ('CRT Pro 10/2-10/23 (VMap span)', [t for t in CP if t['date'] >= '2026-10-02']),
                       ('CRT Pro new since 10/21 export', CP[702:])]:
        rows = sorted(rows, key=lambda x: x['time'])
        s = stats([x['R'] for x in rows], [x['pts'] for x in rows])
        print(f"| {name} {fmt(s)} ${s['usd']:,.0f} net 2ES |")
    # matched: VMap A vs the CRT Pro signal it came from
    cpk = {(t['time'], t['side']): t for t in CP}
    A = [t for t in VM if t['setup'] == 'A']
    matched = [(t, cpk.get((t['time'], t['side']))) for t in A]
    mk = {id(c) for _, c in matched if c}
    print(f"\nVMap A matched to a CRT Pro row: {sum(1 for _, c in matched if c)}/{len(A)}")
    kept = [c for _, c in matched if c]
    span = [c for c in CP if c['date'] >= '2026-10-02']
    removed = [c for c in span if id(c) not in mk]
    for nm, rows in [('CRT Pro rows VMap kept (own stops)', kept), ('CRT Pro rows VMap filtered out (own stops)', removed)]:
        s = stats([x['R'] for x in sorted(rows, key=lambda x: x['time'])], [x['pts'] for x in rows]); print(nm, fmt(s))
    # same signals, same 4/4 bracket on bars
    for nm, rows in [('kept', kept), ('removed', removed)]:
        rs = []; ps = []
        for c in rows:
            b = bracket(c['side'], c['entry'], c['time'] + dt.timedelta(minutes=1), 4, 4)
            if b: rs.append(b[0]/4); ps.append(b[0])
        s = stats(rs, ps)
        if s: print(f'4/4 on bars, signals VMap {nm}:', fmt(s), f"${s['usd']:,.0f}")

    # by day (consistency)
    print('\n## day by day (VMap actual)')
    byd = defaultdict(list)
    for t in VM: byd[t['date']].append(t['R'])
    for d in sorted(byd): print(d, len(byd[d]), f'{sum(byd[d]):+.0f}R')

    print('\n## 2 time of day (VMap actual)')
    g = defaultdict(list)
    for t in VM: g[ses(t['time'])].append(t)
    tbl('Session', [(k, g[k]) for k in ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4', 'After hours'] if k in g])
    hr = defaultdict(list)
    for t in VM: hr[t['time'].hour].append(t)
    tbl('Hour ET', [(f'{h:02d}:00', hr[h]) for h in sorted(hr)])
    tbl('Tim window', [('10:00-11:59 ET', [t for t in VM if 600 <= t['time'].hour*60+t['time'].minute < 720]),
                       ('10:00-15:59 ET (NY, no pre-10)', [t for t in VM if 600 <= t['time'].hour*60+t['time'].minute < 960]),
                       ('00:00-09:59 ET (Asia/London/open)', [t for t in VM if t['time'].hour*60+t['time'].minute < 600 and not (t['time'].hour*60+t['time'].minute >= 1080)])])
    tbl('10-12 by setup', [(f'10-12 {s}', [t for t in VM if 600 <= t['time'].hour*60+t['time'].minute < 720 and t['setup'] == s]) for s in 'AB'])
    # 10-12 on CRT Pro unfiltered
    tbl('CRT Pro unfiltered by session (actual)', [(k, [t for t in CP if ses(t['time']) == k]) for k in ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4', 'After hours']])
    # first-half / second-half for 10-12
    w10 = w = [t for t in VM if 600 <= t['time'].hour*60+t['time'].minute < 720]
    tbl('10-12 early vs late', [('to 10/15', [t for t in w if t['date'] <= '2026-10-15']), ('10/16 on', [t for t in w if t['date'] >= '2026-10-16'])])

    print('\n## 3 direction and EMA20')
    tbl('Direction', [(s, [t for t in VM if t['side'] == s]) for s in ('LONG', 'SHORT')])
    tbl('Direction x setup', [(f'{s} {u}', [t for t in VM if t['side'] == s and t['setup'] == u]) for s in ('LONG', 'SHORT') for u in 'AB'])
    tbl('Direction in Tim window 10-12', [(s, [t for t in w if t['side'] == s]) for s in ('LONG', 'SHORT')])
    E = ema_series()
    def ema_tag(t):
        e = E.get(t['time'] - dt.timedelta(minutes=0)) or E.get(t['time'])
        if e is None or t['time'] not in BARS and (t['time'] - dt.timedelta(minutes=1)) not in BARS: return None
        e = E.get(t['time']) or E.get(t['time'] - dt.timedelta(minutes=1))
        if e is None: return None
        return 'with' if ((t['entry'] > e) == (t['side'] == 'LONG')) else 'against'
    for nm, rows in [('VMap', VM), ('CRT Pro', CP)]:
        gg = defaultdict(list)
        for t in rows:
            tg = ema_tag(t)
            if tg: gg[tg].append(t)
        tbl(f'{nm}: entry vs 1m EMA20 (bars 10/12-10/23 only)', [(f'{k} trend', gg[k]) for k in ('with', 'against')])
    gg = defaultdict(list)
    for t in VM:
        tg = ema_tag(t)
        if tg: gg[(tg, ses(t['time']) == 'NY 10-12')].append(t)
    tbl('VMap EMA with/against x in 10-12', [(f'{k[0]} / {"10-12" if k[1] else "other"}', v) for k, v in sorted(gg.items())])

    dist = []
    for t in VM:
        e = E.get(t['time']) or E.get(t['time'] - dt.timedelta(minutes=1))
        if e is not None: dist.append((abs(t['entry'] - e), t))
    dist.sort(key=lambda x: x[0]); n3 = len(dist)//3
    tbl('VMap by distance from 1m EMA20 at entry (tertiles; pts)', [(f'{a[0][0]:.1f}-{a[-1][0]:.1f} pts', [x[1] for x in a]) for a in (dist[:n3], dist[n3:2*n3], dist[2*n3:])])
    tbl('CRT Pro actual exit reasons (EMA exit is an exit rule, not the entry filter)', [(r, [t for t in CP if t['reason'] == r]) for r in ('SL', 'TP3', 'EMA', 'REVERSE')])
    print('\n## 4 stop hits')
    sl = [t for t in VM if t['reason'] == 'SL']
    print(f"VMap exits at SL: {len(sl)}/{len(VM)} = {100*len(sl)/len(VM):.0f}% (all at the 4 pt stop; TP reached before SL: {sum(1 for t in sl if t['tpr'] >= 1)})")
    print('SL median minutes held:', st.median([(tparse(t['date'], '0:00') and 0) for t in sl]) if False else '')
    # hold time for SL exits
    rows = list(csv.reader(open(os.path.join(DATA, 'crt_pro_vmap.csv'))))
    hold = []
    for r in rows[1:]:
        if r and r[15] == 'SL':
            a = tparse(r[1], r[2]); b = tparse(r[1], r[13])
            if b < a: b += dt.timedelta(days=1)
            hold.append((b-a).total_seconds()/60)
    hold.sort(); print('SL hold minutes: median', st.median(hold), '| <=3 min:', sum(h <= 3 for h in hold), 'of', len(hold), '| <=5:', sum(h <= 5 for h in hold))
    cr = [t for t in CP]
    sz = [t['risk'] for t in cr]
    print(f"CRT Pro risk size (n={len(sz)}): median {st.median(sz)}, <2 pts {sum(s < 2 for s in sz)}, 3.5-4 pts {sum(3.5 <= s <= 4 for s in sz)}, >4 {sum(s > 4 for s in sz)}")
    # stop grid on bars for VMap, target = tp3 distance (12), 4/4, targets
    cov = [t for t in VM if t['time'] in BARS or (t['time'] + dt.timedelta(minutes=1)) in BARS]
    print(f'VMap trades with bar coverage: {len(cov)} (from {min(t["time"] for t in cov)})')
    print('\nStop grid on bars (target 4 pts fixed, hold up to 60 min; $ at 2 ES net):')
    print('| Stop | n | Win | Total R(4pt) | $ net | stopped out |\n|---|---|---|---|---|---|')
    for stop in (2, 3, 3.5, 4, 5, 6, 8):
        res = [bracket(t['side'], t['entry'], t['time'] + dt.timedelta(minutes=1), stop, 4) for t in cov]
        res = [r for r in res if r]
        pts = [r[0] for r in res]; nw = sum(p > 0 for p in pts)
        print(f"| {stop} | {len(res)} | {100*nw/len(res):.0f}% | {sum(pts)/4:+.1f} | ${sum(p*PT-COST for p in pts):,.0f} | {sum(r[1]=='L' for r in res)} ({100*sum(r[1]=='L' for r in res)/len(res):.0f}%) |")
    # MAE before +4 (VMap and CRT Pro)
    for nm, rows in [('VMap', cov), ('CRT Pro (bars)', [t for t in CP if t['time'] in BARS])]:
        mm = [mae_before(t['side'], t['entry'], t['time'] + dt.timedelta(minutes=1), 4) for t in rows]
        wk = sorted(m[1] for m in mm if m and m[0] == 'worked')
        al = sorted(m[1] for m in mm if m)
        if wk:
            q = lambda a, p: a[min(len(a)-1, int(p*len(a)))]
            print(f"{nm}: {len(wk)}/{len(al)} reach +4 within 60 min; adverse before +4: median {q(wk,.5)}, 80th {q(wk,.8)}, 90th {q(wk,.9)}; survive a 4 pt stop {100*sum(x < 4 for x in wk)/len(wk):.0f}%, 3.5 pt {100*sum(x < 3.5 for x in wk)/len(wk):.0f}%")
    # column H
    fl = list(csv.reader(open(os.path.join(DATA, 'forward_test_log.csv'))))
    hf = [r for r in fl[1:] if len(r) > 8 and r[7].strip()]
    nz = [r for r in hf if r[8] not in ('', '0')]
    print(f"\nForward Test Log col H: {len(hf)} filled of {len(fl)-1}; non-zero drawdown {len(nz)}; last row #{fl[-1][0]} {fl[-1][1]}; last H row #{hf[-1][0]} {hf[-1][1]}")

    print('\n## 5 targets (from TP Reached, VMap, stop = 4 pts)')
    print('| Target | n | Win | Avg win R | Avg R | Total R | $ per trade (2 ES, net) |\n|---|---|---|---|---|---|---|')
    def tgt_rows(rows, k):
        rs = []; pt = []
        for t in rows:
            d = abs(t['tp'][k-1] - t['entry'])
            if t['tpr'] >= k: rs.append(d/t['risk']); pt.append(d)
            else: rs.append(-1.0); pt.append(-t['risk'])
        return rs, pt
    for k in (1, 2, 3):
        rs, pt = tgt_rows(VM, k); s = stats(rs, pt)
        wins = [r for r in rs if r > 0]
        print(f"| TP{k} | {s['n']} | {s['win']:.0f}% | {st.mean(wins):.2f} | {s['avg']:+.3f} | {s['tot']:+.1f}R | ${s['usd']/s['n']:+,.0f} |")
    print('\nBy group (Avg R at TP1 / TP2 / TP3):')
    def grp(nm, rows):
        if not rows: return
        out = []
        for k in (1, 2, 3):
            rs, _ = tgt_rows(rows, k); out.append(f"{st.mean(rs):+.2f}")
        print(f'| {nm} | {len(rows)} | ' + ' | '.join(out) + ' |')
    print('| Group | n | TP1 | TP2 | TP3 |\n|---|---|---|---|---|')
    grp('All', VM)
    for s in 'AB': grp(f'Setup {s}', [t for t in VM if t['setup'] == s])
    for k in ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4']: grp(k, [t for t in VM if ses(t['time']) == k])
    for s in ('LONG', 'SHORT'): grp(s, [t for t in VM if t['side'] == s])
    grp('10-12 LONG', [t for t in w10 if t['side'] == 'LONG']); grp('10-12 SHORT', [t for t in w10 if t['side'] == 'SHORT'])
    print('\nTP1 distance (pts) median/mean:', st.median([abs(t['tp'][0]-t['entry']) for t in VM]), round(st.mean([abs(t['tp'][0]-t['entry']) for t in VM]), 2),
          '| TP3 distance median:', st.median([abs(t['tp'][2]-t['entry']) for t in VM]))
    # TP stepping on logged outcome
    tr = defaultdict(int)
    for t in VM: tr[t['tpr']] += 1
    print('TP reached counts (0/1/2/3):', [tr[i] for i in range(4)], ' TP3 exits:', sum(1 for t in VM if t['reason'] == 'TP3'))
    print('\nAlternative exits on logged TP-then-SL rows:')
    r_actual = sum(t['R'] for t in VM)
    b = sum((0 if (t['tpr'] >= 1 and t['reason'] == 'SL') else t['R']) for t in VM)
    # (b) BE after TP1: TP1-then-SL rows -> 0R
    tp1R = lambda t: abs(t['tp'][0]-t['entry'])/t['risk']
    c = sum((0.5*tp1R(t) if (t['tpr'] >= 1 and t['reason'] == 'SL') else (0.5*tp1R(t)+0.5*t['R'] if t['tpr'] >= 1 else t['R'])) for t in VM)
    d = sum((tp1R(t) if t['tpr'] >= 1 else t['R']) for t in VM)
    print(f'actual {r_actual:+.1f}R | (b) BE after TP1 {b:+.1f}R | (c) half at TP1 + rest BE {c:+.1f}R | (d) full at TP1 {d:+.1f}R (all assume no re-entry; TP1-then-SL rows: {sum(1 for t in VM if t["tpr"]>=1 and t["reason"]=="SL")})')

    # bar replay of exit rules (b)(c)(d) on trades with bars; exit time from the log
    rr = {r[0]: r for r in csv.reader(open(os.path.join(DATA, 'crt_pro_vmap.csv')))}
    tot = {'a': 0, 'b': 0, 'c': 0, 'd': 0}; nrep = 0
    for t in cov:
        r = rr[t['id']]; end = tparse(r[1], r[13])
        if end < t['time']: end += dt.timedelta(days=1)
        p_ = path(t['time'] + dt.timedelta(minutes=1), int((end - t['time']).total_seconds()//60))
        if not p_: continue
        sg = 1 if t['side'] == 'LONG' else -1; risk = t['risk']; t1 = sg*(t['tp'][0]-t['entry'])/risk
        def run(rule):
            stop = t['sl']; got = False
            for k, (o, h, l, c) in p_:
                if (l <= stop) if sg > 0 else (h >= stop):
                    x = sg*(stop-t['entry'])/risk; return 0.5*t1+0.5*x if (rule == 'c' and got) else x
                h1 = (h >= t['tp'][0]) if sg > 0 else (l <= t['tp'][0]); h3 = (h >= t['tp'][2]) if sg > 0 else (l <= t['tp'][2])
                if h1 and not got:
                    got = True
                    if rule == 'd': return t1
                if h3:
                    x = sg*(t['tp'][2]-t['entry'])/risk; return 0.5*t1+0.5*x if rule == 'c' else x
                if got and rule in ('b', 'c'): stop = t['entry']
            x = sg*(p_[-1][1][3]-t['entry'])/risk; return 0.5*t1+0.5*x if (rule == 'c' and got) else x
        tot['a'] += t['R']; nrep += 1
        for ru in 'bcd': tot[ru] += run(ru)
    print(f"Bar-replayed exit rules (n={nrep}, bars 10/12-10/23): actual {tot['a']:+.1f}R | (b) BE after TP1 {tot['b']:+.1f}R | (c) half at TP1 + BE {tot['c']:+.1f}R | (d) full at TP1 {tot['d']:+.1f}R")
    print('\n## 5b bar grid: stop 4, target N pts (VMap, bars 10/12-10/23, hold 4h)')
    print('| Target | n | Win | Total R(4pt) | $ net |\n|---|---|---|---|---|')
    for tg in (2, 3, 4, 6, 8, 12, 16):
        res = [vm_sim(t, 4, tg) for t in cov]; res = [r for r in res if r]
        pts = [r[0] for r in res]
        print(f"| {tg} | {len(res)} | {100*sum(p > 0 for p in pts)/len(res):.0f}% | {sum(pts)/4:+.1f} | ${sum(p*PT-COST for p in pts):,.0f} |")

    # charts
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        os.makedirs(OUT, exist_ok=True)
        fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
        a = sorted(VM, key=lambda x: x['time']); cum = 0; xs = []
        for t in a: cum += t['R']; xs.append(cum)
        ax[0].plot(range(1, len(xs)+1), xs, color='#1f77b4', label='VMap actual')
        cc = sorted([t for t in CP if t['date'] >= '2026-10-02'], key=lambda x: x['time']); cum = 0; ys = []
        for t in cc: cum += t['R']; ys.append(cum)
        ax[0].plot(range(1, len(ys)+1), ys, color='#999999', label='CRT Pro unfiltered (10/2+)')
        ax[0].axvline(116, color='#d62728', ls=':', lw=1); ax[0].text(117, min(xs), '10/22 report', fontsize=8, color='#d62728')
        ax[0].set_title('Cumulative R by trade number'); ax[0].set_xlabel('trade #'); ax[0].set_ylabel('R'); ax[0].legend(fontsize=8)
        ks = ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4']
        vals = [sum(t['R'] for t in VM if ses(t['time']) == k) for k in ks]; ns = [sum(1 for t in VM if ses(t['time']) == k) for k in ks]
        ax[1].bar(range(5), vals, color=['#d62728' if v < 0 else '#2ca02c' for v in vals])
        for i, (v, n) in enumerate(zip(vals, ns)): ax[1].text(i, v, f'n={n}', ha='center', va='bottom' if v >= 0 else 'top', fontsize=8)
        ax[1].set_xticks(range(5)); ax[1].set_xticklabels(['Asia', 'London', '9:30-10', '10-12', '12-4'], fontsize=9); ax[1].set_title('VMap total R by session (actual)')
        avg = []
        for k in (1, 2, 3):
            rs, _ = tgt_rows(VM, k); avg.append(st.mean(rs))
        ax[2].bar(['TP1', 'TP2', 'TP3'], avg, color=['#d62728' if v < 0 else '#2ca02c' for v in avg]); ax[2].axhline(0, color='k', lw=.6)
        ax[2].set_title('VMap avg R per trade by fixed target');
        for i, v in enumerate(avg): ax[2].text(i, v, f'{v:+.2f}', ha='center', va='bottom' if v >= 0 else 'top', fontsize=9)
        plt.tight_layout(); plt.savefig(os.path.join(OUT, 'vmap-analysis-2026-11-08.png'), dpi=110)
    except Exception as e:
        print('chart failed', e)

if __name__ == '__main__':
    main(sys.argv[1])
