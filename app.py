
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yolo_traffic import analyze_traffic
import requests
import os


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FOOTAGE_DIR = os.path.join(
    BASE_DIR,
    "footage"
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)


# ============================================================
# CAMERA / VIDEO FILES
# ============================================================

# You currently have route1.mp4 and route2.mp4.
# The available videos are reused for demonstration purposes.

camera_feeds = {

    "Route 1": os.path.join(
        FOOTAGE_DIR,
        "route1.mp4"
    ),

    "Route 2": os.path.join(
        FOOTAGE_DIR,
        "route2.mp4"
    ),

    "Route 3": os.path.join(
        FOOTAGE_DIR,
        "route1.mp4"
    ),

    "Route 4": os.path.join(
        FOOTAGE_DIR,
        "route1.mp4"
    ),

    "Route 5": os.path.join(
        FOOTAGE_DIR,
        "route2.mp4"
    )
}





# ============================================================
# FRONTEND
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/<path:filename>", methods=["GET"])
def frontend_files(filename):
    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# ============================================================
# OSRM ROUTE FUNCTION
# ============================================================

def get_routes(source, destination):

    base_url = (
        "https://router.project-osrm.org"
        "/route/v1/driving"
    )

    lon1, lat1 = source
    lon2, lat2 = destination

    url = (
        f"{base_url}/"
        f"{lon1},{lat1};"
        f"{lon2},{lat2}"
        "?alternatives=true"
        "&overview=full"
        "&geometries=geojson"
    )

    print("\nRequesting routes from OSRM...")

    try:

        response = requests.get(
            url,
            timeout=20
        )

    except requests.RequestException as e:

        print("OSRM connection error:", e)

        return []


    if response.status_code != 200:

        print(
            "OSRM HTTP error:",
            response.status_code
        )

        return []


    try:

        data = response.json()

    except ValueError:

        print("OSRM returned invalid JSON.")

        return []


    if data.get("code") != "Ok":

        print(
            "OSRM error:",
            data
        )

        return []


    routes = []

    for route in data.get(
        "routes",
        []
    ):

        distance_km = (
            route["distance"] / 1000
        )

        duration_min = (
            route["duration"] / 60
        )

        coordinates = (
            route
            .get("geometry", {})
            .get("coordinates", [])
        )

        if not coordinates:
            continue


        routes.append({

            "name":
                f"Route {len(routes) + 1}",

            "distance":
                f"{distance_km:.2f} km",

            "duration":
                f"{duration_min:.2f} mins",

            "coords":
                coordinates
        })


    print(
        f"OSRM returned {len(routes)} route(s)."
    )

    return routes

# ============================================================
# GEOCODING API
# ============================================================

