import requests

def get_live_environmental_data(lat, lon):

    # Weather API
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,rain"
    )

    # AQI API
    aqi_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current=pm2_5,pm10,us_aqi"
    )

    weather_response = requests.get(weather_url)
    aqi_response = requests.get(aqi_url)

    weather_data = weather_response.json()
    aqi_data = aqi_response.json()

    return {
        "Temperature": weather_data["current"]["temperature_2m"],
        "Humidity": weather_data["current"]["relative_humidity_2m"],
        "Rainfall": weather_data["current"]["rain"],

        "pm2_5": aqi_data["current"]["pm2_5"],
        "pm10": aqi_data["current"]["pm10"],
        "us_aqi": aqi_data["current"]["us_aqi"]
    }


