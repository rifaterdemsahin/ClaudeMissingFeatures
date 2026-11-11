#!/usr/bin/env python3
"""Time and order page (timeline.html): every stage of the flow in order, who does it (machine, Claude, owner), how long it took (measured) or is estimated, what runs in
parallel, what to prepare to save time, plus a calculator for the next video. Data: assets/timings.json (+ git for the elapsed time). Run: python3 -I scripts/build_timeline.py"""
import datetime, html, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
T = json.load(open(ROOT / "assets/timings.json")); e = html.escape
mb = T["measured_on"]
def secs(st, raw=mb["raw_minutes"], yt=mb["youtube_minutes"], li=mb["linkedin_minutes"], x=mb["x_minutes"]):
    n = st["n"]; L = raw if n <= 10 else (li if "LinkedIn" in st["stage"] else yt)
    return st["fixed_s"] + st["rate"] * L * 60
fmt = lambda s: (f"{s:.0f} s" if s < 90 else f"{s/60:.0f} min" if s < 5400 else f"{s/3600:.1f} h")
ICON = {"machine": "🖥️ MacBook", "claude": "🤖 Claude", "owner": "👤 You"}
rows, tot = [], {"machine": 0, "claude": 0, "owner": 0}
phase = None
for st in T["stages"]:
    s = secs(st)
    if "LinkedIn and X" in st["stage"]: s = st["fixed_s"] + st["rate"] * (mb["linkedin_minutes"] + mb["x_minutes"]) * 60
    if st["n"] in (13,): s = st["fixed_s"] + st["rate"] * (mb["youtube_minutes"] + mb["linkedin_minutes"] + mb["x_minutes"]) * 60 * 0.75
    tot[st["who"]] += s if st["n"] != 17 else 0
    rows.append((st, s))
total = sum(tot.values())
now = datetime.datetime.now(); started = datetime.datetime.strptime(T["started"], "%Y-%m-%d %H:%M") if T.get("started") else now; el = (now - started).total_seconds()
mx = max(s for _, s in rows)
tr = "".join(f"<tr><td>{st['n']}</td><td>{e(st['phase'])}</td><td><b>{e(st['stage'])}</b><br><code>{e(st['tool'])}</code></td><td>{ICON[st['who']]}</td>"
             f"<td><div class='bar'><i class='{st['who']}' style='width:{max(2, s / mx * 100):.0f}%'></i></div><b>{fmt(s)}</b><br><span class='m'>{e(st['basis'])}</span></td>"
             f"<td>{e(st['llm'])}</td><td>{e(st['parallel'])}</td><td>{e(st['prep'])}</td></tr>" for st, s in rows)
