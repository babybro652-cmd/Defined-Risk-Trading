#!/bin/bash
# Rebuild the 11/20 eval trade reel from DRT Phone Screen_Recording_20261120_050412_TradingView.mp4 (vid.mp4).
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
# cut the long-press menu (9.3-11.8 s, shows "Add alert on CRT Pro VMap"), cover the CRT Filter panel,
# crop status bar (clock, recording dot, notification icons) and the app tab bar / system nav to 1080x1920
COVER="drawbox=x=610:y=1646:w=286:h=110:color=0x0f0f0f:t=fill,drawbox=x=812:y=1750:w=84:h=98:color=0x0f0f0f:t=fill"
SEL="select='not(between(t,9.3,11.8))',setpts=N/FRAME_RATE/TB"
$FF -y -i vid.mp4 -an -vf "fps=30,$SEL,$COVER,crop=1080:1920:0:92,setpts=PTS/1.5,fps=30,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p reel.mp4
A=/home/user/Defined-Risk-Trading/drt/audio/add_audio.py
/usr/bin/python3 $A reel.mp4 -o reel-tt-music.mp4 --music old_key --sheet sheet_reel.png
/usr/bin/python3 $A reel.mp4 -o reel-personal-music.mp4 --music happy_sadie --sheet sheet_personal.png
/usr/bin/python3 $A reel.mp4 -o short-music.mp4 --music waiting_tttt --sheet sheet_short.png
