"""Top-3 coverage (Tim, 11/14/26): did the game's first scorer (first points, FT count) come from our
#1, #2 or #3 game first-basket pick? Plus running hit rate and $1-straight P&L by rank once odds are logged.

Ranks come from the pre-game fb_candidates.json committed for each graded date (source_scorecard.COMMITS),
players tagged Out removed, both teams pooled, sorted by game chance. A ranked player who did not play
counts as a void (no hit, no stake). Odds: analysis/nba/out/top3_odds.csv (date,player,odds American),
filled from the Bets rows when Tim logs prices; a rank with no odds is left out of the P&L.

Run: python3 analysis/reports/top3_coverage.py            (all dates)
     python3 analysis/reports/top3_coverage.py 2026-11-13 (one night, per game)
Writes analysis/nba/out/top3_log.csv (one row per game and rank).
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import source_scorecard as sc

R = sc.R
ODDS = {}
p = R + '/analysis/nba/out/top3_odds.csv'
if os.path.exists(p):
    for r in csv.DictReader(open(p)):
        ODDS[(r['date'], sc.norm(r['player']))] = float(r['odds'])


def ranked(d, a, h):
    both = sc.OURS.get((d, a), []) + sc.OURS.get((d, h), [])
    return sorted(both, key=lambda x: -x[1])[:3]


def rows():
    out = []
    for (d, a, h), g in sorted(sc.G.items()):
        top = ranked(d, a, h)
        if len(top) < 3:
            continue
        for i, (name, pr, _) in enumerate(top, 1):
            n = sc.norm(name)
            played = n in g['played']
            hit = played and n == g['fp']
            o = ODDS.get((d, n))
            pnl = '' if o is None or not played else (round(o / 100 if o > 0 else 100 / abs(o), 2) if hit else -1.0)
            out.append(dict(date=d, game=f'{a} @ {h}', rank=i, player=name, p=round(pr, 4),
                            result='Void' if not played else ('W' if hit else 'L'), odds='' if o is None else o, pnl_1=pnl))
    return out


if __name__ == '__main__':
    rs = rows()
    with open(R + '/analysis/nba/out/top3_log.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rs[0]))
        w.writeheader(); w.writerows(rs)
    dates = sys.argv[1:] or sorted({r['date'] for r in rs})
    for d in dates:
        dr = [r for r in rs if r['date'] == d]
        games = sorted({r['game'] for r in dr})
        top3 = sum(any(r['result'] == 'W' for r in dr if r['game'] == gm) for gm in games)
        by = {k: sum(1 for r in dr if r['rank'] == k and r['result'] == 'W') for k in (1, 2, 3)}
        print(f"{d}: top 3 {top3} of {len(games)} | #1 {by[1]}, #2 {by[2]}, #3 {by[3]}")
        if len(sys.argv) > 1:
            for gm in games:
                print('  ', gm, ' / '.join(f"#{r['rank']} {r['player']} {r['result']}" for r in dr if r['game'] == gm))
    print('RUNNING (all logged dates)')
    for k in (1, 2, 3):
        kr = [r for r in rs if r['rank'] == k and r['result'] != 'Void']
        w = sum(r['result'] == 'W' for r in kr)
        priced = [r for r in kr if r['pnl_1'] != '']
        pnl = round(sum(r['pnl_1'] for r in priced), 2)
        print(f"#{k}: {w} of {len(kr)} ({100 * w / max(len(kr), 1):.0f}%), $1 straights P&L {pnl:+.2f} on {len(priced)} priced")
    ng = len({(r['date'], r['game']) for r in rs})
    t3 = len({(r['date'], r['game']) for r in rs if r['result'] == 'W'})
    print(f"Top 3 coverage: {t3} of {ng} games ({100 * t3 / max(ng, 1):.0f}%)")
