"""
Generate comprehensive PowerPoint Presentation for:
Flood Prediction and Early Warning System
(with Multi-Hazard Landslide & Wildfire Intelligence)
7-Member Team Breakdown: Sachin, Anshul, Ujjwal, Aadi, Malvika, Shubhangi, Sonam
"""
from __future__ import annotations
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(r"c:\Users\lenovo\Desktop\aiml project")
FIGS = PROJECT_ROOT / "outputs" / "figures"
MAPS = PROJECT_ROOT / "outputs" / "maps"
PPTX_OUT = PROJECT_ROOT / "Flood_Prediction_and_Early_Warning_System.pptx"

# Colors
DARK_BG   = RGBColor(0x0A, 0x0F, 0x1E)  # Deep midnight navy
CARD_BG   = RGBColor(0x13, 0x1E, 0x36)  # Dark slate blue card
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
GRAY      = RGBColor(0x94, 0xA3, 0xB8)  # Slate-400
DARKTEXT  = RGBColor(0x0F, 0x17, 0x2A)  # Slate-900 for light card
CYAN      = RGBColor(0x06, 0xB6, 0xD4)  # Cyan
BLUE      = RGBColor(0x3B, 0x82, 0xF6)  # Blue
GREEN     = RGBColor(0x22, 0xC5, 0x5E)  # Green
ORANGE    = RGBColor(0xF9, 0x73, 0x16)  # Fire Orange
PURPLE    = RGBColor(0xA8, 0x55, 0xF7)  # Purple
GOLD      = RGBColor(0xFA, 0xCC, 0x15)  # Gold
TEAL      = RGBColor(0x14, 0xB8, 0xA6)  # Teal
LIME      = RGBColor(0x84, 0xCC, 0x16)  # Lime
ROSE      = RGBColor(0xF4, 0x3F, 0x5E)  # Rose
RED       = RGBColor(0xEF, 0x44, 0x44)  # Red

# Member Colors (7 distinct vibrant colors)
C_SACHIN    = CYAN     # Full Stack & Architecture (M1)
C_ANSHUL    = LIME     # Geospatial & Grid (M2)
C_UJJWAL    = ORANGE   # Wildfire ML & Feature Engineering (M3)
C_AADI      = PURPLE   # Landslide ML & QA (M4)
C_MALVIKA   = TEAL     # Flood Ingestion & Hydrology (M5)
C_SHUBHANGI = BLUE     # Flood ML & Benchmark (M6)
C_SONAM     = GOLD     # Multi-Hazard & Domain Shift (M7)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def set_bg(slide, color=DARK_BG):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, l, t, w, h, fill_color, border_color=None, border_pt=0):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color and border_pt > 0:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, l, t, w, h, font_size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT, italic=False, wrap=True, line_spacing=None):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    paragraphs = str(text).split("\n")
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = para
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
        if line_spacing:
            p.line_spacing = Pt(line_spacing)
    return txBox

def add_header(slide, title, subtitle="", tag="HIMA MULTI-HAZARD AI", tag_color=CYAN):
    add_rect(slide, 0, 0, 13.333, 1.1, CARD_BG)
    add_rect(slide, 0, 1.05, 13.333, 0.05, tag_color)
    add_text(slide, tag.upper(), 0.5, 0.12, 10, 0.25, font_size=10, bold=True, color=tag_color)
    add_text(slide, title, 0.5, 0.35, 12.3, 0.45, font_size=22, bold=True, color=WHITE)
    if subtitle:
        add_text(slide, subtitle, 0.5, 0.78, 12.3, 0.25, font_size=12, bold=False, color=GRAY)

def add_img(slide, img_path, l, t, w, h=None):
    p = Path(img_path)
    if p.exists():
        if h:
            slide.shapes.add_picture(str(p), Inches(l), Inches(t), Inches(w), Inches(h))
        else:
            slide.shapes.add_picture(str(p), Inches(l), Inches(t), Inches(w))
    else:
        add_rect(slide, l, t, w, h or 3, CARD_BG, border_color=GRAY, border_pt=1)
        add_text(slide, f"Figure: {p.name}", l+0.2, t+0.2, w-0.4, 0.5, font_size=12, color=GRAY)

def section_slide(title, subtitle, member_name, role_title, color):
    slide = prs.slides.add_slide(BLANK)
    set_bg(slide, DARK_BG)
    add_rect(slide, 0, 0, 0.25, 7.5, color)
    add_rect(slide, 0.8, 1.5, 11.5, 4.5, CARD_BG, border_color=color, border_pt=1.5)
    add_text(slide, "MODULE DIVISION — APPLICATION OF AI", 1.2, 1.8, 10, 0.3, font_size=12, bold=True, color=color)
    add_text(slide, title, 1.2, 2.2, 10.5, 1.0, font_size=32, bold=True, color=WHITE)
    add_rect(slide, 1.2, 3.3, 8.0, 0.04, color)
    add_text(slide, subtitle, 1.2, 3.5, 10.5, 0.6, font_size=16, color=GRAY)
    
    # Member Badge
    add_rect(slide, 1.2, 4.4, 6.0, 1.1, RGBColor(0x1E, 0x29, 0x3B), border_color=color, border_pt=1)
    add_text(slide, f"OWNER: {member_name.upper()}", 1.4, 4.55, 5.5, 0.35, font_size=16, bold=True, color=WHITE)
    add_text(slide, role_title, 1.4, 4.95, 5.5, 0.35, font_size=12, color=color)
    return slide

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: TITLE SLIDE
# ═══════════════════════════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(BLANK)
set_bg(s1, DARK_BG)
add_rect(s1, 0, 0, 0.3, 7.5, CYAN)
add_rect(s1, 0.8, 0.8, 11.7, 5.9, CARD_BG, border_color=RGBColor(0x33, 0x41, 0x55), border_pt=1)

add_text(s1, "ACADEMIC CAPSTONE PROJECT • APPLICATION OF AI (CSET312)", 1.2, 1.1, 10, 0.3, font_size=12, bold=True, color=CYAN)
add_text(s1, "Flood Prediction and Early Warning System", 1.2, 1.5, 11, 0.9, font_size=36, bold=True, color=WHITE)
add_text(s1, "with Multi-Hazard Landslide & Wildfire Intelligence", 1.2, 2.3, 11, 0.5, font_size=20, bold=False, color=GOLD)
add_rect(s1, 1.2, 2.9, 10.5, 0.04, CYAN)

add_text(s1, "An End-to-End Machine Learning Framework Coupling NASA FIRMS, IMD Gridded Rainfall,\n"
             "ECMWF ERA5-Land Reanalysis, GSI Field Inventories, and INDOFLOODS River Gauges",
         1.2, 3.1, 10.5, 0.6, font_size=13, color=GRAY)

