import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import subs from "./subs.json";
import { srcTime } from "./cuts";
import { theme } from "./theme";

type Word = { t: string; from: number; to: number };
type Cue = { from: number; to: number; text: string; words: Word[] };

// Animated captions: the phrase springs in, the spoken word pops and turns accent colour,
// upcoming words are dimmed, the phrase fades out.
export const Subtitles = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = srcTime(frame);
  const cue = (subs as Cue[]).find((c) => t >= c.from && t < c.to);
  if (!cue) return null;
  const inF = (t - cue.from) * fps;
  const enter = spring({ frame: inF, fps, config: { damping: 14, stiffness: 160 } });
  const fade = interpolate(t, [cue.to - 0.15, cue.to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 56 }}>
      <div style={{
        display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0 26px", maxWidth: 1500,
        fontFamily: theme.font, fontSize: 50, fontWeight: 800, lineHeight: 1.3, padding: "10px 28px", borderRadius: 16,
        background: "rgba(0,0,0,.62)", opacity: enter * fade, transform: `translateY(${(1 - enter) * 24}px) scale(${0.94 + 0.06 * enter})`,
      }}>
        {cue.words.map((w, i) => {
          const spoken = t >= w.from, active = spoken && t < w.to + 0.08;
          const pop = active ? spring({ frame: (t - w.from) * fps, fps, config: { damping: 9, stiffness: 260 } }) : 1;
          return (
            <span key={i} style={{
              color: active ? theme.accent : spoken ? "#fff" : "rgba(255,255,255,.55)",
              transform: `scale(${active ? 1 + 0.07 * Math.min(pop, 1.4) : 1})`, display: "inline-block",
              textShadow: active ? `0 0 18px ${theme.accent}88` : "none",
            }}>{w.t}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
