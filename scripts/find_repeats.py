"""List candidate cuts from the subtitle cues: stutters/repeated phrases and long silences.
Usage: python3 -I scripts/find_repeats.py   (reads remotion/src/subs.json, source timeline)"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
cues = json.load(open(ROOT / "remotion/src/subs.json"))
norm = lambda t: re.sub(r"[^a-z ]", "", t.lower()).split()
tm = lambda s: f"{int(s//60)}:{int(s%60):02d}"
print("# repeated phrases (same 4-word run again within 25 s, or an identical short cue)")
seen = {}
for c in cues:
    w = norm(c["text"])
    for i in range(len(w) - 3):
        g = " ".join(w[i:i+4])
        if g in seen and 0 < c["from"] - seen[g][0] < 25 and seen[g][1] != c["from"]:
            print(f"{tm(c['from'])}  repeats '{g}' (first at {tm(seen[g][0])}): {c['text'][:70]}")
            break
        seen[g] = (c["from"], c["from"])
print("\n# stutters (a word repeated back to back)")
for c in cues:
    m = re.search(r"\b(\w+)[, ]+\1\b", c["text"], re.I)
    if m and len(m.group(1)) > 2: print(f"{tm(c['from'])}  '{m.group(0)}': {c['text'][:70]}")
print("\n# gaps over 3 s between cues (silence / screen-only)")
for a, b in zip(cues, cues[1:]):
    if b["from"] - a["to"] > 3: print(f"{tm(a['to'])} -> {tm(b['from'])}  ({b['from']-a['to']:.1f}s)")
