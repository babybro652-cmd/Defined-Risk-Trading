# DRT Shorts audio

`add_audio.py` adds music, an optional voice (Tim's memo or the local AI voice) and burned-in
captions to a Short, then runs the audio QA. Run `python3 drt/audio/add_audio.py -h` for options.

    pip install -q numpy pyloudnorm soundfile faster-whisper piper-tts
    python3 drt/audio/add_audio.py in.mp4 -o out.mp4 --sheet sheet.png                 # music only
    python3 drt/audio/add_audio.py in.mp4 --voice memo.m4a --captions -o out.mp4       # Tim's memo
    python3 drt/audio/add_audio.py in.mp4 --tts-text "..." --captions -o out.mp4       # AI voice

- Music: `music/` (CC0, see `music/LICENSES.md`), picked by date unless `--music NAME|synth|none`.
- AI voice: Piper `en_US-norman-medium`, downloaded to `~/.cache/drt-piper` on first use.
- Exit code 1 and `AUDIO QA: FAIL` if any check fails. Don't upload a failing file.