@app.route("/api/geocode", methods=["POST"])
def geocode():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON request body is required."
        }), 400

    location = data.get("location")

    if not location:
        return jsonify({
            "error": "Location is required."
        }), 400

    location = location.strip()

    if not location:
        return jsonify({
            "error": "Location cannot be empty."
        }), 400

    print("\nGeocoding location:", location)

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": location,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in"
    }

    headers = {
        "User-Agent": "AmbulanceRouteOptimization/1.0"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

    except requests.RequestException as e:

        print("Geocoding error:", e)

        return jsonify({
            "error": "Unable to connect to geocoding service."
        }), 500

    if response.status_code != 200:

        print(
            "Nominatim HTTP error:",
            response.status_code
        )

        return jsonify({
            "error": "Geocoding service returned an error."
        }), 500

    try:

        results = response.json()

    except ValueError:

        return jsonify({
            "error": "Invalid response from geocoding service."
        }), 500

    if not results:

        return jsonify({
            "error": f"Location not found: {location}"
        }), 404

    result = results[0]

    latitude = float(result["lat"])
    longitude = float(result["lon"])

    display_name = result.get(
        "display_name",
        location
    )

    print("Found location:")
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    print("Address:", display_name)

    return jsonify({

        "latitude": latitude,

        "longitude": longitude,

        "display_name": display_name

    })
# ============================================================
# BEST ROUTE API
# ============================================================

@app.route(
    "/api/best_route",
    methods=["POST"]
)
def best_route():

    print("\n")
    print("=" * 60)
    print("NEW BEST ROUTE REQUEST")
    print("=" * 60)


    # --------------------------------------------------------
    # GET JSON DATA
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "error":
                "JSON request body is required."
        }), 400


    source = data.get(
        "source"
    )

    destination = data.get(
        "destination"
    )


    # --------------------------------------------------------
    # VALIDATE SOURCE / DESTINATION
    # --------------------------------------------------------

    if (
        source is None
        or destination is None
    ):

        return jsonify({
            "error":
                "Source and destination are required."
        }), 400


    if (
        not isinstance(source, (list, tuple))
        or not isinstance(destination, (list, tuple))
    ):

        return jsonify({
            "error":
                "Source and destination must be arrays."
        }), 400


    if (
        len(source) != 2
        or len(destination) != 2
    ):

        return jsonify({
            "error":
                "Coordinates must be [longitude, latitude]."
        }), 400


    try:

        source = [
            float(source[0]),
            float(source[1])
        ]

        destination = [
            float(destination[0]),
            float(destination[1])
        ]

    except (
        ValueError,
        TypeError
    ):

        return jsonify({
            "error":
                "Coordinates must contain valid numbers."
        }), 400


    # --------------------------------------------------------
    # DISPLAY REQUEST
    # --------------------------------------------------------

    print(
        "Source:",
        source
    )

    print(
        "Destination:",
        destination
    )


    # --------------------------------------------------------
    # GET ROUTES FROM OSRM
    # --------------------------------------------------------

    routes = get_routes(
        source,
        destination
    )


    if not routes:

        return jsonify({
            "error":
                "No routes found from OSRM."
        }), 400


    # --------------------------------------------------------
    # ANALYZE ROUTES
    # --------------------------------------------------------

    analyzed_routes = []

    best_route = None

    lowest_score = float("inf")


    for route in routes:

        route_name = route["name"]


        # ----------------------------------------------------
        # GET VIDEO FOR THIS ROUTE
        # ----------------------------------------------------

        video_path = camera_feeds.get(
            route_name
        )


        if not video_path:

            print(
                f"No video configured for {route_name}"
            )

            continue


        # ----------------------------------------------------
        # CHECK VIDEO EXISTS
        # ----------------------------------------------------

        if not os.path.exists(
            video_path
        ):

            print(
                f"Video not found: {video_path}"
            )

            continue


        print("\n")
        print("-" * 50)

        print(
            f"Analyzing {route_name}"
        )

        print(
            "Video:",
            video_path
        )


        # ----------------------------------------------------
        # YOLO TRAFFIC ANALYSIS
        # ----------------------------------------------------

        try:

            traffic = analyze_traffic(
                video_path
            )

        except Exception as e:

            print(
                f"YOLO error for {route_name}:",
                e
            )

            continue


        score = float(
            traffic.get(
                "traffic_score",
                0
            )
        )

        vehicle_count = int(
            traffic.get(
                "vehicle_count",
                0
            )
        )

        congestion = traffic.get(
            "congestion_level",
            "Unknown"
        )


        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        analyzed = {

            "name":
                route_name,

            "distance":
                route["distance"],

            "duration":
                route["duration"],

            "traffic_score":
                round(score, 2),

            "vehicle_count":
                vehicle_count,

            "congestion_level":
                congestion,

            "coords":
                route["coords"]
        }


        analyzed_routes.append(
            analyzed
        )


        print(
            f"{route_name} -> "
            f"Score: {score:.2f} | "
            f"Vehicles: {vehicle_count} | "
            f"Congestion: {congestion}"
        )


        # ----------------------------------------------------
        # FIND LOWEST TRAFFIC SCORE
        # ----------------------------------------------------

        if score < lowest_score:

            lowest_score = score

            best_route = analyzed


    # ========================================================
    # CHECK ANALYSIS RESULT
    # ========================================================

    if not analyzed_routes:

        return jsonify({
            "error":
                "No routes could be analyzed."
        }), 500


    if best_route is None:

        best_route = analyzed_routes[0]


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n")
    print("=" * 60)

    print(
        "BEST ROUTE:",
        best_route["name"]
    )

    print(
        "DISTANCE:",
        best_route["distance"]
    )

    print(
        "DURATION:",
        best_route["duration"]
    )

    print(
        "TRAFFIC SCORE:",
        best_route["traffic_score"]
    )

    print(
        "VEHICLES:",
        best_route["vehicle_count"]
    )

    print(
        "CONGESTION:",
        best_route["congestion_level"]
    )

    print("=" * 60)


    # ========================================================
    # SEND RESPONSE TO FRONTEND
    # ========================================================

    return jsonify({

        "best_route":
            best_route["name"],

        "distance":
            best_route["distance"],

        "duration":
            best_route["duration"],

        "traffic_score":
            best_route["traffic_score"],

        "vehicle_count":
            best_route["vehicle_count"],

        "congestion_level":
            best_route["congestion_level"],

        "route_coords":
            best_route["coords"],

        "all_routes":
            analyzed_routes
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("🚑 AMBULANCE ROUTE OPTIMIZATION SERVER")
    print("=" * 60)

    print(
        "Backend:",
        BASE_DIR
    )

    print(
        "Frontend:",
        FRONTEND_DIR
    )

    print(
        "Footage:",
        FOOTAGE_DIR
    )


    # --------------------------------------------------------
    # CHECK FRONTEND
    # --------------------------------------------------------

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )


    if os.path.exists(
        index_file
    ):

        print(
            "[OK] Frontend index.html"
        )

    else:

        print(
            "[MISSING] frontend/index.html"
        )


    # --------------------------------------------------------
    # CHECK VIDEOS
    # --------------------------------------------------------

    print("\nConfigured videos:")


    for name, path in camera_feeds.items():

        if os.path.exists(path):

            print(
                f"[OK] {name}: {path}"
            )

        else:

            print(
                f"[MISSING] {name}: {path}"
            )


    # --------------------------------------------------------
    # START FLASK
    # --------------------------------------------------------

    print("\n")
    print(
        "Starting Flask server..."
    )

    print(
        "Open in browser:"
    )

    print(
        "http://127.0.0.1:5000/"
    )

    print("=" * 60)
    print("\n")


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )

