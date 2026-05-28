#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d venv ]]; then
  python3 -m venv venv
fi

./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

mkdir -p temp Inbox/Youtube Inbox/Instagram Inbox/_archived

if ! command -v ffmpeg &>/dev/null; then
  echo "⚠️  ffmpeg not found. Install with: brew install ffmpeg"
else
  echo "✓ ffmpeg found"
fi

echo "✓ Setup complete. Run: ./run_ingest.sh"
