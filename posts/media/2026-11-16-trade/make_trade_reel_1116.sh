#!/bin/bash
# Rebuild the 11/16 trade reel from the two DRT Phone files (vid.mp4, shot.jpg).
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
# screenshot: cover indicator legend (names an indicator), crop status bar and nav
$FF -y -i shot.jpg -vf "drawbox=x=0:y=235:w=905:h=262:color=0x0f0f0f:t=fill,crop=1080:1920:0:95" shot_clean.png
# video: crop status bar (top 100) and app/system nav (bottom), 1080x1920
$FF -y -i vid.mp4 -an -vf "crop=1080:1920:0:100,fps=30,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p v_full.mp4
$FF -y -i vid.mp4 -an -vf "crop=1080:1920:0:100,setpts=PTS/1.6,fps=30,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p v_fast.mp4
$FF -y -loop 1 -t 4 -i shot_clean.png -vf "fps=30,format=yuv420p,setsar=1" -c:v libx264 -crf 20 still4.mp4
$FF -y -loop 1 -t 3.5 -i shot_clean.png -vf "fps=30,format=yuv420p,setsar=1" -c:v libx264 -crf 20 still35.mp4
$FF -y -i v_full.mp4 -i still4.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p reel.mp4
$FF -y -i v_fast.mp4 -i still35.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1[v]" -map "[v]" -c:v libx264 -crf 20 -pix_fmt yuv420p short.mp4
A=drt/audio/add_audio.py
/usr/bin/python3 $A reel.mp4 -o reel-tt-music.mp4 --music cliff_road_chill --sheet sheet_reel.png
/usr/bin/python3 $A reel.mp4 -o reel-personal-music.mp4 --music sugar_and_coffee --sheet sheet_personal.png
/usr/bin/python3 $A short.mp4 -o short-music.mp4 --music once_more_with_you --sheet sheet_short.png
