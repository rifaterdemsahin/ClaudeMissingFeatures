import { AbsoluteFill, Series } from "remotion";
import overlays from "./overlays.json";
import { SlideBody } from "./Slide";
import { theme, FPS } from "./theme";
import project from "./project.json";

type Part = { seconds: number; kind: string; title: string; bullets?: string[]; line?: string; url?: string; note?: string };
export const outroParts = (): Part[] => ((overlays as { outro?: Part[] }).outro ?? []) as Part[];
export const outroFrames = () => outroParts().reduce((n, p) => n + Math.round(p.seconds * FPS), 0);

const Cta = ({ p }: { p: Part }) => (
  <AbsoluteFill style={{ background: `linear-gradient(135deg, ${theme.bg}, #1d1030)`, fontFamily: theme.font, color: theme.fg, justifyContent: "center", alignItems: "center", textAlign: "center", padding: 120 }}>
    <div style={{ fontSize: 44, fontWeight: 700, color: theme.accent, letterSpacing: 3, textTransform: "uppercase" }}>{project.brand}</div>
    <div style={{ fontSize: 128, fontWeight: 900, margin: "20px 0 30px" }}>{p.title}</div>
    <div style={{ fontSize: 56, fontWeight: 700, marginBottom: 40 }}>{p.line}</div>
    <div style={{ fontSize: 76, fontWeight: 900, color: "#000", background: theme.accent, borderRadius: 24, padding: "20px 56px" }}>{p.url}</div>
    <div style={{ fontSize: 40, marginTop: 44, opacity: 0.85 }}>{p.note}</div>
  </AbsoluteFill>
);

// Ending: summary slide(s) then the community call to action. Silent, no transitions.
export const Outro = () => (
  <Series>
    {outroParts().map((p, i) => (
      <Series.Sequence key={i} durationInFrames={Math.round(p.seconds * FPS)}>
        {p.kind === "cta" ? <Cta p={p} /> : <SlideBody title={p.title} bullets={p.bullets ?? []} />}
      </Series.Sequence>
    ))}
  </Series>
);
