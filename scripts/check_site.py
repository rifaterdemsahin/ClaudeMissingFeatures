#!/usr/bin/env python3
"""Check the whole website: every menu item exists, every page loads project.js + nav.js, every local link/src resolves.
Usage: python3 -I scripts/check_site.py        (exit 1 if something is broken)
Optional media that only exists after rendering (long.mp4, export.mp4, exports/*.mp4, artifacts/*.jpg) is not required."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
OPTIONAL = re.compile(r"^(long\.mp4|export\.mp4|exports/.*\.mp4|artifacts/.*\.jpg|publish_links\.js|azure_links\.js)$")
bad = []
nav = (ROOT / "nav.js").read_text()
menu = [m for m in re.findall(r'\["([\w./-]+\.html)"\s*,', nav) if not m.startswith("http")]
for m in sorted(set(menu)):
    if not (ROOT / m).exists(): bad.append(f"menu item missing page: {m}")
pages = sorted(p for p in ROOT.glob("*.html"))
for p in pages:
    t = p.read_text()
    if 'src="nav.js"' not in t: bad.append(f"{p.name}: no nav.js")
    if 'src="project.js"' not in t: bad.append(f"{p.name}: no project.js")
    for ref in re.findall(r'(?:href|src)=["\']([^"\'#]+)["\']', t):
        if re.match(r"^(https?:|mailto:|data:|blob:|javascript:|//)", ref) or "{{" in ref or "${" in ref: continue
        ref = ref.split("?")[0]
        if OPTIONAL.match(ref): continue
        if not (ROOT / ref).exists(): bad.append(f"{p.name}: broken link {ref}")
for need in ("project.js", "nav.js", "subs.js", "exports.js", "export_map.js", "chapters.js"):
    if not (ROOT / need).exists(): bad.append(f"missing support file: {need}")
print(f"{len(pages)} pages, {len(set(menu))} menu items checked")
print("\n".join("❌ " + b for b in bad) if bad else "✅ site check passed: every menu item, link and script resolves")
sys.exit(1 if bad else 0)
