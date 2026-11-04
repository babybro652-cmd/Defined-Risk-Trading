# UCL props tab (Bet Tracker)

Builds the **UCL** tab in Tim's Bet Tracker sheet
(https://docs.google.com/spreadsheets/d/1zrv3wVqAmBfJ3DW1jzBuOP6BhtM-K0vTVJxJl6zOwUc/edit#gid=9300,
tab `sheetId` 9300). Anytime and first goalscorer, shots on target, team goals (BTTS, over
2.5), corners, and the fixture list. Small stakes, for fun.

## Refresh (the day before each matchday, and again the morning of)

1. Build. `--date` is where to start looking for the next matchday (default: today, Eastern).
   The slate is the first UCL date on or after it with unplayed matches, plus the next day when
   it is the other half of the same matchday.

   ```
   python3 analysis/ucl/build_ucl_tab.py
   python3 analysis/ucl/build_ucl_tab.py --date 2026-10-20
   ```

   It downloads only new final matches (cached in `data/matches_<comp>.json`, schedules in
   `data/schedule_<comp>.json`) for UCL 2025-26, UCL 2026-27 and each UCL club's domestic league
   since 8/1, and writes:
   - `out/sheet_values.json`: the whole tab as one 2D array (`UCL`) plus row positions (`meta`)
   - `out/ucl_tab.csv`: the same grid
   - `out/shortlist.md`: the matchday's picks as text

2. Push with the Google Sheets connector:
   - `batch_clear_values` on `'UCL'!A1:Q400`
   - `update_formulas` on `'UCL'!A1` with the `UCL` array (split it in two calls if it is large)
   - Formatting: `python3 analysis/tab_format.py ucl` prints the batchUpdate requests (header
     colors, number formats, gradients, widths) for the current row positions; pass them to
     `update_spreadsheet`. On a rerun, first delete the tab's old gradient rules
     (`deleteConditionalFormatRule`, index 0, repeated) so they don't stack.

   Do not touch the other tabs. The Bets tab has an ARRAYFORMULA in J2:K2; never write J3:K.

3. Commit `data/` and `out/` so the next run starts from the cache.

## 2026-27 matchdays (ESPN schedule)

MD1 9/8-10, MD2 10/13-14, MD3 10/20-21, MD4 11/3-4, MD5 11/24-25, MD6 12/8-9, MD7 1/19-20,
MD8 1/27. Knockout playoffs from 2/15. The script reads the dates from ESPN each run.

## Layout (one tab, top to bottom)

- Row 1 title (frozen), legend, and **B3 = UCL 26 start weight** (input, default 3). The
  Blend goal% column is a formula that reads B3.
- Next matchday shortlist: 5 anytime goal, 3 first goal, up to 4 shot-on-target picks, then
  game angles (over 2.5, BTTS, match corners, team corners).
- Next matchday games: GF/GA per game, BTTS and over 2.5 rates, expected corners, match over 9.5
  corners rate, form.
- Goalscorers: top 60 players at UCL clubs by blended share of starts with a goal, with shots,
  shots on target, 1+ SOT and 2+ shots rates, and first goals.
- Teams: goals for and against, BTTS, over 2.5, scores first (2026-27 all comps), UCL-only splits
  for 2026-27 and 2025-26, form.
- Corners: won and conceded per game, match total, match over 8.5 / 9.5 / 10.5, team over
  4.5 / 5.5, first-half total and over 4.5, and UCL 2025-26 for reference.
- Fixtures: every 2026-27 UCL match with result, corners and first goalscorer.

## How numbers are computed

- Player rates are per start (bench appearances ignored). Blend pools UCL 2026-27, UCL 2025-26
  and domestic 2026-27 starts, with each UCL 2026-27 start weighted by B3.
- First goal = the first goal of the match in ESPN's key events; an own goal counts for nobody
  (most books settle first scorer that way or void it, so check yours).
- Corners = ESPN team stat `wonCorners`. First-half corners are counted from the ESPN
  commentary ("Corner, Team. Conceded by Player.") up to "First Half ends"; matches without
  commentary are left out of the 1H columns (the "1H games" column shows the sample).
- Team goals and corners use every 2026-27 match we have (UCL plus domestic league), because
  the UCL sample alone is two or three games per club early on.
- Picks only use players who started their club's latest match; ESPN has no soccer injury feed,
  so check lineups an hour before kickoff.

## Sources

- ESPN `site.api.espn.com/apis/site/v2/sports/soccer/<league>`: scoreboard and summary
  (rosters with goals, shots and shots on target; key events; team stats; commentary).
- Domestic leagues used: eng.1, esp.1, ita.1, ger.1, fra.1, por.1, ned.1, bel.1, tur.1, aut.1,
  gre.1, nor.1. ESPN has no league feed for Shakhtar, Slavia Prague, Slovan Bratislava or Sabah,
  so those clubs use UCL matches only.

## Calibration (11/4 review) and pick rules

`python3 analysis/ucl/review.py [--scope UCL|Domestic|all]` prints hit rate vs average predicted
chance and ROI at our own fair price per category, from `picks_log.csv` (one row per graded pick;
add the matchday's rows after grading, with pred = the Bets row's est % as a decimal).

Through 11/3 (UCL + domestic weekend picks, 53 with an estimate): 27-26, 51% hit vs 66% predicted.
1+ SOT 10-1 (80% pred) and over 2.5 8-3 (75%) held up. Overconfident: anytime goal 4-4 (60%),
first goal 0-3 (17%), 2+ SOT 1-4 (56%), BTTS 1-5 (76%), match corners 2-2 (75%), team corners
0-2 (82%), parlays with 2+ SOT legs 0-3.

Rules in `build_ucl_tab.py` since 11/4 (constants `CAL`, `MIN_EST`, `SOT2_*`, `GOAL_CAP`):
- Every shortlist pick shows **Est %** (calibrated) and **Fair** (cols F:G). Log the Est and Fair
  in the Bets row, not the raw tab rate.
- Anytime and first goal: est x0.80 (rate x opponent factor capped at 85% first). First goal =
  share of team goals x team scores first x 0.93. First goal stake $0.10 to $0.25.
- 1+ SOT: shrunk rate, unchanged. Skip above 75% (shorter than -300).
- 2+ SOT: only 2.0+ SOT per start over 10+ starts, est x0.80, listed only at 50%+, max 2 a day,
  never as parlay legs.
- Over 2.5: x0.90. BTTS: x0.80, max 1 a day, only at est 55%+, $0.25.
- Match corners: x0.80, the highest line with est 55% to 75%, $0.25. Team corners: no longer picked.
- Parlays: 1+ SOT legs only, using the shrunk rate, 65%+ legs.
- Player props only after the confirmed XI (about 1 hr before kickoff).
- Revisit the factors after 20+ more graded picks per category.
