# 🧠 Facial Recognition Attendance System (YOLO + DeepFace + FastAPI)

## 🧾 Overview
This project is an **offline facial-recognition attendance system** powered by **YOLO** (for face detection) and **DeepFace** (for face verification/recognition).  
It can run locally with a GUI or expose REST APIs (via **FastAPI**) for integration with other systems — e.g., HR or employee management apps.

---

## 🚀 Features
- **YOLOv8 Face Detection:** Real-time face detection via YOLO (CPU/GPU).
- **DeepFace Recognition:** Face embedding + verification (supports ArcFace, Facenet, VGG-Face, etc.).
- **SQLite-based logging:** Records each check-in with `user_id`, `timestamp`, `is_valid`, and `message`.
- **FastAPI microservice:** Allows other apps to call face verification via HTTP API.
- **Optional GUI (Tkinter):** For local interactive use and registration.
- **Offline-first:** Runs fully on local machine — no cloud dependency.

---

## 🧱 Architecture
```
📦 face-attendance/
│
├── faces/                 # Stored reference face images (by user)
│   ├── user_1/
│   │   └── tuan.jpg
│   └── user_2/
│       └── minh.jpg
│
├── yolov8n-face.pt        # YOLO model weights (for detection)
├── database.db            # SQLite database (auto-created)
│
├── app/
│   ├── main.py            # FastAPI microservice entry
│   ├── recognize.py       # Core logic (YOLO + DeepFace)
│   ├── gui.py             # Tkinter GUI (optional)
│   ├── db.py              # SQLite database helpers
│   ├── schemas.py         # Pydantic schemas for API
│   └── utils.py           # Common utilities
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation
```bash
git clone <repo-url>
cd face-attendance

# Create venv (Python 3.10 recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Example requirements.txt
```text
ultralytics==8.3.13
deepface==0.0.93
opencv-python==4.10.0.84
torch>=2.0.0
torchvision
pandas
numpy
Pillow
fastapi
uvicorn
```

---

## ⚙️ Configuration
You can define a JSON or YAML config file:
```yaml
model_path: yolov8n-face.pt
deepface_backend: ArcFace
recognition_threshold: 0.45
db_path: database.db
faces_dir: faces/
```

---

## 💻 Run modes

### 🧍 GUI Local Mode
```bash
python app/gui.py
```
- Opens camera.
- Detects & verifies faces in real-time.
- Logs attendance to `database.db`.

### ⚙️ API Server Mode (FastAPI)
```bash
uvicorn app.main:app --reload --port 8000
```

Then visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

---

## 🧩 Example FastAPI Endpoints

### 1️⃣ Verify Face (Attendance Check)
**POST** `/api/verify`

**Request:**
```json
{
  "user_id": 1,
  "image_base64": "<base64-encoded-face-image>"
}
```

**Response:**
```json
{
  "verified": true,
  "confidence": 0.87,
  "timestamp": "2025-11-11T10:45:02",
  "message": "Face matched successfully"
}
```

### 2️⃣ List Attendance Logs
**GET** `/api/logs`

**Response:**
```json
[
  {
    "user_id": 1,
    "timestamp": "2025-11-11T10:45:02",
    "is_valid": 1,
    "message": "Face matched successfully"
  }
]
```

---

## 🧠 How It Works
1. **YOLOv8** detects the face region.
2. The detected face is cropped and aligned.
3. **DeepFace** computes embedding vector and compares with stored reference images.
4. If below threshold → `is_valid = 1` → save to `attendance_logs`.
5. API returns verification result.

---

## 🗄️ SQLite Database Schema
### Table: `users`
| id | username | password | face_dir |
|----|-----------|-----------|-----------|

### Table: `attendance_logs`
| id | user_id | timestamp | is_valid | message |

---

## 🔒 Privacy & Security
- All facial data stays **local** on the device.
- Only embeddings are compared in memory.
- Use secure local file access for `faces/` and `database.db`.
- Optionally encrypt or hash embeddings for production.

---

## 🧰 Future Plans
- [ ] Add “face registration” endpoint (`/api/enroll`)
- [ ] Add liveness detection (blink/motion)
- [ ] Containerize via Docker
- [ ] Integrate with HRM / payroll microservices

---

## 🪶 License
MIT License (or your preferred license).  
Respect 3rd-party model licenses (YOLOv8, DeepFace, ArcFace).

---

### 💡 Tips
- For better performance, use **GPU (CUDA)** and **resize frames** to 640×480.
- ArcFace backend in DeepFace gives the best accuracy/speed balance.
- Keep each user’s images in separate folder: `faces/<user_id>/`.
