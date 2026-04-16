import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from pymongo import MongoClient
from mtcnn import MTCNN
from keras_facenet import FaceNet
from datetime import datetime

# -------------------------
# MODELS
# -------------------------

model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

detector = MTCNN()
embedder = FaceNet()

# -------------------------
# DATABASE
# -------------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_attendance"]

users_collection = db["users"]
attendance_collection = db["smart_attendance"]

# -------------------------
# LOAD USERS
# -------------------------

known_embeddings = []
known_names = []
known_ids = []

for user in users_collection.find():
    for emb in user["embeddings"]:
        known_embeddings.append(np.array(emb))
        known_names.append(user["name"])
        known_ids.append(user["user_id"])

print("Total registered faces:", len(known_embeddings))

# -------------------------
# MATCH FUNCTION
# -------------------------

def find_match(face_embedding):
    min_distance = 999
    identity = "Unknown"
    identity_id = None

    for i, known_emb in enumerate(known_embeddings):
        dist = np.linalg.norm(face_embedding - known_emb)

        if dist < min_distance:
            min_distance = dist
            identity = known_names[i]
            identity_id = known_ids[i]

    if min_distance < 0.9:
        return identity, identity_id

    return "Unknown", None

# -------------------------
# ATTENDANCE
# -------------------------

marked_today = set()

def mark_attendance(name, user_id):

    today = datetime.now().strftime("%Y-%m-%d")

    if user_id in marked_today:
        return False

    existing = attendance_collection.find_one({
        "user_id": user_id,
        "date": today
    })

    if existing is None:

        now = datetime.now()

        attendance_collection.insert_one({
            "user_id": user_id,
            "name": name,
            "date": today,
            "time": now.strftime("%H:%M:%S"),
            "attendance": "Present"
        })

        marked_today.add(user_id)
        return True

    marked_today.add(user_id)
    return False

# -------------------------
# TRACK CONTROL
# -------------------------

track_frames = {}
track_done = {}

recognized_ids = set()
attendance_ids = set()

# -------------------------
# CAMERA
# -------------------------

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    # 🔥 IMPORTANT FIX: NEVER BREAK
    if not ret or frame is None:
        continue   # keep trying, don't exit

    try:
        results = model(frame)
    except:
        continue  # avoid crash if model fails temporarily

    detections = []

    for r in results:
        for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):

            if int(cls) == 0:
                x1, y1, x2, y2 = map(int, box)
                w = x2 - x1
                h = y2 - y1

                detections.append(([x1, y1, w, h], float(conf), "person"))

    tracks = tracker.update_tracks(detections, frame=frame)

    total_detected = len([t for t in tracks if t.is_confirmed()])

    for track in tracks:

        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, r, b = map(int, track.to_ltrb())

        track_frames[track_id] = track_frames.get(track_id, 0) + 1

        if track_frames[track_id] >= 2 and not track_done.get(track_id, False):

            person_crop = frame[t:b, l:r]

            if person_crop.size == 0:
                continue

            rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)

            try:
                faces = detector.detect_faces(rgb)
            except:
                continue

            if faces is None or len(faces) == 0:
                continue

            for face in faces:

                x, y, w, h = face['box']
                x = max(0, x)
                y = max(0, y)

                if w < 30 or h < 30:
                    continue

                face_img = person_crop[y:y+h, x:x+w]

                if face_img.size == 0:
                    continue

                face_img = cv2.resize(face_img, (160,160))
                face_array = np.expand_dims(face_img, axis=0)

                try:
                    embedding = embedder.embeddings(face_array)[0]
                except:
                    continue

                name, user_id = find_match(embedding)

                if name != "Unknown":
                    recognized_ids.add(user_id)

                    if mark_attendance(name, user_id):
                        attendance_ids.add(user_id)

                    label = f"{name} (ID:{user_id})"
                    color = (0,255,0)
                else:
                    label = "Unknown"
                    color = (0,0,255)

                cv2.putText(frame, label, (l, t-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                track_done[track_id] = True

        cv2.rectangle(frame, (l,t), (r,b), (0,255,0), 2)

    # -------------------------
    # UI LEFT
    # -------------------------

    cv2.rectangle(frame, (10,300), (300,450), (60,60,60), -1)

    cv2.putText(frame, f"Detected: {total_detected}", (20,330),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,140,255), 2)

    cv2.putText(frame, f"Recognized: {len(recognized_ids)}", (20,370),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,140,255), 2)

    cv2.putText(frame, f"Marked: {len(attendance_ids)}", (20,410),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,140,255), 2)

    # -------------------------
    # UI RIGHT
    # -------------------------

    now = datetime.now()

    cv2.putText(frame, now.strftime("%H:%M:%S"), (850,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.putText(frame, now.strftime("%Y-%m-%d"), (850,70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.rectangle(frame, (850,400), (1150,460), (0,140,255), -1)
    cv2.putText(frame, "PRESS Q TO STOP", (870,440),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

    # -------------------------

    cv2.imshow("Smart Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()