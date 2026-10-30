#!/usr/bin/env python3
"""Add music (and optional voice + burned-in captions) to a DRT Short, then QA the audio.

Examples
  # music only (trade Short without a voice memo, text-card Short)
  python3 drt/audio/add_audio.py in.mp4 -o out.mp4
  # Tim's voice memo, captions from speech-to-text, music ducked underneath
  python3 drt/audio/add_audio.py in.mp4 --voice memo.m4a --captions -o out.mp4
  # education Short with the local AI voice (YouTube containsSyntheticMedia: true)
  python3 drt/audio/add_audio.py in.mp4 --tts-text "Your stop goes where the idea is wrong." --captions -o out.mp4

Mix rules (Tim, 10/30): CC0 instrumental from drt/audio/music (see LICENSES.md), music bed
about -19 LUFS, ducked to about 25 dB under the voice while it talks, fade in 0.5 s, fade
out 1 s, trimmed to the video. Final: -14 LUFS integrated when there's a voice, -18 LUFS for
music-only (calm bed under text cards; override with --target), true peak -2 dBTP,
AAC 192k 48 kHz. The QA block at the end prints PASS/FAIL and exits 1 on any failure.

Needs: ffmpeg with libass (for --captions), numpy, pyloudnorm.
Optional: faster-whisper (captions + intelligibility check), piper-tts (--tts-text).
  pip install numpy pyloudnorm faster-whisper piper-tts
"""
import argparse, datetime, difflib, glob, json, math, os, re, shutil, subprocess, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(HERE, "music")
SR = 48000
PIPER_VOICE = "en_US-norman-medium"  # LibriVox public-domain dataset, see music/LICENSES.md
PIPER_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/norman/medium/"
MUSIC_BED_LUFS = -19.0
VOICE_LUFS = -16.0
DUCK_UNDER_VOICE_DB = 25.0


def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: install it or `pip install imageio-ffmpeg`")


FF = ffmpeg_bin()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode != 0:
        sys.exit("command failed: %s\n%s" % (" ".join(cmd[:6]), r.stderr.decode(errors="ignore")[-2000:]))
    return r


def duration(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True).stderr.decode(errors="ignore")
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        sys.exit("can't read duration of " + path)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def has_audio(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True).stderr.decode(errors="ignore")
    return bool(re.search(r"Stream #\S+.*Audio:", out))


def decode(path, sr=SR, ch=2):
    raw = run([FF, "-v", "error", "-i", path, "-vn", "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"]).stdout
    a = np.frombuffer(raw, np.float32).copy()
    return a.reshape(-1, ch) if ch > 1 else a


def lufs(x, sr=SR):
    import pyloudnorm as pyln
    if len(x) < sr * 0.5 or not np.any(x):
        return -70.0
    v = pyln.Meter(sr).integrated_loudness(x)
    return -70.0 if not np.isfinite(v) else float(v)


def gain_db(x, db):
    return x * (10 ** (db / 20.0))


def fit_length(x, n):
    if len(x) >= n:
        return x[:n]
    reps = int(math.ceil(n / max(len(x), 1)))
    return np.concatenate([x] * reps)[:n]


def fades(x, fin=0.5, fout=1.0, sr=SR):
    n = len(x)
    env = np.ones(n, np.float32)
    a, b = int(fin * sr), int(fout * sr)
    if a:
        env[:a] = np.linspace(0, 1, a)
    if b:
        env[-b:] = np.minimum(env[-b:], np.linspace(1, 0, b))
    return x * env[:, None]