# 7 Member Grid on Title Slide
add_text(s1, "TEAM MEMBERS & TECHNICAL OWNERSHIP:", 1.2, 3.85, 10.5, 0.3, font_size=11, bold=True, color=WHITE)
team_cols = [
    ("Sachin (Lead)", "Full Stack & Web Architecture", C_SACHIN),
    ("Anshul", "Geospatial Grid & Weather Ingest", C_ANSHUL),
    ("Ujjwal", "Wildfire ML & Feature Eng.", C_UJJWAL),
    ("Aadi", "Landslide ML, Calibration & QA", C_AADI),
    ("Malvika", "Flood Ingestion & CHIRPS Hydrology", C_MALVIKA),
    ("Shubhangi", "Flood ML & 6-Model Benchmark", C_SHUBHANGI),
    ("Sonam", "Multi-Hazard & Domain Transfer", C_SONAM),
]

for idx, (m_name, m_role, m_col) in enumerate(team_cols):
    cx = 1.2 + (idx % 4) * 2.65
    cy = 4.25 if idx < 4 else 5.25
    add_rect(s1, cx, cy, 2.5, 0.85, RGBColor(0x0F, 0x17, 0x2A), border_color=m_col, border_pt=1)
    add_text(s1, m_name, cx+0.1, cy+0.1, 2.3, 0.28, font_size=11, bold=True, color=WHITE)
    add_text(s1, m_role, cx+0.1, cy+0.4, 2.3, 0.4, font_size=9, color=m_col)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: EXECUTIVE SUMMARY & PROBLEM STATEMENT
# ═══════════════════════════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(BLANK)
set_bg(s2, DARK_BG)
add_header(s2, "Executive Summary & The Multi-Hazard Challenge", "Why an Integrated Multi-Hazard Early Warning System is Vital for India")

cards_s2 = [
    ("🌊 River Floods (Primary Hazard)", 
     "• Monsoon river overflow causes massive annual infrastructure loss across India.\n"
     "• CWC warning thresholds rely on static gauge heights rather than proactive ML.\n"
     "• Need: Predicting danger level exceedance days in advance using antecedent rainfall lags.", C_SHUBHANGI),
    ("⛰️ Rainfall Landslides (Cascading)", 
     "• Intense rainfall saturates hillslopes, triggering fatal debris flows in fragile terrains.\n"
     "• Complex trigger mechanics: immediate same-day rain vs 3–15 day antecedent moisture accumulation.\n"
     "• Need: Hydrometeorological trigger modeling calibrated for rare-event baseline priors.", C_AADI),
    ("🔥 Pre-Monsoon Wildfires (Compound)", 
     "• Arid pre-monsoon spells (Feb–May) trigger severe forest fires across Northeast India.\n"
     "• Forest burning strips vegetative root cover, severely exacerbating monsoon soil erosion and flash runoff.\n"
     "• Need: Coupling thermal satellite detections with ERA5 atmospheric drying indices.", C_UJJWAL),
]
for i, (title, desc, col) in enumerate(cards_s2):
    x = 0.6 + i * 4.1
    add_rect(s2, x, 1.4, 3.9, 5.6, CARD_BG, border_color=col, border_pt=1.5)
    add_rect(s2, x, 1.4, 3.9, 0.45, col)
    add_text(s2, title, x+0.15, 1.48, 3.6, 0.35, font_size=13, bold=True, color=DARKTEXT)
    add_text(s2, desc, x+0.2, 2.05, 3.5, 4.8, font_size=12, color=WHITE, line_spacing=18)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: 7-MEMBER RESPONSIBILITY MATRIX
# ═══════════════════════════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(BLANK)
set_bg(s3, DARK_BG)
add_header(s3, "7-Member Architectural Responsibility Matrix", "Complete Technical Ownership Across Codebase, Models, Data & Verification")

mem_matrix = [
    ("Sachin", "Full Stack AI Lead", "frontend/index.html, app.js, styles.css, src/api/predict.py", "Interactive Web UI, Live Multi-Hazard Gauge, REST API Server", C_SACHIN),
    ("Anshul", "Geospatial Data Lead", "src/geospatial/, src/audit/, src/ingestion/firms.py, imd.py", "253,408 Grid Cells (EPSG:32646), FIRMS Fires, IMD & ERA5 Ingestion", C_ANSHUL),
    ("Ujjwal", "Wildfire ML Lead", "src/features/weather_features.py, src/training/wildfire_pipelines.py", "33 Features, Cyclical Encodings, Wildfire 6-Model Benchmark (0.9358 AUC)", C_UJJWAL),
    ("Aadi", "Landslide & QA Lead", "src/ingestion/gsi.py, src/training/landslide_pipelines.py, tests/", "GSI PDF Mining, Bayesian Prior Calibration, 9 Pytest Integrity Tests", C_AADI),
    ("Malvika", "Flood Ingestion Lead", "src/ingestion/flood.py, data/raw/flood/, config/project.yaml", "INDOFLOODS Ingestion (4,548 events), CHIRPS T1d–T10d Lags, Parquet Sync", C_MALVIKA),
    ("Shubhangi", "Flood ML Lead", "src/training/flood_pipelines.py, models/flood_model.joblib", "Flood 6-Model Benchmark, HistGradientBoosting Tuning (0.9557 Test AUC)", C_SHUBHANGI),
    ("Sonam", "Domain Transfer Lead", "src/api/predict.py, src/evaluation/metrics.py, frontend/app.js", "Spatial Confounder Elimination, Catchment Scaling, Multi-Hazard Scenarios", C_SONAM),
]

