import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error


# Load processed dataset
df = pd.read_csv("data/processed/grid_features.csv")

# Load trained model
model = joblib.load("models/load_forecasting_model.pkl")

# Features
features = [
    "temperature",
    "humidity",
    "solar_mw",
    "wind_mw",
    "voltage",
    "frequency",
    "hour",
    "day_of_week",
    "month",
    "day_of_year",
    "is_weekend",
    "load_lag_1",
    "load_lag_24",
    "load_lag_168",
    "load_rolling_24",
    "load_rolling_168",
    "solar_lag_1",
    "wind_lag_1",
]

# Same 80/20 time split
split_index = int(len(df) * 0.80)

test_df = df.iloc[split_index:].copy()

X_test = test_df[features]
actual = test_df["load_mw"]

# Predictions
predicted = model.predict(X_test)

test_df["predicted_load_mw"] = predicted

# Error
mae = mean_absolute_error(actual, predicted)

print("=" * 50)
print("VAJRA LOAD PREDICTION")
print("=" * 50)

print(f"\nTest samples: {len(test_df)}")
print(f"MAE: {mae:.2f} MW")

print("\nSample Predictions:")
print(
    test_df[
        ["timestamp", "load_mw", "predicted_load_mw"]
    ].head(10).to_string(index=False)
)

# -------------------------
# Plot
# -------------------------
plt.figure(figsize=(14, 6))

plt.plot(
    test_df["timestamp"],
    actual,
    label="Actual Load"
)

plt.plot(
    test_df["timestamp"],
    predicted,
    label="Predicted Load"
)

plt.title("Vajra - Actual vs Predicted Electricity Load")
plt.xlabel("Time")
plt.ylabel("Load (MW)")
plt.legend()
plt.tight_layout()

plt.savefig("notebooks/actual_vs_predicted_load.png")
plt.show()

print("\nPrediction graph saved:")
print("notebooks/actual_vs_predicted_load.png")