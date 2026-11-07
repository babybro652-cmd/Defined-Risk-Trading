import sys, os, wave
sys.path.insert(0,'/home/user/Defined-Risk-Trading/drt/audio')
import add_audio as A
parts=["A mental stop is not a stop.",
"You tell yourself you'll get out when price hits your number.",
"But in a fast move on ES, price can run past that number before you click.",
"So put a hard stop in the platform before you enter. Even a stop order can fill a little worse in a fast market.",
"Then size for the slip, not the perfect fill. Plan as if the exit comes in worse than your level.",
"Define your risk. Wait for your setup."]
os.makedirs('/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/tts',exist_ok=True)
for i,p in enumerate(parts):
    f=A.tts(p,f'/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/tts/p{i}.wav',0.9)
    w=wave.open(f'/tmp/claude-0/-home-user-Defined-Risk-Trading/05c24c70-3eb0-5846-be76-141b208fd758/scratchpad/tts/p{i}.wav'); print(i, round(w.getnframes()/w.getframerate(),2))
open('mental-stop-short-script.txt','w').write(" ".join(parts))
