"""Thu 11/19 daily content. IG 12:30 PM: size an ES trade from the stop in 3 steps (light chart palette).
Chart-first: frame 0 = drawn chart already printing, hook text on screen from frame 0. No prices/dates on the chart.
Reuses the drawing helpers from posts/media/2026-11-18-daily/make_reels.py (copied into _base.py).
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())
P = LIGHT
trend = walk(13, 31, -1.0, 0.1)
ig = []
ig.append(scene(P, 4.6, trend, None, "Size an ES trade in 3 steps, before you click.", start=5.0))
ig.append(scene(P, 5.4, trend, "STEP 1", "Stop distance in points, from entry.", "Example: 4 points.", start=6.0, ls=60))
ig.append(scene(P, 5.6, trend, "STEP 2", "Points x $50 = risk per ES contract.", "4 x $50 = $200. On MES, $5 a point: 4 x $5 = $20.", start=7.5, ls=60))
ig.append(scene(P, 5.6, trend, "STEP 3", "Risk you'll accept on the trade, divided by that number.", "$400 / $200 = 2 ES. Same $400 = 20 MES.", start=9.0, ls=60, hs=68))
ig.append(scene(P, 4.4, walk(11, 9, 0.0, 0.05), None, "Contracts come from the stop. Not the other way around.", "Define your risk. Wait for your setup.", start=7.0))
render("size-from-stop.mp4", ig)
