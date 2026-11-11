"""OCR (assets/ocr_frames.json, every 2 s, frame NNNN.jpg = second NNNN-1) -> blur boxes + slide cover -> remotion/src/overlays.json.
Usage: python3 -I scripts/build_blurs.py     Re-run after changing KEYWORDS or the slides below.
Rules: A) chat-title list in the Claude sidebar  B) sensitive words anywhere  C) the pasted screenshot's mini sidebar (anchored to the line under it)."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "assets/ocr_frames.json"))
OV = json.load(open(ROOT / "remotion/src/overlays.json"))
P = json.load(open(ROOT / "remotion/src/project.json"))
KEYWORDS = "|".join(P["sensitive_keywords"])   # project.json
NAV = re.compile(r"^(New|Search|Projects|Artifacts|Scheduled|Dispatch( Beta)?|Design|Customize|Pinned.*|View all|Recents.*|Show( \d+)? more|Erdem.*|Claude|Docs|Slides|Data)$", re.I)
covered = [(OV["intro_card"]["from"], OV["intro_card"]["to"])] + [(s["from"], s["to"]) for s in OV["slides"]]
is_covered = lambda t: any(a <= t < b for a, b in covered)
raw = []   # (t, rule, x, y, w, h)
for f, L in sorted(D.items()):
    t = int(f[:4]) - 1
    if is_covered(t): continue
    side = [l for l in L if 120 <= l["x"] <= 640 and l["w"] < 500 and 100 <= l["y"] <= 1040 and not NAV.match(l["t"].strip(" •")) and len(l["t"]) > 3 and "Erdem" not in l["t"]]
    claude = any((re.match(r"(Scheduled|Dispatch|Customize|Projects|Recents|Pinned|Show)", l["t"]) and l["x"] < 300) or ("Erdem" in l["t"] and l["x"] < 300 and l["y"] > 1030) for l in L)
    navvis = any(re.match(r"(Scheduled|Customize|Projects)", l["t"]) and l["x"] < 300 and l["y"] < 420 for l in L)
    if claude and len(side) >= 3:
        # two fixed boxes: nav visible -> chat list below it; list scrolled to the top -> whole column
        raw.append((t, "A", 128, 462 if navvis else 95, 484, (1030 - 462) if navvis else (1030 - 95)))
    for l in L:
        if re.search(KEYWORDS, l["t"], re.I) and not (claude and 120 <= l["x"] <= 640):
            raw.append((t, "B", l["x"] - 10, l["y"] - 8, l["w"] + 20, l["h"] + 16))
    anc = [l for l in L if "Checking which Artifacts" in l["t"]]
    if anc: raw.append((t, "C", 1065, max(anc[0]["y"] - 280, 0), 185, 232))
# screenshot just pasted (before Claude's reply line exists): fixed box
for t in range(226, 236, 2):
    if not is_covered(t): raw.append((t, "C", 1065, 90, 185, 270))
# merge: same rule + similar box on consecutive samples -> one interval
raw.sort(key=lambda r: (r[1], r[0]))
out, cur = [], {}
close = lambda a, b: all(abs(a[i] - b[i]) < 16 for i in range(4))
for t, rule, x, y, w, h in raw:
    box = (x, y, w, h); c = cur.get((rule, round(x / 40)))
    if c and t - c["to"] <= 2.01 and close(box, c["box"]):
        c["to"] = t + 1; c["box"] = tuple(max(a, b) if i >= 2 else min(a, b) for i, (a, b) in enumerate(zip(box, c["box"])))
        c["box"] = (c["box"][0], c["box"][1], c["box"][2], max(c["box"][3], h))
    else:
        if c: out.append(c)
        cur[(rule, round(x / 40))] = c = {"from": t - 1 if t > 0 else 0, "to": t + 1, "box": box, "rule": rule}
out += list(cur.values())
seen = set(); res = []
for c in sorted(out, key=lambda c: c["from"]):
    k = (c["from"], c["to"], c["rule"], c["box"])
    if k in seen: continue
    seen.add(k); x, y, w, h = c["box"]
    res.append({"from": float(c["from"]), "to": float(c["to"]), "x": int(x), "y": int(max(y, 0)), "w": int(w), "h": int(h), "rule": c["rule"]})
PAD = 1.5   # OCR samples every 2 s: widen every box so transitions cannot leak
for r in res: r["from"] = max(0.0, r["from"] - PAD); r["to"] = r["to"] + PAD
OV["blurs"] = res
(ROOT / "remotion/src/overlays.json").write_text(json.dumps(OV, indent=1))
from collections import Counter
print(len(res), "blur boxes", dict(Counter(r["rule"] for r in res)))