prep = "".join(f"<tr><td>{i}</td><td>{e(p['do'])}</td><td><b>{e(p['saves'])}</b></td></tr>" for i, p in enumerate(T["prep"], 1))
PAGE = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>timeline</title>
<style>.bar{{background:#2a2a38;border-radius:6px;height:10px;width:130px;display:inline-block;margin-right:6px;vertical-align:middle}}.bar i{{display:block;height:100%;border-radius:6px}}.bar i.machine{{background:#4cc9f0}}.bar i.claude{{background:#ff7a3d}}.bar i.owner{{background:#c792ea}}
.m{{opacity:.65;font-size:12px}}.box{{background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:12px 16px;margin:10px 0}}.big{{font-size:34px;font-weight:900;color:#ff7a3d;line-height:1.1}}
.kpis{{display:flex;flex-wrap:wrap;gap:14px}}.kpis>div{{flex:1;min-width:170px}}input[type=number]{{background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;padding:6px 8px;width:90px}}
td{{vertical-align:top}}.calc label{{display:inline-block;margin:4px 14px 4px 0}}</style></head><body><main>
<h1>⏱️ Time and order: how long each stage takes</h1>
<p>The whole flow in order, who does each stage (🖥️ the MacBook with local tools, 🤖 Claude, 👤 you), how long it took on this project (<b>measured</b>) or how long it usually takes (<b>estimate</b>), what can run in parallel, and what to prepare so the next video is faster. Machine: {e(T['machine'])}.</p>
<div class="box kpis"><div><div class="big">{fmt(el)}</div>elapsed since work started ({e(T['started'])}), including every owner note round, the kit, site and publishing tools</div>
<div><div class="big">{fmt(total)}</div>one clean pass of the flow for this video ({mb['youtube_minutes']:.0f} min YouTube + {mb['linkedin_minutes']:.1f} + {mb['x_minutes']:.1f} min cuts), no rounds</div>
<div><div class="big">{fmt(tot['machine'])}</div>🖥️ machine time (mostly unattended)</div><div><div class="big">{fmt(tot['claude'])}</div>🤖 Claude (estimate): judgement on one page of text</div></div>
<h2>📋 The stages, in order</h2>
<table><tr><th>#</th><th>Phase</th><th>Stage and tool</th><th>Who</th><th>Time for this video</th><th>LLM involvement</th><th>Runs in parallel with</th><th>Prepare to save time</th></tr>{tr}</table>
<p class="m">The slowest stage is always the Remotion render (about 2.3 × the video length at 13 frames/s). Claude's share is small because the MacBook does the analysis and Claude reads a one-page report (see Architecture). Extra owner-note rounds repeat stages 8 to 15 (batch the notes: one render per round).</p>
<h2>🧮 Plan the next video</h2>
<div class="box calc"><label>Raw footage (min) <input id="raw" type="number" value="{mb['raw_minutes']}" step="0.5"></label><label>YouTube (min) <input id="yt" type="number" value="{mb['youtube_minutes']}" step="0.5"></label><label>LinkedIn (min) <input id="li" type="number" value="{mb['linkedin_minutes']}" step="0.5"></label><label>X (min) <input id="x" type="number" value="{mb['x_minutes']}" step="0.5"></label><label>Owner note rounds <input id="rounds" type="number" value="2" min="0" step="1"></label><label>Machine idle during renders? <select id="idle"><option value="1">yes (13 frames/s)</option><option value="2">no (about half speed)</option></select></label>
<div id="out" style="margin-top:10px"></div></div>
<h2>🧰 What to do to prepare (and what each saves)</h2>
<table><tr><th>#</th><th>Do</th><th>Saves</th></tr>{prep}</table>
<p class="m">Numbers come from <code>assets/timings.json</code> (edit them when a stage gets faster); the elapsed time reads the start time there. Generated by <code>scripts/build_timeline.py</code>.</p>
</main><script src="project.js"></script><script src="nav.js"></script><script>
const ST={json.dumps([{"n": s["n"], "stage": s["stage"], "who": s["who"], "fixed": s["fixed_s"], "rate": s["rate"]} for s in T["stages"]])};
const f=s=>s<90?Math.round(s)+" s":s<5400?Math.round(s/60)+" min":(s/3600).toFixed(1)+" h";
function calc(){{const raw=+document.getElementById("raw").value,yt=+document.getElementById("yt").value,li=+document.getElementById("li").value,x=+document.getElementById("x").value,R=+document.getElementById("rounds").value,slow=+document.getElementById("idle").value;
  const g=n=>ST.find(s=>s.n===n),t=(n,L)=>g(n).fixed+g(n).rate*L*60;
  const base=t(3,raw)+Math.max(t(4,raw),t(5,raw)),ocr=t(6,raw),an=t(7,raw)+t(9,raw),rend=(g(11).rate*yt*60+g(11).fixed+g(12).rate*(li+x)*60+g(12).fixed)*slow,ver=g(13).fixed+g(13).rate*(yt+li+x)*60*0.75,fin=t(14,yt)+g(15).fixed;
  const claude=g(8).fixed+g(10).fixed+R*g(17).fixed,owner=(1+R)*g(16).rate*yt*60;
  const firstMachine=g(2).fixed+base+ocr+an+rend+ver+fin, roundMachine=(g(11).rate*yt*60+g(12).rate*(li+x)*60)*slow*0.6+ver*0.5+fin;
  const machine=firstMachine+R*roundMachine, wall=firstMachine+claude+owner+R*roundMachine;
  document.getElementById("out").innerHTML="<b>First pass</b>: machine "+f(firstMachine)+" (ingest "+f(base+ocr)+", renders "+f(rend)+", checks "+f(ver+fin)+") · Claude "+f(g(8).fixed+g(10).fixed)+"<br><b>Each extra round</b> (about 60% of the video re-rendered): machine "+f(roundMachine)+" · Claude "+f(g(17).fixed)+"<br><b>Total for "+R+" round(s)</b>: machine "+f(machine)+" + Claude "+f(claude)+" + your review "+f(owner)+" ≈ <b style='font-size:20px;color:#ff7a3d'>"+f(wall)+"</b> start to finish (machine work overlaps with your review and Claude in practice, so real time is often shorter)."}}
document.querySelectorAll(".calc input,.calc select").forEach(i=>i.oninput=calc);calc();
</script></body></html>'''
(ROOT / "timeline.html").write_text(PAGE)
print(f"timeline.html: {len(rows)} stages; one pass {fmt(total)}; elapsed {fmt(el)}")
