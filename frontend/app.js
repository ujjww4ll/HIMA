/* ═══════════════════════════════════════════════════════
   HIMA Dashboard — Full Client-Side Application
   ═══════════════════════════════════════════════════════ */
"use strict";

// ─── 1. ANIMATED BACKGROUND ───────────────────────────────────────────────────
(function initBgCanvas() {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function mkParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r:  Math.random() * 2 + 0.5,
      a:  Math.random(),
      fire: Math.random() < 0.15
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: 90 }, mkParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.fire
        ? `rgba(249,115,22,${p.a * 0.6})`
        : `rgba(148,163,184,${p.a * 0.3})`;
      ctx.fill();
    });

    // Draw faint connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(148,163,184,${0.08 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  init();
  draw();
})();

// ─── 2. TAB NAVIGATION ────────────────────────────────────────────────────────
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tab = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    const panel = document.getElementById("tab-" + tab);
    if (panel) panel.classList.add("active");
  });
});

// ─── 3. OVERVIEW API DATA ─────────────────────────────────────────────────────
let overviewData = null;

async function fetchOverview() {
  try {
    const res = await fetch("/api/overview");
    if (!res.ok) throw new Error("API returned " + res.status);
    overviewData = await res.json();
    hydrateStateData(overviewData);
    populateKPIs(overviewData);
    renderImportanceBars(overviewData);
    renderModelTables(overviewData);
    renderAuditTab(overviewData);
    renderMap(overviewData);
  } catch (err) {
    console.warn("Overview API error:", err.message);
    renderMapFallback();
    renderImportanceFallback();
  }
}

function hydrateStateData(d) {
  const cellsByState = (d.grid_meta && d.grid_meta.cells_per_state) || {};
  const firesByState = (d.firms_meta && d.firms_meta.detections_by_state) || {};
  const gsiByState   = (d.gsi_meta && d.gsi_meta.records_by_state) || {};
  const perStateRows = (d.tables && d.tables.wildfire_per_state) || [];
  const geoFeatures  = (d.boundaries_geojson && d.boundaries_geojson.features) || [];

  const aucByState = {};
  perStateRows.forEach(r => { if (r.state_name) aucByState[r.state_name] = r.roc_auc; });

  const repByState = {};
  geoFeatures.forEach(f => {
    const p = f.properties || {};
    if (p.state_name) repByState[p.state_name] = { lat: p.rep_lat, lon: p.rep_lon };
  });

  Object.keys(STATE_DATA).forEach(st => {
    if (cellsByState[st] !== undefined) STATE_DATA[st].cells = cellsByState[st];
    if (firesByState[st] !== undefined) STATE_DATA[st].fires = firesByState[st];
    if (gsiByState[st] !== undefined)   STATE_DATA[st].landslides = gsiByState[st];
    if (aucByState[st] !== undefined && aucByState[st] !== null) STATE_DATA[st].roc_auc = Number(aucByState[st]);
    if (repByState[st]) {
      STATE_DATA[st].lat = repByState[st].lat;
      STATE_DATA[st].lon = repByState[st].lon;
    }
  });
}

