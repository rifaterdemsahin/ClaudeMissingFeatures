# ClaudeMissingFeatures



A repeatable recipe for turning a source clip or idea into a finished YouTube Short: script, realistic visuals, voice, music, SFX, thumbnail, metadata and a cost report. Built and proven on "You're the Pilot" (this repo). Copy this file to a new project, fill in section 0, and follow the stages in order.

> 🔒 Secrets rule: the fal key lives in an env var for one command at a time. Never write it to a file, a commit or a chat log. If a key was pasted into a chat, rotate it.

---

## 0. 📝 Brief (fill in per video)

| Field | Value |
|---|---|
| Working title | |
| Source clip URL (optional) | |
| The claim we answer | one sentence |
| Our reply (the reverse response) | one sentence |
| Core metaphor (what the tool is to us) | e.g. horse → car → pilots of bots. One image per beat. |
| Hook (≤ 12 words, true open loop) | |
| Payoff (formula / result) | e.g. 3 audit questions |
| Tone limits | e.g. about delivery of value, **not war**; no weapons or military look |
| CTA: community name | e.g. "Delivery Pilot" (say it aloud **and** show it) |
| CTA: platform + brand asset | e.g. Skool + `skool.png` |
| CTA URL | `<URL>` placeholder until supplied |
| Target length | ≤ 40 s (hard limit 60 s). Real length is set by the voice. |
| Format | 9:16, 1080×1920, 30 fps. **Thumbnail is also 1080×1920.** |
| Voice | model + voice id |
| Visual style | photoreal / cinematic, no on-image text |
| On-screen extras | progress bar (yes/no), act labels (**no**) |
| Budget cap | e.g. ≤ $0.25 |

---|---|
| Working title | |
| Source clip URL (optional) | |
| The claim we answer | one sentence |
| Our reply (the reverse response) | one sentence |
| Hook (≤ 12 words, true open loop) | |
| Payoff (formula / result) | |
| CTA target (community / link) | name + `<URL>` placeholder |
| Target length | ≤ 40 s (hard limit 60 s) |
| Format | 9:16, 1080×1920, 30 fps |
| Voice | model + voice id |
| Visual style | photoreal / cinematic, no on-image text |

---

## 1. 🧭 Pipeline at a glance

```
source clip ─► transcript (Whisper) ─► script (hook + 3 acts + CTA)
                                              │
                       storyboard.json  ◄─────┘   (single source of truth)
                         │
   ┌──────────┬──────────┼───────────┬────────────┐
 images    animation   voice      music + SFX   thumbnail bg
 (fal)     (fal, 2)    (fal)        (fal)        (fal)
   └──────────┴──────────┼───────────┴────────────┘
                         ▼
        Whisper word timestamps ─► prep_remotion.py ─► data.json
                         ▼
             mix_audio.py (duck, SFX, -14 LUFS)
                         ▼
                 Remotion render ─► short.mp4 + thumbnail.png
                         ▼
        metadata.html · costs.html · SANITY_CHECK.md · commit & push
```

---

## 2. 🗂️ Repo layout

```
README.md              source link
MASTER_SPEC.md         this file
PROPOSAL.md            the idea + script + storyboard table
storyboard.json        single source of truth (scenes, voice lines, prompts)
SANITY_CHECK.md        hook / delivery / value, unproven claims, not-verified list
index.html             project page (video, script beats, status, links)
script.html            printable script
metadata.html          YouTube title, description, tags, upload settings, thumbnail
costs.html             spend breakdown
thumbnail.png          1080×1920
skool.png (etc.)       brand assets used in the CTA
assets/{img,video,audio}   generated outputs (cached; delete a file to regenerate)
scripts/               fal.py, make_*.py, prep_remotion.py, mix_audio.py
remotion/              src/{Short,Thumb,Root,data,theme}.tsx, public/ (generated)
```

---

## 3. 📖 Script structure

Hook, then three acts, then CTA. About 95 to 110 spoken words for a 35 to 40 s Short.

