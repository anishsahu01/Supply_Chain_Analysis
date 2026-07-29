"""
data_preprocessing.py
----------------------
Handles loading of the raw supply chain dataset and preparation of
feature/target matrices used for model training and prediction.

This module is intentionally kept dependency-light (pandas / numpy only)
so it can be imported both by the training script (src/train_model.py)
and by the Flask app at request time.
"""

import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "supply_chain_data.csv")

# ---------------------------------------------------------------------------
# Column configuration
# ---------------------------------------------------------------------------
# Categorical columns used as model features (will be one-hot encoded)
CATEGORICAL_FEATURES = [
    "Product type",
    "Supplier name",
    "Location",
    "Transportation modes",
]

# Numerical columns used as model features
NUMERICAL_FEATURES = [
    "Price",
    "Availability",
    "Number of products sold",
    "Stock levels",
    "Lead times",
    "Order quantities",
    "Shipping times",
    "Shipping costs",
    "Production volumes",
    "Manufacturing costs",
]

TARGET_COLUMN = "Revenue generated"

# Columns exposed as dropdown filters in the dashboard UI
FILTER_COLUMNS = [
    "Product type",
    "Supplier name",
    "Location",
    "Shipping carriers",
    "Transportation modes",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES


def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load the raw CSV dataset into a DataFrame, with light cleaning."""
    df = pd.read_csv(path)

    # Strip whitespace from string columns for safe matching in filters
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    return df


def get_filter_options(df: pd.DataFrame) -> dict:
    """Return unique sorted values for each dropdown filter column."""
    options = {}
    for col in FILTER_COLUMNS:
        options[col] = sorted(df[col].dropna().unique().tolist())
    return options


def filter_dataframe(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply a dict of {column: value} filters to the dataframe.
    Empty / 'All' values are ignored (no filtering applied for that column).
    """
    filtered = df.copy()
    for col, value in filters.items():
        if value and value not in ("All", "all", ""):
            filtered = filtered[filtered[col] == value]
    return filtered


def build_feature_target(df: pd.DataFrame):
    """
    Split the dataframe into the feature matrix X and target vector y
    used for model training.
    """
    X = df[ALL_FEATURES].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPI metrics shown on the dashboard cards."""
    if df.empty:
        return {
            "total_revenue": 0,
            "total_sales": 0,
            "avg_defect_rate": 0,
            "total_products": 0,
            "avg_shipping_cost": 0,
        }

    return {
        "total_revenue": round(float(df["Revenue generated"].sum()), 2),
        "total_sales": int(df["Number of products sold"].sum()),
        "avg_defect_rate": round(float(df["Defect rates"].mean()), 2),
        "total_products": int(df["SKU"].nunique()),
        "avg_shipping_cost": round(float(df["Shipping costs"].mean()), 2),
    }


if __name__ == "__main__":
    data = load_dataset()
    print("Dataset shape:", data.shape)
    print("Filter options:", get_filter_options(data))
    print("KPIs (full dataset):", compute_kpis(data))
