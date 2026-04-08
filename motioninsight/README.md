# MotionInsight AI — Full Stack

A full-stack pose analysis app using **MediaPipe**, **Groq LLaMA Vision**, and a clean **FastAPI + React** architecture.

---

## Project Structure

```
motioninsight/
├── backend/
│   ├── main.py                  # FastAPI app & all API routes
│   ├── config.py                # Paths, model name, supported types
│   ├── requirements.txt         # Python deps
│   ├── .env                     # GROQ_API_KEY (create from .env.example)
│   ├── start.sh                 # One-command startup (downloads model too)
│   ├── models/
│   │   └── pose_landmarker_full.task  # MediaPipe model (auto-downloaded)
│   ├── analyzers/
│   │   ├── image_analyzer.py    # Single image pose analysis
│   │   ├── video_analyzer.py    # Video pose analysis (frame sampling)
│   │   └── metrics.py           # Angle calc, aggregation, comparison
│   └── utils/
│       ├── ai_describer.py      # Groq vision AI descriptions
│       ├── drawing.py           # MediaPipe landmark drawing
│       └── file_util.py         # Temp file save helper
└── frontend/
    └── index.html               # Single-file React frontend (no build step)
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Copy and fill in your env
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# Run the startup script (installs deps + downloads model + starts server)
bash start.sh
```

The API will be live at **http://localhost:8000**

> **Model download**: On first run, `start.sh` downloads `pose_landmarker_full.task` (~30MB) automatically into `backend/models/`.

### 2. Frontend

No build step needed. Just open:

```bash
open frontend/index.html
# or double-click it in Finder/Explorer
```

Or serve it with any static server:

```bash
cd frontend
npx serve .        # Node
python3 -m http.server 3000   # Python
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/health` | Healthcheck |
| `POST` | `/analyze/image` | Analyze a single image |
| `POST` | `/analyze/video` | Analyze a video |
| `POST` | `/compare/images` | Compare before/after images |
| `POST` | `/compare/videos` | Compare before/after videos |

### Example: Analyze Image

```bash
curl -X POST http://localhost:8000/analyze/image \
  -F "file=@pose.jpg"
```

Response:
```json
{
  "success": true,
  "metrics": {
    "left_knee_angle": 162.4,
    "right_knee_angle": 158.9,
    "left_elbow_angle": 87.3,
    "right_elbow_angle": 91.2,
    "avg_elbow_angle": 89.25,
    "avg_knee_angle": 160.65,
    "left_right_elbow_diff": 3.9,
    "left_right_knee_diff": 3.5
  },
  "description": "The subject is standing with slightly asymmetric knee extension...",
  "annotated_image": [[...]], 
  "message": "Pose detected successfully."
}
```

### Example: Compare Videos

```bash
curl -X POST http://localhost:8000/compare/videos \
  -F "before=@before.mp4" \
  -F "after=@after.mp4" \
  -F "sample_every_n_frames=10"
```

---

## Environment Variables

Create `backend/.env`:

```env
GROQ_API_KEY=gsk_your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

---

## Metrics Explained

| Metric | Description |
|--------|-------------|
| `left/right_knee_angle` | Angle at the knee joint (hip→knee→ankle) |
| `left/right_elbow_angle` | Angle at the elbow (shoulder→elbow→wrist) |
| `avg_elbow_angle` | Mean of left + right elbow |
| `avg_knee_angle` | Mean of left + right knee |
| `left_right_elbow_diff` | Asymmetry between elbows (lower = more symmetric) |
| `left_right_knee_diff` | Asymmetry between knees (lower = more symmetric) |

---

## Supported Formats

- **Images**: JPG, JPEG, PNG
- **Videos**: MP4, MOV, AVI, MKV

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Pose detection | MediaPipe Pose Landmarker |
| AI descriptions | Groq · LLaMA 4 Scout Vision |
| Backend API | FastAPI + Uvicorn |
| Frontend | React 18 (no build step) |
| Image processing | OpenCV + Pillow |

---

## Development

To run with auto-reload:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

To update the AI model used, edit `config.py`:

```python
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
```

---