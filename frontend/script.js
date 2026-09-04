// ============================================================
// MAP INITIALIZATION
// ============================================================

const map = L.map("map").setView(
    [22.5726, 88.3639],
    13
);


// ============================================================
// OPENSTREETMAP TILES
// ============================================================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// ============================================================
// GLOBAL VARIABLES
// ============================================================

let routeLayers = [];

let sourceMarker = null;

let destinationMarker = null;


// ============================================================
// GEOCODE LOCATION
// Converts location name → latitude + longitude
// ============================================================

async function geocodeLocation(location) {

    console.log("Searching location:", location);

    const response = await fetch(
        "/api/geocode",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                location: location
            })
        }
    );


    let data;

    try {

        data = await response.json();

    }
    catch (error) {

        throw new Error(
            "Invalid response from geocoding service."
        );

    }


    if (!response.ok) {

        throw new Error(
            data.error ||
            `Unable to find location: ${location}`
        );

    }


    if (
        data.latitude === undefined ||
        data.longitude === undefined
    ) {

        throw new Error(
            `Coordinates not found for ${location}`
        );

    }


    console.log(
        "Location found:",
        data.display_name
    );

    console.log(
        "Latitude:",
        data.latitude
    );

    console.log(
        "Longitude:",
        data.longitude
    );


    return data;

}


// ============================================================
// OPTIMIZE ROUTE
// ============================================================

async function optimizeRoute() {

    // --------------------------------------------------------
    // GET LOCATION NAMES
    // --------------------------------------------------------

    const sourceLocation =
        document
            .getElementById("sourceLocation")
            .value
            .trim();


    const destinationLocation =
        document
            .getElementById("destinationLocation")
            .value
            .trim();


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (!sourceLocation) {

        showError(
            "Please enter the source location."
        );

        return;

    }


    if (!destinationLocation) {

        showError(
            "Please enter the destination location."
        );

        return;

    }


    // --------------------------------------------------------
    // SHOW LOADING
    // --------------------------------------------------------

    const button =
        document.getElementById(
            "optimizeBtn"
        );


    button.disabled = true;

    button.innerText =
        "Finding Locations...";


    document
        .getElementById("loading")
        .classList.remove("hidden");


    document
        .getElementById("errorBox")
        .classList.add("hidden");


    // Hide old results

    document
        .getElementById("resultPanel")
        .classList.add("hidden");


    document
        .getElementById("routesPanel")
        .classList.add("hidden");


    // --------------------------------------------------------
    // CLEAR PREVIOUS ROUTES
    // --------------------------------------------------------

    clearRoutes();


    // --------------------------------------------------------
    // FIND SOURCE + DESTINATION
    // --------------------------------------------------------

    try {

        // ====================================================
        // SOURCE GEOCODING
        // ====================================================

        button.innerText =
            "Finding Source...";


        const source =
            await geocodeLocation(
                sourceLocation
            );


        // Display source coordinates

        const sourceCoordinates =
            document.getElementById(
                "sourceCoordinates"
            );


        sourceCoordinates.innerText =
            `${source.latitude.toFixed(6)}, ` +
            `${source.longitude.toFixed(6)} ✓`;


        // ====================================================
        // DESTINATION GEOCODING
        // ====================================================

        button.innerText =
            "Finding Destination...";


        const destination =
            await geocodeLocation(
                destinationLocation
            );


        // Display destination coordinates

        const destinationCoordinates =
            document.getElementById(
                "destinationCoordinates"
            );


        destinationCoordinates.innerText =
            `${destination.latitude.toFixed(6)}, ` +
            `${destination.longitude.toFixed(6)} ✓`;


        // ====================================================
        // ADD SOURCE MARKER
        // ====================================================

        if (sourceMarker) {

            map.removeLayer(
                sourceMarker
            );

        }


        sourceMarker =
            L.marker(
                [
                    source.latitude,
                    source.longitude
                ]
            )
            .addTo(map)
            .bindPopup(
                `<b>🚑 Ambulance Source</b><br>` +
                `${source.display_name}`
            );


        // ====================================================
        // ADD DESTINATION MARKER
        // ====================================================

        if (destinationMarker) {

            map.removeLayer(
                destinationMarker
            );

        }


        destinationMarker =
            L.marker(
                [
                    destination.latitude,
                    destination.longitude
                ]
            )
            .addTo(map)
            .bindPopup(
                `<b>🏥 Destination</b><br>` +
                `${destination.display_name}`
            );


        // ====================================================
        // ZOOM TO SOURCE + DESTINATION
        // ====================================================

        const locationBounds =
            L.latLngBounds(
                [
                    source.latitude,
                    source.longitude
                ],
                [
                    destination.latitude,
                    destination.longitude
                ]
            );


        map.fitBounds(
            locationBounds,
            {
                padding: [50, 50]
            }
        );


        // ====================================================
        // SEND COORDINATES TO FLASK
        // ====================================================

        button.innerText =
            "Analyzing Routes...";


        const response =
            await fetch(
                "/api/best_route",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        // Backend expects:
                        // [longitude, latitude]

                        source: [
                            source.longitude,
                            source.latitude
                        ],

                        destination: [
                            destination.longitude,
                            destination.latitude
                        ]

                    })
                }
            );


        // ====================================================
        // READ RESPONSE
        // ====================================================

        let data;

        try {

            data = await response.json();

        }
        catch (error) {

            throw new Error(
                "Invalid response from Flask server."
            );

        }


        // ====================================================
        // CHECK SERVER ERROR
        // ====================================================

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Unable to calculate route."
            );

        }


        // ====================================================
        // DISPLAY BEST ROUTE
        // ====================================================

        displayResult(data);


        // ====================================================
        // DISPLAY ALL ROUTES
        // ====================================================

        displayRoutes(data);


    }
    catch (error) {

        console.error(
            "Route optimization error:",
            error
        );


        showError(
            error.message ||
            "Something went wrong."
        );

    }
    finally {

        // ----------------------------------------------------
        // RESTORE BUTTON
        // ----------------------------------------------------

        button.disabled = false;

        button.innerText =
            "🚑 Find Best Route";


        // ----------------------------------------------------
        // HIDE LOADING
        // ----------------------------------------------------

        document
            .getElementById("loading")
            .classList.add("hidden");

    }

}


