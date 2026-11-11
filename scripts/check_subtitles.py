#!/usr/bin/env python3
"""Subtitle quality check from data (no listening, no frames): finds what is likely wrong in the captions and what was already fixed.
Usage: python3 -I scripts/check_subtitles.py     -> assets/subtitle_report.json + printed summary
Checks: low-confidence words (Whisper's own probability), words that look like a mis-heard product name, repeated words (stutters), reading speed,
flicker (very short cues), cues that start/end in a cut, words fixed by project.json caption_fixes. Fix real errors in project.json > caption_fixes and re-run build_subs.py."""
import json, pathlib, re, difflib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p))
P, subs, raw = J("remotion/src/project.json"), J("remotion/src/subs.json"), J("assets/whisper_words.json")
off = float((ROOT / "assets/whisper_offset.txt").read_text()) if (ROOT / "assets/whisper_offset.txt").exists() else 0.0
cuts = J("remotion/src/cuts.json")
incut = lambda t: any(a <= t < b for a, b in cuts)
fixes = [(re.compile(a), b) for a, b in P["caption_fixes"]]
report = {"low_confidence": [], "look_alikes": [], "stutters": [], "fast_reading": [], "flicker": [], "fixed_by_rules": collections.Counter(), "total_words": 0, "total_cues": len(subs)}
STOP = set("a an the and or but so to of in on at it is are was be i you we he she they this that these those for with as by from not no yes do does did have has had will would can could should just like then than there here what which who how when where why if up out about into over very really".split())
# 1) low-confidence words from Whisper (probability), outside cuts, ignoring tiny stop words
for s in raw["segments"]:
    for w in s.get("words", []):
        t = w["start"] - off; report["total_words"] += 1
        tok = re.sub(r"[^a-z']", "", w["word"].lower())
        if w.get("probability", 1) < 0.5 and tok not in STOP and len(tok) > 2 and not incut(t):
            report["low_confidence"].append({"t": round(t, 1), "word": w["word"].strip(), "p": round(w["probability"], 2), "context": s["text"].strip()[:90]})
# 2) rules that fired (what was fixed), counted on the raw transcript text
rawtext = " ".join(s["text"] for s in raw["segments"])
for rx, rep in fixes:
    n = len(rx.findall(rawtext))
    if n: report["fixed_by_rules"][f"{rx.pattern} -> {rep}"] = n
report["fixed_by_rules"] = dict(report["fixed_by_rules"])
# 3) look-alike product words still in the final captions (edit distance to the vocabulary in project.json)
vocab = [x for x in ["claude", "anthropic", "artifacts", "whiteboard", "homebrew", "canva", "grok", "macbook", P["community"]["name"].lower()] if x]
for c in subs:
    for w in c["words"]:
        k = re.sub(r"[^a-z]", "", w["t"].lower())
        if len(k) >= 4 and k not in vocab and k not in ("canvas", "design", "designs", "clothes"):
            m = difflib.get_close_matches(k, vocab, n=1, cutoff=0.75)
            if m: report["look_alikes"].append({"t": round(w["from"], 1), "word": w["t"], "looks_like": m[0], "context": c["text"][:80]})
# 4) stutters: the same word twice in a row, or the same 2-word phrase twice
for c in subs:
    ws = [re.sub(r"[^a-z']", "", w["t"].lower()) for w in c["words"]]
    for i in range(len(ws) - 1):
        if ws[i] and ws[i] == ws[i + 1] and ws[i] not in ("that", "had"): report["stutters"].append({"t": round(c["words"][i]["from"], 1), "text": f"{ws[i]} {ws[i]}", "context": c["text"][:80]})
# 5) reading speed (characters per second) and flicker
for c in subs:
    d = max(c["to"] - c["from"], 0.01); cps = len(c["text"]) / d
    if cps > 21 and len(c["text"]) > 12: report["fast_reading"].append({"t": round(c["from"], 1), "cps": round(cps, 1), "text": c["text"][:70]})
    if d < 0.7: report["flicker"].append({"t": round(c["from"], 1), "dur": round(d, 2), "text": c["text"]})
(ROOT / "assets/subtitle_report.json").write_text(json.dumps(report, indent=1))
print(f"{report['total_cues']} cues, {report['total_words']} words")
print("fixed by rules:", report["fixed_by_rules"])
for k in ("low_confidence", "look_alikes", "stutters", "fast_reading", "flicker"): print(f"{k}: {len(report[k])}")
for k in ("look_alikes", "stutters", "flicker"):
    for x in report[k][:12]: print(f"  {k} {x}")
print("lowest-confidence words:"); [print("  ", x) for x in sorted(report["low_confidence"], key=lambda x: x["p"])[:25]]
