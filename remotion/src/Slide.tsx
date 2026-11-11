import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";

export type SlideData = { from: number; to: number; title: string; bullets: string[] };

// Full-frame explainer slide. `t` = source seconds. Bullets spring in one after another.
export const Slide = ({ s, t }: { s: SlideData; t: number }) => {
  const { fps } = useVideoConfig();
  const opacity = interpolate(t, [s.from, s.from + 0.35, s.to - 0.35, s.to], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ opacity, background: `linear-gradient(135deg, ${theme.bg}, #1d1030)`, fontFamily: theme.font, color: theme.fg, padding: "110px 150px", justifyContent: "flex-start" }}>
      <div style={{ fontSize: 40, fontWeight: 700, color: theme.accent, letterSpacing: 3, textTransform: "uppercase" }}>Claude Missing Features</div>
      <div style={{ fontSize: 96, fontWeight: 900, margin: "18px 0 50px" }}>{s.title}</div>
      {s.bullets.map((b, i) => {
        const p = spring({ frame: (t - s.from - 0.5 - i * 0.9) * fps, fps, config: { damping: 16, stiffness: 140 } });
        return (
          <div key={i} style={{ display: "flex", gap: 24, alignItems: "flex-start", fontSize: 48, fontWeight: 600, lineHeight: 1.3, marginBottom: 26, opacity: Math.max(0, Math.min(1, p)), transform: `translateX(${(1 - Math.min(p, 1)) * 60}px)` }}>
            <span style={{ color: theme.accent, fontWeight: 900 }}>{i + 1}</span>
            <span>{b}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
