# import pandas as pd
# import requests
# import os
# import time

# # =========================
# # LOAD NASA DATASET
# # =========================

# nasa_df = pd.read_csv(
#     "src/data/processed/nasa_weather_data.csv"
# )

# print("NASA dataset loaded")

# # =========================
# # UNIQUE LOCATIONS
# # =========================

# locations_df = nasa_df[
#     ["City", "Latitude", "Longitude"]
# ].drop_duplicates()

# print(f"Unique locations: {len(locations_df)}")

# # =========================
# # OUTPUT FILE
# # =========================

# output_file = "src/data/processed/daily_aqi.csv"

# # =========================
# # RESUME SUPPORT
# # =========================

# completed_cities = set()

# if os.path.exists(output_file):

#     existing_df = pd.read_csv(output_file)

#     completed_cities = set(existing_df["City"].unique())

#     print(f"Already completed: {len(completed_cities)} cities")

# # =========================
# # MAIN LOOP
# # =========================

# for index, row in locations_df.iterrows():

#     city = row["City"]
#     lat = row["Latitude"]
#     lon = row["Longitude"]

#     # Skip completed cities
#     if city in completed_cities:

#         print(f"Skipping {city}")

#         continue

#     print(f"{index+1}/{len(locations_df)} Fetching AQI for {city}")

#     # =========================
#     # OPEN-METEO API
#     # =========================

#     url = (
#         f"https://air-quality-api.open-meteo.com/v1/air-quality?"
#         f"latitude={lat}"
#         f"&longitude={lon}"
#         f"&hourly=pm10,pm2_5,us_aqi"
#         f"&start_date=2024-01-01"
#         f"&end_date=2024-12-31"
#         f"&timezone=auto"
#     )

#     try:

#         response = requests.get(url, timeout=60)

#         data = response.json()

#         hourly = data.get("hourly", {})

#         dates = hourly.get("time", [])
#         pm25 = hourly.get("pm2_5", [])
#         pm10 = hourly.get("pm10", [])
#         aqi = hourly.get("us_aqi", [])

#         city_rows = []

#         # =========================
#         # STORE HOURLY TEMP DATA
#         # =========================

#         for i in range(len(dates)):

#             city_rows.append({

#                 "City": city,

#                 "Date": dates[i].split("T")[0],

#                 "pm2_5": pm25[i],
#                 "pm10": pm10[i],
#                 "us_aqi": aqi[i]
#             })

#         # =========================
#         # CONVERT TO DATAFRAME
#         # =========================

#         temp_df = pd.DataFrame(city_rows)

#         # =========================
#         # DAILY AVERAGE
#         # =========================

#         daily_df = temp_df.groupby(

#             ["City", "Date"]

#         ).mean().reset_index()

#         # =========================
#         # SAVE IMMEDIATELY
#         # =========================

#         if os.path.exists(output_file):

#             daily_df.to_csv(
#                 output_file,
#                 mode='a',
#                 header=False,
#                 index=False
#             )

#         else:

#             daily_df.to_csv(
#                 output_file,
#                 index=False
#             )

#         print(f"Saved daily AQI for {city}")

#     except Exception as e:

#         print(f"Error for {city}: {e}")

#     time.sleep(1)

# print("Daily AQI collection completed")

# =========================
# CLEAN AQI DATA
# =========================

# import pandas as pd

# file_path = "src/data/processed/daily_aqi.csv"

# df = pd.read_csv(
#     file_path,
#     on_bad_lines='skip'
# )

# # Remove duplicate headers
# df = df[df["City"] != "City"]

# # Remove duplicates
# df.drop_duplicates(inplace=True)

# df.to_csv(
#     file_path,
#     index=False
# )

# print("AQI file cleaned")

import pandas as pd
import requests
import os
import time

# =========================
# LOAD NASA DATASET
# =========================

nasa_df = pd.read_csv(
    "src/data/processed/nasa_weather_data.csv"
)

print("NASA dataset loaded")

# =========================
# UNIQUE LOCATIONS
# =========================

locations_df = nasa_df[
    ["City", "Latitude", "Longitude"]
].drop_duplicates()

# RESET INDEX
locations_df = locations_df.reset_index(drop=True)

print(f"Unique locations: {len(locations_df)}")

# =========================
# OUTPUT FILE
# =========================

output_file = "src/data/processed/daily_aqi.csv"

# =========================
# LOAD COMPLETED CITIES
# =========================

completed_cities = set()

if os.path.exists(output_file):

    try:

        existing_df = pd.read_csv(
            output_file,
            on_bad_lines='skip'
        )

        # Remove duplicate headers if present
        if "City" in existing_df.columns:

            existing_df = existing_df[
                existing_df["City"] != "City"
            ]

            completed_cities = set(

                existing_df["City"]
                .astype(str)
                .str.strip()
                .unique()
            )

    except Exception as e:

        print(f"Error reading existing AQI file: {e}")

print(f"Already completed cities: {len(completed_cities)}")

# =========================
# MAIN LOOP
# =========================

total = len(locations_df)

for index, row in locations_df.iterrows():

    city = str(row["City"]).strip()

    lat = row["Latitude"]
    lon = row["Longitude"]

    # =========================
    # SKIP COMPLETED CITIES
    # =========================

    if city in completed_cities:

        print(f"Skipping {city}")

        continue

    print(f"{index+1}/{total} Fetching AQI for {city}")

    # =========================
    # OPEN-METEO API
    # =========================

    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}"
        f"&longitude={lon}"
        f"&hourly=pm10,pm2_5,us_aqi"
        f"&start_date=2024-01-01"
        f"&end_date=2024-12-31"
        f"&timezone=auto"
    )

    try:

        response = requests.get(url, timeout=60)

        data = response.json()

        hourly = data.get("hourly", {})

        dates = hourly.get("time", [])
        pm25 = hourly.get("pm2_5", [])
        pm10 = hourly.get("pm10", [])
        aqi = hourly.get("us_aqi", [])

        city_rows = []

        # =========================
        # CREATE HOURLY DATA
        # =========================

        for i in range(len(dates)):

            city_rows.append({

                "City": city,

                "Date": dates[i].split("T")[0],

                "pm2_5": pm25[i],
                "pm10": pm10[i],
                "us_aqi": aqi[i]
            })

        # =========================
        # CONVERT TO DATAFRAME
        # =========================

        temp_df = pd.DataFrame(city_rows)

        # =========================
        # DAILY AVERAGE
        # =========================

        daily_df = temp_df.groupby(

            ["City", "Date"]

        ).mean().reset_index()

        # =========================
        # SAVE IMMEDIATELY
        # =========================

        if os.path.exists(output_file):

            daily_df.to_csv(
                output_file,
                mode='a',
                header=False,
                index=False
            )

        else:

            daily_df.to_csv(
                output_file,
                index=False
            )

        print(f"Saved AQI data for {city}")

    except Exception as e:

        print(f"Error for {city}: {e}")

    # Avoid API overload
    time.sleep(1)

print("AQI collection resume completed")