# NBA props tab (Bet Tracker)

Builds the **NBA** tab in Tim's Bet Tracker sheet
(https://docs.google.com/spreadsheets/d/1zrv3wVqAmBfJ3DW1jzBuOP6BhtM-K0vTVJxJl6zOwUc/edit#gid=9200,
tab `sheetId` 9200). First basket (the main ask), opening tip, points and threes, built for
consistency (hit rate game to game). Small stakes, for fun.

## First shot log (Tim, 10/22)

Tim wants to know who took the first shot in every game, even when they missed. When grading a
date, run:

```
python3 analysis/first_events.py <YYYY-MM-DD> nba
```

It appends one row per game to `analysis/first_events/log.csv` (re-running a date replaces its
rows): first shot of the game and its result, each team's first shot, the first basket (first made FG) and first points including free throws.
Include the first shot and first score for each game in the grading message to Tim.

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
   - `batch_clear_values` on `'NBA'!A1:S460` (19 columns since 10/21)
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
- Estimated FB chance (model v2, 10/21/26) = P(team scores first) x the player's share of his team's
  first FG. P(team scores first) comes from the two main jumpers' tip rates (log5, each shrunk toward 50%
  with 6 pseudo tips) and the 2025-26 league rate that the tip winner scores first (64%).
- Share, step by step (code: `V2` and `v2_shares` in build_nba_tab.py):
  1. Accuracy blend: 0.5 x first-FG share + 0.5 x first-shot share x (his FG% / league FG% 47%).
     Both shares are shrunk toward 1 in 5 with 10 pseudo starts; FG% is shrunk toward league with 150
     pseudo attempts. Since 10/23: a player with fewer than 10 starts in the data (both seasons, any team)
     gets up to 10 more pseudo starts (20 at 0 starts, fading to 10 at 10 starts), and his 26-27 games count
     1x at 0 starts for his current team, ramping to the full B3 weight at 5 (`cur_weight`, `ramp_n`,
     `k_new`, `settle_n` in V2). A player who takes the first shot a lot but misses often is discounted.
  2. Opponent defense: x (opponent's rate of allowing the first FG to his position G/F/C, 2025-26 plus
     2026-27 x weight, shrunk toward the league rate with 120 pseudo games) / league rate, kept within
     0.85 to 1.15. These rates match the public @nbafirstbasket "allowed by position" table closely
     (r = 0.93 for 22 teams checked 10/21/26).
  3. Injury ripple: the probable five's shares are rescaled to sum to 99% (starters scored 99.7% of team
     first FGs in 2025-26). When a regular who often took the first shot is Out, his share goes to the
     rest in proportion to their shares; the pick text names him ("X out (28% share spread to the rest)")
     when his share was 25%+ over 20+ starts.
- Main jumper: this season's opening tips for the team, newest first (weights 3, 2, 1.5, then 1; regular
  season counts double), plus 0.05 per tip last season for any team, so traded bigs carry over but the
  current role wins. The main jumper is always put in the probable five.
- Backtest (`python3 analysis/nba/backtest_fb.py`): walk-forward on 936 games (12/1/25 to 4/12/26 plus
  10/20/26), each predicted from earlier games only, with actual starters and jumpers. Log loss of the
  first-FG scorer among the 10 starters: v1 2.293, v2 2.283 (uniform is 2.303); Brier 0.898 vs 0.896; top
  pick hit 13.9% vs 14.0%. Accuracy was the biggest gain; defense was neutral (kept modest at k=120); the
  ripple alone was neutral to slightly better. First basket is mostly noise, so treat the edge as small.
  `out/fb_candidates.json` lists every starter with v2 and old-model (v1) chances side by side.
- 10/23 fix backtest (`python3 analysis/nba/backtest_fb.py --team`, applies W like the build): 2025-26 (933
  games) log loss 2.2828 old vs 2.2826 new, top pick 14.0% both; 2026-27 (16 games through 10/22) 2.2902 vs
  2.2861, top pick 1 of 16 both. Top pick changed in 27 of 948 games (3 right each way). Too small to call a
  real gain; it stops one-start players from taking the pick. Counting only starts with the current team for
  the extra shrink was worse (2.2830, top pick 13.7%): it discards traded regulars' real history (Herro).
- Not added: home/away (the tip winner scores first 65.3% at home vs 63.0% away, within noise of 2.7
  points, and home is already inside the tip rates) and pace (who scores first is settled in the first one
  or two trips; a team-accuracy factor on P(team scores first) was tested and did not help).
