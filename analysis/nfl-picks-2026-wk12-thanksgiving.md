# NFL Week 12 Thanksgiving picks (Thu 11/26/26)

Built 11:30 AM ET with `python3 analysis/nfl/build_tracker.py --week 11 --slate 12 --injuries-only` (TD model v2),
`python3 analysis/nfl/first_td_week.py --week 12` (chain model, backup RB 85% rule) and `python3 analysis/nfl/first_score_week.py --week 12`.
Lines patched to ESPN (CHI -1.5 / 56.5, DAL -8.5 / 49.5, BUF -3 / 45.5). Sides: ESPN FPI win % to fair spread (sd 13.5),
cover chance shrunk halfway to 50%; lean at a 3+ point gap. No totals model: totals are a pass.
Charts: `analysis/nfl/out/charts/thanksgiving_{chi_det,phi_dal,kc_buf}.png` (`analysis/nfl/thanksgiving_charts.py`).
Bets tab full at row 1935, so picks are logged here only. Budget about $5 total; BET only at take-at (fair x1.2) or longer.

Injuries: CHI Roschon Johnson OUT. DAL Jake Ferguson OUT. KC Kenneth Walker OUT (Emmett Johnson RB1), Noah Gray Q.
BUF Dalton Kincaid Q. PHI Dontayvion Wicks IR; depth chart lists Joe Milton at QB (backup QB cut applied to PHI).

## CHI @ DET 1:00 PM

| Pick | Chance | Fair | Take-at | Stake | Note |
|---|---|---|---|---|---|
| DET +1.5 | 55% | -122 | -110 ok | $0.50 | FPI DET by 1.9, 3.4 pt gap, lean |
| D'Andre Swift anytime TD | 56% | -126 | -105 | $0.50 | RB Play 45%+ |
| Kyle Monangai anytime TD | 41% | +142 | +170 | $0.20 | Roschon Johnson out |
| Jahmyr Gibbs anytime TD | 65% | -188 | -156 | $0.50 | FanDuel usually shorter: likely skip |
| Swift first TD | 12.1% | +726 | +891 | $0.20 | |
| Gibbs first TD | 13.1% | +664 | +816 | $0.20 | |
| First scoring play | CHI TD 34.9% | +186 | +244 | pass | model = spread-only (x1.00) |
| Total 56.5 | - | - | - | pass | no model |

## PHI @ DAL 4:30 PM

| Pick | Chance | Fair | Take-at | Stake | Note |
|---|---|---|---|---|---|
| DAL -8.5 | 56% | -127 | -110 ok | $0.50 | FPI DAL by 12.5, 4.0 pt gap, lean; PHI backup QB |
| Javonte Williams anytime TD | 63% | -171 | -143 | $0.50 | GL share 47%, PHI implied 20.5 |
| Javonte Williams first TD | 16.0% | +524 | +649 | $0.20 | top first TD chance of the day |
| DAL TD first scoring play | 41.5% | +141 | +189 | $0.20 | x1.03 vs spread, thin |
| Saquon Barkley anytime TD | 39% | +158 | +190 | $0.20 | QB cut applied |
| Total 49.5 | - | - | - | pass | no model |

## KC @ BUF 8:20 PM

| Pick | Chance | Fair | Take-at | Stake | Note |
|---|---|---|---|---|---|
| Side | - | - | - | pass | FPI BUF by 0.9 vs -3: 2.1 pt gap, under 3 |
| James Cook anytime TD | 55% | -124 | -103 | $0.50 | KC RZ TD% allowed rank 32 |
| BUF TD first scoring play | 35.9% | +179 | +235 | $0.30 | x1.10 vs spread, best first score edge today |
| James Cook first TD | 12.1% | +725 | +890 | $0.20 | |
| Emmett Johnson first TD | 8.7% | +1046 | +1275 | $0.20 | Walker out, gets 85% of his usage |
| Total 45.5 | - | - | - | pass | no model |

If every price qualifies the total is $5.90; drop the Gibbs, Barkley and DAL first-score plays first to stay near $5.
First TD and first scoring play are mostly noise (top first TD pick hits about 1 in 6). No promises.

## Tim's placed slip (FanDuel, logged 11/26 8:15 PM ET)
3-leg parlay, "either player" first TD scorer (slip: analysis/nfl/slips/2026-11-26-first-td-either-parlay.jpg)
| Game | Leg | Odds | Result |
|---|---|---|---|
| CHI@DET | Gibbs or Loveland first TD | +322 | W (Gibbs) |
| PHI@DAL | CeeDee Lamb or Javonte Williams first TD | +202 | W |
| KC@BUF | James Cook or Emmett Johnson first TD | +253 | W (BUF TD in 2nd) |
Combined about +4400 (4.22 x 3.02 x 3.53 = 45.0x). Stake: TBD from Tim. All 3 legs show green on the slip: WIN.
Not on the Bets tab: tab is full at row 1935.

