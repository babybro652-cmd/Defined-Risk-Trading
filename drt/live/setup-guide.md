# DRT TikTok LIVE: setup guide

Evening show on @definedrisktrading, 2-3 nights a week, about 30 minutes.
Overlays: `drt/live/overlays/` (rebuild with `python3 drt/live/make_overlays.py`).
Show plan: `drt/live/show-outline.md`.

## 1. Eligibility check (do this first, on the phone)

TikTok changes these rules by region and over time, so check the app instead of trusting a number.

1. Open TikTok on @definedrisktrading, tap **+**, swipe the bottom bar to **LIVE**.
   - LIVE tab shows up: the account can go LIVE from the phone.
   - No LIVE tab: not eligible yet. The usual gates are age 18+, a follower minimum
     (often 1,000 in the US), and an account in good standing.
2. Check standing: **Profile > menu > Settings and privacy > Account status** (or
   **Account check**). Any active LIVE restriction or violation has to clear first.
3. LIVE Studio (the Windows app) and stream keys for OBS can need their own access on top of
   phone LIVE. If LIVE Studio says the account isn't eligible, stream from the phone for now
   (see section 6) and check again after the follower count grows.
4. Gifts and LIVE rewards need 18+ and separate eligibility. Not needed for the show.

Content policy to keep in mind: TikTok restricts promoting financial services and
get-rich-quick claims. The show stays education: process, levels, risk. No signals,
no income claims, no pushing people off the app on repeat. One calm Skool mention at the end.

## 2. TikTok LIVE Studio (Windows) install and first setup

1. On the PC, download **TikTok LIVE Studio** from TikTok's official site (search
   "TikTok LIVE Studio download" and use the tiktok.com link). Install and sign in to
   @definedrisktrading (QR code from the phone works).
2. Pick the **Portrait** layout (1080x1920). That matches the portrait overlay set.
3. Settings > Video: 1080x1920, 30 fps. Let it auto-pick bitrate, or set about
   4,000-6,000 kbps if the upload speed allows (run a speed test; you want 10+ Mbps up).
   Wired Ethernet beats Wi-Fi.
4. Title idea format: "ES futures: today's levels + tomorrow's plan". Topic: Education or
   Finance. No "signals", "calls" or money amounts in the title.

## 3. Build the scene (sources, bottom layer first)

Open `drt/live/overlays/portrait-layout-guide.png` next to the Studio window while you set this up.

| Layer (bottom to top) | Source type | Where |
|---|---|---|
| 1. TradingView chart | Window Capture (or Display Capture) | Bottom 60%: y 768 to 1920 |
| 2. Webcam | Camera / Video capture device | Top 40%: y 0 to 768 |
| 3. `portrait-banner.png` | Image | Stretch to full canvas |
| 4. `portrait-disclaimer.png` | Image | Full canvas (bar sits on the cam/chart seam) |
| 5. `portrait-tagline.png` | Image | Full canvas |
| 6. Bias / plan cards | Image, toggle on and off | Full canvas |

Every overlay PNG is full-canvas (1080x1920) and transparent, so "Fit to screen" puts each
piece in the right spot. Turn them on and off with the eye icon.

**Webcam:** add the camera, crop or zoom so it fills the top 1080x768 box with your face in
the middle, slightly below the banner. Light in front of you, window behind the camera, not
behind you.

**TradingView window:**
- Use the TradingView desktop app (or a browser window with only the chart). Size the window
  close to 1080 wide by 1152 tall so it drops into the bottom box without heavy cropping.
- Dark theme, bigger candles, scale font size up (Chart settings > Appearance / Scales).
  Phones show this small: fewer indicators, thicker level lines.
- **Hide indicator names.** Chart settings > Status line: turn off indicator titles and
  values. The indicator's name must not show on stream, and label text on the chart should
  not show the acronyms either. Check the preview before every show.
- Hide the broker / trading panel, account numbers, balance and order ticket. Close
  messages, email and anything personal on that screen.
- If the capture is black: switch to Display Capture, or turn off hardware acceleration in
  the TradingView app / browser settings.
