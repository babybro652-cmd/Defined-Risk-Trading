import json
c = {}
c["tt_new"] = "ES weekend gap check, 10 seconds: mark Friday's close before Sunday 6 PM ET. Open above it = gap up. Below = gap down. Your guess: up, down, or flat?"
c["ig_new"] = """4 points of risk, 8 points of target: on ES you can lose 2 out of 3 trades and still break even.

The math on 1 ES contract:
Stop: 4 points = $200.
Target: 8 points = $400.
3 trades, 1 winner, 2 losers: +$400, -$200, -$200 = $0.

Flip it to 2 winners and 1 loser and the same 3 trades finish +$600.

That's before fees and slippage, which push the break-even win rate a little higher. Shrink the target to 4 points on the same stop and you need to be right more than half the time once fees come in.

What's your usual target on a 4 point stop: 4, 8, or 12 points?"""
c["fb_new"] = """Working a full-time job and trading ES? My trading window has a hard end time, and the chart doesn't set it.

I work 6:00 AM to 4:30 PM at a distribution center. Some days I trade on my lunch break, around 10 AM. When the break ends, the phone goes away, because no phones are permitted on the floor.

That clock forces the plan to be finished before I look. The stop is decided before I click: 3.5 to 4 points from entry. If my setup doesn't confirm while I'm on break, there's no trade. The full review waits until night, after my son is asleep.

A short window can feel like a handicap. For me it's a guardrail on screen time.

When does your trading day end: at a set time, at a set loss, or when you feel done?"""
old = {
"tt_1115": "Lunch break over, ES trade still open. Phones aren't allowed on the floor at work, so it gets closed. Some days price hits my target without me.",
"fb_1115": "My son goes to bed, and then the ES chart comes back out. Monday to Friday belongs to my full-time job, so my trade review happens at night. It's short and it looks the same every time: the levels I marked, the trades I took, the setups I skipped. Then I ask myself if I followed my rules.",
"fb_1118": "Set your ES day in 3 numbers before you look for a trade. Here are mine. 1 to 2: good trades, then I'm done. 3.5 to 4: the gap in points between my entry and my hard stop. On 1 ES, 4 points is $200. $1,000: the most I'll risk in a day. I work a full-time job and trade around it. With the numbers fixed ahead of time, there's no risk decision left to make in the middle of a trade.",
"ig_1114": "$2,000 of drawdown sounds like room. Do the math on a 4 point ES stop first. ES moves $50 a point, so 4 points is $200 per contract. 2 ES: $400 a stop. 5 full losses and the limit is gone. 1 ES: $200 a stop. 10 losses. Same stop, same setup. Numbers are before fees and slippage, and every firm writes its drawdown rules a little differently, so read yours.",
"fb_1114": "Quick math for anyone working a prop firm evaluation with a $2,000 drawdown limit. On ES, 4 points of stop costs $200 per contract. That math leaves out fees and slippage.",
"ig_1119": "Size an ES trade in 3 steps, before you click. 1. Measure your stop in points from entry. Say 4. 2. Multiply by $50. That's the risk on 1 ES contract: $200. MES moves $5 a point, so the same stop costs $20. 3. Divide the risk you'll accept on the trade by that number. $400 / $200 = 2 ES. The stop sets the contract count.",
"fb_1116": "My hard stop sits 3.5 to 4 points from entry. I decide it before I click. Moving it once it's under pressure doesn't save the trade.",
"ig_1120": "ES traders: price moves 23 hours a day. New York's 6.5 hours are my main session. ES trades on Globex, CME's electronic platform, from Sunday 6 PM to Friday 5 PM ET, with a 1-hour pause from 5:00 to 6:00 PM each day.",
"fb_1119": "My ES trades all carry a hard stop 3.5 to 4 points from my entry, and I set my daily max before the session opens. I've got a full-time job, and the trading fits around it.",
"ig_1117": "Long ES, hard stop 3.5 to 4 points under my entry. On 1 ES, 3.5 points is $175 and 4 points is $200.",
"ig_1118": "That night, after my son's bedtime, my review comes down to one question: did I follow my rules?",
"tt_1120": "5 days, 1 rule on ES: no early entries. Week 1 ends today. The setup confirms, then I enter. Did you wait this week: always, mostly, or never?",
}
c.update(old)
json.dump(c, open("caps.json","w"))
import re
for k in ["tt_new","ig_new","fb_new"]:
    t=c[k]; print(k, len(t), "emdash" if "—" in t else "", [w for w in ["actually","really","just","simply","truly","genuinely","link in bio","save this","follow for","comment below","tag "] if w in t.lower()], t.strip().endswith("?"))