def synth_pad(seconds, sr=SR, seed=7):
    """Original ambient bed: slow sine chords (Am7 - Fmaj7 - Cmaj7 - G6), soft swells."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * sr)) / sr
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]
    seg = 6.0
    out = np.zeros((len(t), 2), np.float32)
    for i, chord in enumerate(chords * int(math.ceil(seconds / (seg * 4)) + 1)):
        s0 = i * seg
        if s0 > seconds:
            break
        idx = (t >= s0 - 1.5) & (t < s0 + seg + 1.5)
        tt = t[idx] - s0
        env = np.clip(np.minimum((tt + 1.5) / 2.0, (seg + 1.5 - tt) / 2.0), 0, 1) ** 1.5
        for note in chord:
            f = 440 * 2 ** ((note - 69) / 12)
            for det, pan in ((-0.6, 0.3), (0.6, 0.7)):
                ph = rng.uniform(0, 2 * np.pi)
                w = np.sin(2 * np.pi * (f + det) * tt + ph) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * tt + ph)
                out[idx, 0] += (env * w * (1 - pan)).astype(np.float32)
                out[idx, 1] += (env * w * pan).astype(np.float32)
    out += rng.normal(0, 0.002, out.shape).astype(np.float32)
    return out / (np.max(np.abs(out)) + 1e-9) * 0.5


def pick_music(choice, seed_date):
    tracks = sorted(glob.glob(os.path.join(MUSIC_DIR, "*.mp3")))
    if choice == "auto":
        if not tracks:
            return "synth"
        return tracks[seed_date.toordinal() % len(tracks)]
    if choice in ("synth", "none"):
        return choice
    if not os.path.exists(choice):
        cand = os.path.join(MUSIC_DIR, choice if choice.endswith(".mp3") else choice + ".mp3")
        if os.path.exists(cand):
            return cand
        sys.exit("music track not found: " + choice)
    return choice


def piper_model():
    d = os.path.expanduser("~/.cache/drt-piper")
    os.makedirs(d, exist_ok=True)
    m = os.path.join(d, PIPER_VOICE + ".onnx")
    for ext in (".onnx", ".onnx.json"):
        p = os.path.join(d, PIPER_VOICE + ext)
        if not os.path.exists(p):
            run(["curl", "-sSL", "-m", "300", "-o", p, PIPER_URL + PIPER_VOICE + ext])
    return m


def tts(text, out_wav, speed=1.0):
    run([sys.executable, "-m", "piper", "-m", piper_model(), "-f", out_wav,
         "--length-scale", str(1.0 / speed), "--sentence-silence", "0.25"], input=text.encode())
    return out_wav


def activity(voice_mono, sr=SR, win=0.02):
    """Boolean per-window voice activity + window size in samples."""
    w = int(sr * win)
    n = len(voice_mono) // w
    frames = voice_mono[: n * w].reshape(n, w)
    db = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-9)
    if n == 0:
        return np.zeros(0, bool), w
    thr = max(np.percentile(db, 95) - 30, -55)
    act = db > thr
    hold = int(0.3 / win)
    if hold:
        act = np.convolve(act.astype(float), np.ones(hold * 2 + 1), "same") > 0
    return act, w


def duck_envelope(act, w, n_samples, duck_db, sr=SR):
    target = np.where(act, duck_db, 0.0)
    a_att = math.exp(-w / (0.08 * sr))
    a_rel = math.exp(-w / (0.40 * sr))
    g = np.zeros_like(target)
    cur = 0.0
    for i, tg in enumerate(target):
        a = a_att if tg < cur else a_rel
        cur = a * cur + (1 - a) * tg
        g[i] = cur
    env_db = np.repeat(g, w)
    env_db = np.pad(env_db, (0, max(0, n_samples - len(env_db))), mode="edge")[:n_samples]
    return 10 ** (env_db / 20.0)


def whisper_words(audio_mono16k):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    model = WhisperModel(os.environ.get("DRT_WHISPER", "base.en"), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio_mono16k, word_timestamps=True, vad_filter=True)
    words = []
    for s in segs:
        for wd in s.words or []:
            words.append((wd.start, wd.end, wd.word.strip()))
    return words


def ass_time(t):
    t = max(t, 0)
    return "%d:%02d:%05.2f" % (t // 3600, (t % 3600) // 60, t % 60)


def chunk_words(words, max_words=3, max_chars=18):
    chunks, cur = [], []
    for st, en, w in words:
        cur.append((st, en, w))
        text = " ".join(x[2] for x in cur)
        if len(cur) >= max_words or len(text) >= max_chars or re.search(r"[.,!?;:]$", w):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return [(c[0][0], c[-1][1], " ".join(x[2] for x in c)) for c in chunks]


def write_ass(chunks, path, width, height, margin_v):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: %d
PlayResY: %d
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,%d,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,%d,2,2,60,60,%d,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (width, height, int(height * 0.04), max(3, int(height * 0.0028)), margin_v)
    lines = []
    for i, (st, en, text) in enumerate(chunks):
        nxt = chunks[i + 1][0] if i + 1 < len(chunks) else en + 0.4
        en = min(max(en + 0.15, st + 0.5), nxt)
        text = text.replace("{", "(").replace("}", ")")
        lines.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,%s" % (ass_time(st), ass_time(en), text.upper()))
    open(path, "w").write(head + "\n".join(lines) + "\n")


def even_chunks(text, start, end):
    words = text.split()
    n = max(1, int(math.ceil(len(words) / 3)))
    span = max(end - start, 0.5) / n
    out = []
    for i in range(n):
        out.append((start + i * span, start + (i + 1) * span, " ".join(words[i * 3:(i + 1) * 3])))
    return out


def norm_words(t):
    return re.findall(r"[a-z0-9']+", t.lower().replace("-", " "))


def to16k(x):
    mono = x.mean(axis=1) if x.ndim == 2 else x
    idx = np.arange(0, len(mono), SR / 16000.0).astype(int)
    return mono[idx[idx < len(mono)]].astype(np.float32)


def video_size(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True).stderr.decode(errors="ignore")
    m = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", out)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 1920)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--voice", help="voice memo / narration file (any format ffmpeg reads)")
    ap.add_argument("--voice-offset", type=float, default=0.0, help="seconds into the video where the voice starts")
    ap.add_argument("--voice-trim", type=float, default=0.0, help="seconds to cut from the start of the voice file")
    ap.add_argument("--tts-text", help="AI voiceover text (local Piper voice)")
    ap.add_argument("--tts-file", help="file with the AI voiceover text")
    ap.add_argument("--tts-speed", type=float, default=1.05)
    ap.add_argument("--video-audio", choices=["auto", "drop", "voice"], default="auto",
                    help="auto: treat the video's own audio as voice if it isn't silent")
    ap.add_argument("--music", default="auto", help="auto (date rotation) | synth | none | file or library name")
    ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--captions", action="store_true", help="burn captions from the voice")
    ap.add_argument("--caption-text", help="fallback caption text if speech-to-text isn't available")
    ap.add_argument("--caption-margin", type=int, default=None, help="caption distance from bottom (px)")
    ap.add_argument("--target", type=float, default=None, help="final integrated LUFS (default -14 voice, -18 music only)")
    ap.add_argument("--date", help="YYYY-MM-DD for music rotation (default today)")
    ap.add_argument("--sheet", help="also write a frame contact sheet PNG here (for media QA)")
    a = ap.parse_args()

    vdur = duration(a.video)
    n = int(round(vdur * SR))
    tmp = tempfile.mkdtemp(prefix="drt_audio_")
    report = {"video": a.video, "duration_s": round(vdur, 2)}

    # ---- voice ----
    voice, ref_text, synthetic = None, None, False
    if a.tts_text or a.tts_file:
        ref_text = a.tts_text or open(a.tts_file).read()
        vpath = tts(ref_text.strip(), os.path.join(tmp, "tts.wav"), a.tts_speed)
        synthetic = True
    elif a.voice:
        vpath = a.voice
    else:
        vpath = None
        if a.video_audio != "drop" and has_audio(a.video):
            va = decode(a.video)
            if a.video_audio == "voice" or 20 * np.log10(np.sqrt(np.mean(va ** 2)) + 1e-9) > -50:
                vpath = a.video
                report["voice_source"] = "video's own audio"
    if vpath:
        v = decode(vpath)
        v = v[int(a.voice_trim * SR):]
        off = int(a.voice_offset * SR)
        voice = np.zeros((n, 2), np.float32)
        seg = v[: max(0, n - off)]
        voice[off: off + len(seg)] = seg
        if len(v) > n - off:
            report["warning_voice_cut_s"] = round((len(v) - (n - off)) / SR, 2)
        vl = lufs(voice)
        voice = gain_db(voice, VOICE_LUFS - vl)
        report["voice"] = vpath
        report["voice_synthetic"] = synthetic

    # ---- music ----
    seed_date = datetime.date.fromisoformat(a.date) if a.date else datetime.date.today()
    mchoice = pick_music(a.music, seed_date)
    music = None
    if mchoice == "synth":
        music = synth_pad(vdur + 1)
    elif mchoice != "none":
        music = decode(mchoice)[int(a.music_start * SR):]
    if music is not None:
        music = fit_length(music, n)
        music = gain_db(music, MUSIC_BED_LUFS - lufs(music))
        report["music"] = os.path.basename(mchoice) if mchoice != "synth" else "synth (original pad)"

    # ---- duck + mix ----
    mix = np.zeros((n, 2), np.float32)
    under = None
    if music is not None:
        if voice is not None:
            act, w = activity(voice.mean(axis=1))
            duck_db = (VOICE_LUFS - DUCK_UNDER_VOICE_DB) - MUSIC_BED_LUFS
            env = duck_envelope(act, w, n, duck_db)
            music = music * env[:, None]
            mask = np.repeat(act, w)[:n]
            if mask.any():
                vm = 20 * np.log10(np.sqrt(np.mean(voice[: len(mask)][mask] ** 2)) + 1e-9)
                mm = 20 * np.log10(np.sqrt(np.mean(music[: len(mask)][mask] ** 2)) + 1e-9)
                under = vm - mm
        music = fades(music, 0.5, 1.0)
        mix += music
    if voice is not None:
        mix += voice
    if not np.any(mix):
        sys.exit("nothing to mix: no voice and --music none")

    target = a.target if a.target is not None else (-14.0 if voice is not None else -18.0)
    raw_wav = os.path.join(tmp, "mix.wav")
    import soundfile  # noqa: F401  (pyloudnorm dependency stack)
    run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw_wav],
        input=mix.astype(np.float32).tobytes())
    # two-pass loudnorm, linear, true peak -1.5
    p1 = subprocess.run([FF, "-hide_banner", "-i", raw_wav, "-af",
                         "loudnorm=I=%s:TP=-2.0:LRA=11:print_format=json" % target, "-f", "null", "-"],
                        capture_output=True).stderr.decode(errors="ignore")
    js = json.loads(p1[p1.rfind("{"): p1.rfind("}") + 1])
    ln = ("loudnorm=I=%s:TP=-2.0:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:"
          "measured_thresh=%s:offset=%s:linear=true" % (target, js["input_i"], js["input_tp"],
                                                       js["input_lra"], js["input_thresh"], js["target_offset"]))
    final_wav = os.path.join(tmp, "final.wav")
    run([FF, "-v", "error", "-y", "-i", raw_wav, "-af", ln + ",aresample=48000", "-ar", "48000", final_wav])

    # ---- captions ----
    vf = None
    if a.captions and voice is not None:
        words = whisper_words(to16k(voice))
        if words:
            chunks = chunk_words(words)
            report["captions"] = "speech-to-text (faster-whisper)"
            if ref_text is None:
                ref_text = " ".join(w[2] for w in words)
        else:
            act, w = activity(voice.mean(axis=1))
            idx = np.nonzero(act)[0]
            txt = a.caption_text or ref_text
            if txt is None:
                sys.exit("--captions needs faster-whisper or --caption-text")
            s0, s1 = (idx[0] * w / SR, idx[-1] * w / SR) if len(idx) else (0, vdur)
            chunks = even_chunks(txt, s0, s1)
            report["captions"] = "even split of supplied text"
        W, H = video_size(a.video)
        ass = os.path.join(tmp, "caps.ass")
        write_ass(chunks, ass, W, H, a.caption_margin if a.caption_margin is not None else int(H * 0.27))
        vf = "ass=" + ass.replace(":", r"\:")

    # ---- mux ----
    cmd = [FF, "-v", "error", "-y", "-i", a.video, "-i", final_wav, "-map", "0:v:0", "-map", "1:a:0"]
    cmd += (["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
            if vf else ["-c:v", "copy"])
    cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "%.3f" % vdur, "-movflags", "+faststart", a.out]
    run(cmd)

    # ---- QA ----
    checks = []
    out_has_audio = has_audio(a.out)
    checks.append(("audio stream present", out_has_audio, ""))
    od = decode(a.out)
    eb = subprocess.run([FF, "-hide_banner", "-nostats", "-i", a.out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                        capture_output=True).stderr.decode(errors="ignore")
    summ = eb[eb.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp_m = re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summ)
    tp = float(tp_m.group(1)) if tp_m else 0.0
    clipped = int(np.sum(np.abs(od) >= 0.999))
    report.update({"integrated_lufs": I, "true_peak_dbfs": tp, "clipped_samples": clipped, "target_lufs": target})
    checks.append(("loudness near target", abs(I - target) <= 1.5, "%.1f LUFS (target %.0f)" % (I, target)))
    checks.append(("no clipping", clipped == 0 and tp <= -0.5, "%d clipped samples, true peak %.1f dBFS" % (clipped, tp)))
    odur = duration(a.out)
    checks.append(("length matches video", abs(odur - vdur) < 0.15, "%.2f s vs %.2f s" % (odur, vdur)))
    if voice is not None and music is not None:
        checks.append(("music under voice", under is not None and under >= 15,
                       "voice %.1f dB above music while talking" % (under or 0)))
    if voice is not None:
        heard = whisper_words(to16k(od))
        if heard is None:
            checks.append(("voice intelligible", True, "SKIPPED: faster-whisper not installed, listen to it"))
        else:
            ref = norm_words(ref_text or "")
            got = norm_words(" ".join(w[2] for w in heard))
            if ref:
                sm = difflib.SequenceMatcher(None, ref, got)
                recall = sum(b.size for b in sm.get_matching_blocks()) / len(ref)
            else:
                recall = 1.0 if got else 0.0
            report["heard"] = " ".join(w[2] for w in heard)
            checks.append(("voice intelligible", recall >= 0.8, "%.0f%% of the words recovered by speech-to-text" % (recall * 100)))
    report["checks"] = [{"check": c, "pass": bool(p), "detail": d} for c, p, d in checks]

    if a.sheet:
        cols, fps = 8, 2
        rows = int(math.ceil(vdur * fps / cols))
        run([FF, "-v", "error", "-y", "-i", a.out, "-vf", "fps=%d,scale=180:-1,tile=%dx%d" % (fps, cols, rows),
             "-frames:v", "1", a.sheet])
        report["contact_sheet"] = a.sheet

    print(json.dumps(report, indent=2))
    ok = all(p for _, p, _ in checks)
    print("AUDIO QA: " + ("PASS" if ok else "FAIL"))
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
