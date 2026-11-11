# Claude Missing Features Kit

Everything needed to start the next long-form 1080p video in minutes. Spec: `MASTER_SPEC.md` (v3.1). Contents:

| Path | What |
|---|---|
| `MASTER_SPEC.md` | the recipe (sync, render, cuts, subtitles, site, sanity check) |
| `scripts/` | `sync_clips.py`, `render_base.sh`, `build_subs.py`, `find_repeats.py`, `build_site.py`, `pull_kit.sh` |
| `remotion/` | Remotion project: `LongForm`, `Subtitles` (animated), `ImageOverlays`, `Thumb`, `cuts.json`, `overlays.json` |
| `nav.js` | shared site menu + notes panel |
| `templates/` | `BRIEF`, `metadata`, `SANITY_CHECK`, and the HTML page templates (`index`, `preprod`, `prod`, `postprod`, `player`) with `{{PLACEHOLDERS}}` |
| `new-video.sh` | scaffold a project folder from the kit |

## Use
```bash
scripts/pull_kit.sh ~/projects/<new-video>        # pulls the latest kit zip from Google Drive (folder id from Azure Key Vault)
cd ~/projects/<new-video> && ./new-video.sh "<Title>" <duration_seconds>
```
Then follow MASTER_SPEC.md §1. Never commit media (`*.mp4`, `*.wav`).

## Where it lives
- Google Drive folder: "Claude Missing Features Kit" (My Drive). Link and id are stored in Azure Key Vault `dp-kv-deliverypilot` as `cmf-kit-drive-folder-url` and `cmf-kit-drive-folder-id`. Values are not written in the repo.
- Refresh the zip after changing the kit: `scripts/build_kit.sh`, then upload the zip to the same Drive folder (replace the old file).
