"""Wed 11/25 daily content (catch-up run, ~10 AM ET).
IG 12:30: holiday week, same risk numbers (plum palette).
FB 5 PM: son's first Thanksgiving, rules don't take the week off (slate palette).
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

PLUM = dict(bg_top=(46, 22, 56), bg_bot=(24, 10, 32), grid=(72, 44, 86), text=(246, 238, 250), muted=(196, 170, 210),
            accent=(250, 170, 120), up=(120, 214, 180), down=(240, 110, 130), panel=(30, 12, 40, 205))
SLATE = dict(bg_top=(232, 236, 240), bg_bot=(206, 214, 222), grid=(186, 196, 208), text=(30, 40, 54), muted=(90, 104, 122),
             accent=(196, 98, 40), up=(30, 140, 110), down=(196, 64, 64), panel=(250, 250, 252, 220))
P = PLUM; s = walk(13, 125, 0.0, 0.03)
ig = [scene(P, 4.4, s, None, "1 ES, 4 points, $200.", "A holiday week doesn't change that number.", start=5.0, hs=84),
      scene(P, 4.8, s, "HOLIDAY WEEK", "Volume often runs thinner.", "Price can jump between levels faster.", start=6.0),
      scene(P, 4.8, s, "MY STOP", "3.5 to 4 points from entry.", "On 1 ES: $175 to $200.", start=7.5),
      scene(P, 4.2, s, "MY TRADES", "1 to 2 good trades.", start=9.0),
      scene(P, 4.6, s, "MY DAILY MAX", "$1,000 of risk in a day.", start=10.5),
      scene(P, 4.4, walk(11, 126, 0.0, 0.05), None, "Same plan, any week.", "Define your risk. Wait for your setup.", start=7.0, hs=80)]
render("holiday-risk.mp4", ig)
P = SLATE; s = walk(13, 1125, 0.0, 0.04)
fb = [scene(P, 4.6, s, None, "7 months old. His first Thanksgiving is tomorrow.", start=5.0, hs=76),
      scene(P, 4.6, s, "THE JOB", "I trade around a full-time job.", "New York is my main session.", start=6.0),
      scene(P, 4.4, s, "THE REVIEW", "At night, once he's asleep.", start=7.5),
      scene(P, 5.2, s, "MY RULES DON'T TAKE THE WEEK OFF", "Stop: 3.5 to 4 points from entry.", "1 to 2 good trades. $1,000 daily max.", start=9.0, ls=36),
      scene(P, 4.4, s, None, "No setup, no trade.", "More time at the table.", start=10.5, hs=80),
      scene(P, 4.0, walk(11, 1126, 0.0, 0.05), None, "Define your risk. Wait for your setup.", start=7.0, hs=76)]
render("first-thanksgiving.mp4", fb)
