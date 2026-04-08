import cv2
import numpy as np

POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (24, 26), (26, 28),
    (27, 29), (29, 31), (28, 30), (30, 32),
    (15, 17), (15, 19), (15, 21), (16, 18), (16, 20), (16, 22),
]

def draw_pose_on_image(image_bgr, pose_landmarks_list):
    annotated = image_bgr.copy()
    h, w = annotated.shape[:2]
    if not pose_landmarks_list:
        return annotated
    for landmarks in pose_landmarks_list:
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx >= len(landmarks) or end_idx >= len(landmarks):
                continue
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            if start.visibility < 0.3 or end.visibility < 0.3:
                continue
            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)
            cv2.line(annotated, (x1, y1), (x2, y2), (0, 230, 200), 2, cv2.LINE_AA)
        for lmk in landmarks:
            if lmk.visibility < 0.3:
                continue
            cx, cy = int(lmk.x * w), int(lmk.y * h)
            cv2.circle(annotated, (cx, cy), 4, (0, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 0), 1, cv2.LINE_AA)
    return annotated

def bgr_to_rgb(image_bgr):
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)