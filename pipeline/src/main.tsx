import { createRoot } from "react-dom/client";
import { useState, useEffect } from "react";
import { Tldraw, toRichText, createShapeId, Editor } from "tldraw";
import "tldraw/tldraw.css";

type Node = { id: string; kind?: string; x: number; y: number; w?: number; h?: number; color: string; fill?: string; text: string; size?: string };
type Band = { name: string; x: number; y: number; w: number; h: number };
type Edge = { from: string; to: string; label?: string; bend?: number };
type Data = { title: string; bands: Band[]; nodes: Node[]; edges: Edge[] };

function draw(editor: Editor, d: Data) {
  const sid = (id: string) => createShapeId(id);
  editor.createShapes(d.bands.map((b, i) => ({ id: sid("bandbox" + i), type: "geo", x: b.x, y: b.y, props: { geo: "rectangle", w: b.w, h: b.h, color: "grey", fill: "none", dash: "dashed", size: "s" } } as never)));
  const pos: Record<string, Node> = {};
  d.nodes.forEach((n) => (pos[n.id] = n));
  editor.createShapes(
    d.nodes.map((n) =>
      n.kind === "text"
        ? ({ id: sid(n.id), type: "text", x: n.x, y: n.y, props: { richText: toRichText(n.text), color: n.color, size: n.size ?? "l", font: "sans", autoSize: true } } as never)
        : ({ id: sid(n.id), type: "geo", x: n.x, y: n.y, props: { geo: "rectangle", w: n.w, h: n.h, richText: toRichText(n.text), color: n.color, fill: n.fill ?? "semi", size: "s", font: "sans", align: "middle", verticalAlign: "middle", dash: "draw" } } as never)
    )
  );
  d.edges.forEach((e, i) => {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) return;
    const ax = a.x + (a.w ?? 0) / 2, ay = a.y + (a.h ?? 0) / 2, bx = b.x + (b.w ?? 0) / 2, by = b.y + (b.h ?? 0) / 2, id = sid("arrow-" + i);
    editor.createShapes([{ id: id, type: "arrow", x: ax, y: ay, props: { start: { x: 0, y: 0 }, end: { x: bx - ax, y: by - ay }, bend: e.bend ?? 0, arrowheadEnd: "arrow", color: "black", size: "m", richText: toRichText(e.label ?? "") } } as never]);
    editor.createBindings([
      { type: "arrow", fromId: id, toId: sid(e.from), props: { terminal: "start", normalizedAnchor: { x: 0.5, y: 0.5 }, isExact: false, isPrecise: false, snap: "none" } },
      { type: "arrow", fromId: id, toId: sid(e.to), props: { terminal: "end", normalizedAnchor: { x: 0.5, y: 0.5 }, isExact: false, isPrecise: false, snap: "none" } },
    ] as never);
  });
  const W = window as unknown as { __pipelineBands: Band[]; __zoomBand: (i: number) => void };
  W.__pipelineBands = d.bands;
  W.__zoomBand = (i: number) => { const b = d.bands[i]; editor.zoomToBounds({ x: b.x, y: b.y, w: b.w, h: b.h } as never, { animation: { duration: 250 }, inset: 24 } as never); };
  W.__zoomBand(0);
}

function App() {
  const [data, setData] = useState<Data | null>(null);
  useEffect(() => { fetch("pipeline/pipeline.json?x=" + Date.now()).then((r) => r.json()).then(setData).catch(() => setData(null)); }, []);
  if (!data) return <div style={{ padding: 24, color: "#ccc" }}>Loading the pipeline…</div>;
  return (
    <Tldraw
      persistenceKey="video-production-pipeline"
      onMount={(editor) => {
        (window as unknown as { __pipelineEditor: Editor }).__pipelineEditor = editor;
        editor.selectAll(); editor.deleteShapes(editor.getSelectedShapeIds());   // always draw from the data
        draw(editor, data);
        editor.updateInstanceState({ isReadonly: true });
      }}
    />
  );
}
createRoot(document.getElementById("app") as HTMLElement).render(<App />);
