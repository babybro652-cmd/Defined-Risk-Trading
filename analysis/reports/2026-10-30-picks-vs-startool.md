# Our picks vs StarTool, season to date (through 10/29/26)

Chart: `analysis/reports/2026-10-30-picks-vs-startool.png`. Numbers: `analysis/reports/out/summary.json`.
Rerun: `python3 analysis/reports/picks_vs_startool.py <bets.csv> analysis/reports/data/startool_nba_cards.txt analysis/reports/data/startool_nba_star_bomb.txt` (bets.csv = Bets tab export, first column the sheet row) then
`python3 analysis/reports/chart_picks_vs_startool.py`.

Sources: Bets tab rows 2-510 (all graded rows, read only), `analysis/first_events/log.csv`, the 53 NBA
StarTool cards in `analysis/nba/out/startool/` (top 5 per team read off each card), the 3 NHL StarTool nights,
the 10/26 Manus compare page, and a walk-forward rerun of our first basket model (`backtest_fb.py`, current
model with the 10/23 ramp). Every sample here is small. Read the numbers as direction, not proof.

## 1. NBA first basket

### Our logged picks (Bets rows)

| | Picks | Hits | Expected (sum of our %) | Note |
|---|---|---|---|---|
| All graded first basket picks | 80 | 12 (15.0%) | 12.4 | 1 void (Doncic DNP 10/28) |
| Picks with an est % logged | 75 | 11 (14.7%) | 11.8 | calibrated |
| Picks with a FanDuel slip price | 23 | 3 | | ROI +33% at slip odds (Wallace +1100, Vassell +850, Barrett +800) |
| All 80 at the median slip price (+600) | 80 | 12 | | ROI +5% |

Our picks hit at the rate the model said. The +33% on slips is three long prices landing; one fewer hit makes it
negative. First basket pays only when FanDuel's price beats our fair price.

### Calibration (walk-forward, every starter, actual starters known)

| Model chance | 2026-27 starter-games | Hit rate (expected) | 2025-26 Dec-Apr | Hit rate (expected) |
|---|---|---|---|---|
| under 8% | 184 | 8.2% (6.4%) | 2,481 | 7.7% (6.7%) |
| 8-11% | 299 | 8.0% (9.5%) | 3,871 | 9.4% (9.5%) |
| 11-14% | 122 | 14.8% (12.3%) | 2,203 | 12.3% (12.3%) |
| 14-17% | 57 | 12.3% (15.4%) | 628 | 13.7% (15.1%) |
| 17%+ | 18 | 22.2% (19.0%) | 147 | 15.0% (18.5%) |

Our 15-16% picks hit about 13.5-14% over the big 2025-26 sample, so the top end runs 1-3 points hot. The
middle is right. Top pick per game: 9 of 68 this season (10.9 expected), 131 of 933 last season (140 expected).

### StarTool (53 cards, 10/22 to 10/29)

| | Picks | Hits | StarTool's own expected | ROI at +600 flat |
|---|---|---|---|---|
| StarTool top % per game | 53 | 7 (13.2%) | 8.3 | -8% |
| Stars (2 per game, 10/23 on) | 102 | 10 (9.8%) | 14.8 | -31% |
| Bombs (2 per game, 10/23 on) | 102 | 14 (13.7%) | 12.0 | -4% (real bomb prices are longer) |
| Tim's own first basket singles off the cards (10/23, 10/25) | 17 | 0 | | -100% |

Stars run well under StarTool's own numbers. Bombs beat theirs. StarTool's 10 listed players sum to 100% per
game (their note: starter share x about 50% per team), so the tip barely moves their numbers, and the cards
keep injured or traded players (Flagg 10/24, Knueppel and Coby White, Zubac on IND, Jalen Williams).

### Head to head, 50 games with both lists (10/29's 3 games are not in the model cache yet)

