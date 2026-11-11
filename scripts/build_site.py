"""Render the Markdown docs into site pages. Run: python3 -I scripts/build_site.py"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = {"MASTER_SPEC.md": ("spec.html", "Master spec v3"),
      "metadata.md": ("metadata.html", "YouTube metadata"),
      "README.md": ("readme.html", "README (Shorts flow)"),
      "ENVIRONMENT.md": ("environment.html", "Environment"),
      "EDL.md": ("edl.html", "EDL"),
      "CHANGELOG.md": ("changelog.html", "Changelog"),
      "docs/SHORTS_FLOW.md": ("shortsflow.html", "Shorts flow (legacy)")}
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{proj}: {title}</title></head><body><main><div id="md"></div><pre id="raw" hidden></pre></main>
<script src="project.js"></script><script src="nav.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const SRC = {src};
const raw = document.getElementById("raw"), md = document.getElementById("md");
if (window.marked) {{
  md.innerHTML = marked.parse(SRC);
  md.querySelectorAll("h1,h2,h3,h4").forEach(h => {{ h.id = h.textContent.trim().toLowerCase().replace(/[^\\p{{L}}\\p{{N}}_\\- ]/gu, "").replace(/ /g, "-"); }});   // same anchors as GitHub, so the contents links work
  if ({copy}) document.querySelectorAll("h2").forEach(h => {{
    const b = document.createElement("button"); b.className = "copy"; b.textContent = "Copy section";
    b.onclick = () => {{ let t = h.textContent + "\\n", n = h.nextElementSibling; while (n && n.tagName !== "H2") {{ t += n.innerText + "\\n"; n = n.nextElementSibling; }} copyText(t.trim()); b.textContent = "Copied"; }};
    h.appendChild(b);
  }});
  if ({stats}) {{
    const lines = SRC.split(/\\r\\n|\\r|\\n/).length;
    const words = (SRC.match(/\\b\\w+\\b/g) || []).length;
    const chars = SRC.length;
    const h2s = md.querySelectorAll("h2").length;
    const headings = md.querySelectorAll("h1,h2,h3,h4,h5,h6").length;
    const readMin = Math.max(1, Math.round(words / 200));
    const sb = document.createElement("div");
    sb.id = "doc-stats";
    sb.style.cssText = "margin-top:40px;padding:16px 20px;background:#14141c;border:1px solid #2a2a38;border-radius:10px;font-size:14px;color:#bbb;display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center";
    sb.innerHTML = '<span style="font-weight:700;color:#eee">📊 Document Stats:</span>' +
      '<span><b>' + lines.toLocaleString() + '</b> lines</span>' +
      '<span><b>' + words.toLocaleString() + '</b> words</span>' +
      '<span><b>' + chars.toLocaleString() + '</b> characters</span>' +
      '<span><b>' + h2s + '</b> sections (' + headings + ' headings total)</span>' +
      '<span>~<b>' + readMin + '</b> min read</span>';
    document.querySelector("main").appendChild(sb);
  }}
}} else {{ raw.hidden = false; raw.textContent = SRC; }}
</script></body></html>"""
PROJ = json.load(open(ROOT / "remotion/src/project.json"))
_pj = ROOT / "assets/publish.json"
PROJ["publish"] = {x["id"]: x.get("post_url", "") for x in json.load(open(_pj)).get("platforms", [])} if _pj.exists() else {}
(ROOT / "project.js").write_text("window.PROJECT = " + json.dumps(PROJ, ensure_ascii=False) + ";")   # read by nav.js (brand, community link, notes footer)
for src, (out, title) in MD.items():
    if not (ROOT / src).exists(): continue
    text = (ROOT / src).read_text()
    if text.startswith("---\n"): text = text.split("---\n", 2)[2]
    html = PAGE.format(proj=PROJ["title"], title=title, src=json.dumps(text).replace("</", "<\\/"), copy="true" if src == "metadata.md" else "false", stats="true" if src == "MASTER_SPEC.md" else "false")
    (ROOT / out).write_text(html); print("built", out)
