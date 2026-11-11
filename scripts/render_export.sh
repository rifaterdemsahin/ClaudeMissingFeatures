#!/bin/zsh
# Render the next numbered export for one or more PLATFORMS. Never overwrites an old version.
# Usage: scripts/render_export.sh "what changed" [platform ...] [--version N]
#   platforms: youtube (the full video, default), linkedin, x  (see remotion/src/variants.json)
#   --version N : render more platforms for an already used number (same state of the edit); otherwise the next number is used.
# Files: exports/<slug>-<platform>-v<N>.mp4 (e.g. youtube, linkedin, x). About 2x the video length per render at 13 frames/s.
cd "$(dirname "$0")/.." || exit 1
NOTES=""; PLATFORMS=(); VER=""
while [ $# -gt 0 ]; do case "$1" in --version) VER="$2"; shift 2;; *) if [ -z "$NOTES" ]; then NOTES="$1"; else PLATFORMS+=("$1"); fi; shift;; esac; done
[ ${#PLATFORMS[@]} -eq 0 ] && PLATFORMS=(youtube)
SLUG=$(python3 -c "import json;print(json.load(open('remotion/src/project.json')).get('slug','video'))")
[ -z "$VER" ] && VER=$(python3 -c "import json,os;r=json.load(open('assets/exports.json')) if os.path.exists('assets/exports.json') else [];print(max([e['v'] for e in r]+[0])+1)")
mkdir -p exports assets/maps
OFF=$(cat assets/whisper_offset.txt 2>/dev/null || echo 0)
for P in $PLATFORMS; do
  OUT="exports/$SLUG-$P-v$VER.mp4"
  [ -f "$OUT" ] && { echo "refusing to overwrite $OUT (use the next version)"; exit 1; }
  [ -f assets/whisper_words.json ] && python3 -I scripts/build_subs.py assets/whisper_words.json "$OFF" $P | tail -1   # captions + time map for THIS state and platform
  [ "$P" = youtube ] && python3 -I scripts/build_chapters.py | tail -1
  echo "Rendering $P export v$VER -> $OUT"
  (cd remotion && npx remotion render src/index.ts LongForm "out/tmp-$P.mp4" --props="{\"variant\":\"$P\"}") || exit 1
  mv "remotion/out/tmp-$P.mp4" "$OUT"; cp "$OUT" "$HOME/Downloads/$(basename $OUT)"
  if [ "$P" = youtube ]; then ln -f "$OUT" remotion/out/long.mp4; ln -sf "$OUT" export.mp4; python3 scripts/register_export.py "$OUT" "$VER" "$NOTES" --platform youtube
  else python3 scripts/register_export.py "$OUT" "$VER" "$NOTES" --platform "$P" --map "assets/maps/$P.json"; fi
done
echo "Done: v$VER for: $PLATFORMS. Next: scripts/verify_export.py <file> for each, measure_video.py, upload_exports.py, build_all.sh, commit and back up."