| | Ours | StarTool |
|---|---|---|
| Top pick scored first | 6 | 6 |
| Actual scorer in the top 2 | 16 | 12 |
| Actual scorer in the top 4 | 26 | 22 |
| Mean rank of the actual scorer (of 10) | 4.98 | 5.34 |
| Ranked the actual scorer higher | 28 games | 15 games (7 ties) |
| Log loss (uniform guess = 2.303) | 2.298 | 2.303 |
| Top pick ROI at +600 | -16% | -16% |

Our list ranks the eventual scorer higher more often (28 to 15). Both are barely better than a uniform guess
on these 50 games; first basket is mostly noise. Caveat: our walk-forward run knows the real starters, so it
has a small edge over what we priced pregame. StarTool missed the scorer entirely twice (Ace Bailey 10/23,
Dean Wade 10/24).

Manus (10/26 only): its top 2 per team (about 36 names over 9 games) caught 4 scorers (Miller, Allen, Amen
Thompson, Jokic). Ours caught 3 of 8 picks that night. One night; no conclusion.

### Tip, position, jumpers (all 68 regular season games so far)

- Tip winner's team scored first in 41 of 68 (60%). Last season 64%. The 4-point gap is inside noise (SE about 6).
- First basket by ESPN position: forwards 29, guards 23 (34%), centers 16. ESPN lists Smith, Gafford and
  Diabate as F, so bigs are undercounted.
- The jumper (almost always the starting center) scored first in 19 of 68 (28%). Our model expected 15.3.
  13 of the 19 came after his team won the tip, and 16 of 19 came on his team's first shot (Edey 10/23 and
  10/29, Allen 10/22 and 10/26, Smith 10/23, Adebayo 10/24 and 10/28, Carter 10/28). This is the
  tip-winner jumper bias flagged 10/24, still showing.

### Jumper fix backtest (log loss, lower is better)

| Jumper share x (team wins tip / loses) | 2025-26 (933 games) | 2026-27 (68 games) |
|---|---|---|
| 1.0 / 1.0 (current) | 2.2826 | 2.2844 |
| 1.1 / 1.0 | 2.2812 | 2.2818 |
| **1.2 / 0.95** | **2.2808** | 2.2813 |
| 1.2 / 1.0 | 2.2810 | **2.2810** |
| 1.3 / 1.0 | 2.2820 | 2.2816 |
| 1.4 / 1.0 | 2.2840 | 2.2838 |

1.2 / 0.95 wins on both seasons. It lifts jumpers' expected count from 15.3 to 17.0 (19 actual) and this
season's top pick hits from 9 to 10 of 68. The gain is small but it shows in both seasons.

### Blend backtest (ours x w + StarTool x (1 - w), 50 games, unlisted starters get 3%)

| w (weight on ours) | 0 | 0.3 | 0.5 | 0.6 | 0.7 | 1.0 |
|---|---|---|---|---|---|---|
| Log loss | 2.303 | 2.280 | **2.276** | 2.276 | 2.278 | 2.298 |

Leave-one-day-out picks w between 0.4 and 0.8 (average 0.55) and scores 2.2945 vs 2.2977 for ours alone,
a small gain. The bootstrap 90% range for ours minus the 50/50 blend is -0.04 to +0.09, so the gain could
be zero. The 50/50 blend's top pick hit only 4 of 50 (ours 6). The data supports a blend for ranking and
pricing, not for picking a single name.

## 2. NHL: ours vs StarTool (10/22, 10/23, 10/28 cards)

| | Skaters | Scored | Expected |
|---|---|---|---|
| All StarTool-listed skaters | 56 | 14 (25%) | 19.7 (35%) |
| StarTool 40%+ | 15 | 4 (27%) | 6.9 (46%) |
| StarTool stars | 18 | 6 | |
| StarTool bombs | 17 | 4 | |
| Shared with our picks | 13 | 4 | StarTool 5.7, ours 5.5 |

