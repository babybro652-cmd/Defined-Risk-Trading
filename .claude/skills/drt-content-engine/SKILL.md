---
name: drt-content-engine
description: Tim's end-to-end content engine for Defined Risk Trading. Takes a trade screenshot, trade video (via Google Drive), or a topic, writes a separate native caption for each platform (Instagram, TikTok, Facebook), makes sure no two captions share wording, runs the pre-publish checks, then schedules to Blotato. Non-trade posts go out on autopilot. Trade posts are held and Tim gets a phone notification to approve. Triggers on "post this trade", "make content from this", "DRT post", a dropped trade screenshot/video, or "run the content engine".
argument-hint: "[screenshot | Drive video link/name | topic]"
---

# DRT Content Engine

You run content for **Defined Risk Trading** so Tim doesn't have to. Tim works a full-time job and trades at lunch. Every minute he spends on posting is a minute he doesn't have. Be fast, be finished, and only interrupt him when the rules below say to.

This skill orchestrates the existing skills. Don't re-implement them:
- `brand-brief.md` (repo root) for the voice, the wedge, and the CTA
- `viral-hooks` for hooks
- `post-grader` for scoring (every caption must score **8+/10**)
- Blotato MCP tools for publishing

Brands in scope right now: **Defined Risk Trading only.** Prosperity Legendz is on hold until Tim redefines it. Nested Lumen is dead, so never post to it.

---

## The 6 rules Tim set (non-negotiable)

1. **Autopilot by default.** Non-trade posts (mindset, education, 9-5 grind, promos, testimonials already approved by the student) get written, graded, and scheduled without asking.
2. **Trade posts need Tim's approval.** A post is a *trade post* if it contains any of: P&L or dollar results, entries/exits/stops/targets, a trade screenshot or trade video, win/loss counts, a weekly recap, or funded/prop account numbers. Build it in full, but **do not schedule it** until Tim approves (see Approval gate).
3. **No two posts share the same words.** Each platform gets its own caption written for that platform. It's the same idea, not the same text. Enforce this with `scripts/check_unique.py` (below).
4. **Never publish placeholder or test text.** If the caption contains `Post Text`, `[`, `TODO`, `TEST`, `lorem`, or is under 20 characters, stop. (A literal "Post Text" post went live on 9/26. Never again.)
5. **Never name "AMD" or "CRT" in public copy.** They're Tim's proprietary method names and belong only inside the paid course. `brand-brief.md` mentions them for context only. In captions, describe the idea instead ("the 3-candle entry", "session liquidity").
6. **Fact-check before anything posts.** Every claim about markets, sessions, contracts, or numbers gets checked against "Verified Market Facts" in `brand-brief.md`. Anything not covered there and not confirmable from CME Group gets cut. (A post on 9/27 called Globex a session. Globex is the electronic platform that runs almost the whole week.)

---

## Workflow

### Step 1: Intake

Figure out what you were given:

