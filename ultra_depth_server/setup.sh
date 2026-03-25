#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3.10 -m venv .venv --system-site-packages
fi

source .venv/bin/activate
python -m pip install fastapi uvicorn python-multipart timm pillow_heif

if [[ ! -f vendor/ml-depth-pro/checkpoints/depth_pro.pt ]]; then
  mkdir -p vendor/ml-depth-pro/checkpoints
  if command -v wget >/dev/null 2>&1; then
    (
      cd vendor/ml-depth-pro
      source ./get_pretrained_models.sh
    )
  else
    curl -L https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt \
      -o vendor/ml-depth-pro/checkpoints/depth_pro.pt
  fi
fi

echo "Depth Pro server dependencies and checkpoint are ready."
