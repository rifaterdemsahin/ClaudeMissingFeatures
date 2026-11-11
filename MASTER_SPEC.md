# MASTER SPEC v3: long-form 1080p screen-recording video (YouTube)

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

## 7. Website (GitHub Pages)

| Page | File | Built by | Purpose |
|---|---|---|---|
| Project | `index.html` | by hand | pre-prod, prod, post-prod status |
| Player | `player.html` | by hand | plays `long.mp4` if hosted, otherwise a local file picker (the video is never committed) |
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
- [ ] No secrets in the repo (`grep -rI "fal_sk_\|sk-"`); no media files tracked (`git ls-files | grep -E "mp4|wav"`)

---

## 9. Delivery checklist

- [ ] `~/Downloads/<slug>-1080p.mp4` rendered and verified
- [ ] `metadata.md` written and copied to `~/Downloads`
- [ ] Remotion project typechecks (`npx tsc --noEmit`) and Studio opens
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
| Feature missing on screen | Title says so; do not promise the feature. |

---

## 11. Start prompt for a new Claude session

> Use MASTER_SPEC.md (v3) in this repo. Brief: title `…`; source folder `~/Downloads/<name>/`; CTA `…`. Sync the clips to the voice, render a 1920x1080 base video, transcribe, write title/description/chapters, set up Remotion and open Studio, build the site and open it in Chrome. Work on a branch, commit and push, never commit the media files. Show every file as a clickable URL and use emojis.
