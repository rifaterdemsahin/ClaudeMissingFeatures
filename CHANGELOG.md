---
published: false
---
# 🗒️ Changelog: everything that happened

Legend: 🚀 start · 🎬 video edit · 🧩 site or tool · 🐛 bug found and fixed · 🔒 privacy · 🔊 audio · ♻️ reuse and kit · ☁️ publish and backup · 🧪 tests · 🛑 blocked by the permission system · 📈 measured · 📝 owner's notes · 🧠 decision

## 🎞️ Export versions

| Version | Rendered | Length | Size | What changed |
|---|---|---|---|---|
| **v5** (latest) | 2026-11-11 18:54 | 114.0 s | 10.5 MB | Platform cuts of v5: LinkedIn highlights (3:19) and X highlights (1:54) with shorter endings |
| **v5** (latest) | 2026-11-11 18:50 | 198.8 s | 27.9 MB | Platform cuts of v5: LinkedIn highlights (3:19) and X highlights (1:54) with shorter endings |
| **v5** (latest) | 2026-11-11 18:43 | 719.3 s | 95.4 MB | Subtitle quality: Claude's answer corrected from the on-screen text, 'code connectors' fixed, stutters dropped from captions, flicker removed (min 0.9 s / merged); everything else as v4 (round-4 notes) |
| **v4**  | 2026-11-11 18:15 | 719.3 s | 95.4 MB | Round 4 notes: WhatsApp banner blurred; Grok Bot window shown (agent list blurred) for the update; lower third at 8:44; captions fixed (Claude not clothe); hoover part cut (50.8 s) with an animated apology card; Whiteboard expected-output picture again at the end |
| **v3**  | 2026-11-11 15:51 | 764.1 s | 97.0 MB | Whiteboard picture card with arrow added (expected feature), caption box clear of the picture |
| **v2**  | 2026-11-11 15:22 | 764.1 s | 97.2 MB | Leaks fixed (blur and slide edges padded), no transitions, hoover noise reduced, summary slide and Skool call-to-action added, family-photo moment covered |
| **v1**  (not kept) | 2026-11-11 14:15 | 743.1 s | 150.4 MB | First full export (not kept): OCR check found private text at 6:30, 6:58, 8:36 and 12:22 at box edges; no summary or call-to-action yet |

## 📈 Where it stands

- 🎯 Value-recognition score **77.0 / 100**, grade B (good); key results: ✅ 11 met · 🟡 1 almost · ❌ 0 missed · ⏳ 4 open (see the Pre-prod page)

## Round 7 · 🗺️ Pipeline canvas, public player on Azure, deterministic spec evals (spec v3.18)
*2026-11-11 evening*

- 🗺️ **Pipeline canvas**: Built tldraw interactive pipeline diagram (pipeline.html) driven by assets/timings.json with 3 bands (prepare, render, publish), swimlanes (MacBook, Claude, owner), zoom/pan, editable toggle, and PNG export
- ☁️ **Public player**: Added stored access policy site-player (read-only, 90 days) on Azure container via upload_exports.py --site; writes azure_links.js; public mode plays from Azure while keeping original recording locked
- 🧪 **Spec evals**: Added deterministic spec evaluation suite (scripts/eval_spec.py) testing 4 groups: A. Recreate from kit (40), B. Spec coverage (30), C. Retrieval questions (20), E. Kit completeness (10); evals.html page displays score 100/100 (A)
- ♻️ **Kit completeness**: Updated build_kit.sh to bundle pipeline app, evals, questions and Azure player support; passes reuse and idempotence checks

## Round 6 · 📣 Publishing: three platforms, Azure, script and changelog
*2026-11-11 night*