- Probable starters are an estimate (recent regular-season starts once the season begins,
  otherwise preseason starts plus last season's starter share). Players listed Out or Doubtful are left out.

## Sources

- ESPN `site.api.espn.com/apis/site/v2/sports/basketball/nba`: scoreboard, summary
  (boxscore starters and play-by-play), teams, rosters, injuries. Works from the container.
- `cdn.nba.com` (403) and `stats.nba.com` (times out) are blocked here and not used.

## Lessons log

- 10/20/26 (opening night): the value first-basket picks hit (Collins +1000, Vassell +800); the book
  favorites (Wembanyama, Embiid) missed; Queta was projected but did not start. Prefer confirmed
  starters priced well past the fair line over short favorites. Tim bets $0.20 to $1 and likes longer shots.
- 10/21/26: model v2 (accuracy, defense by position, injury ripple). Jumper choice now follows this
  season's tips (Hayes for UTAH, Edey for MEM, Kessler for LAL) instead of last season's team counts.
  Game cache gained FG made/attempted per player and first-shot make (`v` 2); old caches are refetched.
- 10/21/26 results: first basket 1-10 (Ty Jerome +560 fair hit); props 4-1 (Curry 3+ threes missed with 2).
  First FGs went mostly to non-picks (Jalen Johnson, Jaquez, Randle, Missi, Clingan): role starters again.
- Fixed 10/21: the schedule cache now refetches any day with games not yet final, so finished games
  (like opening night) load into the 26-27 numbers on the next run.

- 10/22 lesson (applied from 10/23): a questionable big who is confirmed starting keeps his full first-basket
  share. Do not discount him for the tag; recheck lineups about 30 min before tip and rerun if he is in.
- 10/22 CLE @ PHI: Jarrett Allen (day-to-day, knee) started, won the tip and scored the first basket on CLE's first shot. A day-to-day center who jumps should keep his full first-basket share once he is confirmed in the lineup; recheck starters about 30 min before tip and rerun if a questionable big is in.

- 10/23: Jaquez Jr. got 36% of MIL's first FG and the CHI@MIL pick off one 26-27 start (1/1) at weight 3,
  with 1 start in 25-26. Fix: 26-27 weight ramps 1x to B3 over his first 5 starts with his current team, and
  players with under 10 starts get extra shrink toward 1 in 5. Jaquez fell to 27% share (fair +643 from +462)
  but still edges Rollins (22%): CHI allows forwards more often (x1.06 vs x0.93 for guards) and Jaquez shoots
  51%. Picks that changed tonight: LAC@LAL Doncic over Kessler, POR@SAC Morant over Sabonis, TOR@WSH Leonard
  over Barrett.

- 10/23 CHI @ MIL: Jalen Smith (CHI's jumper) won the tip and scored the first basket on CHI's first shot, the second straight game a tip-winning center scored first (Allen 10/22). Turner, MIL's jumper, scored MIL's first basket. Check whether the model underrates centers who win the tip on the first possession.

- 10/23 full slate: first basket 1-12 for our picks (Barrett +800 hit, pre-fix pick; the post-fix picks Leonard, Doncic,
  Morant all missed). StarTool stars 1 of 24 (Tatum); bombs 3 (Barrett, Sengun, Reaves). Starting centers scored
  5 of the 12 first baskets: Jalen Smith CHI, Diabate CHA, Gafford DAL, Sengun HOU, Edey MEM (Smith, Gafford and
  Diabate are listed F by ESPN but play the 5). Only Edey and Smith were on a tip-winning team; Sengun and Gafford
  scored after the other side won the tip and missed. Our center picks (Adebayo, Kessler, Zubac, Wembanyama) all missed.
  Check the center share in the build against these 13 games (Allen 10/22 + 5 of 12 on 10/23) before the next slate.

- 10/24 center check (`python3 analysis/nba/center_check.py`, walk-forward, current model, 1,922 jumper-games 25-26 + 26-27):
  the jumper (almost always the starting center) is underrated when his team wins the tip. Won tip: model 14.1%, actual
  17.0% (163 of 961, about 2.5 standard errors); his share of his team's first FG when the team scores first is 26.5%
  actual vs 21.8% model. Lost tip: model 7.6%, actual 7.3% (fine). Before the tip (what we price): 10.9% model vs 12.1%
  actual. Other starters are slightly overrated after a tip win (12.3% vs 11.7%). 26-27 so far: jumpers 9 of 56 (16.1%)
  vs 10.8% model. Likely cause: the model treats share as independent of the tip, but a tip win gives the jumper the
  first possession's lob or post-up. Candidate fix (not applied): a jumper-specific share boost x about 1.2 when his
  team wins the tip (and x about 0.95 when it loses), fit in backtest_fb.py before switching. 10/24 picks flag the center
  option with that adjustment as "center check".

## Tim vs model log (first basket)

Tim's picks come from his own read of the StarTool card (not just its star), so the Tim column tests how he uses StarTool's data; the StarTool column is its star/bomb as printed.

On game days Tim sends the StarTool Analytics "Game Script" card for each game (tip %, player model %, star/bomb). Save it to out/startool/<date>-<game>.jpg, note the numbers in that day's run file, and when grading add a row per game here: who scored first, Tim's picks, StarTool's top, our model's picks, hits.

| Date | Game | Scored first | Tim | StarTool top | Our model | Tim hit | Model hit |
|---|---|---|---|---|---|---|---|
| 10/22 | CLE @ PHI | Jarrett Allen (CLE won tip; first shot Allen, made) | Mobley, Mitchell | Mitchell | Mobley, Brown, Mitchell | No | No |
| 10/22 | DEN @ OKC | Cason Wallace (OKC won tip; first shot Wallace three, made) | Gordon, Murray | SGA (Jokic for DEN) | Murray, Jokic, Wallace | No | Yes (Wallace +1100) |
| 10/23 | CHI @ MIL 4:00 | Jalen Smith CHI (CHI won tip; first shot Smith layup, made). MIL first: Myles Turner | Rollins, Kuzma (changed from Herro, Turner) | Powell / Herro | Jaquez Jr. | No | No |
| 10/23 | NY @ BOS | Jayson Tatum BOS (NY won tip; first shot Bridges, missed) | (none sent) | Brunson / Tatum | Paul George | - | No (StarTool star hit) |
| 10/23 | ATL @ CHA | Moussa Diabate CHA, center (ATL won tip; Diabate first shot, made) | (none sent) | Alexander-Walker / Miller | Brandon Miller | - | No |
| 10/23 | DAL @ IND | Daniel Gafford DAL, center (IND won tip; first shot Nembhard, missed) | (none sent) | Flagg / Haliburton | Zubac | - | No |
| 10/23 | MIN @ ORL | Jaden McDaniels MIN (ORL won tip; first shot F. Wagner, missed) | (none sent) | Edwards / Banchero | Bane | - | No |
| 10/23 | TOR @ WSH | RJ Barrett TOR (WSH won tip; first shot Young, missed) | (none sent) | Leonard / Davis (bomb Barrett hit) | RJ Barrett (pre-fix; post-fix top was Leonard) | - | Yes, Barrett +800 |
| 10/23 | DET @ MIA | John Collins DET (MIA won tip; first shot Klay Thompson, missed) | (none sent) | Cunningham / Giannis (bombs Duren, Adebayo missed) | Adebayo | - | No |
| 10/23 | HOU @ SA | Alperen Sengun HOU, center (SA won tip; first shot Harper, missed) | (none sent) | Durant / Wembanyama (bomb Sengun hit) | Wembanyama | - | No |
| 10/23 | NO @ UTAH | Ace Bailey UTAH (UTAH won tip; first shot Bailey, missed; scored on UTAH's second shot) | (none sent) | Murphy / Markkanen (bombs Zion, K. George missed) | Jaren Jackson Jr. | - | No |
| 10/23 | MEM @ GS | Zach Edey MEM, center (MEM won tip; Edey first shot, dunk off Jerome assist) | (none sent) | Jerome / Curry (bombs Coward, Podziemski missed) | Ty Jerome | - | No |
| 10/23 | LAC @ LAL | Austin Reaves LAL (LAL won tip; first shot Kessler, blocked) | (none sent) | Garland / Doncic (bomb Reaves hit) | Kessler, Doncic | - | No |
| 10/23 | POR @ SAC | Keegan Murray SAC (POR won tip; first shot Lillard, missed) | (none sent) | Lillard / LaVine (bombs Avdija, Sabonis missed) | Sabonis (pre-fix), Morant (post-fix) | - | No |
| 10/24 | MIA @ CHA 6:00 | (grade) | Giannis, Adebayo (from StarTool allow ranks) | Giannis / Miller (bombs Adebayo, Knueppel) | Adebayo | (grade) | (grade) |
| 10/24 | BKN @ CLE 7:30 | (grade) | Mitchell, Allen (from StarTool allow ranks) | Porter Jr. / Mitchell | Mobley (center: Allen) | (grade) | (grade) |
| 10/24 | MIL @ PHI 7:30 | (grade) | (none sent) | Herro / Maxey | Jaylen Brown | (grade) | (grade) |
| 10/24 | WSH @ CHI 8:00 | (grade) | Kyshawn George, Sarr, Powell (from StarTool allow ranks) | Davis / Powell | Jalen Smith | (grade) | (grade) |
| 10/24 | SA @ DAL 8:00 | (grade) | Wembanyama, Fox (from StarTool allow ranks) | Wembanyama / Flagg (out) | Wembanyama | (grade) | (grade) |
| 10/24 | HOU @ ATL 8:30 | (grade) | Okongwu, Jabari Smith, Sengun (from StarTool allow ranks) | Durant / Alexander-Walker | Sengun | (grade) | (grade) |
| 10/24 | NO @ DEN 9:00 | (grade) | Murray, Jokic (from StarTool allow ranks) | Murphy / Jokic | Murray (center: Jokic) | (grade) | (grade) |
| 10/24 | GS @ PHX 10:00 | (grade) | Booker, Miles Bridges (from StarTool allow ranks) | Curry / Booker | Jalen Green | (grade) | (grade) |
