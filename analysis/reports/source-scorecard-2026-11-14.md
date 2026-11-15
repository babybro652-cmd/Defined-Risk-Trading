# NBA source scorecard, 11/14/26 results (graded 11/15): ours vs StarTool vs @NBAFirstBasket vs Tip-off Projections

Script: `analysis/reports/source_scorecard.py` (now through 11/14; 11/14 picks from commit d5fc33e, the 6:30 PM CLE rerun).
Window: 11/4 to 11/14, 75 games (11/14 added 5).

## 11/14 alone

| Source | Tip | Game FB #1 | Team FB top 2 |
|---|---|---|---|
| Ours (chain) | 3-2 | 0 of 5 | 5 of 10 |
| StarTool | 3-1 (DET @ MIA loading) | 2 of 4 (Randle, LaMelo) | 5 of 9 |
| @NBAFirstBasket sheets | 3-2 | 1 of 5 (LaMelo) | 3 of 9 |
| Tip-off Projections | 3-2 | - | - |

All four sources took the same tip side in every game; DET (at MIA) and BKN (at MEM) won the tip against everyone.
Expected jumpers right 3 of 5 (Edey and J. Smith sat; Stewart and Zach Collins jumped). Tip winner scored first 4 of 5.
Our top 3 held the scorer 2 of 5, both at #2 (Meleek Thomas, LaMelo).

## Season to date (all logged games per source)

| Source | Tip W-L (%) | Game FB #1 | First-scoring team top 2 | Team FB top 2 (random about 40%) |
|---|---|---|---|---|
| Ours | 47-26 (64%) | 10 of 75 (13%) | 39 of 75 (52%) | 72 of 150 (48%) |
| StarTool | 40-27 (60%) | 5 of 30 (17%) | 35 of 73 (48%) | 65 of 146 (45%) |
| @NBAFirstBasket | 31-23 (57%) | 7 of 39 (18%) | 19 of 41 (46%) | 35 of 83 (42%) |
| Tip-off Projections | 16-11 (59%) | - | - | - |

## Head to head (games every listed source called)

| Measure | Games | Ours | StarTool | @NBAFirstBasket | TipProj |
|---|---|---|---|---|---|
| Tip | 48 | 34-14 (71%) | 28-20 (58%) | 29-19 (60%) | - |
| Tip (all 4) | 25 | 16-9 | 16-9 | 13-12 | 15-10 |
| Game FB #1 (all 3) | 11 | 2 | 2 | 3 | - |
| Team FB top 2 | 80 | 44 (55%) | 36 (45%) | 33 (41%) | - |

## Top 3 coverage (ours)

11/4 to 11/14: top 3 held the first scorer in 30 of 75 games (40%). #1 10 of 73 (14%), #2 11 of 75 (15%), #3 9 of 74 (12%).
No odds logged yet, so the $1-straight P&L by rank is blank (`analysis/nba/out/top3_odds.csv`).

Charts: `analysis/nba/out/charts/results_2026-11-14_game.png`, `_tip.png`, `_firstshot.png` (script `results_2026-11-14.py`).
