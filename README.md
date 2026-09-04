# 🚑 LifeRush — AI-Powered Ambulance Route Optimization

> **LifeRush** is an AI-powered emergency route optimization system that combines **OSRM route generation** with **YOLO-based traffic analysis** to help identify a lower-traffic route for ambulances.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLO-Computer%20Vision-00FFFF?logo=yolo&logoColor=black)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?logo=opencv&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-Interactive%20Map-199900?logo=leaflet&logoColor=white)
![OSRM](https://img.shields.io/badge/OSRM-Routing-2D3748)
![GitHub](https://img.shields.io/badge/GitHub-Version%20Control-181717?logo=github&logoColor=white)

</p>

---

## 🌟 What is LifeRush?

In an emergency, choosing a route based only on distance may not be enough.

**LifeRush** takes a source and destination, requests available driving routes from **OSRM**, analyzes associated traffic footage using **YOLO**, calculates a traffic score, and selects the route with the lowest traffic score.

### The core idea

```text
Upload / Configure Traffic Data
              ↓
        Generate Routes
              ↓
      Analyze Traffic
              ↓
       Calculate Score
              ↓
       Compare Routes
              ↓
       🚑 Best Route
```

---

## ✨ Key Features

- 🚑 **Emergency-focused route optimization**
- 🗺️ **Interactive Leaflet map**
- 🛣️ **OSRM-based route generation**
- 👁️ **YOLO vehicle detection**
- 🎥 **Traffic analysis from video footage**
- 📊 **Traffic score calculation**
- 🚦 **Low / Medium / High congestion classification**
- 🔄 **Route comparison**
- ⚡ **Flask REST API**
- 🌐 **Browser-based frontend**
- 📍 **Source and destination coordinate input**
- 📱 **Responsive frontend design**

---

# 🏗️ Project Architecture

LifeRush follows a simple **client-server architecture**.

```text
┌──────────────────────┐
│       Browser        │
│                      │
│      HTML / CSS      │
│      JavaScript      │
│      Leaflet.js      │
└──────────┬───────────┘
           │
           │ HTTP POST
           │ /api/best_route
           ▼
┌──────────────────────┐
│    Flask Backend     │
│       app.py         │
└──────────┬───────────┘
           │
           ├─────────────────────► OSRM
           │                         │
           │                         ▼
           │                    Route Data
           │
           └─────────────────────► YOLO
                                     │
                                     ▼
                              Traffic Analysis
                                     │
                                     ▼
                                Route Score
                                     │
                                     ▼
                              Best Route
```

### Architecture responsibilities

| Component | Responsibility |
|---|---|
| Browser | User interaction and route visualization |
| HTML | Page structure |
| CSS | UI styling |
| JavaScript | API calls and map interaction |
| Flask | Backend API and frontend serving |
| OSRM | Driving route generation |
| YOLO | Vehicle detection |
| OpenCV | Video/frame processing |
| Leaflet | Interactive map rendering |

---

# 🔄 System Workflow

```text
┌────────────────────────────┐
│           User             │
│  Source + Destination      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│         Frontend           │
│    HTML / CSS / JavaScript │
└─────────────┬──────────────┘
              │
              │ POST /api/best_route
              ▼
┌────────────────────────────┐
│          Flask             │
│         Backend            │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│           OSRM             │
│      Route Generation      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│           YOLO             │
│     Vehicle Detection      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Traffic Score & Congestion │
│         Analysis           │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Route Comparison & Best    │
│      Route Selection       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│       🚑 Best Route        │
│      Displayed on Map      │
└────────────────────────────┘
```

---

# 🧠 How Route Selection Works

For every route returned by OSRM:

1. The backend identifies the video configured for that route.
2. OpenCV reads a limited number of video frames.
3. YOLO detects objects/vehicles in each frame.
4. The average number of detections is used as the traffic score.
5. A congestion level is assigned.
6. Routes are compared using their traffic score.
7. The route with the **lowest traffic score** is selected.

```text
Route
  │
  ▼
Traffic Video
  │
  ▼
OpenCV → Frames
  │
  ▼
YOLO → Vehicle Detections
  │
  ▼
Average Detection Score
  │
  ├── < 5   → Low
  ├── < 15  → Medium
  └── ≥ 15  → High
  │
  ▼
Route Comparison
  │
  ▼
🚑 Lowest Traffic Score = Best Route
```

> **Note:** The current prototype uses YOLO detections across sampled frames. The reported vehicle count is a derived metric, not a unique vehicle count. A production implementation should use object tracking such as ByteTrack/BoT-SORT to estimate unique vehicles more accurately.

---

# 🗂️ Project Structure

```text
LifeRush/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── footage/
│   ├── route1.mp4
│   └── route2.mp4
│
├── app.py
├── yolo_traffic.py
├── yolo_debug_view.py
│
├── kolkataday_yolov8.pt
├── yolov8n.pt
│
├── requirements.txt
├── .gitignore
└── README.md
```

### File overview

<details>
<summary>📁 Click to expand file responsibilities</summary>

| File / Folder | Purpose |
|---|---|
| `frontend/index.html` | Main web interface |
| `frontend/style.css` | Frontend styling |
| `frontend/script.js` | API calls, route display and map logic |
| `app.py` | Flask server, OSRM integration and route selection |
| `yolo_traffic.py` | YOLO traffic analysis |
| `yolo_debug_view.py` | YOLO debugging / visualization utility |
| `footage/` | Traffic videos used for analysis |
| `kolkataday_yolov8.pt` | Custom YOLO model |
| `yolov8n.pt` | YOLO model |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

</details>

---

# 🛠️ Technology Stack

## Backend

- 🐍 Python
- Flask
- Flask-CORS
- Requests

## AI / Computer Vision

- YOLO
- Ultralytics
- OpenCV

## Routing

- OSRM

## Frontend

- HTML5
- CSS3
- JavaScript
- Leaflet.js
- OpenStreetMap

## Version Control

- Git
- GitHub

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Arka-ops/LIfeRush.git
cd LIfeRush
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not yet present, the main Python dependencies used by the project are:

```text
flask
flask-cors
requests
ultralytics
opencv-python
```

---

## 4. Check the project structure

Make sure the frontend exists:

```text
frontend/
├── index.html
├── style.css
└── script.js
```

And traffic footage is available locally:

```text
footage/
├── route1.mp4
└── route2.mp4
```

> The repository's `.gitignore` excludes video files because raw footage can be large. Keep the required footage in your local `footage/` directory when running the prototype.

---

## 5. Start the Flask server

From the project root:

```powershell
python app.py
```

You should see:

```text
🚑 AMBULANCE ROUTE OPTIMIZATION SERVER

Starting Flask server...

http://127.0.0.1:5000/
```

---

## 6. Open LifeRush

Open your browser:

**http://127.0.0.1:5000/**

You should see the LifeRush interface with the route-planning panel and interactive map.

---

# 🔌 API

LifeRush exposes the following main endpoint:

```text
POST /api/best_route
```

### Request

Coordinates use:

```text
[longitude, latitude]
```

Example:

```json
{
  "source": [88.3639, 22.5726],
  "destination": [88.4000, 22.5800]
}
```

### Example PowerShell request

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/best_route" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"source":[88.3639,22.5726],"destination":[88.4000,22.5800]}'
```

### Response

A successful response contains information such as:

```json
{
  "best_route": "Route 1",
  "distance": "5.17 km",
  "duration": "7.38 mins",
  "traffic_score": 12.25,
  "vehicle_count": 122,
  "congestion_level": "Medium",
  "route_coords": [],
  "all_routes": []
}
```

`route_coords` and `all_routes` are populated by the backend with the route geometry and analyzed route information.

---

# 🗺️ Frontend Flow

```text
User enters coordinates
          ↓
Click "🚑 Find Best Route"
          ↓
JavaScript sends POST request
          ↓
Flask receives coordinates
          ↓
OSRM generates route(s)
          ↓
YOLO analyzes configured traffic footage
          ↓
Flask compares traffic scores
          ↓
Best route returned as JSON
          ↓
JavaScript updates UI
          ↓
Leaflet draws route on map
```

---

# 📊 Example Output

The dashboard presents:

| Metric | Example |
|---|---|
| 🚑 Best Route | Route 1 |
| 📏 Distance | 5.17 km |
| ⏱️ Duration | 7.38 mins |
| 🚦 Traffic Score | 12.25 |
| 🚗 Vehicles | 122 |
| 🚥 Congestion | Medium |

> Values above are example output from the prototype and can change depending on the selected route, OSRM response, traffic footage and YOLO detections.

---

# 🎥 Traffic Analysis

The traffic-analysis pipeline currently processes a limited number of frames from each configured video.

```text
Video
  ↓
OpenCV
  ↓
Frame Sampling
  ↓
YOLO Inference
  ↓
Detections
  ↓
Average Traffic Score
  ↓
Congestion Level
```

### Current congestion thresholds

| Average detections / frame | Level |
|---:|---|
| `< 5` | 🟢 Low |
| `5 – <15` | 🟡 Medium |
| `≥ 15` | 🔴 High |

---

# 🧪 Testing

### Test the frontend

Open:

```text
http://127.0.0.1:5000/
```

### Test the API

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/best_route" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"source":[88.3639,22.5726],"destination":[88.4000,22.5800]}'
```

### Check Git status

```bash
git status
```

---

# ⚠️ Current Prototype Limitations

LifeRush is currently a **prototype / academic project**.

<details>
<summary>🔍 Click to see limitations</summary>

### 1. OSRM alternatives

OSRM may return only one alternative route for some source/destination pairs.

### 2. Vehicle counting

The current traffic analysis counts detections across sampled frames. It does not perform persistent vehicle tracking, so the reported vehicle count should not be interpreted as the exact number of unique vehicles.

### 3. Route-to-video mapping

The prototype maps available traffic videos to routes using the configured `camera_feeds` dictionary. Route 3–5 may reuse existing footage when dedicated videos are unavailable.

### 4. Traffic score

The current traffic score is based on YOLO detection activity. It is a prototype metric rather than a calibrated real-world congestion index.

### 5. Real-time traffic

The current implementation analyzes local video footage rather than continuously streaming live traffic-camera data.

### 6. Emergency deployment

This project should not be used as the sole decision-making system for real emergency dispatch. Real-world deployment would require validated traffic data, reliable map/routing infrastructure, safety testing, monitoring and appropriate emergency-service integration.

</details>

---

# 🔮 Future Improvements

- [ ] Real-time CCTV / camera stream integration
- [ ] YOLO object tracking with ByteTrack or BoT-SORT
- [ ] Accurate unique vehicle counting
- [ ] Dynamic traffic-weighted route scoring
- [ ] Live traffic updates
- [ ] More accurate ETA prediction
- [ ] Dedicated traffic footage for each route
- [ ] Ambulance GPS tracking
- [ ] Emergency vehicle priority routing
- [ ] Traffic-signal coordination
- [ ] Historical traffic prediction
- [ ] Database for traffic history
- [ ] Authentication and role-based access
- [ ] Cloud deployment
- [ ] Docker support
- [ ] Automated testing and CI/CD

---

# 🔐 Security & Deployment Notes

For development, the application runs locally:

```text
127.0.0.1:5000
```

For production deployment, consider:

- Production WSGI server
- HTTPS
- Environment variables for configuration
- API rate limiting
- Authentication
- Input validation
- Logging and monitoring
- Secure model/file handling
- Production-grade routing infrastructure

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then open a Pull Request on GitHub.

---

# 📜 License

Add your preferred open-source license here, such as MIT, before publishing the project for reuse.

---

# 👨‍💻 Project

**LifeRush — AI-Powered Ambulance Route Optimization**

Built with:

**Python · Flask · YOLO · OpenCV · OSRM · JavaScript · Leaflet**

<p align="center">

🚑 **Faster decisions. Smarter routes. Better emergency response.**

</p>
