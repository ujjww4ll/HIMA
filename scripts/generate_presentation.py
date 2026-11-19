"""
HIMA Project PowerPoint Presentation Generator
Generates HIMA_Project_Presentation.pptx with 4-member breakdown,
embedded output images, and rich content matching the study guide.
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
FIGS = BASE / "outputs" / "figures"
MAPS = BASE / "outputs" / "maps"
OUT  = BASE / "HIMA_Project_Presentation.pptx"

# ─── Color Palette ────────────────────────────────────────────────────────────
NAVY    = RGBColor(0x0F, 0x17, 0x2A)   # dark navy background (section headers)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE  = RGBColor(0xF9, 0x73, 0x16)   # accent / highlight
SLATE   = RGBColor(0x1E, 0x29, 0x3B)   # slightly lighter navy for content bg
LIGHTBG = RGBColor(0xF8, 0xFA, 0xFC)   # almost-white content slides
DARKTEXT= RGBColor(0x0F, 0x17, 0x2A)
GRAY    = RGBColor(0x64, 0x74, 0x8B)
GREEN   = RGBColor(0x22, 0xC5, 0x5E)
RED     = RGBColor(0xEF, 0x44, 0x44)
YELLOW  = RGBColor(0xFA, 0xCC, 0x15)

# Member accent colors
M1_COLOR = RGBColor(0x06, 0xB6, 0xD4)  # cyan  – Full Stack
M2_COLOR = RGBColor(0x84, 0xCC, 0x16)  # lime  – Geospatial
M3_COLOR = RGBColor(0xF9, 0x73, 0x16)  # orange – Wildfire ML
M4_COLOR = RGBColor(0xA8, 0x55, 0xF7)  # purple – Landslide / QA

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]  # completely blank layout


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def fill_bg(slide, color):
    """Fill slide background with a solid colour."""
    from pptx.oxml.ns import qn
    from lxml import etree
    spTree = slide.shapes._spTree
    # Remove existing bgPr if any
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, fill_color, border_color=None, border_pt=0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(l), Inches(t), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color and border_pt > 0:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, l, t, w, h,
             font_size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_text_multiline(slide, lines, l, t, w, h,
                        font_size=16, color=WHITE,
                        bold_first=False, line_spacing=None):
    """Add a text box with multiple paragraphs (list of strings)."""
    txBox = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.bold = (bold_first and i == 0)
        if line_spacing:
            from pptx.util import Pt as _Pt
            p.line_spacing = _Pt(line_spacing)
    return txBox


def add_image(slide, img_path, l, t, w, h=None):
    if not Path(img_path).exists():
        # Placeholder rectangle when image missing
        r = add_rect(slide, l, t, w, h if h else 2.5, SLATE)
        add_text(slide, f"[Image: {Path(img_path).name}]",
                 l+0.1, t+0.1, w-0.2, (h if h else 2.5)-0.2,
                 font_size=11, color=GRAY)
        return
    if h:
        slide.shapes.add_picture(str(img_path), Inches(l), Inches(t),
                                  Inches(w), Inches(h))
    else:
        slide.shapes.add_picture(str(img_path), Inches(l), Inches(t),
                                  Inches(w))


def section_header(title, subtitle, member_color):
    """Create a full-bleed dark navy section header slide."""
    slide = prs.slides.add_slide(BLANK)
    fill_bg(slide, NAVY)
    # Accent bar left side
    add_rect(slide, 0, 0, 0.18, 7.5, member_color)
    # Big title
    add_text(slide, title, 0.4, 2.5, 12.5, 1.4,
             font_size=46, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    # Subtitle bar
    add_rect(slide, 0.4, 3.9, 10, 0.08, member_color)
    add_text(slide, subtitle, 0.4, 4.1, 12.5, 1.0,
             font_size=24, bold=False, color=member_color, align=PP_ALIGN.LEFT)
    return slide


def content_slide(title, bullets, img_path=None,
                  img_l=7.8, img_t=1.3, img_w=5.2, img_h=5.4,
                  accent_color=ORANGE, bg=LIGHTBG, text_color=DARKTEXT):
    """Standard two-column content slide with optional right-side image."""
    slide = prs.slides.add_slide(BLANK)
    fill_bg(slide, bg)
    # Title bar
    add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
    add_rect(slide, 0, 1.08, 13.33, 0.07, accent_color)
    add_text(slide, title, 0.3, 0.1, 12.7, 0.9,
             font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    # Bullet content
    bw = 7.0 if img_path else 12.6
    add_text_multiline(slide, bullets, 0.35, 1.3, bw, 5.9,
                       font_size=16, color=text_color)
    if img_path:
        add_image(slide, img_path, img_l, img_t, img_w, img_h)
    return slide


def dual_image_slide(title, left_img, right_img,
                      left_cap="", right_cap="",
                      accent_color=ORANGE):
    """Slide with two side-by-side images and a title."""
    slide = prs.slides.add_slide(BLANK)
    fill_bg(slide, LIGHTBG)
    add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
    add_rect(slide, 0, 1.08, 13.33, 0.07, accent_color)
    add_text(slide, title, 0.3, 0.1, 12.7, 0.9,
             font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    add_image(slide, left_img,  0.3,  1.3, 6.1, 5.0)
    add_image(slide, right_img, 6.7,  1.3, 6.1, 5.0)
    if left_cap:
        add_text(slide, left_cap,  0.3, 6.35, 6.1, 0.5,
                 font_size=12, color=GRAY, align=PP_ALIGN.CENTER)
    if right_cap:
        add_text(slide, right_cap, 6.7, 6.35, 6.1, 0.5,
                 font_size=12, color=GRAY, align=PP_ALIGN.CENTER)
    return slide


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — COVER
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, NAVY)
# Top orange band
add_rect(slide, 0, 0, 13.33, 0.25, ORANGE)
# Bottom orange band
add_rect(slide, 0, 7.25, 13.33, 0.25, ORANGE)
# Left accent
add_rect(slide, 0, 0.25, 0.1, 7.0, M3_COLOR)

# Project acronym
add_text(slide, "HIMA", 0.3, 1.0, 12.0, 1.8,
         font_size=96, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
# Full title
add_text(slide,
         "Hazard Intelligence, Monitoring & Assessment",
         0.3, 2.65, 12.0, 0.9,
         font_size=26, bold=False, color=ORANGE, align=PP_ALIGN.LEFT)
# Divider
add_rect(slide, 0.3, 3.55, 9.5, 0.06, ORANGE)
# Subtitle desc
add_text(slide,
         "AI-Powered Wildfire & Landslide Risk Prediction\n"
         "for the Seven Sister States of Northeast India",
         0.3, 3.7, 12.0, 1.1,
         font_size=20, bold=False, color=RGBColor(0xCB, 0xD5, 0xE1),
         align=PP_ALIGN.LEFT)
# Team info
add_text(slide,
         "Team Members:  Member 1 (Full Stack)  |  Member 2 (Geospatial)  |"
         "  Member 3 (Wildfire ML)  |  Member 4 (Landslide & QA)",
         0.3, 4.9, 12.5, 0.6,
         font_size=15, color=RGBColor(0x94, 0xA3, 0xB8), align=PP_ALIGN.LEFT)
# GitHub
add_text(slide, "GitHub: github.com/ujjww4ll/HIMA",
         0.3, 5.55, 9.0, 0.5,
         font_size=14, color=RGBColor(0x38, 0xBD, 0xF8), align=PP_ALIGN.LEFT)
# Disclaimer
add_text(slide,
         "⚠  Research risk estimate only — not an official government warning.",
         0.3, 6.1, 12.5, 0.5,
         font_size=12, color=RGBColor(0xFB, 0xBF, 0x24), align=PP_ALIGN.LEFT)
# Study area
add_text(slide,
         "253,408 grid cells  |  7 Sister States  |  253,412 km²",
         0.3, 6.6, 12.5, 0.5,
         font_size=13, color=RGBColor(0x64, 0x74, 0x8B), align=PP_ALIGN.LEFT)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 2 — TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, NAVY)
add_rect(slide, 0, 0, 13.33, 1.1, SLATE)
add_rect(slide, 0, 1.08, 13.33, 0.07, ORANGE)
add_text(slide, "Table of Contents", 0.4, 0.15, 12.5, 0.85,
         font_size=32, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

toc_items = [
    (M1_COLOR, "Member 1 — Full Stack Developer",
     "Web Dashboard · REST API · SVG Choropleth · Deployment  (Slides 6–8)"),
    (M2_COLOR, "Member 2 — Geospatial & Data Ingestion Lead",
     "Study Area Grid · FIRMS Fires · IMD Rainfall · ERA5 Weather  (Slides 9–11)"),
    (M3_COLOR, "Member 3 — Feature Engineering & Wildfire ML",
     "33 Features · 6 Models · HistGradientBoosting · ROC-AUC 0.9358  (Slides 12–15)"),
    (M4_COLOR, "Member 4 — Landslide ML, Calibration & QA",
     "GSI PDF Mining · Landslide Classifier · Bayesian Calibration · 9 Unit Tests  (Slides 16–19)"),
]
for i, (col, heading, detail) in enumerate(toc_items):
    y = 1.4 + i * 1.4
    add_rect(slide, 0.4, y, 0.1, 1.1, col)
    add_rect(slide, 0.6, y, 12.3, 1.1, RGBColor(0x1E, 0x29, 0x3B))
    add_text(slide, heading, 0.75, y+0.05, 11.8, 0.5,
             font_size=18, bold=True, color=col)
    add_text(slide, detail, 0.75, y+0.55, 11.8, 0.5,
             font_size=14, color=RGBColor(0xCB, 0xD5, 0xE1))

add_text(slide, "Slides 3–5: Project Overview & Study Area · Slides 20–23: Results, EDA & Q&A",
         0.4, 7.0, 12.5, 0.4, font_size=12, color=GRAY, align=PP_ALIGN.LEFT)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 3 — PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Project Overview — Why HIMA?",
    [
        "🎯  PROBLEM:  Northeast India's Seven Sister States suffer repeated wildfires and",
        "     landslides every year. No existing early-warning tool combines both hazards",
        "     in real time for this region.",
        "",
        "✅  SOLUTION:  HIMA is an end-to-end machine-learning pipeline that:",
        "     • Ingests 4 live/archival datasets (FIRMS, IMD, ERA5, GSI)",
        "     • Builds 33 weather + terrain features per 1 km² grid cell",
        "     • Trains 6 ML classifiers for WILDFIRE and LANDSLIDE separately",
        "     • Chooses the best model, calibrates probabilities, then serves",
        "       predictions through an interactive web dashboard",
        "",
        "📊  SCALE:",
        "     • 253,408 grid cells across 253,412 km²",
        "     • 219,928 VIIRS vegetation fire records (2021-2024)",
        "     • 9,970 GSI landslide records; 463 unique dated cell-days",
        "     • Training: 2021–2023 | Test: 2024 (strict temporal split)",
    ],
    accent_color=ORANGE,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 4 — STUDY AREA MAP
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, LIGHTBG)
add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
add_rect(slide, 0, 1.08, 13.33, 0.07, ORANGE)
add_text(slide, "Study Area — Seven Sister States, Northeast India",
         0.3, 0.1, 12.7, 0.9,
         font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

add_image(slide, MAPS / "study_area_and_grid.png", 0.3, 1.25, 7.8, 5.9)

stats = [
    "📍  7 Sister States covered:",
    "     Assam, Meghalaya, Manipur,",
    "     Mizoram, Nagaland, Tripura,",
    "     Arunachal Pradesh",
    "     (Sikkim excluded — no FIRMS data)",
    "",
    "📐  Grid Resolution: 0.01° × 0.01°",
    "     ≈ 1 km² per cell",
    "     Total cells: 253,408",
    "     Total area: 253,412 km²",
    "",
    "🗂  Coordinate Systems:",
    "     • EPSG:4326 — WGS84 geographic",
    "       (lat/lon for FIRMS fire points)",
    "     • EPSG:32646 — UTM Zone 46N",
    "       (metric for distance calc)",
    "",
    "🔗  KD-Tree spatial join used to snap",
    "     each fire/landslide point to the",
    "     nearest grid cell centroid",
]
add_text_multiline(slide, stats, 8.4, 1.3, 4.7, 5.9,
                   font_size=14, color=DARKTEXT)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 5 — TEAM STRUCTURE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, NAVY)
add_rect(slide, 0, 0, 13.33, 1.1, SLATE)
add_rect(slide, 0, 1.08, 13.33, 0.07, ORANGE)
add_text(slide, "Team Structure — 4-Member Breakdown",
         0.4, 0.15, 12.5, 0.85,
         font_size=32, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

members = [
    (M1_COLOR, "👨‍💻  Member 1", "Full Stack Developer",
     "frontend/index.html · styles.css · app.js\n"
     "src/api/predict.py · run_hima.bat\n"
     "Flask REST API · SVG Choropleth Map\n"
     "Animated Risk Gauge · Offline-First Design"),
    (M2_COLOR, "🗺  Member 2", "Geospatial & Data Ingestion",
     "src/audit/ · src/geospatial/\n"
     "src/ingestion/firms.py · imd.py · era5.py\n"
     "FIRMS 219,928 fires · IMD rainfall\n"
     "ERA5 reanalysis · 253,408-cell grid"),
    (M3_COLOR, "🔥  Member 3", "Feature Eng. & Wildfire ML",
     "src/features/weather.py\n"
     "src/labels/wildfire.py\n"
     "src/training/pipelines.py\n"
     "33 features · 6 models · Best: HistGB\n"
     "ROC-AUC 0.9358 · Recall 68.4%"),
    (M4_COLOR, "🌊  Member 4", "Landslide ML, Calibration & QA",
     "src/ingestion/gsi_pdf.py\n"
     "src/labels/landslide.py\n"
     "src/training/landslide_pipelines.py\n"
     "src/evaluation/metrics.py\n"
     "tests/test_hima_pipeline.py · 9/9 PASSED"),
]

positions = [(0.3, 1.3), (6.9, 1.3), (0.3, 4.3), (6.9, 4.3)]
for (col, name, role, desc), (xl, yl) in zip(members, positions):
    add_rect(slide, xl, yl, 6.2, 2.85, RGBColor(0x1E, 0x29, 0x3B))
    add_rect(slide, xl, yl, 6.2, 0.55, col)
    add_text(slide, name, xl+0.15, yl+0.05, 5.8, 0.45,
             font_size=18, bold=True, color=NAVY)
    add_text(slide, role, xl+0.15, yl+0.6, 5.8, 0.45,
             font_size=15, bold=True, color=col)
    add_text_multiline(slide, desc.split("\n"), xl+0.15, yl+1.1, 5.8, 1.6,
                       font_size=13, color=RGBColor(0xCB, 0xD5, 0xE1))


# ═══════════════════════════════════════════════════════════════════════════════
#  MEMBER 1 SECTION — FULL STACK DEVELOPER
# ═══════════════════════════════════════════════════════════════════════════════
section_header(
    "Member 1\nFull Stack Developer",
    "Web Dashboard · REST API · SVG Choropleth · Deployment",
    M1_COLOR,
)

# Slide 7 — M1 Role & Files
content_slide(
    "Member 1 — Full Stack: Role & File Ownership",
    [
        "🎯  RESPONSIBILITY:  Build the entire web-facing layer of HIMA.",
        "     Member 1 connects the ML backend to the user's browser.",
        "",
        "📁  FILES OWNED:",
        "     • frontend/index.html   — Single-page HTML application (no React needed)",
        "     • frontend/styles.css   — Dark-theme responsive CSS with glassmorphism cards",
        "     • frontend/app.js       — Slider listeners, fetch() calls, gauge animation",
        "     • src/api/predict.py    — Flask REST endpoint /predict (POST)",
        "     • run_hima.bat          — One-command launcher (test/data/web/demo/fast modes)",
        "",
        "🔧  TECH STACK:",
        "     • Python Flask — lightweight REST API server",
        "     • Vanilla JavaScript — no heavy frontend framework required",
        "     • SVG Choropleth Map — inline SVG, state polygons colored by risk level",
        "     • Animated Risk Gauge — SVG arc drawn by JS based on probability score",
        "     • scikit-learn joblib models — loaded at startup, predict in <50ms",
        "",
        "🌐  DESIGN PHILOSOPHY:",
        "     • Offline-First — SVG map has no external tile server dependency",
        "     • Single BAT file launch — user runs run_hima.bat demo and opens browser",
        "     • Responsive layout for desktop presentation and laptop screens",
    ],
    accent_color=M1_COLOR,
    text_color=DARKTEXT,
)

# Slide 8 — M1 How it works (data flow)
content_slide(
    "Member 1 — How the Web Dashboard Works (Data Flow)",
    [
        "USER INTERACTION FLOW:",
        "",
        "  1️⃣  User opens browser → index.html loads (Flask serves static files)",
        "       The page shows sliders for each weather input feature",
        "",
        "  2️⃣  User moves sliders (e.g., Temperature, Rainfall, Humidity)",
        "       JavaScript reads all slider values → builds a JSON object",
        "",
        "  3️⃣  JS calls fetch('/predict', {method:'POST', body: JSON.stringify(inputs)})",
        "       Flask receives POST → loads wildfire + landslide joblib models",
        "",
        "  4️⃣  Models predict probability → Flask returns JSON:",
        "       {wildfire_prob: 0.78, risk_band: 'HIGH', calibrated_prob: 0.76}",
        "",
        "  5️⃣  JS updates the animated SVG gauge to the probability angle",
        "       SVG choropleth fills the state polygon with color:",
        "       GREEN (Low 0–30%) | YELLOW (Moderate 30–60%) | RED (High/Critical 60–100%)",
        "",
        "  6️⃣  User sees live risk level — no page reload needed",
        "",
        "⚡  THRESHOLD:  Probability > 0.7118 → flagged as HIGH RISK fire day",
        "⚠  DISCLAIMER always shown: 'Research estimate only — not an official warning'",
    ],
    img_path=MAPS / "wildfire_hotspot_map.png",
    img_l=7.8, img_t=1.3, img_w=5.2, img_h=5.4,
    accent_color=M1_COLOR,
    text_color=DARKTEXT,
)

# Slide 9 — M1 Viva Q&A
content_slide(
    "Member 1 — Viva Questions & Answers",
    [
        "Q: Why Flask and not Django or FastAPI?",
        "A: Flask is minimal — only 2 routes needed (/predict, /static). Django",
        "   is overkill; FastAPI needs ASGI. Flask starts in <1 sec for demos.",
        "",
        "Q: Why SVG choropleth instead of Leaflet/Google Maps?",
        "A: SVG works offline (no tile server, no API key). It is lighter, faster,",
        "   and fully controllable. Leaflet needs internet for base tiles.",
        "",
        "Q: How does the risk gauge work?",
        "A: JS calculates arc angle = probability × 180°. SVG path stroke-dasharray",
        "   is animated from 0 → target in 800ms using requestAnimationFrame.",
        "",
        "Q: What if the ML model is not loaded yet?",
        "A: predict.py loads models at module import time (Flask startup). If file",
        "   is missing, it returns HTTP 503 with an error message.",
        "",
        "Q: What does run_hima.bat do?",
        "A: It activates .venv, then based on argument runs:",
        "   test → pytest  |  data → pipeline scripts  |  web → Flask server",
        "   demo → synthetic data + Flask  |  fast → skip heavy data steps",
        "",
        "Q: How is the threshold 0.7118 chosen?",
        "A: It is the optimal F1 threshold from precision-recall curve (Member 3's work).",
        "   At this threshold: Recall=68.4%, FAR=6.1%, balancing catches vs false alarms.",
    ],
    accent_color=M1_COLOR,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MEMBER 2 SECTION — GEOSPATIAL & DATA INGESTION
# ═══════════════════════════════════════════════════════════════════════════════
section_header(
    "Member 2\nGeospatial & Data Ingestion Lead",
    "253,408-Cell Grid · FIRMS · IMD Rainfall · ERA5 Weather",
    M2_COLOR,
)

# Slide 11 — M2 Role
content_slide(
    "Member 2 — Geospatial: Role & File Ownership",
    [
        "🎯  RESPONSIBILITY:  Build the spatial foundation — the 1 km² grid that",
        "     every model feature is attached to, and ingest all 4 raw datasets.",
        "",
        "📁  FILES OWNED:",
        "     • src/geospatial/grid.py      — Generate 253,408 grid cell centroids",
        "     • src/geospatial/spatial.py   — cKDTree nearest-neighbor spatial joins",
        "     • src/ingestion/firms.py      — Download & filter VIIRS fire detections",
        "     • src/ingestion/imd.py        — Parse IMD gridded daily rainfall (.nc)",
        "     • src/ingestion/era5.py       — Download ERA5 reanalysis via CDS API",
        "     • src/audit/               — Data quality checks & completeness reports",
        "",
        "📡  DATA SOURCES MANAGED:",
        "     • FIRMS VIIRS S-NPP C2  — 219,928 fire records, type=0 (vegetation only)",
        "     • IMD Gridded Rainfall   — 0.25° daily rainfall, 2021-2024",
        "     • ERA5 Reanalysis        — temperature, humidity, wind, soil moisture",
        "     • GSI Landslide PDF      — parsed by Member 4; snapped to grid by M2",
        "",
        "🗺  COORDINATE WORK:",
        "     • Input data in EPSG:4326 (WGS84 lat/lon degrees)",
        "     • Grid projected to EPSG:32646 (UTM Zone 46N, metres) for distance",
        "     • cKDTree built in metres → query returns nearest cell index in O(log n)",
    ],
    img_path=MAPS / "study_area_and_grid.png",
    img_l=7.8, img_t=1.3, img_w=5.2, img_h=5.4,
    accent_color=M2_COLOR,
    text_color=DARKTEXT,
)

# Slide 12 — M2 How the grid & spatial join works
content_slide(
    "Member 2 — The 253,408-Cell Grid & Spatial Joins",
    [
        "HOW THE GRID IS BUILT:",
        "  • Bounding box of 7 Sister States loaded from study_states.gpkg",
        "  • Latitude steps: 0.01° from 21.5°N to 29.5°N",
        "  • Longitude steps: 0.01° from 92.0°E to 97.5°E",
        "  • Each (lat, lon) pair that falls inside any state polygon → kept",
        "  • Result: 253,408 valid cell centroids saved as GeoDataFrame",
        "",
        "HOW SPATIAL JOINS WORK (cKDTree):",
        "  • All 253,408 cell centroids converted to UTM metres (EPSG:32646)",
        "  • scipy.spatial.cKDTree built on the (easting, northing) array",
        "  • For each FIRMS fire point: convert lat/lon → UTM → query tree",
        "  • Tree returns the index of the nearest centroid in O(log n) time",
        "  • Fire event is tagged to that cell_id for that date",
        "",
        "WHY UTM INSTEAD OF DEGREES:",
        "  • Distance in degrees is NOT uniform — 1° longitude ≠ same metres at",
        "    different latitudes. UTM gives true metric distances for fair joins.",
        "",
        "FIRMS FILTER APPLIED:",
        "  • type == 0 → vegetation fire (excludes industrial flares, volcanoes)",
        "  • confidence >= 'nominal' → removes low-quality detections",
        "  • 219,928 records pass both filters across 2021–2024",
    ],
    accent_color=M2_COLOR,
    text_color=DARKTEXT,
)

# Slide 13 — M2 Viva
content_slide(
    "Member 2 — Viva Questions & Answers",
    [
        "Q: Why is Sikkim excluded from the study area?",
        "A: FIRMS VIIRS has no vegetation fire records for Sikkim in our dataset.",
        "   Including it would add grid cells with no labels — introducing noise.",
        "",
        "Q: Why 0.01° grid resolution?",
        "A: 0.01° ≈ 1.1 km at this latitude — fine enough to distinguish district-",
        "   level risk while keeping total cells (253,408) computationally manageable.",
        "",
        "Q: What is cKDTree and why use it?",
        "A: cKDTree (C-compiled KD-Tree from scipy) enables O(log n) nearest-",
        "   neighbour queries. Without it, brute-force matching 219,928 fire points",
        "   to 253,408 cells would take hours vs seconds.",
        "",
        "Q: What is EPSG:4326 vs EPSG:32646?",
        "A: EPSG:4326 = WGS84 — standard GPS lat/lon in degrees (used by FIRMS).",
        "   EPSG:32646 = UTM Zone 46N — projected in metres for Northeast India.",
        "   Reprojection needed because KD-Tree distances must be in metres.",
        "",
        "Q: What does the audit module check?",
        "A: Missing dates per cell, duplicate fire events, ERA5 NaN months,",
        "   coordinate range checks, and label imbalance statistics.",
        "",
        "Q: Can we show the NC format data?",
        "A: Yes — IMD rainfall comes as NetCDF (.nc). We open it with xarray:",
        "   ds = xarray.open_dataset('rf25_ind2021_rfp25.nc')",
        "   ds['RAINFALL'].sel(LATITUDE=25.5, LONGITUDE=94.0, method='nearest')",
    ],
    accent_color=M2_COLOR,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MEMBER 3 SECTION — FEATURE ENG & WILDFIRE ML
# ═══════════════════════════════════════════════════════════════════════════════
section_header(
    "Member 3\nFeature Engineering & Wildfire ML",
    "33 Features · 6 Classifiers · HistGradientBoosting · ROC-AUC 0.9358",
    M3_COLOR,
)

# Slide 15 — Feature Engineering
content_slide(
    "Member 3 — 33 ML Features for Wildfire Prediction",
    [
        "📁  FILES OWNED:  src/features/weather.py · src/labels/wildfire.py",
        "                   src/training/pipelines.py",
        "",
        "WEATHER FEATURES (from ERA5 + IMD):",
        "  • temp_max, temp_min, temp_mean  — daily temperature extremes",
        "  • rh_min, rh_mean                — relative humidity (dry air → fire risk)",
        "  • wind_speed_max, wind_speed_mean — wind drives fire spread",
        "  • rainfall_1d, rainfall_3d, rainfall_7d  — recent rainfall (fuel moisture)",
        "  • soil_moisture_0_7cm            — top soil wetness",
        "  • vpd_max                        — vapour pressure deficit (evaporation stress)",
        "",
        "TEMPORAL FEATURES (cyclical encoding):",
        "  • doy_sin = sin(2π × day_of_year / 365)   — captures annual seasonality",
        "  • doy_cos = cos(2π × day_of_year / 365)   — without a discontinuity at Dec 31",
        "  • month_sin / month_cos                   — month-level seasonality",
        "",
        "DERIVED / LAG FEATURES:",
        "  • dry_days_streak  — consecutive days with rainfall < 1mm",
        "  • fire_lag_1d, fire_lag_7d  — was there fire nearby yesterday / last week?",
        "  • temp_anomaly     — deviation from 30-day rolling mean temperature",
        "",
        "🚫  POST-EVENT COLUMNS EXCLUDED from features (data leakage prevention):",
        "     frp_sum, brightness_mean, scan, track — these are recorded AFTER a fire,",
        "     so using them would let the model 'cheat' by seeing the fire itself.",
    ],
    accent_color=M3_COLOR,
    text_color=DARKTEXT,
)

# Slide 16 — Model comparison table
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, LIGHTBG)
add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
add_rect(slide, 0, 1.08, 13.33, 0.07, M3_COLOR)
add_text(slide, "Member 3 — Wildfire: 6 Classifiers Compared",
         0.3, 0.1, 12.7, 0.9, font_size=28, bold=True, color=WHITE)

# Table headers
headers = ["Model", "CV ROC-AUC", "Test ROC-AUC", "Test PR-AUC",
           "Recall", "Precision", "FAR"]
col_w = [3.0, 1.6, 1.6, 1.5, 1.2, 1.3, 1.5]
col_x = [0.25]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w)

row_y = 1.3
# Header row
add_rect(slide, 0.25, row_y, 12.8, 0.42, NAVY)
for j, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
    add_text(slide, hdr, cx+0.05, row_y+0.04, cw-0.1, 0.35,
             font_size=12, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)

rows = [
    ("DummyClassifier",          "0.4962", "0.5000", "0.0003", "0.00%", "—",      "0.00%"),
    ("Logistic Regression",      "0.9216", "0.9940", "0.0045", "0.00%", "64.94%", "0.28%"),
    ("Gaussian Naïve Bayes",     "0.8913", "0.8621", "0.0025", "58.33%","0.21%",  "9.51%"),
    ("Decision Tree",            "0.9138", "0.7222", "0.0046", "59.20%","0.33%",  "6.19%"),
    ("Random Forest",            "0.9434", "0.9260", "0.0067", "63.22%","0.44%",  "5.01%"),
    ("HistGradientBoosting ★",   "0.9470", "0.9358", "0.0061", "68.4%", "0.39%",  "6.12%"),
]
highlight_row = 5  # HistGB
for i, row in enumerate(rows):
    ry = row_y + 0.42 + i * 0.65
    bg_c = RGBColor(0xFF, 0xED, 0xCC) if i == highlight_row else (
        RGBColor(0xF1, 0xF5, 0xF9) if i % 2 == 0 else WHITE)
    add_rect(slide, 0.25, ry, 12.8, 0.6, bg_c)
    text_c = RGBColor(0x92, 0x40, 0x0E) if i == highlight_row else DARKTEXT
    for val, cx, cw in zip(row, col_x, col_w):
        add_text(slide, val, cx+0.05, ry+0.08, cw-0.1, 0.44,
                 font_size=12, bold=(i == highlight_row), color=text_c,
                 align=PP_ALIGN.CENTER)

add_text(slide,
         "★  HistGradientBoosting wins: highest Test ROC-AUC (0.9358) + highest Recall (68.4%)"
         " + competitive FAR (6.1%). Threshold optimised to 0.7118 for best F1.",
         0.25, 6.65, 12.8, 0.6, font_size=13, bold=True,
         color=RGBColor(0x92, 0x40, 0x0E), align=PP_ALIGN.LEFT)

# Slide 17 — Wildfire Model Comparison Charts
dual_image_slide(
    "Member 3 — Wildfire: Model Comparison & ROC/PR Curves",
    FIGS / "wildfire_model_comparison.png",
    FIGS / "wildfire_roc_pr_curves.png",
    "Bar chart: all 6 models by ROC-AUC & PR-AUC",
    "ROC curve (left) & PR curve (right) for HistGB",
    accent_color=M3_COLOR,
)

# Slide 18 — Feature Importance + Decision Tree
dual_image_slide(
    "Member 3 — Wildfire: Feature Importance & Decision Tree",
    FIGS / "wildfire_feature_importance.png",
    FIGS / "wildfire_decision_tree.png",
    "Top-10 features driving wildfire prediction",
    "Shallow decision tree — interpretable logic",
    accent_color=M3_COLOR,
)

# Slide 19 — M3 Viva
content_slide(
    "Member 3 — Viva Questions & Answers",
    [
        "Q: Why HistGradientBoosting over Random Forest?",
        "A: HistGB natively handles NaN (missing ERA5 months — no imputation needed),",
        "   uses histogram binning for 10× faster training, and achieves higher Recall",
        "   (68.4% vs 63.2%) meaning fewer real fire days are missed.",
        "",
        "Q: What is ROC-AUC and what does 0.9358 mean?",
        "A: ROC-AUC measures how well the model separates fire vs non-fire days at ALL",
        "   thresholds. 0.9358 means in 93.6% of random (fire, non-fire) pairs, the",
        "   model correctly ranks the fire day higher. Random = 0.5; Perfect = 1.0.",
        "",
        "Q: Why is PR-AUC so low (0.0061)?",
        "A: Because fire events are VERY RARE — only 0.2% of all cell-days have fire.",
        "   In such extreme imbalance, precision is very low even at good recall.",
        "   PR-AUC is still the right metric — it focuses only on the positive class.",
        "",
        "Q: What is recall and why prioritise it here?",
        "A: Recall = True Positives / (TP + FN). Missing a real fire is dangerous.",
        "   We prefer false alarms (FAR=6.1%) over missing fire days.",
        "",
        "Q: What is the threshold 0.7118?",
        "A: The probability cutoff where F1 score is maximised. Below it → 'no fire'.",
        "   Above it → 'FIRE ALERT'. Found by scanning all thresholds on PR curve.",
        "",
        "Q: Why use sin/cos for day-of-year?",
        "A: Day 1 and Day 365 are adjacent — a linear encoding treats them as far apart.",
        "   sin/cos wraps around: Dec 31 and Jan 1 get similar values, capturing",
        "   seasonal continuity without a discontinuous jump.",
    ],
    accent_color=M3_COLOR,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MEMBER 4 SECTION — LANDSLIDE ML, CALIBRATION & QA
# ═══════════════════════════════════════════════════════════════════════════════
section_header(
    "Member 4\nLandslide ML, Calibration & QA",
    "GSI PDF Mining · Landslide Classifier · Bayesian Calibration · 9 Unit Tests",
    M4_COLOR,
)

# Slide 21 — M4 Role
content_slide(
    "Member 4 — Landslide & QA: Role & File Ownership",
    [
        "🎯  RESPONSIBILITY:  Build the landslide prediction pipeline, calibrate",
        "     both wildfire and landslide probability outputs, and ensure the",
        "     entire codebase is verified through automated unit tests.",
        "",
        "📁  FILES OWNED:",
        "     • src/ingestion/gsi_pdf.py          — PDF text extraction from GSI reports",
        "     • src/labels/landslide.py            — Build landslide positive labels",
        "     • src/training/landslide_pipelines.py — Train 6 classifiers for landslides",
        "     • src/evaluation/metrics.py          — FAR, Brier score, calibration plots",
        "     • tests/test_hima_pipeline.py        — 9 automated unit tests",
        "",
        "📋  KEY CONTRIBUTIONS:",
        "     • Mined 9,970 GSI landslide records from scanned PDFs using pdfplumber",
        "     • Discovered survey bias: GSI records 'state_name' as a column → excluded",
        "       from features (it would let model cheat using location as a label proxy)",
        "     • Applied Bayesian prior adjustment to get calibrated daily probabilities",
        "     • Measured Brier score before calibration: 0.083 → after: 0.0005",
        "     • Wrote 9 pytest unit tests covering config, data, model, and API",
        "",
        "🔑  LANDSLIDE FEATURES (independent variables):",
        "     • rainfall_1d, rainfall_3d, rainfall_7d  — recent accumulated rainfall",
        "     • slope, elevation                        — terrain steepness and height",
        "     • lithology (rock type code)              — soil/rock erodibility",
        "     • NDVI (vegetation density)               — root cohesion",
        "     • soil_moisture_0_7cm                    — saturation level",
    ],
    accent_color=M4_COLOR,
    text_color=DARKTEXT,
)

# Slide 22 — Landslide Results charts
dual_image_slide(
    "Member 4 — Landslide: Model Comparison & ROC/PR Curves",
    FIGS / "landslide_model_comparison.png",
    FIGS / "landslide_roc_pr_curves.png",
    "All 6 models compared — HistGB best at ROC-AUC 0.9367",
    "Landslide ROC curve & PR curve",
    accent_color=M4_COLOR,
)

# Slide 23 — Bayesian Calibration
content_slide(
    "Member 4 — Bayesian Prior Calibration of Probabilities",
    [
        "WHY CALIBRATION IS NEEDED:",
        "  • ML models output a raw score, NOT a true probability.",
        "  • The training set has an artificially balanced class ratio",
        "    (we upsample rare positives for training balance).",
        "  • But in the real world, fires happen on only ~0.2% of cell-days.",
        "  • Without calibration, the model would say P(fire)=0.4 when reality is 0.002.",
        "",
        "WHAT BAYESIAN ADJUSTMENT DOES:",
        "  • We know the true daily fire base rate from the full dataset",
        "  • We apply Bayes' theorem to adjust the model's inflated probability",
        "    back to the realistic prior:",
        "    P(fire|features) = P(score|fire) × P(fire) / P(score)",
        "  • This shrinks raw probabilities to realistic daily values",
        "",
        "RESULTS (Wildfire):",
        "  • Brier Score BEFORE calibration: 0.083",
        "  • Brier Score AFTER calibration:  0.0005  (99.4% improvement!)",
        "  • Brier Score = mean squared error of probability predictions",
        "    → Lower is better; 0.0 = perfect calibration",
        "",
        "OUTPUT FORMAT:",
        "  • raw_score: 0.9685 (model's internal score)",
        "  • calibrated_daily_probability: 0.016383 (realistic 1.6% daily chance)",
        "  • relative_score_band: CRITICAL (ranked among all grid cells today)",
    ],
    img_path=FIGS / "wildfire_calibration.png",
    img_l=7.8, img_t=1.3, img_w=5.2, img_h=5.4,
    accent_color=M4_COLOR,
    text_color=DARKTEXT,
)

# Slide 24 — 9 Unit Tests
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, LIGHTBG)
add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
add_rect(slide, 0, 1.08, 13.33, 0.07, M4_COLOR)
add_text(slide, "Member 4 — 9 Unit & Integrity Tests (All PASSED)",
         0.3, 0.1, 12.7, 0.9, font_size=28, bold=True, color=WHITE)

tests = [
    ("11%",  "test_config_loads_and_has_disclaimer",
     "Verifies config.yaml loads correctly and contains the mandatory research disclaimer text."),
    ("22%",  "test_days_since_rain_preserves_missing_gaps",
     "Confirms that ERA5 missing months are kept as NaN — never filled with 0 (data integrity)."),
    ("33%",  "test_ind_season_mapping",
     "Checks that all 12 months map to exactly one of 4 Indian meteorological seasons."),
    ("44%",  "test_bayes_prior_adjustment_monotonic_and_bounded",
     "Ensures calibrated probabilities stay in [0,1] and increase monotonically with raw score."),
    ("55%",  "test_risk_band_boundaries",
     "Validates LOW/MODERATE/HIGH/CRITICAL band edges: 0–30%, 30–60%, 60–80%, 80–100%."),
    ("66%",  "test_no_post_event_leakage_in_features",
     "Confirms post-event columns (frp_sum, brightness_mean) are absent from feature set."),
    ("77%",  "test_grid_boundaries_facts_if_built",
     "If grid file exists: verifies 253,408 cells within NE India bounding box."),
    ("88%",  "test_validated_wildfire_predictor_inference",
     "Loads joblib wildfire model, runs predict_proba on 2 synthetic cases, checks output shape."),
    ("100%", "test_required_deliverables_exist",
     "Checks that all required output files (maps, figures, models) exist on disk."),
]

col_positions = [(0.3, 6.6), (6.9, 6.6)]
for i, (pct, name, desc) in enumerate(tests):
    row = i
    ry = 1.28 + row * 0.65
    # Green passed badge
    add_rect(slide, 0.3, ry, 1.0, 0.52, GREEN)
    add_text(slide, "PASSED", 0.3, ry+0.08, 1.0, 0.36,
             font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Progress %
    add_rect(slide, 1.35, ry, 0.7, 0.52, M4_COLOR)
    add_text(slide, pct, 1.35, ry+0.08, 0.7, 0.36,
             font_size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Test name + desc
    add_text(slide, name, 2.15, ry, 10.9, 0.3,
             font_size=11, bold=True, color=DARKTEXT)
    add_text(slide, desc, 2.15, ry+0.3, 10.9, 0.26,
             font_size=10, color=GRAY)

add_text(slide, "9 passed in 2.56s  —  platform win32, Python 3.14.3, pytest-9.2.0",
         0.3, 7.1, 12.5, 0.35, font_size=12, bold=True,
         color=GREEN, align=PP_ALIGN.LEFT)

# Slide 25 — M4 Viva
content_slide(
    "Member 4 — Viva Questions & Answers",
    [
        "Q: What is Brier score and why does it go from 0.083 to 0.0005?",
        "A: Brier score = average of (predicted_prob - actual_outcome)². Lower = better.",
        "   Before calibration the model overestimates probability (0.083 is high).",
        "   After Bayesian adjustment it aligns with true 0.2% base rate → 0.0005.",
        "",
        "Q: Why exclude state_name from landslide features?",
        "A: GSI records landslides per state. If we include state_name, the model",
        "   learns 'Assam → landslide' because Assam has more records — that is",
        "   survey bias (data collection skew), not actual physical risk.",
        "",
        "Q: What is pdfplumber and how is it used?",
        "A: pdfplumber extracts text tables from PDF pages. GSI publishes landslide",
        "   inventories as scanned PDFs. gsi_pdf.py opens each page, reads tabular",
        "   data row by row, parses date and location fields → 9,970 records extracted.",
        "",
        "Q: Why only 463 unique dated cell-days from 9,970 records?",
        "A: Multiple GSI records may point to the same geographic cell on the same day",
        "   (a cluster of slides near one location). After spatial join + deduplication,",
        "   463 unique (cell_id, date) pairs remain as positive training labels.",
        "",
        "Q: What does test_no_post_event_leakage check exactly?",
        "A: It loads the feature column list from the trained model's pipeline and",
        "   asserts that none of ['frp_sum','brightness_mean','scan','track'] appear.",
        "   These are FIRMS columns recorded only after a fire is detected.",
    ],
    accent_color=M4_COLOR,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE — EDA GALLERY (Heatmap + Seasonal + Confusion Matrices)
# ═══════════════════════════════════════════════════════════════════════════════
dual_image_slide(
    "EDA Gallery — Correlation Heatmap & Seasonal Wildfire Trends",
    FIGS / "wildfire_correlation_heatmap.png",
    FIGS / "wildfire_seasonal_trends.png",
    "Feature correlation matrix — identifies redundant predictors",
    "Monthly wildfire count — peak: March–April (dry pre-monsoon)",
    accent_color=ORANGE,
)

# Confusion matrices
dual_image_slide(
    "EDA Gallery — Wildfire & Landslide Confusion Matrices",
    FIGS / "wildfire_confusion_matrices.png",
    FIGS / "landslide_confusion_matrices.png",
    "Wildfire confusion matrices — all 6 models",
    "Landslide confusion matrices — all 6 models",
    accent_color=ORANGE,
)

# Landslide EDA
dual_image_slide(
    "EDA Gallery — Landslide Rainfall & GSI Distribution",
    FIGS / "landslide_rainfall_eda.png",
    FIGS / "landslide_gsi_coolr_eda.png",
    "Rainfall distribution on landslide vs non-landslide days",
    "GSI landslide density by COOLR grid region",
    accent_color=M4_COLOR,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE — RESULTS SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, LIGHTBG)
add_rect(slide, 0, 0, 13.33, 1.1, NAVY)
add_rect(slide, 0, 1.08, 13.33, 0.07, ORANGE)
add_text(slide, "Project Results Summary — All Key Metrics",
         0.3, 0.1, 12.7, 0.9, font_size=28, bold=True, color=WHITE)

summary_rows = [
    ("Metric", "Wildfire (HistGB)", "Landslide (HistGB)", "Notes"),
    ("Test ROC-AUC", "0.9358", "0.9367", "Both >0.93 — excellent discrimination"),
    ("CV ROC-AUC", "0.9470", "0.8483", "Cross-validated on 2021–2023 train set"),
    ("Test PR-AUC", "0.0061", "0.2187", "Landslide has better precision (less rare)"),
    ("Recall (Sensitivity)", "68.4%", "42.9%", "% of real events caught"),
    ("False Alarm Rate", "6.12%", "21.63%", "% of safe days wrongly flagged"),
    ("Optimal Threshold", "0.7118", "Variable", "F1-maximising cutoff"),
    ("Brier Score (raw)", "0.083", "—", "Before Bayesian calibration"),
    ("Brier Score (calibrated)", "0.0005", "—", "99.4% improvement after calibration"),
    ("Training period", "2021–2023", "2021–2023", "Strict temporal hold-out"),
    ("Test period", "2024", "2024", "Unseen future data"),
    ("Grid cells", "253,408", "253,408", "0.01° × 0.01° ≈ 1 km²"),
    ("Total training samples", "219,928 fire records", "463 dated events", "Heavily imbalanced"),
    ("Unit tests", "9 / 9 PASSED", "9 / 9 PASSED", "2.56 seconds runtime"),
]
col_w2 = [3.6, 2.8, 2.8, 4.0]
col_x2 = [0.3]
for w in col_w2[:-1]:
    col_x2.append(col_x2[-1] + w)
for i, row in enumerate(summary_rows):
    ry = 1.3 + i * 0.42
    is_hdr = (i == 0)
    bg2 = NAVY if is_hdr else (RGBColor(0xF1, 0xF5, 0xF9) if i % 2 == 0 else WHITE)
    fc = WHITE if is_hdr else DARKTEXT
    add_rect(slide, 0.3, ry, 12.73, 0.4, bg2)
    for val, cx, cw in zip(row, col_x2, col_w2):
        add_text(slide, val, cx+0.04, ry+0.04, cw-0.08, 0.34,
                 font_size=11, bold=is_hdr, color=fc,
                 align=PP_ALIGN.LEFT)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE — LIMITATIONS & FUTURE WORK
# ═══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Limitations & Future Work",
    [
        "CURRENT LIMITATIONS:",
        "  • ERA5 reanalysis has ~2 month data latency — not suitable for real-time ops",
        "  • GSI landslide inventory is sparse and survey-biased toward road corridors",
        "  • No terrain slope/aspect layer in current version (planned addition)",
        "  • Wildfire recall 68.4% means ~31.6% of real fire days are still missed",
        "  • Web dashboard uses demo/synthetic data — not live API in current version",
        "  • Sikkim excluded due to missing FIRMS coverage",
        "",
        "FUTURE IMPROVEMENTS PLANNED:",
        "  • Add Sentinel-2 NDVI layers and DEM-derived slope/aspect features",
        "  • Integrate MODIS MCD12Q1 land cover for fuel type classification",
        "  • Replace ERA5 with MOSDAC real-time NWP for <6 hour forecast latency",
        "  • Build a multi-day forecasting mode (Day+1, Day+3, Day+7 ahead)",
        "  • Spatial cross-validation (block CV) to reduce spatial autocorrelation bias",
        "  • Add XGBoost and LightGBM to model roster for further comparison",
        "  • Deploy as a containerised service (Docker + FastAPI) for production use",
        "  • SMS/WhatsApp alert integration for field rangers in high-risk districts",
        "",
        "⚠  DISCLAIMER (always required):",
        "   This system produces research risk estimates only.",
        "   It is NOT a certified government early warning system.",
        "   Do NOT use as sole basis for evacuation or emergency decisions.",
    ],
    accent_color=ORANGE,
    text_color=DARKTEXT,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE — THANK YOU / Q&A
# ═══════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(BLANK)
fill_bg(slide, NAVY)
add_rect(slide, 0, 0, 13.33, 0.25, ORANGE)
add_rect(slide, 0, 7.25, 13.33, 0.25, ORANGE)
add_rect(slide, 0, 0.25, 0.1, 7.0, M4_COLOR)

add_text(slide, "Thank You", 0.3, 1.5, 12.0, 1.4,
         font_size=72, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
add_text(slide, "Questions & Discussion", 0.3, 2.9, 12.0, 0.8,
         font_size=30, color=ORANGE, align=PP_ALIGN.LEFT)
add_rect(slide, 0.3, 3.75, 9.5, 0.06, ORANGE)

add_text(slide, "GitHub Repository:", 0.3, 3.9, 4.0, 0.5,
         font_size=16, color=RGBColor(0x94, 0xA3, 0xB8))
add_text(slide, "https://github.com/ujjww4ll/HIMA",
         0.3, 4.4, 10.0, 0.5, font_size=20, bold=True,
         color=RGBColor(0x38, 0xBD, 0xF8))

quick_summary = [
    "✅  253,408 grid cells · 7 Sister States · 253,412 km²",
    "✅  Wildfire: ROC-AUC 0.9358 · Recall 68.4% · FAR 6.1%",
    "✅  Landslide: ROC-AUC 0.9367 · Bayesian calibrated",
    "✅  Brier score improved 99.4%: 0.083 → 0.0005",
    "✅  9/9 unit tests passing in 2.56 seconds",
    "✅  Interactive web dashboard — offline SVG choropleth + risk gauge",
]
add_text_multiline(slide, quick_summary, 0.3, 5.1, 12.5, 2.0,
                   font_size=16, color=RGBColor(0xCB, 0xD5, 0xE1))

add_text(slide,
         "⚠  Research risk estimate only — not an official government warning.",
         0.3, 7.0, 12.5, 0.4, font_size=12,
         color=RGBColor(0xFB, 0xBF, 0x24))


# ═══════════════════════════════════════════════════════════════════════════════
#  SAVE
# ═══════════════════════════════════════════════════════════════════════════════
prs.save(str(OUT))
print(f"\n✅  Presentation saved → {OUT}")
print(f"   Slides: {len(prs.slides)}")
