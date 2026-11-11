import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import overlays from "./overlays.json";
import { isInsertFrame, srcTime } from "./cuts";
import { Thumb } from "./Thumb";
import { theme } from "./theme";
import { Slide, SlideData } from "./Slide";

type Arrow = { x1: number; y1: number; x2: number; y2: number };
type Img = { from: number; to: number; src: string; w?: number; h?: number; caption?: string; caption2?: string; highlight?: { x: number; y: number; w: number; h: number }; arrow?: Arrow };
type Blur = { from: number; to: number; x: number; y: number; w: number; h: number };
type LowerThird = { from: number; to: number; text: string; label?: string };

// intro card (hides the OBS window) -> slides (cover personal screen content) -> blur boxes -> images. All on SOURCE time.
export const ImageOverlays = () => {
  const frame = useCurrentFrame();
  if (isInsertFrame(frame)) return null;
  const t = srcTime(frame);
  const intro = overlays.intro_card;
  return (
    <>
      {[...(overlays.blurs as Blur[]), ...(((overlays as { manual_blurs?: Blur[] }).manual_blurs ?? []) as Blur[])].filter((b) => t >= b.from && t < b.to).map((b, i) => (
        <div key={"b" + i} style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)", background: "rgba(18,18,22,.6)", borderRadius: 8 }} />
      ))}
      {(overlays.slides as SlideData[]).filter((s) => t >= s.from && t < s.to).map((s, i) => <Slide key={"s" + i} s={s} />)}
      {(overlays.images as Img[]).filter((o) => t >= o.from && t < o.to).map((o, i) => <ImageCard key={"i" + i} o={o} />)}
      {(((overlays as { lower_thirds?: LowerThird[] }).lower_thirds ?? []) as LowerThird[]).filter((l) => t >= l.from && t < l.to).map((l, i) => (
        <div key={"l" + i} style={{ position: "absolute", left: 80, bottom: 215, maxWidth: 1250, padding: "18px 30px", background: "rgba(10,10,16,.88)", borderLeft: `12px solid ${theme.accent}`, borderRadius: 10, fontFamily: theme.font, color: "#fff" }}>
          {l.label && <div style={{ fontSize: 26, fontWeight: 800, color: theme.accent, letterSpacing: 3, textTransform: "uppercase", marginBottom: 6 }}>{l.label}</div>}
          <div style={{ fontSize: 46, fontWeight: 800, lineHeight: 1.2 }}>{l.text}</div>
        </div>
      ))}
      {t < intro.to && <AbsoluteFill><Thumb /></AbsoluteFill>}
    </>
  );
};

// Full-frame picture. With caption/highlight/arrow it becomes an "expected feature" card: caption on top,
// a box around the feature and an arrow pointing at it (coordinates are in the picture's own pixels). Static, no transitions.
const ImageCard = ({ o }: { o: Img }) => {
  const W = 1920, H = 1080, capH = o.caption ? 120 : 0, w = o.w ?? 1920, h = o.h ?? 1080;
  const sc = Math.min(W / w, (H - capH - (o.caption ? 175 : 0)) / h), iw = w * sc, ih = h * sc, ox = (W - iw) / 2, oy = capH + (o.caption ? 10 : (H - ih) / 2);
  const P = (x: number, y: number) => [ox + x * sc, oy + y * sc];
  let head = null, line = null;
  if (o.arrow) {
    const [x1, y1] = P(o.arrow.x1, o.arrow.y1), [x2, y2] = P(o.arrow.x2, o.arrow.y2), a = Math.atan2(y2 - y1, x2 - x1), L = 64, wd = 34;
    const bx = x2 - L * Math.cos(a), by = y2 - L * Math.sin(a);
    line = <line x1={x1} y1={y1} x2={bx} y2={by} stroke={theme.accent} strokeWidth={16} strokeLinecap="round" />;
    head = <polygon fill={theme.accent} points={`${x2},${y2} ${bx + wd * Math.sin(a)},${by - wd * Math.cos(a)} ${bx - wd * Math.sin(a)},${by + wd * Math.cos(a)}`} />;
  }
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {o.caption && (
        <div style={{ position: "absolute", left: 0, top: 0, width: W, height: capH, display: "flex", alignItems: "center", justifyContent: "center", gap: 22, fontFamily: theme.font, fontSize: 64, fontWeight: 800, color: "#fff", background: "#14141c" }}>
          <span>{o.caption}</span><span style={{ color: theme.accent }}>{o.caption2}</span>
        </div>
      )}
      <Img src={staticFile("img/" + o.src)} style={{ position: "absolute", left: ox, top: oy, width: iw, height: ih }} />
      {o.highlight && (() => { const [x, y] = P(o.highlight.x, o.highlight.y); return <div style={{ position: "absolute", left: x - 6, top: y - 6, width: o.highlight.w * sc + 12, height: o.highlight.h * sc + 12, border: `8px solid ${theme.accent}`, borderRadius: 18, boxShadow: "0 0 30px rgba(255,122,61,.6)" }} />; })()}
      <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>{line}{head}</svg>
    </AbsoluteFill>
  );
};
