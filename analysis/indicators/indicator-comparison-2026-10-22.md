# Indicator comparison, 10/22/2026

All indicators with logged data, scored on the same terms. Read-only: no sheet was edited.
Full tables (every split, exit rule and stop-size test): `out/tables-2026-10-22.md`.
Script: `compare_indicators.py` (rerun: export the tabs to `data/`, download Yahoo ES=F 1m bars to a
folder, `python3 compare_indicators.py <bars folder>`).

## Sources and method

| Indicator | Sheet / tab | Rows used |
|---|---|---|
| CRT Pro ES (primary) | CRT Trade Tracker, "CRT Pro Trades" | 702 closed, 9/30-10/21 (3 open) |
| CRT Pro VMap (TEST) | CRT Trade Tracker, "CRT Pro VMap" | 116 closed, 10/2-10/21 (1 open) |
| CRT + Divergence | CRT Forward Test Log, "Untitled" | #1-#533, 9/21-10/21: 56 BUY/SELL, 362 Div, 115 CRT tags |
| CRT Setups | CRT Setups Tracker | **0 trades**; 4 setup rows on 9/28 04:00-04:31, nothing since |
| Tim's hand trades | "Tim Trades" | 3 (kept out of indicator stats; see the end) |

- Times in ET. The Forward Test Log is Central, so +1 hour. Sessions (ET): Asia 18:00-03:00,
  London 03:00-09:30, NY open 9:30-10:00, **NY 10-12 (learning window)**, NY PM 12:00-16:00,
  After hours 16:00-18:00.
- Outcomes replayed on Yahoo ES=F 1-minute bars (9/22 19:25 to 10/21 20:13 ET, 28,715 bars).
  Replaying CRT Pro's own SL/TP3/EMA exits on bars gives -57.1R vs the logged -59.5R (699 trades),
  so the bars match the tracker.
- **Tim's rule (4/4)** = 4 pt stop, 4 pt target from the indicator's entry, stop first if one bar
  touches both, timeout at 60 minutes. R in 4 pt units. Div = entry at the label (close of the bar
  5 bars after the pivot). CRT tag = entry at the tag. BUY/SELL and CRT Pro = their logged entry.
- **$ at 2 ES** = points x $100 minus $10 round trip per trade (net). Win % counts any trade that
  closed positive (timeouts included).
- Alternative exits (TP-then-SL rows): (b) stop to BE after TP1, (c) half at TP1 + rest to BE,
  (d) full exit at TP1, replayed bar by bar.

## 1. Side by side

| Indicator | Signals | Win % | Avg R | Total R | $ 2 ES net | Exp $/trade | Max DD | Best / worst streak |
|---|---|---|---|---|---|---|---|---|
| CRT Pro, actual exits | 702 | 23.2% | -0.085 | **-59.5R** | **-$22,045** (gross -$15,025) | -$31 | 84.0R / $25,385 | 5 / 17 |
| CRT Pro, 4/4 | 702 | 48.1% | -0.026 | -18.6R | -$14,445 | -$21 | 36.8R | 7 / 9 |
| VMap, actual (already a 4 pt stop) | 116 | 23.3% | -0.069 | -8.0R | -$4,360 | -$38 | 17.0R | 3 / 13 |
| VMap, 4/4 | 116 | 43.1% | -0.109 | -12.6R | -$6,210 | -$54 | 17.5R | 4 / 4 |
| CRT + Div BUY/SELL, logged | 48 closed | 31.3% | -0.146 | -7.0R | n/a (stops 10 pts median) | | 10.0R | 3 / 4 |
| **CRT + Div BUY/SELL, 4/4** | 54 | **59.3%** | **+0.153** | **+8.3R** | **+$2,760** | **+$51** | 4.0R / $1,660 | 4 / 3 |
| CRT + Div, Div from label, 4/4 | 343 | 51.0% | +0.034 | +11.8R | +$1,295 | +$4 | 18.9R | 5 / 7 |
| CRT + Div, CRT tag, 4/4 | 106 | 42.5% | -0.134 | -14.3R | -$6,760 | -$64 | 25.6R | 5 / 8 |
| CRT Setups | 0 | | | | | | | |

TP hit rates: CRT Pro TP1 42% / TP2 27% / TP3 17%; VMap 44% / 30% / 23%; CRT + Div BUY/SELL
TP1 52% / TP2 2% / TP3 0% (the indicator trails or replaces the trade before TP2).

**Alternative exits** (bar replay, total R)

| | (a) Actual | (b) BE after TP1 | (c) Half at TP1 + BE | (d) Full at TP1 | TP-then-full-SL rows: actual / b / c / d |
|---|---|---|---|---|---|
| CRT Pro (699) | -57.1R | -63.5R | -75.7R | -87.9R | 85 rows: -85 / -20 / +12.5 / +45R |
| VMap (116) | -8.0R | -30.0R | -22.0R | -14.1R | 24 rows: -24 / -1 / +10.5 / +22R |
| CRT + Div BUY/SELL (54, held to SL/TP3) | | +0.5R | +1.4R | +2.2R | |

