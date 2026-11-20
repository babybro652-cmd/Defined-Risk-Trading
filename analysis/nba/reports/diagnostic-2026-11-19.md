# NBA first basket diagnostic, 11/19/26

Tim, after another 0-for-3 night: "Then let's figure it out. What's missing?"

Data: every graded game 11/4 to 11/19 (LIVE = the picks we published, projected fives, 113 games) and a
walk-forward backtest with the actual fives and jumpers (BT: 933 games of 2025-26 from 12/1, 226 games of
2026-27, each predicted from earlier games only). Scripts: `diagnostic.py`, `diagnostic_bt.py`, `jumper_test.py` in
this folder.

## The short version

1. **The model is not broken. It is doing what it says, and what it says is not much.** Live, our top 3 held the
   first scorer in 46 of 113 games; the model's own chances predicted 46.8. Player chances are
   on the line by bucket and by rank once the real five is known. The ceiling is about 42-45% top-3 coverage (random is
   30%), and each pick is about a 1-in-7 shot. Our live #1s are a bit overconfident (13% hit vs 16.6% priced, 15 of
   111, about 1 SE); #1 to #3 hit about the same rate, so the order inside the top 3 carries little information.
2. **The last three nights are mostly bad luck.** Play-list games 11/17-11/19: 0 of 8
   with 3.4 expected; the chance of 0 of 8 if the model is right is about 1 in 80. That is rare, but this
   window was picked because it was bad; a run of 8 straight misses somewhere in 19 play-list games happens about 6% of the time (1 in 15). Weekly
   top 3 went 45%, 41%, 34% against 40-42% expected. No clear drift. Real fives would have added one hit in 11/17-11/19 (6 of
   21 games vs 5), so lineups explain little of this slump.
3. **The weakest link is tip winner to first score, not player choice.** The tip winner scored first only
   58% of games live (59% in the backtest since 11/1), while the chain prices it at 68-69%. First shots are
   going in far less this season (31% of games' first shots live; team first shots 46.5% last season, 40.2%
   since 11/1). A cold opening hands the other team more chances, so a tip edge is worth less than the model thinks.
   Of our 67 top-3 misses: lost the tip 25, won the tip but the other team scored first 21,
   scorer not in our projected five 13, right team but wrong player only 8.
4. **Lineups are the fixable part.** Our projected five was wrong in 77 of 226 team-games (one in
   three), the game's first scorer was not in our projected ten in 13 games, and the jumper was wrong in
   30 team-games (OKC Mara 5 times, GS 4 times incl. 11/19 Bassey for Horford, MEM Hendricks for Stewart).
   The same model with the real fives would have hit 49 of 113 instead of 46. RotoWire "expected"
   fives and a 3:30 PM run on 11/18 are not good enough.
5. **No source clearly beats us, and the book prices about where we do.** StarTool is even with us: top 3 27 vs 25
   of 65 games, log loss 2.265 vs 2.259 (on the 38 games with all three sources it was a bit better, 2.207 vs 2.254;
   a 50/50 blend scored 2.217 to 2.238 but lowered top-3 hits); the @NBAFirstBasket cheat sheet is worse than picking at random by log loss. Tim's 36 priced
   singles averaged 15.1% by our model vs 14.9% implied by his price: about +3% expected value, break-even. Only 5 of 36
   beat our take-at price.

**What is failing:** link (b), the tip winner scoring first, plus stale lineups and jumpers on the day. The player
link (c) is calibrated.

**Tested fixes (fit before 11/1, scored on 134-138 held-out games from 11/1):** none beat the live chain beyond noise.
Tip shrink, a smaller tip-winner edge, flatter or sharper player shares, more weight on this season (W 6 and W 10 are
worse), trusting first-shot history more or less, the jumper boost, and the team-first-share blend. The one clear,
tested fix is the **jumper rule**: pick the jumper from the five by co-start history, 94% right vs 81% (walk-forward,
2026-27). It is in `build_nba_tab.py` (default `--jumper-rule costart`, `old` keeps the old rule). Its effect on first
basket hits is small.

