#!/usr/bin/env python3
"""Script page: the whole spoken script by chapter (final captions) with source + export timecodes that open the player, every caption change
(before -> after), the subtitle issues and how each was fixed, and what still needs the owner's ear.
Run: python3 -I scripts/build_script.py      -> script.html      (inputs: remotion/src/subs.json, assets/*.json, export_map.js; reusable)"""
import html, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p, d=None: json.load(open(ROOT / p)) if (ROOT / p).exists() else d
P, subs, cuts, ov = J("remotion/src/project.json"), J("remotion/src/subs.json", []), J("remotion/src/cuts.json", []), J("remotion/src/overlays.json", {})
chapters, issues, rep, raw = J("assets/chapters.json", []), J("assets/subtitle_issues.json", []), J("assets/subtitle_report.json", {}), J("assets/whisper_words.json", {"segments": []})
reg = J("assets/exports.json", []); latest = max([e["v"] for e in reg if e.get("file")] or [0])
_m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()) if (ROOT / "export_map.js").exists() else None
M = json.loads(_m.group(1)) if _m else {"segs": [[0, 1e9, 1, False, 0]], "inserts": [], "total": 0}
off = float((ROOT / "assets/whisper_offset.txt").read_text()) if (ROOT / "assets/whisper_offset.txt").exists() else 0.0
e = html.escape
def out(t):
    for a, b, r, m, o in M["segs"]:
        if a <= t < b + 1e-9: return o + (t - a) / r
    return None
tc = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
incut = lambda t: any(a <= t < b for a, b in cuts)
muted = lambda t: any(s.get("mute") and s["from"] <= t < s["to"] for s in ov.get("speedups", []))
def link(t, label=None):
    o = out(t)
    return f"<a target='_blank' href='player.html?v=exp&amp;t={max(o - 1, 0):.1f}'>{label or tc(o)}</a>" if o is not None else "<span title='cut from the video'>✂️</span>"

# ---- before -> after (same rules as build_subs.py)
fixes = [(re.compile(a), b) for a, b in P.get("caption_fixes", [])]
def fixed(t):
    for rx, rep_ in fixes: t = rx.sub(rep_, t)
    return re.sub(r"\s+", " ", t).strip()
changes = []
for s in raw["segments"]:
    before = re.sub(r"\s+", " ", s["text"]).strip(); after = fixed(before); t = s["start"] - off
    if after != before and not incut(t): changes.append((t, before, after))

# ---- script by chapter
ch = sorted([(c[0], c[1]) for c in chapters]) or [(0, "Script")]
words = sum(len(c["words"]) for c in subs); speak = sum(min(w["to"] - w["from"], 1.2) for c in subs for w in c["words"])
sections = []
for i, (t0, name) in enumerate(ch):
    t1 = ch[i + 1][0] if i + 1 < len(ch) else 1e9
    rows = []
    for c in subs:
        if not (t0 <= c["from"] < t1): continue
        cls, mark = ("cut", "✂️ ") if incut(c["from"]) else (("mute", "🔇 ") if muted(c["from"]) else ("", ""))
        rows.append(f"<tr class='{cls}'><td class='t'>{link(c['from'])}</td><td>{mark}{e(c['text'])}</td></tr>")
    o0 = out(t0)
    sections.append(f"<details class='pn' open><summary>{e(name)} <span class='m'>source {tc(t0)} · export {tc(o0) if o0 is not None else '✂️'} · {len(rows)} lines</span></summary><div class='pnb'><table class='sc'>{''.join(rows) or '<tr><td>(no speech)</td></tr>'}</table></div></details>")
ICON = {"fixed": "✅ fixed", "review": "👂 needs your ear", "by design": "ℹ️ by design", "known limit": "🟡 known limit"}
iss = "".join(f"<tr><td>{e(x['id'])}</td><td class='st {x['status'].replace(' ', '')}'>{ICON.get(x['status'], x['status'])}</td><td>{e(x['issue'])}</td><td>{e(x['found'])}</td><td>{e(x['fix'])}</td><td><code>{e(x['where'])}</code></td></tr>" for x in issues)
chg = "".join(f"<tr><td class='t'>{link(t)}</td><td class='bf'>{e(b)}</td><td class='af'>{e(a)}</td></tr>" for t, b, a in changes)
nfix = sum(1 for x in issues if x["status"] == "fixed"); nrev = sum(1 for x in issues if x["status"] == "review")
met = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in [("Captions (cues)", len(subs)), ("Words", words), ("Speaking time", f"{speak / 60:.1f} min"), ("Lines changed by the fix rules", len(changes)),
      ("Words Whisper was unsure of (probability under 0.5)", len(rep.get("low_confidence", []))), ("Stutters left in the captions", len(rep.get("stutters", []))), ("Captions shown under 0.7 s", len(rep.get("flicker", []))),
      ("Caption fix rules (project.json)", len(fixes)), ("Issues fixed / need the owner's ear", f"{nfix} / {nrev}")])
