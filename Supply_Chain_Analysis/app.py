"""
app.py
------
Main Flask application for the Supply Chain Analytics & Revenue
Prediction Dashboard.

Routes:
    GET  /            -> renders dashboard.html (main UI shell)
    POST /filter       -> returns updated KPIs + charts (JSON) for selected filters
    POST /predict      -> returns predicted revenue (JSON) for selected filters

Run:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import os
from flask import Flask, render_template, request, jsonify

from src.data_preprocessing import (
    load_dataset,
    get_filter_options,
    filter_dataframe,
    compute_kpis,
    FILTER_COLUMNS,
)
from src.visualization import build_all_charts
from src.prediction import predict_revenue

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load dataset once at startup (cached in memory - no SQL database used)
# ---------------------------------------------------------------------------
DATASET = load_dataset()
FILTER_OPTIONS = get_filter_options(DATASET)

# Map dropdown filter keys (as sent from the frontend) to dataframe columns
FILTER_KEY_TO_COLUMN = {
    "product_type": "Product type",
    "supplier_name": "Supplier name",
    "location": "Location",
    "shipping_carrier": "Shipping carriers",
    "transportation_mode": "Transportation modes",
}


def _extract_filters(payload: dict) -> dict:
    """Translate incoming JSON payload keys into dataframe column filters."""
    filters = {}
    for key, column in FILTER_KEY_TO_COLUMN.items():
        filters[column] = payload.get(key, "All")
    return filters


@app.route("/")
def dashboard():
    """Render the main dashboard shell with dropdown options + initial data."""
    kpis = compute_kpis(DATASET)
    charts = build_all_charts(DATASET)

    return render_template(
        "dashboard.html",
        filter_options=FILTER_OPTIONS,
        kpis=kpis,
        charts=charts,
    )


@app.route("/filter", methods=["POST"])
def filter_data():
    """
    Accepts JSON dropdown selections, returns updated KPIs + chart JSON
    for the filtered subset of data.
    """
    payload = request.get_json(force=True) or {}
    column_filters = _extract_filters(payload)

    filtered_df = filter_dataframe(DATASET, column_filters)

    kpis = compute_kpis(filtered_df)
    charts = build_all_charts(filtered_df) if not filtered_df.empty else build_all_charts(DATASET)

    return jsonify({
        "kpis": kpis,
        "charts": charts,
        "row_count": int(len(filtered_df)),
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts JSON dropdown selections, returns predicted revenue using the
    trained RandomForestRegressor model + encoder + scaler.
    """
    payload = request.get_json(force=True) or {}

    filters = {
        "product_type": payload.get("product_type", "All"),
        "supplier_name": payload.get("supplier_name", "All"),
        "location": payload.get("location", "All"),
        "shipping_carrier": payload.get("shipping_carrier", "All"),
        "transportation_mode": payload.get("transportation_mode", "All"),
    }

    try:
        result = predict_revenue(filters)
        return jsonify({"success": True, **result})
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "Model artifacts not found. Please run: python src/train_model.py"
        }), 500
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