**Recommendation: change the strategy, keep the volume plan paused.**
- Keep the tip 70%+ filter. It works: top 3 hit 55% vs 39% in 2026-27 with real fives (48% vs 40% in 2025-26).
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

| Span | Games | Top 3 hit | Top 3 expected | #1 hit | #1 expected | Tip right | Tip expected |
|---|---|---|---|---|---|---|---|
| wk 11/4-11/9 | 47 | 21/47 (45%) | 40% | 9/47 (19%) | 16% | 33/47 (70%) | 66% |
| wk 11/11-11/15 | 37 | 15/37 (41%) | 42% | 3/37 (8%) | 17% | 24/37 (65%) | 68% |
| wk 11/16-11/19 | 29 | 10/29 (34%) | 42% | 3/29 (10%) | 17% | 17/29 (59%) | 66% |
| before 11/13 (11/4-11/12) | 61 | 23/61 (38%) | 41% | 9/61 (15%) | 16% | 40/61 (66%) | 67% |
| last 7 (11/13-11/19) | 52 | 23/52 (44%) | 42% | 6/52 (12%) | 17% | 34/52 (65%) | 67% |
| ALL | 113 | 46/113 (41%) | 41% | 15/113 (13%) | 17% | 74/113 (65%) | 67% |

Last 7 days: observed 23 of 52, model expected 21.9. P(<= observed | model right) = 0.68
Season live: observed 46 of 113, model expected 46.8. P(<= observed | model right) = 0.483
play list 11/17-11/19: observed 0 of 8, expected 3.4; P(0 | model right) = 0.012

A run of 8 straight misses somewhere in 19 play-list games at a 43% hit rate: about 6% (simulated).

## 2. Selection: play list vs the rest

| Group | Games | Tip right | Tip pred | Tip winner scored first | Fav team scored first (pred) | Top 3 hit (exp) | #1 hit (exp) |
|---|---|---|---|---|---|---|---|
| play list, tip 70%+ | 17 | 13/17 (76%) | 77% | 12/17 (71%) | 10/17 (59%) (61%) | 7/17 (41%) (45%) | 3/17 (18%) (19%) |
| play list, exception | 2 | 0/2 (0%) | 60% | 1/2 (50%) | 1/2 (50%) (54%) | 0/2 (0%) (38%) | 0/2 (0%) (14%) |
| not played | 24 | 15/24 (62%) | 60% | 11/24 (46%) | 12/24 (50%) (54%) | 11/24 (46%) (41%) | 2/24 (8%) (16%) |
| ALL season: tip fav 70%+ | 39 | 27/39 (69%) | 80% | 25/39 (64%) | 21/39 (54%) (62%) | 19/39 (49%) (45%) | 6/39 (15%) (20%) |
| ALL season: tip fav < 70% | 74 | 47/74 (64%) | 60% | 40/74 (54%) | 37/74 (50%) (54%) | 27/74 (36%) (39%) | 9/74 (12%) (15%) |

 (season live): picks on the tip-favorite team
  1 of 3 on the fav team: 17 games, top 3 hit 5/17 (29%)
  2 of 3 on the fav team: 55 games, top 3 hit 23/55 (42%)
  3 of 3 on the fav team: 41 games, top 3 hit 18/41 (44%)

Backtest, actual fives and jumpers:

| Season | Group | Games | Fav won tip (pred) | Fav team scored first (pred) | Top 3 (pred) |
|---|---|---|---|---|---|
| 2025-26 | tip 70%+ | 268 | 78% (77%) | 61% (60%) | 48% (43%) |
| 2025-26 | tip < 70% | 665 | 55% (59%) | 52% (54%) | 40% (40%) |
| 2026-27 | tip 70%+ | 78 | 77% (79%) | 62% (62%) | 55% (45%) |
| 2026-27 | tip < 70% | 148 | 58% (59%) | 50% (54%) | 39% (40%) |

Model-accuracy exception check (2026-27, walk-forward): past rate 55%+: next game top 2 hit 53/103 (51%); past rate 45-55%: next game top 2 hit 36/82 (44%); past rate under 45%: next game top 2 hit 60/117 (51%)

