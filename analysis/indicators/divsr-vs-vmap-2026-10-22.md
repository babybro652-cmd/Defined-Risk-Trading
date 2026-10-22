# CRT DIV SR vs CRT Pro VMap, 10/22/2026

Tim asked which of the two is performing better and which entry type (A or B) is better.
Read-only: no sheet was edited. Full tables: `out/divsr-vs-vmap-tables-2026-10-22.md`.
Script: `divsr_vs_vmap.py` (reuses `compare_indicators.py`; run
`python3 divsr_vs_vmap.py <folder of Yahoo ES=F 1m JSON>`).

## What each indicator's entries are

- **CRT DIV SR** (`indicators/CRT-Divergence-SR.pine`, logs to the CRT Forward Test Log). It has
  **no A/B setups**. Three entry types:
  - **BUY/SELL**: 15m CRT sweep at a pivot S/R level with a same-side RSI divergence in the last
    25 bars. Own levels: entry = candle-3 close, SL beyond the sweep + 0.15 ATR (median 10 pts),
    TP1-3 = 1/2/3R, SL to BE at TP1.
  - **Div**: RSI divergence label (entered at the label close, 5 bars after the pivot). No stop or
    target of its own, so 4/4 only.
  - **CRT tag**: CRT pattern that failed the confluence filter. No levels, 4/4 only.
- **CRT Pro VMap** (`pine/crt-pro-vmap-es.pine`, "CRT Pro VMap" tab). **Tim's "A or B" = these:**
  - **Setup A**: a CRT Pro signal the volume map agrees with (sweep wick through a thin zone or the
    POC, or a shelf reclaim; skips mid-shelf entries and entries with under 3.5 pts to the POC).
  - **Setup B**: a POC reaction (touch within 1 pt, close more than 1 pt away) in the CRT bias
    direction, inside the session windows.
  - Own levels: 4 pt hard stop, TP1 at the POC (or 1R), final target at the untaken session
    high/low (or 3R). TP hits don't move the stop.

## Data and method

- Refreshed from the sheets 10/22: VMap has 4 new rows (10/22 00:47-05:13), so **120 closed**
  (85 A, 35 B), 10/2-10/22 (10/3-10/7 empty, TradingView lapsed). Forward Test Log #1-#534.
- Replayed on Yahoo ES=F 1m bars, 9/22 19:25 to 10/22 05:36 ET (29,268 bars). Same conventions
  as `indicator-comparison-2026-10-22.md`: 4/4 = 4 pt stop and target, stop first on a bar that
  touches both, 60 min timeout; $ = 2 ES at $100/pt minus $10 a trade.
- "Own" = the indicator's logged result (VMap R is already in 4 pt units). DIV SR BUY/SELL own R
  is in units of its wide stop, so its $ per R is about 2.5x VMap's.
