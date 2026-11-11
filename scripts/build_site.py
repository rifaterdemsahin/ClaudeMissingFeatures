"""Render the Markdown docs into site pages. Run: python3 -I scripts/build_site.py"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = {"MASTER_SPEC.md": ("spec.html", "Master spec v3"),
      "metadata.md": ("metadata.html", "YouTube metadata"),
      "README.md": ("readme.html", "README (Shorts flow)")}
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Missing Features: {title}</title></head><body><main><div id="md"></div><pre id="raw" hidden></pre></main>
<script src="nav.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const SRC = {src};
const raw = document.getElementById("raw"), md = document.getElementById("md");
if (window.marked) {{
  md.innerHTML = marked.parse(SRC);
  if ({copy}) document.querySelectorAll("h2").forEach(h => {{
    const b = document.createElement("button"); b.className = "copy"; b.textContent = "Copy section";
    b.onclick = () => {{ let t = h.textContent + "\\n", n = h.nextElementSibling; while (n && n.tagName !== "H2") {{ t += n.innerText + "\\n"; n = n.nextElementSibling; }} copyText(t.trim()); b.textContent = "Copied"; }};
    h.appendChild(b);
  }});
}} else {{ raw.hidden = false; raw.textContent = SRC; }}
</script></body></html>"""
for src, (out, title) in MD.items():
    text = (ROOT / src).read_text()
    if text.startswith("---\n"): text = text.split("---\n", 2)[2]
    html = PAGE.format(title=title, src=json.dumps(text).replace("</", "<\\/"), copy="true" if src == "metadata.md" else "false")
    (ROOT / out).write_text(html); print("built", out)
