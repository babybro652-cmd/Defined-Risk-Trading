**STATUS: ON HOLD (Tim 11/18 evening). Tweak with Tim this weekend; do not schedule any explainer until he approves.**

# Animated chart explainers: series plan (Tim, 11/18)

Tim, 11/18 evening, on the "Pips Beyond Borders" volume-profile reel he saved to DRT Phone: "I mean for you to
create videos like this for content." So DRT makes its own animated chart explainers: real ES bars, the concept
builds on the chart step by step, on-screen text teaches, music only. Never their frames, text, audio or branding.

## What we took from the reference (style only)
Reference: 98.7 s, voice + music, word-by-word burned captions, gold chart with a left-side profile, a new
element every 4-6 s (profile, green high-volume bands, red low-volume bands, then a simplified line diagram),
closes on "the profile shows which levels attracted the most volume". 5.2K saves vs 3.5K likes: a clear "how this
tool works" explainer gets saved.

Our format (different on purpose): real ES session bars (not a drawn line), navy/teal reset palette, a text panel
that builds word by word, one new layer per scene, real numbers from the session as the payoff, a defined-risk
close. 45-75 s, chart moving and hook on screen at frame 0, no voice.

## Render
- Script: `posts/media/explainers/make_explainer.py --topic <name> --out X.mp4 --stills DIR` (`--list` shows topics).
- Bars: `posts/media/explainers/data/*.csv` (time_et, OHLC, volume), saved from Yahoo ES=F 1m JSON so renders stay
  reproducible. A new topic = one function returning Scenes + an entry in `TOPICS`.
- Music: `python3 drt/audio/add_audio.py X.mp4 -o X-music.mp4 --music NAME --sheet sheet.png` (AUDIO QA: PASS,
  track not used on TikTok the same day or the day before). Then the usual media QA (contact sheet, frame 0).
- On-screen numbers come from the bars; the script asserts them so a data change can't leave stale text.

## Pilot: volume profile (built 11/18, NOT scheduled; Tim sees it first)
`posts/media/explainers/volume-profile/volume-profile-music.mp4`, 67.8 s, music soft_as_a_dry_pillow, AUDIO QA PASS.
ES NY session Tue 11/17 (date not on screen), 5m candles from 1m bars, 1-pt profile bins.
Facts on screen: 60 points in 13 minutes (10:30 to 10:43 ET closes, 7400.25 to 7340.25); POC 7348; heavy zone
7337-7364 (226 of 390 one-minute closes); thin zone 7381-7402 (9 closes all day).

Captions (5-gram clean vs each other and 81 post/plan files; no em dashes, filler, AMD/CRT, link in bio):

**TikTok** (144 chars before hashtags)
ES dropped 60 points in 13 minutes, then sat in one zone for hours. Thin vs heavy volume, animated. Which zone do you mark first: thin or heavy?
#definedrisktrading #ES #volumeprofile #futurestrading

**Instagram**
60 points down in 13 minutes. Then hours of sideways.

Same ES session, two kinds of price levels. Where few contracts traded, price had nothing to slow it down. Where volume piled up, buyers and sellers kept trading against each other and the candles went flat. The longest bar sits where the most volume printed.

A volume level is a planning tool. The stop still gets decided before the entry.

Which would you rather trade near: a thin gap or a heavy shelf?
#MyHobbyismyFREEDOM #definedrisktrading #futurestrading #volumeprofile

**Facebook**
One New York session on ES, replayed bar by bar. Price dropped 60 points in 13 minutes through a stretch where almost nothing traded, then spent most of the afternoon inside one crowded range. Stack the day's volume at each price and the reason shows up: thin areas give price room to run, crowded areas slow it down. Marking both before the next session gives you a map. It doesn't pick the stop for you. Do you look at volume by price on your chart, or only volume by time?

**YouTube Short (only if Tim allows explainers as a Shorts exception)**
Title: Volume Profile on ES: 60 Points in 13 Minutes, Then Chop
Description: Watch one ES session get sorted into thin and heavy volume, then see where the candles sped up and where they stalled. Which one shows up on your chart first, the gap or the shelf?
Education only. Not financial advice.
#shorts #futurestrading #volumeprofile
Fields: public, shouldNotifySubscribers false, isMadeForKids false, containsSyntheticMedia false (rendered chart, no AI voice or AI imagery).

