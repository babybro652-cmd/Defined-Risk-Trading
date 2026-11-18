#!/usr/bin/env python3
"""Indicator analysis, 11/18/2026 (private; indicator names fine here, never in public copy).

Scores every indicator with logged data, season to date and since the 11/8 report:
  - CRT Pro ES (CRT Trade Tracker, tab "CRT Pro Trades"), Tim's primary
  - CRT Pro VMap (TEST) (same workbook, tab "CRT Pro VMap")
  - CRT + Divergence (CRT Forward Test Log): BUY/SELL trades, Div signals (from the label), CRT tags
  - CRT Setups Tracker: no trades ever logged (reported as a gap, not scored)

Inputs (read-only exports of the sheets via the Sheets connector; no sheet is edited):
  data/crt_pro_trades.csv, data/crt_pro_vmap.csv, data/forward_test_log.csv
Bars: ES=F from Yahoo at 1m (last ~30 days), 2m (~36 days) and 5m (~60 days). Pass folders of the
raw Yahoo JSON with --1m/--2m/--5m; they are merged into data/es_bars_<res>.csv.gz so later runs
keep the history Yahoo drops. Each trade is replayed on the finest bars that cover it.

Conventions (checked on the bars, 11/18):
  - Entry price = close of the bar BEFORE the logged entry minute; the bar labelled with the entry
    minute is the first live bar. An exit logged at minute x happened in bar x-1.
    (compare_indicators.py started one bar late; fixed here.)
  - Forward Test Log times are Central; +1 hour to ET.
  - Sessions (ET): Asia 18:00-3:00, London 3:00-9:30, NY open 9:30-10:00, NY AM 10:00-12:00,
    NY PM 12:00-16:00, After hours 16:00-18:00.
  - $ on 1 ES = points x $50 minus $5 round trip.
  - Exit rules: (a) actual, (b) stop to BE after TP1, (c) half off at TP1 + rest to BE, (d) full
    exit at TP1. Replayed on bars to the logged exit; EMA/REVERSE exits still close at their logged
    time and price. A bar touching both levels counts as the stop (conservative).
  - Tim's bracket: fixed 4 pt (and 3.5 pt) stop from ENTRY, 8 pt target (2R), 1 ES, timeout 120 min
    or 16:59 ET at that bar's close.
"""
import csv, json, glob, gzip, os, sys, argparse, datetime as dt
from collections import defaultdict, Counter
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data'); OUT = os.path.join(HERE, 'out')
ET = ZoneInfo('America/New_York')
PT, COST = 50.0, 5.0                     # 1 ES
RES = (1, 2, 5)
BARS = {r: {} for r in RES}
TAG = '2026-11-18'
AMB_MODE = os.environ.get('AMB', 'stop')   # ambiguous coarse bar: 'stop' (count as a loss) or 'skip'
SINCE = '2026-11-08'                      # last report

# ------------------------------------------------------------------ bars
def cache_fn(r): return os.path.join(DATA, f'es_bars_{r}m.csv.gz')

def load_cache():
    for r in RES:
        fn = cache_fn(r)
        if not os.path.exists(fn): continue
        with gzip.open(fn, 'rt') as f:
            for row in csv.reader(f):
                if row[0] == 'time': continue
                BARS[r][dt.datetime.fromisoformat(row[0])] = tuple(float(x) for x in row[1:5])

def merge_yahoo(folder, r):
    n = 0
    for f in sorted(glob.glob(os.path.join(folder, '*.json'))):
        res = json.load(open(f))['chart']['result']
        if not res: continue
        d = res[0]; q = d['indicators']['quote'][0]
        for i, t in enumerate(d.get('timestamp') or []):
            v = (q['open'][i], q['high'][i], q['low'][i], q['close'][i])
            if None in v: continue
            k = dt.datetime.fromtimestamp(t, ET).replace(tzinfo=None, second=0)
            if k.minute % r: continue                       # partial live bar
            BARS[r][k] = tuple(round(x * 4) / 4 for x in v); n += 1
    return n

def save_cache():
    for r in RES:
        with gzip.open(cache_fn(r), 'wt', newline='') as f:
            w = csv.writer(f); w.writerow(['time', 'open', 'high', 'low', 'close'])
            for k in sorted(BARS[r]): w.writerow([k.isoformat(timespec='minutes'), *BARS[r][k]])

def pick_res(t):
    """Finest resolution with bars around t (within 10 min after)."""
    for r in RES:
        b = BARS[r]
        base = t - dt.timedelta(minutes=t.minute % r)
        if any((base + dt.timedelta(minutes=m)) in b for m in range(0, 10 + r, r)): return r
    return None

def path(start, minutes, r):
    """Bars at resolution r from the bar containing `start` for `minutes` minutes."""
    b = BARS[r]; out = []
    k = start - dt.timedelta(minutes=start.minute % r)
    end = start + dt.timedelta(minutes=minutes)
    while k < end:
        if k in b: out.append((k, b[k]))
        k += dt.timedelta(minutes=r)
    return out

def bar_before(t):
    k = t - dt.timedelta(minutes=1)
    return BARS[1].get(k)

