import { getInputProps } from "remotion";
import cutsJson from "./cuts.json";
import variants from "./variants.json";
import overlays from "./overlays.json";
import { DURATION, FPS } from "./theme";

// Cuts remove source ranges; speedups play a range faster; inserts place a card at a source time (e.g. at a cut). All times are SOURCE seconds.
export type Insert = { at: number; seconds: number; kind?: string; animation?: string; title?: string; text?: string };
export type Seg = { src0: number; src1: number; rate: number; mute: boolean; out0: number; frames: number; insert?: Insert };
type Speed = { from: number; to: number; rate: number; mute?: boolean };

// Platform variants: the same edit cut for another platform (variants.json). Chosen at render time with --props '{"variant":"x"}'; Studio and the default render use "youtube" (the full video).
type VCfg = { keep?: number[][]; outro?: unknown[]; inserts?: boolean };
export const variantName = (): string => ((getInputProps() as { variant?: string }).variant) || "youtube";
export const variantCfg = (): VCfg => ((variants as unknown as Record<string, VCfg>)[variantName()] ?? {}) as VCfg;

export const speedups = (): Speed[] => [...(overlays.speedups as Speed[])].sort((a, b) => a.from - b.from);
export const inserts = (): Insert[] => [...(((overlays as { inserts?: Insert[] }).inserts ?? []) as Insert[])].sort((a, b) => a.at - b.at);

export const getSegments = (): Seg[] => {
  const total = DURATION / FPS;
  const cuts = [...(cutsJson as number[][])].sort((a, b) => a[0] - b[0]);
  const kept: [number, number][] = [];
  const base: number[][] = variantCfg().keep ?? [[0, total]];
  for (const [ba, bb] of base) {                // each wanted range, minus the global cuts
    let pos = ba;
    for (const [a, b] of cuts) { if (b <= pos || a >= bb) continue; if (a > pos) kept.push([pos, Math.min(a, bb)]); pos = Math.max(pos, b); }
    if (pos < bb) kept.push([pos, Math.min(bb, total)]);
  }
  const segs: Seg[] = [];
  const pending = (variantCfg().inserts ?? !variantCfg().keep) ? inserts() : [];
  let out = 0;
  const flush = (upTo: number) => {            // place every insert whose point is at or before the next video piece
    while (pending.length && pending[0].at <= upTo + 1e-6) {
      const ins = pending.shift() as Insert, frames = Math.round(ins.seconds * FPS);
      segs.push({ src0: ins.at, src1: ins.at, rate: 1, mute: true, out0: out, frames, insert: ins }); out += frames;
    }
  };
  const push = (a: number, b: number, rate: number, mute: boolean) => {
    const frames = Math.round(((b - a) * FPS) / rate);
    if (frames > 0) { flush(a); segs.push({ src0: a, src1: b, rate, mute, out0: out, frames }); out += frames; }
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
  flush(1e9);
  return segs;
};
export const videoFrames = () => getSegments().reduce((n, s) => n + s.frames, 0);

// output frame -> source seconds (captions, slides, blurs stay on the source timeline). Inside an insert the source time is frozen at the insert point.
export const srcTime = (outFrame: number): number => {
  const segs = getSegments();
  const s = [...segs].reverse().find((x) => outFrame >= x.out0) ?? segs[0];
  return s.insert ? s.insert.at : s.src0 + ((outFrame - s.out0) / FPS) * s.rate;
};
export const isInsertFrame = (outFrame: number): boolean => getSegments().some((s) => s.insert && outFrame >= s.out0 && outFrame < s.out0 + s.frames);
export const isMuted = (t: number): boolean => speedups().some((s) => s.mute && t >= s.from && t < s.to);
