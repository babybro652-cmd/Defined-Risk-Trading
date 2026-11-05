# DRT Phone videos, Thu 11/5/2026: ES longs, 2-part breakeven series (TRADE POST, DRAFT, needs Tim's go)

## CURRENT BUILD (Tim ~11:50 AM: "I think I gave you the wrong videos. Upload 2 new ones to drt.")
New uploads in Drive "DRT Phone" (created 16:50 UTC):
- V1 `Screen_Recording_20261105_110059_TradingView.mp4` (11M5MfoHF9KPWeHVggMSSNhWVZrLoEwgT, 25 MB, 4:49.5, ~16 fps), 10:56:10-11:00:59 ET. NEW.
- V2 `Screen_Recording_20261105_111010_TradingView.mp4` (1biHbRIrDb-FnYRYf2UKIruf_LVFG19AP), byte-identical (sha256) to the first
  upload's V2 (1pdagl6atV6IkOBr9R4QcFSUu1SGVoIZE). Same trade as before.
- Tim's 1m screenshot of all three fills (chat upload 1ee697f6-image.jpg) used as a still for the middle trade, which is in neither video.
Framing (Tim via Jarvis): Part 1 = instead of a breakeven stop he protected the trade by getting out in profit; must mention the
next trade lost from an IMPATIENT re-entry. Part 2 = same setup came back, proper entry, target hit. Tim confirmed all LONG.

### Trade facts (frames + screenshot), all 2 ES (screen shows TradingView Paper Trading; tag off until Tim confirms)
| # | Source | Entry | Stop | Target | Exit | Result | Exit type |
|---|---|---|---|---|---|---|---|
| 1 | V1 (Part 1) | long 7,448.25 (10:55 bar) | 7,444.50 (3.75 pts), dragged 1 tick wider to 7,444.25 (4.00) at 21.6-30.6 s | 7,497.75 (+$4,950) | 7,457.25 ~11:00:54 | +9.00 pts, +$900 | MANUAL: tap on the position's close X at ~285 s; price had run to ~7,477 and was rolling over |
| 2 | screenshot only | long 7,452.00 (~11:01) | 7,448.00 (4 pts) | 7,478.75 | 7,445.75 ~11:04:51 | -6.25 pts, -$625 | stop, filled 2.25 pts past it (from the first-upload recording) |
| 3 | V2 (Part 2) | long 7,442.75 (11:06 bar) | 7,438.75 (4 pts), never moved | 7,471.25 | 7,471.25 ~11:10:06 | +28.50 pts, +$2,850, 7.1R | TARGET |
Day +$3,125 gross. Private notes: 3 trades (rule 1-2), $1,200 risk taken across the 3 (rule max $1,000), all inside work hours (not the
~10 AM lunch), so no time of day or lunch line anywhere. Stop on trade 1 moved one tick wider, never toward breakeven (captions say
only "never to breakeven" for Part 1; "stop never moved" is used for Part 2 only).

### Privacy scan
V1: 10 fps scan of every frame + 1 fps sheets: no notifications, names, home screen or legend (collapsed "v 4"). Cut 21.6-30.8 s
(stop-order menu "Sell 2 @7,444.50 Stop / Modify / Cancel" while dragging). Status bar shows 82.6-84.9 s (clock 10:57): cropped. V2 cuts as
before. Screenshot: status bar (11:56 clock, app icons) cropped, time axis/toolbar/tab/nav covered; the "TP 1" line stays (Tim OK).
Output scan of every frame of all builds: only end-card frames flag (expected).

