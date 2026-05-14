import joblib
import numpy as np
import pandas as pd

# Load trained model once
model = joblib.load(
    "src/models/isolation_forest_model.pkl"
)

def detect_anomaly(normalized_data):

    feature_order = [
        "Temperature_norm",
        "Rainfall_norm",
        "Humidity_norm",
        "pm2_5_norm",
        "pm10_norm",
        "us_aqi_norm"
    ]

    # Convert dict → ordered array
  
    X_live = pd.DataFrame([{
        feature: normalized_data[feature]
        for feature in feature_order
        }])
    # Predict anomaly
    prediction = model.predict(X_live)[0]

    # Get anomaly score
    score = model.decision_function(X_live)[0]

    return {
        "anomaly": int(prediction),
        "anomaly_score": float(score)
    }