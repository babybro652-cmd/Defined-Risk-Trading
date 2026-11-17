# Peace by Page: TikTok audit (Tue 11/17/2026)

Written by the ventures agent after Tim said PbP views are dropping on TikTok. The audit itself was read-only.

> **Decision, Tue 11/17: Tim approved the plan ("Go").** What is now in effect:
> - PbP TikTok = **3 real-footage posts a week, Mon / Wed / Fri evenings.** No rendered text-card reels on TikTok (Facebook can keep them). No offer-first posts. No "link in bio" end cards.
> - **Blotato draft-to-inbox flow:** Jarvis sends each finished clip to the @peace.by.page TikTok inbox as a draft; Tim adds a TikTok sound and posts it from the app.
> - **Captions** open with a question and end with a question viewers can answer in a word. Gift angle through 12/20. Paperback mentioned only once the KDP listing is live (Calm Wings submitted 11/16 at $16.99, not live yet).
> - Week 1 starts once Tim films the proof copy (about 20 min). Full schedule and rules: `content-plan-2026-11.md`.
> - Stats: Tim doesn't have TikTok Studio. App steps are in **section 7** below (they replace the Studio steps in section 3).
> - Routines checked 11/17: no PbP routine or scheduled PbP post existed, so nothing had to be stopped. See section 8.

Sources: Blotato `list_accounts` (TikTok), `list_posts` for every TikTok account 10/1 to 12/10 (165 posts: 13 PbP, 135 DRT, 17 personal), `get_post_analytics` snapshot history on 5 PbP posts, the reel build scripts in `launch/`, `content-plan-2026-11.md`, the 11/2 analysis, the 11/11 deep dive, and the DRT engagement plan (`posts/plans/2026-11-17-engagement-plan.md`).

## What Blotato can and can't see
- PbP TikTok is in Blotato: **@peace.by.page, account 65985.**
- Blotato gives TikTok **views, likes, comments, shares**. It does **not** give saves, watch time, traffic sources, followers or profile views.
- Snapshots: 1 to 3 per post, taken 1 to 14 days after posting.
- Blotato can't see anything Tim posted by hand in the TikTok app (launch post, V1, and anything since 11/9).
- **Last PbP TikTok in Blotato: Mon 11/9.** Nothing has posted through Blotato since, and nothing is scheduled.

## 1. Data: every PbP TikTok in Blotato (10/26 to 11/9)

Times ET. Views are the latest snapshot.

| Date | Time | Post | Format | Views | Likes | Comments | Shares | Saves |
|---|---|---|---|---|---|---|---|---|
| Mon 10/26 | 8:45 PM | V2 Calm Nights evening pages | Rendered pages + text, silent | no data (analytics "not found") | | | | n/a |
| Wed 10/28 | 6:30 PM | V3 Calm Petals coloring reveal | Rendered reveal, silent | 94 | 5 | 0 | 0 | n/a |
| Fri 10/30 | 6:30 PM | V4 Three editions | Rendered product cards, silent | 35 | 2 | 3 | 0 | n/a |
| Mon 11/2 | 6:33 PM | V5 Free sampler | Rendered offer post, music | 38 | 7 | 2 | 0 | n/a |
| Tue 11/3 | 6:30 PM | V6 Box breathing | Rendered text card, music | 75 | 2 | 0 | 0 | n/a |
| Tue 11/3 | 8:45 PM | Coloring test "Color with me" | Animated coloring, music + pencil | 51 | 0 | 0 | 0 | n/a |
| Wed 11/4 | 6:30 PM | V7 5-4-3-2-1 grounding | Rendered text card, music | 36 | 3 | 0 | 0 | n/a |
| Thu 11/5 | 6:30 PM | V8 Balanced thought | Rendered text card, music | 78 | 0 | 0 | 0 | n/a |
| Thu 11/5 | 8:45 PM | Page-flip test | Animated page flip, music + flips | 85 | 0 | 0 | 0 | n/a |
| Fri 11/6 | 6:31 PM | V9 I handled it | Rendered text card, music | 84 | 0 | 0 | 0 | n/a |
| Sat 11/7 | 6:30 PM | V10 Mood petals | Rendered text card, music | 87 | 0 | 0 | 0 | n/a |
| Sun 11/8 | 6:30 PM | V11 Three good things | Rendered text card, music | 41 | 0 | 0 | 0 | n/a |
| Mon 11/9 | 6:30 PM | V12 Worry time ("Worries louder at bedtime?") | Rendered text card, music | 96 | 0 | 0 | 0 | n/a |
| 11/10 to 11/17 | | **nothing posted through Blotato** | | | | | | |

