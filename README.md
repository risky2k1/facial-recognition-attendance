# Facial Recognition Attendance (YOLO + DeepFace)

Short, self-contained README for a facial-recognition attendance system that uses YOLO for face detection and DeepFace for face verification/recognition.

## Project overview
This repository implements an attendance system that:
- Detects faces in live video or images using YOLO (object detection).
- Verifies/recognizes faces using DeepFace embeddings and a matching strategy.
- Logs attendance records (timestamp, identity, confidence) to CSV or a database.

## Features
- Real-time face detection with YOLO (CPU/GPU).
- Face embedding and recognition via DeepFace (supports multiple backends).
- Simple enrollment workflow for registering new users.
- Configurable thresholds, video source, and output formats.

## Prerequisites
- Python 3.8+
- GPU recommended for real-time performance (CUDA if using PyTorch/CUDA GPU)
- Basic packages: numpy, opencv-python, torch (if using PyTorch YOLO), deepface

## Installation
1. Clone repository:
    git clone <repo-url>
2. Create virtual environment and activate it:
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    source .venv/bin/activate  # Linux / macOS
3. Install dependencies:
    pip install -r requirements.txt

Example requirements (put in requirements.txt):
- opencv-python
- numpy
- pandas
- deepface
- torch torchvision  # if using PyTorch based YOLO
- yolov5  # or yolov8 / chosen YOLO implementation

## Configuration
Configure settings in config.yaml or config.json:
- model: path to YOLO weights or model name
- deepface_backend: Facenet | VGG-Face | ArcFace | etc.
- detection_threshold: float
- recognition_threshold: float (embedding distance)
- video_source: 0 | path/to/video.mp4
- output_csv: path/to/attendance.csv

## Usage
- Enroll a new user:
  python enroll.py --name "Alice" --image path/to/alice.jpg
  This builds a template embedding for later recognition.

- Run attendance capture (camera):
  python attendance.py --source 0 --config config.yaml

- Run on a video file:
  python attendance.py --source path/to/video.mp4 --config config.yaml

Outputs:
- attendance.csv with rows: timestamp, id/name, confidence, frame_no
- Optional annotated video or snapshots of detections

## Implementation notes
- YOLO detects face bounding boxes; crop + align before passing to DeepFace.
- Use a consistent embedding backend and normalization for reliable matching.
- Set recognition_threshold experimentally per dataset (common range: 0.3–0.6 depending on backend).
- For high accuracy, prefer ArcFace or Facenet backends and good-quality enrollment images.

## Data and privacy
- Store only required data (embeddings or hashed IDs) and secure access.
- Obtain consent from subjects before capturing facial data.
- Consider forgetting/retention policies for GDPR or local regulations.

## Troubleshooting
- Low recognition accuracy: increase enrollment images per person, improve lighting, tune threshold.
- Slow performance: enable GPU, reduce input resolution, use optimized YOLO variant.
- Missing dependencies: verify installed versions and CUDA compatibility.

## License
Include an appropriate license file (e.g., MIT) and respect third-party model licenses.

For more detailed implementation, add sections for file structure, API, and examples as the project evolves.