from ultralytics import YOLO
import cv2
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "kolkataday_yolov8.pt"
)

model = YOLO(MODEL_PATH)


def analyze_traffic(video_path):

    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")

        return {
            "vehicle_count": 0,
            "traffic_score": 0,
            "congestion_level": "Low"
        }

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open video: {video_path}")

        return {
            "vehicle_count": 0,
            "traffic_score": 0,
            "congestion_level": "Low"
        }

    frame_count = 0
    total_vehicles = 0

    max_frames = 60

    while frame_count < max_frames:

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        try:
            results = model(frame, verbose=False)

            for result in results:
                total_vehicles += len(result.boxes)

        except Exception as e:
            print("YOLO error:", e)
            continue

    cap.release()

    if frame_count == 0:
        return {
            "vehicle_count": 0,
            "traffic_score": 0,
            "congestion_level": "Low"
        }

    avg_vehicles = total_vehicles / frame_count

    if avg_vehicles < 5:
        congestion = "Low"

    elif avg_vehicles < 15:
        congestion = "Medium"

    else:
        congestion = "High"

    return {
        "vehicle_count": int(avg_vehicles * 10),
        "traffic_score": round(avg_vehicles, 2),
        "congestion_level": congestion
    }