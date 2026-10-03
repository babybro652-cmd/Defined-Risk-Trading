# CRT Forward Test Log analysis, 10/3/2026

Source: CRT Forward Test Log (`1H9KSzv9C0hIhDuWjUCQKpKURv_kEkRE5CLlLV-kmofA`, tab "Untitled"),
rows #1 to #247 (9/21 to 10/2). Read only; the sheet was not edited. Log times are Central;
sessions below are ET (Central + 1h): Asia 18:00-03:00, London 03:00-09:30, NY AM 09:30-12:00,
NY PM 12:00-17:00. ES: 0.25 tick, $12.50/tick, $50/pt per contract.
Anything with n < 10 is tentative. Tim said more data is still going in.

## 1. Data status

| Type | Rows | H filled (valid) | Notes |
|---|---|---|---|
| Bull Div | 102 | 28 | 26 |
| Bear Div | 68 | 27 | 27 |
| CRT Bull (unfiltered) | 20 | 0 | 0 |
| CRT Bear (unfiltered) | 28 | 0 | 0 |
| BUY | 17 | n/a | n/a |
| SELL | 12 | n/a | n/a |
| Total | 247 | 55 | 53 |

H and notes start at #139 (9/28 evening). Everything before that is signal-only.

Rows to fix:
- **#140** (sheet line 141), Bull Div: H = 0, I = 30,940 ticks. Excluded. Needs a price (G is 7735).
- **#139** (line 140) is valid (H 7734, 16 ticks). If Jarvis's "#139/#140" meant sheet lines, it is the same single bad row. Its column S holds the text "7 mins" instead of a time.
- **Column S (Div Valid Until)** is blank on every other Div row, so the validity window can't be read from the sheet. This analysis used 25 minutes (25 bars on the 1-minute chart).
- **No result** on BUY/SELL #9, #91, #94, #138, #247 (blank O). Excluded from trade stats.
- **"TP1 HIT" is a live status, not a final result**, on #37, #81, #119, #200. Each is scored +1R by the sheet formula, but the final exit (TP2/TP3, BE or trail) is not recorded.
- **#223 and #224** notes have reversal times (20:25, 20:58) earlier than the signal (22:05, 22:45). Likely 22:25 and 22:58.
- **#245** note has no "Dropped to X" part, so no favorable move could be read. **#246** has no note.
- **#239**: the read of H = 7810.25 conflicts with the convention. The note says it dropped to 7796.25 first and only rallied to 7810.25 at 9:42 afterwards; that is the reversal, not adverse excursion before the move. H should stay 7808.75 (0 ticks) and 7810.25 belongs in the "reversed to" part.
- Pending reads #240 (7810.25), #243 (7782.25), #245 (7778.50), #246 (7773.75) already match the sheet (H = G).
- Minor: a few rows are out of time order (#3/#4, #124/#125, #141/#142, #190/#191).

## 2. Signal quality (Div rows with H and notes)

### Adverse excursion (column H)
| Type | n | Zero adverse | Median | 75th | 90th | Max |
|---|---|---|---|---|---|---|
| Bull Div | 28 | 27 | 0 | 0 | 0 | 16 ticks (4 pts, #139) |
| Bear Div | 27 | 27 | 0 | 0 | 0 | 0 |
| CRT Bull / Bear | 0 | | | | | |

54 of 55 rows show zero adverse move. This is built into the indicator, not an edge: the
Div ref price is the pivot low/high (`low[divPivotLen]`), logged at the pivot bar's time, and the
divergence is only confirmed 5 bars later (pivot length 5). A pivot can't confirm unless those
bars stayed on the right side of it. So column H measured from G will almost always read 0 and
can't size a stop. The usable risk data is in the notes (how often price came back through G).

### Favorable move and reversal (from column R notes, 52 parsed)
| | Bull Div (n=26) | Bear Div (n=26) |
|---|---|---|
| Median favorable move | 7.25 pts | 4.9 pts |
| 25th / 75th pct | 4.9 / 10.25 pts | 3.0 / 10.1 pts |
| Reached 2 pts | 24 (92%) | 25 (96%) |
| Reached 4 pts | 22 (85%) | 15 (58%) |
| Reached 8 pts | 10 (38%) | 9 (35%) |
| Reached 12 pts | 4 (15%) | 3 (12%) |
| Median reversal off the best price | 4.75 pts | 3.5 pts |
| Median share of the move given back | 76% | 93% |
| Later broke back through G | 8 of 25 (32%) | 9 of 25 (36%) |

Both combined: 37/52 (71%) reached 4 pts, 19/52 (37%) reached 8, 7/52 (13%) reached 12.

Caveat: the move is measured from the pivot price. A real entry happens 5 bars later, so
part of each move has already happened by the time the signal can be acted on. Treat these as
upper bounds.

**Stop and target read (tentative):** a stop a couple of ticks past the pivot survived the
initial move on 54/55 signals. About a third later broke the pivot, so a runner past TP1 needs
the stop at break-even. A 4 pt target is hit by most Bull Divs (85%) but only 58% of Bear Divs;
8 pts is a roughly one-in-three event for both.

## 3. Session breakdown (ET)

Signal counts, all 218 Div/CRT rows:

| Type | Asia | London | NY AM | NY PM |
|---|---|---|---|---|
| Bull Div | 41 | 26 | 14 | 21 |
| Bear Div | 28 | 19 | 7 | 14 |
| CRT Bull | 6 | 10 | 1 | 3 |
| CRT Bear | 7 | 10 | 4 | 7 |

Div favorable move by session (rows with notes; every cell is n < 12, all tentative):

| Type, session | n | Median pts | Reached 4 | Reached 8 | Broke G later |
|---|---|---|---|---|---|
| Bull Div, Asia | 10 | 6.6 | 8 | 4 | 1 |
| Bull Div, London | 5 | 4.0 | 3 | 0 | 3 |
| Bull Div, NY AM | 5 | 13.75 | 5 | 4 | 2 |
| Bull Div, NY PM | 6 | 6.9 | 6 | 2 | 2 |
| Bear Div, Asia | 11 | 3.0 | 3 | 0 | 5 |
| Bear Div, London | 6 | 6.1 | 4 | 2 | 2 |
| Bear Div, NY AM | 2 | 10.75 | 2 | 2 | 1 |
| Bear Div, NY PM | 7 | 10.5 | 6 | 5 | 1 |

Best looking: Bull Div NY AM (Tim's 10-12 window; 5/5 reached 4 pts, 4/5 reached 8) and Bear
Div NY PM (6/7 reached 4, 5/7 reached 8). Weakest: Bear Div in Asia (median 3 pts, 0/11 reached
8, 5/11 later broke the pivot) and Bull Div in London (0/5 reached 8, 3/5 broke). The two big
NY AM Bull Div failures (#213, #215) were the 10/1 selloff: both ran 14-24 pts first, then fell
28-43 pts off the high.

## 4. BUY/SELL trades

29 signals, 24 closed (5 blank). This indicator moves the stop to entry at TP1 and to TP1 at
TP2, so "STOPPED (BE)" = reached TP1 then back to entry (0R), "STOPPED (TRAIL)" = reached TP2
then back to TP1 (+1R). TP1/TP2/TP3 are 1R/2R/3R.

| | n | Win | BE | Loss | Total R | Avg R | Reached TP1 |
|---|---|---|---|---|---|---|---|
| All | 24 | 10 | 4 | 10 | 0R | 0.00 | 14 (58%) |
| BUY | 13 | 5 | 2 | 6 | -1R | -0.08 | 7 |
| SELL | 11 | 5 | 2 | 4 | +1R | +0.09 | 7 |
| Asia | 11 | 5 | 3 | 3 | +2R | +0.18 | 8 |
| London | 7 | 2 | 1 | 4 | -2R | -0.29 | 3 |
| NY AM | 5 | 3 | 0 | 2 | +1R | +0.20 | 3 |
| NY PM | 1 | 0 | 0 | 1 | -1R | -1.00 | 0 |

Results: 10 STOPPED, 4 STOPPED (BE), 6 STOPPED (TRAIL), 4 TP1 HIT (open status).
Win rate 42% on final R; 58% touched TP1. 4 trades hit TP1 and came back to entry; none hit TP1
and then took a full loss (the BE move prevents it).

Alternative exits (scored from Result values):
| Rule | Total R (24) |
|---|---|
| (a) Actual (BE at TP1, trail at TP2) | 0R |
| (b) Stop to BE after TP1 | 0R (same as actual; that is the built-in rule) |
| (c) Half off at TP1, rest to BE/trail | 0R (BE rows +0.5, TP1 HIT rows counted +0.5 floor) |
| (d) Full exit at TP1 | **+4R** |
| No stop management (CRT Pro style) | Not determinable: the log doesn't say how far TRAIL / TP1 HIT trades ran |

Full exit at TP1 wins here because every trade that reached TP1 banks 1R, and the 4 BE trades
turn from 0R into +1R. By session under full exit: Asia +5R, London -1R, NY AM +1R, NY PM -1R.

**Stop size:** median 9 pts ($450/contract), range 3 to 35 pts. Only 2 of 29 (two 3-pt
stops, #51 and #169) fit the course's 3.5-4 pt rule; 18 of 29 are wider than 8 pts. Widest:
#101 35 pts, #38 25, #188 21.5, #218 21, #241 17.75, #61 14.25, #194 13.75. Stops 8 pts and
under (n=10) and over 8 pts (n=14) both netted 0R, so the wide stops are not buying a better
win rate. At a fixed $ risk, a 35 pt stop means one-ninth the size of a 4 pt stop.

## 5. Confluence (same-direction Div before the BUY/SELL)

Every closed trade had a same-direction Div within 60 minutes, as the indicator requires.
Split by a Div within 25 minutes (the 25-bar window on the 1-minute chart):

| | n | Win | BE | Loss | Total R | Full exit at TP1 |
|---|---|---|---|---|---|---|
| Div within 25 min | 11 | 6 | 2 | 3 | **+3R** | +5R |
| No Div within 25 min | 13 | 4 | 2 | 7 | **-3R** | -1R |

Fresh divergence looks better, but n = 11 vs 13; a 6R swing could flip with a few trades.
Tentative. Column S being blank makes the exact window uncheckable from the sheet.

## 6. Takeaways

1. **Bank TP1.** Full exit at TP1 is the best of the four exit rules: +4R vs 0R actual over 24
   trades, and 14/24 reached TP1. This matches the 10/1 CRT Pro read that runners give back
   too much (Div moves give back a median 76-93% of their best price).
2. **Stops are too wide for the plan.** Median 9 pts; only 2 of 29 meet the 3.5-4 pt rule, and
   wide stops did no better. Consider a max-risk filter (skip or flag any signal with a stop over
   ~8 pts) in the indicator.
3. **Fresh divergence matters (tentative).** Trades with a same-direction Div in the last
   25 minutes: +3R; without: -3R.
4. **Session:** Asia trades carried the results (+2R actual, +5R full TP1 exit); London was
   negative (-2R, 2 wins in 7). For Div signals, Bull Div NY AM and Bear Div NY PM ran furthest;
   Bear Div in Asia rarely reached 4 pts and often broke the pivot, so it's a candidate to ignore.
   4 pt target: 85% of Bull Divs reach it, 58% of Bear Divs.
5. **Fix what H measures.** H from the pivot is 0 by construction (54/55). Log adverse/favorable
   from the bar where the Div actually confirms (5 bars after the pivot), or have the webhook
   write that bar's close as an entry price. Otherwise H can't size a stop.

## What more data is needed

- Div with notes: 52 now, 2-11 per type-by-session cell. About 20 per cell (roughly 150-200
  more noted Div rows, 1-2 weeks at the current pace) before session calls firm up.
- BUY/SELL: 24 closed. About 60-100 closed trades (3-4 more weeks) for a win rate within about
  +/-10%. Record final results on TP1 HIT rows and fill the 5 blanks.
- CRT Bull/Bear: 0 of 48 have H or notes; start filling them or drop them from the log.
- Column S needs to populate so the confluence window can be checked exactly.

Chart: `crt-forward-test-2026-10-03.png` (scratchpad, not committed).

## 7. Follow-up (10/3): opposite-Div exits and trading Divs directly

Assumptions for both parts:
- 1-minute chart, Div pivot length 5. The log's Div time and price are the **pivot** bar
  (`time[5]`, `low[5]`/`high[5]`), and the Div is only known 5 bars later.
- **Timing check from the notes (36 rows with times):** the first favorable leg peaked within
  5 minutes of the pivot on 27 of 36 (75%), median 3 minutes, median size 4 pts. So most of
  the visible move is over before the Div can be acted on. This drives both results below.
- A new BUY/SELL replaces the active trade in the indicator, so a trade's window ends at
  the next BUY/SELL.

### A. Exit on the next opposite Div (24 closed trades)

Rule: BUY exits on the next Bear Div, SELL on the next Bull Div, if the Div's pivot comes after
entry and confirms before the trade ended. The indicator's own BE-at-TP1 / trail-at-TP2 stop
stays on. Exit price: best = pivot (G); realistic A = pivot minus 35% of the entry-to-pivot
move; realistic B = pivot minus 4 pts (median first leg inside the 5-bar lag). R = pts / stop.

- 7 trades: no opposite Div before the trade ended (#37, #61, #89, #119, #146, #188, #200),
  actual stands.
- 5 trades: stop hit before the Div (an opposite Div or CRT tag beyond the stop printed first:
  #10, #121, #147, #153, #229), actual stands.
- 12 trades: Div exit possible. 2 of them (#101, #218, both full stops) have unverified order:
  the stop may have come first.

| Variant | Best (pivot) | Realistic A (35%) | Realistic B (4 pt) |
|---|---|---|---|
| (1) Full exit on opposite Div | +5.65R | +1.65R | +0.08R |
| (1) excluding #101/#218 | +3.85R | +0.05R | -1.42R |
| (2) Half at TP1 (if before Div), rest on Div, BE after TP1 | +4.24R | +1.62R | +0.09R |
| (2) excluding #101/#218 | +2.44R | +0.02R | -1.41R |
| Actual | 0R | | |
| Full exit at TP1 | +4R | | |

It helps the BE trades (#97, #173, #194) and cuts the two wide-stop losers (#101, #218),
but it exits the TRAIL winners early (#38, #64, #81, #203). Only the best case (exit at the
exact pivot, which can't be done) beats full exit at TP1. Realistic: about 0 to +1.7R, below
+4R. Verdict: opposite-Div exits don't add value over banking TP1.

### B. Trading Divs directly: TP 4 pts, SL 3.5 / 4 pts

52 Div rows with notes (H = G on all of them). Each was walked through its notes in order:
target first = win, stop first = loss, neither recorded = unresolved. Unresolved shown three
ways: best (scratch, 0), mark (closed at the last price in the notes, capped -SL..+4), worst
(full stop). Costs: MES $1.88, ES $5 round trip. Breakeven win rate: 4/4 = 54.7% MES,
51.3% ES; 4/3.5 = 51.7% MES, 48.0% ES.

**Realistic (timing-aware) entry:** price at confirmation = midpoint of the last noted price
before pivot+5 min and the next noted price; rows without times assume the first leg finished
before confirmation (the 75% base rate). 2 rows skipped (already back through the pivot).

| Filter, SL 4 | n | W / L / unresolved | Mark pts | ES $ (mark) | MES $ (mark) | Clears breakeven? |
|---|---|---|---|---|---|---|
| All | 50 | 9 / 9 / 32 | -32.6 | -$1,881 | -$257 | No |
| Bull only | 25 | 5 / 5 / 15 | -11.6 | -$706 | -$105 | No |
| Bear only | 25 | 4 / 4 / 17 | -21.0 | -$1,175 | -$152 | No |
| Bull NY AM (tentative) | 4 | 1 / 2 / 1 | -4.0 | -$220 | -$28 | No |
| Bear NY PM (tentative) | 7 | 2 / 1 / 4 | -2.3 | -$148 | -$24 | No (best case +$165 ES) |
| Excl Bear Asia | 40 | 7 / 9 / 24 | -34.0 | -$1,900 | -$245 | No |

SL 3.5: All 9 W / 10 L / 31 unresolved, mark -27.9 pts (-$1,644 ES, -$233 MES). Same picture.

**Optimistic (fixed lag, ignores timing):** entry = pivot +/- 2 pts, all noted moves counted
as after entry. SL 4: All 29 W / 1 L / 19 unresolved, mark +87.5 pts (+$4,130 ES, +$345 MES);
Bull NY AM 5/5 wins; Excl Bear Asia 27 W / 0 L. With a 4 pt lag: All 19 W / 6 L / 12
unresolved, mark +24.8 pts; 15 rows never reach the entry. This model counts moves that the
timing data says mostly happened before the Div confirmed, so it overstates.

Verdict: option 2 only makes money if entries come near the pivot, and the notes say 75% of
first legs are done before confirmation. Under the realistic entry no filter clears
breakeven. Low confidence either way: 32 of 50 outcomes are unresolved because the notes
don't record the path after confirmation. To settle it, log the confirmation-bar close and
whether +4 or -4 from that price hit first.