| Beat | Time | Job |
|---|---|---|
| 🪝 Hook | 0:00–0:03 | Typed card on frame 0. A true curiosity trigger plus the question the Short answers. No voice. Hold about 1 s after typing. |
| 🎭 Act 1: Setup | to ~0:10 | Name the opposing view fairly in one sentence. Establish the old world. |
| ⚔️ Act 2: Confrontation | to ~0:23 | The turn: the question everyone asks is the wrong one. Name the trap. |
| ✅ Act 3: Resolution | to ~0:30 | Pay off the hook with a formula (e.g. 3 questions) and a one-line close. |
| 📣 CTA | last 5 s | One ask, no promises or income claims. Name the community. |

Rules: close the open loop; end opinions as opinions; don't invent facts; mark anything unprovable in `SANITY_CHECK.md`.

---

## 4. 🧾 `storyboard.json` schema

```jsonc
{
  "title": "…", "language": "en", "max_seconds": 40, "cta_url": "<URL>",
  "scenes": [
    { "id": 1, "act": "hook", "type": "hook_card", "text": "…", "voice": null },
    { "id": 2, "act": "1", "type": "shot", "art": "horse",
      "image_prompt": "… no text, letters, numbers, UI",
      "motion": "ken_burns | image_to_video", "voice": "…" },
    { "id": 5, "act": "2", "type": "screenshot_callout", "quote": "line|HIGHLIGHT|line", "callout": "HIGHLIGHT", "voice": "…" },
    { "id": 6, "act": "3", "type": "svg_flow", "steps": ["…","…","…"], "voice": "…" },
    { "id": 8, "act": "cta", "type": "banner", "text": "Join <Community>", "sub": "…", "image": "brand.png", "voice": "…" }
  ]
}
```

Times are **not** hand-written. `prep_remotion.py` sets each voiced scene's start from its first word's timestamp (hook owns the first 3 s), then writes `remotion/public/data.json` including per-word timings for subtitles.

---

## 5. 🤖 fal.ai models and prices (checked 2026-11-10)

Price check: `GET https://api.fal.ai/v1/models/pricing?endpoint_id=<id>` with header `Authorization: Key $FAL_KEY`.

| Job | Endpoint | Unit price | Notes |
|---|---|---|---|
| Images | `fal-ai/flux/schnell` | $0.003 / MP | 4 steps, 768×1344 for 9:16 (shots and thumbnail). Always add "no text, letters, numbers, UI". |
| Animation | `fal-ai/ltx-video-13b-distilled/image-to-video` | $0.04 / unit | Pass `aspect_ratio: "9:16"`, `resolution: "480p"`. ⚠️ `fal-ai/ltx-video/image-to-video` ignores portrait and returns a stretched 768×512 clip. |
| Voice | `fal-ai/kokoro/american-english` | $0.02 / 1000 chars | Voice `am_michael`. Clean after: highpass 80, atempo 1.12, loudnorm. |
| Music | `cassetteai/music-generator` | $0.02 / min | One 36 s bed, loops and ducks. |
| SFX | `cassetteai/sound-effects-generator` | $0.01 / generation | Whoosh (2 s), click (1 s). |

Client: `scripts/fal.py` (queue API: POST `https://queue.fal.run/<model>`, poll `status_url`, GET `response_url`). Auth header `Authorization: Key <id>:<secret>`.

Run every generation as `FAL_KEY='…' python3 -I scripts/<script>.py`. Outputs are cached by filename. Delete a file to regenerate it.

---

## 6. 🎙️ Audio spec

1. Generate voice, then `ffmpeg -af "highpass=f=80,atempo=1.12,loudnorm=I=-14:TP=-3:LRA=7" -ac 1 -ar 24000`.
2. Check it by ear and by transcript. Whisper hallucinates "Thank you." on silence. Force `--language en`.
3. Word timestamps: resample to 16 kHz mono, `whisper --model base --word_timestamps True`. **Word count must equal the script's word count**, or `prep_remotion.py` stops. The word pass can drop the last word (use patches).
4. Mix (`scripts/mix_audio.py`): voice delayed by the 3 s hook, music at 0.55 with `sidechaincompress` ducking, fade in 1.5 s and out 3 s, whoosh at each scene change (30%), clicks on the hook, `loudnorm` then `volume=1.8dB`.
5. Verify: `ffmpeg -i mix.wav -af ebur128=peak=true -f null -`. Target **-14 LUFS, true peak ≤ -3 dBFS**.

---

## 7. 🎨 Visual spec

