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
        ("minh", "1234", "faces/user2")
    ]
    for u in users:
        try:
            c.execute("INSERT INTO users (username, password, face_dir) VALUES (?, ?, ?)", u)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

# --- Ghi log ---
def log_attendance(user_id, is_valid, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO attendance_logs (user_id, timestamp, is_valid, message) VALUES (?, ?, ?, ?)",
              (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), is_valid, message))
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
        c.execute("SELECT id, face_dir FROM users WHERE username=? AND password=?", (username, password))
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
        self.root.geometry("900x600")

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.info_label = tk.Label(root, text=f"Xin chào, {username}. Đang mở camera...", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.model = YOLO(MODEL_PATH)

        # Load ảnh preset của user
        self.presets = {}
        if os.path.exists(self.face_dir):
            for filename in os.listdir(self.face_dir):
                if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                    name = os.path.splitext(filename)[0]
                    self.presets[name] = os.path.join(self.face_dir, filename)
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy thư mục khuôn mặt: {self.face_dir}")

        self.update_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.info_label.config(text="Không đọc được hình từ camera.")
            return

        results = self.model(frame, stream=True)
        recognized_name = None

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                face_crop = frame[y1:y2, x1:x2]
                cv2.imwrite("temp_face.jpg", face_crop)

                # giá trị mặc định
                color = (100, 100, 100)
                label = "Detecting..."

                # So sánh với preset
                for name, preset_path in self.presets.items():
                    try:
                        result = DeepFace.verify("temp_face.jpg", preset_path, model_name="ArcFace", enforce_detection=False)
                        if result["verified"]:
                            recognized_name = name
                            log_attendance(self.user_id, 1, f"Đã xác thực {name}")
                            color = (0, 255, 0)
                            label = f"{name}"
                            break
                        else:
                            color = (0, 0, 255)
                            label = "Unknown"
                            log_attendance(self.user_id, 0, "Không trùng khớp khuôn mặt")
                    except Exception:
                        color = (255, 255, 0)
                        label = "Error"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if recognized_name:
            self.info_label.config(text=f"✅ Xác thực thành công: {recognized_name}")
        else:
            self.info_label.config(text=f"⏳ Đang quét khuôn mặt...")

        # Cập nhật GUI
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if self.running:
            self.root.after(30, self.update_frame)

    def on_close(self):
        self.running = False
        self.cap.release()
        self.root.destroy()

# --- Main ---
if __name__ == "__main__":
    init_db()
    seed_users()

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
