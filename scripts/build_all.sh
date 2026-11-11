#!/bin/zsh
# Build the WHOLE website from data + templates, in the right order, then check it. Safe to run any time; stages skip when their inputs are missing.
# Usage: scripts/build_all.sh        (see MASTER_SPEC.md "Build the whole website")
cd "$(dirname "$0")/.." || exit 1
TITLE=$(python3 -c "import json;print(json.load(open('remotion/src/project.json'))['title'])")
# 1. hand-written pages come from the templates when a project does not have them yet
for f in index preprod prod postprod player run architecture; do
  [ -f $f.html ] || { [ -f templates/$f.html ] && sed "s/{{TITLE}}/$TITLE/g" templates/$f.html > $f.html && echo "created $f.html from the template"; }
done
[ -f README.md ] || echo "# $TITLE" > README.md
# 2. data that feeds the pages (each stage only when its inputs exist)
[ -f assets/whisper_words.json ] && python3 -I scripts/build_subs.py assets/whisper_words.json "$(cat assets/whisper_offset.txt 2>/dev/null || echo 0)" | tail -1
[ -f assets/chapters.json ] && [ -f export_map.js ] && python3 -I scripts/build_chapters.py | tail -1
python3 -I scripts/build_edl.py
[ -f assets/metrics.json ] && python3 -I scripts/build_okr.py | tail -1
python3 -I scripts/build_architecture.py
python3 -I scripts/build_artifacts.py | tail -1        # works without an export too (cards without pictures)
# 3. markdown pages (spec, readme, environment, metadata, edl) + project.js, after their sources are final
python3 -I scripts/build_site.py | tail -1
# 4. check everything resolves
python3 -I scripts/check_site.py