for idx, (m_name, m_role, m_files, m_contrib, m_col) in enumerate(mem_matrix):
    y = 1.35 + idx * 0.82
    add_rect(s3, 0.5, y, 12.33, 0.74, CARD_BG, border_color=m_col, border_pt=1)
    add_rect(s3, 0.5, y, 0.15, 0.74, m_col)
    add_text(s3, m_name, 0.8, y+0.12, 1.8, 0.28, font_size=13, bold=True, color=WHITE)
    add_text(s3, m_role, 0.8, y+0.42, 1.8, 0.25, font_size=10, color=m_col)
    add_text(s3, f"Files: {m_files}", 2.7, y+0.12, 4.5, 0.28, font_size=10, color=GRAY)
    add_text(s3, f"Core Contribution: {m_contrib}", 2.7, y+0.4, 9.8, 0.3, font_size=11, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: SYSTEM ARCHITECTURE & DATA FLOW
# ═══════════════════════════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(BLANK)
set_bg(s4, DARK_BG)
add_header(s4, "Multi-Hazard System Architecture & Data Pipeline", "Seamless Offline-First Coupling from Raw Satellite Archives to Browser UI")

arch_blocks = [
    ("RAW DATA LAYER", ["• NASA FIRMS VIIRS (219,928 fires)", "• IMD 0.25° Gridded Rain (48 mo)", "• ECMWF ERA5-Land Reanalysis (44 mo)", "• GSI 9,970 Landslide PDFs", "• INDOFLOODS (4,548 flood events)"], CYAN),
    ("GEOSPATIAL & FEATURE LAYER", ["• 1 km UTM Zone 46N Grid (253,408 cells)", "• Spatial KD-Tree Nearest Neighbor", "• 33 Weather Features + Cyclical DOY", "• CHIRPS Lags (T1d to T10d)", "• Zero Fabricated / Interpolated Values"], LIME),
    ("MACHINE LEARNING ENGINES", ["• 3 Independent Hazard Pipelines", "• 6 Standard Classifiers per Hazard", "• Spatial 5-Fold CV + Hold-Out Tests", "• Bayesian Prior Calibrated Probabilities", "• Serialized Scikit-Learn Pipelines (.joblib)"], GOLD),
    ("SERVING & INTERFACE LAYER", ["• Python Multi-Threaded HTTP API", "• Real-Time POST /api/predict/{hazard}", "• Animated SVG Gauge & Bands", "• Interactive 7-State Choropleth Map", "• Scenario Simulator with Instant Feedback"], ROSE),
]
for i, (title, items, col) in enumerate(arch_blocks):
    x = 0.5 + i * 3.1
    add_rect(s4, x, 1.4, 2.9, 5.5, CARD_BG, border_color=col, border_pt=1.5)
    add_rect(s4, x, 1.4, 2.9, 0.45, col)
    add_text(s4, title, x+0.1, 1.5, 2.7, 0.3, font_size=11, bold=True, color=DARKTEXT)
    add_text(s4, "\n\n".join(items), x+0.15, 2.05, 2.6, 4.7, font_size=11, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: SACHIN — FULL STACK & API INTEGRATION (SLIDES 5–8)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Full-Stack AI Architecture & Real-Time Dashboard", 
              "REST API Engine · Interactive SVG Map · Multi-Hazard Risk Simulator",
              "Sachin", "Team Lead & Full-Stack AI Engineer", C_SACHIN)

# Slide 6: Sachin - Web Dashboard Architecture
s6 = prs.slides.add_slide(BLANK)
set_bg(s6, DARK_BG)
add_header(s6, "Web Dashboard & Interactive Risk Simulator", "Crafted by Sachin — Zero External Framework Overhead, 100% Native Web Standards", tag_color=C_SACHIN)
add_rect(s6, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=C_SACHIN, border_pt=1)
add_text(s6, "🖥️ ARCHITECTURAL HIGHLIGHTS (Sachin)", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_SACHIN)
add_text(s6, 
    "• Single-Page Application (SPA) built without heavy React/Vue runtime overhead.\n\n"
    "• Native Canvas Particle System rendering dynamic ambient atmospheric background.\n\n"
    "• Interactive SVG Map of Northeast India: renders geojson state boundaries offline with zero mapbox/leaflet dependencies.\n\n"
    "• Animated SVG Risk Gauge: uses CSS arc offset interpolation (`stroke-dashoffset`) for smooth real-time risk indication.\n\n"
    "• Tabbed Modular Navigation: Overview, Risk Simulator, ML Models, Visuals Gallery, and Data Audit.",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=18)

add_rect(s6, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=RGBColor(0x33, 0x41, 0x55), border_pt=1)
add_text(s6, "🌐 REST API & ENDPOINTS (Sachin)", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=CYAN)
add_text(s6,
    "• Multi-Threaded HTTP Server: Implemented in `src/api/predict.py` using Python's standard `ThreadingHTTPServer`.\n\n"
    "• `/api/overview`: Aggregates ingestion audits, model cards, GeoJSON polygons, and comparison tables in single JSON payload.\n\n"
    "• `/api/predict/wildfire`: Evaluates 33 features, applies Bayesian prior correction, returns calibrated probability & risk band.\n\n"
    "• `/api/predict/landslide`: Runs preliminary hydrometeorological trigger pipeline.\n\n"
    "• `/api/predict/flood`: Evaluates antecedent CHIRPS lags (T1d–T10d) + catchment area, returns danger level exceedance prob.",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=18)

# Slide 7: Sachin - Interactive SVG Map
s7 = prs.slides.add_slide(BLANK)
set_bg(s7, DARK_BG)
add_header(s7, "Geospatial SVG Map & Multi-Hazard Simulator", "Built by Sachin — Real-Time Coordinate Injection & Dynamic Scenario Presets", tag_color=C_SACHIN)
add_img(s7, MAPS / "study_area_and_grid.png", 0.5, 1.4, 6.0, 5.6)
add_rect(s7, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=C_SACHIN, border_pt=1)
add_text(s7, "🎯 INTERACTIVE WORKFLOW", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_SACHIN)
add_text(s7,
    "1. Map Selection → Simulator Coupling:\n"
    "   Clicking any of the 7 states on the choropleth map automatically extracts its representative latitude & longitude and injects them into the Risk Simulator.\n\n"
    "2. Real-World Hazard Toggle:\n"
    "   Seamless 3-way toggle between Wildfire, Landslide, and Flood. The UI dynamically switches visible input sliders, removing non-pertinent weather fields in Flood mode.\n\n"
    "3. Real-Time Risk Bands:\n"
    "   Maps model probabilities into research display bands: LOW (0–30%), MODERATE (30–60%), HIGH (60–80%), and CRITICAL (80–100%).\n\n"
    "4. One-Click Scenario Presets:\n"
    "   Includes pre-calibrated real meteorological events (e.g., Cyclone Remal, Dry Pre-Monsoon, Flash Flood).",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

# Slide 8: Sachin - Viva Q&A
s8 = prs.slides.add_slide(BLANK)
set_bg(s8, DARK_BG)
add_header(s8, "Member 1 (Sachin) — Viva Defense & Architecture Q&A", "Technical Justifications for Full-Stack System Design", tag_color=C_SACHIN)
add_rect(s8, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_SACHIN, border_pt=1)
viva_s = [
    ("Q1: Why use Python's built-in ThreadingHTTPServer instead of Flask or FastAPI?",
     "A: To maintain zero external deployment friction. The university demo requires instant 1-click startup via `run_hima.bat` without installing heavy WSGI containers or external server binaries. Threading handles concurrent requests smoothly."),
    ("Q2: How does the web UI prevent cross-origin resource sharing (CORS) blocks?",
     "A: The server acts as both the static file server (serving index.html, app.js, styles.css) and the API handler on the exact same port (8000). All API routes are relative (`/api/*`), completely eliminating CORS pre-flight checks."),
    ("Q3: Why did you build an offline SVG map instead of embedding Google Maps or Mapbox?",
     "A: Mapbox and Google Maps require active API tokens and external internet connectivity. Our SVG map uses simplified TopoJSON/GeoJSON polygons rendered directly in the DOM, guaranteeing 100% offline functionality in isolated test environments.")
]
for i, (q, a) in enumerate(viva_s):
    y = 1.6 + i * 1.75
    add_text(s8, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=CYAN)
    add_text(s8, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: ANSHUL — GEOSPATIAL & MULTI-SOURCE INGESTION (SLIDES 9–11)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Geospatial Engineering & Multi-Source Ingestion",
              "253,408 1 km² Grid · FIRMS VIIRS · IMD Gridded Rainfall · ERA5 Reanalysis",
              "Anshul", "Geospatial & Data Pipeline Lead", C_ANSHUL)

# Slide 10: Anshul - Geospatial Grid
s10 = prs.slides.add_slide(BLANK)
set_bg(s10, DARK_BG)
add_header(s10, "1 km² Spatiotemporal Fishnet Grid Construction", "Engineered by Anshul — Dual Projected CRS & Strict Multi-Source Geometry Clipping", tag_color=C_ANSHUL)
add_rect(s10, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=C_ANSHUL, border_pt=1)
add_text(s10, "📐 GEOSPATIAL SPECIFICATIONS (Anshul)", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_ANSHUL)
add_text(s10,
    "• Study Region: Seven Sister States of Northeast India (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura).\n\n"
    "• Metric Projection: Converted geographic WGS84 coordinates into **EPSG:32646 (UTM Zone 46N)** where 1 unit = exactly 1 metre.\n\n"
    "• Fishnet Grid: Generated exactly **253,408 unique 1 km × 1 km grid cells** across 253,412 km².\n\n"
    "• Spatial Indexing: Constructed Scipy cKD-Tree data structures using cell centroid coordinates for microsecond-level nearest neighbor spatial joins.\n\n"
    "• Elimination of Spatial Gaps: Clipped strictly to Survey of India official boundary polygons.",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=18)

add_rect(s10, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=RGBColor(0x33, 0x41, 0x55), border_pt=1)
add_text(s10, "🛰️ MULTI-SOURCE INGESTION AUDIT", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=LIME)
add_text(s10,
    "• NASA FIRMS VIIRS (S-NPP C2):\n"
    "  Mined 219,928 confirmed vegetation fires (Type=0). Deduplicated exact spatio-temporal co-detections within the same 375m pixel footprint.\n\n"
    "• IMD 0.25° Gridded Rainfall:\n"
    "  48 complete NetCDF calendar months (2021–2024). 415 grid points mapped with median station-to-cell distance of 10.57 km.\n\n"
    "• ECMWF ERA5-Land Reanalysis:\n"
    "  0.1° resolution (~10 km), 2,491 grid points. 4 missing months (2023-08, 09, 11, 12) strictly preserved as NaN rather than corrupted with artificial zeros.",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=18)

# Slide 11: Anshul - Viva Q&A
s11 = prs.slides.add_slide(BLANK)
set_bg(s11, DARK_BG)
add_header(s11, "Member 2 (Anshul) — Viva Defense & Geospatial Q&A", "Technical Justifications for Coordinate Reference Systems & Data Cleanliness", tag_color=C_ANSHUL)
add_rect(s11, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_ANSHUL, border_pt=1)
viva_anshul = [
    ("Q1: Why couldn't you create a 1 km grid directly in WGS84 (EPSG:4326) degrees?",
     "A: In EPSG:4326, coordinates are measured in degrees. 1 degree of longitude at the equator is ~111 km, but shrinks significantly as latitude increases toward the Himalayas (28°N). Generating cells in degrees creates deformed trapezoids. UTM Zone 46N (EPSG:32646) uses metres, guaranteeing exact 1,000m × 1,000m squares."),
    ("Q2: Why was Sikkim excluded from the continuous ERA5 grid?",
     "A: The local ERA5 NetCDF reanalysis bounding box begins at longitude 89.8°E, while Sikkim is located entirely between 88.0°E and 88.9°E. Forcing Sikkim into the grid would have required fabricating weather data. We chose academic honesty over synthetic filling."),
    ("Q3: How did you join point-level fire detections to 1 km polygon cells without massive memory bottlenecks?",
     "A: We mapped cell centroids into a Scipy KD-Tree structure and performed nearest-neighbor lookup in Euclidean UTM coordinates, reducing join complexity from O(N × M) to O(N log M), running in under 4 seconds.")
]
for i, (q, a) in enumerate(viva_anshul):
    y = 1.6 + i * 1.75
    add_text(s11, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=LIME)
    add_text(s11, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: UJJWAL — WILDFIRE ML & FEATURE ENGINEERING (SLIDES 12–15)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Wildfire Machine Learning & Feature Engineering",
              "33 Spatiotemporal Variables · Cyclical DOY · 6 Classifiers · 0.9358 Test ROC-AUC",
              "Ujjwal", "Feature Engineering & Wildfire ML Lead", C_UJJWAL)

# Slide 13: Ujjwal - Features
s13 = prs.slides.add_slide(BLANK)
set_bg(s13, DARK_BG)
add_header(s13, "33 Spatiotemporal Weather Features & Cyclical Encodings", "Crafted by Ujjwal — Capturing Pre-Monsoon Aridity and Forest Desiccation", tag_color=C_UJJWAL)
add_rect(s13, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=C_UJJWAL, border_pt=1)
add_text(s13, "🔬 FEATURE TAXONOMY (Ujjwal)", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_UJJWAL)
add_text(s13,
    "• Cyclical Temporal Transformations:\n"
    "  Encodes day-of-year into periodic wavefunctions to preserve annual continuity between Dec 31 (DOY 365) and Jan 1 (DOY 1):\n"
    "  $$\\sin(2\\pi \\cdot \\text{doy} / 365), \\quad \\cos(2\\pi \\cdot \\text{doy} / 365)$$\n\n"
    "• Atmospheric Moisture Deficit:\n"
    "  Calculated Dewpoint Depression: $T_{air} - T_{dew}$. Higher depression indicates extreme evaporative drying of forest litter.\n\n"
    "• Antecedent Drought Tracking:\n"
    "  Consecutive dry days ($rain < 1.0\\text{ mm}$), 3-day, 7-day, and 15-day cumulative antecedent IMD rainfall.",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

add_img(s13, FIGS / "wildfire_feature_importance.png", 6.8, 1.4, 6.0, 5.6)

# Slide 14: Ujjwal - Wildfire Models
s14 = prs.slides.add_slide(BLANK)
set_bg(s14, DARK_BG)
add_header(s14, "Wildfire Classifier Benchmark — 6 Syllabus Models", "Evaluated on 2024 Temporal Hold-Out (1,000,000 cell-days, 0.035% Realistic Prevalence)", tag_color=C_UJJWAL)
add_img(s14, FIGS / "wildfire_model_comparison.png", 0.5, 1.4, 6.0, 5.6)
add_img(s14, FIGS / "wildfire_roc_pr_curves.png", 6.8, 1.4, 6.0, 5.6)

# Slide 15: Ujjwal - Viva Q&A
s15 = prs.slides.add_slide(BLANK)
set_bg(s15, DARK_BG)
add_header(s15, "Member 3 (Ujjwal) — Viva Defense & Feature Engineering Q&A", "Technical Justifications for Model Selection & Temporal Splits", tag_color=C_UJJWAL)
add_rect(s15, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_UJJWAL, border_pt=1)
viva_u_ml = [
    ("Q1: Why did HistGradientBoosting beat Random Forest and Decision Trees?",
     "A: HistGradientBoosting bins continuous numerical values into 256 integer buckets, dramatically accelerating split calculations and handling natural NaN gaps in ERA5 reanalysis without imputation distortion. Its boosting mechanism sequentially corrects hard false positives."),
    ("Q2: Why did you evaluate on a realistic prevalence test set (0.035%) instead of a 50-50 balanced set?",
     "A: In the real world, wildfires occur in less than 0.04% of daily cells. Evaluating on a 50-50 synthetic balanced test set yields artificially inflated precision and false confidence. Our 1,000,000 cell-day 2024 test set proves real-world deployment viability."),
    ("Q3: Why was sin(DOY) the #1 permutation feature importance driver?",
     "A: Forest fires in Northeast India are hyper-seasonal, peaking strictly between February and April (pre-monsoon slash-and-burn jhum cycles). The sine transform gives the tree an uninterrupted seasonal clock signal.")
]
for i, (q, a) in enumerate(viva_u_ml):
    y = 1.6 + i * 1.75
    add_text(s15, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=ORANGE)
    add_text(s15, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: AADI — LANDSLIDE ML, CALIBRATION & QA (SLIDES 16–19)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Landslide Modeling, Calibration & QA Test Suite",
              "GSI PDF Extraction · Bayesian Prior Adjustment · 9 Pytest Automated Tests",
              "Aadi", "Landslide ML, Calibration & QA Lead", C_AADI)

# Slide 17: Aadi - Landslide Models
s17 = prs.slides.add_slide(BLANK)
set_bg(s17, DARK_BG)
add_header(s17, "Landslide Hydrometeorological Trigger Modeling", "Engineered by Aadi — GSI PDF Extraction & Weather-Only Feasibility Analysis", tag_color=C_AADI)
add_img(s17, FIGS / "landslide_model_comparison.png", 0.5, 1.4, 6.0, 5.6)
add_rect(s17, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=C_AADI, border_pt=1)
add_text(s17, "⛏️ GSI INVENTORY & CHALLENGES", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_AADI)
add_text(s17,
    "• Mined 9,970 Landslide Records:\n"
    "  Extracted from scanned Geological Survey of India (GSI) multi-page PDF bulletins using `pdfplumber`.\n\n"
    "• Critical Temporal Filtering:\n"
    "  Out of 9,970 records, only 673 possessed valid calendar dates within the 2021–2024 study window (collapsing to 463 unique cell-days).\n\n"
    "• Scientific Candor (Honest Limitations):\n"
    "  High-resolution static DEM (slope/aspect) and SoilGrids were unavailable locally. Aadi modeled this strictly as a **Weather-Trigger Pipeline** (rainfall + soil saturation), explicitly avoiding fabricated terrain layers.",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

# Slide 18: Aadi - Bayesian Calibration & 9 Tests
s18 = prs.slides.add_slide(BLANK)
set_bg(s18, DARK_BG)
add_header(s18, "Bayesian Prior Calibration & 9 Automated Pytest Cases", "Guaranteed Mathematical Monotonicity, Non-Negativity, and Zero Future Leakage", tag_color=C_AADI)
add_rect(s18, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=C_AADI, border_pt=1)
add_text(s18, "⚖️ BAYESIAN PRIOR ODDS CALIBRATION", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_AADI)
add_text(s18,
    "• The Problem: Classifiers trained on balanced subsets output raw probabilities near 0.5, creating severe false alarms in deployment.\n\n"
    "• The Bayesian Correction:\n"
    "  $$\\text{Odds}_{true} = \\text{Odds}_{sample} \\times \\left( \\frac{\\pi_{true}}{1 - \\pi_{true}} \\Big/ \\frac{\\pi_{sample}}{1 - \\pi_{sample}} \\right)$$\n"
    "• Brier Score plummeted from 0.083 to **0.0005**, aligning probabilities with true population frequency while preserving ROC-AUC ranking.",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

add_rect(s18, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=GREEN, border_pt=1)
add_text(s18, "✅ 9 INTEGRITY TEST CASES (ALL PASSED)", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=GREEN)
test_list = [
    "test_config_loads_and_has_disclaimer",
    "test_days_since_rain_preserves_missing_gaps",
    "test_imd_season_mapping",
    "test_bayes_prior_adjustment_monotonic_and_bounded",
    "test_risk_band_boundaries",
    "test_no_post_event_leakage_in_features",
    "test_grid_and_boundaries_artifacts_if_built",
    "test_validated_wildfire_predictor_inference",
    "test_required_deliverables_exist"
]
for idx, tname in enumerate(test_list):
    ty = 2.15 + idx * 0.48
    add_text(s18, f"✔ {tname}", 7.2, ty, 5.2, 0.3, font_size=10, bold=True, color=WHITE)

# Slide 19: Aadi - Viva Q&A
s19 = prs.slides.add_slide(BLANK)
set_bg(s19, DARK_BG)
add_header(s19, "Member 4 (Aadi) — Viva Defense & Quality Assurance Q&A", "Technical Justifications for Spatial Bias Removal & Test Rigor", tag_color=C_AADI)
add_rect(s19, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_AADI, border_pt=1)
viva_aadi = [
    ("Q1: Why did you exclude 'state_name' from landslide features?",
     "A: In the GSI dataset, 529 out of 673 dated landslide records originated from specialized survey teams in Mizoram. Including `state_name` would cause the model to learn 'Mizoram = Landslide', exploiting survey collection bias rather than physical precipitation mechanisms."),
    ("Q2: What does `test_no_post_event_leakage_in_features` verify?",
     "A: It mathematically asserts that zero feature values depend on time $t+1$ or later. Any future information leakage invalidates an early warning system. Every rolling rainfall metric uses strictly lags up to day $t$."),
    ("Q3: Does Bayesian calibration alter the ROC-AUC score?",
     "A: No. Because the Bayesian odds adjustment is strictly monotonic, it preserves the relative ranking of samples. The ROC-AUC remains identical, while the probability values are calibrated to true real-world occurrence rates.")
]
for i, (q, a) in enumerate(viva_aadi):
    y = 1.6 + i * 1.75
    add_text(s19, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=C_AADI)
    add_text(s19, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: MALVIKA — FLOOD DATA INGESTION & CHIRPS HYDROLOGY (SLIDES 20–22)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Flood Ingestion & CHIRPS Hydrological Processing",
              "INDOFLOODS 4,548 Gauged Events · Antecedent Rainfall Lags T1d–T10d · 1.3M Gauge Days",
              "Malvika", "Flood Data Ingestion & CHIRPS Hydrological Processing Lead", C_MALVIKA)

# Slide 21: Malvika - INDOFLOODS & CHIRPS Ingestion
s21 = prs.slides.add_slide(BLANK)
set_bg(s21, DARK_BG)
add_header(s21, "INDOFLOODS Ingestion & CHIRPS Antecedent Moisture", "Engineered by Malvika — Multi-Lag Hydrological Descriptors for National River Basins", tag_color=C_MALVIKA)
add_rect(s21, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=C_MALVIKA, border_pt=1)
add_text(s21, "🌊 INDOFLOODS BENCHMARK INGESTION (Malvika)", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_MALVIKA)
add_text(s21,
    "• National River Basin Archive:\n"
    "  Ingested **4,548 all-India gauged river flood events** spanning 1965 to 2020 from Central Water Commission (CWC) monitoring stations.\n\n"
    "• Target Threshold Formulation:\n"
    "  Target variable `exceeds_danger_level`: binary label indicating whether river peak discharge $\\ge$ official CWC danger mark.\n"
    "  - Positive events: 3,481 (76.5%)\n"
    "  - Negative events: 1,067 (23.5%)\n\n"
    "• High-Performance Storage:\n"
    "  Processed into snappy-compressed `data/processed/flood.parquet` (611 KB), ensuring sub-millisecond query execution.",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

add_rect(s21, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=RGBColor(0x33, 0x41, 0x55), border_pt=1)
add_text(s21, "🌧️ CHIRPS ANTECEDENT LAG MATRIX", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=TEAL)
add_text(s21,
    "• CHIRPS Rainfall Integration:\n"
    "  Processed 1,302,155 daily rainfall observations across 155 river gauges from 1998 to 2020.\n\n"
    "• Cumulative Antecedent Lag Vectors:\n"
    "  Built multi-temporal precipitation accumulation windows:\n"
    "  - $T_{1d}$: 24-hour flash precipitation\n"
    "  - $T_{2d}, T_{3d}$: Immediate channel runoff accumulation\n"
    "  - $T_{4d}, T_{5d}, T_{6d}, T_{7d}$: Sub-surface catchment saturation\n"
    "  - $T_{8d}, T_{9d}, T_{10d}$: Basin-scale peak inundation volume\n\n"
    "• Supporting Variables: Mapped river stream order, catchment area ($km^2$), soil type, lithology, and urban fraction.",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

# Slide 22: Malvika - Viva Q&A
s22 = prs.slides.add_slide(BLANK)
set_bg(s22, DARK_BG)
add_header(s22, "Member 5 (Malvika) — Viva Defense & Hydrology Q&A", "Technical Justifications for Multi-Day Rainfall Lags & Event Labeling", tag_color=C_MALVIKA)
add_rect(s22, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_MALVIKA, border_pt=1)
viva_malvika = [
    ("Q1: Why are multi-day antecedent rainfall lags (T1d–T10d) necessary for flood prediction?",
     "A: River discharge does not depend solely on same-day rainfall. In large catchments, rainfall takes several days to travel through tributaries to the main river channel (time of concentration). Lags $T_{1d}$ through $T_{10d}$ capture the progressive hydrological accumulation curve."),
    ("Q2: Why was CHIRPS daily rainfall chosen over localized weather stations?",
     "A: Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) provides high-resolution 0.05° satellite-gauge blended rainfall with continuous coverage across all Indian river basins, eliminating localized station outage gaps."),
    ("Q3: How did you handle the sparse coverage of INDOFLOODS gauges in Northeast India?",
     "A: INDOFLOODS contains only 2 gauges in Northeast India. Malvika established that physical hydrological rainfall-runoff mechanisms are invariant across geomorphological basins. The model is trained national-scale and applied regionally.")
]
for i, (q, a) in enumerate(viva_malvika):
    y = 1.6 + i * 1.75
    add_text(s22, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=TEAL)
    add_text(s22, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: SHUBHANGI — FLOOD MACHINE LEARNING ARCHITECTURE (SLIDES 23–26)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Flood Machine Learning Architecture & Benchmarking",
              "6-Classifier Evaluation · HistGradientBoosting Winner · 0.9557 Test ROC-AUC",
              "Shubhangi", "Flood Machine Learning Architecture & Model Benchmark Lead", C_SHUBHANGI)

# Slide 24: Shubhangi - Flood Model Comparison
s24 = prs.slides.add_slide(BLANK)
set_bg(s24, DARK_BG)
add_header(s24, "Flood Classifier Benchmark — 6 Syllabus Models", "Engineered by Shubhangi — 70/30 Stratified Split & 5-Fold Stratified Cross-Validation", tag_color=C_SHUBHANGI)
add_img(s24, FIGS / "flood_model_comparison.png", 0.5, 1.4, 6.0, 5.6)
add_img(s24, FIGS / "flood_roc_pr_curves.png", 6.8, 1.4, 6.0, 5.6)

# Slide 25: Shubhangi - Decision Tree & Matrices
s25 = prs.slides.add_slide(BLANK)
set_bg(s25, DARK_BG)
add_header(s25, "Confusion Matrices & Decision Tree Interpretability", "Trained by Shubhangi — 98.56% Recall at Optimal F1 Operating Threshold", tag_color=C_SHUBHANGI)
add_img(s25, FIGS / "flood_confusion_matrices.png", 0.5, 1.4, 6.0, 5.6)
add_img(s25, FIGS / "flood_decision_tree.png", 6.8, 1.4, 6.0, 5.6)

# Slide 26: Shubhangi - Viva Q&A
s26 = prs.slides.add_slide(BLANK)
set_bg(s26, DARK_BG)
add_header(s26, "Member 6 (Shubhangi) — Viva Defense & ML Benchmark Q&A", "Technical Justifications for Pipeline Selection, Recall Maximization & FAR Control", tag_color=C_SHUBHANGI)
add_rect(s26, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_SHUBHANGI, border_pt=1)
viva_shubhangi = [
    ("Q1: Why is Recall prioritized over overall Accuracy in flood prediction?",
     "A: In disaster early warning, a False Negative (missing an actual catastrophic flood) leads to loss of human lives. A False Positive (issuing a precautionary alert for an event that stays below danger level) costs significantly less. HistGradientBoosting achieved 98.56% Recall."),
    ("Q2: Why did Gaussian Naive Bayes have a high False Alarm Rate (77.19%)?",
     "A: Naive Bayes assumes strict feature independence. Antecedent rainfall variables ($T_{1d}, T_{2d}, \\dots, T_{10d}$) exhibit extreme collinearity ($r > 0.85$). Correlated features artificially amplify the posterior odds, driving severe over-prediction."),
    ("Q3: How was the optimal operating threshold (0.2849) determined?",
     "A: Shubhangi swept classification thresholds across precision-recall curves to maximize F1-score ($2 \\times P \\times R / (P + R)$), balancing high disaster capture rate (98.56%) while restricting the False Alarm Rate to 16.56%.")
]
for i, (q, a) in enumerate(viva_shubhangi):
    y = 1.6 + i * 1.75
    add_text(s26, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=BLUE)
    add_text(s26, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: SONAM — DOMAIN TRANSFER & MULTI-HAZARD GENERALIZATION (SLIDES 27–30)
# ═══════════════════════════════════════════════════════════════════════════════
section_slide("Domain Transfer & Multi-Hazard Generalization",
              "Solving Spatial Confounder · Catchment Scaling · Cascading Disaster Chains",
              "Sonam", "Multi-Hazard Integration, Domain Generalization & Operational Decision Support Lead", C_SONAM)

# Slide 28: Sonam - Solving Domain Shift
s28 = prs.slides.add_slide(BLANK)
set_bg(s28, DARK_BG)
add_header(s28, "Solving the Spatial Domain Shift (The 1.7% Bug Fix)", "Discovered & Engineered by Sonam — Eliminating Geographic Confounders for Pure Hydrology", tag_color=C_SONAM)
add_rect(s28, 0.5, 1.4, 6.0, 5.6, CARD_BG, border_color=RED, border_pt=1.5)
add_text(s28, "⚠️ THE SPATIAL CONFOUNDER BUG", 0.8, 1.6, 5.4, 0.35, font_size=14, bold=True, color=RED)
add_text(s28,
    "• Initial Symptom: The flood meter refused to rise above 1.7%, even under 500mm catastrophic rainfall!\n\n"
    "• Sonam's Root Cause Analysis:\n"
    "  - INDOFLOODS gauges reside between **72.8°E and 91.6°E**.\n"
    "  - Northeast India coordinates reside at **92.8°E to 97.3°E**.\n"
    "  - HistGradientBoosting split on Longitude: any coordinate $> 91.6°E$ was routed to an empty leaf with zero training samples, capping predicted probability at **0.017 (1.7%)**!",
    0.8, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

add_rect(s28, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=GREEN, border_pt=1.5)
add_text(s28, "✅ SONAM'S HYDROLOGICAL TRANSFER FIX", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=GREEN)
add_text(s28,
    "• Eliminating Spatial Coordinates:\n"
    "  Removed `Latitude` and `Longitude` from features. Flood physics depends on **rainfall and catchment mechanics**, not GPS digits!\n\n"
    "• Expanding Catchment Scale:\n"
    "  Updated basin scale parameterization from small headwaters ($100\\text{ km}^2$) to major river systems ($50,000\\text{ km}^2$).\n\n"
    "• The Result:\n"
    "  The flood meter now operates dynamically across the full **0% to 100%** spectrum (Low: 18.6%, Moderate: 86.8%, Extreme: 92.4%).",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

# Slide 29: Sonam - Feature Importance & Cascading Risk
s29 = prs.slides.add_slide(BLANK)
set_bg(s29, DARK_BG)
add_header(s29, "Permutation Feature Importance & Cascading Multi-Hazards", "Analyzed by Sonam — Catchment Scale ($km^2$) and Rain Lags as Primary Flood Drivers", tag_color=C_SONAM)
add_img(s29, FIGS / "flood_feature_importance.png", 0.5, 1.4, 6.0, 5.6)
add_rect(s29, 6.8, 1.4, 6.0, 5.6, CARD_BG, border_color=C_SONAM, border_pt=1)
add_text(s29, "🔗 THE MULTI-HAZARD CASCADING CHAIN", 7.1, 1.6, 5.4, 0.35, font_size=14, bold=True, color=C_SONAM)
add_text(s29,
    "Sonam synthesized the compound interaction across all three hazards:\n\n"
    "1. PHASE 1 (Pre-Monsoon March–April):\n"
    "   High temperatures and low humidity ignite widespread forest fires. The burning destroys root structures and creates hydrophobic soil layers.\n\n"
    "2. PHASE 2 (Early Monsoon May–June):\n"
    "   Torrential rains strike destabilized slopes, triggering massive debris flows and landslides.\n\n"
    "3. PHASE 3 (Peak Monsoon July–August):\n"
    "   Eroded hillslope sediments choke riverbeds, elevating channel beds and causing catastrophic river floods with minimal discharge capacity.",
    7.1, 2.1, 5.4, 4.6, font_size=12, color=WHITE, line_spacing=17)

# Slide 30: Sonam - Viva Q&A
s30 = prs.slides.add_slide(BLANK)
set_bg(s30, DARK_BG)
add_header(s30, "Member 7 (Sonam) — Viva Defense & Multi-Hazard Q&A", "Technical Justifications for Domain Generalization & Multi-Hazard Synthesis", tag_color=C_SONAM)
add_rect(s30, 0.5, 1.4, 12.33, 5.6, CARD_BG, border_color=C_SONAM, border_pt=1)
viva_sonam = [
    ("Q1: Did removing Latitude and Longitude degrade the flood model's performance?",
     "A: No. Cross-validation proved CV PR-AUC remained identical at 0.9886, and CV ROC-AUC held at 0.9696 vs 0.9703. Eliminating coordinates removed geographic memorization while preserving pure hydrological generalization."),
    ("Q2: Why is catchment area the single most important flood feature?",
     "A: In hydrological physics, peak discharge ($Q$) scales directly with basin area ($A$) via the rational equation $Q = C \\cdot I \\cdot A$. A 100mm storm over a 20,000 km² basin concentrates hundreds of millions of cubic metres of runoff, whereas the same rain over a 100 km² stream dissipates rapidly."),
    ("Q3: What makes this project an 'Application of AI' rather than three separate projects?",
     "A: Real-world disasters are compound and coupled. Sonam's multi-hazard framework integrates disparate satellite, atmospheric, hillslope, and river basin modalities into a unified spatial decision-support system.")
]
for i, (q, a) in enumerate(viva_sonam):
    y = 1.6 + i * 1.75
    add_text(s30, q, 0.8, y, 11.7, 0.35, font_size=13, bold=True, color=GOLD)
    add_text(s30, a, 0.8, y+0.4, 11.7, 1.2, font_size=12, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 31: COMPARATIVE MASTER TABLE
# ═══════════════════════════════════════════════════════════════════════════════
s31 = prs.slides.add_slide(BLANK)
set_bg(s31, DARK_BG)
add_header(s31, "Cross-Hazard Comparative ML Benchmark Master Table", "Unified Evaluation Across Wildfire, Landslide, and Flood Prediction Engines")

table_headers = ["Hazard", "Best Model", "Training Dataset", "Test Set Size", "Test ROC-AUC", "Test PR-AUC", "Test Recall", "False Alarm Rate"]
table_data = [
    ["🔥 Wildfire", "HistGradientBoosting", "2021–2023 Cells (717k)", "1,000,000 cell-days (2024)", "0.9358", "0.0827*", "85.20%", "4.30%"],
    ["⛰️ Landslide", "HistGradientBoosting", "2021–2023 GSI Dated (97)", "366 cell-days (2024)", "0.9367", "0.8912", "88.50%", "18.20%"],
    ["🌊 River Flood", "HistGradientBoosting", "1965–2020 Gauges (3,183)", "1,365 events (Holdout)", "0.9557", "0.9825", "98.56%", "16.56%"],
]

# Render Table
rows = len(table_data) + 1
cols = len(table_headers)
left = Inches(0.5)
top = Inches(1.6)
width = Inches(12.33)
height = Inches(2.8)

table_shape = s31.shapes.add_table(rows, cols, left, top, width, height)
tbl = table_shape.table
col_widths = [1.5, 2.3, 2.3, 1.8, 1.1, 1.1, 1.1, 1.1]
for i, w in enumerate(col_widths):
    tbl.columns[i].width = Inches(w)

for j, h in enumerate(table_headers):
    cell = tbl.cell(0, j)
    cell.fill.solid()
    cell.fill.fore_color.rgb = CARD_BG
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p.alignment = PP_ALIGN.CENTER

for i, row in enumerate(table_data):
    for j, val in enumerate(row):
        cell = tbl.cell(i+1, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B) if i % 2 == 0 else CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER if j >= 4 else PP_ALIGN.LEFT

add_rect(s31, 0.5, 4.7, 12.33, 2.3, CARD_BG, border_color=CYAN, border_pt=1)
add_text(s31, "💡 SCIENTIFIC TAKEAWAYS FROM THE MASTER BENCHMARK", 0.8, 4.9, 11.5, 0.35, font_size=13, bold=True, color=CYAN)
add_text(s31,
    "• Uniform Winner Across All 3 Modalities:\n"
    "  HistGradientBoosting outperformed traditional Decision Trees and Random Forests across all three hazards due to native binning and NaN tolerance.\n\n"
    "• Precision-Recall Rarity Effect:\n"
    "  Wildfire PR-AUC appears low (0.0827) strictly due to realistic 0.035% baseline prevalence, representing a **236× lift** over random guessing (0.00035).\n\n"
    "• Operational Early Warning Readiness:\n"
    "  All three models achieved $> 85\\%$ Recall, guaranteeing safety-critical alert coverage for civil protection.",
    0.8, 5.3, 11.5, 1.6, font_size=11, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 32: HONEST ACADEMIC LIMITATIONS
# ═══════════════════════════════════════════════════════════════════════════════
s32 = prs.slides.add_slide(BLANK)
set_bg(s32, DARK_BG)
add_header(s32, "Honest Academic Limitations & Zero Fabricated Data", "Strict Adherence to Scientific Integrity and Ground-Truth Availability")

limitations = [
    ("🏔️ Terrain Layers (DEM/Slope) Missing", "High-resolution SRTM/ASTER elevation and slope data were not available in the local offline environment. Landslide modeling was honestly limited to hydrometeorological weather triggers rather than fabricating synthetic slope maps."),
    ("🌿 Satellite Land-Cover & Soil Moisture", "ESA WorldCover (10m) and Sentinel-2 NDVI vegetative health layers were absent. These are known physical firebreak and soil-cohesion indicators that will elevate future model precision."),
    ("🛰️ ERA5-Land Reanalysis Gap (4 Months)", "August, September, November, and December 2023 were missing from the local ERA5 NetCDF archive. These were strictly preserved as NaN rather than corrupted with zero-filling or synthetic interpolation."),
    ("📍 Spatial Survey Imbalance in GSI PDF", "Out of 9,970 GSI landslide records, 78% of dated entries came from Mizoram highway teams. We mitigated this by explicitly banning `state_name` from model inputs to prevent geographic bias exploitation."),
]

for idx, (title, desc) in enumerate(limitations):
    x = 0.5 + (idx % 2) * 6.3
    y = 1.5 + (idx // 2) * 2.7
    add_rect(s32, x, y, 6.0, 2.5, CARD_BG, border_color=ROSE, border_pt=1)
    add_text(s32, title, x+0.2, y+0.2, 5.6, 0.35, font_size=13, bold=True, color=ROSE)
    add_text(s32, desc, x+0.2, y+0.65, 5.6, 1.7, font_size=11, color=WHITE, line_spacing=16)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 33: CONCLUSION & FUTURE WORK
# ═══════════════════════════════════════════════════════════════════════════════
s33 = prs.slides.add_slide(BLANK)
set_bg(s33, DARK_BG)
add_header(s33, "Conclusion & Future Research Roadmap", "Transitioning from Academic Prototype to Operational Disaster Decision Support")

cards_s33 = [
    ("✅ WHAT WE ACHIEVED",
     "• Fully integrated 3-hazard prediction platform (Flood, Landslide, Wildfire).\n\n"
     "• Ingested 5 national/international datasets: NASA FIRMS, IMD, ERA5, GSI, INDOFLOODS.\n\n"
     "• 253,408 unique 1 km² grid cells with dual CRS projection (EPSG:32646).\n\n"
     "• HistGradientBoosting won all 3 hazards (Flood AUC 0.9557, Wildfire 0.9358, Landslide 0.9367).\n\n"
     "• Interactive browser dashboard running live on localhost:8000 with animated SVG gauge.", GREEN),
    ("🚀 FUTURE ENGINEERING ROADMAP",
     "• SAR InSAR Soil Deformation: Ingest Sentinel-1 synthetic aperture radar to detect millimeter-level slope creep before catastrophic landslides occur.\n\n"
     "• Real-Time IoT River Gauge Telemetry: Connect edge ultrasonic water-level sensors via LoRaWAN / 4G for real-time calibration.\n\n"
     "• Deep Learning Spatiotemporal Ensembles: Replace tabular gradient boosters with ConvLSTM / Graph Neural Networks (GNNs) across river stream networks.\n\n"
     "• Automated SMS/WhatsApp CAP Early Warning Alerts for civil defence.", BLUE),
]

for i, (title, desc, col) in enumerate(cards_s33):
    x = 0.6 + i * 6.2
    add_rect(s33, x, 1.4, 5.9, 5.6, CARD_BG, border_color=col, border_pt=1.5)
    add_rect(s33, x, 1.4, 5.9, 0.45, col)
    add_text(s33, title, x+0.15, 1.48, 5.6, 0.35, font_size=13, bold=True, color=DARKTEXT)
    add_text(s33, desc, x+0.2, 2.05, 5.5, 4.8, font_size=12, color=WHITE, line_spacing=18)

# Save
prs.save(str(PPTX_OUT))
print(f"Presentation successfully created: {PPTX_OUT} ({len(prs.slides)} slides)")
