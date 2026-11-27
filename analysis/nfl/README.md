# NFL Scorer Tracker

Builds the Google Sheet **NFL Scorer Tracker 2026**
(https://docs.google.com/spreadsheets/d/1VPYeOtn3BGq4JYPiwkI_XfvVXCGyvg7nMhGGOzl2VTM/edit,
spreadsheet ID `1VPYeOtn3BGq4JYPiwkI_XfvVXCGyvg7nMhGGOzl2VTM`) from ESPN box scores,
play-by-play and the ESPN injuries feed. Small stakes, for fun.

## Weekly refresh (Tuesday, after Monday night)

1. Rebuild every tab. `--week` is the last 2026 week to include:

   ```
   python3 analysis/nfl/build_tracker.py --week 5
   ```

   It downloads only the new 2026 games (parsed games are cached in `data/`), then writes:
   - `out/sheet_values.json`: every tab as a 2D array, ready for the Sheets connector
     (text like `3/4` is prefixed with `'` so Sheets does not turn it into a date)
   - `out/*.csv`: the same tabs as CSV
   - `out/rank_2026.md`: the 2026-only top 15 TD and receptions tables for the report

   A game inside `--week` that is not final yet is skipped and named on the Notes tab;
   rerun the same command after it ends.

2. Push to the sheet with the Google Sheets connector, one tab at a time:
   `batch_clear_values` on `'<Tab>'!A2:AD500`, then `update_values` with range `'<Tab>'!A1`
   and the tab's array from `out/sheet_values.json`. Tabs: Scorers, Red Zone, Injuries,
   Defense, Week Shortlist, Notes. To print one tab:

   ```
   python3 -c "import json;print(json.dumps(json.load(open('analysis/nfl/out/sheet_values.json'))['Scorers']))"
   ```

3. Commit `data/` and `out/` so the next run starts from the cache.

## Mid-week (after TNF)

```
python3 analysis/nfl/build_tracker.py --week 5 --slate 5
```

Adds the Thursday game to the stats and keeps the Week Shortlist on the rest of Week 5
(`--slate` defaults to `--week + 1`). The unplayed games show as "not final" on Notes.

## Saturday injury recheck

```
python3 analysis/nfl/build_tracker.py --week 5 --slate 5 --injuries-only
```

Refreshes only Injuries, Week Shortlist and Notes from the live injuries feed (no game downloads).
Push those three tabs.

## How numbers are computed

- TD = rushing + receiving TD (no return or passing TDs). Hit % = games with a TD / games played.
- RZ opp = target or carry on a play that started inside the opponent 20 (i10 = inside the 10),
  counted from play-by-play text, penalties excluded. Estimates, not official counts.
- Defense rank #1 = allows the most to that position (softest). RZ TD% allowed = opponent drives
  with a play inside the 20 that ended in a TD.
- Week Shortlist uses TD model v2 (below); the verdict rule is written on the Notes tab. The old hit-rate verdict stays in the last column.
- Inside-5 opps (`i5`) = carry or target on a play that started inside the opponent 5; goal-line share = a player's i5 / his team's i5 in the games he played. Cached games are schema 3 (adds i5, RZ targets, QBs, game odds); older caches re-download automatically.
- Sources that block scripts (Pro-Football-Reference, FootballDB) are not used; routes run and
  snap counts are not available.

## TD model v2 (11/8/26): backtest and rules

Why: anytime TD singles went 18-22 in Weeks 5-9 (RB/QB 16-10, WR/TE 2-12, plus odds 2-8). The old method (2025+2026 hit rate)
was overconfident for WR/TE and small samples.

Code: `analysis/nfl/td_model.py` (model + backtest, `python3 analysis/nfl/td_model.py` writes `out/td_backtest.txt` and `.json`);
`build_tracker.py` feeds it to the Week Shortlist. Spread and total come from the ESPN pickcenter (core odds as fallback);
implied team total = total/2 -/+ spread/2, divided by the league average implied total (ln ratio is the feature).

