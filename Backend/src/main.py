import pandas as pd

df = pd.read_csv(
    "src/data/processed/final.csv"
)

nasa_df = df[[
    "City",
    "Latitude",
    "Longitude",
    "Date",
    "Temperature",
    "Rainfall",
    "Humidity"
]]

nasa_df.to_csv(
    "src/data/processed/recovered_nasa_weather_data.csv",
    index=False
)

print("NASA dataset recovered")