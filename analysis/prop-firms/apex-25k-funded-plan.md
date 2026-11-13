# Apex 25K funded (PA) account: rules and the $1,000 payout plan (Fri 11/13/2026)

Read-only research. Nothing was traded, requested or changed.

## The account (from Gmail)

| What | Detail | Email |
|---|---|---|
| Eval bought | "25k Tradovate No Activation Fee Intraday Trail", $690 list, $621 off, **paid $69.00** (invoice NLLCJ1U) | Thu 11/12, 11:17 AM ET |
| Eval passed | APEX-694864-02 (Tradovate number APEX6948640000002). Eval equity ended at $27,394 | Thu 11/12, 7:31 PM ET |
| PA converted | "Your Tradovate Intraday PA is in the process of being activated". No activation fee charged (the "No Activation Fee" product) | Thu 11/12, 9:14 PM ET |
| PA active | **PA-APEX-694864-01**. Log out and restart Tradovate to see it | Thu 11/12, 9:16 PM ET |
| Eval closed | Eval subscription NLLCJ1U cancelled automatically | Thu 11/12, 9:15 PM ET |

- **The eval profit does not carry over.** The PA starts fresh at **$25,000**. The $27,394 was the eval only.
- No rules PDF came by email. The activation email links Apex's official pages "Intraday Trailing Drawdown PA Guidelines" and "Intraday Trailing Drawdown Payouts". **Open those two links from the 11/12 9:14 PM email before trading** and check the numbers below against them.
- Apex's help center blocked every automated read (HTTP 403), and no archived copy could be reached. The rules below come from dated third-party guides (Sept-Nov 2026) that quote the Apex help center. Where they disagree, it's flagged.

## Funded (PA) rules, 25K Intraday Trail

