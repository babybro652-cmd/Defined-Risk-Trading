import sys, os, wave
sys.path.insert(0,'/home/user/Defined-Risk-Trading/drt/audio')
import add_audio as A
parts=["Here are 4 things to do before the trading week starts.",
"First, check the calendar for scheduled news. Big reports can move ES fast, so know the day and the time.",
"Second, write your risk limits for the week. Your stop size, your max loss per day, and your max trades per day.",
"Third, read last week's journal. The rule you broke the most is this week's focus.",
"Fourth, pick your trading window. Decide your session and your hours before Monday.",
"Define your risk. Wait for your setup."]
d='/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/tts'; os.makedirs(d,exist_ok=True)
for i,p in enumerate(parts):
    A.tts(p,f'{d}/p{i}.wav',0.9)
    w=wave.open(f'{d}/p{i}.wav'); print(i, round(w.getnframes()/w.getframerate(),2))
open('weekly-prep-short-script.txt','w').write(" ".join(parts))
