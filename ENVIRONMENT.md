---
published: false
---
# Environment: what must be there

Run `scripts/check_env.sh` first. It prints ✅ / ❌ for everything below and the install command for anything missing (exit code 1 if a required item is missing). **No API keys or paid services are needed** for the video itself ($0); everything runs on the MacBook.

## 1. Machine used here (measured)

| Item | Value |
|---|---|
| Computer | MacBook Pro, Apple silicon, 10 cores, 64 GB RAM, macOS |
| Free disk | at least 20 GB (this project: inputs 700 MB, base 105 MB, cleaned base 105 MB, export 150 MB, Whisper model `small` 461 MB (the cache folder can hold several models, 3.6 GB here), `remotion/node_modules` ~200 MB, plus temporary frames and the Remotion bundle copy) |
| Ports | 3000 (Remotion Studio), 8000 (site and player) |
| Accounts | none for the video. Optional: GitHub (`gh`), Azure (`az`, Key Vault), Google Drive (`rclone`) for the kit and Pages |

## 2. Installs

| Tool | Version used | Why it is needed | Install | Used by |
|---|---|---|---|---|
| **ffmpeg + ffprobe** | 9.0.2 | extract audio, sync, 1080p base render, frames for OCR, audio mux | `brew install ffmpeg` | `build_base.py`, `ocr_all.sh`, `denoise_audio.py`, spec checks |
| **python3** | 3.15.2 | all scripts | `brew install python` | everything in `scripts/` |
| **node + npm** | 26.10.0 / 11.19.1 | Remotion, local web server | `brew install node` | `remotion/`, `scripts/serve.sh` |
| **git** (+ Xcode command line tools) | 2.56.1 | version control; also provides `swiftc` | `xcode-select --install` | commits, `ocr_frames.swift` |
| **swiftc** (Apple Swift) | 6.x (Xcode CLT) | compiles the Apple Vision OCR tool (text and positions of the screen, local) | `xcode-select --install` | `scripts/ocr_all.sh` -> `~/.cache/cmf-ocr` |
| **openai-whisper** | pip package | transcript with word timestamps (subtitles, chapters, repeat finder) | `pip install openai-whisper` (or `pipx install openai-whisper`) | `scripts/pipeline.sh` |
| **Whisper model `small`** | 461 MB | downloads on first run to `~/.cache/whisper/small.pt` | automatic | Whisper |
| **Google Chrome** | any recent | Remotion renders with it (`remotion.config.ts` points to it; the bundled headless shell fails on this Mac) | `brew install --cask google-chrome` | `npm run studio`, `npm run render` |
| **Python packages** | numpy, scipy, noisereduce, soundfile | sync by cross-correlation, noise removal | **automatic**: created in `~/.cache/cmf-venv` on first run | `build_base.py`, `denoise_audio.py` |
| **npm packages** (in `remotion/`) | remotion + @remotion/cli 4.0.250, react + react-dom 18.3.1, typescript 5.6.3, @types/react 18.3.12 | the video project | `cd remotion && npm install` | Studio, render, typecheck |
| **http-server** | 14.1.1 | serves the site and player with video seeking (Range) | automatic via `npx` | `scripts/serve.sh` |
| Optional: **gh**, **az** (also `az storage`), **rclone** | current | GitHub Pages, Azure Key Vault (Drive folder id), Google Drive kit pull and `scripts/backup_drive.sh` (always back up) | `brew install gh azure-cli rclone`, then `gh auth login`, `az login`, `rclone config` (remote name `gdrive-shared`) | `pull_kit.sh`, Pages step |

## 3. Files that must exist before processing

