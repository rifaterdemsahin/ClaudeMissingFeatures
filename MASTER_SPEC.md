# MASTER SPEC v3.18: long-form 1080p screen-recording video (YouTube)

<!--TOC-->
## 📑 Contents

1. [♻️ Reuse first (standing rule, read before changing anything)](#-reuse-first-standing-rule-read-before-changing-anything)
2. [⚙️ `project.json` (the one config per video)](#-projectjson-the-one-config-per-video)
3. [▶ Prompt to execute (paste into Claude Code, fill the `<…>`)](#-prompt-to-execute-paste-into-claude-code-fill-the-)
4. [Get what is needed (so a video starts in minutes)](#get-what-is-needed-so-a-video-starts-in-minutes)
5. [0. Brief (fill in per video)](#0-brief-fill-in-per-video)
6. [0. Architecture and token budget (read first)](#0-architecture-and-token-budget-read-first)
7. [0b. Environment (check it before you start)](#0b-environment-check-it-before-you-start)
8. [0a. Fast start: the kit on Google Drive](#0a-fast-start-the-kit-on-google-drive)
9. [0c. Save raw footage and source artifacts to Azure Storage (per-video container)](#0c-save-raw-footage-and-source-artifacts-to-azure-storage-per-video-container)
10. [1. Pipeline](#1-pipeline)
11. [2. Repo layout](#2-repo-layout)
12. [3. Sync clips to the voice recording](#3-sync-clips-to-the-voice-recording)
13. [4. Render the base video (ffmpeg)](#4-render-the-base-video-ffmpeg)
14. [5. Transcript, chapters, title and description](#5-transcript-chapters-title-and-description)
15. [6. Remotion (long form)](#6-remotion-long-form)
16. [6a. Cuts (repetitive parts)](#6a-cuts-repetitive-parts)
17. [6b. Animated subtitles](#6b-animated-subtitles)
18. [6c. Recorder UI and image overlays](#6c-recorder-ui-and-image-overlays)
19. [6d. Run it (links and commands)](#6d-run-it-links-and-commands)
20. [6e. Speed-ups, slides, blur boxes (editing personal or slow parts)](#6e-speed-ups-slides-blur-boxes-editing-personal-or-slow-parts)
21. [6f. Export render and the player's version switch](#6f-export-render-and-the-players-version-switch)
22. [6g. EDL: the edit decision list (record every decision)](#6g-edl-the-edit-decision-list-record-every-decision)
23. [6h. Audio: remove steady noise (hoover, fan)](#6h-audio-remove-steady-noise-hoover-fan)
24. [6i. Ending: summary and community call to action](#6i-ending-summary-and-community-call-to-action)
25. [6j. OKRs and value recognition (in the Pre-prod page)](#6j-okrs-and-value-recognition-in-the-pre-prod-page)
26. [6k. Artifacts page (every added element, clickable)](#6k-artifacts-page-every-added-element-clickable)
27. [6l. Export versions (every export is numbered)](#6l-export-versions-every-export-is-numbered)
28. [6m. Cuts with an apology card, lower thirds, manual blurs](#6m-cuts-with-an-apology-card-lower-thirds-manual-blurs)
29. [6n. Script page and subtitle quality (find it, fix it, record it)](#6n-script-page-and-subtitle-quality-find-it-fix-it-record-it)
30. [6o. Changelog page (everything that happened, with emojis)](#6o-changelog-page-everything-that-happened-with-emojis)
31. [6p. Notes on the Artifacts page](#6p-notes-on-the-artifacts-page)
32. [6q. README and the contents table (navigation)](#6q-readme-and-the-contents-table-navigation)
33. [6r. Platforms: separate renders, the Publish page, Azure storage](#6r-platforms-separate-renders-the-publish-page-azure-storage)
34. [6s. Completion time: stages, order, who, and how to prepare](#6s-completion-time-stages-order-who-and-how-to-prepare)
35. [6t. The pipeline drawn with tldraw](#6t-the-pipeline-drawn-with-tldraw)
36. [6u. Evals: can the spec recreate this project?](#6u-evals-can-the-spec-recreate-this-project)
37. [6v. Post-publish performance analytics and value reconciliation](#6v-post-publish-performance-analytics-and-value-reconciliation)
38. [6w. AI-assisted curiosity thumbnail generation (fal.ai / FLUX / subagents)](#6w-ai-assisted-curiosity-thumbnail-generation-falai--flux--subagents)
39. [7. Website (GitHub Pages)](#7-website-github-pages)
40. [7a. Publish: GitHub Pages (do this for every project, do not forget)](#7a-publish-github-pages-do-this-for-every-project-do-not-forget)
41. [7b. Always back up to Google Drive](#7b-always-back-up-to-google-drive)
42. [7c. Build the whole website (every page, from the kit)](#7c-build-the-whole-website-every-page-from-the-kit)
43. [8. Sanity check (before publishing)](#8-sanity-check-before-publishing)
44. [9. Delivery checklist](#9-delivery-checklist)
45. [10. Lessons learned (this project)](#10-lessons-learned-this-project)
46. [11. Start prompt for a new Claude session (short form; the full prompt is at the top of this file)](#11-start-prompt-for-a-new-claude-session-short-form-the-full-prompt-is-at-the-top-of-this-file)
<!--/TOC-->









## ♻️ Reuse first (standing rule, read before changing anything)

**The owner must always be able to reuse this structure for the next video.** Every change, feature or fix is judged by that. Rules:

1. **Project facts live in data, never in code.** Everything that belongs to one video lives only in: `remotion/src/project.json` (title, brand, thumbnail text, community name/platform/URL, sensitive words, personal-app patterns, caption fixes), `remotion/src/overlays.json` and `cuts.json` (the edit), `assets/*.json` (OKRs, decisions, chapters, audio fixes, metrics), `metadata.md`. Scripts, Remotion components, `nav.js`, `player.html` and templates contain no names, URLs or keywords of one video.
2. **Before adding a feature:** make it generic and parameterised; put it in the kit (`scripts/build_kit.sh`) with a blank template if it needs data; document it in this spec; add a step to the prompt below if it is part of the flow.
3. **After every change run the three checks:** `scripts/check_reuse.sh` (fails if reusable code contains this video's words, read from `project.json`); the kit from scratch in a temp folder (`unzip` the kit, `./new-video.sh "T" 60 "<community>" <url> <platform>`, `npx tsc --noEmit`, `python3 -m py_compile scripts/*.py`); and regenerate this project's outputs and `cmp` them against the previous ones (a refactor must change nothing visible).
4. **Ship the structure:** rebuild the kit and back it up to Drive (section 7b) so the next video pulls the newest version with `scripts/pull_kit.sh`.
5. **The kit carries blanks, not this video:** empty `[]` data files, `okr.template.json`, a blank `project.json`; no media, no OCR, no this-video text. Never commit media or OCR output.
6. **Log reusable lessons here**, not in chat; the spec is the memory.
7. **Trunk-based development (always merge to `main`):** Follow trunk-based development. All active code converges continuously into `main` (the trunk). Never leave work unmerged on stale or long-running branches. If short-lived topic branches are used, merge them immediately back to `main` upon verification ("remember to merge always") and keep `main` green, tested, and pushed.

## ⚙️ `project.json` (the one config per video)

`remotion/src/project.json`, created by `./new-video.sh "<Title>" <seconds> [slug] [community] [url] [platform]` and edited by hand.

| Field | Used by |
|---|---|
| `title`, `brand` | page titles and the menu brand (`nav.js`), slide and ending headers (`Slide.tsx`, `Outro.tsx`), site build |
| `thumb.line1`, `thumb.line2` | the title card (`Thumb.tsx`), EDL text |
| `community.{name,platform,url,display}` | menu link, notes footer, last chapter, EDL, KRs (`measure_video.py` checks the URL is in the description) |
| `sensitive_keywords` | blur boxes (`build_blurs.py`) and the export privacy check (`verify_export.py`) |
| `personal_app_patterns`, `verify_app_patterns` | finding windows to cover with slides (`find_personal_windows.py`) and the privacy check |
| `caption_fixes` | `[regex, replacement]` pairs applied to the transcript (product names heard wrongly) |
| `reuse_allow` | words that are also general vocabulary used by reusable code (e.g. a platform name); `check_reuse.sh` skips them |
| `links` | extra menu links (Azure portal pages) |

`project.js` (generated by `build_site.py`) hands the same values to every page.

---


## ▶ Prompt to execute (paste into Claude Code, fill the `<…>`)

```text
Use the Master Spec (MASTER_SPEC.md in this repo; if this is a new project run scripts/pull_kit.sh <folder> then ./new-video.sh "<Title>" <seconds> first).
Goal: turn my screen recordings + voice WAV into a finished 1080p YouTube long-form video, as fast as possible and with as few tokens as possible.

Inputs: clips + WAV in ~/Downloads/<Project>/ ; title <…> ; slug <…> ; CTA community <name> at <URL> ; my images in ~/Downloads (<file> = <what it shows, where it should appear, arrow at what>) ; my notes (paste the [orig m:ss] / [vN m:ss] lines here; the version tag says which export they are about).

Do this in order and do not stop to ask unless you are blocked:
1. scripts/check_env.sh, then install anything missing. Fill remotion/src/project.json (title, community, sensitive words, caption fixes) and assets/okr.json (objectives, key results, value proposition) BEFORE producing.
2. At the start of the project, save raw footage and source artifacts to Azure Storage in a dedicated per-video container (<slug>-source): python3 scripts/upload_source.py. Run scripts/pipeline.sh "~/Downloads/<Project>" <slug>, then read REPORT.md only. Do not view frames to find things; use OCR, numbers and one still to confirm a look.
3. Edit remotion/src/overlays.json and cuts.json: slides over personal windows, speed-up for slow typing, my images with caption and arrow, a summary slide and a CTA card at the end, no transitions. Run scripts/build_blurs.py. If the audio scan shows steady noise (hoover, fan) remove it with scripts/denoise_audio.py instead of cutting minutes of content.
4. Apply my notes: convert export time to source time, decide, log every decision in assets/edl_decisions.json.
5. One render round: scripts/render_export.sh "what changed" youtube linkedin x (numbers it v1, v2, … and never overwrites; each platform has its own length, section 6r), then scripts/verify_export.py on every file, then scripts/upload_exports.py (private Azure container, read-only links, keys in Key Vault) and review everything on the Publish page (OCR privacy check) and fix leaks by padding boxes or slides, then re-render once if needed.
6. python3 -I scripts/build_subs.py ..., check_subtitles.py (fix what the evidence supports, list the rest for my ear), then scripts/measure_video.py, build_okr.py (score the value recognition honestly), and scripts/build_all.sh (script, artifacts, changelog, README, contents, all pages); add every notable change to assets/changelog.json; write title, description, chapters, tags and pinned comment in metadata.md.
7. Run scripts/check_reuse.sh and test the kit from scratch (Reuse first section). Commit, push, merge to main, enable GitHub Pages, put the live link on top of README.md, back up to Google Drive (section 7b), and update the kit on Drive.
8. Open the site, the player and Remotion Studio in Google Chrome (open -a "Google Chrome" <url>).

Rules: media files, OCR output and REPORT.md never go to git; cover personal content with slides and blur titles; hard cuts; report each check with numbers; show clickable URLs; use emojis; if the permission system blocks a push, merge or upload, stop and tell me the exact command to run with the ! prefix.
```

## Get what is needed (so a video starts in minutes)

| You provide | Where it comes from | Notes |
|---|---|---|
| Clips (`*.mp4`) + one voice `*.WAV` | `~/Downloads/<Project>/` | the only large inputs |
| Title, slug, CTA name and URL | the prompt above | CTA is shown in the last card and in the description |
| Your own images (feature screenshots, logos) | `~/Downloads/<file>` | copied to `remotion/public/img/` (local, not committed); placed with `overlays.json` `images` (caption, highlight box, arrow) |
| Your notes from the player | pasted into the prompt | tagged `[orig m:ss]` / `[export m:ss]` |

| The kit supplies | How to get it |
|---|---|
| scripts, Remotion project, templates, this spec | `scripts/pull_kit.sh <folder>` (Drive + Key Vault), then `./new-video.sh` |
| a checked machine | `scripts/check_env.sh` (prints the install command for anything missing) |
| the analysis | `scripts/pipeline.sh` (sync, base, Whisper, OCR, report) |

Generated for you: base video, subtitles, blur boxes, personal-window list, cut candidates, chapters, EDL, site pages. Never needed: API keys, paid services.

---


Generic recipe for turning **screen recordings + your own voice recording** into a finished 16:9 YouTube long-form video: sync, render, Remotion overlays, title, description, chapters, site. Proven on "Claude Missing Features" (12:30, 1920x1080). It replaces the Shorts-only flow in `README.md` for long form; the Shorts rules there still apply to 9:16 videos.

> Secrets rule: keys live in an env var for one command at a time. Never write them to a file, commit or chat. Nothing in this flow needs a key ($0 spend).

---

## 0. Brief (fill in per video)

| Field | Value |
|---|---|
| Working title | |
| Topic / the one thing the viewer learns | |
| Source folder | e.g. `~/Downloads/<Project name>/` (clips `*.mp4` + voice `*.WAV`) |
| Format | 16:9, 1920x1080, 30 fps, H.264 CRF 18, AAC 192k |
| Target length | whatever the voice is; chapters every 1-3 min |
| Thumbnail | 1920x1080 (not 1080x1920) |
| CTA | community name + URL, one ask |
| Privacy risks | names, chats, file paths, tokens visible on screen |

---

## 0. Architecture and token budget (read first)

Picture: [architecture.html](architecture.html) (top page of the site; regenerate with `python3 -I scripts/build_architecture.py`).

**Principle:** the MacBook Pro does the heavy work with local libraries; Claude only makes judgement calls from a one-page text report. This keeps token use low, makes every step repeatable by the owner without Claude, and keeps video and private screens off the cloud.

| Lane | What | Tools |
|---|---|---|
| 🖥️ MacBook (0 tokens) | sync clips, 1080p base, transcript with word timings, OCR of the screen, subtitles, cut candidates, personal-window finder, blur boxes, report, Remotion preview and render, privacy check of the export | ffmpeg, scipy, Whisper, Apple Vision, Python, Remotion + Chrome |
| 🤖 Claude (few thousand tokens) | read `REPORT.md`; write slide text; choose cuts and speed-ups; edit `overlays.json` / `cuts.json`; read the owner's timestamped notes | text in, text out |
| ☁️ Cloud (reuse) | kit zip + spec on Google Drive; folder id and link in Azure Key Vault; code, docs and the site on GitHub Pages (no media) | `pull_kit.sh`, `az`, `rclone`, `git` |

**Token rules (every video):**
1. **Do not have Claude look at frames to find things.** OCR returns text and pixel positions locally; Claude reads that. View a still only to confirm a final look (a few per video).
2. **One hand-off file:** `REPORT.md` (sync offsets and confidence, cut candidates, personal windows with what is said, edit counts, export privacy result). Read it instead of many outputs.
3. **Verify with a script:** `verify_export.py` OCRs the finished export and lists sensitive text still visible (pass/fail, exit code 1 on leaks). Fix `overlays.json`, re-render, re-run. No re-watching.
4. **Batch and background:** long jobs (Whisper, OCR, render) run in the background with one wait, not a poll every minute. Print counts and `head`, not whole files.
5. **OCR output is private.** `assets/ocr_frames.json`, `export_ocr.json`, `export_leaks.json`, `personal_windows.json` and `REPORT.md` contain the text you are hiding (chat titles, contact names). They are gitignored; never commit or paste them anywhere public (the repo and Pages site are public).
6. **Pull, do not rediscover:** the kit carries scripts and this spec. Start a session with the start prompt in section 11.

**One command prepares everything locally, then Claude reads one page:**
```bash
scripts/pipeline.sh "~/Downloads/<folder>" <slug>   # build_base.py (sync + 1080p base), Whisper, build_subs.py, ocr_all.sh, find_repeats.py, find_personal_windows.py, report.py
cat REPORT.md                                       # the only thing Claude needs to read
# edit remotion/src/overlays.json (slides, speedups) and cuts.json
python3 -I scripts/build_blurs.py                   # blur boxes from the OCR
cd remotion && npm run render && cd ..              # export
python3 -I scripts/verify_export.py                 # privacy check; then scripts/serve.sh and review in the player
```
Stages skip when their output exists, so a re-run only redoes what changed. `build_base.py` handles N clips (not just two): it finds offsets by cross-correlation, warns when confidence is under 3, checks clips tile, renders the base and sets `DURATION` in `theme.ts`.

---

## 0b. Environment (check it before you start)

Page: [environment.html](environment.html) (menu: 🧰 Environment, built from `ENVIRONMENT.md`). Run `scripts/check_env.sh`: it prints a tick or a cross for every item with the install command for anything missing.

| Need | Version here | Install |
|---|---|---|
| ffmpeg + ffprobe | 9.0.2 | `brew install ffmpeg` |
| python3 | 3.15.2 | `brew install python` |
| node + npm | 26.10.0 / 11.19.1 | `brew install node` |
| git + Xcode CLT (`swiftc` for Apple Vision OCR) | 2.56.1 | `xcode-select --install` |
| openai-whisper + model `small` (461 MB, auto-download) | pip | `pip install openai-whisper` |
| Google Chrome (Remotion browser) | current | `brew install --cask google-chrome` |
| Python packages numpy, scipy, noisereduce, soundfile | auto | created in `~/.cache/cmf-venv` by `build_base.py` / `denoise_audio.py` |
| npm packages (remotion + cli 4.0.250, react 18.3.1, typescript 5.6.3) | in `remotion/` | `cd remotion && npm install` |
| Optional: gh, az, rclone (remote `gdrive-shared`) | current | kit pull, Key Vault, Pages |

Inputs: one folder with `*.mp4` clips and one `*.WAV`. `remotion/public/base.mp4` must be a **hard link**, and the base video must have its index at the front (`-movflags +faststart`). No API keys; about 20 GB free disk; ports 3000 and 8000. The page also lists every processing step (input, script, output, committed or not) and measured machine times.

---

## 0a. Fast start: the kit on Google Drive

Everything reusable (this spec, scripts, the Remotion project, page and metadata templates) is packaged as one zip so the next video starts in minutes, not hours.

| Where | What |
|---|---|
| Google Drive (My Drive) folder **"Claude Missing Features Kit"** | `claude-missing-features-kit.zip`, `MASTER_SPEC.md`, `KIT_README.md` |
| Azure Key Vault **`dp-kv-deliverypilot`** (uksouth) | secrets `cmf-kit-drive-folder-id` and `cmf-kit-drive-folder-url` (the link lives here, not in the repo) |
| Repo | `kit/` (README, templates, `new-video.sh`), `scripts/pull_kit.sh`, `scripts/build_kit.sh` |

```bash
# new video in 3 commands (needs: az login, rclone remote "gdrive-shared")
mkdir -p ~/projects/<new-video> && cd ~/projects/<new-video>
~/projects/ClaudeMissingFeatures/scripts/pull_kit.sh .        # folder id comes from Key Vault, zip from Drive
./new-video.sh "<Title>" <duration_seconds>                   # fills page/metadata/brief templates, sets Remotion duration
# then section 1 of this spec; run it with the commands in section 6d
```

Templates in the kit (`templates/`): `BRIEF`, `metadata`, `SANITY_CHECK`, and the pages `index`, `preprod`, `prod`, `postprod`, `player`, `run` with `{{TITLE}}`-style placeholders.

**Keep the kit fresh:** after improving scripts, Remotion or this spec, run `scripts/build_kit.sh`, then upload the new `claude-missing-features-kit.zip` (and `MASTER_SPEC.md`) to the same Drive folder, replacing the old files. Test the kit from scratch every time: unzip into a temp folder, `./new-video.sh "T" 60`, `npm install`, `npx tsc --noEmit`.

**Rules:** the Drive link and any key go in Key Vault, never in the repo or chat. Do not put media in the kit. Reuse the existing vault; add new secrets with a `cmf-kit-` prefix.

---

## 0c. Save raw footage and source artifacts to Azure Storage (per-video container)

At the start of the project, save raw footage (`*.mp4` clips, `*.WAV` clean audio) and generated source artifacts to a **dedicated private Azure Storage container per video** (`<slug>-source`).

- **Per-video container:** each video project has its own separate container named `<slug>-source` (e.g. `claude-missing-features-source` in storage account `dpprojects`), keeping large source files and per-video assets isolated from other projects.
- **What is saved:**
  - Raw footage (`raw/` prefix): original camera/screen recording clips (`*.mp4`, `*.mov`), the clean audio track (`*.WAV`), and the base synced video (`<slug>-1080p.mp4`).
  - Source artifacts (`artifacts/` prefix): `REPORT.md`, `BRIEF.md`, `metadata.md`, `EDL.md`, analysis data (`assets/base_info.json`, `whisper_words.json`, `ocr_frames.json`, `personal_windows.json`, `repeats.txt`, `timings.json`), and the edit data (`remotion/src/project.json`, `overlays.json`, `cuts.json`, `variants.json`).
- **Tool:** `python3 scripts/upload_source.py [--folder ~/Downloads/<Project>] [--artifacts-only] [--raw-only] [--force]`
- **Credentials & Security:** uses Azure Key Vault (`cmf-exports-storage-account`, `cmf-exports-storage-key`); the container is strictly **private** (`--public-access off`); nothing private or signed is committed to git.
- **Why at the start:** guarantees that raw footage and source artifacts are preserved in the cloud immediately, allowing reproduction or recovery on any machine even if local files are deleted.

---

## 1. Pipeline

```
screen clips (.mp4, own audio) ─┐
voice recording (.WAV)          ├─► upload_source.py ─► Azure Storage: <slug>-source (raw/ + artifacts/)
                                ├─► sync (cross-correlation) ─► offsets
                                ┘
 offsets ─► ffmpeg: 1080p video + clean voice ─► base.mp4 (check loudness, frames)
 base.mp4 + voice ─► Whisper (small, en) ─► transcript + chapters
 base.mp4 ─► Remotion (overlays, title, callouts, thumbnail) ─► out/long.mp4
 transcript ─► metadata.md (title, description, chapters, tags, pinned comment)
 everything ─► build_site.py ─► index/player/metadata/spec .html ─► commit + push branch
```

---

## 2. Repo layout

```
README.md  MASTER_SPEC.md  metadata.md  .gitignore
index.html  player.html  metadata.html  spec.html  nav.js
scripts/build_site.py              renders *.md into the site
remotion/                          src/{index,Root,LongForm,Thumb,theme}.tsx, public/ (symlinks, ignored)
```

**Never committed** (`.gitignore`): `*.mp4`, `*.wav`, `node_modules/`, `remotion/out/`, `remotion/public/*`. Media stays in `~/Downloads`; Remotion reads it through symlinks in `remotion/public/`.

---

## 3. Sync clips to the voice recording

The camera/screen clips carry their own scratch audio; the clean voice is the Zoom/recorder WAV. Use the clip audio **only to find the offset**.

1. `ffmpeg -vn -ac 1 -ar 8000` each clip and the WAV to mono 8 kHz.
2. 100 Hz envelope (`mean(abs)` per 80 samples, `log1p`, subtract mean), then FFT cross-correlation (`scipy.signal.fftconvolve`).
3. Print `voice_time = clip_time + X` and confidence = peak / median of the top 50 peaks. **Want > 3.** Below that, listen and adjust by hand.
4. Sanity check: consecutive clips should tile (`offset2 = offset1 + duration1`). In this project 4.75 + 481.34 = 486.09, exactly the measured offset of clip 2.
5. The WAV can end before the last clip does: trim the video to the voice (`trim=0:<seconds>`), `-shortest`.
6. No numpy? `python3 -m venv <scratch>/venv && pip install numpy scipy`. Keep the venv out of the repo.

Check `ffprobe` for the audio stream before claiming a clip is silent.

---

## 4. Render the base video (ffmpeg)

- Fit a non-16:9 screen (e.g. 3456x2234 Retina) **without cropping**: scale to full height and fill the sides with a blurred, darkened copy of the same frame (`scale=480:270` -> `boxblur=12:2` -> `scale=1920:1080` -> `eq=brightness=-0.08`, then overlay the `scale=-2:1080` foreground centred).
- `fps=30` (screen recordings are often 60). `format=yuv420p`, `setsar=1`.
- Audio: `highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11`, `aresample=48000`, from the WAV started at the first clip's offset (`-ss <offset>`).
- `-c:v libx264 -preset medium -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k`. 4K screen input renders at about 3x real time on Apple silicon.
- Verify: `ffprobe` (1920x1080, 30 fps, duration), `ebur128=peak=true` (target about -14 LUFS, AAC costs ~0.5 to 1.5 LU), and a **contact sheet of frames** (start, middle, every clip join, end). Read the tiles.

---

## 5. Transcript, chapters, title and description

1. `whisper voice16k.wav --model small --language en --output_format json`. Use `medium` plus a vocabulary prompt when product names matter.
2. Subtract the voice offset from segment starts to get **video timeline** times.
3. Known ASR slips: product names (e.g. "Claude" heard as "cloud"). Fix them in all copy and any caption file.
4. **Title** <= 100 chars, plain, honest, names the problem and the payoff; keep 2 alternates. No `#Shorts`.
5. **Description:** one-paragraph hook, bullet list of what the viewer sees, **chapters** (first at `0:00`, at least 3, each >= 10 s, real timeline times), takeaways, honesty note (own experience, not affiliated, things change), CTA + URL, 3-5 hashtags.
6. Tags <= 500 chars. Pinned comment: explain the core term in 2-3 sentences, CTA, end with a question.
7. Upload settings: not made for kids; synthetic content = **No** when it is your real voice and a real screen recording; private first, public after checks.
8. Do not overclaim. If the feature did not appear on screen, the title must say so.

---

## 6. Remotion (long form)

- Composition `LongForm`: 1920x1080, 30 fps, `durationInFrames = round(seconds * 30)` (22502 for 750.07 s). `OffthreadVideo` plays `public/base.mp4`; overlays are siblings in an `AbsoluteFill`.
- Overlay ideas: title chip (first 3 s), chapter lower-thirds at chapter times, zoom-ins on UI (CSS `transform: scale` about the target point), callout arrows/boxes, end card with CTA (>= 5 s).
- `Thumb` is a `Still` at 1920x1080: claim in 2 lines, the answer largest in accent colour, readable at 160 px wide, no real faces.
- `remotion.config.ts` must point at the installed Chrome (`Config.setBrowserExecutable`), because the downloaded headless-shell fails to spawn on this Mac (error -88).
- Studio: `cd remotion && npm run studio` (http://localhost:3000). Render: `npm run render` -> `out/long.mp4`. Thumbnail: `npm run still`.
- Text always rendered with Remotion (this Mac's ffmpeg has no libass/freetype: no `subtitles`/`drawtext`).
- Edit by timeline: if an overlay must align with speech, take the time from the transcript, not from guesses.

---

## 6a. Cuts (repetitive parts)

Cuts are data, not edits to the video: `remotion/src/cuts.json` = `[[from,to],...]` in **seconds on the source (base.mp4) timeline**. `cuts.ts` builds the kept segments; `LongForm` plays them back to back with `Series` (3-frame audio fade at each cut, so no click); `Root` sets the composition length with `calculateMetadata`. `srcTime(outFrame)` maps the output back to the source, so subtitles and overlays stay on **source** time and never need re-timing.

1. Find candidates: `python3 -I scripts/find_repeats.py` lists repeated 4-word runs, stutters ("blank, blank") and gaps over 3 s (silence or screen-only).
2. Decide by ear and by eye in the player (timestamped feedback), then write the ranges to `cuts.json`. Cut on sentence or breath boundaries; never inside a word.
3. Re-run `python3 -I scripts/build_subs.py assets/whisper_words.json <offset>`: `subtitles.srt/.vtt` are rewritten on the **final** timeline (cues inside a cut dropped, later cues shifted); `subs.json`/`subs.js` stay on the source timeline.
4. **Chapters shift:** every chapter after a cut moves earlier by the removed length. Recompute them from the final timeline before pasting into the description.
5. Test with a still, not by eye alone: temp cut `[[10,20]]`, render frame 420, expect source second 24.0 and the matching caption, then restore `[]`.

## 6b. Animated subtitles

- Need **word timestamps**: `whisper voice16k.wav --model small --language en --word_timestamps True --output_format json` (about 10-15 min on CPU for 12 min of audio). Without them `build_subs.py` falls back to estimated timings (character-length weights).
- `build_subs.py` applies the product-name fixes (`FIX`: "cloud" -> Claude, "Grok bot", "Homebrew", "HTML", "Canva"), chunks cues to 70 characters, and keeps real word timings when the fixed text still has the same word count.
- `Subtitles.tsx`: phrase springs in and fades out; the spoken word turns accent colour and pops (scale <= 1.07); upcoming words are dimmed. **Keep the flex gap >= 24 px**, otherwise the pop makes words touch ("newfeature").
- Burned-in captions cover UI at the bottom; also upload the `.srt` so viewers can use YouTube's own captions. Proof-read the `.srt` first.

## 6c. Recorder UI and image overlays

- Screen recordings often **start (and end) on the recorder itself** (OBS Studio window, dock tooltip "OBS"). Check frames at 0-3 s and the last 3 s, and sweep the whole video with a 10 s contact sheet.
- Do not cut the opening if the voice already speaks: cover it. `overlays.json` -> `intro_card` shows the `Thumb` design over `0 to 4.3 s` (2 s longer on request, so the title lands), fading out over 0.3 s.
- `overlays.json` -> `images: [{from,to,src,w,h,caption,caption2,highlight:{x,y,w,h},arrow:{x1,y1,x2,y2}}]` shows an image full-frame; with `caption` it becomes an **expected-feature card**: caption on top, an orange box around the feature and an arrow pointing at it (coordinates in the picture's own pixels, read them from the image; verify with one still). Example: `whiteboard.jpeg` (the Artifacts page with the Whiteboard tile) at 1:51–2:03, "This is the feature I expected to see: Whiteboard". Plain `images: [{from,to,src}]` shows an image full-frame (files in `remotion/public/img/`, not committed) on source time, with 0.2 s fades. Use it wherever private or distracting screen content must be replaced.
- Tooltips that flash while the cursor crosses the dock (iTerm, OBS) are small; cover them only if the owner asks.

## 6d. Run it (links and commands)

| What | Link | Start it with |
|---|---|---|
| Remotion Studio (edit, preview, cuts, subtitles) | http://localhost:3000/LongForm | `cd remotion && npm run studio` |
| Thumbnail still | http://localhost:3000/Thumb | same Studio |
| Site + player (video seeking works) | http://localhost:8000/player.html | `scripts/serve.sh` |

```bash
cd ~/projects/<project>/remotion
npm install                                                  # first time
ln ~/Downloads/<slug>-1080p.mp4 public/base.mp4             # HARD link, once (a symlink breaks render)
npm run studio                                               # http://localhost:3000/LongForm
npm run render                                               # -> remotion/out/long.mp4
npm run still                                                # thumbnail -> remotion/out/thumbnail.png
npx tsc --noEmit                                             # typecheck
cd .. && scripts/serve.sh                                    # http://localhost:8000/player.html (new terminal)
open -a "Google Chrome" http://localhost:3000/LongForm       # always open in Chrome
```
The same table and a troubleshooting list are on the site page `run.html` (menu: 🧪 Run & links). Both links only work while the command is running.

**Player rule:** the player needs the video next to it as `long.mp4` (git-ignored). `scripts/serve.sh` hard-links your render to `long.mp4` and serves the folder with HTTP Range support (plain `python -m http.server` has none, so seeking and chapters break). The player shows a status line: green "Playing long.mp4 (12:30)" or a warning with the fix. Verified in Chrome: loads 1920x1080, seeks to 20 s, caption cue active.

## 6e. Speed-ups, slides, blur boxes (editing personal or slow parts)

All three are data in `remotion/src/overlays.json`, times are **source seconds** (user timecodes like `04:17:28` are `mm:ss:ff` at 30 fps, so 257.93 s; `01:08:14` is 68.47 s).

**Speed-ups** `speedups: [{from,to,rate,mute}]`: `cuts.ts` splits the timeline there and plays that range with Remotion `playbackRate`. Speech sped up is unusable, so `mute: true` silences it and `Subtitles.tsx` hides captions inside it (`build_subs.py` drops those cues from the `.srt`). Example: typing the prompt, 68.47 to 79.0 s at 3x (10.5 s -> 3.5 s, muted). `build_subs.py` also writes `export_map.js` (source <-> export time map) so the player can switch versions at the same moment.

**Slides** `slides: [{from,to,title,bullets[]}]`: full-frame explainer (`Slide.tsx`, bullets spring in). Use one to replace a whole personal window (here: the opening IBM/Grok Bot scene, 4.3 to 16 s, and nine short Grok Bot windows later). Write the bullets from what is said at that moment (transcript), never invent claims. Keep short slides to 1-2 bullets.

**Blur boxes** `blurs: [{from,to,x,y,w,h}]` (pixels in the 1920x1080 frame; frosted `backdrop-filter` plus tint, unreadable). Generate them, do not place by hand:
```bash
mkdir frames && ffmpeg -i long.mp4 -vf fps=1 -q:v 4 frames/%04d.jpg            # frame NNNN = second NNNN-1
swiftc -O scripts/ocr_frames.swift -o ocr_frames                                # Apple Vision, no cloud
# every 2 s is enough (static sidebars): split odd frames into 4 folders and run 4 processes in parallel (~2 min for 375 frames)
./ocr_frames frames_part0 ocr/part0.json  (x4) ; merge into assets/ocr_frames.json
python3 -I scripts/build_blurs.py                                               # rewrites "blurs" in overlays.json
```
`build_blurs.py` rules: **A** chat-title list in the Claude sidebar, two fixed boxes (nav visible: y 462-1030; list scrolled to top: y 95-1030, x 128-612); **B** sensitive words anywhere (`KEYWORDS`: market participant, employment gap, capgemini, gap proof, kaya, lacan, incident report, onboarding bot, pexabo); **C** the mini sidebar inside a pasted screenshot, anchored to the line below it ("Checking which Artifacts…") because OCR cannot read tiny text. Frames covered by the intro card or a slide are skipped. Do not blur words the speaker says on purpose (the "IBM" 9-to-5 block in the planner canvas stays).

**Find personal windows (for slides):** scan the OCR for contact/agent names (Skool, LinkedIn, Gmail, Rag Manager, your own name) on 2+ lines; merge hits closer than 6 s; pad -1/+2 s; read the narration in each span (from `subs.json`) and write the slide from it.

**Verify with real stills, not just numbers:** render frames at the user's timecodes and at one frame per distinct layout (`npx remotion still src/index.ts LongForm out/x.png --frame=<n>`; output frame = source seconds minus the time saved by earlier speed-ups, times 30). Montage them with ffmpeg and read every tile.

## 6f. Export render and the player's version switch

- `scripts/render_export.sh "what changed"` (calls `npx remotion render`) -> `exports/<slug>-<platform>-v<N>.mp4` (e.g. `exports/<slug>-youtube-v<N>.mp4`), also `remotion/out/long.mp4` = latest (section 6l). 22,291 frames (12:23) took about 25 min at about 13 fps (10-core Apple silicon, concurrency 5). **The ETA printed in the first minutes is far too high (it said 2 h); measure frames per 30 s.** Do not run other heavy jobs (OCR, still renders) meanwhile.
- `scripts/serve.sh` links `long.mp4` (hard link to the original) and `export.mp4` (symlink to `remotion/out/long.mp4`, always the newest render, git-ignored).
- Chapters in the player and in `metadata.md` come from `assets/chapters.json` through `build_chapters.py` (source and export timelines).
- **Go to last review point:** a ⏮ **Last point** button on the video, a button in the Feedback panel (it shows the last note, e.g. `[export 1:35]`) and the `R` key jump to the most recent `[orig|export m:ss]` note, switching version if the note belongs to the other one and starting 3 s earlier; with no notes it goes to where you last stopped watching (saved every 3 s). The player also opens at a moment from a link: `player.html?v=exp|orig&t=<seconds>`.
- **Keyboard (YouTube/editor style, on the player):** `Space` or `K` pause/play; `L` faster (1 -> 2 -> 4 -> 8x); `J` slower (halves down to 0.25x); `1` normal speed; `<-` / `->` skip 5 s; `,` / `.` step one frame while paused; `F` fullscreen; `M` add a note at this moment; `R` go to the last review point. Keys are ignored while typing in the feedback box. The speed menu follows the keys (options 0.25x to 8x). Reference for the behaviour: https://www.youtube.com/shorts/H-KoWWXG5OI
- **Add-note button (fastest feedback):** a 📍 **Add note** button sits on the video (bottom-right, above the controls) and `M` does the same: it pauses, opens the Feedback panel if collapsed, stamps `[orig m:ss]` or `[export m:ss]` by the version being watched and puts the cursor at the end; type the note, then `Ctrl/⌘ + Enter` to carry on watching. Typing the letter m in the box is safe. "Insert current time" (no pause) and "Clear feedback" (with Undo) stay in the panel.
- **Layout:** the video, then the **Feedback** panel directly under it (so notes are typed without scrolling), then collapsible panels: Chapters, Keyboard shortcuts, Sources and tools, Measured specs. Each panel is a `<details class="pn" data-key="…">`; open/closed state is remembered per panel in the browser, and **Collapse all / Expand all** sits in the control bar. Keep new panels in this pattern.
- `player.html` has **Original / Latest export** buttons, **Side by side** (the export follows the original through speed-ups and cuts via `export_map.js`, muted, re-synced every 250 ms), live export info (size, render time from a HEAD request), chapters re-timed per version, subtitles track on the original only (the export has them burned in), and feedback notes tagged `[orig m:ss]` / `[export m:ss]`.

## 6g. EDL: the edit decision list (record every decision)

Page: [edl.html](edl.html) (menu: ✂️ EDL), built from `EDL.md`, which `python3 -I scripts/build_edl.py` **generates** from the real edit data: `remotion/src/overlays.json` (intro, slides, blurs, speed-ups, outro), `cuts.json`, `assets/audio_fixes.json`, `assets/edl_decisions.json` and `export_map.js`. Edit those files, never `EDL.md`.

It contains: (1) the list, one row per edit with **source and export timecodes**, duration, what, why, status; (2) how we worked (the loop below); (3) the **decision log**: every owner note, the interpretation, the decision, where it was implemented and how it was checked; (4) cut candidates (nothing applied until the owner decides); (5) rules for the next EDL. Add an entry to `assets/edl_decisions.json` for every note and every problem the checks find.

**The loop:** prepare locally and read `REPORT.md` -> owner reviews in the player and pastes `[orig m:ss]` / `[export m:ss]` notes -> convert to source time (`source = export + time saved by earlier speed-ups`) -> check against data (transcript, OCR, audio analysis, one still) -> change `overlays.json` / `cuts.json` / run an audio step -> **one** render for all pending notes -> `verify_export.py` and stills -> log it in the EDL. If the literal request would damage the video, do the smaller fix that meets the goal and say so.

**Decision rules:** cover before cut (slides over personal windows keep the narration whole); cut only dead or repeated parts and only when the owner says; no transitions unless asked (hard cuts; audio fades at cuts stay to avoid clicks); pad generated boxes and slides at the edges; measure instead of guessing; chapters follow the **export** timeline (`build_chapters.py`, each at least 10 s).

## 6h. Audio: remove steady noise (hoover, fan)

Owner note example: "[export 9:25] the hoover comes in the audio, cut all that part out".
1. **Find it with numbers, not by ear:** `python3 scripts/denoise_audio.py in.mp4 --scan` (noise haze above the clean baseline per 20 s) and one spectrogram of the window (`ffmpeg -ss <t> -t 40 -i in.mp4 -lavfi showspectrumpic=s=1200x360:legend=1:scale=log:fscale=log:start=60:stop=6000 spec.png`): steady broadband haze plus horizontal tone lines = hoover or fan. Here it began at source 571 s and ran to the end.
2. If the noise lasts for minutes, **do not cut it** (that removed the conclusion); remove it: `python3 scripts/denoise_audio.py in.mp4 out.mp4 --noise <start> <end> --from <t> --strength 0.8` where `--noise` is a stretch with only the noise and no speech (here 592 to 622 s). Library: `noisereduce` (stationary mode). Video is stream-copied; a 1.5 s crossfade enters the cleaned part.
3. **Check by numbers:** the script prints haze before -> after per minute (want about 0 dB against the clean part; here +11 -> -1/0) and speech level change (want above -3 dB; here -0.5). Strength 0.95 over-cleans (below the natural room tone, watery); 0.8 is natural. Point `remotion/public/base.mp4` (hard link) at the cleaned file; keep the original for the player's Original.
4. A hard cut stays available if the owner insists: add the range to `cuts.json`.
5. **Fix the file layout:** the output must have `moov` first (`-movflags +faststart`, done by the script). Without it Remotion rendered at 8.7 instead of 13 frames per second.

## 6i. Ending: summary and community call to action

`overlays.json` -> `outro: [{seconds,kind,title,bullets|line,url,note}]`. `Outro.tsx` plays after the footage (silent, hard cuts): a **summary slide** (4 points taken from what was said, never invented) then a **CTA card**: "Learn it in depth", "Join the Delivery Pilot community on Skool", `skool.com/delivery-pilot-8938`, "Link in the description and the pinned comment". No income or result promises. The composition length is `videoFrames() + outroFrames()`. Each outro part counts as a YouTube chapter (the last must be at least 10 s). Also put the full URL in the description and pinned comment.

## 6j. OKRs and value recognition (in the Pre-prod page)

Set the **objectives and key results before producing**, measure after the export, score honestly. Page: [preprod.html](preprod.html#okr) (block generated between `<!--OKR-->` markers).

- **Data:** `assets/okr.json` (start from `kit/okr.template.json`): objectives with key results (`metric` + `op` + `target`, or `manual` for numbers that need YouTube data), a one-sentence **value proposition**, and a rubric.
- **Measure:** `python3 scripts/measure_video.py` writes `assets/metrics.json` from the real export: loudness and true peak (EBU R128), words per minute, dead air (silence over 3 s) and its share, stutter spots, time to the first problem statement and first action, summary points, chapters and their shortest length, CTA seconds, URL in description and pinned comment, private lines left, noise left after the audio fix.
- **Statuses:** ✅ met · 🟡 within 10% · ❌ missed · ⏳ open (needs YouTube data after publishing).
- **Value recognition:** value only counts if the viewer recognises it. The page lists the five moments where that happens with export timecodes that open the player (recognise my situation; first useful action; see the proof; get the recap; know what next).
- **Score (0 to 100):** nine dimensions, weights 15/15/10/15/15/10/10/5/5 (promise clarity, time to value, proof on screen, actionability, pacing, audio and picture quality, trust and honesty, structure and discoverability, call-to-action fit), each 0 to 10 with the evidence written from the measurements (`{metric}` placeholders), the way to raise it and the points it would add. It is a **pre-publish estimate**; replace it with real numbers after 28 days (day 2, 14, 28 checklist on the page). Propose improvements, never apply them without the owner. Honest example: "(and the Fix)" in a title when the honest outcome is "wait" costs promise clarity.
- Run: `python3 scripts/measure_video.py && python3 -I scripts/build_okr.py`.

## 6k. Artifacts page (every added element, clickable)

Page: [artifacts.html](artifacts.html) (menu 🧩 Artifacts, group Review), generated by `python3 -I scripts/build_artifacts.py` **after the export render**. It lists everything placed on or around the footage: source clips, title card, slides, picture cards, blur regions, speed-ups, audio fixes, captions, ending. Each artifact has **source and export timecodes**, a frame taken from the final export (so previews are exactly what viewers see and are already privacy-checked), a search box, type filters and an export-timeline strip. Click a card: large image (blur regions show their box outline; audio fixes show before/after spectrograms), what it is, **how it is used**, where it lives (file and JSON path), the owner's original request and the decision from the EDL, previous/next arrows, and buttons that open the **player at that moment** (`player.html?v=exp&t=<s>` or the original at source time). Frames go to `artifacts/` (about 3 MB); re-run after every new export. Nothing in it is specific to one video.

## 6l. Export versions (every export is numbered)

**Rule: every export gets a version number and platform tag, is never overwritten, and the number appears in all feedback.** File `exports/<slug>-<platform>-v<N>.mp4` (previously `exports/<slug>-v<N>.mp4`; `slug` in `project.json`; e.g. `exports/<slug>-youtube-v<N>.mp4`, `exports/<slug>-linkedin-v<N>.mp4`, `exports/<slug>-x-v<N>.mp4`), a copy `~/Downloads/<slug>-<platform>-v<N>.mp4`, the Drive copy `videos/<slug>-<platform>-v<N>.mp4`.
- **Render with** `scripts/render_export.sh "what changed in this version"`: picks the next number, regenerates captions, the time map and chapters for this exact state of the edit, renders, stores the file, points `export.mp4` and `remotion/out/long.mp4` at the latest, and registers it.
- **Registry:** `assets/exports.json` (committed; no media) holds for each version the file, render time, length, size, short checksum, a one-line **what changed**, and the **source-to-export time map as it was for that render** (later edits move times). `exports.js` hands it to the player. `scripts/register_export.py` writes both; it refuses to overwrite a version.
- **Player:** a version selector next to "Export vN (latest)"; switching keeps your place through each version's own time map. Every note is tagged **`[vN m:ss]`** (`[orig m:ss]` for the original); old `[export m:ss]` notes mean the latest. **Copy feedback** starts with a header naming the version and its render time. "Last review point" jumps to the note's own version. Deep links: `player.html?v=v3&t=<s>`.
- **Reading a note:** the number tells which timeline the time is on. Convert with that version's map (`source = export time + time saved by earlier speed-ups, minus cards and cuts that shift it`); the EDL shows source and export times side by side, and its decision log has an **In export** column saying which version implemented each note.
- **Version notes in the registry are the changelog.** v1 here was the first export (not kept); v2 fixed leaks and added the ending; v3 added the Whiteboard card; v4 applied the round-4 notes.
- Back up each new version to Drive `videos/` (keep old ones), name and tag everything with the number, mention the version when asking for or reporting feedback.

## 6m. Cuts with an apology card, lower thirds, manual blurs

- **Cuts and cards** (`cuts.json`, `overlays.json › inserts: [{at,seconds,kind,animation,title,text}]`): an **insert** is a card placed on the timeline at a source time, normally where something was cut out. `cuts.ts` places it before the next kept piece, shifts later export times by its length, freezes source time during it (no captions, blurs or slides), keeps the audio silent. `animation: "hoover"` draws a frame-driven cartoon vacuum (like a GIF; add other animations in `InsertCard.tsx`). `build_subs.py` writes inserts into `export_map.js` so the player, EDL, chapters and Artifacts page stay correct.
- **Where to cut:** at sentence boundaries (look at cue start/end times in `subs.json`), even if the owner's timecode lands inside a sentence; say so in the decision. A chapter that falls inside a cut starts at the next kept moment.
- **Lower third** (`overlays.json › lower_thirds: [{from,to,label,text}]`): a text bar in the lower left above the captions for a point made on screen without covering the footage. Hard cut in and out.
- **Manual blurs** (`overlays.json › manual_blurs: [{from,to,x,y,w,h,why}]`): hand-placed boxes for what OCR cannot do: a notification banner that appears for a few seconds (find it with a 1 fps strip of the corner), or part of a window that must stay readable. `build_blurs.py` never overwrites them. Also add the sender or name to `project.json › sensitive_keywords` so the export check flags it anywhere else; match OCR spelling (a name with a space is two words).
- **Showing a real window that holds private lists:** prefer the real window with the private list blurred over a slide when the owner wants to see the action (here: the Grok Bot update). Use one box while a menu is closed and a shorter one while it is open; get the timings from OCR (`New update available`).
- **Look-alike words in captions:** when the owner reports one mis-heard word, search every variant by regex (`cloth*`, `clod*`, `claw*`), fix them all in `project.json › caption_fixes`, and say how many were found.
- **Files named in a note:** if the file named is not in Downloads (or two are identical), ask which one before rendering; do not guess.

## 6n. Script page and subtitle quality (find it, fix it, record it)

Page: [script.html](script.html) (menu 📜 Script), built by `python3 -I scripts/build_script.py`. It holds the **whole spoken script by chapter** (the final captions) with source and export timecodes that open the player (✂️ = cut from the video, 🔇 = muted speed-up), a search box, a **before → after table of every caption change**, the **subtitle issues and how each was fixed** (`assets/subtitle_issues.json`, status ✅ fixed · 👂 needs the owner's ear · ℹ️ by design · 🟡 known limit), and measured numbers. The same cleaned text goes to `subtitles.srt/.vtt` on the final export timeline.

**Process (every video):**
1. `python3 -I scripts/check_subtitles.py` finds likely errors from data, without listening: words **Whisper is unsure of** (probability under 0.5), look-alikes of product names, **stutters** (same word twice), reading speed, **flicker** (captions under 0.7 s), and which fix rules fired.
2. **Fix what the evidence supports:** product names and fixed phrases go into `remotion/src/project.json › caption_fixes` (`[regex, replacement]`). When the narrator reads text that is on screen (an answer from Claude, a menu), take the correct wording from the screen (OCR of that frame) instead of guessing. Search every look-alike of a reported word (`cloth*`, `clod*`, `claw*`).
3. **Automatic clean-up in `build_subs.py`:** immediate repeated words are dropped from the caption (the voice keeps them; the highlight keeps the kept word's real timing); a caption stays on screen at least 0.9 s (extended into the silence after it) and a very short one joins the previous caption when close and under 80 characters; captions are hidden inside muted speed-ups and cards.
4. **Do not invent:** where the text stays doubtful (spoken version numbers, garbled phrases), list it as 👂 needs the owner's ear with its time, and change it only after the owner confirms (then add a rule).
5. Record every issue with how it was found and how it was fixed in `assets/subtitle_issues.json`; re-run `build_all.sh`. A caption change needs a new numbered export (section 6l) because captions are burned in; the `.srt/.vtt` update without one.
6. Known limit: when a fix changes the number of words in a line, that line's word highlight uses estimated timing (it still starts and ends with the line).

## 6o. Changelog page (everything that happened, with emojis)

Page: [changelog.html](changelog.html) (menu 🗒️ Changelog), from `CHANGELOG.md`, which `python3 -I scripts/build_changelog.py` generates. It combines: a **legend of emojis** (🚀 start · 🎬 video edit · 🧩 site or tool · 🐛 bug found and fixed · 🔒 privacy · 🔊 audio · ♻️ reuse and kit · ☁️ publish and backup · 🧪 tests · 🛑 blocked by the permission system · 📈 measured · 🧠 decision); the **export versions** table (`assets/exports.json`: what changed in each); the current **score and key results**; the **timeline by rounds** (`assets/changelog.json`, written by hand as work happens, newest round first, including mistakes and blocked actions); the **decision log** (`assets/edl_decisions.json`); and the **commits** from git. Add an entry to `changelog.json` for every notable change, bug, block or result; the tables update themselves.

## 6p. Notes on the Artifacts page

Every artifact has a **📝 My note** box in its detail view (and the cards show a 📝 badge when they have one). Notes are saved in this browser under a **stable key** (kind + title + start time), so they stay on the same artifact after the page is rebuilt, and each note is **tagged with the export version** (`[v5 4:02] (artifact #41 · Blur region: …) text`). Saving shows the green **✔ Saved** pop and a green glow on the box. The toolbar has **📝 My notes** (list of all notes with links back to the artifacts), **Copy all notes** (header names the export version), **↗ Send all to player feedback** (appends the notes to the player's feedback box, so one list goes to the owner's reviewer), **Clear all notes** with **Undo**, and an "only artifacts with notes" filter. Each artifact also has its own **↗ Add to player feedback** button.

## 6q. README and the contents table (navigation)

- **`README.md` is a navigation hub, generated** by `python3 -I scripts/build_readme.py` (never edit it by hand): first line is the live-site link (from `project.json › repo`), then **Start here** (every site page with what it is), **Master spec at a glance** (the linked contents and the full **prompt to execute**), a **commands** cheat sheet, **what is where**, the export versions and the score. The older Shorts recipe lives in `docs/SHORTS_FLOW.md` (site page `shortsflow.html`).
- **`MASTER_SPEC.md` has a linked table of contents** at the top, kept current by `python3 -I scripts/build_toc.py` (anchors follow GitHub's rule; the site adds the same ids to its headings, so the links work in both places). Run it after adding or renaming a section; `build_all.sh` does it.
- Rule: a new section in the spec means a new line in the contents (automatic), a row in the README table if it is a page, and a note in the changelog.

## 6r. Platforms: separate renders, the Publish page, Azure storage

**One edit, three cuts.** Each platform gets its own length and its own numbered export (same version number for the same state of the edit):

| Platform | Limit (as of writing, check your account) | Target | This project's cut |
|---|---|---|---|
| ▶️ YouTube | long form, no limit that matters here | about 12 min | the full video, 11:59 |
| 💼 LinkedIn | native video 3 s to 10 min, 5 GB | 1 to 3 minutes performs best | 3:19 (9 highlight ranges + a 14 s ending) |
| ✖️ X | standard accounts 2 min 20 s (Premium longer), 512 MB | about 2 min | 1:54 (5 ranges + an 11 s ending) |

All are 16:9, 1920×1080, captions burned in (no separate file needed).
- **Cut lists live in data:** `remotion/src/variants.json` per platform: `keep` (source-second ranges in time order; the global `cuts.json` still applies), `outro` (a shorter summary and call to action), `inserts` (cards at cuts, off by default for highlight cuts). A platform without `keep` is the full video. Choose highlights along a **story spine**: hook (what and why) → proof (the expected feature on screen) → the answer → the action → the takeaway; snap every range to caption boundaries (`subs.json`) so no sentence is cut mid-way; add up the kept seconds plus the ending and stay under the limit with margin.
- **Render:** `scripts/render_export.sh "what changed" youtube linkedin x` (or `--version N` to add platforms to an existing number). Files `exports/<slug>-<platform>-v<N>.mp4` across all platforms (`exports/<slug>-youtube-v<N>.mp4` for YouTube, `exports/<slug>-linkedin-v<N>.mp4` for LinkedIn, `exports/<slug>-x-v<N>.mp4` for X). Remotion picks the cut with `--props '{"variant":"linkedin"}'`; `build_subs.py <words.json> <offset> <platform>` writes that cut's time map to `assets/maps/<platform>.json` (captions and `.srt` always stay for the full video); the registry keeps `platform` and the map per export. In the player the keys are `v5`, `v5-linkedin`, `v5-x`; notes are tagged with them (`[v5-x 0:40]`).
- **Check each file:** `python3 -I scripts/verify_export.py exports/<file>` (the result is stored per export and shown on the Publish page) and `measure_video.py` for the full video.
- **Publish page** ([publish.html](publish.html), menu 📣 Publish, built by `scripts/build_publish.py` from `assets/publish.json`): one collapsible card per platform with format and limit, the export (key, length, size, what changed), a **length bar against the limit** (red when over), the privacy-check result, a player link, the **storage link placeholder** `Azure storage link appears here after upload`, the **post link placeholder** `Paste the … post link when shared`, ready-to-paste title and text with **character counters** (YouTube title 100, X 280, LinkedIn 3,000), a **My note** box per platform and an all-notes list (copy, send to player feedback, clear with undo, green ✔ Saved), and a "before you share" checklist. **Rule: angled brackets are not allowed** in UI text, placeholders, or copy on the Publish page (they look like unrendered HTML tags or can be malformed/stripped by browsers and platforms; use plain text or square brackets/parentheses instead). The page also features a dedicated **Video Thumbnail section** (`assets/thumbnail.jpg`, 1920×1080 px, rendered from `Thumb.tsx` via `cd remotion && npm run still`) with live preview, 1-click download, and inclusion in the "Download all exports & metadata" zip. When the owner shares, they give the post links; put them in `assets/publish.json` (`post_url`, `status: shared`) and run `build_all.sh`: the page fills in and the menu **🔗 Links** group shows ▶️ YouTube post, 💼 LinkedIn post, ✖️ X post (the group also lists the community and the Azure portal links from `project.json › links`).
- **Azure Storage and Key Vault:** exports go to a **private** blob container (`claude-missing-features-exports` in the owner's storage account), never public. Secrets live in Key Vault: `cmf-exports-storage-account`, `cmf-exports-container`, `cmf-exports-storage-key`. **One-time setup by the owner:** `! scripts/setup_azure_exports.sh [account] [resource-group] [vault]` (creates the container and stores the three secrets; the assistant's permission system does not copy storage keys into the vault). Then `python3 scripts/upload_exports.py [--version N] [--days 30]` reads the vault, uploads the latest export of each platform and creates **time-limited read-only SAS links**; or `--login` uses `az login` (Azure AD, no key, links up to 7 days). **Signed links are credentials:** they are written only to the git-ignored `publish_links.js` / `assets/publish_links.json`, which the Publish page loads locally; never commit them or put them on the public site.
- **Verify the links (done this way here):** HEAD/range requests with the signature must return 206 with the full file size, and the same URL without the signature must return 404 (private). Print status and sizes only, never the signed URL.
- **Public player (GitHub Pages) plays from Azure:** `python3 scripts/upload_exports.py --version N --site --skip-upload` creates a **stored access policy** `site-player` (read only, 90 days) on the container and writes `azure_links.js` (committed on purpose; read-only SAS links that reference the policy, no key in them). `player.html` switches to **public mode** on any host except localhost (or with `?public=1`): only exports that have a link are listed, they play from `*.blob.core.windows.net`, and the **original recording is locked** (it shows unblurred screen content and is never uploaded; side-by-side is off). To extend access change the policy expiry (`az storage container policy update --name site-player --expiry …`); to **revoke** delete the policy (`az storage container policy delete`) and every public link stops working without touching the repo. Only publish exports that passed `verify_export.py`; test with `?public=1` locally before pushing. Links in the repo are public by nature: treat them as a published video.
- **Review flow:** render all platforms → verify each → upload → open `publish.html` locally and the player → write notes → the owner shares and sends the post links → fill the placeholders → rebuild → back up to Drive.

## 6s. Completion time: stages, order, who, and how to prepare

Page: [timeline.html](timeline.html) (menu ⏱️ Time & order, group Start), built by `python3 -I scripts/build_timeline.py` from `assets/timings.json`. It lists **every stage in order** (19 here: prep, ingest, analyse, decide, preview, render, check, publish, review, rounds, wrap-up) with **who does it** (🖥️ MacBook with local tools, 🤖 Claude, 👤 the owner), **how long it took** (measured on this project, each marked *measured* or *estimate*), the **LLM involvement** (none for the machine stages; Claude reads a one-page report and writes JSON), what **runs in parallel**, and what to **prepare** to save time. It also shows the elapsed time since work started, the time of one clean pass, and a **calculator** (raw minutes, YouTube / LinkedIn / X minutes, number of owner rounds, machine idle or busy) for the next video.

**Rule of thumb (measured, 10-core Apple-silicon MacBook Pro):** sync + base video about 0.4 × raw length; Whisper small about 0.36 ×; OCR about 0.32 × (cached); **Remotion render about 2.3 × the video length** (13 frames/s idle, 5 to 9 when the machine is busy); privacy check about 0.33 × per file; denoise about 1 min; the page builds a few seconds. **The render dominates**: a full pass of 12 + 3.3 + 1.9 minutes of video is roughly 45 min of rendering. Claude's share is small and mostly one decision pass (10 to 20 min) plus about 15 to 30 min per round of owner notes (estimates).

**Order (critical path):** check machine → scaffold → sync → (base video ∥ Whisper) → OCR → analyse → **Claude decides** (slides, cuts, ending, OKRs) → blur boxes and noise → stills → **render YouTube → render LinkedIn + X** → privacy check each → measure, score, build pages → upload → **owner review** → notes → repeat from the decide step for the changed parts only → publish and fill the post links → commit, push, back up.

**What to do to prepare (each saves real time):** install and check everything first and cache the Whisper model; create the Azure container and Key Vault secrets once; start Whisper as soon as the sync is done; **keep the machine idle during a render**; make the base video with the index at the front (faststart, about 35% faster renders); **collect all notes and render once per round**; use stills, `--scale=0.5` or `--frames=a-b` for quick looks instead of full renders; choose the platform highlight ranges while the YouTube render runs and queue all platforms in one command; run the privacy check on the YouTube file while choosing cuts; keep caches (OCR, transcript, registry); fill `project.json` and `okr.json` before editing; record cleanly (no notifications, quiet room), which avoids blur work, cuts and apology cards. Update `assets/timings.json` when a stage gets faster; add new stages with who, basis, parallel and prep.

## 6t. The pipeline drawn with tldraw

Page: [pipeline.html](pipeline.html) (menu 🗺️ Pipeline, group Start). The whole flow on one **tldraw** canvas: every stage as a box in the lane of whoever does it (🖥️ MacBook, 🤖 Claude, 👤 you) with its tool and time, arrows for the order, the Whisper-beside-base-render parallel step, the **review loop** back to the decide step, and where results go (Azure private container, Key Vault, Google Drive, GitHub Pages, the platforms). Three **bands** (1 prepare and ingest, 2 decide, render and check, 3 publish, review and wrap up) with buttons to jump between them; Fit, Make editable and Download PNG.
- **Data, not drawing:** `python3 -I scripts/build_pipeline_diagram.py` turns `assets/timings.json` (the Time & order data) into `pipeline/pipeline.json` (boxes, arrows, bands); the page reads it at runtime, so changing a stage or a time needs no rebuild of the JavaScript. Arrows are bound to their boxes, so dragging a box in edit mode keeps them connected.
- **The app** is `pipeline/src/main.tsx` (React + tldraw 5.x), bundled with esbuild: `cd pipeline && npm install && npm run build` writes `pipeline/dist/app.js` and `app.css` (about 2 MB, **committed**, so GitHub Pages and the kit need no build). `node_modules` is not committed.
- **License:** tldraw is used under its own license; it may show a "Get a license for production" watermark and loads fonts and icons from its CDN. Set `licenseKey` in `main.tsx` if you hold one. If the canvas cannot load, the page lists the stages as text.

## 6u. Evals: can the spec recreate this project?

Page: [evals.html](evals.html) (menu 🧪 Evals, group Start), built from `assets/evals.json` by `python3 -I scripts/eval_spec.py --page-only`; **run the evals with `python3 scripts/eval_spec.py`** (about 2 minutes; `--quick` skips the from-scratch kit test). Run them before every release; a failing eval is a **gap in the spec or the kit**: fix the spec or kit, never the test.

| Group (weight) | What it proves | Checks |
|---|---|---|
| **A. Recreate from the kit** (40) | A fresh folder made only from the kit builds the whole project | the kit builds and has every required file; `new-video.sh` scaffolds; `build_all.sh` + `check_site.py` pass; TypeScript compiles; every script compiles; a second build changes nothing; the kit contains none of this video's words |
| **B. Spec coverage** (30) | Nothing the project needs is undocumented | every script, data file and site page is named in the spec or `ENVIRONMENT.md`; every `scripts/...` path in the spec exists; every contents link and every "section 6x" reference resolves; every command in the prompt to execute exists |
| **C. Retrieval questions** (20) | The spec alone answers what a newcomer must know | `evals/spec_questions.json`: about 30 questions, each with the facts (regular expressions) that must appear in the spec; score = share answered |
| **E. Kit completeness** (10) | Everything generic is in the kit | every script, Remotion source file, template and the nav/menu code in the repo is shipped in the kit zip |

The page shows the score and grade, every check with its detail and a fix hint, the unanswered questions, the history of runs, and a **ready-to-paste prompt for an LLM eval**: give a fresh Claude session only `MASTER_SPEC.md` and the questions, then compare its answers with the expected facts. Deterministic evals prove the spec is *complete*; the LLM eval shows whether it is *clear*.

## 6v. Post-publish performance analytics and value reconciliation

Page: [analytics.html](analytics.html) (menu 📈 Analytics, group Review), built by `python3 -I scripts/build_analytics.py` from `assets/publish.json` and `assets/okr.json`.

- **Live published post links:**
  - ▶️ **YouTube:** https://youtu.be/fnKeTQYBHN8 (direct Studio analytics: `https://studio.youtube.com/video/fnKeTQYBHN8/analytics`)
  - 💼 **LinkedIn:** https://lnkd.in/p/eZreMED5
  - ✖️ **X:** https://x.com/rifaterdemsahin/status/2120640398091804833 (direct post analytics: `https://x.com/i/status/2120640398091804833/analytics`)
  - 🚀 **Community:** https://www.skool.com/delivery-pilot-8938
- **Review horizons:**
  - **Day 2 (48h velocity):** early click-through rate (CTR), thumbnail/title appeal, initial subscriber notification reach.
  - **Day 14 (mid-tail):** browse and suggested video recommendation velocity, audience retention drop-off check, community link clicks (KR target: 30+).
  - **Day 28 (maturity):** search indexing, final OKR evaluation (KR target: 40%+ retention, 10+ helpful comments, 5+ community joins), and value-recognition score reconciliation.
- **Interactive scorecard:** auto-saves in browser `localStorage`, with "📋 Copy Analytics Report" for rapid status reporting, JSON export, and actuals reconciliation against the pre-production value score.

## 6w. AI-assisted curiosity thumbnail generation (fal.ai / FLUX / subagents)

A video's click-through rate (CTR) is heavily determined by thumbnail curiosity and visual clarity at small sizes. Remotion renders a clean, programmatic title card (`cd remotion && npm run still` -> `assets/thumbnail_card.jpg`), but competitive YouTube and social platform feeds demand a high-contrast **curiosity gap** image that visually poses an unanswered question or mystery.

- **Tooling & architecture:**
  - Script: `python3 scripts/generate_thumbnail.py [--prompt "..."] [--model fal-ai/flux/schnell] [--out assets/thumbnail_fal.jpg]`
  - Authentication: fal.ai API key fetched from `FAL_KEY` environment variable, or retrieved from Azure Key Vault (`dp-kv-deliverypilot` secret `FAL-AI-KEY`).
  - Fallback / Agentic generation: when direct external API access is blocked or credentials expire, the system uses built-in AI image generation subagents (`image-generator`), upscaling to 1920×1080 (16:9) via `ffmpeg -vf "scale=1920:1080:flags=lanczos" -q:v 2`.
- **Abstract Curiosity Thumbnail Formula (Modular Framework):**
  > **[Media Format & Style]:** High-converting YouTube thumbnail, [Aesthetic Style] aesthetic, 16:9 aspect ratio.
  >
  > **[Left Side - Subject & Emotion]:** [Subject/Persona] displaying [Emotion: e.g., confusion, shock, frustration] while interacting with [Hardware/Device], accompanied by [Symbolic Element: e.g., glowing question mark, exclamation point].
  >
  > **[Right Side - The Problem/Object]:** Enlarged 3D floating [UI / Product / Software Interface] highlighting a set of [Available/Working Features] contrasted against a [Missing/Broken Feature: depicted with placeholder outline, lock, or error symbol].
  >
  > **[Top/Overlay - Typography]:** Bold, high-contrast, glowing hook text reading "[BRAND/SUBJECT] [CORE CONFLICT/QUESTION]?!".
  >
  > **[Lighting & Atmosphere]:** Dramatic studio rim lighting, [Accent Effects: e.g., embers, sparks, glow], and warm background ambience.

- **Formula Instantiation & Application:**
  - **Subject & Context:** Authentic dark-mode product UI interface with clearly categorized panels or cards.
  - **The Missing Piece / Anomaly:** An empty, glowing dashed slot or missing feature examined by an illuminated magnifying glass or glowing neon inspection beam.
  - **Color Palette & Contrast:** Deep sleek charcoal/midnight navy (#0e0e17) background contrasted with vivid amber / warm bronze neon accents (#f59e0b) to create depth and focus.
  - **Clarity at small scale:** Bold geometric silhouettes, high contrast, zero tiny illegible micro-text, 16:9 ratio (1920×1080).
- **Dual thumbnail assets on Publish page:**
  - `assets/thumbnail_fal.jpg`: High-CTR AI curiosity thumbnail designed for public browse feeds and discovery.
  - `assets/thumbnail_card.jpg`: Clean Remotion typography title card still for documentation and formal previews.
  - `assets/thumbnail.jpg`: The active default thumbnail deployed with exports and metadata bundles.

## 7. Website (GitHub Pages)

| Page | File | Built by | Purpose |
|---|---|---|---|
| Menu groups | `nav.js` `GROUPS` | by hand | **🧭 Start** (Architecture, Environment, Time & order, Pipeline, Evals, Master spec) · **🎬 Make** (Project, Pre-prod with OKRs, Prod, Post-prod, Run & links, Publish) · **🔎 Review** (Player, Artifacts, Script, EDL, Changelog, YouTube metadata, Analytics) · **🔗 Links** (Remotion Studio, README, community, Azure portal links from `project.json › links`, and the platform post links once shared). Put a new page in the group that matches what the reader is doing; every item keeps its emoji |
| Project hub | `index.html` | by hand | links to the stage pages |
| Pre / Prod / Post | `preprod.html`, `prod.html`, `postprod.html` | by hand | one page per stage with a status table |
| Run & links | `run.html` | by hand | Studio and player links, run commands, troubleshooting |
| Player | `player.html` | by hand | plays `long.mp4` if hosted, otherwise a local file picker (never committed); subtitle track from `subs.js`; **timestamped feedback box** (Insert current time, Copy) whose text the owner pastes back to Claude |
| Metadata | `metadata.html` | `build_site.py` | title, description, tags with copy buttons |
| Master spec | `spec.html` | `build_site.py` | this file, rendered |
| Menu + notes | `nav.js` | by hand | shared menu (`LINKS`), emoji on every item, 📝 notes panel |

Re-run `python3 -I scripts/build_site.py` after editing any `.md`, and commit the generated `.html`. Markdown is embedded as JSON and rendered in the browser with `marked` (cdnjs, pinned 12.0.2), with a plain-text fallback offline. Preview locally with `open -a "Google Chrome" file:///<repo>/index.html`.

Deploy from the feature branch (main untouched):
```bash
git add -A && git commit -m "…" && git push -u origin <branch>
gh api -X POST repos/<user>/<repo>/pages -f "source[branch]=<branch>" -f "source[path]=/"   # once
gh api repos/<user>/<repo>/pages -q '.status+" "+.html_url'
```
Everything committed becomes public (repo must be public for free Pages). Keep each file < 100 MB.

---

## 7a. Publish: GitHub Pages (do this for every project, do not forget)

1. `scripts/build_all.sh` (builds every page and checks them; section 7c), check no private data or media is staged: `git add -n . | grep -Ei "\.(mp4|wav|zip)$|ocr_|REPORT.md"` must print nothing.
2. **Trunk-based development & merge to `main`:** Follow trunk-based development. Work converges immediately into `main`. If working on a short-lived branch (`<slug>-v1`), commit after each change: `git add -A && git commit -m "…" && git push -u origin <branch>`, then immediately **merge to `main`** ("remember to merge always"): `git checkout main && git pull && git merge --no-ff <branch> && git push origin main`. Keep both `main` and the branch in parity, with `main` being the definitive source of truth for deployment.
3. **Enable GitHub Pages** (once per repo; the repo must be public or on a paid plan; everything committed becomes public):
```bash
gh api -X POST repos/<user>/<repo>/pages -f "source[branch]=<branch>" -f "source[path]=/"
gh api repos/<user>/<repo>/pages -q '.status+" "+.html_url'          # built? -> https://<user>.github.io/<repo>/
until [ "$(curl -s -o /dev/null -w '%{http_code}' https://<user>.github.io/<repo>/)" = 200 ]; do sleep 10; done
```
   Keep an empty `.nojekyll` at the repo root so Pages serves the files as they are. Later pushes to the branch redeploy automatically (about 1 minute; add `?x=$RANDOM` to bypass the cache when checking).
4. **Put the live link at the top of `README.md`** (first line): `> 🌐 **Live site (GitHub Pages):** https://<user>.github.io/<repo>/ · [Architecture](…/architecture.html) · [Player](…/player.html) · [Master spec](…/spec.html)`. Commit and push again.
5. Open it in Chrome (`open -a "Google Chrome" https://<user>.github.io/<repo>/`) and click through the menu. The hosted player has no video (media is never committed): it shows the file-picker warning. To share the video itself, upload to YouTube (unlisted first).
6. If the assistant's permission system blocks the push, the merge, the Pages call or an upload, run them yourself in the session with `! git push` and `! gh api -X POST …`, or allow them in settings.

## 7b. Always back up to Google Drive

After **every push** (and always after the merge to `main`), back up to the Drive folder "Claude Missing Features Kit" (id in Key Vault, secret `cmf-kit-drive-folder-id`):

| What | Where in the folder | How |
|---|---|---|
| kit zip (scripts, Remotion project, templates) | `claude-missing-features-kit.zip` (replaced) | `scripts/build_kit.sh`, then upload |
| `MASTER_SPEC.md`, `KIT_README.md` | same folder (replaced) | upload |
| project backup (everything tracked by git, no media) | `project-backup-latest.zip` (replaced) and `backups/project-<time>-<branch>.zip` (kept) | `git archive --format=zip HEAD` |
| latest export video (videos are not in git) | `videos/claude-missing-features-export-latest.mp4` | upload |

Ways to do it: (a) `scripts/backup_drive.sh` does all of the above with `rclone` (0 tokens; needs `az` logged in and the `gdrive-shared` remote); (b) the assistant uploads the same files through the Google Drive connector; replace in place (upload the new file, then trash the old copy) so `pull_kit.sh` always gets the newest zip. (c) Optional, off by default: `git config core.hooksPath .githooks` makes `.githooks/pre-push` run (a) in the background on every push; install it yourself, the assistant's permission system may refuse standing automation. Never put OCR output, `REPORT.md`, keys or the Drive link in the repo; the Drive backup is private to the owner, but still back up only the tracked files plus the export video.

## 7c. Build the whole website (every page, from the kit)

**One command builds the complete site, a second checks it:** `scripts/build_all.sh` then `python3 -I scripts/check_site.py` (build_all runs the check at the end). A new project gets all pages straight from the kit: `./new-video.sh "<Title>" <seconds> [slug] [community] [url] [platform]` creates the hand-written pages from `templates/` and runs `build_all.sh`; pages fill with data as each step of the flow completes. Tested from scratch in a temp folder: **every page builds, every menu item exists, every link and script resolves, a second run changes nothing** (this project: 16 pages, 15 menu items).

| Page | File | Built by | Reads |
|---|---|---|---|
| Architecture | `architecture.html` | template, diagram by `build_architecture.py` | nothing project-specific |
| Environment | `environment.html` | `build_site.py` from `ENVIRONMENT.md` | the page text |
| Master spec (with the prompt) | `spec.html` | `build_site.py` from `MASTER_SPEC.md` | the spec |
| Project hub | `index.html` | template | `project.json` title |
| Pre-prod (with OKRs, value score) | `preprod.html` | template + `build_okr.py` | `assets/okr.json`, `assets/metrics.json` |
| Prod | `prod.html` | template (edit by hand) | |
| Post-prod | `postprod.html` | template (edit by hand) | `subtitles.srt/.vtt` |
| Run & links | `run.html` | template | |
| Time and order | `timeline.html` | `build_timeline.py` | `assets/timings.json` |
| Pipeline (tldraw) | `pipeline.html` | template + `build_pipeline_diagram.py`, app in `pipeline/` | `assets/timings.json` -> `pipeline/pipeline.json` |
| Evals (spec can recreate?) | `evals.html` | `eval_spec.py --page-only` | `assets/evals.json`, `evals/spec_questions.json` |
| Publish (YouTube, LinkedIn, X) | `publish.html` | `build_publish.py` | `assets/publish.json`, `assets/exports.json`, `assets/export_checks.json`, local `publish_links.js` |
| Player | `player.html` | template | `subs.js`, `chapters.js`, `export_map.js`, `exports.js` |
| Script and subtitle issues | `script.html` | `build_script.py` (+ `check_subtitles.py`) | `subs.json`, `assets/chapters.json`, `assets/subtitle_issues.json`, `assets/whisper_words.json`, `project.json` caption rules |
| Artifacts (with notes) | `artifacts.html` | `build_artifacts.py` | `overlays.json`, `cuts.json`, `export_map.js`, frames from the latest export |
| Changelog | `changelog.html` | `build_site.py` from `CHANGELOG.md`, which `build_changelog.py` generates | `assets/changelog.json`, `exports.json`, decisions, git |
| Shorts recipe (legacy) | `shortsflow.html` | `build_site.py` from `docs/SHORTS_FLOW.md` | |
| EDL | `edl.html` | `build_site.py` from `EDL.md`, which `build_edl.py` generates | `overlays.json`, `cuts.json`, `assets/edl_decisions.json`, `assets/exports.json` |
| YouTube metadata | `metadata.html` | `build_site.py` from `metadata.md` | `metadata.md`, chapters |
| Analytics and post-publish OKRs | `analytics.html` | `build_analytics.py` | `assets/publish.json`, `assets/okr.json` |
| README (navigation hub) | `readme.html` | `build_site.py` from `README.md`, which `build_readme.py` generates | `project.json`, the spec, exports, score |

Support files every page loads: `project.js` (from `project.json`), `nav.js` (menu and notes panel), and for the player `subs.js`, `chapters.js`, `export_map.js`, `exports.js` (all generated).

**Build order** (what `build_all.sh` does; each stage is skipped when its input does not exist yet): create missing hand-written pages from `templates/` -> `build_subs.py` (captions, `export_map.js`) -> `build_chapters.py` -> `build_edl.py` -> `check_subtitles.py` -> `build_script.py` -> `build_okr.py` -> `build_architecture.py` -> `build_artifacts.py` (works without an export: cards without pictures) -> `build_timeline.py` -> `build_pipeline_diagram.py` -> `build_publish.py` -> `build_analytics.py` -> `build_changelog.py` -> `build_toc.py` -> `build_readme.py` -> `build_site.py` (markdown pages and `project.js`, last, after their sources are final) -> `check_site.py`.

**Menu:** `nav.js` `GROUPS` (Start, Make, Review, Links). The menu is **collapsible**: the ▾ Menu button folds it to the brand bar and the choice is remembered in the browser.

**Adding a page (rule):** hand-written page = a template in `kit/templates/` (use `{{TITLE}}`, load `project.js` then `nav.js`); document page = a `.md` file added to `MD` in `build_site.py`; then add it to `nav.js` `GROUPS`, add it to the table above, add the generator to `build_all.sh`, and make `check_site.py` pass in a kit-from-scratch test. A page that needs data from a render must still build without it.

- **Document stats at bottom of spec:** `spec.html` (generated by `build_site.py` from `MASTER_SPEC.md`) features a live document statistics banner at the bottom with total line count, word count, character count, section count (`h2` sections and total headings), and estimated reading duration.

## 8. Sanity check (before publishing)

- [ ] Hook in the first 10 s says what the video is about
- [ ] Voice and picture in sync at start, at each clip join, at the end (lag < 1 frame)
- [ ] Loudness about -14 LUFS, true peak <= -1.5 dBFS
- [ ] Contact sheet read: nothing clipped, no private data on screen (names, chats, paths, tokens)
- [ ] Title/description claims match what is on screen; no income or result promises
- [ ] Chapters spot-checked against the video; first is `0:00`
- [ ] Product names corrected in captions and copy
- [ ] Thumbnail 1920x1080 readable at 160 px wide
- [ ] First and last 3 s checked for recorder UI (OBS) and covered; cuts proven with a still
- [ ] Subtitles proof-read; `.srt` matches the final timeline (cuts applied); chapters re-timed after cuts
- [ ] No secrets in the repo (`grep -rI "fal_sk_\|sk-"`); no media files tracked (`git ls-files | grep -E "mp4|wav"`)

---

## 9. Delivery checklist

- [ ] `~/Downloads/<slug>-1080p.mp4` rendered and verified
- [ ] `metadata.md` written and copied to `~/Downloads`
- [ ] Remotion project typechecks (`npx tsc --noEmit`), a test still renders (no error output) and Studio opens
- [ ] Site built, committed, pushed, **merged to `main`**, **GitHub Pages enabled** (section 7a), live link at the top of `README.md`, opened in Chrome
- [ ] **Whole site builds and checks** (`scripts/build_all.sh`, 7c); **evals pass** (`python3 scripts/eval_spec.py`, 6u)
- [ ] **Reuse check passed** (`scripts/check_reuse.sh`) and the kit tested from scratch; OKRs measured and scored (6j); Artifacts page rebuilt (6k)
- [ ] **Backed up to Google Drive** (section 7b); every `scripts/*.py` compiles (`for f in scripts/*.py; do python3 -m py_compile $f; done`) and `zsh -n scripts/*.sh`
- [ ] Follow trunk-based development: merge all work into `main` ("remember to merge always"), keep branches in parity, never commit media
- [ ] Show every file as a clickable URL; use emojis in summaries

---

## 10. Lessons learned (this project)

| Problem | Fix |
|---|---|
| Retina recording is not 16:9 | Scale to full height, blurred fill on the sides; no cropping of menu bar/dock. |
| No numpy for sync | Throwaway venv in the scratchpad. |
| Whisper heard "Claude" as "cloud" | Fix in all copy; give a vocabulary prompt on the next run. |
| Voice shorter than the last clip | Trim video to the voice (`-shortest`). |
| Private content in the first minute of a screen recording | Review the contact sheet and trim/blur before upload. |
| Video must not go to git | `.gitignore` `*.mp4`/`*.wav`, symlinks in `remotion/public/`. |
| Working directory moved into `remotion/` | Use absolute paths in commands. |
| Remotion render 404 on `base.mp4` | The bundler does not follow a symlink to another folder. Use a **hard link** (`ln`, same disk, no extra space) in `remotion/public/`. |
| `interpolate` threw "inputRange must be strictly monotonically increasing" | A volume fade with 0-frame edges made `[0,0,n,n]`. Use a `fade()` helper that only adds the edges that touch a cut. |
| Animated captions: words touched | The active-word scale ate the 14 px gap. Gap 26 px, scale 1.07. |
| Whole transcript flagged as repeats | 3-word runs match everywhere ("be able to"). Use 4-word runs from a different cue. |
| **A scaffold test run from the repo root overwrote real pages** (`new-video.sh` used relative paths) | Scaffold scripts must `cd` to their own folder, check `templates/` exists and refuse in a git folder with uncommitted changes. **Only ever test them in a temp dir** (`T=$(mktemp -d); unzip kit.zip -d $T; (cd /tmp && $T/new-video.sh ...)`), then confirm `git status` shows nothing new. Recovery was `git checkout -- <files>` because work was committed: commit before experimenting. |
| A note's timecode pointed into a sentence | Cut at the nearest sentence boundary and record why; never chop words. |
| A note named a file that was not in Downloads | Two recent files were byte-identical (`shasum`); asked which one instead of guessing. |
| The assistant could not copy a storage key into Key Vault (permission system: secret-store write); a login identity could create the container but not write blobs (no data role) | The owner ran `! scripts/setup_azure_exports.sh` once; the upload script then read the vault and worked. `--login` (no key) needs the Storage Blob Data Contributor role on the account. Never grant yourself roles or move keys without the owner. |
| Subtitles had stutters, flicker and garbled readings of on-screen text | `check_subtitles.py` (Whisper probabilities) found them; fixed from the screen text and by clean-up rules; four doubtful spots listed for the owner (section 6n). |
| A chapter inside a cut jumped to the end | `build_chapters.py` returned the video total for times before a segment; now it returns the next kept moment. |
| Render slowed to 8.7 fps after adding the cleaned audio | The remux left `moov` at the end of the file. Use `-movflags +faststart`. |
| Owner timecodes are on the export timeline | Convert to source time first (add the time saved by speed-ups); EDL shows both. |
| Owner asked to "cut" a 3-minute noise | Remove the noise instead (denoise), explain, keep a cut as an option. |
| The kit could not build the site by itself (a script assumed `kit/` existed; the Post-prod page linked subtitle files that did not exist yet) | Found by testing the kit from scratch with `build_all.sh` + `check_site.py`; the kit now ships empty subtitle files and the scripts guard optional folders. |
| Hard-coded project names crept into scripts and templates | `scripts/check_reuse.sh` scans reusable code for this video's words (from `project.json`) and fails; run it after every change. All such facts moved into `project.json`. |
| `build_kit.sh kit-dist/x.zip` (relative path) wrote the zip into a temp folder and left the old zip | The script cds before zipping; resolve the output path to absolute first (fixed). After building, check the file's timestamp. |
| HTML player showed no video | `long.mp4` was never in git (404, media error 4). Hard-link the render as `long.mp4` and serve with `scripts/serve.sh` (Range support); the player now shows a status message. |
| `file://` pages can't be driven by the browser tool | Serve the folder over http://localhost:8000 for testing. |
| Many small polls and image reads inflated token use | Local scripts produce one `REPORT.md`; wait once for background jobs; verify the export by OCR (`verify_export.py`), not by viewing. |
| Remotion ETA said 2 h, real time 25 min | The first ETA is meaningless. Measure frames per 30 s (about 13 fps here). |
| OCR could not read the tiny sidebar inside a pasted screenshot | Anchor a box to a line OCR can read (the sentence below the image) plus a fixed box for the first seconds. |
| Per-frame OCR union boxes jittered and hid nav items | Use two fixed canonical sidebar boxes chosen by layout. |
| Blurring the keyword "IBM" hid the planner canvas the speaker talks about | Keep keyword lists to what is private; check stills for words said aloud. |
| Recording opened on the OBS window | Intro card over 0-2.3 s instead of cutting the first spoken words. |
| Feature missing on screen | Title says so; do not promise the feature. |

---

## 11. Start prompt for a new Claude session (short form; the full prompt is at the top of this file)

> Use MASTER_SPEC.md (v3) in this repo. Brief: title `…`; source folder `~/Downloads/<name>/`; CTA `…`. Sync the clips to the voice, render a 1920x1080 base video, transcribe, write title/description/chapters, set up Remotion and open Studio, build the site and open it in Chrome. Work on a branch, commit and push, never commit the media files. Show every file as a clickable URL and use emojis.
