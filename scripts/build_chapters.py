"""Chapters on the SOURCE and EXPORT timelines from assets/chapters.json (+ the outro). Writes chapters.js (player) and the Chapters block of metadata.md.
Run after build_subs.py (needs export_map.js): python3 -I scripts/build_chapters.py"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
C = json.load(open(ROOT / "assets/chapters.json")); M = json.loads(re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()).group(1))
def out(t):
    for a, b, r, m, o in M["segs"]:
        if a <= t < b + 1e-9: return o + (t - a) / r
    return M["total"]
exp = [[round(out(s), 1), n] for s, n in C] + [[o[0], o[1]] for o in M.get("outro", [])]
exp[-1][1] = "Join the Delivery Pilot community" if len(exp) > len(C) else exp[-1][1]
fmt = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
for i in range(1, len(exp)):
    if exp[i][0] - exp[i - 1][0] < 10: print("WARNING chapter shorter than 10 s:", exp[i - 1], exp[i])
(ROOT / "chapters.js").write_text("window.CHAPTERS = " + json.dumps({"src": C, "exp": exp}) + ";")
md = ROOT / "metadata.md"; t = md.read_text(); block = "Chapters (export timeline, first at 0:00, each at least 10 s):\n" + "\n".join(f"{fmt(s)} {n}" for s, n in exp) + "\n\n"
t = re.sub(r"Chapters[^\n]*:\n.*?\n\nTakeaways:", lambda m: block + "Takeaways:", t, flags=re.S); md.write_text(t)
print(len(exp), "export chapters; last at", fmt(exp[-1][0]))
