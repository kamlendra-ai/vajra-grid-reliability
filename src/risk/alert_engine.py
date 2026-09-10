import pandas as pd


# -------------------------
# Load Vajra results
# -------------------------
df = pd.read_csv("data/processed/supply_gap_results.csv")


# -------------------------
# Alert Engine
# -------------------------
def generate_alert(row):

    risk = row["risk_score"]
    gap = row["supply_gap_mw"]

    if risk >= 80 or gap >= 150:
        return (
            "CRITICAL ALERT: Severe grid stress predicted. "
            "Activate reserve capacity and reduce non-critical load."
        )

    elif risk >= 60 or gap >= 100:
        return (
            "HIGH ALERT: Grid stress detected. "
            "Prepare backup capacity and optimize renewable usage."
        )

    elif risk >= 31 or gap >= 50:
        return (
            "WATCH ALERT: Supply-demand imbalance developing. "
            "Increase grid monitoring."
        )

    else:
        return "NORMAL: Grid conditions stable."


# -------------------------
# Generate alerts
# -------------------------
df["alert"] = df.apply(generate_alert, axis=1)


# -------------------------
# Alert Level
# -------------------------
def get_alert_level(row):

    if row["risk_score"] >= 80 or row["supply_gap_mw"] >= 150:
        return "CRITICAL"

    elif row["risk_score"] >= 60 or row["supply_gap_mw"] >= 100:
        return "HIGH"

    elif row["risk_score"] >= 31 or row["supply_gap_mw"] >= 50:
        return "WATCH"

    else:
        return "NORMAL"


df["alert_level"] = df.apply(get_alert_level, axis=1)


# -------------------------
# Save final intelligence
# -------------------------
output_file = "data/processed/vajra_intelligence.csv"

df.to_csv(output_file, index=False)


# -------------------------
# Results
# -------------------------
print("=" * 50)
print("VAJRA ALERT & RECOMMENDATION ENGINE")
print("=" * 50)

print("\nTotal observations:", len(df))

print("\nAlert Distribution:")
print(df["alert_level"].value_counts())

print("\nCritical Alerts:")

critical = df[df["alert_level"] == "CRITICAL"]

print(
    critical[
        [
            "timestamp",
            "load_mw",
            "renewable_supply_mw",
            "supply_gap_mw",
            "risk_score",
            "alert",
        ]
    ]
    .sort_values("risk_score", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nFinal intelligence saved:")
print(output_file)