# Webhook auto-logging for the forward-test sheet

Wires the indicator's `alert()` calls straight into the "CRT Forward Test
Log" Google Sheet, so BUY/SELL/CRT/Divergence signals and TP/SL hits get
logged automatically instead of by hand.

## How it works

`CRT-Divergence-SR.pine` fires `alert()` with a JSON payload at every
signal point (BUY, SELL, CRT Bull/Bear unfiltered, Bull/Bear Div, and
SL/TP1/TP2/TP3 hits). One TradingView alert, set to fire on *any* of
these, POSTs that JSON to a webhook URL. `Code.gs` is a small Google Apps
Script bound to the sheet that receives that POST and either appends a
new row (a signal) or updates the Result cell of the currently open trade
(a TP/SL hit).

## Setup

**1. Attach the script to the sheet**

- Open the [CRT Forward Test Log](https://docs.google.com/spreadsheets/d/1H9KSzv9C0hIhDuWjUCQKpKURv_kEkRE5CLlLV-kmofA/edit) sheet.
- Extensions -> Apps Script. This opens a blank script project already bound to this spreadsheet.
- Delete the default `myFunction() {}` stub and paste in the contents of `Code.gs` from this folder.
- Save the project (any name is fine, e.g. "CRT Webhook").

**2. (Optional) Set a shared secret**

Skip this if you're fine with anyone who has the URL being able to post rows - low
stakes for a personal trade log, but easy to lock down if you want to:

- In the Apps Script editor: Project Settings (gear icon) -> Script Properties -> Add script property.
- Name: `WEBHOOK_SECRET`, value: any string you make up.
- You'd then need to add `"secret":"<same value>"` into the Pine alert
  payloads too - ask if you want this wired in; it's not in the script by
  default so it works with zero extra setup.

**3. Deploy as a Web App**

- Deploy -> New deployment.
- Select type: Web app.
- Execute as: **Me**.
- Who has access: **Anyone**.
- Deploy, authorize the permissions prompt (it's your own script touching
  your own sheet), then copy the `/exec` URL it gives you. Keep this URL
  private - treat it like a password, since anyone with it can post rows
  into your sheet.

**4. Create the TradingView alert**

- On a chart with `CRT-Divergence-SR` applied, tap the alarm-clock icon -> Create Alert.
- Condition: pick the indicator, then choose **"Any alert() function call"** (not one of the named conditions - this one fires for every `alert()` in the script, so a single alert covers BUY, SELL, CRT, Div, and TP/SL hits).
- Trigger: Once Per Bar Close.
- Under Notifications, enable **Webhook URL** and paste the `/exec` URL from step 3.
- Expiration: set to open-ended if your plan allows it, otherwise the longest option - the alert stops firing once it expires.
- Create.

That's it - one alert, no need to set up the 10 separate ones from before. From here every BUY, SELL, CRT Bull/Bear (unfiltered), Bull Div, Bear Div, and every SL/TP1/TP2/TP3 hit lands in the sheet on its own.

## What still needs manual entry

- **Furthest Adverse Price** (column H) on CRT/Div rows - this is inherently a hindsight number (the worst price reached *after* the signal, before it turned), so there's no way to know it at the moment the signal fires. Fill it in once you can see what happened, same as before. Only check price up to the **Div Valid Until** timestamp (column S, Bull/Bear Div rows only) - that's the same window the indicator itself uses to still count the divergence as "recent" for confluence, so it's the natural cutoff for what counts as this signal's drawdown. If price hasn't made a new adverse extreme by then, log 0 ticks; anything the market does after that point belongs to a different move, not this signal.
- **Notes** (column R) - free text, not something a webhook has anything meaningful to say.

Everything else - Date, Time, Instrument, Signal Type, Direction, Entry/SL/TP1-3, Signal Ref Price, Div Valid Until, and the Result as the trade progresses (TP1 HIT -> TP2 HIT -> ... -> STOPPED/STOPPED (BE)/STOPPED (TRAIL)) - now fills itself in.

## Troubleshooting

- **Nothing showing up**: check the Apps Script project's Executions log (left sidebar, clock icon) - it records every `doPost` call and any errors. Also confirm the TradingView alert actually fired (Alerts panel -> tap the alert -> History).
- **A row appears with blank Entry/SL/TP**: that's expected for CRT/Div signals - only BUY/SELL rows carry those.
- **Result never updates**: `updateLastOpenTrade` targets the most recent row where Signal Type is BUY or SELL. If you've manually added or reordered rows in a way that puts a non-trade row after the real trade row, it'll update the wrong one (or none). Keep manual edits to existing rows, not reordering.
