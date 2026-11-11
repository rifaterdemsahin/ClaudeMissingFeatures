#!/usr/bin/env python3
"""Artifacts page: every element added to the video (title card, slides, picture cards, blur regions, speed-ups, audio fixes, captions, ending, source clips)
with source + export timecodes, a frame from the FINAL export (already privacy-checked), how it is used, and a link that opens the player at that moment.
Run after the export render:  python3 -I scripts/build_artifacts.py     (needs ffmpeg; reads remotion/src/overlays.json, cuts.json, project.json, export_map.js, assets/*)
Writes artifacts.html and artifacts/*.jpg. Reusable: nothing here is specific to one video."""
import json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p))
P, ov, cuts = J("remotion/src/project.json"), J("remotion/src/overlays.json"), J("remotion/src/cuts.json")
dec = J("assets/edl_decisions.json") if (ROOT / "assets/edl_decisions.json").exists() else []
afix = J("assets/audio_fixes.json") if (ROOT / "assets/audio_fixes.json").exists() else []
base = J("assets/base_info.json") if (ROOT / "assets/base_info.json").exists() else None
_m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()) if (ROOT / "export_map.js").exists() else None
M = json.loads(_m.group(1)) if _m else {"segs": [[0, 1e9, 1, False, 0]], "total": 1e9, "outro": []}
EXPORT = ROOT / "remotion/out/long.mp4"; ORIG = ROOT / "long.mp4"
OUT = ROOT / "artifacts"; OUT.mkdir(exist_ok=True)

def out(t):
    for a, b, r, m, o in M["segs"]:
        if a <= t < b + 1e-9: return o + (t - a) / r
    return None
decmap = {d["id"]: d for d in dec}
items = []
def add(kind, title, src, exp, what, how, edl=(), files=(), extra=None):
    items.append({"n": len(items) + 1, "kind": kind, "title": title, "src": src, "exp": exp, "what": what, "how": how,
                  "edl": [{"id": i, "said": decmap[i]["said"], "decision": decmap[i]["decision"]} for i in edl if i in decmap], "files": list(files), "extra": extra or {}})
def span(a, b): return [round(out(a) or 0, 2), round(out(b - 0.001) or out(a) or 0, 2)]

# source clips
if base:
    t = 0.0
    for c in base["clips"]:
        add("source", f"Source clip: {c['clip']}", [round(t, 2), round(t + c["keep"], 2)], span(t, t + c["keep"]), f"Screen recording kept for {c['keep']} s (sync offset {c['offset']} s against the voice recording, confidence {c['conf']}).",
            "Synced to the clean voice recording by cross-correlation and joined with the other clips into the 1080p base video (blurred side fill, so nothing is cropped).", (), ["scripts/build_base.py"]); t += c["keep"]
# title card
ic = ov["intro_card"]
if ic["to"] > ic["from"]:
    add("intro", f"Title card: {P['thumb']['line1']} {P['thumb']['line2']}", [ic["from"], ic["to"]], span(ic["from"], ic["to"]), "Full-frame title card shown first.",
        "Covers the recorder window at the start of the screen recording; the voice keeps playing underneath. Hard cut, no fade.", (1,), ["remotion/src/Thumb.tsx", "remotion/src/overlays.json › intro_card"])
# slides
for i, s in enumerate(ov["slides"]):
    edl = (2,) if i == 0 else ((9, 3) if "finished" in s["title"].lower() else (3,))
    add("slide", f"Slide: {s['title']}", [s["from"], s["to"]], span(s["from"], s["to"]), " · ".join(s["bullets"]),
        "Replaces a window that showed personal content (or a distracting screen) with an explainer written from what is said at that moment. The narration continues; captions stay on top. Hard cut in and out.", edl, ["remotion/src/Slide.tsx", f"remotion/src/overlays.json › slides[{i}]"], {"bullets": s["bullets"]})
