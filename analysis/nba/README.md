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

   Confirmed lineups (since 10/30): put them in `data/lineups_<date>.json`
   (`{"WSH": {"five": [names as on the ESPN roster], "jumper": "Anthony Davis"}}`) and add
   `--lineups analysis/nba/data/lineups_<date>.json`. Listed teams use those five and that jumper instead of the estimate.

   It downloads only new final games (parsed games are cached in `data/games_<season>.json`,
   the schedule in `data/schedule_<season>.json`), then pulls current rosters and ESPN injuries,
   and writes:
   - `out/sheet_values.json`: the whole tab as one 2D array (`NBA`) plus row positions (`meta`)
   - `out/nba_tab.csv`: the same grid
   - `out/shortlist.md`: the slate's picks and tip matchups as text

   The first run downloads all 1,230 2025-26 games (about 2 minutes); later runs take seconds.

2. Push with the Google Sheets connector:
   - `batch_clear_values` on `'NBA'!A1:S480` (19 columns since 10/21; about 467 rows since the method
     sections were added 10/29). If the tab has fewer rows than the grid, first `appendDimension` rows
     (the formatting step then sets rowCount to rows + 20).
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
  Since 10/30: the jumper split and top-end shrink below ("Model changes 10/30/26").
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

## First basket method (added 10/29/26)

How the first points are scored, for "first basket method" markets and player + method props
("Ty Jerome first basket: 3-pointer"). Code: `fb_method.py` (imported by the build). Cache:
`data/methods_<season>.json`, one ESPN summary parse per game (first points method, first FG method,
each team's first points / first FG method and scorer, every player's made FGs by type).

- Methods from the ESPN play type: **rim** = dunk, layup, tip-in, putback, finger roll, alley-oop;
  **j2** = every other 2 (jump shots, floaters, hooks, fadeaways); **3**; **ft** (first points only).
  Book rules vary (some group hooks or floaters with layups); check the market's rules.
- League base rates, 2025-26 (1,235 games): first points rim 35.9%, j2 28.1%, 3 27.0%, FT 9.0%.
  First basket (FG only) rim 39.5%, j2 29.9%, 3 30.6%. 2026-27 so far (68 games): first points rim 30.9%,
  j2 29.4%, 3 29.4%, FT 10.3%; first basket rim 36.8%, j2 29.4%, 3 33.8%.
- By position, share of team first FGs (both seasons): G rim 30 / j2 30 / 3 40; F 41 / 28 / 30;
  C 52 / 30 / 18 (%). ESPN lists some centers as F (Sabonis, Gafford, Diabate).
