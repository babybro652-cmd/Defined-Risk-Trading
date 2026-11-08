# CRT Pro VMap analysis, 11/8/2026

Private analysis (indicator names fine here; never in public posts). Read-only: no sheet was edited.
Indicator analyzed: **CRT Pro VMap** (`pine/crt-pro-vmap-es.pine`, volume-map filter on CRT Pro signals).
No VWAP feature exists in the repo, so "VWAP" was read as VMap.
Script: `vmap_analysis.py` (run `python3 vmap_analysis.py <folder of Yahoo ES=F 1m JSON>`).
Full tables: `out/vmap-analysis-tables-2026-11-08.md`. Chart: `out/vmap-analysis-2026-11-08.png`.
Builds on `vmap-take-skip-2026-10-22.md`, `divsr-vs-vmap-2026-10-22.md`, `indicator-comparison-2026-10-22.md`.

## Data, and the big gap

| Source | Rows | Span |
|---|---|---|
| CRT Pro VMap tab | 140 closed (102 Setup A, 38 Setup B), 1 open | 10/2 to 10/23 13:38 ET |
| CRT Pro Trades (the unfiltered signals) | 810 closed | 9/30 to 10/23 14:18 ET |
| CRT Forward Test Log (CRT + Div) | #1-#534 | 9/21 to 10/21 |

- **Nothing has been logged since 10/23 (16 days).** New since the 10/22 reports: 24 VMap trades and
  108 CRT Pro trades (10/22 to 10/23 midday). The Forward Test Log has no rows after #534 (10/21
  20:16). Likely the TradingView alerts stopped again (or the chart was off). Tim should check the
  alerts; without them the forward test is dead.
- **Column H does not exist on the VMap tab.** In the Forward Test Log it is filled on 122 rows,
  last one #293 (10/9): 120 Div rows (0 ticks by construction) and 2 CRT rows. So H adds nothing for
  VMap. Drawdown below comes from the VMap logs (4 pt stop) and 1m ES bars.
- Bars (Yahoo ES=F 1m) only reach back 30 days, so bar-based tests cover **10/12 to 10/23 (111 VMap
  trades)**. Logged-result tests cover all 140.
- Win/loss math: VMap uses a fixed 4 pt stop and TP3 = 3R, so break-even is a **25% win rate**.
  Standard error of average R at n=140 is about +/-0.145R. Every "edge" below is inside that noise
  unless said otherwise.

## 1. VMap-filtered vs unfiltered

| | n | Win | Avg R | Total R | Max DD | Worst streak | $ net, 2 ES |
|---|---|---|---|---|---|---|---|
| VMap, all (actual) | 140 | 24% | -0.057 | -8.0R | 17R | 13 | -$4,600 (-$33/trade) |
| VMap Setup A | 102 | 25% | +0.020 | +2.0R | 9R | 9 | -$220 |
| VMap Setup B | 38 | 18% | -0.263 | -10.0R | 10R | 8 | -$4,380 |
| CRT Pro unfiltered, same dates (10/2+) | 731 | 24% | -0.065 | -47.8R | 84R | 15 | -$20,560 |
| CRT Pro unfiltered, all | 810 | 24% | -0.067 | -54.7R | 84R | 17 | -$23,150 |

- Per trade the filtered and unfiltered results are the same (-0.057R vs -0.065R). The map cut the
  signal count by about 5x and the drawdown from 84R to 17R, but did not add expectancy.
- Same signals, same 4/4 bracket on bars (10/12-10/23): signals the map kept 75 trades, 48%, -0.6R;
  signals it removed 505 trades, 49%, -4.9R. Per trade -0.008R vs -0.010R. **The map is not picking
  better signals.**
- What helps is the 4 pt stop, not the map. The 87 Setup A signals that match a CRT Pro row lost
  -22.6R under CRT Pro's own stops (median stop 1.75 pts; 459 of 810 CRT Pro stops under 2 pts, only 39
  inside 3.5-4) but A as a whole is +2.0R under VMap's 4 pt stop / 3R target.
- Setup B (POC reaction) is the weak half: -10R on 38. In 10-12 it is +7R on 5 trades, too few to use.
- Take/skip (Tim's Z/AA marks): still 28 marks, nothing new after 10/22 (Take 4W/4L +32 pts; Skip 1W/12L;
  Opposite 0/5). He stopped marking on 10/23.

## 2. Time of day (ET, VMap actual)

