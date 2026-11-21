#!/usr/bin/env python3
"""Live NFL first scoring play prices for one week (first_score_model.py).

Per game: P(away TD, away FG, home TD, home FG, safety) for the game's first score, fair and take-at (fair decimal x1.2),
plus the spread-only baseline (B2) so we can see where our model disagrees with a line-based price.
Inputs: data/ftd_*.csv + data/fs_*.csv (all games so far), raw/games.csv (schedule, spread, total, roof).
Outputs: out/first_score_wk<N>.csv / .json, out/charts/first_score_wk<N>.png

  python3 analysis/nfl/first_score_model.py build     # after first_td_data.py --download (Tuesday)
  python3 analysis/nfl/first_score_week.py --week 11
"""
import csv, json, os, sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import first_td_model as m  # noqa
import first_score_model as fsm  # noqa

OUT = m.OUT


def schedule(season, week):
    out = []
    for r in csv.DictReader(open(os.path.join(m.RAW, 'games.csv'))):
        if int(r['season']) == season and int(r['week']) == week and r['game_type'] == 'REG':
            out.append(dict(game_id=r['game_id'], home=r['home_team'], away=r['away_team'], spread_line=r['spread_line'],
                            total_line=r['total_line'], day=r['weekday'], date=r['gameday'], time=r['gametime'],
                            roof=r['roof'] or 'outdoors'))
    return out


def run(season, week):
    _, st, fs, _, _, frows, drows, bl = fsm.walk(eval_from=(9999, 0))
    wd = m.ridge_logit(np.array([r[1] for r in drows]), np.array([r[2] for r in drows], float), lam=2.0)
    wf = m.ridge_logit(np.array([r[1] for r in frows]), np.array([r[2] for r in frows], float), lam=2.0)
    bl.fit()
    qo, qs = fs.q()
    res = []
    for g in schedule(season, week):
        h, a = g['home'], g['away']
        ih, ia = m.implied(g, h), m.implied(g, a)
        tf = {t: st.team_feats(t, o, m.implied(g, t)) for t, o in ((h, a), (a, h))}
        ff = {t: fs.feats(t, o, g['roof']) for t, o in ((h, a), (a, h))}
        pa = min(0.85, max(0.15, 0.5 + st.recv_tend(h) - st.recv_tend(a)))
        p = fsm.fs_chain(wd, wf, tf[h], tf[a], ff[h], ff[a], qo, qs, pa, st.pace(h) + st.pace(a))
        b = bl.predict(m.f(g['spread_line']), ih, ia, total=True)
        res.append(dict(game=g, p=[float(x) for x in p], b2=[float(x) for x in b], ff={t: ff[t] for t in ff}))
    write(season, week, res)
    return res


LABELS = [('home', 'TD', 0), ('home', 'FG', 1), ('away', 'TD', 2), ('away', 'FG', 3)]


def spots(res):
    rows = []
    for o in res:
        g = o['game']
        for side, ty, i in LABELS:
            t = g[side]
            p, b = o['p'][i], o['b2'][i]
            rows.append(dict(game=f"{g['away']} @ {g['home']}", kickoff=f"{g['day']} {g['date']} {g['time']}", date=g['date'],
                             outcome=f'{t} {"Touchdown" if ty == "TD" else "Field Goal"}', team=t, type=ty, p=p, b2=b, ratio=p / b))
        rows.append(dict(game=f"{g['away']} @ {g['home']}", kickoff=f"{g['day']} {g['date']} {g['time']}", date=g['date'],
                         outcome='Safety', team='', type='SAF', p=o['p'][4], b2=o['b2'][4], ratio=o['p'][4] / o['b2'][4]))
    return rows


def write(season, week, res):
    os.makedirs(os.path.join(OUT, 'charts'), exist_ok=True)
    rows = spots(res)
    with open(os.path.join(OUT, f'first_score_wk{week}.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Game', 'Kickoff', 'First scoring play', 'Our chance', 'Fair', 'Take at', 'Spread-only chance', 'Ours vs spread-only'])
        for r in rows:
            w.writerow([r['game'], r['kickoff'], r['outcome'], f"{r['p'] * 100:.1f}%", m.american(r['p']), m.take_at(r['p']),
                        f"{r['b2'] * 100:.1f}%", f"{r['ratio']:.2f}"])
    json.dump(dict(season=season, week=week, built=datetime.now().isoformat(timespec='minutes'),
                   games=[dict(game=f"{o['game']['away']} @ {o['game']['home']}", kickoff=f"{o['game']['day']} {o['game']['date']} {o['game']['time']}",
                               spread_line=o['game']['spread_line'], total_line=o['game']['total_line'], roof=o['game']['roof'],
                               **{k: o['p'][i] for i, k in enumerate(fsm.OUTCOMES)},
                               **{'b2_' + k: o['b2'][i] for i, k in enumerate(fsm.OUTCOMES)}) for o in res]),
              open(os.path.join(OUT, f'first_score_wk{week}.json'), 'w'), indent=1)
    today = datetime.now().strftime('%Y-%m-%d')
    left = [r for r in rows if r['date'] >= today and r['type'] != 'SAF']
    print('Top FG-first by our chance (games not yet played):')
    for r in sorted([r for r in left if r['type'] == 'FG'], key=lambda r: -r['p'])[:8]:
        print(f"  {r['outcome']:22s} {r['game']:10s} {r['p'] * 100:5.1f}%  fair {m.american(r['p']):>5s}  take {m.take_at(r['p']):>5s}  spread-only {r['b2'] * 100:4.1f}%  x{r['ratio']:.2f}")
    print('Biggest gaps vs spread-only baseline:')
    for r in sorted(left, key=lambda r: -r['ratio'])[:8]:
        print(f"  {r['outcome']:22s} {r['game']:10s} {r['p'] * 100:5.1f}%  fair {m.american(r['p']):>5s}  take {m.take_at(r['p']):>5s}  spread-only {r['b2'] * 100:4.1f}%  x{r['ratio']:.2f}")
    chart(week, res)


