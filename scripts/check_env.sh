#!/bin/zsh
# Check everything this workflow needs on the MacBook and print how to install what is missing.
# Usage: scripts/check_env.sh        (exit 1 if a REQUIRED item is missing)
cd "$(dirname "$0")/.." || exit 1
miss=0
row(){ # name required(y/n) version-or-empty install-hint
  if [ -n "$3" ]; then printf "✅ %-22s %s\n" "$1" "$3"; else
    if [ "$2" = y ]; then printf "❌ %-22s MISSING (required)  → %s\n" "$1" "$4"; miss=1; else printf "⚪ %-22s not found (optional)  → %s\n" "$1" "$4"; fi; fi; }
v(){ command -v "$1" >/dev/null 2>&1 && "$@" 2>&1 | head -1 | cut -c1-60; }
echo "== Core tools"
row "ffmpeg"   y "$(v ffmpeg -version | awk '{print $3}')" "brew install ffmpeg"
row "ffprobe"  y "$(command -v ffprobe >/dev/null && echo present)" "brew install ffmpeg"
row "python3"  y "$(v python3 --version)" "brew install python"
row "node"     y "$(v node -v)" "brew install node"
row "npm"      y "$(v npm -v)" "brew install node"
row "git"      y "$(v git --version)" "xcode-select --install"
row "swiftc"   y "$(command -v swiftc >/dev/null && swiftc --version 2>&1 | head -1 | cut -c1-50)" "xcode-select --install   (Apple Vision OCR needs it)"
echo "== Speech and noise"
row "whisper"  y "$(command -v whisper >/dev/null && echo present)" "pip install openai-whisper   (or: pipx install openai-whisper)"
ls ~/.cache/whisper/small.pt >/dev/null 2>&1 && row "whisper model small" n "$(du -h ~/.cache/whisper/small.pt | cut -f1) cached" "" || row "whisper model small" n "" "downloads automatically on the first run (about 460 MB)"
PYV=~/.cache/cmf-venv/bin/python
if [ -x $PYV ]; then row "python venv (cmf-venv)" n "$($PYV -c 'import importlib.metadata as m;print(*[x+" "+m.version(x) for x in ("numpy","scipy","noisereduce","soundfile")])' 2>&1 | tail -1)" "created automatically by build_base.py / denoise_audio.py"
else row "python venv (cmf-venv)" n "" "created automatically on first run of scripts/build_base.py or denoise_audio.py (installs numpy, scipy, noisereduce, soundfile)"; fi
echo "== Video build"
row "Google Chrome" y "$([ -d '/Applications/Google Chrome.app' ] && echo installed)" "brew install --cask google-chrome   (Remotion renders with it)"
[ -d remotion/node_modules ] && row "remotion deps" y "$(cd remotion && node -e 'console.log("remotion",require("remotion/package.json").version)' 2>/dev/null)" "" || row "remotion deps" y "" "cd remotion && npm install"
[ -L remotion/public/base.mp4 ] && echo "⚠️  remotion/public/base.mp4 is a symlink: use a hard link (ln src remotion/public/base.mp4)"
[ -e remotion/public/base.mp4 ] && row "remotion/public/base.mp4" n "present" "" || row "remotion/public/base.mp4" n "" "ln ~/Downloads/<slug>-1080p.mp4 remotion/public/base.mp4   (created by pipeline.sh)"
echo "== Cloud and sharing (only for the kit, Key Vault and Pages)"
row "gh (GitHub CLI)" n "$(command -v gh >/dev/null && (gh auth status >/dev/null 2>&1 && echo "logged in" || echo "installed, run: gh auth login"))" "brew install gh && gh auth login"
row "az (Azure CLI)"  n "$(command -v az >/dev/null && (az account show >/dev/null 2>&1 && echo "logged in" || echo "installed, run: az login"))" "brew install azure-cli && az login"
row "rclone"          n "$(command -v rclone >/dev/null && (rclone listremotes 2>/dev/null | grep -q gdrive-shared && echo "remote gdrive-shared found" || echo "installed, no gdrive-shared remote: rclone config"))" "brew install rclone && rclone config"
echo "== Machine"
printf "✅ %-22s %s cores, %s GB RAM, %s GB free on this disk\n" "hardware" "$(sysctl -n hw.ncpu)" "$(( $(sysctl -n hw.memsize) / 1073741824 ))" "$(df -g . | awk 'NR==2{print $4}')"
for p in 3000 8000; do lsof -ti :$p >/dev/null 2>&1 && echo "ℹ️  port $p in use (Remotion Studio is 3000, site/player is 8000)" || echo "✅ port $p free"; done
echo; [ $miss = 0 ] && echo "All required items present." || echo "Some REQUIRED items are missing: install them with the hints above."
exit $miss
