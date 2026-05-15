

var API_URL = "http://127.0.0.1:8000";
var map, markers = [];
var lastAnalysis = null;
var detailsRequestInFlight = false;
var emptyStateDefaultHtml = null;

var riskColors = {
    "NORMAL": "#22c55e", "LOW": "#eab308", "HIGH": "#f97316",
    "VERY HIGH": "#ef4444", "EXTREME": "#881337"
};


// ── Initialize Map ──
window.addEventListener("DOMContentLoaded", function () {
    emptyStateDefaultHtml = document.getElementById("emptyState").innerHTML;
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

        if (data.service_available === false) {
            lastAnalysis = null;
            showComingSoon(data.service_message);
            return;
        }

        lastAnalysis = {
            lat: lat,
            lon: lon,
            data: data
        };

        showResults(data);
        addMarker(data);
        map.setView([lat, lon], 10);
    } catch (err) {
        alert("Cannot connect to backend!\n\nStart backend:\n  cd Backend\n  uvicorn src.main:app --reload\n\n" + err.message);
    } finally {
        document.getElementById("loader").style.display = "none";
    }
}


// ── Show Results ──
function restoreEmptyState() {
    if (emptyStateDefaultHtml !== null) {
        document.getElementById("emptyState").innerHTML = emptyStateDefaultHtml;
    }
}


function showComingSoon(message) {
    markers.forEach(function (m) { map.removeLayer(m); });
    markers = [];
    document.getElementById("results").style.display = "none";
    var emptyState = document.getElementById("emptyState");
    emptyState.style.display = "flex";
    emptyState.innerHTML = '<div><h3>Our service is coming soon</h3><p>' + escapeHtml(message || "This location is outside our current coverage.") + '</p></div>';
    resetRiskDetailsPanel();
}


function showResults(data) {
    restoreEmptyState();
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
    resetRiskDetailsPanel();
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


function resetRiskDetailsPanel() {
    document.getElementById("riskDetailsPanel").style.display = "none";
    document.getElementById("riskDetailsBtn").textContent = "View Risk Details";
    document.getElementById("riskDetailsReport").innerHTML = "";
}


function handleRiskDetailsButton() {
    var panel = document.getElementById("riskDetailsPanel");
    if (panel.style.display === "block") {
        resetRiskDetailsPanel();
        return;
    }

    fetchRiskDetails();
}


function parseReport(report) {
    var lines = (report || "").split(/\r?\n/).map(function (line) { return line.trim(); }).filter(Boolean);
    return lines.map(function (line) {
        return line.replace(/^\d+\.\s*/, "");
    });
}


function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}


function renderReportSections(report, riskLevel) {
    var lines = parseReport(report);
    var prettyRisk = escapeHtml(riskLevel || "UNKNOWN");
    var sections = lines.map(function (line, index) {
        var parts = line.split(/:\s*/);
        var title = parts.shift() || "Detail";
        var body = parts.join(": ") || line;
        return '<div class="report-section report-section-' + (index + 1) + '">'
            + '<div class="report-section-head">'
            + '<span class="report-step">' + String(index + 1).padStart(2, "0") + '</span>'
            + '<span class="report-title">' + escapeHtml(title) + '</span>'
            + '</div>'
            + '<div class="report-section-body">' + escapeHtml(body) + '</div>'
            + '</div>';
    }).join("");

    return '<div class="report-shell report-shell-' + prettyRisk.toLowerCase().replace(/[^a-z0-9]+/g, "-") + '">'
        + '<div class="report-shell-top">'
        + '<div>'
        + '<div class="report-heading">Environmental Risk Report</div>'
        + '</div>'
        + '<span class="report-chip">' + prettyRisk + '</span>'
        + '</div>'
        + '<div class="report-sections">' + sections + '</div>'
        + '</div>';
}


async function fetchRiskDetails() {
    if (!lastAnalysis || detailsRequestInFlight) return;

    var btn = document.getElementById("riskDetailsBtn");
    var panel = document.getElementById("riskDetailsPanel");
    var reportBox = document.getElementById("riskDetailsReport");

    detailsRequestInFlight = true;
    panel.style.display = "block";
    btn.textContent = "Loading Risk Details...";
    btn.disabled = true;

    reportBox.innerHTML = '<div class="details-report-line">Loading backend report...</div>';

    try {
        var response = await fetch(API_URL + "/details?lat=" + lastAnalysis.lat + "&lon=" + lastAnalysis.lon);
        if (!response.ok) throw new Error("Backend error " + response.status);
        var details = await response.json();

        if (details.service_available === false) {
            reportBox.innerHTML = '<div class="details-report-empty">' + escapeHtml(details.service_message || "Our service is coming soon for this location.") + '</div>';
            btn.textContent = "View Risk Details";
            return;
        }

        reportBox.innerHTML = details.report
            ? renderReportSections(details.report, details.risk_level)
            : '<div class="details-report-empty">No report text returned by the backend.</div>';

        btn.textContent = "Hide Risk Details";
    } catch (err) {
        reportBox.innerHTML = '<div class="details-report-empty">Check the backend server and your Gemini API key if the report is unavailable.</div>';
        btn.textContent = "View Risk Details";
    } finally {
        btn.disabled = false;
        detailsRequestInFlight = false;
    }
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
    var emptyState = document.getElementById("emptyState");
    emptyState.style.display = "flex";
    restoreEmptyState();
    resetRiskDetailsPanel();
    markers.forEach(function (m) { map.removeLayer(m); });
    markers = [];
}
