"""Sun 11/22 daily content.
IG 12:30: daily max loss, set before the first trade (forest palette).
FB 5 PM reuses the 11/21 weekend-gap card (already has music).
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

FOREST = dict(bg_top=(16, 44, 40), bg_bot=(8, 26, 24), grid=(34, 70, 64), text=(238, 246, 242), muted=(160, 196, 186),
              accent=(240, 196, 92), up=(92, 210, 160), down=(232, 104, 96), panel=(10, 32, 30, 205))
P = FOREST
s = walk(13, 91, 0.0, 0.04)
ig = []
ig.append(scene(P, 4.6, s, None, "ES traders: set your daily max before the first trade.", start=5.0, hs=70))
ig.append(scene(P, 4.8, s, "MY STOP", "3.5 to 4 points from entry.", "On 1 ES: $175 to $200.", start=6.0))
ig.append(scene(P, 4.6, s, "MY TRADES", "1 to 2 good trades, then done.", start=7.5))
ig.append(scene(P, 5.4, s, "MY DAILY MAX", "$1,000 of risk in a day.", "A 3rd trade is fine if the day stays under it.", start=9.0))
ig.append(scene(P, 4.8, s, "WHEN", "Pick it while you're calm.", "Not after a loss.", start=10.5))
ig.append(scene(P, 4.2, walk(11, 93, 0.0, 0.05), None, "The max is the line. Not the trade count.", "Define your risk. Wait for your setup.", start=7.0, hs=70))
render("daily-max.mp4", ig)
