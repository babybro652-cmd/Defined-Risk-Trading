# FVG / IFVG tag test, 11/18/2026

Private analysis (indicator names are fine here; never in public posts). Read-only: no sheet was edited.
Tim, 11/18: "On the indicators, can you say if there was an fvg or ifvg." Follow-up, same day: "Test with a 6 point
stop."

- Script: `fvg_tag.py`. It reuses `indicator_analysis.py` (same signals, same entry timing, same bracket scorer)
  and the cached ES bars in `data/`.
- Full tables: `out/fvg-ifvg-tables-2026-11-18.md`. Every indicator, every view, both gap sizes, every tag group,
  with 4/8, 3.5/8, 6/8 and 6/12, 2-max-a-day, own exits, and the losers-that-flip count.
- Per-signal tags: `data/fvg_tags_2026-11-18.csv`.

## Plain-English answer

- **Div labels: an FVG or IFVG at the label looked better, but it isn't proven.**
  - 5m chart, NY 10-4, Tim's 4 pt stop / 8 pt target, 1 ES:
    - With an FVG or IFVG: 35 signals, 46% win, **+11.9R, +$2,200**.
    - Without: 46 signals, 33% win, -1.0R, -$430.
  - Same direction on all four views that have enough trades: 5m at 1 tick, 5m at 1 pt, 2m at 1 tick, 2m at 1 pt.
  - The gap is about +0.36R a trade, which is about 1 standard error. Too small a sample to call it real.
  - IFVG alone was the strongest tag: 16 signals (thin), 56% win, +9.9R, +$1,895.
  - Taking the first 2 a day:
    - Tagged signals only: 23 trades, +17.9R, +$3,460.
    - All Div signals: 36 trades, +16.9R, +$3,195.
    - So about the same money on 13 fewer trades.
- **CRT Pro longs: no clear help.**
  - 1m chart (10/20 on): with a tag 28 trades +11.0R, without 5 (thin) -5.0R.
  - 5m chart (whole season): it flips. With a tag 102 trades +1.4R, without 39 trades +9.0R. At a 1 pt gap: -8.6R
    on 85 vs +19.0R on 56.
  - CRT Pro's own exits point the other way again: tagged +13.9R, untagged -19.1R.
  - Signs that change with the chart and the scoring mean there's no filter here.
- **Other indicators:**
  - CRT Pro shorts lose with or without a tag.
  - VMap loses with or without a tag.
  - Forward Test BUY/SELL is too thin to read (11 NY trades).
  - CRT tags: 37 of 41 already have a tag, so nothing to split.
- **"FVG right after the entry" is hindsight.**
  - It splits winners from losers on every indicator. Example: Div +24.9R with one vs -14.0R without.
  - That's only because a gap in your direction needs price to move your way first.
  - The tradable version waits for that gap and enters at its close. It lost on Div (-11.0R on 59) and was mixed
    on CRT Pro.
- **Combined indicator: put it in as a LABEL now, not a filter.**
  - Show FVG / IFVG on the chart and log `fvg` / `ifvg` with each Div trade.
  - Re-test the Div + FVG/IFVG split when about 100 more NY Div trades are logged.
  - Don't filter CRT Pro longs on it.
- **6 pt stop (TEST only; Tim's rule is still a 3.5-4 pt stop):**
  - It doesn't change the FVG answer. Div tagged vs untagged at 6/8: +7.6R vs -1.7R. The same direction, a
    smaller gap.
  - It turns few losers into winners: 6 of 50 Div 4 pt losers (12%), 20 of 202 for CRT Pro (10%).
  - It lowers Div's R and $ at an 8 pt target. 6/12 on the first 2 a day made more $ than 4/8 (+$3,895 vs
    +$3,195), but at lower R (+13.6R vs +16.9R) and with more risk per trade.
  - Daily risk on 1 ES with 2 trades:
    - 2 stops at 6 pts = **$610** with fees.
    - At 4 pts: $410. At 3.5 pts: $360.
    - All are inside his $1,000 max.

## Definitions used (standard ICT, OHLC only)

- **Bullish FVG**:
  - On 3 consecutive candles, candle 3's low is above candle 1's high.
  - The gap runs from candle 1's high to candle 3's low.
- **Bearish FVG**:
  - Candle 3's high is below candle 1's low.
  - The gap runs from candle 3's high to candle 1's low.
- **Minimum gap**:
  - **1 tick (0.25 pt)** is the default and the headline.
  - **1 pt** is the variant; both are in the tables.
  - The 3 candles must be back to back, with no session break.
