import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate } from "remotion";
import { FPS, theme } from "./theme";

// Base layer: the synced 1080p screen recording + Zoom voice. Add overlays below.
export const LongForm = () => {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 10, 3 * FPS, 3 * FPS + 15], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <OffthreadVideo src={staticFile("base.mp4")} />
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "flex-start", padding: 60, opacity: titleOpacity }}>
        <div style={{ fontFamily: theme.font, fontSize: 64, fontWeight: 800, color: theme.fg, background: "rgba(0,0,0,.65)", padding: "14px 28px", borderRadius: 16, borderLeft: `10px solid ${theme.accent}` }}>
          Claude Missing Features
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
