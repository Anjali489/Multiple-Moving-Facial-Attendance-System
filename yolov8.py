import cv2
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")   # nano model (fast)

# Open webcam
cap = cv2.VideoCapture(0)
frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    frame_count += 1
    print("Frame:", frame_count)

    # Run YOLO detection
    results = model(frame)

    # Draw bounding boxes
    for r in results:
        boxes = r.boxes
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # detect only person (class 0 in COCO)
            if cls == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,
                            f"Person {conf:.2f}",
                            (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0,255,0),
                            2)

    cv2.imshow("YOLOv8 Person Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
     break

cap.release()
cv2.destroyAllWindows()