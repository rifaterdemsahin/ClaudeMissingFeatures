#!/bin/zsh
# Render the next numbered export: <slug>-v<N>.mp4. Never overwrites an old version.
# Usage: scripts/render_export.sh "what changed in this version"     (about 2x the video length at 13 frames/s)
cd "$(dirname "$0")/.." || exit 1
NOTES="${1:-}"; SLUG=$(python3 -c "import json;print(json.load(open('remotion/src/project.json')).get('slug','video'))")
N=$(python3 -c "import json,os;r=json.load(open('assets/exports.json')) if os.path.exists('assets/exports.json') else [];print(max([e['v'] for e in r]+[0])+1)")
mkdir -p exports; OUT="exports/$SLUG-v$N.mp4"
[ -f assets/whisper_words.json ] && python3 -I scripts/build_subs.py assets/whisper_words.json "$(cat assets/whisper_offset.txt 2>/dev/null || echo 0)" | tail -1   # captions + export map for THIS state of the edit
python3 -I scripts/build_chapters.py | tail -1
echo "Rendering export v$N -> $OUT"
(cd remotion && npx remotion render src/index.ts LongForm "out/v$N.mp4") || exit 1
mv "remotion/out/v$N.mp4" "$OUT" && ln -f "$OUT" remotion/out/long.mp4        # long.mp4 = latest, for the check scripts
ln -sf "$OUT" export.mp4; cp "$OUT" "$HOME/Downloads/$SLUG-v$N.mp4"
python3 scripts/register_export.py "$OUT" "$N" "$NOTES"
echo "Done: export v$N ($OUT, copy in ~/Downloads). Next: scripts/verify_export.py, measure_video.py, build_artifacts.py, then commit and back up."
