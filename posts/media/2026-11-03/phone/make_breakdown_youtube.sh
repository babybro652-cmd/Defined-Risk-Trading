#!/bin/sh
# YouTube Shorts cut of the 11/3 breakdown: retime the no-music time-lapse so the fill marker (base 65.1 s) lands on
# fill_out from make_breakdown_voiceover.py --youtube. Entry hold (0-2 s) and the 2 s before the fill stay real speed;
# base 2.0-63.1 s is sped up to fit. Usage: make_breakdown_youtube.sh BASE.mp4 timing.json OUT_RETIMED.mp4
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
FILL=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['fill_out'])" "$2")
F=$(python3 -c "print(($FILL-4.0)/61.1)")
"$FF" -y -loglevel error -i "$1" -filter_complex \
 "[0:v]trim=0:2,setpts=PTS-STARTPTS[a];[0:v]trim=2:63.1,setpts=(PTS-STARTPTS)*$F[b];[0:v]trim=63.1,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps=30[v]" \
 -map "[v]" -an -c:v libx264 -crf 16 -pix_fmt yuv420p "$3"
echo "speed factor $F"
