# NBA source scorecard, 11/13/26 results (graded 11/14): ours vs StarTool vs @NBAFirstBasket vs Tip-off Projections

Script: `analysis/reports/source_scorecard.py` (now through 11/13; TipProj "EVEN" calls count as no call).
Window: 11/4 to 11/13, 70 games (11/13 added 9).

## 11/13 alone

| Source | Tip | Game FB #1 | Team FB top 2 |
|---|---|---|---|
| Ours (chain) | 6-3 | 1 of 9 (Zion) | 6 of 18 |
| StarTool | 5-4 | 3 of 9 (Giannis, J. Johnson, Zion) | 10 of 18 |
| @NBAFirstBasket tip sheet | 4-5 | - | - |
| Tip-off Projections | 5-3 (UTAH @ HOU even) | - | - |

Expected jumpers right in 6 of 9 games (NY Bridges, IND Oubre, NO D. Jordan, OKC Mara jumped instead). Tip winner scored first 7 of 9.
Our 1st-shot pick took his team's first shot 2 of 17 (Sabonis, Garland); either two-slot pick scored the team's first points 6 of 18.
StarTool's best night so far on first basket. One night; it does not change the season read.

## Season to date (all logged games per source)

| Source | Tip W-L (%) | Game FB #1 | First-scoring team top 2 | Team FB top 2 (random about 40%) |
|---|---|---|---|---|
| Ours | 44-24 (65%) | 10 of 70 (14%) | 36 of 70 (51%) | 67 of 140 (48%) |
| StarTool | 37-26 (59%) | 3 of 26 (12%) | 33 of 69 (48%) | 60 of 137 (44%) |
| @NBAFirstBasket | 28-21 (57%) | 6 of 34 (18%) | 18 of 37 (49%) | 32 of 74 (43%) |
| Tip-off Projections | 13-9 (59%) | - | - | - |

## Head to head (games every listed source called)

| Measure | Games | Ours | StarTool | @NBAFirstBasket | TipProj |
|---|---|---|---|---|---|
| Tip | 44 | 31-13 (70%) | 25-19 (57%) | 26-18 (59%) | - |
| Tip (all 4) | 21 | 13-8 | 13-8 | 10-11 | 12-9 |
| Game FB #1 (all 3) | 7 | 2 | 0 | 2 | - |
| Team FB top 2 | 71 | 40 (56%) | 31 (44%) | 30 (42%) | - |

## By date (tip / game #1 / team top 2)

| Date | Ours | StarTool | @NBAFirstBasket | TipProj |
|---|---|---|---|---|
| 11/4 | 8-6 / 2 of 14 / 11 of 28 | 7-5 / - / 14 of 28 | - | - |
| 11/5 | 2-0 / 0 of 2 / 2 of 4 | 2-0 / - / 2 of 4 | 1-0 / - / 1 of 4 | - |
| 11/6 | 7-1 / 2 of 9 / 10 of 18 | 5-3 / - / 9 of 18 | 6-3 / 2 of 9 / 9 of 18 | - |
| 11/7 | 4-2 / 3 of 7 / 7 of 14 | 3-3 / - / 6 of 14 | 4-2 / 1 of 7 / 8 of 14 | - |
| 11/8 | 5-2 / 0 of 7 / 6 of 14 | 3-4 / - / 6 of 14 | 4-3 / 1 of 7 / 2 of 14 | - |
| 11/9 | 5-3 / 2 of 8 / 12 of 16 | 4-2 / 0 of 7 / 6 of 15 | 3-0 / 2 of 7 / 9 of 16 | - |
| 11/11 | 6-4 / 0 of 10 / 9 of 20 | 6-4 / 0 of 9 / 5 of 20 | 5-5 / - / - | 6-4 |
| 11/12 | 1-3 / 0 of 4 / 4 of 8 | 2-1 / 0 of 1 / 2 of 6 | 1-3 / 0 of 4 / 3 of 8 | 2-2 |
| 11/13 | 6-3 / 1 of 9 / 6 of 18 | 5-4 / 3 of 9 / 10 of 18 | 4-5 / - / - | 5-3 |

## Read

- Tip: ours still leads (65% overall, 70% head to head on 44 games).
- Game FB #1: noise for everyone. StarTool 3 of 9 on 11/13 lifts it to 3 of 26.
- Team top 2: ours 48% over 140 team-games (StarTool 44%); 11/13 was our worst team night (6 of 18).

Charts: `analysis/nba/out/charts/results_2026-11-13_game.png`, `_team.png`, `_firstshot.png` (script `results_2026-11-13.py`).

Top 3 coverage (added 11/14): 11/13 our top 3 held the first scorer in 5 of 9 games (#1 1, #2 2, #3 2); 11/4 to 11/13: 28 of 70 (40%). Script: analysis/reports/top3_coverage.py.
