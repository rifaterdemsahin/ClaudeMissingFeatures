#!/bin/zsh
# Scaffold a new long-form video project from the kit. Usage: ./new-video.sh "Title" duration_seconds [slug]
cd "$(dirname "$0")" || exit 1
[ -f templates/index.html ] || { echo "run from an unpacked kit (templates/ missing)"; exit 1; }
[ -n "$(git status --porcelain 2>/dev/null)" ] && { echo "refusing: this folder has uncommitted git changes. Use a fresh folder."; exit 1; }
TITLE="${1:?title}"; DUR="${2:?duration seconds}"; SLUG="${3:-$(echo "$TITLE" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-')}"
FRAMES=$(python3 -c "print(round($DUR*30))")
sed -i '' "s/DURATION = [0-9]*;/DURATION = $FRAMES;/" remotion/src/theme.ts
for f in architecture index preprod prod postprod player run; do sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g" templates/$f.html > $f.html; done
sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g; s/{{FOLDER}}/$TITLE/g" templates/BRIEF.template.md > BRIEF.md
sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g" templates/metadata.template.md > metadata.md
sed "s/{{TITLE}}/$TITLE/g" templates/SANITY_CHECK.template.md > SANITY_CHECK.md
[ -f README.md ] || printf "> 🌐 **Live site (GitHub Pages):** https://<user>.github.io/<repo>/  (enable Pages: MASTER_SPEC.md section 7a)\n\n# %s\n" "$TITLE" > README.md
echo '[]' > remotion/src/subs.json; echo 'window.SUBS = [];' > subs.js
git init -q 2>/dev/null; python3 -I scripts/build_edl.py; python3 -I scripts/build_site.py
echo "Done. Next: MASTER_SPEC.md section 1 (sync clips, render base, transcribe). Run: see run.html"
