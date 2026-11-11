#!/usr/bin/env python3
"""OKRs + value recognition + score -> the OKR block in preprod.html (between <!--OKR--> and <!--/OKR-->).
Usage: python3 scripts/measure_video.py && python3 -I scripts/build_okr.py
Inputs: assets/okr.json (objectives, key results, rubric), assets/metrics.json (measured), remotion/src/overlays.json + export_map.js (timecodes).
Reusable: for a new video edit assets/okr.json (start from kit/okr.template.json); nothing here is specific to one video."""
import html, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p))
import sys
if not (ROOT / "assets/okr.json").exists() or not (ROOT / "assets/metrics.json").exists() or not (ROOT / "export_map.js").exists():
    print("build_okr: need assets/okr.json, assets/metrics.json (run scripts/measure_video.py after the export) and export_map.js"); sys.exit(0)
okr, X, ov, P = J("assets/okr.json"), J("assets/metrics.json"), J("remotion/src/overlays.json"), J("remotion/src/project.json")
_m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()); M = json.loads(_m.group(1))
out = lambda t: next((o + (t - a) / r for a, b, r, m, o in M["segs"] if a <= t < b + 1e-9), t)
e = html.escape
fill = lambda s: re.sub(r"\{(\w+)\}", lambda m: str(X.get(m.group(1), "n/a")), s)
tc = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"

def evaluate(kr):
    if kr.get("manual"): return "open", "to measure"
    a = X.get(kr["metric"]); op = kr["op"]
    if a is None: return "open", "n/a"
    if op == "true": ok, near = bool(a), False
    elif op == "<=": ok = a <= kr["target"]; near = not ok and a <= kr["target"] * 1.1 + 0.5
    elif op == ">=": ok = a >= kr["target"]; near = not ok and a >= kr["target"] * 0.9 - 0.5
    else: ok = abs(a - kr["target"]) <= kr["tol"]; near = False
    shown = ("yes" if a else "no") if op == "true" else f"{a:g} {kr.get('unit', '')}".strip()
    return ("met" if ok else "almost" if near else "missed"), shown
ICON = {"met": "✅ met", "almost": "🟡 almost", "missed": "❌ missed", "open": "⏳ open"}
def target_text(kr):
    if kr.get("manual"): return kr["target"]
    op = kr["op"]; u = kr.get("unit", "")
    return "yes" if op == "true" else (f"within ±{kr['tol']:g} of {kr['target']:g} {u}" if op == "within" else f"{op} {kr['target']:g} {u}").strip()

counts = {"met": 0, "almost": 0, "missed": 0, "open": 0}; obj_html = []
for o in okr["objectives"]:
    rows = []
    for kr in o["krs"]:
        st, shown = evaluate(kr); counts[st] += 1
        rows.append(f"<tr><td>{e(kr['id'])}</td><td>{e(kr['text'])}</td><td>{e(target_text(kr))}</td><td><b>{e(shown)}</b></td><td class='st {st}'>{ICON[st]}</td></tr>")
    obj_html.append(f"<h4>{e(o['id'])}: {e(o['title'])}</h4><table><tr><th>KR</th><th>Key result</th><th>Target</th><th>Actual</th><th>Status</th></tr>{''.join(rows)}</table>")

# value recognition checkpoints (timecodes from the real edit data)
cp = []
ic, sl, im = ov["intro_card"], (ov["slides"] or [None])[0], (ov["images"] or [None])[0]
cp.append(("1. Recognise my situation", "Title card, then the slide “" + (sl["title"] if sl else "") + "”", 0, "I see my own problem named in the first seconds."))
cp.append(("2. First useful action", "First chapter after the intro", X.get("time_to_first_action_s") or 0, "I learn something I can try right now."))
if im: cp.append(("3. See the proof", "Picture card" + (": " + (im.get("caption", "") + " " + im.get("caption2", "")).strip() if im.get("caption") else ""), round(out(im["from"]), 1), "I see exactly what is expected next to what I have."))
osum = next((p for p in ov.get("outro", []) if p["kind"] != "cta"), None); ocat = next((p for p in ov.get("outro", []) if p["kind"] == "cta"), None); t = M["total"]
if osum: cp.append(("4. Get the recap", "“" + osum["title"] + "” (" + str(len(osum.get("bullets", []))) + " points)", round(t, 1), "I leave with the answer in one slide.")); t += osum["seconds"]
if ocat: cp.append(("5. Know what next", f"Card: {ocat['line']} ({ocat['url']})", round(t, 1), "I know where to learn it in depth."))
cp_html = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td><a href='player.html?v=exp&amp;t={max(c - 1, 0):.1f}' target='_blank'>{tc(c)}</a></td><td>{e(d)}</td></tr>" for a, b, c, d in cp)

