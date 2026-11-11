#!/usr/bin/env python3
"""Keep a linked table of contents at the top of MASTER_SPEC.md (between <!--TOC--> and <!--/TOC-->). Anchors follow GitHub's rule
(lowercase, drop everything except letters, digits, _ - and spaces, spaces become hyphens), the site uses the same rule. Run: python3 -I scripts/build_toc.py"""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = ROOT / "MASTER_SPEC.md"; s = spec.read_text()
slug = lambda t: re.sub(r"[^\w\- ]", "", t.strip().lower(), flags=re.UNICODE).replace(" ", "-")
heads = [m.group(1).strip() for m in re.finditer(r"^## (.+)$", re.sub(r"<!--TOC-->.*?<!--/TOC-->", "", s, flags=re.S), flags=re.M) if not m.group(1).startswith("📑")]
toc = "<!--TOC-->\n## 📑 Contents\n\n" + "\n".join(f"{i}. [{h}](#{slug(h)})" for i, h in enumerate(heads, 1)) + "\n<!--/TOC-->"
if "<!--TOC-->" in s:
    s = re.sub(r"<!--TOC-->.*?<!--/TOC-->", toc, s, flags=re.S)
else:
    first = s.index("\n") + 1
    s = s[:first] + "\n" + toc + "\n" + s[first:]
spec.write_text(s); print(f"MASTER_SPEC.md: table of contents with {len(heads)} sections")
