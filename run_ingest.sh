#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x venv/bin/python ]]; then
  echo "venv not found. Run: ./setup.sh"
  exit 1
fi

PYTHON=./venv/bin/python
EXIT=0

"$PYTHON" youtube_ingest.py || EXIT=1
"$PYTHON" telegram_fetch_links.py || EXIT=1
"$PYTHON" instagram_ingest.py || EXIT=1

exit "$EXIT"
