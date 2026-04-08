import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"
os.environ["DISPLAY"] = ":0"
import traceback
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path

from analyzers.image_analyzer import analyze_image
from analyzers.video_analyzer import analyze_video
from analyzers.metrics import compare_metric_sets
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="MotionInsight AI API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://motion-insight-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_upload(file: UploadFile) -> str:
    suffix = Path(file.filename).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        return tmp.name


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze/image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    try:
        path = save_upload(file)
        result = analyze_image(path)
        # Convert numpy arrays to lists for JSON serialization
        if result.get("annotated_image") is not None:
            result["annotated_image"] = result["annotated_image"].tolist()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/video")
async def analyze_video_endpoint(
    file: UploadFile = File(...),
    sample_every_n_frames: int = Form(10),
):
    try:
        path = save_upload(file)
        result = analyze_video(path, sample_every_n_frames=sample_every_n_frames)
        # Convert preview frames
        if result.get("preview_frames"):
            result["preview_frames"] = [f.tolist() for f in result["preview_frames"]]
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare/images")
async def compare_images_endpoint(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
):
    try:
        before_path = save_upload(before)
        after_path = save_upload(after)

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

        # Serialize numpy arrays
        if before_result.get("annotated_image") is not None:
            before_result["annotated_image"] = before_result["annotated_image"].tolist()
        if after_result.get("annotated_image") is not None:
            after_result["annotated_image"] = after_result["annotated_image"].tolist()

        return JSONResponse(content={
            "before": before_result,
            "after": after_result,
            "comparison": comparison,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare/videos")
async def compare_videos_endpoint(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    sample_every_n_frames: int = Form(10),
):
    try:
        before_path = save_upload(before)
        after_path = save_upload(after)

        before_result = analyze_video(before_path, sample_every_n_frames=sample_every_n_frames)
        after_result = analyze_video(after_path, sample_every_n_frames=sample_every_n_frames)

        comparison = None
        if before_result.get("success") and after_result.get("success"):
            comparison = compare_metric_sets(
                before_result["summary_metrics"],
                after_result["summary_metrics"],
                first_name="Before",
                second_name="After",
            )

        if before_result.get("preview_frames"):
            before_result["preview_frames"] = [f.tolist() for f in before_result["preview_frames"]]
        if after_result.get("preview_frames"):
            after_result["preview_frames"] = [f.tolist() for f in after_result["preview_frames"]]

        return JSONResponse(content={
            "before": before_result,
            "after": after_result,
            "comparison": comparison,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