- Game market: P(method) = P(away scores first) x away split + P(home first) x home split. A team's split
  = league rate x (team offense rate / league) x (opponent's allowed rate / league), each team rate
  shrunk toward the league with `K_TEAM` = 80 pseudo games, renormalized. Team first points and team
  first FG (both teams per game) are the sample, 26-27 games x B3 weight.
- Player prop: P(first basket) (model v2) x P(method | he scores first). P(method | first) = his own team-first
  FG methods (weighted counts) shrunk with `K_PLAYER` = 40 toward a prior = position first-FG mix x
  (his made-FG mix / position made-FG mix), his made mix shrunk toward the position with `K_MIX` = 10 makes.
- Check (`python3 analysis/nba/fb_method.py --base`): fit on 2025-26 games before 2/1/26, scored on the
  rest plus 2026-27 (1,146 team first FGs). Player method log loss: league 1.094, position 1.078, mix prior
  0.948, model 0.947. His overall shot mix is the real signal; his first-FG history adds almost nothing
  (samples are 5 to 25 first FGs), so it is weighted lightly. Team game split: first points 1.324 league vs
  1.315 model, first FG 1.094 vs 1.086. Small gain; game-level method is mostly the league rate.
- Output: the tab gets "First basket method: game level" (each slate game: P away first, first points
  split incl FT, first FG split, fair odds) and "First basket method: player props" (top 24 candidates:
  P(FB), the method split if he scores first, P and fair odds for FB dunk/layup, FB 2pt jumper, FB 3PT,
  and the weighted samples). `out/shortlist.md` has a "First basket method" section with the game
  splits and the 8 best player + method combos (max 3 per game).
- Minimum price: we log fair plus a 10% cushion (fair probability / 1.1) as "take X or better". These are
  long shots stacked on a noisy market; 0.20 to 0.50 stakes.
- first_events log: columns `first_basket_method` and `first_points_method` since 10/29 (backfilled for
  every NBA row from the cache with `python3 analysis/first_events.py --backfill-methods`).

## Model changes 10/30/26 (Tim approved, from `analysis/reports/2026-10-30-picks-vs-startool.md`)

Backtest: `python3 analysis/nba/backtest_fb.py --jumper` (walk-forward, current model V2 + ramp, actual starters and
jumpers, priced pregame through our tip chance; log loss renormalized over the 10 starters, uniform 2.303).

1. **Jumper split** (`JB`, `jumper_split` in build_nba_tab.py). The tip jumper's share of his team's first FG is
   x1.2 when his team wins the tip and x0.95 when it loses; the other four are rescaled so the team total holds.
   P(FB) = P(win tip) x 64% x boosted share + P(lose tip) x 36% x cut share.
2. **Top-end shrink** (`TOP`, `shrink_top`). Each game's 10 final chances are raised to the power 0.8 and rescaled to
   the same total. It pulls 15%+ chances in and lifts the under-8% names (they ran hot and cold). 0.8 is the 2025-26
   optimum (0.75 to 0.8 is flat); the report's guess was 0.9, which also helps but less.

| Model | 25-26 log loss (933) | 25-26 top pick hits | 26-27 log loss (71) | 26-27 top pick hits | Jumper FB expected / actual (25-26; 26-27) |
|---|---|---|---|---|---|
| Before (10/23 model) | 2.2826 | 131 | 2.2912 | 9 | 201.0 / 224; 16.0 / 20 |
| + jumper 1.2 / 0.95 | 2.2808 | 136 | 2.2875 | 10 | 223.1 / 224; 17.8 / 20 |
| + temp 0.9 | 2.2789 | 136 | 2.2838 | 10 | 219.0 / 224; 17.4 / 20 |
| **+ temp 0.8 (used)** | **2.2778** | 136 | **2.2813** | 10 | 215.0 / 224; 17.0 / 20 |

Calibration, 25-26, 15%+ chances: before 466 at 16.6% predicted vs 15.0% hit; after 280 at 16.5% vs 14.3%; 17%+ before
18.5% vs 15.0%. Under 8%: 6.6% vs 7.7% before, 6.9% vs 7.4% after. Brier 0.8958 to 0.8947. The 26-27 numbers through 10/29
are 71 games (the report's 68 plus 10/29). Gains are small; first basket is still mostly noise. Pick text marks the jumper
("tip jumper x1.2 if his team wins the tip"). `out/fb_candidates.json` keeps the pre-fix chance (`p_before_10_30_fix`).

3. **No StarTool blend.** Tim rejected it 10/30 (the gain could be zero). StarTool stays side by side only.
   Save each card's star/bomb in `out/startool/star_bomb.txt` (`date|AWAY @ HOME|star,star|bomb,bomb`, names as printed)
   and rerun the build: the shortlist's "StarTool check" section flags each game "agree (StarTool star)", "agree (StarTool
   bomb)" or "differs" when our top first basket pick is (or is not) one of its stars or bombs. Code: `agree_flag` in
   `analysis/parlays.py`. The NHL build does the same with our top anytime goal pick per game.
4. **Parlays** (`analysis/parlays.py`, a combined "## Parlays" section written into this shortlist and the NHL one, and the
   UCL one on matchdays). Legs only from categories that beat their price season to date: NBA 3+ threes, NHL 3+ SOG,
   NFL receptions, soccer 1+ shot on target. Never NBA points overs (singles only, at a higher alt line), never first
   basket, first goal or anytime goal. Each build writes `out/parlay_legs.json`; NFL receptions have no build, so write
   `analysis/nfl/out/parlay_legs.json` by hand (same format: date, sport "NFL", legs with player, team, game "AWAY @ HOME",
   market "4+ receptions", p) and run `python3 analysis/parlays.py <date>`. Rules: 2 or 3 legs, leg chance 55% to 88%,
   different games first (a same-game combo is marked correlated; its fair price is the plain product, so it is
   optimistic), each leg in at most two parlays. Fair = product of the leg chances. Minimum FanDuel price = fair chance /
   1.1 (10% cushion). Stake $0.10 to $0.20.
5. **-300 rule in the build** (Tim 10/29). Points and threes picks over 75% (fair shorter than -300) now say "take over X
   instead" with the next line's rate and fair price. Points picks say "singles only, never in a parlay".

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

- 10/24: center pattern cooled. Only 1 of 8 first baskets was a starting center (Adebayo). Running total 7 of 22 (10/22-10/24). StarTool bombs hit 4 of 16 (Adebayo, Young, Fox, Lendeborg); stars 0 of 16. Hold the 1.2x jumper fix until it's backtested.

- 10/28: our first basket picks 2 of 7 graded (Adebayo, Murray; Doncic DNP, void). StarTool stars 3 of 24 (Siakam, Herro,
  Flagg); bombs 4 (Adebayo, C. Wilson, Murray, Fox). Starting centers scored 2 of 12 (Adebayo, Carter). 5 of 12 first baskets
  came on the game's first shot. Tim's round robin cashed one combo: Adebayo + Murray with the Doncic leg voided.
- 10/29: first basket method added (see section above). Logged 5 player + method picks for 10/29 (Bets rows 506-510).
- 10/29 rule (Tim): skip props priced shorter than about -300; offer the next line up (25+ points instead of 20+,
  3+ threes instead of 2+, 3+ SOG instead of 2+).
- 10/30 (Tim approved the 10/30 report): jumper split x1.2 / x0.95 and top-end shrink (power 0.8) applied; StarTool
  blend rejected (side by side plus an agree flag only); daily parlays only from 3+ threes, 3+ SOG, receptions and soccer
  SOT; NHL anytime goal x0.77 and only at +150 or longer. See "Model changes 10/30/26".

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
| 10/24 | MIA @ CHA 6:00 | Bam Adebayo MIA (center) | Giannis, Adebayo (from StarTool allow ranks) | Giannis / Miller (bombs Adebayo, Knueppel) | Adebayo | Yes (Adebayo) / StarTool star No (bomb Adebayo hit) | Yes |
| 10/24 | BKN @ CLE 7:30 | Peyton Watson CLE | Mitchell, Allen (from StarTool allow ranks) | Porter Jr. / Mitchell | Mobley (center: Allen) | No / StarTool star No | No |
| 10/24 | MIL @ PHI 7:30 | Dean Wade PHI | (none sent) | Herro / Maxey | Jaylen Brown | - / StarTool star No | No |
| 10/24 | WSH @ CHI 8:00 | Trae Young WSH | Kyshawn George, Sarr, Powell (from StarTool allow ranks) | Davis / Powell | Jalen Smith | No / StarTool star No (bomb Young hit) | No |
| 10/24 | SA @ DAL 8:00 | De'Aaron Fox SA | Wembanyama, Fox (from StarTool allow ranks) | Wembanyama / Flagg (out) | Wembanyama | Yes (Fox) / StarTool star No (bomb Fox hit) | No |
| 10/24 | HOU @ ATL 8:30 | Dyson Daniels ATL | Okongwu, Jabari Smith, Sengun (from StarTool allow ranks) | Durant / Alexander-Walker | Sengun | No / StarTool star No | No |
| 10/24 | NO @ DEN 9:00 | Aaron Gordon DEN | Murray, Jokic (from StarTool allow ranks) | Murphy / Jokic | Murray (center: Jokic) | No / StarTool star No | No |
| 10/24 | GS @ PHX 10:00 | Yaxel Lendeborg GS | Booker, Miles Bridges (from StarTool allow ranks) | Curry / Booker | Jalen Green | No / StarTool star No (bomb Lendeborg hit) | No |
| 10/25 | LAL @ UTAH | Luka Doncic (first shot, made) | Doncic, Ziaire Williams | Doncic / Markkanen | Kessler, Doncic | Yes (Doncic) | Yes (Doncic) |
| 10/25 | IND @ BKN | Ivica Zubac IND, center (first shot Siakam, missed) | Siakam, Nembhard, Randle | Siakam / Porter Jr. | Porter Jr., Zubac | No | Yes (Zubac) |
| 10/25 | ORL @ NY | Jalen Brunson NY (first shot W. Carter, missed) | F. Wagner, Suggs | Banchero / Brunson (StarTool star hit) | - | No | - |
| 10/25 | TOR @ MIN | Rudy Gobert MIN, center (first shot Barnes, missed) | Leonard (DNP), Barrett | Leonard / Edwards | Edwards | No | No |
| 10/25 | LAC @ OKC | Isaiah Jackson LAC, center (first shot, made) | SGA, Jalen Williams, Hachimura | Garland / SGA | Cason Wallace | No | No |
| 10/25 | DET @ PHI | John Collins DET (first shot Robinson, missed) | Ausar Thompson, Edgecombe, Jaylen Brown | Cunningham / Embiid | Jaylen Brown | No | No |
| 10/25 | MEM @ SAC | Zach LaVine SAC (first shot, made; StarTool bomb hit) | Sabonis, Hunter | Jerome / Acuff Jr. | Ty Jerome | No | No |
| 10/28 | MIA @ ATL | Bam Adebayo MIA, center (first shot, made) | Adebayo (placed our list) | Giannis / Alexander-Walker (bomb Adebayo hit) | Adebayo | Yes | Yes |
| 10/28 | WSH @ CLE | Alex Sarr WSH (first shot Watson CLE, missed) | - | Davis / Mitchell | - | - | - |
| 10/28 | CHA @ DET | Naz Reid CHA (first shot Collins DET, missed) | Miller, Reed | Miller / Cunningham | Miller, Reed | No | No |
| 10/28 | PHI @ IND | Pascal Siakam IND (first shot Edgecombe, missed) | - | J. Brown / Siakam (StarTool star hit) | - | - | - |
| 10/28 | ORL @ TOR | Wendell Carter Jr. ORL, center (first shot, made) | - | Bane / Barrett | - | - | - |
| 10/28 | NY @ CHI | Caleb Wilson CHI (first shot Brunson, missed) | - | Brunson / Powell (bomb C. Wilson hit) | - | - | - |
| 10/28 | HOU @ MIL | Tyler Herro MIL (first shot VanVleet, missed) | - | Durant / Herro (StarTool star hit) | - | - | - |
| 10/28 | GS @ MIN | Jaden McDaniels MIN (first shot Green, missed) | - | Curry / LaMelo | - | - | - |
| 10/28 | DEN @ NO | Jamal Murray DEN (first shot, made) | Murray | Jokic / Murphy (bomb Murray hit) | Murray | Yes | Yes |
| 10/28 | SA @ UTAH | De'Aaron Fox SA (first shot, made) | Wembanyama | Wembanyama / Markkanen (bomb Fox hit) | Wembanyama | No | No |
| 10/28 | OKC @ DAL | Cooper Flagg DAL (first shot A. Mitchell, missed) | Ajay Mitchell | SGA / Flagg (StarTool star hit) | Ajay Mitchell | No | No |
| 10/28 | LAL @ LAC | Matisse Thybulle LAL (first shot, made); Doncic DNP | Doncic (void), Kessler | Doncic / Garland | Doncic (void), Kessler | No | No |
| 10/29 | CLE @ ATL | James Harden CLE, driving layup (rim) at 10:27 (first shot Watson three, missed; first points Mobley FTs) | (none sent) | Mitchell / NAW (bomb Harden hit) | Allen, Mobley; method Allen rim | - | No |
| 10/29 | SAC @ NO | Trey Murphy III NO, running dunk (rim) (first shot Hunter, missed) | (none sent) | Acuff / Murphy (StarTool star hit) | Sabonis, LaVine; method Sabonis rim, Zion rim | - | No |
| 10/29 | MEM @ POR | Zach Edey MEM, center, dunk (rim) off Boozer (first shot Camara three, missed) | (none sent) | Jerome / Avdija | Jerome, Coward; method Jerome j2, Coward 3 | - | No |
