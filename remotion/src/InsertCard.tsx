import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "./theme";
import type { Insert } from "./cuts";

// A card placed on the timeline at a cut. animation "hoover": a cartoon vacuum cleaner with noise waves, bobbing and sucking dust (frame-driven, like a GIF).
const Hoover = ({ f }: { f: number }) => {
  const bob = Math.sin(f / 5) * 7, nozzle = Math.sin(f / 7) * 55, wave = (k: number) => 0.35 + 0.65 * Math.abs(Math.sin((f + k * 9) / 6));
  const dust = Array.from({ length: 9 }, (_, i) => { const ph = ((f * 5 + i * 83) % 700) / 700; return { x: 1700 - ph * 520 + nozzle, y: 700 + Math.sin(i * 2.1) * 55 + ph * 20, o: 1 - ph * 0.9, r: 7 + (i % 3) * 4 }; });
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
      <g transform={`translate(0 ${bob})`}>
        {[0, 1, 2].map((k) => <path key={k} d={`M${470 - k * 38} ${600 - k * 26} q-34 ${46} 0 ${92}`} fill="none" stroke="#9ad0ff" strokeWidth={10} strokeLinecap="round" opacity={wave(k)} />)}
        <ellipse cx={740} cy={650} rx={200} ry={112} fill={theme.accent} />
        <ellipse cx={740} cy={572} rx={150} ry={72} fill="#ffa070" />
        <rect x={690} y={520} width={100} height={26} rx={13} fill="#7a3a1c" />
        <circle cx={600} cy={758} r={38} fill="#1b1b24" /><circle cx={600} cy={758} r={14} fill="#fff" />
        <circle cx={890} cy={758} r={38} fill="#1b1b24" /><circle cx={890} cy={758} r={14} fill="#fff" />
        <path d="M930 610 C1130 520 1120 370 1290 430" fill="none" stroke="#8d99ae" strokeWidth={38} strokeLinecap="round" />
        <line x1={1290} y1={430} x2={1480 + nozzle * 0.4} y2={660} stroke="#c9d1dc" strokeWidth={30} strokeLinecap="round" />
        <rect x={1380 + nozzle} y={650} width={230} height={48} rx={22} fill="#c9d1dc" />
        <rect x={1380 + nozzle} y={686} width={230} height={14} rx={7} fill="#1b1b24" />
        {dust.map((d, i) => <circle key={i} cx={d.x} cy={d.y} r={d.r} fill="#d7ccc8" opacity={Math.max(d.o, 0)} />)}
        <text x={640} y={470} fontSize={64} fontWeight={900} fill="#9ad0ff" opacity={wave(1)}>vroooom</text>
      </g>
    </svg>
  );
};

export const InsertCard = ({ ins }: { ins: Insert }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: `linear-gradient(135deg, ${theme.bg}, #1d1030)`, fontFamily: theme.font, color: theme.fg }}>
      {ins.animation === "hoover" && <Hoover f={f} />}
      <div style={{ position: "absolute", left: 0, right: 0, top: 70, textAlign: "center", fontSize: 150, fontWeight: 900, color: theme.accent }}>{ins.title}</div>
      <div style={{ position: "absolute", left: 160, right: 160, top: 250, textAlign: "center", fontSize: 50, fontWeight: 700, lineHeight: 1.3 }}>{ins.text}</div>
    </AbsoluteFill>
  );
};
