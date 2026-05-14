

var API_URL = "http://127.0.0.1:8000";
var map, markers = [];

var riskColors = {
    "NORMAL": "#22c55e", "LOW": "#eab308", "HIGH": "#f97316",
    "VERY HIGH": "#ef4444", "EXTREME": "#881337"
};


// ── Initialize Map ──
window.addEventListener("DOMContentLoaded", function () {
    map = L.map("map").setView([20.5, 78.9], 5);

    // Google Maps-style tiles (English labels)
    L.tileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
        attribution: "Map data © Google",
        maxZoom: 20
    }).addTo(map);

    map.on("click", function (e) {
        var lat = e.latlng.lat.toFixed(4);
        var lon = e.latlng.lng.toFixed(4);
        document.getElementById("locationInput").value = lat + ", " + lon;
        analyzeLocation(parseFloat(lat), parseFloat(lon));
    });

    document.getElementById("locationInput").addEventListener("keydown", function (e) {
        if (e.key === "Enter") handleSearch();
    });
});


// ── Search Handler ──
// Supports both: "Chennai" (city name) or "13.08, 80.27" (coordinates)
function handleSearch() {
    var input = document.getElementById("locationInput").value.trim();
    if (!input) return;

    var parts = input.split(",");
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
        analyzeLocation(parseFloat(parts[0]), parseFloat(parts[1]));
    } else {
    
        searchCity(input);
    }
}


// ── Convert city name → la     t/lon using free Nominatim API ──
async function searchCity(cityName) {
    document.getElementById("loader").style.display = "flex";
    document.getElementById("locationInput").value = cityName;

    try {
        var url = "https://nominatim.openstreetmap.org/search?q=" + encodeURIComponent(cityName) + "&format=json&limit=1";
        var response = await fetch(url);
        var results = await response.json();

        if (results.length === 0) {
            alert("City not found: " + cityName);
            document.getElementById("loader").style.display = "none";
            return;
        }

        var lat = parseFloat(results[0].lat);
        var lon = parseFloat(results[0].lon);
        document.getElementById("locationInput").value = cityName + " (" + lat.toFixed(2) + ", " + lon.toFixed(2) + ")";

        await analyzeLocation(lat, lon);
    } catch (err) {
        alert("Could not search city: " + err.message);
        document.getElementById("loader").style.display = "none";
    }
}


// ══════════════════════════════════════════════════
//  MAIN: Send lat/lon to backend for analysis
//
//  Calls: GET http://127.0.0.1:8000/analyze?lat=X&lon=Y
//  File:  Backend/src/api/api_routes.py
// ══════════════════════════════════════════════════
async function analyzeLocation(lat, lon) {
    document.getElementById("loader").style.display = "flex";

    try {
        var response = await fetch(API_URL + "/analyze?lat=" + lat + "&lon=" + lon);
        if (!response.ok) throw new Error("Backend error " + response.status);
        var data = await response.json();

        showResults(data);
        addMarker(data);
        map.setView([lat, lon], 10);
    } catch (err) {
        alert("Cannot connect to backend!\n\nStart backend:\n  cd Backend\n  uvicorn src.main:app --reload\n\n" + err.message);
    }

    document.getElementById("loader").style.display = "none";
}


// ── Show Results ──
function showResults(data) {
    document.getElementById("emptyState").style.display = "none";
    document.getElementById("results").style.display = "block";

    document.getElementById("locationLabel").textContent =
        data.location.lat.toFixed(4) + "°, " + data.location.lon.toFixed(4) + "°  |  Cell: " + data.cell_id;

    var color = riskColors[data.risk_level] || "#6366f1";
    document.getElementById("riskCard").style.background = color;
    document.getElementById("riskLevel").textContent = data.risk_level;
    document.getElementById("anomalyScore").textContent = data.anomaly_result.anomaly_score.toFixed(4);

    showAlerts(data);
    showDataCards(data);
    renderRiskDetails(data);
}


