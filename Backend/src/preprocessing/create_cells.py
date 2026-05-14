import pandas as pd

# Load dataset
df = pd.read_csv("src/data/processed/ml_ready_time_dataset.csv")

# Grid size
GRID_SIZE = 0.1

# Cell creation function
def get_cell(lat, lon):
    lat_cell = int(lat / GRID_SIZE)
    lon_cell = int(lon / GRID_SIZE)

    return f"{lat_cell}_{lon_cell}"

# Create cell_id column
df["cell_id"] = df.apply(
    lambda x: get_cell(x["Latitude"], x["Longitude"]),
    axis=1
)

# Save dataset
output_path = "src/data/processed/cell_dataset.csv"

df.to_csv(output_path, index=False)

print("Cell IDs created successfully")
print(f"Saved at: {output_path}")

print("\nDataset Shape:")
print(df.shape)

print("\nUnique Cells:")
print(df['cell_id'].nunique())

print("\nPreview:")
print(df.head())