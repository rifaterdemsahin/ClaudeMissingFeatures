#!/bin/zsh
# Reuse check: the reusable code must contain NO words that belong to one video. The words come from remotion/src/project.json
# (title, brand, community, thumbnail text, sensitive words, personal-app patterns). Data files, generated pages, the spec and docs are not scanned.
# Usage: scripts/check_reuse.sh      (exit 1 if a project-specific word is found in reusable code)
cd "$(dirname "$0")/.." || exit 1
TERMS=$(python3 - <<'PY'
import json,re
p=json.load(open("remotion/src/project.json")); t=set()
for k in ("title","brand"): t.add(p.get(k,""))
t.update([p["thumb"].get("line1",""),p["thumb"].get("line2",""),p["community"].get("name",""),p["community"].get("display",""),p["community"].get("url","").replace("https://","").replace("http://","").replace("www.","")])
t.update(p.get("sensitive_keywords",[])); t.update(x for x in p.get("personal_app_patterns",[]) if len(x)>3)
print("\n".join(sorted(x for x in t if len(x)>3)))
PY
)
[ -z "$TERMS" ] && { echo "project.json has no terms to check"; exit 0; }
FILES=(scripts/*.py scripts/*.sh scripts/*.swift remotion/src/*.ts remotion/src/*.tsx remotion/remotion.config.ts nav.js player.html kit/new-video.sh)
bad=0
while IFS= read -r term; do
  hits=$(grep -nIiF -- "$term" $FILES 2>/dev/null | grep -v "check_reuse.sh")
  [ -n "$hits" ] && { echo "❌ \"$term\" is hard-coded in reusable code:"; echo "$hits" | cut -c1-140 | head -6; bad=1; }
done <<< "$TERMS"
[ $bad = 0 ] && echo "✅ reuse check passed: no project-specific words in reusable code ($(echo "$TERMS" | wc -l | tr -d ' ') terms checked)" || echo "Move those words into remotion/src/project.json (or another data file) and read them from there."
exit $bad
