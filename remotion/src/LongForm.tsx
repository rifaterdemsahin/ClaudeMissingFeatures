import { AbsoluteFill, OffthreadVideo, Sequence, Series, staticFile, interpolate } from "remotion";
import { FPS, theme } from "./theme";
import { Subtitles } from "./Subtitles";
import { getSegments, videoFrames } from "./cuts";
import { Outro, outroFrames } from "./Outro";
import { InsertCard } from "./InsertCard";
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
  const segs = getSegments();
  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      <Series>
        {segs.map((s, i) => (
          <Series.Sequence key={i} durationInFrames={s.frames}>
            {s.insert ? (
              <InsertCard ins={s.insert} />
            ) : (
              <OffthreadVideo
                src={staticFile("base.mp4")}
                startFrom={Math.round(s.src0 * FPS)}
                volume={(f) => (s.mute ? 0 : fade(f, s.frames, i > 0, i < segs.length - 1))}
                playbackRate={s.rate}
              />
            )}
          </Series.Sequence>
        ))}
      </Series>
      <Sequence from={0} durationInFrames={videoFrames()}>
        <ImageOverlays />
        <Subtitles />
      </Sequence>
      <Sequence from={videoFrames()} durationInFrames={outroFrames()}>
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