The alternative exits rescue the TP-then-SL rows, but they cut more TP3 winners than they save
(CRT Pro and VMap get worse under every one). Same answer as the 10/4 bar check: no exit rule fixes
CRT Pro. Its stops are the issue: median 1.5 pts, 412 of 702 under 2 pts, only 32 inside 3.5-4.

## 2. Sessions, 10-12 window, direction

4/4 $ net at 2 ES (actual R in brackets for CRT Pro and VMap).

| Group | CRT Pro | VMap | BUY/SELL | Div label | CRT tag |
|---|---|---|---|---|---|
| Asia | 200: 50.5%, +$675 (-9.3R) | 11: 18%, -$1,960 | 22: 55%, +$130 | 137: 52%, +$1,930 | 36: 44%, -$1,610 |
| London | 202: 52.0%, +$430 (-14.2R) | 37: 57%, +$1,630 | 20: 60%, +$1,150 | 98: 54%, +$2,220 | 34: 44%, -$1,590 |
| NY open 9:30-10 | 27: 33%, -$3,870 | 5: 60%, +$350 | 2: 2/2, +$780 | 16: 63%, +$1,440 | 1: 0/1 |
| **NY 10-12** | 88: 44%, -$4,880 (-6.4R) | 27: 41%, -$2,270 (+5R) | **6: 6/6, +$2,340** | 24: 58%, +$1,360 | 11: 45%, -$510 |
| NY PM 12-4 | 163: 47%, -$5,130 | 36: 36%, -$3,960 | 3: 0/3, -$1,230 | 57: 42%, -$4,170 | 22: 36%, -$2,620 |
| Outside 10-12 | 614: 49%, -$9,565 | 89: 44%, -$3,940 | 48: 54%, +$420 | 319: 50.5%, -$65 | 95: 42%, -$6,250 |
| Long | 347: 51%, +$555 | 51: 47%, -$1,485 | 33: 58%, +$970 | 188: 51%, -$855 | 51: 37%, -$5,735 |
| Short | 355: 45%, -$15,000 | 65: 40%, -$4,725 | 21: 62%, +$1,790 | 155: 51%, +$2,150 | 55: 47%, -$1,025 |

**Tim's day** (NY only, first 2 signals per day, 4/4, one trade at a time):

| | NY 9:30-4 | 10-12 only |
|---|---|---|
| CRT Pro | 26: 35%, -8R, -$3,460 | 24: 50%, 0R, -$240 |
| VMap | 22: 55%, +2R, +$580 | 20: 50%, 0R, -$200 |
| **BUY/SELL** | **11: 73%, +5R, +$1,890** | **6: 100%, +6R, +$2,340** |
| Div label | 35: 66%, +11R, +$4,050 | 22: 59%, +4R, +$1,380 |
| CRT tag | 27: 37%, -7R, -$3,070 | 11: 45%, -1R, -$510 |

## 3. Out-of-sample check (rule picked on the earlier rows, tested on the later rows)

| Rule | Earlier | Later | Held? |
|---|---|---|---|
| **BUY/SELL at 4/4 (all)** | before 10/8: 27, 59%, +$1,480 | 10/8 on: 27, 59%, +$1,280 | **Yes** |
| BUY/SELL with a same-side Div in the 25 min before | to 10/9: 16, 81%, +$3,590 | 10/11 on: 11, 55%, +$40 | Faded |
| BUY/SELL in NY | 7, 86%, +$1,930 | 4, 50%, -$40 | Too few |
| Div NY AM 9:30-12 | 24, 67%, +$2,960 | 16, 50%, -$160 | Faded |
| Div NY PM 12-4 (skip) | 32, 34%, -$4,320 | 25, 52%, +$150 | Faded |
| CRT Pro stop >= 2 pts | 9/30-10/2: 72, +4.9R | 10/8 on: 218, -21.1R | No |
| CRT Pro London + 10-12 at 4/4 (10/4 idea) | 61, +$590 | 229, -$5,040 | No |
| CRT Pro long at 4/4 | 66, 61%, +$4,615 | 281, 49%, -$4,060 | No |
| CRT Bear tag | 28, 57%, +$1,670 | 27, 37%, -$2,695 | No |

Every filter found on 10/4 and 10/11 shrank or reversed on the newer rows. The one result that
held is the plain one: the CRT + Div BUY/SELL signal with a 4 pt stop and 4 pt target, 59% in both
halves.

## 4. Column H, entry drawdown and stop size

