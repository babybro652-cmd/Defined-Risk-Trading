# Shorts cut of chase.mp4: card lengths match the AI voice segments in tts/durs.txt
import re
src=open("make_reels.py").read()
exec(src[:src.index('render("chase')])
d=[float(x) for x in open("tts/durs.txt").read().split(",")]
render("chase-short-base.mp4",[
 (card(None,"The candle already moved. Chasing it costs you."),d[0]),
 (card("THE ENTRY","Buy after a big push and you get the worst price of the move."),d[1]),
 (card("THE STOP","Under the whole candle is wide. Inside it is noise."),d[2]),
 (card("THE FIX","Let price come back to a level you marked."),d[3]),
 (card(None,"If it never comes back, the trade wasn't yours.","Define your risk. Wait for your setup."),d[4])])
