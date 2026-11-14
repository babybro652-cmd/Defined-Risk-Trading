# MLB anytime home run model

Built 11/14/26 in the offseason so it is ready for Opening Day 2027 (late March).
One market: **anytime HR** (batter hits 1+ home run). Small stakes; HR props are long odds and
mostly variance. Never promise wins.

## Files

| Path | What |
|---|---|
| `fetch_data.py` | Pulls and cleans all inputs (leaderboards, splits, parks, venues, boxscores) |
| `hr_model.py` | Model: `backtest`, `fit`, `picks` |
| `data/hitters.csv` | Hitters 2022-2026: PA, HR, HR/PA, barrels, barrel/PA, barrel%, hard-hit%, launch angle, EV, sweet spot%, FB%, pull%, pulled air balls (% of BBE and % of air balls), xISO, xSLG, ISO, PA and HR vs LHP / RHP |
| `data/pitchers.csv` | Pitchers 2022-2026: GS, IP, BF, HR, HR/BF, HR/9, HR/FB, barrels allowed, barrel%, hard-hit%, launch angle, FB%, xISO, xSLG, BF and HR vs LHB / RHB |
| `data/park_factors.csv` | Statcast HR park index by batter hand (L / R), 3-year rolling, tables 2022-2026 |
| `data/venues.csv` | Every MLB park: lat / long, azimuth (home plate to CF bearing), elevation, roof type, fence lines |
| `data/hands.csv` | Bats / throws for every player in the data |
| `data/games_2025.json.gz`, `games_2026.json.gz` | Compact game logs from every boxscore: lineup slot, PA, HR per batter; BF, HR per pitcher (starter first); venue; boxscore weather and wind |
| `data/model_params.json` | Fitted parameters the `picks` command uses (fit on 2026 for the 2027 season) |
| `backtest/` | 2026 backtest results, calibration and top-N tables |
| `out/shortlist_<date>.md`, `out/picks_<date>.csv` | Daily output |
| `raw/` | Gitignored. Raw Savant CSVs, full game caches |

## Data sources (all free, all reachable through the proxy on 11/14)

- **Baseball Savant** (`baseballsavant.mlb.com`):
  - Custom leaderboard CSV: `/leaderboard/custom?year=Y&type=batter|pitcher&min=1&selections=...&csv=true`
  - Batted-ball leaderboard CSV (pull-air rate, FB rate): `/leaderboard/batted-ball?type=batter|pitcher&season%5B%5D=Y&min=1&csv=true`
  - Park factors: `/leaderboard/statcast-park-factors?type=year&year=Y&batSide=L|R&stat=index_hr&rolling=3` (HTML page; data is parsed from the embedded `var data = [...]`).
- **MLB Stats API** (`statsapi.mlb.com/api/v1`): season lines, `statSplits` with `sitCodes=vl,vr` (platoon),
  `/venues?hydrate=location,fieldInfo`, `/people?personIds=` (handedness), `/schedule` (with
  `hydrate=probablePitcher,lineups,weather,venue,team` on game day) and `/game/{pk}/boxscore`.
- **Weather on game day**, in order:
  1. MLB schedule `weather` hydrate (or `/api/v1.1/game/{pk}/feed/live` `gameData.weather`): temp, condition
     and wind as text ("12 mph, Out To CF"). Filled in a few hours before first pitch. Same strings the
     backtest used, so this is the preferred input.
  2. `api.weather.gov` hourly forecast at the park's lat / long (works now). The model turns wind speed and
     direction into an "out to CF" component with the park azimuth.
  3. Open-Meteo returned 429 (daily limit, shared IP) on 11/14. Not used.
  4. Manual override: `--weather "gamePk,tempF,windOutMph;..."`.
- Not used but reachable: FanGraphs API, Baseball-Reference.

## Model (`hr_model.py`)

Per starting batter:

1. **Expected PA by lineup slot**, home and away separately, from last season's boxscores
   (slot 1 about 4.6 PA away, slot 9 about 3.35 home).
