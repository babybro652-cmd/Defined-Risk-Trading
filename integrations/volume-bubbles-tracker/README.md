# Volume Bubbles Tracker (Google Sheet)

Logs every Volume Bubbles ES alert (`pine/volume-bubbles-es.pine`) into its own sheet, **Volume Bubbles
Tracker**, so the "Vol" / "Vol hold" tags can be tested as a filter for the one final indicator (see "End
goal" in `.claude/agents/drt.md`). It is separate from the CRT Pro and Forward Test trackers; those scripts
are untouched.

- Sheet: https://docs.google.com/spreadsheets/d/1YHKqEq8lbUV4Ubm7dKDieI5fPB7aZQdlzC3GPVJx9Ec/edit
  (Drive folder "DRT Indicator Tracking (fix later)")
- Phone copy of the code: Drive "2 - Apps Scripts (sheet trackers)" / `Volume Bubbles Tracker - Code.gs.txt`
  https://drive.google.com/file/d/1YlouEQ1I7FtuCkrzKat5w5Jj3PxzJZlT/view
- Payload format: `pine/README.md`, "Alerts". The Pine needed no change.

## Tabs

**Bubbles Log**, one row per event:

| Columns | From |
|---|---|
| Date ET, Time ET | `time` (the event bar, already ET, stored as text) |
| Type | `bubble`, `vol_hold` or `pivot_vol` |
| Side | `up`/`down`/`flat` (bubble), `bull`/`bear` (Vol hold, pivot) |
| Price, Volume, zScore, RVOL | as sent |
| Near HVN, Held, FVG, IFVG | TRUE / FALSE; blank when the alert sends `null` (bubbles) |
| Symbol, TF, Confirm Time ET | as sent; Confirm Time = the bar the alert fired on |
| Received | when the sheet got it |
| MFE 30m (pts), MAE 30m (pts), Held Level 30m, Outcome Notes | **blank** (yellow). Filled later by the analysis scripts in `analysis/indicators` from 1m ES bars. Tim never fills these. |
| Raw JSON | the full alert body |

**Log**: one line per post: `OK`, `DUPLICATE`, `NOT JSON`, `OTHER SOURCE`, `BAD KEY` or `ERROR`.

- Duplicates (same type + time + price within the last 50 rows) are skipped and only noted in Log.
- Posts whose `source` isn't `volume-bubbles-es` go to Log only (protects the sheet if a URL gets mixed up).
- `SECRET` is `""`. The indicator has no Webhook Key input, so no password is used.

Outcome definitions for the analysis scripts (measured from `Price`, the tagged level):
MFE / MAE = best and worst move in points in the event's direction within 30 1m bars after `Confirm Time`
(bull/up = up is favorable; bear/down = down is favorable; `flat` bubbles are scored both ways in notes).
Held Level 30m = TRUE if price did not trade more than 1 tick through `Price` in those 30 bars.

## Setup (Tim)

1. Open the **Volume Bubbles Tracker** sheet > Extensions > Apps Script. Delete what's there, paste all of
   `Code.gs` (Raw view on GitHub, or the Drive .txt on the phone), Save.
2. Function dropdown > **addTestBubble** > Run > approve permissions. A TEST row lands in Bubbles Log. Delete it.
3. Deploy > New deployment > type **Web app** > Execute as **Me** > Who has access **Anyone** > Deploy. Copy the
   URL ending in `/exec`. Open it in a browser: it says `ok`.
4. TradingView, **ES1! 1 minute**, Volume Bubbles ES on the chart with the settings you want (alerts keep the
   settings they were made with): Create Alert > Condition **Volume Bubbles ES** > **Any alert() function call**
   > **Once Per Bar Close** > Expiration **Open-ended** > Notifications: tick **Webhook URL**, paste the `/exec`
   URL > Name **LOG Vol Bubbles** > Create. Only one such alert.
5. After the next bubble in NY hours, check Bubbles Log for a row. Nothing? Look at the Log tab and Apps Script >
   Executions. `NOT JSON` means the alert used a named condition instead of "Any alert() function call".

To change the code later: paste the new version, Save, then Deploy > Manage deployments > pencil > Version
**New version** > Deploy, so the URL stays the same.
