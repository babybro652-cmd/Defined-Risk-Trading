# NHL props tab (Bet Tracker)

Builds the **NHL** tab in Tim's Bet Tracker sheet
(https://docs.google.com/spreadsheets/d/1zrv3wVqAmBfJ3DW1jzBuOP6BhtM-K0vTVJxJl6zOwUc/edit#gid=9100,
tab `sheetId` 9100). Anytime goal, first goal and shots on goal, built for consistency
(hit rate game to game). Small stakes, for fun.

## Refresh (weekly, or any game day for a new shortlist)

1. Build. `--date` is the slate date (default: today, Eastern):

   ```
   python3 analysis/nhl/build_nhl_tab.py --date 2026-10-15
   ```

   It downloads only new final games (parsed games are cached in `data/games_<season>.json`),
   then pulls rosters, team/goalie/PP stats, Daily Faceoff goalies and ESPN injuries, and writes:
   - `out/sheet_values.json`: the whole tab as one 2D array (`NHL`) plus row positions (`meta`)
   - `out/nhl_tab.csv`: the same grid
   - `out/shortlist.md`: the night's picks and goalies as text

2. Push with the Google Sheets connector:
   - `batch_clear_values` on `'NHL'!A1:Q300`
   - `update_formulas` on `'NHL'!A1` with the `NHL` array (split it in two calls if it is large)
   - Formatting is already on the tab. If the section rows move (the player count or number of
     picks changes), redo the header colors and number formats for the new rows; `meta` lists
     where each section starts.

   Do not touch the other tabs. The Bets tab has an ARRAYFORMULA in J2:K2; never write J3:K.

3. Commit `data/` and `out/` so the next run starts from the cache.

## Layout (one tab, top to bottom)

- Row 1 title (frozen), legend, and **B3 = 26-27 game weight** (input, default 3). All Blend
  columns are formulas that read B3.
- Tonight's shortlist (4 goal, 3 first goal, 5 SOG) with one-line reasons, then probable goalies
  (Daily Faceoff Confirmed / Likely) and notable Out/IR players for each game.
- Anytime goal: 34 forwards by blended goal hit%, plus the 6 D with the most shots.
- First goal: same players, first goal of the game counts and rates, team scores-first rate.
- Shots on goal: SOG/G each season, blended share of games over 1.5 / 2.5 / 3.5 / 4.5, last 5.
- Opponent weakness: all 32 teams, GA/G, SA/G, PK% both seasons, main starter SV%, how often
  opponents score first, and tonight's matchup and goalie.

## How numbers are computed

- Hit% = games with a goal / games played. Shootout goals are not counted anywhere.
- Blend = (W x 26-27 count + 25-26 count) / (W x 26-27 GP + 25-26 GP), W in B3. Early in the
  season 25-26 carries most of the weight on purpose; raise W as 26-27 games pile up.
- First goal = scorer of the first non-shootout goal in the game summary.
- Role = TOI rank among team forwards (Top 6 / Mid 6 / Bottom) or D (Top pair / 2nd / 3rd),
  plus PP TOI rank on the team (PP1 = top 5, PP2 = next 5). This is a proxy for line charts.
- Shortlist rules are written on the tab under the picks.

## Sources

- NHL API `api-web.nhle.com`: boxscores, game landing (goal order), schedule, rosters, standings.
- NHL stats API `api.nhle.com/stats/rest`: team summary (GA/G, SA/G, PK%), skater TOI (PP TOI),
  goalie summary (SV%).
- Daily Faceoff `dailyfaceoff.com/starting-goalies/<date>` (page JSON) for probable goalies.
- ESPN `site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries`.
