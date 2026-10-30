# NHL props tab (Bet Tracker)

Builds the **NHL** tab in Tim's Bet Tracker sheet
(https://docs.google.com/spreadsheets/d/1zrv3wVqAmBfJ3DW1jzBuOP6BhtM-K0vTVJxJl6zOwUc/edit#gid=9100,
tab `sheetId` 9100). Anytime goal, first goal and shots on goal, built for consistency
(hit rate game to game). Small stakes, for fun.

## First shot log (Tim, 10/22)

Tim wants to know who took the first shot in every game, even when they missed. When grading a
date, run:

```
python3 analysis/first_events.py <YYYY-MM-DD> nhl
```

It appends one row per game to `analysis/first_events/log.csv` (re-running a date replaces its
rows): first shot of the game and its result, each team's first shot, first shot attempt of any kind (missed or blocked) and the first goal. "First shot" = first shot on goal.
Include the first shot and first score for each game in the grading message to Tim.

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

## Anytime goal calibration (10/30/26, Tim approved)

The blended goal hit% ran hot for the players we pick (top of the list regresses). Est = `GOAL_F` x blend, with
`GOAL_F` = 0.77 in build_nhl_tab.py, from `python3 analysis/nhl/calibrate_goal.py` (walk-forward, top 4 a night by blend):

| Sample | Picks | Predicted (raw blend) | Scored | Factor |
|---|---|---|---|---|
| 25-26, from 11/15 (season to date only) | 508 | 47.0% | 36.4% | 0.775 |
| 26-27 through 10/29 (W = 3 blend) | 112 | 45.3% | 33.0% | 0.729 |
| Logged Bets picks with a % | 25 | 46.4% | 36.0% | 0.776 |
| Pooled | 645 | 46.7% | 35.8% | 0.767 |

The shrink is stronger at the top (blend 45%+ scores about 36 to 39%) than for 35-45% names (factor 0.87 to 0.91), so
0.77 is set for shortlist picks. Shortlist text gives Est, fair, and "bet only at +X or longer", X = the larger of +150
and fair with a 10% cushion. Anytime goal is never a parlay leg. SOG picks over 75% name the next line up (-300 rule).
Parlays: 3+ SOG legs only (`analysis/parlays.py`; see the NBA README "Model changes 10/30/26"). StarTool: star/bomb lines
in `out/startool/star_bomb.txt` (`date|AWAY @ HOME|star,star|bomb,bomb`; last names as printed are fine) give an
"agree" or "differs" flag for our top anytime goal pick per game. No blend.

## Sources

- NHL API `api-web.nhle.com`: boxscores, game landing (goal order), schedule, rosters, standings.
- NHL stats API `api.nhle.com/stats/rest`: team summary (GA/G, SA/G, PK%), skater TOI (PP TOI),
  goalie summary (SV%).
- Daily Faceoff `dailyfaceoff.com/starting-goalies/<date>` (page JSON) for probable goalies.
- ESPN `site.api.espn.com/apis/site/v2/sports/hockey/nhl/injuries`.
