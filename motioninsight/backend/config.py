from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "pose_landmarker_full.task"

SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png"]
SUPPORTED_VIDEO_TYPES = ["mp4", "mov", "avi", "mkv"]

DEFAULT_SAMPLE_EVERY_N_FRAMES = 10
APP_TITLE = "MotionInsight AI"

GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"