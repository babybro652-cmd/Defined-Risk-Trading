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