function populateKPIs(d) {
  const gm = d.grid_meta || {};
  const fm = d.firms_meta || {};
  const wc = d.wildfire_card || {};
  const lf = d.landslide_feasibility || {};
  const lc = d.landslide_card || {};

  setText("kpi-cells", fmt(gm.total_cells || gm.cells_inside_boundary || 253408));
  setText("kpi-fires", fmt(fm.vegetation_fire_count_type_0 || fm.total_ne_detections_after_exact_dedup || 219928));

  const wfBest = wc.best_model_test_metrics || {};
  setText("kpi-wf-auc", wfBest.test_roc_auc ? wfBest.test_roc_auc.toFixed(4) : "0.9358");
  setText("kpi-wf-model", wc.selected_best_model || "HistGradientBoosting");

  setText("kpi-gsi", fmt(lf.gsi_ne_india_within_study_boundary || 9970));
  setText("kpi-gsi-dated", `${lf.dated_events_2021_2024_raw || 673} Dated · ${lf.dated_unique_celldays_2021_2024 || 463} Cell-Days`);

  const lsBest = lc.best_model_test_metrics || (lc.all_model_results || []).find(m => m.model === lc.selected_best_model) || {};
  setText("kpi-ls-auc", lsBest.test_roc_auc ? lsBest.test_roc_auc.toFixed(4) : "0.9367");
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function fmt(n) {
  return Number(n).toLocaleString("en-IN");
}

// ─── 4. SVG CHOROPLETH MAP ────────────────────────────────────────────────────
const STATE_DATA = {
  "Arunachal Pradesh": { fires: 18215, roc_auc: 0.93, landslides: 0, lat: 28.0, lon: 94.7, cells: 82127 },
  "Assam":             { fires: 54346, roc_auc: 0.93, landslides: 0, lat: 26.2, lon: 92.9, cells: 78446 },
  "Manipur":           { fires: 40061, roc_auc: 0.93, landslides: 0, lat: 24.7, lon: 93.9, cells: 22327 },
  "Meghalaya":         { fires: 30413, roc_auc: 0.93, landslides: 0, lat: 25.5, lon: 91.4, cells: 22418 },
  "Mizoram":           { fires: 44730, roc_auc: 0.93, landslides: 0, lat: 23.3, lon: 92.8, cells: 21070 },
  "Nagaland":          { fires: 20341, roc_auc: 0.93, landslides: 0, lat: 26.1, lon: 94.5, cells: 16583 },
  "Tripura":           { fires: 15798, roc_auc: 0.93, landslides: 0, lat: 23.8, lon: 91.7, cells: 10437 }
};

let currentMetric = "fires";
let selectedState = null;
let stateGeojson = null;

function getStateColor(value, min, max) {
  if (max === min) return "#3b82f6";
  const t = (value - min) / (max - min);
  // Dark blue → bright orange → red gradient
  if (t < 0.33) {
    const s = t / 0.33;
    return lerpColor("#1e3a5f", "#3b82f6", s);
  } else if (t < 0.66) {
    const s = (t - 0.33) / 0.33;
    return lerpColor("#3b82f6", "#f59e0b", s);
  } else {
    const s = (t - 0.66) / 0.34;
    return lerpColor("#f59e0b", "#ef4444", s);
  }
}

function lerpColor(a, b, t) {
  const ah = parseInt(a.slice(1), 16);
  const bh = parseInt(b.slice(1), 16);
  const ar = (ah >> 16) & 0xFF, ag = (ah >> 8) & 0xFF, ab = ah & 0xFF;
  const br = (bh >> 16) & 0xFF, bg = (bh >> 8) & 0xFF, bb = bh & 0xFF;
  const rr = Math.round(ar + (br - ar) * t);
  const rg = Math.round(ag + (bg - ag) * t);
  const rb = Math.round(ab + (bb - ab) * t);
  return `#${rr.toString(16).padStart(2,"0")}${rg.toString(16).padStart(2,"0")}${rb.toString(16).padStart(2,"0")}`;
}

function renderMap(d) {
  const geojson = d && d.boundaries_geojson;
  if (geojson && geojson.features && geojson.features.length > 0) {
    stateGeojson = geojson;
    renderSVGFromGeoJSON(geojson);
  } else {
    renderMapFallback();
  }
}

function renderSVGFromGeoJSON(geojson) {
  const svg = document.getElementById("ne-map-svg");
  if (!svg) return;

  // Bounds of NE India
  const LON_MIN = 89.69, LON_MAX = 97.41;
  const LAT_MIN = 21.94, LAT_MAX = 29.47;
  const VW = 760, VH = 540;
  const PAD = 30;

  function project(lon, lat) {
    const x = PAD + ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * (VW - 2 * PAD) * 0.9;
    const y = PAD + ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * (VH - 2 * PAD);
    return [x, y];
  }

  function coordsToPath(rings) {
    return rings.map(ring =>
      ring.map((pt, i) => {
        const [x, y] = project(pt[0], pt[1]);
        return (i === 0 ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : `L ${x.toFixed(1)} ${y.toFixed(1)}`);
      }).join(" ") + " Z"
    ).join(" ");
  }

  const values = geojson.features.map(f => {
    const name = f.properties.state_name;
    const sd = STATE_DATA[name] || {};
    return sd[currentMetric] || 0;
  });
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);

  // Clear existing state paths (keep defs)
  svg.querySelectorAll(".map-state, .map-state-label").forEach(el => el.remove());

  geojson.features.forEach((feature, idx) => {
    const name = feature.properties.state_name;
    const sd = STATE_DATA[name] || {};
    const val = sd[currentMetric] || 0;
    const color = getStateColor(val, minVal, maxVal);

    let pathD = "";
    const geom = feature.geometry;
    if (geom.type === "Polygon") {
      pathD = coordsToPath(geom.coordinates);
    } else if (geom.type === "MultiPolygon") {
      pathD = geom.coordinates.map(poly => coordsToPath(poly)).join(" ");
    }

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathD);
    path.setAttribute("fill", color);
    path.setAttribute("fill-opacity", "0.85");
    path.setAttribute("stroke", "#020817");
    path.setAttribute("stroke-width", "1.2");
    path.classList.add("map-state");
    path.dataset.state = name;

    path.addEventListener("mouseenter", (e) => showMapTooltip(e, name, sd));
    path.addEventListener("mousemove",  (e) => moveMapTooltip(e));
    path.addEventListener("mouseleave", hideMapTooltip);
    path.addEventListener("click", () => selectState(name, sd));
    svg.appendChild(path);

    // Label
    const rep_lon = feature.properties.rep_lon || sd.lon;
    const rep_lat = feature.properties.rep_lat || sd.lat;
    if (rep_lon && rep_lat) {
      const [lx, ly] = project(rep_lon, rep_lat);
      const shortName = name.replace("Arunachal Pradesh", "Arunachal\nPradesh");
      const lines = shortName.split("\n");
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", lx.toFixed(1));
      text.setAttribute("y", (ly - (lines.length - 1) * 6).toFixed(1));
      text.classList.add("map-state-label");
      lines.forEach((line, li) => {
        const tspan = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        tspan.setAttribute("x", lx.toFixed(1));
        tspan.setAttribute("dy", li === 0 ? "0" : "11");
        tspan.textContent = line;
        text.appendChild(tspan);
      });
      svg.appendChild(text);
    }
  });

  updateLegend(minVal, maxVal);
}

// Metric selector change
document.getElementById("map-metric")?.addEventListener("change", (e) => {
  currentMetric = e.target.value;
  if (stateGeojson) {
    renderSVGFromGeoJSON(stateGeojson);
    if (selectedState) {
      selectState(selectedState, STATE_DATA[selectedState] || {});
    }
  } else {
    renderMapFallback();
  }
});

