# Ultra Depth local server

This runs `Depth Pro` on your Mac and exposes a simple HTTP API for the Android app.

## Files

- `app.py`: FastAPI server
- `setup.sh`: installs Python dependencies and downloads the official Apple checkpoint
- `run_local.sh`: starts the server on port `8000`

## Setup

```bash
cd /Users/weiyuankong/Projects/real_depth_photo/ultra_depth_server
chmod +x setup.sh run_local.sh
./setup.sh
```

This creates `./.venv` and keeps the server dependencies isolated.

## Run

```bash
cd /Users/weiyuankong/Projects/real_depth_photo/ultra_depth_server
./run_local.sh
```

Safer low-RAM options:

```bash
DEPTH_PRO_DEVICE=cpu DEPTH_PRO_MAX_DIM=1024 ./run_local.sh
```

Defaults:
- `DEPTH_PRO_PRELOAD=1`
- `DEPTH_PRO_MAX_DIM=1152`
- device auto-selects `mps`, then `cuda`, then `cpu`

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Inference:

```bash
curl -X POST \
  -F image=@/Users/weiyuankong/Projects/zero_waste_photo/2.jpg \
  http://127.0.0.1:8000/v1/depth \
  --output /tmp/depth.png
```

## Phone access

If the app runs on a physical Android phone, use your Mac's LAN IP, not `localhost`.

Example:

```text
http://192.168.1.23:8000
```

`localhost` only works if the app and server run on the same machine. For the Android emulator, `http://10.0.2.2:8000` is the correct host alias.
