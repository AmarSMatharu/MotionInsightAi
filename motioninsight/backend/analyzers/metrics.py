import numpy as np

LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28


def calculate_angle(a, b, c):
    ba = np.array([a[0] - b[0], a[1] - b[1]], dtype=np.float32)
    bc = np.array([c[0] - b[0], c[1] - b[1]], dtype=np.float32)

    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-8
    cosine_angle = np.dot(ba, bc) / denom
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    return float(np.degrees(np.arccos(cosine_angle)))


def get_landmark_xy(landmarks, idx):
    return landmarks[idx].x, landmarks[idx].y


def extract_pose_metrics_from_landmarks(landmarks):
    metrics = {
        "left_elbow_angle": calculate_angle(
            get_landmark_xy(landmarks, LEFT_SHOULDER),
            get_landmark_xy(landmarks, LEFT_ELBOW),
            get_landmark_xy(landmarks, LEFT_WRIST),
        ),
        "right_elbow_angle": calculate_angle(
            get_landmark_xy(landmarks, RIGHT_SHOULDER),
            get_landmark_xy(landmarks, RIGHT_ELBOW),
            get_landmark_xy(landmarks, RIGHT_WRIST),
        ),
        "left_knee_angle": calculate_angle(
            get_landmark_xy(landmarks, LEFT_HIP),
            get_landmark_xy(landmarks, LEFT_KNEE),
            get_landmark_xy(landmarks, LEFT_ANKLE),
        ),
        "right_knee_angle": calculate_angle(
            get_landmark_xy(landmarks, RIGHT_HIP),
            get_landmark_xy(landmarks, RIGHT_KNEE),
            get_landmark_xy(landmarks, RIGHT_ANKLE),
        ),
    }

    metrics["avg_elbow_angle"] = (
        metrics["left_elbow_angle"] + metrics["right_elbow_angle"]
    ) / 2
    metrics["avg_knee_angle"] = (
        metrics["left_knee_angle"] + metrics["right_knee_angle"]
    ) / 2
    metrics["left_right_elbow_diff"] = abs(
        metrics["left_elbow_angle"] - metrics["right_elbow_angle"]
    )
    metrics["left_right_knee_diff"] = abs(
        metrics["left_knee_angle"] - metrics["right_knee_angle"]
    )

    return {k: round(v, 2) for k, v in metrics.items()}


def aggregate_metric_dicts(metric_dicts):
    if not metric_dicts:
        return None

    keys = metric_dicts[0].keys()
    out = {}

    for key in keys:
        values = [d[key] for d in metric_dicts if key in d]
        out[key] = round(float(np.mean(values)), 2)

    out["frames_or_images_used"] = len(metric_dicts)
    return out


def compare_metric_sets(first_metrics, second_metrics, first_name="First", second_name="Second"):
    comparison = []

    shared_keys = [
        "left_elbow_angle",
        "right_elbow_angle",
        "left_knee_angle",
        "right_knee_angle",
        "avg_elbow_angle",
        "avg_knee_angle",
        "left_right_elbow_diff",
        "left_right_knee_diff",
    ]

    for key in shared_keys:
        a = first_metrics.get(key)
        b = second_metrics.get(key)

        if a is None or b is None:
            comparison.append(
                {"metric": key, first_name: a, second_name: b, "difference": None}
            )
        else:
            comparison.append(
                {
                    "metric": key,
                    first_name: a,
                    second_name: b,
                    "difference": round(b - a, 2),
                }
            )

    return comparison