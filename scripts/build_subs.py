"""Whisper JSON -> subtitles.srt/.vtt (FINAL timeline, cuts applied), subs.js + remotion/src/subs.json (SOURCE timeline, with word timings).
Usage: python3 -I scripts/build_subs.py assets/whisper_words.json 4.75
Cuts live in remotion/src/cuts.json as [[from,to],...] seconds on the source (base.mp4) timeline."""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
raw, offset = json.load(open(sys.argv[1])), float(sys.argv[2])
cuts = sorted(json.load(open(ROOT / "remotion/src/cuts.json")))
FIX = [(r"\b[Tt]he cloud\b", "Claude"), (r"\bcloud\b", "Claude"), (r"\b[Cc]louds?\b", "Claude"),
       (r"\b[Gg]rowth ?bot\b|\bGrogbot\b", "Grok bot"), (r"\bhdml'?s\b", "HTML"), (r"\bKamba\b", "Canva"),
       (r"\bhomebrief\b", "Homebrew"), (r"\bbrief upgrade\b", "brew upgrade"),
       (r"\bwhite ?boards?\b", lambda m: m.group(0)[:1] + "hiteboard" + ("s" if m.group(0).endswith("s") else ""))]
def fix(t):
    for a, b in FIX: t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()
def remap(t):  # source seconds -> final seconds (None if inside a cut)
    removed = 0.0
    for a, b in cuts:
        if t >= b: removed += b - a
        elif t > a: return None
    return t - removed
cues = []
for s in raw["segments"]:
    text = fix(s["text"]); st = s["start"] - offset; en = s["end"] - offset
    if en <= 0 or not text: continue
    toks = text.split(); ow = s.get("words")
    if ow and len(ow) == len(toks):
        tw = [(w["start"] - offset, w["end"] - offset) for w in ow]
    else:  # fallback: spread by character length
        en = min(en, max(st, 0) + max(1.5, len(text) / 13)); tot = sum(len(t) for t in toks); t0 = st; tw = []
        for t in toks: d = (en - st) * len(t) / tot; tw.append((t0, t0 + d)); t0 += d
    chunks, cur = [], []
    for t, (a, b) in zip(toks, tw):
        a = max(a, 0.0); b = min(max(b, 0.0), a + 1.2)   # cap a word at 1.2 s so the highlight never sticks over silence
        if cur and (sum(len(x[0]) + 1 for x in cur) + len(t) > 70 or a - cur[-1][2] > 1.5): chunks.append(cur); cur = []   # new cue after a long gap
        cur.append((t, a, b))
    if cur: chunks.append(cur)
    for c in chunks:
        cues.append({"from": round(c[0][1], 2), "to": round(c[-1][2] + 0.25, 2), "text": " ".join(x[0] for x in c),
                     "words": [{"t": x[0], "from": round(x[1], 2), "to": round(x[2], 2)} for x in c]})
for i in range(len(cues) - 1): cues[i]["to"] = round(min(cues[i]["to"], cues[i + 1]["from"]), 2)
cues = [c for c in cues if c["to"] > c["from"]]
(ROOT / "remotion/src/subs.json").write_text(json.dumps(cues))
(ROOT / "subs.js").write_text("window.SUBS = " + json.dumps(cues) + ";")
final = []
for c in cues:
    a, b = remap(c["from"]), remap(c["to"] - 0.001)
    if a is not None and b is not None: final.append((a, b + 0.001, c["text"]))
def ts(x, sep):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"
def wrap(c):
    if len(c) <= 42: return c
    mid = len(c) // 2; i = min((m.start() for m in re.finditer(" ", c)), key=lambda p: abs(p - mid)); return c[:i] + "\n" + c[i + 1:]
(ROOT / "subtitles.srt").write_text("\n".join(f"{i+1}\n{ts(a,',')} --> {ts(b,',')}\n{wrap(c)}\n" for i, (a, b, c) in enumerate(final)))
(ROOT / "subtitles.vtt").write_text("WEBVTT\n\n" + "\n".join(f"{ts(a,'.')} --> {ts(b,'.')}\n{wrap(c)}\n" for a, b, c in final))
print(len(cues), "cues,", len(final), "after cuts,", "word timings" if raw["segments"][0].get("words") else "estimated word timings")
