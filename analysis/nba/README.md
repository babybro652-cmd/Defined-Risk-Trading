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

- First basket (FB) = first made field goal of the game. CORRECTION (Tim, 11/4): FanDuel
  credited Giannis's free throw over Bam's layup in MIA@LAC, so FanDuel settles on the first
  POINTS, free throws included. Grade Tim's FanDuel first basket bets on "First pts incl FT".
  Since 11/5 the model's target is first points incl FT (see "Model change 11/5/26").
- Team 1st = the player made his team's first field goal. 1st shot = he took the team's first
  field-goal attempt. All three count only games he started.
- Opening tip = the first jump ball in the 1st quarter; the winner is the team that gains
  possession.
- Blend = (W x 26-27 count + 25-26 count) / (W x 26-27 starts + 25-26 starts), W in B3.
  Preseason is shown but left out of the blend (starters rest, lineups are experiments).
- Estimated FB chance (model v2, 10/21/26) = P(team scores first) x the player's share of his team's
  first FG. P(team scores first) comes from the two main jumpers' tip rates (log5, each shrunk toward 50%
  with 6 pseudo tips) and the 2025-26 league rate that the tip winner scores first (64%).
  Since 10/30: the jumper split and top-end shrink below ("Model changes 10/30/26"). Since 11/2: the first-3-FGA share
  (half the share, "Model change 11/2/26").
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

## Model change 11/2/26: first-3-FGA share (Tim approved the test)

Idea from the @nbafirstbasket sheet's "# of 1st 3 shot attempts": how many of his team's first 3 field-goal attempts a
starter takes per start (early shot volume). Code: `first3.py` (cache `data/first3_<season>.json`, game id -> each team's
first 3 FGA shooters, FTs excluded; checked: the first entry matches the cached first shot in all 2,654 team-games) and
`w3` in `V2` / `v2_shares`. Step 1 of the share is now: 0.5 x (old accuracy blend) + 0.5 x first-3 share, where first-3
share = (his first-3 FGA / 3 + k / 5) / (starts + k), the same shrink toward 1 in 5 with the same pseudo starts (10, more
for new starters) and the same 26-27 weight ramp. Defense, ripple, jumper split and top-end shrink (0.8) are unchanged.

Backtest `python3 analysis/nba/backtest_fb.py --first3` (walk-forward, current model, log loss over the 10 starters):

| w3 | 25-26 log loss (933) | Brier | top pick hits | 26-27 log loss (92) | Brier | top pick hits |
|---|---|---|---|---|---|---|
| 0 (before) | 2.2778 | 0.8947 | 136 | 2.2894 | 0.8958 | 13 |
| 0.15 | 2.2760 | 0.8944 | 134 | 2.2840 | 0.8948 | 13 |
| 0.25 | 2.2750 | 0.8942 | 133 | 2.2808 | 0.8943 | 13 |
| 0.35 | 2.2742 | 0.8940 | 136 | 2.2779 | 0.8937 | 14 |
| **0.5 (used)** | **2.2734** | 0.8938 | **140** | **2.2741** | 0.8930 | 13 |
| 0.65 | 2.2730 | 0.8937 | 137 | 2.2709 | 0.8924 | 13 |
| 1.0 | 2.2739 | 0.8939 | 137 | 2.2653 | 0.8914 | 13 |

The gain kept growing past the planned 0.35, so 0.5 was picked on 2025-26 (0.5 to 0.65 is flat in log loss; 0.5 has the
best top pick). Multiplying the first-3 share by FG% lowers 25-26 log loss a bit more (0.5: 2.2727) but costs top-pick hits
(135; 127 at 0.8), so it is off. Paired per game, w3 = 0.5 vs before: 25-26 log loss down 0.0045 (SE 0.0023), 26-27 down
0.0152 (SE 0.0084), about 1.9 SE each. A bigger gain than the 10/30 changes, still small: first basket is mostly noise.
Retuning the top-end shrink with it in was flat (0.9 helps 25-26 by 0.0005, hurts 26-27), so 0.8 stays.
Top pick changed in 157 of 933 25-26 games. Pick text now shows "first 3 FGA x.xx per start".

## Model change 11/5/26: first points target + shot type (Tim approved the backtest)

Why: 11/2 and 11/4 our top picks went 1/15 and 3/14 (about the 14% we predict), but none took the game's first FGA on
11/2, and 7 of 14 first baskets on 11/4 were 3s, often by role players. FanDuel settles on first POINTS incl FT (11/4).