### Media (`make_trade_reel_1105.py V1 V2 OUT --mode part1|part2|combined|breakdown --still SHOT`), AUDIO QA: PASS on all 7, sha256 match
| File | Length | Music (CC0) | Blotato URL |
|---|---|---|---|
| es-1105-part1.mp4 (DRT) | 43.0 s | im_glad_you_are_here | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/7ff9beff-7e15-459c-bacf-668a6beb04b8.mp4 |
| es-1105-part2.mp4 (DRT) | 42.0 s | one_cool_minute | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/778de853-fd2a-437b-b557-fd6dd1f2a88d.mp4 |
| es-1105-part1-personal.mp4 | 43.0 s | drowning_in_your_smile | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/d8f74ccd-13f5-46ac-9791-d73776632562.mp4 |
| es-1105-part2-personal.mp4 | 42.0 s | static_shoes | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/42fe8d80-8332-40d7-9010-49a2b8ac642a.mp4 |
| es-1105-combined.mp4 (DRT option, incl. 3 s screenshot) | 58.3 s | one_cool_minute | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/538c560d-b597-4baf-b158-5cae6a2d584f.mp4 |
| es-1105-combined-personal.mp4 | 58.3 s | static_shoes | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/ffba2673-06fa-43db-8d9c-79ee374323f6.mp4 |
| es-1105-breakdown-base.mp4 (no music, no card, incl. screenshot) | 85.1 s | silent | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/593446ad-1d7a-42f3-9ae7-b42c38e44d0a.mp4 |
| es-1105-breakdown-music.mp4 | 85.1 s | im_glad_you_are_here, -29.9 LUFS | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/9b89e083-4c4d-4d29-8191-86a59a83533c.mp4 |
End cards: Part 1 = facts + "I protect a trade by getting out." + "Next trade: an impatient re-entry, -$625."; Part 2 = facts +
"Before it: an impatient re-entry, -$625. Waiting for the proper entry paid."; combined = all three + "Patience paid. Impatience cost."
No day total on cards (open question). Sheets read: es-1105-*-sheet-2fps.png, es-1105-keyframes.png, audio sheets.

### Captions (5-gram OK vs each other and 71 caption blocks 10/28-11/5; no em dashes, filler, AMD/CRT, time of day, lunch)
#### Part 1
TikTok DRT (58063), 139 chars, isAiGenerated false
```
Part 1: no breakeven stop. I protect a trade by getting out. Long 2 ES at 7,448.25, sold at 7,457.25 for +$900. Next trade I got impatient.

#definedrisktrading #esfutures #daytrading #riskmanagement #stoploss
```
Instagram (68887, reel)
```
Part 1: Why I don't move my stop to breakeven.

A follower asked why I leave my stop where it is once a trade moves my way. A breakeven stop feels safe, but it isn't free. Every round trip is charged commissions and fees, so getting taken out at your entry still costs money.

I protect a trade a different way. When price stops doing what I need, I get out.

The trade: long 2 ES at 7,448.25, stop 7,444.25, 4 points of risk. Price ran, then started to roll over, so I sold it myself at 7,457.25. +9 points on each contract, +$900.

The next trade is where I slipped. I got impatient on the re-entry and took a -$625 loss. Part 2 shows what happened when I waited for the setup properly.

#MyHobbyismyFREEDOM #definedrisktrading #esfutures #daytrading #riskmanagement
```
Facebook (50185, page 993318963868124)
```
Someone asked me why I don't slide my stop to breakeven once a trade is working. Fair question, so here's Part 1 of my answer.

Breakeven sounds like a free trade. It's not. Commissions and fees come out on the way in and on the way out, so a scratch still shrinks the account.

My protection is the exit. On this ES long I bought 2 contracts at 7,448.25 with a 4 point stop. When the move faded, I closed it myself at 7,457.25 for +$900.

Then I made a mistake: I jumped back in too early and lost $625 on that re-entry. Part 2 covers the patient one.
```
YouTube Short (48727). Title (52 chars): `Breakeven Stop? Why I Take the Exit Instead (Part 1)`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
```
Breakeven exits still pay round-trip commissions and fees. Here I sold an ES long myself for +9 points a contract instead of moving my stop.

Education only. Not financial advice.

#shorts #esfutures #stoploss
```
Personal TikTok (59764), 132 chars
```
Got asked why my stop never goes to breakeven. I'd rather take the exit. +$900 on this one, then I got impatient and gave some back.

#MyHobbyismyFREEDOM #esfutures #trading
```