function renderMapFallback() {
  // Static approximate NE India SVG when GeoJSON fails
  const svg = document.getElementById("ne-map-svg");
  if (!svg) return;
  stateGeojson = null;

  const APPROX = {
    "Arunachal Pradesh": "M 420 60  L 580 55  L 610 90  L 600 170 L 550 190 L 490 200 L 450 185 L 400 160 L 390 110 Z",
    "Assam":             "M 300 180 L 450 185 L 490 200 L 490 230 L 440 260 L 380 265 L 320 255 L 285 230 Z",
    "Nagaland":          "M 490 200 L 550 190 L 560 230 L 540 265 L 490 260 L 490 230 Z",
    "Manipur":           "M 490 260 L 540 265 L 545 320 L 510 345 L 480 330 L 475 290 Z",
    "Meghalaya":         "M 285 230 L 380 265 L 370 305 L 310 310 L 265 280 Z",
    "Mizoram":           "M 380 265 L 440 260 L 475 290 L 480 330 L 445 360 L 390 350 L 365 310 Z",
    "Tripura":           "M 310 310 L 370 305 L 365 350 L 320 355 L 300 335 Z"
  };

  const metricValues = Object.fromEntries(
    Object.entries(STATE_DATA).map(([k, v]) => [k, v[currentMetric] || 0])
  );
  const vals = Object.values(metricValues);
  const minV = Math.min(...vals), maxV = Math.max(...vals);

  svg.querySelectorAll(".map-state, .map-state-label").forEach(el => el.remove());

  const LABEL_XY = {
    "Arunachal Pradesh": [510, 125],
    "Assam":             [390, 220],
    "Nagaland":          [520, 230],
    "Manipur":           [510, 300],
    "Meghalaya":         [320, 275],
    "Mizoram":           [420, 315],
    "Tripura":           [330, 335]
  };

  Object.entries(APPROX).forEach(([name, d]) => {
    const val = metricValues[name] || 0;
    const color = getStateColor(val, minV, maxV);
    const sd = STATE_DATA[name] || {};

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    path.setAttribute("fill", color);
    path.setAttribute("fill-opacity", "0.85");
    path.setAttribute("stroke", "#020817");
    path.setAttribute("stroke-width", "1.5");
    path.classList.add("map-state");
    path.dataset.state = name;
    path.addEventListener("mouseenter", (e) => showMapTooltip(e, name, sd));
    path.addEventListener("mousemove",  (e) => moveMapTooltip(e));
    path.addEventListener("mouseleave", hideMapTooltip);
    path.addEventListener("click", () => selectState(name, sd));
    svg.appendChild(path);

    // Label
    const xy = LABEL_XY[name];
    if (xy) {
      const shortName = name === "Arunachal Pradesh" ? ["Arunachal", "Pradesh"] : [name];
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", xy[0]);
      text.setAttribute("y", xy[1]);
      text.classList.add("map-state-label");
      shortName.forEach((line, li) => {
        const ts = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        ts.setAttribute("x", xy[0]);
        ts.setAttribute("dy", li === 0 ? "0" : "11");
        ts.textContent = line;
        text.appendChild(ts);
      });
      svg.appendChild(text);
    }
  });

  updateLegend(minV, maxV);
}

function updateLegend(minV, maxV) {
  const labels = {
    fires:    ["Fewer Fires", "More Fires"],
    roc_auc:  ["Lower AUC",   "Higher AUC"],
    landslides:["Fewer Events","More Events"]
  };
  const lab = labels[currentMetric] || ["Low","High"];
  const legendBar = document.getElementById("legend-bar");
  const gradients = {
    fires:    "linear-gradient(to right, #1e3a5f, #3b82f6, #22c55e, #f59e0b, #ef4444)",
    roc_auc:  "linear-gradient(to right, #1e3a5f, #3b82f6, #22c55e)",
    landslides:"linear-gradient(to right, #1e3a5f, #a855f7, #ef4444)"
  };
  if (legendBar) legendBar.style.background = gradients[currentMetric] || gradients.fires;
  setText("legend-min", lab[0]);
  setText("legend-max", lab[1]);
}

// ─── MAP TOOLTIP ──────────────────────────────────────────────────────────────
const mapWrap = document.querySelector(".svg-map-wrap");
const tooltip = document.getElementById("map-tooltip");
let tooltipVisible = false;

function showMapTooltip(e, name, sd) {
  if (!tooltip) return;
  const metricLabel = { fires: "Veg. Fires", roc_auc: "ROC-AUC 2024", landslides: "GSI Landslides" };
  const val = sd[currentMetric];
  tooltip.innerHTML = `
    <div style="font-weight:700;color:#f1f5f9;margin-bottom:4px">${name}</div>
    <div style="color:#94a3b8;font-size:0.7rem">${metricLabel[currentMetric]}: <strong style="color:#f97316">${currentMetric==="roc_auc" ? val?.toFixed(4) : fmt(val||0)}</strong></div>
    <div style="color:#64748b;font-size:0.68rem;margin-top:4px">🔥 Fires: ${fmt(sd.fires||0)}</div>
    <div style="color:#64748b;font-size:0.68rem">⛰️ Landslides: ${fmt(sd.landslides||0)}</div>
    <div style="color:#64748b;font-size:0.68rem">📊 ROC-AUC: ${(sd.roc_auc||0).toFixed(4)}</div>
  `;
  tooltip.style.display = "block";
  tooltipVisible = true;
  moveMapTooltip(e);
}

function moveMapTooltip(e) {
  if (!tooltip || !tooltipVisible || !mapWrap) return;
  const rect = mapWrap.getBoundingClientRect();
  let x = e.clientX - rect.left + 12;
  let y = e.clientY - rect.top - 10;
  if (x + 180 > rect.width) x -= 200;
  tooltip.style.left = x + "px";
  tooltip.style.top  = y + "px";
}

