#!/usr/bin/env bash
# One-time setup on a clean Linux machine (Debian/Ubuntu, Python >= 3.10).
# Installs ffmpeg (if missing), Python packages, Kokoro TTS model files and Poppins fonts.
# Usage:  bash tools/setup.sh            (from the repo root)
# Optional: PIP_FLAGS="--break-system-packages" bash tools/setup.sh   (system Python without venv)
set -euo pipefail
cd "$(dirname "$0")"

# 1) ffmpeg (libx264 + aac)
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "installing ffmpeg..."
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -y && $SUDO apt-get install -y ffmpeg
fi

# 2) Python packages (kokoro-onnx pulls onnxruntime, phonemizer, espeakng-loader;
#    espeak-ng is bundled by espeakng-loader, no apt package needed)
python3 -m pip install ${PIP_FLAGS:-} -r requirements.txt

# 3) Kokoro v1.0 model files (~350 MB) from the kokoro-onnx GitHub release
mkdir -p models
BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ ! -s "models/$f" ]; then
    echo "downloading $f..."
    curl -fsSL --retry 3 -o "models/$f.part" "$BASE/$f" && mv "models/$f.part" "models/$f"
  fi
done

# 4) Poppins fonts (SIL Open Font License) from google/fonts
mkdir -p fonts
for f in Poppins-Bold.ttf Poppins-Medium.ttf; do
  if [ ! -s "fonts/$f" ]; then
    curl -fsSL --retry 3 -o "fonts/$f" "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/$f"
  fi
done

# 5) smoke test: TTS loads and speaks
python3 - <<'EOF'
from kokoro_onnx import Kokoro
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")
s, sr = k.create("Setup works.", voice="am_michael", speed=1.0, lang="en-us")
print(f"TTS OK: {len(s)/sr:.2f}s at {sr} Hz")
EOF
echo "setup done"
