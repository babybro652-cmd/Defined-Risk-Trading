# Liquidity Sweep → Google Sheet

Records every trade from the **Liquidity Sweep** TradingView indicator (`pine/liquidity-sweep.pine`) in a Google Sheet using a webhook alert and Google Apps Script (`crt-webhook.gs`).

## 1. Create the sheet and script

1. Create a new Google Sheet (for example "CRT Trade Tracker").
2. Open **Extensions → Apps Script**, delete the sample code and paste in all of `crt-webhook.gs`.
3. Change `const SECRET = 'change-me';` to a password of your own.
4. Save. In the function menu choose **setup**, then **Run**. Approve the permissions the first time it asks. This creates the **Trades**, **Log** and **Summary** sheets.
5. Optional: choose **testTrade** and click **Run**. A test trade should appear in **Trades**. Delete that row afterwards.

## 2. Deploy it as a web app

1. **Deploy → New deployment**. Click the gear and choose **Web app**.
2. Set **Execute as** to **Me** and **Who has access** to **Anyone**.
3. Click **Deploy** and copy the **Web app URL** (it ends in `/exec`).
4. Paste the URL into a browser. It should show `CRT webhook is live`.

If you edit the script later, use **Deploy → Manage deployments → Edit → Version: New version** so the URL stays the same.

## 3. Set up the TradingView alert

1. On your chart, open the **Liquidity Sweep** settings. Under **Alerts / Webhook**:
   - Set **Alert Format** to `JSON (webhook)`.
   - Set **Webhook Key** to the same password as `SECRET`.
2. Create an alert:
   - **Condition:** `Liquidity Sweep` → **Any alert() function call**
   - **Expiration:** open-ended, or as long as your plan allows
   - **Notifications:** tick **Webhook URL** and paste the `/exec` URL
3. Click **Create**.

Webhook alerts need a paid TradingView plan and 2-factor authentication turned on.

An alert keeps using the script and settings it was created with. **After you change the script or its settings, delete the alert and create it again.**

## What gets recorded

| Alert | When | Sheet |
|---|---|---|
| `SETUP` | A pool is swept and the retest limit order is placed | **Log** only |
| `ENTRY` | The limit order fills | New row in **Trades** |
| `TP1` / `TP2` | A partial target is hit | Sets TP1 Hit / TP2 Hit = Yes |
| `EXIT` | SL, BE, or the final target (TP2 or TP3) | Adds exit price, reason, P&L $ and R |
| `MISSED` | The limit order expired without filling | **Log** only |
| `SKIP` | A sweep was skipped (risk over your max) | **Log** only |

**Summary** shows closed trades, win rate, net P&L, average win and loss, average R, TP1 and TP2 hit rates, how trades exited, how many setups were placed and missed, and a **by-pool table** (trades, net P&L and average R for each swept pool: PDH, Asia L, EQH, 4H H, ...).

**Upgrading from an earlier version of the script:** the Trades columns changed when TP3 was added. Delete the old **Trades** and **Summary** tabs (or start a new sheet), paste in the new script, run **setup** again, and deploy a new version.

P&L is calculated from the indicator's levels (stop and target prices) for the number of contracts in the settings. It does not include commission or slippage.
