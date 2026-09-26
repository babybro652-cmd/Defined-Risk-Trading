# CRT Setups → Google Sheet

Records every setup and trade from the **CRT Setups** TradingView indicator (`pine/crt-setups.pine`) in a Google Sheet using webhook alerts and Google Apps Script (`crt-setups-tracker.gs`). The sheet fills in as you trade, so the weekly review is ready without copying anything from the chart.

(The older Liquidity Sweep tracker is in `archive/`.)

## 1. Attach the script to the sheet

1. Open the **CRT Setups Tracker** Google Sheet (or create a new blank one).
2. Open **Extensions → Apps Script**, delete the sample code and paste in all of `crt-setups-tracker.gs`.
3. Change `const SECRET = 'change-me';` to a password of your own.
4. Save. In the function menu choose **setup**, then **Run**. Approve the permissions the first time it asks. This creates the **Summary**, **Trades**, **Setups** and **Log** tabs.
5. Optional: choose **testTrade** and click **Run**. A test trade appears in **Trades** and two rows in **Setups**. Delete those rows afterwards (and the matching rows in **Log**).

## 2. Deploy it as a web app

1. **Deploy → New deployment**. Click the gear and choose **Web app**.
2. Set **Execute as** to **Me** and **Who has access** to **Anyone**.
3. Click **Deploy** and copy the **Web app URL** (it ends in `/exec`).
4. Paste the URL into a browser. It should show `CRT Setups tracker is live`.

If you edit the script later, use **Deploy → Manage deployments → Edit → Version: New version** so the URL stays the same.

## 3. Set up the TradingView alert

1. On the **1m chart**, open the **CRT Setups** settings. Under **Alerts / Webhook**:
   - Set **Alert Format** to `JSON (webhook)`.
   - Set **Webhook Key** to the same password as `SECRET`.
2. Create an alert:
   - **Condition:** `CRT Setups` → **Any alert() function call**
   - **Expiration:** open-ended, or as long as your plan allows
   - **Notifications:** tick **Webhook URL** and paste the `/exec` URL
3. Click **Create**.

Webhook alerts need a paid TradingView plan (Essential or higher) and 2-factor authentication turned on.

An alert keeps using the script and settings it was created with. **After you change the script or its settings, delete the alert and create it again.**

With JSON format, TradingView's own pop-ups and app notifications show the raw JSON text. If you also want readable phone notifications, add the indicator to the chart a second time with **Alert Format** set to `Text` and create a second alert from that copy (without the webhook).

## What gets recorded

| Alert | When | Sheet |
|---|---|---|
| `SETUP` | A setup is armed, a level sweep is waiting for C3, or a sweep is confirmed | New row in **Setups** |
| `MISSED` | An armed setup's window ended with no 1m retest or clean break | New row in **Setups** |
| `ENTRY` | The 1m trigger fired | New row in **Trades** |
| `STOP` | The stop moved (breakeven, 15m trail, profit floor) | Updates **Last Stop** |
| `EXIT` | SL, BE, TRAIL, REVERSE or NO-TRADE TIME | Adds exit time, price, reason, P&L $, best open $ and Win/Loss/Breakeven |

Every alert is also copied to **Log** as it arrived.

**Trades** columns: Trade ID, Week Of (Monday), Date, Entry Time, Session (London / NY AM), Side, Setup (CRT / SWEEP), Level (e.g. `London`, `1H+Asia`, `NY low`), Counter-Trend, Trigger (retest / break), Entry, Stop, TP1, Last Stop, Exit Time, Exit Price, Exit Reason, P&L $, Best Open $ (the most the trade was up), Result, Contracts.

**Summary** shows closed trades, wins, losses, win rate, net P&L, average win and loss, profit factor, largest win and loss, average best open profit, setups alerted and missed, plus tables **by week**, **by setup type**, **by level**, **by session** and **by exit reason**.

P&L is calculated from the indicator's own entry and exit prices for the number of contracts in the settings. It does not include commission or slippage.
