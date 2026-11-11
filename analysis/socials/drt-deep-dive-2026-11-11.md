# DRT social media deep dive (Wed 11/11/2026)

Read-only analysis. Nothing was posted, deleted or rescheduled.

**Sources.** Blotato `list_accounts`, `list_posts` (all statuses, 9/1 to 11/12), `get_post_analytics`
(spot checks), `list_top_posts` (not needed: `list_posts` already carries the latest snapshot), `list_comments`
(IG + FB, since 9/1), `get_credits`. Repo: `posts/*.md` run logs, `.claude/agents/drt.md`,
`.claude/skills/drt-content-engine/SKILL.md` (slot plan), `drt/youtube/2026-10-30-youtube-monetization-plan.md`,
`TODO.md`, `posts/2026-11-07-christina-reply-script.md`. Gmail searched for Skool emails (none found).
I also downloaded the 253 Oct-Nov videos from their public Blotato URLs to measure length and whether each
has audible audio (ffmpeg `volumedetect`, mean above -60 dB = music or voice).

Accounts covered: TikTok @definedrisktrading `58063`, Instagram @definedrisktrading `68887`, Facebook page
Defined Risk Trading (`50185` / page `993318963868124`), YouTube `48727`. Posting started 9/2 (FB) and
9/7 (TT, IG), not early October, so totals run from the start and the trend tables show every week.
The detailed breakdowns (pillar, format, slot, hook, length, audio) use **10/1 to 11/9** so they reflect the
current system (text-card reels, the slot plan, Tim's DRT Phone trade reels) and skip the 9/10-9/28 period of
AI video and cohort promos.

## 0. Data gaps (read first)

| Gap | Effect |
|---|---|
| **No follower counts** on any platform. Blotato has no follower or profile endpoint. | Follower growth can't be measured here. Only YouTube reports `followsCount` per Short (subs gained). Tim can read follower history in each app (TikTok Studio, IG Insights, Meta Business Suite, YouTube Studio). |
| **No link clicks, profile visits or bio taps** on any platform. | The Skool funnel can't be measured from Blotato (section 6). |
| **Facebook views missing on 67 of 158 posts** (metrics carry likes and comments only, `lastError` null). Worst in the weeks of 9/28 (17 posts) and 10/12 (15). | FB medians use the 91 posts that have views. The earlier note of a 3,406-view FB post (9/14 "first move traps retail traders") can no longer be verified: that post now shows likes only. |
| **TikTok: 34 of 191 posts have no analytics** (null), spread across all weeks, including the 11/3 "thinking behind" trade reel. Saves are never reported for TikTok. | TikTok medians use 157 posts. |
| **YouTube: 12 of 20 Shorts have empty metrics** (every Short from 11/4 on). Snapshots seem to arrive about 1 and 7 days after posting, and the 11/4-11/9 ones haven't filled yet. | YouTube conclusions rest on 7 Shorts (10/30-11/3). Re-check after 11/18. |
| **Comment text only for IG and FB.** `list_comments` doesn't cover TikTok or YouTube. | TikTok comments (48 total, the only real comment volume) can be counted per post but not read. Cameron and Christina's comments are TikTok, known only from the repo. |
| Snapshot age: views are the last snapshot, not lifetime-to-date. Posts from the last 7 days are understated. | Rankings stop at 11/9; the 11/10-11/11 posts are left out. |

## 1. Platform scorecard

### Totals since posting started (published posts with views; scheduled and failed posts excluded)

| Platform | Posts published | Posts with views | Total views | Median views | Likes | Comments | Shares | Saves | Follower growth |
|---|---|---|---|---|---|---|---|---|---|
| TikTok | 191 | 157 | 41,687 | 193 | 1,477 | 48 | 33 | n/a | n/a (no API) |
| Instagram | 123 | 120 | 9,047 (reach 7,875) | 13 | 85 | 0 | 3 | 9 | n/a |
| Facebook | 158 | 91 | 8,570 | 10 | 97 | 1 | 3 | n/a | n/a |
| YouTube | 20 (19 since 10/30) | 8 | 706 | 69 | 16 | 0 | 0 | n/a | **+3 subs** (from 3 Shorts) |

Failed posts: TikTok 7 (all 9/14-10/13: frame rate, picture size, media URL), IG 1 (video over 120 s), FB 1 (access token, 10/4). None since 10/13.

### Since 10/1 (current system)

| Platform | Posts | With views | Total views | Median | Mean | Likes | Comments | Shares | Saves |
|---|---|---|---|---|---|---|---|---|---|
| TikTok | 117 | 101 | 31,532 | 210 | 312 | 1,178 | 45 | 26 | n/a |
| Instagram | 61 | 59 | 8,372 | 38 | 142 | 74 | 0 | 3 | 9 |
| Facebook | 88 | 47 | 5,837 | 33 | 124 | 53 | 0 | 0 | n/a |
| YouTube | 19 | 7 | 706 | 118 | 101 | 16 | 0 | 0 | n/a |

YouTube Shorts with data: average watch 12-48 s per view; the two trade Shorts held viewers longest (48 s and 35 s).

### Week over week (Mon-start weeks, ET; "med" = median views of posts with data)

| Week of | TT posts / views / med | IG posts / views / med | FB posts / views / med (synced) | YT posts / views |
|---|---|---|---|---|
| 9/7 | 17 / 1,218 / 137 | 14 / 150 / 8 | 17 / 1,656 / 62 (16) | 1 / 0 |
| 9/14 | 27 / 2,279 / 18 | 23 / 259 / 4 | 23 / 769 / 19 (12) | - |
| 9/21 | 20 / 5,356 / 305 | 17 / 178 / 3 | 21 / 282 / 6 (14) | - |
| 9/28 | 21 / 3,186 / 193 | 14 / 199 / 12 | 18 / 5 / 5 (1) | - |
| 10/5 | 15 / 5,429 / 340 | 10 / 350 / 28 | 11 / 448 / 3 (9) | - |
| 10/12 | 24 / 5,766 / 174 | 10 / 487 / 29 | 17 / 780 / 390 (2) | - |
| 10/19 | 23 / 6,472 / 210 | 10 / 473 / 33 | 16 / 18 / 2 (7) | - |
| 10/26 | 12 / 3,515 / 277 | 7 / 2,486 / 71 | 9 / 174 / 3 (7) | 2 / 125 |
| 11/2 | 28 / 7,594 / 198 | 15 / 4,346 / **121** | 22 / 4,302 / **112** (20) | 15 / 581 (5 synced) |
| 11/9 (partial) | 4 / 872 | 2 / 119 | 3 / 115 | 2 / no data |

Read:
- **TikTok is flat.** Median 175-340 a post every week since 9/21, total views 3.5k-7.6k a week, set by how many
  posts go out. No upward trend per post. More posts = more total views, not better posts.
- **Instagram and Facebook woke up in the weeks of 10/26 and 11/2.** IG median went 3 → 12 → 28-33 → 71 → 121; FB went
  from 2-6 to 112. Both line up with (a) Tim's real trade footage with captions on screen (DRT Phone reels from 10/29 on)
  and (b) every FB/IG video in the 11/2 week carrying audio (section 2). It's one strong week, so treat it as a lead, not proof.
- **YouTube** is too new and too thin on data to call.

## 2. Top 10 and bottom 10

Ranked by views, all four platforms, posts through 11/9 with data. Audio = audible music or voice in the file.

### Top 10

| # | Plat | Date (ET) | Views | Likes / Com / Sh | Pillar / format | Length, audio | Hook (first line) |
|---|---|---|---|---|---|---|---|
| 1 | IG | Fri 10/30 6:46 PM | 2,064 (reach 1,797) | 22 / 0 / 1 | trade / trade reel | 43 s, silent | "I didn't wait for my target. Here's why." |
| 2 | IG | Thu 11/5 1:02 PM | 1,386 | 11 / 0 / 0 | trade / trade reel | 58 s, music | "Breakeven stops cost money. Three ES trades show what I do instead, and where I slipped." |
| 3 | IG | Tue 11/3 3:58 PM | 1,258 | 26 / 0 / 2, 2 saves | trade / "thinking behind" reel | 83 s, music | "The thinking behind a 4.1R paper short, told in captions." |
| 4 | TT | Mon 11/2 1:02 PM | 1,123 | 71 / 2 / 1 | trade / trade reel | 45 s, music | "ES short, 4 pt stop. Lunch break ended, so I closed at +8.5 pts. It kept falling without me." |
| 5 | TT | Thu 10/29 4:45 PM | 1,071 | 60 / **17** / 2 | trade / trade reel | 45 s, silent | "ES short at 7,746, 4 pt stop. It ran, came back near my entry, then hit 7,718. +28 pts, 7R" |
| 6 | TT | Sun 9/27 12:01 PM | 937 | 37 / 0 / 0 | weekly recap / carousel | - | "Green week: +$3,275 across 4 trades while working a 9-5." |
| 7 | TT | Tue 11/3 12:38 PM | 910 | 57 / 0 / 1 | trade / trade reel | 58 s, music | "ES short with a 4 pt stop and a 16 pt target. Bracket set, hands off." |
| 8 | TT | Sat 10/10 12:01 PM | 884 | 24 / 0 / 0 | mindset / carousel | - | "Paper trading without structure builds bad habits, not skills." |
| 9 | TT | Mon 11/9 3:40 PM | 872 (1 day old) | 74 / 2 / 0 | trade / trade reel | 66 s, music | "Long at the open, short at the top. 2 ES, +$1,125 and +$1,575. ... closed when my lunch break ended" |
| 10 | TT | Wed 10/7 6:01 PM | 859 | 30 / 0 / 0 | lifestyle / carousel | - | "Trading around a 6 AM shift. This is my whole routine, night before to after work." |

Just outside: TT 10/13 lunch-break paper long (856, 65 likes), TT 10/8 "Day 1 on a new account" image (854),
TT 10/25 7 AM "Breakout above the overnight high, then the candle closes back inside?" (842, the best non-trade text card),
TT 10/23 "Stopped out twice ... third long ran 22.5 pts" (835), TT 11/5 7 AM "Yesterday's high and low" (834), FB 11/3
"thinking behind today's ES short" (815, best FB since 10/1).

### Bottom 10 (10/1-11/9)

| Plat | Date (ET) | Views | Pillar / format | Length, audio | Hook |
|---|---|---|---|---|---|
| FB | Thu 10/8 9:00 AM | 0 | education / AI video | 18 s, silent | "A wick above the range high looks like a breakout..." |
| FB | Sat 10/10 9:01 AM | 0 | education / AI video | 43 s, music | "The most expensive minute for retail futures traders is 9:30 AM." |
| FB | Sat 10/10 5:00 PM | 0 | trade-ish / reel | 40 s, music | "After a green week in ES, the instinct is to size up." |
| FB | Sat 10/24 5:00 PM | 0 | mindset / text card | 20 s, silent | "The trade right after a stop-out is the most dangerous one I can take." |
| IG | Wed 11/4 12:30 PM | 0 | education / carousel | - | "Bull or bear comes first. The entry comes second." |
| FB | Sat 10/24 9:01 AM | 1 | education / text card | 24 s, silent | "Before the New York open, I draw 2 lines on the ES chart..." |
| FB | Sun 10/25 9:01 AM | 1 | mindset / text card | 20 s, silent | "1 losing trade doesn't mean your strategy is broken." |
| FB | Fri 10/9 5:32 PM | 2 | trade / reel | 28 s, music | "Thursday morning I hit the wrong button." |
| FB | Mon 10/26 5:00 PM | 2 | education / text card | 20 s, silent | "The most common thing I see in trade reviews isn't a bad entry." |
| FB | Thu 10/29 8:15 PM | 2 | lifestyle / FB lifestyle reel | 28 s, silent | "The first thing my son inherits from me won't be money." |

TikTok's worst (10/1-11/9) was a 7 AM text card on 11/7 ("A mental stop isn't a stop", 9 views); every other TT post had 79+.

### What the winners share

1. **Tim's real chart footage.** 8 of the top 10 (and 9 of the top 12) are Tim's own trades or real results; the other
   2 are early carousels that also lean on his real story (green week while working a 9-5, 6 AM shift routine).
   Trade reels are 30 of 115 TikToks since 10/1 but have the highest median (263 vs 180 for text cards) and the
   highest engagement (6.0% likes+comments+shares per view vs 3.2%). On IG, trade reels are half the posts and **85%
   of all views**.
2. **The hook states the trade plainly:** instrument, direction, stop size, then the twist ("Lunch break ended, so I
   closed at +8.5", "came back near my entry, then hit 7,718", "I didn't wait for my target"). A loss or a mistake in
   the story (slipped stop, impatient re-entry, closed early) gets as many views as a clean win.
3. **Explained, not only shown.** The two "thinking behind the trade, told in captions" reels (11/3) were top 3 on
   IG and the best FB post since 10/1. The 3-trade breakeven video (11/5) is #2.
4. **Longer.** 30-60 s+ beats 15-30 s on every platform (TT median 231 vs 186, IG 109 vs 40, FB 85 vs 5). That's
   mostly because trade reels run longer; plain text cards at 20-24 s don't gain from being made longer.
5. **Posted when the trade happened** (12:30-5 PM, "post now"). That isn't a slot effect (see section 4).
6. **Music: no effect on TikTok, big gap on FB.** TT trade reels: silent 287 vs music 239 median; non-trade 219 vs
   194. On FB, silent videos got a median of 2-5 views vs 98-121 with audio. On IG, trade reels with audio got 124 vs 44 silent.
   The FB and IG audio cases mostly fall in the 11/2 week, so timing is mixed in.
7. **Day:** Monday is TikTok's best day (median 338), Thursday the weakest (163). The gap is small with n=10-23 a day.

Hook style (TikTok since 10/1, median views): plain statement or how-to 220 (n=57), number/P&L first 366 (n=5),
contrarian "X isn't Y" 193 (n=25), question 174 (n=14). Contrarian hooks were also the weakest on IG (29) and FB (4).
The current house style leans on "X isn't Y" openers, and they underperform.

## 3. Content pillars ranked (10/1-11/9, median views; engagement = likes+comments+shares+saves per view)

| Rank | Pillar | TikTok | Instagram | Facebook | YouTube | Notes |
|---|---|---|---|---|---|---|
| 1 | **Trade recaps / trade reels** (Tim's footage, weekly recaps) | 238 med, mean 454, 5.3% eng (n=22) | 108 med, mean 230 (n=31) | 24 med, mean 135 (n=20) | 210 (n=2) | Biggest outliers, nearly all comments, 85% of IG views. Needs Tim's go each time. |
| 2 | **Education** (levels, sweeps, sessions, sizing) | 228, 3.4% (n=43) | 28 (n=12) | 2 med, mean 111 (n=12) | 69 (n=4) | Best autopilot pillar on TikTok, at 7 AM especially (equal highs 799, overnight breakout 842, yesterday's high/low 834). |
| 3 | **Mindset / discipline** | 173, 3.2% (n=30) | 5 (n=1) | 43 (n=5) | 7 (n=1) | Steady, few outliers. Sizing after a good week (830) is the exception. |
| 4 | **Lifestyle** (day job, new dad, routine) | 156 (n=4) | 29 (n=14) | 140 med (n=8) | - | Best FB non-trade pillar (11/8 "hard edge on both sides" 250, 10/8 "By 8 PM" 204). The 6 AM shift carousel was a TT top 10. |
| 5 | **Commentary** (Wed TikTok) | 211 (n=2) | - | - | - | Too few posts to rank; matches the TT median. |
| - | Testimonial (Keaira) | 171-198 | 120 | 33 | no data | One post each; average. |

## 4. Posting slots

Trade posts go out whenever Tim approves, so they land 11 AM-5 PM and make those hours look good. The table
covers **non-trade posts only** (10/1-11/9), the posts the slot plan controls.

| Platform | Slot (ET) | Non-trade posts | Median views | Verdict |
|---|---|---|---|---|
| TikTok | **7:00 AM** | 25 | **292** (text cards 278) | Best slot. Most of the non-trade outliers (799, 834, 842) |
| TikTok | 12:00 PM | 27 | 181 (text cards 155, carousels 189) | Weakest TT slot; collides with trade posts going out at 12:30-1 PM |
| TikTok | 8:00 PM | 22 | 188 | Average. Wed commentary sits here |
| Instagram | 12:30 PM | 21 | **29** | Weak. IG non-trade reels are ~30 views |
| Instagram | carousels (various) | 6 | **4** (0-7) | Dead |
| Facebook | **9:00 AM** | 11 | **3** (0,0,1,1,2,2,3,5,33,43,309,775) | Dead apart from 2 hits. 8 of 12 posts got 5 views or fewer |
| Facebook | 5:00 PM | 10 | 44 (mean 144) | Works since 11/2 |
| Facebook | Thu ~8 PM lifestyle reel | 3 | 2 (1 synced) | No signal yet; the 10/22 and 10/29 ones were silent |
| YouTube | 6:12 PM daily AI-voice Short | 9 | 20 (3 synced: 118, 20, 17) | Weak so far; 6 of 9 have no data yet |
| YouTube | trade Shorts (12:30-4 PM) | 4 | 132-287 (3 synced) | 6-14x the AI-voice Shorts, longer watch time |

Day of week (all posts): TikTok Mon best (338), Thu weakest (163). IG Sun/Thu highest, Mon lowest (7). FB Tue
highest (106), Sat lowest (0). Small samples; don't build the plan around day of week.

## 5. Comments and engagement

**What the API shows.** IG: 0 comments on 123 posts. FB: 1 audience thread and 1 other comment since 9/1:
- Xavier Thompson (FB, 9/21) asked "What is an HTF Framework and what is the LFT strategy?" The page replied with the
  Skool link, and he wrote "I've found the course. Getting started." He also asked "What is 'ES for sells'?" on
  another post; it got no direct reply, but his own follow-up says it doesn't need one. Closed.
- Sector Zero Capital (FB, 9/18): "Slow and steady wins the race!", page replied "yes sir", then "Did you have a good
  week mate?" got no answer. 2 months old; low value.

**TikTok has the conversations** (48 comments, text not available via Blotato). Where they land:
- 17 on the 10/29 7R short ("ES short at 7,746, 4 pt stop ... +28 pts, 7R"). The most-discussed post DRT has
  made. Tim should scroll it in the app for unanswered questions.
- 4 on 10/23 "Stopped out twice ... third long ran 22.5 pts", 3 on 10/24 "Paper trading only counts if ...", 2 each on
  the 10/13 lunch-break long, 10/20 equal highs, 10/20 two shorts, 10/23 week recap, 10/24 winning streak, 11/2 lunch-break
  short, **11/6 "Right bias, red day" (Christina Cain's question)** and 11/9 long + short.
- Pattern: people comment on **real trades with a twist**, and ask how the exit worked (Christina: "how can people be
  up $1000 and end negative ... is it either SL or TP no matter what?"). Text cards rarely get comments (3 of 45
  education TikToks got any).

**Worth replying to (open as of the repo state):**
1. **Christina Cain** (TikTok, 11/6 eval trade post). A video-reply script is ready in `posts/2026-11-07-christina-reply-script.md`;
   Tim hasn't recorded it yet. A reply video built around a comment is the best way to turn the trade-reel audience into a series.
   Highest value open item.
2. **Cameron Wright** (TikTok). Per `TODO.md`, the plan is to reply after the Skool link is in the TikTok bio. Comment text
   isn't in Blotato or the repo, so check it in the app. If he asked how to learn more, reply now with "link's on my profile"
   once the bio link is live, or a short text reply naming the Skool group if the field still isn't available.
3. The **10/29 7R short (17 comments)**: check for unanswered questions; a reply-with-video on one of them is ready-made content.
4. FB "Did you have a good week mate?" (9/18): optional, stale.

Engagement rates (likes+comments+shares+saves per view, 10/1+): TikTok trade reels 6.0%, text cards 3.2%, carousels
2.4%. IG and FB about 1%. TikTok shares top out at 4; IG saves total 9.

## 6. Funnel to Skool

**There's no measurable evidence of social traffic to Skool.**
- Blotato has no link-click, profile-visit or bio-tap data on any platform.
- The TikTok bio still has no Skool link (`TODO.md`: "DRT TikTok: add Skool link ... Then reply to Cameron Wright", open).
  TikTok is where 70%+ of DRT's views are, so the biggest audience has no path to Skool.
- Captions carry no CTA (cohort closed 9/28, and the rules ban signup CTAs). The YouTube description rules ban links.
- The one traceable conversion: Xavier Thompson on FB (9/21) got a Skool referral link in a comment reply and said he found
  the course. That was during the cohort.
- Keaira (Skool member) passed her eval; the 11/6 testimonial got average reach (TT 198, IG 120, FB 33, YT no data).
- Gmail: no Skool notification emails in babybro652@gmail.com since 9/15 (they likely go to support@definedrisktrading.com,
  which Blotato is registered to). The Skool admin panel (members joined, referral source) is the only real funnel data.
- YouTube: +3 subscribers from the 3 Shorts that report follows (10/30 sim reps Short, 11/3 trade Short, 11/3 thinking Short).

## 7. Wasted effort

| Item | Cost | Return | Call |
|---|---|---|---|
| **FB 9:00 AM slot** | ~1 rendered reel a day + QA + caption | Median 3 views; 8 of 12 posts at 5 or fewer | Stop |
| **IG carousels** (Mon 7 PM carousel routine + extra) | Slide rendering, QA of every slide | 6 posts since 10/1: 0, 3, 3, 5, 5, 7 views | Stop on IG. Carousels still do OK on TikTok (median 204, two top-10s), so keep them there |
| **IG 12:30 PM non-trade reel** | 1 reel a day | Median 29 | Keep only as a repost of the TikTok 7 AM winner, never a separate build |
| **Silent videos on FB/IG** | Same build | FB silent median 2-5 | Fix: audio on every FB/IG video (add_audio.py already exists) |
| **YouTube daily AI-voice Short** | The heaviest daily build: Piper TTS, captions, audio QA, extra 5-gram check | 20 median (3 synced), 12-21 s average watch | Cut to trade/footage Shorts; decide after the 11/18 data |
| **TikTok 12 PM text card** | 1 a day | Median 155, weakest TT slot, runs into trade posts | Replace with a chart-footage education cut, or drop |
| **Blotato AI visuals (10/15-10/20)** | ~325 credits charged with no media returned | 0 | Already paused. Current pipeline costs 0 credits (2,085 unchanged for days) |
| **TikTok posts with no analytics** | 34 posts | Can't learn from them | Not effort, but worth a Blotato support ticket |

Credits: 2,085 left (well above the 600 alert line). The cost now is build time, not credits.

## 8. Recommendations (ranked by expected impact)

1. **Double down on Tim's chart footage, explained on screen.** Every top post is a real trade with a plain hook and a
   twist, and the "thinking behind the trade, told in captions" cut beat everything on IG and FB. Ask Tim for 2-3 DRT
   Phone recordings a week, including **no-trade recordings** ("the setup I passed on and why"). Those carry no P&L, so
   they could run like normal posts if Tim agrees. Re-cut each trade into a second **education cut**: the same chart,
   reframed around one concept, with the result shown last. One recording then fills about 3 slots. Needs Tim's decision
   on the approval scope.
2. **Open the funnel and work the comments.** Add the Skool link to the TikTok bio (switch to Business/Education if the field
   is missing), then reply to Cameron, record Christina's video reply (script ready), and check the 17-comment 7R post.
   Make "reply with video" a weekly format: it's the only content type built from what the audience actually asked.
   Ask Tim to check Skool admin for new members since 10/1 and their source. That's the only funnel number available.
3. **Cut the dead slots** (FB 9 AM, IG carousels, IG separate 12:30 builds, TikTok 12 PM text card) and move the time
   into recommendation 1. Total output falls from ~7-8 non-trade posts a day to ~5, and the median should rise.
4. **Audio on every FB and IG video**, not only TikTok and YouTube. FB silent videos are effectively invisible
   (median 2-5 views); every FB post that broke 100 since 10/1 had audio. Extend the TikTok music rule to FB/IG in
   `drt.md` and in the daily prompt (Step 5b).
5. **Rework YouTube to footage-first.** Trade Shorts got 125-287 views with 35-48 s watch time; AI-voice education Shorts
   got 17-118 with 12-21 s. Keep 6:12 PM, but fill it with the education cut of Tim's footage (recommendation 1) or
   the day's best TikTok with audio. Use AI voice only when no footage exists. Re-check 11/18 when the 11/4-11/11
   metrics fill in, and don't treat any YouTube conclusion as final before then.

Also: lead hooks with the concrete situation ("ES short, 4 pt stop. Lunch break ended, so...") rather than
"X isn't Y" negation openers, which ran below the platform median everywhere (TikTok -8%, IG -24%, FB -88%).

### Stop / start / double down

- **Stop:** FB 9 AM post, IG carousels, separate IG 12:30 builds, silent FB/IG videos, "X isn't Y" hooks as the default,
  AI-voice as the default YouTube format.
- **Start:** Skool link in the TikTok bio, weekly reply-with-video from a real comment, no-trade chart recordings,
  education re-cuts of every trade recording, a monthly Skool-admin funnel check, a Blotato ticket about missing TT/FB/YT analytics.
- **Double down:** Tim's trade reels (with his go), "thinking behind the trade" captioned breakdowns, TikTok 7 AM
  education (levels, sweeps, overnight high/low), FB 5 PM, Monday posting.

### Proposed weekly slot plan (ET)

| Platform | Daily slots | Content |
|---|---|---|
| TikTok | **7:00 AM** | Education text card or chart cut (levels, sweeps, sessions, sizing). Best non-trade slot |
| TikTok | **8:00 PM** | Mindset / lifestyle / Wed commentary / reply-with-video (Tue or Thu) |
| TikTok | trade reels as approved (cap 2) | Tim's footage, posted right after his go (~12:30-4 PM) |
| TikTok | 12:00 PM: **dropped** | Use only for an education re-cut of that week's trade footage (2-3x a week) |
| Instagram | 1 a day, **~5:00 PM** (test vs 12:30 for 2 weeks) | The day's best video with audio: trade reel when there is one, else the 7 AM TikTok's video. No carousels |
| Facebook | **5:00 PM** | Same video as IG when captions fit; lifestyle and job/dad angle does best here |
| Facebook | Thu 7:52 PM lifestyle reel | Keep 3 more weeks **with audio**, then judge |
| Facebook | 9:00 AM: **dropped** | - |
| YouTube | **6:12 PM daily** | Footage-based Short first (trade with Tim's go, or education cut). AI-voice only as a fallback |
| All | Mon 6:52 PM IG carousel routine: **move to TikTok** (carousels work there) or retire | - |

Weekly total: ~14 TikTok non-trade + 2-6 trade, 7 IG, 7-8 FB, 7 YouTube (down from ~21 TT, 7 IG, 14 FB, 7 YT).

## Decisions only Tim can make

1. Record Christina's reply video (script in `posts/2026-11-07-christina-reply-script.md`) and reply to Cameron.
2. Add the Skool link to the TikTok bio (in the app; it may need a switch to a Business account).
3. Send 2-3 DRT Phone recordings a week, and decide whether **no-trade "why I passed" recordings** (no P&L) can post without
   a per-post go, and whether education re-cuts of an already-approved trade need a second go.
4. Approve cutting FB 9 AM, IG carousels and the TikTok 12 PM card, and making footage the default for the YouTube Short.
5. Check Skool admin for new members since 10/1 and how they found the group (the only funnel data).

## Method notes

- Pillar and format were assigned by keyword rules on the caption plus media type and date (text-card reels from 10/15,
  when AI visuals were paused; AI or stock video before). A few posts sit on the line between education and mindset;
  the ranking doesn't depend on those.
- "Audio" = audio track with mean volume above -60 dB in the posted file. Silent tracks measure about -91 dB.
- The personal TikTok (59764), Peace by Page and Prosperity Legendz posts are excluded.
- Scratch data (not committed): `posts_full.json` in the session scratchpad.
