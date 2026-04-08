from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import MODEL_PATH
from analyzers.metrics import extract_pose_metrics_from_landmarks
from utils.drawing import draw_pose_on_image
from utils.ai_describer import generate_ai_description


def create_image_landmarker():
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_poses=1,
    )
    return vision.PoseLandmarker.create_from_options(options)


def analyze_image(image_path: str):
    landmarker = create_image_landmarker()

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        raise ValueError("Invalid image")

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    result = landmarker.detect(mp_image)

    if not result.pose_landmarks:
        return {
            "success": False,
            "metrics": None,
            "description": "No pose detected",
            "annotated_image": image_rgb,
            "message": "No pose detected",
        }

    metrics = extract_pose_metrics_from_landmarks(result.pose_landmarks[0])
    annotated_bgr = draw_pose_on_image(image_bgr, result.pose_landmarks)
    annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

    try:
        description = generate_ai_description(
            mode="single_image",
            metrics=metrics,
            image_arrays_rgb=[annotated_rgb],
            extra_context="This is a single uploaded image with pose landmarks drawn on top.",
        )
    except Exception as e:
        description = f"AI description unavailable: {e}"

    return {
        "success": True,
        "metrics": metrics,
        "description": description,
        "annotated_image": annotated_rgb,
        "message": "Pose detected successfully.",
    }