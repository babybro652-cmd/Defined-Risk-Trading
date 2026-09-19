# CRT + Divergence + S/R Confluence Indicator

TradingView Pine Script v6 indicator (`CRT-Divergence-SR.pine`) built for the
Defined Risk Trading process: it doesn't call trades on its own, it flags
where three independent signals line up so a discretionary trader can run the
pre-trade checklist against a real setup instead of scanning charts by hand.

## The three ingredients

**1. CRT (Candle Range Theory) — a 3-candle sequence**
- **Range candle**: sets a high/low.
- **Manipulation candle**: wicks beyond the range (sweeps liquidity) and
  closes back inside it — a false breakout / stop hunt.
- **Distribution candle**: confirms the reversal. In "Break of Range" mode
  (default, strict) it must close beyond the range candle's *opposite*
  extreme; in "Close Back Inside Range" mode (fast) it just needs to close
  in the reversal direction.

**Range Timeframe** (default `15`) is independent of whatever chart you're
looking at. Set it once to the timeframe you actually trade CRT on, and the
same formations, labels, and BUY/SELL signals show up whether you're viewing
the 15min chart itself or a 1min execution chart — you don't need to flip
timeframes to see if a setup is forming. This only works when the chart
timeframe is **at or below** the Range Timeframe (e.g. viewing 1min or 5min
while Range Timeframe is 15 is fine; viewing 30min or higher is not — the
status panel's Chart TF cell turns orange with a ⚠ if you're on an invalid
combination). Leave it blank to build CRT from the chart's own candles
instead.

**2. Support & Resistance — pivot-based, self-maintaining**
Tracks swing high/low pivots as horizontal levels, each valid until price
closes (or wicks, depending on **Break Invalidation**) through it. A CRT
sweep only counts as "at a level" if it comes within **Proximity Zone**
(a multiple of ATR) of a still-valid level.

**3. Divergence — regular RSI divergence at swing pivots**
Compares consecutive swing lows (bullish) or swing highs (bearish) on price
against RSI at the same pivots. A divergence stays "active" for
**Divergence Validity Window** bars, so it can still count toward a
confluence signal even if it formed a few bars before the CRT confirmation.

## The signal

A **BUY** confluence label + triangle fires when: a bullish CRT sequence
confirms, the sweep occurred at/through a tracked support level, and a
bullish RSI divergence is still active. **SELL** is the mirror at
resistance. Either `requireSR` or `requireDiv` can be turned off in the
Confluence Rules group to loosen the filter (e.g. CRT + S/R only, no
divergence requirement) — useful while backtesting which combination fits a
given instrument/session.

Unfiltered CRT patterns that don't reach full confluence still get a plain
"CRT" label so you can see what the filters excluded.

A status panel in the top-right corner (toggle with **Show Status Panel**)
always shows the current Range Timeframe, your chart's timeframe (flagged
if it's set higher than the Range Timeframe, which breaks the multi-timeframe
fetch), and the last BUY/SELL signal — so you can tell the indicator is
tracking correctly even when scrolled away from the actual formation.

## Alerts

Four alert conditions are exposed: full bullish/bearish confluence, and
raw (unfiltered) bullish/bearish CRT patterns — set alerts on whichever
fits your workflow.

## Suggested starting point for ES futures

- Range Timeframe: `15` (matches the 15min CRT / 1min entry workflow).
- Chart timeframe while scanning or executing: 1min, or 5min — anything at
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