2. **PA vs starter vs bullpen.** The starter's expected batters faced (his starts this season, last season
   and the league average, shrunk) decides how many of each slot's PA come against him; the rest are vs
   the bullpen.
3. **Batter skill** (HR rate index, 1.0 = league): Marcel weights 5/4/3 on the last three seasons,
   park neutral (each season's HR divided by the home park's average effect). A regression fit on the
   following season picks the mix of HR/PA, barrels/PA, xISO and pulled air balls/PA, then shrinks to
   average by sample size. This season's HR to date updates it (prior worth about 530 PA).
   Rookies start at the rookie average (about 0.84).
4. **Pitcher** the same way with HR/BF, barrels/BF, FB% and xISO (prior worth about 1,800 BF; pitcher HR
   rates are mostly noise, as the fit says).
5. **Platoon**: league HR multiplier by batter hand x pitcher hand, then the batter's and pitcher's own
   splits, heavily shrunk (1,000 PA / 1,500 BF of league platoon added).
6. **Bullpen**: the opponent's relief HR rate (half of last season's, plus this season to date).
7. **Per-PA rate** = log5 (odds ratio) of batter vs pitcher (or bullpen) against the league rate.
   The league rate is last season's blended with this season to date.
8. **Park**: Statcast HR index for the batter's hand at that park, to the power 0.29 (the fit shrinks the
   index a lot).
9. **Weather**: x exp(0.0099 x (temp - 72F)) x exp(0.0079 x wind out mph). About +10% per 10F, +8% for
   10 mph blowing out to CF, -8% blowing in. Domes and closed roofs = 72F, no wind.
10. **P(HR 1+)** = 1 - (1 - p_sp)^PA_sp x (1 - p_pen)^PA_pen, times a calibration constant.
11. **Top-end haircut** for picks: above 16%, keep 75% of the excess (2026 out-of-sample, the top picks
    hit 21-22% when the raw model said 25-28%).

**Fair** = 1 / P (American odds). **Take at** = fair decimal x 1.2. Bet only at take-at or longer.

## Backtest 2026 (fit on 2025, scored on every 2026 regular-season game)

Out of sample: priors from 2023-2025, parameters fit on 2025 games, then every 2026 starter scored
day by day with only data known before that day. 43,722 batter-games, 184 dates.

- Actual HR rate 11.5%, model average 11.7% (11.5% with the haircut).
- Log loss 0.3472 vs 0.3566 for a flat rate (2.6% better). Batter-only version (no pitcher, bullpen, park,
  weather): 0.3493. So matchup, park and weather add a little; the batter is most of it.

Calibration (raw model):

| Model P(HR) | Batter-games | Predicted | Actual |
|---|---|---|---|
| 0-6% | 4011 | 4.6% | 4.6% |
| 6-8% | 5973 | 7.1% | 7.2% |
| 8-10% | 7797 | 9.0% | 9.0% |
| 10-12% | 7614 | 11.0% | 11.0% |
| 12-14% | 6200 | 13.0% | 13.0% |
| 14-16% | 4530 | 14.9% | 14.1% |
| 16-18% | 3250 | 16.9% | 17.1% |
| 18-20% | 1934 | 18.9% | 17.6% |
| 20-23% | 1471 | 21.3% | 20.6% |
| 23%+ | 942 | 25.7% | 22.9% |

Top-N per day (whole slate ranked by model P):

| N per day | Picks | Raw model | With haircut | Hit rate | Fair at hit rate |
|---|---|---|---|---|---|
| 1 | 184 | 28.3% | 25.2% | 20.7% | +383 |
| 3 | 552 | 26.2% | 23.7% | 22.1% | +352 |
| 5 | 920 | 25.0% | 22.8% | 22.1% | +352 |
| 10 | 1840 | 23.3% | 21.4% | 21.5% | +365 |

