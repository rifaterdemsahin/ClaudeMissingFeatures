> 🌐 **Live site (GitHub Pages):** https://rifaterdemsahin.github.io/ClaudeMissingFeatures/ · [Architecture](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/architecture.html) · [Player](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/player.html) · [Master spec](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/spec.html) · [Changelog](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/changelog.html)

# 🎬 Claude Missing Features

A repeatable way to turn **screen recordings + your own voice** into a finished 1080p YouTube long-form video: the MacBook does the heavy work with local tools, Claude only makes judgement calls from a one-page report, and everything is reusable for the next video.

## 🧭 Start here

| Where | Page | What it is |
|---|---|---|
| 🧭 Start | [🏛️ Architecture](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/architecture.html) | who does what: MacBook, Claude, cloud; token rules |
| 🧭 Start | [🧰 Environment](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/environment.html) | installs, files, code, machine times |
| 🧭 Start | [⏱️ Time & order](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/timeline.html) | how long each stage takes, who does it, in what order, how to prepare |
| 🧭 Start | [📘 Master spec](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/spec.html) | the recipe and the prompt to execute |
| 🎬 Make | [🏠 Project](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/index.html) | hub |
| 🎬 Make | [📝 Pre-prod](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/preprod.html) | OKRs, value recognition, score |
| 🎬 Make | [🎬 Prod](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/prod.html) | production steps |
| 🎬 Make | [✅ Post-prod](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/postprod.html) | subtitles, thumbnail, publish |
| 🎬 Make | [🧪 Run & links](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/run.html) | commands, Studio, troubleshooting |
| 🔎 Review | [▶️ Player](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/player.html) | original vs export versions, notes, keys |
| 🔎 Review | [🧩 Artifacts](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/artifacts.html) | every added element, clickable, with notes |
| 🔎 Review | [📜 Script](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/script.html) | the spoken script and subtitle issues and fixes |
| 🔎 Review | [✂️ EDL](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/edl.html) | edit decision list and decision log |
| 🔎 Review | [🗒️ Changelog](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/changelog.html) | everything that happened |
| 🔎 Review | [📺 YouTube metadata](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/metadata.html) | title, description, chapters |

## 🗺️ Master spec at a glance

[`MASTER_SPEC.md`](MASTER_SPEC.md) · [on the site](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/spec.html). **Standing rule: ♻️ reuse first**: per-video facts live only in data (`remotion/src/project.json`, `overlays.json`, `cuts.json`, `assets/*.json`); code, templates and the kit stay generic.

**Contents**

