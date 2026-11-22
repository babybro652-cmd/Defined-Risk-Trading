# AI explainer test (Blotato credits), 11/22

**STATUS: TEST ONLY. NOT SCHEDULED, NOT POSTED.** Tim approved one AI-generated explainer (11/22) to compare with our
locally built reels. Nothing goes out unless Tim says so.

## What was made
- Topic: daily max math (evergreen, non-trade). Uses documented rules only: hard stop 3.5-4 pts from ENTRY, wait for
  the label, 1-2 good trades, $1,000 daily max. ES $50/pt is contract spec. No AMD/CRT, no real trade, no P&L.
- Blotato template: "AI Video with AI Voice" (`/base/v2/ai-story-video/5903fe43-514d-40ee-a060-0d6628c5f8fd/v1`),
  6 scenes, flux-schnell images (not animated), ElevenLabs voice "Bill (American, trustworthy)", word-by-word captions
  center, teal highlight #2EC4B6, fade transitions, 9:16. Design id `7fe449e3-c9ab-4dbb-a2ae-11dda309f287`.
- Raw render (Blotato): https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/videogen2-render-854c66b9-8bdf-4627-a8ea-d71d21a5615f.mp4
  (41.2 s, 63 MB, voice only, -23.2 LUFS).
- Final local file: `posts/media/2026-11-22-ai-test/ai-test-explainer.mp4` (41.2 s, 1080x1920, 7.4 MB): music bed
  cliff_road_chill ducked under the AI voice with `drt/audio/add_audio.py --video-audio auto` (AUDIO QA: PASS, voice
  22.5 dB over music, 100% of words recovered, true peak -2.0 dBFS), then re-encoded CRF 23.
- QA files: `contact_sheet.png` (1 fps), `frame0.png`, `audio_sheet.png` in the same folder.

## Voiceover script (as spoken; speech-to-text matched every word)
1. This is the math that decides how long your trading day lasts.
2. One ES contract moves fifty dollars a point. A four point stop is two hundred dollars of risk.
3. The rule here is a hard stop, three and a half to four points from the entry. Measured from the entry, every time.
4. The daily max is one thousand dollars. At two hundred a stop, five full stops use up the whole day.
5. So the plan is to wait for the label, take one or two good trades, and keep that max far away.
6. Define your risk before the trade. What is your daily max loss?

## Media QA
- Frame 0: hook caption "THIS IS THE MATH THAT DECIDES" on screen at 0.0 s over a glowing bar shape, no black fade. PASS.
- Text: captions are Blotato's own burn-in of our script, spelled right, no garbled AI text, no dates, no invented
  prices. The images carry no text. PASS.
- People/creators: no faces, no logos, no third-party media. PASS.
- **Topic match: PARTIAL FAIL.** Scene 2 ("a single candlestick bar") came back as a literal wax candle with a flame,
  and scene 6's "faint candlestick silhouettes" are wax candles too. Scene 1's "chart" is wickless boxes, not a real
  chart. Scene 4's "five blocks" reads as one dark box. Scene 5 is an empty wooden chair by a window (mood, no
  teaching). The stop scene (teal line, red band under it) is the one image that teaches.
- Audio: raw had no music and sat at -23 LUFS; fixed locally (above). AUDIO QA: PASS after the fix.
- Last ~0.2 s goes to black (fade out). Fine for TikTok loops; trim if ever used.
- YouTube (if ever): `containsSyntheticMedia: true` (AI images and AI voice). Not a Short under the 11/17 footage-only rule.

## Draft captions (5-gram clean against each other; no em dashes, filler, AMD/CRT, link in bio; end on a question)

**TikTok** (128 chars before hashtags; `isAiGenerated: true`)
One ES contract, a 4 point stop, $200 at risk. A $1,000 daily max holds five of those. How many stops does your daily max allow?
#definedrisktrading #ES #futurestrading #riskmanagement

**Instagram**
Do the stop math before the session opens.

ES pays $50 a point, so a hard stop 3.5 to 4 points from entry costs about $175 to $200 on one contract. Against a $1,000 daily max, five full losers end the day. That's why the plan is one or two good trades after the label prints, then done.

What number do you use for your own daily max: $500, $1,000 or something else?
#MyHobbyismyFREEDOM #definedrisktrading #futurestrading #riskmanagement

**Facebook**
Here is the arithmetic behind a defined risk day on ES. Each point is worth $50 per contract. A hard stop measured 3.5 to 4 points from the entry puts roughly $175 to $200 on the line. Set a $1,000 ceiling for the day and you know in advance that five full stops would finish it. Knowing that number keeps a two-trade plan from turning into ten bad ones. Do you set your daily loss limit in dollars or in number of trades?

## Comparison: Blotato AI vs our local reels
| | Blotato AI story video | Our local reels (PIL/ffmpeg explainer, e.g. volume-profile pilot) |
|---|---|---|
| Credits | **6** (2,085 before, 2,079 after; 2 at submit, 4 at render) | 0 |
| Time | about 3.5 min render, about 6 min to a QA'd file | 20-60 min per new topic (script + render), minutes for a re-render |
| Voice | ElevenLabs, natural, clear numbers, 100% STT match | Piper john, more robotic, 98% STT match (number formats) |
| Captions | Polished word-highlight burn-in, center | Phrase captions, our layout |
| Visuals | Pretty, on-palette, but generic and sometimes wrong (wax candles for "candlestick") | Real ES bars, real numbers, asserted from data |
| Teaching value | Low: images decorate the voice, nothing on screen proves the point | High: the chart shows the concept happening |
| Control | Prompt only; can't place a stop band at an exact price or show real bars | Full control, reproducible |
| Risks | Literal misreads of trading words, wrong charts, AI look (lower trust in a trading niche), `isAiGenerated`/synthetic labels required, past 10/19-10/20 credit charges with no media | Slower to build, voice sounds synthetic |

