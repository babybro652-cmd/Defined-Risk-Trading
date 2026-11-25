#!/bin/bash
# 11/24 NY morning: two back-to-back ES shorts from DRT Phone Screen_Recording_20261124_105727 (src/rec1057.mp4,
# short 1 @ 7187.00 stopped at 7191.50) and Screen_Recording_20261124_110348 (src/rec1103.mp4, short 1 @ 7187.50,
# out 1 @ 7172.50). Raw src/ kept out of git (Drive ids 1SrXyeG-EDkI_hcmCuGyr5V7HifIqDM5j, 15yFZYt7v4ygQC3o8tS00W4Gspt7okngO). hdr.png = 11/23 header ("S&P 500 E-mini (ES), 1-minute"). Run from this folder.
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
# Covers: indicator legend + signal/volume tables (names indicators) -> chart black; "CRT Filter" panel -> chart black.
COVER="drawbox=x=0:y=92:w=908:h=402:color=0x0f0f0f:t=fill,drawbox=x=612:y=1646:w=282:h=200:color=0x0f0f0f:t=fill"
PRE="fps=30,$COVER[c];[c][1:v]overlay=0:0,crop=1080:1920:0:92,setsar=1"
# Part 1 (rec1057): cut 0-1 s (quick settings panel shows Wi-Fi name), 1-118 s at 10x, 118-137 s at 2x (stop fill ~128.5 s),
# cut after 137 s (timeframe menu + 15m chart with indicator labels).
$FF -y -i src/rec1057.mp4 -i hdr.png -an -filter_complex "[0:v]$PRE,split[a][b];[a]trim=1:118,setpts=(PTS-STARTPTS)/10[x];[b]trim=118:137,setpts=(PTS-STARTPTS)/2[y];[x][y]concat=n=2:v=1:a=0,fps=30[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p p1.mp4
# Part 2 (rec1103): cut 134-142.5 s (alert menu names indicators), 168-174.5 s (order menu + ticket showing margin),
# 284-289 s (order menu). Riding parts at 12x, 289-321 at 6x, 321-end at 1.5x (exit fill ~328 s), last frame held 1.5 s.
$FF -y -i src/rec1103.mp4 -i hdr.png -an -filter_complex "[0:v]$PRE,split=5[a][b][c][d][e];[a]trim=0:134,setpts=(PTS-STARTPTS)/12[p];[b]trim=142.5:168,setpts=(PTS-STARTPTS)/12[q];[c]trim=174.5:284,setpts=(PTS-STARTPTS)/12[r];[d]trim=289:321,setpts=(PTS-STARTPTS)/6[s];[e]trim=321,setpts=(PTS-STARTPTS)/1.5[t];[p][q][r][s][t]concat=n=5:v=1:a=0,tpad=stop_mode=clone:stop_duration=1.5,fps=30[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p p2.mp4
$FF -y -i p1.mp4 -i p2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p reel-a.mp4
rm -f p1.mp4 p2.mp4
