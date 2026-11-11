"""Find windows that show personal apps (contacts, agents, mail) from OCR + what is said there, as compact text.
Usage: python3 -I scripts/find_personal_windows.py [min_lines=2]   -> assets/personal_windows.json + printed list (write slides from it)"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "assets/ocr_frames.json")); subs = json.load(open(ROOT / "remotion/src/subs.json"))
minl = int(sys.argv[1]) if len(sys.argv) > 1 else 2
P = json.load(open(ROOT / "remotion/src/project.json"))
PAT = re.compile("|".join(P["personal_app_patterns"]), re.I)   # project.json
hits = sorted(int(f[:4]) - 1 for f, L in D.items() if sum(1 for l in L if PAT.search(l["t"])) >= minl)
spans = []
if hits:
    s = p = hits[0]
    for x in hits[1:]:
        if x - p > 6: spans.append([s, p]); s = x
        p = x
    spans.append([s, p])
res = []
for a, b in spans:
    a2, b2 = max(a - 1, 0), b + 4   # sampled every 2 s: the window can outlast the last hit
    said = " ".join(c["text"] for c in subs if c["to"] > a2 and c["from"] < b2)
    res.append({"from": a2, "to": b2, "said": said[:300]}); print(f"{a2}-{b2}s ({a2//60}:{a2%60:02d}-{b2//60}:{b2%60:02d}): {said[:160]}")
(ROOT / "assets/personal_windows.json").write_text(json.dumps(res, indent=1))