# picture cards
for i, im in enumerate(ov["images"]):
    cap = (im.get("caption", "") + " " + im.get("caption2", "")).strip()
    add("image", f"Picture card: {im['src']}" + (f" ({cap})" if cap else ""), [im["from"], im["to"]], span(im["from"], im["to"]), im.get("why", "Picture supplied by the owner, shown full frame."),
        "Full-frame picture" + (" with a caption on top, an orange box around the feature and an arrow pointing at it (coordinates are in the picture's own pixels)." if im.get("arrow") or im.get("highlight") else "."), (15,) if i == 0 else (27,), ["remotion/src/ImageOverlays.tsx", f"remotion/src/overlays.json › images[{i}]", f"remotion/public/img/{im['src']} (local only, not committed)"], {"arrow": im.get("arrow"), "highlight": im.get("highlight")})
# blur regions
rule = {"A": ("Blurred: chat-title list in the app sidebar", "Chat titles and pinned names in the sidebar are frosted over whenever they are visible. Two fixed boxes (nav visible / list scrolled to the top)."),
        "B": ("Blurred: sensitive words", "A box around any line that contains a word from project.json › sensitive_keywords."),
        "C": ("Blurred: mini sidebar inside the pasted screenshot", "OCR cannot read the tiny text inside a pasted screenshot, so the box is anchored to the sentence below the picture.")}
for i, b in enumerate(ov["blurs"]):
    t, d = rule[b["rule"]]
    add("blur", f"{t} ({b['w']}×{b['h']} px)", [b["from"], b["to"]], span(b["from"], b["to"]), f"Box at x={b['x']}, y={b['y']}, {b['w']}×{b['h']} px (1920×1080 frame).", d + " Generated from OCR by scripts/build_blurs.py, padded by 1.5 s at each end.", (5, 6), ["scripts/build_blurs.py", "scripts/ocr_frames.swift", f"remotion/src/overlays.json › blurs[{i}]"], {"box": [b["x"], b["y"], b["w"], b["h"]], "rule": b["rule"]})
for i, b in enumerate(ov.get("manual_blurs", [])):
    add("blur", f"Manual blur: {b['why']}", [b["from"], b["to"]], span(b["from"], b["to"]), f"Box at x={b['x']}, y={b['y']}, {b['w']}×{b['h']} px (1920×1080 frame).", "Placed by hand where OCR cannot help (a notification banner) or where part of a window must stay readable (the update menu).", (22, 23), [f"remotion/src/overlays.json › manual_blurs[{i}]"], {"box": [b["x"], b["y"], b["w"], b["h"]], "rule": "M"})
for i, l in enumerate(ov.get("lower_thirds", [])):
    add("lower", f"Lower third: {l['text']}", [l["from"], l["to"]], span(l["from"], l["to"]), (l.get("label", "") + ": " if l.get("label") else "") + l["text"], "A text bar in the lower left, above the captions, so a point can be made on screen without covering the footage. Hard cut in and out.", (24,), ["remotion/src/ImageOverlays.tsx", f"remotion/src/overlays.json › lower_thirds[{i}]"])
for i, c in enumerate(cuts):
    add("cut", f"Cut: {c[1] - c[0]:.1f} s removed", [c[0], c[1]], [round(out(c[0]) or 0, 2)] * 2, f"Source {c[0]}–{c[1]} s removed from the video.", "Cut at sentence boundaries so no sentence is chopped; the apology card sits at the cut. Every later export time moves earlier by the removed length minus the card.", (26,), ["remotion/src/cuts.json"], {"after": c[1]})
for i, ins in enumerate(ov.get("inserts", [])):
    mi = M.get("inserts", [[0, 0, 0]])[i]
    add("insert", f"Card at the cut: {ins.get('title', '')}", [ins["at"], ins["at"]], [mi[0], round(mi[0] + ins["seconds"], 2)], ins.get("text", ""), f"A {ins['seconds']} s card placed on the timeline at the cut" + (", with a frame-driven cartoon hoover (like a GIF)" if ins.get("animation") == "hoover" else "") + ". Silent; captions paused.", (26,), ["remotion/src/InsertCard.tsx", f"remotion/src/overlays.json › inserts[{i}]"])
