import _ensure_gles  # noqa: F401 — must be first; preloads libGLESv2 before mediapipe

import os
import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from analyzers.image_analyzer import analyze_image
from analyzers.video_analyzer import analyze_video
from analyzers.metrics import compare_metric_sets
from config import SUPPORTED_IMAGE_TYPES, SUPPORTED_VIDEO_TYPES

logger = logging.getLogger(__name__)

app = FastAPI(title="MotionInsight AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://motion-insight-ai.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Accept"],
)

# ── File limits ──────────────────────────────────────────────────────────────
MAX_IMAGE_BYTES = 50 * 1024 * 1024   # 50 MB
MAX_VIDEO_BYTES = 200 * 1024 * 1024  # 200 MB

ALLOWED_IMAGE_SUFFIXES = {f".{ext}" for ext in SUPPORTED_IMAGE_TYPES}
ALLOWED_VIDEO_SUFFIXES = {f".{ext}" for ext in SUPPORTED_VIDEO_TYPES}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_upload(file: UploadFile, allowed_suffixes: set[str], max_bytes: int) -> None:
    """Raise HTTPException 400 if the upload fails type or size checks."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Accepted: {', '.join(sorted(allowed_suffixes))}",
        )
    # Peek at actual content length header if present; full check is done after read.
    if file.size is not None and file.size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {max_bytes // (1024 * 1024)} MB.",
        )


@contextmanager
def _saved_upload(file: UploadFile, max_bytes: int):
    """
    Context manager that writes an upload to a temp file,
    yields the path, and always deletes the file on exit.
    """
    suffix = Path(file.filename or "").suffix.lower() or ".tmp"
    tmp_path: str | None = None
    try:
        data = file.file.read()
        if len(data) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed size is {max_bytes // (1024 * 1024)} MB.",
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        yield tmp_path
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Already deleted or never created


def _clamp_sample_rate(n: int) -> int:
    """Clamp sample_every_n_frames to a safe range [1, 60]."""
    return max(1, min(n, 60))


def _safe_tolist(arr):
    """Convert a numpy array to a nested list, or return None."""
    return arr.tolist() if arr is not None else None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    _validate_upload(file, ALLOWED_IMAGE_SUFFIXES, MAX_IMAGE_BYTES)
    try:
        with _saved_upload(file, MAX_IMAGE_BYTES) as path:
            result = analyze_image(path)
        if result.get("annotated_image") is not None:
            result["annotated_image"] = _safe_tolist(result["annotated_image"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("analyze_image failed")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.") from exc


@app.post("/analyze/video")
async def analyze_video_endpoint(
    file: UploadFile = File(...),
    sample_every_n_frames: int = Form(10),
):
    _validate_upload(file, ALLOWED_VIDEO_SUFFIXES, MAX_VIDEO_BYTES)
    n = _clamp_sample_rate(sample_every_n_frames)
    try:
        with _saved_upload(file, MAX_VIDEO_BYTES) as path:
            result = analyze_video(path, sample_every_n_frames=n)
        if result.get("preview_frames"):
            result["preview_frames"] = [_safe_tolist(f) for f in result["preview_frames"]]
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("analyze_video failed")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.") from exc


@app.post("/compare/images")
async def compare_images_endpoint(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
):
    _validate_upload(before, ALLOWED_IMAGE_SUFFIXES, MAX_IMAGE_BYTES)
    _validate_upload(after, ALLOWED_IMAGE_SUFFIXES, MAX_IMAGE_BYTES)
    try:
        with _saved_upload(before, MAX_IMAGE_BYTES) as before_path, \
             _saved_upload(after, MAX_IMAGE_BYTES) as after_path:

            before_result = analyze_image(before_path)
            after_result = analyze_image(after_path)

        comparison = None
        if before_result.get("success") and after_result.get("success"):
            comparison = compare_metric_sets(
                before_result["metrics"],
                after_result["metrics"],
                first_name="Before",
                second_name="After",
            )

        if before_result.get("annotated_image") is not None:
            before_result["annotated_image"] = _safe_tolist(before_result["annotated_image"])
        if after_result.get("annotated_image") is not None:
            after_result["annotated_image"] = _safe_tolist(after_result["annotated_image"])

        return JSONResponse(content={
            "before": before_result,
            "after": after_result,
            "comparison": comparison,
        })
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("compare_images failed")
        raise HTTPException(status_code=500, detail="Comparison failed. Please try again.") from exc


@app.post("/compare/videos")
async def compare_videos_endpoint(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    sample_every_n_frames: int = Form(10),
):
    _validate_upload(before, ALLOWED_VIDEO_SUFFIXES, MAX_VIDEO_BYTES)
    _validate_upload(after, ALLOWED_VIDEO_SUFFIXES, MAX_VIDEO_BYTES)
    n = _clamp_sample_rate(sample_every_n_frames)
    try:
        with _saved_upload(before, MAX_VIDEO_BYTES) as before_path, \
             _saved_upload(after, MAX_VIDEO_BYTES) as after_path:

            before_result = analyze_video(before_path, sample_every_n_frames=n)
            after_result = analyze_video(after_path, sample_every_n_frames=n)

        comparison = None
        if before_result.get("success") and after_result.get("success"):
            comparison = compare_metric_sets(
                before_result["summary_metrics"],
                after_result["summary_metrics"],
                first_name="Before",
                second_name="After",
            )

        if before_result.get("preview_frames"):
            before_result["preview_frames"] = [_safe_tolist(f) for f in before_result["preview_frames"]]
        if after_result.get("preview_frames"):
            after_result["preview_frames"] = [_safe_tolist(f) for f in after_result["preview_frames"]]

        return JSONResponse(content={
            "before": before_result,
            "after": after_result,
            "comparison": comparison,
        })
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("compare_videos failed")
        raise HTTPException(status_code=500, detail="Comparison failed. Please try again.") from exc