#### Part 2
TikTok DRT (58063), 130 chars
```
Part 2: my impatient re-entry lost $625. When the setup showed up again I was patient: long 2 ES at 7,442.75, target paid +$2,850.

#definedrisktrading #esfutures #daytrading #futurestrading #tradingdiscipline
```
Instagram (68887, reel)
```
Part 2: Same setup, new entry, target hit.

Quick confession first. After the Part 1 exit I got impatient, bought back in too early at 7,452.00, and took a -$625 loss.

Then the setup I trade showed up again, and this time I waited for it. Long 2 ES at 7,442.75, stop 7,438.75, target 7,471.25.

The stop sat 4 points under my entry the whole way while price climbed. The target filled at 7,471.25: that's +28.50 points for each of my 2 contracts, +$2,850, a 7.1R winner.

Same setup, different behavior, different result. Patience was the edge on this one.

#MyHobbyismyFREEDOM #definedrisktrading #esfutures #daytrading #tradingdiscipline
```
Facebook (50185, page 993318963868124)
```
Part 2 of the breakeven question, and an honest one.

Between the two trades in this series, I re-entered too fast. Long at 7,452.00, out at 7,445.75, -$625. That one was on me, not the setup.

Once the setup formed again, I let my entry come to me: long 2 contracts at 7,442.75, risking 4 points to 7,438.75. I didn't touch it. Price worked up to my target at 7,471.25 and the order filled for +28.50 points a contract, +$2,850.

Losses still happen, and impatience makes them more likely. The risk stays fixed either way.
```
YouTube Short (48727). Title (45 chars): `Same Setup, New Entry: ES Target Hit (Part 2)`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
```
An impatient re-entry cost me first. Then the ES setup returned and I waited for it, kept a fixed 4 point stop and let the target fill for +28.50 points a contract.

Education only. Not financial advice.

#shorts #esfutures #daytrading
```
Personal TikTok (59764), 122 chars
```
Got impatient and lost $625 on a re-entry. Waited for the same setup again, left my stop alone, target filled for +$2,850.

#MyHobbyismyFREEDOM #esfutures #daytrading
```

#### Combined option
TikTok DRT (58063), 128 chars
```
Breakeven stops cost fees, so I take exits instead. +$900, then an impatient re-entry for -$625, then a patient one for +$2,850.

#definedrisktrading #esfutures #daytrading #riskmanagement
```
Instagram (68887, reel)
```
Breakeven stops cost money. Three ES trades show what I do instead, and where I slipped.

Scratching a trade at entry still means paying commissions and fees on the round trip. It's a loss with a nicer name.

Trade 1: bought 2 ES at 7,448.25, 4 point stop. Took my exit at 7,457.25 when the move faded. +$900.
Trade 2: got impatient and re-entered too early at 7,452.00. Out at 7,445.75, -$625.
Trade 3: the setup came back, and I was patient. Bought 2 at 7,442.75, stop 7,438.75. Target filled at 7,471.25, +$2,850, about 7.1R.

The setup didn't change. My patience did.

#MyHobbyismyFREEDOM #definedrisktrading #esfutures #riskmanagement
```
Facebook (50185, page 993318963868124)
```
A viewer wanted to know why my stop stays put instead of going to breakeven. This video answers with three trades from one session.

First, the cost: commissions and fees get charged whether a trade wins, loses or scratches, so breakeven still drains the account.

My first ES long at 7,448.25 faded, so I got out at 7,457.25 for +$900. Then I rushed a re-entry at 7,452.00 and lost $625 at 7,445.75. When the setup returned at 7,442.75, I bought 2 with a 4 point stop and my target at 7,471.25 filled for +$2,850.

The difference between the last two trades was my patience.
```
YouTube Short (48727). Title (49 chars): `Why My Stop Never Moves to Breakeven: 3 ES Trades`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
```
An exit in profit, an impatient re-entry that lost, then the same setup with a patient entry and a filled target. Breakeven exits still pay commissions and fees.

Education only. Not financial advice.

#shorts #esfutures #riskmanagement
```
Personal TikTok (59764), 145 chars
```
Took +$900, got impatient and gave back $625, then let the same setup form again and hit my target for +$2,850. Never moved my stop to breakeven.

#MyHobbyismyFREEDOM #esfutures #futurestrading
```