## Fri DEN@PIT 3:00 PM (Prime, built 11/27 10:30 AM ET)

Reran `build_tracker.py --week 11 --slate 12 --injuries-only`, `first_td_week.py --week 12 --q "Tyler Badie"`, `first_score_week.py --week 12`.
Fixed `first_td_week.py`: ESPN status "Suspension" was not dropped (Dobbins had 6.0% first TD); his share now goes to Coleman / Harvey.
Line ESPN DEN -4.5 / 37.5. Chart: `analysis/nfl/out/charts/blackfriday_den_pit.png` (`analysis/nfl/blackfriday_chart.py`).

Injuries: PIT released Aaron Rodgers (cleared waivers 11/26); Mason Rudolph starts (backup QB cut applied to PIT). Michael Pittman Jr.
activated off IR (in the model, 3.8% first TD). PIT LB Alex Highsmith OUT, LB Cole Holcomb Q, WR Ben Skowronek IR.
DEN J.K. Dobbins suspended (out), RB Tyler Badie Q, S Taylor Rapp OUT, TE Caleb Lohner IR. Recheck inactives at 1:30 PM.

| Pick | Chance | Fair | Take-at | Stake | Note |
|---|---|---|---|---|---|
| Side PIT +4.5 | 57% | -132 | - | pass | FPI PIT by 0.3 (4.8 pt gap), but QB change on PIT side and FPI may predate the Rodgers release |
| Jonah Coleman anytime TD | 49% | +105 | +126 | $1.00 | RB1, Dobbins out; TD model did not shift Dobbins usage, so slightly conservative |
| RJ Harvey anytime TD | 34% | +192 | +230 | $0.50 | |
| Coleman first TD | 11.7% | +758 | +929 | $0.50 | top first TD pick |
| Harvey first TD | 8.0% | +1143 | +1391 | $0.25 | |
| Jaylen Warren first TD | 7.6% | +1213 | +1476 | $0.25 | PIT top |
| Either: Coleman or Harvey (top-2 combo, best DEN pair) | 19.7% | +407 | +509 | $0.50 | same team |
| Either: Warren or Dowdle (best PIT pair) | 14.1% | +611 | +754 | $0.25 | |
| Next pairs | Coleman or Warren 19.3% (+419, take +523); Coleman or Dowdle 18.1% (+452, take +563) | | | tracking | |
| First scoring play | DEN TD 30.6% | +227 | +293 | pass | x0.92 to x1.04 vs spread-only: no edge |
| Total 37.5 | - | - | - | pass | no model |

If every price qualifies the total is $3.25 (cap $4). FanDuel usually prices Coleman ATD and the either pairs short: skip anything under take-at.
First TD and first scoring play are mostly noise. No promises.

### Update 11/27 ~11:00 AM ET: RJ Harvey not on FanDuel (treated OUT)
No injury listed for Harvey; ESPN depth chart now has him 5th at RB (Coleman, Dobbins (suspended), Tyler Badie Q, Cody Schrader, Harvey),
so likely a healthy scratch. Coleman takes most of his work; Badie (Q) / Schrader are the backups.
Reran `first_td_week.py --week 12 --out "RJ Harvey" --q "Tyler Badie"`. The anytime TD model does not move usage, so Coleman's anytime
chance is hand-adjusted from 49% to about 55% (his team first TD share rose x1.31 with Dobbins and Harvey out; scaled at x1.2 to stay conservative).
Harvey rows above are void. New plays:

| Pick | Chance | Fair | Take-at | Stake | Note |
|---|---|---|---|---|---|
| Jonah Coleman anytime TD | 55% | -123 | -102 | $1.00 | hand-adjusted, see above |
| Coleman first TD | 13.6% | +633 | +780 | $0.50 | |
| Jaylen Warren first TD | 7.6% | +1213 | +1476 | $0.25 | |
| Courtland Sutton first TD | 6.8% | +1373 | +1667 | $0.25 | WR, small |
| Either: Coleman or Warren (new top-2 combo) | 21.3% | +370 | +465 | $0.50 | different teams |
| Either: Coleman or Sutton (best DEN pair) | 20.4% | +389 | +487 | $0.25 | same team |
| Either: Warren or Dowdle (best PIT pair) | 14.1% | +611 | +754 | $0.25 | |

Side, first scoring play and total: still pass. Max $3.00 if every price qualifies (cap $4).
