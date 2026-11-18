# Order flow "absorption bubbles": what's possible, 11/18/2026

Research only. Nothing was built, bought or signed up for. Private analysis (indicator names are fine here).

**The ask (Tim, 11/18):** bubbles like the Profit Pro reel in DRT Phone
(`Screen_Recording_20261118_125009_Facebook.mp4`, ATAS / NinjaTrader on NQ): big-volume bubbles with numbers on
the candles as price drops into a high-volume node (HVN), the biggest bubble (~481) at the zone low where price
stops falling ("heavy absorption"), then a long with the stop under the zone.

**What the clip needs underneath:** traded volume split by bid and ask, per price, per bar (footprint data), plus
a volume profile for the HVN. "Absorption" means a lot of aggressive selling hits the bid at a level and price
does not go lower. You can only see that honestly with bid/ask traded volume. A plain volume bar can show "a lot
traded here", not who was aggressive or that passive buyers soaked it up.

## Short answer

| Path | Monthly cost | What he gets | Close to the clip? |
|---|---|---|---|
| 0. Tradovate "Bid-Ask Volume" chart (already on his Apex login) | $0 (verify) | Real bid x ask numbers per price on each candle | Numbers yes, bubbles no; not on TradingView |
| a. Pine proxy on current Essential plan | $0 (plus $7 CME real-time if he doesn't have it) | Bubbles sized by bar volume at a Pine-built HVN, wick/close-position "held" test | About 40%: looks similar, can't see bid vs ask |
| b1. TradingView Plus | $34.95/mo ($29.95/mo yearly) | Native footprint chart type to read by eye, second bars (better delta estimate in Pine) | About 60% by eye; Pine still can't read footprint |
| b2. TradingView Premium | $69.95/mo ($59.95/mo yearly) | Pine `request.footprint()`: real buy/sell volume per price row, delta, POC, imbalance, so Pine can draw true absorption bubbles | About 85%; no DOM / resting orders |
| c. NinjaTrader 8 + Order Flow+ | $59/mo (or $1,499 lifetime plan) | Volumetric bars + Order Flow Trade Detector bubbles, logs in with his Apex Tradovate account | About 90%, the clip's own tool family; Windows desktop only |
| c. ATAS Pro | EUR 69.95/mo (EUR 39.95/mo yearly) | Cluster charts, big-trades bubbles, the other tool in the clip | About 95%; Rithmic route, desktop only |

**Cheapest real bubbles (true bid/ask):** NinjaTrader Order Flow+ at $59/mo is the cheapest packaged "bubbles
on candles" tool, but TradingView Premium at $69.95/mo is the cheapest way to get them **on his phone and on his
current charts** (Pine indicators draw in the TradingView mobile app; NinjaTrader Order Flow+ is desktop only).

**Recommendation:** spend $0 this month. (1) Open the Tradovate Bid-Ask Volume chart on his Apex login and watch
a few Div levels for real numbers. (2) If Tim says go, Jarvis has a Pine volume-bubble proxy built on Essential
and forward-logs "big volume at the Div pivot, low held" as a tag. (3) Only if that tag looks like it helps after
3-4 weeks, take **one month of TradingView Premium ($69.95, cancel after)** to build and test the real version
with `request.footprint()`. Skip ATAS, Sierra Chart, Bookmap and Jigsaw for now: they mean a new desktop
platform and, for most, a Rithmic account Apex won't convert his Tradovate PA into.

## 1. TradingView native, CME ES

Plan availability is read from the live pricing page's own plan table (tradingview.com/pricing, fetched
11/18/2026; plan ids in the page data: `pro` = Essential, `pro_realtime` = Plus, `pro_premium` = Premium,
`pro_premium_expert` = Ultimate). Several third-party articles disagree with each other; the page data wins.

| Feature | Essential (Tim) | Plus | Premium | Ultimate |
|---|---|---|---|---|
| Volume footprint chart type | No | Yes | Yes | Yes |
| Volume profile indicators (Session, Visible Range, Fixed Range, Periodic) | Yes | Yes | Yes | Yes |
| Predefined second intervals (1s, 5s...) | No | Yes | Yes | Yes |
| Historical data by the second | No | No | Yes ("all", from Aug 2022) | Yes |
| Custom second intervals | No | No | No | Yes |
| Tick-based intervals | No | No | No | Yes (Expert too) |
| Pine `request.footprint()` | No | No | Yes | Yes |
| Built-in Volume Delta / CVD | Yes (estimate, below) | Yes | Yes | Yes |
| Large-trade bubbles | Not a native feature on any plan | | | |

