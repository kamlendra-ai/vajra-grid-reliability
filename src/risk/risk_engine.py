import pandas as pd


# -------------------------
# Load anomaly results
# -------------------------
df = pd.read_csv("data/processed/anomaly_results.csv")


# -------------------------
# Load Stress Score
# -------------------------
# 180 MW ko high-load reference point maana gaya hai.
load_score = ((df["load_mw"] - 100) / 80 * 100).clip(0, 100)


# -------------------------
# Renewable Shortfall Score
# -------------------------
renewable_generation = df["solar_mw"] + df["wind_mw"]

supply_gap = df["load_mw"] - renewable_generation

renewable_score = (
    supply_gap / 150 * 100
).clip(0, 100)


# -------------------------
# Voltage Risk
# -------------------------
voltage_deviation = abs(df["voltage"] - 230)

voltage_score = (
    voltage_deviation / 4 * 100
).clip(0, 100)


# -------------------------
# Frequency Risk
# -------------------------
frequency_deviation = abs(df["frequency"] - 50)

frequency_score = (
    frequency_deviation / 0.3 * 100
).clip(0, 100)


# -------------------------
# Anomaly Risk
# -------------------------
anomaly_score = df["anomaly"] * 100


# -------------------------
# Combined Vajra Risk Score
# -------------------------
df["risk_score"] = (
    load_score * 0.30
    + renewable_score * 0.25
    + voltage_score * 0.15
    + frequency_score * 0.15
    + anomaly_score * 0.15
)

df["risk_score"] = df["risk_score"].clip(0, 100).round(2)


# -------------------------
# Risk Level
# -------------------------
def get_risk_level(score):

    if score <= 30:
        return "SAFE"

    elif score <= 60:
        return "WATCH"

    elif score <= 80:
        return "HIGH"

    else:
        return "CRITICAL"


df["risk_level"] = df["risk_score"].apply(get_risk_level)


# -------------------------
# Recommendations
# -------------------------
def get_recommendation(row):

    if row["risk_level"] == "CRITICAL":
        return "Immediate grid intervention required"

    elif row["risk_level"] == "HIGH":
        return "Activate reserve capacity and monitor grid"

    elif row["risk_level"] == "WATCH":
        return "Increase monitoring and prepare backup"

    else:
        return "Grid operating normally"


df["recommendation"] = df.apply(get_recommendation, axis=1)


# -------------------------
# Save results
# -------------------------
output_file = "data/processed/risk_results.csv"

df.to_csv(output_file, index=False)


# -------------------------
# Results
# -------------------------
print("=" * 50)
print("VAJRA RISK INTELLIGENCE ENGINE")
print("=" * 50)

print("\nTotal observations:", len(df))

print("\nRisk Distribution:")
print(df["risk_level"].value_counts())

print("\nAverage Risk Score:")
print(round(df["risk_score"].mean(), 2))

print("\nMaximum Risk Score:")
print(round(df["risk_score"].max(), 2))

print("\nHighest Risk Events:")

print(
    df[
        [
            "timestamp",
            "load_mw",
            "solar_mw",
            "wind_mw",
            "risk_score",
            "risk_level",
            "recommendation",
        ]
    ]
    .sort_values("risk_score", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nResults saved:")
print(output_file)