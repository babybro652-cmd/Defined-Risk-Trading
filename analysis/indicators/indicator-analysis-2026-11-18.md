# Indicator analysis, 11/18/2026

Private analysis (indicator names are fine here; never in public posts). Read-only: no sheet was edited.
Script: `indicator_analysis.py` (run `python3 indicator_analysis.py --1m DIR --2m DIR --5m DIR` with folders
of Yahoo ES=F JSON, or with no arguments to reuse the cached bars). Full tables:
`out/indicator-analysis-tables-2026-11-18.md` (ambiguous coarse bars counted as losses) and
`out/indicator-analysis-tables-2026-11-18-amb-skipped.md` (ambiguous left out). Per-trade bar scores:
`data/bar_scores_2026-11-18.csv`. Bars are now cached in `data/es_bars_{1m,2m,5m}.csv.gz`, so later runs keep
history that Yahoo drops after 30-60 days.

Builds on `vmap-analysis-2026-11-08.md`, `indicator-comparison-2026-10-22.md`, `divsr-vs-vmap-2026-10-22.md`,
`../crt-pro-2026-10-04.md` and `../crt-forward-test-2026-10-*.md`.

## Plain-English summary

**Almost nothing new to score.** Since the 11/8 report the sheets got 3 days of rows (11/11-11/13): 6 CRT Pro
trades, 4 VMap trades, 31 Forward Test rows (2 BUY/SELL trades). Logging stopped again on Friday 11/13, so the
newest rows are:

| Sheet | Newest row | Gap |
|---|---|---|
| CRT Trade Tracker, CRT Pro Trades | 11/13 15:57 ET | none since (Mon 11/16-Wed 11/18 missing) |
| CRT Trade Tracker, CRT Pro VMap | 11/13 15:20 ET | same |
| CRT Trade Tracker, CRT Pro Log (raw webhook) | 11/13 15:58 ET | same; 11/12 21:47 and 22:04 were webhook tests |
| CRT Forward Test Log | #565, 11/13 5:30 CT (6:30 ET) | stopped before the NY open on 11/13 |
| CRT Setups Tracker | 9/28 setups, 9/30 setup run | dead for 7 weeks, 0 trades ever |

Before that, nothing was logged 10/24-11/10. Season to date there are 18 logged trading days for CRT Pro.
So this report is mostly a **season-to-date** re-score with Tim's current rules, not a read on new data.

What the season says, scored the way Tim trades now (NY 10:00-16:00, fixed 4 pt stop from entry, 8 pt
target, 1 ES, $5 round trip):

- **Best: Divergence signals entered at the label.** 83 signals in NY 10-4, 37% win, +9.8R, **+$1,548 on 1 ES**
  (+$19 a trade). With a 3.5 pt stop: +15.2R, +$2,248. Taking only the first 2 a day: 37 trades over 19 days,
  49% win, **+$3,178**, worst day -$410. It is the only signal family that is positive in all hours and in
  Tim's hours, under both ways of scoring the coarse bars. Not proven: +0.12R a trade with n=83 is about
  0.7 standard errors from zero, and inside the window it flips (NY AM +12R on 18 to 10/9, then -2R on 8;
  NY PM -11R then +11R).
- **CRT Pro longs in NY 10-4 are a lead.** 141 trades, central estimate +20R / +$3,294 at 4/8, positive in
  both halves (+15R to 10/9, +5R after). **CRT Pro shorts in NY 10-4 lose in both halves**: 147 trades,
  central -29R / -$6,533.
- **Worst: CRT Pro as a whole and VMap.** CRT Pro with its own stops lost -57.9R / -$12,050 on 1 ES over 816
  trades; in NY 10-4, -28.7R / -$5,840 on 288. On Tim's 4/8 bracket in NY 10-4 it is still about -9R /
  -$3,241 (central; range -$8,015 to +$1,825). VMap in NY 10-4: -13.8R / -$3,140 on 75 at 4/8, -7R / -$1,775
  on its own exits, negative in both halves. The 4 new VMap trades were all losses.