1. [♻️ Reuse first (standing rule, read before changing anything)](MASTER_SPEC.md#-reuse-first-standing-rule-read-before-changing-anything)
2. [⚙️ `project.json` (the one config per video)](MASTER_SPEC.md#-projectjson-the-one-config-per-video)
3. [▶ Prompt to execute (paste into Claude Code, fill the `<…>`)](MASTER_SPEC.md#-prompt-to-execute-paste-into-claude-code-fill-the-)
4. [Get what is needed (so a video starts in minutes)](MASTER_SPEC.md#get-what-is-needed-so-a-video-starts-in-minutes)
5. [0. Brief (fill in per video)](MASTER_SPEC.md#0-brief-fill-in-per-video)
6. [0. Architecture and token budget (read first)](MASTER_SPEC.md#0-architecture-and-token-budget-read-first)
7. [0b. Environment (check it before you start)](MASTER_SPEC.md#0b-environment-check-it-before-you-start)
8. [0a. Fast start: the kit on Google Drive](MASTER_SPEC.md#0a-fast-start-the-kit-on-google-drive)
9. [1. Pipeline](MASTER_SPEC.md#1-pipeline)
10. [2. Repo layout](MASTER_SPEC.md#2-repo-layout)
11. [3. Sync clips to the voice recording](MASTER_SPEC.md#3-sync-clips-to-the-voice-recording)
12. [4. Render the base video (ffmpeg)](MASTER_SPEC.md#4-render-the-base-video-ffmpeg)
13. [5. Transcript, chapters, title and description](MASTER_SPEC.md#5-transcript-chapters-title-and-description)
14. [6. Remotion (long form)](MASTER_SPEC.md#6-remotion-long-form)
15. [6a. Cuts (repetitive parts)](MASTER_SPEC.md#6a-cuts-repetitive-parts)
16. [6b. Animated subtitles](MASTER_SPEC.md#6b-animated-subtitles)
17. [6c. Recorder UI and image overlays](MASTER_SPEC.md#6c-recorder-ui-and-image-overlays)
18. [6d. Run it (links and commands)](MASTER_SPEC.md#6d-run-it-links-and-commands)
19. [6e. Speed-ups, slides, blur boxes (editing personal or slow parts)](MASTER_SPEC.md#6e-speed-ups-slides-blur-boxes-editing-personal-or-slow-parts)
20. [6f. Export render and the player's version switch](MASTER_SPEC.md#6f-export-render-and-the-players-version-switch)
21. [6g. EDL: the edit decision list (record every decision)](MASTER_SPEC.md#6g-edl-the-edit-decision-list-record-every-decision)
22. [6h. Audio: remove steady noise (hoover, fan)](MASTER_SPEC.md#6h-audio-remove-steady-noise-hoover-fan)
23. [6i. Ending: summary and community call to action](MASTER_SPEC.md#6i-ending-summary-and-community-call-to-action)
24. [6j. OKRs and value recognition (in the Pre-prod page)](MASTER_SPEC.md#6j-okrs-and-value-recognition-in-the-pre-prod-page)
25. [6k. Artifacts page (every added element, clickable)](MASTER_SPEC.md#6k-artifacts-page-every-added-element-clickable)
26. [6l. Export versions (every export is numbered)](MASTER_SPEC.md#6l-export-versions-every-export-is-numbered)
27. [6m. Cuts with an apology card, lower thirds, manual blurs](MASTER_SPEC.md#6m-cuts-with-an-apology-card-lower-thirds-manual-blurs)
28. [6n. Script page and subtitle quality (find it, fix it, record it)](MASTER_SPEC.md#6n-script-page-and-subtitle-quality-find-it-fix-it-record-it)
29. [6o. Changelog page (everything that happened, with emojis)](MASTER_SPEC.md#6o-changelog-page-everything-that-happened-with-emojis)
30. [6p. Notes on the Artifacts page](MASTER_SPEC.md#6p-notes-on-the-artifacts-page)
31. [6q. README and the contents table (navigation)](MASTER_SPEC.md#6q-readme-and-the-contents-table-navigation)
32. [6r. Platforms: separate renders, the Publish page, Azure storage](MASTER_SPEC.md#6r-platforms-separate-renders-the-publish-page-azure-storage)
33. [6s. Completion time: stages, order, who, and how to prepare](MASTER_SPEC.md#6s-completion-time-stages-order-who-and-how-to-prepare)
34. [7. Website (GitHub Pages)](MASTER_SPEC.md#7-website-github-pages)
35. [7a. Publish: GitHub Pages (do this for every project, do not forget)](MASTER_SPEC.md#7a-publish-github-pages-do-this-for-every-project-do-not-forget)
36. [7b. Always back up to Google Drive](MASTER_SPEC.md#7b-always-back-up-to-google-drive)
37. [7c. Build the whole website (every page, from the kit)](MASTER_SPEC.md#7c-build-the-whole-website-every-page-from-the-kit)
38. [8. Sanity check (before publishing)](MASTER_SPEC.md#8-sanity-check-before-publishing)
39. [9. Delivery checklist](MASTER_SPEC.md#9-delivery-checklist)
40. [10. Lessons learned (this project)](MASTER_SPEC.md#10-lessons-learned-this-project)
41. [11. Start prompt for a new Claude session (short form; the full prompt is at the top of this file)](MASTER_SPEC.md#11-start-prompt-for-a-new-claude-session-short-form-the-full-prompt-is-at-the-top-of-this-file)

### ▶ Prompt to execute (paste into Claude Code, fill the `<…>`)

```text
Use the Master Spec (MASTER_SPEC.md in this repo; if this is a new project run scripts/pull_kit.sh <folder> then ./new-video.sh "<Title>" <seconds> first).
Goal: turn my screen recordings + voice WAV into a finished 1080p YouTube long-form video, as fast as possible and with as few tokens as possible.

Inputs: clips + WAV in ~/Downloads/<Project>/ ; title <…> ; slug <…> ; CTA community <name> at <URL> ; my images in ~/Downloads (<file> = <what it shows, where it should appear, arrow at what>) ; my notes (paste the [orig m:ss] / [vN m:ss] lines here; the version tag says which export they are about).

Do this in order and do not stop to ask unless you are blocked:
1. scripts/check_env.sh, then install anything missing. Fill remotion/src/project.json (title, community, sensitive words, caption fixes) and assets/okr.json (objectives, key results, value proposition) BEFORE producing.
2. scripts/pipeline.sh "~/Downloads/<Project>" <slug>, then read REPORT.md only. Do not view frames to find things; use OCR, numbers and one still to confirm a look.
3. Edit remotion/src/overlays.json and cuts.json: slides over personal windows, speed-up for slow typing, my images with caption and arrow, a summary slide and a CTA card at the end, no transitions. Run scripts/build_blurs.py. If the audio scan shows steady noise (hoover, fan) remove it with scripts/denoise_audio.py instead of cutting minutes of content.
4. Apply my notes: convert export time to source time, decide, log every decision in assets/edl_decisions.json.
5. One render round: scripts/render_export.sh "what changed" youtube linkedin x (numbers it v1, v2, … and never overwrites; each platform has its own length, section 6r), then scripts/verify_export.py on every file, then scripts/upload_exports.py (private Azure container, read-only links, keys in Key Vault) and review everything on the Publish page (OCR privacy check) and fix leaks by padding boxes or slides, then re-render once if needed.
6. python3 -I scripts/build_subs.py ..., check_subtitles.py (fix what the evidence supports, list the rest for my ear), then scripts/measure_video.py, build_okr.py (score the value recognition honestly), and scripts/build_all.sh (script, artifacts, changelog, README, contents, all pages); add every notable change to assets/changelog.json; write title, description, chapters, tags and pinned comment in metadata.md.
7. Run scripts/check_reuse.sh and test the kit from scratch (Reuse first section). Commit, push, merge to main, enable GitHub Pages, put the live link on top of README.md, back up to Google Drive (section 7b), and update the kit on Drive.
8. Open the site, the player and Remotion Studio in Google Chrome (open -a "Google Chrome" <url>).

Rules: media files, OCR output and REPORT.md never go to git; cover personal content with slides and blur titles; hard cuts; report each check with numbers; show clickable URLs; use emojis; if the permission system blocks a push, merge or upload, stop and tell me the exact command to run with the ! prefix.
```

## ⚡ Commands

| Do | Command |
|---|---|
| Check the machine | `scripts/check_env.sh` |
| Pull the kit (new video) | `scripts/pull_kit.sh <folder>` then `./new-video.sh "<Title>" <seconds> [slug] [community] [url] [platform]` |
| Prepare everything locally | `scripts/pipeline.sh "~/Downloads/<folder>" <slug>` then read `REPORT.md` |
| Blur boxes from OCR | `python3 -I scripts/build_blurs.py` |
| Preview / edit | `cd remotion && npm run studio` → http://localhost:3000/LongForm |
| Numbered export | `scripts/render_export.sh "what changed"` |
| Privacy check of the export | `python3 -I scripts/verify_export.py` |
| Measure and score | `python3 scripts/measure_video.py && python3 -I scripts/build_okr.py` |
| Build the whole site + check | `scripts/build_all.sh` |
| Serve the site and player | `scripts/serve.sh` → http://localhost:8000/player.html |
| Reuse check | `scripts/check_reuse.sh` |
| Back up to Drive | `scripts/backup_drive.sh` (or the Drive tool) |

## 📁 What is where

| Path | What |
|---|---|
| `MASTER_SPEC.md`, `ENVIRONMENT.md`, `EDL.md`, `CHANGELOG.md` | the documents (the site pages are built from them) |
| `remotion/` | the video project (`src/overlays.json`, `cuts.json`, `project.json` are the edit and the config) |
| `scripts/` | every tool: pipeline, OCR, blur, captions, export, measure, build site, checks |
| `assets/` | data: transcript, OKRs, decisions, chapters, exports registry, metrics (OCR output is private and ignored) |
| `kit/`, `kit-dist/` | what is packed into the Drive kit (the zip is not committed) |
| `exports/` | numbered exports (not committed) |
| `*.html`, `nav.js`, `project.js` | the website |
| `docs/SHORTS_FLOW.md` | the older Shorts recipe (kept for reference) |

## 🎞️ Exports and results

| Version | Length | What changed |
|---|---|---|
| **v5** | 114.0 s | Platform cuts of v5: LinkedIn highlights (3:19) and X highlights (1:54) with shorter endings |
| **v5** | 198.8 s | Platform cuts of v5: LinkedIn highlights (3:19) and X highlights (1:54) with shorter endings |
| **v5** | 719.3 s | Subtitle quality: Claude's answer corrected from the on-screen text, 'code connectors' fixed, stutters dropped from captions, flicker removed (min 0.9 s / merged); everything else as v4 (round-4 notes) |
| **v4** | 719.3 s | Round 4 notes: WhatsApp banner blurred; Grok Bot window shown (agent list blurred) for the update; lower third at 8:44; captions fixed (Claude not clothe); hoover part cut (50.8 s) with an animated apology card; Whiteboard expected-output picture again at the end |
| **v3** | 764.1 s | Whiteboard picture card with arrow added (expected feature), caption box clear of the picture |
| **v2** | 764.1 s | Leaks fixed (blur and slide edges padded), no transitions, hoover noise reduced, summary slide and Skool call-to-action added, family-photo moment covered |
| **v1** | 743.1 s | First full export (not kept): OCR check found private text at 6:30, 6:58, 8:36 and 12:22 at box edges; no summary or call-to-action yet |

🎯 Value-recognition score **77.0 / 100** (B (good)); key results ✅ 11 met · 🟡 1 almost · ❌ 0 missed · ⏳ 4 open.

## 📚 More

- [🗒️ Changelog](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/changelog.html) · [✂️ EDL](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/edl.html) · [🧰 Environment](https://rifaterdemsahin.github.io/ClaudeMissingFeatures/environment.html)
- [Older Shorts recipe](docs/SHORTS_FLOW.md)

*This file is generated by `scripts/build_readme.py`; edit the data and the spec, not this file.*
