#!/bin/zsh
# Whole local prep in one command (MacBook only, no Claude tokens). Usage: scripts/pipeline.sh "<folder with clips + WAV>" <slug>
# Skips any stage whose output exists. Then read REPORT.md, write slides into remotion/src/overlays.json, run build_blurs.py, render.
cd "$(dirname "$0")/.." || exit 1
IN="${1:?folder}"; SLUG="${2:?slug}"; OUT="$HOME/Downloads/$SLUG-1080p.mp4"; mkdir -p assets
[ -f "$OUT" ] || python3 scripts/build_base.py "$IN" "$OUT" || exit 1
[ -f assets/base_info.json ] || python3 scripts/build_base.py "$IN" "$OUT" --sync-only
mkdir -p remotion/public; ln -f "$OUT" remotion/public/base.mp4 2>/dev/null; ln -f "$OUT" long.mp4 2>/dev/null
OFF=$(python3 -c "import json;print(json.load(open('assets/base_info.json'))['voice_start'])")
[ -f assets/whisper_offset.txt ] && OFF=$(cat assets/whisper_offset.txt)   # offset the saved transcript was made with
if [ ! -f assets/whisper_words.json ]; then
  T=$(mktemp -d); ffmpeg -v error -y -ss $OFF -i "$(ls "$IN"/*.WAV "$IN"/*.wav 2>/dev/null | head -1)" -ac 1 -ar 16000 $T/v.wav
  (cd $T && whisper v.wav --model small --language en --word_timestamps True --output_dir out --output_format json >/dev/null 2>&1); cp $T/out/v.json assets/whisper_words.json
  OFF=0; echo 0 > assets/whisper_offset.txt   # audio was already cut at the voice start
fi
python3 -I scripts/build_subs.py assets/whisper_words.json ${OFF:-0}
[ -f assets/ocr_frames.json ] || scripts/ocr_all.sh long.mp4 assets/ocr_frames.json
python3 -I scripts/find_repeats.py > assets/repeats.txt
python3 -I scripts/find_personal_windows.py
python3 -I scripts/report.py