Data: `opening.py` caches one ESPN summary per game in `data/opening_<season>.json`: each team's first points scorer
(FT included), its shooting events up to its first score, and every player's attempts and makes by rim / j2 / 3 plus FT
trips (the build fetches new games itself). First points differ from the first made FG in 8% of 25-26 games (102 of 1,235).

Backtest `python3 analysis/nba/backtest_fix.py` (walk-forward, no lookahead, actual starters and jumpers, jumper split
and shrink 0.8 as built; target = first points incl FT; log loss over the 10 starters; SE = paired per game vs current):

| Model | LL 25-26 (933) | LL 26-27 (107) | Brier 25 / 26 | Top pick hit 25 / 26 | Top pick took team 1st FGA 25 / 26 |
|---|---|---|---|---|---|
| Current (11/2) | 2.2705 | 2.2486 | .8931 / .8886 | 140 (15.0%) / 14 (13.1%) | 286 / 26 |
| Fix 1: fit on first points | 2.2692 | 2.2447 | .8928 / .8876 | 140 / 16 | 285 / 28 |
| Fix 2: recent opening share (best: last 20 starts, k 10, w 0.25) | 2.2727 | 2.2457 | .8935 / .8881 | 140 / 16 | 281 / 26 |
| Fix 3: shot type w 0.7 | 2.2686 | 2.2317 | .8927 / .8856 | 133 / 17 | 266 / 26 |
| **Fix 1 + 3 (used)** | **2.2679** (SE .0022) | **2.2294** (SE .0056) | .8925 / .8850 | 133 (14.3%) / 17 (15.9%) | 272 / 25 |
| All three (fix 2 w 0.1) | 2.2706 | 2.2291 | .8929 / .8849 | 138 / 18 | 268 / 25 |

- Fix 1: share counts his team's first POINTS (`tp1`), tip-winner-scores-first rate on first points (66% vs 64%). Better on both.
- Fix 2: his share of his team's first FGA over his last N starts with this team (shrunk toward his season first-shot
  share), x FG% / league. Worse on 25-26 at every setting (N 10/15/20, w 0.1 to 0.7, added or replacing the season
  first-shot term); helps 26-27 a little. Not adopted: the season first-shot and first-3 shares already hold the signal and
  a 15 to 20 start window is mostly noise.
- Fix 3: event share x scoring chance. Early FGA share (half first shot, half first 3 FGA) x [his FGA mix rim / j2 / 3
  (shrunk to his position, 30 attempts) x his make rates (shrunk to league 63% / 45% / 36%, 40 attempts) + FT trips per
  FGA (shrunk, 100 FGA) x trips scored (91% league, 20 trips)], normalized per team, 70% of the share. Better on both at
  every weight (25-26 flat from 0.55 to 1.0; 0.7 picked). The FT term helps (no-FT version 2.2696 / 2.2378).
- Calibration by decile, 25-26 (pred / hit), current: 6.7/6.8 ... 12.0/12.5, top 14.1/16.2; new: 6.3/6.6 ... 12.3/12.1,
  top 14.8/15.4. The top decile was underpriced and is now close.
- Trade-off: top-pick hits drop on 25-26 (140 to 133) and rise on 26-27 (14 to 17); the top pick takes the team's first FGA
  slightly less often (it leans to efficient finishers and FT drawers, less to volume first shooters).
- Value sim (assumption, no Tim odds): FanDuel's view = the plain season model (team first FG share x tip chance) with a
  30% overround on the starters (FanDuel first basket boards sum to about 125 to 140%). Bet only when the price beats our
  fair by 20%+: current 2.1 bets/night (25-26) and 3.4 (26-27); new 2.8 and 3.9. Fewer than 3 or 4 a night either way.

Code: `FP` and the `fit_fp` / `w_shot3` branch of `v2_shares` in build_nba_tab.py; default `--fb-model fp`, and
`--fb-model fg` rebuilds with the 11/2 model. backtest_fix.py runs the adopted variants through the build's `v2_shares`
(checked: same numbers as its own copy). Gains are small; first basket is still mostly noise.

## Model change 11/5/26 (chain): first-possession chain + two-slot picks (Tim's idea, adopted)

Tim: "Who takes the first shot is important only if they are hitting more than missing, and if they are missing then
the second pick should be next in line." Example: Giannis took MIA's first shot 1 of 8 starts but scored MIA's first
points 4 of 8 (2 FT trips, putbacks after misses).