Brier on the 13 shared players: ours 0.222, StarTool 0.232 (ours slightly closer; tiny sample). Both run
high: StarTool's goal % are about 10 points too high, and ours are too (our anytime goal picks with a
logged %: 9 of 25 scored vs 46% expected). SOG: StarTool's shot estimates landed within one shot on most
players graded 10/23; not enough to score them.

## 3. Our picks by category (all graded Pick, No and placed rows that were ours)

ROI at $0.20 a pick. "Slip" = FanDuel slip or logged market odds; "fair" = our own fair price where no slip,
which only checks calibration (a pick at fair odds breaks even by definition).

| Category | Record | Hit rate | Expected hit (picks with a %) | ROI at slip odds (n) | P/L at $0.20, slip else fair |
|---|---|---|---|---|---|
| NBA first basket | 12-68 (1 void) | 15% | 11 of 75 vs 11.8 | +33% (23) | +$1.21 |
| NBA first basket method (10/29) | 0-5 | 0% | 0.4 | none | -$1.00 |
| NBA points | 21-8 (2 void) | 72% | 16 of 23 vs 18.8 (82%) | -37% (6) | -$0.63 |
| NBA threes | 12-2 (2 void) | 86% | 9 of 10 vs 7.2 (72%) | -6% (4) | +$0.58 |
| NHL anytime goal | 19-33 | 37% | 9 of 25 vs 11.6 (46%) | -3% (16) | -$1.39 |
| NHL first goal | 3-25 | 11% | about 9% each | +169% (8) | +$1.50 (14 unpriced) |
| NHL SOG 2+ (over 1.5) | 24-8 | 75% | 6 of 10 vs 8.2 (82%) | none | -$0.56 (22 unpriced) |
| NHL SOG 3+ (over 2.5) | 14-8 | 64% | 13 of 19 vs 13.6 (72%) | +8% (9) | -$0.10 |
| NFL anytime TD | 18-21 (1 void) | 46% | | -14% (22) | -$0.72 |
| NFL first TD | 1-3 | 25% | | none | unpriced |
| NFL receptions | 22-10 (1 void) | 69% | 7 of 7 | +9% (4) | +$0.36 (21 unpriced) |
| NFL sides/totals (10/4) | 6-6 | 50% | | -5% (12) | -$0.11 |
| CFB sides | 7-5 | 58% | | -2% (4) | +$0.29 |
| CFB anytime TD | 8-1 | 89% | | +2% (4) | +$0.02 |
| Soccer SOT | 10-1 (3 void) | 91% | 6 of 7 vs 5.3 | none | +$0.41 (fair) |
| Soccer goals/sides | 15-13 (2 void) | 54% | 9 of 16 vs 11.4 | none | +$0.15 (fair) |

Steady: threes, SOG 3+, receptions, soccer SOT. Short-priced points overs lose money even when they hit 72%.

## 4. Tim's placed bets (H = Yes), net P/L

216 settled slips, $99.22 staked, **net about -$4.72**. Bet Protect+ fees not included.

| Sport | Category | Slips | Wins | Staked | P/L |
|---|---|---|---|---|---|
| NHL | first goal | 14 | 4 | $3.70 | +$8.15 |
| NHL | parlays / round robins | 15 | 3 | $11.08 | +$3.94 (10/13 cash-out $10.12) |
| NHL | anytime goal | 23 | 9 | $7.00 | -$0.11 |
| NHL | SOG 3+ | 14 | 9 | $5.20 | -$0.22 |
| **NHL total** | | 66 | 25 | $26.98 | **+$11.76** |
| NBA | first basket singles | 55 | 7 | $20.70 | -$8.26 |
| NBA | parlays / round robins | 11 | 3 | $13.24 | +$2.62 (10/20 cash-out $7.57) |
| NBA | points | 12 | 6 | $7.20 | -$2.60 |
| NBA | threes | 4 | 3 | $4.00 | -$0.24 |
| **NBA total** | | 82 | 19 | $45.14 | **-$8.48** |
| NFL | parlays / SGPs | 10 | 2 | $6.40 | -$4.15 |
| NFL | anytime TD / 2+ TDs | 14 | 8 | $6.10 | -$1.67 |
| NFL | receptions | 11 | 10 | $3.90 | +$0.24 |
| NFL | sides/totals | 2 | 1 | $1.50 | +$0.41 |
| **NFL total** | | 37 | 21 | $17.90 | **-$5.17** |
| CFB | all | 27 | 17 | $5.20 | +$1.17 |
| Multi-sport parlays | | 4 | 0 | $4.00 | -$4.00 |

