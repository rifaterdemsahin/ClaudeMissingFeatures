#!/usr/bin/env python3
"""Measure the finished video so OKRs and the value-recognition score rest on numbers, not opinion.
Usage: python3 scripts/measure_video.py [remotion/out/long.mp4]   -> assets/metrics.json (ffmpeg + data files; ~1 min)"""
import json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p: json.load(open(ROOT / p))
video = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "remotion/out/long.mp4")
ov, subs, P = J("remotion/src/overlays.json"), J("remotion/src/subs.json"), J("remotion/src/project.json")
_m = re.search(r"=\s*(\{.*\});", (ROOT / "export_map.js").read_text()); M = json.loads(_m.group(1))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
def out(t):   # source -> export seconds; a time inside a cut maps to the next kept moment (same rule as the player and build_chapters.py)
    for a, b, r, m, o in M["segs"]:
        if a <= t < b + 1e-9: return o + (t - a) / r
        if t < a: return o
    return M["total"]
X = {"export_seconds": round(dur, 1), "video_seconds": M["total"], "outro_seconds": round(sum(p["seconds"] for p in ov.get("outro", [])), 1)}
# loudness (EBU R128 integrated) of the export
txt = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
X["loudness_lufs"] = float(I[-1]) if I else None; X["true_peak_dbfs"] = float(TP[-1]) if TP else None
# speech: words, speaking time, pace, silences between cues (source timeline, excluding muted speed-ups)
words = [w for c in subs for w in c["words"]]; spoken = sum(min(w["to"] - w["from"], 1.2) for w in words)
mutes = [(s["from"], s["to"]) for s in ov["speedups"] if s.get("mute")] + [tuple(c) for c in J("remotion/src/cuts.json")]   # muted speed-ups and cuts hide the silence
cues = sorted(subs, key=lambda c: c["from"]); gaps = []
for a, b in zip(cues, cues[1:]):
    g0, g1 = a["to"], b["from"]
    if g1 - g0 > 3 and not any(m0 - 0.5 <= g0 and g1 <= m1 + 0.5 for m0, m1 in mutes): gaps.append([round(g0, 1), round(g1, 1)])
X.update({"words": len(words), "words_per_minute": round(len(words) / max(spoken / 60, 0.1)), "dead_air_gaps": len(gaps), "dead_air_seconds": round(sum(b - a for a, b in gaps), 1), "dead_air_percent": round(100 * sum(b - a for a, b in gaps) / M["total"], 1), "longest_silence_s": round(max([b - a for a, b in gaps] or [0]), 1), "dead_air_ranges_source": gaps})
rep = ROOT / "assets/repeats.txt"; st = 0
if rep.exists():
    sec = "";
    for l in rep.read_text().splitlines():
        if l.startswith("#"): sec = l
        elif l.strip() and "stutters" in sec: st += 1
X["stutter_spots"] = st
# structure: first problem statement, first action, takeaways, CTA
first_slide = min([s["from"] for s in ov["slides"]] or [0]); ch = J("assets/chapters.json") if (ROOT / "assets/chapters.json").exists() else []
X["time_to_problem_s"] = round(out(first_slide) or first_slide, 1)
X["time_to_first_action_s"] = round(out(ch[1][0]) or ch[1][0], 1) if len(ch) > 1 else None
X["chapters"] = len(ch) + len(M.get("outro", [])); starts = [out(c[0]) or c[0] for c in ch] + [o[0] for o in M.get("outro", [])]
X["chapter_min_len_s"] = round(min([b - a for a, b in zip(starts, starts[1:])] + [(M.get("outro") or [[0, "", 99]])[-1][2]]), 1)
o_sum = next((p for p in ov.get("outro", []) if p["kind"] != "cta"), None); o_cta = next((p for p in ov.get("outro", []) if p["kind"] == "cta"), None)
X["summary_points"] = len(o_sum.get("bullets", [])) if o_sum else 0; X["cta_seconds"] = o_cta["seconds"] if o_cta else 0
md = (ROOT / "metadata.md").read_text() if (ROOT / "metadata.md").exists() else ""; url = P["community"]["url"].split("//")[-1]
X["url_in_description_and_pinned"] = md.count(url) >= 2
X["slides"] = len(ov["slides"]); X["blur_boxes"] = len(ov["blurs"]); X["speedups"] = len(ov["speedups"])
lk = ROOT / "assets/export_leaks.json"; X["privacy_leaks"] = len(json.load(open(lk))) if lk.exists() else None
# residual steady noise after the audio fix (haze above the clean part, worst 20 s block after the fix)
try:
    r = subprocess.run([sys.executable, str(ROOT / "scripts/denoise_audio.py"), video, "--scan"], capture_output=True, text=True).stdout.splitlines()[-1]
    blocks = [(int(a), int(b)) for a, b in re.findall(r"(\d+):([+-]?\d+)", r)]; fix = min([a["from"] for a in J("assets/audio_fixes.json")] or [0]); fx = out(fix) or fix
    X["noise_haze_max_db_after_fix"] = max([b for t, b in blocks if t >= fx + 20 and t < dur - 40] or [None])
except Exception as e: X["noise_haze_max_db_after_fix"] = None
(ROOT / "assets/metrics.json").write_text(json.dumps(X, indent=1)); print(json.dumps({k: v for k, v in X.items() if k != "dead_air_ranges_source"}, indent=1))
