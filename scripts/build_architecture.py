"""Regenerates the SVG in architecture.html (head and tail stay as written). Run: python3 -I scripts/build_architecture.py"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
def box(x,y,w,h,title,sub,fill,stroke):
    t=''.join(f'<tspan x="{x+w/2}" dy="15">{l}</tspan>' for l in sub)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/><text x="{x+w/2}" y="{y+22}" text-anchor="middle" font-weight="700" font-size="13" fill="#fff">{title}</text><text x="{x+w/2}" y="{y+24}" text-anchor="middle" font-size="11" fill="#cfcfe0">{t}</text>'
def arrow(x1,y1,x2,y2,c="#ff7a3d"): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2" marker-end="url(#ah)"/>'
def label(x,y,t,anchor="middle"): return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="10.5" fill="#ffb38f">{t}</text>'
svg=['<svg viewBox="0 0 1000 580" role="img" aria-label="Architecture: local MacBook pipeline, Claude judgement lane, cloud lane" style="width:100%;height:auto;background:#101018;border-radius:12px">',
'<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#ff7a3d"/></marker></defs>',
'<text x="20" y="28" font-size="14" font-weight="800" fill="#ff7a3d">🖥️ MacBook Pro: local libraries (0 tokens)</text><rect x="10" y="38" width="980" height="196" rx="14" fill="none" stroke="#2a2a38" stroke-dasharray="5 5"/>']
A=[("Inputs",["screen clips .mp4","voice .WAV"],"#1f2a3a"),("ffmpeg + scipy",["sync clips to voice","1080p30 base video"],"#1d2b24"),("Whisper",["transcript with","word timings"],"#1d2b24"),("Apple Vision OCR",["every 2 s: text","+ screen positions"],"#1d2b24"),("Python scripts",["subs, blur boxes,","repeats, REPORT.md"],"#1d2b24"),("Remotion + Chrome",["slides, blur, 3x,","captions → export"],"#2b2230"),("OCR verify",["privacy check of","the final export"],"#1d2b24")]
xs=[]
for i,(t,sub,f) in enumerate(A):
    x=22+i*138; xs.append(x); svg.append(box(x,66,118,92,t,sub,f,"#3a3a52"))
    if i: svg.append(arrow(x-20,112,x-1,112))
svg.append('<text x="22" y="184" font-size="11" fill="#9a9ab0">Scripts: pipeline.sh, build_base.py, ocr_all.sh, build_subs.py, build_blurs.py, verify_export.py. Re-runs skip finished stages.</text>')
svg.append('<text x="22" y="206" font-size="11" fill="#9a9ab0">Never committed: long.mp4, export.mp4. Only text (REPORT.md, overlays.json) goes to Claude.</text>')
py=xs[4]+59; rm=xs[5]+59                      # centres of Python and Remotion boxes
svg.append('<text x="20" y="282" font-size="14" font-weight="800" fill="#ff7a3d">🤖 Claude: judgement only (a few thousand tokens)</text><rect x="10" y="292" width="980" height="108" rx="14" fill="none" stroke="#2a2a38" stroke-dasharray="5 5"/>')
svg.append(box(300,312,170,70,"Your player notes",["timestamped feedback","[orig/export m:ss]"],"#2b2230","#5a3a52"))
svg.append(box(py-70,312,140,70,"Reads REPORT.md",["one text page,","not images"],"#2b2230","#5a3a52"))
svg.append(box(rm+8,312,150,70,"Decides + edits",["slides, speedups,","cuts, overlays.json"],"#2b2230","#5a3a52"))
svg.append(arrow(470,347,py-71,347)); svg.append(arrow(py+71,347,rm+7,347))
svg.append(arrow(py,158,py,311)); svg.append(label(py+8,236,"REPORT.md","start"))
svg.append(arrow(rm+60,311,rm+60,159)); svg.append(label(rm+68,236,"overlays.json","start"))
svg.append('<text x="20" y="432" font-size="14" font-weight="800" fill="#ff7a3d">☁️ Cloud (reuse, not compute)</text><rect x="10" y="442" width="980" height="116" rx="14" fill="none" stroke="#2a2a38" stroke-dasharray="5 5"/>')
for i,(t,sub) in enumerate([("Google Drive kit",["kit zip + MASTER_SPEC","scripts/pull_kit.sh pulls it"]),("Azure Key Vault",["Drive folder id + link","(never in the repo)"]),("GitHub + Pages",["code, docs, this site","(no media files)"])]):
    svg.append(box(22+i*320,468,290,70,t,sub,"#1f2a3a","#3a4a62"))
svg.append('</svg>')
page=(ROOT/"architecture.html").read_text(); a=page.index("<svg"); b=page.index("</svg>")+6
page=page[:a]+"".join(svg)+page[b:]
(ROOT/"architecture.html").write_text(page)
(ROOT/"kit/templates/architecture.html").write_text(page.replace("Claude Missing Features: architecture","{{TITLE}}: architecture"))
print("architecture.html regenerated")
