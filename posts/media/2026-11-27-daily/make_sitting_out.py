"""Fri 11/27 (Black Friday) 'not trading today' card (Tim's request via Jarvis, 11/26 10:15 PM). TikTok/IG/FB.
Graphite + amber palette, chart printing at frame 0, no close time stated (CME's own schedule couldn't be reached).
Usage: python3 make_sitting_out.py"""
exec(open("_base.py").read())
GRAPHITE = dict(bg_top=(34, 36, 44), bg_bot=(16, 17, 22), grid=(56, 60, 72), text=(244, 244, 248), muted=(176, 180, 196),
                accent=(246, 186, 64), up=(120, 196, 236), down=(232, 112, 120), panel=(22, 24, 30, 215))
P = GRAPHITE; s = walk(13, 1127, 0.0, 0.0)
sc = [scene(P, 3.4, s, None, "No ES trades for me today.", start=5.0, hs=84),
      scene(P, 3.6, s, "WHY", "The market closes early today.", "Holiday schedule, the day after Thanksgiving.", start=6.5),
      scene(P, 3.8, s, "VOLUME", "A short session tends to mean thin volume.", "Fewer orders behind each price.", start=8.0),
      scene(P, 3.6, s, "MY PLAN", "I'm sitting out and watching.", start=9.5),
      scene(P, 3.6, s, None, "Define your risk. Wait for your setup.", start=11.0, hs=80)]
render("sitting-out.mp4", sc)
