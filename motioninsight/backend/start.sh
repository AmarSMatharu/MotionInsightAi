#!/bin/bash
# MotionInsight AI — local development startup
# Run from the backend/ directory: bash start.sh

set -euo pipefail

echo "==> Checking Python..."
if ! command -v python3 &> /dev/null; then
  echo "ERROR: Python 3 not found. Please install Python 3.10+."
  exit 1
fi

echo "==> Installing dependencies..."
pip install -r requirements.txt --quiet

echo "==> Checking for MediaPipe pose model..."
if [ ! -f "models/pose_landmarker_full.task" ]; then
  echo "==> Downloading pose_landmarker_full.task (~30 MB)..."
  mkdir -p models
  curl -fsSL -o models/pose_landmarker_full.task \
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
  echo "==> Model downloaded."
fi

if [ ! -f ".env" ]; then
  echo ""
  echo "WARNING: No .env file found. Create one with:"
  echo "  echo 'GROQ_API_KEY=your_key_here' > .env"
  echo ""
fi

echo "==> Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