// ============================================================
// DISPLAY BEST ROUTE RESULT
// ============================================================

function displayResult(data) {

    const resultPanel =
        document.getElementById(
            "resultPanel"
        );


    resultPanel.classList.remove(
        "hidden"
    );


    // --------------------------------------------------------
    // BEST ROUTE
    // --------------------------------------------------------

    document
        .getElementById("bestRoute")
        .innerText =
        data.best_route || "-";


    // --------------------------------------------------------
    // DISTANCE
    // --------------------------------------------------------

    document
        .getElementById("distance")
        .innerText =
        data.distance || "-";


    // --------------------------------------------------------
    // DURATION
    // --------------------------------------------------------

    document
        .getElementById("duration")
        .innerText =
        data.duration || "-";


    // --------------------------------------------------------
    // TRAFFIC SCORE
    // --------------------------------------------------------

    document
        .getElementById("trafficScore")
        .innerText =
        data.traffic_score ?? "-";


    // --------------------------------------------------------
    // VEHICLE COUNT
    // --------------------------------------------------------

    document
        .getElementById("vehicleCount")
        .innerText =
        data.vehicle_count ?? "-";


    // --------------------------------------------------------
    // CONGESTION
    // --------------------------------------------------------

    const congestion =
        document.getElementById(
            "congestion"
        );


    const congestionLevel =
        data.congestion_level ||
        "Unknown";


    congestion.innerText =
        "Traffic: " +
        congestionLevel;


    // --------------------------------------------------------
    // CONGESTION COLOR
    // --------------------------------------------------------

    if (
        congestionLevel === "Low"
    ) {

        congestion.style.background =
            "#dcfce7";

        congestion.style.color =
            "#166534";

    }

    else if (
        congestionLevel === "Medium"
    ) {

        congestion.style.background =
            "#fef9c3";

        congestion.style.color =
            "#854d0e";

    }

    else if (
        congestionLevel === "High"
    ) {

        congestion.style.background =
            "#fee2e2";

        congestion.style.color =
            "#991b1b";

    }

    else {

        congestion.style.background =
            "#e5e7eb";

        congestion.style.color =
            "#374151";

    }

}


// ============================================================
// DISPLAY ALL ROUTES
// ============================================================

