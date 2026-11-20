# NBA first basket diagnostic, 11/19/26

Tim, after another 0-for-3 night: "Then let's figure it out. What's missing?"

Data: every graded game 11/4 to 11/19 (LIVE = the picks we published, projected fives, __LIVE_N__ games) and a
walk-forward backtest with the actual fives and jumpers (BT: 933 games of 2025-26 from 12/1, __BT26_N__ games of
2026-27, each predicted from earlier games only). Scripts: `diagnostic.py`, `diagnostic_bt.py`, `jumper_test.py` in
this folder.

## The short version

1. **The model is not broken. It is doing what it says, and what it says is not much.** Live, our top 3 held the
   first scorer in __T3_SEASON__ of __LIVE_N__ games; the model's own chances predicted __T3_EXP__. Player chances are
   on the line by bucket and by rank once the real five is known. The ceiling is about 42-45% top-3 coverage (random is
   30%), and each pick is about a 1-in-7 shot.
2. **The last three nights are mostly bad luck on top of a lineup problem.** Play-list games 11/17-11/19: 0 of 8
   with __PL_EXP__ expected; the chance of 0 of 8 if the model is right is about __PL_P0__. That is rare, but this
   window was picked because it was bad; a run like it somewhere in 20 play-list games is about a 1-in-10 event. Weekly
   top 3 went 45%, 41%, __WK3__ against 40-42% expected. No clear drift.
3. **The weakest link is tip winner to first score, not player choice.** The tip winner scored first only
   __TWF_LIVE__ of games live (60% in the backtest since 11/1), while the chain prices it at 68-69%. First shots are
   going in far less this season (__FS_LIVE__ of games' first shots live; team first shots 46.5% last season, 40.3%
   since 11/1). A cold opening hands the other team more chances, so a tip edge is worth less than the model thinks.
   Of our __MISS_N__ top-3 misses: lost the tip __M_TIP__, won the tip but the other team scored first __M_OTHER__,
   scorer not in our projected five __M_LINEUP__, right team but wrong player only __M_PLAYER__.
4. **Lineups are the fixable part.** Our projected five was wrong in __FIVE_BAD__ of __TEAMG__ team-games (one in
   three), the game's first scorer was not in our projected ten in __FP_UNPROJ__ games, and the jumper was wrong in
   __J_BAD__ team-games (OKC Mara 5 times, GS 4 times incl. 11/19 Bassey for Horford, MEM Hendricks for Stewart).
   The same model with the real fives would have hit __BT_MATCH__ instead of __LIVE_MATCH__. RotoWire "expected"
   fives and a 3:30 PM run on 11/18 are not good enough.
5. **No source beats us, and the book prices about where we do.** StarTool ties us on top 3 (25 vs 24 of 61 games)
   with a worse log loss; the @NBAFirstBasket cheat sheet is worse than picking at random by log loss. Tim's 36 priced
   singles averaged 15.1% by our model vs 14.9% implied by his price: about +3% expected value, break-even. Only 5 of 36
   beat our take-at price.

**What is failing:** link (b), the tip winner scoring first, plus stale lineups and jumpers on the day. The player
link (c) is calibrated.

**Tested fixes (fit before 11/1, scored on 134 held-out games from 11/1):** none beat the live chain beyond noise.
Tip shrink, a smaller tip-winner edge, flatter or sharper player shares, more weight on this season (W 6 and W 10 are
worse), trusting first-shot history more or less, the jumper boost, and the team-first-share blend. The one clear,
tested fix is the **jumper rule**: pick the jumper from the five by co-start history, 94% right vs 81% (walk-forward,
2026-27). It is in `build_nba_tab.py` (default `--jumper-rule costart`, `old` keeps the old rule). Its effect on first
basket hits is small.

**Recommendation: change the strategy, keep the volume plan paused.**
- Keep the tip 70%+ filter. It works: top 3 hit 57% vs 38% in 2026-27 with real fives (48% vs 40% in 2025-26).
- Drop the model-accuracy exception. A team's past top-2 hit rate does not predict its next game (51% at 55%+, 51%
  under 45%); the two exception games went 0 for 2.
- Bet only after the official starting lineups (about 30 minutes before tip) and a rerun. No RotoWire-only plays.
- Price gate: straights only at take-at (fair x1.2) or longer, $0.20-$0.50. At book prices first basket is about
  break-even by our own numbers; the 3-straights-per-game plan has no edge to grind. Cut the 3- to 5-leg parlays.
- Team first basket: our team top 2 hit 50% vs 40% random. Log FanDuel's team prices for a week before moving money
  there; switch only if its prices beat fair x1.2 more often than game first basket does.
- First basket stays mostly noise. Points, threes and SOG remain the steadier plays.

---

