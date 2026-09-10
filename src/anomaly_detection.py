import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest


# -------------------------
# Load dataset
# -------------------------
df = pd.read_csv("data/processed/grid_features.csv")

# Features for anomaly detection
features = [
    "load_mw",
    "solar_mw",
    "wind_mw",
    "temperature",
    "humidity",
    "voltage",
    "frequency",
]

X = df[features]

# -------------------------
# Isolation Forest
# -------------------------
model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

model.fit(X)

# Predictions
df["anomaly_prediction"] = model.predict(X)

# -1 = anomaly
#  1 = normal
df["anomaly"] = df["anomaly_prediction"].apply(
    lambda x: 1 if x == -1 else 0
)

# Anomaly score
df["anomaly_score"] = -model.score_samples(X)

# -------------------------
# Save model
# -------------------------
model_path = "models/anomaly_detection_model.pkl"

joblib.dump(model, model_path)

# Save results
output_file = "data/processed/anomaly_results.csv"

df.to_csv(output_file, index=False)

# -------------------------
# Results
# -------------------------
anomalies = df[df["anomaly"] == 1]

print("=" * 50)
print("VAJRA ANOMALY DETECTION")
print("=" * 50)

print("\nTotal observations:", len(df))
print("Anomalies detected:", len(anomalies))
print(
    "Anomaly percentage:",
    round(len(anomalies) / len(df) * 100, 2),
    "%"
)

print("\nSample anomalies:")
print(
    anomalies[
        [
            "timestamp",
            "load_mw",
            "solar_mw",
            "wind_mw",
            "voltage",
            "frequency",
            "anomaly_score",
        ]
    ].head(10).to_string(index=False)
)

print("\nModel saved:")
print(model_path)

print("\nResults saved:")
print(output_file)