import pandas as pd

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv(
    "src/data/processed/final.csv"
)

print("Dataset loaded successfully")

# =========================
# CONVERT DATE COLUMN
# =========================

df["Date"] = pd.to_datetime(
    df["Date"]
)

# =========================
# EXTRACT TIME FEATURES
# =========================

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day

# =========================
# SEASON FUNCTION
# =========================

def get_season(month):

    if month in [12, 1, 2]:
        return "Winter"

    elif month in [3, 4, 5]:
        return "Summer"

    elif month in [6, 7, 8, 9]:
        return "Monsoon"

    else:
        return "Post-Monsoon"

# =========================
# CREATE SEASON COLUMN
# =========================

df["Season"] = df["Month"].apply(
    get_season
)

# =========================
# ONE HOT ENCODING
# =========================

df = pd.get_dummies(

    df,

    columns=["Season"],

    dtype=int
)

# =========================
# DROP ORIGINAL DATE COLUMN
# =========================

df.drop(
    columns=["Date"],
    inplace=True
)

# =========================
# SAVE ML READY DATASET
# =========================

output_path = (
    "src/data/processed/ml_ready_time_dataset.csv"
)

df.to_csv(

    output_path,

    index=False
)

# =========================
# FINAL OUTPUT
# =========================

print("ML-ready dataset created successfully")

print(f"Saved at: {output_path}")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nPreview:")
print(df.head())