#!/usr/bin/env python3
"""Remove steady background noise (hoover, fan) locally with noisereduce, learned from a noise-only stretch of the same recording.
Usage: python3 scripts/denoise_audio.py in.mp4 out.mp4 --noise 592 622 --from 566 [--strength 0.8]
Video is stream-copied. Prints the haze (1.5-6 kHz noise floor) before/after and the speech level change; want haze ~0 dB vs the clean part, speech > -3 dB.
Find the noise start/end first: python3 scripts/denoise_audio.py in.mp4 --scan"""
import sys, os, subprocess, tempfile, argparse, pathlib
def ensure():
    try: import noisereduce, soundfile, numpy; return
    except ImportError: pass
    v = pathlib.Path.home() / ".cache/cmf-venv"
    if not (v / "bin/python").exists(): subprocess.check_call([sys.executable, "-m", "venv", str(v)])
    subprocess.check_call([str(v / "bin/pip"), "install", "-q", "numpy", "scipy", "noisereduce", "soundfile"])
    os.execv(str(v / "bin/python"), [str(v / "bin/python")] + sys.argv)
ensure()
import numpy as np, soundfile as sf, noisereduce as nr
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out", nargs="?"); ap.add_argument("--noise", nargs=2, type=float); ap.add_argument("--from", dest="frm", type=float); ap.add_argument("--strength", type=float, default=0.8); ap.add_argument("--scan", action="store_true")
a = ap.parse_args(); tmp = pathlib.Path(tempfile.mkdtemp())
def haze(path):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", str(tmp / "m.wav")])
    x, sr = sf.read(str(tmp / "m.wav"), dtype="float32"); N = 1600; nf = len(x) // N
    S = np.abs(np.fft.rfft(x[:nf * N].reshape(nf, N) * np.hanning(N), axis=1)); f = np.fft.rfftfreq(N, 1 / sr)
    hz = 20 * np.log10(S[:, (f >= 1500) & (f < 6000)].mean(1) + 1e-9)
    H = np.array([np.percentile(hz[k * 10:(k + 1) * 10], 20) for k in range(nf // 10)]); L = 20 * np.log10(np.sqrt((x[:len(x) // sr * sr].reshape(-1, sr) ** 2).mean(1)) + 1e-9)
    return H, L
H0, L0 = haze(a.inp)
if a.scan:
    base = np.median(H0[:max(60, len(H0) // 4)]); print("haze above the early (clean) baseline, per 20 s (>+6 dB = steady noise):"); print(" ".join(f"{t}:{H0[t:t+20].mean()-base:+.0f}" for t in range(0, len(H0), 20))); sys.exit(0)
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", str(tmp / "a.wav")])
y, sr = sf.read(str(tmp / "a.wav"), dtype="float32"); noise = y[int(a.noise[0] * sr):int(a.noise[1] * sr)]; t0 = int(a.frm * sr)
out = nr.reduce_noise(y=y[t0:].T, sr=sr, y_noise=noise.T, stationary=True, prop_decrease=a.strength, n_fft=2048, freq_mask_smooth_hz=300, time_mask_smooth_ms=60).T
fade = int(1.5 * sr); w = np.linspace(0, 1, fade)[:, None]; res = y.copy(); res[t0:] = out; res[t0:t0 + fade] = y[t0:t0 + fade] * (1 - w) + out[:fade] * w
sf.write(str(tmp / "c.wav"), res, sr, subtype="FLOAT")
subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-i", str(tmp / "c.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", a.out])   # faststart: moov at the front, else Remotion frame lookups are slow
H1, L1 = haze(a.out); base = np.median(H0[:max(60, int(a.frm) - 10)]); n = min(len(L0), len(L1)); sp = L0 > np.percentile(L0, 60); sp[:int(a.frm)] = False
print("haze vs clean baseline, per 60 s after --from:", " ".join(f"{t}: {H0[t:t+60].mean()-base:+.0f}->{H1[t:t+60].mean()-base:+.0f}" for t in range(int(a.frm), min(len(H0), len(H1)), 60)))
print("speech level change %.1f dB" % float((L1[:n][sp[:n]] - L0[:n][sp[:n]]).mean()), "->", a.out)
