"""Replace listed bad frames with the previous good frame; keep audio stream as is. Usage: in out f1,f2,..."""
import subprocess,sys,numpy as np
FF="/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
src,out,bad=sys.argv[1],sys.argv[2],set(int(x) for x in sys.argv[3].split(","))
W,H=1080,1920
dec=subprocess.Popen([FF,"-loglevel","error","-i",src,"-f","rawvideo","-pix_fmt","yuv420p","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen([FF,"-loglevel","error","-y","-f","rawvideo","-pix_fmt","yuv420p","-s",f"{W}x{H}","-r","30","-i","-","-i",src,
  "-map","0:v","-map","1:a?","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart","-shortest",out],stdin=subprocess.PIPE)
fs=W*H*3//2; i=0; last=None
while True:
    b=dec.stdout.read(fs)
    if len(b)<fs: break
    if i in bad and last is not None: b=last
    else: last=b
    enc.stdin.write(b); i+=1
enc.stdin.close(); enc.wait(); print("frames",i)
