# Modules 4 & 5: Recording Scripts (v4)

Word-for-word teleprompter scripts for `module_4_liquidity_volume_v4.pptx` and `module_5_workflow_risk_v4.pptx`. The same script is in each slide's speaker notes, so Presenter View works as a teleprompter. Lines in [brackets] are actions, not spoken. Run times assume about 140 words a minute plus the live chart time.

## Decide before you record (3 calls, 1 minute)

1. **Option A daily limit.** v3 said Option A sits "inside the $200 early-session limit" and also "A gives you more attempts". With a $200 limit, one 3.5-4 point loss ($175-200) ends the day on A too, so A doesn't give more attempts. v4 keeps your $200 and says "A takes a smaller hit per loss" (Lesson 5.2, Module 5 slide 11). If you meant A's limit to be $400 (2 losses), change "Daily limit: $200" to "$400" on that slide and say "A gives you two attempts".
2. **3.5 or 4 points.** Your rule stays 3.5-4. The 10/4 test on 137 real CRT Pro trades: a fixed 4 pt stop / 4 pt target made +$2,105 on 2 ES; the same with a 3.5 pt stop lost $745. Thin data (3 days). If you want, say once in 5.3: "If you're unsure, use 4. 3.5 is the tightest you go."
3. **Runners on the POC exit.** 4.5 teaches your read: full exit or partial with a runner. The forward-test notes show signals giving back most of their best move (median 76-93%), and on the CRT + Divergence log a full exit at the first target beat the other exit rules (+4R vs 0R). Optional line for 4.5: "While you're learning, take the full exit at the POC. Partials come later, with screen time."

## Recording checklist

**Before you hit record**

- TradingView Essentials lapsed 10/5. The free plan limits indicators per chart. Open one chart now and check that Session Liquidity, your CRT indicator and Fixed Range Volume Profile all load together. If not, renew first or split them across two saved layouts.
- Hide anything personal: broker/account panel, P&L, order history, alerts list.
- If CRT Pro is on the chart, its SL line sits at the sweep wick (often 1-2 pts). The course teaches a 3.5-4 pt hard stop from entry. Hide the SL/TP lines, or point out the difference when you measure the stop (5.3 script has the line).
- Record at 1080p. Slides full screen. Zoom TradingView so candles and the price scale are readable, and use the dark theme so it matches the slides.
- Tools you'll use: Measure (Shift + drag), Fixed Range Volume Profile, Long/Short Position (shows the R on 5.4).

**Charts to set up (save each as a layout or tab, ES 30-minute unless noted)**

