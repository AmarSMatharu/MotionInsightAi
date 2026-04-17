#!/bin/bash
# Render build script — runs as root in the build container
set -euo pipefail

echo "==> Installing and bundling system libraries..."
apt-get update -y
apt-get install -y --no-install-recommends libgles2 libgl1 libglx-mesa0 libglib2.0-0
mkdir -p libs
cp -P /usr/lib/x86_64-linux-gnu/libGLESv2.so* libs/
cp -P /usr/lib/x86_64-linux-gnu/libGL.so* libs/ 2>/dev/null || true
cp -P /usr/lib/x86_64-linux-gnu/libGLX.so* libs/ 2>/dev/null || true
cp -P /usr/lib/x86_64-linux-gnu/libglib-2.0.so* libs/ 2>/dev/null || true
echo "==> Bundled libs: $(ls libs/)"

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Checking for MediaPipe pose model..."
if [ ! -f "models/pose_landmarker_full.task" ]; then
  echo "==> Downloading pose_landmarker_full.task..."
  mkdir -p models
  curl -fsSL -o models/pose_landmarker_full.task \
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
  echo "==> Model downloaded."
else
  echo "==> Model already present, skipping download."
fi

echo "==> Build complete."
