"""
prediction.py
--------------
Loads the persisted model/encoder/scaler artifacts and exposes a single
`predict_revenue()` function that the Flask app calls whenever the user
changes a dashboard filter.

Design note:
The dashboard does NOT collect manual numeric input from the user. Instead,
when the user picks Product Type / Supplier / Location / Carrier /
Transportation Mode from dropdowns, we look up the matching rows in the
historical dataset and use their AVERAGE numeric attributes (price,
stock levels, lead times, etc.) as the numeric features for that
combination. This lets the model produce a realistic revenue prediction
purely from dropdown selections.
"""

import os
import numpy as np
import pandas as pd
import joblib

from src.data_preprocessing import (
    load_dataset,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "revenue_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoder.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

_model = None
_encoder = None
_scaler = None
_dataset = None


def _load_artifacts():
    """Lazy-load model artifacts and the dataset (cached in module globals)."""
    global _model, _encoder, _scaler, _dataset

    if _model is None:
        _model = joblib.load(MODEL_PATH)
    if _encoder is None:
        _encoder = joblib.load(ENCODER_PATH)
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)
    if _dataset is None:
        _dataset = load_dataset()

    return _model, _encoder, _scaler, _dataset


def _resolve_row(filters: dict, df: pd.DataFrame) -> pd.Series:
    """
    Given the user's dropdown selections, find matching historical rows
    and derive a representative feature row (mean of numeric columns,
    mode/selection of categorical columns).
    """
    subset = df.copy()

    mapping = {
        "Product type": filters.get("product_type"),
        "Supplier name": filters.get("supplier_name"),
        "Location": filters.get("location"),
        "Shipping carriers": filters.get("shipping_carrier"),
        "Transportation modes": filters.get("transportation_mode"),
    }

    for col, val in mapping.items():
        if val and val not in ("All", "all", ""):
            candidate = subset[subset[col] == val]
            # Only narrow down if it doesn't eliminate everything;
            # otherwise fall back to the broader subset so we always
            # have data to compute averages from.
            if not candidate.empty:
                subset = candidate

    if subset.empty:
        subset = df  # ultimate fallback: whole dataset

    row = {}
    for col in NUMERICAL_FEATURES:
        row[col] = subset[col].mean()

    for col in CATEGORICAL_FEATURES:
        selected = mapping.get(col)
        if selected and selected not in ("All", "all", ""):
            row[col] = selected
        else:
            row[col] = subset[col].mode().iloc[0]

    return pd.Series(row)


def predict_revenue(filters: dict) -> dict:
    """
    Predict revenue given a dict of dropdown filter selections:
        {
            "product_type": "Skincare",
            "supplier_name": "Supplier 3",
            "location": "Mumbai",
            "shipping_carrier": "Carrier A",
            "transportation_mode": "Road",
        }

    Returns a dict with the predicted revenue and the feature values used.
    """
    model, encoder, scaler, df = _load_artifacts()

    feature_row = _resolve_row(filters, df)

    # Build single-row DataFrames matching training-time column order
    cat_df = pd.DataFrame([feature_row[CATEGORICAL_FEATURES]])
    num_df = pd.DataFrame([feature_row[NUMERICAL_FEATURES]]).astype(float)

    X_cat = encoder.transform(cat_df)
    X_num = scaler.transform(num_df)

    X_final = np.hstack([X_num, X_cat])

    prediction = model.predict(X_final)[0]

    return {
        "predicted_revenue": round(float(prediction), 2),
        "used_features": {
            **{k: round(float(v), 2) for k, v in feature_row[NUMERICAL_FEATURES].items()},
            **{k: feature_row[k] for k in CATEGORICAL_FEATURES},
        },
    }


if __name__ == "__main__":
    sample_filters = {
        "product_type": "skincare",
        "supplier_name": "Supplier 3",
        "location": "Mumbai",
        "shipping_carrier": "Carrier A",
        "transportation_mode": "Road",
    }
    result = predict_revenue(sample_filters)
    print("Prediction result:", result)
