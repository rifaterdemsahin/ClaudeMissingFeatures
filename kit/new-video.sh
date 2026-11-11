#!/bin/zsh
# Scaffold a new long-form video project from the kit. Usage: ./new-video.sh "Title" duration_seconds [slug] [community name] [community url] [platform]
# Everything project-specific lives in remotion/src/project.json (title, brand, community, sensitive words, caption fixes).
cd "$(dirname "$0")" || exit 1
[ -f templates/index.html ] || { echo "run from an unpacked kit (templates/ missing)"; exit 1; }
[ -n "$(git status --porcelain 2>/dev/null)" ] && { echo "refusing: this folder has uncommitted git changes. Use a fresh folder."; exit 1; }
TITLE="${1:?title}"; DUR="${2:?duration seconds}"; SLUG="${3:-$(echo "$TITLE" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-')}"
COMM_NAME="${4:-}"; COMM_URL="${5:-}"; COMM_PLATFORM="${6:-}"
FRAMES=$(python3 -c "print(round($DUR*30))")
sed -i '' "s/DURATION = [0-9]*;/DURATION = $FRAMES;/" remotion/src/theme.ts
for f in architecture index preprod prod postprod player run; do sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g" templates/$f.html > $f.html; done
sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g; s/{{FOLDER}}/$TITLE/g" templates/BRIEF.template.md > BRIEF.md
sed "s/{{TITLE}}/$TITLE/g; s/{{SLUG}}/$SLUG/g" templates/metadata.template.md > metadata.md
sed "s/{{TITLE}}/$TITLE/g" templates/SANITY_CHECK.template.md > SANITY_CHECK.md
[ -f README.md ] || printf "> 🌐 **Live site (GitHub Pages):** https://<user>.github.io/<repo>/  (enable Pages: MASTER_SPEC.md section 7a)\n\n# %s\n" "$TITLE" > README.md
python3 - "$TITLE" "$COMM_NAME" "$COMM_URL" "$COMM_PLATFORM" "$SLUG" <<'PY'
import json,sys,re
t,n,u,pl=sys.argv[1:5]; p=json.load(open('remotion/src/project.json')); p['title']=p['brand']=t; p['slug']=sys.argv[5] if len(sys.argv)>5 else re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-'); p['thumb']['line1']=t; p['community']={'name':n,'platform':pl,'url':u,'display':re.sub(r'^https?://(www\.)?','',u)}
json.dump(p,open('remotion/src/project.json','w'),indent=1)
PY
python3 -c "import json,datetime;d=json.load(open('assets/timings.json'));d['started']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M');json.dump(d,open('assets/timings.json','w'),indent=1,ensure_ascii=False)"
echo '[]' > remotion/src/subs.json; echo 'window.SUBS = [];' > subs.js
git init -q 2>/dev/null; scripts/build_all.sh
echo "Done. Next: MASTER_SPEC.md section 1 (sync clips, render base, transcribe). Run: see run.html"