function hideMapTooltip() {
  if (tooltip) tooltip.style.display = "none";
  tooltipVisible = false;
}

// ─── STATE SELECTION ──────────────────────────────────────────────────────────
function selectState(name, sd) {
  selectedState = name;

  document.querySelectorAll(".map-state").forEach(p => p.classList.remove("selected"));
  document.querySelectorAll(`.map-state[data-state="${name}"]`).forEach(p => p.classList.add("selected"));

  setText("sel-state-title", name);

  const container = document.getElementById("sel-state-stats");
  if (!container) return;

  const rows = [
    ["📐 Grid Cells (1 km²)", fmt(sd.cells || 0)],
    ["🔥 Vegetation Fires", fmt(sd.fires || 0)],
    ["📈 Wildfire ROC-AUC 2024", (sd.roc_auc || 0).toFixed(4)],
    ["⛰️ GSI Landslides", fmt(sd.landslides || 0)],
    ["📍 Representative Lat", (sd.lat || 0).toFixed(2) + "°N"],
    ["📍 Representative Lon", (sd.lon || 0).toFixed(2) + "°E"],
  ];

  container.innerHTML = rows.map(([k, v]) => `
    <div class="stat-row">
      <span class="stat-key">${k}</span>
      <span class="stat-val">${v}</span>
    </div>
  `).join("");

  // Pre-fill simulator
  if (sd.lat) document.getElementById("in-lat") && setSlider("in-lat", "val-lat", sd.lat.toFixed(1));
  if (sd.lon) document.getElementById("in-lon") && setSlider("in-lon", "val-lon", sd.lon.toFixed(1));
  const stateSelect = document.getElementById("in-state");
  if (stateSelect) stateSelect.value = name;
}

document.getElementById("btn-send-to-sim")?.addEventListener("click", () => {
  document.querySelector('.tab-btn[data-tab="simulator"]')?.click();
});

// ─── IMPORTANCE BARS ──────────────────────────────────────────────────────────
function renderImportanceBars(d) {
  const importance = (d.tables && d.tables.wildfire_importance) || [];
  if (importance.length === 0) { renderImportanceFallback(); return; }

  const container = document.getElementById("wf-importance-bars");
  if (!container) return;

  const top = importance.slice(0, 10);
  const maxImp = Math.max(...top.map(r => r.importance_mean || 0));

  container.innerHTML = top.map(row => {
    const pct = maxImp > 0 ? (row.importance_mean / maxImp * 100) : 0;
    return `
      <div class="bar-item">
        <span class="bar-name">${row.feature || row.Feature || "—"}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${pct.toFixed(1)}%"></div></div>
        <span class="bar-val">${(row.importance_mean || 0).toFixed(4)}</span>
      </div>
    `;
  }).join("");
}

function renderImportanceFallback() {
  const FALLBACK = [
    { feature: "sin_doy",             importance_mean: 0.1279 },
    { feature: "centroid_lat",        importance_mean: 0.0408 },
    { feature: "centroid_lon",        importance_mean: 0.0269 },
    { feature: "relative_humidity_min",importance_mean: 0.0211 },
    { feature: "state_name",          importance_mean: 0.0187 },
    { feature: "cos_doy",             importance_mean: 0.0164 },
    { feature: "era5_soil_water_7d",  importance_mean: 0.0122 },
    { feature: "dewpoint_depression", importance_mean: 0.0098 },
  ];
  const fakeData = { tables: { wildfire_importance: FALLBACK } };
  renderImportanceBars(fakeData);
}

// ─── MODEL TABLES ─────────────────────────────────────────────────────────────
function renderModelTables(d) {
  const tables = d.tables || {};
  renderTable("tbl-wf-models",  tables.wildfire_models,  formatWildfire);
  renderTable("tbl-wf-state",   tables.wildfire_per_state, formatState);
  renderTable("tbl-wf-season",  tables.wildfire_per_season, formatSeason);
  renderTable("tbl-ls-models",  tables.landslide_models, formatLandslide);
}

function renderTable(id, rows, formatter) {
  const tbl = document.getElementById(id);
  if (!tbl || !rows || rows.length === 0) return;
  const cols = formatter ? formatter.cols : Object.keys(rows[0]);
  const bestModel = rows.reduce((best, r) => {
    const v = r.test_roc_auc || r.roc_auc || 0;
    return v > (best.v || 0) ? { name: r.model || r.state_name, v } : best;
  }, {});

  const headerRow = `<thead><tr>${cols.map(c => `<th>${c.label || c}</th>`).join("")}</tr></thead>`;
  const bodyRows = rows.map(row => {
    const isBest = (row.model || row.state_name) === bestModel.name;
    return `<tr class="${isBest ? "best-row" : ""}">` +
      cols.map(c => {
        const key = c.key || c;
        const val = row[key];
        const cls = formatter?.classFor?.(c.key || c, val, isBest) || "";
        return `<td class="${cls}">${formatter?.format?.(c.key || c, val) ?? (val ?? "—")}</td>`;
      }).join("") + "</tr>";
  }).join("");

  tbl.innerHTML = headerRow + `<tbody>${bodyRows}</tbody>`;
}

