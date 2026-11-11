#!/bin/zsh
# Pull the latest kit zip from Google Drive and unpack it. Usage: scripts/pull_kit.sh [target_dir]
# The Drive folder id is read from Azure Key Vault (secret cmf-kit-drive-folder-id); override with KIT_FOLDER_ID.
# Needs: az (logged in), rclone with a Google Drive remote (default gdrive-shared, override with KIT_REMOTE).
DEST="${1:-.}"; VAULT="${KIT_VAULT:-dp-kv-deliverypilot}"; REMOTE="${KIT_REMOTE:-gdrive-shared}"
FID="${KIT_FOLDER_ID:-$(az keyvault secret show --vault-name "$VAULT" --name cmf-kit-drive-folder-id --query value -o tsv)}"
[ -n "$FID" ] || { echo "no folder id (az login? vault $VAULT)"; exit 1; }
TMP=$(mktemp -d); mkdir -p "$DEST"
rclone copy "${REMOTE}:" "$TMP" --drive-team-drive "" --drive-root-folder-id "$FID" --include "claude-missing-features-kit.zip" -q 2>&1 | grep -v NOTICE
[ -f "$TMP/claude-missing-features-kit.zip" ] || { echo "kit zip not found in Drive folder"; exit 1; }
unzip -o -q "$TMP/claude-missing-features-kit.zip" -d "$DEST" && chmod +x "$DEST"/scripts/*.sh "$DEST"/new-video.sh
echo "Kit unpacked in $DEST. Next: cd $DEST && ./new-video.sh \"<Title>\" <duration_seconds>"