## 1. Drift (live)

__TABLE_DRIFT__

## 2. Selection: play list vs the rest

__TABLE_SEL__

Backtest, actual fives and jumpers:

__TABLE_TIP70__

Model-accuracy exception check (2026-27, walk-forward): __EXC__

## 3. The chain, link by link

Live:

__CHAIN_LIVE__

Backtest by season:

__TABLE_LINKS__

__FIRST_SHOT__

## 4. Calibration

Live (projected fives):

__CAL_LIVE__

Backtest 2026-27 (actual fives):

__CAL_BT__

Role players: with the real five, team #1 to #5 shares are on the line (BT). Live, our team #1 scored his team's first
points less than predicted mostly because he was sometimes not in the real five or the five around him changed.

## 5. Data checks

__DATA__

- Giannis on MIA and Herro on MIL are real: each has 18 games for that team in ESPN's 2026-27 box scores.
- Positions: ESPN lists some centers as F (Sabonis, Gafford, Diabate). The chain uses position only as a shrink prior;
  not a driver.
- Last season's weight: this season counts 3x (ramped by starts with the team). More recency is worse out of sample
  (held-out LL 2.2669 at W 3, 2.2753 at W 6, 2.2874 at W 10, 2.2640 at W 1).

Jumper rule test (given the actual five, 2026-27 regular season, walk-forward):

__JUMPER__

## 6. Sources vs us

__SOURCES__

Tip picks, all logged games (scorecard): __TIPS__

## 7. Market

- Tim's placed first basket singles with a logged price and our estimate: 36. Our average chance 15.1%, his price's
  implied chance 14.9%. Expected value at the price he got: +2.6% per $1. Price better than our fair: 21 of 36; better
  than take-at (fair x1.2): 5 of 36.
- Placed singles season to date: 89 rows, $211 staked, +$76.70, all of it from the 11/15 $10-$15 straights (Doncic,
  Garland, Wembanyama, Maxey, Mitchell). 11/16 lost $40. 11/17-11/19 have no placed rows logged in the Bets tab.
- Logged pick rows: game first basket 37 hits on 245 graded vs 39.1 expected; team first basket 53 on 222 vs 57.4.
- 11/18 MIL@MIA board vs us: Giannis +370 (us +538), Bam +460 (us +373), Herro +650 (us +1,028). The book had Herro at
  about twice our chance. Klay Thompson scored first (us +951).
- Is the book's ranking better? We do not have enough full boards to test it. On the picks Tim priced, the book and we
  agree within 3% on average, which means there is little edge either way.

## 8. What is missing from the model

Held-out results (fit on games before 11/1, scored on 134 games 11/1-11/18; log loss of the first points scorer over
the 10 starters, lower is better; uniform 2.3026):

__FIX__

| Full rerun variant | Held-out LL | Top 3 | Train LL |
|---|---|---|---|
| Live chain (W 3, k 50, jq 1.2) | 2.2669 | 57 | 2.2496 |
| This season weight W 1 | 2.2640 | 57 | 2.2495 |
| W 6 | 2.2753 | 56 | 2.2498 |
| W 10 | 2.2874 | 53 | 2.2501 |
| First-shot share k 20 (trust opening tendencies more) | 2.2783 | 54 | 2.2523 |
| First-shot share k 100 (trust them less) | 2.2624 | 60 | 2.2505 |
| No jumper boost (jq 1.0) | 2.2613 | 59 | 2.2527 |
| Jumper boost 1.4 | 2.2745 | 56 | 2.2487 |
| Team-first-share blend w 0.3 | 2.2734 | 51 | 2.2516 |

k 100 and jq 1.0 look better on the held-out games but worse on the training games, so a fit made before 11/1 would
not have picked them. Adopting them now would be fitting the recent losses. Recheck at 400+ games of 2026-27.

Candidates:
- Current-season usage and opening tendencies: tested (k 20 / k 100, team-first blend). No gain.
- Who takes the first shot by team (first_events): this is the first-shot share; trusting it more hurts.
- Offensive rebounds and putbacks: already in the chain; rebound and putback shrink were flat in the 11/5 grid.
- Free throws first: in the chain (FT trips); first points come from FTs about 10% of the time, as modeled.
- Home/away: tested 10/21 (65.3% vs 63.0% tip winner first), inside noise; home is already in the tip rates.
- Opponent defense on the first possession: tested 10/21 as position defense, neutral. The chain has the opponent's
  turnover and rebound rates only. Not retested.
- Transition after a steal: not modeled (a turnover gives the other team a normal possession). Needs live-ball vs
  dead-ball turnovers in the cache; not built.
- Recency weighting: tested, worse.
- Cold opening make rates: tested 11/15, no gain on who scores; it does explain the weaker tip-winner edge.
