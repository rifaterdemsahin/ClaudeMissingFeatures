import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import overlays from "./overlays.json";
import { srcTime } from "./cuts";
import { Thumb } from "./Thumb";

// 1) intro card: covers the OBS window at the start (fades out). 2) images from overlays.json shown full-frame.
export const ImageOverlays = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = srcTime(frame);
  const intro = overlays.intro_card;
  const introOpacity = interpolate(t, [intro.to - 0.3, intro.to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <>
      {t < intro.to && <AbsoluteFill style={{ opacity: introOpacity }}><Thumb /></AbsoluteFill>}
      {(overlays.images as { from: number; to: number; src: string }[]).filter((o) => t >= o.from && t < o.to).map((o, i) => {
        const o1 = interpolate(t, [o.from, o.from + 0.2, o.to - 0.2, o.to], [0, 1, 1, 0]);
        return (
          <AbsoluteFill key={i} style={{ opacity: o1, background: "#000", justifyContent: "center", alignItems: "center" }}>
            <Img src={staticFile("img/" + o.src)} style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} />
          </AbsoluteFill>
        );
      })}
    </>
  );
};
