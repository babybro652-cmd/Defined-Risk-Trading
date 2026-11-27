#!/usr/bin/env python3
"""Black Friday 11/27/26 DEN @ PIT play chart (same layout as thanksgiving_charts.py)."""
import sys
sys.path.insert(0, '/home/user/Defined-Risk-Trading/analysis/nfl')
import thanksgiving_charts as tc

tc.G['den_pit'] = ('DEN @ PIT  Fri 3:00 PM ET  Prime  (DEN -4.5, total 37.5)  RJ Harvey OUT', [
  ('PIT +4.5 (side)', '-110', '57% / -132', 'FPI PIT by 0.3: QB change on PIT', 57, 'PASS (Rudolph, Rodgers cut)'),
  ('Jonah Coleman anytime TD', 'take -102+', '55% / -123', 'Harvey + Dobbins out (hand adj)', 55, 'BET at price $1'),
  ('Coleman first TD', 'take +780+', '13.6% / +633', 'top first TD pick', 13.6, '$0.50 at price'),
  ('Courtland Sutton first TD', 'take +1667+', '6.8% / +1373', 'only at +1667 or longer', 6.8, '$0.25 at price'),
  ('Jaylen Warren first TD', 'take +1476+', '7.6% / +1213', 'PIT top, backup QB cut', 7.6, '$0.25 at price'),
  ('Coleman or Warren 1st TD', 'take +465+', '21.3% / +370', 'new top-2 combo', 21.3, '$0.50 at price'),
  ('Coleman or Sutton 1st TD', 'take +487+', '20.4% / +389', 'best DEN pair', 20.4, '$0.25 at price'),
  ('Warren or Dowdle 1st TD', 'take +754+', '14.1% / +611', 'best PIT pair', 14.1, '$0.25 at price'),
  ('First scoring play', 'no edge', 'DEN TD 30.6% / +227', 'x0.92 to x1.04 vs spread', 30.6, 'PASS'),
  ('Total 37.5', 'no model', '-', 'no edge', 0, 'PASS'),
])

if __name__ == '__main__':
    tc.draw('den_pit', '/home/user/Defined-Risk-Trading/analysis/nfl/out/charts/blackfriday_den_pit.png')
