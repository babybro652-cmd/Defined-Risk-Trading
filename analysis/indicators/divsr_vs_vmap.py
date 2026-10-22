#!/usr/bin/env python3
"""CRT DIV SR vs CRT Pro VMap, head to head (10/22/2026).

Reuses compare_indicators.py (loaders, bar replay, stats). Same inputs:
  data/crt_pro_vmap.csv, data/forward_test_log.csv (read-only sheet exports)
  argv[1] = folder of Yahoo ES=F 1m JSON files.

Entry types
  CRT DIV SR (indicators/CRT-Divergence-SR.pine, logs to the CRT Forward Test Log):
    BUY/SELL  = CRT sweep at S/R with a recent same-side RSI divergence. Own levels:
                SL beyond the sweep + 0.15 ATR, TP1-3 = 1/2/3R, SL to BE at TP1.
    Div       = RSI divergence label (entry at the label close, 5 bars after the pivot).
                No stop/target of its own, so 4/4 only.
    CRT tag   = CRT pattern without the confluence. No levels of its own, 4/4 only.
    (No A/B setups in this indicator.)
  CRT Pro VMap (pine/crt-pro-vmap-es.pine):
    Setup A   = CRT Pro signal the volume map agrees with.
    Setup B   = POC reaction in the CRT bias direction.
    Own levels: 4 pt hard stop, TP1 at the POC (or 1R), final at the untaken session
    high/low (or 3R).

4/4 = 4 pt stop / 4 pt target, stop first on a bar touching both, 60 min timeout.
$ = 2 ES, $100/pt, minus $10 per trade.
Tim's rules = NY 9:30-16:00 only, first 2 trades per ET day, one position at a time
(the next trade must come after the previous one closed).
"""
import sys, os, datetime as dt
from collections import defaultdict
import compare_indicators as ci

HERE = os.path.dirname(os.path.abspath(__file__))
NY = {'NY open 9:30-10', 'NY 10-12', 'NY PM 12-4'}


def bracket_t(side, entry, start, stop_pts=4.0, tgt_pts=4.0, minutes=60):
    """ci.bracket plus the exit time."""
    p = ci.path(start, minutes)
    if not p: return None
    sgn = 1 if side == 'LONG' else -1
    sl = entry - sgn*stop_pts; tp = entry + sgn*tgt_pts
    for k, (o, h, l, c) in p:
        if k.hour == 17 and k.minute == 0: return (sgn*(o-entry), 'T', k)
        if (l <= sl if sgn > 0 else h >= sl): return (-stop_pts, 'L', k)
        if (h >= tp if sgn > 0 else l <= tp): return (tgt_pts, 'W', k)
    return (sgn*(p[-1][1][3]-entry), 'T', p[-1][0])


def build():
    vm = ci.analyze_tracker('VMap', ci.load_tracker('crt_pro_vmap.csv'), [], {})
    sig = ci.analyze_forward([], {})
    X = []
    for t in vm:
        b = bracket_t(t['side'], t['entry'], t['time'] + dt.timedelta(minutes=1))
        X.append(dict(ind='VMap', typ='Setup ' + t['setup'], et=t['time'], date=t['time'].date(),
                      sess=ci.session(t['time']), own=(t['R'], t['pnl']), own_end=t['xtime'],
                      b44=b))
    for s in sig:
        if s['typ'] in ('BUY', 'SELL'):
            if s['res'] not in ci.RES_R and not s.get('b44'): continue
            own = (s['Rl'], s['Rl']*s['risk']) if s['res'] in ci.RES_R else None
            b = bracket_t(s['side'], s['entry'], s['time'])
            X.append(dict(ind='DivSR', typ='BUY/SELL', et=s['time'], date=s['time'].date(),
                          sess=s['sess'], own=own, own_end=b[2] if b else s['time'], b44=b))
        elif 'Div' in s['typ'] and s.get('label') is not None:
            b = bracket_t(s['side'], s['label'], s['lt'] + dt.timedelta(minutes=1))
            X.append(dict(ind='DivSR', typ='Div', et=s['lt'], date=s['lt'].date(),
                          sess=s['sess'], own=None, own_end=None, b44=b))
        elif s['typ'].startswith('CRT') and s.get('tag') is not None:
            b = bracket_t(s['side'], s['tag'], s['time'])
            X.append(dict(ind='DivSR', typ='CRT tag', et=s['time'], date=s['time'].date(),
                          sess=s['sess'], own=None, own_end=None, b44=b))
    return X


def tim(xs, mode):
    """NY only, first 2 per day, one position at a time (by that mode's exit)."""
    by = defaultdict(list)
    for x in sorted(xs, key=lambda x: x['et']):
        if x['sess'] in NY and (x['b44'] if mode == '44' else x['own']): by[x['date']].append(x)
    took = []
    for d, ys in by.items():
        busy = None; n = 0
        for y in ys:
            if n >= 2: break
            if busy and y['et'] < busy: continue
            took.append(y); n += 1
            busy = y['b44'][2] if mode == '44' else (y['own_end'] or y['b44'][2])
    return took