- **The 9:30-10:00 window**: too few trades to judge (CRT Pro 31, VMap 10, Div 16). Tim mostly watches then.
- **Div within 25 min does not help CRT Pro in Tim's hours**: 35 trades with a Div, 17% win, -17R at 4/8, vs
  253 without, -15.9R. On the Forward Test BUY/SELL it looks better (+5.0R on 28 vs -6.6R on 30 at 4/8;
  logged -1R vs -7R) but both sides are thin.
- **Exit rules (b)-(d) don't rescue anything.** On the 211 CRT Pro trades with 1m bars: actual -5.0R, BE after
  TP1 -10.3R, half at TP1 + BE -6.8R, full exit at TP1 -3.3R. The logged-only method says BE after TP1 is
  +60R season wide, but it ignores winners that touch BE first; the bar replay is the one to trust (same
  lesson as 10/4 and 11/8).
- **Stop size.** CRT Pro's own stops of 1 pt or less are the money pit: 195 trades, -50.2R. The few CRT Pro
  signals whose own stop is already 3.5-4 pts did badly (40 trades, 20% win, -6.1R; thin in NY, 22). A fixed
  4 pt stop survives only about half of the moves that later reach +8 (CRT Pro 52%, Div 52%, VMap 41%).

Sample sizes: every group under 20 trades is marked "(thin)" in the tables. Standard error on a 4/8 group is
about 1.45R / sqrt(n) per trade, so a group of 80 needs about +0.32R a trade (+26R total) to be clearly real.
**Nothing in this report clears that bar.**

## Three recommendations

1. **Get the alerts logging every day before any more indicator work.** 3 logged days in the last 26. The
   11/12 test webhook worked and real rows came 11/12-11/13, then stopped; check the TradingView alerts
   (CRT Pro, VMap, Forward Test) are active and not expired. Also check the Forward Test Div alert is on the
   1m chart: the 2 new Div rows (11/12, 11/13) sit on 15-minute marks with "valid until" 6 h 15 min later,
   unlike the earlier Div rows (odd minutes, 1m chart), so they may not compare. Retire or fix the CRT Setups Tracker (no data
   since 9/30).
2. **If Tim wants one indicator to watch in NY, make it the Divergence label, with his 3.5-4 pt stop and an
   8 pt target, first 2 trades of the day.** +$3,178 on 37 trades in the simulation, worst day -$410, never
   near the $1,000 cap. Treat it as a forward test, not an edge: it needs about 100 more NY trades to confirm.
3. **On CRT Pro, ignore shorts in NY and skip VMap.** CRT Pro NY shorts lost in both halves (-29R central on
   147); VMap lost in NY under every rule (-13.8R on 75). Keep logging CRT Pro longs in NY 10-4 as the one
   CRT Pro slice to test (+20R central on 141, both halves positive). Leave the indicator exits alone: BE and
   partial rules were worse on bars.

## How Tim's rules line up

| Rule | What the data says |
|---|---|
| NY only | CRT Pro at 4/8: Asia +18.6R (n=233), London -20.3R (239), NY 10-4 about -9R (288). Asia's gain is all after 10/10. Tim doesn't trade Asia, and this doesn't argue he should: it flips by half. Div: Asia +9.3R (147), NY 10-4 +9.8R (83). |
| No trades before 10 | 9:30-10 is thin for every indicator; no evidence either way. |
| Wait for the label | Div is scored from the label close; that is the version that is positive. |
| 3.5-4 pt stop | 3.5 vs 4 pts in NY 10-4: CRT Pro -3.8R vs -9.0R (central), Div +15.2R vs +9.8R, VMap -16.6R vs -13.8R. Small, noisy differences; both sizes sit inside his rule. |
| $1,000 max loss | At 1 ES and 4 pts a loss is $205. Taking every CRT Pro NY signal would have hit the cap on 9 of 16 days. Capping at 2 trades: worst day -$410 on every indicator. |
| 1-2 good trades | "2 max" beat "take everything" for every indicator (CRT Pro -$560 vs -$4,838; VMap +$260 vs -$4,340; Div +$3,178 vs +$1,622). |

