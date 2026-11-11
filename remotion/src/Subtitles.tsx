import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import subs from "./subs.json";
import { isMuted, srcTime } from "./cuts";
import { theme } from "./theme";

type Word = { t: string; from: number; to: number };
type Cue = { from: number; to: number; text: string; words: Word[] };

// Animated captions: the phrase springs in, the spoken word pops and turns accent colour,
// upcoming words are dimmed, the phrase fades out.
export const Subtitles = () => {
  const frame = useCurrentFrame();
  const t = srcTime(frame);
  if (isMuted(t)) return null;
  const cue = (subs as Cue[]).find((c) => t >= c.from && t < c.to);
  if (!cue) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 56 }}>
      <div style={{
        display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0 26px", maxWidth: 1500,
        fontFamily: theme.font, fontSize: 50, fontWeight: 800, lineHeight: 1.3, padding: "10px 28px", borderRadius: 16,
        background: "rgba(0,0,0,.62)", 
      }}>
        {cue.words.map((w, i) => {
          const spoken = t >= w.from, active = spoken && t < w.to + 0.08;
          return (
            <span key={i} style={{
              color: active ? theme.accent : spoken ? "#fff" : "rgba(255,255,255,.55)",
              display: "inline-block",
              
            }}>{w.t}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
