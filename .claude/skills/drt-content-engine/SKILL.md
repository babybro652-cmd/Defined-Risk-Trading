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

## The 4 rules Tim set (non-negotiable)

1. **Autopilot by default.** Non-trade posts (mindset, education, 9-5 grind, promos, testimonials already approved by the student) get written, graded, and scheduled without asking.
2. **Trade posts need Tim's approval.** A post is a *trade post* if it contains any of: P&L or dollar results, entries/exits/stops/targets, a trade screenshot or trade video, win/loss counts, a weekly recap, or funded/prop account numbers. Build it in full, but **do not schedule it** until Tim approves (see Approval gate).
3. **No two posts share the same words.** Each platform gets its own caption written for that platform. It's the same idea, not the same text. Enforce this with `scripts/check_unique.py` (below).
4. **Never publish placeholder or test text.** If the caption contains `Post Text`, `[`, `TODO`, `TEST`, `lorem`, or is under 20 characters, stop. (A literal "Post Text" post went live on 9/26. Never again.)

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

**Video limits:** keep it under 100 MB and at a steady **30 fps**. TikTok rejects variable or high frame rates ("Unsupported frame rate"). If TikTok fails for that reason, still post to the other platforms and tell Tim to re-export at 30 fps.

### Step 2: Write one native caption per platform

Write each from scratch. Don't write one and trim it into the others.

| Platform | Blotato account | Native shape |
|---|---|---|
| **Instagram** | `68887` (@definedrisktrading) | Hook in the first 125 chars. 3-6 short lines with line breaks. CTA that drives **saves or shares**. 3-5 niche hashtags at the end, always including `#MyHobbyismyFREEDOM`. Needs media. Use `mediaType: "reel"` for video. |
| **TikTok** | `58063` (@definedrisktrading) | Short caption: **under 150 chars**, keyword in the first 30. Talks like a person, not a post. Max 5 hashtags. `privacyLevel: PUBLIC_TO_EVERYONE` for live posts, `isAiGenerated: false`, `isBrandedContent: false`, `isYourBrand: false`. |
| **Facebook** | `50185`, **pageId `993318963868124`** (Defined Risk Trading page) | Story-first and conversational. Can run longer than IG. **No hashtags.** CTA that drives **shares or comments**. ⚠️ The account's default page is Prosperity Legendz, so **always pass `pageId: 993318963868124` explicitly.** |

YouTube is connected but has no posts yet. Skip it unless Tim asks.

Voice (from `brand-brief.md`): calm, disciplined, real. A trader working a 9-5 who defines risk first. Use contractions and digits for numbers. No em dashes. No hype ("to the moon", "easy money"). Never promise returns.

### Step 3: Grade

Run `post-grader` on each caption for its platform. Rewrite anything under 8/10.

### Step 4: Uniqueness check

Save the captions to a JSON file (`{"instagram": "...", "tiktok": "...", "facebook": "..."}`) in the scratchpad and run:

```bash
python3 .claude/skills/drt-content-engine/scripts/check_unique.py /path/to/captions.json
```

It fails if any two captions share a run of 5+ words in a row (hashtags and trade numbers don't count). On failure, rewrite the flagged caption and re-run. Also compare against the **last 7 days** of published posts (`blotato_list_posts`) so no post repeats an old one's wording.

### Step 5: Pre-publish checks

- [ ] Rule 4 placeholder scan passes
- [ ] Hashtag counts: IG 3-5, TikTok ≤5, Facebook 0
- [ ] Media attached for IG and TikTok
- [ ] Facebook `pageId` = `993318963868124`
- [ ] Every number in the caption matches the screenshot/video exactly (trade posts)

### Step 6: Schedule or hold

**Non-trade post:** schedule straight away in the next open slot (below). No approval needed.

**Trade post → Approval gate:**
1. Show Tim all 3 captions in one compact block, labeled by platform, with the planned post times.
2. Send a phone notification with `PushNotification`: under 200 chars, leading with the action. Example: `Approve trade post: ES short +$1,075 (IG/TT/FB). Reply "go" or send edits.`
3. Wait. Schedule only after Tim says go (or approves an edited version). If he edits one platform, re-run Step 4 before scheduling.

**Posting slots (ET)**, matching the rhythm already working:
- Instagram: **10:00 AM**
- TikTok: **12:00 PM** and **7:00 PM**
- Facebook: **5:00 PM**

Trade posts approved during the trading day can go out right away instead ("post now"). Keep about **2-4 posts per platform per day**. Check `blotato_list_posts` for what's already scheduled so you don't stack posts into a slot that's taken.

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
