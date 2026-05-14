import pandas as pd

# =========================
# LOAD DATASETS
# =========================

nasa_df = pd.read_csv(
    "src/data/processed/nasa_weather_data.csv"
)

aqi_df = pd.read_csv(
    "src/data/processed/daily_aqi.csv"
)

print("Datasets loaded")

# =========================
# CLEAN CITY NAMES
# =========================

nasa_df["City"] = (
    nasa_df["City"]
    .astype(str)
    .str.strip()
    .str.lower()
)

aqi_df["City"] = (
    aqi_df["City"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# =========================
# NORMALIZE DATES
# =========================

# NASA date format: 20240101
nasa_df["Date"] = pd.to_datetime(
    nasa_df["Date"],
    format="%Y%m%d",
    errors="coerce"
)

# AQI date format: 2024-01-01
aqi_df["Date"] = pd.to_datetime(
    aqi_df["Date"],
    errors="coerce"
)

# =========================
# REMOVE INVALID DATES
# =========================

nasa_df.dropna(subset=["Date"], inplace=True)

aqi_df.dropna(subset=["Date"], inplace=True)

# =========================
# MERGE DATASETS
# =========================

final_df = nasa_df.merge(

    aqi_df,

    on=["City", "Date"],

    how="inner"
)

print("Datasets merged")

# =========================
# REMOVE NULL VALUES
# =========================

final_df.dropna(inplace=True)

print("Null values removed")

# =========================
# REMOVE DUPLICATES
# =========================

final_df.drop_duplicates(inplace=True)

print("Duplicates removed")

# =========================
# RESET INDEX
# =========================

final_df.reset_index(
    drop=True,
    inplace=True
)

# =========================
# SAVE FINAL DATASET
# =========================

final_df.to_csv(

    "src/data/processed/final.csv",

    index=False
)

# =========================
# FINAL INFO
# =========================

print("Final dataset saved")

print("Final Shape:", final_df.shape)

print(final_df.head())