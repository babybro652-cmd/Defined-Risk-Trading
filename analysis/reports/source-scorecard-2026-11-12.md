# NBA source scorecard, 11/12/26: ours vs StarTool vs @NBAFirstBasket vs Tip-off Projections

Question (Tim): which source is winning on tip calls and first basket scorers?

Script: `analysis/reports/source_scorecard.py` (rerun any time; add new dates to its tables).
Window: every graded NBA date with an outside source logged, 11/4 to 11/11 (no NBA 11/10 cards; 11/12 not played yet).
Games: 57 (11/4: 14, 11/5: 2, 11/6: 9, 11/7: 7, 11/8: 7, 11/9: 8, 11/11: 10).

## Scorecard (all logged games per source)

| Source | Tip W-L (%) | Game FB #1 hits | First-scoring team: scorer in top 2 | Team FB top 2 (random about 40%) |
|---|---|---|---|---|
| Ours (chain model) | 37-18 (67%), 55 games | 9 of 57 (16%) | 31 of 57 (54%) | 57 of 114 (50%) |
| StarTool | 30-21 (59%), 51 games | 0 of 16 (0%) | 27 of 57 (47%) | 48 of 113 (42%) |
| @NBAFirstBasket | 23-13 (64%), 36 games | 6 of 30 (20%) | 17 of 33 (52%) | 29 of 66 (44%) |
| Tip-off Projections | 6-4 (60%), 10 games | no data (tip only) | no data | no data |

## Head to head (only the games every listed source called)

| Measure | Games | Ours | StarTool | @NBAFirstBasket | Tip-off Proj |
|---|---|---|---|---|---|
| Tip | 32 | 24-8 (75%) | 18-14 (56%) | 21-11 (66%) | - |
| Tip, 11/11 (all 4) | 10 | 6-4 | 6-4 | 5-5 | 6-4 |
| Game FB #1 | 30 | 7 of 30 (23%) | - | 6 of 30 (20%) | - |
| Game FB #1 (all 3) | 6 | 2 of 6 | 0 of 6 | 2 of 6 | - |
| Team FB top 2 | 65 team-games | 37 (57%) | 29 (45%) | 28 (43%) | - |
| First-scoring team top 2 | 33 | 21 (64%) | 17 (52%) | 17 (52%) | - |

## By date (tip W-L / game #1 hits / team top 2 hits)

| Date | Ours | StarTool | @NBAFirstBasket | Tip-off Proj |
|---|---|---|---|---|
| 11/4 | 8-6 / 2 of 14 / 11 of 28 | 7-5 / - / 14 of 28 | - | - |
| 11/5 | 2-0 / 0 of 2 / 2 of 4 | 2-0 / - / 2 of 4 | 1-0 / - / 1 of 4 | - |
| 11/6 | 7-1 / 2 of 9 / 10 of 18 | 5-3 / - / 9 of 18 | 6-3 / 2 of 9 / 9 of 18 | - |
| 11/7 | 4-2 / 3 of 7 / 7 of 14 | 3-3 / - / 6 of 14 | 4-2 / 1 of 7 / 8 of 14 | - |
| 11/8 | 5-2 / 0 of 7 / 6 of 14 | 3-4 / - / 6 of 14 | 4-3 / 1 of 7 / 2 of 14 | - |
| 11/9 | 5-3 / 2 of 8 / 12 of 16 | 4-2 / 0 of 7 / 6 of 15 | 3-0 / 2 of 7 / 9 of 16 | - |
| 11/11 | 6-4 / 0 of 10 / 9 of 20 | 6-4 / 0 of 9 / 5 of 20 | 5-5 / - / - | 6-4 / - / - |

## Leaders

- Tip: ours (67% over 55; 75% vs 56% StarTool and 66% the sheet on the same 32 games). Tip-off Projections has 10 games only.
- Game first basket #1: no clear leader. Ours 16% and the sheet 20% are both near what a top pick should hit (15 to 20%); StarTool 0 of 16.
- Team first basket top 2: ours 50% (57% head to head) vs StarTool 42% and the sheet 44%, both at the 40% random line.

## Sample-size caution

- Tip: ours 55 and StarTool 51 games are enough to lean on; the sheet (36) is borderline; Tip-off Projections (10) is too small to judge.
- Game FB #1: too small and too noisy for every source. A 15% shot needs a few hundred games to separate 15% from 20%. StarTool 16 games and the sheet 30 games: too small to judge.
- Team top 2: ours 50% on 114 team-games is about 2 standard errors over 40%, an early edge, not proof. The sheet (66) and StarTool (113) are not above random yet.

## How it was scored

- Results: tip winner and game first points (free throws count) from the ESPN game files; each team's first points from `analysis/nba/data/opening_2026-27.json`.
- Ours: the last `fb_candidates.json` and `shortlist.md` committed for each date (after lineup reruns). Tip call = jumper vs jumper; 50% = no call. Game #1 = highest game chance; this differs from the logged Bets row on 11/6 (BOS @ CHA: model top Reid after the Kalkbrenner rerun, row stayed Tatum) and 11/7 (HOU @ PHX: Sengun top after the 8:30 rerun, row was Brooks).
- StarTool: tip favorite = higher of the two team tip rates (equal = no call; 6 games). Team top 2 = star and bomb as printed (11/4 to 11/8), printed model % top 2 on 11/9 and 11/11. Game #1 only where model % was logged (11/9, 11/11); GS @ HOU 11/11 was a tie, no call.
- @NBAFirstBasket: tip favorite = normalized player tip rates (even = no call). Team top 2 = highest "1st Bsk"; game #1 = highest "1st Gm" (from the fb-card images 11/6 to 11/9; 11/5 had team shares only; 11/11 had no first basket card).
- Tip-off Projections: `analysis/nba/out/cheatsheet/tipproj_log.csv`, graded 11/11 only.
- A named player who did not play is dropped and the next name moves up (same as a voided bet rolled to the next pick).
- 11/12 sources (fbsheet, StarTool, sheet tips) are logged and will be scored after tonight's games.
