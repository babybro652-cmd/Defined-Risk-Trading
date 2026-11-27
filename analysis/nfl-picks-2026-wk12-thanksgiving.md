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
