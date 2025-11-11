# 🧠 Face Attendance System (YOLO + DeepFace + Tkinter)

## 🧾 Giới thiệu
**Face Attendance System** là một ứng dụng **chấm công bằng khuôn mặt chạy offline**, sử dụng:
- **YOLOv8** để phát hiện khuôn mặt.
- **DeepFace** (ArcFace backend) để xác thực danh tính người dùng.
- **Tkinter GUI** để tạo giao diện trực quan.

Người dùng đăng nhập, bật camera, chụp ảnh khuôn mặt và hệ thống sẽ xác thực khuôn mặt đó dựa trên các ảnh mẫu (preset) được lưu sẵn của từng nhân viên.

---

## 🚀 Tính năng chính
- **Đăng nhập người dùng:** xác thực tài khoản từ SQLite.
- **Chụp ảnh khuôn mặt qua camera** khi người dùng bấm nút "📸 Chấm công".
- **Phát hiện khuôn mặt bằng YOLOv8.**
- **So khớp khuôn mặt với preset bằng DeepFace (ArcFace).**
- **Ghi log chấm công** (thời gian, kết quả, ghi chú) vào cơ sở dữ liệu SQLite.
- **Chạy hoàn toàn offline** — không cần kết nối Internet.

---

## 🧱 Cấu trúc dự án

```
face-attendance/
│
├── faces/                     # Thư mục chứa ảnh preset khuôn mặt của từng user
│   ├── user1/
│   │   ├── user1-1.png
│   │   └── user1-2.png
│   └── user2/
│       ├── user2-1.png
│       └── user2-2.png
│
├── yolov8n-face.pt            # Model YOLOv8 dùng để phát hiện khuôn mặt
├── database.db                # SQLite database (tự động tạo nếu chưa có)
│
├── main.py                    # File chính (GUI + xử lý nhận diện)
├── requirements.txt            # Danh sách thư viện cần cài
└── README.md
```

---

## ⚙️ Cài đặt môi trường

### 1️⃣ Tạo môi trường ảo và cài thư viện
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# hoặc
source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
```

### 2️⃣ File `requirements.txt` mẫu
```text
ultralytics==8.3.13
deepface==0.0.93
opencv-python==4.10.0.84
torch>=2.0.0
torchvision
pandas
numpy
Pillow
```

### 3️⃣ Tải model YOLOv8-face
Tải file model YOLOv8 đã huấn luyện phát hiện khuôn mặt:

👉 [yolov8n-face.pt (GitHub)]([https://github.com/derronqi/yolov8-face/releases/download/v0.0.1/yolov8n-face.pt](https://drive.google.com/file/d/1qcr9DbgsX3ryrz2uU8w4Xm3cOrRywXqb/view))

Đặt file đó vào thư mục gốc của dự án:
```
face-attendance/yolov8n-face.pt
```

---

## 💻 Cách sử dụng

### 🔹 1. Chuẩn bị dữ liệu
- Mỗi người dùng có 1 thư mục riêng trong `faces/`.
- Bên trong chứa các ảnh khuôn mặt rõ nét, chính diện:
  ```
  faces/user1/user1-1.png
  faces/user1/user1-2.png
  ```

### 🔹 2. Chạy chương trình
```bash
python main.py
```
Ứng dụng sẽ:
- Tự khởi tạo `database.db` và thêm tài khoản mẫu:
  - `username: tuan` → `faces/user1`
  - `username: minh` → `faces/user2`
- Mở cửa sổ đăng nhập.

### 🔹 3. Đăng nhập
Nhập:
```
Username: tuan
Password: 1234
```

### 🔹 4. Giao diện chấm công
Sau khi đăng nhập:
- Camera bật lên (chỉ hiển thị, chưa detect).
- Căn mặt vào giữa khung hình → bấm **📸 Chấm công**.
- Hệ thống:
  - Dò khuôn mặt trong ảnh chụp.
  - So sánh với ảnh preset tương ứng.
  - Hiển thị kết quả:
    - ✅ Nếu khớp → xác thực thành công, log được lưu.
    - ❌ Nếu không khớp → thông báo lỗi & lưu log thất bại.

---

## 🗄️ Cấu trúc cơ sở dữ liệu

### Bảng `users`
| Cột | Kiểu dữ liệu | Mô tả |
|-----|---------------|------|
| id | INTEGER | Khóa chính |
| username | TEXT | Tên đăng nhập |
| password | TEXT | Mật khẩu |
| face_dir | TEXT | Đường dẫn thư mục ảnh preset |

### Bảng `attendance_logs`
| Cột | Kiểu dữ liệu | Mô tả |
|-----|---------------|------|
| id | INTEGER | Khóa chính |
| user_id | INTEGER | ID người dùng |
| timestamp | TEXT | Thời gian chấm công |
| is_valid | INTEGER | 1: thành công, 0: thất bại |
| message | TEXT | Ghi chú / kết quả |

---

## 🧠 Cơ chế hoạt động

1. Người dùng đăng nhập → hệ thống lấy thư mục khuôn mặt tương ứng.
2. Khi bấm **Chấm công**, camera chụp lại 1 frame.
3. YOLOv8 phát hiện khuôn mặt trong ảnh.
4. DeepFace (ArcFace backend) so khớp khuôn mặt chụp được với các ảnh preset.
5. Ghi log kết quả vào SQLite.
6. Hiển thị kết quả trực tiếp trên GUI.

---

## 💡 Gợi ý mở rộng
- Thêm **tính năng đăng ký khuôn mặt mới** trực tiếp trong GUI.
- Lưu ảnh chụp mỗi lần chấm công.
- Thêm **biểu đồ thống kê chấm công** (Pandas + Matplotlib).
- Sau này có thể mở rộng sang **microservice API (FastAPI)** để tích hợp với phần mềm chấm công khác.

---

## 🪶 Giấy phép
Dự án này mang tính học thuật và thử nghiệm.  
Vui lòng tôn trọng giấy phép gốc của các mô hình:
- [YOLOv8 (Ultralytics)](https://github.com/ultralytics/ultralytics)
- [DeepFace](https://github.com/serengil/deepface)
- [ArcFace (InsightFace)](https://github.com/deepinsight/insightface)