# ------------------------------------------------------------------ helpers
def session(t):
    m = t.hour * 60 + t.minute
    if m >= 18*60 or m < 3*60: return 'Asia'
    if m < 9*60+30: return 'London'
    if m < 10*60: return 'NY open 9:30-10'
    if m < 12*60: return 'NY AM 10-12'
    if m < 16*60: return 'NY PM 12-4'
    return 'After hours'
SESS = ['Asia', 'London', 'NY open 9:30-10', 'NY AM 10-12', 'NY PM 12-4', 'After hours']
TIM = ('NY AM 10-12', 'NY PM 12-4')       # NY only, 10 AM on

def f2(x):
    try: return float(str(x).replace(',', '').replace('$', ''))
    except Exception: return None

def tparse(d, t):
    h, m = t.strip().split(':')
    return dt.datetime.strptime(d.strip(), '%Y-%m-%d').replace(hour=int(h), minute=int(m))

AMB = Counter()
def bracket(side, entry, start, stop, tgt, minutes=120):
    """Fixed stop/target from entry. Returns (pts, 'W'|'L'|'T'|'A', res, both, exit_bar) or None.
    On 1m bars a bar touching both levels counts as the stop. On 2m/5m bars that case, or any hit
    inside a first bar that starts before the entry, is 'A' (ambiguous) and is left out of totals."""
    if entry is None: return None
    r = pick_res(start)
    if r is None: return None
    p = path(start, minutes, r)
    if not p: return None
    sgn = 1 if side == 'LONG' else -1
    sl = entry - sgn*stop; tp = entry + sgn*tgt
    for i, (k, (o, h, l, c)) in enumerate(p):
        if k.hour == 17:
            return (sgn*(o-entry), 'T', r, False, k)
        hs = l <= sl if sgn > 0 else h >= sl
        ht = h >= tp if sgn > 0 else l <= tp
        if r > 1 and (hs or ht) and ((hs and ht) or (i == 0 and k < start)):
            return (0.0, 'A', r, True, k)
        if hs: return (-stop, 'L', r, ht, k)
        if ht: return (tgt, 'W', r, False, k)
    return (sgn*(p[-1][1][3]-entry), 'T', r, False, p[-1][0])

def br(x, key, side, entry, start, stop, tgt):
    """Stores a bracket result on x[key] (with the stop appended), None if ambiguous or no bars."""
    b = bracket(side, entry, start, stop, tgt)
    if b and b[1] == 'A':
        AMB[(x.get('src', ''), key)] += 1; x[key + '_amb'] = True
        x[key] = (-stop, 'L', b[2], True, b[4], stop) if AMB_MODE == 'stop' else None
        return
    x[key] = b + (stop,) if b else None

def live_entry(t_live):
    """Signal confirmed at the close of the bar before t_live. Returns (entry, start).
    1m: close of bar t_live-1, start t_live. Coarse: close of the coarse bar holding minute
    t_live-1, start at the next coarse bar (a few minutes late, at a known price)."""
    b = BARS[1].get(t_live - dt.timedelta(minutes=1))
    if b: return b[3], t_live
    for r in (2, 5):
        m = t_live - dt.timedelta(minutes=1)
        k = m - dt.timedelta(minutes=m.minute % r)
        if k in BARS[r]: return BARS[r][k][3], k + dt.timedelta(minutes=r)
    return None, None

