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

Runs on the chart's own candles by default. Set **Range Timeframe** to a
higher timeframe (e.g. `240` for 4H, `D` for daily) to detect that range's
CRT sequence while entries are timed on a lower timeframe chart — the same
idea as running HTF bias with an LTF kill-zone entry.

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

A **LONG** confluence label fires when: a bullish CRT sequence confirms, the
sweep occurred at/through a tracked support level, and a bullish RSI
divergence is still active. **SHORT** is the mirror at resistance. Either
`requireSR` or `requireDiv` can be turned off in the Confluence Rules group
to loosen the filter (e.g. CRT + S/R only, no divergence requirement) —
useful while backtesting which combination fits a given instrument/session.

Unfiltered CRT patterns that don't reach full confluence still get a plain
"CRT" label so you can see what the filters excluded.

## Alerts

Four alert conditions are exposed: full bullish/bearish confluence, and
raw (unfiltered) bullish/bearish CRT patterns — set alerts on whichever
fits your workflow.

## Suggested starting point for ES futures

- Chart timeframe: 1–5 min for entries.
- Range Timeframe: blank (chart TF) for kill-zone-scale CRT, or `60`
  for hourly range context.
- Keep both `requireSR` and `requireDiv` on for the highest-conviction
  signals; this will fire less often but each hit has three confirmations
  stacked.
- This indicator does not manage risk. Every signal still goes through the
  full checklist: defined risk before entry, daily/session loss limits, and
  the paper-trading track before size.

## Disclaimer

Educational tool only, not financial advice. Past pattern confluence does
not guarantee future results.
