"""Thu 11/26 daily content (5:02 AM routine).
TT 7 AM: ES equal highs, audience callout. Light palette (new week look, light chart bg, navy text).
IG 12:30: Thanksgiving, 3 checks before any ES trade (speed how-to). Sage palette.
Chart-first: frame 0 = chart already printing, hook on screen from frame 0. No prices or dates.
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

# two highs at the same level (+4.0), pullback between, third push back to the level
eq = [(0,0.8,-0.4,0.6),(0.6,1.6,0.4,1.4),(1.4,2.6,1.2,2.4),(2.4,4.0,2.2,3.5),(3.5,3.7,2.2,2.5),(2.5,2.8,1.4,1.7),
      (1.7,2.6,1.5,2.4),(2.4,3.6,2.2,3.4),(3.4,4.0,3.0,3.3),(3.3,3.5,2.0,2.3),(2.3,2.6,1.2,1.5),(1.5,2.8,1.3,2.6),(2.6,3.9,2.4,3.7)]
P = LIGHT
tt = [scene(P, 4.0, eq, None, "ES traders: 2 highs at the same price.", "Mark them before you trade.", line=(4.0, "EQUAL HIGHS"), start=5.0, hs=80),
      scene(P, 4.6, eq, "WHY MARK THEM", "Price can come back to test that level.", "It can push through or turn away.", line=(4.0, "EQUAL HIGHS"), start=7.0),
      scene(P, 4.2, eq, "MY ENTRY", "I wait for my setup to confirm.", "No early entry.", line=(4.0, "EQUAL HIGHS"), start=9.0),
      scene(P, 4.2, eq, "MY STOP", "3.5 to 4 points from entry.", line=(4.0, "EQUAL HIGHS"), start=11.0),
      scene(P, 4.0, eq, None, "Mark the level. Wait for your setup.", line=(4.0, "EQUAL HIGHS"), start=12.0, hs=80)]
render("equal-highs.mp4", tt)

SAGE = dict(bg_top=(28, 48, 40), bg_bot=(14, 28, 22), grid=(50, 76, 64), text=(240, 246, 238), muted=(180, 204, 188),
            accent=(232, 196, 110), up=(130, 210, 160), down=(232, 112, 104), panel=(16, 34, 26, 205))
P = SAGE; s = walk(13, 1126, 0.0, 0.03)
ig = [scene(P, 4.4, s, None, "Holiday or not: 3 checks before any ES trade.", start=5.0, hs=80),
      scene(P, 4.8, s, "CHECK 1", "Look up CME's holiday hours.", "Thanksgiving runs on a holiday schedule.", start=6.0),
      scene(P, 4.6, s, "CHECK 2", "Is my setup there?", "No setup, no trade.", start=7.5),
      scene(P, 4.6, s, "CHECK 3", "Stop 3.5 to 4 points from entry.", "$1,000 max risk for the day.", start=9.0),
      scene(P, 4.4, s, None, "A 0-trade day still counts.", "Define your risk. Wait for your setup.", start=10.5, hs=80)]
render("holiday-checks.mp4", ig)
