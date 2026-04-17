#!/bin/bash
# Render build script — runs as root in the build container
set -euo pipefail

echo "==> Installing system dependencies..."
apt-get update -y
apt-get install -y --no-install-recommends \
  libgles2 \
  libgl1 \
  libglx-mesa0 \
  libglib2.0-0
ldconfig

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