- Realistic shots: 3 images, animate **at most 2** hero shots. Others use a slow zoom (Ken Burns). Freeze the last frame if a clip is shorter than its scene.
- One image per metaphor beat. Example: horse rider (past) → car windscreen (present) → pilot over a delivery-route strategy map (new tool).
- "Strategy game / command-and-conquer" look for the oversight shot: over-the-shoulder pilot in a headset, holographic map with glowing routes and friendly parcel-carrying units. Say "no weapons, no military" when the topic is delivery of value.
- Diagrams and anything with meaning: draw in Remotion SVG, never ask an image model for text.
- Brand logos and the author's real screenshots: use as given, on a white card for contrast.
- Always look at every generated image at full size. **Reject and regenerate** any with garbled text (maps and floors invent letters), bad hands or wrong aspect. Use the stronger negative: "no text, no letters, no words, no labels, no numbers, no UI" and "map shows only glowing lines and icons with no labels".
- No act labels on screen (only a small "JOIN US" chip on the CTA), word-by-word subtitles (3 words at a time, 76 px, bottom third), progress bar (16 px, bottom edge).
- Palette and fonts live in `remotion/src/theme.ts`.
- This Mac's ffmpeg has no libass or freetype, so use Remotion for all text. Do not use `subtitles` or `drawtext`.

---

## 8. 🖼️ Thumbnail spec

- 1080×1920 vertical Remotion still (`Thumb` composition), matching the Short. Photoreal 768×1344 background from flux/schnell with a dark empty upper half for text.
- Text: the claim in 2 lines (white) plus the answer (accent, largest). One small tag line. Max 6 to 8 words.
- Render: `npx remotion still src/index.ts Thumb out/thumbnail.png`, copy to repo root.
- Layout: claim at the top third, answer largest, tag line about 230 px above the bottom (clear of the Shorts UI).
- Check: nothing overlaps, readable at 160 px wide, no real person's face.

---

## 9. 📺 YouTube metadata spec (`metadata.html`)

- **Title** ≤ 100 chars, claim plus answer, `#Shorts` at the end. Keep 2 alternates.
- **Description:** hook line, 2 to 3 sentence reframe, the formula as a list, CTA with community name and `<URL>`, honesty line (opinion, AI-generated media), 3 to 5 hashtags.
- **Tags** ≤ 500 chars total.
- **Upload settings:** Not made for kids. **Altered or synthetic content = Yes** when voice or visuals are realistic AI. Pinned comment with the CTA.
- Copy buttons and character counters on the page.

---

## 10. 💰 Cost spec (`costs.html`)

Report: total spent including mistakes, cost to rebuild cleanly, line items (endpoint, unit price, what ran, cost, note), what is free (Whisper, ffmpeg, Remotion), and where the money went. Say clearly these are estimates from the pricing API, not an invoice, and link the fal dashboard.

Reference (this project): about $0.19 spent, about $0.14 clean rebuild. Biggest line is animation.

Cost rules: animate ≤ 2 shots; test a new model on 1 image first; lock the script and CTA before generating the voice; reuse the music bed; keep a shared SFX folder.

---

## 11. 🧪 Sanity check (before publishing)

Fill in `SANITY_CHECK.md`:

- [ ] **Hook:** curiosity trigger on frame 0, ≤ 12 words, typed and held about 1 s, about 3 s before the first spoken word
- [ ] **Delivery:** voice listened to by a human; transcript matches script
- [ ] **Value:** reframe lands; payoff delivered; one CTA
- [ ] **Length:** measured, under the limit
- [ ] **Loudness:** -14 LUFS, TP ≤ -3
- [ ] **Unproven claims:** listed and framed as opinion
- [ ] **Not verified:** listed (reuse rights of source footage, speaker identity, etc.)
- [ ] `<URL>` placeholders replaced
- [ ] No secrets in the repo (`grep -rI "fal_sk_"`)

---

## 12. 🧠 Lessons learned (don't repeat)

