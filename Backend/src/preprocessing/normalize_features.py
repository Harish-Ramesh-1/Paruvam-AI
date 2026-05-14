import pandas as pd

# Load datasets
df = pd.read_csv("src/data/processed/cell_dataset.csv")
regional_stats = pd.read_csv(
    "src/data/processed/regional_baselines.csv"
)

# Merge regional statistics into main dataset
df = df.merge(
    regional_stats,
    on="cell_id",
    how="left"
)

# Normalize features
features = [
    "Temperature",
    "Rainfall",
    "Humidity",
    "pm2_5",
    "pm10",
    "us_aqi"
]

for feature in features:
    mean_col = f"{feature}_mean"
    std_col = f"{feature}_std"

    norm_col = f"{feature}_norm"

    df[norm_col] = (
        (df[feature] - df[mean_col]) /
        df[std_col]
    )

# Save normalized dataset
output_path = "src/data/processed/normalized_dataset.csv"

df.to_csv(output_path, index=False)

print("Regional normalization completed successfully")
print(f"Saved at: {output_path}")

print("\nDataset Shape:")
print(df.shape)

print("\nNormalized Columns:")
norm_cols = [col for col in df.columns if "_norm" in col]
print(norm_cols)

print("\nPreview:")
print(df[norm_cols].head())