### Totals (12 posts with data)
| Window | Posts | Views | Avg views | Likes | Comments | Shares | Engagement |
|---|---|---|---|---|---|---|---|
| 10/26 to 11/2 | 3 | 167 | 56 | 14 | 5 | 0 | 11% |
| 11/3 to 11/9 | 9 | 633 | 70 | 5 | 0 | 0 | 0.8% |
| **All** | **12** | **800** | **67** | **19** | **5** | **0** | 3% |
| 11/10 to 11/17 | 0 | 0 | | | | | |

### Views stop on day 1
Snapshot history shows the views are set within the first day and never grow:
- V12 worry time: 96 on 11/10, still 96 on 11/16.
- Page-flip test: 85 on 11/6, 85 on 11/13.
- V10 mood petals: 85 on 11/8, 87 on 11/15.
- V5 sampler: 37 on 11/3, 38 on 11/17.

That is TikTok's first test batch (a few dozen to ~100 people) and no second push. No PbP post has ever been pushed past that batch.

## 2. Diagnosis

### When the drop started
- **Per-post views never dropped.** They sat in the same 35 to 96 band from 10/28 to 11/9, and week 2 averaged a little higher (70) than week 1 (56).
- **What dropped was posting.** PbP went from 9 TikToks in 7 days (11/3 to 11/9) to **0 in the 8 days since 11/9.** The 11/16 Monday slot in the content plan didn't run (it needs Tim's Clips A to D, and the week wasn't scheduled). TikTok Studio's overview counts views across the account for the last 7 or 28 days. With nothing new, that number falls fast. That is most likely the drop Tim is seeing.
- **Engagement dropped from 11/5.** The first 4 posts got 14 likes and 5 comments. The last 6 posts (11/5 to 11/9, 471 views) got **0 likes, 0 comments, 0 shares.** Early likes were likely friends and first followers. Strangers in the test batch watched and swiped on. With no engagement TikTok has no reason to show a post to more people.
- If Tim hand-posted TikToks after 11/9 that are doing worse, Blotato can't see them. The screenshots below would show it.

### What held views and what didn't
| Held (75 to 96) | Didn't (35 to 51) |
|---|---|
| V12 "Worries louder at bedtime?" (question hook, bedtime) 96 | V4 three editions (product pitch) 35 |
| V3 coloring reveal 94 | V7 5-4-3-2-1 grounding 36 |
| V10 mood petals 87 | V5 free sampler (offer) 38 |
| Page-flip test 85 | V11 three good things 41 |
| V9 I handled it 84 | Coloring test 51 (it won on IG and FB, not here) |
| V8 balanced thought 78, V6 box breathing 75 | |

The gap between best and worst is small (35 vs 96), all inside the first test batch. The only clear signal: **offer and product posts sit at the bottom** (three editions, sampler). The bedtime question hook and coloring reveal sit at the top, which matches FB and IG.

