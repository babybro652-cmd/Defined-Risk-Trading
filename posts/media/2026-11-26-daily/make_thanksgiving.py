"""Thu 11/26 Happy Thanksgiving card (Tim's request via Jarvis). TikTok/IG/FB. Warm autumn palette, chart printing at frame 0.
No baby, no son mention, no hours stated beyond 'short holiday session'. Usage: python3 make_thanksgiving.py"""
exec(open("_base.py").read())
AUTUMN = dict(bg_top=(58, 30, 18), bg_bot=(30, 14, 8), grid=(84, 50, 34), text=(252, 242, 228), muted=(226, 196, 164),
              accent=(240, 150, 60), up=(150, 200, 120), down=(226, 104, 80), panel=(40, 18, 10, 210))
P = AUTUMN; s = walk(13, 2611, 0.0, 0.05)
tg = [scene(P, 3.6, s, None, "Happy Thanksgiving from Defined Risk Trading.", start=5.0, hs=80),
      scene(P, 3.6, s, "GRATEFUL", "For everyone who trades with a plan.", start=6.5),
      scene(P, 3.6, s, "TODAY", "Family at the table first.", start=8.0),
      scene(P, 3.8, s, "THE MARKET", "ES runs a short holiday session today.", "Thin market. Same rules.", start=9.5),
      scene(P, 3.6, s, None, "Define your risk. Enjoy your people.", start=11.0, hs=80)]
render("thanksgiving.mp4", tg)
