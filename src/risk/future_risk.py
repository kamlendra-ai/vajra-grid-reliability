import os
import pandas as pd
import numpy as np


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

INTELLIGENCE_FILE = os.path.join(
    BASE_DIR, "data", "processed", "vajra_intelligence.csv"
)

FORECAST_FILE = os.path.join(
    BASE_DIR, "data", "processed", "load_forecast_24h.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "data", "processed", "future_risk_24h.csv"
)


def risk_level(score):
    if score <= 30:
        return "SAFE"
    elif score <= 60:
        return "WATCH"
    elif score <= 80:
        return "HIGH"
    return "CRITICAL"


def recommendation(level):
    if level == "CRITICAL":
        return "Immediate operator attention and reserve support recommended."
    elif level == "HIGH":
        return "Prepare reserve and monitor renewable availability closely."
    elif level == "WATCH":
        return "Monitor demand and renewable generation."
    return "Normal monitoring."


def main():

    print("\n⚡ Vajra Future 24-Hour Risk Prediction")
    print("-" * 50)

    if not os.path.exists(INTELLIGENCE_FILE):
        print("❌ vajra_intelligence.csv not found.")
        return

    if not os.path.exists(FORECAST_FILE):
        print("❌ load_forecast_24h.csv not found.")
        return

    df = pd.read_csv(INTELLIGENCE_FILE)
    forecast = pd.read_csv(FORECAST_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    forecast["timestamp"] = pd.to_datetime(forecast["timestamp"])

    # Last 24 forecast hours
    future = forecast.tail(24).copy()

    # Detect forecast load column
    possible_load_columns = [
        "predicted_load_mw",
        "forecast_load_mw",
        "predicted_load",
        "forecast"
    ]

    load_column = None

    for col in possible_load_columns:
        if col in future.columns:
            load_column = col
            break

    if load_column is None:
        numeric_columns = future.select_dtypes(
            include=np.number
        ).columns.tolist()

        if not numeric_columns:
            print("❌ Could not find load forecast column.")
            return

        load_column = numeric_columns[0]

    future["forecast_load_mw"] = future[load_column]

    # Historical hour-wise renewable averages
    df["hour"] = df["timestamp"].dt.hour

    solar_hourly = df.groupby("hour")["solar_mw"].mean()
    wind_hourly = df.groupby("hour")["wind_mw"].mean()

    future["hour"] = future["timestamp"].dt.hour

    future["forecast_solar_mw"] = future["hour"].map(
        solar_hourly
    )

    future["forecast_wind_mw"] = future["hour"].map(
        wind_hourly
    )

    future["forecast_renewable_mw"] = (
        future["forecast_solar_mw"]
        + future["forecast_wind_mw"]
    )

    future["supply_gap_mw"] = (
        future["forecast_load_mw"]
        - future["forecast_renewable_mw"]
    )

    future["gap_load_ratio"] = (
        future["supply_gap_mw"]
        / future["forecast_load_mw"].replace(0, np.nan)
    )

    future["gap_load_ratio"] = (
        future["gap_load_ratio"].fillna(0).clip(lower=0)
    )

    # Demand stress
    historical_mean_load = df["load_mw"].mean()

    future["demand_stress"] = (
        future["forecast_load_mw"]
        / historical_mean_load
        * 100
    ).clip(0, 100)

    # Renewable shortfall
    renewable_target = (
        df["solar_mw"] + df["wind_mw"]
    ).mean()

    future["renewable_shortfall"] = (
        1
        - future["forecast_renewable_mw"]
        / renewable_target
    ).clip(0, 1) * 100

    # Gap pressure
    future["gap_pressure"] = (
        future["gap_load_ratio"] * 100
    ).clip(0, 100)

    # Final risk score
    future["risk_score"] = (
        future["demand_stress"] * 0.35
        + future["renewable_shortfall"] * 0.40
        + future["gap_pressure"] * 0.25
    ).clip(0, 100)

    future["risk_level"] = future["risk_score"].apply(
        risk_level
    )

    future["recommended_action"] = future["risk_level"].apply(
        recommendation
    )

    # Keep useful columns
    output_columns = [
        "timestamp",
        "forecast_load_mw",
        "forecast_solar_mw",
        "forecast_wind_mw",
        "forecast_renewable_mw",
        "supply_gap_mw",
        "risk_score",
        "risk_level",
        "recommended_action"
    ]

    future[output_columns].to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n✅ Future risk prediction completed!")
    print(f"📁 Saved to: {OUTPUT_FILE}")

    print("\nRisk Summary:")
    print(
        future["risk_level"]
        .value_counts()
        .to_string()
    )

    critical = future[
        future["risk_level"] == "CRITICAL"
    ]

    high = future[
        future["risk_level"] == "HIGH"
    ]

    if not critical.empty:
        print(
            "\n🚨 First CRITICAL hour:",
            critical.iloc[0]["timestamp"]
        )
    elif not high.empty:
        print(
            "\n⚠️ First HIGH-risk hour:",
            high.iloc[0]["timestamp"]
        )
    else:
        print("\n✅ No HIGH/CRITICAL risk predicted.")

    print("\nDone.")


if __name__ == "__main__":
    main()