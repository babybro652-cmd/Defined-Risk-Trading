"""Fri 11/20 daily content, TikTok reset day 3.
TT 7 AM: "One rule, one week" week 1 close (no early entries), navy/teal reset palette. No result claims (no footage from Tim).
IG 12:30: ES session map, Asia / London / New York in ET (light palette).
Chart-first: frame 0 = drawn chart already printing, hook text on screen from frame 0. No prices/dates on the chart.
Reuses posts/media/2026-11-18-daily/make_reels.py helpers (copied into _base.py).
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

# ---- TikTok 7 AM: week 1 close, no early entries (navy) ----
P = NAVY
build = walk(12, 41, -1.2, 0.08)
tt = []
tt.append(scene(P, 4.6, build, None, "5 days. 1 rule. No early entries on ES.", start=4.0))
tt.append(scene(P, 5.2, build, "THE RULE", "The setup confirms first. Then I enter.", "Almost done doesn't count.", start=6.0))
tt.append(scene(P, 5.2, build, "EVERY NIGHT", "One review question: did my entry wait for the confirmation?", start=8.0, hs=68))
tt.append(scene(P, 4.6, build, "WEEK 1", "Closes today.", "Hard stop 3.5-4 pts from entry, every time.", start=10.0))
tt.append(scene(P, 4.0, walk(11, 13, 0.0, 0.05), None, "Wait for it to confirm.", "Define your risk. Wait for your setup.", start=7.0))
render("week1-close.mp4", tt)

# ---- IG 12:30: ES session map (light) ----
P = LIGHT
day = walk(13, 52, 0.0, 0.04)
ig = []
ig.append(scene(P, 4.6, day, None, "ES traders: 3 sessions, 1 trading day. Know which one you're in.", start=5.0, hs=68))
ig.append(scene(P, 5.0, day, "ASIA", "6:00 PM to 3:00 AM ET", "The trading day opens here.", start=6.0, ls=60))
ig.append(scene(P, 5.0, day, "LONDON", "3:00 AM to 9:30 AM ET", "Overnight trading, before the cash open.", start=7.5, ls=60))
ig.append(scene(P, 5.2, day, "NEW YORK", "9:30 AM to 4:00 PM ET", "Regular trading hours. My main session, but I always watch for my setup.", start=9.0, ls=60))
ig.append(scene(P, 5.0, day, "THE BREAK", "5:00 to 6:00 PM ET, daily.", "Globex is the platform, not a session.", start=10.5, ls=60))
ig.append(scene(P, 4.2, walk(11, 17, 0.0, 0.05), None, "Know the session before the setup.", "Define your risk. Wait for your setup.", start=7.0))
render("session-map.mp4", ig)
