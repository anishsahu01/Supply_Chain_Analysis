/* =====================================================================
   dashboard.js
   Handles: KPI count-up animation, filter change -> /filter fetch,
   chart rendering via Plotly, and /predict button behaviour.
   ===================================================================== */

const PLOTLY_CONFIG = { responsive: true, displayModeBar: false };

const CHART_TARGETS = {
  revenue_by_product: "chart_revenue_by_product",
  sales_trend: "chart_sales_trend",
  supplier_performance: "chart_supplier_performance",
  inventory_levels: "chart_inventory_levels",
  defect_rate: "chart_defect_rate",
  shipping_cost: "chart_shipping_cost",
};

const overlay = document.getElementById("loadingOverlay");

function showLoading() { overlay.classList.add("active"); }
function hideLoading() { overlay.classList.remove("active"); }

/* -----------------------------------------------------------------
   KPI count-up animation
----------------------------------------------------------------- */
function animateValue(el, start, end, formatFn, duration = 900) {
  const startTime = performance.now();
  function step(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = start + (end - start) * eased;
    el.textContent = formatFn(current);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = formatFn(end);
  }
  requestAnimationFrame(step);
}

function fmtCurrency(v) {
  return "₹" + Math.round(v).toLocaleString("en-IN");
}

function fmtInt(v) {
  return Math.round(v).toLocaleString("en-US");
}
function fmtPercent(v) {
  return v.toFixed(2) + "%";
}

function updateKPIs(kpis) {
  const map = [
    ["kpi_total_revenue", kpis.total_revenue, fmtCurrency],
    ["kpi_total_sales", kpis.total_sales, fmtInt],
    ["kpi_defect_rate", kpis.avg_defect_rate, fmtPercent],
    ["kpi_total_products", kpis.total_products, fmtInt],
    ["kpi_shipping_cost", kpis.avg_shipping_cost, fmtCurrency],
  ];
  map.forEach(([id, value, fmt]) => {
    const el = document.getElementById(id);
    const prevRaw = parseFloat(el.dataset.rawValue || "0");
    animateValue(el, prevRaw, value, fmt);
    el.dataset.rawValue = value;
  });
}

/* -----------------------------------------------------------------
   Chart rendering
----------------------------------------------------------------- */
function renderCharts(chartData) {
  Object.entries(CHART_TARGETS).forEach(([key, elId]) => {
    const spec = chartData[key];
    const el = document.getElementById(elId);
    if (!spec || !el) return;
    Plotly.react(el, spec.data, spec.layout, PLOTLY_CONFIG);
  });
}

/* -----------------------------------------------------------------
   Gather current filter selections
----------------------------------------------------------------- */
function getCurrentFilters() {
  return {
    product_type: document.getElementById("f_product_type").value,
    supplier_name: document.getElementById("f_supplier_name").value,
    location: document.getElementById("f_location").value,
    shipping_carrier: document.getElementById("f_shipping_carrier").value,
    transportation_mode: document.getElementById("f_transportation_mode").value,
  };
}

/* -----------------------------------------------------------------
   /filter call — updates KPIs + charts
----------------------------------------------------------------- */
async function refreshDashboard() {
  showLoading();
  try {
    const res = await fetch("/filter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getCurrentFilters()),
    });
    const data = await res.json();
    updateKPIs(data.kpis);
    renderCharts(data.charts);
    document.getElementById("rowCountBadge").textContent = `${data.row_count} Records Matched`;
  } catch (err) {
    console.error("Failed to refresh dashboard:", err);
  } finally {
    hideLoading();
  }
}

/* -----------------------------------------------------------------
   /predict call
----------------------------------------------------------------- */
async function runPrediction() {
  const btn = document.getElementById("predictBtn");
  const valueEl = document.getElementById("predictionValue");
  const subEl = document.getElementById("predictionSub");
  const card = document.getElementById("predictionCard");

  btn.disabled = true;
  subEl.textContent = "Predicting...";

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getCurrentFilters()),
    });
    const data = await res.json();

    if (data.success) {
      valueEl.textContent = fmtCurrency(data.predicted_revenue);
      subEl.textContent = "Based on current filter selection";
    } else {
      valueEl.textContent = "Error";
      subEl.textContent = data.error || "Could not generate prediction";
    }
    card.classList.remove("updated");
    void card.offsetWidth; // restart animation
    card.classList.add("updated");
  } catch (err) {
    valueEl.textContent = "Error";
    subEl.textContent = "Request failed";
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

/* -----------------------------------------------------------------
   Init
----------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  // Render server-provided initial charts
  renderCharts(INITIAL_CHARTS);

  // Animate KPI cards on first load (from 0 -> server value)
  const initialKPIs = {
    total_revenue: parseFloat(document.getElementById("kpi_total_revenue").dataset.value),
    total_sales: parseFloat(document.getElementById("kpi_total_sales").dataset.value),
    avg_defect_rate: parseFloat(document.getElementById("kpi_defect_rate").dataset.value),
    total_products: parseFloat(document.getElementById("kpi_total_products").dataset.value),
    avg_shipping_cost: parseFloat(document.getElementById("kpi_shipping_cost").dataset.value),
  };
  updateKPIs(initialKPIs);

  // Wire up filter change listeners
  ["f_product_type", "f_supplier_name", "f_location", "f_shipping_carrier", "f_transportation_mode"]
    .forEach((id) => {
      document.getElementById(id).addEventListener("change", refreshDashboard);
    });

  document.getElementById("resetFiltersBtn").addEventListener("click", () => {
    ["f_product_type", "f_supplier_name", "f_location", "f_shipping_carrier", "f_transportation_mode"]
      .forEach((id) => { document.getElementById(id).value = "All"; });
    refreshDashboard();
  });

  document.getElementById("predictBtn").addEventListener("click", runPrediction);
});
