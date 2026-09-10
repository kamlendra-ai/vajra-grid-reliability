import pandas as pd


def create_features(df):
    df = df.copy()

    # Timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Time-based features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Load lag features
    df["load_lag_1"] = df["load_mw"].shift(1)
    df["load_lag_24"] = df["load_mw"].shift(24)
    df["load_lag_168"] = df["load_mw"].shift(168)

    # Rolling load features
    df["load_rolling_24"] = (
        df["load_mw"]
        .shift(1)
        .rolling(window=24)
        .mean()
    )

    df["load_rolling_168"] = (
        df["load_mw"]
        .shift(1)
        .rolling(window=168)
        .mean()
    )

    # Renewable features
    df["solar_lag_1"] = df["solar_mw"].shift(1)
    df["wind_lag_1"] = df["wind_mw"].shift(1)

    # Remove rows created by lag/rolling operations
    df = df.dropna().reset_index(drop=True)

    return df


if __name__ == "__main__":

    # Load raw dataset
    input_file = "data/raw/grid_data.csv"
    output_file = "data/processed/grid_features.csv"

    df = pd.read_csv(input_file)

    # Create features
    df = create_features(df)

    # Save processed dataset
    df.to_csv(output_file, index=False)

    print("=" * 50)
    print("VAJRA FEATURE ENGINEERING")
    print("=" * 50)

    print("\nOriginal rows: 8760")
    print("Processed rows:", len(df))

    print("\nNew features:")
    print([
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
        "wind_lag_1"
    ])

    print("\nProcessed dataset saved to:")
    print(output_file)