import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load normalized dataset
df = pd.read_csv(
    "src/data/processed/normalized_dataset.csv"
)

# Features for anomaly detection
features = [
    "Temperature_norm",
    "Rainfall_norm",
    "Humidity_norm",
    "pm2_5_norm",
    "pm10_norm",
    "us_aqi_norm"
]

X = df[features]

# Create model
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

# Train model
model.fit(X)

# Predict anomalies
df["anomaly"] = model.predict(X)

# Get anomaly scores
df["anomaly_score"] = model.decision_function(X)

# Save trained model
joblib.dump(
    model,
    "src/models/isolation_forest_model.pkl"
)

# Save prediction dataset
output_path = (
    "src/data/processed/anomaly_dataset.csv"
)

df.to_csv(output_path, index=False)

print("Isolation Forest trained successfully")

print(f"Model saved at:")
print("src/models/isolation_forest_model.pkl")

print(f"\nDataset saved at:")
print(output_path)

print("\nAnomaly Distribution:")
print(df["anomaly"].value_counts())

print("\nPreview:")
print(
    df[[
        "Temperature_norm",
        "us_aqi_norm",
        "anomaly",
        "anomaly_score"
    ]].head()
)