- 🧩 **Script page**: Whole script by chapter with clickable timecodes, a before→after table of every caption change and the subtitle issues with how each was found and fixed
- 📈 **Subtitles**: check_subtitles.py found 57 low-confidence words, 5 stutters, 21 flickering captions; fixed from the on-screen text, rules and clean-up (stutters 5→0, flicker 21→5); 4 doubtful spots left for the owner
- 🗒️ **Changelog**: This page: rounds, versions, decisions, commits
- 🧩 **Artifacts notes**: Per-artifact notes with green Saved animation, version tags, copy and send-to-player
- 🧩 **README**: Generated navigation hub with the prompt to execute; spec gets a linked contents table
- 🎬 **Platform cuts**: One edit, three cuts: LinkedIn 3:19 (9 highlight ranges + ending), X 1:54 (5 ranges + ending, under the 2:20 limit), YouTube full; shorter endings per platform
- 🧩 **Publish page**: YouTube, LinkedIn, X cards with limits, length bars, checks, text with character counters, placeholders for storage and post links, notes
- 🛑 **Blocked**: Copying the storage key into Key Vault was refused by the permission system (secret-store write). Not worked around: a one-time setup script is for the owner to run with !
- 🔗 **Menu**: Links group now has Azure Storage, Azure Key Vault and the platform post links (once shared)
- ⏱️ **Time page**: Time and order: 19 stages with who does each, measured vs estimated time, LLM involvement, parallelism, prep tips and a planning calculator (the render is about 2.3 × the video; keep the machine idle while it runs)
- 🎬 **Renders v5**: YouTube 11:59 (95.4 MB), LinkedIn 3:19 (27.9 MB), X 1:54 (10.5 MB, under the 2:20 limit); all three pass the OCR privacy check (0 sensitive lines); score 77.0 / 100, 11 key results met
- 🐛 **Bug**: The privacy check flagged the ending of the platform cuts (it used the YouTube file's end); and the chapter measurement used source time for a chapter inside a cut, faking a 7 s chapter. Both fixed
- ☁️ **Azure**: Private container claude-missing-features-exports in the storage account dpprojects. My first attempts (login identity) could create the container but not write files, and copying the storage key into Key Vault was blocked, so the owner ran the one-time setup (scripts/setup_azure_exports.sh) which stored cmf-exports-* in Key Vault. Then upload_exports.py read the key from the vault and uploaded the three v5 exports with 30-day read-only links (expire 2026-12-11)
- 🧪 **Azure check**: All three links answer HTTP 206 with the exact file sizes (95.4, 27.9, 10.5 MB); the same URLs without the signature return 404, so the container is private. The links live only in the git-ignored publish_links.js; the live site and repo never contain them

## Round 5 · 📝 Owner's third notes (export v3) and versions
*2026-11-11 night*

- 🎬 **Blur**: WhatsApp notification banner (sender "Onur Alp Taner") blurred at the top right, 250–256 s; OCR had missed it because the keyword had no space
- 🎬 **Grok Bot**: The real Grok Bot window shown for the update (slide shortened) with its list of personal agent chats blurred in two states (menu closed/open) so the update menu with "76% used" stays readable
- 🎬 **Lower third**: "We are entering a world of exponentially more updates and deliveries" at 8:44
- 🎬 **Hoover cut**: Cut 574.4–625.2 s (50.8 s) at sentence boundaries (the note's end time would have chopped a sentence) and an apology card with an animated cartoon hoover; every later time moves 45 s earlier
- 🎬 **Picture**: The Whiteboard picture shown again at 12:01 as the expected output (the only new file in Downloads; asked the owner first because two files were identical)
- 🧩 **Versions**: Every export is numbered and never overwritten (exports/<slug>-vN.mp4, registry, render_export.sh); notes are tagged [vN m:ss]; copied feedback names the version; the registry keeps each version's own time map
- 🐛 **Bug**: A chapter inside a cut jumped to the end of the video: it now starts at the next kept moment
- 🧩 **Notes**: The Artifacts page has per-artifact notes (saved per browser, version-tagged, green Saved animation, copy all, send to player feedback, clear with undo)
- 📈 **Subtitles**: check_subtitles.py (Whisper confidence, stutters, reading speed, flicker) found real problems: Claude's on-screen answer garbled by the recogniser (fixed from the screen text), "code connectors", 5 stutters, 21 flickering captions; 4 spots left for the owner's ear. The Script page lists every issue and how it was fixed
- 🔒 **v4 check**: Export v4 passed the OCR privacy check: 360 frames, 0 sensitive lines

## Round 4 · 🧱 Structure, reuse and review tools
*2026-11-11 evening*

- 🧩 **Pages**: Architecture, Environment (with check_env.sh), EDL (edit decision list with source and export timecodes and a decision log), Artifacts (every added element with a frame, how it is used and a link into the player), Script, Changelog; menu grouped Start · Make · Review · Links and collapsible
- 🧩 **Player**: Original vs export side by side; keys (Space/K, J/L speed, arrows, frame step); 📍 add note; ⏪ ⏩ 1-second buttons; ⏮ last review point; collapsible panels with the feedback under the video; green ✔ Saved animation; version selector
- 📈 **OKRs**: Objectives and key results, value proposition, value-recognition checkpoints and a 100-point score from measured numbers (loudness, dead air, time to first action…); honest pre-publish estimate 75.5 / 100 (B)
- ♻️ **Reuse first**: The owner's standing rule: every per-video fact moved into remotion/src/project.json; scripts, components, menu and templates read it; check_reuse.sh fails if code contains this video's words; kit carries blanks
- ♻️ **Whole site**: build_all.sh builds all pages from the kit and check_site.py checks every menu item, link and script. The test caught two reuse bugs (a script assuming a kit/ folder; missing subtitle files)
- 🧪 **Tests**: Each change is checked: py_compile of every script, tsc, the kit unpacked in a temp folder, outputs regenerated and compared byte for byte
- ☁️ **Backup**: Standing rule: after every push back up to Drive (kit, spec, project zip, each export version)

## Round 3 · 🎙️ Owner's second notes, privacy and the hoover
*2026-11-11 afternoon–evening*

- 🔒 **Privacy check**: verify_export.py OCRs the finished video every 2 s: it found private text at 6:30, 6:58, 8:36 and 12:22 at the edges of boxes and slides (sampling every 2 s); boxes padded 1.5 s, slides 0.5 s before and 1.8 s after; result 0 leaks
- 🎬 **Transitions**: All fades and springs removed: hard cuts, captions appear and disappear without animation (only the active word is highlighted)
- 🔊 **Hoover**: Noise found with numbers (noise-floor, spectrogram: a steady haze from source 571 s to the end). Cutting it would have removed the conclusion, so it was removed with noisereduce learned from a noise-only stretch: haze +12 dB → about 0 dB, speech −0.5 dB
- 🎬 **Family photo**: A photo widget on the desktop (while the app reopened) covered by the "Update finished" slide
- 🎬 **Ending**: Summary slide (4 points from the narration) and a 10 s Skool call-to-action card for Delivery Pilot
- 🎬 **Picture**: whiteboard.jpeg shown at 1:44 with caption, orange box and arrow: "This is the feature I expected to see: Whiteboard"
- 🐛 **Bug**: Adding the cleaned audio put the video index at the end of the file and slowed the render from 13 to 8.7 frames/s: fixed with faststart
- 🐛 **Bug**: A syntax slip (a comment inside a call) in denoise_audio.py was caught by the kit test and fixed

## Round 2 · 🧰 Kit, Drive, Key Vault and the mistakes
*2026-11-11 afternoon*

- ♻️ **Kit**: Packed scripts, Remotion project, templates and the spec into a kit zip; MASTER_SPEC v3 written for reuse
- ☁️ **Drive**: Created the Drive folder "Claude Missing Features Kit" and uploaded the kit; stored its id and link in the existing Azure Key Vault (dp-kv-deliverypilot) as secrets, never in the repo; pull_kit.sh reads the id and pulls with rclone
- 🐛 **Mistake**: I tested new-video.sh from the repo root: it emptied real pages (index, prod, player, metadata…) and set the duration to 900 frames. Everything was restored from git and the script now changes into its own folder and refuses to run in a git folder with changes. Lesson: test scaffolding only in a temp folder, commit before experiments
- 🐛 **Bug**: build_kit.sh given a relative output path zipped into a temp folder and left the old zip; now resolves the path first
- 🛑 **Blocked**: The permission system blocked a bundled commit+push, and later a standing git hook plus an automatic Drive upload. I did not work around either; the hook is written but not installed, and Drive backups go through the Drive tool
- ☁️ **Publish**: Merged to main (GitHub already held two PR merges of this branch: integrated, no force), pushed, enabled GitHub Pages from main, README starts with the live link

## Round 1 · ✂️ First edit list from the owner
*2026-11-11 midday*

- 🎬 **Intro**: The recording opened on the OBS window: covered by a title card; later extended by 2 s on request (0–4.3 s)
- 🎬 **Slides**: The opening IBM chat scene replaced by a slide "What we are doing"; nine more windows with personal apps (Grok Bot lists) found by OCR and covered with explainer slides written from the narration
- 🔒 **Blur**: Chat titles in the app sidebar (Market Participant Onboarding and the rest) blurred. Boxes are generated from Apple Vision OCR, not placed by hand (two fixed sidebar boxes, sensitive words, the screenshot's mini sidebar)
- 🎬 **Speed**: Typing at 1:08 played at 3× and muted (68.47 to 79 s); captions hidden inside it
- 🧩 **Captions**: Word-by-word animated captions from Whisper word timings; product names fixed (Claude, Grok bot, Homebrew, Canva, HTML); .srt/.vtt for YouTube
- 🧩 **Cuts**: Cut-aware timeline in Remotion (cuts.json) with audio fades; script that lists repeats, stutters and silences as cut candidates (nothing cut without the owner)
- 🐛 **Bug**: Volume fade made an invalid range and crashed the render: replaced by a helper that only fades at real cuts
- 🐛 **Bug**: A symlink to the video made the render bundle 404: Remotion needs a hard link
- 📈 **Render**: The first on-screen render ETA said hours; real speed was 13 frames/s (about 25 min)

## Round 0 · 🚀 Start: from the README to a first video
*2026-11-11 morning*

- 🎬 **Source**: Read the README spec; the repo held only that file. Material: two screen recordings (3456×2234 @ 60 fps, 8:01 and 4:34) and a Zoom voice WAV (12:35) in ~/Downloads/Claude Missing Features
- 🧩 **Sync**: Synced the clips to the clean voice by cross-correlation: clip 1 at +4.75 s (confidence 5.5), clip 2 at +486.09 s (confidence 4.0); the two clips tile exactly
- 🎬 **Base video**: Rendered a 1920×1080, 30 fps base with a blurred side fill (nothing cropped) and the voice normalised to −14.5 LUFS: 12:30
- 🧩 **Transcript**: Whisper transcript with word timings; title, description, 14 chapters and tags written (YouTube metadata page)
- 🧩 **Remotion**: Remotion project created; Studio on :3000; Chrome path set in remotion.config.ts because the bundled browser fails on this Mac
- 🧩 **Website**: First site: project hub, pre-prod, prod, post-prod, player, metadata, spec; shared menu and notes panel (nav.js)
- ☁️ **Publish**: First commit and push on a feature branch; media never committed

## 🧠 Decision log: every owner note and how it was handled

| # | In | Said | Decision |
|---|---|---|---|
| 35 | site | add a page for the completion time and how long each stage takes with the llm, give the order and what can be done to prep up | Time and order page: 19 stages in order with who does them, measured or estimated time, LLM involvement, parallelism, prep tips, a planning calculator and the elapsed time |
| 34 | site | in the links add azure and links | Menu Links group: Azure Storage and Azure Key Vault portal links (generic, no account ids) from project.json, and the platform post links once shared |
| 33 | v5 platforms | publish page for YouTube, X.com and LinkedIn with placeholders; renders for all three with different lengths; upload exports to Azure Storage with keys in Key Vault, embed in the placeholders, let me review, add note taking | Publish page with per-platform cards, placeholders, counters, checks and notes. Platform cuts in variants.json: LinkedIn 3:19, X 1:54 (limit 2:20), YouTube full. Azure: private container in dpprojects; the owner ran the one-time setup that stores the storage key in Key Vault (the assistant may not copy keys into the vault); upload_exports.py then read it from the vault, uploaded the three v5 files and made 30-day read-only links kept only in a git-ignored local file |
| 32 | site | update the readme.md, make it more navigational and have the master spec populated | README is a generated navigation hub (live links, pages, spec contents, the prompt to execute, commands, what is where, versions, score); the old Shorts recipe moved to docs/; the spec has a linked contents table |
| 31 | site | add a note taking feature on the artifacts page | Per-artifact notes with stable keys, version tags, green Saved animation, copy, send to player feedback, clear with undo |
| 30 | site | have a page for the changelog showing everything that happened with emojis; update the master spec | Changelog page generated from a hand-written timeline, the export registry, the decision log, the score and git |
| 29 | v5 | have a page for the script and mention the issues with the subtitles and how it is fixed; if not fixed, fix it | Script page (spoken script by chapter with timecodes, every caption change before→after, 14 issues with how found and fixed, 4 left for the owner's ear). Fixed from evidence: Claude's on-screen answer corrected from the screen text, 'code connectors', stutters dropped, flicker removed |
| 28 | site | name every export with a version number and mention that in the feedback | Every export is numbered and never overwritten: exports/<slug>-v<N>.mp4 with a registry (assets/exports.json); the player has a version selector, every note is tagged [vN m:ss] (or [orig m:ss]), copied feedback starts with a header naming the version, Drive and Downloads copies carry the number. v1 (not kept), v2 and v3 registered; this round is v4 |
| 27 | v4 | [export 12:01] add the visual expected output that is in downloads folder | Owner chose to show whiteboard.jpeg again (the only new file in Downloads; the WhatsApp copy is byte-identical). Picture card at source 726 to 734 s (export 12:01 in v3), caption "The expected output: Whiteboard", orange box and arrow on the Whiteboard tile |
| 26 | v4 | [export 9:29] there is a hover sound it needs to be cutted start; [export 10:20] cut till this timeline hover ends and the design is out. Show a hover gif and apologize | Cut source 574.4 to 625.2 s (50.8 s). The note said export 10:20 (= source 627.0) but the next sentence starts at 625.4, so the cut ends just before it instead of chopping "Yes, now it's created…"; it starts in the silence before "And let's see the double click…". A 6 s card is placed at the cut: "Sorry! A hoover joined the recording here, so about 50 seconds are cut." with an animated cartoon hoover (frame-driven, like a GIF). Everything after moves 45 s earlier |
| 25 | v4 | [export 8:59] claude not clothe, fix the subtitles, check other places as well; [export 11:38] not clothe but Claude | Caption fix "clothe/clothes" to "Claude" added to project.json. Searched the transcript for every look-alike (cloth, clod, claw, clou, clau): 5 slips in total (4 clothe, 1 clothes), all fixed; earlier fixes (cloud, growth bot, Kamba, hdml, homebrief) unchanged; .srt/.vtt regenerated |
| 24 | v4 | [export 8:44] mention we are entering into world of exponentially more updates and deliveries in the lower third | Lower third at source 531 to 540 s: label "Why keep updating", text "We are entering a world of exponentially more updates and deliveries"; sits above the captions |
| 23 | v4 | [export 5:36] show the grokbot just to update this part | The slide now ends at 336.0 s; the real Grok Bot window shows from 336 to 346 s with its list of personal agent chats blurred (two boxes: menu closed, menu open) while the update chat and the open menu ("New update available", "Weekly usage 76% used") stay readable |
| 22 | v4 | [export 4:04] onuralp whatsapp message to be blurred out on right top | A WhatsApp notification banner (sender and message) sits top right from source 251 to 256 s (export 4:04 = source 251). OCR missed it because the keyword had no space (the sender shows as "Onur Alp"). Blurred by a hand-placed box 250.0 to 256.3 s; "onur alp" added to sensitive_keywords so the export check flags it anywhere else |
| 21 | site | in preprod add objectives and key results, mention the value recognition and score it | OKR block in Pre-prod from assets/okr.json + measured metrics; value-recognition checkpoints with timecodes; weighted score 75.5/100 (B) with evidence and proposed improvements (not applied) |
| 20 | site | create a page for all artifacts used with timecodes, clickable, to see how they are used | Artifacts page: 44 elements, source+export timecodes, frames from the export, how used, request and decision, deep links into the player |
| 19 | site | always remember that I need to be able to reuse this structure | All per-video facts moved into remotion/src/project.json; scripts, components, nav and templates read it; scripts/check_reuse.sh enforces it; 'Reuse first' rules at the top of the spec; kit carries blanks |
| 18 | site | add a feature to go to last review point | ⏮ Last point button (video + Feedback panel) and the R key jump to the last [orig|export m:ss] note (switching version, 3 s lead-in); without notes they go to where you stopped |
| 17 | site | master spec should create a video faster by getting what is needed; include a prompt to execute on top | Prompt to execute and a 'get what is needed' checklist added at the top of the spec |
| 16 | site | logically group to menu | Site menu grouped: Start, Make, Review, Links |
| 15 | v3 | use whiteboard.jpeg from Downloads: mention in the video this was the expected feature to see, and use an arrow to the whiteboard feature | Image card at 1:51 to 2:03 (source 111 to 123 s), where the narration says the whiteboard is missing: caption 'This is the feature I expected to see: Whiteboard', orange box around the Whiteboard (Beta) tile and an arrow pointing at it. Image stays local (remotion/public/img, not committed) |
| 14 | v1 | have the subtitles done / animated | Whisper word timings -> animated captions (active word highlighted) and .srt/.vtt for YouTube; product names fixed (Claude, Grok bot, Homebrew) |
| 13 | site | have original and the latest export on the player page | Original / Latest export buttons, side by side with a time map, export info, version-tagged feedback notes |
| 12 | site | player needs speed up and speed down, J K L mapped; space bar to stop | Space/K pause, L faster (1,2,4,8x), J slower (down to 0.25x), 1 normal, arrows 5 s, comma/period frame step, F fullscreen; ignored while typing |
| 11 | v2 | at the end have the CTA to delivery pilot skool community to learn in depth | Final 10 s card: 'Learn it in depth', 'Join the Delivery Pilot community on Skool', skool.com/delivery-pilot-8938, 'Link in the description and the pinned comment'. No income or result promises |
| 10 | v2 | [export 12:23] end the video with a summary part | Added an ending after the footage: 'Summary: what we learned' slide, 11 s, four points taken from what is said (gradual rollout, no beta switch, update everything, use other artifact types). Silent |
| 9 | v2 | [export 11:20] remove the family picture part in the back | Export 11:20 = source 687 s: while the app quits and reopens the desktop shows the wallpaper and a photo widget with people. Covered by the 'Update finished' slide, extended to 672.5 to 689.0 s (narration kept) |
| 8 | v2 | [export 9:25] the hoover comes in the audio, cut all that part out | Export 9:25 = source 572 s. Spectrogram and noise-floor analysis: the hoover starts at about 571 s and runs to the end of the recording (haze +12 dB). Cutting all of it would remove the planner canvas demo and the conclusion (about 3 min), so the hoover is removed with noise reduction learned from 592 to 622 s (hoover-only room tone), from 566 s on, with a 1.5 s crossfade. Result: haze back to 0 dB vs the clean part, speech level -0.5 dB |
| 7 | v2 | [export 0:03] in and out transition should not be there | Removed every in/out effect: intro card and slides cut hard (no fades), slide bullets appear at once, caption phrases appear and disappear without spring or fade (the active word is still highlighted by colour). Audio fades at cuts stay (they prevent clicks) |
| 6 | v2 | verify_export.py found sensitive text still visible at 6:30, 6:58, 8:36 and 12:22 | OCR samples every 2 s, so edges leaked 1 to 2 s. Pad every blur box by 1.5 s and slides by 0.5 s before and 1.8 s after; checker flags app lists only when 2+ lines show together |
| 5 | v1 | blur the parts that say market participant onboarding 04:17:28 and similar places | 04:17:28 = 257.93 s. Blur the chat-title list in the app sidebar whenever it shows (two fixed boxes), sensitive words anywhere, and the mini sidebar inside the pasted screenshot (anchored to the line under it). Boxes are generated from OCR, not placed by hand |
| 4 | v1 | 01:08:14 typing speed up the back footage | Timecode read as mm:ss:ff at 30 fps = 68.47 s. Typing runs to the send at about 79 s: played at 3x and muted (speech sped up is unusable; the typed text is on screen). Captions hidden inside it |
| 3 | v1 | cover up personal stuff with slides | Found 9 more windows with personal apps (OCR: Skool, LinkedIn, Gmail, Rag Manager lists) and covered each with a short explainer slide written from what is said at that moment. Covered, not cut, so the narration stays intact |
| 2 | v1 | remove the background where it shows IBM, instead place a slide that explains what we are doing | Slide 'What we are doing' over 4.3 to 16.0 s; the real recording there showed an IBM chat and a personal Grok Bot window |
| 1 | v1 | have initial 0:00 stay 2 seconds more longer Claude Whiteboard missing | Intro card (Thumb design) extended from 2.3 s to 4.3 s on the source timeline |

## ☁️ Commits (from git)

| Commit | When | Message |
|---|---|---|
| `88a50d4` | 2026-11-11 20:59 | Azure per-video source backup (<slug>-source), tldraw pipeline diagram, deterministic spec evals (score 100/100), note saver with URL in nav, download all exports with metadata |
| `c03d0c7` | 2026-11-11 19:06 | Azure upload done: v5 exports in a private container with read-only links (local only); changelog, decisions and spec v3.17 |
| `2f4a7e8` | 2026-11-11 18:59 | Platform cuts (LinkedIn 3:19, X 1:54), numbered exports v5 for all three, Publish page, Time & order page, Script page, Changelog, README hub, artifact notes, Azure upload tooling (spec v3.16) |
| `3690f0f` | 2026-11-11 18:01 | Reuse-first refactor (project.json), export versions, artifacts page, OKRs, player features, whole-site build, collapsible menu (spec v3.13) |
| `f087cbc` | 2026-11-11 17:25 | Player: add-note button on the video (+ M key, Ctrl/Cmd+Enter resumes); fix build_kit.sh relative output path; spec v3.10 |
| `e3e8e7a` | 2026-11-11 17:24 | Player: collapsible panels, feedback directly under the video, collapse/expand all, remembered state (spec v3.9) |
| `9a41b70` | 2026-11-11 15:53 | Merge origin/main (PR #1 and #2 of this branch) into main |
| `eb6eb30` | 2026-11-11 15:53 | Merge long-form-1080p-v1: final export, EDL, Environment, Architecture, kit and spec v3.8 |
| `566b7bd` | 2026-11-11 15:53 | Final export: Whiteboard image card with arrow, summary + Skool CTA ending, hoover noise removed, no transitions; EDL, Environment, grouped menu, execute prompt, Drive backup rule, clear-feedback button (spec v3.8) |
| `1b2fcb9` | 2026-11-11 14:56 | Fix denoise_audio.py syntax (comment inside call); verified by compile of all scripts and a functional test |
| `a430560` | 2026-11-11 14:56 | EDL page + generator, Environment page + check_env.sh, denoise (hoover), outro summary and Skool CTA, no transitions, export-timeline chapters, kit updates, spec v3.6 |
| `74df541` | 2026-11-11 14:33 | Architecture page, local pipeline + OCR privacy check, slides/blur/speed-up edits, player keys (Space/J/K/L), Pages step in spec v3.5 |
| `85e5500` | 2026-11-11 14:27 | Merge pull request #2 from rifaterdemsahin/long-form-1080p-v1 |
| `882ed98` | 2026-11-11 13:39 | Add Drive kit (templates, pull/build scripts), run page, serve script, working player; spec v3.2 |
| `d97de46` | 2026-11-11 13:24 | Add cut support, animated subtitles, intro card over OBS window, spec v3.1 |
| `5e87658` | 2026-11-11 13:17 | Add pre/prod/post pages, subtitles (SRT/VTT, Remotion layer), player feedback box |
| `0a73652` | 2026-11-11 13:16 | Add Remotion project, website and master spec v3 for long-form 1080p |
| `8b53bea` | 2026-11-11 13:15 | Merge pull request #1 from rifaterdemsahin/long-form-1080p-v1 |
| `12bbbb3` | 2026-11-11 13:13 | Add YouTube title, description and metadata for 1080p long-form video |
| `2180577` | 2026-11-11 12:32 | Update README.md |
| `24abad8` | 2026-11-11 12:31 | Initial commit |

---
*Generated by `scripts/build_changelog.py`. Add events to `assets/changelog.json` as you work; the tables update themselves.*