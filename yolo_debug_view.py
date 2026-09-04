import cv2
from ultralytics import YOLO
import time

model = YOLO("yolov8n.pt") 

def debug_video(path):
    cap = cv2.VideoCapture(path)
    frame_count = 0
    total_vehicles = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)

        # Draw detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                label = model.names[cls]

                # Only count cars, bikes, buses, trucks
                if label in ["car", "motorcycle", "bus", "truck"]:
                    total_vehicles += 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        frame_count += 1

        # Show debug window
        cv2.putText(frame,
                    f"Frame: {frame_count}/30 | Vehicles: {total_vehicles}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("YOLO Traffic Debug", frame)

        if frame_count >= 250:  # same as backend logic
            break

        # Press Q to exit preview early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    avg = total_vehicles / frame_count
    print(f"\n✅ Video: {path}")
    print(f"Frames analyzed: {frame_count}")
    print(f"Total vehicles detected: {total_vehicles}")
    print(f"Average vehicles per frame: {avg:.2f}")

    return avg


if __name__ == "__main__":
    debug_video("Z:/Projects/Ambulance/backend/footage/route3.mp4")
