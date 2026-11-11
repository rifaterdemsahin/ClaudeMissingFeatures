"""One-page text report so Claude reads ~1 page instead of looking at images. Usage: python3 -I scripts/report.py -> REPORT.md"""
import json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
L = ["# REPORT (generated locally; read this instead of viewing frames)\n"]
def load(p):
    f = ROOT / p
    return json.load(open(f)) if f.exists() else None
b = load("assets/base_info.json")
if b:
    L.append(f"## Base video\n- voice start offset {b['voice_start']} s; length {b['total_s']} s = {b['frames']} frames (theme.ts DURATION set)")
    for c in b["clips"]: L.append(f"- {c['clip']}: offset {c['offset']} s, keep {c['keep']} s, sync confidence {c['conf']} (want > 3), gap to next {c['gap_to_next']}")
s = load("remotion/src/subs.json")
if s: L.append(f"\n## Subtitles\n- {len(s)} cues; word timings {'yes' if s and s[0].get('words') else 'no'}; files subtitles.srt/.vtt")
r = ROOT / "assets/repeats.txt"
if r.exists(): L.append("\n## Cut candidates (stutters, repeats, gaps; nothing is cut yet)\n" + "\n".join("- " + x for x in r.read_text().splitlines() if x and not x.startswith("#"))[:3000])
p = load("assets/personal_windows.json")
if p is not None:
    L.append(f"\n## Personal windows to cover with slides ({len(p)})")
    for w in p: L.append(f"- {w['from']}-{w['to']} s: {w['said'][:140]}")
o = load("remotion/src/overlays.json")
if o: L.append(f"\n## Edits in overlays.json\n- slides {len(o['slides'])}, blur boxes {len(o['blurs'])}, speedups {len(o['speedups'])}, images {len(o['images'])}, intro card to {o['intro_card']['to']} s")
lk = load("assets/export_leaks.json")
if lk is not None: L.append(f"\n## Export privacy check (OCR of the final video)\n- {len(lk)} sensitive lines still visible" + "".join(f"\n  - {k['t']//60}:{k['t']%60:02d} {k['text']}" for k in lk[:15]))
(ROOT / "REPORT.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
