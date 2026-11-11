#!/bin/zsh
# ONE-TIME SETUP (run it yourself: it moves a storage key into Key Vault, which the assistant's permission system does not do for you).
#   ! scripts/setup_azure_exports.sh [storage-account] [resource-group] [vault]
# Creates a PRIVATE container for the exports and stores three secrets in Key Vault: cmf-exports-storage-account, cmf-exports-container, cmf-exports-storage-key.
# upload_exports.py then reads them from the vault (the key is never printed or written to the repo).
ACC="${1:-dpprojects}"; RG="${2:-deliverypilot-rg}"; VAULT="${3:-dp-kv-deliverypilot}"; CONT="claude-missing-features-exports"
KEY=$(az storage account keys list -n "$ACC" -g "$RG" --query "[0].value" -o tsv) || exit 1
az storage container create --account-name "$ACC" --account-key "$KEY" -n "$CONT" --public-access off -o none && echo "container $CONT ready (private)"
T=$(mktemp -d); chmod 700 "$T"; printf %s "$KEY" > "$T/k"; printf %s "$ACC" > "$T/a"; printf %s "$CONT" > "$T/c"
for p in "cmf-exports-storage-key:k" "cmf-exports-storage-account:a" "cmf-exports-container:c"; do az keyvault secret set --vault-name "$VAULT" --name "${p%%:*}" --file "$T/${p##*:}" --encoding utf-8 -o none && echo "stored ${p%%:*}"; done
rm -rf "$T"; unset KEY; echo "Done. Next: python3 scripts/upload_exports.py"
