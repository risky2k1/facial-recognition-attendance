import cv2
from ultralytics import YOLO
from deepface import DeepFace
import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

DB_PATH = "database.db"
MODEL_PATH = "yolov8n-face.pt"

# --- Khởi tạo DB ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    face_dir TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    timestamp TEXT,
                    is_valid INTEGER,
                    message TEXT
                )""")
    conn.commit()
    conn.close()

# --- Thêm user test ---
def seed_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    users = [
        ("tuan", "1234", "faces/user1"),
        ("minh", "1234", "faces/user2"),
    ]
    for u in users:
        try:
            c.execute(
                "INSERT INTO users (username, password, face_dir) VALUES (?, ?, ?)",
                u,
            )
        except sqlite3.IntegrityError:
            # đã tồn tại thì bỏ qua
            pass
    conn.commit()
    conn.close()

# --- Ghi log ---
def log_attendance(user_id, is_valid, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO attendance_logs (user_id, timestamp, is_valid, message) VALUES (?, ?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), is_valid, message),
    )
    conn.commit()
    conn.close()

# --- GUI Đăng nhập ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập hệ thống chấm công")
        self.root.geometry("300x200")

        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Đăng nhập", command=self.login).pack(pady=15)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT id, face_dir FROM users WHERE username=? AND password=?",
            (username, password),
        )
        user = c.fetchone()
        conn.close()

        if user:
            user_id, face_dir = user
            self.root.destroy()
            app_root = tk.Tk()
            AttendanceApp(app_root, user_id, username, face_dir)
            app_root.mainloop()
        else:
            messagebox.showerror("Đăng nhập thất bại", "Sai tên đăng nhập hoặc mật khẩu!")

# --- GUI chấm công ---
class AttendanceApp:
    def __init__(self, root, user_id, username, face_dir):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.face_dir = face_dir
        self.root.title(f"Hệ thống chấm công - {username}")
        self.root.geometry("900x650")

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.info_label = tk.Label(
            root,
            text=f"Xin chào, {username}. Hãy căn mặt vào khung, sau đó bấm 'Chấm công'.",
            font=("Arial", 12),
        )
        self.info_label.pack(pady=10)

        # Nút chấm công (chụp + so sánh)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.capture_btn = tk.Button(
            btn_frame,
            text="📸 Chấm công",
            font=("Arial", 11),
            command=self.capture_and_verify,
        )
        self.capture_btn.pack(side=tk.LEFT, padx=10)

        self.exit_btn = tk.Button(
            btn_frame, text="Thoát", font=("Arial", 11), command=self.on_close
        )
        self.exit_btn.pack(side=tk.LEFT, padx=10)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.model = YOLO(MODEL_PATH)

        # frame mới nhất từ camera
        self.last_frame = None

        # Load ảnh preset của user
        self.presets = {}
        if os.path.exists(self.face_dir):
            for filename in os.listdir(self.face_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    name = os.path.splitext(filename)[0]
                    self.presets[name] = os.path.join(self.face_dir, filename)
        else:
            messagebox.showerror(
                "Lỗi", f"Không tìm thấy thư mục khuôn mặt: {self.face_dir}"
            )

        print("Presets loaded:", self.presets)  # debug

        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        """Chỉ hiển thị video từ camera, KHÔNG detect ở đây."""
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.info_label.config(text="Không đọc được hình từ camera.")
        else:
            self.last_frame = frame.copy()

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(30, self.update_frame)

    def capture_and_verify(self):
        """Chụp 1 frame hiện tại và so sánh với preset."""
        if self.last_frame is None:
            messagebox.showerror("Lỗi", "Chưa có frame từ camera, vui lòng thử lại.")
            return

        frame = self.last_frame.copy()

        # Chạy YOLO detect mặt trên frame hiện tại
        results = self.model(frame, stream=False)

        # Nếu không có mặt
        if len(results[0].boxes) == 0:
            self.info_label.config(text="❌ Không tìm thấy khuôn mặt trong ảnh chụp.")
            log_attendance(self.user_id, 0, "Không tìm thấy khuôn mặt")
            return

        # Chọn 1 khuôn mặt (ví dụ: khuôn mặt lớn nhất)
        best_box = None
        best_area = 0
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            if area > best_area:
                best_area = area
                best_box = (x1, y1, x2, y2)

        x1, y1, x2, y2 = best_box
        face_crop = frame[y1:y2, x1:x2]

        # Lưu tạm khuôn mặt
        temp_path = "temp_face.jpg"
        cv2.imwrite(temp_path, face_crop)

        # Mặc định
        verified = False
        matched_name = None
        confidence = None

        if not self.presets:
            self.info_label.config(
                text="⚠️ Không có ảnh preset nào cho user này. Vui lòng thêm ảnh vào thư mục."
            )
            log_attendance(self.user_id, 0, "Không có preset khuôn mặt")
        else:
            # So sánh với từng preset
            for name, preset_path in self.presets.items():
                try:
                    result = DeepFace.verify(
                        temp_path,
                        preset_path,
                        model_name="ArcFace",
                        enforce_detection=False,
                    )
                    # DeepFace trả về distance + threshold, ta dùng verified luôn
                    if result.get("verified"):
                        verified = True
                        matched_name = name
                        confidence = 1 - float(result.get("distance", 0.0))
                        break
                except Exception as e:
                    print("DeepFace error:", e)
                    continue

            # Cập nhật UI + log
            if verified:
                msg = f"✅ Xác thực thành công: {matched_name}"
                self.info_label.config(text=msg)
                log_attendance(self.user_id, 1, msg)
                color = (0, 255, 0)
                label = matched_name
            else:
                msg = "❌ Không trùng khớp với preset khuôn mặt."
                self.info_label.config(text=msg)
                log_attendance(self.user_id, 0, msg)
                color = (0, 0, 255)
                label = "Unknown"

            # Vẽ khung + label lên frame chụp để hiển thị kết quả
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

    def on_close(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()

# --- Main ---
if __name__ == "__main__":
    init_db()
    seed_users()

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
