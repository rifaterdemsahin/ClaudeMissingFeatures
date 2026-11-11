"""Privacy check on the FINAL export, no images read by Claude: OCR it every 2 s and list any sensitive text still visible.
Usage: python3 -I scripts/verify_export.py [remotion/out/long.mp4]   -> assets/export_leaks.json, exit 1 if leaks"""
import json, re, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
v = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "remotion/out/long.mp4")
kw = re.search(r'KEYWORDS = r"([^"]+)"', (ROOT / "scripts/build_blurs.py").read_text()).group(1)
extra = r"skool|linkedin|rag manager|nda agent|prospecting"          # personal app lists must be covered by slides (2+ lines in one frame)
subprocess.check_call([str(ROOT / "scripts/ocr_all.sh"), v, str(ROOT / "assets/export_ocr.json")])
D = json.load(open(ROOT / "assets/export_ocr.json")); leaks = []
for f, L in sorted(D.items()):
    t = int(f[:4]) - 1
    apps = [l for l in L if re.search(extra, l["t"], re.I)]
    hits = [l for l in L if re.search(kw, l["t"], re.I)] + (apps if len(apps) >= 2 else [])
    for l in hits: leaks.append({"t": t, "text": l["t"][:80], "x": int(l["x"]), "y": int(l["y"])})
(ROOT / "assets/export_leaks.json").write_text(json.dumps(leaks, indent=1))
print(f"{len(D)} frames checked, {len(leaks)} sensitive lines still visible")
for k in leaks[:25]: print(f"  {k['t']//60}:{k['t']%60:02d} {k['text']}  @({k['x']},{k['y']})")
sys.exit(1 if leaks else 0)