## Method notes (read before using any number)

- **Bars.** Yahoo keeps 1m bars for 30 days (10/20 on), 2m for about 36 days (10/13 on) and 5m for 60 days
  (9/10 on). Each trade uses the finest bars that cover it: CRT Pro 4/8 scores are 200 on 1m, 257 on 2m,
  289 on 5m, 69 ambiguous.
- **Ambiguous coarse bars.** On a 2m/5m bar that touches both the stop and the target (or hits inside a first
  bar that started before the entry) the order is unknown. On the 240 tracker trades from 10/20 that have all
  three, every non-ambiguous coarse result matched 1m exactly; the ambiguous ones averaged -1.7 pts (2m) and
  -2.2 pts (5m) on 1m. "Central" figures score each ambiguous trade at that average; the tables also show the
  range from "count as a loss" to "leave out". Div and CRT tag entries on coarse bars enter at the close of
  the coarse bar that holds the signal (up to 4 min late), so they have almost no ambiguous trades but a
  slightly different entry than Tim would get.
- **Entry timing** (checked on 1m bars): entry = close of the bar before the logged minute, and the logged
  minute is the first live bar. The 10/22 and 11/8 scripts started one bar late; fixed here.
- **Forward Test Log** times are Central (+1 hour to ET). BUY/SELL actual is the logged result column
  (STOPPED -1, BE 0, TP1 +1, TP2 +2, TP3 +3); the indicator's stops are wide (often 10-20 pts), so its
  actual $ figures are large and should not be compared with the 4 pt bracket.
