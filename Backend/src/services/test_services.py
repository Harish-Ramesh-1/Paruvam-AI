from src.services.cell_service import get_cell_id

from src.services.weather_service import (
    get_live_environmental_data
)

from src.services.normalization_service import (
    normalize_live_data
)

from src.services.anomaly_service import (
    detect_anomaly
)

# Coordinates
lat = 28.61
lon = 77.20

# Generate cell
cell_id = get_cell_id(lat, lon)

print("Cell ID:")
print(cell_id)

# Fetch live data
live_data = get_live_environmental_data(
    lat,
    lon
)

print("\nLive Data:")
print(live_data)

# Normalize
normalized_data = normalize_live_data(
    cell_id,
    live_data
)

print("\nNormalized Data:")
print(normalized_data)

# Detect anomaly
result = detect_anomaly(
    normalized_data
)

print("\nAnomaly Result:")
print(result)