Prices (list, monthly billing): Essential $14.95, Plus $34.95, Premium $69.95; billed yearly: $12.95 / $29.95 /
$59.95 a month (Premium $719.40/yr). Tim pays $18.99/mo, above the $14.95 web list price, which suggests an App
Store / Google Play subscription; upgrading on the website is usually cheaper than in the app. Check before any
upgrade.

- **Footprint chart:** Plus and up. It shows sell volume left / buy volume right per price, POC, imbalance lines
  (default 300%), value area, and delta per bar. Recent bars use finer intrabar data, older history coarser;
  tick-based calculation needs a plan with tick data (up to 3 million ticks). **Mobile:** no TradingView source
  confirms the footprint chart type in the iOS/Android app. Unverified; check on a trial before paying for it.
- **Volume Delta / CVD built-ins:** they are estimates. By default each intrabar's volume is counted as buy if
  the intrabar closed up and sell if it closed down (1-minute intrabars on minute charts, 1-second on second
  charts). On Essential, a 1-minute ES chart has no lower timeframe to look into, so delta on his 1m chart is
  close to meaningless. Tick-based mode (aggressor side from the exchange) needs a tick-data plan.
- **Volume profile / HVN:** all paid plans, so Essential already has Session VP, Visible Range VP, Fixed Range
  VP (also a drawing tool, works on mobile). HVN zones like the clip's are available today.
- **CME real-time data:** separate from every plan. Without it CME symbols are 10 minutes delayed (useless for
  order flow). TradingView's CME page lists real-time CME Group futures at **$7.00/month, non-professional**
  (one third-party source cites $9.95; the TradingView page says $7.00). If Tim already sees live ES on
  TradingView, he has it or gets it through another route; confirm under his TradingView account, Data.

## 2. What Pine Script can do

- **`request.footprint(ticks_per_row, va_percent, imbalance_percent)`** exists in Pine v6 (added early 2026).
  TradingView's Pine docs: "only users who have a Premium or Ultimate plan can use scripts that call it", one
  unique call per script. It returns, per bar: `footprint.buy_volume`, `sell_volume`, `delta`, `poc`, `vah`,
  `val`, `rows`, `get_row_by_price`, and per price row `volume_row.buy_volume / sell_volume / delta /
  has_buy_imbalance / has_sell_imbalance`. That is the data the clip's bubbles are made of.
- **`request.security_lower_tf()`:** pulls intrabar bars (up to 100K intrabars on Essential/Plus/Premium). On
  Essential, the lowest timeframe is 1 minute, so on Tim's 1m chart there is nothing below to read; on a 5m
  chart it gives 5 one-minute bars per candle (coarse). Plus and up add 1-second bars, so a 1m candle gets up to
  60 sub-bars and the up/down-close delta estimate gets much better. Still an estimate, not bid/ask.
- **Size-scaled bubbles at an HVN:** yes on any plan. Pine can build its own volume profile (spread each bar's
  volume across its range over a lookback, find high-volume rows), then draw `label.new` circles whose size and
  text scale with volume (e.g. a volume z-score over the last 20-50 bars), only when the bar sits inside an HVN
  row. Labels draw in the mobile app too.
