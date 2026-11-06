import sys, os, wave
sys.path.insert(0,'/home/user/Defined-Risk-Trading/drt/audio')
import add_audio as A
parts=["ES trades nearly 24 hours a day. Here's the session map, in Eastern time.",
"Asia runs from 6 PM to about 3 AM.",
"London runs from 3 AM to 9:30 AM.",
"New York, the regular session, runs from 9:30 AM to 4 PM. That's my focus.",
"Every day there's a 1 hour break, from 5 to 6 PM. The week runs Sunday 6 PM to Friday 5 PM.",
"Each session can set its own high and low. Know which one you're trading in.",
"Define your risk. Wait for your setup."]
os.makedirs('tts',exist_ok=True)
for i,p in enumerate(parts):
    f=A.tts(p,f'tts/p{i}.wav',0.9)
    w=wave.open(f'tts/p{i}.wav'); print(i, round(w.getnframes()/w.getframerate(),2))
open('sessions-short-script.txt','w').write(" ".join(parts))
