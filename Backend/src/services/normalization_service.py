import pandas as pd

# Load regional baselines once
regional_stats = pd.read_csv(
    "src/data/processed/regional_baselines.csv"
)

def normalize_live_data(cell_id, live_data):

    # Find matching regional baseline
    region = regional_stats[
        regional_stats["cell_id"] == cell_id
    ]

    if region.empty:
        raise ValueError(
            f"No baseline found for {cell_id}"
        )

    region = region.iloc[0]

    normalized_data = {}

    features = [
        "Temperature",
        "Rainfall",
        "Humidity",
        "pm2_5",
        "pm10",
        "us_aqi"
    ]

    for feature in features:

        mean = region[f"{feature}_mean"]
        std = region[f"{feature}_std"]

        # Prevent divide-by-zero
        if std == 0:
            normalized_value = 0
        else:
            normalized_value = (
                (live_data[feature] - mean) / std
            )

        normalized_data[
            f"{feature}_norm"
        ] = normalized_value

    return normalized_data