| Chart | What it shows | Used in |
|---|---|---|
| A | One recent full day, Session Liquidity on: Asia range, London sweeps it, New York goes after the untouched level | 4.1, 4.2 |
| B | Yesterday's session, ready to draw Fixed Range Volume Profile | 4.3 |
| C | Two real sweeps with the profile drawn: one through a low-volume gap, one into a high-volume node | 4.4 |
| D | Two POC setups: one where the POC was the target, one POC entry (reaction candle, stop, untaken session-high/low target) | 4.5 |
| E | One three-tool example: session liquidity target, CRT sweep, sweep through a low-volume gap, POC target | 4.6 |
| F | One recent setup for the checklist, sizing and stop measuring (can reuse D's entry) | 5.1, 5.2, 5.3 |
| G | One full trade, start to finish, inside 10 AM-12 PM ET, on your CRT entry chart plus the 30-minute profile | 5.4 |

**Order and screen-shares** (record each lesson as its own video)

| Lesson | Slides | Switch to TradingView at slide | Chart | Est. time |
|---|---|---|---|---|
| M4 intro + disclaimer | 1–3 | none | none | 1 min |
| 4.1 What Session Liquidity Means | 4–8 | 7 | A | 4 min |
| 4.2 Reading the Three Sessions | 9–12 | 11 | A | 4 min |
| 4.3 Fixed Range Volume Profile Basics | 13–18 | 17 | B | 4 min |
| 4.4 Using Volume to Confirm Zones | 19–23 | 22 | C | 5 min |
| 4.5 Using the POC as an Entry or Exit | 24–33 | 32 | D | 9 min |
| 4.6 Combining Both Tools with CRT | 34–37 | 36 | E | 5 min |
| M4 recap | 38 | none | none | 1 min |
| M5 intro + disclaimer | 1–3 | none | none | 1 min |
| 5.1 Pre-Trade Checklist | 4–8 | 7 | F | 5 min |
| 5.2 Position Sizing & Daily Risk Rules | 9–17 | 16 | F | 7 min |
| 5.3 Stop Placement | 18–23 | 22 | F | 4 min |
| 5.4 Full Worked Example | 24–28 | 27 | G | 8 min |
| M5 recap | 29 | none | none | 1 min |

Module 4 is about 33 minutes on camera, Module 5 about 26. Budget about 1.5x that for retakes and setup: roughly 90 minutes for both.

Put the M4 intro, disclaimer and lessons slide at the start of the 4.1 video (same for 5.1), and the recap at the end of 4.6 and 5.4. Or record them as a short separate intro video.

---

# MODULE 4: Session Liquidity & Volume Profile

## Intro (about 1 min)

**Slide 1 · TITLE · Session Liquidity & Volume Profile**

Welcome to Module 4. In Module 3 you learned the CRT setup. Now we answer two questions that make that setup better. Where is price headed? And does volume agree with the move? That's session liquidity and volume profile.

**Slide 2 · DISCLAIMER · Before We Start**

Quick note before we start. This is education, not financial advice. Futures can take money out of your account fast, and more than you planned if you trade without a stop. The chart examples are for teaching. Nothing I show you is a promise of what the next trade does. Only trade money you can afford to lose.

**Slide 3 · LESSONS · Module 4 Lessons**

Here's the plan. Six short lessons. 4.1 and 4.2 are session liquidity: where the orders sit. 4.3 and 4.4 are volume profile: where the trading happened. 4.5 is how I use the POC as an entry or an exit. And 4.6 puts all of it together with your CRT setup.

## 4.1: What Session Liquidity Means (about 4 min)

**Slide 4 · LESSON TITLE · 4.1: What Session Liquidity Means**

Lesson 4.1. What session liquidity means.

**Slide 5 · TELL · Three Sessions, Three Ranges**

Every trading session has its own high and its own low. Asia runs 7 PM to 2:59 AM Eastern. London runs 3 AM to 9:29. New York runs 9:30 AM to 3:59 PM. Three sessions, so six levels on your chart every day.

**Slide 6 · TELL · Sand at the Base of a Slide**

Here's why those levels matter. Stop-losses and pending orders cluster around them, like sand piling up at the base of a slide. That pile of orders is fuel. So I treat those highs and lows as targets. When price runs toward one, it's going where the orders are.

**Slide 7 · SCREEN-SHARE · Session Lines on a Live Chart**

*Screen-share, chart A. On screen: Turn on the Session Liquidity indicator; Point to each session's high and low; Show what price does with London's high once New York opens.*

Let me show you on a live chart. [Switch to TradingView.] This is the Session Liquidity indicator. This line is the Asia high, and this one is the Asia low. Here's London's high and low. Now New York opens at 9:30. Watch London's high. [Scroll forward.] See how price went after it? That's the liquidity resting there, and that's why I mark these lines every morning. [Switch back to the slides.]

**Slide 8 · DO · Your Turn: Lesson 4.1**

Your turn. Turn on your Session Liquidity indicator if you haven't yet. Screenshot your chart with all three sessions' lines showing. Post it.

## 4.2: Reading the Three Sessions (about 4 min)

**Slide 9 · LESSON TITLE · 4.2: Reading the Three Sessions**

Lesson 4.2. Reading the three sessions.

**Slide 10 · TELL · Sessions Hand Off to Each Other**

Same tool, more depth. In 4.1 you spotted the lines. Now we read how the sessions interact. Asia builds a range. London often sweeps that range. Then New York often goes after whichever session level hasn't been touched yet. Often, not always. That's why we watch it every day.

**Slide 11 · SCREEN-SHARE · One Full Day, Session by Session**

*Screen-share, chart A. On screen: Start at the Asia open and mark its range; Show London sweeping the Asia high or low; Show New York going after the untouched level.*

Let's walk one full day. [Switch to TradingView.] Here's the Asia open. Price builds this range overnight. Here's the high, here's the low. Now London opens at 3 AM. Watch what it does to the Asia range. [Scroll.] There's the sweep. Now which level is still sitting there untouched? This one. New York opens at 9:30, and here's price going after it. [Switch back.]

**Slide 12 · DO · Your Turn: Lesson 4.2**

Your turn. Track today's three session highs and lows on your chart. At the end of the day, post which one got swept first.

## 4.3: Fixed Range Volume Profile Basics (about 4 min)

**Slide 13 · LESSON TITLE · 4.3: Fixed Range Volume Profile Basics**

Lesson 4.3. Fixed Range Volume Profile basics.

**Slide 14 · TELL · A Different Question**

This tool answers a different question than price alone. Not where did price go. Where did the most trading happen. Price tells you the path. Volume profile tells you where buyers and sellers spent the most time agreeing.

**Slide 15 · TELL · Two Words to Know**

Two words to know. POC, the Point of Control, is the single price with the most volume. The value area is the zone around it holding about 70% of the volume. That's TradingView's default setting, so leave it there. And I draw this on the 30-minute chart. That's the timeframe for everything in this module.

**Slide 16 · EXAMPLE · What the Profile Looks Like**

Here's what it looks like. The bars on the right are volume at each price. The longest bar is the POC, in orange. The purple band marks the value area. On a normal session you get a fat middle and thin edges.

**Slide 17 · SCREEN-SHARE · Fixed Range Volume Profile, Live**

*Screen-share, chart B. On screen: 30-minute chart; Draw Fixed Range Volume Profile over a recent session; Point out the POC and the value area.*

Now on a live chart. [Switch to TradingView.] I'm on the 30-minute chart. I pick the Fixed Range Volume Profile tool, click the start of the session, and drag to the end. Here's the POC, the price with the most volume. Here's the value area. Fat middle, thin edges. That's a normal session. [Switch back.]

**Slide 18 · DO · Your Turn: Lesson 4.3**

Your turn. Apply Volume Profile to yesterday's session on your own 30-minute chart. Screenshot it and mark where the POC landed.

## 4.4: Using Volume to Confirm Zones (about 5 min)

**Slide 19 · LESSON TITLE · 4.4: Using Volume to Confirm Zones**

Lesson 4.4. Using volume to confirm zones.

**Slide 20 · TELL · High Volume vs. Low Volume**

High-volume areas mean price agrees it belongs there. It might pause there or reverse, and it's harder for a sweep to punch through cleanly. Low-volume gaps mean price moved through fast, without much disagreement. That's where I often see manipulation sweeps happen, because there's less resistance.

**Slide 21 · EXAMPLE · Volume Confirms the Sweep**

Here's the picture. On the left, the sweep goes through a low-volume gap. One wick through, then price reverses hard. Clean. On the right, the sweep goes into a high-volume node. Price chops around inside it, and the reversal is hard to read. Same sweep, different volume, different trade.

**Slide 22 · SCREEN-SHARE · Gap vs. Node on Real Sweeps**

*Screen-share, chart C. On screen: Sweep #1: through a low-volume gap (fast, clean); Sweep #2: into a high-volume node (choppy); Compare how each reversal looked.*

Let's look at two real sweeps. [Switch to TradingView.] Sweep one. Profile's drawn on the 30-minute chart. Look where the wick went: through this thin area, a low-volume gap. One push through and price snapped back. Now sweep two. This one ran into a high-volume node. Look at the chop. Three, four candles going nowhere before anything happened. That's the difference. [Switch back.]

**Slide 23 · DO · Your Turn: Lesson 4.4**

Your turn. Pull up your Module 3 CRT screenshot again. Overlay Volume Profile on it, drawn on the 30-minute chart. Post whether the sweep passed through high or low volume, and whether that changes how you'd read the setup.

## 4.5: Using the POC as an Entry or Exit (about 9 min)

**Slide 24 · LESSON TITLE · 4.5: Using the POC as an Entry or Exit**

Lesson 4.5. Using the POC as an entry or an exit.

**Slide 25 · TELL · One Line, Two Jobs**

In 4.4 we used volume to judge the sweep. Now I'm going to show you how I use one line off that profile, the POC, as my exit or my entry. This is how I trade it. It's not a law the market has to follow.

**Slide 26 · TELL · The POC as My Exit**

First, the POC as my exit. I draw the Fixed Range Volume Profile on the 30-minute chart, over the range I'm trading. After the sweep and my CRT entry, I manage the trade at the POC of that range, or a few ticks before it. Sometimes I take the full exit there. Sometimes I take a partial and let the rest run. Which one depends on how the candles move into the POC. That's a read, not a formula. You build the feel for it with screen time.

**Slide 27 · EXAMPLE · The POC as the Exit**

Here's the exit on a chart. The gray box is the range I profiled. Price sweeps under the range low, then reverses. Entry on the reversal, hard stop 3.5 to 4 points below it. And the target is the POC of that range, the orange line. That's where I expect price to slow down.

**Slide 28 · TELL · Where It's Headed vs. Where It Slows Down**

Why the POC? It's where the most trading happened in that range, so that's where I expect price to stall. Session liquidity tells me where price is headed. The POC tells me where it's likely to slow down on the way.

**Slide 29 · TELL · The POC as My Entry**

Second, the POC as my entry. When price leaves the range and comes back to the POC, I watch how it reacts there. I don't enter on the touch. I wait for a reaction candle at the POC. If it lines up with my CRT direction, I enter on that candle's close.

**Slide 30 · TELL · Your Stop and Target on a POC Entry**

Now your stop. I manage my own trades by hand, but that's me, not you. You use a hard stop of 3.5 to 4 points on ES. On a POC entry, that's 3.5 to 4 points from your entry, the close of the reaction candle. If you're a beginner, you don't take a trade without a stop. No exceptions. My target is the session high or the session low, whichever is the untaken liquidity in my trade direction. I exit at that line or within a point of it. We cover size and risk in detail in Module 5.

**Slide 31 · EXAMPLE · The POC as the Entry**

And here's the entry. Price leaves the range, then comes back to the POC. I don't enter on the touch. This candle wicks into the POC and closes back up. That's the reaction candle. Entry on its close. Hard stop 3.5 to 4 points below the entry. Target is the session high nobody's taken yet, up here.

**Slide 32 · SCREEN-SHARE · The POC on Real Setups**

*Screen-share, chart D. On screen: 30-minute chart: draw the profile over the range you trade; Setup #1: the POC as the target; Setup #2: the POC as the entry, with stop and target marked.*

Now on real charts. [Switch to TradingView.] 30-minute chart. I draw the profile over the range I'm trading, start to end. Here's the POC. Setup one: here's the sweep, here's my CRT entry, and the POC is my target. Look at how the candles slowed down coming into it. Setup two: price left the range, came back down to the POC, and printed this reaction candle. Entry on its close. Hard stop 3.5 to 4 points below. Target up here at the session high nobody's taken yet. [Switch back.]

**Slide 33 · DO · Your Turn: Lesson 4.5**

Your turn. On the 30-minute chart, draw Volume Profile on the range you're trading and mark the POC. Then pull up your Module 3 CRT screenshot and mark the POC on it. Was it your entry or your target? Post it with your entry, stop and target marked. One line doesn't make the trade. The POC has to fit the setup.

## 4.6: Combining Both Tools with CRT (about 5 min)

**Slide 34 · LESSON TITLE · 4.6: Combining Both Tools with CRT**

Lesson 4.6. Combining both tools with CRT.

**Slide 35 · TELL · 3 Tools, 1 Trade**

None of these tools work in isolation. Session liquidity tells you where price is headed. CRT gives you the sweep and the entry. Volume profile tells you if volume agrees, and where the POC sits. When all three agree, that's the trade. This lesson proves it out loud, one more time, on a live example.

**Slide 36 · SCREEN-SHARE · One Trade, All Three Tools**

*Screen-share, chart E. On screen: Mark the session liquidity target; Show the CRT sweep into it; Volume profile (30m): sweep through a low-volume gap, entry, POC as the target.*

[Switch to TradingView.] Step one, session liquidity. Which level is untaken? This one. That's where price is headed. Step two, CRT. Here's the sweep, right into that level. Step three, volume. Profile's on the 30-minute chart, and look: the sweep went through a low-volume gap. Clean. Here's the entry, and the POC is my target. Three tools, all saying the same thing. [Switch back.]

**Slide 37 · DO · Your Turn: Lesson 4.6**

Your turn. Find your own three-tool confluence example this week. Session liquidity, CRT and Volume Profile all agreeing, with the POC marked as your target. Post it whenever you spot one. No deadline.

## Recap (about 1 min)

**Slide 38 · RECAP · Module 4 in One Slide**

That's Module 4. Session highs and lows are where the orders sit. London often sweeps Asia, and New York often goes after the level nobody touched. The POC is the most-traded price, drawn on the 30-minute chart. Sweeps through low-volume gaps read cleaner. And the POC is your exit or your entry, with a 3.5 to 4 point hard stop every time. Next up, Module 5: putting it into one workflow, and the risk rules that keep you in the game.

---

# MODULE 5: Full Workflow & Risk Management

## Intro (about 1 min)

**Slide 1 · TITLE · Full Workflow & Risk Management**

Welcome to Module 5. You've got every tool now. This module turns them into one process you run the same way every time, and gives you the risk rules that keep you trading next month.

**Slide 2 · DISCLAIMER · Before We Start**

Same note as last module. This is education, not financial advice. Futures carry a real risk of loss. The dollar numbers in this module are examples of risk, not promises of profit. Only trade money you can afford to lose.

**Slide 3 · LESSONS · Module 5 Lessons**

Four lessons. 5.1 is the checklist you run before every trade. 5.2 is position size and your daily limits. 5.3 is where your stop goes. And 5.4 is one full trade, start to finish.

## 5.1: Pre-Trade Checklist (about 5 min)

**Slide 4 · LESSON TITLE · 5.1: Pre-Trade Checklist**

Lesson 5.1. The pre-trade checklist.

**Slide 5 · TELL · Glue This to Your Monitor**

This is the one thing I want glued to your monitor. Seven steps before any entry. One, confirm the AMD phase. Two, check the higher-timeframe daily bias. Three, confirm you're in your window. While you're learning, that's 10 AM to 12 PM Eastern. Four, identify the session liquidity targets. Five, check that volume profile agrees on the 30-minute chart, and mark the POC. Is it your entry or your target? Six, confirm CRT confluence. Seven, define your risk before entry.

**Slide 6 · TELL · Every Single Time**

Every single time. No skipping steps because you're excited. The day you skip one is the day you take the trade you shouldn't have.

**Slide 7 · SCREEN-SHARE · The Checklist on a Real Setup**

*Screen-share, chart F. On screen: Pick a recent setup; Run all 7 steps out loud; Check off each one as you go.*

Let's run it on a real setup. [Switch to TradingView.] Step one, AMD phase: [say the phase]. Step two, daily bias: [say it]. Step three, the time is [say it], inside the window. Step four, session liquidity: the untaken level is here. Step five, volume profile on the 30-minute: here's the POC, and it's my [entry or target]. Step six, CRT: here's the sweep and the confirmation. Step seven, risk: hard stop 3.5 to 4 points, here. Seven for seven. That's a trade I'm allowed to take. [Switch back.]

**Slide 8 · DO · Your Turn: Lesson 5.1**

Your turn. Print or save this checklist somewhere you'll see it before every trade. Post a photo of wherever you put it. Screen, wall, notebook, doesn't matter.

## 5.2: Position Sizing & Daily Risk Rules (about 7 min)

**Slide 9 · LESSON TITLE · 5.2: Position Sizing & Daily Risk Rules**

Lesson 5.2. Position sizing and daily risk rules.

**Slide 10 · TELL · The Sizing Formula**

Here's the math in plain terms. Decide how many dollars you're willing to risk on this one trade. Divide that by how many points your stop is from entry. Divide by 50 dollars, the ES point value. That's your number of contracts. So 200 dollars, divided by a 4 point stop, divided by 50, is 1 contract. That's the formula professional position sizing is built on.

**Slide 11 · TELL · Your Size While You Learn: Pick One**

But that's not what you'll use day to day while you're in this program. I'm giving you two options instead. Option A, 1 ES contract. Every point is 50 dollars. With the 3.5 to 4 point hard stop, one stopped trade is 175 to 200 dollars, inside a 200 dollar limit. Option B, 2 ES contracts. Every point is 100 dollars, and your daily limit goes up to 400. One stopped trade is 350 to 400 dollars, so that one loss ends your session. Here's the trade-off. A takes a smaller hit per loss. B makes bigger moves, and takes bigger losses. It's your choice.

**Slide 12 · TELL · Keep It Fixed**

Whichever you pick, keep it fixed, every trade. Stay with it until your account has grown 1.5 to 2 times your starting capital. Once you hit that milestone, you can size up, to a max of 4 contracts.

**Slide 13 · TELL · Know Your Number Before You Trade**

Know your number before you trade. On Option A, your hard stop risks 175 to 200 dollars per trade. On Option B, it's 350 to 400, and one loss ends your session. So do the quick math for your option. How many losing trades would it take to hit your daily limit? If you don't know that number before you start trading, you're flying blind. Once you can answer it without doing math in the moment, you're ready to size up, to a max of 4.

**Slide 14 · TELL · My Numbers, Not Yours**

Here are my numbers. I never risk more than 1,000 dollars total in a single day, and no more than 200 of that during the manipulation session, 3 to 9:29 AM, which I don't want you trading yet anyway. My daily goal is 1 or 2 good trades, then I'm done. These are my numbers, not yours. Set your own daily cap before you trade. In an eval, it's the firm's daily loss limit. And more trades isn't better. It usually means you stopped waiting for the real setup.

**Slide 15 · TELL · Your Daily Profit Goal (While Learning)**

While you're learning, set a daily profit goal. Two ways. A flat 400 dollars a day. Or personalize it. Take your hourly rate, multiply by 8, then multiply that by 2. So at 20 dollars an hour, 20 times 8 is 160, times 2 is 320. It's a reference number, not a quota. You still stop after 1 or 2 good trades.

**Slide 16 · SCREEN-SHARE · Sizing a Real Setup**

*Screen-share, chart F. On screen: Measure a 3.5–4 point hard stop on a real setup; Option A, 1 ES: $175–200 of risk; Option B, 2 ES: $350–400. One loss ends the session.*

[Switch to TradingView.] Here's a real setup. Entry here. Hard stop 3.5 to 4 points away, here. On Option A, 1 ES contract, that's 175 to 200 dollars of risk on this trade. On Option B, 2 ES contracts, it's 350 to 400, and if it stops out, my session's over. And here's my profit goal for the day next to it, so I know what done looks like. [Switch back.]

**Slide 17 · DO · Your Turn: Lesson 5.2**

Your turn. Three numbers, posted together. One: pick Option A or Option B, then use the 3.5 to 4 point hard stop on a real setup from your chart, and write your dollar risk on that trade. Two: write down your daily limit, then how many losers like that one it allows. Three: your daily profit goal, either 400 flat or your hourly rate times 8 times 2.

## 5.3: Stop Placement (about 4 min)

**Slide 18 · LESSON TITLE · 5.3: Stop Placement**

Lesson 5.3. Stop placement.

**Slide 19 · TELL · A Hard Stop, Every Setup**

Your stop is a hard stop, 3.5 to 4 points from your entry on ES. Every setup: the sweep entry and the POC entry. No exceptions.

**Slide 20 · TELL · What That Stop Costs**

Here's what that costs. On Option A, 1 contract, 175 to 200 dollars. On Option B, 2 contracts, 350 to 400 dollars. Plus commissions. Know this number before you click.

**Slide 21 · TELL · If Price Gets There, You're Out**

I manage my own trades by hand, but that's me, not you. You use the hard stop, and you never take a trade without one. If price gets there, your read on the setup was wrong, and you're out. No moving it. No hoping.

**Slide 22 · SCREEN-SHARE · Measuring the Hard Stop**

*Screen-share, chart F. On screen: Take a sweep entry; Measure 3.5–4 points from the entry and count it out loud; Show the dollar risk for Option A and Option B.*

[Switch to TradingView.] Here's a sweep entry. I'll use the measure tool from the entry and count the points: 1, 2, 3, 3 and a half, 4. That's 14 to 16 ticks. Stop goes here. On 1 contract that's 175 to 200 dollars. On 2 contracts, 350 to 400. [If the indicator draws its own stop line at the sweep wick, point out that it's a different line: in this course you measure 3.5 to 4 points from your entry.] [Switch back.]

**Slide 23 · DO · Your Turn: Lesson 5.3**

Your turn. On your CRT screenshot from Module 3, mark your entry and a 3.5 to 4 point hard stop from it. Post it with your dollar risk for your option, 1 or 2 ES contracts.

## 5.4: Full Worked Example (about 8 min)

**Slide 24 · LESSON TITLE · 5.4: Full Worked Example**

Lesson 5.4. The full worked example.

**Slide 25 · TELL · One Trade. Every Piece.**

One real trade, every piece of this curriculum, start to finish. The AMD read. The CRT entry. Session liquidity and volume confirmation. Position size. A 3.5 to 4 point hard stop. And the target. This is the lesson that proves it's one process, not five separate tools you're juggling.

**Slide 26 · TELL · Measure the Target in R**

The target is the top or the bottom of the range. Measure it in R against your stop. 1R is your stop distance, 3.5 to 4 points. So 2R is 7 to 8 points.

**Slide 27 · SCREEN-SHARE · One Trade, Start to Finish**

*Screen-share, chart G. On screen: AMD read, daily bias, time window; Session liquidity + CRT entry + volume profile; Position size, 3.5–4 pt hard stop, target measured in R.*

[Switch to TradingView.] One trade, start to finish. First the AMD read: [say the phase]. Daily bias: [say it]. Time: inside the 10 to 12 window. Session liquidity: the untaken level is here. That's where price is headed. Volume profile on the 30-minute: here's the POC. CRT: here's the sweep, and here's my entry. Size: [Option A or B], so my risk is [dollar amount]. Hard stop, 3.5 to 4 points, here. Target, the top of the range, here. That's [number] points, so about [number] R. Here's what price did. [Walk it forward to the exit, win or loss.] [Switch back.]

**Slide 28 · DO · Your Turn: Lesson 5.4**

Your turn, and this is your Module 5 capstone. Re-create this exact walkthrough on your own chart, using a setup from this week. Post the full breakdown, every step.

## Recap (about 1 min)

**Slide 29 · RECAP · Module 5 in One Slide**

That's Module 5. Run the checklist before every trade. 1 or 2 contracts, fixed, until your account grows 1.5 to 2 times. Know how many losers your daily limit allows. Hard stop, 3.5 to 4 points, every setup. And measure every target in R. One process, not five separate tools. Post your capstone, and I'll see you in the community.

---

## What changed from v3

- One idea per slide, text at 22-36 pt for 1080p, and a speaker-notes script on every slide.
- Every TradingView moment has its own dashed "SCREEN-SHARE: TRADINGVIEW" slide with the 3 things to show.
- New example charts with large labels; the 4.5 example is split into "POC as the exit" and "POC as the entry".
- Added: a risk disclaimer and a lessons slide at the start of each module, a recap slide at the end, a worked sizing example ($200 / 4 pts / $50 = 1 ES), and a stop-cost table that notes commissions.
- Same method and 10/1 decisions: POC lesson 4.5, 30-minute profile, 3.5-4 pt hard stop, 1 or 2 ES fixed, 10 AM-12 PM window, your $1,000 / $200 / 1-2 trades, $400 or hourly × 8 × 2 profit goal.
- One wording change for consistency: Option A is now "a smaller hit per loss" instead of "more attempts" (see Decide before you record #1).

Still open from v3: Lesson 3.2 Kill Zones teaches three windows. One line there ("while you're learning, 10 AM-12 PM is the one you'll use") would set up the Module 5 checklist.
