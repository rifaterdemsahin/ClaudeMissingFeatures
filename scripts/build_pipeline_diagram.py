#!/usr/bin/env python3
"""Data for the tldraw page 'Video production pipeline': every stage as a box in its lane (MacBook, Claude, you), arrows for the order and the review loop,
and the places the results go (Azure, Key Vault, Drive, GitHub Pages). Source: assets/timings.json (same data as the Time & order page). Run: python3 -I scripts/build_pipeline_diagram.py
Writes pipeline/pipeline.json (read at runtime by the page, so changing the data needs no rebuild of the JavaScript)."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
T = json.load(open(ROOT / "assets/timings.json")); P = json.load(open(ROOT / "remotion/src/project.json"))
mb = T["measured_on"]
def secs(st):
    L = mb["raw_minutes"] if st["n"] <= 10 else mb["youtube_minutes"]
    if "LinkedIn and X" in st["stage"]: L = mb["linkedin_minutes"] + mb["x_minutes"]
    return st["fixed_s"] + st["rate"] * L * 60
fmt = lambda s: f"{s:.0f} s" if s < 90 else f"{s/60:.0f} min" if s < 5400 else f"{s/3600:.1f} h"
LANE = {"machine": 0, "claude": 1, "owner": 2}; COLOR = {"machine": "light-blue", "claude": "orange", "owner": "violet"}
W, H, GX, GY0, LH = 240, 112, 275, 150, 250
BANDS = [("1 · Prepare and ingest", lambda n: n <= 7), ("2 · Decide, render and check", lambda n: 8 <= n <= 14), ("3 · Publish, review and wrap up", lambda n: n >= 15)]
BH = 3 * LH + 210
nodes, edges, bands = [], [], []
band_of = lambda n: next(i for i, (_, f) in enumerate(BANDS) if f(n))
cols = {}; cnt = {}
for st in T["stages"]:
    n, b = st["n"], band_of(st["n"])
    if n == 5: cols[n] = (cols[4][0], 1)                    # Whisper runs beside the base render: same column, stacked below it
    else: cols[n] = (cnt.get(b, 0), 0); cnt[b] = cnt.get(b, 0) + 1
pos = lambda st: (60 + cols[st["n"]][0] * GX, GY0 + band_of(st["n"]) * BH + LANE[st["who"]] * LH + cols[st["n"]][1] * (H + 16))
for st in T["stages"]:
    x, y = pos(st)
    nodes.append({"id": f"s{st['n']}", "x": x, "y": y, "w": W, "h": H, "color": COLOR[st["who"]], "fill": "semi",
                  "text": f"{st['n']}. {st['stage']}\n{st['tool'].split(' (')[0][:36]}\n⏱ {fmt(secs(st))}" + (" (est.)" if "estimate" in st["basis"] else "")})
widest = max(cnt.values())
for i, (name, _) in enumerate(BANDS):
    top = GY0 + i * BH - 120
    bands.append({"name": name, "x": 20, "y": top, "w": 60 + (widest + (2 if i == 2 else 0)) * GX, "h": BH - 40})
    nodes.append({"id": f"band{i}", "kind": "text", "x": 50, "y": top + 10, "text": name, "color": "black", "size": "xl"})
    for lane, (key, txt) in enumerate((("machine", "🖥️ MacBook: local tools, 0 Claude tokens"), ("claude", "🤖 Claude: judgement from one page of text"), ("owner", "👤 You: record, review, decide"))):
        nodes.append({"id": f"lane{i}{key}", "kind": "text", "x": 60, "y": GY0 + i * BH + lane * LH - 40, "text": txt, "color": COLOR[key], "size": "m"})
nodes.append({"id": "inputs", "x": 60 + 2 * GX, "y": GY0 + 2 * LH + 0, "w": W, "h": H, "color": "green", "fill": "solid", "text": "🎥 Clips (.mp4) + voice (.WAV)\n~/Downloads/<Project>/"})
rx = 60 + (cnt[2] + 1) * GX; ry = GY0 + 2 * BH
for i, (id_, txt, colr) in enumerate((("azure", "☁️ Azure Blob (private)\nread-only links", "blue"), ("kv", "🔑 Key Vault\nstorage key + folder id", "yellow"), ("drive", "📦 Google Drive\nkit, spec, backups, videos", "green"), ("pages", "🌐 GitHub Pages\nthis site + player", "grey"), ("platforms", "▶️ YouTube · 💼 LinkedIn · ✖️ X\nyou share, I fill the post links", "red"))):
    nodes.append({"id": id_, "x": rx, "y": ry + i * (H + 30) - 60, "w": W, "h": H, "color": colr, "fill": "solid", "text": txt})
E = lambda a, b, label="", bend=0: edges.append({"from": a, "to": b, "label": label, "bend": bend})
for a, b in ((0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6), (5, 7), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (16, 18)):
    if any(s["n"] == a for s in T["stages"]) and any(s["n"] == b for s in T["stages"]): E(f"s{a}", f"s{b}")
E("inputs", "s3"); E("s17", "s8", "next round: only what changed", 140)
E("s15", "azure", "upload"); E("s1", "kv"); E("kv", "s15", "key", -80); E("s18", "drive", "backup"); E("s18", "pages", "push"); E("s16", "platforms", "approve"); E("pages", "platforms", "post links")
(ROOT / "pipeline").mkdir(exist_ok=True)
(ROOT / "pipeline/pipeline.json").write_text(json.dumps({"title": f"{P['title']}: video production pipeline", "bands": bands, "nodes": nodes, "edges": edges}, ensure_ascii=False, indent=1))
print(f"pipeline/pipeline.json: {len(nodes)} shapes, {len(edges)} arrows, {len(bands)} bands")
