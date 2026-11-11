#!/usr/bin/env python3
"""AI Thumbnail generator (fal.ai / FLUX): generate high-CTR curiosity-triggering thumbnails.
Usage: python3 scripts/generate_thumbnail.py [--prompt "custom prompt"] [--out assets/thumbnail_fal.jpg]
Reads: FAL_KEY from environment or Azure Key Vault (secret FAL-AI-KEY in dp-kv-deliverypilot).

Abstract Curiosity Thumbnail Formula:
- [Media Format & Style]: High-converting YouTube thumbnail, [Aesthetic Style] aesthetic, 16:9 aspect ratio.
- [Left Side - Subject & Emotion]: [Subject/Persona] displaying [Emotion] while interacting with [Hardware/Device], accompanied by [Symbolic Element].
- [Right Side - The Problem/Object]: Enlarged 3D floating [UI / Product Interface] highlighting [Working Features] vs [Missing/Broken Feature].
- [Top/Overlay - Typography]: Bold, high-contrast hook text reading "[BRAND/SUBJECT] [CORE CONFLICT/QUESTION]?!".
- [Lighting & Atmosphere]: Dramatic studio rim lighting, [Accent Effects: embers, sparks, glow], warm background ambience.
"""
import argparse, json, os, pathlib, subprocess, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.load(open(ROOT / "remotion/src/project.json")) if (ROOT / "remotion/src/project.json").exists() else {}

def get_fal_key():
    k = os.environ.get("FAL_KEY")
    if k: return k
    try:
        vault = os.environ.get("KIT_VAULT", "dp-kv-deliverypilot")
        r = subprocess.run(["az", "keyvault", "secret", "show", "--vault-name", vault, "--name", "FAL-AI-KEY", "--query", "value", "-o", "tsv"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None

def build_curiosity_prompt():
    title = P.get("title", "Missing AI Feature")
    return (
        f"A dramatic, cinematic YouTube thumbnail for a tech video about '{title}'. "
        "A sleek dark-mode AI software interface on an ultrawide display showing categorized tiles, "
        "with one missing empty glowing dashed slot emitting vibrant amber neon particles and an inquisitive glowing magnifying glass, "
        "dramatic high-contrast lighting, deep obsidian blacks and vivid neon accents, 8k resolution, visual mystery and curiosity gap, 16:9 aspect ratio."
    )

def main():
    parser = argparse.ArgumentParser(description="Generate curiosity-triggering thumbnail with fal.ai")
    parser.add_argument("--prompt", default="", help="Custom generation prompt")
    parser.add_argument("--out", default="assets/thumbnail_fal.jpg", help="Output path")
    parser.add_argument("--model", default="fal-ai/flux/schnell", help="fal.ai model ID")
    args = parser.parse_args()

    prompt = args.prompt or build_curiosity_prompt()
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    key = get_fal_key()
    if not key:
        print("Warning: FAL_KEY not found in environment or Key Vault. Ensure FAL-AI-KEY is present.")
        sys.exit(1)

    print(f"Generating thumbnail via fal.ai ({args.model})...")
    print(f"Prompt: {prompt[:80]}...")

    req = urllib.request.Request(
        f"https://fal.run/{args.model}",
        headers={
            "Authorization": f"Key {key}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "prompt": prompt,
            "image_size": "landscape_16_9",
            "num_images": 1,
            "enable_safety_checker": False
        }).encode("utf-8")
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            images = data.get("images", [])
            if images and "url" in images[0]:
                img_url = images[0]["url"]
                print(f"Downloading generated image from: {img_url[:60]}...")
                with urllib.request.urlopen(img_url) as img_resp:
                    out_path.write_bytes(img_resp.read())
                print(f"✅ Saved AI thumbnail to {out_path}")
            else:
                print("No image URL returned in response:", data)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"fal.ai API returned HTTP {e.code}: {body}")
        if e.code == 401:
            print("Note: FAL-AI-KEY credential is expired/unauthorized. Update FAL-AI-KEY in Key Vault.")
        sys.exit(1)
    except Exception as e:
        print("Error calling fal.ai:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