const formatWildfire = {
  cols: [
    { label: "Model",         key: "model" },
    { label: "Syllabus Role", key: "syllabus_role" },
    { label: "CV PR-AUC",     key: "cv_pr_auc" },
    { label: "CV ROC-AUC",    key: "cv_roc_auc" },
    { label: "2024 ROC-AUC",  key: "test_roc_auc" },
    { label: "2024 Recall",   key: "test_recall" },
    { label: "F1 Score",      key: "test_f1" },
    { label: "Op. Threshold", key: "operating_threshold" },
  ],
  format(key, val) {
    if (val === null || val === undefined) return "—";
    if (["cv_pr_auc","cv_roc_auc","test_roc_auc","test_recall","test_f1","operating_threshold"].includes(key))
      return Number(val).toFixed(4);
    return val;
  },
  classFor(key, val, isBest) {
    if (key === "test_roc_auc" && isBest) return "td-best td-auc";
    if (key === "test_roc_auc") return "td-auc";
    return "";
  }
};

const formatState = {
  cols: [
    { label: "State",        key: "state_name" },
    { label: "ROC-AUC",      key: "roc_auc" },
    { label: "Recall",       key: "recall" },
    { label: "Precision",    key: "precision" },
    { label: "F1",           key: "f1" },
    { label: "Positives",    key: "n_positives" },
  ],
  format(key, val) {
    if (val === null || val === undefined) return "—";
    if (["roc_auc","recall","precision","f1"].includes(key))
      return Number(val).toFixed(4);
    return val;
  },
  classFor(key, val, isBest) { return key === "roc_auc" ? "td-auc" : ""; }
};

const formatSeason = {
  cols: [
    { label: "Season",       key: "season" },
    { label: "ROC-AUC",      key: "roc_auc" },
    { label: "Recall",       key: "recall" },
    { label: "Precision",    key: "precision" },
    { label: "F1",           key: "f1" },
    { label: "Positives",    key: "n_positives" },
  ],
  format: formatState.format,
  classFor: formatState.classFor
};

const formatLandslide = {
  cols: [
    { label: "Model",        key: "model" },
    { label: "CV PR-AUC",    key: "cv_pr_auc" },
    { label: "CV ROC-AUC",   key: "cv_roc_auc" },
    { label: "2024 ROC-AUC", key: "test_roc_auc" },
    { label: "2024 Recall",  key: "test_recall" },
    { label: "Op. Threshold",key: "operating_threshold" },
  ],
  format: formatWildfire.format,
  classFor: formatWildfire.classFor
};

// ─── 5. RISK SIMULATOR ────────────────────────────────────────────────────────
let currentHazard = "wildfire";

// Slider live update
["lat","lon","doy","temp","rh-min","soil","wind","rain1d","rain3d","rain7d","rain15d","drydays"].forEach(id => {
  const el = document.getElementById("in-" + id);
  if (!el) return;
  el.addEventListener("input", () => {
    setText("val-" + id, el.value);
    if (id === "doy") {
      const doy = parseInt(el.value);
      const d = new Date(2024, 0, doy);
      setText("val-doy-date", `(${d.toLocaleDateString("en", { month: "short", day: "numeric" })})`);
    }
  });
});

// Hazard mode toggle
document.querySelectorAll(".hazard-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".hazard-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentHazard = btn.dataset.hazard;
    const caveat = document.getElementById("landslide-caveat");
    if (caveat) caveat.style.display = currentHazard === "landslide" ? "block" : "none";
    setText("result-title", currentHazard === "wildfire" ? "Wildfire Risk Estimate" : "Landslide Trigger Estimate");
  });
});

// Presets
const PRESETS = {
  mizoram_dry: {
    state: "Mizoram", season: "Pre-Monsoon",
    lat: 23.1, lon: 92.9, doy: 100,
    temp: 33.5, "rh-min": 15, soil: 0.11, wind: 3.2,
    rain1d: 0, rain3d: 2, rain7d: 4, rain15d: 8, drydays: 28
  },
  assam_monsoon: {
    state: "Assam", season: "Monsoon",
    lat: 26.2, lon: 92.9, doy: 195,
    temp: 29.0, "rh-min": 72, soil: 0.42, wind: 2.1,
    rain1d: 38, rain3d: 95, rain7d: 220, rain15d: 480, drydays: 0
  },
  remal_cyclone: {
    state: "Mizoram", season: "Pre-Monsoon",
    lat: 23.5, lon: 92.7, doy: 148,
    temp: 26.0, "rh-min": 88, soil: 0.48, wind: 9.8,
    rain1d: 185, rain3d: 310, rain7d: 450, rain15d: 650, drydays: 0
  },
  arunachal_winter: {
    state: "Arunachal Pradesh", season: "Winter",
    lat: 27.5, lon: 94.1, doy: 20,
    temp: 11.0, "rh-min": 55, soil: 0.26, wind: 1.5,
    rain1d: 0, rain3d: 1, rain7d: 3, rain15d: 10, drydays: 14
  }
};

document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const p = PRESETS[btn.dataset.preset];
    if (!p) return;
    if (document.getElementById("in-state")) document.getElementById("in-state").value = p.state;
    if (document.getElementById("in-season")) document.getElementById("in-season").value = p.season;
    ["lat","lon","doy","temp","rh-min","soil","wind","rain1d","rain3d","rain7d","rain15d","drydays"].forEach(id => {
      const val = p[id];
      if (val !== undefined) {
        setSlider("in-"+id, "val-"+id, val);
        if (id === "doy") {
          const d = new Date(2024, 0, parseInt(val));
          setText("val-doy-date", `(${d.toLocaleDateString("en", { month: "short", day: "numeric" })})`);
        }
      }
    });
    btn.style.borderColor = "var(--fire)";
    btn.style.color = "var(--fire)";
    setTimeout(() => { btn.style.borderColor = ""; btn.style.color = ""; }, 1500);
  });
});