| Rule | 25K Intraday PA | Confidence |
|---|---|---|
| Drawdown | **$1,000, INTRADAY trailing.** Floor starts at **$24,000** and moves up with the highest balance, **open (unrealized) profit included**, in real time. Touch it and the PA is closed for good | High (all sources) |
| Where it stops trailing | Stops at **$25,100** (start + $100). That happens once the peak balance reaches **$26,100** | High (Tradervana 11/12, QuantCrawler 11/2026). One guide words it ambiguously |
| Safety net | **$26,100.** Only profit above it can be paid out, for the life of the PA | High |
| Contracts (scaling tiers) | Profit $0-999: **1 ES (10 MES)**. $1,000-1,999: **2 ES**. $2,000+: **2 ES**. Tiers update once a day at the 4:59 PM ET close, from the closing balance, and apply to the next session. Orders above the limit are rejected | Medium-high. QuantCrawler lists "4 minis / 40 micros", which looks like the eval limit. Check the dashboard |
| "Half size until buffer" rule | Not in the current (Apex 4.0, March 2026) rules. The tier table above replaced it. Practical effect is the same: **1 ES until the account has $1,000 profit** | Medium |
| Daily loss limit | **$500** at $0-1,999 profit, **$1,250** at $2,000+. Soft: positions flattened, trading paused until the next session, account kept. Resets 6 PM ET | **Uncertain for Intraday.** Two guides say the tier DLL applies to both drawdown types; Phidias and QuantCrawler say "no DLL on Intraday". Treat $500 as real |
| Qualifying days | **5 trading days with $100+ NET profit each** (after fees), not consecutive, no deadline. Counted fresh after every payout | High (4 sources). One older guide (prop25k, Sept) says "8 days, 5 of them $50+"; that's the pre-4.0 rule |
| What a trading day is | 6:00 PM to 4:59 PM ET. A day with less than $100 net doesn't count (it isn't a fail, it just doesn't qualify) | High |
| Consistency | **Best day must be under 50%** of total profit since the last payout. Breaking it doesn't fail the account; the payout button stays off until more profit brings it back under | High |
| Payout size | **Min $500, max $1,000** per payout, payouts 1 through 6 ($6,000 lifetime). After payout 6 the PA closes | High |
| Balance to request | **$26,600 for $500. $27,100 for $1,000.** The balance after the payout must stay at or above the $26,100 safety net. If the balance drops below the minimum while the request is pending, it's denied | High |
| Split | **100%** (90/10 only past $25,000 lifetime, which a 25K can't reach) | High |
| Timing | Up to weekly. Review about 2 business days, then payment. US ACH 1-3 business days after approval (propfirmsfinder 11/2); Traders Second Brain estimates 5-11 business days total. Provider: one source says Deel was dropped in 2026 for ACH/Plane, another still says Deel. Check the dashboard | Medium |
| Overnight | **Not allowed.** Flat with all orders cancelled by 4:59 PM ET | High |
| News | Allowed as part of a normal strategy. No orders on both sides of a release, no news-chasing strategies | Medium |
| Other | No hedging (across accounts or correlated products), no bots. **Inactivity: at least two $50+ net days every 30 days** or the PA closes | Medium-high |

## Can he get a full $1,000 paid within 5 trading days (Fri 11/13 to Thu 11/19)?

**NO, not paid.** On a perfect week he can **request** it after the close on Thu 11/19 (day 5), but the money lands about 2-11 business days later, and a perfect week is unlikely.

What blocks it:
1. **Safety net (the big one).** A $1,000 payout needs a balance of **$27,100 = $2,100 profit**, not $1,000. The first $1,100 of profit can never be withdrawn.
2. **5 qualifying days.** All 5 days must close **$100+ net**. One red or flat day pushes the request out a day, and a red day also has to be made back.
3. **Contract tier.** 1 ES until $1,000 profit. $2,100 in 5 days means about $420 a day, every day. On 1 ES that's an 8.4 pt winner daily.
4. **Processing.** Review plus payment adds 2-11 business days after the request.
5. Consistency is **not** a blocker if the days are even ($400-500 each is about 20-24% of the total).

**Realistic dates.** One red day in the next two weeks: request about **Mon 11/23 or Tue 11/24** (trading day 7-8). Cash about **Mon 11/30 to Fri 12/4**, since Thanksgiving week (CME closed Thu 11/26, half day Fri 11/27) slows it. Two red days or a slow week: request in the **first week of December**.

## Day-by-day plan

Same rules as always: NY session only, **10 AM-12 PM ET**, wait for the label, **hard stop 3.5-4 pts from entry**, fixed target, no trailing a runner. ES = $50/pt, about $3 fees per ES round turn (from the 11/12 eval). MES = $5/pt.

**Funded daily stop:** his personal max of $1,000 a day equals the whole drawdown here, so it does not apply. **One loss and done** while the trail is still moving (peak below $26,100). After the floor locks at $25,100, **two losses or -$420, whichever comes first.**

| Day | Contracts | Daily target | Daily stop | Done for the day when | Running profit if on plan |
|---|---|---|---|---|---|
| 1 Fri 11/13 | 1 ES (tier 1) | +$400 (one 8 pt win) | 1 loss (about -$205) | +$400 hit, or 1 loss, or 12 PM | $400. Floor $24,400 or higher |
| 2 Mon 11/16 | 1 ES | +$400 | 1 loss | Same | $800 |
| 3 Tue 11/17 | 1 ES (still under $1,000) | +$400 | 1 loss | Same | $1,200. Peak passes $26,100, **floor locks at $25,100** |
| 4 Wed 11/18 | Up to 2 ES (tier 2). 1 ES is fine | +$450 (2 ES x 4.5 pts, or 1 ES x 9) | 2 losses or -$420 | +$450, or the stop, or 12 PM | $1,650 |
| 5 Thu 11/19 | Up to 2 ES | +$450-550 (aim for $2,200 total for a fee cushion) | 2 losses or -$420 | Total at $2,200+, or the stop, or 12 PM | $2,100-2,200, balance $27,100-27,200 |
| After close 11/19 | | Request **$1,000** only if all 5 days were $100+ net and the balance is $27,100+ | | | |
| Days 6+ (if behind) | Same tier rules | Keep $400-450 a day | Same | Same | Continue until $2,100 and 5 qualifying days |

Rules inside the plan:
- **A qualifying day needs $100 NET.** On 1 ES a 2-pt win nets about $97 and does **not** count. Take 2.25+ pts or the day doesn't count.
- **Consistency guard: stop for the day at +$800.** If total profit will be about $2,100-2,200, a single day has to stay under about $1,050. Stopping at $800 keeps it safe even if another day goes red. Never "make it all back in one day".
- **No adds before tier 2, and no adds at all before the floor locks.** A 1 ES trade is the only position on days 1-3.
- **While a payout request is pending: don't trade**, or 1 ES with a 1-loss stop. A drop below $27,100 before approval cancels the request.
- Behind plan is fine. Being late is not a rule break; overtrading to catch up is how the London accounts went.

**MES option** (10 MES = 1 ES, so tier 1 = 10 MES max):

| Size | Risk on a 4 pt stop | 8 pt win | Days to $2,100 at 1 win a day |
|---|---|---|---|
| 1 ES | $200 + fees | $400 | 5-6 |
| 10 MES | $200 + more fees (about $1/contract round turn, so about $10) | $400 | 5-6, slightly worse fees |
| 5 MES | $100 | $200 | 10-11 |
| 3 MES | $60 | $120 | 18. Each win barely clears the $100 qualifying bar after fees |

Use 5 MES for any day right after a red day (slows the payout, protects the account). Otherwise 1 ES.

## How to request the payout

1. Before requesting, check: 5 days of $100+ net since the PA started, best day under 50% of total profit, balance at least **$27,100** (safety net $26,100 + $1,000), and no open positions.
2. Log in at apextraderfunding.com (member login, user ID timwill652) and open the dashboard.
3. Go to the Performance Account **PA-APEX-694864-01**. The **Request Payout** button only shows when all requirements are met. If it's missing, one rule isn't met yet.
4. Enter **$1,000** and confirm the payout method on file. Complete any payment-provider, ID or tax form it asks for (the first payout usually asks). The method has changed in 2026 (Deel vs ACH/Plane); use whatever the dashboard shows.
5. Submit, take a screenshot of the confirmation, and keep the balance above $27,100 until it's approved (best: don't trade until then).
6. Approval takes about 2 business days, payment 1-3 business days on ACH, and up to 11 business days total by some reports. Questions go to the new Apex help desk (email from Apex 11/12, 9:43 PM ET).

