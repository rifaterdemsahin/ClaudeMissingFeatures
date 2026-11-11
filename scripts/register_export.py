#!/usr/bin/env python3
"""Record an export in the version registry (assets/exports.json) and write exports.js for the player.
Usage: python3 scripts/register_export.py <file.mp4> <version> "<what changed in this version>" [--platform youtube|linkedin|x] [--map assets/maps/<p>.json] [--replace]
Stores: file, rendered time, length, size, short checksum, notes and the source<->export time map (from export_map.js) so the player can
convert times for THIS version even after later edits change the timeline. Never overwrite a version; use the next number."""
import json, pathlib, re, subprocess, sys, hashlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
f, v, notes = pathlib.Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else ""
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
platform = arg("--platform", "youtube")
P = json.load(open(ROOT / "remotion/src/project.json"))
reg = json.load(open(ROOT / "assets/exports.json")) if (ROOT / "assets/exports.json").exists() else []
if any(e["v"] == v and e.get("file") and e.get("platform", "youtube") == platform for e in reg) and "--replace" not in sys.argv: sys.exit(f"version v{v} ({platform}) is already registered; use the next number")
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))
h = hashlib.sha256(); h.update(f.read_bytes()[:50_000_000]); size = f.stat().st_size
mp = None
if arg("--map"): mp = json.load(open(ROOT / arg("--map")))
else:
    m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()); mp = json.loads(m.group(1)) if m else None
entry = {"v": v, "platform": platform, "file": str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f), "rendered": datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
         "seconds": round(dur, 1), "size_mb": round(size / 1048576, 1), "sha12": h.hexdigest()[:12], "notes": notes, "map": mp}
reg = [e for e in reg if not (e["v"] == v and e.get("platform", "youtube") == platform)] + [entry]; reg.sort(key=lambda e: (e["v"], {"youtube": 0, "linkedin": 1, "x": 2}.get(e.get("platform", "youtube"), 9)))
(ROOT / "assets/exports.json").write_text(json.dumps(reg, indent=1))
(ROOT / "exports.js").write_text("window.EXPORTS = " + json.dumps([{k: e.get(k) for k in ("v", "platform", "file", "rendered", "seconds", "size_mb", "notes", "map")} for e in reg]) + ";")
md = ROOT / "metadata.md"
if md.exists() and platform == "youtube":
    t = md.read_text(); line = f"Video: `~/Downloads/{P.get('slug', 'video')}-youtube-v{v}.mp4` (export v{v}, {entry['seconds']} s, 1920x1080, 30 fps)" if platform == "youtube" else None
    md.write_text(re.sub(r"^Video:.*$", line, t, count=1, flags=re.M) if re.search(r"^Video:", t, re.M) else t)
print(f"registered export v{v} ({platform}): {entry['seconds']} s, {entry['size_mb']} MB, {entry['sha12']}")