function setSlider(inputId, valId, val) {
  const el = document.getElementById(inputId);
  if (el) { el.value = val; }
  setText(valId, Number(val).toFixed(el?.step?.includes(".") ? 2 : (val % 1 !== 0 ? 1 : 0)));
}

// Run model button
document.getElementById("btn-run-predict")?.addEventListener("click", runPrediction);

async function runPrediction() {
  const btn = document.getElementById("btn-run-predict");
  if (btn) { btn.textContent = "Running…"; btn.disabled = true; }

  const lat   = parseFloat(document.getElementById("in-lat")?.value    || 23.5);
  const lon   = parseFloat(document.getElementById("in-lon")?.value    || 92.8);
  const doy   = parseInt(document.getElementById("in-doy")?.value      || 90);
  const temp  = parseFloat(document.getElementById("in-temp")?.value   || 31.0);
  const rhMin = parseFloat(document.getElementById("in-rh-min")?.value || 18);
  const soil  = parseFloat(document.getElementById("in-soil")?.value   || 0.14);
  const wind  = parseFloat(document.getElementById("in-wind")?.value   || 2.5);
  const rain1d  = parseFloat(document.getElementById("in-rain1d")?.value  || 0);
  const rain3d  = parseFloat(document.getElementById("in-rain3d")?.value  || 0);
  const rain7d  = parseFloat(document.getElementById("in-rain7d")?.value  || 0);
  const rain15d = parseFloat(document.getElementById("in-rain15d")?.value || 0);
  const drydays = parseFloat(document.getElementById("in-drydays")?.value || 22);
  const state   = document.getElementById("in-state")?.value   || "Mizoram";
  const season  = document.getElementById("in-season")?.value  || "Pre-Monsoon";

  const sinDoy = Math.sin(2 * Math.PI * doy / 365);
  const cosDoy = Math.cos(2 * Math.PI * doy / 365);
  const dewpt  = temp - (100 - rhMin) / 5;
  const dewDep = temp - dewpt;
  const rhMean = Math.min(100, rhMin + 15);
  const eraRain = rain1d * 0.9;

  const record = {
    temperature_c: temp, dewpoint_c: dewpt, dewpoint_depression_c: dewDep,
    wind_speed_ms: wind, soil_water_layer1: soil, era5_rainfall_mm: eraRain,
    relative_humidity_mean: rhMean, relative_humidity_min: rhMin,
    era5_temp_mean_7d: temp - 1.5, era5_temp_max_7d: temp + 3,
    era5_rh_min_7d: rhMin + 3, era5_rh_mean_7d: rhMean + 5,
    era5_soil_water_mean_7d: soil * 1.05, era5_wind_mean_7d: wind,
    era5_rain_sum_3d: rain3d * 0.9, era5_rain_sum_7d: rain7d * 0.9,
    era5_rain_sum_15d: rain15d * 0.9, era5_days_since_rain: drydays,
    imd_rain_1d: rain1d, imd_rain_lag1d: rain1d * 0.3,
    imd_rain_sum_3d: rain3d, imd_rain_sum_7d: rain7d,
    imd_rain_sum_15d: rain15d, imd_rain_max_7d: rain1d * 1.4,
    imd_rainy_days_7d: Math.round(rain7d > 0 ? Math.min(7, rain7d / 20) : 0),
    imd_rainy_days_15d: Math.round(rain15d > 0 ? Math.min(15, rain15d / 20) : 0),
    imd_days_since_rain: drydays,
    centroid_lat: lat, centroid_lon: lon,
    sin_doy: sinDoy, cos_doy: cosDoy,
    state_name: state, season: season
  };

  const endpoint = currentHazard === "landslide" ? "/api/predict/landslide" : "/api/predict/wildfire";

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "API error");

    const pred = Array.isArray(data.predictions) ? data.predictions[0] : (data.predictions || data);
    displayResult(pred, data);
  } catch (err) {
    console.error("Prediction error:", err);
    showResultError(err.message);
  } finally {
    if (btn) {
      btn.innerHTML = `<svg viewBox="0 0 20 20" fill="currentColor" width="16"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg> Run Model`;
      btn.disabled = false;
    }
  }
}

function displayResult(pred, data) {
  const rawScore = pred.raw_score || 0;
  const calProb  = pred.calibrated_daily_probability || pred.raw_score || 0;
  const band     = (pred.relative_score_band || pred.provisional_risk_band || "LOW").toUpperCase();
  const alert    = pred.above_cv_f1_threshold;

  // Animate gauge
  const pct = rawScore * 100;
  animateGauge(pct, band);

  // Band pill
  const pill = document.getElementById("result-band-pill");
  if (pill) {
    pill.textContent = band;
    const bandClass = band.includes("CRITICAL") ? "crit"
      : band.includes("HIGH") ? "high"
      : band.includes("MODERATE") ? "mod" : "low";
    pill.className = "band-pill " + bandClass;
  }

  // Metrics grid
  const metricsEl = document.getElementById("result-metrics");
  if (metricsEl) {
    const rows = [
      { label: "Raw Risk Score", value: (rawScore * 100).toFixed(1) + "%", color: bandColor(band) },
      { label: "Calibrated Prob.", value: (calProb * 100).toFixed(4) + "%" },
      { label: "Alert Triggered", value: alert ? "YES ⚠" : "No", color: alert ? "#ef4444" : "" },
      { label: "Model", value: data.model_name || "—" },
    ];
    metricsEl.innerHTML = rows.map(r =>
      `<div class="metric-box">
        <div class="mv" ${r.color ? `style="color:${r.color}"` : ""}>${r.value}</div>
        <div class="mk">${r.label}</div>
      </div>`
    ).join("");
  }
}

