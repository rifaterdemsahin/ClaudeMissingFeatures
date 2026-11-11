#!/usr/bin/env python3
"""Publish page (publish.html): one card per platform (YouTube, LinkedIn, X) with limits, the export and its length against the limit, placeholders for the
storage link and the post link, ready-to-paste text with character counters, a review checklist fed by the privacy check, and notes (saved per browser, version-tagged).
Storage links are NOT written into this page: they come from a git-ignored local file (publish_links.js, made by upload_exports.py), so signed URLs never reach the public site.
Run: python3 -I scripts/build_publish.py   (reusable: data in assets/publish.json and assets/exports.json)"""
import html, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p, d=None: json.load(open(ROOT / p)) if (ROOT / p).exists() else d
P, pub, reg, checks, variants = J("remotion/src/project.json", {}), J("assets/publish.json", {"platforms": [], "checklist": []}), J("assets/exports.json", []), J("assets/export_checks.json", {}), J("remotion/src/variants.json", {})
md = (ROOT / "metadata.md").read_text() if (ROOT / "metadata.md").exists() else ""
def meta(section):
    m = re.search(r"^## " + section + r"[^\n]*\n(.*?)(?=^## |\Z)", md, flags=re.M | re.S); return m.group(1).strip() if m else ""
yt_title = (meta("Title").splitlines() or [""])[0].strip()
yt_text = meta("Description")
key = lambda e: "v%d" % e["v"] + ("" if e.get("platform", "youtube") == "youtube" else "-" + e["platform"])
data = []
for pl in pub["platforms"]:
    es = [e for e in reg if e.get("file") and e.get("platform", "youtube") == pl["id"]]
    e = es[-1] if es else None
    d = dict(pl); d["export"] = {"key": key(e), "v": e["v"], "file": e["file"], "seconds": e["seconds"], "size_mb": e["size_mb"], "rendered": e["rendered"], "notes": e.get("notes", "")} if e else None
    d["check"] = checks.get(key(e)) if e else None
    if pl.get("title_from_metadata"): d["title"] = yt_title
    if pl.get("text_from_metadata"): d["text"] = yt_text
    d["variant_note"] = variants.get(pl["id"], {}).get("note", "")
    data.append(d)
PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>publish</title>
<style>
.pn{background:#14141c;border:1px solid #2a2a38;border-radius:10px;margin:12px 0}.pn>summary{cursor:pointer;padding:12px 16px;font-weight:800;font-size:18px;list-style:none}.pn>summary::-webkit-details-marker{display:none}.pn>summary::before{content:"▸ ";color:#ff7a3d}.pn[open]>summary::before{content:"▾ "}.pnb{padding:0 16px 14px}
.chip{display:inline-block;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:700;margin-left:8px;color:#000}.s-draft{background:#9ca3af}.s-shared{background:#4ade80}.ok{color:#4ade80}.warn{color:#facc15}.bad{color:#f87171}
.row{display:grid;grid-template-columns:150px 1fr;gap:6px 14px;margin:8px 0}.row b{opacity:.7}.ph{opacity:.6;font-style:italic}
.bar{background:#2a2a38;border-radius:6px;height:10px;width:220px;display:inline-block;vertical-align:middle;margin-right:8px}.bar i{display:block;height:100%;border-radius:6px;background:#4ade80}
textarea{width:100%;background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;box-sizing:border-box;padding:8px;min-height:110px}.cnt{font-size:12px;opacity:.75;float:right}
.saved{display:inline-block;margin-left:10px;color:#4ade80;font-weight:700;font-size:13px;opacity:0}.saved.on{animation:savedpop 1.8s ease-out}.saved.warn{color:#fbbf24}
@keyframes savedpop{0%{opacity:0;transform:scale(.6)}14%{opacity:1;transform:scale(1.18)}28%{transform:scale(1)}80%{opacity:1}100%{opacity:0}}
textarea.flash{animation:savedglow 1.2s ease-out}@keyframes savedglow{0%{box-shadow:0 0 0 0 rgba(74,222,128,.85);border-color:#4ade80}100%{box-shadow:0 0 0 14px rgba(74,222,128,0);border-color:#2a2a38}}
.tools{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.tools button.off,button.off{background:#2a2a38;color:#ddd}
</style></head><body><main>
<h1>📣 Publish: YouTube · LinkedIn · X</h1>
<p>One edit, three cuts. Each platform has its own length, so each gets its own numbered export (<code>scripts/render_export.sh "what changed" youtube linkedin x</code>). Storage links and post links are <b>placeholders</b> until you share; then give me the post links and I fill them in (they also appear in the menu under 🔗 Links). Review everything here first, and write notes.</p>
<div class="tools"><button id="shownotes" class="off">📝 All notes <span id="ncount">0</span></button><button id="copynotes" class="off">Copy all notes</button><button id="sendall" class="off">↗ Send all to player feedback</button><button id="clearnotes" class="off">🗑️ Clear all notes</button><button id="undonotes" style="display:none">↩ Undo clear</button><span id="notesaved" class="saved">✔ Saved</span></div>
<div id="allnotes" class="pn" style="display:none;padding:8px 16px"></div>
<div id="cards"></div>
<h2>✅ Before you share</h2><ul id="check"></ul>
<p style="opacity:.7">Limits are as of writing; platforms change them, so check your account. Storage: exports are uploaded to a <b>private</b> Azure container with time-limited read-only links (<code>scripts/upload_exports.py</code>, keys in Azure Key Vault); the links live only in a local, git-ignored file and are never published with this site.</p>
</main><script src="project.js"></script><script src="nav.js"></script><script src="exports.js"></script><script>
const D=__DATA__, CHECK=__CHECK__; let LINKS={};
const $=id=>document.getElementById(id), fmt=s=>Math.floor(s/60)+":"+String(Math.round(s%60)).padStart(2,"0"), esc=t=>String(t||"").replace(/&/g,"&amp;").replace(/</g,"&lt;");
const VER=D.find(p=>p.export)&&D.find(p=>p.export).export.v;
let NOTES={};try{NOTES=JSON.parse(localStorage.getItem("pub:notes")||"{}")}catch(e){}
let lastCleared=null,savedT=null;
function tag(p){return p.export?"["+p.export.key+"]":"["+p.id+"]"}
function saveNotes(src){let ok=true;try{localStorage.setItem("pub:notes",JSON.stringify(NOTES))}catch(e){ok=false}clearTimeout(savedT);savedT=setTimeout(()=>{document.querySelectorAll(".saved").forEach(s=>{s.textContent=ok?"✔ Saved":"⚠ Not saved (private window?)";s.classList.toggle("warn",!ok);s.classList.remove("on");void s.offsetWidth;s.classList.add("on")});if(ok&&src){src.classList.remove("flash");void src.offsetWidth;src.classList.add("flash")}},350);refresh()}
const noteOf=p=>(NOTES[p.id]||"").trim();
function refresh(){const w=D.filter(noteOf);$("ncount").textContent=w.length;$("allnotes").innerHTML=w.length?"<ol>"+w.map(p=>`<li><b>${p.emoji} ${p.label}</b> ${tag(p)}<br>${esc(noteOf(p)).replace(/\n/g,"<br>")}</li>`).join("")+"</ol>":"<i>No notes yet.</i>"}
function header(){return "Notes on the publish page (tags: [vN] = YouTube export, [vN-linkedin], [vN-x]):\n\n"}
$("shownotes").onclick=()=>{const a=$("allnotes");a.style.display=a.style.display==="none"?"":"none"};
$("copynotes").onclick=()=>navigator.clipboard.writeText(header()+D.filter(noteOf).map(p=>tag(p)+" ("+p.label+" publish) "+noteOf(p)).join("\n")).then(()=>{$("copynotes").textContent="Copied ✔";setTimeout(()=>$("copynotes").textContent="Copy all notes",1500)});
function toPlayer(items){let fb="";try{fb=localStorage.getItem("fb:player")||""}catch(e){}try{localStorage.setItem("fb:player",(fb&&!fb.endsWith("\n")?fb+"\n":fb)+items.map(p=>tag(p)+" ("+p.label+" publish) "+noteOf(p)).join("\n")+"\n")}catch(e){}}
$("sendall").onclick=()=>{const w=D.filter(noteOf);if(w.length){toPlayer(w);$("sendall").textContent="Sent to the player ✔";setTimeout(()=>$("sendall").textContent="↗ Send all to player feedback",1800)}};
$("clearnotes").onclick=()=>{lastCleared=JSON.stringify(NOTES);NOTES={};document.querySelectorAll("textarea.pnote").forEach(t=>t.value="");saveNotes();$("undonotes").style.display=""};
$("undonotes").onclick=()=>{if(lastCleared){NOTES=JSON.parse(lastCleared);lastCleared=null;document.querySelectorAll("textarea.pnote").forEach(t=>t.value=NOTES[t.dataset.id]||"");saveNotes()}$("undonotes").style.display="none"};
function card(p){const e=p.export,lim=p.limit_s,len=e?e.seconds:0,pct=lim&&e?Math.min(100,len/lim*100):(e?35:0),over=lim&&e&&len>lim;
  const link=LINKS[e&&e.key]; const chk=p.check?(p.check.privacy_leaks===0?`<span class="ok">✅ privacy check: ${p.check.frames} frames, 0 sensitive lines (${esc(p.check.when)})</span>`:`<span class="bad">❌ ${p.check.privacy_leaks} sensitive lines</span>`):`<span class="warn">⏳ privacy check not run yet (python3 -I scripts/verify_export.py ${e?e.file:""})</span>`;
  const txt=p.text||"", max=p.text_max;
  return `<details class="pn" open data-id="${p.id}"><summary>${p.emoji} ${p.label}<span class="chip s-${p.status}">${p.status}</span>${e?`<span style="font-weight:400;opacity:.7;font-size:14px;margin-left:10px">${e.key} · ${fmt(e.seconds)}${lim?" of "+fmt(lim):""}</span>`:'<span style="font-weight:400;opacity:.7;font-size:14px;margin-left:10px">not rendered yet</span>'}</summary><div class="pnb">
  <div class="row"><b>Format</b><span>${p.aspect} · ${esc(p.target)} · file up to ${p.file_limit}</span><b>Limit</b><span>${esc(p.limit_note)}</span><b>This cut</b><span>${esc(p.variant_note||"")}</span>
  <b>Export</b><span>${e?`<b>${e.key}</b> · <code>${e.file}</code> · ${fmt(e.seconds)} · ${e.size_mb} MB · rendered ${e.rendered}<br><span style="opacity:.75">${esc(e.notes)}</span>`:'<span class="ph">&lt;render with scripts/render_export.sh "…" '+p.id+'&gt;</span>'}</span>
  <b>Length</b><span>${e?`<span class="bar"><i style="width:${pct}%;${over?"background:#f87171":""}"></i></span>${lim?(over?`<span class="bad">❌ ${fmt(len-lim)} over the limit</span>`:`<span class="ok">✅ ${fmt(lim-len)} under the limit</span>`):'<span class="ok">✅ no limit to worry about</span>'}`:"–"}</span>
  <b>Checks</b><span>${chk}</span>
  <b>Preview</b><span>${e?`<a target="_blank" href="player.html?v=${e.key}&t=0">▶ open ${e.key} in the player</a> · <a href="${e.file}" target="_blank">local file</a>`:"–"}</span>
  <b>Storage link</b><span id="az-${p.id}">${link?`<a target="_blank" href="${link.url}">open</a> <button class="off" data-copy="${link.url}">Copy link</button> <span style="opacity:.7">read-only, expires ${esc(link.expires)}</span>`:'<span class="ph">&lt;Azure storage link appears here after upload&gt;</span>'}</span>
  <b>Post link</b><span>${p.post_url?`<a target="_blank" href="${p.post_url}">${esc(p.post_url)}</a>`:`<span class="ph">${esc(p.post_url_hint)}</span>`}</span></div>
  ${p.title?`<p><b>Title</b> <span class="cnt">${p.title.length} / ${p.title_max}</span></p><textarea readonly style="min-height:46px">${esc(p.title)}</textarea><div class="tools"><button class="off" data-copy-id="t-${p.id}">Copy title</button></div>`:""}
  <p><b>${p.id==="youtube"?"Description":"Post text"}</b> <span class="cnt ${txt.length>max?"bad":""}">${txt.length} / ${max} characters</span></p><textarea id="t-${p.id}" readonly>${esc(txt)}</textarea><div class="tools"><button class="off" data-copy-id="t-${p.id}">Copy text</button></div>
  <p><b>📝 My note</b> <span class="saved">✔ Saved</span></p><textarea class="pnote" data-id="${p.id}" placeholder="Your review notes for ${p.label} (saved in this browser, tagged ${e?e.key:p.id}).">${esc(NOTES[p.id]||"")}</textarea></div></details>`}
function render(){$("cards").innerHTML=D.map(card).join("");
  document.querySelectorAll("textarea.pnote").forEach(t=>{t.oninput=()=>{if(t.value.trim())NOTES[t.dataset.id]=t.value;else delete NOTES[t.dataset.id];saveNotes(t)}});
  document.querySelectorAll("[data-copy]").forEach(b=>b.onclick=()=>navigator.clipboard.writeText(b.dataset.copy).then(()=>{b.textContent="Copied ✔"}));
  document.querySelectorAll("[data-copy-id]").forEach(b=>b.onclick=()=>navigator.clipboard.writeText($(b.dataset.copyId).value).then(()=>{b.textContent="Copied ✔"}));refresh()}
$("check").innerHTML=CHECK.map(c=>"<li>"+esc(c)+"</li>").join("");
render();
// local-only storage links (git-ignored file made by upload_exports.py); the page works without it
const s=document.createElement("script");s.src="publish_links.js";s.onload=()=>{LINKS=window.PUBLISH_LINKS||{};render()};s.onerror=()=>{};document.head.appendChild(s);
</script></body></html>'''
out = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")).replace("__CHECK__", json.dumps(pub.get("checklist", []), ensure_ascii=False))
(ROOT / "publish.html").write_text(out)
print(f"publish.html: {len(data)} platforms; exports: " + ", ".join(f"{d['id']}={d['export']['key'] if d['export'] else 'none'}" for d in data))