| Input | What to do |
|---|---|
| Screenshot/image in chat | Read it. Pull the instrument, direction, entry, exit, stop, targets hit, and $ result if visible. It's a trade post. |
| Video | Videos must come from **Google Drive**. Find the file with Drive search (Tim's phone drops them there), confirm its sharing includes `anyone` → `reader` (`get_file_permissions`), then use `https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t` as the media URL. If it isn't shared, ask Tim to set it to "anyone with the link" and don't change sharing yourself. |
| Topic / idea only | Non-trade post. Pull the angle from `brand-brief.md` (wedge: risk management before strategy). |

If a trade number is unreadable, don't guess. Ask Tim once, in one short message.

**Where videos live:** Tim's phone uploads to the **DRT Phone** folder in the support@definedrisktrading.com Drive. That folder is shared with the connected babybro652@gmail.com account and set to "anyone with the link", so new clips show up in Drive search (`mimeType contains 'video/'`, newest first) and need no sharing changes. CapCut exports are named `lv_0_<timestamp>.mp4`.

**Photo limits:** TikTok rejects phone screenshots taller than 9:16 ("Unsupported picture size"; a 1080x2340 screenshot failed on 9/27). Ask Tim to crop to 9:16 (1080x1920) before uploading, or skip TikTok for that post.

**Video limits:** keep it under 100 MB and at a steady **30 fps**. Raw phone screen recordings get rejected by TikTok ("Unsupported frame rate"), so Tim runs them through **CapCut** and exports at 30 fps first. If TikTok still fails for that reason, post to the other platforms anyway and tell Tim to re-export at 30 fps.

### Step 2: Write one native caption per platform

Write each from scratch. Don't write one and trim it into the others.

| Platform | Blotato account | Native shape |
|---|---|---|
| **Instagram** | `68887` (@definedrisktrading) | Hook in the first 125 chars. 3-6 short lines with line breaks. CTA that drives **saves or shares**. 3-5 niche hashtags at the end, always including `#MyHobbyismyFREEDOM` and `#definedrisktrading`. **Reels only** (`mediaType: "reel"`): usually the TikTok video with its own caption. |
| **TikTok** | `58063` (@definedrisktrading) | Short caption: **under 150 chars**, keyword in the first 30. Talks like a person, not a post. Max 5 hashtags, always including `#definedrisktrading`. Video or photo carousel (the top TikTok so far was a carousel). `privacyLevel: PUBLIC_TO_EVERYONE` for live posts, `isAiGenerated: false`, `isBrandedContent: false`, `isYourBrand: false`. |
| **Facebook** | `50185`, **pageId `993318963868124`** (Defined Risk Trading page) | Story-first and conversational. Can run longer than IG. **No hashtags.** **Every post needs a video (reel). No text-only posts.** CTA that drives **saves or shares**. ⚠️ The account's default page is Prosperity Legendz, so **always pass `pageId: 993318963868124` explicitly.** |

YouTube is connected but has no posts yet. Skip it unless Tim asks.

Voice (from `brand-brief.md`): calm, disciplined, real. A trader working a 9-5 who defines risk first. Use contractions and digits for numbers. No em dashes. No hype ("to the moon", "easy money"). Never promise returns. No filler words: actually, really, just, simply, truly, genuinely.

**CTAs:** ask for a save, share, or follow ("Save this", "Follow for the exit"). Don't ask people to comment or tag someone: every post from 9/8 to 9/26 got 0 comments.

**Content mix** (from Blotato results 9/8-9/26):

| Share | Type | Why |
|---|---|---|
| 40% | **9-5 proof**: a real result framed around the day job ("$2,100 before 8 AM. Then I went to work.") | Top 2 TikToks (447 and 374 views, most likes) |
| 40% | **Education**: one market concept, no P&L ("The market's first move is designed to trap retail traders") | Only breakout post: 3,406 views on Facebook |
| 20% | **Loss lessons and lifestyle**: stop-outs, rules broken, rest days | Mid-to-low reach (190-220 views). Keep for honesty, don't lead with it |

Open with the result or the concept, not with a confession. Proof posts are trade posts, so they still go through the approval gate.

### Step 3: Fact-check, then grade

First, list every factual claim in each caption (session names and times, contract specs, how the market works, any statistic, any trade number) and check each one against "Verified Market Facts" in `brand-brief.md` and, for trades, against Tim's source. Fix or cut anything wrong or unverifiable. Then run `post-grader` on each caption for its platform. Rewrite anything under 8/10.

### Step 4: Uniqueness check

Save the captions to a JSON file (`{"instagram": "...", "tiktok": "...", "facebook": "..."}`) in the scratchpad and run:

```bash
python3 .claude/skills/drt-content-engine/scripts/check_unique.py /path/to/captions.json
```

It fails if any two captions share a run of 5+ words in a row (hashtags and trade numbers don't count). On failure, rewrite the flagged caption and re-run. Also compare against the **last 7 days** of published posts (`blotato_list_posts`) so no post repeats an old one's wording.

### Step 5: Pre-publish checks

**Media QA (mandatory, every post, before any `blotato_create_post` or `blotato_update_schedule` that sets media).** Added 10/3 after a review video showed an AI calendar reading "2024" and a fake "$155 target / $1.35 per share" chart, and a stop-cluster video went out under a volume caption.

1. Extract frames and look at them. Videos: `ffmpeg -i in.mp4 -vf fps=2,scale=240:-1 f_%03d.png`, tile into a contact sheet (PIL), and Read the sheet. ffmpeg lives at `/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2` (or `pip install imageio-ffmpeg`). Images and carousels: Read every slide. Download Blotato visuals from their `mediaUrl` first.
2. **Topic match:** the visuals and any burned-in captions/narration match the caption's topic.
3. **Dates:** no visible dates or years (calendars, clocks, chart axes, documents) unless correct for the post date.
4. **AI text:** no garbled, misspelled or nonsense text, and no invented prices, targets, P&L or per-share/stock numbers on ES content.
5. **Reuse:** one video goes to several platforms only if every platform's caption fits that video.
6. Any failure: fix it (blur/cover the region or replace the shot, keeping captions, audio and length), regenerate, or swap the media. Never schedule it as is. Note the contact sheet path in the Step 7 report.

For AI image prompts add "no text, no numbers, no dates, no calendars, no screens". Put text the viewer must read on a clean graphic you render yourself (PIL) and upload it as a scene.

- [ ] Media QA above passed for every video/image (contact sheet checked)

- [ ] Fact-check done: every market claim matches "Verified Market Facts" or was cut
- [ ] Rule 4 placeholder scan passes
- [ ] Hashtag counts: IG 3-5, TikTok ≤5, Facebook 0. `#definedrisktrading` on IG and TikTok
- [ ] Video attached for IG and Facebook, video or carousel for TikTok
- [ ] No filler words, no comment/tag CTAs
- [ ] Facebook `pageId` = `993318963868124`
- [ ] Every number in the caption matches the screenshot/video exactly (trade posts)

### Step 6: Schedule or hold

**Non-trade post:** schedule straight away in the next open slot (below). No approval needed.

**Trade post → Approval gate:**
1. Show Tim all 3 captions in one compact block, labeled by platform, with the planned post times.
2. Send a phone notification with `PushNotification`: under 200 chars, leading with the action. Example: `Approve trade post: ES short +$1,075 (IG/TT/FB). Reply "go" or send edits.`
3. Wait. Schedule only after Tim says go (or approves an edited version). If he edits one platform, re-run Step 4 before scheduling.

**Posting cadence (per day): TikTok 3, Facebook 2, Instagram 1.** TikTok is the growth platform. Instagram reels reach 12-64 views, so 1 repurposed reel a day is enough there. The daily routine "Master Content Agent — Daily" (5:00 AM ET) fills these slots with non-trade posts:

| Platform | Slots (ET) |
|---|---|
| TikTok | 7:00 AM, 12:00 PM, 8:00 PM |
| Facebook | 9:00 AM, 5:00 PM |
| Instagram | 12:30 PM |

Trade posts from this skill are extra on top of those, with a daily cap of TikTok 4, Facebook 3, Instagram 2. Before scheduling, check `blotato_list_schedules`. If a platform is already at its cap today, replace (`blotato_update_schedule`) the next upcoming non-trade post on that platform instead of adding another. Approved trade posts usually go out right away ("post now"); otherwise use the next open slot at least 30 minutes from any other post on that platform.

### Step 7: Report

One short table: platform, scheduled time (ET), Blotato post ID or submission ID, and status. For immediate posts, poll `blotato_get_post_status` until it's `published` or `failed`. If one platform fails, report the exact error and still ship the others.

---

## What NOT to do

- Don't copy-paste one caption across platforms, even with small tweaks. Rule 3.
- Don't schedule a trade post without Tim's explicit go. Rule 2.
- Don't change Google Drive sharing settings yourself.
- Don't post for Prosperity Legendz, Propa Pit Designs, or Nested Lumen from this skill.
- Don't use customer names or testimonials unless Tim has confirmed the student agreed.
- Don't send a push notification for anything except a trade approval or a failure Tim needs to act on.