Model (`chain_model.py`, default `--fb-model chain`; `--fb-model fp` = the 11/5 morning model, `fg` = 11/2): the opening is
played possession by possession until someone scores (exact Markov chain, no simulation).
- Tip: jumper vs jumper tip chance decides who has the ball first. The tip winner's jumper gets x1.2 on his first-shot
  share in that first possession (`jq`).
- Each possession (or reset after an offensive rebound): turnover with the team's TO rate per possession end (offense x
  opponent, shrunk; league 12.3%). Else one starter ends it: first possession by his first-FGA share, later ones by his
  first-3-FGA share, both shrunk hard to his usage (FGA + FT trips per minute) with 50 pseudo starts (`k_sh1`, `k_f3`).
- His event: FT trip with his trip share (trips / (trips + FGA), and-ones excluded; league 10%), scores with his trip
  rate (94%); or an FGA that scores with his shot-type make rate (rim / j2 / 3 mix x make rates, as the 11/5 term).
- Miss: offensive rebound with the team's rate vs the opponent (league 31% after a missed FG, team rebounds included).
  Rebounder split by OREB per minute (shrunk to position). He takes a putback with his putback rate (league 53% of
  OREBs, scores 60%), else a reset possession. Otherwise the other team's possession.
- No top-end shrink (the chain is calibrated without it; temp 0.8 and 0.9 were worse once `k_sh1` was 50).

Data: `chain_data.py` caches one ESPN summary per game in `data/chain_<season>.json`: per player OREB, DREB, turnovers,
putback tries and makes, FT trips without and-ones, FGA; per team missed FG, OREB after a miss, turnovers; the opening
event sequence up to the first points. The build fetches new games itself.

Backtest `python3 analysis/nba/backtest_chain.py` (walk-forward, no lookahead, actual starters and jumpers, same games
and same "current" numbers as backtest_fix.py; target = first points incl FT; log loss over the 10 starters; SE paired
per game vs current). `--grid` runs the tuning grid; tuned on 25-26 only.

| Model | LL 25-26 (933) | LL 26-27 (121) | Brier 25 / 26 | Top pick hits 25 / 26 |
|---|---|---|---|---|
| Current (11/5 first points + shot type) | 2.2679 | 2.2417 | .8925 / .8867 | 133 / 18 |
| Chain, first-shot share k 8 | 2.2660 | 2.2378 | .8919 / .8860 | 146 / 19 |
| **Chain, k 50 (used)** | **2.2552** (SE .0046) | **2.2204** (SE .0111) | .8897 / .8819 | 139 / 21 |
| Blend 50/50 current + chain (k 8) | 2.2638 | 2.2364 | .8915 / .8856 | 142 / 19 |

- Better on both seasons (-0.013 and -0.021, about 2.8 and 1.9 SE). The big gain came from shrinking the first-shot share
  toward usage: who took the first shot in past games is mostly noise; who shoots, makes, draws fouls and rebounds is not.
- Calibration by decile, 25-26 (pred / hit): current 6.3/6.6 ... 12.3/12.1, top 14.8/15.4; chain 5.6/5.9, 6.9/6.8, 7.8/7.9,
  8.5/8.8, 9.2/9.8, 10.0/7.8, 10.8/11.0, 11.8/11.8, 13.1/14.1, top 16.3/16.1. Wider spread, still on the line.
- Flat (within 0.0005): usage shrink k_u 50 to 400, OREB k 50 to 500, putback k 5 to 60, make-rate k 15 to 100, trip k 300.

