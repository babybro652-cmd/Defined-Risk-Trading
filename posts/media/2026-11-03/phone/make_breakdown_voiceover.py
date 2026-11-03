"""Voiceover track + caption timings for the 11/3/2026 captioned ES short breakdown (Tim 11/3: "First delete music
from video and do a voiceover"). Local Piper voice en_US-norman-medium (same setup as the education Shorts, via
drt/audio/add_audio.py tts()). Each spoken unit starts at its action anchor (or 0.6 s after the previous unit ends,
whichever is later); the fill line starts on the fill marker (65.1 s). Units that span two caption cards switch the
card on the first word of the second card, using faster-whisper word timestamps.
Writes OUT_DIR/voice.wav (48 kHz stereo, -16 LUFS) and OUT_DIR/timing.json for make_breakdown_captions.py --timing.
Usage: /usr/bin/python3 make_breakdown_voiceover.py OUT_DIR"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../drt/audio"))
import add_audio as A

FILL_T = 65.1   # "2 @ 7597.75" fill marker appears
GAP = 0.6       # silence between spoken units
TAIL = 0.5      # caption stays up after its speech ends
END_PAD = 1.6   # hold after the last word
# (spoken text, anchor s, caption cards, word index where each extra card starts)
UNITS = [
    ("Four points of risk. Sixteen points of reward.", 0.3, [["Four points of risk.", "Sixteen points of reward."]], []),
    ("Here's how I think about a trade like this.", 2.8, [["Here's how I think", "about a trade like this."]], []),
    ("Before I enter, I want to know where price sits in the bigger picture.", 6.0,
     [["Before I enter,", "I want to know"], ["where price sits", "in the bigger picture."]], [7]),
    ("Price pushed into an area I had marked, and started to stall.", 12.2,
     [["Price pushed into", "an area I had marked"], ["and started to stall."]], [8]),
    ("I don't short because price looks high.", 18.4, [["I don't short because", "price looks high."]], []),
    ("I wait for my confirmation.", 21.2, [["I wait for", "my confirmation."]], []),
    ("When I got it, I sold two contracts at seventy-six fourteen.", 24.4,
     [["When I got it, I sold", "2 contracts at 7,614."]], []),
    ("Risk comes first.", 28.2, [["Risk comes first."]], []),
    ("Stop four points above, where the idea is wrong.", 30.4, [["Stop 4 points above,", "where the idea is wrong."]], []),
    ("Target sixteen points lower, the next area I expected.", 33.4,
     [["Target 16 points lower,", "the next area I expected."]], []),
    ("That's one to four, risk to reward.", 37.2, [["That's 1 to 4,", "risk to reward."]], []),
    ("I set the bracket and let it work.", 39.8, [["I set the bracket", "and let it work."]], []),
    ("No moving the stop.", 44.0, [["No moving the stop."]], []),
    ("No grabbing a few points erly.", 46.4,  # "erly": Piper slurs "early" (heard as "Berlin")
     [["No grabbing", "a few points early."]], []),
    ("The plan was set before the trade, so there was nothing to decide.", 53.0,
     [["The plan was set", "before the trade,"], ["so there was", "nothing to decide."]], [7]),
    ("Target filled. Plus sixteen and a quarter points a contract. Paper.", FILL_T,
     [["Target filled.", "+16.25 pts a contract. Paper."]], []),
    ("Pick your spot. Define your risk.", 0, [["Pick your spot.", "Define your risk."]], []),
    ("Let it work.", 0, [["Let it work."]], []),
    ("Full process in the Skool. Link in bio.", 0, [["Full process in the Skool.", "Link in bio."]], []),
]


def trim(x, thr=1e-3):
    idx = np.where(np.abs(x).max(axis=1) > thr)[0]
    return x[max(idx[0] - 240, 0): idx[-1] + 2400] if len(idx) else x


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    clips, t, units = [], 0.0, []
    for i, (text, anchor, cards, splits) in enumerate(UNITS):
        w = A.tts(text, os.path.join(out, f"u{i:02d}.wav"))
        x = trim(A.decode(w))
        start = max(anchor, t)
        dur = len(x) / A.SR
        bounds = [start]
        if splits:
            words = A.whisper_words(A.to16k(x))
            for k in splits:
                bounds.append(start + float(words[k][0]) - 0.05)
        units.append((start, start + dur, cards, bounds)); clips.append((start, x))
        t = max(start + dur + GAP, start + 1.8)
    end = units[-1][1] + END_PAD
    n = int(round(end * A.SR))
    v = np.zeros((n, 2), np.float32)
    for s, x in clips:
        o = int(s * A.SR); v[o:o + len(x)] += x[: n - o]
    v = A.gain_db(v, -16.0 - A.lufs(v))
    import soundfile as sf
    sf.write(os.path.join(out, "voice.wav"), v, A.SR)
    caps = []
    for j, (s, e, cards, bounds) in enumerate(units):
        nxt = units[j + 1][0] - 0.15 if j + 1 < len(units) else end
        stop = min(max(e + TAIL, s + 1.6), nxt) if j + 1 < len(units) else end
        for c, lines in enumerate(cards):
            cs = max(bounds[c] - (0.15 if c == 0 else 0), 0)
            ce = bounds[c + 1] if c + 1 < len(cards) else stop
            caps.append([round(cs, 2), round(ce, 2), lines])
    json.dump({"end": round(end, 2), "caps": caps, "spoken": [u[0] for u in UNITS],
               "units": [[round(s, 2), round(e, 2)] for s, e, _, _ in units]}, open(os.path.join(out, "timing.json"), "w"), indent=1)
    print("end", round(end, 2))
    for c in caps:
        print(c)


if __name__ == "__main__":
    main()