- **$ on 1 ES** = points x $50 minus $5 round trip. 4/8 R is in 4 pt units (3.5 pt units for 3.5/8).
- Exit rules (a)-(d) are replayed on 1m bars only for the trackers (coarse bars can't place a 1-2 pt stop);
  the Forward Test BUY/SELL trades (wide stops) also use 2m/5m bars.
- 4 CRT Pro rows (10/2, 10/12, 10/15, 10/21) and 1 VMap row (10/14) are still marked OPEN in the sheet and are
  left out.

## Tables

### A. Data

| Source | Closed | Dates | Since 11/8 | 4/8 bars (1m / 2m / 5m / ambiguous / none) |
|---|---|---|---|---|
| CRT Pro Trades | 816 (+4 open) | 9/30-11/13, 18 days | 6 | 200 / 257 / 289 / 69 / 1 |
| CRT Pro VMap | 144 (+1 open) | 10/2-11/13 | 4 | 41 / 50 / 34 / 19 / 0 |
| Forward Test BUY/SELL | 50 with a result, 58 entries | 9/22-11/12 | 2 | 5 / 17 / 35 / 1 / 0 |
| Forward Test Div rows | 365 | 9/21-11/13 | 2 | 27 / 95 / 238 / 1 / 4 |
| Forward Test CRT tags | 142 | 9/21-11/13 | 27 | 36 / 28 / 76 / 0 / 2 |
| CRT Setups Tracker | 0 trades | 9/28 | 0 | n/a |

### B. Season to date, Tim's 4/8 bracket (central estimate, 1 ES)

| Indicator | All hours n | All hours | NY 10-4 n | NY 10-4 | NY 10-4 $/trade | NY 10-4 range $ |
|---|---|---|---|---|---|---|
| CRT Pro | 815 | -9.2R, -$5,919 | 288 | -9.0R, -$3,241 | -$11 | -$8,015 .. +$1,825 |
| VMap | 144 | -16.8R, -$4,087 | 75 | -13.8R, -$3,141 | -$42 | -$4,575 .. -$1,705 |
| Fwd BUY/SELL | 58 | -1.1R, -$501 | 11 (thin) | +1.0R, +$145 | +$13 | same |
| **Div from label** | 361 | **+15.9R, +$1,373** | 83 | **+9.8R, +$1,548** | **+$19** | same |
| CRT tag (unfiltered) | 140 | -2.6R, -$1,212 | 41 | +1.0R, -$5 | $0 | same |

3.5 pt stop / 8 pt target, NY 10-4 (central): CRT Pro -3.8R / -$2,103 (288); VMap -16.6R / -$3,273 (75);
Fwd BUY/SELL -1.1R / -$255 (11, thin); Div +15.2R / +$2,248 (83); CRT tag -4.9R / -$1,055 (41).

The precise slice, 1m bars only (10/20-10/23 and 11/11-11/13): CRT Pro 200 trades -1.9R / -$1,388 (NY 10-4:
64, -7.0R / -$1,720); VMap 41, -2.9R / -$780; Div 27, +3.1R / +$490; CRT tag 36, +6.0R / +$1,020;
Fwd BUY/SELL 5 (thin), 0 wins.

### C. Indicator exit rules (a)-(d), replayed on 1m bars

| Indicator | n | (a) Actual | (b) BE after TP1 | (c) Half at TP1 + BE | (d) Full at TP1 | (a) $ net 1 ES |
|---|---|---|---|---|---|---|
| CRT Pro, all hours | 211 | -5.0R | -10.3R | -6.8R | -3.3R | -$4,568 |
| CRT Pro, NY 10-4 | 67 | -4.8R | -1.7R | -2.5R | -3.3R | -$1,998 |
| VMap, all hours | 41 | +3.0R | +2.0R | +2.3R | +2.6R | +$395 |
| VMap, NY 10-4 (thin) | 19 | -3.0R | -2.0R | -2.5R | -3.0R | -$695 |
| Fwd BUY/SELL (2m/5m too), all | 33 | -6.0R | -0.3R | +0.5R | +1.2R | -$4,815 |
| Fwd BUY/SELL, NY 10-4 (thin) | 10 | -3.0R | -2.6R | -2.4R | -2.3R | -$2,962 |

Season-wide actual (logged, all rows): CRT Pro 816 trades, 24% win, -57.9R, -$12,050 on 1 ES; NY 10-4: 288,
-28.7R, -$5,840. VMap 144, 23% win, -12.0R, -$3,120; NY 10-4: 75, -7.0R, -$1,775. Fwd BUY/SELL 50, -8.0R.
Logged-only (b)/(c)/(d) for CRT Pro, all rows: +60.2R / +10.8R / -38.5R. Optimistic (ignores BE shake-outs).

### D. By session (4/8 bracket, conservative = ambiguous counted as a loss; central in brackets where it differs; "c." = central $)

| Session | CRT Pro n | CRT Pro | VMap n | VMap | Div n | Div | CRT tag n | CRT tag |
|---|---|---|---|---|---|---|---|---|
| Asia | 233 | +18.2R (+18.6R), +$2,563 c. | 14 (thin) | -2.9R | 147 | +9.3R, +$1,128 | 50 | +5.2R |
| London | 239 | -25.9R (-20.3R), -$5,254 c. | 45 | +1.2R | 103 | +0.1R | 44 | -9.8R |
| NY open 9:30-10 | 31 | -1.0R (+3.2R) | 10 (thin) | -4.0R | 16 (thin) | +2.0R | 1 (thin) | -1.0R |
| NY AM 10-12 | 104 | -17.0R (-8.1R), -$2,147 c. | 34 | -10.0R | 26 | **+10.0R, +$1,870** | 13 (thin) | +5.0R |
| NY PM 12-4 | 184 | -15.9R (-0.9R), -$1,092 c. | 41 | -11.0R | 57 | -0.2R | 28 | -4.0R |
| After hours | 24 | -1.8R | 0 | | 12 (thin) | -5.8R | 4 (thin) | +2.0R |

Halves (central, to 10/9 vs 10/10 on): CRT Pro NY AM -8.6R (29) vs +0.4R (75); NY PM +2.1R (72) vs -3.0R
(112); Asia +1.7R (47) vs +16.9R (186); London +10.9R (66) vs -31.2R (173). Div NY AM +12.0R (18) vs -2.0R
(8); Div NY PM -11.0R (32) vs +10.8R (25). No session holds steady in both halves except CRT Pro's
negative London after 10/10 and VMap's negative NY.

Actual (indicator exits) by session, CRT Pro: Asia -15.7R (233), London -0.5R (239), NY open -5.2R (31),
NY AM -15.4R (104), NY PM -13.3R (184), after hours -8.8R (25). VMap: NY AM +2.0R (34), NY PM -9.0R (41),
London -5.0R (45).

### E. Long vs short (4/8, NY 10-4)

| Group | n | Conservative | Central | To 10/9 (central) | 10/10 on (central) |
|---|---|---|---|---|---|
| CRT Pro long | 141 | +10.4R | +20.0R, +$3,294 | +15.0R (53) | +5.0R (88) |
| CRT Pro short | 147 | -43.3R | -29.0R, -$6,533 | -21.4R (48) | -7.6R (99) |
| VMap long | 30 | +0.0R | | | |
| VMap short | 45 | -21.0R | | | |
| Div long (Bull) | 45 | +6.0R, +$975 | same | | |
| Div short (Bear) | 38 | +3.8R, +$572 | same | | |
| CRT tag long (thin) | 18 | -6.0R | same | | |
| CRT tag short | 23 | +7.0R, +$1,285 | same | | |

All hours, CRT Pro long +11.2R (402) vs short -54.6R (413), conservative. CRT Pro on its own exits shows the
same tilt in NY 10-4 (long -5.2R on 141, short -23.6R on 147). ES fell about 300 pts between mid-October and
11/13, and shorts still lost, so this is not just trend.

### F. Stop size (CRT Pro's own stop)

| CRT Pro own stop | n | Actual R | Actual $ 1 ES | NY 10-4 n | NY 10-4 actual | NY 10-4 at 4/8 |
|---|---|---|---|---|---|---|
| 1 pt or less | 195 | -50.2R | -$3,100 | 26 | -5.5R | +1.0R |
| 1.25-2 pts | 322 | +5.1R | -$1,510 | 91 | -11.4R | -12.9R |
| 2.25-3.25 pts | 184 | +8.5R | +$118 | 108 | -0.4R | -3.0R |
| 3.5-4 pts (Tim's size) | 40 | -6.1R | -$1,412 | 22 | -7.7R | -4.0R |
| 4.25-6 pts | 52 | -5.5R | -$1,548 | 33 | -0.3R | -12.0R |
| over 6 pts | 23 | -10.5R | -$4,652 | 8 (thin) | -3.4R | -2.0R |

VMap's stop is always 4 pts (144 trades, -12.0R actual).

Adverse move before +8 (NY 10-4, 120 min): CRT Pro 288 signals, 59% reach +8, median heat 3.75 pts, a 4 pt
stop survives 52% of them, 3.5 pts 46%. Div 83: 58% reach +8, median 3.75, 52% / 48%. VMap 75: 41% / 34%.
CRT tag 41: 50% / 35%.

### G. Signal type and Div within 25 minutes (4/8, conservative)

| Group | n | All hours | n | NY 10-4 |
|---|---|---|---|---|
| CRT Pro, Div pivot 0-25 min before | 120 | -20.7R | 35 | -17.0R (17% win) |
| CRT Pro, no Div | 695 | -22.6R | 253 | -15.9R |
| VMap, Div (thin) | 14 | -5.0R | 7 (thin) | -1.0R |
| VMap, no Div | 130 | -21.6R | 68 | -20.0R |
| Fwd BUY/SELL, Div | 28 | +5.0R, +$860 | 3 (thin) | 0R |
| Fwd BUY/SELL, no Div | 30 | -6.6R, -$1,475 | 8 (thin) | +1.0R |

Forward Test BUY/SELL on the logged result: with Div 22 trades, -1.0R; without 28, -7.0R (10/3 baseline: +3R
vs -3R). On CRT Pro's own exits, Div helps all hours (+5.0R on 120 vs -63.9R on 696) but not in NY 10-4
(-6.4R on 35 vs -22.4R on 253). Mixed signs: no filter to adopt.

Signal types at 4/8, NY 10-4 (central): Div label +9.8R (83), CRT tag +1.0R (41), Fwd BUY/SELL +1.0R (11,
thin), CRT Pro -9.0R (288), VMap -13.8R (75). VMap Setup A NY 10-4 -21.0R (60) conservative; Setup B +0.0R (15,
thin).

### H. Tim's day simulation (NY 10-4, 4/8, 1 ES, one position at a time, stop before -$1,000)

| Indicator | Variant | Days | Trades | Win % | R | $ net | Worst day | Days at the cap |
|---|---|---|---|---|---|---|---|---|
| CRT Pro | every signal | 16 | 145 | 29% | -20.6R | -$4,838 | -$850 | 9 |
| CRT Pro | 2 max | 16 | 32 | 31% | -2.0R | -$560 | -$410 | 0 |
| VMap | every signal | 14 | 68 | 24% | -20.0R | -$4,340 | -$835 | 4 |
| VMap | 2 max | 14 | 28 | 36% | +2.0R | +$260 | -$410 | 0 |
| Div from label | every signal | 19 | 68 | 38% | +9.8R | +$1,622 | -$820 | 2 |
| **Div from label** | **2 max** | 19 | 37 | 49% | **+16.8R** | **+$3,178** | -$410 | 0 |
| CRT tag | 2 max | 20 | 30 | 37% | +3.0R | +$450 | -$410 | 0 |
| Fwd BUY/SELL | any (thin) | 10 | 11 | 36% | +1.0R | +$145 | -$410 | 0 |

Coarse-bar ambiguous trades count as losses here, so CRT Pro and VMap are on the low side. "Done after a
win" (stop after the first winner) was worse than "2 max" for every indicator except CRT tag.

### I. Since 11/8 (all thin)

| Group | n | Actual | 4/8 |
|---|---|---|---|
| CRT Pro (11/13, NY PM) | 6 | 1 W / 5 L, -4.2R, -$530 | -3.0R, -$630 |
| VMap (11/13) | 4 | 0 W / 4 L, -4.0R, -$820 | -1.0R, -$220 |
| Fwd BUY/SELL (11/12) | 2 | 1 stop, 1 BE, -1.0R | -2.0R, -$410 |
| Div from label | 2 | | -2.0R |
| CRT tag (11/11-11/13) | 27 | | +6.0R, +$1,065 |

### J. What held and what changed since 11/8

- Held: VMap is flat to negative (now -12.0R on 144 vs -8.0R on 140); no exit rule beats leaving CRT Pro's
  exits alone; NY PM is weak for CRT Pro and VMap; CRT Pro's sub-1 pt stops are the worst bucket.
- Changed: this is the first pass on Tim's 8 pt target (2R) instead of 4/4; at 4/8 CRT Pro is near flat
  instead of clearly negative, and Div from the label is the best family (it was second to BUY/SELL at 4/4 on
  10/22). Forward Test BUY/SELL, the 10/22 leader at 4/4 (+8.3R on 54), is flat at 4/8 (-1.1R on 58) and
  lost -11.1R after 10/10.
- Logging: still broken. 3 logged days since 10/23.
