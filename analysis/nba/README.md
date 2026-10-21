# NBA props tab (Bet Tracker)

Builds the **NBA** tab in Tim's Bet Tracker sheet
(https://docs.google.com/spreadsheets/d/1zrv3wVqAmBfJ3DW1jzBuOP6BhtM-K0vTVJxJl6zOwUc/edit#gid=9200,
tab `sheetId` 9200). First basket (the main ask), opening tip, points and threes, built for
consistency (hit rate game to game). Small stakes, for fun.

## Refresh (daily on game days, before about 5 PM ET)

1. Build. `--date` is where to start looking for the slate (default: today, Eastern). The slate
   is the first date on or after it with games. Before the regular season starts (10/20/26),
   preseason dates are skipped and the slate is opening night.

   ```
   python3 analysis/nba/build_nba_tab.py
   python3 analysis/nba/build_nba_tab.py --date 2026-10-21
   ```

   It downloads only new final games (parsed games are cached in `data/games_<season>.json`,
   the schedule in `data/schedule_<season>.json`), then pulls current rosters and ESPN injuries,
   and writes:
   - `out/sheet_values.json`: the whole tab as one 2D array (`NBA`) plus row positions (`meta`)
   - `out/nba_tab.csv`: the same grid
   - `out/shortlist.md`: the slate's picks and tip matchups as text

   The first run downloads all 1,230 2025-26 games (about 2 minutes); later runs take seconds.

2. Push with the Google Sheets connector:
   - `batch_clear_values` on `'NBA'!A1:Q400`
   - `update_formulas` on `'NBA'!A1` with the `NBA` array (split it in two calls if it is large)
   - Formatting: `python3 analysis/tab_format.py nba` prints the batchUpdate requests (header
     colors, number formats, gradients, widths) for the current row positions; pass them to
     `update_spreadsheet`. On a rerun, first delete the tab's old gradient rules
     (`deleteConditionalFormatRule`, index 0, repeated) so they don't stack.

   Do not touch the other tabs. The Bets tab has an ARRAYFORMULA in J2:K2; never write J3:K.

3. Commit `data/` and `out/` so the next run starts from the cache.

## Layout (one tab, top to bottom)

- Row 1 title (frozen), legend, and **B3 = 26-27 game weight** (input, default 3). All Blend
  columns are one ARRAYFORMULA each (in the first data row) that reads B3.
- Slate shortlist: up to 8 first basket picks (max 2 per game) with an estimated chance and the
  fair (break-even) price, 4 team-first-basket picks, and up to 6 points / threes overs.
- Slate tip-off table: each game's main jumpers and their tip-win %, the chance the away team
  wins the tip and scores first, and notable Out / Doubtful players.
- First basket: the probable five for all 30 teams (FB, team first FG, first shot as a starter,
  26-27 and 25-26, blends, preseason line, first points including free throws).
- Tip-off by team: main jumper now, his tip record both seasons, the team's tip %, how often the
  team scores first, and how often it scores first after winning the tip.
- Points and threes: share of starts over 9.5 / 14.5 / 19.5 / 24.5 points and 1+ to 4+ threes.
- Next NBA games for 7 days with the jumper matchup.

## How numbers are computed

- First basket (FB) = first made field goal of the game (FanDuel's rule; free throws don't
  count). "First pts incl FT" is the other rule, shown for books that count free throws.
- Team 1st = the player made his team's first field goal. 1st shot = he took the team's first
  field-goal attempt. All three count only games he started.
- Opening tip = the first jump ball in the 1st quarter; the winner is the team that gains
  possession.
- Blend = (W x 26-27 count + 25-26 count) / (W x 26-27 starts + 25-26 starts), W in B3.
  Preseason is shown but left out of the blend (starters rest, lineups are experiments).
- Estimated FB chance = P(team scores first) x the player's share of team first FGs (shrunk
  toward 1 in 5 with 10 pseudo starts). P(team scores first) comes from the two main jumpers'
  tip rates (log5, shrunk toward 50%) and the 2025-26 league rate that the tip winner scores
  first.
- Probable starters are an estimate (recent regular-season starts once the season begins,
  otherwise preseason starts plus last season's starter share). Players listed Out are dropped.

## Sources

- ESPN `site.api.espn.com/apis/site/v2/sports/basketball/nba`: scoreboard, summary
  (boxscore starters and play-by-play), teams, rosters, injuries. Works from the container.
- `cdn.nba.com` (403) and `stats.nba.com` (times out) are blocked here and not used.

## Lessons log

- 10/20/26 (opening night): the value first-basket picks hit (Collins +1000, Vassell +800); the book
  favorites (Wembanyama, Embiid) missed; Queta was projected but did not start. Prefer confirmed
  starters priced well past the fair line over short favorites. Tim bets $0.20 to $1 and likes longer shots.
- Fixed 10/21: the schedule cache now refetches any day with games not yet final, so finished games
  (like opening night) load into the 26-27 numbers on the next run.