- **Filled**: price later trades through the whole gap.
  - Bull: a low at or below candle 1's high.
  - Bear: a high at or above candle 1's low.
- **IFVG (inverse FVG)**: an FVG that a later candle closes fully through, so it flips role.
  - A bearish FVG closed above becomes bullish support.
  - A bullish FVG closed below becomes bearish resistance.
  - It stays active until a close back through its far side, or 3x the age limit.
- **Known only after the fact**: an FVG counts only once its third candle has closed. An inversion counts only
  once its closing candle is done. No look-ahead, except the hindsight tag.

**Tags**, on the 1m chart (the main view), with 2m and 5m as further views:

- (a) `a_in`: an FVG in the trade's direction whose third candle closed in the 10 bars before entry. This is "the
  move into the entry". On 5m that's 50 minutes.
- (a) `a_out`: an FVG in the trade's direction formed in the 10 bars after entry, "the move out of the entry".
  HINDSIGHT, reported only as a label.
- (b) Entry inside or within 1 tick of an unfilled FVG in the trade's direction. Lookback: 240 bars on 1m, 150 on
  2m, 96 on 5m.
- (c) An active IFVG in the trade's direction within 1.5 pts of entry.
- **any** = (a_in) or (b) or (c), all known at entry. (d) **none** = not any.
- **conf** (extra): wait for the first FVG in the trade's direction after the signal (within 10 bars) and enter at
  the close of its third candle.

**Scoring**:

- NY 10:00-16:00 by entry time.
- Fixed stop from entry: 4 pts (headline) and 3.5 pts.
- Target 8 pts, 1 ES, $5 round trip, 120 min timeout.
- A 2m/5m bar that touches both levels is counted as the stop. That's the conservative read, the same as the day
  simulation on 11/18, so totals sit a little under that report's "central" figures.
- "2 max a day" = the first 2 signals of each day within that tag group, one position at a time.
- Own exits = the logged result (CRT Pro, VMap, Forward Test BUY/SELL).
- R is in stop units. Anything with n under 20 is marked thin. One standard error is about 1.45R/sqrt(n) a trade.

**Bars**: Yahoo ES=F, cached. 1m from 10/20, 2m from 10/13, 5m from 9/10. The 1m view covers only the 10/20-10/23
and 11/11-11/13 logged days: 63 CRT Pro NY signals, but only 4 Div. So the season-long read is the 5m view.

## Results, NY 10-4, 1-tick gap

### Div labels (5m view, 81 signals; all at 4/8: 38% win, +10.9R, +$1,770)

| Tag | n | Win % | R (avg) | $ 1 ES | 2 max a day |
|---|---|---|---|---|---|
| (a) FVG formed in the last 10 bars | 23 | 43% | +5.9R (+0.26) | +$1,060 | 19, +9.9R, +$1,880 |
| (b) Entry in an unfilled FVG | 4 (thin) | 25% | -1.0R | -$220 | |
| (c) IFVG within 1.5 pts | 16 (thin) | 56% | +9.9R (+0.62) | +$1,895 | 14, +11.9R, +$2,305 |
| **Any** | 35 | 46% | **+11.9R (+0.34)** | **+$2,200** | 23, +17.9R, +$3,460 |
| **(d) None** | 46 | 33% | -1.0R (-0.02) | -$430 | 32, +1.0R, +$40 |
| FVG after entry (hindsight) | 55 | 49% | +24.9R | +$4,700 | |
| No FVG after entry (hindsight) | 26 | 15% | -14.0R | -$2,930 | |
| Confirmation entry (conf) | 59 | 27% | -11.0R | -$2,495 | 32, -11.0R, -$2,360 |

Other views, any vs none:

| View | Any | None |
|---|---|---|
| 5m, 1 pt gap | +8.9R on 29 (+$1,630) | +2.0R on 52 (+$140) |
| 2m, 1 tick | +6.0R on 15 (thin) | +2.0R on 10 (thin) |
| 2m, 1 pt | +9.0R on 9 (thin) | -1.0R on 16 (thin) |
| 1m | 4 signals in all; not readable | |

Bull and Bear both lean the same way, both thin:

| Side | Any | None |
|---|---|---|
| Bull | +5.0R on 19 | +2.0R on 25 |
| Bear | +6.9R on 16 | -3.0R on 21 |

### CRT Pro longs (5m view, 141 signals; all at 4/8: 36% win, +10.4R, +$1,382)