| What | Where | Rule |
|---|---|---|
| Screen recordings | one folder, e.g. `~/Downloads/<Project>/` | `*.mp4`, any resolution (here 3456x2234 @ 60 fps), sorted by name = recording order; each has its own scratch audio (used only to find the offset) |
| Clean voice recording | the same folder | exactly one `*.WAV` (Zoom recorder) covering all clips |
| Project folder | `~/projects/<project>/` | from the kit (`pull_kit.sh`, then `new-video.sh`) |
| Base video link | `remotion/public/base.mp4` | a **hard link** to the base video (`ln`), never a symlink (Remotion's bundler cannot follow it) |
| Player links | repo root `long.mp4`, `export.mp4` | created by `scripts/serve.sh`; git-ignored |

## 4. Processing files: what each step reads and writes

| Step | Reads | Script | Writes | Committed? |
|---|---|---|---|---|
| Audio sync | scratch audio from clips, clean WAV | `sync_clips.py` | cross-correlation offsets and confidence | no |
| Source backup | raw footage, source artifacts | `upload_source.py` | Azure Blob: `<slug>-source` (raw/, artifacts/) | cloud private |
| Sync + base video | clips, WAV | `build_base.py`, `render_base.sh` | `~/Downloads/<slug>-1080p.mp4`, `assets/base_info.json`, `DURATION` in `theme.ts` | no (video) |
| Transcript | base audio | Whisper (`pipeline.sh`) | `assets/whisper_words.json`, `assets/whisper_raw.json`, `assets/whisper_offset.txt` | words yes; raw optional |
| Subtitles | transcript, `overlays.json`, `cuts.json` | `build_subs.py` | `subtitles.srt/.vtt`, `remotion/src/subs.json`, `subs.js`, `export_map.js` | yes |
| Subtitle check | transcript, fixes | `check_subtitles.py` | `assets/subtitle_issues.json`, `assets/subtitle_report.json` | yes |
| Screen text | base video | `ocr_all.sh` + `ocr_frames.swift` | `assets/ocr_frames.json` | **no: contains the private text** |
| Cut candidates | subs | `find_repeats.py` | `assets/repeats.txt` | optional |
| Personal windows | OCR, subs | `find_personal_windows.py` | `assets/personal_windows.json` | **no** |
| Report | the above | `report.py` | `REPORT.md` | **no** |
| Blur boxes | OCR, slides | `build_blurs.py` | `overlays.json` (`blurs`) | yes |
| Noise removal | base video | `denoise_audio.py` | `~/Downloads/<slug>-1080p-clean.mp4` | no (video) |
| Export | base video, `overlays.json`, `cuts.json`, `subs.json` | `scripts/render_export.sh` | `exports/<slug>-<platform>-vN.mp4`, `remotion/out/long.mp4` (latest), `assets/exports.json`, `exports.js` | media no; registry yes |
| Privacy check | export | `verify_export.py` | `assets/export_leaks.json` | **no** |
| Score and OKRs | export, metrics | `measure_video.py`, `build_okr.py` | `assets/metrics.json`, `assets/okr_result.json`, OKR block in `preprod.html` | yes |
| Evals | spec, kit, questions | `eval_spec.py` | `assets/evals.json`, `evals.html` | yes |
| EDL | decisions, overlays | `build_edl.py` | `EDL.md` | yes |
| Site | `*.md` | `build_site.py` | `spec.html`, `edl.html`, `environment.html`, `metadata.html`, `readme.html` | yes |

## 5. Code in the project (what runs)

| Path | Role |
|---|---|
| `scripts/pipeline.sh` | one command: sync, base video, subtitles, OCR, repeats, personal windows, REPORT.md |
| `scripts/build_base.py` | N clips + WAV -> synced 1080p30 base, offsets and confidence |
| `scripts/ocr_frames.swift`, `ocr_all.sh` | Apple Vision OCR every 2 s |
| `scripts/build_subs.py`, `build_blurs.py`, `find_repeats.py`, `find_personal_windows.py`, `report.py` | analysis and edit data |
| `scripts/denoise_audio.py` | remove steady noise (hoover, fan) with `noisereduce`; `--scan` finds where it starts |
| `scripts/build_chapters.py` | chapters on the source and export timelines (`assets/chapters.json`) -> `chapters.js`, `metadata.md` |
| `scripts/check_env.sh` | verifies this whole page on the machine |
| `scripts/build_publish.py` | the Publish page (YouTube, LinkedIn, X) from `assets/publish.json` and the export registry |
| `scripts/setup_azure_exports.sh`, `upload_exports.py` | one-time private Azure container + Key Vault secrets (run by the owner), then upload of the exports and read-only links (local, git-ignored) |
| `scripts/upload_source.py` | save raw footage and source artifacts to per-video Azure Storage container (`<slug>-source`) |
| `remotion/src/variants.json` | per-platform cuts (keep ranges, shorter ending) |
| `scripts/check_subtitles.py`, `build_script.py` | find caption problems from data and build the Script page with the subtitle issues and fixes |
| `scripts/build_changelog.py`, `build_toc.py`, `build_readme.py` | the Changelog, the contents table in the spec, and the navigational README |
| `scripts/build_pipeline_diagram.py`, `pipeline/` | the tldraw pipeline page: data from `timings.json`; app built with `npm install && npm run build` in `pipeline/` (needs node; `node_modules` not committed) |
| `scripts/eval_spec.py`, `evals/spec_questions.json` | the evals that test whether the spec and kit can recreate the project, and the Evals page |
| `scripts/build_all.sh`, `check_site.py` | build every page of the site in order, then check menu items, links and scripts |
| `scripts/render_export.sh`, `register_export.py` | numbered exports (`exports/<slug>-<platform>-vN.mp4`) and their registry `assets/exports.json` |
| `scripts/check_reuse.sh` | fails if reusable code contains this video's words (from `project.json`) |
| `scripts/measure_video.py`, `build_okr.py` | measure the export, then write the OKR and value-recognition score into the Pre-prod page (`assets/okr.json`) |
| `scripts/build_artifacts.py` | the Artifacts page: every added element with timecodes, frames from the export, links into the player |
| `remotion/src/project.json` | the one per-video config: title, community, sensitive words, caption fixes |
| `scripts/verify_export.py` | OCR the final video for leaked text |
| `scripts/build_edl.py`, `build_site.py`, `build_architecture.py` | docs and site pages |
| `scripts/serve.sh`, `pull_kit.sh`, `build_kit.sh`, `check_env.sh`, `sync_clips.py`, `render_base.sh` | helpers, serve, kit, environment |
| `remotion/src/LongForm.tsx` | the video: cut-aware playback, speed-ups, overlays, captions, ending |
| `remotion/src/{Slide,Outro,ImageOverlays,Subtitles,Thumb,cuts}.ts(x)` | slides, ending, blur/intro, captions, thumbnail, timeline maths |
| `remotion/src/overlays.json`, `cuts.json` | **the edit list as data** (slides, blurs, speed-ups, outro, cuts) |
| `remotion.config.ts` | Chrome path, JPEG frames, h264, CRF 18 |
| `player.html`, `nav.js`, `*.html` | site, player (original vs export, keys), menu |

## 6. Set up from zero

```bash
brew install ffmpeg python node git gh azure-cli rclone && brew install --cask google-chrome
xcode-select --install                       # swiftc for Apple Vision OCR
pip install openai-whisper                   # or: pipx install openai-whisper
gh auth login; az login; rclone config       # only for kit, Key Vault, Pages
scripts/pull_kit.sh ~/projects/<new> && cd ~/projects/<new>
cd remotion && npm install && cd ..
scripts/check_env.sh                         # all required items must show a green tick
./new-video.sh "<Title>" <seconds> && scripts/pipeline.sh "~/Downloads/<Project>" <slug>
```

## 7. Machine time (measured, mostly unattended)

| Step | Time for 12 min of footage |
|---|---|
| Sync + 1080p base render | about 4 min (3.4x real time) |
| Whisper `small` with word timestamps (CPU) | about 4 to 5 min |
| OCR, every 2 s, 4 processes | about 4 min for 372 frames |
| Noise removal | about 1 min |
| Remotion export render (about 13 frames/s) | about 29 min for 22,920 frames. The first on-screen ETA is wrong (said hours) |
| Export OCR privacy check | about 4 min |

## 8. Environment problems and fixes

| Symptom | Fix |
|---|---|
| Render error 404 on `base.mp4` | `remotion/public/base.mp4` must be a hard link, not a symlink |
| Chrome / "spawn -88" error | keep `Config.setBrowserExecutable("/Applications/Google Chrome.app/…")` in `remotion.config.ts` |
| `swiftc` not found | `xcode-select --install`, then re-run `scripts/ocr_all.sh` |
| Whisper very slow | it runs on CPU; `small` is the balance. Run it once, it is cached in `assets/whisper_words.json` |
| Remotion render much slower than 13 frames/s | the base video's index must be at the front: `ffmpeg -i in.mp4 -c copy -movflags +faststart out.mp4` (`denoise_audio.py` does this) |
| Port 3000 or 8000 busy | `lsof -ti :3000 \| xargs kill` |
| Nothing at the Pages link | enable Pages (`MASTER_SPEC.md` section 7a) |