# score
rows, total, gain = [], 0.0, 0.0
for r in okr["score"]["rows"]:
    sc = r.get("score"); pts = r["weight"] * (sc or 0) / 10; total += pts; gain += r.get("gain", 0)
    rows.append(f"<tr><td>{e(r['dimension'])}</td><td>{r['weight']}</td><td><div class='bar'><i style='width:{(sc or 0) * 10}%'></i></div><b>{str(sc) + '/10' if sc is not None else 'to score'}</b></td><td>{pts:.1f}</td><td>{e(fill(r['evidence']))}</td><td>{e(fill(r['improve']))}{(' <b>(+' + format(r['gain'], 'g') + ')</b>') if r.get('gain') else ''}</td></tr>")
grade = "A (excellent)" if total >= 90 else "B+ (very good)" if total >= 80 else "B (good)" if total >= 70 else "C (needs work)" if total >= 60 else "D (rework)"
page = f"""<!--OKR-->
<style>.okr .bar{{background:#2a2a38;border-radius:6px;height:10px;width:110px;display:inline-block;margin-right:8px;vertical-align:middle}}.okr .bar i{{display:block;height:100%;background:#ff7a3d;border-radius:6px}}
.okr .st.met{{color:#4ade80}}.okr .st.almost{{color:#facc15}}.okr .st.missed{{color:#f87171}}.okr .st.open{{color:#9ca3af}}.okr .big{{font-size:44px;font-weight:900;color:#ff7a3d;line-height:1}}.okr .box{{background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:12px 16px;margin:10px 0}}</style>
<div class="okr">
<h2 id="okr">🎯 Objectives and key results (OKRs)</h2>
<p>Set before the video is judged; measured from the finished export (<code>scripts/measure_video.py</code>). Status: ✅ met · 🟡 within 10% · ❌ missed · ⏳ needs YouTube data after publishing. <b>{counts['met']} met, {counts['almost']} almost, {counts['missed']} missed, {counts['open']} open.</b></p>
{''.join(obj_html)}

<h2 id="value">💎 Value recognition</h2>
<div class="box"><b>Value proposition.</b> {e(okr['value_proposition'])}</div>
<p>Value only counts when the viewer <b>recognises</b> it. These are the moments where that happens, with export timecodes (click to check them in the <a href="player.html">player</a>):</p>
<table><tr><th>Moment</th><th>What the viewer sees</th><th>Export time</th><th>What the viewer concludes</th></tr>{cp_html}</table>

<h3>Score: how clearly is the value recognised?</h3>
<div class="box" style="display:flex;gap:24px;align-items:center;flex-wrap:wrap"><div><div class="big">{total:.1f}<span style="font-size:20px"> / 100</span></div><div>Grade <b>{grade}</b></div></div>
<div style="flex:1;min-width:260px">{e(okr['score']['scale'])}<br>With the proposed improvements (about <b>+{gain:g}</b> points) the estimate is <b>{min(total + gain, 100):.1f}</b>. Nothing proposed has been applied: the owner decides.</div></div>
<table><tr><th>Dimension</th><th>Weight</th><th>Score</th><th>Points</th><th>Evidence (measured)</th><th>How to raise it</th></tr>{''.join(rows)}</table>
<h3>After publishing</h3><ul>{''.join('<li>' + e(x) + '</li>' for x in okr.get('after_publish', []))}</ul>
<p style="opacity:.7">Generated by <code>scripts/build_okr.py</code> from <code>assets/okr.json</code> and <code>assets/metrics.json</code>.</p>
</div>
<!--/OKR-->"""
pp = ROOT / "preprod.html"; s = pp.read_text()
if "<!--OKR-->" in s: s = re.sub(r"<!--OKR-->.*?<!--/OKR-->", lambda m: page, s, flags=re.S)
else:
    k = s.index("<p>Next:") if "<p>Next:" in s else s.index("</main>"); s = s[:k] + page + "\n" + s[k:]
pp.write_text(s)
(ROOT / "assets/okr_result.json").write_text(json.dumps({"score": round(total, 1), "grade": grade, "kr": counts, "potential": round(min(total + gain, 100), 1)}, indent=1))
print(f"OKR block written: score {total:.1f}/100 {grade}; KRs {counts}")
