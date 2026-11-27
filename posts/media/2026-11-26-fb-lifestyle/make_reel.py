"""Thu 11/26 FB lifestyle reel: the market humbled me and I kept showing up (ember palette).
Usage: python3 make_reel.py"""
exec(open(__file__.replace("make_reel.py", "_base.py")).read())
EMBER = dict(bg_top=(44, 28, 20), bg_bot=(20, 12, 8), grid=(70, 50, 38), text=(248, 238, 226), muted=(206, 182, 160),
             accent=(236, 150, 72), up=(118, 196, 150), down=(226, 96, 84), panel=(30, 18, 12, 210))
P = EMBER; s = walk(13, 2611, 0.0, -0.02)
fb = [scene(P, 4.4, s, None, "I've read the market wrong more than once this month.", start=5.0, hs=72),
      scene(P, 4.6, s, "THE STOP", "3.5 to 4 points from entry.", "Then the trade is over.", start=6.0),
      scene(P, 4.6, s, "THE NEXT MOVE", "Back to the chart.", "Wait for my setup to show again.", start=7.5),
      scene(P, 4.6, s, "THE REVIEW", "Every trade, at night after work.", "The green ones and the red ones.", start=9.0),
      scene(P, 4.4, walk(11, 2612, 0.0, 0.05), None, "Showing up after a bad day is the skill nobody claps for.", start=6.0, hs=70),
      scene(P, 4.0, walk(11, 2612, 0.0, 0.05), None, "Define your risk. Wait for your setup.", start=8.0, hs=76)]
render("humbled.mp4", fb)
