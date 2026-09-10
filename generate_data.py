import pandas as pd
import numpy as np

# Reproducible data
np.random.seed(42)

# 1 year of hourly data
timestamps = pd.date_range(
    start="2025-01-01 00:00:00",
    end="2025-12-31 23:00:00",
    freq="h"
)

df = pd.DataFrame({"timestamp": timestamps})

# Time features
hour = df["timestamp"].dt.hour
day = df["timestamp"].dt.dayofyear

# -------------------------
# Temperature
# -------------------------
df["temperature"] = (
    27
    + 8 * np.sin(2 * np.pi * (day - 80) / 365)
    + 4 * np.sin(2 * np.pi * (hour - 14) / 24)
    + np.random.normal(0, 1.5, len(df))
)

# -------------------------
# Humidity
# -------------------------
df["humidity"] = (
    65
    - 15 * np.sin(2 * np.pi * (day - 80) / 365)
    - 10 * np.sin(2 * np.pi * (hour - 6) / 24)
    + np.random.normal(0, 4, len(df))
)

df["humidity"] = df["humidity"].clip(20, 95)

# -------------------------
# Solar Generation
# -------------------------
sunlight = np.maximum(
    0,
    np.sin(np.pi * (hour - 6) / 12)
)

season_factor = (
    0.85
    + 0.15 * np.sin(2 * np.pi * (day - 80) / 365)
)

df["solar_mw"] = (
    80
    * sunlight
    * season_factor
    + np.random.normal(0, 3, len(df))
)

df["solar_mw"] = df["solar_mw"].clip(0, None)

# -------------------------
# Wind Generation
# -------------------------
df["wind_mw"] = (
    30
    + 8 * np.sin(2 * np.pi * day / 7)
    + 5 * np.sin(2 * np.pi * hour / 24)
    + np.random.normal(0, 4, len(df))
)

df["wind_mw"] = df["wind_mw"].clip(5, 55)

# -------------------------
# Electricity Load
# -------------------------
morning_peak = 35 * np.exp(-((hour - 9) ** 2) / 8)
evening_peak = 55 * np.exp(-((hour - 19) ** 2) / 10)

temperature_effect = np.maximum(df["temperature"] - 25, 0) * 3

df["load_mw"] = (
    100
    + morning_peak
    + evening_peak
    + temperature_effect
    + 8 * np.sin(2 * np.pi * day / 365)
    + np.random.normal(0, 5, len(df))
)

df["load_mw"] = df["load_mw"].clip(70, 220)

# -------------------------
# Grid Voltage
# -------------------------
df["voltage"] = (
    230
    - (df["load_mw"] - 100) * 0.015
    + np.random.normal(0, 0.8, len(df))
)

# -------------------------
# Grid Frequency
# -------------------------
df["frequency"] = (
    50
    - (df["load_mw"] - 100) * 0.002
    + np.random.normal(0, 0.03, len(df))
)

# Save dataset
df.to_csv("data/raw/grid_data.csv", index=False)

print("Dataset generated successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())