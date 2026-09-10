import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# -------------------------
# Load processed dataset
# -------------------------
df = pd.read_csv("data/processed/grid_features.csv")

# -------------------------
# Features for forecasting
# -------------------------
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

target = "load_mw"

X = df[features]
y = df[target]

# -------------------------
# Time-based train/test split
# -------------------------
split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("=" * 50)
print("VAJRA LOAD FORECASTING MODEL")
print("=" * 50)

print("\nTraining samples:", len(X_train))
print("Testing samples :", len(X_test))

# -------------------------
# XGBoost Model
# -------------------------
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42
)

# Train
model.fit(X_train, y_train)

# -------------------------
# Predictions
# -------------------------
predictions = model.predict(X_test)

# -------------------------
# Evaluation
# -------------------------
mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\nMODEL PERFORMANCE")
print("-" * 30)
print(f"MAE  : {mae:.2f} MW")
print(f"RMSE : {rmse:.2f} MW")
print(f"R²   : {r2:.4f}")

# -------------------------
# Save model
# -------------------------
model_path = "models/load_forecasting_model.pkl"

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print(model_path)