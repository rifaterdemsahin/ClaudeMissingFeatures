"""Usage: python3 -I sync_clips.py voice8k.wav clip1.wav clip2.wav ...  (all mono 8 kHz WAV)
Prints voice_time = clip_time + X and a confidence (want > 3). Needs numpy + scipy."""
import sys, wave, numpy as np
from scipy.signal import fftconvolve
def load(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
def env(a, hop=80):
    n = len(a) // hop; e = np.log1p(np.abs(a[:n*hop]).reshape(n, hop).mean(1)); return e - e.mean()
ve = env(load(sys.argv[1]))
for c in sys.argv[2:]:
    ae = env(load(c)); xc = fftconvolve(ve, ae[::-1], mode="full")
    lags = np.arange(-(len(ae)-1), len(ve)); pk = int(np.argmax(xc))
    conf = xc[pk] / np.median(np.sort(np.abs(xc))[::-1][:50])
    print(f"{c}: dur {len(ae)/100:.2f}s  voice_time = clip_time + {lags[pk]/100:.2f}s  conf {conf:.1f}")