function showAlerts(data) {
    var norm = data.normalized_data;
    var alerts = [];
    var features = [
        { k: "Temperature_norm", n: "Temperature" }, { k: "Humidity_norm", n: "Humidity" },
        { k: "Rainfall_norm", n: "Rainfall" }, { k: "pm2_5_norm", n: "PM2.5" },
        { k: "pm10_norm", n: "PM10" }, { k: "us_aqi_norm", n: "US AQI" }
    ];

    features.forEach(function (f) {
        var v = norm[f.k];
        if (v > 2)       alerts.push({ t: "danger",  m: "🔴 " + f.n + " is " + v.toFixed(1) + "σ above baseline" });
        else if (v > 1.5) alerts.push({ t: "warning", m: "🟠 " + f.n + " is " + v.toFixed(1) + "σ above baseline" });
        else if (v < -2)  alerts.push({ t: "danger",  m: "🔵 " + f.n + " is " + Math.abs(v).toFixed(1) + "σ below baseline" });
    });

    if (data.anomaly_result.anomaly === -1)
        alerts.unshift({ t: "danger", m: "⚠️ Isolation Forest detected ANOMALY" });

    var box = document.getElementById("alertsBox");
    var list = document.getElementById("alertsList");
    box.style.display = "block";
    list.innerHTML = alerts.length > 0
        ? alerts.map(function (a) { return '<div class="alert-item ' + a.t + '">' + a.m + '</div>'; }).join("")
        : '<div class="alert-item ok">✅ All values normal</div>';
}


// ── Data Cards ──
function showDataCards(data) {
    var L = data.live_data, N = data.normalized_data;
    var cards = [
        ["tempVal","tempSigma", L.Temperature, "°C", N.Temperature_norm, 1],
        ["humidityVal","humiditySigma", L.Humidity, "%", N.Humidity_norm, 0],
        ["rainfallVal","rainfallSigma", L.Rainfall, "mm", N.Rainfall_norm, 1],
        ["pm25Val","pm25Sigma", L.pm2_5, "", N.pm2_5_norm, 1],
        ["pm10Val","pm10Sigma", L.pm10, "", N.pm10_norm, 1],
        ["aqiVal","aqiSigma", L.us_aqi, "", N.us_aqi_norm, 0]
    ];
    var els = document.querySelectorAll(".data-card");

    cards.forEach(function (c, i) {
        document.getElementById(c[0]).textContent = c[2].toFixed(c[5]) + c[3];
        var s = document.getElementById(c[1]);
        s.textContent = (c[4] >= 0 ? "+" : "") + c[4].toFixed(2) + "σ";
        s.className = "card-sigma " + (Math.abs(c[4]) < 1 ? "normal" : c[4] > 0 ? "high" : "low");
        els[i].className = "data-card" + (Math.abs(c[4]) > 1.5 ? " anomalous" : "");
    });
}


function riskBand(sigma) {
    var a = Math.abs(sigma);
    if (a >= 2) return "critical";
    if (a >= 1.5) return "watch";
    if (a >= 1) return "mild";
    return "normal";
}


function cautionForFactor(name, sigma) {
    var high = sigma > 0;
    if (name === "Temperature") return high
        ? "Limit outdoor exertion in peak hours, hydrate frequently, and monitor vulnerable groups."
        : "Watch for sudden cold stress and keep indoor spaces stable for sensitive people.";
    if (name === "Humidity") return high
        ? "High humidity can worsen heat stress; improve airflow and reduce prolonged exposure."
        : "Low humidity can irritate eyes/airways; consider hydration and humidification indoors.";
    if (name === "Rainfall") return high
        ? "Check for localized waterlogging and transport disruption risk before travel."
        : "Low rainfall may increase dryness and dust movement; track air quality closely.";
    if (name === "PM2.5" || name === "PM10") return high
        ? "Sensitive groups should reduce outdoor activity and use proper masks when needed."
        : "Particulate levels are below usual baseline; continue routine monitoring.";
    if (name === "US AQI") return high
        ? "Elevated AQI suggests poorer air; reduce outdoor intensity and keep medication ready."
        : "AQI is currently below baseline risk; maintain normal precautions.";
    return "Continue monitoring this factor for rapid local changes.";
}


