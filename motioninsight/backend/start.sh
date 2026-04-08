#!/bin/bash
# MotionInsight AI - Backend Startup Script
# Run from the backend/ directory

set -e

echo "🚀 Starting MotionInsight AI Backend..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for model file
if [ ! -f "models/pose_landmarker_full.task" ]; then
    echo "📥 Downloading MediaPipe pose model..."
    mkdir -p models
    curl -L -o models/pose_landmarker_full.task \
      "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
    echo "✅ Model downloaded."
fi

# Start server
echo "✅ Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