- Keep key levels in the upper half of the chart box and toward the right side. Phone
  viewers see comments over the lower left and buttons on the right edge (red zones on the
  layout guide).

**Bias and plan cards:** `portrait-bias.png` has a blank slot. Either type over it with a
Text source (DejaVu Sans Bold or Arial Bold, gold #E8B25C), or use the ready versions
`portrait-bias-bullish.png`, `-bearish.png`, `-neutral.png`. Show the bias card in the recap
segment, swap to `portrait-tomorrow-plan.png` for the plan segment. Only one card at a time.

**Banner versions:** `portrait-banner.png` (with "Skool link in bio"),
`portrait-banner-plain.png` (name only), `portrait-banner-code.png` (adds a CODE slot on the
right for a future affiliate code; rebuild with
`python3 drt/live/make_overlays.py --code YOURCODE` once there is one).

## 4. Mic and sound

- A USB dynamic mic (or a headset mic) close to your mouth beats the webcam mic. Keep it
  4-6 inches away, slightly off to the side.
- In Studio audio settings: pick the mic, turn on noise suppression, mute desktop audio
  unless you need it. Speak and watch the meter: peaks in the yellow, never the red.
- No background music. Business accounts can't use most songs, and copyrighted music can
  get a LIVE cut off.
- Turn off PC notification sounds and put the phone on Do Not Disturb.
- Wear headphones if you read comments out loud from a second device, to stop echo.

## 5. OBS alternative (and the landscape set)

Two ways OBS helps:

1. **OBS as the camera for LIVE Studio** (works without a stream key). Build the scene in OBS
   at 1080x1920 (Settings > Video > Base and Output 1080x1920), click **Start Virtual
   Camera**, then in LIVE Studio add a Camera source and pick "OBS Virtual Camera".
2. **OBS streaming direct** needs a TikTok server URL and stream key. TikTok gives those only
   to some accounts (LIVE Center / LIVE Producer on the web). If the account has it: OBS >
   Settings > Stream > Service "Custom", paste the server and key. The key changes, so copy it
   fresh before each show. Never share it or show it on screen.

OBS scene setup: same order as the table above. Add each overlay as an **Image** source,
right-click > Transform > Fit to screen. Use Scenes for segments ("Recap" with the bias card,
"Plan" with the plan card) and switch with one click.

The **landscape set** (`landscape-*.png`, 1920x1080) is for a 16:9 OBS canvas: YouTube LIVE
later, or a TikTok landscape LIVE. Layout: chart on the left 72% (0 to 1380 px), webcam in
the right column (about 540x710), banner top left, disclaimer bar across the bottom. See
`landscape-layout-guide.png`.

## 6. Phone-only fallback

If LIVE Studio isn't unlocked yet: go LIVE from the phone and share the screen (LIVE > Mobile
gaming / screen share, where offered) with the TradingView app. Overlays won't show, so say
the disclaimer out loud and put "Education only. Not financial advice." in the LIVE title.

## 7. Test before going public

TikTok doesn't offer a fully private LIVE, so test in layers:

1. **Preview and record locally.** In LIVE Studio (or OBS > Start Recording), run 3-5
   minutes of the intro and a chart walkthrough. Watch the recording on the phone: is the
   chart readable, are indicator names hidden, any account info showing, is the voice clear,
   do the cards line up?
2. **Private stream test with OBS:** stream the OBS scene to YouTube with visibility set to
   **Private** or **Unlisted** (YouTube needs phone verification and can take 24 hours to turn
   on live streaming the first time). Watch it on the phone.
3. **Soft launch:** first public LIVE short (10-15 minutes), the segments from the outline
   without pressure. Then go to the full 30.

## Pre-show checklist (2 minutes)

- [ ] Phone on Do Not Disturb, PC notifications off
- [ ] TradingView: indicator titles hidden, no account panel, levels drawn for today
- [ ] Bias decided (bullish / bearish / neutral) and card ready
- [ ] Mic check: meter peaks in the yellow
- [ ] Disclaimer bar and banner on
- [ ] Water, notes from the outline, timer running
