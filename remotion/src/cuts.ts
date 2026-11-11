import cutsJson from "./cuts.json";
import { DURATION, FPS } from "./theme";

// Cuts are [from,to] seconds on the SOURCE (base.mp4) timeline. Edit cuts.json only.
export type Seg = { src0: number; src1: number; out0: number; frames: number };

export const getSegments = (): Seg[] => {
  const total = DURATION / FPS;
  const cuts = [...(cutsJson as number[][])].sort((a, b) => a[0] - b[0]);
  const segs: Seg[] = [];
  let pos = 0, out = 0;
  const push = (a: number, b: number) => {
    const frames = Math.round((b - a) * FPS);
    if (frames > 0) { segs.push({ src0: a, src1: b, out0: out, frames }); out += frames; }
  };
  for (const [a, b] of cuts) { if (a > pos) push(pos, a); pos = Math.max(pos, b); }
  if (pos < total) push(pos, total);
  return segs;
};
export const totalFrames = () => getSegments().reduce((n, s) => n + s.frames, 0);

// output frame -> source seconds (for subtitles, chapters, overlays timed on the source)
export const srcTime = (outFrame: number): number => {
  const segs = getSegments();
  const s = [...segs].reverse().find((x) => outFrame >= x.out0) ?? segs[0];
  return s.src0 + (outFrame - s.out0) / FPS;
};
