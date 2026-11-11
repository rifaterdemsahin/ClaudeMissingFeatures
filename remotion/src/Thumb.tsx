import { AbsoluteFill } from "remotion";
import { theme } from "./theme";
import project from "./project.json";

export const Thumb = () => (
  <AbsoluteFill style={{ background: `linear-gradient(135deg, ${theme.bg}, #1d1030)`, fontFamily: theme.font, color: theme.fg, justifyContent: "center", padding: 120 }}>
    <div style={{ fontSize: 120, fontWeight: 900, lineHeight: 1.05 }}>{project.thumb.line1}</div>
    <div style={{ fontSize: 170, fontWeight: 900, color: theme.accent }}>{project.thumb.line2}</div>
  </AbsoluteFill>
);
