#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  echo "Missing .venv. Run ./setup.sh first." >&2
  exit 1
fi

source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