## 3. The chain, link by link

Live:

(a) tip favorite won the tip: 74/113 (65%), predicted 67%
(b) tip winner scored first: 65/113 (58%) (model assumes about 64% via the chain; 2025-26 league 64%)
    tip favorite TEAM scored first: 58/113 (51%), predicted 56%
(c) scorer in OUR projected five of his team: 100/113 (88%); our team #1 21/113 (19%), team top 2 54/113 (48%) (predicted top 2 share 51%)
(d) game's first shot went in: 35/113 (31%) (2025-26: 48.6%; model make rates are full-game, about 47-50%)

Top 3 misses, first broken link:
  hit: 46
  lost the tip: 25
  won tip, other team scored first: 21
  scorer not in our projected five (lineup): 13
  right team, wrong player: 8

First shot made vs missed, top 3 hit:
  first shot made: 35 games, top 3 14/35 (40%)
  first shot missed: 78 games, top 3 32/78 (41%)

Backtest by season:

| Season | Games | Tip fav won (pred) | Tip 70%+ games: won (pred) | Tip winner scored first (model X) | Team-first scorer in chain team top 2 | Game top 3 (pred) |
|---|---|---|---|---|---|---|
| 2025-26 | 933 | 569/933 61% (64%) | 208/268 78% (77%) | 613/933 66% (68%) | 899/1866 48% | 394/933 42% (41%) |
| 2026-27 to 10/31 | 88 | 67/88 76% (68%) | 31/38 82% (79%) | 57/88 65% (69%) | 89/176 51% | 42/88 48% (42%) |
| 2026-27 11/1 on | 138 | 78/138 57% (65%) | 29/40 72% (80%) | 81/138 59% (68%) | 139/276 50% | 58/138 42% (42%) |

Team first FGA made: 2025-26: team first FGA made 867/1866 (46.5%); 2026-27 to 10/31: team first FGA made 79/176 (44.9%); 2026-27 11/1 on: team first FGA made 111/276 (40.2%)

## 4. Calibration

Live (projected fives):

| Predicted | Players | Avg pred | Hit rate | Hits | Expected hits |
|---|---|---|---|---|---|
| 0%-5% | 29 | 4.2% | 6.9% | 2 | 1.2 |
| 5%-8% | 300 | 6.8% | 6.0% | 18 | 20.3 |
| 8%-11% | 404 | 9.4% | 8.4% | 34 | 38.0 |
| 11%-14% | 265 | 12.2% | 11.7% | 31 | 32.3 |
| 14%-18% | 71 | 15.3% | 11.3% | 8 | 10.8 |
| 18%-22% | 19 | 19.9% | 15.8% | 3 | 3.8 |
| 22%-100% | 13 | 25.0% | 30.8% | 4 | 3.2 |

By game rank:
  #1: pred 16.6%, hit 15/111 (14%)
  #2: pred 13.2%, hit 14/110 (13%)
  #3: pred 11.6%, hit 17/110 (15%)
  #4: pred 10.7%, hit 9/106 (8%)
  #5: pred 10.0%, hit 8/112 (7%)
  #6: pred 9.2%, hit 7/111 (6%)
  #7: pred 8.4%, hit 13/111 (12%)
  #8: pred 7.5%, hit 4/112 (4%)
  #9: pred 6.9%, hit 7/111 (6%)
  #10: pred 5.7%, hit 6/107 (6%)

By rank within his team (team_share order): predicted share of team first points vs actual
  team #1: pred 27.7%, actual 43/226 (19%)
  team #2: pred 23.1%, actual 61/226 (27%)
  team #3: pred 19.6%, actual 43/226 (19%)
  team #4: pred 16.6%, actual 32/226 (14%)
  team #5: pred 13.3%, actual 24/221 (11%)
  team first scorer not in our projected five: 23 of 226

Backtest 2026-27 (actual fives):