## The #1 risk: the $1,000 intraday trailing drawdown, sized up the way he passed the eval

- **The whole account is one bad 4 ES trade.** On 11/12 he passed by trading 2 ES, then scaling to 4 ES. In this PA, $1,000 is **20 pts on 1 ES but only 5 pts on 4 ES**, one stop plus slippage.
- **Open profit moves the floor.** Until the peak balance reaches $26,100, every point a trade runs in his favor raises the floor, even if price comes back. A 1 ES trade that runs +10 pts and comes back to entry moves the floor up $500 and leaves $500 of room. That's how drawdown accounts die without a big loss, and drawdown is what took the two accounts on 11/11.
- **The fix is his own rules plus three funded-only ones:** 1 ES until $1,000 profit (the tier enforces it), no adds until the floor locks at $25,100, a fixed 8 pt target in the same bracket (no running trades), and one loss and done until the floor locks.

## Sources

- Gmail (read-only): Apex receipt 11/12 (NLLCJ1U, $69), passed-eval email 11/12, PA conversion email 11/12, PA active email 11/12 (PA-APEX-694864-01), subscription cancelled 11/12, help desk notice 11/12.
- [Tradervana, Apex rules (updated 11/12/2026)](https://www.tradervana.com/guides/apex-trader-funding-rules): drawdown stop at $25,100, safety net $26,100, tiers, DLL, 5 x $100 days, inactivity, overnight, news.
- [propfirmsfinder, Apex payouts (data verified 11/2/2026)](https://propfirmsfinder.com/prop-firm/apex-trader-funding/payouts/): $1,000 cap x6, $26,600 to request, balance after payout, ACH 1-3 days.
- [Copilink, Apex payout rules (checked 11/4/2026)](https://copilink.com/prop-firms/apex-trader-funding): safety net, 5 x $100, 50% consistency, auto-denial.
- [QuantCrawler, Apex rules (Nov 2026)](https://quantcrawler.com/learn/apex-trader-funding-rules): $1,000 intraday trail from $24,000, stops at $25,100, "no DLL" on 25K Intraday.
- [TraderPayout, Apex scaling plan (6/15/2026)](https://traderpayout.com/apex/apex-trader-funding-scaling-plan): 25K tier table, DLL applies to both drawdown types, daily tier update.
- [FundedSim, Apex PA rules](https://fundedsim.com/en/guides/apex-performance-account-rules) (undated): tiers, 5 x $100, $26,600, inactivity.
- [Traders Second Brain, Apex payout rules (9/22/2026)](https://traderssecondbrain.com/guides/apex-payout-rules-explained): 5-11 business day estimate.
- [Phidias, Apex 4.0 explained](https://phidiaspropfirm.com/education/apex-trader-funding-4-0-explained) (competitor, March 2026): "no DLL on Intraday", overnight rule.
- [prop25k review (Sept/Oct 2026)](https://www.prop25k.com/review/apex-trader-funding/): older 8-day / $50 rule, shown as the outlier.
- [rbtrading (10/8/2026)](https://rbtrading.site/prop-firms/apex-trader-funding-rules): trading day 6 PM-4:59 PM ET, no overnight.
- Apex's own help center (support.apextraderfunding.com, apextraderfunding.com/help-center) returned 403 to automated reads. Most of these sites are affiliates.