| Tag | n | Win % | R (avg) | $ 1 ES | Own exits R |
|---|---|---|---|---|---|
| (a) FVG formed in the last 10 bars | 97 | 36% | +6.4R | +$802 | +14.6R |
| (b) Entry in an unfilled FVG | 7 (thin) | 57% | +5.0R | +$965 | +5.6R |
| (c) IFVG within 1.5 pts | 16 (thin) | 25% | -4.0R | -$880 | +3.4R |
| **Any** | 102 | 34% | **+1.4R (+0.01)** | -$222 | +13.9R |
| **(d) None** | 39 | 41% | **+9.0R (+0.23)** | +$1,605 | -19.1R |
| Confirmation entry (conf) | 86 | 30% | -10.5R | -$2,530 | |

Other views, any vs none:

| View | Any | None |
|---|---|---|
| 1m, 1 tick | +11.0R on 28 (46% win, +$2,060) | -5.0R on 5 (thin) |
| 1m, 1 pt | +11.0R on 22 | -5.0R on 11 (thin) |
| 2m, 1 tick | +4.0R on 56 | -3.0R on 15 (thin) |
| 2m, 1 pt | +8.0R on 43 | -7.0R on 28 |
| 5m, 1 pt | -8.6R on 85 | +19.0R on 56 |

On the same 10/13-11/13 trades, the 5m tag splits much less: +1.0R on 56 vs 0.0R on 15. So the 1m/2m edge
isn't seen on 5m, and the full-season 5m split runs the other way. There's no consistent sign.

2 max a day, CRT Pro longs: -9.6R with a tag (32 trades) vs +6.0R without (24). The first-2 rule already hurts
CRT Pro longs (-8.0R on 32 vs +10.4R taking all 141), so this slice isn't a good test.

### Everything else (5m view, 1 tick, 4/8)

| Indicator | NY n | Any: n, win, R, $ | None: n, win, R, $ |
|---|---|---|---|
| CRT Pro, all | 288 | 211, 30%, -23.6R, -$5,768 | 77, 30%, -9.3R, -$2,248 |
| CRT Pro shorts | 147 | 109, 26%, -25.0R, -$5,545 | 38, 18%, -18.3R, -$3,852 |
| VMap | 75 | 60, 27%, -12.0R, -$2,700 | 15 (thin), 13%, -9.0R, -$1,875 |
| Fwd BUY/SELL | 11 | 8 (thin), 50%, +4.0R, +$760 | 3 (thin), 0%, -3.0R, -$615 |
| CRT tag | 41 | 37, 38%, +5.0R, +$815 | 4 (thin), 0%, -4.0R, -$820 |

How often the tag fires (NY, 5m, 1 tick):

| Indicator | (a) | (b) | (c) | Any |
|---|---|---|---|---|
| CRT Pro | 69% | 3% | 12% | 73% |
| Div | 28% | 5% | 20% | 43% |
| VMap | 80% | 3% | 7% | 80% |
| CRT tag | 83% | 0% | 24% | 90% |

On 1m at 1 tick, 81-89% of CRT Pro signals have one. 1-tick gaps are common on 1m; the 1 pt variant cuts them by
about a quarter.

(b) "entry inside an unfilled FVG" almost never fires (2-5%). Most of these signals are reversals, so price is
coming out of the opposite side, not pulling back into a gap in the trade's direction.

## 6 pt stop test (TEST only, not Tim's rule)

NY 10-4, all signals, 1 ES, $5 round trip, conservative. The 6/12 bracket compares 6 pts at the same 2R as 4/8.

| Indicator | n | 4/8 | 3.5/8 | 6/8 | 6/12 |
|---|---|---|---|---|---|
| Div label | 81 | 38%, +10.9R, +$1,770 | 37%, +16.3R, +$2,445 | 47%, +6.0R, +$1,382 | 37%, +5.1R, +$1,120 |
| CRT Pro longs | 141 | 36%, +10.4R, +$1,382 | 33%, +11.6R, +$1,332 | 45%, +6.0R, +$1,082 | 36%, -0.3R, -$805 |
| CRT Pro shorts | 147 | 24%, -43.3R, -$9,398 | 21%, -46.6R, -$8,898 | 30%, -45.2R, -$14,298 | 25%, -38.0R, -$12,122 |
| CRT Pro, all | 288 | 30%, -32.9R, -$8,015 | 27%, -35.0R, -$7,565 | 37%, -39.3R, -$13,215 | 31%, -38.3R, -$12,928 |
| VMap | 75 | 24%, -21.0R, -$4,575 | 20%, -25.7R, -$4,875 | 35%, -14.3R, -$4,675 | 31%, -8.7R, -$2,988 |
| CRT tag | 41 | 34%, +1.0R, -$5 | 27%, -4.9R, -$1,055 | 44%, +0.0R, -$192 | 37%, -2.4R, -$930 |
| Fwd BUY/SELL | 11 (thin) | 36%, +1.0R, +$145 | 27%, -1.1R, -$255 | 45%, +0.7R, +$145 | 36%, +1.0R, +$245 |

