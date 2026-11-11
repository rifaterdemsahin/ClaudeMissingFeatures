import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import overlays from "./overlays.json";
import { srcTime } from "./cuts";
import { Thumb } from "./Thumb";
import { Slide, SlideData } from "./Slide";

type Img = { from: number; to: number; src: string };
type Blur = { from: number; to: number; x: number; y: number; w: number; h: number };

// intro card (hides the OBS window) -> slides (cover personal screen content) -> blur boxes -> images. All on SOURCE time.
export const ImageOverlays = () => {
  const t = srcTime(useCurrentFrame());
  const intro = overlays.intro_card;
  const introOpacity = interpolate(t, [intro.to - 0.3, intro.to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <>
      {(overlays.blurs as Blur[]).filter((b) => t >= b.from && t < b.to).map((b, i) => (
        <div key={"b" + i} style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)", background: "rgba(18,18,22,.6)", borderRadius: 8 }} />
      ))}
      {(overlays.slides as SlideData[]).filter((s) => t >= s.from && t < s.to).map((s, i) => <Slide key={"s" + i} s={s} t={t} />)}
      {(overlays.images as Img[]).filter((o) => t >= o.from && t < o.to).map((o, i) => {
        const o1 = interpolate(t, [o.from, o.from + 0.2, o.to - 0.2, o.to], [0, 1, 1, 0]);
        return (
          <AbsoluteFill key={"i" + i} style={{ opacity: o1, background: "#000", justifyContent: "center", alignItems: "center" }}>
            <Img src={staticFile("img/" + o.src)} style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} />
          </AbsoluteFill>
        );
      })}
      {t < intro.to && <AbsoluteFill style={{ opacity: introOpacity }}><Thumb /></AbsoluteFill>}
    </>
  );
};
