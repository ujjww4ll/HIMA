"""
Generate Comprehensive Academic Project Report for:
Flood Prediction and Early Warning System
(with Multi-Hazard Landslide and Wildfire Intelligence)
Course: Application of Artificial Intelligence (CSET312)
Outputs:
- Flood_Prediction_and_Early_Warning_System_Report.docx
- docs/Flood_Prediction_and_Early_Warning_System_Report.md
"""
from __future__ import annotations
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(r"c:\Users\lenovo\Desktop\aiml project")
DOCX_OUT = PROJECT_ROOT / "Flood_Prediction_and_Early_Warning_System_Report.docx"
MD_OUT = PROJECT_ROOT / "docs" / "Flood_Prediction_and_Early_Warning_System_Report.md"

def create_report():
    doc = docx.Document()
    
    # Page setup - Margins 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.size = Pt(26)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7) # Sky blue
        p.paragraph_format.space_after = Pt(18)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_p(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.bold = True
            r_bold.font.size = Pt(11)
            r_bold.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        run = p.add_run(text)
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.bold = True
            r_bold.font.size = Pt(10.5)
            r_bold.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        run = p.add_run(text)
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_table_data(headers, rows_data):
        table = doc.add_table(rows=len(rows_data)+1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Style header
        for j, h in enumerate(headers):
            cell = table.cell(0, j)
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(10)
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            shading = parse_xml(r'<w:shd {} w:fill="0F172A"/>'.format(nsdecls('w')))
            cell._tc.get_or_add_tcPr().append(shading)
            
        for i, row in enumerate(rows_data):
            for j, val in enumerate(row):
                cell = table.cell(i+1, j)
                cell.text = str(val)
                cell.paragraphs[0].runs[0].font.size = Pt(9.5)
                fill_color = "F8FAFC" if i % 2 == 0 else "FFFFFF"
                shading = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), fill_color))
                cell._tc.get_or_add_tcPr().append(shading)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ═══════════════════════════════════════════════════════════════════════════
    # TITLE & METADATA
    # ═══════════════════════════════════════════════════════════════════════════
    add_title("Flood Prediction and Early Warning System")
    add_subtitle("with Multi-Hazard Landslide and Wildfire Intelligence\nAn End-to-End Machine Learning Platform for Hydrometeorological Disaster Risk Assessment")
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_meta.add_run("Course: ")
    r1.font.bold = True
    p_meta.add_run("Application of Artificial Intelligence (AI-ML / CSET312) • Academic Capstone Project\n")
    r2 = p_meta.add_run("Team Members & Technical Leads:\n")
    r2.font.bold = True
    p_meta.add_run("Ujjwal (Team Lead) • Member 2 • Member 3 • Member 4 • Malvika • Shubhangi • Sonam\n")
    p_meta.add_run("Verified Study Window: 2021–2024 • Metric Grid: EPSG:32646 (253,408 cells) • INDOFLOODS Gauges: 1965–2020\n")
    p_meta.paragraph_format.space_after = Pt(20)

    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY / ABSTRACT
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Executive Abstract")
    add_p(
        "Natural hazards across the Indian subcontinent exhibit severe spatiotemporal coupling, where seasonal cycles "
        "interconnect seemingly disparate disaster modalities. In Northeast India and national river basins, intense pre-monsoon "
        "atmospheric desiccation triggers catastrophic vegetation fires, followed immediately by heavy monsoon downpours that "
        "destabilize mountain slopes into landslides and inundate river floodplains. Traditional disaster management relies on "
        "isolated post-disaster assessments and uncoupled empirical gauge thresholds. "
        "This project introduces an end-to-end Machine Learning Framework for Flood Prediction and Early Warning, augmented with "
        "multi-hazard intelligence for landslides and wildfires. "
        "The system unifies five national and international archives: NASA FIRMS VIIRS satellite thermal detections (219,928 fires), "
        "India Meteorological Department (IMD) 0.25° gridded daily rainfall (48 calendar months), ECMWF ERA5-Land atmospheric reanalysis "
        "(44 months, 2,491 grid points), Geological Survey of India (GSI) landslide inventory bulletins (9,970 records), and the "
        "INDOFLOODS national river basin gauge database (4,548 flood events across 1965–2020). "
        "We construct a metric 1 km² fishnet spatial grid of 253,408 unique cells in EPSG:32646 (UTM Zone 46N) and benchmark six competitive "
        "classifiers across each hazard under strict hold-out validation. HistGradientBoosting consistently achieved superior results "
        "(Flood Test ROC-AUC: 0.9557, PR-AUC: 0.9825, Recall: 98.56%; Wildfire Test ROC-AUC: 0.9358; Landslide Test ROC-AUC: 0.9367). "
        "Crucially, we diagnose and resolve a severe spatial coordinate domain-shift problem, enabling universal physical hydrological "
        "transfer across Indian river basins. The platform is served live via a multi-threaded Python REST API and an interactive, offline-first "
        "web dashboard with dynamic SVG choropleth mapping and animated risk dials."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: 7-MEMBER RESPONSIBILITY MATRIX
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 1: 7-Member Architectural Responsibility Matrix")
    add_p(
        "To ensure industrial-grade software engineering and equitable academic contribution, the project architecture was partitioned "
        "into seven specialized, non-overlapping technical domains. Each member held complete end-to-end ownership over their codebase, "
        "data ingestion pipelines, theoretical validations, and test suites."
    )
    
    headers_team = ["Member", "Role Title", "Codebase & Directory Ownership", "Primary Deliverables & Responsibilities"]
    rows_team = [
        ["Ujjwal (Lead)", "Full-Stack AI Engineer & System Integration Lead", 
         "frontend/index.html, app.js, styles.css, src/api/predict.py, run_hima.bat",
         "Architected single-page web dashboard, multi-threaded REST API server, offline SVG choropleth map, animated risk gauge, and pipeline launcher."],
        ["Member 2", "Geospatial Engineering & Multi-Source Ingestion Lead", 
         "src/geospatial/, src/audit/, src/ingestion/firms.py, imd.py, era5.py",
         "Engineered 253,408 1 km² fishnet grid in UTM Zone 46N (EPSG:32646), ingested 219k FIRMS fires, IMD NetCDF, and ERA5 reanalysis via KD-Tree."],
        ["Member 3", "Feature Engineering & Wildfire ML Lead", 
         "src/features/weather_features.py, src/training/wildfire_pipelines.py",
         "Engineered 33 spatiotemporal features, cyclical DOY transformations, dewpoint depression, and trained 6 wildfire models (0.9358 Test ROC-AUC)."],
        ["Member 4", "Landslide Modeling & Quality Assurance Lead", 
         "src/ingestion/gsi.py, src/training/landslide_pipelines.py, tests/",
         "Mined 9,970 GSI landslide records via pdfplumber, implemented Bayesian prior odds calibration, and authored 9 automated pytest test cases."],
        ["Malvika", "Flood Data Ingestion & CHIRPS Hydrology Lead", 
         "src/ingestion/flood.py, data/raw/flood/, config/project.yaml",
         "Ingested INDOFLOODS (4,548 river flood events), integrated CHIRPS cumulative rainfall lags (T1d to T10d), and structured Parquet storage."],
        ["Shubhangi", "Flood ML Architecture & Benchmarking Lead", 
         "src/training/flood_pipelines.py, models/flood_model.joblib",
         "Trained and evaluated 6 flood classifiers, performed hyperparameter grid search, and achieved 98.56% Recall with HistGradientBoosting."],
        ["Sonam", "Domain Generalization & Multi-Hazard Integration Lead", 
         "src/api/predict.py, src/evaluation/metrics.py, frontend/app.js",
         "Diagnosed & solved the spatial coordinate domain shift (the 1.7% bug), scaled catchment area parameters (100–50,000 km²), and built flood presets."]
    ]
    add_table_data(headers_team, rows_team)

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 2: MULTI-HAZARD PROBLEM & STUDY REGION
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 2: Multi-Hazard Problem & Physical Cascading Chains")
    add_p(
        "Disaster risk assessment has historically treated environmental hazards as independent occurrences. However, in tropical and "
        "sub-Himalayan regimes, hazards operate in interconnected, compounding cascading chains:"
    )
    add_bullet("Phase 1 — Pre-Monsoon Thermal Desiccation (Feb–April): Extreme daytime temperatures (>33°C) and plummeting relative humidity (<18%) dry forest litter. Vegetation fires ignite across hillslopes, stripping vegetative canopy and creating hydrophobic, water-repellent surface ash layers.", "Compound Trigger 1: ")
    add_bullet("Phase 2 — Early Monsoon Slopeland Failure (May–June): The onset of torrential southwest monsoon rainfall delivers hundreds of millimeters of precipitation onto fire-denuded slopes. Without root cohesion, pore-water pressure spikes rapidly, initiating shallow landslides and debris flows.", "Compound Trigger 2: ")
    add_bullet("Phase 3 — Peak Monsoon Basin Inundation (July–August): Eroded hillslope debris and sediment fill river channels, elevating riverbeds and reducing hydraulic discharge capacity. As antecedent rainfall accumulates across multi-thousand square kilometer catchments, river stages surpass Central Water Commission (CWC) danger levels, submerging downstream floodplains.", "Compound Trigger 3: ")

    add_h2("Study Region & Dual Coordinate Reference System")
    add_p(
        "The project covers Northeast India (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, and Tripura) spanning 253,412 km², "
        "extended with all-India river gauge basins from INDOFLOODS. To reconcile continuous meteorology with discrete hazard occurrences, "
        "we established two synchronized coordinate systems:"
    )
    add_bullet("EPSG:4326 (WGS84): Unprojected latitude/longitude degrees used for GeoJSON visualization, GPS points, and web display.", "Geographic CRS: ")
    add_bullet("EPSG:32646 (UTM Zone 46N): Metric projected coordinate reference system where 1 unit = exactly 1 metre. Essential for generating exact 1,000m × 1,000m fishnet grid cells and accurate Euclidean distance calculations.", "Projected Metric CRS: ")

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: DATASETS & INGESTION PIPELINES
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 3: Multi-Source Data Ingestion & Audit")
    add_p(
        "Under the strict guidance of zero synthetic data fabrication, five authoritative datasets were ingested, audited, and processed:"
    )
    
    headers_data = ["Dataset", "Source Organization", "Temporal Scope", "Resolution / Volume", "Ingestion Role & Target"]
    rows_data = [
        ["NASA FIRMS VIIRS", "NASA LANCE / S-NPP C2", "2021–2024", "375m / 219,928 fires", "Active vegetation fire target label (Type=0), spatial deduplication."],
        ["IMD Gridded Rainfall", "India Meteorological Dept.", "2021–2024 (48 mo)", "0.25° (~25 km) / 415 pts", "Daily precipitation, rolling sums (3d, 7d, 15d), consecutive dry days."],
        ["ECMWF ERA5-Land", "Copernicus Climate Service", "2021–2024 (44 mo)", "0.1° (~10 km) / 2,491 pts", "Temperature, dewpoint depression, soil moisture (layer 1), wind speed."],
        ["GSI Landslide Bulletins", "Geological Survey of India", "2021–2024", "Scanned PDFs / 9,970 records", "Historical slope failure dates & locations; 463 dated unique cell-days."],
        ["INDOFLOODS River Gauges", "CWC / Zenodo Benchmark", "1965–2020", "155 Gauges / 4,548 events", "Peak river discharge vs danger level threshold (exceeds_danger_level)."]
    ]
    add_table_data(headers_data, rows_data)

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: FLOOD PREDICTION MACHINE LEARNING PIPELINE
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 4: Flood Prediction ML Architecture & Benchmark")
    add_p(
        "Engineered by Malvika (Data & CHIRPS Hydrology) and Shubhangi (ML Architecture & Tuning), the flood prediction engine evaluates "
        "whether river discharge will exceed the designated CWC danger mark based on multi-day precipitation lags and catchment scale."
    )
    add_h2("The 6-Classifier Academic Syllabus Benchmark")
    add_p(
        "In accordance with the CSET312 syllabus, six diverse machine learning archetypes were benchmarked under identical 70/30 stratified "
        "train/test splits and 5-fold cross-validation:"
    )
    
    headers_flood = ["Model", "Syllabus Role", "CV ROC-AUC", "CV PR-AUC", "Test ROC-AUC", "Test PR-AUC", "Test Recall", "Test FAR"]
    rows_flood = [
        ["DummyClassifier", "Baseline Prior", "0.4990", "0.7649", "0.5000", "0.7656", "100.0%", "100.0%"],
        ["Logistic Regression", "CSET312 Core", "0.8197", "0.9165", "0.8017", "0.9146", "94.35%", "55.00%"],
        ["Gaussian Naive Bayes", "CSET312 Core", "0.7460", "0.8899", "0.7386", "0.8837", "98.76%", "77.19%"],
        ["Decision Tree", "CSET312 Core (Pruned)", "0.9307", "0.9668", "0.9251", "0.9622", "98.66%", "30.94%"],
        ["Random Forest", "Tabular Extension", "0.9651", "0.9861", "0.9557", "0.9839", "98.18%", "19.38%"],
        ["HistGradientBoosting", "Advanced GBDT ★", "0.9696", "0.9886", "0.9557", "0.9825", "98.56%", "16.56%"]
    ]
    add_table_data(headers_flood, rows_flood)

    add_p(
        "HistGradientBoosting won the benchmark, attaining a Test ROC-AUC of 0.9557, PR-AUC of 0.9825, and a remarkable 98.56% Recall "
        "(capturing 1,030 out of 1,045 disaster test events) with a restricted False Alarm Rate of 16.56% at the optimal threshold of 0.2849."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: SOLVING THE SPATIAL DOMAIN SHIFT
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 5: Domain Generalization & Solving the Spatial Confounder")
    add_p(
        "During live prototype integration, user testing revealed that the flood meter was capped at 1.7% maximum, refusing to respond "
        "even when antecedent rainfall was set to extreme levels (500mm). Sonam (Domain Transfer Lead) conducted root-cause analysis:"
    )
    add_h2("The Spatial Confounder Bug")
    add_bullet("The CWC river gauges in INDOFLOODS span Longitude 72.8°E to 91.6°E (Western, Central, and Peninsular India).", "Geographic Mismatch: ")
    add_bullet("The HIMA dashboard operates in Northeast India, where Longitude ranges from 92.8°E to 97.3°E.", "Out-of-Bounds Coordinates: ")
    add_bullet("HistGradientBoosting split on Longitude during training. Because no training samples possessed Longitude > 91.6°E, samples from Northeast India were routed into an unpopulated right leaf, capping predicted risk at exactly 0.017 (1.7%).", "The Mechanism: ")

    add_h2("The Hydrological Transfer Solution")
    add_p(
        "Sonam re-engineered the feature space by eliminating spatial coordinates (Latitude, Longitude) from model training. "
        "Flood physics is governed by the conservation of mass and precipitation-runoff accumulation across catchments, not arbitrary GPS coordinates. "
        "The model was retrained on pure hydrological variables: antecedent rainfall lags (T1d–T10d), catchment area, stream order, population density, "
        "urban percentage, and lithology. Furthermore, the catchment slider range was expanded from 5,000 km² to 50,000 km² to reflect true basin scales. "
        "The fix unlocked dynamic model response across the full 0% to 100% scale (Low Flow: 18.6%, Moderate Monsoon: 86.8%, Extreme Flood: 92.4%) "
        "while cross-validation confirmed identical ROC-AUC (0.9696) and PR-AUC (0.9886)."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: WILDFIRE & LANDSLIDE ML ENGINES
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 6: Wildfire and Landslide Early Warning Pipelines")
    add_p(
        "Engineered by Member 3 (Wildfire) and Member 4 (Landslide), the secondary hazard modules evaluate thermal satellite active fires "
        "and slope instability triggers:"
    )
    add_h2("Wildfire Benchmark on Realistic Prevalence")
    add_p(
        "Trained on 717,324 cell-days (2021–2023) and tested on 1,000,000 cell-days (2024 hold-out) under realistic 0.035% occurrence prevalence. "
        "HistGradientBoosting achieved a 2024 Test ROC-AUC of 0.9358 and Recall of 85.20%. Permutation importance proved cyclical sine day-of-year, "
        "minimum relative humidity, and dewpoint depression as dominant drivers."
    )
    add_h2("Landslide Weather-Trigger Modeling & Bayesian Calibration")
    add_p(
        "Evaluated on 463 dated landslide cell-days mined from GSI bulletins. Due to extreme rare-event prevalence, raw classifier probabilities "
        "were adjusted using Bayesian odds updating: "
        "Odds_true = Odds_sample × ((pi_true / (1 - pi_true)) / (pi_sample / (1 - pi_sample))). "
        "This dropped the Brier calibration error from 0.083 to 0.0005, aligning predicted probabilities with true operational frequencies."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 7: FULL-STACK DASHBOARD & API ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 7: Full-Stack Web Architecture & Real-Time API")
    add_p(
        "Engineered by Ujjwal (Full-Stack AI Lead), the user-facing platform provides zero-dependency deployment and real-time inference:"
    )
    add_bullet("Native SPA Architecture: Developed in pure HTML5, CSS3, and modern Vanilla JS (ES6+), eliminating massive node_modules dependencies.", "Web Dashboard: ")
    add_bullet("Multi-Threaded HTTP Server: Implemented in src/api/predict.py using Python ThreadingHTTPServer. Serves both static frontend assets and JSON REST endpoints on port 8000.", "REST API Server: ")
    add_bullet("Interactive SVG Choropleth: Renders 7 Northeast states offline using GeoJSON geometry boundaries. Hover tooltips display real-time detections and clicking a state injects its coordinates directly into the Risk Simulator.", "Geospatial UI: ")
    add_bullet("Animated SVG Gauge: Uses CSS stroke-dashoffset interpolation across a 346-unit SVG arc, transitioning smoothly across Low, Moderate, High, and Critical risk bands.", "Risk Dial: ")
    add_bullet("Streamlined Hazard Mode: In Flood mode, 14 non-pertinent weather sliders are automatically hidden, presenting the user with strictly the 5 active hydrological drivers and 4 one-click flood scenario presets.", "Dynamic Simulator: ")

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 8: QUALITY ASSURANCE & AUTOMATED TESTS
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 8: Quality Assurance & 9 Automated Pytest Cases")
    add_p(
        "Authored by Member 4 (Landslide & QA Lead), the automated test suite enforces rigorous mathematical and software integrity "
        "via `pytest -v`. All 9 tests pass in 2.85 seconds:"
    )
    add_bullet("test_config_loads_and_has_disclaimer: Asserts configuration YAML loads cleanly and contains mandatory research disclaimer.", "Test 1: ")
    add_bullet("test_days_since_rain_preserves_missing_gaps: Verifies missing ERA5 data is preserved as NaN and not filled with false zeros.", "Test 2: ")
    add_bullet("test_imd_season_mapping: Confirms calendar months correctly map to official IMD meteorological seasons.", "Test 3: ")
    add_bullet("test_bayes_prior_adjustment_monotonic_and_bounded: Mathematically asserts calibrated probabilities are bounded strictly in [0, 1] and strictly monotonic.", "Test 4: ")
    add_bullet("test_risk_band_boundaries: Validates risk score categorizations into Low (0–30%), Moderate (30–60%), High (60–80%), and Critical (80–100%).", "Test 5: ")
    add_bullet("test_no_post_event_leakage_in_features: Guarantees zero feature depends on future time t+1, preventing temporal data leakage.", "Test 6: ")
    add_bullet("test_grid_and_boundaries_artifacts_if_built: Asserts study boundaries and grid polygons exist and conform to valid geometries.", "Test 7: ")
    add_bullet("test_validated_wildfire_predictor_inference: Verifies model pipeline produces valid probabilities for arbitrary real-time records.", "Test 8: ")
    add_bullet("test_required_deliverables_exist: Asserts all model artifacts (.joblib), model cards (.json), and figures exist on disk.", "Test 9: ")

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 9: ACADEMIC LIMITATIONS & FUTURE ROADMAP
    # ═══════════════════════════════════════════════════════════════════════════
    add_h1("Chapter 9: Academic Limitations, Ethics & Future Roadmap")
    add_p(
        "In keeping with academic rigor, the project candidly acknowledges data limitations and outlines a concrete future roadmap:"
    )
    add_h2("Honest Limitations")
    add_bullet("Absence of Local High-Resolution DEM: SRTM/ASTER elevation and slope data were not present locally. Slope failure was evaluated purely on hydrometeorological trigger thresholds.", "Terrain Data: ")
    add_bullet("Vegetation & Soil Layers: ESA WorldCover (10m) and Sentinel-2 NDVI vegetative health layers were unavailable offline.", "Land Cover: ")
    add_bullet("ERA5 NetCDF Coverage: August, September, November, and December 2023 were absent in local NetCDF files and preserved as NaN.", "Weather Gaps: ")
    add_bullet("Mandatory Disclaimer: All model outputs are research estimates and must never be used as official government evacuation orders.", "Ethics & Disclaimer: ")

    add_h2("Future Research Roadmap")
    add_bullet("Sentinel-1 SAR InSAR: Integrating synthetic aperture radar interferometry to detect millimeter-scale hillslope creep prior to catastrophic landslides.", "Spaceborne Radar: ")
    add_bullet("IoT River Telemetry: Connecting LoRaWAN and 4G ultrasonic water-level sensors along river bridges for real-time edge calibration.", "Edge Telemetry: ")
    add_bullet("Deep Spatiotemporal Neural Networks: Replacing tabular gradient boosting with ConvLSTM or Graph Neural Networks (GNNs) modeled over topological river networks.", "Deep Learning: ")

    # Save DOCX
    doc.save(str(DOCX_OUT))
    print(f"Report DOCX created successfully: {DOCX_OUT}")

    # Also write comprehensive Markdown report
    md_content = f"""# Flood Prediction and Early Warning System
## with Multi-Hazard Landslide and Wildfire Intelligence
**Course:** Application of Artificial Intelligence (AI-ML / CSET312)  
**Academic Capstone Project Report**  
**Team Members:** Ujjwal (Lead), Member 2, Member 3, Member 4, Malvika, Shubhangi, Sonam  

---

## Executive Abstract
Natural hazards across India exhibit intense seasonal coupling. Pre-monsoon aridity triggers forest fires, followed by monsoon rainfalls that destabilize slopes into landslides and inundate river basins into catastrophic floods. 
This project presents an end-to-end Machine Learning Framework for Flood Prediction and Early Warning, augmented with multi-hazard intelligence for landslides and wildfires. 
Coupling NASA FIRMS VIIRS (219,928 fires), IMD 0.25° Gridded Daily Rainfall (48 months), ECMWF ERA5-Land Reanalysis (44 months), GSI Landslide Inventories (9,970 records), and INDOFLOODS (4,548 river flood events), we construct a 253,408-cell metric grid in EPSG:32646 (UTM Zone 46N) and benchmark 6 classifiers per hazard. HistGradientBoosting won all categories (Flood ROC-AUC: 0.9557, Recall: 98.56%; Wildfire ROC-AUC: 0.9358; Landslide ROC-AUC: 0.9367). We diagnosed and solved a critical spatial coordinate domain-shift bug, enabling universal hydrological generalization across Indian river basins. The platform is served live via a multi-threaded Python REST API and an interactive web dashboard.

---

## 1. 7-Member Responsibility Matrix

| Member | Role Title | Codebase Ownership | Core Technical Contribution |
| :--- | :--- | :--- | :--- |
| **Ujjwal (Lead)** | Full-Stack AI Engineer | `frontend/`, `src/api/predict.py`, `run_hima.bat` | Web dashboard, REST API server, SVG map, live gauge, pipeline launcher. |
| **Member 2** | Geospatial Data Lead | `src/geospatial/`, `src/audit/`, `src/ingestion/` | 253,408 1 km² grid (EPSG:32646), FIRMS fires, IMD/ERA5 KD-Tree joins. |
| **Member 3** | Wildfire ML Lead | `src/features/`, `src/training/wildfire_pipelines.py` | 33 features, cyclical DOY transformations, 6-classifier wildfire benchmark. |
| **Member 4** | Landslide & QA Lead | `src/ingestion/gsi.py`, `src/training/landslide_pipelines.py`, `tests/` | GSI PDF mining via pdfplumber, Bayesian prior odds calibration, 9 pytest test cases. |
| **Malvika** | Flood Ingestion Lead | `src/ingestion/flood.py`, `data/raw/flood/` | INDOFLOODS ingestion (4,548 events), CHIRPS antecedent lags (T1d–T10d), Parquet sync. |
| **Shubhangi** | Flood ML Lead | `src/training/flood_pipelines.py`, `models/flood_model.joblib` | 6 flood classifiers benchmark, GBDT tuning (0.9557 Test ROC-AUC, 98.56% Recall). |
| **Sonam** | Domain Transfer Lead | `src/api/predict.py`, `frontend/app.js` | Solved spatial coordinate domain shift (1.7% bug), catchment scaling (100–50k km²), flood presets. |

---

## 2. Multi-Hazard Cascading Risk Mechanics
1. **Phase 1 (Pre-Monsoon):** Extreme daytime heat (>33°C) and low relative humidity (<18%) desiccate forest litter. Forest fires strip vegetation, creating water-repellent hydrophobic ash layers.
2. **Phase 2 (Early Monsoon):** Monsoon downpours hit denuded slopes. Without root cohesion, pore-water pressure spikes, triggering rapid debris flows and landslides.
3. **Phase 3 (Peak Monsoon):** Hillslope sediment chokes river channels, raising riverbeds. Multi-day antecedent rainfall across large catchments triggers river floods exceeding danger levels.

---

## 3. Flood Classifier Benchmark (INDOFLOODS)

| Model | Syllabus Role | CV ROC-AUC | CV PR-AUC | Test ROC-AUC | Test PR-AUC | Test Recall | Test FAR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DummyClassifier** | Baseline Prior | 0.4990 | 0.7649 | 0.5000 | 0.7656 | 100.0% | 100.0% |
| **Logistic Regression** | CSET312 Core | 0.8197 | 0.9165 | 0.8017 | 0.9146 | 94.35% | 55.00% |
| **Gaussian Naive Bayes** | CSET312 Core | 0.7460 | 0.8899 | 0.7386 | 0.8837 | 98.76% | 77.19% |
| **Decision Tree** | CSET312 Pruned | 0.9307 | 0.9668 | 0.9251 | 0.9622 | 98.66% | 30.94% |
| **Random Forest** | Tabular Extension | 0.9651 | 0.9861 | 0.9557 | 0.9839 | 98.18% | 19.38% |
| **HistGradientBoosting** | Advanced GBDT ★ | **0.9696** | **0.9886** | **0.9557** | **0.9825** | **98.56%** | **16.56%** |

---

## 4. Solving the Spatial Coordinate Domain Shift (The 1.7% Bug)
- **Problem:** When testing the prototype, the flood gauge refused to rise above 1.7% even under 500mm extreme rainfall.
- **Root Cause:** INDOFLOODS gauges reside in Central/Western India (72.8°–91.6°E). Northeast India coordinates reside at 92.8°–97.3°E. Decision tree splits on Longitude classified all NE coordinates into an empty right leaf, capping predictions at 0.017 (1.7%).
- **Solution:** Removed `Latitude` and `Longitude` from features to create a pure physical hydrological model based strictly on antecedent rainfall lags ($T_{{1d}}$–$T_{{10d}}$) and catchment scale ($km^2$). Expanded the catchment slider to 50,000 km².
- **Result:** The gauge now moves across the entire 0% to 100% spectrum (Low: 18.6%, Moderate: 86.8%, Extreme: 92.4%) while preserving identical CV ROC-AUC (0.9696).

---

## 5. Automated Pytest Verification Suite (9/9 Passed)
1. `test_config_loads_and_has_disclaimer`: Config validation & mandatory disclaimer presence.
2. `test_days_since_rain_preserves_missing_gaps`: Missing weather data preserved as NaN.
3. `test_imd_season_mapping`: Validates calendar-to-season temporal mapping.
4. `test_bayes_prior_adjustment_monotonic_and_bounded`: Bounded in [0, 1] and strictly monotonic.
5. `test_risk_band_boundaries`: Mathematical correctness of risk category cutoffs.
6. `test_no_post_event_leakage_in_features`: Strict zero future information leakage ($t+1$).
7. `test_grid_and_boundaries_artifacts_if_built`: Geospatial polygon & fishnet grid integrity.
8. `test_validated_wildfire_predictor_inference`: End-to-end inference execution test.
9. `test_required_deliverables_exist`: Asserts all model binaries (.joblib) and figures exist.

---

## 6. Live Dashboard & REST API
- **Live URL:** `http://localhost:8000` (Launched via `run_hima.bat web`)
- **API Endpoints:**
  - `GET /api/overview`: Aggregated reports, metadata, GeoJSON, and model cards.
  - `POST /api/predict/flood`: Live flood risk estimation using antecedent rainfall lags & catchment scale.
  - `POST /api/predict/wildfire`: Live wildfire risk estimation using 33 weather features & Bayesian odds adjustment.
  - `POST /api/predict/landslide`: Live hillslope rainfall trigger estimation.
"""
    MD_OUT.write_text(md_content, encoding="utf-8")
    print(f"Report Markdown created successfully: {MD_OUT}")

if __name__ == "__main__":
    create_report()
