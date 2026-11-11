#!/bin/zsh
# Build the kit zip. Usage: scripts/build_kit.sh [out.zip]  (default ~/Downloads/claude-missing-features-kit.zip)
cd "$(dirname "$0")/.." || exit 1
OUT="${1:-$HOME/Downloads/claude-missing-features-kit.zip}"; ST=$(mktemp -d)/kit; mkdir -p "$ST/scripts" "$ST/remotion/src" "$ST/remotion/public/img" "$ST/templates"
cp MASTER_SPEC.md nav.js .gitignore "$ST/"; cp kit/KIT_README.md "$ST/README.md"; cp kit/new-video.sh "$ST/"
cp scripts/{sync_clips.py,render_base.sh,build_subs.py,find_repeats.py,build_site.py,serve.sh,pull_kit.sh,build_kit.sh} "$ST/scripts/"
cp remotion/{package.json,package-lock.json,tsconfig.json,remotion.config.ts} "$ST/remotion/"
cp remotion/src/*.ts remotion/src/*.tsx "$ST/remotion/src/"; echo '[]' > "$ST/remotion/src/cuts.json"; echo '[]' > "$ST/remotion/src/subs.json"
cp remotion/src/overlays.json "$ST/remotion/src/"; touch "$ST/remotion/public/.gitkeep" "$ST/remotion/public/img/.gitkeep"
cp kit/templates/* "$ST/templates/"; echo 'window.SUBS = [];' > "$ST/subs.js"
(cd "$ST" && zip -qr "$OUT" .); echo "built $OUT ($(du -h "$OUT" | cut -f1)), $(unzip -Z1 "$OUT" | wc -l | tr -d ' ') files"
