#!/usr/bin/env python3
"""Indicator comparison, 10/22/2026.

Scores every indicator with logged data on the same terms:
  - CRT Pro ES (CRT Trade Tracker, tab "CRT Pro Trades"), Tim's primary
  - CRT Pro VMap (TEST) (tab "CRT Pro VMap")
  - CRT + Divergence (CRT Forward Test Log): BUY/SELL trades, Div signals, CRT tags
  - CRT Setups (CRT Setups Tracker): no trades logged, reported as a gap

Inputs (read-only exports of the sheets, made with the Sheets connector):
  data/crt_pro_trades.csv, data/crt_pro_vmap.csv, data/forward_test_log.csv
1-minute ES bars: Yahoo ES=F JSON files in a folder passed as argv[1]
(not committed; Yahoo keeps about 30 days of 1m bars).

Rules used everywhere:
  - Times in ET. Forward Test Log times are Central, so +1 hour.
  - Sessions (ET): Asia 18:00-03:00, London 03:00-09:30, NY open 09:30-10:00,
    NY 10-12 (Tim's learning window), NY PM 12:00-16:00, After hours 16:00-18:00.
  - Tim's rule ("4/4"): 4 pt stop, 4 pt target from the indicator's entry, a bar touching
    both counts as the stop, timeout after 60 one-minute bars at that bar's close.
  - R: actual = the indicator's own R; 4/4 R is in 4 pt units.
  - $ at 2 ES = points x $100, minus $10 round trip per trade (net). Gross also kept.
  - Alternative exits replayed on bars from the bar after entry: (b) stop to BE after TP1,
    (c) half off at TP1 + rest with BE stop, (d) full exit at TP1. EMA/REVERSE exits still
    close at their logged time and price.
"""
import csv, json, glob, os, sys, datetime as dt
from collections import defaultdict, Counter
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
ET = ZoneInfo('America/New_York')
COST = 10.0          # $ per round trip, 2 ES
PT = 100.0           # $ per point, 2 ES

# ---------------------------------------------------------------- bars
def load_bars(folder):
    bars = {}
    for f in sorted(glob.glob(os.path.join(folder, '*.json'))):
        d = json.load(open(f))['chart']['result']
        if not d: continue
        d = d[0]; ts = d.get('timestamp') or []
        q = d['indicators']['quote'][0]
        for i, t in enumerate(ts):
            o, h, l, c = q['open'][i], q['high'][i], q['low'][i], q['close'][i]
            if None in (o, h, l, c): continue
            k = dt.datetime.fromtimestamp(t, ET).replace(tzinfo=None, second=0)
            bars[k] = (o, h, l, c)
    return bars

BARS = {}
def path(start, minutes):
    """Bars from start (inclusive) for `minutes` calendar minutes; skips missing minutes."""
    out = []
    for m in range(minutes):
        k = start + dt.timedelta(minutes=m)
        if k in BARS: out.append((k, BARS[k]))
    return out

def first_bar(t):
    return min((k for k in BARS if k >= t), default=None)

# ---------------------------------------------------------------- helpers
def session(t):
    m = t.hour * 60 + t.minute
    if m >= 18*60 or m < 3*60: return 'Asia'
    if m < 9*60+30: return 'London'
    if m < 10*60: return 'NY open 9:30-10'
    if m < 12*60: return 'NY 10-12'
    if m < 16*60: return 'NY PM 12-4'
    return 'After hours'

def bracket(side, entry, start, stop_pts=4.0, tgt_pts=4.0, minutes=60):
    """Fixed stop/target from entry. Returns (pts, outcome) or None if no bars."""
    p = path(start, minutes)
    if not p: return None
    sgn = 1 if side == 'LONG' else -1
    sl = entry - sgn*stop_pts; tp = entry + sgn*tgt_pts
    for k, (o, h, l, c) in p:
        if k.hour == 17 and k.minute == 0: return (sgn*(o-entry), 'T')
        hit_sl = l <= sl if sgn > 0 else h >= sl
        hit_tp = h >= tp if sgn > 0 else l <= tp
        if hit_sl: return (-stop_pts, 'L')
        if hit_tp: return (tgt_pts, 'W')
    c = p[-1][1][3]
    return (sgn*(c-entry), 'T')

def excursion(side, entry, start, minutes=60, work=4.0):
    """Max adverse excursion (pts) before price moves `work` pts in favor; None if never."""
    p = path(start, minutes)
    if not p: return None
    sgn = 1 if side == 'LONG' else -1
    mae = 0.0
    for k, (o, h, l, c) in p:
        adv = (entry - l) if sgn > 0 else (h - entry)
        fav = (h - entry) if sgn > 0 else (entry - l)
        mae = max(mae, adv)
        if fav >= work: return ('worked', mae)
    return ('never', mae)

