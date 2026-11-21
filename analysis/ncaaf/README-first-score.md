# CFB first scoring play model (FBS, built 11/21/26)

FanDuel market: "First Scoring Play - LSU Field Goal", "LSU Touchdown", and so on (team + type). Tim approved 11/21.
Mirrors the NFL first TD chain (`analysis/nfl/first_td_model.py`): play the game drive by drive until someone scores.

## Data (free, no key)

ESPN public API:
- `site.api.espn.com/.../college-football/scoreboard?groups=80` for the FBS game list (and tonight's spread / total).
- `summary?event=<id>` for drives (team, result, start spot), scoring plays and the pickcenter line.
- `sports.core.api.espn.com/.../events/<id>/competitions/<id>/odds` for closing lines on older games (2023-2025
  summaries have no pickcenter).

collegefootballdata.com needs an API key (not used). The cfbfastR GitHub releases are not reachable from this session.

FBS vs FBS only (both teams in an FBS conference; FCS opponents skipped). 3,032 games and 71,766 drives,
2023 through the 11/21/26 early kicks. Raw per-game extracts in `raw/games/` (gitignored). Clean tables in `data/`:
`fs_games.csv` (lines, first drive team, first score team / type) and `fs_drives.csv` (every drive, result class).

## Steps

```
python3 analysis/ncaaf/first_score_data.py --download     # refresh raw (only new games) + lines + rebuild data/
python3 analysis/ncaaf/first_score.py backtest            # out/first_score_backtest.txt / .json
python3 analysis/ncaaf/first_score.py week --date 2026-11-28   # out/first_score_<date>.png / .csv / .json
```

`week` prices every FBS vs FBS game on that date that has not kicked off and has an ESPN spread and total.
Run it Saturday morning after the data refresh, and again about 1 hour before the first kick.

## Model

1. Opening possession: 50/50 coin toss plus each team's shrunk receive habit (most toss winners defer).
2. Drive chain: drives alternate, the second half starts with the other team receiving, drive count from both teams'
   pace (about 12.5 drives per team). Each drive ends in offense TD / offense FG / defense score (pick six, fumble or
   return TD, safety) / no score from a ridge multinomial logit on: implied team total (spread + total), offense TD and
   FG rates per drive, defense TD and FG rates allowed, the offense's early-drive (team drives 1-3) rates, and team
   drive 1 / 2 terms. Team rates decay game to game (0.93) and keep half their weight into a new season.
3. Stage 2 calibration on earlier games (recent weeks weigh more, half-life about one season): which team scores first
   = logistic on the chain's side logit + spread; TD vs FG given the team = logistic on the chain's TD-share logit, home
   flag and team spread.
4. Output per game: P(home TD), P(home FG), P(away TD), P(away FG), P(safety). A team's TD includes its defensive and
   return TDs. Fair = 1 / chance. Take-at = fair decimal x 1.2.

## Backtest (walk-forward, refit every week; 2024 through 11/21/26 early kicks, 2,173 games)

| | Our model | Naive (spread + league rates) |
|---|---|---|
| 6-way log loss (lower is better) | **1.258** | 1.282 |
| Which team scores first | 0.6531 | 0.6532 |
| TD vs FG, given the team | **0.581** | 0.604 |
| Top option hit rate | 46.9% | 46.9% |

Each season alone shows the same pattern (2024 1.285 vs 1.303, 2025 1.244 vs 1.269, 2026 1.243 vs 1.272).

Plain read: the model beats the naive baseline because it uses the total (high totals mean more TDs first, low totals
more FGs). Against a stronger naive (TD vs FG from the team's implied total alone) it ties: 0.5829 vs 0.5832. Team
drive stats, kicker / FG habits, opening-drive scripts and receive habits added nothing measurable beyond the
spread and total. So the prices are line-based fair prices, well calibrated, with no independent edge. Value exists
only where FanDuel's price is longer than take-at.

Base rates 2024-2026: favorite scores first 61%; first score is a TD 71%, FG 29%; safety 0.5%; home TD 41%, home FG
14.5%, away TD 29.5%, away FG 14.5%. A team FG first is 9% to 20% in every game priced so far (fair about +400 to
+1000), so a price like +175 on a team FG first is far below fair.

Calibration (every team TD / FG option, predicted vs actual): 5-10% 8.8 / 12.1, 10-15% 12.9 / 13.1, 15-20% 16.6 /
16.9, 20-25% 22.5 / 20.4, 25-30% 27.5 / 23.0, 30-35% 32.4 / 31.8, 35-40% 37.5 / 36.5, 40-50% 44.2 / 45.4, 50%+ 58.2 /
60.8. Weak spot: underdog TD first runs about 2 points high (25.6% vs 23.4%; the dog-TD-first rate fell every season
2023 31.5% to 2026 19.8%). Underdog FG runs about 1 point low (14.2% vs 15.3%). FG options are well calibrated.

Caveats: lines are ESPN closing lines (ESPN BET / DraftKings); no FanDuel price history, so no ROI test; 2023 is
warm-up only; a QB change after the line is set is not modeled beyond the line.

## Rules

- Bet only at take-at or longer, $0.10 to $0.25. First scoring play is mostly noise, like first basket.
- Skip a game with a starting QB change not in the line.
- Grade on the first scoring play in ESPN's scoring plays (a defensive or return TD counts for that team's TD).