Model (every input uses only games before the one being scored):
1. Shrunk hit rate: (TD games + 6 x prior) / (games + 6). Prior = hit rate of players at the same position (RB, WR, TE, QB) in the same
   usage bin (red-zone + 2 x inside-5 opps per game).
2. Implied team total vs league average.
3. Goal-line share: player inside-5 opps / team inside-5 opps (8 pseudo team opps added to the denominator).
4. Red-zone share, and red-zone target share for WR/TE.
5. Ridge logistic regression on those plus position, refit before every week on all earlier games (2025 + earlier 2026).
6. Backup-QB flag as a model input: the QB expected to start (depth chart, skipping Out/Doubtful/IR) is not the team primary (most pass
   attempts over its last 17 games) and has under 150 prior pass attempts in 2025-26. Backtest estimate: team skill-position TDs in
   127 backup-QB team games ran 0.86x of what the implied total predicts (RB 0.87, WR 0.76, TE 1.01, QB rushing 1.03). Inside the model the
   flag cuts a player's chance about 9% (18.8% vs 20.6% on 240 backup rows in 2026 Weeks 2-9; actual 18.8%). The line already moves a lot when
   a backup starts, so the extra cut is small. The Why column says "QB CUT: ...".
7. Fair price from the chance; take-at = fair with the profit stretched 20% (+300 fair becomes +360).

Backtest (player-games with 3+ prior games, a box-score line that week, closing line and starting QB as known at kickoff):

| | 2026 Wk 2-9 (n=1,828) | 2025 Wk 7-18 (n=3,061) |
|---|---|---|
| Log-loss, old hit rate | 0.5255 | 0.5558 |
| Log-loss, shrink only | 0.5057 | 0.5058 |
| + implied total | 0.5024 | 0.5041 |
| + goal-line share | 0.5007 | 0.5032 |
| + RZ and RZ target share | 0.4981 | 0.4997 |
| Log-loss, full v2 (with QB flag) | **0.4981** | **0.4999** |
| Brier, old / v2 | 0.1702 / 0.1614 | 0.1784 / 0.1617 |

(Old hit rate clipped to 3%-97% so a 0% history does not give infinite loss. Lower is better. Every added piece helped in both seasons.)

Calibration, 2026 Weeks 2-9 (predicted vs actual TD rate):

| Bucket | New n | New pred / actual | Old n | Old pred / actual |
|---|---|---|---|---|
| 0-10% | 61 | 8.9% / 8.2% | 447 | 2.5% / 11.9% |
| 10-20% | 816 | 15.2% / 13.5% | 404 | 14.1% / 17.3% |
| 20-30% | 587 | 24.4% / 24.7% | 388 | 24.2% / 25.3% |
| 30-40% | 243 | 34.4% / 39.5% | 289 | 34.0% / 26.3% |
| 40-50% | 57 | 44.9% / 33.3% | 136 | 43.3% / 30.1% |
| 50-60% | 52 | 54.2% / 63.5% | 105 | 53.5% / 45.7% |
| 60%+ | 12 | 64.0% / 83.3% | 59 | 64.1% / 54.2% |

The new chances track reality through 40%; the top buckets are thin (under 60 players) and ran hotter than predicted in 2026. The old
method overstates every bucket from 30% up by 8 to 14 points. 2025 (trained on earlier 2025 only) is similar: new within 3 points up to
50%, old overstated 50-60% by 12 and 60%+ by 29 points.

Picks at 40%+ chance (hits / bets), 2026 Weeks 2-9:

| | New v2 | Old hit rate |
|---|---|---|
| RB/QB | 55 / 101 (54%) | 69 / 142 (49%) |
| WR/TE | 7 / 20 (35%) | 52 / 158 (33%) |
| Weekly top 10 by chance | 50 / 80 (62%) | 43 / 80 (54%) |

