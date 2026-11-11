"""Privacy check on the FINAL export, no images read by Claude: OCR it every 2 s and list any sensitive text still visible.
Usage: python3 -I scripts/verify_export.py [remotion/out/long.mp4]   -> assets/export_leaks.json, exit 1 if leaks"""
import json, re, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
v = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "remotion/out/long.mp4")
P = json.load(open(ROOT / "remotion/src/project.json"))
kw = "|".join(P["sensitive_keywords"])
extra = "|".join(P["verify_app_patterns"])          # personal app lists must be covered by slides (2+ lines in one frame)
subprocess.check_call([str(ROOT / "scripts/ocr_all.sh"), v, str(ROOT / "assets/export_ocr.json")])
D = json.load(open(ROOT / "assets/export_ocr.json")); leaks = []
_m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()) if (ROOT / "export_map.js").exists() else None
VIDEO_END = json.loads(_m.group(1))["total"] if _m else 1e9
_reg = json.load(open(ROOT / "assets/exports.json")) if (ROOT / "assets/exports.json").exists() else []   # a platform cut has its own timeline: use that export's own map
for _e in _reg:
    if _e.get("file") and pathlib.Path(_e["file"]).name == pathlib.Path(v).name and _e.get("map"): VIDEO_END = _e["map"]["total"]   # the intentional ending (summary, community CTA) starts here and is not checked
for f, L in sorted(D.items()):
    t = int(f[:4]) - 1
    if t >= VIDEO_END: continue
    apps = [l for l in L if re.search(extra, l["t"], re.I)]
    hits = [l for l in L if re.search(kw, l["t"], re.I)] + (apps if len(apps) >= 2 else [])
    for l in hits: leaks.append({"t": t, "text": l["t"][:80], "x": int(l["x"]), "y": int(l["y"])})
(ROOT / "assets/export_leaks.json").write_text(json.dumps(leaks, indent=1))
reg = json.load(open(ROOT / "assets/exports.json")) if (ROOT / "assets/exports.json").exists() else []   # remember the result for the Publish page
key = next((("v%d" % e["v"]) + ("" if e.get("platform", "youtube") == "youtube" else "-" + e["platform"]) for e in reg if e.get("file") and pathlib.Path(e["file"]).name == pathlib.Path(v).name), None)
if key:
    import datetime; ck = json.load(open(ROOT / "assets/export_checks.json")) if (ROOT / "assets/export_checks.json").exists() else {}
    ck[key] = {"privacy_leaks": len(leaks), "frames": len(D), "when": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}; (ROOT / "assets/export_checks.json").write_text(json.dumps(ck, indent=1))
print(f"{len(D)} frames checked, {len(leaks)} sensitive lines still visible")
for k in leaks[:25]: print(f"  {k['t']//60}:{k['t']%60:02d} {k['text']}  @({k['x']},{k['y']})")
sys.exit(1 if leaks else 0)