### Proposed slots (ET), NOT scheduled
Part 1 tonight Thu 11/5: FB 5:00 PM, IG 5:15 PM, DRT TikTok 5:30 PM, personal TikTok 6:15 PM, YouTube 6:45 PM (2nd Short today).
Part 2 Fri 11/6: FB 5:30 PM, IG 5:45 PM, DRT TikTok 6:00 PM, personal TikTok 6:45 PM, YouTube 7:00 PM.
Combined instead: tonight on the Part 1 times. Tim overrides caps for trade posts.

---
## SUPERSEDED (first upload, wrong videos per Tim). Do NOT use these 8 Blotato uploads or captions:
a511e957-6234-4602-b94e-265653502ef0, c934a3a9-5008-47b2-b987-5f0bcb96daa3, 8742eb0f-9e51-486f-8ed5-6af0a5491983,
b335081c-a231-4e15-93b0-d656cecb92f7, 9c0e412a-dbc9-49e6-ae36-e3b58fc08302, 5852e961-12b2-4bda-83e7-f0cd93b3356b,
54ec5f12-ecd1-4924-91d0-64b2e2cea282, 1a207684-ee44-48ed-bb23-6d558d998c10 (local files removed; in git history at 5c81611).
Original notes kept below for the record.

> 
> Tim 11/5 ~11:30 AM: "2 New videos in drt." Framing from Tim (via Jarvis): Part 1 answers a viewer who asked why he never moves
> his stop to breakeven (breakeven still pays commissions/fees, so it's a loss; he protects a trade by getting out, not by moving
> the stop). Part 2: same setup, different entry, target hit. Combined ~60 s version as an option. Skool recap already posted.
> 
> Sources (Drive "DRT Phone", TradingView mobile, ES1! 1m, ESZ2026, 1080x2340, silent audio track -91 dB):
> - V1 `Screen_Recording_20261105_110512_TradingView.mp4` (1Vl7lqN_i9Y82KgsyoJxP9a_tQMo6y098, 15 MB, 2:26.6, 22 fps). Clock 11:02:46-11:05:12 ET.
> - V2 `Screen_Recording_20261105_111010_TradingView.mp4` (1pdagl6atV6IkOBr9R4QcFSUu1SGVoIZE, 24 MB, 3:06.3, ~26 fps). Clock 11:07:04-11:10:10 ET.
> 
> ## Facts (from the frames)
> - V1 (Part 1): LONG 2 ES @ 7,452.00 (fill marker on the 11:01 1m bar, filled before the recording). Stop 7,448.00 (4 pts, -$400),
>   target 7,478.75 (26.75 pts, +$2,675). Price fell through the stop: at 124.75 s the position showed -$450 (7,447.75) with the stop
>   still working; at 125.1 s (~11:04:51 ET) it closed, sell 2 @ 7,445.75. -6.25 pts x 2 = -$625 (2.25 pts / $225 past the stop).
>   Stop line never moved. No touch marker (Show Touches is on) and the stop line stays on the chart until the fill, so it reads as
>   the stop filling late with slippage, not a manual tap. CONFIRM with Tim (he described a manual exit).
> - V2 (Part 2): LONG 2 ES @ 7,442.75 (fill marker on the 11:06 bar, before the recording). Stop 7,438.75 (4 pts, -$400), target
>   7,471.25 (28.50 pts, +$2,850). Stop never moved. Target filled at 182.4 s (~11:10:06 ET): sell 2 @ 7,471.25. +28.50 pts x 2 = +$2,850, 7.1R.
> - The 15m view in V2 (cut) shows the day's aggregated fills: buy 2 @ 7,448.25 on the 10:45 bar, sell 4 @ 7,451.50 and buy 4 @ 7,447.38 on
>   the 11:00 bar. So the earlier screenshot "6 @ 7,458.08 sell / 4 @ 7,447.38 + 2 @ 7,448.25 buy" is three LONGS of 2 ES, not a short of 6:
>   (1) buy 2 @ 7,448.25 (10:45 bar), sell 2 @ 7,457.25 (11:00 bar) = +9.00 pts, +$900 (not in these recordings, stop unknown);
>   (2) V1 -$625; (3) V2 +$2,850. Day = +$3,125 gross. Never more than 2 ES open.
> - Account: V2 95-106 s shows the TradingView "Trading account: Paper Trading" sheet and "Failed to login: Paper Trading is currently
>   unavailable" (cut). So PAPER per the screen; tag left off the cards and captions until Tim confirms.
> - Private notes (not for captions): 3 trades (his rule is 1-2); risk taken 3 x $400 = $1,200 if trade 1 also had a 4 pt stop (over the
>   $1,000 max); all trades ~10:45-11:10 AM ET, inside work hours, not the ~10 AM lunch, so no time of day or lunch line anywhere.
> 
> ## Privacy scan
> 10 fps scan of every frame (status bar, bright sheet, legend, purple edge light) + 1 fps contact sheets of both videos + 4-10 fps sheets of
> every flagged window. No notifications, no names, no home screen, no rotation, indicator legend stays collapsed ("v 4", no names).
> Cut: V1 15.0-18.8 s chart reload without the position lines; V2 61.8-74.9 s interval menu + 15m detour; V2 95.0-106.6 s chart reload +
> Paper Trading account sheet + "Failed to login" dialog. Status bar (clock, recorder, app icons) cropped (top 98 px); everything below
> source y 1788 covered with chart background (time axis, toolbar, tab bar, nav bar, order-ticket bar). Output scan of every frame of
> all 4 builds: only the end-card frames flag (expected), 0 chart frames.
> 
> ## Media (script `posts/media/2026-11-05/phone/make_trade_reel_1105.py --mode part1|part2|combined|breakdown [--account paper|live]`)
> Real speed on the opening fill marker and on each exit (V1 123.6-125.6 s, V2 181.4-183.4 s). Title band burned in over the empty chart
> area ("Part 1 / Why I don't move my stop to breakeven", "Part 2 / Same setup, new entry, target hit"). End cards with the facts.
> Music: all 10 old tracks were used 11/3-11/5, so 4 new CC0 tracks added (drt/audio/music/LICENSES.md). AUDIO QA: PASS on all 7 audio runs.
> All uploads sha256-match the local files.
> | File | Length | Music | Blotato URL |
> |---|---|---|---|
> | es-1105-part1.mp4 (DRT) | 40.0 s | im_glad_you_are_here, -18 LUFS | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/a511e957-6234-4602-b94e-265653502ef0.mp4 |
> | es-1105-part2.mp4 (DRT) | 42.0 s | one_cool_minute, -18 LUFS | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/c934a3a9-5008-47b2-b987-5f0bcb96daa3.mp4 |
> | es-1105-part1-personal.mp4 | 40.0 s | drowning_in_your_smile | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/8742eb0f-9e51-486f-8ed5-6af0a5491983.mp4 |
> | es-1105-part2-personal.mp4 | 42.0 s | static_shoes | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/b335081c-a231-4e15-93b0-d656cecb92f7.mp4 |
> | es-1105-combined.mp4 (DRT, option) | 58.5 s | one_cool_minute | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/9c0e412a-dbc9-49e6-ae36-e3b58fc08302.mp4 |
> | es-1105-combined-personal.mp4 (option) | 58.5 s | static_shoes | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/5852e961-12b2-4bda-83e7-f0cd93b3356b.mp4 |
> | es-1105-breakdown-base.mp4 (breakdown, NO music, no card) | 71.8 s | silent track | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/54ec5f12-ecd1-4924-91d0-64b2e2cea282.mp4 |
> | es-1105-breakdown-music.mp4 (breakdown, low music) | 71.8 s | im_glad_you_are_here, -29.9 LUFS, peak -15.6 dBFS | https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/1a207684-ee44-48ed-bb23-6d558d998c10.mp4 |
> QA sheets read: es-1105-part1/part2/combined/breakdown-sheet-2fps.png and the add_audio sheets. Breakdown: ~15 frames after the V1 exit
> (chart scrolled) were held on the previous frame by the guard (about 0.5 s still).
> 
> ## Captions (5-gram OK vs each other and 71 caption blocks in posts/ 10/28-11/5; no em dashes, filler, AMD/CRT, time of day, lunch)
> Paper/live tag left off. "stop-out" wording (Part 2 card, YouTube) matches the frames; swap if Tim says manual exit.
> 
> ### Part 1
> TikTok DRT (58063), 135 chars before hashtags, isAiGenerated false
> ```
> Part 1: my stop never goes to breakeven. Exiting at entry still costs commissions and fees, so it's a loss. Long 2 ES, closed at -$625.
> 
> #definedrisktrading #esfutures #daytrading #riskmanagement #stoploss
> ```
> Instagram (68887, reel)
> ```
> Part 1: Why I don't move my stop to breakeven.
> 
> A follower asked why I leave my stop alone once a trade moves my way. Moving it to breakeven feels like protection, but it isn't free. Every round trip is charged commissions and fees, which means a "breakeven" exit still takes money out of the account.
> 
> My protection is the exit itself. When a trade isn't working, I get out.
> 
> The trade: long 2 ES at 7,452.00, stop 7,448.00, 4 points of risk. Price rolled over and I was out at 7,445.75. -6.25 points on each contract, -$625.
> 
> Part 2 shows what happened when the same setup came back.
> 
> #MyHobbyismyFREEDOM #definedrisktrading #esfutures #daytrading #riskmanagement
> ```
> Facebook (50185, page 993318963868124)
> ```
> Someone asked me why I don't slide my stop to breakeven once a trade is working. Fair question, so here's Part 1 of my answer.
> 
> Breakeven sounds like a free trade. It's not. Commissions and fees come out on the way in and on the way out, so getting taken out at your entry price still shrinks the account.
> 
> On this ES long I bought 2 contracts at 7,452.00 with a 4 point stop at 7,448.00. It didn't work. Closed at 7,445.75 for -$625.
> 
> I protect a trade by getting out when it stops working, not by moving the stop around. Part 2 is the re-entry on the same setup.
> ```
> YouTube Short (48727). Title (43 chars): `Breakeven Stop? Why Mine Stays Put (Part 1)`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
> ```
> Breakeven exits still pay round-trip commissions and fees, so they cost money. Here's an ES long that didn't work, and why the stop never budged.
> 
> Education only. Not financial advice.
> 
> #shorts #esfutures #stoploss
> ```
> Personal TikTok (59764), 124 chars
> ```
> Got asked why I won't put my stop at breakeven. Fees still hit you on a scratch trade. This one lost me $625. Part 2 coming.
> 
> #MyHobbyismyFREEDOM #esfutures #trading
> ```
> 
> ### Part 2
> TikTok DRT (58063), 138 chars
> ```
> Part 2: the setup came back, so I took it again. Long 2 ES at 7,442.75, 4 pt stop never moved. Target filled, +28.50 pts a contract, 7.1R.
> 
> #definedrisktrading #esfutures #daytrading #futurestrading #tradingdiscipline
> ```
> Instagram (68887, reel)
> ```
> Part 2: Same setup, new entry, target hit.
> 
> After the loss in Part 1, the setup I trade showed up again 9.25 points lower. I took it. Long 2 ES at 7,442.75, stop 7,438.75, target 7,471.25.
> 
> No breakeven stop this time either. It sat 4 points under my entry the whole way while price climbed. The target filled at 7,471.25: that's +28.50 points for each of my 2 contracts, +$2,850, a 7.1R winner.
> 
> One loss doesn't cancel a setup. Keeping the risk the same size every time is what lets you take the next one.
> 
> #MyHobbyismyFREEDOM #definedrisktrading #esfutures #daytrading #tradingdiscipline
> ```
> Facebook (50185, page 993318963868124)
> ```
> Part 2 of the breakeven question.
> 
> Right after that ES loss, the same setup gave me a second entry. I went long 2 contracts at 7,442.75 with the same 4 point stop, 7,438.75.
> 
> I didn't touch it. Price worked up to my target at 7,471.25 and the order filled: +28.50 points a contract, +$2,850, roughly seven times the risk.
> 
> Two trades, one plan, the same risk. One lost and one paid, and neither stop got moved. Losses still happen, which is why the risk stays fixed.
> ```
> YouTube Short (48727). Title (45 chars): `Same Setup, New Entry: ES Target Hit (Part 2)`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
> ```
> Re-entered the same ES setup after a stop-out, kept a fixed 4 point stop, and let the target fill for +28.50 points a contract.
> 
> Education only. Not financial advice.
> 
> #shorts #esfutures #daytrading
> ```
> Personal TikTok (59764), 115 chars
> ```
> Took the same setup again after that loss. Left my stop alone and the target filled, +$2,850. Two trades, one plan.
> 
> #MyHobbyismyFREEDOM #esfutures #daytrading
> ```
> 
> ### Combined option (one post instead of the two parts)
> TikTok DRT (58063), 136 chars
> ```
> Breakeven stops still cost fees, so mine stays put. First ES long lost $625. Same setup came back, new entry, target filled for +$2,850.
> 
> #definedrisktrading #esfutures #daytrading #riskmanagement
> ```
> Instagram (68887, reel)
> ```
> Breakeven stops cost money. Two ES trades show why mine stays put.
> 
> Scratching a trade at entry still means paying commissions and fees on the round trip. It's a loss with a nicer name.
> 
> Trade 1: bought 2 ES at 7,452.00, stop 7,448.00. Didn't work. Out at 7,445.75, -$625.
> Trade 2: the same setup again with a lower entry. Bought 2 at 7,442.75, stop 7,438.75. Target filled at 7,471.25, +$2,850, about 7.1R.
> 
> Same risk both times, and the stop stayed where I put it.
> 
> #MyHobbyismyFREEDOM #definedrisktrading #esfutures #riskmanagement
> ```
> Facebook (50185, page 993318963868124)
> ```
> A viewer wanted to know why my stop stays put instead of going to breakeven. This video answers with two trades.
> 
> First, the cost: commissions and fees get charged whether a trade wins, loses or scratches, so breakeven still drains the account.
> 
> Then the follow-through. My first ES long at 7,452.00 failed and closed at 7,445.75 for -$625. The same setup returned at 7,442.75, I bought 2 again with a 4 point stop, and my target at 7,471.25 filled for +$2,850.
> 
> Net for the pair: +$2,225 before costs.
> ```
> YouTube Short (48727). Title (49 chars): `Why My Stop Never Moves to Breakeven: 2 ES Trades`. privacyStatus public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.
> ```
> A stop-out, then the same setup with a new entry and a filled target. Breakeven exits still pay commissions and fees, so the stop stays put.
> 
> Education only. Not financial advice.
> 
> #shorts #esfutures #riskmanagement
> ```
> Personal TikTok (59764), 124 chars
> ```
> Lost $625 on my first long, then the same setup showed up again and paid +$2,850 at my target. Stop never went to breakeven.
> 
> #MyHobbyismyFREEDOM #esfutures #futurestrading
> ```
> 
> ## Proposed slots (ET), NOT scheduled
> Part 1 tonight Thu 11/5: FB 5:00 PM, IG 5:15 PM, DRT TikTok 5:30 PM, personal TikTok 6:15 PM, YouTube 6:45 PM (2nd Short today).
> Part 2 Fri 11/6: FB 5:30 PM, IG 5:45 PM, DRT TikTok 6:00 PM, personal TikTok 6:45 PM, YouTube 7:00 PM (Fri recap routine runs 4:57 PM).
> Combined instead: tonight FB 5:00, IG 5:15, DRT TikTok 5:30, personal TikTok 6:15, YouTube 6:45.
> Caps today before these: TikTok 3 of 4, FB 1 of 3 (+ 7:52 PM lifestyle reel), IG 1 of 2, YouTube 1 of 1; Tim overrides caps for trade posts.
> 