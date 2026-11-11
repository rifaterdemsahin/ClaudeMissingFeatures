#!/bin/zsh
# OCR a frame every 2 s with Apple Vision (local, 0 tokens). Usage: scripts/ocr_all.sh video.mp4 [out.json]
# Output frame name NNNN.jpg = second NNNN-1 (0001=0 s, 0003=2 s ...), same as build_blurs.py expects.
cd "$(dirname "$0")/.." || exit 1
V="$1"; OUT="${2:-assets/ocr_frames.json}"; W=$(mktemp -d); mkdir -p assets
[ -x ~/.cache/cmf-ocr ] || { mkdir -p ~/.cache && swiftc -O scripts/ocr_frames.swift -o ~/.cache/cmf-ocr || exit 1; }
for k in 0 1 2 3; do mkdir -p $W/p$k; done
ffmpeg -v error -i "$V" -vf "fps=1/2,scale=1920:1080" -q:v 4 $W/raw_%05d.jpg
i=0; for f in $W/raw_*.jpg; do n=$((10#$(basename $f .jpg | cut -d_ -f2))); mv $f $W/p$((i%4))/$(printf %04d $((2*(n-1)+1))).jpg; i=$((i+1)); done
echo "$i frames, OCR in 4 processes…"
for k in 0 1 2 3; do ~/.cache/cmf-ocr $W/p$k $W/o$k.json >/dev/null & done; wait
python3 -I -c "import json,glob,sys; d={}; [d.update(json.load(open(f))) for f in glob.glob('$W/o*.json')]; json.dump(d,open('$OUT','w')); print('wrote $OUT',len(d),'frames')"
rm -rf $W