- **Div rows:** H filled on 120 rows (#108-#293), all equal to G (0 ticks). That's built in: a
  length-5 pivot can't confirm if price breaks it before the label. From the label on bars, 62%
  move 4 pts in favor within an hour; the adverse move first is median 1.5 pts, 80th pct 3.75,
  90th 5.75. A 4 pt stop survives 81% of the moves that work. Stop grid (4 pt target): 2-3 pts
  +$4,820 to +$5,495, 3.5 pts -$455, 4 pts +$1,295, 5-8 pts about +$4,500. No stop size gives a
  clear edge: about $4-16 a trade.
- **CRT rows:** H filled on 2 of 115 (#291 held, 16 ticks above the swept low; #292 held, 22 ticks
  below the swept high; bars agree within 2 ticks). On bars: the sweep level held 60 min on 75%
  (80/106), but it sits a median 10.5 pts from the tag (quartiles 6.75-15), 7 of 106 within 4 pts.
  Drawdown before +4: median 2.25 pts, 80th pct 6, 90th 7.75. A 4 pt stop survives 68% of the
  moves that work. CRT tags lose at every stop from 2 to 8 pts.
- **BUY/SELL:** stop grid peaks at **4 pts** (+$2,760; 5-6 pts +$2,360 to +$2,610; 3.5 pts -$190).
- **Recommended stop: 4 pts** (top of Tim's 3.5-4 rule). 3.5 pts was worse than 4 on all three
  signal types; going wider than 4 adds nothing and breaks the rule.

## 5. Verdict

**Strongest: CRT + Divergence BUY/SELL with Tim's 4/4 bracket.** 54 trades, 59% win, +8.3R,
+$2,760 net on 2 ES, max drawdown 4R, and the only result that held from the first half of the data
to the second. Best in NY (11: 8 W / 3 L) and in 10-12 (6 of 6), both tiny. Its weakness is volume:
about 1 NY signal every 2 sessions.

Second: Div from the label in NY (Tim's-day version 35 trades, 66%, +$4,050), but the NY AM edge
faded from 67% to 50% in the newer rows, so treat it as a confirm, not a trade on its own.

**Weakest: CRT Pro ES (primary)**, by volume and $: 702 trades, 23% win, -59.5R, -$22,045 net,
17-loss streak. With Tim's 4/4 it's 48% and still -$14,445. NY only, it lost under every rule
(n=278). VMap (116): 23% win, -$4,360; its 10-12 actual (+5R, n=27) is too small to use.
CRT tags alone: 42.5%, -$6,760. CRT Setups: no trades to judge.

## 6. Rule changes the data supports

1. **Trade the CRT + Div BUY/SELL signal with a fixed 4 pt stop / 4 pt target, NY only.** The
   indicator's own stops (median 10 pts) lost -7R; the same signals at 4/4 made +8.3R, in both halves.
2. **Don't take CRT Pro or CRT tag entries on their own in NY.** CRT Pro NY: -27.8R actual,
   -$13,880 at 4/4 (278 trades). Skip 9:30-10:00 CRT Pro signals (27: 33% at 4/4, -$3,870).
   Use CRT Pro as context; keep it logging as a shadow test.
3. **One loss and done at 2 ES.** A 4 pt stop on 2 ES is $810 with costs, so a second loss breaks
   the $1,000 daily cap. Trade the second setup on 1 ES (or stop) after a loss.
4. Watch, not yet rules: Div in the 9:30-12 window as a confirm; avoid NY PM Divs (34% then 52%).

## 7. Data gaps

- **10/3-10/7: no rows anywhere** (TradingView lapsed 10/5, alerts back 10/8). 10/8 starts mid-day.
- **CRT Setups has never logged a trade**: 4 setup rows on 9/28, then nothing. The webhook alert
  likely wasn't re-created after the 9/28 setup or the 10/8 renewal. Needs Tim to re-create it.
- **Column H stopped at #293 (10/9).** 240 newer rows (10/11-10/21) have no H, including 161 Div and
  ~50 CRT rows. CRT H: 2 of 115. Notes (column R) also stop at #293. Column S is blank on all rows.
- 8 BUY/SELL rows have no result (#9, #91, #94, #138, #247, #384, #418, #488; mostly replaced by the
  next signal). Scored on bars only.
- 30 Forward Test rows (#1-#23 and 7 others) fall before 9/22 19:25 ET or in bar gaps: no bar score.
- Yahoo keeps 1m bars for 30 days; rows before 9/22 can no longer be re-scored.
- VMap row VM-A-20261014-0102-SHORT has been OPEN since 10/14 with TP1=TP2=TP3 (7858.5).
- Sample sizes: everything in the 10-12 window is n=6 to 88; BUY/SELL NY is 11. Any 10-12 or NY
  split under 30 trades is a lead, not a result.

## Tim's own trades (not in indicator stats)

"Tim Trades": 3 paper trades on 10/20, all 2 ES with a 4 pt stop: long 9:55 +30 pts (+$3,000),
short 1:44 PM stop (-$400), short 1:53 PM closed by hand +11.25 pts (+$1,125). +$3,725 gross,
2 W / 1 L. Three trades is too few to score against the indicators.

## Comparison tab

`apps-script/indicator-comparison.gs`: paste into the CRT Trade Tracker's Apps Script editor
(as a new file), run `addIndicatorComparison`. It adds or refreshes an "Indicator Comparison" tab
with the side-by-side table above. It writes only that tab.
