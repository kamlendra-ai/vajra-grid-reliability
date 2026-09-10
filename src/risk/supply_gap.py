import pandas as pd


# -------------------------
# Load risk results
# -------------------------
df = pd.read_csv("data/processed/risk_results.csv")


# -------------------------
# Calculate renewable supply
# -------------------------
df["renewable_supply_mw"] = (
    df["solar_mw"] + df["wind_mw"]
)


# -------------------------
# Supply-Demand Gap
# -------------------------
df["supply_gap_mw"] = (
    df["load_mw"] - df["renewable_supply_mw"]
)


# -------------------------
# Reserve capacity needed
# -------------------------
df["reserve_capacity_mw"] = (
    df["supply_gap_mw"] * 0.20
).clip(lower=0)


# -------------------------
# Gap Status
# -------------------------
def get_gap_status(gap):

    if gap <= 50:
        return "LOW"

    elif gap <= 100:
        return "MODERATE"

    elif gap <= 150:
        return "HIGH"

    else:
        return "CRITICAL"


df["gap_status"] = df["supply_gap_mw"].apply(
    get_gap_status
)


# -------------------------
# Recommendation
# -------------------------
def get_recommendation(row):

    if row["gap_status"] == "CRITICAL":
        return "Activate reserve generation and reduce non-critical load"

    elif row["gap_status"] == "HIGH":
        return "Prepare backup capacity and optimize renewable usage"

    elif row["gap_status"] == "MODERATE":
        return "Monitor supply-demand balance closely"

    else:
        return "Supply-demand balance is stable"


df["gap_recommendation"] = df.apply(
    get_recommendation,
    axis=1
)


# -------------------------
# Save results
# -------------------------
output_file = "data/processed/supply_gap_results.csv"

df.to_csv(output_file, index=False)


# -------------------------
# Results
# -------------------------
print("=" * 50)
print("VAJRA SUPPLY-DEMAND GAP ENGINE")
print("=" * 50)

print("\nTotal observations:", len(df))

print("\nAverage Load:")
print(round(df["load_mw"].mean(), 2), "MW")

print("\nAverage Renewable Supply:")
print(round(df["renewable_supply_mw"].mean(), 2), "MW")

print("\nAverage Supply Gap:")
print(round(df["supply_gap_mw"].mean(), 2), "MW")

print("\nMaximum Supply Gap:")
print(round(df["supply_gap_mw"].max(), 2), "MW")

print("\nGap Distribution:")
print(df["gap_status"].value_counts())

print("\nHighest Supply Gap Events:")

print(
    df[
        [
            "timestamp",
            "load_mw",
            "solar_mw",
            "wind_mw",
            "renewable_supply_mw",
            "supply_gap_mw",
            "gap_status",
            "reserve_capacity_mw",
        ]
    ]
    .sort_values("supply_gap_mw", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nResults saved:")
print(output_file)