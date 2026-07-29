"""
visualization.py
-----------------
Builds Plotly figures (dark themed) for the dashboard, returned as JSON
so they can be rendered client-side with Plotly.js inside dashboard.html.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils
import json

# ---------------------------------------------------------------------------
# Shared dark theme
# ---------------------------------------------------------------------------
DARK_BG = "rgba(0,0,0,0)"
FONT_COLOR = "#e5e7eb"
GRID_COLOR = "rgba(255,255,255,0.08)"
ACCENT_COLORS = ["#7c3aed", "#06b6d4", "#f43f5e", "#22c55e", "#f59e0b", "#3b82f6", "#ec4899"]


def _apply_dark_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#f8fafc", family="Poppins, sans-serif")),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=FONT_COLOR, family="Poppins, sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        hoverlabel=dict(bgcolor="#1e1b3a", font_color="#f8fafc"),
    )
    return fig


def to_json(fig):
    return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


def revenue_by_product_type(df: pd.DataFrame):
    grouped = df.groupby("Product type", as_index=False)["Revenue generated"].sum()
    fig = px.bar(
        grouped, x="Product type", y="Revenue generated",
        color="Product type", color_discrete_sequence=ACCENT_COLORS,
        text_auto=".2s",
    )
    fig.update_traces(marker_line_width=0, textfont_color="#f8fafc")
    _apply_dark_layout(fig, "Revenue by Product Type")
    return to_json(fig)


def sales_trend(df: pd.DataFrame):
    # No explicit date column exists; use SKU order as a pseudo-timeline
    ordered = df.reset_index(drop=True).copy()
    ordered["Index"] = range(1, len(ordered) + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ordered["Index"], y=ordered["Number of products sold"],
        mode="lines+markers", name="Units Sold",
        line=dict(color="#06b6d4", width=3),
        marker=dict(size=6, color="#7c3aed"),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.15)",
    ))
    _apply_dark_layout(fig, "Sales Trend (Units Sold Across Records)")
    fig.update_xaxes(title="Record Sequence")
    fig.update_yaxes(title="Units Sold")
    return to_json(fig)


def supplier_performance(df: pd.DataFrame):
    grouped = df.groupby("Supplier name", as_index=False).agg(
        Revenue=("Revenue generated", "sum"),
        AvgDefectRate=("Defect rates", "mean"),
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["Supplier name"], y=grouped["Revenue"],
        name="Revenue", marker_color="#7c3aed", yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=grouped["Supplier name"], y=grouped["AvgDefectRate"],
        name="Avg Defect Rate (%)", mode="lines+markers",
        marker=dict(color="#f43f5e", size=8),
        line=dict(color="#f43f5e", width=2, dash="dot"),
        yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="Revenue", gridcolor=GRID_COLOR),
        yaxis2=dict(title="Avg Defect Rate (%)", overlaying="y", side="right", showgrid=False),
    )
    _apply_dark_layout(fig, "Supplier Performance: Revenue vs Defect Rate")
    return to_json(fig)


def inventory_level_chart(df: pd.DataFrame):
    grouped = df.groupby("Product type", as_index=False)["Stock levels"].mean()
    fig = px.bar(
        grouped, x="Product type", y="Stock levels",
        color="Product type", color_discrete_sequence=ACCENT_COLORS,
    )
    _apply_dark_layout(fig, "Average Inventory (Stock) Levels")
    return to_json(fig)


def defect_rate_analysis(df: pd.DataFrame):
    grouped = df.groupby("Product type", as_index=False)["Defect rates"].mean()
    fig = go.Figure(go.Scatterpolar(
        r=grouped["Defect rates"],
        theta=grouped["Product type"],
        fill="toself",
        line=dict(color="#f59e0b"),
        fillcolor="rgba(245,158,11,0.25)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=DARK_BG,
            radialaxis=dict(gridcolor=GRID_COLOR, color=FONT_COLOR),
            angularaxis=dict(gridcolor=GRID_COLOR, color=FONT_COLOR),
        )
    )
    _apply_dark_layout(fig, "Defect Rate Analysis by Product Type")
    return to_json(fig)


def shipping_cost_analysis(df: pd.DataFrame):
    grouped = df.groupby("Shipping carriers", as_index=False)["Shipping costs"].mean()
    fig = px.pie(
        grouped, names="Shipping carriers", values="Shipping costs",
        color_discrete_sequence=ACCENT_COLORS, hole=0.55,
    )
    fig.update_traces(textfont_color="#f8fafc", marker=dict(line=dict(color="#0f0c29", width=2)))
    _apply_dark_layout(fig, "Avg Shipping Cost by Carrier")
    return to_json(fig)


def build_all_charts(df: pd.DataFrame) -> dict:
    """Convenience wrapper: build every chart and return as a dict of JSON specs."""
    if df.empty:
        return {}
    return {
        "revenue_by_product": revenue_by_product_type(df),
        "sales_trend": sales_trend(df),
        "supplier_performance": supplier_performance(df),
        "inventory_levels": inventory_level_chart(df),
        "defect_rate": defect_rate_analysis(df),
        "shipping_cost": shipping_cost_analysis(df),
    }
