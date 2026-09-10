import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/raw/grid_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# -------------------------
# 1. Load Forecasting Pattern
# -------------------------
plt.figure(figsize=(14, 5))
plt.plot(df["timestamp"], df["load_mw"])
plt.title("Vajra - Electricity Load")
plt.xlabel("Time")
plt.ylabel("Load (MW)")
plt.tight_layout()
plt.savefig("notebooks/load_pattern.png")
plt.show()

# -------------------------
# 2. Solar Generation
# -------------------------
plt.figure(figsize=(14, 5))
plt.plot(df["timestamp"], df["solar_mw"])
plt.title("Vajra - Solar Generation")
plt.xlabel("Time")
plt.ylabel("Solar (MW)")
plt.tight_layout()
plt.savefig("notebooks/solar_pattern.png")
plt.show()

# -------------------------
# 3. Wind Generation
# -------------------------
plt.figure(figsize=(14, 5))
plt.plot(df["timestamp"], df["wind_mw"])
plt.title("Vajra - Wind Generation")
plt.xlabel("Time")
plt.ylabel("Wind (MW)")
plt.tight_layout()
plt.savefig("notebooks/wind_pattern.png")
plt.show()

# -------------------------
# 4. Temperature
# -------------------------
plt.figure(figsize=(14, 5))
plt.plot(df["timestamp"], df["temperature"])
plt.title("Vajra - Temperature")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.tight_layout()
plt.savefig("notebooks/temperature_pattern.png")
plt.show()

print("All visualization graphs generated successfully!")