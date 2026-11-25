#!/bin/bash
# 11/25 early long from DRT Phone Screen_Recording_20261125_045721 (../2026-11-24-trades/src/rec0457.mp4): long 2 @ 7113.75, sell stop moved to
# 7115.00, out 2 @ 7116.00. Run from this folder (raw source kept out of git; DRT Phone id 11O6VXYmJ-e_HF6WBiqCP3oGRiAD6_45d). Same covers as make_trade_reel_1124am.sh.
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
COVER="drawbox=x=0:y=92:w=908:h=402:color=0x0f0f0f:t=fill,drawbox=x=612:y=1646:w=282:h=200:color=0x0f0f0f:t=fill"
# Cut 9.5-13.5 s (alert menu names indicators) and everything after 80 s (broker panel with account number and balance).
# 0-9.5 and 13.5-70 at 4x, 70-80 at 1.5x (exit fill ~76.5 s), last frame held 1.5 s.
$FF -y -i ../2026-11-24-trades/src/rec0457.mp4 -i hdr.png -an -filter_complex "[0:v]fps=30,$COVER[c];[c][1:v]overlay=0:0,crop=1080:1920:0:92,setsar=1,split=3[a][b][d];[a]trim=0:9.5,setpts=(PTS-STARTPTS)/4[p];[b]trim=13.5:70,setpts=(PTS-STARTPTS)/4[q];[d]trim=70:80,setpts=(PTS-STARTPTS)/1.5[r];[p][q][r]concat=n=3:v=1:a=0,tpad=stop_mode=clone:stop_duration=1.5,fps=30[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p reel-c.mp4