| Predicted | Players | Avg pred | Hit rate | Hits | Expected |
|---|---|---|---|---|---|
| 0%-5% | 58 | 4.2% | 6.9% | 4 | 2.5 |
| 5%-8% | 604 | 6.8% | 6.6% | 40 | 40.9 |
| 8%-11% | 886 | 9.4% | 8.5% | 75 | 83.6 |
| 11%-14% | 479 | 12.3% | 14.8% | 71 | 58.8 |
| 14%-18% | 173 | 15.7% | 12.1% | 21 | 27.1 |
| 18%-22% | 32 | 19.7% | 25.0% | 8 | 6.3 |
| 22%-100% | 28 | 24.2% | 25.0% | 7 | 6.8 |
Game rank: #1 16.7% / 15.5%; #2 13.5% / 15.9%; #3 11.5% / 12.8%; #4 10.6% / 9.7%; #5 9.8% / 11.5%; #6 9.2% / 5.8%
Team rank (share of team first points): #1 26.5% / 25.7%; #2 23.1% / 24.8%; #3 19.7% / 19.2%; #4 16.8% / 15.7%; #5 13.9% / 14.2%

Role players: with the real five, team #1 to #5 shares are on the line (BT). Live, our team #1 scored his team's first
points less than predicted mostly because he was sometimes not in the real five or the five around him changed.

## 5. Data checks

Jumper right: 196/226 (87%) team-games. Wrong jumpers (30):
   2026-11-04 OKC hartenstein:i mara:a
   2026-11-04 TOR poeltl:j murrayboyles:c
   2026-11-05 PHX maluach:k ighodaro:o
   2026-11-06 WSH ayton:d sarr:a
   2026-11-06 CLE allen:j mobley:e
   2026-11-07 OKC hartenstein:i mara:a
   2026-11-08 SAC sabonis:d cardwell:d
   2026-11-09 WSH sarr:a davis:a
   2026-11-09 DET reed:p collins:j
   2026-11-11 WSH sarr:a davis:a
   2026-11-11 GS green:d horford:a
   2026-11-11 OKC hartenstein:i mara:a
   2026-11-13 NY towns:k bridges:m
   2026-11-13 IND zubac:i oubre:k
   2026-11-13 NO matkovic:k jordan:d
   2026-11-13 OKC hartenstein:i mara:a
   2026-11-14 MEM edey:z stewart:i
   2026-11-14 CHI smith:j collins:z
   2026-11-15 PHI james:l walker:j
   2026-11-15 TOR poeltl:j murrayboyles:c
   2026-11-15 MIL turner:m sims:j
   2026-11-15 SAC sabonis:d cardwell:d
   2026-11-16 BOS robinson:m garza:l
   2026-11-16 GS green:d horford:a
   2026-11-17 LAL mamukelashvili:s looney:k
   2026-11-18 OKC hartenstein:i mara:a
   2026-11-18 GS horford:a bassey:c
   2026-11-19 GS horford:a bassey:c
   2026-11-19 MEM stewart:i hendricks:t
   2026-11-19 MIL sims:j ware:k
Projected five not the actual five: 77 of 226 team-games
Game first scorer was not a projected starter: 13 of 113
  both jumpers right=True: 86 games, tip right 56/86 (65%), pred 68%
  both jumpers right=False: 27 games, tip right 18/27 (67%), pred 62%

Live vs the same model with actual fives: live top 3 46/113 (41%), same model with actual fives and jumpers 49/113 (43%)
  play list 11/14+: live 7/19, actual fives 7/19
  11/17-11/19: live 5/21, actual fives 6/21

- Giannis on MIA and Herro on MIL are real: each has 18 games for that team in ESPN's 2026-27 box scores.
- Positions: ESPN lists some centers as F (Sabonis, Gafford, Diabate). The chain uses position only as a shrink prior;
  not a driver.
- Last season's weight: this season counts 3x (ramped by starts with the team). More recency is worse out of sample
  (held-out LL 2.2669 at W 3, 2.2753 at W 6, 2.2874 at W 10, 2.2640 at W 1).

Jumper rule test (given the actual five, 2026-27 regular season, walk-forward):

  current   all 365/451 (80.9%)   11/1 on 216/276 (78.3%)
  in-five   all 420/451 (93.1%)   11/1 on 255/276 (92.4%)
  co-start  all 425/451 (94.2%)   11/1 on 260/276 (94.2%)

