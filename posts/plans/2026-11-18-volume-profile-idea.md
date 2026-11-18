# Content idea from DRT Phone, Wed 11/18 3:50 PM: volume profile (NOT POSTED, third-party clip)

Source: Drive DRT Phone `Screen_Recording_20261118_155041_Facebook.mp4` (id 1FlkwtbDsrF2AbwJhAIBvlnRmrBC1uLIq,
15.1 MB, 98.7 s, 1080x2340). Tim: "New video in drt phone. Idea for content for drt."

## What it is
A phone screen recording of another creator's Facebook reel ("Pips Beyond Borders", Follow button, posted
September 23; 3.5K likes, 55 comments, 409 shares, **5.2K saves**). Animated explainer of the volume profile on a
gold chart (XAU/USD 1H): long profile bars = high-volume areas where price slows and consolidates (both sides
trading), short bars = low-volume areas price moves through fast (one side in control). Ends with "the profile shows
which levels attracted the most volume". Their voiceover and music, burned-in word captions, a "free trading PDF
guide" search tag. Not Tim's chart, voice or footage.

Why it's worth copying the idea, not the clip: saves beat likes (5.2K vs 3.5K). A clear "how this tool works"
explainer gets saved. It also lines up with what Tim is building now: Volume Bubbles ES already draws HVN zones
and a POC line (`pine/volume-bubbles-es.pine`), and TradingView's built-in Session Volume Profile works on his
Essential plan.

Never repost it, its audio, its animation or its text. Don't name or show the creator.

## Concepts

### 1. "Fast through thin, slow at heavy" on Tim's own ES chart (BEST)
- Hook (trade situation first): ES flies through some prices and sits for half an hour at others; the profile shows why.
- Format: 9:16 screen recording of Tim's TradingView ES chart (1m or 5m, today's NY session) with Volume Bubbles ES
  HVN zones + POC, or the built-in Session Volume Profile. Slow scroll: one fast move through a thin area, one stall
  in a heavy zone. Tim's voice memo over it (20-40 s, his own words). Music bed via add_audio.py.
- Platforms: TikTok 12 PM or 8 PM footage slot (reset week allows footage cuts there), IG reel, FB reel, YouTube Short
  (it's Tim's footage and voice, so it qualifies as a footage-only Short).
- Tim records: the chart clip (chart only, no account panel, no other app on screen) + a voice memo. Under 60 s.
- Tim confirms: OK to say publicly "I'm testing a volume profile on my chart, it isn't a rule". If not, cut that line
  and keep it pure education.

### 2. "Why I passed Wednesday": price walked into a heavy-volume zone and chopped
- Hook (confession): "Label printed right inside the busiest price of the day. I passed."
- Only if Tim has a real pass where that happened and says so in his own words. Wed TikTok series ("Pass #N"),
  then cut for IG/FB/Short. Never invent the reason he passed.
- Tim records: the clip of the skipped setup + one sentence on why he passed.

### 3. Moving diagram card for the 7:00 AM TikTok (reset week, no Tim recording needed)
- Hook (speed how-to): "Thick volume = slow price. Thin volume = fast price. 10 seconds."
- Format: rendered diagram (ffmpeg/PIL, 0 credits): candles already printing at frame 0, a side profile drawn on
  the left, price racing through a thin gap then stalling at a thick shelf. Reset palette (navy/teal), hook text by 0.3 s.
  Our own drawing, nothing traced from the creator's animation. No prices or numbers on it.
- Fits the reset rule of 1 DRT text card a day at 7 AM. The daily routine can use it on Thu 11/19 or Fri 11/20.

## Engagement plan fit
- TikTok reset 11/18-11/24: concept 3 fits the 7 AM card slot; concept 1 fits 12 PM / 8 PM (footage only).
- Shorts: concept 1 only (Tim's footage + voice). Thu 11/19 6:12 PM is open if he records by then.
- Series: concept 2 is a "Why I passed Wednesday" entry next week (11/25) if Tim has the clip. Too late for tonight's
  7:22 PM slot (no Tim footage today).
- Trending audio draft flow: not for this (that's for 1 trade reel a week).
- Every caption ends with a question. No "comment SKOOL" (automations inactive), no link in bio.

## Draft captions for concept 1 (ready when Tim records; swap in his words where his memo says it differently)
Checks: 5-gram unique across all four and vs 55 post files (posts/2026-10-3* and 2026-11-*, incl. 2026-11-18-trade.md),
disclaimer stripped. No em dashes, no filler words, no AMD/CRT, no P&L.

**TikTok** (146 chars before hashtags)
Why ES flies through some prices and stalls at others. Thin volume runs, heavy volume chops. Do you use a volume profile: yes, no, or testing one?
#definedrisktrading #ES #futurestrading #volumeprofile

**Instagram**
Thin volume, fast candles. Heavy volume, slow chop.

That's what the volume profile on my ES chart shows: where the market traded a lot and where it barely traded at all. I'm testing it as a tool on my chart, not a new rule. My rules stay the same: New York session, wait for the label, 3.5 to 4 point stop from entry.

Which part of the profile do you watch most: the busiest level, the thin gaps, or neither?
#MyHobbyismyFREEDOM #definedrisktrading #futurestrading #volumeprofile

**Facebook**
Ever notice ES rips through one area in seconds, then grinds sideways for half an hour somewhere else? The volume profile explains it. Where lots of contracts changed hands, both sides showed up and price slows down. Where few traded, one side was in control and price moved fast. I'm trying this out on my own chart. It doesn't change my risk. A trade I take on ES still gets a hard 3.5 to 4 point stop, New York hours only. Have you used a volume profile on futures before, or is it new to you?

**YouTube Short**
Title: Volume Profile on ES: Why Price Speeds Up Then Stalls
Description: Heavy volume levels slow ES down. Thin ones let it run. Here is how that looks on my chart. Which do you watch more, heavy levels or thin gaps?
Education only. Not financial advice.
#shorts #futurestrading #volumeprofile
Fields: public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false.

Note: the "half an hour" line (FB) and "seconds" must match what Tim's clip shows; adjust before scheduling.

QA of the source clip: contact sheets `v1550/sheet1.png`, `v1550/sheet2.png` and transcript `v1550/transcript.txt`
in the 11/18 session scratchpad (read).
