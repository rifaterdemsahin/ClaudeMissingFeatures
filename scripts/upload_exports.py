#!/usr/bin/env python3
"""Upload the latest export of each platform (YouTube, LinkedIn, X) to a PRIVATE Azure Blob container and make time-limited, read-only links.
Keys come from Azure Key Vault (secrets cmf-exports-storage-account / -container / -storage-key, made by scripts/setup_azure_exports.sh); nothing secret is printed or committed.
Usage: python3 scripts/upload_exports.py [--version N] [--days 30] [--login] [--check] [--account A --container C] [--create-container]
  --login : use `az login` (Azure AD) instead of the account key; links are user-delegation SAS (at most 7 days). Needs the Storage Blob Data Contributor role.
  --account/--container : name them directly (skips Key Vault; with --login no secret is involved at all). --create-container: create the private container first.
  --site : ALSO make links for the PUBLIC player (azure_links.js, committed on purpose): read-only SAS tied to a stored access policy "site-player" on the container, so the
           expiry can be extended or the access revoked in Azure without changing any URL, and no key is in the repo. Only exports are ever listed (never the original recording).
  --skip-upload : with --site, do not upload again (the files are already there).
  --check : only list what would be uploaded.
Writes assets/publish_links.json and publish_links.js (git-ignored; the Publish page shows the links locally; signed URLs must never be committed)."""
import datetime, json, os, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
VAULT = os.environ.get("KIT_VAULT", "dp-kv-deliverypilot"); days = int(arg("--days", 30)); login = "--login" in sys.argv
reg = json.load(open(ROOT / "assets/exports.json")); want = int(arg("--version", 0)) or max(e["v"] for e in reg if e.get("file"))
items = [e for e in reg if e.get("file") and e["v"] == want]
key = lambda e: "v%d" % e["v"] + ("" if e.get("platform", "youtube") == "youtube" else "-" + e["platform"])
for e in items: print(f"  {key(e):14s} {e['file']}  ({e['seconds']} s, {e['size_mb']} MB)")
if "--check" in sys.argv or not items: sys.exit(0)
def secret(n):
    return subprocess.run(["az", "keyvault", "secret", "show", "--vault-name", VAULT, "--name", n, "--query", "value", "-o", "tsv"], capture_output=True, text=True).stdout.strip()
acc, cont = arg("--account") or secret("cmf-exports-storage-account"), arg("--container") or secret("cmf-exports-container")
if not acc or not cont: sys.exit("Key Vault has no cmf-exports-* secrets yet. Run once:  ! scripts/setup_azure_exports.sh")
env = dict(os.environ); common = ["--account-name", acc]
if login: common += ["--auth-mode", "login"]
else: env["AZURE_STORAGE_KEY"] = secret("cmf-exports-storage-key")        # passed through the environment, never printed
if login and "--create-container" in sys.argv: subprocess.check_call(["az", "storage", "container", "create", *common, "-n", cont, "--public-access", "off", "-o", "none"], env=env)
if not login and not env["AZURE_STORAGE_KEY"]: sys.exit("storage key missing in Key Vault; run scripts/setup_azure_exports.sh")
expiry = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=min(days, 7) if login else days)).strftime("%Y-%m-%dT%H:%MZ")
site = "--site" in sys.argv
if site:   # stored access policy: read only, expiry controlled in Azure (extend with `az storage container policy update`, revoke by deleting it)
    pol_exp = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=int(arg("--policy-days", 90)))).strftime("%Y-%m-%dT%H:%MZ")
    for verb in ("create", "update"):
        r = subprocess.run(["az", "storage", "container", "policy", verb, "--container-name", cont, "--name", "site-player", "--permissions", "r", "--expiry", pol_exp, *common], capture_output=True, text=True, env=env)
        if r.returncode == 0: break
    if r.returncode != 0: sys.exit("could not create the stored access policy: " + r.stderr[-200:])
site_links = {}
links = json.load(open(ROOT / "assets/publish_links.json")) if (ROOT / "assets/publish_links.json").exists() else {}
for e in items:
    blob = pathlib.Path(e["file"]).name
    if "--skip-upload" not in sys.argv: subprocess.check_call(["az", "storage", "blob", "upload", *common, "-c", cont, "-n", blob, "-f", str(ROOT / e["file"]), "--overwrite", "false", "--no-progress", "-o", "none"], env=env)
    sas = ["az", "storage", "blob", "generate-sas", *common, "-c", cont, "-n", blob, "--permissions", "r", "--expiry", expiry, "--https-only", "--full-uri", "-o", "tsv"]
    if login: sas += ["--as-user"]
    url = subprocess.run(sas, capture_output=True, text=True, env=env).stdout.strip()
    links[key(e)] = {"url": url, "expires": expiry[:10], "blob": blob}; print(f"  uploaded {blob}; link expires {expiry[:10]}")
    if site:
        su = subprocess.run(["az", "storage", "blob", "generate-sas", *common, "-c", cont, "-n", blob, "--policy-name", "site-player", "--https-only", "--full-uri", "-o", "tsv"], capture_output=True, text=True, env=env).stdout.strip()
        site_links[key(e)] = {"url": su, "seconds": e["seconds"], "size_mb": e["size_mb"], "policy_expires": pol_exp[:10]}
(ROOT / "assets/publish_links.json").write_text(json.dumps(links, indent=1))
(ROOT / "publish_links.js").write_text("window.PUBLISH_LINKS = " + json.dumps(links) + ";")
if site:
    (ROOT / "azure_links.js").write_text("// Public player links (read-only, stored access policy site-player). Exports only; the original recording is never listed.\nwindow.AZURE_LINKS = " + json.dumps(site_links, indent=1) + ";")
    print(f"azure_links.js written for the public player ({len(site_links)} exports; policy expires {pol_exp[:10]})")
print("Links written to publish_links.js (local only). Open publish.html to review, then share the post links with the assistant to fill the placeholders.")