2025 Weeks 7-18: RB/QB new 90 / 181 (50%) vs old 133 / 318 (42%); WR/TE new 20 / 56 (36%) vs old 93 / 306 (30%); weekly top 10 new 63 / 120 (53%)
vs old 40 / 120 (33%).

Takeaways: RB/QB hit about 50-55% at 40%+, WR/TE about 35%, which the old method rated about the same (49-52%). The new model gives WR/TE far fewer
40%+ ratings (20 vs 158), so the WR/TE leak is mostly gone from the shortlist. Verdict: adopt v2 (`ADOPT_NEW = True`). Caveats: one season of closing lines
per week, a 2026 sample of 8 weeks, top buckets thin, and backtest QB flag uses the actual starter (live uses depth chart + injuries).

Shortlist verdict rule (Tim's 11/8 rule pending his confirm): RB/QB Play at 45%+, Small stake 30-44%; WR/TE Small stake at 30%+ and only at +250 or
longer; bet only at take-at or longer. Questionable, cold 2026 and small-sample drops still apply. Games already started are Skip.

## First TD chain model (11/17/26)

Replaces the crude first TD estimate in `td_charts.py` (player TD rate / both teams' TD rates x P(any TD)). Built like the NBA
first basket chain: play the game drive by drive until a TD, then split the scoring team's first TD among its players.

Data: nflverse play-by-play, weekly rosters, snap counts and depth charts (GitHub release downloads work through the proxy),
schedule + spread/total from nflverse `games.csv` (jsdelivr mirror; the raw GitHub repo is blocked), injuries from the ESPN feed.
Raw files go in `raw/` (gitignored). Cleaned tables in `data/`: `ftd_games.csv` (lines, opening kickoff receiver, first TD team /
player / type), `ftd_drives.csv` (every drive, offensive TD or not), `ftd_player_games.csv` (snaps, carries, targets, RZ, inside-5,
first-2-drives and 1st-quarter usage, TDs, team first TD, game first TD). 2024, 2025, 2026 Weeks 1-10.

Weekly steps:

```
python3 analysis/nfl/first_td_data.py --download          # refresh raw + rebuild data/ (Tuesday after MNF)
python3 analysis/nfl/first_td_week.py --week 11           # chart out/charts/first_td_wk11.png + out/first_td_wk11.csv/.json
python3 analysis/nfl/first_td_week.py --week 11 --out "Name One" --q "Name Two"   # manual Out / Questionable overrides
python3 analysis/nfl/first_td_model.py backtest           # out/first_td_backtest.txt/.json
```

Rerun `first_td_week.py` Thursday (TNF), Saturday after final injury reports, and Sunday after inactives.

Model (`first_td_model.py`; every input uses only earlier games):
1. Opening kickoff: 50/50 coin toss plus each team's shrunk receive habit (teams that take the ball). Receiver scored the first
   offensive TD 58% of the time in 2025-26.
2. Drive chain: drives alternate, second half starts with the other team receiving, drive count from both teams' pace. Each
   drive's offensive TD chance comes from a ridge logistic model: implied team total, team TD rate per drive, opponent TD rate
   allowed, opening-drive rates (offense and defense) and team drive 1 / 2 terms. Each drive also has a league chance (about 1%)
   of a defensive or special teams TD. Gives P(home offense first), P(away offense first), P(non-offensive TD first), P(no TD).
3. Player share of his team's first TD: conditional logit over active skill players plus "other", on decayed shares (recent
   games weigh more) of team TDs, RZ and inside-5 carries + targets, first-2-drives and 1st-quarter touches, snap share, team
   first TD share, position terms; shares shrink toward position priors.
4. Injuries and QB changes: out players are dropped and their usage shares go to active teammates at the same position. The
   expected starting QB (schedule file / depth chart) is the only QB candidate and inherits the QB role. Line moves for QB changes
   flow through the implied total.
   Live only (11/21/26): when a team's lead RB (top-snap regular RB) is out, the next RB on the depth chart takes 85% of his
   usage and snaps (or keeps his own if higher), the rest goes pro rata. The old pro-rata split capped at 2x left Emmett Johnson
   (KC, Walker out) at 11.9%; now 16.0%. Backtest path unchanged (no depth charts there).
5. Chance = P(team offense first) x share. Fair = 1 / chance. Take-at = fair decimal x1.2.

Backtest (walk-forward, refit before every week, 2025 Weeks 1-18 + 2026 Weeks 1-10, 421 games; full output in
`out/first_td_backtest.txt`):

| | Chain model | Old method |
|---|---|---|
| Top-1 / 2 / 3 per game has the first TD scorer (all 421 games) | 15.2% / 26.6% / 35.2% | n/a |
| Same, 316 games where both exist (2025 Wk 7 - 2026 Wk 10) | 16.1% / 27.8% / 37.0% | 15.2% / 27.2% / 34.8% |
| Player log loss, same 5,347 player-games | **0.1918** | 0.1963 |
| Team-first log loss (home / away / non-offense) | **0.8397** | 0.8972 |
| Favored team scored the first offensive TD | 58.0% | 57.0% |

2026 Weeks 1-10 alone: top-3 38.9%, favored team 57.2%. Team first TD scorer market: our top 2 per team hit 39.4%.

Calibration (chain, all games, predicted / actual): 0-3% 1.5 / 1.5, 3-6% 4.3 / 3.9, 6-9% 7.3 / 8.4, 9-12% 10.3 / 9.9,
12-15% 13.2 / 12.6, 15-20% 16.8 / 17.0, 20%+ 21.5 / 37.5 (16 players only). The old method understated its 9%+ picks
(10.2% predicted vs 16.7% actual at 9-12%, 16.4% vs 26.9% at 15-20%) and overstated its 0-3% bucket.

First TD type, 421 games: receiving 58.2%, rushing 37.1%, defensive 2.9%, special teams 1.2%, no TD 0.5%. So about 4.5% of
games lose every player first TD bet (model average 4.8%, shown as "No off. TD" on the chart).

Read: a top pick is about 15-18% (fair +450 to +570). Even the best model hits the top-3 about 1 game in 3. Value is only in
prices at take-at or longer. Small stakes. Backtest caveats: active players = those who played (live uses injuries and the
depth chart), lines are nflverse closing lines, 2026 sample is 10 weeks.

## Either Player - First Touchdown Scorer (11/27/26)

FanDuel market "Gibbs or Loveland +322": the bet wins if either player scores the game's first TD. First TD scorers are
mutually exclusive, so P(A or B) = pA + pB from the chain model. Fair = 1 / (pA + pB). Take-at = fair decimal x1.2 (same as singles).

`first_td_week.py` now also writes `out/first_td_either_wk<N>.csv`, `out/charts/first_td_either_wk<N>.png` and an `either` block per
game in `out/first_td_wk<N>.json`: the top-2 combo (our #1 + #2), pairs #2 and #3, and the best same-team pair for each team
(favored team first). Helper: `either_pairs()` in `first_td_model.py`; backtest section in `out/first_td_backtest.txt`.

Backtest (walk-forward, 2025 Weeks 1-18 + 2026 Weeks 1-11, 435 games):

| Pair | Predicted | Hit | Fair at hit rate |
|---|---|---|---|
| Top-2 combo | 24.6% | 26.9% (117) | +272 |
| Pair #2 | 23.0% | 24.6% | +307 |
| Pair #3 | 22.0% | 24.1% | +314 |
| Best same-team pair, favored team | 23.3% | 24.1% | +314 |
| Best same-team pair, other team | 15.6% | 16.1% | +521 |

Any of the top-3 pairs hit 41.6%. Top-2 combo: 2025 25.4%, 2026 29.4%. Calibration is close; 25-35% pairs ran a bit hot (pred 27-32%, actual 33-39%).

Tim's 11/26 slip (3/3 hit, a parlay): Gibbs or Loveland +322 (ours 19.4%, fair +416, take +519); Lamb or Javonte Williams +202
(25.9%, fair +286, take +363); Cook or Emmett Johnson +253 (20.9%, fair +378, take +473). All three were shorter than our fair, so
they would have been SKIP as straights. FanDuel prices these pairs about 1.2x-1.35x our chance: value needs a long price.

Play rules: straights only, at take-at or longer, $0.20 to $0.50. Parlays of either-player legs are tracking only unless Tim says
otherwise. Never shorter than -300. Log as Bet type "Either first TD", Pick "A or B (ours X%, fair +F, take at +T or longer)".

## First scoring play model (11/21/26)

FanDuel "First Scoring Play": team + type ("LSU Field Goal", "KC Touchdown", "Safety"). TD = any TD by that team (offense,
defense or return). Files: `first_score_model.py` (data build + model + backtest), `first_score_week.py` (live prices + chart).

Weekly steps (after `first_td_data.py --download`):

```
python3 analysis/nfl/first_score_model.py build       # data/fs_drives.csv (drive results, red zone, FG tries), data/fs_games.csv (first score team + type)
python3 analysis/nfl/first_score_week.py --week 11    # out/first_score_wk11.csv/.json + out/charts/first_score_wk11.png
python3 analysis/nfl/first_score_model.py backtest    # out/first_score_backtest.txt/.json
```

Model: the first TD drive chain, with each drive ending in own TD, made FG, opponent TD (pick six, return), safety or nothing.
- Offensive TD chance: the first TD ridge logistic, unchanged.
- FG chance given no TD: ridge logistic on implied team total, team FG rate per non-TD drive and opponent's allowed (shrunk,
  decayed), red-zone stall rate (FG share of scoring red-zone trips, offense and defense), team kicking over expected (makes
  minus distance-based expected), dome / closed roof, team TD terms, drive 1 / 2. Only the implied total carries much weight;
  kicking, dome and stall terms are small.
- Opponent TD 0.95% and safety 0.19% per drive (league rates). Kickoff 50/50 plus receive habit; second half flips.
- Fair = 1 / chance, take-at = fair decimal x1.2.

Base rates 2024-26 (694 games): first score TD 59%, FG 40%, safety 0.3%; spread favorite scored first 57%.

Backtest (walk-forward, refit weekly, 2024 Wk 8 to 2026 Wk 10, 587 games). B1 = spread logistic x league type split;
B2 = B1 plus implied-total logistic for TD vs FG.

| 6-way log loss (lower better) | Model | B1 spread | B2 spread+total |
|---|---|---|---|
| All 587 | **1.3596** | 1.3781 | 1.3736 |
| 2024 (165) | **1.3453** | 1.3785 | 1.3772 |
| 2025 (272) | **1.3663** | 1.3838 | 1.3781 |
| 2026 (150) | 1.3632 | 1.3675 | **1.3617** |

Brier follows the same order (all: 0.7269 vs 0.7337 B2). Calibration is good: team outcomes at 15-20% hit 18.3%, 20-25% hit 21.2%,
30-35% hit 34.4%, 40-50% hit 45.1%. FG predictions sit in a narrow 15-27% band (actual tracks within 1 point), so the model
separates WHO scores first better than it separates FG from TD. 2026 alone is a wash with B2 (who scores first slightly worse
than the spread).

ROI is SIMULATED: no historical first scoring play prices exist in our data. Book = B2 chance with an 18% hold. Betting where
our chance x price >= 1.2 (take-at) found 15 bets, all in 2024 (+6.8 units); 0 in 2025-26. At any edge (>= 1.0): 234 bets,
+12.4% overall but 2026 -5.5% (17 bets). Read: a small, real gain over a line-only model, but rarely a 20% gap vs a line-based
price. Value only shows if FanDuel prices an outcome long (often FG first). Price check: BET only at take-at or longer, small stakes.

Chart: per game, away/home TD and FG chances with fair and take-at, and "vs spread-only" (our chance / B2). Green = 8%+ above B2.