def replay(t):
    """(b)/(c)/(d) for a tracker trade. Returns dict of R or None."""
    risk = abs(t['entry'] - t['sl'])
    if risk <= 0 or 'xtime' not in t: return None
    r = pick_res(t['time'])
    if r is None or (r > 1 and risk < 8): return None      # coarse bars only for wide stops
    mins = int((t['xtime'] - t['time']).total_seconds() // 60)
    p = [x for x in path(t['time'], max(mins, 1), r)]
    sgn = 1 if t['side'] == 'LONG' else -1
    R1 = sgn*(t['tp1']-t['entry'])/risk
    def run(rule):
        stop = t['sl']; got1 = False
        for k, (o, h, l, c) in p:
            hs = l <= stop if sgn > 0 else h >= stop
            if hs:
                rr = sgn*(stop-t['entry'])/risk
                return 0.5*R1 + 0.5*rr if (rule == 'c' and got1) else rr
            h1 = h >= t['tp1'] if sgn > 0 else l <= t['tp1']
            h3 = h >= t['tp3'] if sgn > 0 else l <= t['tp3']
            if h1 and not got1:
                got1 = True
                if rule == 'd': return R1
            if h3:
                r3 = sgn*(t['tp3']-t['entry'])/risk
                return 0.5*R1 + 0.5*r3 if rule == 'c' else r3
            if got1 and rule in ('b', 'c'): stop = t['entry']
        rr = t['R'] if t['R'] is not None else 0
        if rule in ('b', 'c') and got1 and t['reason'] == 'SL': rr = 0.0   # BE stop took it
        return 0.5*R1 + 0.5*rr if (rule == 'c' and got1) else rr
    return dict(a=t['R'], b=run('b'), c=run('c'), d=run('d'), res=r)

def logged_alt(t):
    """(b)/(c)/(d) from the logged TP Reached only (no bars). Optimistic: ignores BE shake-outs of
    winners. Used only as a cross-check beside the bar replay."""
    risk = abs(t['entry']-t['sl']); sgn = 1 if t['side'] == 'LONG' else -1
    R1 = sgn*(t['tp1']-t['entry'])/risk if risk else 1
    a = t['R']
    if t['tpr'] < 1: return dict(a=a, b=a, c=a, d=a)
    b = a if a >= 0 else 0.0
    return dict(a=a, b=b, c=0.5*R1 + 0.5*b, d=R1)

def stats(rs, pts=None):
    n = len(rs)
    if n == 0: return dict(n=0)
    w = sum(1 for r in rs if r > 1e-9); l = sum(1 for r in rs if r < -1e-9)
    cum = peak = dd = 0.0; cw = cl = bl = 0
    for r in rs:
        cum += r; peak = max(peak, cum); dd = max(dd, peak-cum)
        if r < -1e-9: cl += 1; bl = max(bl, cl)
        elif r > 1e-9: cl = 0
    out = dict(n=n, w=w, l=l, be=n-w-l, win=100.0*w/n, tot=sum(rs), avg=sum(rs)/n, dd=dd, worst=bl)
    if pts is not None:
        net = sum(pts)*PT - COST*n
        cum = peak = ddd = 0.0
        for p_ in pts:
            cum += p_*PT - COST; peak = max(peak, cum); ddd = max(ddd, peak-cum)
        out.update(net=net, exp=net/n, dd_usd=ddd)
    return out

def thin(n): return ' (thin)' if n < 20 else ''

HDR = ('| Group | n | W/BE/L | Win % | Total R | Avg R | $ net 1 ES | $/trade | Max DD | Worst run |\n'
       '|---|---|---|---|---|---|---|---|---|---|')
def row(lab, rs, pts):
    s = stats(rs, pts)
    if s['n'] == 0: return f'| {lab} | 0 | | | | | | | | |'
    return (f"| {lab}{thin(s['n'])} | {s['n']} | {s['w']}/{s['be']}/{s['l']} | {s['win']:.0f}% | {s['tot']:+.1f}R | "
            f"{s['avg']:+.3f} | ${s['net']:,.0f} | ${s['exp']:,.0f} | {s['dd']:.1f}R / ${s['dd_usd']:,.0f} | {s['worst']} |")

def btable(title, groups, key):
    """groups: [(label, trades)]; key: bracket key on trades."""
    L = [f'\n**{title}**\n', HDR]
    for lab, xs in groups:
        xs = [x for x in xs if x.get(key)]
        stop = xs[0][key][5] if xs else 4
        L.append(row(lab, [x[key][0]/x[key][5] for x in xs], [x[key][0] for x in xs]))
    return '\n'.join(L)

def atable(title, groups):
    L = [f'\n**{title}**\n', HDR]
    for lab, xs in groups:
        xs = [x for x in xs if x.get('R') is not None]
        L.append(row(lab, [x['R'] for x in xs], [x['pnl'] for x in xs]))
    return '\n'.join(L)

# ------------------------------------------------------------------ load
def load_tracker(fn):
    rows = list(csv.reader(open(os.path.join(DATA, fn))))
    hdr = rows[0]; ix = {h: i for i, h in enumerate(hdr)}; out = []
    for r in rows[1:]:
        r = r + ['']*(len(hdr)-len(r))
        if not r[0].strip(): continue
        d = dict(id=r[0], date=r[ix['Date']], t=r[ix['Entry Time (ET)']], side=r[ix['Side']],
                 entry=f2(r[ix['Entry']]), sl=f2(r[ix['SL']]), tp1=f2(r[ix['TP1']]), tp2=f2(r[ix['TP2']]),
                 tp3=f2(r[ix['TP3']]), risk=f2(r[ix['Risk (pts)']]), tpr=int(f2(r[ix['TP Reached']]) or 0),
                 xt=r[ix['Exit Time (ET)']], xp=f2(r[ix['Exit']]), reason=r[ix['Exit Reason']],
                 pnl=f2(r[ix['P&L (pts)']]), R=f2(r[ix['R']]), result=r[ix['Result']],
                 setup=r[ix['Setup']] if 'Setup' in ix else '')
        d['time'] = tparse(d['date'], d['t'])
        if d['xt']:
            x = tparse(d['date'], d['xt'])
            if x < d['time']: x += dt.timedelta(days=1)
            d['xtime'] = x
        out.append(d)
    return [t for t in out if t['result'] in ('Win', 'Loss', 'Breakeven') and t['R'] is not None], \
           [t for t in out if t['result'] not in ('Win', 'Loss', 'Breakeven')]

def load_forward():
    rows = list(csv.reader(open(os.path.join(DATA, 'forward_test_log.csv'))))[1:]
    sig = []
    for r in rows:
        r = r + ['']*(20-len(r))
        if not r[0].strip().isdigit() or not r[2].strip(): continue
        t = tparse(r[1], r[2]) + dt.timedelta(hours=1)
        sig.append(dict(n=int(r[0]), date=r[1], time=t, typ=r[4].strip(), G=f2(r[6]), H=f2(r[7]),
                        entry=f2(r[9]), sl=f2(r[10]), tp1=f2(r[11]), tp3=f2(r[13]), res=r[14].strip(),
                        Rl=f2(r[15]), note=r[17]))
    return sig

def stop_bucket(x):
    if x <= 1: return 'a) <=1 pt'
    if x < 2.25: return 'b) 1.25-2 pts'
    if x < 3.5: return 'c) 2.25-3.25 pts'
    if x <= 4: return 'd) 3.5-4 pts (Tim rule)'
    if x <= 6: return 'e) 4.25-6 pts'
    return 'f) over 6 pts'

# ------------------------------------------------------------------ main analysis
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--1m', dest='m1'); ap.add_argument('--2m', dest='m2'); ap.add_argument('--5m', dest='m5')
    a = ap.parse_args()
    load_cache()
    for r, d in ((1, a.m1), (2, a.m2), (5, a.m5)):
        if d: merge_yahoo(d, r)
    save_cache()
    md = []
    span = {r: (min(BARS[r]), max(BARS[r]), len(BARS[r])) for r in RES if BARS[r]}
    md.append('<!-- generated by indicator_analysis.py; bars: ' + '; '.join(
        f'{r}m {v[0]} to {v[1]} ({v[2]})' for r, v in span.items()) + ' -->')

    pro, pro_open = load_tracker('crt_pro_trades.csv')
    vm, vm_open = load_tracker('crt_pro_vmap.csv')
    sig = load_forward()
    divs = [s for s in sig if s['typ'] in ('Bull Div', 'Bear Div')]
    for s in divs:
        s['side'] = 'LONG' if s['typ'] == 'Bull Div' else 'SHORT'
        s['lt'] = s['time'] + dt.timedelta(minutes=5)          # label bar (1m, divPivotLen 5)

    def div_near(side, t, mins=25):
        """Same-direction Div pivot 0-25 min before t (same definition as the 10/3 and 10/22 reports)."""
        return any(d['side'] == side and dt.timedelta(0) <= t - d['time'] <= dt.timedelta(minutes=mins) for d in divs)

    # ---- trackers
    for t in pro: t['src'] = 'crtpro'
    for t in vm: t['src'] = 'vmap'
    for t in pro + vm:
        t['sess'] = session(t['time'])
        t['alt'] = replay(t); t['lalt'] = logged_alt(t)
        for k, st, tg in (('b48', 4, 8), ('b358', 3.5, 8), ('b44', 4, 4)):
            br(t, k, t['side'], t['entry'], t['time'], st, tg)
        t['div'] = div_near(t['side'], t['time'])
        t['new'] = t['date'] > SINCE

    # ---- forward test BUY/SELL
    RES_R = {'STOPPED': -1, 'STOPPED (BE)': 0, 'TP1 HIT': 1, 'TP2 HIT': 2, 'TP3 HIT': 3, 'STOPPED (TRAIL)': 1}
    bs = [s for s in sig if s['typ'] in ('BUY', 'SELL')]
    for s in bs:
        s['src'] = 'fwd_bs'
        s['side'] = 'LONG' if s['typ'] == 'BUY' else 'SHORT'
        s['sess'] = session(s['time']); s['risk'] = abs(s['entry']-s['sl'])
        s['R'] = RES_R.get(s['res']); s['pnl'] = s['R']*s['risk'] if s['R'] is not None else None
        for k, st, tg in (('b48', 4, 8), ('b358', 3.5, 8), ('b44', 4, 4)):
            br(s, k, s['side'], s['entry'], s['time'], st, tg)
        s['div'] = div_near(s['side'], s['time']); s['new'] = s['date'] > SINCE
        # (b)/(c)/(d) on bars, held to SL or TP3, 4 h cap
        s['xtime'] = s['time'] + dt.timedelta(minutes=240); s['reason'] = 'T'; s['tpr'] = 0
        s['alt'] = None
        r = pick_res(s['time'])
        if r and s['R'] is not None:
            p = path(s['time'], 240, r)
            if p:
                tmp = dict(s, R=None); tmp['R'] = 0
                # exit at last bar close if neither hit
                sgn = 1 if s['side'] == 'LONG' else -1
                tmp['R'] = sgn*(p[-1][1][3]-s['entry'])/s['risk']
                s['alt'] = replay(tmp)
                if s['alt']: s['alt']['a'] = s['R']
    bsc = [s for s in bs if s['R'] is not None]
    # ---- Div from label
    for s in divs:
        s['src'] = 'fwd_div'
        s['sess'] = session(s['lt']); s['new'] = s['date'] > SINCE
        s['entry'], st0 = live_entry(s['lt'] + dt.timedelta(minutes=1))
        for k, st, tg in (('b48', 4, 8), ('b358', 3.5, 8), ('b44', 4, 4)):
            br(s, k, s['side'], s['entry'], st0, st, tg) if st0 else s.update({k: None})
    # ---- CRT tags
    crt = [s for s in sig if s['typ'].startswith('CRT')]
    for s in crt:
        s['src'] = 'fwd_crt'
        s['side'] = 'LONG' if 'Bull' in s['typ'] else 'SHORT'
        s['sess'] = session(s['time']); s['new'] = s['date'] > SINCE
        s['entry'], st0 = live_entry(s['time'])
        for k, st, tg in (('b48', 4, 8), ('b358', 3.5, 8), ('b44', 4, 4)):
            br(s, k, s['side'], s['entry'], st0, st, tg) if st0 else s.update({k: None})

    # ================================================================ write tables
    def coverage(xs, key='b48'):
        c = Counter(x[key][2] for x in xs if x.get(key))
        amb = sum(1 for x in xs if x.get(key + '_amb'))
        return (', '.join(f'{r}m {c[r]}' for r in RES if c[r]) + f'; ambiguous (left out) {amb}'
                + f'; no bars {sum(1 for x in xs if not x.get(key) and not x.get(key + "_amb"))}')

    md.append('\n# Tables\n')
    md.append('## 0. Data\n')
    md.append('| Source | Closed rows | Dates | Newest row | Since 11/8 | Bars used (4/8 bracket) |\n|---|---|---|---|---|---|')
    for lab, xs, op in (('CRT Pro Trades', pro, pro_open), ('CRT Pro VMap', vm, vm_open)):
        md.append(f"| {lab} | {len(xs)} (+{len(op)} open) | {min(x['date'] for x in xs)} to {max(x['date'] for x in xs)} | "
                  f"{max(x['time'] for x in xs)} ET | {sum(x['new'] for x in xs)} | {coverage(xs)} |")
    md.append(f"| Forward Test BUY/SELL | {len(bsc)} | {min(s['date'] for s in bs)} to {max(s['date'] for s in bs)} | "
              f"#{max(s['n'] for s in sig)} {max(s['time'] for s in sig)} ET | {sum(s['new'] for s in bs)} | {coverage(bs)} |")
    md.append(f"| Forward Test Div rows | {len(divs)} | | | {sum(s['new'] for s in divs)} | {coverage(divs)} |")
    md.append(f"| Forward Test CRT tags | {len(crt)} | | | {sum(s['new'] for s in crt)} | {coverage(crt)} |")
    md.append('| CRT Setups Tracker | 0 trades, 4 setup rows | 9/28 only | 9/30 13:21 (setup run) | 0 | n/a |')
    days = Counter(x['date'] for x in pro + vm)
    md.append('\nLogged dates (CRT Pro + VMap rows): ' + ', '.join(f'{d[5:]} {n}' for d, n in sorted(days.items())) + '.')
    fd = Counter(s['date'] for s in sig)
    md.append('\nForward Test Log dates (Central): ' + ', '.join(f'{d[5:]} {n}' for d, n in sorted(fd.items())) + '.')

    # ---- calibration: coarse vs 1m on the same trades (CRT Pro + VMap, 10/20 on)
    def only(r, *a):
        save = {q: BARS[q] for q in RES}
        for q in RES:
            if q != r: BARS[q] = {}
        try: return bracket(*a)
        finally:
            for q in RES: BARS[q] = save[q]
    AVG_AMB = {}
    for key, st, tg in (('b48', 4, 8), ('b358', 3.5, 8)):
        cal = []
        for t in pro + vm:
            if t['time'] < min(BARS[1]) + dt.timedelta(minutes=5): continue
            row_ = {r: only(r, t['side'], t['entry'], t['time'], st, tg) for r in RES}
            if all(row_.get(r) for r in RES) and row_[1][2] == 1: cal.append(row_)
        md.append(f'\n**Bar calibration, {st}/{tg} bracket** (CRT Pro + VMap trades from 10/20 on, the same trades scored on '
                  '1m, 2m and 5m bars, 1 ES):\n')
        md.append('| Bars | Trades | Scored | Ambiguous | Same outcome as 1m (scored) | Scored pts | 1m pts, same trades | '
                  'Ambiguous: 1m avg pts | All, ambiguous = stop | All, 1m truth |\n|---|---|---|---|---|---|---|---|---|---|')
        for r in RES:
            sc = [c for c in cal if c[r][1] != 'A']; am = [c for c in cal if c[r][1] == 'A']
            same = sum(1 for c in sc if c[r][1] == c[1][1])
            AVG_AMB[(key, r)] = sum(c[1][0] for c in am)/len(am) if am else 0.0
            cons = sum(c[r][0] for c in sc) - st*len(am)
            md.append(f'| {r}m | {len(cal)} | {len(sc)} | {len(am)} | {100*same/max(1,len(sc)):.0f}% | {sum(c[r][0] for c in sc):+.1f} | '
                      f'{sum(c[1][0] for c in sc):+.1f} | {AVG_AMB[(key, r)]:+.2f} | {cons:+.1f} | {sum(c[1][0] for c in cal):+.1f} |')
    md.append('\nReading: scored coarse-bar trades match 1m exactly; the error is all in the ambiguous ones, which on 1m '
              'average a loss. "Central" estimates below score each ambiguous trade at that 1m average for its bar size.')

    def central(xs, key):
        """(n, $ conservative, $ skip, $ central, pts central) for one group."""
        sc = [x for x in xs if x.get(key) and not x.get(key + '_amb')]
        am = [x for x in xs if x.get(key + '_amb')]
        stop = 4 if key == 'b48' else 3.5
        ps = sum(x[key][0] for x in sc)
        amp = [AVG_AMB.get((key, pick_res(x.get('lt', x['time'])) or 5), -stop) for x in am]
        n = len(sc) + len(am)
        return dict(n=n, amb=len(am), cons=(ps - stop*len(am))*PT - COST*n, skip=ps*PT - COST*len(sc),
                    cen=(ps + sum(amp))*PT - COST*n, cen_r=(ps + sum(amp))/stop)

    def ctable(title, groups, key):
        L = [f'\n**{title}**\n', '| Group | n | Ambiguous | Central R | Central $ net 1 ES | Central $/trade | Range $ (amb = stop .. amb left out) |',
             '|---|---|---|---|---|---|---|']
        for lab, xs in groups:
            c = central(xs, key)
            if not c['n']: continue
            L.append(f"| {lab}{thin(c['n'])} | {c['n']} | {c['amb']} | {c['cen_r']:+.1f}R | ${c['cen']:,.0f} | ${c['cen']/c['n']:,.0f} | "
                     f"${c['cons']:,.0f} .. ${c['skip']:,.0f} |")
        return '\n'.join(L)

    # ---- validation: logged actual vs 1m replay of the same rules
    # ---- headline
    md.append('\n## 1. Headline, season to date\n')
    groups = []
    md.append('**Indicator rules (a)-(d), replayed on bars** (R in the indicator\'s own risk units; $ on 1 ES uses points)\n')
    md.append('| Indicator | n | (a) Actual | (b) BE after TP1 | (c) Half at TP1 + BE | (d) Full at TP1 | (a) $ net 1 ES | Logged-only (b)/(c)/(d) |\n|---|---|---|---|---|---|---|---|')
    def altrow(lab, xs):
        rp = [x for x in xs if x.get('alt')]
        if not rp: return f'| {lab} | 0 | | | | | | |'
        s = {k: sum(x['alt'][k] for x in rp) for k in 'abcd'}
        net = sum(x['pnl'] for x in rp)*PT - COST*len(rp)
        lo = [x for x in xs if x.get('lalt')]
        ls = {k: sum(x['lalt'][k] for x in lo) for k in 'bcd'}
        lstr = f"{ls['b']:+.1f} / {ls['c']:+.1f} / {ls['d']:+.1f}R" if lo else 'n/a'
        return (f"| {lab}{thin(len(rp))} | {len(rp)} | {s['a']:+.1f}R | {s['b']:+.1f}R | {s['c']:+.1f}R | {s['d']:+.1f}R | "
                f"${net:,.0f} | {lstr} |")
    md.append(altrow('CRT Pro, all hours', pro))
    md.append(altrow('CRT Pro, NY 10-4 (Tim hours)', [t for t in pro if t['sess'] in TIM]))
    md.append(altrow('VMap, all hours', vm))
    md.append(altrow('VMap, NY 10-4', [t for t in vm if t['sess'] in TIM]))
    md.append(altrow('Forward Test BUY/SELL, all', bsc))
    md.append(altrow('Forward Test BUY/SELL, NY 10-4', [s for s in bsc if s['sess'] in TIM]))
    md.append('\nForward Test BUY/SELL (a) is the logged result (the indicator moves its stop to BE at TP1); '
              '(b)-(d) hold the same entries to SL or TP3 on bars for up to 4 h.')

    md.append(btable("Tim's bracket: 4 pt stop from entry, 8 pt target (2R), 1 ES, all hours",
                     [('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag (unfiltered)', crt)], 'b48'))
    md.append(f'\nAmbiguous coarse bars (2m/5m bar touching both levels, or a hit in a first bar that starts before the entry): '
              + ('counted as the stop (conservative).' if AMB_MODE == 'stop' else 'left out (optimistic; the left-out trades were mostly losers on 1m).'))
    one = lambda xs: [x for x in xs if x.get('b48') and x['b48'][2] == 1]
    md.append(btable("4/8 bracket on 1m bars only (10/20-10/23 and 11/11-11/13; the precise slice)",
                     [('CRT Pro', one(pro)), ('CRT Pro, NY 10-4', [x for x in one(pro) if x['sess'] in TIM]),
                      ('VMap', one(vm)), ('VMap, NY 10-4', [x for x in one(vm) if x['sess'] in TIM]),
                      ('Div from label', one(divs)), ('Div, NY 10-4', [x for x in one(divs) if x['sess'] in TIM]),
                      ('CRT tag', one(crt)), ('Fwd BUY/SELL', one(bs))], 'b48'))
    G5 = (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag (unfiltered)', crt))
    for key, lab in (('b48', '4 pt stop / 8 pt target'), ('b358', '3.5 pt stop / 8 pt target')):
        md.append(ctable(f'Central estimate, {lab}, all hours', G5, key))
        md.append(ctable(f'Central estimate, {lab}, NY 10:00-16:00', [(l, [x for x in xs if x['sess'] in TIM]) for l, xs in G5], key))
    md.append(btable("Same, NY 10:00-16:00 only (Tim's hours)",
                     [(l, [x for x in xs if x['sess'] in TIM]) for l, xs in
                      (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag (unfiltered)', crt))], 'b48'))
    md.append(btable("3.5 pt stop / 8 pt target, NY 10:00-16:00",
                     [(l, [x for x in xs if x['sess'] in TIM]) for l, xs in
                      (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag (unfiltered)', crt))], 'b358'))
    md.append(btable("For continuity with 10/22: 4/4 bracket, NY 10:00-16:00",
                     [(l, [x for x in xs if x['sess'] in TIM]) for l, xs in
                      (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag (unfiltered)', crt))], 'b44'))

    # ---- breakdowns per indicator
    def breakdown(name, xs, actual=True):
        md.append(f'\n## {name}: breakdowns\n')
        gs = [(s_, [x for x in xs if x['sess'] == s_]) for s_ in SESS if any(x['sess'] == s_ for x in xs)]
        gs += [('NY 10-4 (Tim hours)', [x for x in xs if x['sess'] in TIM]),
               ('Long', [x for x in xs if x['side'] == 'LONG']), ('Short', [x for x in xs if x['side'] == 'SHORT']),
               ('Long, NY 10-4', [x for x in xs if x['side'] == 'LONG' and x['sess'] in TIM]),
               ('Short, NY 10-4', [x for x in xs if x['side'] == 'SHORT' and x['sess'] in TIM])]
        if 'div' in xs[0]:
            gs += [('Div within 25 min before', [x for x in xs if x['div']]),
                   ('No Div within 25 min', [x for x in xs if not x['div']]),
                   ('Div within 25 min, NY 10-4', [x for x in xs if x['div'] and x['sess'] in TIM]),
                   ('No Div, NY 10-4', [x for x in xs if not x['div'] and x['sess'] in TIM])]
        if xs[0].get('setup'):
            for s_ in sorted(set(x['setup'] for x in xs)):
                gs += [(f'Setup {s_}', [x for x in xs if x['setup'] == s_]),
                       (f'Setup {s_}, NY 10-4', [x for x in xs if x['setup'] == s_ and x['sess'] in TIM])]
        wk = defaultdict(list)
        for x in xs:
            d = dt.date.fromisoformat(x['date']); wk[(d - dt.timedelta(days=d.weekday())).isoformat()].append(x)
        gs += [(f'Week of {k[5:]}', wk[k]) for k in sorted(wk)]
        gs += [('Since 11/8', [x for x in xs if x['new']])]
        if actual:
            md.append(atable(f'{name}, actual (indicator exits)', [(l, [x for x in g if x.get('R') is not None]) for l, g in gs]))
            sb = defaultdict(list)
            for x in xs: sb[stop_bucket(x['risk'])].append(x)
            md.append(atable(f'{name}, actual by the indicator\'s stop size', [(k, sb[k]) for k in sorted(sb)]))
            sbn = defaultdict(list)
            for x in xs:
                if x['sess'] in TIM: sbn[stop_bucket(x['risk'])].append(x)
            md.append(atable(f'{name}, actual by stop size, NY 10-4 only', [(k, sbn[k]) for k in sorted(sbn)]))
            # alt exits by session
            L = [f'\n**{name}, exit rules by session (bars; total R)**\n',
                 '| Group | n | (a) | (b) BE | (c) Half+BE | (d) Full TP1 |', '|---|---|---|---|---|---|']
            for l, g in gs[:len(SESS)+1]:
                rp = [x for x in g if x.get('alt')]
                if rp: L.append(f"| {l}{thin(len(rp))} | {len(rp)} | " + ' | '.join(f"{sum(x['alt'][k] for x in rp):+.1f}R" for k in 'abcd') + ' |')
            md.append('\n'.join(L))
        md.append(btable(f"{name}, Tim's bracket 4/8 (1 ES)", gs, 'b48'))
        if actual:
            sb = defaultdict(list)
            for x in xs:
                if x['sess'] in TIM: sb[stop_bucket(x['risk'])].append(x)
            md.append(btable(f"{name}, 4/8 bracket NY 10-4, split by the indicator's own stop size", [(k, sb[k]) for k in sorted(sb)], 'b48'))

    breakdown('CRT Pro ES', pro)
    breakdown('CRT Pro VMap', vm)
    breakdown('Forward Test BUY/SELL', bs)
    breakdown('Div from label', divs, actual=False)
    breakdown('CRT tag (unfiltered)', crt, actual=False)

    # ---- Tim's day simulation
    md.append("\n## Tim's day simulation (NY 10:00-16:00, 4/8 bracket, 1 ES, one position at a time)\n")
    md.append('Rules: take signals in order; skip any that fire while a trade is open; stop for the day when the '
              'next full loss would push the day past -$1,000. Variant "2 max" stops after 2 trades. '
              'Variant "done after a win" stops after the first winner.\n')
    md.append('| Indicator | Variant | Days | Trades | Win % | Total R | $ net 1 ES | Best day | Worst day | Red days | Days hitting -$1,000 cap |\n|---|---|---|---|---|---|---|---|---|---|---|')
    def sim(xs, variant, key='b48', start_sess=TIM):
        by = defaultdict(list)
        for x in sorted([x for x in xs if x['sess'] in start_sess and x.get(key)], key=lambda x: x.get('lt', x['time'])):
            by[x['date'] if 'lt' not in x else x['lt'].date().isoformat()].append(x)
        took = []; dayp = {}; capped = 0
        for d, ys in sorted(by.items()):
            free = None; pnl = 0.0; n = 0; won = False; cap = False
            for y in ys:
                t0 = y.get('lt', y['time'])
                if free and t0 < free: continue
                if variant == '2 max' and n >= 2: break
                if variant == 'done after a win' and won: break
                loss = y[key][5]*PT + COST
                if pnl - loss < -1000: cap = True; break
                took.append(y); n += 1
                p = y[key][0]*PT - COST; pnl += p; won = won or y[key][1] == 'W'
                free = y[key][4] + dt.timedelta(minutes=y[key][2])   # flat after the exit bar
            dayp[d] = pnl; capped += cap
        return took, dayp, capped
    for name, xs in (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag', crt)):
        for v in ('cap only', '2 max', 'done after a win'):
            took, dayp, capped = sim(xs, v)
            if not took: continue
            s = stats([x['b48'][0]/x['b48'][5] for x in took], [x['b48'][0] for x in took])
            dv = list(dayp.values())
            md.append(f"| {name} | {v} | {len(dayp)} | {s['n']}{thin(s['n'])} | {s['win']:.0f}% | {s['tot']:+.1f}R | ${s['net']:,.0f} | "
                      f"${max(dv):,.0f} | ${min(dv):,.0f} | {sum(1 for v_ in dv if v_ < 0)} | {capped} |")

    # ---- since 11/8
    md.append('\n## Since the 11/8 report (rows dated after 11/8)\n')
    md.append(atable('Actual', [('CRT Pro', [t for t in pro if t['new']]), ('VMap', [t for t in vm if t['new']]),
                                ('Fwd BUY/SELL', [s for s in bsc if s['new']])]))
    md.append(btable('4/8 bracket', [('CRT Pro', [t for t in pro if t['new']]), ('VMap', [t for t in vm if t['new']]),
                                    ('Fwd BUY/SELL', [s for s in bs if s['new']]), ('Div from label', [s for s in divs if s['new']]),
                                    ('CRT tag', [s for s in crt if s['new']])], 'b48'))

    # ---- stop survival (adverse excursion before +8)
    md.append('\n## How far price goes against the entry before +8 (1m/2m/5m bars, 120 min, NY 10-4)\n')
    md.append('| Indicator | n | Reached +8 | Median adverse before +8 | 75th pct | 90th pct | 4 pt stop survives | 3.5 pt survives |\n|---|---|---|---|---|---|---|---|')
    def mae(x, start, entry):
        r = pick_res(start)
        if r is None or entry is None: return None
        sgn = 1 if x['side'] == 'LONG' else -1; m = 0.0
        for k, (o, h, l, c) in path(start, 120, r):
            m = max(m, (entry-l) if sgn > 0 else (h-entry))
            if ((h-entry) if sgn > 0 else (entry-l)) >= 8: return ('w', m)
        return ('n', m)
    for name, xs in (('CRT Pro', pro), ('VMap', vm), ('Fwd BUY/SELL', bs), ('Div from label', divs), ('CRT tag', crt)):
        ms = []
        for x in xs:
            if x['sess'] not in TIM: continue
            st = x['lt'] + dt.timedelta(minutes=1) if 'lt' in x else x['time']
            v = mae(x, st, x['entry'])
            if v: ms.append(v)
        w = sorted(m for o, m in ms if o == 'w')
        if not w: continue
        q = lambda p: w[min(len(w)-1, int(p*len(w)))]
        md.append(f"| {name} | {len(ms)} | {len(w)} ({100*len(w)/len(ms):.0f}%) | {q(.5):.2f} | {q(.75):.2f} | {q(.9):.2f} | "
                  f"{100*sum(1 for m in w if m < 4)/len(w):.0f}% | {100*sum(1 for m in w if m < 3.5)/len(w):.0f}% |")

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f'indicator-analysis-tables-{TAG}' + ('' if AMB_MODE == 'stop' else '-amb-skipped') + '.md')
    open(out, 'w').write('\n'.join(md) + '\n')
    # per-trade results so later runs keep bar scores after Yahoo drops the bars
    if AMB_MODE != 'stop': print(out); return
    with open(os.path.join(DATA, f'bar_scores_{TAG}.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source', 'id', 'date', 'time_et', 'session', 'side', 'entry', 'risk', 'R_actual',
                    'b48_pts', 'b48_out', 'b358_pts', 'b358_out', 'b44_pts', 'bars', 'alt_b', 'alt_c', 'alt_d', 'div25', 'b48_ambiguous'])
        for src, xs in (('crtpro', pro), ('vmap', vm), ('fwd_bs', bs), ('fwd_div', divs), ('fwd_crt', crt)):
            for x in xs:
                b, b3, b4, al = x.get('b48'), x.get('b358'), x.get('b44'), x.get('alt')
                w.writerow([src, x.get('id', x.get('n')), x['date'], x.get('lt', x['time']).isoformat(timespec='minutes'),
                            x['sess'], x['side'], x.get('entry'), x.get('risk'), x.get('R'),
                            b[0] if b else '', b[1] if b else '', b3[0] if b3 else '', b3[1] if b3 else '',
                            b4[0] if b4 else '', b[2] if b else '',
                            *(round(al[k], 3) if al else '' for k in 'bcd'), x.get('div', ''), int(bool(x.get('b48_amb')))])
    print(out)

if __name__ == '__main__':
    main()