- **What a proxy on Essential can't capture:**
  - who was aggressive (sells hitting the bid vs buys lifting the offer): one volume number per 1m bar;
  - where inside the bar the volume traded (the clip's 481 sits at one price, a proxy only knows the bar);
  - resting limit orders (absorption is passive buyers soaking up sellers; even the real footprint only shows
    the result, the DOM shows the orders, and no TradingView plan gives a DOM history);
  - "price not moving" at the tick level. The best a proxy can do is: big volume + close in the upper part of
    the bar after a down move + the low not broken for N bars. That flags a high-volume reversal candle, which
    is often absorption but can also be stops running or a news spike.
- **History caveat:** footprint data for older bars can be thin or missing (`na`), so any backtest of a
  footprint filter will be short.

## 3. Dedicated tools

Tim's accounts: Apex PA-02 funded, Tradovate-based. Apex does not convert accounts between Rithmic and
Tradovate, so a Rithmic-only tool means a new Apex plan. Apex data comes with the account (non-professional),
and Apex's help center says add-ons like Order Flow+ are bought through Tradovate or NinjaTrader, not Apex.

| Tool | Cost | Data for CME ES | Connects to his Apex Tradovate account? | Phone |
|---|---|---|---|---|
| **Tradovate built-in** (Bid-Ask Volume chart style) | Included (reported); Order Flow+ upgrade price not listed on tradovate.com (one user cites $720/yr) | Through the Apex account | Yes, it is his platform | NinjaTrader/Tradovate mobile app exists; footprint on mobile unverified |
| **NinjaTrader 8 + Order Flow+** | $59/mo add-on, or included with the $1,499 lifetime plan; the free license from eval firms excludes it | Through Apex/Tradovate login | Yes (NinjaTrader owns Tradovate; Apex Tradovate accounts log into NT8) | Order Flow+ is a desktop (Windows) feature |
| **ATAS** | Plus EUR 24.95/mo is 15-min delayed for futures; Pro EUR 69.95/mo (EUR 39.95 yearly), Ultra EUR 89.95; lifetime Pro EUR 1,799 | Via Rithmic (or dxFeed) | Rithmic is the documented route; Tradovate not confirmed by ATAS's page | No (Windows/macOS) |
| **Sierra Chart** | Package 5 about $36-60/mo, exchange fees on top (CME non-pro L1 $1.55, L2 $12.10/mo per exchange, NexusFi citing CME) | Rithmic or Denali | Rithmic route | No |
| **Bookmap** | Global Plus $297 per 3 months or $948/yr (about $79-99/mo); CME data add-on extra unless via broker | Rithmic, Tradovate and others listed | Tradovate listed as a connection | No phone app found |
| **Jigsaw daytradr** | About $579 one-time (prop connections included); other sources list $50/mo | Rithmic, Tradovate | Yes (reported) | No |

Closest to the clip: ATAS (big-trades / cluster bubbles) and NinjaTrader Order Flow+ (Order Flow Trade Detector:
markers for big volume at bid/ask, at a price, or single block trades, sized and colored by buy/sell share).
Bookmap shows the resting orders too (the heatmap), which is the most honest view of absorption, but it is the
priciest and Windows-heavy. Jigsaw is DOM/tape, not candle bubbles.

**No dedicated order-flow platform here has a phone app with footprint/bubbles.** For Tim's 10 AM lunch break on
the phone, TradingView (Pine on mobile) is the only path that reaches his phone.

## 4. Paths, cheapest first

**(0) $0, now: Tradovate Bid-Ask Volume.** On his Apex Tradovate web login: Chart, style "Bid-Ask Volume". Real
bid x ask numbers per price. No bubbles, no TradingView, desktop/web. Good enough to look at what happened at a
few Div pivots before spending anything. Verify it shows for his account.

**(a) Pine proxy on Essential: $0/mo** (+$7/mo only if he doesn't already have CME real-time on TradingView).
Bubble on 1m bars with volume in the top few percent of the session, inside a Pine-built HVN, labeled with the
volume number, plus a "held" check (close in the upper/lower third, extreme not broken for N bars). Looks like
the clip; is a high-volume-reversal detector, not absorption. Works on mobile. Build only on Tim's go.

**(b1) Plus: +$16-20/mo over today.** Native footprint chart by eye on desktop (mobile unverified), 1-second
bars so the Pine proxy's delta estimate gets real sub-bar detail. Pine still can't read the footprint, so no
automatic true bubbles. Middle step; skip it unless Tim wants to read footprints by eye on TradingView.

**(b2) Premium: +$51/mo over today ($69.95/mo; $59.95 yearly).** `request.footprint()` lets Pine draw true
absorption bubbles: biggest sell-volume row at the bar low inside the HVN, delta strongly negative, low holds.
Closest thing to the clip on his own charts and his phone. One month is enough to build and forward-test.

**(c) Separate platform: $59/mo (NinjaTrader Order Flow+) to EUR 69.95/mo (ATAS Pro).** The clip's exact look,
true bid/ask, desktop only, a second platform to learn. ATAS likely means a Rithmic Apex account.

**Money:** Tim is tight this month and the week of 11/26 is short (Thanksgiving, fewer full sessions). Nothing
here should be bought this month. Path (0) and (a) cost nothing; Premium is a one-month test for December at the
earliest, and only if the free tag shows promise.

## 5. Absorption as a Div entry filter

The 11/18 indicator analysis (`indicator-analysis-2026-11-18.md`) found **Div entered at the label** is Tim's
best signal: 83 signals in NY 10-4, 37% win, +9.8R / +$1,548 on 1 ES at 4/8 (+$3,178 taking the first 2 a day),
but only about 0.7 standard errors from zero, so not proven.

The idea fits: a Bull Div pivot low with heavy sell volume that doesn't break (absorption) should hold more often
than a pivot low on thin volume. That's the clip's setup in Tim's terms. Caveats:

- **Can't test it on what we have.** The cached ES bars (`data/es_bars_1m.csv.gz`, 10/20-11/18) have OHLC but no
  volume column, and the sheets don't log volume or delta. So no backtest today.
- **A filter shrinks n.** Cutting 83 trades to, say, 30 makes any result even less certain. It needs a forward log.
- **How to test it for $0:** have the Div alert also send the pivot bar's volume, its volume rank in the session,
  and the proxy "held" flag (all Pine on Essential), logged to the Forward Test Log; after 3-4 weeks compare Div
  win rate with vs without the tag. If the tag helps, that's the case for one month of Premium to test the true
  bid/ask version.
- Stop rule is unchanged: Tim's stop stays a fixed 3.5-4 pts from entry, not "under the zone" as in the clip.

## Sources

- TradingView pricing and plan table (plan availability read from page data, 11/18/2026): https://www.tradingview.com/pricing/
- TradingView blog, volume footprint chart type ("Premium and higher-tier plans" at launch): https://www.tradingview.com/blog/en/new-chart-type-volume-footprint-44399
- TradingView Help, Volume footprint chart: https://tradingview.com/support/solutions/43000726164-volume-footprint-chart
- TradingView Help, Cumulative Volume Delta (how delta is estimated): https://in.tradingview.com/support/solutions/43000725058-cumulative-volume-delta/
- TradingView blog, Volume Delta indicators: https://www.tradingview.com/blog/en/new-volume-delta-indicators-44132
- Pine docs, Other timeframes and data (`request.footprint`, `request.security_lower_tf`): https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data
- Pine docs, Limitations (footprint Premium/Ultimate only; intrabar limits): https://www.tradingview.com/pine-script-docs/writing/limitations/
- footprint.* / volume_row.* function list: https://blog.traderspost.io/article/pine-script-footprint-volume-row-functions
- TradingView CME real-time ($7.00/mo non-pro): https://www.tradingview.com/cme/
- TradingView footprint limits vs dedicated platforms: https://traderprofesional.com/en/footprint-tradingview/ and https://www.luxalgo.com/compare/tradingview/footprint-chart/
- ATAS pricing: https://atas.net/pricing/
- NinjaTrader Order Flow Trade Detector: https://ninjatrader.com/support/helpguides/nt8/order_flow_trade_detector.htm
- NinjaTrader Order Flow+ ($59/mo or lifetime plan; not in free eval license): https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1296751-order-flow-add-on-in-ninjatrader-if-i-already-pay-for-it-in-my-tradovate-account and https://ninjatrader.com/pricing/
- Tradovate pricing (Order Flow+ listed, no price): https://www.tradovate.com/pricing/
- Tradovate Bid-Ask Volume chart style: https://pickmytrade.trade/fr/how-to/tradovate-bid-ask-volume-charts/
- Apex Rithmic vs Tradovate (no conversion), commissions: https://blog.pickmytrade.io/rithmic-vs-tradovate-vs-cqg-fees-latency-measured-2026/ and https://www.benzinga.com/money/apex-trader-funding-rithmic-vs-tradovate-accounts
- Sierra Chart packages and CME fees: https://nexusfi.com/a/data/exchange-data-fees-market-data-costs and https://support.optimusfutures.com/what-is-the-pricing-for-sierra-chart-platform-subscription-information
- Bookmap data and connections: https://bookmap.com/bmdata
- Jigsaw daytradr: https://thegodfunded.com/en/tools/jigsaw-trading/ and https://daytradr.jigsawtrading.com/data-feeds.html
- Free community Pine bubble proxies (reference only): https://www.luxalgo.com/library/indicator/4O5cdSZ9-big-notional-volume-bubbles-lower-tf-order-flow-approximation/

Prices from third-party pages conflict in places (noted above); confirm on the vendor page before any purchase.