# speed-ups
for i, s in enumerate(ov["speedups"]):
    add("speed", f"Speed-up {s['rate']}x" + (" (muted)" if s.get("mute") else ""), [s["from"], s["to"]], span(s["from"], s["to"]), s.get("why", "Slow section played faster."),
        f"Played at {s['rate']}x with Remotion playbackRate" + ("; audio muted and captions hidden because speech sped up is unusable" if s.get("mute") else "") + f". The {s['to'] - s['from']:.1f} s section takes {(s['to'] - s['from']) / s['rate']:.1f} s in the export, which shifts every later export timecode.", (4,), ["remotion/src/cuts.ts", f"remotion/src/overlays.json › speedups[{i}]"])
# audio fixes (spectrograms before/after)
for i, a in enumerate(afix):
    add("audio", "Audio fix: steady noise removed", [a["from"], a["to"]], span(a["from"], min(a["to"], M["segs"][-1][1])), a["what"], a["why"] + ". Library: noisereduce (stationary mode), profile learned from a noise-only stretch; video stream copied untouched.", (8,), ["scripts/denoise_audio.py", f"assets/audio_fixes.json[{i}]"], {"spec": True})
# captions
add("caption", "Animated captions", [0, base["total_s"] if base else 0], [0, M["total"]], "Whisper word timings drive a highlighted word; phrases appear and disappear without transitions. Also exported as .srt/.vtt for YouTube.", "Captions are burned in over the footage (not over slides' outro). Product names are corrected from project.json › caption_fixes. Hidden inside muted speed-ups.", (14,), ["remotion/src/Subtitles.tsx", "scripts/build_subs.py", "subtitles.srt", "subtitles.vtt"])
# ending
t = M["total"]
for k, p in enumerate(ov.get("outro", [])):
    cta = p["kind"] == "cta"
    add("outro", f"Ending: {p['title']}" + (f" ({P['community']['name']} on {P['community']['platform']})" if cta else ""), None, [round(t, 2), round(t + p["seconds"], 2)],
        (f"{p['line']} · {p['url']} · {p['note']}" if cta else " · ".join(p.get("bullets", []))), "Silent card after the footage, hard cuts. " + ("Community call to action." if cta else "Summary taken from what was said."), (11,) if cta else (10,), ["remotion/src/Outro.tsx", f"remotion/src/overlays.json › outro[{k}]"]); t += p["seconds"]

# ---- frames from the final export (and spectrograms)
have_export = EXPORT.exists()
def grab(it):
    if not have_export: return
    a, b = it["exp"]; mid = a + (b - a) / 2 if it["kind"] not in ("source", "caption") else a + min(5, (b - a) / 2)
    if it["kind"] == "cut": mid = (out(it["extra"]["after"] + 0.5) or a)
    if it["kind"] == "caption": mid = out(300) or 100
    for name, w in (("", 1280), ("_s", 400)):
        f = OUT / f"{it['n']:02d}{name}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(EXPORT), "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "4", str(f)], check=False)
    it["img"] = f"artifacts/{it['n']:02d}.jpg"; it["thumb"] = f"artifacts/{it['n']:02d}_s.jpg"; it["at"] = round(mid, 2)
for it in items:
    grab(it)
    if it["extra"].get("spec") and have_export and ORIG.exists():
        a = items[it["n"] - 1]["src"][0] - 14; a = max(a, 0)
        for tag, path, start in (("before", ORIG, a), ("after", EXPORT, out(a) or a)):
            f = OUT / f"{it['n']:02d}_{tag}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", "40", "-i", str(path), "-lavfi", "showspectrumpic=s=1100x330:legend=0:scale=log:fscale=log:start=60:stop=6000:color=intensity", str(f)], check=False)
            it["extra"][tag] = f"artifacts/{f.name}"
        it["extra"]["window"] = f"source {a:.0f}–{a + 40:.0f} s (before) and export {(out(a) or a):.0f}–{(out(a) or a) + 40:.0f} s (after)"
tot = M["total"] + sum(p["seconds"] for p in ov.get("outro", []))

PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__: artifacts</title>
<style>
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}.tools input{background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;padding:8px 10px;min-width:220px}
.chip{background:#2a2a38;color:#ddd;border:0;border-radius:999px;padding:6px 12px;cursor:pointer;font-size:13px}.chip.on{background:#ff7a3d;color:#000;font-weight:700}
#strip{position:relative;height:34px;background:#14141c;border:1px solid #2a2a38;border-radius:8px;margin:8px 0 4px;overflow:hidden}
#strip i{position:absolute;top:4px;height:12px;border-radius:3px;cursor:pointer;opacity:.9}#strip i.row2{top:19px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:12px 0}
.card{background:#14141c;border:1px solid #2a2a38;border-radius:12px;overflow:hidden;cursor:pointer;display:flex;flex-direction:column}.card:hover{border-color:#ff7a3d}
.card img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;display:block}.card .b{padding:8px 10px 10px;font-size:13px}.card .t{font-weight:700;font-size:14px;margin:2px 0}.card .m{opacity:.75}
.kind{display:inline-block;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:700;color:#000}
#modal{position:fixed;inset:0;background:rgba(0,0,0,.82);display:none;z-index:50;overflow:auto}#modal.on{display:block}
#mbox{max-width:1100px;margin:30px auto;background:#14141c;border:1px solid #2a2a38;border-radius:14px;padding:16px}
#mimg{position:relative}#mimg img{width:100%;border-radius:10px;display:block;background:#000}#mimg .box{position:absolute;border:3px dashed #ff7a3d;border-radius:6px;box-shadow:0 0 0 2px rgba(0,0,0,.4)}
.kv{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:10px 0}.kv b{opacity:.7}
.acts{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.acts a{background:#ff7a3d;color:#000;border-radius:8px;padding:8px 14px;font-weight:700;text-decoration:none}.acts a.alt{background:#2a2a38;color:#fff}.acts button{background:#2a2a38;color:#fff}
.nb{display:inline-block;background:#fde047;color:#000;border-radius:999px;padding:0 7px;font-size:11px;font-weight:800;margin-left:6px}
.note{width:100%;min-height:92px;background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;box-sizing:border-box;padding:8px}
.saved{display:inline-block;margin-left:10px;color:#4ade80;font-weight:700;font-size:13px;opacity:0}.saved.on{animation:savedpop 1.8s ease-out}.saved.warn{color:#fbbf24}
@keyframes savedpop{0%{opacity:0;transform:scale(.6)}14%{opacity:1;transform:scale(1.18)}28%{transform:scale(1)}80%{opacity:1}100%{opacity:0}}
.note.flash{animation:savedglow 1.2s ease-out}@keyframes savedglow{0%{box-shadow:0 0 0 0 rgba(74,222,128,.85);border-color:#4ade80}100%{box-shadow:0 0 0 14px rgba(74,222,128,0);border-color:#2a2a38}}
#notesbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}#allnotes{background:#14141c;border:1px solid #2a2a38;border-radius:10px;padding:8px 14px;margin:8px 0}#allnotes li{margin:6px 0}
.q{border-left:3px solid #ff7a3d;padding:2px 10px;margin:6px 0;opacity:.9}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.two figure{margin:0}.two img{width:100%;border-radius:8px}
</style></head><body><main>
<h1>🧩 Artifacts: everything added to the video</h1>
<p>Every element placed on top of the footage, with its timecode on the <b>source</b> (original) and <b>export</b> timelines. Click a card to see it large, how it is used and why, and to open the player at that moment. Previews are frames from the final export.</p>
<div class="tools"><input id="q" placeholder="Search (title, text, timecode)…"><span id="chips"></span><span id="count" style="opacity:.7"></span></div>
<div id="notesbar"><button class="chip" id="shownotes">📝 My notes <span id="ncount">0</span></button><button class="chip" id="copynotes">Copy all notes</button><button class="chip" id="sendall">↗ Send all to player feedback</button><button class="chip" id="clearnotes">🗑️ Clear all notes</button><button class="chip" id="undonotes" style="display:none">↩ Undo clear</button><span id="notesaved" class="saved">✔ Saved</span><label style="margin-left:auto;font-size:13px"><input type="checkbox" id="onlynotes"> only artifacts with notes</label></div>
<div id="allnotes" style="display:none"></div>
<div id="strip" title="Export timeline: click a marker"></div>
<div id="grid" class="grid"></div>
<div id="modal"><div id="mbox"></div></div>
</main><script src="project.js"></script><script src="nav.js"></script><script src="exports.js"></script><script>
const D=__DATA__, TOTAL=__TOTAL__;
const K={source:["🎞️","Source clip","#7aa7ff"],intro:["🪧","Title card","#ffd166"],slide:["🧾","Slide","#c792ea"],image:["🖼️","Picture card","#06d6a0"],blur:["🔒","Blur region","#8d99ae"],speed:["⏩","Speed-up","#ef476f"],audio:["🔊","Audio fix","#4cc9f0"],caption:["💬","Captions","#f4a261"],outro:["🎬","Ending","#ff7a3d"],lower:["🏷️","Lower third","#e9c46a"],insert:["🧹","Card at a cut","#ff9f1c"],cut:["✂️","Cut","#e63946"]};
const fmt=s=>{const m=Math.floor(s/60);return m+":"+(s%60).toFixed(1).padStart(4,"0")};
const $=id=>document.getElementById(id); let filter="all",view=D.slice(),cur=-1;
// ---- notes: saved in this browser per artifact (stable key: kind + title + source/export time), tagged with the export version
const EXPS=(window.EXPORTS||[]).filter(e=>e.file),VER=EXPS.length?EXPS[EXPS.length-1].v:null;
const keyOf=i=>i.kind+"|"+i.title+"|"+(i.src?i.src[0]:i.exp[0]);
let NOTES={};try{NOTES=JSON.parse(localStorage.getItem("art:notes")||"{}")}catch(e){}
let lastCleared=null,savedT=null;
function saveNotes(){let ok=true;try{localStorage.setItem("art:notes",JSON.stringify(NOTES))}catch(e){ok=false}
  clearTimeout(savedT);savedT=setTimeout(()=>{[$("notesaved"),$("msaved")].forEach(s=>{if(!s)return;s.textContent=ok?"✔ Saved":"⚠ Not saved (private window?)";s.classList.toggle("warn",!ok);s.classList.remove("on");void s.offsetWidth;s.classList.add("on")});
    const t=$("mnote");if(t&&ok){t.classList.remove("flash");void t.offsetWidth;t.classList.add("flash")}},350);refreshNotes()}
const noteOf=i=>(NOTES[keyOf(i)]||"").trim();
function noteLine(i,withTag=true){const t=Math.floor(i.exp[0]),tag="["+(VER?"v"+VER:"export")+" "+Math.floor(t/60)+":"+String(t%60).padStart(2,"0")+"]";return (withTag?tag+" ":"")+"(artifact #"+i.n+" · "+K[i.kind][1]+": "+i.title+") "+noteOf(i)}
function refreshNotes(){const withN=D.filter(i=>noteOf(i));$("ncount").textContent=withN.length;$("clearnotes").disabled=!withN.length;
  $("allnotes").innerHTML=withN.length?"<ol>"+withN.map(i=>`<li><a href="#${i.n}" data-n="${i.n}">#${i.n} ${i.title}</a> <span style="opacity:.6">export ${fmt(i.exp[0])}</span><br>${noteOf(i).replace(/</g,"&lt;").replace(/\n/g,"<br>")}</li>`).join("")+"</ol>":"<i>No notes yet. Open an artifact and write one.</i>";
  document.querySelectorAll(".card").forEach(c=>{const it=D.find(x=>x.n===+c.dataset.n),b=c.querySelector(".nb");if(it&&noteOf(it)){if(!b)c.querySelector(".t").insertAdjacentHTML("beforeend",'<span class="nb">📝</span>')}else if(b)b.remove()})}
function header(){return "Notes on the artifacts"+(VER?" of export v"+VER:"")+" (tags: [vN m:ss] = export time):\n\n"}
$("shownotes").onclick=()=>{const a=$("allnotes");a.style.display=a.style.display==="none"?"":"none"};
$("allnotes").onclick=e=>{const n=e.target.dataset.n;if(n){e.preventDefault();openN(+n)}};
$("copynotes").onclick=()=>{const t=header()+D.filter(i=>noteOf(i)).map(i=>noteLine(i)).join("\n");navigator.clipboard.writeText(t).then(()=>{$("copynotes").textContent="Copied ✔";setTimeout(()=>$("copynotes").textContent="Copy all notes",1500)})};
function sendToPlayer(items){let fb="";try{fb=localStorage.getItem("fb:player")||""}catch(e){}const add=items.map(i=>noteLine(i)).join("\n");try{localStorage.setItem("fb:player",(fb&&!fb.endsWith("\n")?fb+"\n":fb)+add+"\n")}catch(e){}}
$("sendall").onclick=()=>{const w=D.filter(i=>noteOf(i));if(!w.length)return;sendToPlayer(w);$("sendall").textContent="Sent to the player ✔";setTimeout(()=>$("sendall").textContent="↗ Send all to player feedback",1800)};
$("clearnotes").onclick=()=>{lastCleared=JSON.stringify(NOTES);NOTES={};saveNotes();$("undonotes").style.display=""};
$("undonotes").onclick=()=>{if(lastCleared){NOTES=JSON.parse(lastCleared);lastCleared=null;saveNotes()}$("undonotes").style.display="none"};
$("onlynotes").onchange=()=>render();
const tcs=a=>a?fmt(a[0])+"–"+fmt(a[1]):"–";
const search=it=>(it.title+" "+it.what+" "+it.how+" "+tcs(it.src)+" "+tcs(it.exp)).toLowerCase();
function chips(){const c={};D.forEach(i=>c[i.kind]=(c[i.kind]||0)+1);$("chips").innerHTML='<button class="chip on" data-k="all">All '+D.length+'</button>'+Object.keys(K).filter(k=>c[k]).map(k=>`<button class="chip" data-k="${k}">${K[k][0]} ${K[k][1]} ${c[k]}</button>`).join("")}
$("chips").onclick=e=>{const k=e.target.dataset.k;if(!k)return;filter=k;[...$("chips").children].forEach(b=>b.classList.toggle("on",b.dataset.k===k));render()};
$("q").oninput=render;
function render(){const q=$("q").value.toLowerCase().trim();view=D.filter(i=>(filter==="all"||i.kind===filter)&&(!q||search(i).includes(q))&&(!$("onlynotes").checked||noteOf(i)));$("count").textContent=view.length+" shown";
  $("grid").innerHTML=view.map(i=>`<div class="card" data-n="${i.n}">${i.thumb?`<img loading="lazy" src="${i.thumb}" alt="">`:`<div style="aspect-ratio:16/9;display:grid;place-items:center;background:#0b0b0f;font-size:42px">${K[i.kind][0]}</div>`}<div class="b"><span class="kind" style="background:${K[i.kind][2]}">${K[i.kind][0]} ${K[i.kind][1]}</span><div class="t">${i.title}${noteOf(i)?'<span class="nb">📝</span>':""}</div><div class="m">export ${tcs(i.exp)}${i.src?"<br>source "+tcs(i.src):""}</div></div></div>`).join("")}
$("grid").onclick=e=>{const c=e.target.closest(".card");if(c)openN(+c.dataset.n)};
function strip(){$("strip").innerHTML=D.filter(i=>i.kind!=="caption").map(i=>{const l=i.exp[0]/TOTAL*100,w=Math.max((i.exp[1]-i.exp[0])/TOTAL*100,.35);return `<i data-n="${i.n}" class="${i.kind==="blur"||i.kind==="source"?"row2":""}" style="left:${l}%;width:${w}%;background:${K[i.kind][2]}" title="${i.title}"></i>`}).join("")}
$("strip").onclick=e=>{const n=e.target.dataset.n;if(n)openN(+n)};
function link(it,v){const t=v==="exp"?it.exp[0]:(it.src?it.src[0]:0);return `player.html?v=${v}&t=${Math.max(t-1,0).toFixed(1)}`}
function openN(n){const it=D.find(x=>x.n===n);cur=view.findIndex(x=>x.n===n);const b=it.extra.box,bx=b?`<div class="box" style="left:${b[0]/19.2}%;top:${b[1]/10.8}%;width:${b[2]/19.2}%;height:${b[3]/10.8}%"></div>`:"";
  const spec=it.extra.before?`<div class="two"><figure><img src="${it.extra.before}" alt=""><figcaption>Before (original audio)</figcaption></figure><figure><img src="${it.extra.after}" alt=""><figcaption>After (export audio)</figcaption></figure></div><p style="opacity:.7">Spectrograms: ${it.extra.window}. A steady haze across all frequencies is the noise; it is gone after.</p>`:"";
  $("mbox").innerHTML=`<div style="display:flex;justify-content:space-between;gap:10px;align-items:center"><h2 style="margin:0">${K[it.kind][0]} ${it.title}</h2><div><button id="mp">‹ Prev</button> <button id="mn">Next ›</button> <button id="mx">✕ Close (Esc)</button></div></div>
  ${it.img?`<div id="mimg"><img src="${it.img}" alt="">${bx}</div>`:""}${spec}
  <div class="acts"><a target="_blank" href="${link(it,"exp")}">▶ Open in player (export ${fmt(it.exp[0])})</a>${it.src?`<a class="alt" target="_blank" href="${link(it,"orig")}">▶ Original at source ${fmt(it.src[0])}</a>`:""}</div>
  <div style="margin:10px 0"><b>📝 My note</b> <span id="msaved" class="saved">✔ Saved</span> <button id="msend" style="float:right">↗ Add to player feedback</button><textarea id="mnote" class="note" placeholder="Write a note about this artifact (saved in this browser, tagged with the export version). Ctrl/⌘+Enter closes the box."></textarea></div>
  <div class="kv"><b>Type</b><span>${K[it.kind][1]}</span><b>Export timecode</b><span>${tcs(it.exp)} (${(it.exp[1]-it.exp[0]).toFixed(1)} s)</span><b>Source timecode</b><span>${it.src?tcs(it.src):"– (added after the footage)"}</span>
  <b>What</b><span>${it.what}</span><b>How it is used</b><span>${it.how}</span>
  <b>Where it lives</b><span>${it.files.map(f=>"<code>"+f+"</code>").join("<br>")}</span>
  ${it.edl.length?`<b>Decision (EDL)</b><span>${it.edl.map(d=>`<div class="q"><i>“${d.said}”</i><br>${d.decision}</div>`).join("")}<a href="edl.html">Open the EDL →</a></span>`:""}</div>`;
  $("modal").classList.add("on");const mn=$("mnote");mn.value=NOTES[keyOf(it)]||"";mn.oninput=()=>{if(mn.value.trim())NOTES[keyOf(it)]=mn.value;else delete NOTES[keyOf(it)];saveNotes()};
  mn.onkeydown=ev=>{ev.stopPropagation();if((ev.metaKey||ev.ctrlKey)&&ev.key==="Enter")mn.blur()};$("msend").onclick=()=>{if(noteOf(it)){sendToPlayer([it]);$("msend").textContent="Added ✔";setTimeout(()=>$("msend").textContent="↗ Add to player feedback",1500)}};
  $("mx").onclick=close;$("mp").onclick=()=>step(-1);$("mn").onclick=()=>step(1)}
function close(){$("modal").classList.remove("on")}
function step(d){if(cur<0)return;const n=view[(cur+d+view.length)%view.length];if(n)openN(n.n)}
$("modal").onclick=e=>{if(e.target.id==="modal")close()};
addEventListener("keydown",e=>{if(!$("modal").classList.contains("on")||e.target.tagName==="TEXTAREA")return;if(e.key==="Escape")close();else if(e.key==="ArrowRight")step(1);else if(e.key==="ArrowLeft")step(-1)});
chips();render();strip();refreshNotes();const h=location.hash.match(/#(\d+)/);if(h)openN(+h[1]);
</script></body></html>'''
html = PAGE.replace("__TITLE__", P["title"]).replace("__DATA__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/")).replace("__TOTAL__", str(round(tot, 2)))
(ROOT / "artifacts.html").write_text(html)
from collections import Counter
print(f"artifacts.html: {len(items)} artifacts", dict(Counter(i['kind'] for i in items)), "| frames from export:", have_export)