Read: the board's best HR bats go deep about 1 game in 4.5 to 5. FanDuel usually prices Judge /
Ohtani / Schwarber types at +200 to +300, which is shorter than fair. Value, if any, is in the +400 to
+600 range (good hitter, good park / weather / pitcher spot). The 1.2x take-at rule is the cushion
against the top-end miss above. On 2025 in-sample the top picks were on target (top-5 25.6% vs 25.4%),
so part of the 2026 miss is year-to-year noise; recheck after a month of 2027 picks.

Per-player check (2026): stars were on target (Judge 26.0% predicted / 25.8% actual, Schwarber 25.1 / 24.5,
Alvarez 23.4 / 23.4, Ohtani 24.0 / 20.9).

No historical HR prop prices are available for free, so there is no ROI backtest yet. Start one in 2027
by logging FanDuel's price in column F for every pick.

## Refresh

Offseason / before Opening Day 2027:

```
python3 analysis/mlb/fetch_data.py                       # leaderboards 2022-2026, splits, parks, venues, hands
python3 analysis/mlb/fetch_data.py --skip-leaderboards --games 2026   # only if data/games_2026.json.gz is missing
python3 analysis/mlb/hr_model.py backtest --fit 2025 --test 2026      # re-check
python3 analysis/mlb/hr_model.py fit --season 2026                    # params for 2027 (already done 11/14)
```

During the 2027 season:

- Daily, before picks: `python3 analysis/mlb/fetch_data.py --skip-leaderboards --games 2027` (only new final
  games are downloaded; about 15 games a day) so this season's HR, starter BF and bullpen numbers stay current.
- Weekly: add `2027` to `--seasons` in `fetch_data.py` (or pass `--seasons 2023,2024,2025,2026,2027`) so the
  hitters / pitchers tables carry this season's Statcast lines (they are not used for in-season updates
  yet; the model uses boxscore HR to date).
- After the 2027 season: `fit --season 2027` and `backtest --fit 2026 --test 2027`.

## Daily routine (2027 season)

1. **Games and probable pitchers** (morning): update the game cache, then
   `python3 analysis/mlb/hr_model.py picks --date YYYY-MM-DD`. Without confirmed lineups it uses each team's
   last lineup ("projected") and says so. Games without a probable pitcher are skipped for the other side.
2. **Confirmed lineups** (posted 2-4 hours before first pitch): rerun the same command. Lineups come from
   the schedule `lineups` hydrate. Only bet batters in a confirmed lineup.
3. **Weather**: the run pulls MLB's game weather if posted, else the weather.gov forecast for the park and
   first-pitch hour. Retractable roofs under 60F are treated as closed; check the feed or team on game day and
   override with `--weather "gamePk,tempF,windOutMph"` if needed. Wrigley wind matters most.
4. **Picks**: from `out/shortlist_<date>.md`, take up to 3-5 batters, different games first. Report per pick:
   batter, team, slot, opposing SP (hand), park index, temp / wind out, P(HR), fair, take-at.
5. **Bets rows**: Sport "MLB", Event "Away at Home", Bet type "Anytime HR", Pick
   "Name 1+ HR (fair +352, take at +443 or longer)", F blank until Tim's price, H "Pick". Re-read the last
   ~80 rows and write only to empty rows; never write J or K.
6. **Price check**: BET only at take-at or longer (Tim's rule). $0.20 to $0.50. No HR parlays (two legs at
   22% is about 5%).
7. **Grading**: column I from the MLB boxscore (`statsapi.mlb.com/api/v1/game/{pk}/boxscore`, batter
   `homeRuns`). A batter scratched before first pitch is a void on FanDuel.

## Known gaps / next steps

- In-season batter updates use HR only; in-season barrels (Savant to-date leaderboard) could speed them up.
- Bullpen is one team number; no reliever-by-reliever usage or rest.
- Park index is year-level Statcast; no handed wall distances or altitude term beyond the index.
- Weather fit is on boxscore text wind (8 directions). Humidity and air density not used.
- Top-end haircut is from one season; revisit after 4-6 weeks of 2027 results.
