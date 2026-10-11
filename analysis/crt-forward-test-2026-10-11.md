# CRT Forward Test Log analysis, 10/11/2026

Builds on `crt-forward-test-2026-10-03.md` (sections 1-8, rows #1-#247).
Source: CRT Forward Test Log (`1H9KSzv9C0hIhDuWjUCQKpKURv_kEkRE5CLlLV-kmofA`, tab "Untitled"),
columns A-S plus the dashboard (U1:AA19), rows #1-#293. Read only; the sheet was not edited.

New since 10/3: rows #248-#293 (46 rows, 10/8 07:29 CT to 10/9 15:30 CT). No rows 10/3-10/8
(TradingView lapsed). Column H is now filled on Div rows from #108 (9/27) and on 2 CRT rows.

Method:
- Log times are Central. Sessions below are by Central time: **NY = 8:30-15:00 CT** (9:30 AM-4 PM
  ET, Tim's window), Asia = 17:00-02:00 CT, London = 02:00-08:30 CT, Post = 15:00-17:00 CT.
  "Overnight" = Asia + London (+ Post where it appears).
- Outcomes were re-checked on Yahoo ES=F 1-minute bars, 9/20 17:10 CT to 10/9 16:00 CT
  (20,491 bars). All 197 Div rows with a bar match G exactly (low for Bull, high for Bear) at the
  logged time. All 58 CRT rows with bars match G to a 1m wick 15-30 min before the logged time
  (the candle-2 sweep). BUY/SELL entries match the close of the bar before the logged time to
  within a tick. 7 rows fall in bar gaps and are skipped in bar-based stats (#1, #3, #54, #168,
  #175, #203, #225).
- "4/4" = fixed 4 pt stop, 4 pt target, Tim's 3.5-4 pt stop rule. Entry: BUY/SELL at the signal
  close; Div at the **label** (close of the bar 5 bars after the pivot); CRT at the close of the
  confirmation candle. Walk 60 one-minute bars; a bar touching both counts as a loss; otherwise
  timeout at the 60th bar's close. ES: $50/pt, about $5 round trip; MES: $5/pt, about $1.88.
- Anything with n < 20 is tentative. Every split below is small.

## 1. Data status

| Type | Rows | Since 10/8 | H filled | Notes filled |
|---|---|---|---|---|
| Bull Div | 112 | 10 | 61 (all from #108 on) | 60 (#246 blank) |
| Bear Div | 89 | 21 | 59 (all from #108 on) | 59 |
| CRT Bull (unfiltered) | 28 | 8 | 1 (#291) | 0 |
| CRT Bear (unfiltered) | 32 | 4 | 1 (#292) | 0 |
| BUY | 18 | 1 | n/a | n/a |
| SELL | 14 | 2 | n/a | n/a |
| Total | 293 | 46 | | |

Dashboard (U1:AA19) agrees with the rows: 293 signals, 27 closed trades, 10 W / 5 BE / 12 L,
37% win, -2R total, -0.07R per trade. Its CRT "Avg Ticks" (16 Bull, 22 Bear) are one row each.

Data days: 11 sessions (9/22-9/25, 9/28-10/2, 10/9 full; 9/21 evening; 10/8 from 07:29 CT only).

Data issues found (none block the analysis):
- **Note times are mixed time zones.** Bar check: notes on #108-#158 and on all of #248-#293 are
  in **Eastern** (chart time); #159-#247 are Central. Example: #248 "dropped to 7816.75 @ 08:51"
  is the 07:51 CT bar. The convention is Central.
- **10/8-10/9 Div notes have only the favorable move** ("dropped to X @ time"). No label price,
  no "+4 first", no "reversed to" part, so the 10/4 label convention isn't in use yet.
- **Column S (Div Valid Until) is still blank** on every row (#139 holds "7 mins").
- **Blank results #9, #91, #94, #138, #247.** Bars explain 4 of them: the indicator replaced the
  trade with the next BUY/SELL before it resolved (#9 by #10 after 15 min, #91 by #94, #94 by
  #97, #138 by #146; #138 had reached TP2 first). #247 (last row before the lapse) went to TP1
  and back to entry on bars (BE). Left out of the stats below, as before.
- #140 (H = 0) and #239 (H) from the 10/3 list are fixed.

## 2. BUY/SELL trade outcomes

Logged results (the indicator moves the stop to entry at TP1 and to TP1 at TP2; "TP1 HIT" is
scored +1R as the sheet does). Win = TRAIL or TP1 HIT.

| | Signals | Closed | W / BE / L | Win % | Total R | Reached TP1 | Full exit at TP1 | Median stop |
|---|---|---|---|---|---|---|---|---|
| All | 32 | 27 | 10 / 5 / 12 | 37% | **-2R** | 15 | +3R | 9.4 pts |
| BUY (long) | 18 | 14 | 5 / 3 / 6 | 36% | -1R | 8 | +2R | 9.3 |
| SELL (short) | 14 | 13 | 5 / 2 / 6 | 38% | -1R | 7 | +1R | 10.0 |
| Asia | 14 | 12 | 5 / 3 / 4 | 42% | +1R | 8 | +4R | 6.3 |
| London | 10 | 8 | 2 / 2 / 4 | 25% | -2R | 4 | 0R | 9.9 |
| **NY** | 7 | 7 | 3 / 0 / 4 | 43% | -1R | 3 | -1R | **21.0** |
| Since 10/8 (#250, #255, #274) | 3 | 3 | 0 / 1 / 2 | 0% | -2R | 1 | -1R | 10.8 |

Change from 10/3: 24 closed / 0R became 27 closed / -2R. The 3 new trades were a BE (#250,
London, long) and two full stops (#255 NY short, #274 Asia short).

Stops: only 2 of 32 signals have a stop of 4 pts or less (#51, #169, both 3 pts); 20 of 32 are
over 8 pts. NY stops are the widest (median 21 pts: #101 35, #38 25, #188 21.5, #218 21). The
logged R is not what Tim's 3.5-4 pt rule would produce.

**Same signals with a 4 pt stop / 4 pt target (bar check):**

| | n | W / L / timeout | Win % | Net pts | 1 ES gross |
|---|---|---|---|---|---|
| All | 32 | 18 / 12 / 2 | 60% | +25.5 | +$1,275 |
| BUY | 18 | 8 / 8 / 2 | 50% | +1.5 | +$75 |
| SELL | 14 | 10 / 4 / 0 | 71% | +24.0 | +$1,200 |
| **NY** | 7 | 6 / 1 / 0 | 86% | +20.0 | +$1,000 |
| Overnight | 25 | 12 / 11 / 2 | 52% | +5.5 | +$275 |
| Same-direction Div pivot within 25 min before | 17 | 12 / 3 / 2 | 80% | +37.5 | +$1,875 |
| No Div within 25 min | 15 | 6 / 9 / 0 | 40% | -12.0 | -$600 |

All 3 new trades hit +4 before -4, including the 2 that were full stops under the indicator's
wide stops. A 4 pt stop with an 8 pt target does worse on longs (-5 pts) and better on shorts
(+32 pts). Costs take about $5 per ES trade off these.

Read: the BUY/SELL signal looks better with Tim's tight bracket than with the indicator's own
stops, and best with a fresh Div before it (80%, n=15 decided). The NY result is 7 trades.

## 3. Div hold rate

**Before the label: 197 of 197 held.** No bar went through the pivot between the pivot and the
label on any Div with bar data. That's why column H = G (0 ticks) on every Div row. Tim's read is
right, and it's also built in: a pivot (length 5) can't confirm if price takes it out in those 5
bars. So H measured from G can't size a stop.

**After the label** (pivot still unbroken, minutes after the pivot bar):

| Window | All (197) | NY (61) | Overnight (136) | 9/21-10/2 (166) | 10/8-10/9 (31) |
|---|---|---|---|---|---|
| Through +10 min | 162 (82%) | | | | |
| Through +15 min | 140 (71%) | 41 (67%) | 99 (73%) | 123 (74%) | 17 (55%) |
| Through +25 min | 108 (55%) | 33 (54%) | 75 (55%) | 97 (58%) | 11 (35%) |
| Through +30 min | 101 (51%) | | | | |
| Through +60 min | 66 (34%) | 24 (39%) | 42 (31%) | 60 (36%) | 6 (19%) |

Median time to a pivot break, when it breaks within an hour: 17 minutes after the pivot.
This is lower than the 10/3 note-based read ("about a third later break the pivot"): the notes
stop recording after the first move, while bars show about two thirds break within an hour.
The window in column S is blank, so "held until Div Valid Until" can't be checked from the sheet.

**Trading Divs from the label, 4/4 bracket:**

| | n | W / L / T | Win % (W/(W+L)) | Net pts | Label distance from pivot (median) |
|---|---|---|---|---|---|
| All Div | 197 | 92 / 91 / 14 | 50% | +2.5 | 3.0 pts |
| Bull Div | 110 | 53 / 52 / 5 | 50% | +3.25 | 3.25 |
| Bear Div | 87 | 39 / 39 / 9 | 50% | -0.75 | 2.75 |
| NY | 61 | 28 / 33 / 0 | 46% | -20.0 | 5.5 |
| Overnight | 136 | 64 / 58 / 14 | 52% | +22.5 | 2.1 |
| **NY AM (8:30-11:00 CT)** | 27 | 17 / 10 / 0 | 63% | +28.0 | |
| **NY PM (11:00-15:00 CT)** | 34 | 11 / 23 / 0 | 32% | -48.0 | |
| 10/8-10/9 only | 31 | 12 / 18 / 1 | 40% | -24.25 | 2.0 |

Every Div at 4/4 is a coin flip and doesn't clear costs (breakeven about 51% on ES, 55% on MES).
The one split that holds up: **NY AM vs NY PM.** It was flagged on 10/4 and the new rows agree
(10/8-10/9: AM 4 W / 2 L, PM 1 W / 4 L). By type: Bull AM 10/7, Bear AM 7/3, Bull PM 7/11,
Bear PM 4/12. The AM/PM gap (63% vs 32%) is the largest in the log (z about 2.4), but it is one
of many cuts on 61 trades, so treat it as likely, not proven. In NY the label prints a median
5.5 pts from the pivot (vs 2.1 overnight), so by label time much of the NY move is gone.

## 4. CRT signal frequency and behavior

60 CRT rows (28 Bull, 32 Bear) over about 10.5 sessions: **about 5-6 per session, 1.6 per day
in the NY window** (18 in NY; every session had at least one). 10/9 had 11 (7 Bull, 4 Bear),
the most of any day.

| | n | Sweep held 60 min | Stop to the sweep (median) | 4/4: W / L / T | 4/4 net pts |
|---|---|---|---|---|---|
| All CRT | 58 | 49 (84%) | 11.6 pts | 27 / 29 / 2 | -10.75 |
| CRT Bull | 27 | 22 | 12.0 | 11 / 15 / 1 | -18.25 |
| CRT Bear | 31 | 27 | 10.25 | 16 / 14 / 1 | +7.5 |
| NY | 18 | 17 (94%) | 14.25 | 7 / 11 / 0 | -16.0 |
| Overnight | 40 | 32 (80%) | 10.5 | 20 / 18 / 2 | +5.25 |

- The swept level usually holds (84%), but it sits a median 11.6 pts from the entry (quartiles
  7-15, max 42). Only 2 of 58 had a sweep stop within 4 pts.
- With the stop at the sweep and a 1R target (390 bars): 28 W / 20 L / 10 still open,
  about +9.2R, but at stops 3x Tim's limit. NY: 8 W / 5 L / 5 open.
- With Tim's 4/4 bracket the CRT tag loses (48%, -10.75 pts), worst for CRT Bull in NY (2 W / 6 L).
- Column H on CRT rows (Tim's 10/11 convention, worst price after the tag): only #291 (low 4 pts
  above the swept 7859.75, sweep held until the rally) and #292 (high 5.5 pts below the swept
  7869.25). Bars agree within a tick. Two rows can't say anything yet.

## 5. NY session vs overnight

| Signal (Tim's 4 pt rule) | NY | Overnight |
|---|---|---|
| BUY/SELL, 4/4 | 6 W / 1 L, +20 pts (n=7) | 12 W / 11 L / 2 T, +5.5 pts (n=25) |
| BUY/SELL, logged R | -1R (n=7, median stop 21 pts) | -1R (n=20, median stop 8.5) |
| Div from label, 4/4 | 46%, -20 pts (n=61); AM 63%, PM 32% | 52%, +22.5 pts (n=136) |
| Div pivot held 25 min | 54% | 55% |
| CRT tag, 4/4 | 7 W / 11 L, -16 pts (n=18) | 20 W / 18 L, +5.25 pts (n=40) |
| CRT sweep held 60 min | 94% | 80% |
| Signals per session | ~0.6 BUY/SELL, ~5.5 Div, ~1.6 CRT | ~2.3 BUY/SELL, ~12 Div, ~3.8 CRT (all per 11 sessions) |

NY gives fewer signals with bigger moves: wider stops, labels further from the pivot, sweeps that
hold more often. For Tim's rules (NY only, label entry, 4 pt stop) the usable read is:
BUY/SELL in NY with a 4/4 bracket (6/7, tiny n) and Divs in the NY morning (63%, n=27).
NY afternoon Divs (32%) and NY CRT Bull tags (2/8) have been the weakest.

## 6. What the data still can't answer

- **NY-only trade edge.** 7 NY BUY/SELL in 11 sessions (about 0.6 a day). A win rate within
  +/-10% needs about 100 trades, which is about 150 sessions at this pace. Even 30 trades (a rough
  first read) is about 7 more weeks.
- **NY AM Divs.** 27 now; about 2.5 a session. 60 (a 95% range of about +/-12%) is about 13 more
  sessions; 100 is about 30 more sessions.
- **Div Valid Until window.** Column S is blank, so the hold rate inside Tim's window can't be
  measured from the sheet. Needs S filled (or the window in minutes written down once).
- **Label-based Div results from Tim's own notes.** The 10/4 format (label price, "+4 first")
  isn't in the 10/8-10/9 notes, so the bars are the only source. Logging it lets the sheet stand
  on its own and checks the bar data.
- **CRT entry drawdown.** 2 of 60 CRT rows have H. About 30-40 CRT rows with H (around 3 weeks,
  or about 4 weeks for NY only) to size a stop below the sweep.
- **Final result on replaced trades.** The log can't show what a replaced BUY/SELL would have
  done; only bars can.
- **One market regime.** 11 sessions, mostly a 7700-7870 range. Nothing here has seen a trend
  week or a big news day.

## 7. Takeaways

1. Logged BUY/SELL: 27 closed, 37% win, -2R. Wide stops (median 9.4 pts; NY 21 pts) don't fit
   Tim's 3.5-4 pt rule.
2. The same signals at a 4/4 bracket: 60% (+25.5 pts); with a Div within 25 min before: 80%
   (12 W / 3 L). Still small, but it has held from 10/4 to now.
3. Div pivots never break before the label (H = 0 is real and built in). After the label, about
   half break within 25 min and two thirds within an hour.
4. Divs as standalone 4/4 trades: 50%, no edge. NY AM 63% vs NY PM 32%; skip NY PM Divs.
5. CRT tags: about 5-6 per session, 1.6 in NY. The sweep holds 84% of the time but is about
   11-12 pts away, so a 4 pt stop doesn't fit it (4/4: 48%, -10.75 pts).

## 8. What to log next

- Div notes in the 10/4 format, in Central: `Label X @ time CT, +4 first / -4 first / neither`,
  then `Rallied/Dropped to X @ time CT, reversed to Y @ time CT`.
- Fill column S (Div Valid Until) and column H on CRT rows (worst price after the tag).
- When a BUY/SELL is replaced by the next signal, write "REPLACED" in O so blanks mean something.
