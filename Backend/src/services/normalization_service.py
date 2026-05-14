import pandas as pd

# Load regional baselines once
regional_stats = pd.read_csv(
    "src/data/processed/regional_baselines.csv"
)


def normalize_live_data(cell_id, live_data):

    # Try exact cell match
    region = regional_stats[
        regional_stats["cell_id"] == cell_id
    ]

    # Fallback to nearest cell if missing
    if region.empty:

        # Split target cell
        target_lat, target_lon = map(
            int,
            cell_id.split("_")
        )

        # Create temporary distance column
        regional_stats["distance"] = (
            (
                regional_stats["cell_id"]
                .str.split("_")
                .str[0]
                .astype(int) - target_lat
            ) ** 2

            +

            (
                regional_stats["cell_id"]
                .str.split("_")
                .str[1]
                .astype(int) - target_lon
            ) ** 2
        )

        # Find nearest available region
        region = regional_stats.sort_values(
            "distance"
        ).iloc[[0]]

    # Convert single-row dataframe → series
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
        ] = float(normalized_value)

    return normalized_data