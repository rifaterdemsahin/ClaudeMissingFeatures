import cutsJson from "./cuts.json";
import overlays from "./overlays.json";
import { DURATION, FPS } from "./theme";

// Cuts remove source ranges; speedups play a range faster (and optionally muted). All times are SOURCE seconds.
export type Seg = { src0: number; src1: number; rate: number; mute: boolean; out0: number; frames: number };
type Speed = { from: number; to: number; rate: number; mute?: boolean };

export const speedups = (): Speed[] => [...(overlays.speedups as Speed[])].sort((a, b) => a.from - b.from);

export const getSegments = (): Seg[] => {
  const total = DURATION / FPS;
  const cuts = [...(cutsJson as number[][])].sort((a, b) => a[0] - b[0]);
  const kept: [number, number][] = [];
  let pos = 0;
  for (const [a, b] of cuts) { if (a > pos) kept.push([pos, a]); pos = Math.max(pos, b); }
  if (pos < total) kept.push([pos, total]);
  const segs: Seg[] = [];
  let out = 0;
  const push = (a: number, b: number, rate: number, mute: boolean) => {
    const frames = Math.round(((b - a) * FPS) / rate);
    if (frames > 0) { segs.push({ src0: a, src1: b, rate, mute, out0: out, frames }); out += frames; }
  };
  for (const [ka, kb] of kept) {
    let p = ka;
    for (const s of speedups()) {
      const a = Math.max(s.from, ka), b = Math.min(s.to, kb);
      if (b <= a) continue;
      if (a > p) push(p, a, 1, false);
      push(a, b, s.rate, !!s.mute);
      p = b;
    }
    if (p < kb) push(p, kb, 1, false);
  }
  return segs;
};
export const videoFrames = () => getSegments().reduce((n, s) => n + s.frames, 0);

// output frame -> source seconds (captions, slides, blurs stay on the source timeline)
export const srcTime = (outFrame: number): number => {
  const segs = getSegments();
  const s = [...segs].reverse().find((x) => outFrame >= x.out0) ?? segs[0];
  return s.src0 + ((outFrame - s.out0) / FPS) * s.rate;
};
export const isMuted = (t: number): boolean => speedups().some((s) => s.mute && t >= s.from && t < s.to);