| Problem | Fix |
|---|---|
| Cheap i2v model returned a stretched 768×512 clip | Use the 13b distilled model with `aspect_ratio: "9:16"`. Check size before the second clip. |
| Cheap fix cost more than it saved |  Swapping a shot after the render means an extra image, an extra clip and a re-render (about $0.05). Lock visuals before animating. |
| Voice ran 40 s, plan was 33 s | Set `atempo`, or retime scenes to the real word timestamps. Never hand-time scenes. |
| CTA changed after the voice was made | Lock the script first. Each voice redo costs about $0.014 and a re-timing. |
| Subtitle line overflowed the frame | Use flex-wrap in a fixed 960 px box and show 3 words. |
| `sed -i` failed on macOS | Use `sed -i ''` or edit with a script/tool. |
| Key pasted into chat | Use it as an env var only; rotate it afterwards. |
| Generated images invent text | "no text, letters, numbers, UI" and inspect every image. |
| First command-center image had letters on the floor of the map | Reject at full size, add "no labels" to the prompt, regenerate (about $0.003). |
| Download button did nothing from a `file://` page | Also copy the MP4 to `~/Downloads` directly. |
| Landscape thumbnail for a vertical Short | Make the thumbnail 1080×1920 from the start. |
| Act labels cluttered the frame | Don't show act labels; keep the structure in the script only. |
| Two bars at the bottom on Shorts | The platform draws its own progress line; keep ours thin or lift it. |

---

## 13. ▶️ Quick start for a new video

```bash
# 1. copy the repo, edit README.md (source link), PROPOSAL.md, storyboard.json
# 2. transcript of the source (optional)
yt-dlp -x --audio-format mp3 -o "video/audio.%(ext)s" "<url>" && whisper video/audio.mp3 --model base --output_dir video
# 3. generate assets (one command at a time, key as env var)
FAL_KEY='…' python3 -I scripts/make_images.py
FAL_KEY='…' python3 -I scripts/make_video.py fal-ai/ltx-video-13b-distilled/image-to-video
FAL_KEY='…' python3 -I scripts/make_audio.py
# 4. clean voice, word timestamps -> assets/audio/words_raw.json (see section 6)
# 5. build
python3 scripts/prep_remotion.py && python3 scripts/mix_audio.py
cd remotion && npm install && npm run render   # out/short.mp4
npx remotion still src/index.ts Thumb out/thumbnail.png
# 6. update metadata.html, costs.html, SANITY_CHECK.md; open index.html; commit and push
```

Preview any time with `npm run studio` and check stills: `npx remotion still src/index.ts Short out/f.png --frame=N`.

---

## 14. 📦 Delivery checklist (what the user gets)

- [ ] `remotion/out/short.mp4` rendered, and **copied to `~/Downloads/<slug>.mp4`** (browser download buttons on `file://` pages are unreliable)
- [ ] `thumbnail.png` (1080×1920) at repo root, copy in `~/Downloads`
- [ ] `index.html` has the video player plus **⬇️ Download video** and **⬇️ Thumbnail** buttons (`<a download>`)
- [ ] `script.html` (printable), `metadata.html`, `costs.html`, `SANITY_CHECK.md` updated
- [ ] `MASTER_SPEC.md` updated with anything new learned
- [ ] No secrets in the repo; `.gitignore` excludes `node_modules`, `__pycache__`, generated `remotion/public/*` (keep `short.mp4`)
- [ ] Commit with the attribution line. **Never commit to the default branch directly**: create a branch (e.g. `<slug>-v1`), push it, then offer to merge.

---

## 15. 🔁 What to change vs keep when reusing

| Keep (reusable) | Change per video |
|---|---|
| `scripts/*.py`, `remotion/src/*`, `theme.ts`, mix settings | `storyboard.json` (all text, prompts, `art` names) |
| fal endpoints, prices, audio targets | `README.md` source link, `PROPOSAL.md`, `script.html` |
| Hook + 3 acts + CTA structure | Hook, metaphor images, payoff formula, CTA name and logo |
| Thumbnail layout | Thumbnail words and background prompt |
| Costs page layout | Line items and totals |

Adding a new hero shot: add its prompt to `make_images.py` (`SHOTS`) and `make_video.py` (`HERO`), set `"art"` in the scene, and add the name to the hero check in `Short.tsx` (`s.art === "car" || s.art === "command"`).

---

## 16. 🧩 Prompt library (templates that worked)

