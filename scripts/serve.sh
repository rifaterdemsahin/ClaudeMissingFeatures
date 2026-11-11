#!/bin/zsh
# Serve the site at http://localhost:8000 with video seeking (Range) support.
# Usage: scripts/serve.sh [path/to/video.mp4]   (default: ~/Downloads/claude-missing-features-1080p.mp4)
cd "$(dirname "$0")/.." || exit 1
VIDEO="${1:-$HOME/Downloads/claude-missing-features-1080p.mp4}"
[ -e long.mp4 ] || ln "$VIDEO" long.mp4 || { echo "cannot link $VIDEO"; exit 1; }   # long.mp4 is git-ignored (*.mp4)
[ -L export.mp4 ] || ln -s remotion/out/long.mp4 export.mp4   # latest Remotion export (symlink: always the newest render; git-ignored via *.mp4)
echo "Site:   http://localhost:8000/index.html"
echo "Player: http://localhost:8000/player.html"
npx --yes http-server . -p 8000 -c-1 --cors -s
