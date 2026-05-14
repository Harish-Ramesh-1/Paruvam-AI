import pandas as pd
import requests
import time
import os

# =========================
# LOAD INPUT CSV
# =========================

df = pd.read_csv("src/data/raw/latlong.csv")

# =========================
# TARGET STATES (NEW STATES)
# =========================

target_states = [
    "Punjab",
    "Tamil Nadu",
    "Telangana",
    "Puducherry"
]

# Filter only selected states
df = df[df["State"].isin(target_states)]

# =========================
# OUTPUT FILE
# =========================

output_file = "src/data/processed/nasa_weather_data.csv"

# =========================
# LOAD EXISTING DATA
# =========================

completed_cities = set()

if os.path.exists(output_file):

    existing_df = pd.read_csv(output_file)

    completed_cities = set(existing_df["City"].unique())

    print(f"Already completed cities: {len(completed_cities)}")

# =========================
# STORE NEW DATA
# =========================

all_data = []

total = len(df)

# =========================
# MAIN LOOP
# =========================

for index, row in df.iterrows():

    lat = row['Latitude']
    lon = row['Longitude']
    city = row['Location']

    short_city = city.split()[0]

    # Skip already completed cities
    if short_city in completed_cities:

        print(f"Skipping {short_city}")

        continue

    print(f"{index+1}/{total} Processing {short_city}")

    print(f"Fetching data for Latitude: {lat}, Longitude: {lon}")

    # =========================
    # NASA POWER API
    # =========================

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=T2M,PRECTOTCORR,RH2M"
        f"&community=RE"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start=20240101"
        f"&end=20241231"
        f"&format=JSON"
    )

    try:

        response = requests.get(url, timeout=30)

        data = response.json()

        parameters = data['properties']['parameter']

        temp = parameters['T2M']
        rain = parameters['PRECTOTCORR']
        humidity = parameters['RH2M']

        # =========================
        # EXTRACT DAILY DATA
        # =========================

        for date in temp.keys():

            all_data.append({

                "City": short_city,
                "Latitude": lat,
                "Longitude": lon,
                "Date": date,

                "Temperature": temp[date],
                "Rainfall": rain[date],
                "Humidity": humidity[date]
            })

        print(f"Completed {short_city}")

    except Exception as e:

        print(f"Error processing {short_city}: {e}")

    # =========================
    # CHECKPOINT SAVE
    # =========================

    if index % 50 == 0 and len(all_data) > 0:

        temp_df = pd.DataFrame(all_data)

        if os.path.exists(output_file):

            temp_df.to_csv(
                output_file,
                mode='a',
                header=False,
                index=False
            )

        else:

            temp_df.to_csv(
                output_file,
                index=False
            )

        print("Checkpoint Saved")

        # Clear RAM
        all_data = []

    # Avoid API overload
    time.sleep(1)

# =========================
# FINAL SAVE
# =========================

if len(all_data) > 0:

    final_df = pd.DataFrame(all_data)

    if os.path.exists(output_file):

        final_df.to_csv(
            output_file,
            mode='a',
            header=False,
            index=False
        )

    else:

        final_df.to_csv(
            output_file,
            index=False
        )

print("NASA Data Collection Completed")