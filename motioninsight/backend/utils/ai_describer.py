import os
import io
import json
import base64
import logging
from typing import Any

from dotenv import load_dotenv
import numpy as np
from PIL import Image
from groq import Groq

from config import GROQ_VISION_MODEL

logger = logging.getLogger(__name__)

load_dotenv()


def _numpy_rgb_to_data_url(image_rgb: np.ndarray) -> str:
    pil_img = Image.fromarray(image_rgb.astype("uint8"))
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=90)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def _file_to_data_url(image_path: str) -> str:
    ext = image_path.split(".")[-1].lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{encoded}"


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found.")
    return Groq(api_key=api_key)


def _safe_json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def generate_ai_description(
    *,
    mode: str,
    metrics: dict | None = None,
    comparison_metrics: dict | None = None,
    image_paths: list[str] | None = None,
    image_arrays_rgb: list[np.ndarray] | None = None,
    extra_context: str = "",
) -> str:
    client = _get_client()

    if mode in ("compare_images", "compare_videos"):
        prompt = f"""You are an expert movement coach and biomechanics analyst.

You are comparing BEFORE and AFTER images/video.

Your response must have exactly two sections:

First, write 2-3 sentences describing what you observe about the movement or posture in both images — what the person is doing, how their body is positioned, and what changed between before and after.

Then write exactly 3 coaching feedback points as a numbered list. Each point should be a specific, actionable suggestion the person can act on. Format them like:
1. [feedback point]
2. [feedback point]
3. [feedback point]

Keep the tone encouraging and practical. Do not use headers or labels — just write the description paragraph first, then the numbered list.
Do not mention joint angles or technical metrics.

Extra context: {extra_context}
"""
    else:
        prompt = f"""You are an expert movement coach and biomechanics analyst.

Look at the image carefully and analyze the person's posture and movement.

Your response must have exactly two sections:

First, write 2-3 sentences describing what you observe — what the person is doing, how their body is positioned, their posture, and any notable aspects of their movement or form.

Then write exactly 3 coaching feedback points as a numbered list. Each should be specific and actionable — something the person can actually do to improve. Format them like:
1. [feedback point]
2. [feedback point]
3. [feedback point]

Keep the tone encouraging and direct. Do not use headers or labels — just the description paragraph, then the numbered list.
Do not mention joint angles or technical metrics.

Extra context: {extra_context}
"""

    image_content = []

    if image_paths:
        for path in image_paths[:4]:
            image_content.append({
                "type": "image_url",
                "image_url": {"url": _file_to_data_url(path)},
            })

    if image_arrays_rgb:
        remaining = 4 - len(image_content)
        for img in image_arrays_rgb[:remaining]:
            image_content.append({
                "type": "image_url",
                "image_url": {"url": _numpy_rgb_to_data_url(img)},
            })

    if image_content:
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}, *image_content]}]
    else:
        messages = [{"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=messages,
        temperature=0.4,
        max_completion_tokens=400,
        timeout=30.0,  # 30-second hard cap — prevents worker stall on slow upstream
    )

    return completion.choices[0].message.content.strip()
