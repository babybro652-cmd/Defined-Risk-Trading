# CRT Pro Tracker (Google Sheet)

Logs every CRT Pro ES trade (`pine/crt-pro-es.pine`, Tim's primary indicator)
into the **CRT Trade Tracker** Google Sheet, so it can be measured against the
two test indicators (CRT + Divergence, CRT Setups) on the same terms.

## What gets logged

The indicator's "Trade Log (webhook)" section sends one JSON alert per event,
on bar close only:

| Event | When | Sheet |
|---|---|---|
| `ENTRY` | A CRT BUY or CRT SELL label prints and no trade is open | New row in **CRT Pro Trades** (status OPEN) with Entry, SL, TP1, TP2, TP3 |
| `TP` | Price reaches TP1, TP2 or TP3 | **TP Reached** goes to 1, 2 or 3 |
| `EXIT` | The first of: SL touched (`SL`), TP3 reached (`TP3`), an opposite CRT signal (`REVERSE`), or a close on the wrong side of the EMA with an opposite-colour candle (`EMA`) | Fills exit time, price, reason, P&L and Result on that trade's row |

- **Entry** = close of the signal bar.
- **SL** = the signal candle's sweep wick (low for longs, high for shorts),
  plus the **SL Buffer** ticks from the indicator settings (0 by default).
- **TP1 / TP2 / TP3** = 1R / 2R / 3R from entry, where R = entry to SL. The
  multiples are editable under "Entry / SL / Targets" in the indicator settings.
- SL and TPs are checked from the bar after entry, using each bar's high and
  low. If one bar touches both the SL and a TP, the SL counts first (the
  conservative read). SL exits log at the SL price, TP3 exits at TP3, EMA and
  REVERSE exits at the bar's close.
- The chart draws the Entry (white), SL (red) and TP (green dashed) lines for
  each trade, running until the trade closes, with a small TP1/TP2/TP3 or SL
  tag where each was hit.
- **R** = P&L points ÷ risk points. **P&L $** is at **2 ES contracts** ($100
  per point), no commissions.
- Times are **Eastern**. Sessions: Asia (7 PM–2:59 AM), London (3–9:29 AM),
  NY open (9:30–10), NY 10-12, NY afternoon (12–4 PM), After hours.
- A repeated signal in the same direction while a trade is open is ignored.
- Duplicates (two alerts pointed at the sheet) are ignored: a second ENTRY
  with the same trade ID, a repeated TP, or a second EXIT for a closed trade
  only shows up in **CRT Pro Log** marked "(duplicate)".
- **CRT Pro Summary** adds how often trades reach TP1, TP2 and TP3, and how
  many closed at SL, TP3, EMA and opposite signal.

## Setup

1. **Indicator:** replace the CRT Pro script in TradingView's Pine Editor with
   `pine/crt-pro-es.pine` (use the **Raw** view on GitHub to copy it) and save.
   The signals and the original drawings are unchanged; the "Entry / SL /
   Targets" and "Trade Log" inputs and the code at the bottom are new. Leave **Send trade log alerts** on.
2. **Sheet script:** open the CRT Trade Tracker sheet → Extensions → Apps
   Script. Replace everything with `Code.gs` from this folder and save.
3. Pick **setup** in the function dropdown → Run (approve permissions). It
   adds the **CRT Pro Trades**, **CRT Pro Summary** and **CRT Pro Log** tabs.
   The sheet's older tabs are left alone; delete them if you like.
4. **Deploy:** Deploy → New deployment → Web app. Execute as **Me**, access
   **Anyone**. Copy the `/exec` URL. (If the sheet already has a deployment,
   use Manage deployments → edit → New version instead so the URL is kept.)
5. **Alert:** on the chart you trade CRT Pro on → Create Alert → Condition:
   **CRT Pro — ES Futures** → **Any alert() function call** → Once per bar
   close → Notifications: Webhook URL = the `/exec` URL → Create.
   Create exactly **one** such alert.

Optional: **addTestTrade** in the function dropdown adds a sample trade so you
can see the layout; delete its row afterwards.

## Troubleshooting

- **Nothing arrives:** check the alert's History in TradingView and the Apps
  Script Executions log. Webhooks need a paid TradingView plan and 2FA.
- **"NOT JSON" in the log:** an alert on this sheet is using a named condition
  (e.g. "CRT Buy Signal") instead of "Any alert() function call". Delete it.
- **"(duplicate)" rows in the log:** more than one alert points at the sheet.
  Harmless, but delete the extras.
- **"no matching entry":** an EXIT arrived for a trade whose ENTRY was never
  logged (e.g. the alert was created while a trade was already open).
