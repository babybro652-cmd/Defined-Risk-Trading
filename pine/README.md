# Pine indicators

| File | What | Status |
|---|---|---|
| `crt-pro-es.pine` | CRT Pro ES, Tim's primary indicator, logs to the CRT Trade Tracker | live |
| `crt-pro-vmap-es.pine` | CRT Pro VMap test version | test |
| `crt-setups.pine` | CRT Setups (tracker dormant since 9/28) | test |
| `volume-bubbles-es.pine` | Volume Bubbles ES (below) | new 11/18, testing before lock-in |
| `archive/` | old versions | |

The Divergence indicator (CRT-Divergence-SR.pine) lives only in Tim's TradingView, not in this repo.

## Volume Bubbles ES (`volume-bubbles-es.pine`)

Standalone overlay for **1m ES** on the **Essential plan**, desktop and phone. It's a volume proxy for the
"absorption bubbles" in the Profit Pro clip (11/18). Background research:
`analysis/indicators/order-flow-absorption-options-2026-11-18.md`.

### What it shows

- **Bubbles**: circles with the bar's volume (e.g. `8.3K`) on candles with unusual volume. A candle needs both:
  - a robust z-score of 4+ against the last 60 bars
  - 2x+ the normal volume for that minute of the day (5-day average)

  That keeps the 9:30 open and the 3:50-4:00 close from bubbling every bar. The bubble sits on the candle's
  bigger wick, or at the close if the candle has almost no wicks. Green = up candle, red = down candle. A
  bigger circle means a bigger z-score.
- **HVN zones**: shaded boxes over the busiest price rows of a volume profile the script builds itself (default:
  the CME session from 6 PM ET, 1 pt rows, rows at 60%+ of the POC row, top 3 zones). A dotted line marks the POC.
  Zones are drawn on the last bar only, to keep it light on the phone.
- **Vol hold** (green tag under a low / red tag over a high): a bubble within 1.5 pts of an HVN zone where:
  - the candle closed in the top 40% (bull) or bottom 40% (bear)
  - the wick is at least 30% of the bar
  - the bar isn't a news-size candle (over 2.5 ATR)
  - the wick isn't broken for the next 3 bars

  The tag prints once those 3 bars confirm it.
- **Pivot volume tag** (small blue `Vol 3.1` / `Vol 3.1 held`): at each swing pivot with length 5 (same as the Div
  labels), it shows whether the pivot bar or a bar next to it had big volume (z 2+ and 1.5x normal for that minute).
  `held` = the pivot candle closed off its low (or high). The tag prints 5 bars after the pivot, the same bar the
  Div label appears on. So a Div label with a blue tag under it has volume behind it, and one without a tag doesn't.

### How often (tested on Yahoo ES 1m, 11/13-11/18, with a Python copy of the same rules)

- **Bubbles**: 1-9 per NY session, 19 in 4 sessions. They come in clusters during fast moves.
- **Near an HVN**: only 2-3 of those 19 bubbles. Vol hold fired about once in 4 days. It's rare by design. To see
  more of them, lower the HVN threshold, widen "Near zone", or switch the profile to Rolling.
- **Pivot tags**: about 1 pivot in 8 in NY hours gets one, about 4-5 a day.
- The first 2 days on the chart show no bubbles, because the minute-of-day average needs 2 earlier days. Essential
  loads about 7 days of 1m bars, so that's covered.

### Add it in TradingView

1. Copy the code. On the phone, open `volume-bubbles-es.txt` in the Drive folder "1 - TradingView indicators
   (Pine)". On the desktop, use the Raw view of this file on GitHub.
2. On desktop TradingView, open Pine Editor, then Open, then New indicator. Select all, paste, Save as "Volume
   Bubbles ES", then Add to chart. On the phone app, add it from Indicators, then My scripts, after saving it once
   on desktop or web.
3. Chart: ES1! on 1 minute.
4. Essential allows 5 indicators per chart. If the chart is full, take one off or use a second chart layout.

### Settings (defaults)