## Voiced version (Tim, 11/18: "Do a voiceover explanation")
`posts/media/explainers/volume-profile/volume-profile-voice.mp4`, 90.5 s, Piper TTS voice en_US-john-medium (local,
free, public-domain LibriVox dataset; clearer on numbers than norman, the old AI-Short voice), speed 1.15, music
soft_as_a_dry_pillow ducked 22.5 dB under the voice, phrase captions burned in at y 1560 (above the bottom UI), handle
moved to the chart header. Script with start times: `posts/media/explainers/volume-profile/voiceover.txt`.
AUDIO QA PASS (-14.3 LUFS, true peak -1.6 dBFS, 0 clipped). Speech-to-text (faster-whisper small.en) on the final file:
98% of script words; the misses are number formats ("7348" heard as "73 48", "9" as "nine") and one whole-file
mishearing of "226" that reads correctly when the segment is checked on its own.
Render: `make_explainer.py --topic volume-profile --voice --speed 1.15 --music soft_as_a_dry_pillow`.
The voice is synthetic: YouTube `containsSyntheticMedia: true` if Tim ever OKs it as a Short (it's also over 60 s).
The 11/17 stop on AI-voice Shorts was for low performance; this voiced explainer is Tim's 11/18 call for this format.
The captions below still fit the voiced cut (unchanged, still 5-gram clean).

## Next topics (one real ES session each, picked for a clean example)
1. **Liquidity sweep vs breakdown**: price trades under a marked low; the close back above (or below) decides which. Real NY bars, the low marked, two outcomes side by side.
2. **FVG vs IFVG**: a 3-candle gap draws in, price fills it, then the gap flips (inverse) and holds from the other side.
3. **The stop goes in before the entry**: entry line drops in, then a 3.5-4 pt band from entry (never "above the high"), then the dollar risk per contract. Tim's rule stated as his rule, nothing invented.
4. **NY open vs 10 AM**: replay 9:30-10:30 on several real days; the first 30 minutes' range vs what came after 10. Tim mostly watches before 10 and only takes a small trade if his setup shows (his words, 11/13).
5. **HVN/LVN part 2: the next day**: yesterday's heavy and thin zones carried onto today's chart; what price did when it reached them (pick a day that shows it, say it's one example).
6. **Absorption at a level**: big volume bars at a level while price barely moves; drawn from bar volume vs range on real 1m bars. No order-flow tool names.
7. **Risk per point: ES vs MES**: ES $50/pt, MES $5/pt; a 4 pt stop is $200 vs $20. General education only; never say Tim trades micros.
8. **Position sizing to a daily max**: $1,000 daily max, 4 pt stop, 1 ES = $200 a stop; how many stops fit, and why fewer trades protect the max.
9. **Waiting for the label**: the pivot prints, nothing to do until the confirmation bar closes; early entry vs label entry on the same real bars, no indicator names.
10. **Fast through thin, part 3: up moves**: the same idea on a rally day (so the series isn't all selloffs).

## Cadence and slots (suggested; Tim decides)
- **Reset week (through Tue 11/24):** 2 explainers, each used as that day's single 7:00 AM TikTok card (it meets the
  reset look: chart moving at frame 0, hook by 0.3 s, navy/teal). Suggested Fri 11/20 and Mon 11/23. Same MP4 on IG
  12:30 PM and FB 5:00 PM that day (each with its own caption, logged in `analysis/socials/music-test-fb-ig.md`).
- **After the 11/24 readout:** 2-3 a week (e.g. Tue / Thu / Sun) if the explainer views beat the 87 median; drop to 1
  a week if they don't.
- **YouTube Shorts:** none until Tim says explainers are an exception to the 11/17 footage-only rule.
- Explainers count as non-trade education (autopilot) once Tim OKs the format; any explainer that shows one of
  Tim's real trades still needs his go.
- The daily routine (prompt in `trig_01NkNxxc7neQATLrTifB42kv`) can render one per topic with the script above once
  Tim approves the pilot; that prompt is not changed yet.