| Session | n | Win | Avg R | Total R |
|---|---|---|---|---|
| Asia (0:00-3:00) | 14 | 29% | +0.14 | +2R |
| London 3:00-9:30 | 45 | 22% | -0.11 | -5R |
| NY open 9:30-10:00 | 8 | 25% | 0.00 | 0R |
| **NY 10-12** | **33** | **27%** | **+0.09** | **+3R** |
| NY PM 12-4 | 40 | 20% | -0.20 | -8R |

- Tim's window (10:00-11:59) is the only session that is positive, and barely: +3R on 33. Inside it the
  10:00 hour is +7R (17 trades, 35%) and the 11:00 hour -4R (16 trades, 19%).
- 10-12 early vs late: to 10/15 -2R (n=18), 10/16 on +5R (n=15). Not stable.
- 10-12 by setup: A -4R (28), B +7R (5).
- NY 10:00-3:59 PM combined (what the no-pre-10 rule leaves): 73 trades, 23%, -5R. Before 10:00 (Asia,
  London, open): 67 trades, -3R. The pre-10 trades Tim skips were not where the money was lost.
- CRT Pro unfiltered by session is negative in every NY window (10-12: 104 trades, -15.4R actual).

## 3. Direction and EMA20

| | n | Win | Avg R | Total R |
|---|---|---|---|---|
| Long | 60 | 22% | -0.13 | -8R |
| Short | 80 | 25% | 0.00 | 0R |
| Long A / Short A | 39 / 63 | 21% / 29% | -0.18 / +0.14 | -7R / +9R |
| Long B / Short B | 21 / 17 | 24% / 12% | -0.05 / -0.53 | -1R / -9R |
| 10-12 long / short | 12 / 21 | 33% / 24% | +0.33 / -0.05 | +4R / -1R |

- Over all trades, shorts are better (Setup A short +9R on 63). In 10-12 it flips (long +4R on 12).
  The direction split is not stable; treat as noise.
- **EMA20 on vs off cannot be tested.** The trend filter is on by default and every logged signal has
  it on: on 1m bars 111 of 111 VMap entries sit on the trend side of the EMA20 (0 against). Need a
  deliberate off-run to compare.
- Lead found instead: **distance from the 1m EMA20 at entry** (bars, n=111):

| Distance from EMA20 | n | Win | Total R |
|---|---|---|---|
| 0.1-1.4 pts | 37 | 30% | +7R |
| 1.4-3.4 pts | 37 | 30% | +7R |
| 3.4+ pts | 37 | 11% | -21R |

  Within 3.4 pts: 74 trades, +14R. Beyond: 37 trades, 4 wins, -21R. It held in both halves (10/12-10/16:
  near +2R on 38, far -6R on 18; 10/19-10/23: near +11R on 37, far -14R on 18). Setup A within 3.4 pts:
  51 trades, +17R. The cut-off was picked after looking, and the worst bucket is not smooth (beyond 6
  pts is 0R on 16), so this is a **lead to test forward, not a rule**. Yahoo EMA may differ slightly from
  TradingView's; confirm on the chart.

## 4. How often the 3.5-4 pt stop is hit

- VMap stop is a fixed 4 pts. **Stopped out on 107 of 140 trades (76%).** 29 of those first touched TP1
  (21% of all trades), 31 were out within 3 minutes and 43 within 5 (median hold 8 min).
- On bars (n=111): 79 (71%) reach +4 pts within 60 min. Adverse move before +4: median 2.25 pts, 80th
  percentile 6, 90th 12. A 4 pt stop survives 66% of the moves that work, 3.5 pts 65%. Same measure for
  CRT Pro signals: 72% and 68% (n=573).
- Stop grid (target 4 pts, bars, $ net at 2 ES): 2 pts -$2,135, 3 pts -$1,110, **3.5 pts -$860**, 4 pts
  -$2,910, 5 pts -$410, 6 pts -$3,110, 8 pts -$2,810. All negative and not monotone, so no stop size is
  clearly better. 3.5 pts costs nothing in survival (65% vs 66%) and risks $50 less per trade at 2 ES.
- CRT Pro's own risk is the opposite problem: median 1.75 pts, 459 of 810 under 2 pts.

## 5. Which target works best

Fixed target from the logged TP Reached (stop 4 pts, n=140):

| Target | Win | Avg R | Total R | $/trade, 2 ES net |
|---|---|---|---|---|
| TP1 (1R, POC based) | 44% | -0.118 | -16.5R | -$57 |
| TP2 (2R) | 29% | -0.122 | -17.1R | -$59 |
| **TP3 (3R / session level)** | 24% | **-0.057** | **-8.0R** | -$33 |

