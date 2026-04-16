import os
from pathlib import Path

# ── Headless display fix for OpenCV on Linux servers ─────────────────────────
# Set only when DISPLAY is not already configured (i.e. headless servers).
if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":0"

# ── Suppress OpenEXR (not needed, avoids spurious warnings) ──────────────────
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "0")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "pose_landmarker_full.task"

# ── Supported file types ──────────────────────────────────────────────────────
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png"]
SUPPORTED_VIDEO_TYPES = ["mp4", "mov", "avi", "mkv"]

# ── Upload limits ─────────────────────────────────────────────────────────────
MAX_IMAGE_BYTES = 50 * 1024 * 1024   # 50 MB
MAX_VIDEO_BYTES = 200 * 1024 * 1024  # 200 MB

# ── Analysis defaults ─────────────────────────────────────────────────────────
DEFAULT_SAMPLE_EVERY_N_FRAMES = 10
MIN_SAMPLE_EVERY_N_FRAMES = 1
MAX_SAMPLE_EVERY_N_FRAMES = 60

# ── App metadata ──────────────────────────────────────────────────────────────
APP_TITLE = "MotionInsight AI"

# ── AI model ─────────────────────────────────────────────────────────────────
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
