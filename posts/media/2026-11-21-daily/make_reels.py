"""Sat 11/21 daily content, TikTok reset day 4.
TT 7 AM: the ES weekend gap (Fri 5 PM ET stop, Sun 6 PM ET reopen; mark Friday's close), navy/teal reset palette.
IG 12:30: 4 pt stop / 8 pt target break-even math (light palette).
FB 5 PM: full-time job, lunch-break window with a hard end (slate palette).
Chart-first: frame 0 = drawn chart already printing, hook text on screen from frame 0. No prices/dates on the chart.
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

SLATE = dict(bg_top=(34, 40, 52), bg_bot=(20, 24, 33), grid=(54, 62, 78), text=(240, 242, 246), muted=(168, 176, 192),
             accent=(242, 160, 64), up=(92, 200, 140), down=(230, 96, 96), panel=(24, 28, 38, 205))

# ---- TikTok 7 AM: weekend gap (navy) ----
P = NAVY
pre = walk(7, 21, -0.5, 0.05)
fri_close = pre[-1][3]
post = [(o + 4.5, h + 4.5, l + 4.5, c + 4.5) for (o, h, l, c) in walk(5, 22, fri_close, 0.0)]
gap = pre + post
LN = (fri_close, "FRIDAY CLOSE")
tt = []
tt.append(scene(P, 4.4, gap, None, "1 line before Sunday 6 PM ET: Friday's ES close.", start=5.0, line=LN))
tt.append(scene(P, 5.0, gap, "THE WEEKEND", "ES stops Friday at 5:00 PM ET.", "It reopens Sunday at 6:00 PM ET.", start=6.0, line=LN))
tt.append(scene(P, 5.2, gap, "THE GAP", "News can land while it's closed.", "So Sunday can open above or below Friday's close.", start=7.0, line=LN))
tt.append(scene(P, 5.2, gap, "THE LINE", "Mark Friday's close before the open.", "Opens above it: gap up. Below it: gap down.", start=8.0, line=LN))
tt.append(scene(P, 4.0, gap, None, "Know the gap before the first candle.", "Define your risk. Wait for your setup.", start=11.0, line=LN))
render("weekend-gap.mp4", tt)

# ---- IG 12:30: 4 pt stop / 8 pt target math (light) ----
P = LIGHT
rr = walk(13, 61, 0.0, 0.06)
ig = []
ig.append(scene(P, 4.6, rr, None, "4 pt stop. 8 pt target. Lose 2 of 3 and break even.", start=5.0, hs=70))
ig.append(scene(P, 4.6, rr, "THE STOP", "4 points on 1 ES = $200.", start=6.0))
ig.append(scene(P, 4.6, rr, "THE TARGET", "8 points on 1 ES = $400.", start=7.5))
ig.append(scene(P, 5.4, rr, "3 TRADES", "1 win, 2 losses: +$400, -$200, -$200 = $0.", "Before fees and slippage.", start=9.0))
ig.append(scene(P, 5.0, rr, "2 WINS, 1 LOSS", "+$800, -$200 = +$600.", "Same stop. Same target.", start=10.5))
ig.append(scene(P, 4.2, walk(11, 63, 0.0, 0.05), None, "Your target decides how often you need to be right.", "Define your risk. Wait for your setup.", start=7.0, hs=68))
render("stop-target-math.mp4", ig)

# ---- FB 5 PM: full-time job, lunch window (slate) ----
P = SLATE
job = walk(13, 77, 0.0, 0.03)
fb = []
fb.append(scene(P, 4.6, job, None, "Full-time job. ES trader. My window has a hard end time.", start=5.0, hs=70))
fb.append(scene(P, 4.6, job, "THE JOB", "6:00 AM to 4:30 PM, Monday to Friday.", start=6.0))
fb.append(scene(P, 4.6, job, "THE WINDOW", "Some days I trade at lunch, around 10 AM.", start=7.0))
fb.append(scene(P, 5.0, job, "THE HARD END", "Break ends, phone goes away.", "Phones aren't allowed on the floor.", start=8.0))
fb.append(scene(P, 5.0, job, "THE PLAN", "Stop decided before I click: 3.5-4 pts from entry.", start=9.5, hs=70))
fb.append(scene(P, 4.6, job, "AT NIGHT", "The review, after my son is asleep.", start=11.0))
fb.append(scene(P, 4.2, walk(11, 79, 0.0, 0.05), None, "A short window keeps the plan tight.", "Define your risk. Wait for your setup.", start=7.0))
render("lunch-window.mp4", fb)
