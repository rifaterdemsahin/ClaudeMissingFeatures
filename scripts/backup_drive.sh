#!/bin/zsh
# Back up to Google Drive (same folder as the kit; folder id from Azure Key Vault). 0 Claude tokens.
# Uploads: kit zip + MASTER_SPEC.md (replaced in place), a project backup zip of everything tracked by git, a timestamped copy under backups/,
# and the latest export video if it exists (videos are not in git). Usage: scripts/backup_drive.sh [--no-video]
# Needs: az (logged in), rclone with a Google Drive remote (default gdrive-shared, override KIT_REMOTE).
cd "$(dirname "$0")/.." || exit 1
VAULT="${KIT_VAULT:-dp-kv-deliverypilot}"; REMOTE="${KIT_REMOTE:-gdrive-shared}"
FID="${KIT_FOLDER_ID:-$(az keyvault secret show --vault-name "$VAULT" --name cmf-kit-drive-folder-id --query value -o tsv 2>/dev/null)}"
[ -n "$FID" ] || { echo "backup: no Drive folder id (az login? vault $VAULT)"; exit 1; }
R(){ rclone "$@" --drive-team-drive "" --drive-root-folder-id "$FID" -q 2>&1 | grep -v NOTICE; }
mkdir -p kit-dist; STAMP=$(date +%Y%m%d-%H%M); BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-')
scripts/build_kit.sh kit-dist/claude-missing-features-kit.zip >/dev/null
git archive --format=zip -o kit-dist/project-backup-latest.zip HEAD && cp kit-dist/project-backup-latest.zip "kit-dist/project-$STAMP-$BR.zip"
R copy kit-dist/claude-missing-features-kit.zip "${REMOTE}:"
R copy MASTER_SPEC.md "${REMOTE}:"
R copy kit/KIT_README.md "${REMOTE}:"
R copy kit-dist/project-backup-latest.zip "${REMOTE}:"
R copyto "kit-dist/project-$STAMP-$BR.zip" "${REMOTE}:backups/project-$STAMP-$BR.zip"
if [ "$1" != "--no-video" ] && [ -f remotion/out/long.mp4 ]; then R copyto remotion/out/long.mp4 "${REMOTE}:videos/claude-missing-features-export-latest.mp4"; fi
rm -f "kit-dist/project-$STAMP-$BR.zip"
echo "backup done $STAMP ($BR) -> Drive folder; $(R lsf "${REMOTE}:" | tr '\n' ' ')"