- **Past-world shot:** "photorealistic cinematic photo, lone rider on a horse seen from behind walking across an open golden-hour field, long shadows, warm backlight, shallow depth of field, 35mm film, {NEG}"
- **Present-world shot:** "photorealistic cinematic photo, view through a car windscreen of an empty highway at dusk heading toward the horizon, hands on steering wheel in soft focus, warm orange sky, {NEG}"
- **New-tool shot:** "photorealistic cinematic photo, over the shoulder of a calm person in a dark command center looking at a huge glowing holographic strategy map, real-time-strategy command and conquer style top-down view of a city, glowing delivery routes connecting warehouses to homes, small friendly robot units carrying parcels along the routes, teal and amber light, peaceful productive atmosphere, person wearing a pilot headset seen from behind, map shows only glowing lines and icons with no labels, no weapons, no military, {NEG}"
- **Thumbnail background (9:16):** "photorealistic cinematic photo, silhouette of a person seated at the controls of a futuristic cockpit looking out at a glowing sunrise sky with small white drones in the distance, dramatic orange and teal light, dark empty sky area in the upper half for text, person in the lower half, {NEG}"
- **Animation prompts:** describe only motion: "the car drives forward smoothly, road markings flowing toward the camera, gentle camera motion, cinematic".
- `{NEG}` = "no text, no letters, no words, no labels, no numbers, no UI, no watermark"

---

## 17. 🚀 Start prompt for a new Claude session

> Use MASTER_SPEC.md in this repo. Brief: title `…`; source `…`; claim `…`; our reply `…`; metaphor `…`; hook `…`; payoff `…`; CTA community `…` on `…` with logo `…`; budget `…`. Write the script (hook + 3 acts + CTA), storyboard.json and PROPOSAL.md first and show me the script. After I approve it, generate assets, render, build the metadata and costs pages, and copy the MP4 and thumbnail to ~/Downloads. Show every file as a clickable URL and use emojis. I'll provide the fal key as an env var for each command; never write it to a file. Work on a branch.

---

## 18. 🔗 Output conventions (assistant behaviour)

When working on this project: show every file or page as a **clickable URL** (`file:///…` for local files, `https://github.com/…` after a push), and use emojis to make summaries scannable. Open local pages in Google Chrome with `open -a "Google Chrome" <url>`.

---

## 19. 🆕 Update from the "$200 LSP" Short (2026-11-11)

This spec described a fal.ai image/voice flow. The LSP Short used a different, **$0** path, now the default and packaged in [`shorts-kit/`](shorts-kit/README.md) (new generic spec: [`shorts-kit/MASTER_SPEC.md`](shorts-kit/MASTER_SPEC.md)).

| Topic | New rule |
|---|---|
| Voice source | User's own recording (Zoom WAV). **Last take is the correct take.** Transcribe with Whisper `medium` + vocabulary prompt. |
| Scene timing | `storyboard.json` `start_word` (`word#n`) → `prep_remotion.py` derives frames from word timestamps. |
| Visuals | Emoji + SVG motion graphics in Remotion (`kit.tsx` primitives), punch-zoom per cut, subtitles zone kept clear. |
| Audio | Synthesized beat + SFX (`mix_audio.py`), sidechain duck, −14 LUFS / TP ≤ −3. No API. |
| Site | One `index.html` with `#preprod`, `#prod`, `#postprod` sections + shared `nav.js` menu; separate `metadata.html`. |
| Render on macOS | `remotion.config.ts` must use installed Chrome (headless-shell spawn error −88). |
| Cost | $0.00 API spend. |

The branch rule in §14 stays: work on a branch. Project pages: [index.html](index.html) · [metadata.html](metadata.html).

---

## 20. 🆕 Update: on-camera video, logos and images (2026-11-11)

