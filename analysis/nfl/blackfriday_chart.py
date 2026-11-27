#!/usr/bin/env python3
"""Black Friday 11/27/26 DEN @ PIT play chart (same layout as thanksgiving_charts.py)."""
import sys
sys.path.insert(0, '/home/user/Defined-Risk-Trading/analysis/nfl')
import thanksgiving_charts as tc

tc.G['den_pit'] = ('DEN @ PIT  Fri 3:00 PM ET  Prime  (DEN -4.5, total 37.5)', [
  ('PIT +4.5 (side)', '-110', '57% / -132', 'FPI PIT by 0.3: QB change on PIT', 57, 'PASS (Rudolph, Rodgers cut)'),
  ('Jonah Coleman anytime TD', 'take +126+', '49% / +105', 'Dobbins suspended', 49, 'BET at price $1'),
  ('RJ Harvey anytime TD', 'take +230+', '34% / +192', 'only at +230 or longer', 34, 'small $0.50 at price'),
  ('Coleman first TD', 'take +929+', '11.7% / +758', 'top first TD pick', 11.7, '$0.50 at price'),
  ('Harvey first TD', 'take +1391+', '8.0% / +1143', 'only at +1391 or longer', 8.0, '$0.25 at price'),
  ('Jaylen Warren first TD', 'take +1476+', '7.6% / +1213', 'PIT top, backup QB cut', 7.6, '$0.25 at price'),
  ('Coleman or Harvey 1st TD', 'take +509+', '19.7% / +407', 'top-2 combo = DEN pair', 19.7, '$0.50 at price'),
  ('Warren or Dowdle 1st TD', 'take +754+', '14.1% / +611', 'best PIT pair', 14.1, '$0.25 at price'),
  ('First scoring play', 'no edge', 'DEN TD 30.6% / +227', 'x0.92 to x1.04 vs spread', 30.6, 'PASS'),
  ('Total 37.5', 'no model', '-', 'no edge', 0, 'PASS'),
])

if __name__ == '__main__':
    tc.draw('den_pit', '/home/user/Defined-Risk-Trading/analysis/nfl/out/charts/blackfriday_den_pit.png')
