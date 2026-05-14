from fastapi import APIRouter

from src.services.cell_service import (
    get_cell_id
)

from src.services.weather_service import (
    get_live_environmental_data
)

from src.services.normalization_service import (
    normalize_live_data
)

from src.services.anomaly_service import (
    detect_anomaly
)

from src.services.severity_service import (
    get_risk_level
)

router = APIRouter()

@router.get("/analyze")
def analyze_location(lat: float, lon: float):

    # Create regional cell
    cell_id = get_cell_id(lat, lon)

    # Fetch live environmental data
    live_data = get_live_environmental_data(
        lat,
        lon
    )

    # Normalize live data
    normalized_data = normalize_live_data(
        cell_id,
        live_data
    )

    # Detect anomaly
    anomaly_result = detect_anomaly(
        normalized_data
    )

    # Get severity
    severity = get_risk_level(
        anomaly_result["anomaly_score"]
    )

    return {
        "location": {
            "lat": lat,
            "lon": lon
        },
        "cell_id": cell_id,
        "live_data": live_data,
        "normalized_data": normalized_data,
        "anomaly_result": anomaly_result,
        "temperature": live_data["Temperature"],
        "humidity": live_data["Humidity"],
        "aqi": live_data["us_aqi"],
        "risk_level": severity["level"],
        "color": severity["color"],
        "anomaly_detected": anomaly_result["anomaly"] == -1,
        "anomaly_score": round(
            anomaly_result["anomaly_score"],
            3
        )
    }