import tkinter as tk
from tkinter import ttk
from pymongo import MongoClient
from datetime import datetime

# -----------------------
# MongoDB
# -----------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_attendance"]
attendance = db["smart_attendance"]

# -----------------------
# Window
# -----------------------

root = tk.Tk()
root.title("Corporate Attendance Panel")
root.geometry("1200x700")
root.configure(bg="#0D0D0D")

# -----------------------
# Header
# -----------------------

header = tk.Frame(root, bg="#0D0D0D")
header.pack(fill="x", pady=10)

title = tk.Label(
    header,
    text="Attendance Logs",
    font=("Segoe UI", 20, "bold"),
    fg="white",
    bg="#0D0D0D"
)
title.pack(side="left", padx=20)

# Date Input
date_entry = tk.Entry(header, font=("Segoe UI", 11))
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
date_entry.pack(side="right", padx=20)

# -----------------------
# Main Container
# -----------------------

container = tk.Frame(root, bg="#0D0D0D")
container.pack(fill="both", expand=True, padx=20, pady=10)

# -----------------------
# LEFT PANEL
# -----------------------

left = tk.Frame(container, bg="#1B1B1B", width=400, height=300)
left.pack(side="left", padx=10, pady=10)
left.pack_propagate(False)

tk.Label(
    left,
    text="Live Camera",
    fg="white",
    bg="#1B1B1B",
    font=("Segoe UI", 14)
).pack(pady=20)

tk.Label(
    left,
    text="● ON",
    fg="green",
    bg="#1B1B1B",
    font=("Segoe UI", 12, "bold")
).pack()

# -----------------------
# RIGHT TABLE
# -----------------------

right = tk.Frame(container, bg="#1B1B1B")
right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# 🔥 UPDATED COLUMNS
columns = ("ID", "Name", "Date", "Time", "Status")

tree = ttk.Treeview(right, columns=columns, show="headings", height=12)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=110)

tree.pack(fill="both", expand=True, padx=10, pady=10)

# -----------------------
# Style
# -----------------------

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#1B1B1B",
                foreground="white",
                rowheight=35,
                fieldbackground="#1B1B1B")

style.configure("Treeview.Heading",
                background="#FF7A00",
                foreground="black",
                font=("Segoe UI", 11, "bold"))

# -----------------------
# Bottom Stats
# -----------------------

bottom = tk.Frame(root, bg="#0D0D0D")
bottom.pack(pady=20)

def create_card(parent, title, value, color):
    frame = tk.Frame(parent, bg="#1B1B1B", width=200, height=100)
    frame.pack(side="left", padx=15)
    frame.pack_propagate(False)

    tk.Label(frame, text=value,
             font=("Segoe UI", 18, "bold"),
             fg=color,
             bg="#1B1B1B").pack(pady=10)

    tk.Label(frame, text=title,
             font=("Segoe UI", 12),
             fg="white",
             bg="#1B1B1B").pack()

    return frame

total_card = create_card(bottom, "Total", "0", "#A259FF")
present_card = create_card(bottom, "Present", "0", "#00FF7F")
unknown_card = create_card(bottom, "Unknown", "0", "#FFA500")
alert_card = create_card(bottom, "Alerts", "0", "#FF3B3B")

# -----------------------
# Load Data
# -----------------------

def load_logs():

    for row in tree.get_children():
        tree.delete(row)

    selected_date = date_entry.get()

    logs = attendance.find({"date": selected_date})

    total = 0
    present = 0
    unknown = 0

    for log in logs:

        total += 1

        status = log.get("attendance")

        if status == "Present":
            present += 1
            tag = "present"
        else:
            unknown += 1
            tag = "unknown"

        # 🔥 DATE ADDED HERE
        tree.insert("", "end", values=(
            log.get("user_id"),
            log.get("name"),
            log.get("date"),
            log.get("time"),
            status
        ), tags=(tag,))

    tree.tag_configure("present", foreground="#00FF7F")
    tree.tag_configure("unknown", foreground="#FFA500")

    total_card.winfo_children()[0].config(text=str(total))
    present_card.winfo_children()[0].config(text=str(present))
    unknown_card.winfo_children()[0].config(text=str(unknown))
    alert_card.winfo_children()[0].config(text="0")

# -----------------------
# Button
# -----------------------

btn = tk.Button(
    root,
    text="Refresh Logs",
    bg="#FF7A00",
    fg="black",
    font=("Segoe UI", 12, "bold"),
    command=load_logs
)
btn.pack(pady=10)

# Auto Load
load_logs()

root.mainloop()