1. **Video has its own audio? Use it only to sync.** `scripts/sync_video.py cam.MP4 voice.WAV` cross-correlates the camera audio with the recording (100 Hz envelope, then confidence = peak / 50th peak, want > 3), prints `voice_time = camera_time + X`, and cuts the take's clip to `remotion/public/cam.mp4` (cropped 9:16, **no audio**). The mix uses only the clean recording. Check `ffprobe` for an audio stream before claiming a clip is silent.
2. Verify sync numerically: correlate the camera audio with `voice_clean.wav` in 5 windows; lag must be identical (< 33 ms = 1 frame). Mouth-motion correlation is too noisy (hands/beard); don't rely on it.
3. **Cut in and out** with `cams` in `storyboard.json` (`{id, from, to}` seconds on the final timeline). `CamLayer` plays `cam.mp4` at `startFrom = from - hook_seconds` so lips stay on the voice; overlay components per `id` (`CAM` map in `Short.tsx`) add banners/emoji/props. Entry = 7-frame scale-in + white flash. A-roll is zoomed `ZOOM = 1.22` about the face (`transformOrigin: 50% 42%`) + slow push-in; **re-aim any prop that sits on the face (sunglasses) after changing the zoom**. Crop the 4K frame around the face (`video.crop`; test one frame first).
4. Timed inserts use `overlays` (`{id, from, to}`): `logos` (hook), `ronaldinho` (user photos), `bank`. Align them to spoken words (`word timestamps`), not to guessed times; the user's timecodes are targets, snap to the nearest matching words.
5. User-provided images: copy to `remotion/public/img/`, show in tilted bordered cards. Frontier-lab logos: `cdn.jsdelivr.net/npm/simple-icons@13.15.0/icons/<name>.svg` (anthropic, openai, googlegemini, meta, mistralai, deepseek; no xai: draw text). Put logos on white tiles. Brand/car/product images you don't have: draw SVG stand-ins and flag them in the sanity check.
6. Banners: `white-space: nowrap`, 80–104 px; check long text isn't clipped. Keep cam overlays out of the face (hair line y≈300 is free for chips).
7. Loudness: AAC re-encode drops ~1.5 LU; mix at −14 targets final ≈ −15.5 LUFS, still within tolerance; set `loudnorm=I=-12.5` if you need exact −14.
8. **Cuts**: `take.cuts: [[start,end]]` (recording seconds) remove words from the voice; `prep_remotion.py` rebuilds `voice_clean.wav` from the kept pieces (12 ms fades), drops/shifts the word timings and writes `data.cuts` so `clipTime()` skips the same ranges in `cam.mp4`. Windows must not straddle a cut. After a cut, every later timecode moves earlier by the removed length (re-derive `cams`/`overlays` from word times; `word#n` counts change).
9. **Props that sit on the face** (sunglasses): don't place by hand. `scripts/track_eyes.swift` (macOS Vision, `swiftc -O`) writes `assets/eyes.json` (10 fps eye centres); `EyeGlasses` sits **inside** `CamLayer`'s zoomed layer via `inner`, so it follows head, tilt and zoom. Extract frames with `ffmpeg -vf fps=10,scale=540:960`.
10. **User photos of cars/people/places**: blur number plates and other identifiers (`boxblur` on cropped regions; radii must stay < half the crop's chroma size) and say so in the sanity check.
11. "Relaxed / reaction" beats: use the A-roll itself (it already shows you) with a banner + prop card instead of stock emoji art.

Correction to §19: `C1196.MP4` **does** have an audio stream; it was misread as silent. Full generic version: [`shorts-kit/MASTER_SPEC.md`](shorts-kit/MASTER_SPEC.md) §13.

---

## 21. 🆕 Update: HTML site + GitHub Pages (2026-11-11)

**Pages (all share one menu from `nav.js`; edit `LINKS` once):**
| Page | File | Built by | Purpose |
|---|---|---|---|
| Project | `index.html` | by hand | `#preprod`, `#prod`, `#postprod` sections, thumbnail linking to the player |
| Player & output | `player.html` | `scripts/build_site.py` | dedicated player (chapters from `data.json`, speed, copy link), measured specs (length, size, LUFS/peak via ffprobe/ffmpeg), thumbnail, file table with size + download + copy-link |
| YouTube metadata | `metadata.html` | by hand | title, description, tags, pinned comment, upload settings, copy buttons + counters |
| Master spec | `spec.html` ← `MASTER_SPEC.md` | `build_site.py` | rendered Markdown in the shared menu |
| Kit pages | `kit.html`, `kitspec.html`, `skill.html`, `cheatsheet.html` | `build_site.py` | rendered Markdown of `shorts-kit/*` |
Every page also gets the floating 📝 notes panel (`nav.js`: autosave per page, copy / download / clear; key `n` opens, `Esc` closes) and `window.copyText()`. **Copied/downloaded notes start with the page title + URL + time and end with the community CTA** (`CTA` const in `nav.js`; this project: "Join our Skool community: Delivery Pilot", logo `skool.png` shown in the panel). (real link set: https://www.skool.com/delivery-pilot-8938).

**Markdown rendering:** GitHub Pages serves a `.md` URL as raw text (`…/MASTER_SPEC.md` stays raw). To show it formatted inside the menu, `build_site.py` embeds the Markdown as JSON in `<name>.html` and renders it with `marked` (cdnjs, pinned 12.0.2), falling back to plain text offline. **Re-run `python3 -I scripts/build_site.py` after editing any `.md` or re-rendering the video** and commit the generated `.html`.

**Deploy (GitHub Pages, from the feature branch so `main` stays untouched):**
```bash
python3 -I scripts/build_site.py && git add -A && git commit -m "…" && git push -u origin <branch>
gh api -X POST repos/<user>/<repo>/pages -f "source[branch]=<branch>" -f "source[path]=/"   # once; later pushes redeploy automatically
gh api repos/<user>/<repo>/pages -q '.status+" "+.html_url'                                   # built?
# verify the live file is the new one (Pages caches for ~1 min):
until [ "$(curl -sI "https://<user>.github.io/<repo>/short.mp4?x=$RANDOM" | grep -i content-length | tr -dc 0-9)" = "$(stat -f%z short.mp4)" ]; do sleep 5; done
open -a "Google Chrome" https://<user>.github.io/<repo>/
```

**Raw `.md` URLs get the menu too.** Pages serves `…/MASTER_SPEC.md` as plain `text/markdown` (no menu possible). Fix: put `---\npublished: false\n---` front matter at the top of each `.md` so Jekyll does not publish the raw file; the request then hits **`404.html`**, which maps it to the rendered page (`MASTER_SPEC.md`→`spec.html`, `shorts-kit/README.md`→`kit.html`, `shorts-kit/MASTER_SPEC.md`→`kitspec.html`, `RECOMMENDATIONS.md`→`recommendations.html`, `shorts-kit/syntax/cheatsheet.md`→`cheatsheet.html`). Add new docs to `MAP` in `404.html` and to `MD` in `scripts/build_site.py`. (`build_site.py` strips the front matter before rendering.) Skill files keep their own front matter.

**Menu items always carry an emoji** (`LINKS` in `nav.js`): 📝 Pre-prod · 🎬 Prod · ✅ Post-prod · ▶️ Player & output · 📺 YouTube metadata · 💡 Recommendations · 📘 Master spec · 🧰 Starter kit · 📗 Kit spec v2 · 🚀 Join <community> (external link, new tab).

**CTA (community):** name it, show it, one ask. In the video: `cta` overlay in `storyboard.json` (end card 2.6 s: "join our community", Skool logo, name, URL text, "link in the pinned comment"); `outro_seconds` ≥ 2.6. In the notes panel, metadata description and pinned comment: the full URL. This project: **Delivery Pilot** on Skool, `https://www.skool.com/delivery-pilot-8938`, logo `skool.png` (kept in `assets/img/`).


**Community page (`skool.html`, menu 🏫):** built by `scripts/build_community.py` (edit the strings, re-run, commit). Contains the community logo + join button, an **"What is LSP?" explainer** (what it is, what it gives, why it helps cheap models, diagram, honest caveats: not a magic switch, verify the tool passes diagnostics, language server must be installed, OpenCode docs say not always a net positive) and copy-paste **pinned comments**: the YouTube comment (hook line, one-paragraph explainer, CTA + URL, question) and the community's welcome post (start-here steps, explainer, rules of thumb). The same script patches `metadata.html` so the comments never drift. **Every Short's pinned comment explains the core concept in 2–3 sentences** (viewers who don't know the term still get the value) and ends with a question.

Rules: the repo must be public (or a paid plan) for Pages; **everything committed becomes public** (voice, on-camera video stills, user photos, plates blurred); keep each file < 100 MB (the MP4 is ~50 MB; the 4K source and `cam.mp4` stay out of git); `remotion/public/*` and heavy intermediates are gitignored; never commit secrets. Live URLs for this project: `https://rifaterdemsahin.github.io/200DollarAiCostLSP/` (`index.html`, `player.html`, `metadata.html`, `spec.html`, `kit.html`).

Rendered version of this file: [spec.html](spec.html) (same menu as every page).

**Working rule:** commit **and push** after every change (not only at the end); feature branch, then verify the live Pages file.

---

## 22. 🆕 Update: review pass, recommendations, repo hygiene (2026-11-11)

**Deliverable:** `RECOMMENDATIONS.md` → `recommendations.html` (menu 💡): honest verdict, ranked recommendations with why/effort, a measured sanity-check table, a "not verified" list, next steps. Do this **before** calling a Short done.

**Run these checks with evidence, not by eye alone:**
1. Contact sheet of the final MP4 every ~2.5 s (`ffmpeg -ss T … tile=9x2`) and **read every tile**: clipped banners, props over faces, text colliding with subtitles (y 1500–1700), progress dots, emoji over headlines.
2. Subtitles vs audio: re-transcribe the cleaned voice with a second model/size; where they disagree with the script, patch it (below).
3. `ebur128=peak=true` on the final MP4 (AAC re-encode costs ~1.5 LU); lip-sync lag per window (< 1 frame).
4. Link check across all pages (every local `href/src` exists); `grep` for secrets (the spec's own placeholder `fal_sk_` is a known false positive).
5. **Test the kit from scratch**: `new-short.sh <tmp>` then `npx tsc --noEmit` in `remotion/`. (This caught missing `data.json`/`eyes.json`; the template now ships placeholder copies in `remotion/public/`.)
6. Rights check: third-party photos (people, cars), logos (name-only use), plates/identifiers blurred.

**New storyboard fields:**
- `word_patches: [{"match":["a","relax."],"to":"relaxed."}]` fixes ASR mistakes while keeping Whisper's timing (applied after cuts).
- `take.cuts`, `cams`, `overlays`, `cta`, `outro_seconds` (≥ 2.6 s so the end card can be read).

**Subtitle rule:** groups of up to 3 words, **never across a sentence end** (`. ! ?`), current word highlighted.

**Repo hygiene:** do not commit a new MP4 for every iteration: each version stays in git history (this project: `.git` 172 MB after 4 versions). Use GitHub Releases / Git LFS for `short.mp4`, or commit it only at milestones; never rewrite history or force-push without the owner's OK.

**Working rule:** commit **and push** after every change; verify the live Pages file (`content-length` equals local) before reporting done.

See also: [recommendations.html](recommendations.html) (this project's review), [kit spec v2](kitspec.html).

---

## 23. 🆕 Update: term → community flywheel (2026-11-11)

Page: `design.html` (menu 🧭), built by `scripts/build_design.py` (mermaid diagrams via cdnjs `mermaid@10.9.1`, plain-text fallback offline).

**Principle.** Every Short teaches **one term people need to learn** (example: LSP), makes it matter with a metaphor + one payoff, and sends viewers to the **community (Skool: Delivery Pilot)** for the step-by-step. The pinned comment explains the term in 3 sentences (value without a click) and links for depth.

**Brief field:** *Term* (name, one-line meaning, metaphor, proof shot, Skool next step, audience question), stored in `storyboard.json` → `term`.

**Flywheel (mermaid):** Short teaches term → curiosity ("what is X?") → pinned comment (term line + link + question) → Skool lesson/thread → members try it, post wins and stuck points → proof + questions → next term (and proof clips become b-roll) → next Short, which also links to earlier terms.

**Three loops:** content (questions → topics), community (more members → more wins → better reason to join), library (lessons persist; new Shorts point to old terms).

**Pinned-comment template:** hook line · term explainer (2–3 sentences) · `📖 New term of the day: <TERM>. Learn it step by step … inside <community>.` · CTA + URL · question. Shared strings live in `scripts/build_community.py`.

**Measure (hypothesis, no baseline yet):** comments asking "what is X?", new community members after each Short (add a join question "Which Short brought you here?"), activation (intro/result posts), proof shared per term, member-requested terms that become Shorts. Judge the first 3–5 term Shorts as an experiment; no income or result promises to members.

See [design.html](design.html) and [skool.html](skool.html).

---

## 24. 🆕 Long-form 1080p (2026-11-11)

For 16:9 YouTube long form (screen recordings + own voice, synced with `scripts/sync_clips.py`, rendered with `scripts/render_base.sh`, overlays in `remotion/`), use the new **[MASTER_SPEC.md](MASTER_SPEC.md) v3**. Site: [index.html](index.html) · [player.html](player.html) · [metadata.html](metadata.html) · [spec.html](spec.html). Media files are never committed.
