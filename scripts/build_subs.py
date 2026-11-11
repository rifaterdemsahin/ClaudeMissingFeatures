"""Whisper JSON -> subtitles.srt / subtitles.vtt / remotion/src/subs.json on the VIDEO timeline.
Usage: python3 -I scripts/build_subs.py assets/whisper_raw.json 4.75"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
raw, offset = json.load(open(sys.argv[1])), float(sys.argv[2])
FIX = [(r"\b[Tt]he cloud\b", "Claude"), (r"\bcloud\b", "Claude"), (r"\bClouds?\b", "Claude"), (r"\b[Gg]rowth ?bot\b|\bGrogbot\b|\bgrowth bot\b", "Grok bot"),
       (r"\bhdml'?s\b", "HTML"), (r"\bKamba\b", "Canva"), (r"\bhomebrief\b", "Homebrew"), (r"\bbrief upgrade\b", "brew upgrade"),
       (r"\bwhite ?boards?\b", lambda m: m.group(0)[:1] + "hiteboard" + ("s" if m.group(0).endswith("s") else ""))]
def fix(t):
    for a, b in FIX: t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()
cues = []
for s in raw["segments"]:
    text = fix(s["text"]); st = s["start"] - offset; en = s["end"] - offset
    if en <= 0 or not text: continue
    st = max(st, 0.0); en = min(en, st + max(1.5, len(text) / 13))   # no long ghost holds over silence
    words, chunks, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 70 and cur: chunks.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: chunks.append(cur)
    tot, t0 = sum(len(c) for c in chunks), st
    for c in chunks:
        d = (en - st) * len(c) / tot; cues.append([round(t0, 2), round(t0 + d, 2), c]); t0 += d
for i in range(len(cues) - 1): cues[i][1] = min(cues[i][1], cues[i + 1][0])
def ts(x, sep):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"
def wrap(c):  # two balanced lines
    if len(c) <= 42: return c
    mid = len(c) // 2; i = min((m.start() for m in re.finditer(" ", c)), key=lambda p: abs(p - mid)); return c[:i] + "\n" + c[i + 1:]
(ROOT / "subtitles.srt").write_text("\n".join(f"{i+1}\n{ts(a,',')} --> {ts(b,',')}\n{wrap(c)}\n" for i, (a, b, c) in enumerate(cues)))
(ROOT / "subtitles.vtt").write_text("WEBVTT\n\n" + "\n".join(f"{ts(a,'.')} --> {ts(b,'.')}\n{wrap(c)}\n" for a, b, c in cues))
(ROOT / "remotion/src/subs.json").write_text(json.dumps([{"from": a, "to": b, "text": c} for a, b, c in cues]))
(ROOT / "subs.js").write_text("window.SUBS = " + json.dumps([{"from": a, "to": b, "text": c} for a, b, c in cues]) + ";")
print(len(cues), "cues")
