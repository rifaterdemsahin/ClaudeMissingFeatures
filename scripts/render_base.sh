#!/bin/zsh
# Usage: render_base.sh CLIP1 CLIP2 VOICE_WAV VOICE_START_S CLIP2_SECONDS OUT.mp4
# Example: render_base.sh c1.mp4 c2.mp4 voice.WAV 4.75 268.74 ~/Downloads/x-1080p.mp4
FG='fps=30,split[a][b];[a]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,boxblur=12:2,scale=1920:1080,eq=brightness=-0.08[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p'
ffmpeg -y -hide_banner -loglevel error -stats -i "$1" -i "$2" -ss "$4" -i "$3" \
 -filter_complex "[0:v]${FG}[v0];[1:v]trim=0:$5,setpts=PTS-STARTPTS,${FG}[v1];[v0][v1]concat=n=2:v=1:a=0[v];[2:a]highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -r 30 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest "$6"
