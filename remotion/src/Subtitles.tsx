import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import subs from "./subs.json";
import { theme } from "./theme";

// Burned-in captions from subs.json (video timeline, seconds).
export const Subtitles = () => {
  const t = useCurrentFrame() / useVideoConfig().fps;
  const cue = subs.find((c) => t >= c.from && t < c.to);
  if (!cue) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 56 }}>
      <div style={{ fontFamily: theme.font, fontSize: 46, fontWeight: 700, color: "#fff", textAlign: "center", whiteSpace: "pre-line", maxWidth: 1500, lineHeight: 1.25, background: "rgba(0,0,0,.62)", padding: "8px 24px", borderRadius: 12 }}>
        {cue.text}
      </div>
    </AbsoluteFill>
  );
};
