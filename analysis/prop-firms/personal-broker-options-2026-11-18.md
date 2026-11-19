# Personal broker options: $100 MES account on TradingView (researched 11/18-11/19/2026)

Tim's ask (11/18): "Research a broker that I can use to start trading my own money ($100), but I need to use TradingView."

Research only. Nothing was opened, funded or linked. Numbers come from broker pages and TradingView broker listings where
possible; third-party figures are marked "(3rd party)". Fees change, so confirm each number on the broker's own fee page
before funding.

## Bottom line

- The product is **MES** (Micro E-mini S&P 500, $5 a point). Full ES is out of reach. There is no smaller S&P 500 futures
  contract than MES that TradingView routes.
- **$100 can open an account at a few brokers, but it is not enough to trade Tim's rules.** One 4 pt stop is about $22 with
  fees, 22% of the account. Two stops (a normal bad day under his 1-2 trade rule) take the account to about $56, right at the
  $50 day margin. Realistic runway: 2 stops, maybe 3.
- **Workable balance:** about $500 (each stop about 4-5% of the account, roughly 18-20 stops of runway). About $1,000 or more
  is where a 4 pt MES stop is near the usual 2% risk guideline.
- **Recommendation:** don't fund this month. If he wants to start small later, Tradovate retail is the simplest fit (same
  platform family as his Apex logins, $0 minimum, $50 day margin, no TradingView fee). AMP Futures is the best backup ($100
  minimum, $40 day margin, no inactivity fee). Open a free demo first to check the TradingView phone app flow.

## Top 3 for a $100 MES account on TradingView (cheapest all-in first)

