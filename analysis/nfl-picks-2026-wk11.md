# NFL Week 11 first look (built Tue 11/17, TD model v2 + first TD chain model)

Built with `python3 analysis/nfl/build_tracker.py --week 10` (2026 through MNF LAC @ BAL) and
`python3 analysis/nfl/first_td_week.py --week 11`. Sheet tabs all refreshed (Week Shortlist top 55 rows).
Byes: ATL, CLE, GB, LAR, NE, SEA. Final list Saturday after injury reports.
Rules: bet only at take-at or longer; RB/QB Play 45%+; WR/TE only at +250 or longer; no TD parlays over 2 legs.

## Anytime TD (v2 Plays)

| Player | Game | Chance | Fair | Take-at |
|---|---|---|---|---|
| Christian McCaffrey SF | MIN @ SF Sun 8:20 | 68% | -213 | -177 |
| Javonte Williams DAL | TEN @ DAL 1:00 | 65% | -183 | -152 |
| Jahmyr Gibbs DET | TB @ DET 1:00 | 62% | -163 | -136 |
| James Cook III BUF | MIA @ BUF 1:00 | 61% | -159 | -133 |
| Derrick Henry BAL | BAL @ CAR 1:00 | 56% | -129 | -107 |
| D'Andre Swift CHI | NO @ CHI 1:00 | 56% | -128 | -107 |
| Omarion Hampton LAC | NYJ @ LAC 4:05 | 50% | +100 | +120 |
| Jonathan Taylor IND | IND @ HOU Thu | 48% | +109 | +130 |
| Cam Skattebo NYG | JAX @ NYG 4:25 | 46% | +117 | +140 |

Watch: Kenneth Walker Q (groin, 62% if active), Woody Marks doubtful (Montgomery cold 1/5), Mayfield Q, Bowers Q,
Drake Maye doubtful, Addison out (surgery). QB flags to verify Saturday: PHI depth chart lists Joe Milton over Hurts,
LV Mendoza, ARI Carson Beck, MIA McCord (Willis IR).

## Receptions (soft WR catch defenses: TEN #1, GB #2, WSH #3, CAR/DET/HOU #4; TE: DET #1, DEN #2, WSH #3, KC #4)

- CeeDee Lamb 5+ vs TEN: 9/10 at 4.5+, 7/10 at 5.5+.
- Ja'Marr Chase 5+ @ WSH: 7/9 at 4.5+, last 3: 11, 10, 11.
- Trey McBride 5+ @ KC: 10/10 at 4.5+ (ARI backup QB Beck, lower the line if the price is short).
- Tee Higgins 4+ @ WSH.

## First TD (chain model, top by chance)

| Player | Game | Chance | Fair | Take-at |
|---|---|---|---|---|
| Kenneth Walker III KC (Q) | ARI @ KC | 18.2% | +450 | +560 |
| James Cook BUF | MIA @ BUF | 17.5% | +471 | +585 |
| Javonte Williams DAL | TEN @ DAL | 17.1% | +485 | +602 |
| Jahmyr Gibbs DET | TB @ DET | 16.5% | +507 | +628 |
| D'Andre Swift CHI | NO @ CHI | 16.2% | +519 | +643 |
| Derrick Henry BAL | BAL @ CAR | 13.5% | +642 | +790 |
| Chase Brown CIN | CIN @ WSH | 13.3% | +654 | +805 |

Chart: `analysis/nfl/out/charts/first_td_wk11.png`. Even the top pick hits about 1 in 6.

## Saturday recheck (Sat 11/21, final designations)

Built with `python3 analysis/nfl/build_tracker.py --week 11 --slate 11` (TNF IND @ HOU 26-3 now in the stats) and
`python3 analysis/nfl/first_td_week.py --week 11`. Pushed Injuries, Week Shortlist (top 60 rows) and Notes tabs.

TNF results (Tim's 11/19 bets, not yet graded on Bets I1688:I1691): Nico Collins scored the first TD (42 yd, 1st Q) = W at +600 ($0.20 pays $1.40).
Montgomery first TD L, Taylor first TD L, 3-leg SGP L (Montgomery and Taylor no TD). Net on the four: about -$0.40.

### Final anytime TD list (v2)

| Player | Game | Opp RB TD rank | Chance | Fair | Take-at |
|---|---|---|---|---|---|
| Christian McCaffrey SF | MIN @ SF Sun 8:20 | MIN #28 | 68% | -212 | -176 |
| Javonte Williams DAL | TEN @ DAL | TEN #18 | 64% | -179 | -149 |
| Jahmyr Gibbs DET | TB @ DET | TB #31 | 62% | -160 | -133 |
| James Cook III BUF | MIA @ BUF | MIA #8 | 61% | -157 | -131 |
| D'Andre Swift CHI | NO @ CHI | NO #2 | 56% | -125 | -105 |
| Derrick Henry BAL | BAL @ CAR | CAR #2 | 56% | -125 | -104 |
| Omarion Hampton LAC | NYJ @ LAC 4:05 | NYJ #7 | 51% | -103 | +117 |
| Cam Skattebo NYG | JAX @ NYG 4:25 | JAX #28 | 46% | +118 | +141 |

Drops / skips: Kenneth Walker OUT (groin); Jake Ferguson OUT; Kincaid doubtful; Bowers, McConkey, Mike Evans, Waller questionable;
Woody Marks and Marvin Harrison Jr. were out Thursday. QB: PHI Joe Milton starts (Hurts out for season, blood clots), so Barkley
33% only; LV Mendoza, ARI Beck, MIA McCord start; Mayfield questionable (Irving, Tucker lose about 9% if he sits).
Watch: Emmett Johnson KC gets the Walker workload (first TD model 11.9%, anytime v2 only 26% since it does not hand him Walker's share).

### Receptions (WR catches allowed rank: TEN #1, WSH #3, CAR/DET #4; TE: DET #1, DEN #2, WSH #3, KC #4)

- CeeDee Lamb 5+ vs TEN (#1, 15.6 WR catches/g): 9/10 at 5+, Ferguson out adds targets.
- Ja'Marr Chase 5+ @ WSH Mon (#3): 7/9 at 5+, last 3: 11, 10, 11.
- Tee Higgins 4+ @ WSH Mon (#3): 7/9 at 5+.
- Trey McBride 5+ @ KC (TE #4): 10/10 at 5+; backup QB Beck, take a lower line if 5+ is short.
- Amon-Ra St. Brown 5+ vs TB (#18): 7/9 at 5+, neutral matchup.

### First TD (chain model, Saturday)

Cook BUF 17.6% (fair +468, take +581), Gibbs DET 16.9% (+493 / +611), Javonte Williams 16.7% (+498 / +618), Swift 16.2% (+516 / +640),
Chase Brown 13.2% (+658 / +810), Henry 12.7% (+689 / +847), McCaffrey 12.0% (+731 / +897), Emmett Johnson 11.9% (+737 / +904).

Line moves since Tuesday (small): NYJ @ LAC total up 2 (LAC -3), PIT @ PHI PIT -3.5 (was -4.5), DET -5.5 (was -6.5), CIN @ WSH total 53.5 (+1).
