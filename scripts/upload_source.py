#!/usr/bin/env python3
"""Save raw footage and source artifacts to a per-video private Azure Blob container (<slug>-source).
Runs at the start of a project (and as artifacts update).
Keys come from Azure Key Vault (cmf-exports-storage-account / cmf-exports-storage-key); never printed or committed.
Usage:
  python3 scripts/upload_source.py [--folder ~/Downloads/<Project>] [--artifacts-only] [--raw-only] [--force]
"""
import json, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VAULT = os.environ.get("KIT_VAULT", "dp-kv-deliverypilot")

arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d

def get_secret(n):
    return subprocess.run(["az", "keyvault", "secret", "show", "--vault-name", VAULT, "--name", n, "--query", "value", "-o", "tsv"], capture_output=True, text=True).stdout.strip()

# Read project configuration dynamically (no hardcoded project names)
proj_file = ROOT / "remotion/src/project.json"
P = json.loads(proj_file.read_text()) if proj_file.exists() else {}
slug = P.get("slug") or ROOT.name.lower().replace(" ", "-")
title = P.get("title") or ROOT.name

container = arg("--container") or f"{slug}-source"
artifacts_only = "--artifacts-only" in sys.argv
raw_only = "--raw-only" in sys.argv
force = "--force" in sys.argv

account = arg("--account") or get_secret("cmf-exports-storage-account")
storage_key = get_secret("cmf-exports-storage-key")

if not account or not storage_key:
    sys.exit("Azure storage account or key missing in Key Vault (cmf-exports-storage-*).")

env = dict(os.environ)
env["AZURE_STORAGE_KEY"] = storage_key
common = ["--account-name", account]

# Ensure container exists (private)
print(f"Ensuring per-video Azure container '{container}' exists...")
subprocess.run(["az", "storage", "container", "create", *common, "--name", container, "--public-access", "off", "-o", "none"], env=env, check=True)

uploaded = 0
bytes_total = 0

def upload_file(local_path, blob_name):
    global uploaded, bytes_total
    p = pathlib.Path(local_path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        return False
    size = p.stat().st_size
    size_mb = size / (1024 * 1024)
    # Check if already exists unless force
    if not force:
        exists_check = subprocess.run(["az", "storage", "blob", "exists", *common, "--container-name", container, "--name", blob_name, "--query", "exists", "-o", "tsv"], env=env, capture_output=True, text=True).stdout.strip()
        if exists_check == "true":
            print(f"  [cached] {blob_name} ({size_mb:.1f} MB already in {container})")
            return False

    print(f"  Uploading {p.name} -> {blob_name} ({size_mb:.1f} MB)...")
    cmd = ["az", "storage", "blob", "upload", *common, "--container-name", container, "--name", blob_name, "--file", str(p), "--overwrite", "true" if force else "false", "--no-progress", "-o", "none"]
    subprocess.run(cmd, env=env, check=True)
    uploaded += 1
    bytes_total += size
    return True

# 1. Source Artifacts
if not raw_only:
    print(f"\n📦 Saving source artifacts to {container}...")
    candidate_artifacts = [
        ROOT / "REPORT.md",
        ROOT / "BRIEF.md",
        ROOT / "metadata.md",
        ROOT / "EDL.md",
        ROOT / "remotion/src/project.json",
        ROOT / "remotion/src/overlays.json",
        ROOT / "remotion/src/cuts.json",
        ROOT / "remotion/src/variants.json",
    ]
    # Add all files in assets/
    if (ROOT / "assets").exists():
        candidate_artifacts.extend([p for p in (ROOT / "assets").iterdir() if p.is_file() and not p.name.startswith(".")])

    for f in sorted(set(candidate_artifacts)):
        if f.exists() and f.is_file():
            rel_name = f.name if f.parent == ROOT else f"{f.parent.name}/{f.name}"
            upload_file(f, f"artifacts/{rel_name}")

# 2. Raw Footage
if not artifacts_only:
    print(f"\n🎥 Saving raw footage to {container}...")
    # Find raw footage directory: passed via --folder, or ~/Downloads/<Title>, or check assets/base_info.json
    folder_arg = arg("--folder")
    candidates_dirs = []
    if folder_arg:
        candidates_dirs.append(pathlib.Path(folder_arg).expanduser())
    candidates_dirs.append(pathlib.Path.home() / "Downloads" / title)
    candidates_dirs.append(pathlib.Path.home() / "Downloads" / slug)

    base_info_file = ROOT / "assets/base_info.json"
    if base_info_file.exists():
        try:
            bi = json.loads(base_info_file.read_text())
            for c in bi.get("clips", []):
                candidates_dirs.append(pathlib.Path(c).expanduser().parent)
            if bi.get("voice"):
                candidates_dirs.append(pathlib.Path(bi["voice"]).expanduser().parent)
        except Exception:
            pass

    found_dir = None
    for d in candidates_dirs:
        if d.exists() and d.is_dir():
            found_dir = d
            break

    if found_dir:
        print(f"Found source media folder: {found_dir}")
        for ext in ("*.mp4", "*.mov", "*.WAV", "*.wav", "*.m4a"):
            for mf in sorted(found_dir.glob(ext)):
                upload_file(mf, f"raw/{mf.name}")
    else:
        print("Note: Source footage directory not located automatically; specify with --folder if needed.")

    # Base video if present in ~/Downloads
    base_video = pathlib.Path.home() / "Downloads" / f"{slug}-1080p.mp4"
    if base_video.exists():
        upload_file(base_video, f"raw/{base_video.name}")

mb_uploaded = bytes_total / (1024 * 1024)
print(f"\n✅ Azure source backup complete: {uploaded} files uploaded ({mb_uploaded:.1f} MB) to container '{container}'.")