| Rank | Broker | Min deposit | MES day margin | Est. all-in per round turn (1 MES) | Est. monthly cost | Watch out for |
|---|---|---|---|---|---|---|
| 1 | **Tradovate retail** (NinjaTrader group), Free plan | $0 ("any funding amount") | $50 | about $1.90 ($0.39/side commission + about $0.37 exchange + about $0.20 clearing/NFA, per side) | $0-4 (CME Level 1 data: about $4 CME only, $12 CME bundle; one 3rd-party guide says Level 1 is free while funded) | Inactivity fee: $35 if no live trade in 30 days on the Free plan (NinjaTrader's TradingView listing; 3rd-party guides agree). Tradovate's own TradingView listing shows none, so confirm. On $100 that fee alone is 35%. |
| 2 | **AMP Futures** (TradingView via CQG) | $100 | $40 (lowest found) | about $2.00 (commission $0.44-0.60/side, 3rd party, unconfirmed; + exchange/NFA + CQG route $0.10/side) | $5 (CQG CME Level 1, non-pro; $15 for the CME bundle), effective 6/1/2026 | Commission not on a page I could open (AMP's FAQ blocks fetches). Data is billed for the full month even if used one day. No withdrawal or inactivity fee per TradingView listing. |
| 3 | **Plus500US Futures** | $0 on TradingView listing (reviews say $100) | about $50 | about $1.70 ($0.49/side + exchange/NFA, which Plus500 doesn't publish) | $0 reported (reviews say real-time data included); not confirmed for the TradingView connection | TradingView's listing shows a **1% deposit fee and 1% withdrawal fee**. Newer TradingView partner (connection announced 2026), fewer user reports. |

All three: CFTC-registered FCMs / NFA members, listed as TradingView brokers, no TradingView connection fee from the broker,
and they appear on TradingView's list of brokers whose data can carry over to TradingView. TradingView's own plan (Tim's
Essential) is separate and already paid.

**Per-trade math for Tim's stop:** 4 pts x $5 = $20, plus about $2 fees = **about $22 per full stop on 1 MES**. Add 1-2 ticks of
slippage on a stop order ($1.25-2.50) on fast days.

## The $100 reality check

Assume $50 day margin, $22 per stop, $4/month data:

| After | Balance | Can open a new MES trade? |
|---|---|---|
| Fund + first month data | $96 | Yes |
| Stop 1 | $74 | Yes |
| Stop 2 | $52 | Barely; an open trade that goes 0.5 pt against him puts equity under margin, and the broker can liquidate before his 4 pt stop |
| Stop 3 | $30 | No (under margin) |

- AMP's $40 margin buys about the same runway (95, 73, 51, then 29 after stop 3).
- One bad day at his 2-trade max = about -44% of the account.
- Day margin only lasts during the broker's day session window (Webull's ends 4:15 PM ET, for example). Holding past it needs
  full margin (about $2,400-2,900 per MES), so on a small account the broker closes the trade. Tim's 10 AM-4 PM window fits,
  but he has to be flat before the cutoff.
- The pattern day trader rule does not apply to futures.

## What balance makes it workable (no assumptions about his finances)

| Balance | One 4 pt MES stop (about $22) as % of account | Stops of runway before margin | Read |
|---|---|---|---|
| $100 | 22% | 2-3 | Lottery ticket, not a test of his rules |
| $300 | 7% | about 11 | Tight but usable for 1 trade a day |
| $500 | 4.4% | about 20 | Workable floor for his 1-2 trade rule |
| $1,000 | 2.2% | about 43 | Near the common 2% risk guideline |
| $2,000 | 1.1% | about 88 | Comfortable |

Suggested personal account rules if he funds it: 1 MES only, same 3.5-4 pt hard stop from entry, NY 10 AM-4 PM, daily max
loss = 1 stop until the account is above $500, flat before the day-margin cutoff.

## Other brokers checked

| Broker | Why not top 3 for $100 |
|---|---|
| NinjaTrader Brokerage | Same company as Tradovate; $0 min, $50 MES day margin, $0.39/side micros on the free plan, $35 inactivity fee after 30 days. Basically the same deal as Tradovate. NFA fined NinjaTrader $250k in May 2025 over its AML program (3rd party). |
| Ironbeam | $0 minimum, $50 MES day margin, $0.39/side micros (lower promo rates need a $1,000 deposit and referral code). Ironbeam itself recommends $1,000 to day trade micros. Good option once the account is $1,000+. |
| Optimus Futures | $500 minimum for micros, $50 MES day margin, micros from $0.25/side. Fine at $500+. |
| Edge Clear | $500 minimum (TradingView listing); micros $0.20/contract promo for new customers. |
| TradeStation | $0.50/side futures, intraday margin about 10% of initial (about $290 on MES); $100 not enough. |
| Webull Futures | MES day margin $100.95 on Webull's own page, so $100 can't open 1 MES. |
| tastytrade | $0.75/side micros; intraday margin is 25% of overnight (about $500+ on MES). $100 not enough. |
| Interactive Brokers | Connects to TradingView, but margins on MES are much higher than the discount futures brokers; not a $100 option. |

**Event contracts / nano contracts:** Tradovate lists event and nano contracts at $0.05, but those are yes/no event contracts
and crypto nanos, not an S&P futures product that fits his 4 pt stop and label entry. Not relevant to his rules.

## Market data on TradingView

- TradingView's help page says that if you buy real-time data through a listed broker (Tradovate, NinjaTrader, AMP, Ironbeam,
  Optimus, Plus500, EdgeClear, TradeStation, tastytrade, Webull, IBKR and others) and log in through the Trading Panel, you
  don't pay TradingView again; it re-verifies at each login and lasts 7 days.
- Tradovate: TradingView says orders to Tradovate need the data bought on the Tradovate side; data bought on TradingView alone
  doesn't allow order placement.
- Buying CME data from TradingView directly costs about $7-9.95/month for non-pros (3rd party), not needed if the broker covers it.
- Non-pro status: he trades his own money and prop accounts; he should declare non-professional. Prop-firm data agreements are
  separate from a personal account.
- TradingView phone app: broker trading in the Trading Panel works in the TradingView mobile app for supported brokers. Confirm
  with a demo login on his phone before funding (user reviews mention logouts and drag-to-move SL/TP limits on Tradovate and
  NinjaTrader).

## Running it next to his Apex (Tradovate) prop logins

- TradingView keeps one broker login active in the Trading Panel at a time; switching means logging out of one and into the
  other. A personal Tradovate account is a separate Tradovate username from the Apex-issued one.
- Biggest risk is **placing a trade on the wrong account.** Check the account name in the Trading Panel before every order.
- Real-time data stays on: either connection keeps TradingView's CME verification alive for 7 days.
- Don't hold opposite positions in the personal and prop accounts at the same time. Prop firms generally ban hedging across
  accounts; check Apex's current rules before trading both.
- AMP or Plus500 avoid any Tradovate login mix-up because they're a different broker in the Trading Panel list.

## Sources

- Tradovate pricing: https://www.tradovate.com/pricing/
- TradingView broker listing, Tradovate: https://www.tradingview.com/broker/Tradovate/
- TradingView broker listing, NinjaTrader: https://www.tradingview.com/broker/NinjaTrader/
- TradingView broker listing, AMP Futures: https://www.tradingview.com/broker/AMP_Futures/
- AMP exchange/platform data fees (effective 6/1/2026): https://www.ampfutures.com/trading-info/platform-data-fees/
- AMP MES $40 day margin: https://ampfutures.com/news/cme-e-micro-indices-launched-ready-for-live-trading
- AMP commissions (3rd party): https://nexusfi.com/a/brokers/amp-futures-broker-guide , https://www.metrotrade.com/amp-futures-vs-metrotrade-compared/
- TradingView broker listing, Plus500US: https://www.tradingview.com/broker/Plus500US/
- Plus500US joins TradingView: https://liquidityfinder.com/news/plus500us-joins-tradingview-for-direct-futures-trading
- Plus500 reviews (min deposit, data): https://www.barchart.com/brokers/plus500us , https://investingintheweb.com/reviews/plus500-futures-review
- Tradovate fees explained, July 2026 (3rd party): https://damnpropfirms.com/trading-guides/tradovate-fees-explained-commissions-data-plans/
- Tradovate review, Aug 2026 (3rd party): https://www.quantvps.com/blog/tradovate-review
- NinjaTrader pricing / MES day margin: https://ninjatrader.com/eu/en-it/pricing/ , https://www.metrotrade.com/ninjatrader-vs-metrotrade-futures-broker-comparison/
- NinjaTrader NFA fine (3rd party): https://www.daytrading.com/ninjatrader
- Ironbeam minimum and micros: https://www.ironbeam.com/knowledge-base/what-is-the-minimum-deposit-to-open-an-account/ , https://www.ironbeam.com/no-account-minimums-at-ironbeam-heres-what-we-recommend-for-trading-micro-and-mini-futures-contracts/
- Optimus Futures margins: https://optimusfutures.com/Platforms/Margin-Rates.php , https://optimusfutures.com/
- Edge Clear on TradingView: https://www.tradingview.com/broker/EdgeClear , https://tradingtoolshub.com/blog/edgeclear-pricing-guide-2026/
- TradeStation: https://www.tradestation.com/pricing/promotions/ , https://www.metrotrade.com/tradestation-vs-metrotrade-futures-broker-comparison/
- Webull futures margins: https://www.webull.com/futures-margin-rates
- tastytrade futures: https://tastytrade.com/futures , https://www.metrotrade.com/tastytrade-vs-metrotrade-futures-broker-comparison/
- TradingView, broker data carries over: https://www.tradingview.com/support/solutions/43000479666/
- TradingView CME data price (3rd party): https://daytradingtoolkit.com/trading-tools-tutorials/tradingview-pricing-explained
- One broker at a time in the Trading Panel (3rd party): https://blog.traderspost.io/article/hacking-tradingview-multi-broker-and-multi-asset-trading-from-tradingview , https://pickmytrade.trade/debugging/tradingview-multiple-prop-accounts-copy/