function displayRoutes(data) {

    const routesList =
        document.getElementById(
            "routesList"
        );


    routesList.innerHTML = "";


    document
        .getElementById("routesPanel")
        .classList.remove("hidden");


    const allRoutes =
        data.all_routes || [];


    // --------------------------------------------------------
    // NO ROUTES
    // --------------------------------------------------------

    if (allRoutes.length === 0) {

        routesList.innerHTML =
            "<p>No alternative routes available.</p>";

        return;

    }


    // --------------------------------------------------------
    // DRAW EVERY ROUTE
    // --------------------------------------------------------

    allRoutes.forEach(
        (route, index) => {

            const isBest =
                route.name ===
                data.best_route;


            // =================================================
            // CONVERT OSRM COORDINATES
            // [longitude, latitude]
            // →
            // [latitude, longitude]
            // =================================================

            const latLngs =
                route.coords.map(
                    coord => [
                        coord[1],
                        coord[0]
                    ]
                );


            // =================================================
            // DRAW ROUTE
            // =================================================

            const line =
                L.polyline(
                    latLngs,
                    {

                        weight:
                            isBest ? 7 : 4,

                        opacity:
                            isBest ? 1 : 0.55,

                        color:
                            isBest
                                ? "#16a34a"
                                : "#2563eb"

                    }
                )
                .addTo(map);


            // =================================================
            // ROUTE POPUP
            // =================================================

            line.bindPopup(`

                <b>${route.name}</b>

                <br>

                📏 Distance:
                ${route.distance}

                <br>

                ⏱️ Duration:
                ${route.duration}

                <br>

                🚦 Traffic Score:
                ${route.traffic_score}

                <br>

                🚗 Vehicles:
                ${route.vehicle_count ?? "-"}

                <br>

                🚦 Congestion:
                ${route.congestion_level}

            `);


            // Store route layer

            routeLayers.push(
                line
            );


            // =================================================
            // CREATE ROUTE CARD
            // =================================================

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "route-card" +
                (
                    isBest
                        ? " best"
                        : ""
                );


            card.innerHTML = `

                <div class="route-title">

                    <span>

                        ${
                            isBest
                                ? "🚑 "
                                : ""
                        }

                        ${route.name}

                    </span>


                    <span>

                        Traffic:
                        ${route.traffic_score}

                    </span>

                </div>


                <div class="route-details">

                    📏 ${route.distance}

                    &nbsp; | &nbsp;

                    ⏱️ ${route.duration}

                    <br>

                    🚗 Vehicles:
                    ${route.vehicle_count ?? "-"}

                    &nbsp; | &nbsp;

                    🚦 ${route.congestion_level}

                </div>

            `;


            // =================================================
            // CLICK ROUTE CARD
            // =================================================

            card.addEventListener(
                "click",
                () => {

                    map.fitBounds(
                        line.getBounds(),
                        {
                            padding: [
                                30,
                                30
                            ]
                        }
                    );


                    line.openPopup();

                }
            );


            routesList.appendChild(
                card
            );

        }
    );


    // ========================================================
    // FIT MAP TO BEST ROUTE
    // ========================================================

    const bestRoute =
        allRoutes.find(
            route =>
                route.name ===
                data.best_route
        );


    if (bestRoute) {

        const bestLatLngs =
            bestRoute.coords.map(
                coord => [
                    coord[1],
                    coord[0]
                ]
            );


        const bounds =
            L.latLngBounds(
                bestLatLngs
            );


        map.fitBounds(
            bounds,
            {
                padding: [
                    50,
                    50
                ]
            }
        );

    }

}


// ============================================================
// CLEAR OLD ROUTES
// ============================================================

function clearRoutes() {

    routeLayers.forEach(
        layer => {

            map.removeLayer(
                layer
            );

        }
    );


    routeLayers = [];

}


// ============================================================
// ERROR MESSAGE
// ============================================================

function showError(message) {

    const errorBox =
        document.getElementById(
            "errorBox"
        );


    errorBox.innerText =
        "⚠️ " + message;


    errorBox.classList.remove(
        "hidden"
    );

}


// ============================================================
// INITIAL BACKEND CHECK
// ============================================================

async function checkBackend() {

    try {

        const response =
            await fetch("/");


        if (response.ok) {

            document
                .getElementById(
                    "statusDot"
                )
                .style.background =
                "#22c55e";


            document
                .getElementById(
                    "statusText"
                )
                .innerText =
                "Backend Connected";

        }

        else {

            throw new Error(
                "Backend unavailable"
            );

        }

    }
    catch (error) {

        console.error(
            "Backend check failed:",
            error
        );


        document
            .getElementById(
                "statusDot"
            )
            .style.background =
            "#ef4444";


        document
            .getElementById(
                "statusText"
            )
            .innerText =
            "Backend Offline";

    }

}


// ============================================================
// START BACKEND CHECK
// ============================================================

checkBackend();