- TP3 is the least bad overall; no target is positive. By group: London TP1 +0.28R (n=45), Asia TP3
  +0.14R (n=14), 10-12 TP3 +0.09R (n=33; TP1 -0.28R), Setup A TP3 +0.02R. Only the London TP1 result has
  a usable n, and London is the session Tim doesn't trade.
- Fixed point targets on bars (stop 4 pts, n=111): 2 pts -13.5R, 3 pts -7.8R, 4 pts -7.0R, 6 pts -13.5R,
  8 pts -15.0R, 12 pts -7.0R, 16 pts -2.9R. Nothing positive.
- Exit rules, bar replay (n=111): actual -7.0R, stop to BE after TP1 -17.1R, half at TP1 + BE -12.8R,
  full exit at TP1 -8.5R. Every alternative is worse than leaving it alone. Same answer as 10/22.
- 21% of trades touch TP1 and then hit the full stop. They are the loss pool, but BE rules cut more TP3
  winners than they save. (The script's "logged only" alt-exit line ignores shaken-out winners; trust
  the bar replay.)

## 6. What held up and what changed since 10/22

Held:
- VMap is roughly break-even to slightly negative: -8.0R on 116 then, -8.0R on 140 now (24 new trades
  added 0R). Setup A about 0, Setup B negative.
- No exit rule beats the plain 4 pt stop to TP3 (10/22: -30/-22/-14 vs -8; now -17/-13/-8.5 vs -7).
- NY PM and London are weak; the 10-12 window is the only positive session.
- Take/skip: Tim's filter was the only thing that worked and it has no new data.

Changed:
- 10-12: was +5R on 27, now +3R on 33. The 6 new 10-12 trades were 1 W / 5 L (-2R). The edge is shrinking.
- Setup A: +3R on 85, now +2R on 102 (17 new, -1R). Setup B: -7R on 35, now -10R on 38. B in NY
  (+3R on 13 then) is not worth acting on.
- CRT Pro unfiltered: -59.5R on 702, now -54.7R on 810. The last 108 trades are +4.8R but still -$1,105
  net at 2 ES after costs.
- New: the EMA-distance lead (section 3). Not in the 10/22 report.
- Logging stopped 10/23.

## 7. Recommendations (with sample sizes)

1. **Fix the logging first.** Re-check the TradingView alerts and webhook; 0 trades logged in 16
   days. Keep the Z/AA take/skip marks going. The EMA-distance lead needs 100+ new trades to confirm.
2. **Keep the 4 pt hard stop; try 3.5 pts.** Same survival (65% vs 66%, n=79 working moves), $50 less
   risk per trade at 2 ES, within Tim's 3.5-4 rule. Stop-size results are noisy (n=111), so this is a
   risk tweak, not an edge.
3. **Try an "EMA distance" cap of about 3.5 pts** (skip signals more than 3.5 pts from the 1m EMA20).
   Near: 74 trades, +14R; far: 37 trades, -21R, same sign in both halves. Lead only; forward-test it.
4. **Leave targets at TP3 (3R / session level).** TP1 and TP2 lose more (-16.5R, -17.1R vs -8.0R) and
   BE/partial exits lose more on bars. London TP1 +0.28R (n=45) is the only exception and is outside
   Tim's hours.
5. **Setup B off (test).** -10R on 38; its NY 10-12 slice (+7R, n=5) is too small to keep it for.
   Setup A alone is +2R on 102 (flat).
6. **Time filter: keep NY only; 10-12 is the window to test.** Skip NY PM (-8R, n=40, 20% win).
   10-12 is +3R on 33 and fading in the newest rows, so do not size up on it.
7. **Direction: no filter.** The long/short split flips between all-hours and 10-12.
8. **EMA20 trend filter: leave it on.** It cannot be judged without an off-run (all logged signals have
   it on); a direct on/off test is the next step.

Too few trades to act on: Setup B in 10-12 (n=5), long/short in 10-12 (n=12 / 21), the 10:00 hour
(+7R on 17), Asia (n=14), NY open (n=8), anything per hour, and the per-session TP splits below n=30.
Bottom line: VMap is not yet a trading edge. It is a lower-volume, lower-drawdown version of CRT Pro
that is flat once the stop is 4 pts; the one new idea worth testing is the EMA-distance cap.