def st(xs, mode):
    if mode == '44':
        ys = [x for x in xs if x['b44']]
        return ci.stats([x['b44'][0]/4 for x in ys], [x['b44'][0] for x in ys])
    ys = [x for x in xs if x['own']]
    return ci.stats([x['own'][0] for x in ys], [x['own'][1] for x in ys])


def row(name, s):
    if not s or s['n'] == 0: return f'| {name} | 0 | | | | | | | |'
    return (f"| {name} | {s['n']} | {s['win']:.0f}% | {s['avg']:+.2f}R | {s['tot']:+.1f}R | "
            f"${s['net']:,.0f} | ${s['exp']:,.0f} | {s['dd']:.1f}R | {s['worst']} |")

HDR = ('| Entry type | n | Win % | Avg R | Total R | $ 2 ES net | Exp $/trade | Max DD | Longest losing streak |\n'
       '|---|---|---|---|---|---|---|---|---|')

TYPES = [('VMap', 'All'), ('VMap', 'Setup A'), ('VMap', 'Setup B'),
         ('DivSR', 'BUY/SELL'), ('DivSR', 'Div'), ('DivSR', 'CRT tag')]


def pick(X, ind, typ):
    return [x for x in X if x['ind'] == ind and (typ == 'All' or x['typ'] == typ)]


def block(X, title, modes=('own', '44')):
    out = [f'\n### {title}\n']
    for mode in modes:
        lab = "Indicator's own stops/targets" if mode == 'own' else 'Fixed 4/4 (4 pt stop, 4 pt target)'
        for split, f in (('All sessions', lambda x: True), ('NY only 9:30-4', lambda x: x['sess'] in NY),
                         ('10-12 window', lambda x: x['sess'] == 'NY 10-12'), ("Tim's rules", None)):
            out.append(f'\n**{lab}, {split}**\n\n{HDR}')
            for ind, typ in TYPES:
                xs = pick(X, ind, typ)
                if not xs: continue
                if mode == 'own' and ind == 'DivSR' and typ != 'BUY/SELL':
                    continue  # Div and CRT tags have no stop/target of their own
                xs = tim(xs, mode) if f is None else [x for x in xs if f(x)]
                nm = ('VMap ' + typ) if ind == 'VMap' else ('DIV SR ' + typ)
                out.append(row(nm, st(xs, mode)))
    return '\n'.join(out)


def main():
    ci.BARS = ci.load_bars(sys.argv[1])
    ks = sorted(ci.BARS)
    X = build()
    vmd = sorted(x['date'] for x in X if x['ind'] == 'VMap')
    d0, d1 = vmd[0], vmd[-1]
    same = [x for x in X if d0 <= x['date'] <= d1]
    md = [f'<!-- generated by divsr_vs_vmap.py; bars {ks[0]} to {ks[-1]} ET, {len(ks)} 1m bars -->',
          f'VMap dates {d0} to {d1}. DIV SR full history '
          f"{min(x['date'] for x in X if x['ind']=='DivSR')} to {max(x['date'] for x in X if x['ind']=='DivSR')}."]
    md.append(block(same, f'Same dates ({d0} to {d1})'))
    # halves: cut at the median VMap date
    cut = vmd[len(vmd)//2]
    md.append(f'\n### Stability: halves split at {cut} (VMap median trade date)\n')
    for mode in ('own', '44'):
        lab = "own stops" if mode == 'own' else '4/4'
        md.append(f'\n**{lab}**\n\n| Entry type | First half | Second half | NY first half | NY second half | Tim\'s rules first half | Tim\'s rules second half |\n|---|---|---|---|---|---|---|')
        for ind, typ in TYPES:
            if mode == 'own' and ind == 'DivSR' and typ != 'BUY/SELL': continue
            xs = pick(same, ind, typ)
            cells = []
            for g in ([x for x in xs if x['date'] < cut], [x for x in xs if x['date'] >= cut],
                      [x for x in xs if x['date'] < cut and x['sess'] in NY],
                      [x for x in xs if x['date'] >= cut and x['sess'] in NY],
                      tim([x for x in xs if x['date'] < cut], mode),
                      tim([x for x in xs if x['date'] >= cut], mode)):
                s = st(g, mode)
                cells.append('n=0' if s['n'] == 0 else f"n={s['n']}, {s['win']:.0f}%, {s['tot']:+.1f}R, ${s['net']:,.0f}")
            nm = ('VMap ' + typ) if ind == 'VMap' else ('DIV SR ' + typ)
            md.append(f'| {nm} | ' + ' | '.join(cells) + ' |')
    md.append(block([x for x in X if x['ind'] == 'DivSR'], 'DIV SR full history'))
    out = os.path.join(HERE, 'out', 'divsr-vs-vmap-tables-2026-10-22.md')
    open(out, 'w').write('\n'.join(md) + '\n')
    print(out)

if __name__ == '__main__':
    main()
