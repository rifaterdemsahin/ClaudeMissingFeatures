#!/usr/bin/env python3
"""README.md as a navigation hub: live link, where to start, the master spec at a glance (contents + the prompt to execute), commands, what is where,
versions and score. Generated from project.json, MASTER_SPEC.md, assets/exports.json, assets/okr_result.json. Run: python3 -I scripts/build_readme.py"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
J = lambda p, d=None: json.load(open(ROOT / p)) if (ROOT / p).exists() else d
P, reg, okr = J("remotion/src/project.json", {}), J("assets/exports.json", []), J("assets/okr_result.json")
spec = (ROOT / "MASTER_SPEC.md").read_text() if (ROOT / "MASTER_SPEC.md").exists() else ""
repo = P.get("repo") or "<user>/<repo>"; user, name = (repo.split("/") + ["<repo>"])[:2]
site = f"https://{user}.github.io/{name}"
slug = lambda t: re.sub(r"[^\w\- ]", "", t.strip().lower(), flags=re.UNICODE).replace(" ", "-")
prompt = re.search(r"## ▶ Prompt to execute.*?```text\n(.*?)```", spec, flags=re.S)
heads = [m.group(1).strip() for m in re.finditer(r"^## (.+)$", spec, flags=re.M) if not m.group(1).startswith("📑")]
pages = [("🧭 Start", [("architecture", "🏛️ Architecture", "who does what: MacBook, Claude, cloud; token rules"), ("environment", "🧰 Environment", "installs, files, code, machine times"), ("timeline", "⏱️ Time & order", "how long each stage takes, who does it, in what order, how to prepare"), ("pipeline", "🗺️ Pipeline", "the whole flow drawn on a tldraw canvas"), ("evals", "🧪 Evals", "can the spec recreate this project?"), ("spec", "📘 Master spec", "the recipe and the prompt to execute")]),
         ("🎬 Make", [("index", "🏠 Project", "hub"), ("preprod", "📝 Pre-prod", "OKRs, value recognition, score"), ("prod", "🎬 Prod", "production steps"), ("postprod", "✅ Post-prod", "subtitles, thumbnail, publish"), ("run", "🧪 Run & links", "commands, Studio, troubleshooting")]),
         ("🔎 Review", [("player", "▶️ Player", "original vs export versions, notes, keys"), ("artifacts", "🧩 Artifacts", "every added element, clickable, with notes"), ("script", "📜 Script", "the spoken script and subtitle issues and fixes"), ("edl", "✂️ EDL", "edit decision list and decision log"), ("changelog", "🗒️ Changelog", "everything that happened"), ("metadata", "📺 YouTube metadata", "title, description, chapters"), ("analytics", "📈 Analytics", "post-publish tracking (Day 2, 14, 28) and OKR reconciliation")])]
L = [f"> 🌐 **Live site (GitHub Pages):** {site}/ · [Architecture]({site}/architecture.html) · [Player]({site}/player.html) · [Master spec]({site}/spec.html) · [Changelog]({site}/changelog.html)", "",
     f"# 🎬 {P.get('title', 'Video project')}", "",
     "A repeatable way to turn **screen recordings + your own voice** into a finished 1080p YouTube long-form video: the MacBook does the heavy work with local tools, Claude only makes judgement calls from a one-page report, and everything is reusable for the next video.", "",
     "## 🧭 Start here", "", "| Where | Page | What it is |", "|---|---|---|"]
for grp, items in pages:
    for f, t, d in items: L.append(f"| {grp} | [{t}]({site}/{f}.html) | {d} |")
L += ["", "## 🗺️ Master spec at a glance", "", f"[`MASTER_SPEC.md`](MASTER_SPEC.md) · [on the site]({site}/spec.html). **Standing rule: ♻️ reuse first**: per-video facts live only in data (`remotion/src/project.json`, `overlays.json`, `cuts.json`, `assets/*.json`); code, templates and the kit stay generic.", "", "**Contents**", ""]
L += [f"{i}. [{h}](MASTER_SPEC.md#{slug(h)})" for i, h in enumerate(heads, 1)]
if prompt: L += ["", "### ▶ Prompt to execute (paste into Claude Code, fill the `<…>`)", "", "```text", prompt.group(1).rstrip(), "```"]
L += ["", "## ⚡ Commands", "", "| Do | Command |", "|---|---|", "| Check the machine | `scripts/check_env.sh` |", "| Pull the kit (new video) | `scripts/pull_kit.sh <folder>` then `./new-video.sh \"<Title>\" <seconds> [slug] [community] [url] [platform]` |",
      "| Prepare everything locally | `scripts/pipeline.sh \"~/Downloads/<folder>\" <slug>` then read `REPORT.md` |", "| Save source to Azure | `python3 scripts/upload_source.py` |", "| Blur boxes from OCR | `python3 -I scripts/build_blurs.py` |", "| Preview / edit | `cd remotion && npm run studio` → http://localhost:3000/LongForm |",
      "| Numbered export | `scripts/render_export.sh \"what changed\"` |", "| Privacy check of the export | `python3 -I scripts/verify_export.py` |", "| Measure and score | `python3 scripts/measure_video.py && python3 -I scripts/build_okr.py` |",
      "| Build the whole site + check | `scripts/build_all.sh` |", "| Run evals (can spec recreate?) | `python3 scripts/eval_spec.py` |", "| Serve the site and player | `scripts/serve.sh` → http://localhost:8000/player.html |", "| Reuse check | `scripts/check_reuse.sh` |", "| Back up to Drive | `scripts/backup_drive.sh` (or the Drive tool) |",
      "", "## 📁 What is where", "", "| Path | What |", "|---|---|", "| `MASTER_SPEC.md`, `ENVIRONMENT.md`, `EDL.md`, `CHANGELOG.md` | the documents (the site pages are built from them) |", "| `remotion/` | the video project (`src/overlays.json`, `cuts.json`, `project.json` are the edit and the config) |",
      "| `scripts/` | every tool: pipeline, OCR, blur, captions, export, measure, build site, checks |", "| `assets/` | data: transcript, OKRs, decisions, chapters, exports registry, metrics (OCR output is private and ignored) |", "| `kit/`, `kit-dist/` | what is packed into the Drive kit (the zip is not committed) |",
      "| `exports/` | numbered exports (not committed) |", "| `*.html`, `nav.js`, `project.js` | the website |", "| `docs/SHORTS_FLOW.md` | the older Shorts recipe (kept for reference) |"]
if reg:
    L += ["", "## 🎞️ Exports and results", "", "| Version | Length | What changed |", "|---|---|---|"] + [f"| **v{e['v']}** | {e.get('seconds', '')} s | {e.get('notes', '')} |" for e in reversed(reg)]
if okr: L += ["", f"🎯 Value-recognition score **{okr['score']} / 100** ({okr['grade']}); key results ✅ {okr['kr']['met']} met · 🟡 {okr['kr']['almost']} almost · ❌ {okr['kr']['missed']} missed · ⏳ {okr['kr']['open']} open."]
L += ["", "## 📚 More", "", f"- [🗒️ Changelog]({site}/changelog.html) · [✂️ EDL]({site}/edl.html) · [🧰 Environment]({site}/environment.html)", "- [Older Shorts recipe](docs/SHORTS_FLOW.md)", "", "*This file is generated by `scripts/build_readme.py`; edit the data and the spec, not this file.*"]
(ROOT / "README.md").write_text("\n".join(L) + "\n"); print(f"README.md: {len(heads)} spec sections, prompt {'included' if prompt else 'missing'}")
