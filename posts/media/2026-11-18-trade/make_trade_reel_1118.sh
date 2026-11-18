#!/bin/bash
# Rebuild the 11/18 paper trade reel from DRT Phone Screen_Recording_20261118_104040_TradingView.mp4 (vid.mp4).
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
# cover the expanded indicator legend (names indicators) until it collapses at ~18 s, crop status bar and nav
VF="drawbox=x=0:y=228:w=905:h=365:color=0x0f0f0f:t=fill:enable='lt(t,18.5)',crop=1080:1920:0:85"
$FF -y -i vid.mp4 -an -vf "$VF,setpts=PTS/4,fps=30,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p reel.mp4
$FF -y -i vid.mp4 -an -vf "$VF,setpts=PTS/5,fps=30,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p short.mp4
A=drt/audio/add_audio.py
/usr/bin/python3 $A reel.mp4 -o reel-tt-music.mp4 --music static_shoes --sheet sheet_reel.png
/usr/bin/python3 $A reel.mp4 -o reel-personal-music.mp4 --music coexistenz --sheet sheet_personal.png
/usr/bin/python3 $A short.mp4 -o short-music.mp4 --music traveling_in_your_mind --sheet sheet_short.png