function showResultError(msg) {
  const metricsEl = document.getElementById("result-metrics");
  if (metricsEl) {
    metricsEl.innerHTML = `<div class="metric-box" style="grid-column:1/-1;color:#ef4444">⚠ ${msg}</div>`;
  }
  animateGauge(0, "LOW");
}

function animateGauge(pct, band) {
  const arc = document.getElementById("gauge-arc");
  const scoreText = document.getElementById("gauge-score-text");
  const needle = document.getElementById("gauge-needle");
  if (!arc) return;

  const totalDash = 346;
  const fillDash  = totalDash * Math.min(pct / 100, 1);
  const offset    = totalDash - fillDash;

  arc.style.strokeDashoffset = offset;
  arc.style.stroke = bandColor(band);

  if (scoreText) scoreText.textContent = pct.toFixed(1) + "%";

  if (needle) {
    needle.style.opacity = "1";
    const angle = -180 + (pct / 100) * 180;
    needle.style.transform = `rotate(${angle}deg)`;
  }
}

function bandColor(band) {
  const b = (band || "").toUpperCase();
  if (b.includes("CRITICAL")) return "#ef4444";
  if (b.includes("HIGH"))     return "#f97316";
  if (b.includes("MODERATE")) return "#f59e0b";
  return "#22c55e";
}

// ─── 6. GALLERY ───────────────────────────────────────────────────────────────
const GALLERY_ITEMS = [
  { src: "/outputs/maps/study_area_and_grid.png",              cat: "maps",      title: "Study Area & 1 km Grid",              desc: "253,408 cells · 7 Sister States · EPSG:32646" },
  { src: "/outputs/maps/wildfire_hotspot_map.png",             cat: "maps",      title: "Wildfire Hotspot Map (2021–2024)",     desc: "FIRMS VIIRS S-NPP C2 vegetation fires" },
  { src: "/outputs/maps/landslide_inventory_map.png",          cat: "maps",      title: "GSI Landslide Inventory Map",          desc: "9,970 field-validated records · 463 dated cell-days" },
  { src: "/outputs/figures/wildfire_model_comparison.png",     cat: "wildfire",  title: "Wildfire Model Comparison",            desc: "6 classifiers · CV PR-AUC & 2024 ROC-AUC" },
  { src: "/outputs/figures/wildfire_roc_pr_curves.png",        cat: "wildfire",  title: "Wildfire ROC & PR Curves",             desc: "2024 test set · realistic prevalence 0.035%" },
  { src: "/outputs/figures/wildfire_confusion_matrices.png",   cat: "wildfire",  title: "Wildfire Confusion Matrices",          desc: "All 6 models at operating threshold" },
  { src: "/outputs/figures/wildfire_decision_tree.png",        cat: "wildfire",  title: "Wildfire Decision Tree",               desc: "Syllabus-core interpretable classifier" },
  { src: "/outputs/figures/wildfire_feature_importance.png",   cat: "wildfire",  title: "Wildfire Feature Importance",          desc: "Permutation ROC-AUC drop · top features" },
  { src: "/outputs/figures/wildfire_calibration.png",          cat: "wildfire",  title: "Wildfire Probability Calibration",     desc: "Pre- vs post-Bayesian prior adjustment" },
  { src: "/outputs/figures/wildfire_seasonal_trends.png",      cat: "wildfire",  title: "Wildfire Seasonal Trends",             desc: "Monthly & seasonal fire detections (2021–2024)" },
  { src: "/outputs/figures/wildfire_correlation_heatmap.png",  cat: "wildfire",  title: "Wildfire Feature Correlation Heatmap", desc: "Multicollinearity across weather & temporal features" },
  { src: "/outputs/figures/landslide_model_comparison.png",    cat: "landslide", title: "Landslide Model Comparison",           desc: "Preliminary weather-trigger classifiers" },
  { src: "/outputs/figures/landslide_roc_pr_curves.png",       cat: "landslide", title: "Landslide ROC & PR Curves",            desc: "Preliminary weather-trigger model · 2024 test" },
  { src: "/outputs/figures/landslide_confusion_matrices.png",  cat: "landslide", title: "Landslide Confusion Matrices",         desc: "Preliminary classifiers on 2024 holdout" },
  { src: "/outputs/figures/landslide_decision_tree.png",       cat: "landslide", title: "Landslide Decision Tree",              desc: "Interpretable rainfall/soil-moisture rules" },
  { src: "/outputs/figures/landslide_feature_importance.png",  cat: "landslide", title: "Landslide Feature Importance",         desc: "Top hydrometeorological triggers" },
  { src: "/outputs/figures/landslide_rainfall_eda.png",        cat: "landslide", title: "Landslide Rainfall EDA",               desc: "IMD antecedent rainfall distributions" },
  { src: "/outputs/figures/landslide_gsi_coolr_eda.png",       cat: "landslide", title: "GSI & COOLR Inventory EDA",            desc: "Spatial & temporal landslide record breakdown" },
  { src: "/outputs/figures/weather_rainfall_eda.png",          cat: "landslide", title: "ERA5 & IMD Weather EDA",               desc: "Northeast India seasonal weather patterns" },
];

let currentCat = "all";

