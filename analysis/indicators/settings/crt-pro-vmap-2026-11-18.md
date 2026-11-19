# CRT Pro VMap settings, reactivated 11/18/2026 evening (Tim's screenshot)
Score VMap rows from 11/19 on with THESE settings; never mix with rows from before 11/18.

Reference candle: Lookback 2 (was default 3), Min Range 0.75x ATR, ATR 14.
Filters: EMA trend filter ON (20), Volume Confirmation OFF (MA 20, 1.5x), Session filter ON:
  UPDATED 11/18 later: full 1000-1600 ET, no gap (Tim). Lookback stays 2.
  (Screenshot showed Morning 1000-1200, Afternoon 1400-1600.)
Style: line ext 10, show EMA, reference zone, raw CRT signals (small gray) ON.
Volume map: mode Developing, developing start Asia open; fixed London 03:00-09:29 and NY 09:30-15:59 ON;
  profile source 1m intrabar; row 1 pt; shelf >= 60% of POC vol; thin <= 25%; ignore zones < 2 pts;
  POC/shelf tolerance 0.5 pt; max boxes 15; max rows 800; POC line, shelves, thin zones, labels, table ON; POC path OFF.
Asia map (display only): ON, 19:00-02:59 ET, Asia shelves ON.
Test entries: Setup A ON (CRT confirmed by map): sweep wick through thin zone or POC qualifies; wick past shelf edge
  closing back qualifies; skip entries mid-shelf (central 50%); skip when POC too close ahead (min room 3.5 pts).
  Setup B ON (POC reaction): touch distance 1 pt; only inside session windows.
  No new entries after 1530 ET; close open trades at 1600 ET; CRT Pro EMA / opposite-signal exits ON.
Stop/targets: Hard Stop 4 pts from entry (matches Tim's 3.5-4 rule). TP1 at POC: exit 1 pt before it.
  Final target: 1 pt before session high/low; else 3R if no untaken level.
Trade log: Send trade log alerts ON, Webhook Key blank.
