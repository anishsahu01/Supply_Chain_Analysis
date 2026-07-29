"""
train_model.py
---------------
Trains a RandomForestRegressor to predict 'Revenue generated' from the
supply chain dataset, then persists the fitted model, the OneHotEncoder,
and the StandardScaler to the /model directory as .pkl files.

Run directly:
    python src/train_model.py
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Allow running this file directly (python src/train_model.py) as well as
# importing it as part of the `src` package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_preprocessing import (
    load_dataset,
    build_feature_target,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "revenue_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoder.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")


def train():
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("Loading dataset...")
    df = load_dataset()
    X, y = build_feature_target(df)

    print(f"Feature matrix shape: {X.shape}")

    # ------------------------------------------------------------------
    # Encode categorical features
    # ------------------------------------------------------------------
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_cat = encoder.fit_transform(X[CATEGORICAL_FEATURES])
    cat_feature_names = encoder.get_feature_names_out(CATEGORICAL_FEATURES)

    # ------------------------------------------------------------------
    # Scale numerical features
    # ------------------------------------------------------------------
    scaler = StandardScaler()
    X_num = scaler.fit_transform(X[NUMERICAL_FEATURES])

    # ------------------------------------------------------------------
    # Combine into final feature matrix
    # ------------------------------------------------------------------
    X_final = np.hstack([X_num, X_cat])
    feature_names = NUMERICAL_FEATURES + list(cat_feature_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y, test_size=0.2, random_state=42
    )

    # ------------------------------------------------------------------
    # Train RandomForestRegressor
    # ------------------------------------------------------------------
    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # ------------------------------------------------------------------
    # Evaluate
    # ------------------------------------------------------------------
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("\n--- Model Evaluation ---")
    print(f"R2 Score : {r2:.4f}")
    print(f"MAE      : {mae:.4f}")
    print(f"RMSE     : {rmse:.4f}")

    # ------------------------------------------------------------------
    # Persist artifacts
    # ------------------------------------------------------------------
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print(f"\nSaved model   -> {MODEL_PATH}")
    print(f"Saved encoder -> {ENCODER_PATH}")
    print(f"Saved scaler  -> {SCALER_PATH}")

    # Save a small text report
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    with open(os.path.join(reports_dir, "training_report.txt"), "w") as f:
        f.write("Revenue Prediction Model - Training Report\n")
        f.write("=" * 45 + "\n")
        f.write(f"Rows used for training : {len(df)}\n")
        f.write(f"Train/Test split       : 80/20\n")
        f.write(f"R2 Score                : {r2:.4f}\n")
        f.write(f"MAE                     : {mae:.4f}\n")
        f.write(f"RMSE                    : {rmse:.4f}\n")
        f.write(f"Feature count (encoded) : {X_final.shape[1]}\n")

    return model, encoder, scaler


if __name__ == "__main__":
    train()
