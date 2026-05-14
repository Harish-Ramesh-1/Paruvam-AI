import pandas as pd

# Load dataset
df = pd.read_csv("src/data/processed/cell_dataset.csv")

# Calculate regional statistics
regional_stats = df.groupby("cell_id").agg({
    "Temperature": ["mean", "std"],
    "Rainfall": ["mean", "std"],
    "Humidity": ["mean", "std"],
    "pm2_5": ["mean", "std"],
    "pm10": ["mean", "std"],
    "us_aqi": ["mean", "std"]
})

# Flatten column names
regional_stats.columns = [
    "_".join(col) for col in regional_stats.columns
]

# Reset index
regional_stats.reset_index(inplace=True)

# Save regional statistics
output_path = "src/data/processed/regional_baselines.csv"

regional_stats.to_csv(output_path, index=False)

print("Regional baselines created successfully")
print(f"Saved at: {output_path}")

print("\nShape:")
print(regional_stats.shape)

print("\nPreview:")
print(regional_stats.head())