### First 2 a day, $1,000 cap

| Indicator | 4/8 | 6/8 | 6/12 | Worst day 4 pt / 6 pt |
|---|---|---|---|---|
| Div | 36, 50%, +16.9R, +$3,195 | 36, 53%, +7.6R, +$2,095 | 36, 47%, +13.6R, +$3,895 | -$410 / -$610 |
| CRT Pro longs | 32, 25%, -8.0R, -$1,760 | 32, 34%, -6.3R, -$2,060 | 32, 34%, +0.1R, -$122 | -$410 / -$610 |
| CRT Pro, all | 32, 31%, -2.0R, -$560 | 32, 41%, -1.7R, -$660 | 32, 34%, +1.3R, +$240 | -$410 / -$610 |
| VMap | 28, 36%, +2.0R, +$260 | 28, 43%, -0.0R, -$140 | 28, 39%, +4.2R, +$1,122 | -$410 / -$610 |
| CRT tag | 30, 37%, +3.0R, +$450 | 30, 43%, +0.3R, -$50 | 29, 34%, +0.2R, -$82 | -$410 / -$610 |

### Losers that become winners at 6 pts

These are trades that lost at the 4 pt stop and hit +8 with a 6 pt stop. None of the 4/8 winners lose at 6/8.

| Indicator | 4 pt losers | Win at 6/8 | 3.5 pt losers that win at 6/8 |
|---|---|---|---|
| Div | 50 | 6 (12%) | 7 of 51 |
| CRT Pro, all | 202 | 20 (10%) | 28 of 210 |
| CRT Pro longs | 90 | 11 | 15 of 94 |
| CRT Pro shorts | 112 | 9 | 13 of 116 |
| VMap | 57 | 8 | 11 of 60 |
| CRT tag | 27 | 3 | 6 of 30 |
| Fwd BUY/SELL | 7 | 1 | 2 of 8 |

**Daily risk** on 1 ES, if both trades stop out:

- 6 pts: 2 x (6 x $50 + $5) = **$610**.
- 4 pts: $410. 3.5 pts: $360.
- All are well inside the $1,000 max. The worst simulated day matched these numbers.

**Reading:**

- The wider stop buys a higher win rate: Div 38% to 47%, CRT Pro 30% to 37%.
- But each loss costs 1.5x as much, and only about 1 loser in 10 flips. So at an 8 pt target the R drops for every
  indicator but VMap (still negative).
- At 6/12 (same 2R), Div on the first 2 a day made the most money: +$3,895. But that's 36 trades, with a lower R
  than 4/8 and $200 more risk a day. That's not a reason to change the rule.

**FVG answer at 6 pts.** Div, 5m, 1 tick, any vs none:

- 6/8: +7.6R, +$2,112 on 35 vs -1.7R, -$730 on 46.
- 6/12: +4.0R, +$1,012 vs +1.1R, +$108.

CRT Pro longs, 5m, 6/8: +3.0R on both sides (102 vs 39). On 1m: +7.0R on 28 vs -5.0R on 5 (thin).

So the wider stop doesn't change the answer: Div leans the same way, and CRT Pro longs stay mixed.

## What goes in the combined indicator

1. **Label, not filter.**
   - Draw unfilled FVGs and IFVGs.
   - Add "FVG" / "IFVG" to the Div entry label.
   - Send `fvg` / `ifvg` in the alert JSON, so every logged Div trade carries the tag.
   - Volume Bubbles ES does this from 11/18 (pivot tags and alerts; see `pine/README.md`).
2. **Re-test as a Div filter** after about 100 more NY Div trades.
   - To be real, the split needs to hold at roughly +0.3R a trade on 100+ trades.
   - It's about 1 standard error now. IFVG is the sub-tag to watch.
3. **Don't use it on CRT Pro longs, or as a confirmation entry.**
   - CRT Pro longs: the signs change between charts.
   - Confirmation entry (waiting for the gap): it lost on Div and was mixed on CRT Pro.
4. Keep the 3.5-4 pt stop. The 6 pt test doesn't beat it on R for the signals that matter (Div, CRT Pro longs).
