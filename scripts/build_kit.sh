#!/bin/zsh
# Build the kit zip. Usage: scripts/build_kit.sh [out.zip]  (default ~/Downloads/claude-missing-features-kit.zip)
cd "$(dirname "$0")/.." || exit 1
OUT="${1:-$HOME/Downloads/claude-missing-features-kit.zip}"; mkdir -p "$(dirname "$OUT")"; OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")";   # absolute: we cd into the staging dir before zipping
 ST=$(mktemp -d)/kit; mkdir -p "$ST/scripts" "$ST/remotion/src" "$ST/remotion/public/img" "$ST/templates"
cp MASTER_SPEC.md ENVIRONMENT.md nav.js architecture.html .gitignore "$ST/"; mkdir -p "$ST/assets"; for f in edl_decisions chapters audio_fixes; do echo "[]" > "$ST/assets/$f.json"; done; cp kit/KIT_README.md "$ST/README.md"; cp kit/new-video.sh "$ST/"
cp scripts/{sync_clips.py,render_base.sh,build_subs.py,find_repeats.py,build_site.py,serve.sh,pull_kit.sh,build_kit.sh,build_blurs.py,ocr_frames.swift,build_base.py,ocr_all.sh,find_personal_windows.py,verify_export.py,report.py,pipeline.sh,build_architecture.py,check_env.sh,denoise_audio.py,build_edl.py,build_chapters.py,backup_drive.sh} "$ST/scripts/"
cp remotion/{package.json,package-lock.json,tsconfig.json,remotion.config.ts} "$ST/remotion/"
cp remotion/src/*.ts remotion/src/*.tsx "$ST/remotion/src/"; echo '[]' > "$ST/remotion/src/cuts.json"; echo '[]' > "$ST/remotion/src/subs.json"
echo '{"_doc":"source seconds; x,y,w,h in 1920x1080 px","intro_card":{"from":0,"to":0},"slides":[],"blurs":[],"speedups":[],"images":[]}' > "$ST/remotion/src/overlays.json"; echo 'window.EXPORT_MAP = null;' > "$ST/export_map.js"; touch "$ST/remotion/public/.gitkeep" "$ST/remotion/public/img/.gitkeep"
cp kit/templates/* "$ST/templates/"; python3 - "$ST" <<'PY'
import sys,re,pathlib
st=pathlib.Path(sys.argv[1]); h=pathlib.Path('player.html').read_text()
h=re.sub(r'const C=\[\[.*?\]\]; // source seconds','const C=[]; // [[source seconds,"chapter"],...]',h,flags=re.S)
h=h.replace('Claude Missing Features: player','{{TITLE}}: player')
h=re.sub(r'<tr><td>Edits</td>.*?</tr>','<tr><td>Edits</td><td>none</td><td>{{EDITS}}</td></tr>',h,flags=re.S)
(st/'templates'/'player.html').write_text(h)
PY
 echo 'window.SUBS = [];' > "$ST/subs.js"
(cd "$ST" && zip -qr "$OUT" .); echo "built $OUT ($(du -h "$OUT" | cut -f1)), $(unzip -Z1 "$OUT" | wc -l | tr -d ' ') files"