## 6. Sources vs us

Games where StarTool printed % for 8+ starters: 65
| Source | Top 3 hit | #1 hit | Log loss (lower is better; uniform 2.303) |
|---|---|---|---|
| Ours | 25/65 (38%) | 6/65 (9%) | 2.259 |
| StarTool | 27/65 (42%) | 9/65 (14%) | 2.265 |
| 50/50 ours + StarTool | 21/65 (32%) | 9/65 (14%) | 2.238 |

Games where Cheat sheet printed % for 8+ starters: 69
| Source | Top 3 hit | #1 hit | Log loss (lower is better; uniform 2.303) |
|---|---|---|---|
| Ours | 28/69 (41%) | 11/69 (16%) | 2.241 |
| Cheat sheet | 23/69 (33%) | 11/69 (16%) | 2.335 |
| 50/50 ours + Cheat sheet | 26/69 (38%) | 15/69 (22%) | 2.261 |

Games where StarTool and Cheat sheet printed % for 8+ starters: 38
| Source | Top 3 hit | #1 hit | Log loss (lower is better; uniform 2.303) |
|---|---|---|---|
| Ours | 14/38 (37%) | 4/38 (11%) | 2.254 |
| StarTool | 15/38 (39%) | 6/38 (16%) | 2.207 |
| Cheat sheet | 9/38 (24%) | 5/38 (13%) | 2.406 |
| 50/50 ours + StarTool | 12/38 (32%) | 5/38 (13%) | 2.217 |
| 50/50 ours + Cheat sheet | 13/38 (34%) | 7/38 (18%) | 2.303 |
| equal blend of 3 | 12/38 (32%) | 6/38 (16%) | 2.257 |

Tip picks, all logged games (scorecard): ours 71/110 (65%), StarTool 59/101 (58%), @NBAFirstBasket 52/84 (62%), TipProj 35/57 (61%). Head to head on 73 games all three called: ours 67%, StarTool 58%, @NBAFirstBasket 63%. Team top 2 head to head (140 team-games): ours 49%, StarTool 43%, @NBAFirstBasket 36%.

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

Held-out results (fit on games before 11/1; post-hoc fixes scored on 138 games 11/1-11/19, full reruns below on 134 games 11/1-11/18; log loss of the first points scorer over
the 10 starters, lower is better; uniform 2.3026):

fit on 2025-26 + 26-27 to 10/31 (1021 games): best {'s': 1.15, 't': 1.0, 'u': 0.8}
fit on 26-27 to 10/31 only (88 games): best {'s': 1.15, 't': 1.2, 'u': 1.0}
| Variant | Held-out LL | Paired SE vs chain | Top 1 | Top 3 | Train LL (all) |
|---|---|---|---|---|---|
| chain (live model) | 2.2722 | +0.0000 (0.0000) | 19 | 58 | 2.2496 |
| uniform (1/10 each) | 2.3026 | | 14 exp | 41 exp | |
| tip shrink u 0.8 | 2.2701 | -0.0021 (0.0023) | 19 | 57 | 2.2501 |
| tip shrink u 0.6 | 2.2688 | -0.0035 (0.0047) | 19 | 57 | 2.2512 |
| tip-winner edge s 0.7 | 2.2691 | -0.0032 (0.0040) | 19 | 57 | 2.2512 |
| tip-winner edge s 0.5 | 2.2682 | -0.0040 (0.0067) | 19 | 56 | 2.2532 |
| flatten t 0.8 | 2.2715 | -0.0007 (0.0050) | 19 | 57 | 2.2519 |
| flatten t 0.6 | 2.2742 | +0.0019 (0.0100) | 20 | 56 | 2.2571 |
| sharpen t 1.2 | 2.2762 | +0.0040 (0.0050) | 19 | 56 | 2.2502 |
| u 0.8 + s 0.7 | 2.2684 | -0.0038 (0.0056) | 19 | 60 | 2.2522 |
| u 0.8 + s 0.7 + t 0.8 | 2.2679 | -0.0044 (0.0080) | 19 | 56 | 2.2545 |

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
