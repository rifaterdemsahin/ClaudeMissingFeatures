# MASTER SPEC v3.2: long-form 1080p screen-recording video (YouTube)

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

## 1. Pipeline

```
screen clips (.mp4, own audio) ─┐
voice recording (.WAV)          ├─► sync (cross-correlation) ─► offsets
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
- Do not cut the opening if the voice already speaks: cover it. `overlays.json` -> `intro_card` shows the `Thumb` design over `0 to 2.3 s`, fading out over 0.3 s.
- `overlays.json` -> `images: [{from,to,src}]` shows an image full-frame (files in `remotion/public/img/`, not committed) on source time, with 0.2 s fades. Use it wherever private or distracting screen content must be replaced.
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

## 7. Website (GitHub Pages)

| Page | File | Built by | Purpose |
|---|---|---|---|
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
- [ ] Site built and opened in Chrome (`open -a "Google Chrome" <url>`)
- [ ] Work on a branch (`<slug>-v1`), commit and push after each change, never commit media
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
| HTML player showed no video | `long.mp4` was never in git (404, media error 4). Hard-link the render as `long.mp4` and serve with `scripts/serve.sh` (Range support); the player now shows a status message. |
| `file://` pages can't be driven by the browser tool | Serve the folder over http://localhost:8000 for testing. |
| Recording opened on the OBS window | Intro card over 0-2.3 s instead of cutting the first spoken words. |
| Feature missing on screen | Title says so; do not promise the feature. |

---

## 11. Start prompt for a new Claude session

> Use MASTER_SPEC.md (v3) in this repo. Brief: title `…`; source folder `~/Downloads/<name>/`; CTA `…`. Sync the clips to the voice, render a 1920x1080 base video, transcribe, write title/description/chapters, set up Remotion and open Studio, build the site and open it in Chrome. Work on a branch, commit and push, never commit the media files. Show every file as a clickable URL and use emojis.
