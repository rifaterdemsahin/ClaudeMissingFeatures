import { AbsoluteFill } from "remotion";
import { theme } from "./theme";
import project from "./project.json";

export type SlideData = { from: number; to: number; title: string; bullets: string[] };

// Full-frame explainer slide. No transitions (owner feedback): it simply appears and disappears.
export const SlideBody = ({ title, bullets }: { title: string; bullets: string[] }) => (
  <AbsoluteFill style={{ background: `linear-gradient(135deg, ${theme.bg}, #1d1030)`, fontFamily: theme.font, color: theme.fg, padding: "110px 150px", justifyContent: "flex-start" }}>
    <div style={{ fontSize: 40, fontWeight: 700, color: theme.accent, letterSpacing: 3, textTransform: "uppercase" }}>{project.brand}</div>
    <div style={{ fontSize: 96, fontWeight: 900, margin: "18px 0 50px" }}>{title}</div>
    {bullets.map((b, i) => (
      <div key={i} style={{ display: "flex", gap: 24, alignItems: "flex-start", fontSize: 48, fontWeight: 600, lineHeight: 1.3, marginBottom: 26 }}>
        <span style={{ color: theme.accent, fontWeight: 900 }}>{i + 1}</span>
        <span>{b}</span>
      </div>
    ))}
  </AbsoluteFill>
);
export const Slide = ({ s }: { s: SlideData; t?: number }) => <SlideBody title={s.title} bullets={s.bullets} />;
