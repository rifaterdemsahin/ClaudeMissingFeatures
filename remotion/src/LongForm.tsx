import { AbsoluteFill, OffthreadVideo, Series, staticFile, useCurrentFrame, interpolate } from "remotion";
import { FPS, theme } from "./theme";
import { Subtitles } from "./Subtitles";
import { getSegments } from "./cuts";
import { ImageOverlays } from "./ImageOverlays";

const FADE = 3; // frames of audio fade at each cut
const fade = (f: number, n: number, fadeIn: boolean, fadeOut: boolean) => {
  let v = 1;
  if (fadeIn) v = Math.min(v, interpolate(f, [0, FADE], [0, 1], { extrapolateRight: "clamp" }));
  if (fadeOut) v = Math.min(v, interpolate(f, [n - FADE, n], [1, 0], { extrapolateLeft: "clamp" }));
  return v;
};

// Base layer = synced 1080p screen recording + voice, with cuts from cuts.json removed (3-frame audio fades at each cut).
export const LongForm = () => {
  const frame = useCurrentFrame();
  const segs = getSegments();
  const titleOpacity = interpolate(frame, [2.3 * FPS, 2.3 * FPS + 10, 5 * FPS, 5 * FPS + 15], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <Series>
        {segs.map((s, i) => (
          <Series.Sequence key={i} durationInFrames={s.frames}>
            <OffthreadVideo
              src={staticFile("base.mp4")}
              startFrom={Math.round(s.src0 * FPS)}
              volume={(f) => fade(f, s.frames, i > 0, i < segs.length - 1)}
            />
          </Series.Sequence>
        ))}
      </Series>
      <ImageOverlays />
      <Subtitles />
      <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "flex-start", padding: 60, opacity: titleOpacity }}>
        <div style={{ fontFamily: theme.font, fontSize: 64, fontWeight: 800, color: theme.fg, background: "rgba(0,0,0,.65)", padding: "14px 28px", borderRadius: 16, borderLeft: `10px solid ${theme.accent}` }}>
          Claude Missing Features
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
