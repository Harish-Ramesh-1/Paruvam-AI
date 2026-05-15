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

from src.services.llm_service import (
    generate_environment_report
)

router = APIRouter()

COMING_SOON_MESSAGE = "Our service is coming soon for this location."


def build_coming_soon_response(lat: float, lon: float, cell_id: str, message: str):
    return {
        "service_available": False,
        "service_message": message,
        "location": {
            "lat": lat,
            "lon": lon
        },
        "cell_id": cell_id
    }


@router.get("/analyze")
def analyze_location(lat: float, lon: float):

    # Create regional cell
    cell_id = get_cell_id(lat, lon)

    # Fetch live environmental data
    live_data = get_live_environmental_data(
        lat,
        lon
    )

    try:
        # Normalize live data
        normalized_result = normalize_live_data(
            cell_id,
            live_data
        )
    except ValueError as err:
        return build_coming_soon_response(
            lat,
            lon,
            cell_id,
            str(err) or COMING_SOON_MESSAGE
        )

    normalized_data = normalized_result["normalized_data"]

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

@router.get("/details")
def get_details(lat: float, lon: float):

    # Create regional cell
    cell_id = get_cell_id(lat, lon)

    # Fetch live data
    live_data = get_live_environmental_data(
        lat,
        lon
    )

    try:
        # Normalize
        normalized_result = normalize_live_data(
            cell_id,
            live_data
        )
    except ValueError as err:
        return build_coming_soon_response(
            lat,
            lon,
            cell_id,
            str(err) or COMING_SOON_MESSAGE
        )

    normalized_data = normalized_result["normalized_data"]

    # Detect anomaly
    anomaly_result = detect_anomaly(
        normalized_data
    )

    # Severity
    severity = get_risk_level(
        anomaly_result["anomaly_score"]
    )

    # Context for LLM only (report must not echo raw figures — see llm_service prompt)
    llm_input = {
        "temperature": live_data["Temperature"],
        "humidity": live_data["Humidity"],
        "aqi": live_data["us_aqi"],
        "rainfall": live_data["Rainfall"],
        "pm2_5": live_data["pm2_5"],
        "pm10": live_data["pm10"],
        "risk_level": severity["level"],
        "anomaly_detected": anomaly_result["anomaly"] == -1,
    }

    # Generate AI report
    try:
        report = generate_environment_report(
            llm_input
        )
    except Exception:
        if anomaly_result["anomaly"] == -1:
            summary = (
                "1. Environmental summary: Several signals are unusual at once compared with a typical day for this region—"
                "worth reading the day as “check conditions” rather than assuming everything is ordinary.\n"
            )
        else:
            summary = (
                "1. Environmental summary: The overall pattern looks broadly in line with a routine day for the area—"
                "a steady baseline where small shifts in comfort or air matter more than a single dramatic spike.\n"
            )
        report = (
            summary
            + "2. Possible health risks: When heat, stickiness, or murky air build together, irritation and fatigue can creep up faster than people notice—especially for lungs, circulation, and anyone already run down.\n"
            + "3. Precautions: Pace outdoor time, seek shade or cooler air when it feels heavy, drink steadily, and ease back on intense exertion if the air feels thick or harsh.\n"
            + "4. Affected sectors: Outdoor jobs, schoolyards and sports, delivery riders, and anyone with asthma, allergies, or heart issues should treat today as a day to listen to their body and adjust plans if it feels off."
        )

    return {
        "service_available": True,
        "location": {
            "lat": lat,
            "lon": lon
        },
        "cell_id": cell_id,
        "live_data": live_data,
        "normalized_data": normalized_data,
        "anomaly_result": anomaly_result,
        "risk_level":
            severity["level"],

        "report":
            report
    }
