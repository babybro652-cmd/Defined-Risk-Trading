#!/usr/bin/env python3
"""Calibration review of logged soccer picks (analysis/ucl/picks_log.csv).

Usage: python3 analysis/ucl/review.py [--scope UCL|Domestic|all]

For each category: graded picks (W/L only; Void and DUP rows skipped), wins, hit rate, the average
predicted chance (rows with an estimate), hit rate minus predicted, and ROI if every pick had been
bet at its own fair price (1/pred). ROI at fair is 0% for a calibrated model; negative = overconfident.
Add a row per graded pick after each matchday (pred = the est % in the Bets row, as a decimal).
"""
import argparse, csv, os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', default='all')
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'picks_log.csv')))
            if r['result'] in ('W', 'L') and (a.scope == 'all' or r['scope'] == a.scope)]
    cats = {}
    for r in rows:
        cats.setdefault(r['category'], []).append(r)
    print(f"{'category':14} {'n':>3} {'W-L':>6} {'hit':>5} {'pred':>5} {'diff':>6} {'ROI@fair':>9}")
    tot = []
    for c, rs in sorted(cats.items(), key=lambda x: -len(x[1])):
        w = sum(r['result'] == 'W' for r in rs)
        pr = [r for r in rs if r['pred']]
        ps = [float(r['pred']) for r in pr]
        avg = sum(ps) / len(ps) if ps else None
        roi = (sum((1 / float(r['pred']) - 1) if r['result'] == 'W' else -1 for r in pr) / len(pr)) if pr else None
        tot += pr
        f = lambda x, s='{:.0%}': s.format(x) if x is not None else '-'
        print(f"{c:14} {len(rs):>3} {f'{w}-{len(rs) - w}':>6} {w / len(rs):>5.0%} {f(avg):>5} "
              f"{f(w / len(rs) - avg if avg is not None else None, '{:+.0%}'):>6} {f(roi, '{:+.0%}'):>9}")
    if tot:
        w = sum(r['result'] == 'W' for r in tot)
        avg = sum(float(r['pred']) for r in tot) / len(tot)
        roi = sum((1 / float(r['pred']) - 1) if r['result'] == 'W' else -1 for r in tot) / len(tot)
        print(f"{'all (w/ est)':14} {len(tot):>3} {f'{w}-{len(tot) - w}':>6} {w / len(tot):>5.0%} {avg:>5.0%} {w / len(tot) - avg:>+6.0%} {roi:>+9.0%}")


if __name__ == '__main__':
    main()
