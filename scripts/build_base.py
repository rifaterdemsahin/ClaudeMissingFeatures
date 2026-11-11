#!/usr/bin/env python3
"""Sync N screen clips to the voice WAV and render the 1080p30 base video, all locally (ffmpeg + scipy).
Usage: python3 scripts/build_base.py <folder with *.mp4 and one *.WAV> <out.mp4> [--sync-only]
Writes assets/base_info.json and sets DURATION in remotion/src/theme.ts."""
import sys, os, glob, json, subprocess, re, pathlib, tempfile
def ensure_np():
    try: import numpy, scipy; return
    except ImportError: pass
    venv = pathlib.Path.home() / ".cache/cmf-venv"
    if not (venv / "bin/python").exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)]); subprocess.check_call([str(venv / "bin/pip"), "install", "-q", "numpy", "scipy"])
    os.execv(str(venv / "bin/python"), [str(venv / "bin/python")] + sys.argv)
ensure_np()
import numpy as np
from scipy.signal import fftconvolve
ROOT = pathlib.Path(__file__).resolve().parent.parent
folder, out = pathlib.Path(sys.argv[1]).expanduser(), pathlib.Path(sys.argv[2]).expanduser()
clips = sorted(glob.glob(str(folder / "*.mp4"))); voice = (glob.glob(str(folder / "*.WAV")) + glob.glob(str(folder / "*.wav")) or [None])[0]
assert clips and voice, "need *.mp4 clips and one *.WAV in the folder"
tmp = pathlib.Path(tempfile.mkdtemp())
def mono(src, name):
    p = tmp / name; subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "8000", str(p)]); return p
def env(p):
    import wave
    w = wave.open(str(p)); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    n = len(a) // 80; e = np.log1p(np.abs(a[:n * 80]).reshape(n, 80).mean(1)); return e - e.mean()
dur = lambda f: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
ve = env(mono(voice, "voice.wav")); vdur = dur(voice); info = []
for c in clips:
    ae = env(mono(c, "c.wav")); xc = fftconvolve(ve, ae[::-1], mode="full"); lags = np.arange(-(len(ae) - 1), len(ve)); pk = int(np.argmax(xc))
    conf = float(xc[pk] / np.median(np.sort(np.abs(xc))[::-1][:50])); info.append({"clip": os.path.basename(c), "offset": round(float(lags[pk] / 100), 2), "dur": round(dur(c), 2), "conf": round(conf, 1)})
info.sort(key=lambda x: x["offset"])
for i, x in enumerate(info):
    nxt = info[i + 1]["offset"] if i + 1 < len(info) else vdur
    x["keep"] = round(min(x["dur"], nxt - x["offset"]), 2)
    x["gap_to_next"] = round(nxt - (x["offset"] + x["dur"]), 2) if i + 1 < len(info) else None
    if x["conf"] < 3: print("WARNING low sync confidence", x, file=sys.stderr)
total = round(sum(x["keep"] for x in info), 2); start = info[0]["offset"]
res = {"voice": os.path.basename(voice), "voice_dur": round(vdur, 2), "voice_start": start, "clips": info, "total_s": total, "frames": round(total * 30)}
(ROOT / "assets").mkdir(exist_ok=True); (ROOT / "assets/base_info.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res))
if "--sync-only" in sys.argv: sys.exit(0)
FG = "fps=30,split[a][b];[a]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,boxblur=12:2,scale=1920:1080,eq=brightness=-0.08[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1,format=yuv420p"
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"]
for x in info: cmd += ["-i", str(folder / x["clip"])]
cmd += ["-ss", str(start), "-i", voice]
fc = ";".join(f"[{i}:v]trim=0:{x['keep']},setpts=PTS-STARTPTS,{FG}[v{i}]" for i, x in enumerate(info))
fc += ";" + "".join(f"[v{i}]" for i in range(len(info))) + f"concat=n={len(info)}:v=1:a=0[v];[{len(info)}:a]highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
subprocess.check_call(cmd)
th = ROOT / "remotion/src/theme.ts"
if th.exists(): th.write_text(re.sub(r"DURATION = \d+;", f"DURATION = {res['frames']};", th.read_text()))
print("rendered", out, "frames", res["frames"])