### Format
- **Every PbP TikTok so far is rendered by Jarvis.** Pages are drawn from the PDFs (Python-drawn art, not AI-generated images), set in a text-card template, with a fade-in hook and an end card. The two "tests" (coloring, page flip) are animations, not camera footage.
- **No real camera footage, no real hands, no real paper has been posted on TikTok yet.** This is the one format that hasn't been tried, and it is the one the coloring and journaling corner of TikTok rewards.
- All are videos, none are photo slideshows (TikTok photo mode).
- Text overlays: every post is text-driven. To a stranger it reads as an ad for a printable.
- Audio: V2 to V4 silent. V5 on used a music bed from the **same CC0 music library DRT uses** (`drt/audio/add_audio.py`), baked into the file. None used a TikTok sound.
- End cards on V6 to V12 say **"link in bio"**, but the TikTok bio has no link (needs 1,000 followers). Captions had the Payhip URL; the end card contradicts it.

### Hooks, times, frequency, repeats
- Hooks: question hooks did best ("Worries louder at bedtime?" 96). Statement hooks ("A 1-minute reset you can do anywhere") middle. Offer hooks worst. No post asked the viewer a question to answer in the comments, and there have been 0 comments since 11/2.
- Times: 6:30 PM (10 posts, avg 66) vs 8:45 PM (2 with data, avg 68). No difference.
- Frequency: 2 posts on 11/3 and 2 on 11/5, then daily, then nothing. Bursty.
- Repeats: same template, same fonts, same fade-in open, same end card on V6 to V12, and two near-duplicate petal mood posts (11/3 "one petal for every feeling", 11/7 "color one petal a day for your mood"). The same files also went to IG and FB. TikTok limits reach for content that looks templated or unoriginal.
- Captions: compliant (support note and 988 on every one). Long for TikTok. Hashtags fine (#anxietyjournal, #colorwithme, #coloringforadults).

### Is this the same as the DRT drop (11/11)?
| | DRT TikTok | PbP TikTok |
|---|---|---|
| Before 11/11 | 100 to 1,145 per post, trade reels 600 to 1,100 | 35 to 96, never above 100 |
| From 11/11 | Every post 74 to 104 (median 87), even trade reels | **No posts** (last was 11/9) |
| Pattern | Lost a For You push it used to have | Never had a For You push |

- **The timing doesn't match.** PbP stopped posting 2 days before DRT dropped, so there are no PbP posts in the DRT drop window to compare. PbP's normal (about 70) looks like DRT's new floor (about 87): both are "first test batch only."
- **Posting route:** both post through Blotato, which uses TikTok's official posting API from Blotato's servers. So the IP TikTok sees for these posts is Blotato's, not Tim's phone. Both accounts sit in the same Blotato workspace. API posting is allowed and is not a known penalty by itself, but it can't use TikTok sounds or TikTok's own text and effects.
- **Device:** Tim posted the PbP launch and warm-up TikToks from his phone, so PbP, DRT, the personal account and probably PL are logged in on the same phone. I can't confirm this from here. Several accounts on one phone is normal (TikTok allows up to 8) and isn't a known cause of suppression unless one account gets a violation.
- **Shared inputs:** same Blotato pipeline, same CC0 music library, the same rendered text-card style built by Jarvis, and the same posting rhythm. If TikTok reads that library or style as unoriginal, both accounts would feel it.
- **Verdict: a shared cause is possible but not shown.** The more likely story for PbP is simpler: a new account that never got past the test batch, then stopped posting. Two things would settle it: TikTok Studio's Account status on both accounts, and the traffic source on one post from each. If the personal TikTok (also down from 11/9) and DRT both show "not eligible for For You" or a warning, the cause is account-level and PbP may share it.
- One more thing to rule out: anxiety content with "988 crisis" in every caption may be handled as a sensitive wellness topic. TikTok Studio shows "not eligible for the For You feed" on a post if so. Low odds, but the screenshot checks it.

## 3. Screenshots Tim should send (5 minutes, tonight)
**Update 11/17: Tim doesn't have TikTok Studio. Use the app steps in section 7 to reach the same screens.** Original list:

TikTok app on **@peace.by.page** > Profile > menu (3 lines, top right) > **TikTok Studio**:
1. **Overview / Analytics, Last 28 days:** video views, profile views, likes, followers (the graph shows exactly when the drop started).
2. **Account status** (or "Account check"): any violation, warning or "not eligible for For You" note.
3. **One post's analytics:** open V12 worry time (11/9) > **Analytics**. Screenshot the overview (views, average watch time, watched full video %) and **Traffic source** (For You, Personal profile, Following, Search).
4. **Content list** (Analytics > Content): to show any posts made by hand after 11/9.
Optional: the same Account status screen on @definedrisktrading, to compare.

## 4. Plan: top fixes, ranked

### 1. Post again, 3 a week, starting with the real paperback (biggest lever)
- The account has had nothing new for 8 days. Get back to 3 a week (Mon, Wed, Fri evenings), not daily.
- **The Calm Wings paperback proofs are here: film them.** Real hands, real paper, real pencil sound, phone propped above the book. This is the one format PbP hasn't tried on TikTok and the one the coloring corner of TikTok rewards. No face, no voice.
- One sitting (about 20 min, an evening) gives 2 to 3 weeks of clips:
  - flipping through the paperback, slow, lamp light (8 to 10 s)
  - coloring one butterfly page in the book (3 takes: blank, half, nearly done)
  - writing one worry on a worry-time page, then closing the book
  - the proof copy in its Amazon box, opened for the first time (only if Tim has one unopened)
- Jarvis cuts each to 7 to 12 s, adds a 3 to 6 word hook at 0.0 s and the support note and 988 in the caption.

### 2. Post natively from the TikTok app with a TikTok sound
- Jarvis sends each finished clip to Tim's TikTok inbox as a **Blotato draft** (the same draft flow the DRT plan uses), or by text.
- Tim opens it in the app, picks a quiet trending or Commercial Music Library sound (at a low volume under the pencil sound), adds the hook with TikTok's own text tool if he likes, and posts. 2 to 3 minutes a post.
- This also takes PbP off the shared CC0 library and the API-only posting route, so if DRT's issue is one of those, PbP stops sharing it.
- Keep the 11/2 audio standard in the file Jarvis sends (serene, about -23 LUFS); the in-app sound sits underneath.

### 3. Question hooks that ask for a comment
- The best PbP hook was a question ("Worries louder at bedtime?"). 0 comments since 11/2 means TikTok sees no conversation.
- Every post opens on a question and ends on one the viewer can answer in a word:
  - "Does your brain get louder at bedtime?" / end: "What time does yours start?"
  - "Would you color this or write in it first?"
  - "Butterflies, flowers or moon: which one are you?"
- Tim replies to every comment within a day (2 min at 10 AM lunch). A reply with a video is even better once there is a good question.

### 4. Gift angle, now through 12/20
- "For the friend who overthinks everything" (hands tying a ribbon on the paperback or printed pages, then 3 s of coloring).
- "A gift for someone who worries" and "a $3.99 stocking stuffer for the worrier" (SOS kit).
- Ask: "Tag the friend who needs this" (drives comments and shares, the two numbers at 0).
- Link: Payhip printables now. Add "also in paperback on Amazon" only once the KDP listing is live.

### 5. Fewer, better, and no more text cards on TikTok
- **Stop rendered text-card reels on TikTok.** They never broke 100 and they look templated. They can keep running on Facebook, where they do better (FB coloring test 208, V12 189).
- Never lead with the offer on TikTok (sampler and three-editions were the bottom posts). Sampler or shop line in the last second and in the caption only.
- Drop "link in bio" from TikTok end cards; use "free 7-day journal: payhip.com/PeaceByPage".
- If no real clip exists for a slot, skip it rather than fill it with a text card.
- One TikTok photo carousel a week is optional: 5 to 7 phone photos of real paperback pages (photo mode, add a sound in the app). Low effort, a different format from the reels.

### Readout
Check on **Mon 12/7** after 3 weeks (9 posts). Target: at least 1 post past 300 views, and a comment on most posts. If real footage posted natively still stays under 100 every time and Studio shows no flag, cut TikTok to 1 post a week and put the time into Pinterest and the KDP listing, where buyers search.

## 5. What Tim needs to do
| Task | When | Minutes |
|---|---|---|
| Send the 4 TikTok Studio screenshots (section 3) | Tonight | 5 |
| Film the Calm Wings paperback (fix 1 list) | One evening this week | 20 |
| Post each clip from the app with a sound | Mon, Wed, Fri evening | 3 each (about 10 a week) |
| Reply to comments | 10 AM lunch, 3 days a week | 2 each |

About **35 minutes this week**, then about **15 minutes a week**.

## 6. What needs Tim's OK
1. Switch PbP TikTok to 3 a week, real footage only, posted from the app (and stop text-card reels on TikTok; FB keeps them).
2. Use the Blotato draft-to-inbox flow for PbP TikToks (nothing goes public until Tim posts it).
3. The gift angle copy and "tag a friend" asks for the next 4 weeks.
4. Nothing is scheduled right now and no routine was changed. The 11/16 to 12/6 content plan stays as written until Tim says to swap in these changes.
5. Separate, already pending: the KDP publish go for Calm Wings (needed before any "paperback on Amazon" line).

## 7. Reading TikTok stats without TikTok Studio (added 11/17)
Tim's app has no TikTok Studio. Same numbers, from the TikTok app on **@peace.by.page** (switch accounts first: tap your username at the top of the Profile tab).

**Account stats (views, followers, profile views):**
1. Tap **Profile** (bottom right).
2. Tap the **☰ menu** (3 lines, top right).
3. Tap **Creator tools**.
4. Tap **Analytics**. Pick **Last 28 days**. Screenshot Overview, then the Content tab (lists every post, including ones posted by hand).

**If Analytics is missing:**
- Profile > ☰ > **Settings and privacy** > **Account** > **Switch to Business account** (free; it adds Analytics). Note: Business accounts only see the Commercial Music Library for sounds, which is fine for these posts.
- Or, on a personal account: Profile > ☰ > **Creator tools** and turn on **Analytics** there if the app offers it.
- Analytics can take up to 24 hours to fill after it's turned on.

**One post's stats (watch time, traffic source):**
1. Open the video from your profile.
2. Tap **"..."** (or the share arrow, then scroll the bottom row).
3. Tap **Analytics**. Screenshot the overview (views, average watch time, watched full video) and **Traffic source** (For You, Personal profile, Following, Search).

**Account status (flags or "not eligible for For You"):** Profile > ☰ > **Settings and privacy** > **Account** > **Account status** (on some versions: Support > Safety center > Account status).

Send the screenshots to Jarvis. Blotato only sees views, likes, comments and shares on posts it sent, and **drafts Tim posts from the app don't show up in Blotato**, so these screenshots are the only way to read the new posts.

## 8. Routines and scheduled posts (checked 11/17)
- Blotato `list_posts` (scheduled, all platforms, 11/17 to 1/31): **no PbP posts scheduled** on TikTok 65985, Instagram 81296, Facebook page 1255582607649321 or Pinterest 9654. Nothing to stop.
- Routines: **no PbP content routine exists.** The only PbP routine is the one-time "Check Calm Wings KDP is live" reminder (Thu 11/19 8:17 PM ET, trig_01UA4LVhAg4jGjkDXhsrrsWj). Its prompt was updated 11/17 to also switch on the paperback line in the TikTok captions once Tim sends the Amazon link. Its time is unchanged.
- No new recurring routines were created. The Mon 12/7 readout is in the content plan; Jarvis decides whether to set a one-time reminder for it.

