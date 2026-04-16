import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pymongo import MongoClient
from mtcnn import MTCNN
from keras_facenet import FaceNet
from datetime import datetime
import threading
import time

# -----------------------
# Models
# -----------------------

detector = MTCNN()
facenet = FaceNet()

# -----------------------
# MongoDB
# -----------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_attendance"]
users = db["users"]

def generate_id():
    last = users.find_one(sort=[("user_id", -1)])
    return 1 if last is None else last["user_id"] + 1


# -----------------------
# Camera
# -----------------------

cap = cv2.VideoCapture(0)

def update_camera():
    ret, frame = cap.read()

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame).resize((520, 360))
        imgtk = ImageTk.PhotoImage(image=img)

        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    camera_label.after(1, update_camera)


# -----------------------
# Directions
# -----------------------

directions = ["Front", "Left", "Right", "Up", "Down"]

status_labels = []

# -----------------------
# Capture Logic
# -----------------------

def capture_sequence():

    name = name_entry.get()

    if name == "":
        messagebox.showerror("Error", "Enter Name First")
        return

    user_id = generate_id()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    embeddings = []

    for i, direction in enumerate(directions):

        popup = tk.Toplevel(root)
        popup.geometry("300x150")
        popup.configure(bg="#111111")

        tk.Label(
            popup,
            text=f"Look {direction}",
            font=("Segoe UI", 16, "bold"),
            fg="#FF7A00",
            bg="#111111"
        ).pack(pady=30)

        root.update()
        time.sleep(2)
        popup.destroy()

        captured = False

        while not captured:
            ret, frame = cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            faces = detector.detect_faces(rgb)

            for face in faces:
                x, y, w, h = face['box']
                x, y = max(0, x), max(0, y)

                face_crop = frame[y:y+h, x:x+w]

                if face_crop.size == 0:
                    continue

                face_crop = cv2.resize(face_crop, (160, 160))
                face_array = np.expand_dims(face_crop, axis=0)

                embedding = facenet.embeddings(face_array)[0]
                embeddings.append(embedding.tolist())

                # ✅ Green circle fill
                status_labels[i].config(bg="green")

                captured = True

    # Save to DB
    users.insert_one({
        "user_id": user_id,
        "name": name,
        "date": date,
        "time": current_time,
        "embeddings": embeddings
    })

    messagebox.showinfo(
        "Registration Complete",
        f"Registration Successful\n\nYour ID is {user_id}"
    )


# -----------------------
# UI
# -----------------------

root = tk.Tk()
root.title("Employee Registration")
root.geometry("1100x600")
root.configure(bg="#111111")

# Title
tk.Label(
    root,
    text="Employee Registration",
    font=("Segoe UI", 22, "bold"),
    fg="#FF7A00",
    bg="#111111"
).pack(pady=10)

container = tk.Frame(root, bg="#111111")
container.pack(fill="both", expand=True, padx=20)

# -----------------------
# LEFT PANEL
# -----------------------

left = tk.Frame(container, bg="#1B1B1B", width=350)
left.pack(side="left", fill="y", padx=10)

tk.Label(left,
         text="User Details",
         font=("Segoe UI", 18, "bold"),
         fg="#FF7A00",
         bg="#1B1B1B").pack(pady=20)

tk.Label(left, text="Name", bg="#1B1B1B", fg="white").pack()
name_entry = tk.Entry(left, font=("Segoe UI", 12), width=25)
name_entry.pack(pady=10)

# Button
tk.Button(
    left,
    text="Start Capture",
    font=("Segoe UI", 12, "bold"),
    bg="#FF7A00",
    fg="black",
    command=lambda: threading.Thread(target=capture_sequence).start()
).pack(pady=20)

# -----------------------
# Capture Status
# -----------------------

tk.Label(left,
         text="Capture Status",
         font=("Segoe UI", 14, "bold"),
         fg="#FF7A00",
         bg="#1B1B1B").pack(pady=10)

for d in directions:
    frame = tk.Frame(left, bg="#1B1B1B")
    frame.pack(pady=5)

    tk.Label(frame, text=d, fg="white", bg="#1B1B1B", width=10).pack(side="left")

    status = tk.Label(frame, bg="gray", width=2, height=1)
    status.pack(side="right")

    status_labels.append(status)


# -----------------------
# RIGHT PANEL (CAMERA)
# -----------------------

right = tk.Frame(container, bg="#1B1B1B")
right.pack(side="right", fill="both", expand=True, padx=10)

tk.Label(
    right,
    text="Camera Preview",
    font=("Segoe UI", 16, "bold"),
    fg="#FF7A00",
    bg="#1B1B1B"
).pack(pady=10)

camera_label = tk.Label(right, bg="#1B1B1B")
camera_label.pack()

update_camera()

# -----------------------
# RUN
# -----------------------

root.mainloop()

cap.release()
cv2.destroyAllWindows()