| Group | Setting | Default |
|---|---|---|
| 1. Bubbles | Recent bars for z-score / Min z-score | 60 / 4.0 |
| | Min x normal volume for this minute / Days in average | 2.0 / 5 |
| | NY session only / NY session | on / 0930-1600 ET |
| 2. HVN zones | Profile | Session (6 PM ET); also NY session (9:30) or Rolling 390 bars |
| | Row size / HVN threshold / Max zones / Near zone | 1.0 pt / 60% of POC / 3 / 1.5 pts |
| 3. Vol hold | Close location / Min wick / Hold for bars / Max range | 0.6 / 30% / 3 / 2.5 ATR |
| 4. Pivot volume | Pivot length / Bars either side / Min z / Min x normal | 5 / 1 / 2.0 / 1.5 |
| 5. Alerts | Bubble / Vol hold / Pivot volume alerts | all on |

Fewer bubbles: raise Min z-score (5) or Min x normal (2.5). More: lower them.

### Alerts (ready for a tracker, not wired yet)

The script fires one `alert()` per event, once per bar close. When the tracker is built:

1. Create ONE alert: condition "Volume Bubbles ES", then "Any alert() function call".
2. Add the webhook URL.

Alerts keep the settings they were made with, so change settings first and then create the alert. No webhook URL
is in the script. Example payload:

```json
{"source":"volume-bubbles-es","symbol":"ES1!","tf":"1","type":"vol_hold","time":"2026-11-18T10:42","confirmTime":"2026-11-18T10:45","tz":"ET","price":7372.25,"volume":13617,"zScore":4.6,"rvol":3.3,"nearHVN":true,"held":true,"side":"bull"}
```

| Field | Values |
|---|---|
| `type` | `bubble`, `vol_hold` or `pivot_vol` |
| `time` | the event bar, in ET |
| `confirmTime` | the bar the alert fired on: same bar for a bubble, +3 bars for Vol hold, +5 for a pivot |
| `side` | `up` / `down` / `flat` for bubbles; `bull` / `bear` for Vol hold and pivots |
| `held` | `null` on bubbles |

All times are ET. The Forward Test Log uses Central, so subtract 1 hour when matching rows.

### What it can and can't see

It sees one total volume number per 1m bar, plus price. It can't see:

- **Bid vs ask.** It doesn't know who was aggressive. A bubble means "a lot traded on this candle", not "sellers hit
  the bid".
- **Where inside the candle the volume traded.** The clip's 481 sits on one price; here the whole bar's volume goes
  to the wick or the close.
- **Resting limit orders (DOM).** True absorption is passive orders soaking up aggressive ones while price doesn't
  move. Vol hold is "big volume, the wick held, the close came back", which is often absorption but can also be a
  stop run or a news spike. That's why it's labeled Vol hold and not absorption.

For real bid/ask numbers today, check the same spot on the Tradovate "Bid-Ask Volume" chart (research doc,
path 0).

### CME data note (Tim's screenshot, 11/18)

- **His ES data on TradingView looks real-time.** The ES1! screenshot at 1:45 PM ET had no "D" (delayed) badge, a
  green "Market open" dot, and exchange time 12:44 PM Chicago matching his phone.
- **Why it's live:** he doesn't pay TradingView for CME data, so the likely source is his Tradovate broker
  connection. TradingView's help page on broker data lists Tradovate as giving real-time CME, CBOT, COMEX and
  NYMEX data when you connect in the Trading Panel. That data access lasts 7 days and renews each time he logs in
  through the Trading Panel. So if he goes a week without connecting Tradovate in TradingView, ES can drop back to
  delayed.
- **If he ever sees a "D" badge on ES1!:** the chart, the bubbles, the tags and the alerts all run about 10
  minutes behind. Volume is still there, just late. Reconnecting Tradovate in the Trading Panel should bring live
  data back.
- **Roll note:** ES1! is the continuous front month. Around the December roll (mid-December), volume moves to the
  March contract and a few days of bubbles can look odd.

### Before lock-in (Tim checks on his chart)

1. It compiles and loads on desktop, and it shows on the phone.
2. Bubble count per NY session feels right (aim: a handful, like the clip). Tell Jarvis to raise or lower Min z.
3. HVN boxes sit where volume really built up. Compare with TradingView's own Session Volume Profile.
4. Check a few Div labels: does the blue pivot tag show up under the ones that worked?
5. Phone: bubbles and tags are readable and don't cover candles too much.

Once Tim says it's locked, build the tracker (sheet + webhook) for the alert payload above.