- Inside NBA first basket: Tim's placed copies of our picks went 7 of 38 (+$1.24); his own picks off the
  StarTool cards went 0 of 17 (-$9.50).
- Check with Tim: rows 292-294 (10/23 CHI @ MIL: Herro, Kuzma, Jaquez) show $4.00 stakes, 20 to 40 times his
  usual. They cost $12.00. If they were $0.40, NBA is +$2.32 and the season total is about +$6.08.
- Estimated where the sheet has no odds or payout (marked in the script): 10/24 round robin 2s (Adebayo +500
  x Fox +700 combo, about +$2.40), 10/28 round robin (Adebayo x Murray with Doncic void, about +$2.39 net), five
  10/24 CFB anytime TD wins at about -300, Tuch first goal 10/28 at about +900, and 24 other wins with no logged
  price at our fair price (-110 for CFB sides).

## 5. Recommendations

Keep
- NBA threes (12-2) and the "next line up" rule from 10/29.
- NHL SOG 3+ (hit rate matches the model, positive at slip odds).
- NFL and CFB receptions and soccer SOT: high hit rates, but check the price; most were unpriced.
- First basket and first goal singles at $0.10-$0.20, only at a price 10%+ better than our fair. Calibrated,
  positive so far on slips, but the profit is three or four long hits.

Cut
- NBA points overs at 19.5 / 24.5 priced -300 to -1000 (16 of 23 vs 82% expected; Tim lost $1 each on
  Leonard -390, SGA -530, Jokic -460). Skip anything shorter than -200, or go up a line.
- Tim's own first basket picks off the StarTool cards (0 for 17) and StarTool stars as picks (10 of 102).
- NFL and multi-sport parlays (-$8.15 on 14). Keep parlays to NHL SOG legs if Tim wants them.

Resize
- NHL anytime goal: our % runs about 10 points high. Multiply the blend by about 0.8 before pricing (Kaprizov
  56% becomes 45%), or bet only at +150 or longer. Stakes stay $0.20.
- Any first basket stake over $0.50 (the $4 slips) is out of line with the balance.

Blend StarTool into first basket
- Use 60% ours, 40% StarTool for the shortlist ranking and the fair price (in-sample best 0.5-0.6,
  cross-validated 0.55). Evidence is weak (gain could be zero), so do not raise stakes on it, and keep our
  top pick as the pick; the blend's top pick did worse (4 of 50).
- Before blending: drop StarTool players our injury feed has out, then renormalize. StarTool's tip % is a
  team's last-8 rate, so keep our log5 tip in our half.
- Recheck the weight at about 150 shared games.

Model fixes (first basket)
1. Jumper boost: share x1.2 when his team wins the tip, x0.95 when it loses, priced pregame through our tip
   chance. Backtested better on both seasons. This also covers the Edey / Allen / Adebayo first-possession
   dunk: 16 of the 19 jumper first baskets came on his team's first shot.
2. Pull the top end in: 17%+ hit 15% vs 18.5% predicted last season. A mild shrink of shares toward 1 in 5
   (or a temperature of about 0.9 on the final probabilities) before computing fair odds.
3. Keep the tip winner scores first rate at 64% for now; 60% this season is noise at 68 games.