- **Tim's rules** = NY 9:30-16:00, first 2 trades per day, one position at a time.
- Same-date comparison restricts DIV SR to 10/2-10/22 (VMap's dates).

## 1. Head to head, same dates (10/2-10/22)

**Own stops/targets**

| Entry type | Split | n | Win % | Avg R | Total R | $ 2 ES net | Exp $ | Max DD | Losing streak |
|---|---|---|---|---|---|---|---|---|---|
| VMap all | All | 120 | 24% | -0.03 | -4.0R | -$2,800 | -$23 | 17.0R | 13 |
| VMap A | All | 85 | 26% | +0.04 | +3.0R | +$350 | +$4 | 9.0R | 9 |
| VMap B | All | 35 | 20% | -0.20 | -7.0R | -$3,150 | -$90 | 10.0R | 8 |
| DIV SR BUY/SELL | All | 26 | 23% | -0.27 | -7.0R | -$4,910 | -$189 | 7.0R | 4 |
| VMap A | NY | 55 | 25% | +0.02 | +1.0R | -$150 | -$3 | 8.0R | 6 |
| VMap B | NY | 13 | 31% | +0.23 | +3.0R | +$1,070 | +$82 | 4.0R | 4 |
| DIV SR BUY/SELL | NY | 5 | 40% | 0.00 | 0.0R | +$1,600 | +$320 | 1.0R | 1 |
| VMap all | 10-12 | 27 | 30% | +0.19 | +5.0R | +$1,730 | +$64 | 6.0R | 5 |
| VMap all | Tim's rules | 22 | 41% | +0.64 | +14.0R | +$5,380 | +$245 | 4.0R | 4 |
| DIV SR BUY/SELL | Tim's rules | 5 | 40% | 0.00 | 0.0R | +$1,600 | +$320 | 1.0R | 1 |

**Fixed 4/4**

| Entry type | Split | n | Win % | Avg R | Total R | $ 2 ES net | Exp $ | Max DD | Losing streak |
|---|---|---|---|---|---|---|---|---|---|
| VMap all | All | 120 | 45% | -0.07 | -8.6R | -$4,650 | -$39 | 17.5R | 4 |
| VMap A | All | 85 | 45% | -0.07 | -5.6R | -$3,100 | -$36 | 13.6R | 4 |
| VMap B | All | 35 | 46% | -0.09 | -3.0R | -$1,550 | -$44 | 9.0R | 7 |
| **DIV SR BUY/SELL** | All | 30 | 57% | +0.10 | +2.9R | +$850 | +$28 | 4.0R | 3 |
| DIV SR Div | All | 203 | 51% | +0.04 | +7.8R | +$1,070 | +$5 | 18.9R | 7 |
| DIV SR CRT tag | All | 71 | 37% | -0.26 | -18.6R | -$8,135 | -$115 | 22.6R | 8 |
| VMap A | NY | 55 | 36% | -0.25 | -14.0R | -$6,150 | -$112 | 16.0R | 4 |
| VMap B | NY | 13 | 54% | +0.08 | +1.0R | +$270 | +$21 | 4.0R | 3 |
| DIV SR BUY/SELL | NY | 6 | 67% | +0.33 | +2.0R | +$740 | +$123 | 1.0R | 1 |
| DIV SR Div | NY | 57 | 51% | +0.02 | +1.0R | -$170 | -$3 | 9.0R | 5 |
| VMap all | 10-12 | 27 | 41% | -0.19 | -5.0R | -$2,270 | -$84 | 8.0R | 5 |
| DIV SR BUY/SELL | 10-12 | 3 | 100% | +1.00 | +3.0R | +$1,170 | +$390 | 0 | 0 |
| DIV SR Div | 10-12 | 13 | 46% | -0.08 | -1.0R | -$530 | -$41 | 3.0R | 3 |
| VMap all | Tim's rules | 22 | 55% | +0.09 | +2.0R | +$580 | +$26 | 6.0R | 4 |
| VMap A | Tim's rules | 21 | 48% | -0.05 | -1.0R | -$610 | -$29 | 5.0R | 3 |
| VMap B | Tim's rules | 13 | 54% | +0.08 | +1.0R | +$270 | +$21 | 4.0R | 3 |
| **DIV SR BUY/SELL** | Tim's rules | 6 | 67% | +0.33 | +2.0R | +$740 | +$123 | 1.0R | 1 |
| **DIV SR Div** | Tim's rules | 21 | 62% | +0.24 | +5.0R | +$1,790 | +$85 | 1.0R | 1 |
| DIV SR CRT tag | Tim's rules | 17 | 29% | -0.41 | -7.0R | -$2,970 | -$175 | 8.0R | 6 |

## 2. Stability (halves split at 10/15, VMap's median trade date)

| Entry type | Rule | First half | Second half |
|---|---|---|---|
| VMap all | own, all | 54: 20%, -10.0R, -$4,540 | 66: 27%, +6.0R, +$1,740 |
| VMap all | own, Tim's rules | 12: 25%, 0R, -$120 | 10: 60%, +14.0R, +$5,500 |
| VMap A | own, NY | 26: 19%, -6.0R, -$2,660 | 29: 31%, +7.0R, +$2,510 |
| VMap B | own, NY | 6: 17%, -2.0R, -$860 | 7: 43%, +5.0R, +$1,930 |
| VMap A | 4/4, NY | 26: 31%, -9.0R, -$3,860 | 29: 41%, -5.0R, -$2,290 |
| VMap B | 4/4, NY | 6: 17%, -4.0R, -$1,660 | 7: 86%, +5.0R, +$1,930 |
| DIV SR BUY/SELL | own, all | 13: 15%, -6.0R, -$3,730 | 13: 31%, -1.0R, -$1,180 |
| **DIV SR BUY/SELL** | 4/4, all | 15: 53%, -0.1R, -$200 | 15: 60%, +3.0R, +$1,050 |
| **DIV SR BUY/SELL** | 4/4, Tim's rules | 3: 67%, +1.0R, +$370 | 3: 67%, +1.0R, +$370 |
| **DIV SR Div** | 4/4, Tim's rules | 12: 58%, +2.0R, +$680 | 9: 67%, +3.0R, +$1,110 |
| DIV SR CRT tag | 4/4, Tim's rules | 10: 20%, -6.0R, -$2,500 | 7: 43%, -1.0R, -$470 |

VMap's whole edge under Tim's rules (+14R) comes from 10 trades after 10/15; before that it was
flat, and across all sessions it lost -$4,540 in the first half. DIV SR's BUY/SELL and Div label
at 4/4 under Tim's rules made money in both halves.

## 3. DIV SR full history (9/22-10/21)

| Entry type | Rule | n | Win % | Total R | $ 2 ES net | Max DD | Losing streak |
|---|---|---|---|---|---|---|---|
| BUY/SELL | own, all | 48 | 31% | -7.0R | -$9,280 | 10.0R | 4 |
| BUY/SELL | 4/4, all | 54 | 59% | +8.2R | +$2,760 | 4.0R | 3 |
| BUY/SELL | 4/4, NY / Tim's rules | 11 | 73% | +5.0R | +$1,890 | 1.0R | 1 |
| BUY/SELL | 4/4, 10-12 | 6 | 100% | +6.0R | +$2,340 | 0 | 0 |
| Div label | 4/4, all | 344 | 51% | +12.8R | +$1,685 | 18.9R | 7 |
| Div label | 4/4, Tim's rules | 35 | 66% | +11.0R | +$4,050 | 2.0R | 2 |
| CRT tag | 4/4, all | 106 | 42% | -14.2R | -$6,760 | 25.6R | 8 |

## 4. Verdict

**Better: CRT DIV SR, traded with the 4/4 bracket in NY (BUY/SELL and Div label entries).**
Same dates, Tim's rules: BUY/SELL 6 trades, 67%, +$740, max DD 1R; Div label 21 trades, 62%,
+5R, +$1,790, max DD 1R. Both made money in each half, and the full history agrees (BUY/SELL
73% in NY, Div label 66% / +$4,050 under Tim's rules). Its own levels lose (-7R, stops ~10 pts,
outside Tim's 3.5-4 rule), so the 4 pt stop is what makes it work. Skip CRT tags (-$2,970 under
Tim's rules, losing in both halves).

**VMap**: bigger raw number under Tim's rules with its own exits (+14R, +$5,380, 22 trades), but
all of it came after 10/15 (10 trades) and it was flat before; across all sessions it is -$2,800 at
its own exits and -$4,650 at 4/4. It is the better one at its own exits in the last week only. Keep it
logging; it hasn't earned live size yet.

**A vs B (VMap only; DIV SR has no A/B):**
- All sessions, own exits: **A +3R / +$350 (85)** vs B -7R / -$3,150 (35). A is the better setup
  around the clock (NY +1R, outside NY +2R).
- NY (Tim's hours): **B +3R / +$1,070 (13)** vs A +1R / -$150 (55) at own exits; at 4/4 B +$270
  vs A -$6,150. B looks better in NY, but on 13 trades, and B lost in NY before 10/15 (6 trades,
  -$860).
- A at 4/4 in NY lost in both halves (-14R total). If trading VMap in NY, don't put a 4/4 bracket
  on A; A needs its runner target.

## 5. How to trade DIV SR

1. NY 9:30-16:00 only. Take BUY/SELL first; Div label when no BUY/SELL (wait for the label).
2. 4 pt stop, 4 pt target, ignore the indicator's SL/TP lines.
3. First 2 trades a day, one at a time. One loss at 2 ES = $410; two = $820, inside the $1,000 cap.
4. No CRT tag entries.

## 6. Sample-size caveat

VMap has 120 trades but only 68 in NY, 22 under Tim's rules, and 13 B trades in NY. DIV SR
BUY/SELL has 6 NY trades on these dates (11 full history). Every NY or 10-12 split here is a lead,
not proof. A 20-trade sample with 60% wins could be a 45% system by chance. Re-run after 2 more
weeks of logging (`divsr_vs_vmap.py`), especially for VMap B and the post-10/15 VMap run.
