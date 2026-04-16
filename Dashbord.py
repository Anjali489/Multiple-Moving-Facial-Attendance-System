import tkinter as tk
import subprocess
from datetime import datetime
from pymongo import MongoClient
from PIL import Image, ImageTk

# -----------------------
# MongoDB
# -----------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_attendance"]
users = db["users"]
attendance = db["smart_attendance"]

# -----------------------
# Main Window
# -----------------------

root = tk.Tk()
root.title("Smart Attendance Dashboard")
root.geometry("1300x750")
root.configure(bg="#0F0F0F")

# -----------------------
# Sidebar
# -----------------------

sidebar = tk.Frame(root, bg="#121212", width=300)
sidebar.pack(side="left", fill="y")

sidebar_inner = tk.Frame(sidebar, bg="#121212")
sidebar_inner.pack(expand=True)

# -----------------------
# Functions
# -----------------------

def open_registration():
    subprocess.Popen(["python", "registration.py"])

def start_attendance():
    status_text.config(text="Status: Camera Running...", fg="#00FF88")
    subprocess.Popen(["python", "faceDetecyion.py"])

def view_logs():
    subprocess.Popen(["python", "__pycache__\logs.py"])

# -----------------------
# Menu Buttons
# -----------------------

def create_menu(text, command=None):
    return tk.Button(
        sidebar_inner,
        text=text,
        bg="#121212",
        fg="white",
        activebackground="#FF7A00",
        activeforeground="black",
        bd=0,
        font=("Segoe UI", 11),
        anchor="w",
        padx=20,
        command=command
    )

create_menu("🏠 Dashboard").pack(fill="x", pady=8)
create_menu("👤 Register User", open_registration).pack(fill="x", pady=8)
create_menu("▶ Start Attendance", start_attendance).pack(fill="x", pady=8)
create_menu("📄 Attendance Logs", view_logs).pack(fill="x", pady=8)

# -----------------------
# Date Time
# -----------------------

date_label = tk.Label(sidebar_inner, fg="white", bg="#121212")
date_label.pack(pady=20)

time_label = tk.Label(sidebar_inner, fg="white", bg="#121212")
time_label.pack()

def update_time():
    now = datetime.now()
    date_label.config(text=now.strftime("%Y-%m-%d"))
    time_label.config(text=now.strftime("%H:%M:%S"))
    root.after(1000, update_time)

update_time()

# -----------------------
# Main Area (FIXED GRID)
# -----------------------

main = tk.Frame(root, bg="#0F0F0F")
main.pack(side="left", fill="both", expand=True)

# 3 column layout
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=3)  # center ko zyada space
main.columnconfigure(2, weight=1)

# -----------------------
# Title (center)
# -----------------------

title_label = tk.Label(
    main,
    text="SMART ATTENDANCE",
    fg="#FF7A00",
    bg="#0F0F0F",
    font=("Segoe UI", 28, "bold")
)
title_label.grid(row=0, column=0, columnspan=3, pady=20)

# -----------------------
# CENTER FRAME (perfect center)
# -----------------------

center_frame = tk.Frame(main, bg="#1A1A1A", width=900, height=550)
center_frame.grid(row=1, column=1)
center_frame.pack_propagate(False)

# IMAGE
img = Image.open("ai_face.png")
img = img.resize((600, 320))   # 🔥 bigger image
imgtk = ImageTk.PhotoImage(img)

img_label = tk.Label(center_frame, image=imgtk, bg="#1A1A1A")
img_label.image = imgtk
img_label.pack(pady=20)

# TEXT
tk.Label(
    center_frame,
    text="Smart Attendance System",
    fg="white",
    bg="#1A1A1A",
    font=("Segoe UI", 20, "bold")
).pack()

tk.Label(
    center_frame,
    text="Face Recognition Powered",
    fg="#AAAAAA",
    bg="#1A1A1A",
    font=("Segoe UI", 13)
).pack()

# STATUS
status_text = tk.Label(
    center_frame,
    text="Status: Ready to Start",
    fg="#00FF88",
    bg="#1A1A1A",
    font=("Segoe UI", 13, "bold")
)
status_text.pack(pady=10)

# -----------------------
# RIGHT PANEL (aligned properly)
# -----------------------

right = tk.Frame(main, bg="#0F0F0F")
right.grid(row=1, column=2, sticky="n", padx=20)

# Quick Actions
action_frame = tk.Frame(right, bg="#1A1A1A")
action_frame.pack(pady=20, fill="x")

tk.Label(
    action_frame,
    text="Quick Actions",
    fg="white",
    bg="#1A1A1A",
    font=("Segoe UI", 13, "bold")
).pack(pady=10)

tk.Button(
    action_frame,
    text="👤 Register User",
    command=open_registration,
    bg="#FF7A00",
    fg="black",
    font=("Segoe UI", 12, "bold"),
    width=18,
    height=2
).pack(pady=10)

tk.Button(
    action_frame,
    text="▶ Start Attendance",
    command=start_attendance,
    bg="#FF7A00",
    fg="black",
    font=("Segoe UI", 12, "bold"),
    width=18,
    height=2
).pack(pady=10)

tk.Button(
    action_frame,
    text="📄 View Logs",
    command=view_logs,
    bg="#FF7A00",
    fg="black",
    font=("Segoe UI", 12, "bold"),
    width=18,
    height=2
).pack(pady=10)

# -----------------------
# Stats Panel
# -----------------------

stats = tk.Frame(right, bg="#1A1A1A")
stats.pack(pady=20, fill="x")

tk.Label(
    stats,
    text="Today's Summary",
    fg="white",
    bg="#1A1A1A",
    font=("Segoe UI", 13, "bold")
).pack(pady=10)

present_label = tk.Label(stats, fg="#00FF88", bg="#222222",
                         font=("Segoe UI", 16, "bold"))
present_label.pack(pady=5, fill="x")

unknown_label = tk.Label(stats, fg="#FFA500", bg="#222222",
                         font=("Segoe UI", 16, "bold"))
unknown_label.pack(pady=5, fill="x")

alert_label = tk.Label(stats, fg="#FF4444", bg="#222222",
                       font=("Segoe UI", 16, "bold"))
alert_label.pack(pady=5, fill="x")

# -----------------------
# Update Stats
# -----------------------

def update_stats():
    today = datetime.now().strftime("%Y-%m-%d")

    present = attendance.count_documents({"date": today})
    total_users = users.count_documents({})

    unknown = max(0, total_users - present)

    present_label.config(text=f"Present: {present}")
    unknown_label.config(text=f"Unknown: {unknown}")
    alert_label.config(text=f"Alerts: 0")

    root.after(2000, update_stats)

update_stats()

# -----------------------
# Run
# -----------------------

root.mainloop()