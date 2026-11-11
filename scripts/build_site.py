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
    html = PAGE.format(proj=PROJ["title"], title=title, src=json.dumps(text).replace("</", "<\\/"), copy="true" if src == "metadata.md" else "false")
    (ROOT / out).write_text(html); print("built", out)