PAGE = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>script</title>
<style>.pn{{background:#14141c;border:1px solid #2a2a38;border-radius:10px;margin:10px 0}}.pn>summary{{cursor:pointer;padding:10px 14px;font-weight:700;list-style:none}}.pn>summary::-webkit-details-marker{{display:none}}.pn>summary::before{{content:"▸ ";color:#ff7a3d}}.pn[open]>summary::before{{content:"▾ "}}.pnb{{padding:0 14px 12px}}
.m{{font-weight:400;opacity:.65;font-size:13px;margin-left:8px}}table.sc td{{border:0;padding:3px 8px;vertical-align:top}}table.sc td.t{{white-space:nowrap;width:70px;font-variant-numeric:tabular-nums}}tr.cut td,tr.mute td{{opacity:.5}}tr.cut td:last-child{{text-decoration:line-through}}
.bf{{color:#f87171}}.af{{color:#4ade80}}.st.fixed{{color:#4ade80}}.st.review{{color:#facc15;font-weight:700}}.st.bydesign,.st.knownlimit{{color:#9ca3af}}#q{{background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;padding:8px 10px;min-width:260px}}
.tools{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:10px 0}}</style></head><body><main>
<h1>📜 Script and subtitles</h1>
<p>The whole spoken script (the final captions), by chapter. Click a time to open the <a href="player.html">player</a> there (latest export{f" v{latest}" if latest else ""}). ✂️ = cut from the video, 🔇 = muted speed-up (no captions). Download for YouTube: <a href="subtitles.srt">subtitles.srt</a> · <a href="subtitles.vtt">subtitles.vtt</a> (on the final export timeline). To fix a word, add a rule to <code>remotion/src/project.json › caption_fixes</code> and run <code>scripts/build_all.sh</code>.</p>
<div class="tools"><input id="q" placeholder="Search the script…"><span id="n" style="opacity:.7"></span></div>
<details class="pn" open><summary>🧪 Subtitle quality: {nfix} issues fixed, {nrev} need your ear</summary><div class="pnb"><table><tr><th>#</th><th>Status</th><th>Issue</th><th>How it was found</th><th>How it is fixed</th><th>Where</th></tr>{iss}</table>
<h3>Measured</h3><table>{met}</table><p style="opacity:.7">Generated by <code>scripts/check_subtitles.py</code> (Whisper probabilities, stutters, reading speed, flicker). Re-run after every change.</p></div></details>
<details class="pn"><summary>🔧 Every caption change: before → after ({len(changes)} lines)</summary><div class="pnb"><table class="sc"><tr><th>Time</th><th>Heard</th><th>Caption</th></tr>{chg}</table></div></details>
<h2>The script</h2>
{''.join(sections)}
</main><script src="project.js"></script><script src="nav.js"></script><script>
const q=document.getElementById("q"),n=document.getElementById("n");
q.oninput=()=>{{const s=q.value.toLowerCase().trim();let k=0;document.querySelectorAll("table.sc tr").forEach(r=>{{if(!r.querySelector("td.t")){{return}}const hit=!s||r.textContent.toLowerCase().includes(s);r.style.display=hit?"":"none";if(hit&&s)k++}});
  if(s)document.querySelectorAll("details.pn").forEach(d=>{{if(d.querySelector("table.sc"))d.open=true}});n.textContent=s?k+" lines match":""}};
</script></body></html>'''
(ROOT / "script.html").write_text(PAGE)
print(f"script.html: {len(subs)} captions in {len(sections)} sections, {len(changes)} changed lines, {len(issues)} issues ({nfix} fixed, {nrev} need review)")