Two-slot pick rule (adopted for Tim's reports). Per team: **1st-shot pick** = most likely to score on the team's first
shot event (takes it x makes it, or draws FTs and scores); **2nd-chance pick** = the other starter most likely to score
the team's first points after a miss or turnover (team first points chance minus the first-event part). Pair coverage =
the team's first points scorer is one of its two picks (2 teams per game); game = the game's first points scorer is one
of the 4 picks.

| Rule | Team pair 25-26 (1,866) | Team pair 26-27 (242) | Game 4 picks 25-26 | Game 4 picks 26-27 |
|---|---|---|---|---|
| Current model top 2 | 47.9% | 43.4% | 49.2% | 51.2% |
| Chain top 2 | 47.7% | 48.8% | 50.1% | 57.0% |
| **Two-slot (used)** | **48.2%** | **48.3%** | 49.9% | 57.0% |

Slot 1 alone hit 26.2% / 20.2% of team first points, slot 2 alone 22.0% / 28.1%. Two-slot beats our old top 2 on both
seasons; it ties the chain's own top 2 (pick either; the two-slot pair says why each name is there). Small gains: first
basket is still mostly noise.

Report format (Tim's reports, confirmed-lineup reruns): per game the projected tip winner and tip %, then per team (tip
favorite first) "1st-shot pick" and "2nd-chance pick" with each one's chance to score the GAME's first points and fair
price. The shortlist writes this in "First basket two-slot picks (chain model)". Bet only past fair.

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
- 11/5 team-change rule (Tim asked: score Giannis on Miami only): tested in `backtest_teamchange.py` (starts with other teams count `prior` x, optional ramp). Every setting made 26-27 log loss worse (base 2.2417; prior 0.5 2.2447, 0.25 2.2473, 0.25 ramp 10 2.2438) and 25-26 was flat (2.2679 vs 2.2678 best). Not adopted. Giannis with MIA: 4 of 8 MIA first points (2 FT, rim, jumper), 3 of 8 game first points, 1 of 8 MIA first FGA; the model has him at 19% of MIA's first points because he rarely takes the first shot. Watch it; revisit after 15+ MIA starts.
- 11/5 grading rule: FanDuel settles first basket on the first points, free throws included (Bam 11/4 graded L when Giannis hit a FT first). Grade Tim's FB bets on `first_points_any` in analysis/first_events/log.csv. A free throw came first in 13 of 121 logged games (11%), 10/20 to 11/4. Regrade flipped row 286 (Sabonis 10/23) to W.
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

- 10/30 results: first basket 1-6 plus Sengun void (Adebayo +416 fair hit); points 2-1; threes 3-1 (Doncic 6, Curry 8,
  Miller 3; MPJ 2); method props 0-4. StarTool stars 2 of 20 (Porter Jr., LaMelo), bombs 1 (Adebayo). Tip jumpers scored
  1 of 10 first baskets (Adebayo); 6 of 10 first baskets came from the tip-winning team. Our tip favorites lost twice at
  90%+ (LAL 96% vs Green, DAL won with Gafford vs Capela, a jumper change). Tim had no first basket picks logged.
- 10/31 to 11/2: Jarvis offline Fri evening to Mon noon; no picks logged for 10/31 or 11/1, first events logged only.
- 11/2: daylight saving ended 11/1 (ET = UTC-5). The NBA build already uses America/New_York; the NHL build had a fixed UTC-4 and now uses zoneinfo too. 11/2 picks: Bets rows 544-574.
- 11/2: first-3-FGA share added (w3 = 0.5, see "Model change 11/2/26"). Rebuilt the 11/2 tab: first basket top 8 swaps
  Jokic and Jalen Green (logged rows 549 and 551) for Ty Jerome (fair +519) and LaMelo Ball (+551); game top picks changed
  in CHA@DET (Reed to Collins), CHI@PHI (Smith to Embiid), DAL@SAC (Sabonis to Hunter). Bets rows left as logged.
- 11/2 results: first basket 0-13 (Paul George void). 11/3 no games.
- 11/4: 14-game slate, tab rebuilt (107 26-27 games). Bets rows 642-657: 8 first basket, 5 threes, 3 points. Top FB picks are mostly
  tip-favorite centers and stars (Wembanyama, Adebayo); after 0-13 on 11/2 keep stakes at $0.20 to $0.50 and bet only past fair.

- 11/5: first points model (fix 1 + 3 above) is the default. Tested and dropped the recent opening-play share (fix 2).
- 11/5 evening: chain model (Tim's idea) replaces it as the default, and reports use the two-slot picks (1st-shot pick, 2nd-chance pick per team). See "Model change 11/5/26 (chain)". Giannis moves to MIA's 2nd-chance pick (16%, fair +514 tonight vs 12% before).

- 11/5 results: placed 10-19, net -$0.48 on $0.20 stakes. Wiggins FB hit at +750 (fair +835, below fair); Bam, Carter, Wagner missed. Booker scored ORL@PHX's first points on FTs (the FT rule again). NHL 3+ SOG 2-2 plus DeBrincat 4+ hit, both SOG parlays hit; NFL JAX@BAL receptions 0-4 with a 3rd-string QB.

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
| 10/30 | CHA @ WSH | Dennis Schroder CHA, 3 (CHA won tip; first shot Schroder, made) | - | Miller / Davis | Anthony Davis | - | No |
| 10/30 | CHI @ BOS | Jayson Tatum BOS, rim (BOS won tip; first shot Tatum, made) | - | Powell / Tatum (StarTool star hit) | Paul George | - | No |
| 10/30 | DET @ BKN | Michael Porter Jr. BKN, rim (BKN won tip; first shot, made) | - | Cunningham / Porter Jr. (StarTool star hit) | Paul Reed | - | No |
| 10/30 | NY @ PHI | OG Anunoby NY, 3 (NY won tip; first shot Towns, missed; first points Embiid FTs) | - | Brunson / J. Brown | Tyrese Maxey | - | No |
| 10/30 | ORL @ TOR | Scottie Barnes TOR, j2 (TOR won tip; Barnes missed first shot, scored next) | - | Bane / Barrett | Wendell Carter Jr. | - | No |
| 10/30 | IND @ MIA | Bam Adebayo MIA, center, rim (MIA won tip; first shot, made) | - | Siakam / Giannis (bomb Adebayo hit) | Bam Adebayo | - | Yes (fair +416) |
| 10/30 | HOU @ DAL | Fred VanVleet HOU, j2 (DAL won tip; Capela jumped for HOU, Sengun out) | - | Durant / Flagg | Kevin Durant (Sengun void) | - | No |
| 10/30 | LAC @ MIN | LaMelo Ball MIN, 3 (MIN won tip; first shot, made) | - | Garland / LaMelo (StarTool star hit) | Jaden McDaniels | - | No |
| 10/30 | LAL @ GS | Brandin Podziemski GS, rim (GS won tip, our LAL 96% missed; first shot, made) | - | Doncic / Curry | Walker Kessler | - | No |
| 10/30 | DEN @ PHX | Miles Bridges PHX, j2 (PHX won tip; first shot Brooks, missed) | - | Jokic / Booker | Nikola Jokic | - | No |
| 11/5 | ORL @ PHX | Devin Booker PHX, free throws (first shot Brooks, missed; first FG Bane) | Carter, Wagner (our list) | Bane / Booker (StarTool star Booker hit) | Carter, Wagner | No | No |
| 11/5 | MIA @ GS | Andrew Wiggins MIA, j2 (first shot, made) | Bam, Wiggins (+750) | Giannis / Curry | Bam, Giannis (Wiggins third, fair +835) | Yes (Wiggins) | No |
- 11/6: 10:07 refresh. Injury recheck at 10:10 AM ET: no changes (Davis, Jalen Johnson, Diabate, Allen, Watson, Barnes still questionable and in RotoWire's expected fives; Knueppel out). Rebuilt with the 6:25 AM lineups file, chain model; picks unchanged. Bets rows 690-703 (9 first basket, 3 threes, 2 points), all "Pick".
- 11/6 5:40 PM: WSH @ ATL rerun. Davis and Jalen Johnson off the FanDuel board (ESPN: Johnson out, Davis questionable), treated OUT. WSH five Young, George, Dybantsa, Sarr, Ayton (Ayton jumps); ATL five Flemings, NAW, Daniels, Dort, Okongwu. Tip WSH 70%. Top Sarr 14% (+619). Board check: all 10 SKIP (none at take-at = fair x1.2). Bets row 692 changed from Davis to Sarr.
- 11/6 5:50 PM: TOR @ MIL rerun. Barnes off the FanDuel board, treated OUT; Collin Murray-Boyles starts. Tip TOR 78% (Poeltl vs Turner). Top Barrett 16% (+528), Murray-Boyles 16% (+529). Board check: all 10 SKIP (Barrett and Murray-Boyles +650 beat fair, miss take-at +654/+655). Bets row 693 changed from Barnes to Barrett.
- 11/6 6:30 PM recheck (ESPN + RotoWire): Davis officially OUT. BOS @ CHA: Diabate OUT, Kalkbrenner starts and jumps; tip flips to CHA 57%; Reid top 14% (+607); Tatum +615 -> +686 (row 695). OKC @ MEM: Caruso starts for Aday Mara; Jerome +620 -> +606 (row 696). PHI @ CLE (Allen, Watson still questionable, in RotoWire five), UTAH @ DAL, MIN @ NO (Murphy off injury list): no change. RotoWire lists Coulibaly, not Ayton, for WSH; kept the FanDuel board five.
- 11/6 9:30 PM recheck (ESPN + RotoWire, expected lineups): POR @ LAL no change. SA @ SAC: De'Andre Hunter OUT, Malik Monk starts; Wembanyama +296 -> +297 (row 690); SAC chances up slightly (LaVine +1279, Sabonis +1152).
