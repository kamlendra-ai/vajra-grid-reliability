import pandas as pd
import joblib
import numpy as np


# ============================================================
# LOAD DATA + MODEL
# ============================================================

df = pd.read_csv("data/processed/grid_features.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

model = joblib.load(
    "models/load_forecasting_model.pkl"
)


# ============================================================
# MODEL FEATURES
# ============================================================

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


# ============================================================
# HISTORICAL DATA
# ============================================================

history = df.copy()

last_timestamp = history["timestamp"].iloc[-1]


# ============================================================
# GENERATE NEXT 24 HOURS
# ============================================================

future_times = pd.date_range(
    start=last_timestamp + pd.Timedelta(hours=1),
    periods=24,
    freq="h"
)

future = pd.DataFrame({
    "timestamp": future_times
})


# ============================================================
# ESTIMATE FUTURE EXTERNAL VARIABLES
# ============================================================

# Use same hour from previous week as a prototype baseline.
for column in [
    "temperature",
    "humidity",
    "solar_mw",
    "wind_mw",
    "voltage",
    "frequency",
]:
    future[column] = [
        history.iloc[-168 + i][column]
        for i in range(24)
    ]


# ============================================================
# RECURSIVE LOAD FORECAST
# ============================================================

all_loads = history["load_mw"].tolist()

predictions = []


for i in range(24):

    timestamp = future.loc[i, "timestamp"]

    hour = timestamp.hour
    day_of_week = timestamp.dayofweek
    month = timestamp.month
    day_of_year = timestamp.dayofyear
    is_weekend = int(day_of_week >= 5)

    # Lag 1
    load_lag_1 = all_loads[-1]

    # Lag 24
    load_lag_24 = all_loads[-24]

    # Lag 168
    load_lag_168 = all_loads[-168]

    # Rolling averages
    load_rolling_24 = np.mean(all_loads[-24:])
    load_rolling_168 = np.mean(all_loads[-168:])

    # Renewable lags
    if i == 0:
        solar_lag_1 = history["solar_mw"].iloc[-1]
        wind_lag_1 = history["wind_mw"].iloc[-1]
    else:
        solar_lag_1 = future.loc[i - 1, "solar_mw"]
        wind_lag_1 = future.loc[i - 1, "wind_mw"]

    row = pd.DataFrame([{
        "temperature": future.loc[i, "temperature"],
        "humidity": future.loc[i, "humidity"],
        "solar_mw": future.loc[i, "solar_mw"],
        "wind_mw": future.loc[i, "wind_mw"],
        "voltage": future.loc[i, "voltage"],
        "frequency": future.loc[i, "frequency"],
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "day_of_year": day_of_year,
        "is_weekend": is_weekend,
        "load_lag_1": load_lag_1,
        "load_lag_24": load_lag_24,
        "load_lag_168": load_lag_168,
        "load_rolling_24": load_rolling_24,
        "load_rolling_168": load_rolling_168,
        "solar_lag_1": solar_lag_1,
        "wind_lag_1": wind_lag_1,
    }])

    prediction = float(model.predict(row[features])[0])

    predictions.append(prediction)

    all_loads.append(prediction)


# ============================================================
# SAVE FORECAST
# ============================================================

future["predicted_load_mw"] = predictions

output_file = (
    "data/processed/load_forecast_24h.csv"
)

future.to_csv(
    output_file,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

peak_index = future["predicted_load_mw"].idxmax()

peak_load = future.loc[
    peak_index,
    "predicted_load_mw"
]

peak_time = future.loc[
    peak_index,
    "timestamp"
]

print("=" * 55)
print("VAJRA 24-HOUR LOAD FORECAST")
print("=" * 55)

print("\nForecast starting:")
print(future["timestamp"].iloc[0])

print("\nForecast ending:")
print(future["timestamp"].iloc[-1])

print("\nPredicted Peak Load:")
print(f"{peak_load:.2f} MW")

print("\nPredicted Peak Time:")
print(peak_time)

print("\n24-Hour Forecast:")
print(
    future[
        [
            "timestamp",
            "predicted_load_mw"
        ]
    ].to_string(index=False)
)

print("\nForecast saved:")
print(output_file)