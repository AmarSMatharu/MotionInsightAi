from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import MODEL_PATH, DEFAULT_SAMPLE_EVERY_N_FRAMES
from analyzers.metrics import (
    extract_pose_metrics_from_landmarks,
    aggregate_metric_dicts,
)
from utils.drawing import draw_pose_on_image
from utils.ai_describer import generate_ai_description


def create_video_landmarker():
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}. "
            "Download pose_landmarker_heavy.task and place it in /models."
        )

    base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return vision.PoseLandmarker.create_from_options(options)


def analyze_video(
    video_path: str,
    sample_every_n_frames: int = DEFAULT_SAMPLE_EVERY_N_FRAMES,
):
    landmarker = create_video_landmarker()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    frame_idx = 0
    metric_rows = []
    preview_frames = []

    while True:
        success, frame_bgr = cap.read()
        if not success:
            break

        if frame_idx % sample_every_n_frames != 0:
            frame_idx += 1
            continue

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int((frame_idx / fps) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if result.pose_landmarks:
            metrics = extract_pose_metrics_from_landmarks(result.pose_landmarks[0])
            metrics["frame_index"] = frame_idx
            metrics["timestamp_seconds"] = round(frame_idx / fps, 2)
            metric_rows.append(metrics)

            if len(preview_frames) < 3:
                annotated_bgr = draw_pose_on_image(frame_bgr, result.pose_landmarks)
                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
                preview_frames.append(annotated_rgb)

        frame_idx += 1

    cap.release()

    if not metric_rows:
        return {
            "success": False,
            "summary_metrics": None,
            "description": "No pose could be detected in the sampled video frames.",
            "frame_metrics": [],
            "preview_frames": [],
            "message": "No pose detected in sampled video frames.",
        }

    pure_metric_rows = []
    for row in metric_rows:
        pure_metric_rows.append(
            {
                "left_elbow_angle": row["left_elbow_angle"],
                "right_elbow_angle": row["right_elbow_angle"],
                "left_knee_angle": row["left_knee_angle"],
                "right_knee_angle": row["right_knee_angle"],
                "avg_elbow_angle": row["avg_elbow_angle"],
                "avg_knee_angle": row["avg_knee_angle"],
                "left_right_elbow_diff": row["left_right_elbow_diff"],
                "left_right_knee_diff": row["left_right_knee_diff"],
            }
        )

    summary_metrics = aggregate_metric_dicts(pure_metric_rows)

    try:
        if preview_frames:
            description = generate_ai_description(
                mode="single_video",
                metrics=summary_metrics,
                image_arrays_rgb=preview_frames[:3],
                extra_context=(
                    "These are representative sampled frames from one uploaded video. "
                    "Use them with the summary pose metrics to describe movement, posture, and symmetry."
                ),
            )
        else:
            description = generate_ai_description(
                mode="single_video",
                metrics=summary_metrics,
                extra_context=(
                    "No preview frames were available. Describe the movement only from the pose metrics."
                ),
            )
    except Exception as e:
        description = f"AI description unavailable: {e}"

    return {
        "success": True,
        "summary_metrics": summary_metrics,
        "description": description,
        "frame_metrics": metric_rows,
        "preview_frames": preview_frames,
        "message": "Video analyzed successfully.",
    }