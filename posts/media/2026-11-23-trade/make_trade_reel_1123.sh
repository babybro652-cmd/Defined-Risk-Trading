#!/bin/bash
# Rebuild the 11/23 trade reel from DRT Phone Screen_Recording_20261123_102041_TradingView.mp4 (vid.mp4).
# hdr.png: 1080x2340 transparent PNG with the header line "S&P 500 E-mini (ES), 1-minute" at (32,150), Liberation Sans Bold 50.
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
# Covers: top indicator legend + signal table (indicator names) and the instrument header it overlaps -> chart black;
# CRT Filter panel (bottom right, in the shaded band) -> band color. Mic audio dropped (-an).
COVER="drawbox=x=0:y=92:w=908:h=400:color=0x0f0f0f:t=fill,drawbox=x=616:y=1648:w=278:h=112:color=0x382d0c:t=fill,drawbox=x=783:y=1758:w=111:h=106:color=0x382d0c:t=fill"
# 1-110 s at 4x (0-0.7 s is the phone quick-settings panel, cut) (position riding), 110-end at 1.5x (the fill at the target), last frame held 1.5 s. Crop status bar and app nav to 1080x1920.
$FF -y -i vid.mp4 -i hdr.png -an -filter_complex "[0:v]fps=30,$COVER[c];[c][1:v]overlay=0:0,crop=1080:1920:0:92,setsar=1,split[a][b];[a]trim=1:110,setpts=(PTS-STARTPTS)/4[x];[b]trim=110,setpts=(PTS-STARTPTS)/1.5[y];[x][y]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration=1.5,fps=30[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p reel.mp4
A=/home/user/Defined-Risk-Trading/drt/audio/add_audio.py
/usr/bin/python3 $A reel.mp4 -o reel-tt-music.mp4 --music im_glad_you_are_here --sheet sheet_reel.png
/usr/bin/python3 $A reel.mp4 -o reel-personal-music.mp4 --music once_more_with_you --sheet sheet_personal.png
/usr/bin/python3 $A reel.mp4 -o short-music.mp4 --music aeroplane --sheet sheet_short.png
