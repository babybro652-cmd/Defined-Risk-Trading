"""Mon 11/23 daily content, TikTok reset day 6.
TT 7 AM: ES overnight high and low (6:00 PM ET to 9:30 AM ET), 2 lines before the NY open. Navy/teal reset palette.
Chart-first: frame 0 = drawn chart already printing, hook text on screen from frame 0. No prices/dates on the chart.
Usage: python3 make_reels.py"""
exec(open(__file__.replace("make_reels.py", "_base.py")).read())

def scene2(P, dur, seq, label, head, sub=None, lines=(), start=4.0, y_mid=1230, unit=55, hs=74, ls=40):
    n = int(dur * FPS); end = len(seq); base = background(P)
    for k in range(n):
        prog = min(end, start + (end - start) * min(1.0, k / (n * 0.8)) + 0.35)
        im = base.copy(); d = ImageDraw.Draw(im)
        for v, lab, col in lines:
            y = int(y_mid - v * unit)
            for x in range(60, W - 60, 40): d.line([x, y, x + 22, y], fill=P[col], width=4)
            f = font(B, 32); d.text((W - 60 - d.textlength(lab, font=f), y - 48 if "HIGH" in lab else y + 12), lab, font=f, fill=P[col])
        draw_candles(d, P, seq, prog, y_mid, unit)
        text_panel(im, P, label, head, sub, hs, ls)
        handle(ImageDraw.Draw(im), P)
        yield np.asarray(im)

P = NAVY
on = walk(14, 123, 0.0, 0.0)
hi = max(c[1] for c in on); lo = min(c[2] for c in on)
LN = [(hi, "OVERNIGHT HIGH", "accent"), (lo, "OVERNIGHT LOW", "down")]
tt = []
tt.append(scene2(P, 4.4, on, None, "2 lines on ES before 9:30: the overnight high and low.", start=5.0, lines=LN, hs=70))
tt.append(scene2(P, 5.0, on, "THE WINDOW", "Overnight on ES runs from 6:00 PM ET", "to the 9:30 AM ET New York open.", start=6.0, lines=LN))
tt.append(scene2(P, 5.0, on, "THE HIGH", "Find the highest price in that window.", "Draw a line across it.", start=7.0, lines=LN[:1] + LN[1:]))
tt.append(scene2(P, 5.0, on, "THE LOW", "Same for the lowest price.", "Now you know the range price built overnight.", start=8.0, lines=LN))
tt.append(scene2(P, 5.0, on, "AT THE OPEN", "Watch where New York opens:", "inside the range, above it, or below it.", start=9.0, lines=LN))
tt.append(scene2(P, 4.0, on, None, "Mark the levels before the first candle.", "Define your risk. Wait for your setup.", start=11.0, lines=LN))
render("overnight-range.mp4", tt)