def replay_rules(side, entry, sl, tp1, tp3, start, end, end_reason, end_px):
    """Replays b/c/d exit rules. Returns dict of R per rule, or None without bars."""
    risk = abs(entry - sl)
    if risk <= 0: return None
    sgn = 1 if side == 'LONG' else -1
    minutes = int((end - start).total_seconds() // 60) + 1
    if minutes < 1: minutes = 1
    p = path(start, max(minutes, 1))
    if not p: return None
    def run(rule):
        stop = sl; got1 = False
        for k, (o, h, l, c) in p:
            if k > end: break
            hit_sl = l <= stop if sgn > 0 else h >= stop
            if hit_sl:
                r = sgn*(stop-entry)/risk
                return (0.5 + 0.5*r) if (rule == 'c' and got1) else r
            hit1 = h >= tp1 if sgn > 0 else l <= tp1
            hit3 = h >= tp3 if sgn > 0 else l <= tp3
            if hit1 and not got1:
                got1 = True
                if rule == 'd': return sgn*(tp1-entry)/risk
            if hit3:
                r3 = sgn*(tp3-entry)/risk
                return (0.5*sgn*(tp1-entry)/risk + 0.5*r3) if rule == 'c' else r3
            if got1 and rule in ('b', 'c'): stop = entry   # BE from the next bar
        r = sgn*(end_px-entry)/risk
        return (0.5*sgn*(tp1-entry)/risk + 0.5*r) if (rule == 'c' and got1) else r
    return {x: run(x) for x in 'bcd'}

def stats(rs, pts=None, label=''):
    """rs: list of R. pts: list of points for $ (same order)."""
    n = len(rs)
    if n == 0: return dict(n=0)
    w = sum(1 for r in rs if r > 1e-9); l = sum(1 for r in rs if r < -1e-9)
    cum = peak = dd = 0.0
    for r in rs:
        cum += r; peak = max(peak, cum); dd = max(dd, peak-cum)
    bw = bl = cw = cl = 0
    for r in rs:
        if r > 1e-9: cw += 1; cl = 0
        elif r < -1e-9: cl += 1; cw = 0
        else: cw = cl = 0
        bw = max(bw, cw); bl = max(bl, cl)
    out = dict(n=n, w=w, l=l, be=n-w-l, win=100.0*w/n, tot=sum(rs), avg=sum(rs)/n, dd=dd,
               best=bw, worst=bl)
    if pts is not None:
        gross = sum(pts)*PT; net = gross - COST*n
        cum = peak = ddd = 0.0
        for p_ in pts:
            cum += p_*PT - COST; peak = max(peak, cum); ddd = max(ddd, peak-cum)
        out.update(gross=gross, net=net, exp=net/n, dd_usd=ddd, pts=sum(pts))
    return out

def fmt(s, money=True):
    if not s or s['n'] == 0: return '| 0 | | | | | | | |'
    m = f" ${s['net']:,.0f} | ${s['exp']:,.0f} |" if money and 'net' in s else ' | |'
    return (f"| {s['n']} | {s['w']}/{s['be']}/{s['l']} | {s['win']:.1f}% | {s['avg']:+.3f}R | "
            f"{s['tot']:+.2f}R |{m} {s['dd']:.1f}R | {s['best']} / {s['worst']} |")

HDR = '| Group | n | W/BE/L | Win % | Avg R | Total R | $ 2 ES net | Exp $/trade | Max DD | Best/worst streak |\n|---|---|---|---|---|---|---|---|---|---|'

def table(title, groups, money=True):
    lines = [f'\n**{title}**\n', HDR]
    for name, rs, pts in groups:
        lines.append(f'| {name} ' + fmt(stats(rs, pts if money else None), money))
    return '\n'.join(lines)

def f2(x):
    try: return float(str(x).replace(',', '').replace('$', ''))
    except: return None

def tparse(d, t):
    h, m = t.strip().split(':')
    return dt.datetime.strptime(d.strip(), '%Y-%m-%d').replace(hour=int(h), minute=int(m))

# ---------------------------------------------------------------- CRT Pro style trackers
def load_tracker(fn):
    rows = list(csv.reader(open(os.path.join(DATA, fn))))
    hdr = rows[0]; ix = {h: i for i, h in enumerate(hdr)}
    out = []
    for r in rows[1:]:
        r = r + ['']*(len(hdr)-len(r))
        if not r[0].strip(): continue
        d = dict(id=r[0], date=r[ix['Date']], t=r[ix['Entry Time (ET)']], side=r[ix['Side']],
                 entry=f2(r[ix['Entry']]), sl=f2(r[ix['SL']]), tp1=f2(r[ix['TP1']]),
                 tp2=f2(r[ix['TP2']]), tp3=f2(r[ix['TP3']]), risk=f2(r[ix['Risk (pts)']]),
                 tpr=int(f2(r[ix['TP Reached']]) or 0), xt=r[ix['Exit Time (ET)']],
                 xp=f2(r[ix['Exit']]), reason=r[ix['Exit Reason']], pnl=f2(r[ix['P&L (pts)']]),
                 R=f2(r[ix['R']]), result=r[ix['Result']])
        if 'Setup' in ix: d['setup'] = r[ix['Setup']]
        d['time'] = tparse(d['date'], d['t'])
        if d['xt']:
            x = tparse(d['date'], d['xt'])
            if x < d['time']: x += dt.timedelta(days=1)
            d['xtime'] = x
        out.append(d)
    return out

def analyze_tracker(name, trades, md, summary):
    closed = [t for t in trades if t['result'] in ('Win', 'Loss', 'Breakeven') and t['R'] is not None]
    opened = [t for t in trades if t not in closed]
    for t in closed:
        t['sess'] = session(t['time'])
        b = bracket(t['side'], t['entry'], t['time'] + dt.timedelta(minutes=1))
        t['b44'] = b
        t['alt'] = replay_rules(t['side'], t['entry'], t['sl'], t['tp1'], t['tp3'],
                                t['time'] + dt.timedelta(minutes=1), t['xtime'],
                                t['reason'], t['xp'])
    md.append(f'\n## {name}\n')
    days = sorted(set(t['date'] for t in closed))
    md.append(f"Closed trades: {len(closed)} ({days[0]} to {days[-1]}, {len(days)} dates); "
              f"open/blank: {len(opened)}. Trades per date: "
              + ', '.join(f"{d[5:]} {sum(1 for t in closed if t['date']==d)}" for d in days) + '.')
    # actual
    A = [(t['R'], t['pnl']) for t in closed]
    md.append(table('Actual (indicator stops and exits)', [('All', [a for a, _ in A], [p for _, p in A])]))
    risks = sorted(t['risk'] for t in closed)
    med = risks[len(risks)//2]
    inrule = sum(1 for r in risks if 3.5 <= r <= 4.0)
    md.append(f"\nStop size: median {med} pts; {sum(1 for r in risks if r < 2)} under 2 pts, "
              f"{inrule} inside 3.5-4, {sum(1 for r in risks if r > 4)} over 4, "
              f"{sum(1 for r in risks if r > 8)} over 8.")
    # TP hit rates
    n = len(closed)
    tp = [sum(1 for t in closed if t['tpr'] >= k) for k in (1, 2, 3)]
    tpsl = [t for t in closed if t['tpr'] >= 1 and t['reason'] == 'SL']
    md.append(f"\nTP hit rates: TP1 {tp[0]}/{n} ({100*tp[0]/n:.0f}%), TP2 {tp[1]} ({100*tp[1]/n:.0f}%), "
              f"TP3 {tp[2]} ({100*tp[2]/n:.0f}%). TP-then-full-SL rows: {len(tpsl)}. "
              f"Exit reasons: " + ', '.join(f'{k} {v}' for k, v in Counter(t['reason'] for t in closed).most_common()) + '.')
    # alternative exits
    rep = [t for t in closed if t['alt']]
    lines = ['\n**Exit rules re-scored on 1m bars** '
             f'({len(rep)} of {n} trades had bars)\n',
             '| Rule | Win % | Total R | Avg R | Max DD | Best/worst streak |', '|---|---|---|---|---|---|']
    rules = [('(a) Actual', [t['R'] for t in rep])]
    for k, lab in (('b', '(b) BE after TP1'), ('c', '(c) Half at TP1 + BE'), ('d', '(d) Full exit at TP1')):
        rules.append((lab, [t['alt'][k] for t in rep]))
    for lab, rs in rules:
        s = stats(rs)
        lines.append(f"| {lab} | {s['win']:.1f}% | {s['tot']:+.2f}R | {s['avg']:+.3f}R | {s['dd']:.1f}R | {s['best']} / {s['worst']} |")
    # TP-then-SL rows only
    tr = [t for t in tpsl if t['alt']]
    if tr:
        lines.append(f"\nThe {len(tr)} TP-then-full-SL rows alone: actual {sum(t['R'] for t in tr):+.1f}R, "
                     f"BE after TP1 {sum(t['alt']['b'] for t in tr):+.1f}R, half at TP1 "
                     f"{sum(t['alt']['c'] for t in tr):+.1f}R, full at TP1 {sum(t['alt']['d'] for t in tr):+.1f}R.")
    md.append('\n'.join(lines))
    # Tim's rule 4/4
    B = [t for t in closed if t['b44']]
    md.append(table(f"Tim's rule: 4 pt stop / 4 pt target ({len(B)} trades with bars; R in 4 pt units)",
                    [('All', [t['b44'][0]/4 for t in B], [t['b44'][0] for t in B])]))
    # breakdowns
    def grp(key):
        g = defaultdict(list)
        for t in closed: g[key(t)].append(t)
        return g
    order = ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4', 'After hours']
    rows = ['\n**Breakdowns** (actual R / $ 2 ES net; 4/4 win % / $ net)\n',
            '| Group | n | Actual win % | Actual R | Actual $ net | 4/4 n | 4/4 win % | 4/4 $ net | BE after TP1 R |',
            '|---|---|---|---|---|---|---|---|---|']
    def addrow(lab, ts):
        if not ts: return
        s = stats([t['R'] for t in ts], [t['pnl'] for t in ts])
        bb = [t for t in ts if t['b44']]
        s4 = stats([t['b44'][0]/4 for t in bb], [t['b44'][0] for t in bb]) if bb else None
        be = sum(t['alt']['b'] for t in ts if t['alt'])
        rows.append(f"| {lab} | {s['n']} | {s['win']:.1f}% | {s['tot']:+.2f}R | ${s['net']:,.0f} | "
                    + (f"{s4['n']} | {s4['win']:.1f}% | ${s4['net']:,.0f}" if s4 else ' | | ')
                    + f" | {be:+.2f}R |")
    g = grp(lambda t: t['sess'])
    for k in order: addrow(k, g.get(k, []))
    addrow('**10-12 window**', [t for t in closed if t['sess'] == 'NY 10-12'])
    addrow('Outside 10-12', [t for t in closed if t['sess'] != 'NY 10-12'])
    addrow('NY only (9:30-16:00)', [t for t in closed if t['sess'].startswith('NY')])
    addrow('Long', [t for t in closed if t['side'] == 'LONG'])
    addrow('Short', [t for t in closed if t['side'] == 'SHORT'])
    addrow('Long, 10-12', [t for t in closed if t['side'] == 'LONG' and t['sess'] == 'NY 10-12'])
    addrow('Short, 10-12', [t for t in closed if t['side'] == 'SHORT' and t['sess'] == 'NY 10-12'])
    if 'setup' in closed[0]:
        for s_ in sorted(set(t['setup'] for t in closed)):
            addrow(f'Setup {s_}', [t for t in closed if t['setup'] == s_])
    else:
        addrow('Stop < 2 pts', [t for t in closed if t['risk'] < 2])
        addrow('Stop 2-4 pts', [t for t in closed if 2 <= t['risk'] <= 4])
        addrow('Stop > 4 pts', [t for t in closed if t['risk'] > 4])
    # by week
    wk = defaultdict(list)
    for t in closed:
        d = dt.date.fromisoformat(t['date']); wk[(d - dt.timedelta(days=d.weekday())).isoformat()].append(t)
    for k in sorted(wk): addrow(f'Week of {k[5:]}', wk[k])
    md.append('\n'.join(rows))
    s = stats([t['R'] for t in closed], [t['pnl'] for t in closed])
    s4 = stats([t['b44'][0]/4 for t in B], [t['b44'][0] for t in B])
    ny = [t for t in closed if t['sess'] == 'NY 10-12']
    s10 = stats([t['R'] for t in ny], [t['pnl'] for t in ny])
    ny4 = [t for t in ny if t['b44']]
    s104 = stats([t['b44'][0]/4 for t in ny4], [t['b44'][0] for t in ny4])
    summary[name] = dict(actual=s, r44=s4, w10=s10, w10_44=s104,
                         be=sum(t['alt']['b'] for t in rep), half=sum(t['alt']['c'] for t in rep),
                         full=sum(t['alt']['d'] for t in rep), tp=tp, n=n)
    return closed

# ---------------------------------------------------------------- forward test log
RES_R = {'STOPPED': -1, 'STOPPED (BE)': 0, 'TP1 HIT': 1, 'TP2 HIT': 2, 'TP3 HIT': 3, 'STOPPED (TRAIL)': 1}

def analyze_forward(md, summary):
    rows = list(csv.reader(open(os.path.join(DATA, 'forward_test_log.csv'))))[1:]
    sig = []
    for r in rows:
        r = r + ['']*(20-len(r))
        if not r[0].strip().isdigit() or not r[2].strip(): continue
        t = tparse(r[1], r[2]) + dt.timedelta(hours=1)    # Central -> ET
        sig.append(dict(n=int(r[0]), date=r[1], time=t, typ=r[4], G=f2(r[6]), H=f2(r[7]),
                        I=f2(r[8]), entry=f2(r[9]), sl=f2(r[10]), tp1=f2(r[11]), tp2=f2(r[12]),
                        tp3=f2(r[13]), res=r[14].strip(), R=f2(r[15]), note=r[17], S=r[18]))
    md.append('\n## CRT + Divergence (CRT Forward Test Log)\n')
    days = sorted(set(s['date'] for s in sig))
    md.append(f"Rows #{sig[0]['n']}-#{sig[-1]['n']} ({len(sig)} signals), dates {days[0]} to {days[-1]} "
              f"(log dates are Central). Types: " + ', '.join(f'{k} {v}' for k, v in Counter(s['typ'] for s in sig).most_common()) + '.')
    nob = [s['n'] for s in sig if s['time'] + dt.timedelta(minutes=1) not in BARS and first_bar(s['time']) is None]
    # ---- BUY/SELL
    tr = [s for s in sig if s['typ'] in ('BUY', 'SELL')]
    closed = [s for s in tr if s['res'] in RES_R]
    blank = [s['n'] for s in tr if s['res'] not in RES_R]
    for s in tr:
        s['side'] = 'LONG' if s['typ'] == 'BUY' else 'SHORT'
        s['sess'] = session(s['time'])
        s['risk'] = abs(s['entry'] - s['sl'])
        s['b44'] = bracket(s['side'], s['entry'], s['time'])
        # hold to SL/TP3 with b/c/d rules, 4 hour cap
        end = s['time'] + dt.timedelta(minutes=240)
        p = path(s['time'], 240)
        s['alt'] = replay_rules(s['side'], s['entry'], s['sl'], s['tp1'], s['tp3'], s['time'],
                                end, 'T', p[-1][1][3]) if p else None
        # same-direction Div pivot within 25 min before
        want = 'Bull Div' if s['side'] == 'LONG' else 'Bear Div'
        s['div'] = any(x['typ'] == want and dt.timedelta(0) <= s['time'] - x['time'] <= dt.timedelta(minutes=25) for x in sig)
    for s in closed: s['Rl'] = RES_R[s['res']]
    risks = sorted(s['risk'] for s in tr)
    md.append(f"\n### BUY/SELL trades\n\n{len(tr)} signals, {len(closed)} with a logged result "
              f"(blank result: #{', #'.join(map(str, blank))}). Logged R: STOPPED -1, BE 0, TP1 HIT or TRAIL +1, TP2 HIT +2 "
              f"(the indicator moves its stop to BE at TP1). Median stop {risks[len(risks)//2]} pts; "
              f"{sum(1 for x in risks if x <= 4)} of {len(risks)} at 4 pts or less.")
    md.append(table('Logged results (indicator stops; R only, stops too wide for a $ figure to mean much)',
                    [('All', [s['Rl'] for s in closed], [s['Rl']*s['risk'] for s in closed]),
                     ('Long', [s['Rl'] for s in closed if s['side']=='LONG'], [s['Rl']*s['risk'] for s in closed if s['side']=='LONG']),
                     ('Short', [s['Rl'] for s in closed if s['side']=='SHORT'], [s['Rl']*s['risk'] for s in closed if s['side']=='SHORT'])]))
    tp = [sum(1 for s in closed if s['res'] in ('TP1 HIT','TP2 HIT','TP3 HIT','STOPPED (BE)','STOPPED (TRAIL)')),
          sum(1 for s in closed if s['res'] in ('TP2 HIT','TP3 HIT')), sum(1 for s in closed if s['res']=='TP3 HIT')]
    md.append(f"\nTP hit rates (from the result column): TP1 {tp[0]}/{len(closed)} ({100*tp[0]/len(closed):.0f}%), "
              f"TP2 {tp[1]} ({100*tp[1]/len(closed):.0f}%), TP3 {tp[2]}.")
    rep = [s for s in tr if s['alt']]
    md.append(f"\n**Exit rules on 1m bars** ({len(rep)} signals with bars, held up to 4 hours to SL or TP3; "
              "this is what the trade does without the indicator replacing it)\n\n| Rule | Win % | Total R | Avg R | Max DD |\n|---|---|---|---|---|")
    for k, lab in (('b','(b) BE after TP1 (close to the indicator)'),('c','(c) Half at TP1 + BE'),('d','(d) Full exit at TP1')):
        st = stats([s['alt'][k] for s in rep])
        md.append(f"| {lab} | {st['win']:.1f}% | {st['tot']:+.2f}R | {st['avg']:+.3f}R | {st['dd']:.1f}R |")
    B = [s for s in tr if s['b44']]
    def g44(lab, xs):
        return (lab, [x['b44'][0]/4 for x in xs], [x['b44'][0] for x in xs])
    order = ['Asia', 'London', 'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4', 'After hours']
    groups = [g44('All', B)] + [g44(o, [s for s in B if s['sess']==o]) for o in order if any(s['sess']==o for s in B)]
    groups += [g44('**10-12 window**', [s for s in B if s['sess']=='NY 10-12']),
               g44('Outside 10-12', [s for s in B if s['sess']!='NY 10-12']),
               g44('NY 9:30-16:00', [s for s in B if s['sess'].startswith('NY')]),
               g44('Long', [s for s in B if s['side']=='LONG']), g44('Short', [s for s in B if s['side']=='SHORT']),
               g44('Div within 25 min before', [s for s in B if s['div']]),
               g44('No Div within 25 min', [s for s in B if not s['div']]),
               g44('Before 10/8', [s for s in B if s['date'] < '2026-10-08']),
               g44('10/8 on (new)', [s for s in B if s['date'] >= '2026-10-08'])]
    md.append(table(f"Tim's rule 4/4 on the BUY/SELL signals ({len(B)} with bars)", groups))
    sB = stats([s['b44'][0]/4 for s in B], [s['b44'][0] for s in B])
    sL = stats([s['Rl'] for s in closed], [s['Rl']*s['risk'] for s in closed])
    w10 = [s for s in B if s['sess']=='NY 10-12']
    summary['CRT + Div BUY/SELL'] = dict(actual=sL, r44=sB, w10_44=stats([s['b44'][0]/4 for s in w10], [s['b44'][0] for s in w10]),
                                        be=sum(s['alt']['b'] for s in rep), half=sum(s['alt']['c'] for s in rep),
                                        full=sum(s['alt']['d'] for s in rep), tp=tp, n=len(closed))
    # ---- Div signals from the label
    divs = [s for s in sig if s['typ'] in ('Bull Div', 'Bear Div')]
    for s in divs:
        s['side'] = 'LONG' if s['typ'] == 'Bull Div' else 'SHORT'
        lab = s['time'] + dt.timedelta(minutes=5)
        s['lt'] = lab
        s['sess'] = session(lab)
        b = BARS.get(lab)
        s['label'] = b[3] if b else None
        s['b44'] = bracket(s['side'], s['label'], lab + dt.timedelta(minutes=1)) if b else None
        s['mae'] = excursion(s['side'], s['label'], lab + dt.timedelta(minutes=1)) if b else None
    D = [s for s in divs if s['b44']]
    groups = [g44('All Div', D), g44('Bull Div', [s for s in D if s['side']=='LONG']), g44('Bear Div', [s for s in D if s['side']=='SHORT'])]
    groups += [g44(o, [s for s in D if s['sess']==o]) for o in order if any(s['sess']==o for s in D)]
    groups += [g44('**10-12 window**', [s for s in D if s['sess']=='NY 10-12']),
               g44('Outside 10-12', [s for s in D if s['sess']!='NY 10-12']),
               g44('NY AM 9:30-12', [s for s in D if s['sess'] in ('NY open 9:30-10','NY 10-12')]),
               g44('Before 10/11', [s for s in D if s['date'] < '2026-10-11']),
               g44('10/11 on (new)', [s for s in D if s['date'] >= '2026-10-11'])]
    md.append(f"\n### Div signals, entered at the label (close of the bar 5 bars after the pivot)\n\n"
              f"{len(divs)} Div rows, {len(D)} with bars.")
    md.append(table("Div from the label, 4/4 (signals, not taken trades)", groups))
    sD = stats([s['b44'][0]/4 for s in D], [s['b44'][0] for s in D])
    w10 = [s for s in D if s['sess']=='NY 10-12']
    am = [s for s in D if s['sess'] in ('NY open 9:30-10','NY 10-12')]
    summary['CRT + Div: Div label'] = dict(r44=sD, w10_44=stats([s['b44'][0]/4 for s in w10], [s['b44'][0] for s in w10]),
                                           am=stats([s['b44'][0]/4 for s in am], [s['b44'][0] for s in am]))
    # Div column H and drawdown from the label
    dh = [s for s in divs if s['H'] is not None]
    zero = sum(1 for s in dh if abs(s['H']-s['G']) < 1e-9)
    md.append(f"\nColumn H on Div rows: {len(dh)} filled (#{min(s['n'] for s in dh)}-#{max(s['n'] for s in dh)}), "
              f"{zero} equal G (0 ticks). Last Div row with H: #{max(s['n'] for s in dh)}; "
              f"{sum(1 for s in divs if s['H'] is None and s['n'] > max(x['n'] for x in dh))} newer Div rows have no H.")
    md.append(mae_table('Div entry drawdown from the label (1m bars, 60 min)', [s for s in divs if s['mae']]))
    # ---- CRT tags
    crt = [s for s in sig if s['typ'].startswith('CRT')]
    for s in crt:
        s['side'] = 'LONG' if 'Bull' in s['typ'] else 'SHORT'
        s['sess'] = session(s['time'])
        b = BARS.get(s['time'] - dt.timedelta(minutes=1))
        s['tag'] = b[3] if b else None
        s['b44'] = bracket(s['side'], s['tag'], s['time']) if b else None
        s['mae'] = excursion(s['side'], s['tag'], s['time']) if b else None
        if b:
            p = path(s['time'], 60)
            sgn = 1 if s['side'] == 'LONG' else -1
            brk = next((k for k, (o,h,l,c) in p if (l < s['G'] if sgn>0 else h > s['G'])), None)
            s['held'] = brk is None
            s['dist'] = abs(s['tag'] - s['G'])
            worst = None
            for k,(o,h,l,c) in p:
                v = l if sgn>0 else h
                worst = v if worst is None else (min(worst, v) if sgn>0 else max(worst, v))
            s['worst60'] = worst
    C = [s for s in crt if s['b44']]
    groups = [g44('All CRT tags', C), g44('CRT Bull', [s for s in C if s['side']=='LONG']), g44('CRT Bear', [s for s in C if s['side']=='SHORT'])]
    groups += [g44(o, [s for s in C if s['sess']==o]) for o in order if any(s['sess']==o for s in C)]
    groups += [g44('**10-12 window**', [s for s in C if s['sess']=='NY 10-12']),
               g44('Outside 10-12', [s for s in C if s['sess']!='NY 10-12']),
               g44('Before 10/11', [s for s in C if s['date'] < '2026-10-11']),
               g44('10/11 on (new)', [s for s in C if s['date'] >= '2026-10-11'])]
    md.append(f"\n### CRT tags (unfiltered), entered at the tag\n\n{len(crt)} CRT rows, {len(C)} with bars. "
              "Entry = close of the bar before the logged time.")
    md.append(table("CRT tag, 4/4", groups))
    held = [s for s in C if 'held' in s]
    dists = sorted(s['dist'] for s in held)
    md.append(f"\nSweep level (G) held for 60 min after the tag: {sum(s['held'] for s in held)}/{len(held)} "
              f"({100*sum(s['held'] for s in held)/len(held):.0f}%). Distance tag to G: median {dists[len(dists)//2]:.2f} pts, "
              f"quartiles {dists[len(dists)//4]:.2f}-{dists[3*len(dists)//4]:.2f}; {sum(1 for d in dists if d<=4)} of {len(dists)} within 4 pts.")
    md.append(mae_table('CRT tag entry drawdown (1m bars, 60 min)', [s for s in crt if s['mae']]))
    ch = [s for s in crt if s['H'] is not None]
    md.append('\nColumn H on CRT rows (Tim\'s 10/11 convention): ' + '; '.join(
        f"#{s['n']} {s['typ'].split(' (')[0]} G {s['G']}, H {s['H']} ({abs(s['H']-s['G'])*4:.0f} ticks from G, "
        f"sweep {'held' if (s['H'] >= s['G'] if s['side']=='LONG' else s['H'] <= s['G']) else 'broke'}; bars worst 60 min "
        f"{s.get('worst60')})" for s in ch) + f". {len(crt)-len(ch)} CRT rows have no H.")
    # stop sizing grid on CRT tags and BUY/SELL
    md.append(stop_grid('Stop size test: CRT tags (target 4 pts, 60 min)', C, 'tag'))
    md.append(stop_grid('Stop size test: BUY/SELL (target 4 pts, 60 min)', B, 'entry'))
    md.append(stop_grid('Stop size test: Div from label (target 4 pts, 60 min)', D, 'label'))
    sC = stats([s['b44'][0]/4 for s in C], [s['b44'][0] for s in C])
    w10 = [s for s in C if s['sess']=='NY 10-12']
    summary['CRT + Div: CRT tag'] = dict(r44=sC, w10_44=stats([s['b44'][0]/4 for s in w10], [s['b44'][0] for s in w10]))
    gaps = dict(nobars=sorted(s['n'] for s in sig if s.get('b44') is None and s['typ'] not in ('BUY','SELL') or (s['typ'] in ('BUY','SELL') and s.get('b44') is None)),
                days=days)
    summary['_fwd_gaps'] = gaps
    return sig

def mae_table(title, xs):
    worked = sorted(s['mae'][1] for s in xs if s['mae'][0] == 'worked')
    never = [s for s in xs if s['mae'][0] == 'never']
    if not worked: return f'\n{title}: no data.'
    q = lambda p: worked[min(len(worked)-1, int(p*len(worked)))]
    lines = [f'\n**{title}**: {len(xs)} signals; {len(worked)} ({100*len(worked)/len(xs):.0f}%) moved 4 pts in favor '
             f'within 60 min. Adverse move before that (pts): median {q(0.5):.2f}, 75th pct {q(0.75):.2f}, '
             f'80th {q(0.8):.2f}, 90th {q(0.9):.2f}, max {worked[-1]:.2f}. '
             f'Share of eventual +4 moves a stop would survive: '
             + ', '.join(f"{st} pts {100*sum(1 for w in worked if w < st)/len(worked):.0f}%" for st in (2, 3, 3.5, 4, 5, 6, 8))]
    return ''.join(lines) + '.'

def stop_grid(title, xs, key):
    lines = [f'\n**{title}**\n', '| Stop | n | Win % | Net pts | $ 2 ES net | Exp $/trade |', '|---|---|---|---|---|---|']
    for st in (2, 3, 3.5, 4, 5, 6, 8):
        res = []
        for s in xs:
            start = s['lt'] + dt.timedelta(minutes=1) if key == 'label' else s['time']
            b = bracket(s['side'], s[key], start, stop_pts=st, tgt_pts=4)
            if b: res.append(b)
        w = sum(1 for p, o in res if o == 'W'); l = sum(1 for p, o in res if o == 'L')
        pts = sum(p for p, o in res); net = pts*PT - COST*len(res)
        lines.append(f'| {st} | {len(res)} | {100*w/max(1,w+l):.1f}% | {pts:+.2f} | ${net:,.0f} | ${net/max(1,len(res)):,.0f} |')
    return '\n'.join(lines)

# ---------------------------------------------------------------- Tim's day + out-of-sample
def tim_day(xs, window, k=2):
    """First k signals per ET date inside `window` (set of sessions), 4/4, one at a time."""
    by = defaultdict(list)
    for x in sorted(xs, key=lambda x: x['et']):
        if x['sess'] in window and x.get('b44'): by[x['et'].date()].append(x)
    took = []
    for d, ys in by.items():
        busy_until = None; n = 0
        for y in ys:
            if n >= k: break
            if busy_until and y['et'] < busy_until: continue
            took.append(y); n += 1
            busy_until = y['et'] + dt.timedelta(minutes=15)
    return took

def supplemental(pro, vm, fwd):
    for t in pro + vm: t['et'] = t['time']
    for s in fwd:
        s['et'] = s.get('lt', s['time'])
    bs = [s for s in fwd if s['typ'] in ('BUY', 'SELL')]
    dv = [s for s in fwd if 'Div' in s['typ']]
    ct = [s for s in fwd if s['typ'].startswith('CRT')]
    NY = {'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4'}
    W = {'NY 10-12'}
    lines = ["\n## Tim's day: first 2 signals per day, 4/4, one at a time\n",
             HDR]
    for name, xs in (('CRT Pro', pro), ('VMap', vm), ('BUY/SELL', bs), ('Div label', dv), ('CRT tag', ct)):
        for wl, w in (('NY 9:30-4', NY), ('10-12', W)):
            took = tim_day(xs, w)
            lines.append(f'| {name}, {wl} ' + fmt(stats([x["b44"][0]/4 for x in took], [x["b44"][0] for x in took])))
    lines.append('\n## Out-of-sample checks (rule picked on the earlier data, tested on the later data)\n')
    lines.append('| Rule | Earlier | Later |\n|---|---|---|')
    def cell(xs, key='b44'):
        if not xs: return 'n=0'
        if key == 'b44':
            st = stats([x['b44'][0]/4 for x in xs if x['b44']], [x['b44'][0] for x in xs if x['b44']])
        else:
            st = stats([x['R'] for x in xs], [x['pnl'] for x in xs])
        return f"n={st['n']}, {st['win']:.0f}% win, {st['tot']:+.1f}R, ${st['net']:,.0f}"
    cut = '2026-10-05'
    for lab, f, key in (
        ('CRT Pro stop >= 2 pts, actual exits', lambda t: t['risk'] >= 2, 'R'),
        ('CRT Pro stop < 2 pts, actual exits', lambda t: t['risk'] < 2, 'R'),
        ('CRT Pro London + 10-12, 4/4', lambda t: t['sess'] in ('London', 'NY 10-12'), 'b44'),
        ('CRT Pro long, 4/4', lambda t: t['side'] == 'LONG', 'b44'),
        ('CRT Pro short, 4/4', lambda t: t['side'] == 'SHORT', 'b44')):
        e = [t for t in pro if t['date'] < cut and f(t)]; l_ = [t for t in pro if t['date'] >= cut and f(t)]
        lines.append(f'| {lab} (9/30-10/2 vs 10/8-10/21) | {cell(e, key)} | {cell(l_, key)} |')
    cut = '2026-10-11'
    for lab, xs, f in (
        ('BUY/SELL with Div within 25 min, 4/4', bs, lambda s: s['div']),
        ('BUY/SELL without Div, 4/4', bs, lambda s: not s['div']),
        ('BUY/SELL in NY, 4/4', bs, lambda s: s['sess'] in NY),
        ('Div NY AM 9:30-12, 4/4', dv, lambda s: s['sess'] in ('NY open 9:30-10', 'NY 10-12')),
        ('Div NY PM 12-4, 4/4', dv, lambda s: s['sess'] == 'NY PM 12-4'),
        ('CRT Bull tag, 4/4', ct, lambda s: s['side'] == 'LONG'),
        ('CRT Bear tag, 4/4', ct, lambda s: s['side'] == 'SHORT')):
        e = [s for s in xs if s['date'] < cut and f(s) and s.get('b44')]
        l_ = [s for s in xs if s['date'] >= cut and f(s) and s.get('b44')]
        lines.append(f'| {lab} (to 10/9 vs 10/11-10/21) | {cell(e)} | {cell(l_)} |')
    return '\n'.join(lines)

# ---------------------------------------------------------------- main
def main():
    global BARS
    BARS = load_bars(sys.argv[1])
    ks = sorted(BARS)
    md = [f"<!-- generated by compare_indicators.py; bars {ks[0]} to {ks[-1]} ET, {len(ks)} 1m bars -->"]
    summary = {}
    pro = analyze_tracker('CRT Pro ES (primary)', load_tracker('crt_pro_trades.csv'), md, summary)
    vm = analyze_tracker('CRT Pro VMap (TEST)', load_tracker('crt_pro_vmap.csv'), md, summary)
    fwd = analyze_forward(md, summary)
    md.append(supplemental(pro, vm, fwd))
    out = os.path.join(HERE, 'out', 'tables-2026-10-22.md')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write('\n'.join(md) + '\n')
    js = {}
    for k, v in summary.items():
        js[k] = v
    json.dump(js, open(os.path.join(HERE, 'out', 'summary-2026-10-22.json'), 'w'), indent=1, default=str)
    print(out)

if __name__ == '__main__':
    main()