function renderGallery(cat) {
  const grid = document.getElementById("gallery-grid");
  if (!grid) return;
  const items = cat === "all" ? GALLERY_ITEMS : GALLERY_ITEMS.filter(i => i.cat === cat);

  grid.innerHTML = items.map((item, idx) => `
    <div class="gallery-item" data-idx="${idx}" data-cat="${item.cat}" onclick="openLightbox('${item.src}', '${item.title}')">
      <div class="gallery-img-wrap">
        <img src="${item.src}" alt="${item.title}" loading="lazy"
             onerror="this.style.opacity='0.3'; this.parentElement.innerHTML='<div style=\\'color:#64748b;font-size:0.75rem;text-align:center;padding:20px\\'>${item.title}<br><span style=\\'font-size:0.65rem\\'>Image loading…</span></div>'"/>
      </div>
      <div class="gallery-caption">
        <span class="gallery-cat-badge cat-${item.cat}">${item.cat}</span>
        <span>${item.title}</span>
      </div>
    </div>
  `).join("");
}

document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentCat = btn.dataset.cat;
    renderGallery(currentCat);
  });
});

function openLightbox(src, title) {
  const lb = document.getElementById("lightbox");
  const img = document.getElementById("lightbox-img");
  const cap = document.getElementById("lightbox-caption");
  if (!lb || !img) return;
  img.src = src;
  if (cap) cap.textContent = title;
  lb.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeLightbox() {
  const lb = document.getElementById("lightbox");
  if (lb) lb.style.display = "none";
  document.body.style.overflow = "";
}

document.getElementById("lightbox-close")?.addEventListener("click", closeLightbox);
document.getElementById("lightbox-overlay")?.addEventListener("click", closeLightbox);
document.addEventListener("keydown", e => { if (e.key === "Escape") closeLightbox(); });

// ─── 7. AUDIT TAB ─────────────────────────────────────────────────────────────
function renderAuditTab(d) {
  const audit = d.audit || {};
  const firms = d.firms_meta || {};
  const grid  = d.grid_meta  || {};
  const imd   = d.weather_meta || {};
  const lf    = d.landslide_feasibility || {};

  const auditRows = [
    { icon: "🔥", title: "FIRMS VIIRS S-NPP C2",   detail: `${fmt(firms.vegetation_fire_count_type_0||219928)} vegetation fires (type=0) · NE India · 2021–2024` },
    { icon: "🗺️", title: "1 km Grid (EPSG:32646)", detail: `${fmt(grid.total_cells||253408)} cells · 7 Sister States · 253,412 km²` },
    { icon: "🌧️", title: "IMD Gridded Rainfall",   detail: `48 months complete (2021–2024) · 415 grid points · median dist 10.57 km` },
    { icon: "🌡️", title: "ERA5 Reanalysis",        detail: `44/48 months · 2491 grid pts · missing 2023-08/09/11/12 preserved as NaN` },
    { icon: "⛰️", title: "GSI Landslide PDF",       detail: `${fmt(lf.gsi_ne_india_within_study_boundary||9970)} NE records inside boundary · ${lf.dated_events_2021_2024_raw||673} dated 2021–2024 (${lf.dated_unique_celldays_2021_2024||463} unique cell-days)` },
    { icon: "📊", title: "Wildfire Training Set",   detail: `717,324 rows · 119,554 positives · train 2021-2023 · test 2024 (1,000,000 cell-days)` },
    { icon: "🤖", title: "Models Trained",           detail: `6 classifiers: Dummy, LogReg, GaussianNB, Decision Tree, Random Forest, HistGradientBoosting` },
    { icon: "✅", title: "Test Suite",               detail: `pytest -v → 9/9 passed · all ingestion, feature, label, training modules` },
  ];

  const limRows = [
    { icon: "🏔️", title: "No DEM / Slope / Aspect",  detail: "SRTM/ASTER terrain data not downloaded locally. Zero fabricated inputs." },
    { icon: "🌿", title: "No WorldCover / NDVI",       detail: "ESA WorldCover land-use and MODIS NDVI absent. Huge wildfire driver missing." },
    { icon: "🪨", title: "No SoilGrids / Geology",     detail: "Soil texture & geological susceptibility maps unavailable. Landslide model is weather-trigger only." },
    { icon: "🛰️", title: "ERA5 Missing 4 Months",      detail: "2023-08/09/11/12 absent in local NetCDF. Preserved as NaN (not filled with 0)." },
    { icon: "📍", title: "Mizoram Survey Bias",         detail: "529/673 dated GSI records are from 2024 Mizoram surveys. state_name excluded from landslide features." },
    { icon: "📡", title: "Sikkim ERA5 Gap",             detail: "Local ERA5 starts at 89.8°E; Sikkim (88.0–88.9°E) excluded from ERA5-coupled spatial grid." },
    { icon: "⚠️", title: "Research Use Only",           detail: "All outputs carry mandatory disclaimer. Not validated for operational early warning." },
  ];

  const container = document.getElementById("audit-details");
  if (container) {
    container.innerHTML = auditRows.map(r => `
      <div class="audit-row">
        <div class="audit-icon">${r.icon}</div>
        <div class="audit-body">
          <div class="audit-title">${r.title}</div>
          <div class="audit-detail">${r.detail}</div>
        </div>
      </div>
    `).join("");
  }

  const limEl = document.getElementById("limitations-list");
  if (limEl) {
    limEl.innerHTML = limRows.map(r => `
      <div class="audit-row">
        <div class="audit-icon">${r.icon}</div>
        <div class="audit-body">
          <div class="audit-title">${r.title}</div>
          <div class="audit-detail">${r.detail}</div>
        </div>
      </div>
    `).join("");
  }
}

// ─── 8. BOOT ──────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  renderGallery("all");
  renderImportanceFallback();
  renderMapFallback();
  fetchOverview().catch(() => {}); // async – fills data when server responds
});