function renderRiskDetails(data) {
    var featureMap = [
        { key: "Temperature_norm", name: "Temperature", unit: "°C", live: data.live_data.Temperature },
        { key: "Humidity_norm", name: "Humidity", unit: "%", live: data.live_data.Humidity },
        { key: "Rainfall_norm", name: "Rainfall", unit: "mm", live: data.live_data.Rainfall },
        { key: "pm2_5_norm", name: "PM2.5", unit: "", live: data.live_data.pm2_5 },
        { key: "pm10_norm", name: "PM10", unit: "", live: data.live_data.pm10 },
        { key: "us_aqi_norm", name: "US AQI", unit: "", live: data.live_data.us_aqi }
    ];

    var factors = featureMap.map(function (f) {
        var sigma = data.normalized_data[f.key];
        return {
            name: f.name,
            sigma: sigma,
            absSigma: Math.abs(sigma),
            direction: sigma >= 0 ? "above" : "below",
            live: f.live,
            unit: f.unit,
            band: riskBand(sigma)
        };
    }).sort(function (a, b) {
        return b.absSigma - a.absSigma;
    });

    var top = factors.slice(0, 3);
    var summary = document.getElementById("riskSummary");
    summary.textContent = "Primary influence from " + top.map(function (f) { return f.name; }).join(", ") + ". Higher absolute sigma implies greater deviation from local baseline.";

    var factorsHtml = top.map(function (f) {
        var trend = f.direction === "above" ? "above baseline" : "below baseline";
        var severity = f.band === "critical" ? "Critical" : f.band === "watch" ? "Watch" : f.band === "mild" ? "Mild" : "Normal";
        return '<div class="risk-factor-item">'
            + '<div class="risk-factor-head"><strong>' + f.name + '</strong><span class="risk-tag ' + f.band + '">' + severity + '</span></div>'
            + '<div class="risk-factor-body">Live: ' + f.live + f.unit + ' | Deviation: ' + (f.sigma >= 0 ? '+' : '') + f.sigma.toFixed(2) + 'σ (' + trend + ')</div>'
            + '</div>';
    }).join("");
    document.getElementById("riskFactorsList").innerHTML = factorsHtml;

    var cautionTargets = factors.filter(function (f) { return f.absSigma >= 1; }).slice(0, 4);
    if (cautionTargets.length === 0) cautionTargets = top.slice(0, 2);
    var cautionsHtml = cautionTargets.map(function (f) {
        return '<div class="risk-caution-item">• <strong>' + f.name + ':</strong> ' + cautionForFactor(f.name, f.sigma) + '</div>';
    }).join("");
    document.getElementById("riskCautionsList").innerHTML = cautionsHtml;

    var anomalyType = data.anomaly_result.anomaly === -1 ? "Anomalous pattern detected" : "No anomaly pattern detected";
    document.getElementById("riskMeta").innerHTML =
        '<div><strong>Model status:</strong> ' + anomalyType + '</div>'
        + '<div><strong>Anomaly score:</strong> ' + data.anomaly_result.anomaly_score.toFixed(4) + '</div>'
        + '<div><strong>Cell reference:</strong> ' + data.cell_id + '</div>'
        + '<div><strong>Interpretation note:</strong> Risk is estimated from relative deviation (sigma), not absolute health diagnosis.</div>';

    var panel = document.getElementById("riskDetailsPanel");
    var btn = document.getElementById("riskDetailsBtn");
    panel.style.display = "none";
    btn.textContent = "View Risk Details";
}


function toggleRiskDetails() {
    var panel = document.getElementById("riskDetailsPanel");
    var btn = document.getElementById("riskDetailsBtn");
    var open = panel.style.display === "block";
    panel.style.display = open ? "none" : "block";
    btn.textContent = open ? "View Risk Details" : "Hide Risk Details";
}


// ── Map Marker ──
function addMarker(data) {
    markers.forEach(function (m) { map.removeLayer(m); });
    markers = [];
    var c = riskColors[data.risk_level] || "#6366f1";
    var m = L.circleMarker([data.location.lat, data.location.lon], {
        color: c, fillColor: c, fillOpacity: 0.7, radius: 12, weight: 3
    }).addTo(map);
    m.bindPopup("<b style='color:" + c + "'>" + data.risk_level + "</b><br><small>Score: " + data.anomaly_result.anomaly_score.toFixed(4) + "</small>").openPopup();
    markers.push(m);
}

// ── Close ──
function closeResults() {
    document.getElementById("results").style.display = "none";
    document.getElementById("emptyState").style.display = "flex";
    document.getElementById("riskDetailsPanel").style.display = "none";
    document.getElementById("riskDetailsBtn").textContent = "View Risk Details";
    markers.forEach(function (m) { map.removeLayer(m); });
    markers = [];
}
