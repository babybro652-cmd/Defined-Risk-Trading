# CRT + Divergence + S/R Confluence Indicator

TradingView Pine Script v6 indicator (`CRT-Divergence-SR.pine`) built for the
Defined Risk Trading process: it doesn't call trades on its own, it flags
where three independent signals line up so a discretionary trader can run the
pre-trade checklist against a real setup instead of scanning charts by hand.

## The three ingredients

**1. CRT (Candle Range Theory) - a 3-candle sequence**
- **Range candle**: sets a high/low.
- **Manipulation candle**: wicks beyond the range (sweeps liquidity) and
  closes back inside it - a false breakout / stop hunt.
- **Distribution candle**: confirms the reversal. In "Break of Range" mode
  (default, strict) it must close beyond the range candle's *opposite*
  extreme; in "Close Back Inside Range" mode (fast) it just needs to close
  in the reversal direction.

**Range Timeframe** (default `15`) is independent of whatever chart you're
looking at. Set it once to the timeframe you actually trade CRT on, and the
same formations, labels, and BUY/SELL signals show up whether you're viewing
the 15min chart itself or a 1min execution chart - you don't need to flip
timeframes to see if a setup is forming. This only works when the chart
timeframe is **at or below** the Range Timeframe (e.g. viewing 1min or 5min
while Range Timeframe is 15 is fine; viewing 30min or higher is not - the
status panel's Chart TF cell turns orange with a (!) if you're on an invalid
combination). Leave it blank to build CRT from the chart's own candles
instead.

**2. Support & Resistance - pivot-based, self-maintaining**
Tracks swing high/low pivots as horizontal levels, each valid until price
closes (or wicks, depending on **Break Invalidation**) through it. A CRT
sweep only counts as "at a level" if it comes within **Proximity Zone**
(a multiple of ATR) of a still-valid level.

**3. Divergence - regular RSI divergence at swing pivots**
Compares consecutive swing lows (bullish) or swing highs (bearish) on price
against RSI at the same pivots. A divergence stays "active" for
**Divergence Validity Window** bars, so it can still count toward a
confluence signal even if it formed a few bars before the CRT confirmation.
Each divergence pulse marks a small dashed line right at the pivot price
so you can see exactly where the swing high/low that triggered it sits,
alongside the "Bull Div" / "Bear Div" label.

**4. Bias Level - equilibrium + a Bull%/Bear% readout**
Draws a dotted line at the 50% equilibrium of the current CRT range (the
midpoint between the range candle's high and low) with a floating
"Bull - XX%" / "Bear - YY%" label pair next to it, in the spirit of a
generic "unbiased level" style display. The percentage is a composite score
built entirely from signals this indicator already tracks - it isn't a
clone of any third-party indicator's proprietary formula:

| Factor | Weight | Bullish when... |
|---|---|---|
| Price vs. equilibrium | 3 | close is above the 50% level |
| RSI vs. 50 | 2 | RSI is above 50 |
| Recent divergence | 2 | a bullish divergence is still within its validity window |
| Last confirmed CRT direction | 3, decaying | the most recent CRT confirmation was bullish (weight decays to 0 over **CRT Bias Decay** bars) |

The weighted sum is normalized to a 0-100% Bull score; Bear is `100 - Bull`.
Treat it as a quick read of which way the current confluence factors lean,
not a standalone signal.

**5. Trade Levels - Entry, Stop Loss, and three Take Profits**
Every BUY/SELL confluence signal draws a full trade plan, styled like a
typical entry/SL/TP callout:

- **Entry**: the distribution candle's close (the bar that confirmed the CRT reversal).
- **Stop Loss**: beyond the CRT sweep extreme (the manipulation candle's wick) by
  **Stop Buffer Beyond Sweep**, in ATRs - the level a valid setup shouldn't revisit.
- **TP1 / TP2 / TP3**: R-multiples of that risk (defaults 1R / 2R / 3R, all
  configurable), where 1R = the distance from Entry to Stop Loss.

Each level draws as a colored line extending right from the signal, with
its price flag anchored to the current bar - so as long as a level hasn't
been hit, its flag keeps sliding forward with new price action instead of
staying pinned back at the signal candle, the way a live price line
behaves. The moment price actually trades through a level, its line and
flag freeze in place right there, the flag grays out and "(HIT)" is
appended, so you can see at a glance which targets played out on a given
setup. If the Stop Loss is the one that hits, the trade is treated as
closed: any Take Profits that never got reached are removed from the
chart entirely rather than continuing to flow forward on a dead trade,
and Entry also stops moving and stays frozen at the stop-out bar. A new
confluence signal replaces the previous setup's levels entirely - only
one active setup is shown at a time.
Toggle the whole feature off with **Show Entry / SL / Take Profits**.

**Move SL to Breakeven at TP1, Trail at TP2/TP3** (on by default): once TP1
hits, the Stop Loss line moves up to Entry; once TP2 hits, it moves to TP1;
once TP3 hits, it moves to TP2. The original stop segment freezes in place
at the moment of each move so the chart still shows exactly where the stop
was at any point in the trade's history, and the new segment carries a
"(BE)" or "(TRAIL)" tag. Turn this off to keep a single fixed stop for the
life of the trade.

## The signal

A **BUY** confluence label + triangle fires when: a bullish CRT sequence
confirms, the sweep occurred at/through a tracked support level, and a
bullish RSI divergence is still active. **SELL** is the mirror at
resistance. Either `requireSR` or `requireDiv` can be turned off in the
Confluence Rules group to loosen the filter (e.g. CRT + S/R only, no
divergence requirement) - useful while backtesting which combination fits a
given instrument/session.

Unfiltered CRT patterns that don't reach full confluence still get a plain
"CRT" label so you can see what the filters excluded.

A 4-row status panel in the top-right corner (toggle with **Show Status
Panel**) shows: Range TF / chart TF (flagged if the chart TF is higher than
the Range TF, which breaks the multi-timeframe fetch), the current Bull/Bear
bias split (Bull in teal, Bear in red, each in its own cell), the last
BUY/SELL signal, and the active setup's direction, entry, and a live status
word - **WAITING** (no signal yet), **LIVE**, **TP1/TP2/TP3 HIT**,
**STOPPED**, **STOPPED (BE)**, or **STOPPED (TRAIL)** - so you can tell at a
glance whether that setup is still in play or already resolved, and whether
a stop-out was a full loss or a breakeven/trailed exit, without scrolling
back to find it on the chart.

## Alerts

Ten alert conditions are exposed, covering every stage of a setup:
full bullish/bearish confluence (BUY/SELL), raw (unfiltered) bullish/bearish
CRT patterns, bullish/bearish RSI divergence on its own, and Stop
Loss/TP1/TP2/TP3 hit on the active setup. Set alerts on whichever fits your
workflow - the divergence and outcome alerts in particular are worth
turning on if you're forward-testing and logging every occurrence, since
they're easy to miss just glancing at the chart.

## Suggested starting point for ES futures

- Range Timeframe: `15` (matches the 15min CRT / 1min entry workflow).
- Chart timeframe while scanning or executing: 1min, or 5min - anything at
  or below 15min will show the same signals.
- Keep both `requireSR` and `requireDiv` on for the highest-conviction
  signals; this will fire less often but each hit has three confirmations
  stacked.
- This indicator does not manage risk. Every signal still goes through the
  full checklist: defined risk before entry, daily/session loss limits, and
  the paper-trading track before size.

## Disclaimer

Educational tool only, not financial advice. Past pattern confluence does
not guarantee future results.