def chart(week, res):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['text.parse_math'] = False
    order = {'Thursday': 0, 'Friday': 1, 'Saturday': 2, 'Sunday': 3, 'Monday': 4}
    today = datetime.now().strftime('%Y-%m-%d')
    res = [o for o in res if o['game']['date'] >= today] or res
    res = sorted(res, key=lambda o: (order.get(o['game']['day'], 5), o['game']['time'], o['game']['game_id']))
    rows, hi = [], []
    for o in res:
        g = o['game']
        h, a = g['home'], g['away']
        p = o['p']
        hr = '%s %s' % (g['day'][:3], datetime.strptime(g['time'], '%H:%M').strftime('%-I:%M %p'))
        sp = float(g['spread_line'])
        line = f"{h if sp >= 0 else a} -{abs(sp):g}, O/U {float(g['total_line']):g}"
        ha, hh = p[2] + p[3], p[0] + p[1]
        cells = [f"{a} @ {h}\n{hr}\n{line}", f"{a} {ha * 100:.0f}%\n{h} {hh * 100:.0f}%\nSafety {p[4] * 100:.1f}%"]
        for i in (2, 3, 0, 1):
            t = a if i >= 2 else h
            ty = 'TD' if i in (0, 2) else 'FG'
            gap = p[i] / o['b2'][i]
            cells.append(f"{t} {ty}  {p[i] * 100:.1f}%\nfair {m.american(p[i])}   take {m.take_at(p[i])}\nvs spread-only {gap:.2f}x")
        rows.append(cells)
        hi.append([o['p'][i] / o['b2'][i] for i in (2, 3, 0, 1)])
    fig, ax = plt.subplots(figsize=(17, 1.0 * len(rows) + 1.6))
    ax.axis('off')
    ax.set_title(f"NFL First Scoring Play, Week {week} (our drive-chain model)\nChance each team + type is the game's first score, "
                 "fair price / take-at (fair decimal x1.2)", fontsize=15, fontweight='bold', pad=12)
    tb = ax.table(cellText=rows, colLabels=['Game', 'Scores first', 'Away TD', 'Away FG', 'Home TD', 'Home FG'],
                  colWidths=[0.13, 0.11, 0.19, 0.19, 0.19, 0.19], loc='upper center', cellLoc='left')
    tb.auto_set_font_size(False); tb.set_fontsize(10.5)
    hgt = 0.86 / max(len(rows), 1)
    for (r, c), cl in tb.get_celld().items():
        cl.set_height(hgt if r > 0 else 0.03)
        if r == 0:
            cl.set_facecolor('#1f3a5f'); cl.get_text().set_color('white'); cl.get_text().set_fontweight('bold')
        elif r % 2 == 0:
            cl.set_facecolor('#eef2f7')
        if r > 0 and c >= 2 and hi[r - 1][c - 2] >= 1.08:
            cl.set_facecolor('#dff3e3')
    fig.subplots_adjust(bottom=0.08)
    plt.figtext(0.5, 0.01, "Green = our chance is 8%+ above a spread-and-total-only price (where a line-based book may be beatable). "
                "TD = any TD by that team (offense, defense, return).\nFirst score was a TD 59%, FG 40%, safety 0.3% (2024-26). "
                "Backtest: small edge over a spread-only model, well calibrated; no real price history, so the edge vs FanDuel is unproven.\n"
                "Bet only at take-at or longer, small stakes. Rerun after inactives.", ha='center', fontsize=10)
    pth = os.path.join(OUT, 'charts', f'first_score_wk{week}.png')
    plt.savefig(pth, dpi=110, bbox_inches='tight')
    plt.close(fig)
    print(pth)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--week', type=int, default=11)
    ap.add_argument('--season', type=int, default=2026)
    a = ap.parse_args()
    run(a.season, a.week)