## Take
At 6 credits the cost is negligible (2,079 left covers hundreds of these), and the ElevenLabs voice plus caption style
beat our Piper voice. The AI images do not beat our real-chart reels: they're decorative, one scene is a wax candle,
and nothing on screen is real ES data, which is our edge. Best use if Tim wants more: a hybrid, feeding our own
rendered chart clips into the same template as `uploadedMedia` per scene (keeps real bars, gains the better voice and
captions), still about 6 credits. Not recommended as-is for posting.

## Mix version (11/22): our real ES chart scenes + Blotato voice and captions
**STATUS: TEST ONLY. NOT SCHEDULED, NOT POSTED.**
- **File:** `posts/media/2026-11-22-mix-test/mix-test-explainer.mp4` (40.0 s, 1080x1920, 2.9 MB). QA files in the same
  folder: `contact_sheet.png` (1 fps), `frame0.png`, `audio_sheet.png`, `scenes_preview.png`; scene clips in `scenes/`.
- **Credits: 0.** 2,079 before, 2,079 after, across a render:false draft (`facaebd5-...`), a first render
  (`51c7d442-...`) and the final render (`3066b707-bed7-4e40-a2b6-ed471c941458`). The all-AI version charged 6, so the
  charge looks tied to AI image generation, not the voice. Raw final render (voice only, -23.6 LUFS):
  https://database.blotato.io/storage/v1/object/public/public_media/246c6cef-6cbe-4b5b-81a9-7bb84481df9c/videogen2-render-5f1e9566-d4c2-4a77-83c3-886d7881504d.mp4
- **Method:** same template ("AI Video with AI Voice"), same six-line script, voice Bill, teal #2EC4B6 word captions at
  center, fade, 9:16, trim to voiceover. Every scene's `mediaSource` is the public URL of one of OUR clips (plain URL
  string; an `{"uploadedMedia": url}` object is rejected with 422). Clips rendered by
  `posts/media/2026-11-22-mix-test/make_scenes.py` (reuses `posts/media/explainers/make_explainer.py`) on real ES 1m bars
  (Tue 11/17 NY session, date not shown), 12 s each, labels kept in y 150-620 and the chart in y 980-1640 so the center
  captions (about y 720-800) land in clear space. Render took about 9 min per run (stays at "script-ready" for most of
  it, then flips to done). Music added locally: `drt/audio/add_audio.py --video-audio auto --music soft_as_a_dry_pillow`,
  then CRF 23.
- **Scenes:** 1 session bars printing + "DAILY MAX MATH"; 2 four 1 pt blocks light up "$50" each, "1 pt = $50" to
  "4 pts = $200"; 3 example entry line, red band exactly 4 pts under it, "HARD STOP 3.5 to 4 pts from ENTRY",
  "example, not a trade call", candles stop at the entry bar (no outcome shown); 4 a $1,000 meter fills with five $200
  stops; 5 "Wait for the label / 1 or 2 good trades", two of five blocks used, "$600 left as a buffer";
  6 "Define your risk before the trade" + handle.

### Media QA (Step 5b)
- Frame 0: hook caption "THIS IS THE MATH THAT DECIDES" plus "DAILY MAX MATH" over real bars already printing. No black
  frame. PASS.
- Topic match: every scene shows the line being spoken (the $50 blocks fill as he says fifty dollars a point, the
  meter fills on five full stops). PASS. Captions never cover our labels or the chart. PASS.
- Text: Blotato captions match the script word for word, spelled right. Our labels proofread; v1 had "1 pts = $50",
  fixed in v2 to "1 pt". No dates, no invented prices, no P&L, no account numbers, status bar or home screen,
  no AMD/CRT. PASS.
- Rules: only documented rules (hard stop 3.5-4 pts from ENTRY, wait for the label, 1-2 good trades, $1,000 max).
  The stop is shown measured from the entry, not from a high/low. PASS.
- Audio: AUDIO QA: PASS, -14.1 LUFS, true peak -1.9 dBFS, voice 22.5 dB over music, 100% of words recovered.
- Nit: Blotato's "fade" dips to near black for about half a second between scenes. Fine to watch; "none" or "slide"
  would keep the chart on screen the whole time if this format continues.

### Quality vs all-AI vs our usual reels
| | All-AI (6 credits) | Mix (0 credits) | Our usual local reels |
|---|---|---|---|
| Voice | ElevenLabs, natural | Same | Piper john (robotic) or music only |
| Captions | Polished word highlight | Same | Phrase captions / text cards |
| Visuals | Wax candles, fake charts | Real ES bars, every number on screen is correct | Real ES bars |
| Teaching | Low | High: the visual proves each line | High, but text heavy |
| Build time | About 6 min | About 30 min (scene script) + 9 min render | 20-60 min |

### Labels
The images are ours now, but the voice is still AI. TikTok `isAiGenerated: true` and YouTube
`containsSyntheticMedia: true` still apply. Not a Short under the 11/17 footage-only rule.

### Take
Best of the three. It keeps what Tim liked (ElevenLabs voice, teal word captions) and replaces the part that failed
with real chart animation, at 0 credits. Costs: a scene script per topic (the renderer is reusable), a 9 min render,
and the AI voice label. If Tim likes it, it can replace the Piper voice on the animated explainers.
