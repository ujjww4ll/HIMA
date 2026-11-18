"""Generate HIMA Complete Project Study Guide and Viva Preparation PDF.

Creates an exhaustive, publication-grade study guide covering:
- Executive Summary & Project Architecture
- 4-Member Team Breakdown (Full Stack + 3 Data Science Specialists) with individual contributions, explanations, speeches, and member-specific viva Q&A
- Detailed breakdown of all 9 automated test cases (what they test, why they matter, how they pass)
- Dependent vs Independent Variables
- Deep-dive into every single factor and slider in the dashboard
- All 6 ML classifiers explained + mathematical formulation + why HistGradientBoosting won
- Comprehensive project-wide viva question bank with model answers
"""

from pathlib import Path
import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "HIMA_Project_Study_Guide_and_Viva_Prep.pdf"

CSS = """
@page {
    margin: 32pt 36pt 36pt 36pt;
}
body {
    font-family: helvetica, sans-serif;
    font-size: 9pt;
    line-height: 1.42;
    color: #1e293b;
}
.header-box {
    background-color: #0f172a;
    color: #ffffff;
    padding: 14pt 18pt;
    border-radius: 6pt;
    margin-bottom: 12pt;
}
.header-box h1 {
    font-size: 19pt;
    margin: 0 0 4pt 0;
    color: #f97316;
    letter-spacing: -0.5pt;
}
.header-box .sub {
    font-size: 9.5pt;
    color: #94a3b8;
    margin: 0;
}
.member-card {
    background-color: #f8fafc;
    border: 1pt solid #cbd5e1;
    border-top: 3pt solid #0284c7;
    border-radius: 4pt;
    padding: 10pt 12pt;
    margin-bottom: 14pt;
}
.member-title {
    font-size: 12pt;
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 4pt;
}
.member-role {
    font-size: 9pt;
    font-weight: bold;
    color: #0284c7;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    margin-bottom: 6pt;
}
h2 {
    color: #0f172a;
    font-size: 12.5pt;
    border-bottom: 2pt solid #e2e8f0;
    padding-bottom: 3pt;
    margin-top: 16pt;
    margin-bottom: 8pt;
}
h3 {
    color: #0369a1;
    font-size: 10.5pt;
    margin-top: 10pt;
    margin-bottom: 4pt;
}
h4 {
    color: #334155;
    font-size: 9pt;
    margin-top: 8pt;
    margin-bottom: 2pt;
}
p {
    margin: 0 0 5pt 0;
}
ul, ol {
    margin: 0 0 6pt 16pt;
    padding: 0;
}
li {
    margin-bottom: 2.5pt;
}
.callout {
    background-color: #f8fafc;
    border-left: 3pt solid #3b82f6;
    padding: 6pt 10pt;
    margin: 6pt 0;
    border-radius: 0 4pt 4pt 0;
}
.callout-warn {
    background-color: #fffbeb;
    border-left: 3pt solid #f59e0b;
    padding: 6pt 10pt;
    margin: 6pt 0;
    border-radius: 0 4pt 4pt 0;
}
.callout-success {
    background-color: #f0fdf4;
    border-left: 3pt solid #22c55e;
    padding: 6pt 10pt;
    margin: 6pt 0;
    border-radius: 0 4pt 4pt 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 6pt 0 10pt 0;
    font-size: 8pt;
}
th, td {
    border: 1pt solid #cbd5e1;
    padding: 4pt 5pt;
    text-align: left;
    vertical-align: top;
}
th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
.formula {
    background-color: #f1f5f9;
    padding: 3pt 6pt;
    border-radius: 3pt;
    font-family: courier, monospace;
    font-size: 8pt;
    color: #0f172a;
    display: inline-block;
    margin: 2pt 0;
}
.qa-box {
    background-color: #f8fafc;
    border: 1pt solid #e2e8f0;
    border-radius: 4pt;
    padding: 6pt 8pt;
    margin-bottom: 8pt;
}
.qa-q {
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 3pt;
}
.qa-a {
    color: #334155;
}
.test-box {
    background-color: #ffffff;
    border: 1pt solid #cbd5e1;
    border-left: 3pt solid #10b981;
    border-radius: 3pt;
    padding: 6pt 8pt;
    margin-bottom: 6pt;
}
.test-title {
    font-weight: bold;
    color: #0f172a;
    font-family: courier, monospace;
    font-size: 8.5pt;
}
"""

HTML_CONTENT = r"""
<div class="header-box">
    <h1>HIMA Project Study Guide &amp; Comprehensive Viva Prep</h1>
    <p class="sub"><b>Hazard Intelligence, Monitoring &amp; Assessment (Northeast India)</b> &bull; B.Tech Capstone (CSET312 AI-ML)</p>
    <p style="margin-top: 4pt; font-size: 8pt; color: #cbd5e1;">GitHub Repository: https://github.com/ujjww4ll/HIMA &bull; Framework: Python, scikit-learn, GeoPandas, PyMuPDF &bull; Team: 4 Members (1 Full Stack + 3 Data Science)</p>
</div>

<div class="callout-warn">
    <b>Mandatory Academic Disclaimer:</b> Research risk estimate only &mdash; not an official operational warning. All predictions represent academic statistical simulations across Northeast India.
</div>

<h2>1. Executive Summary &amp; Architecture</h2>
<p>
    <b>HIMA</b> is an operational machine learning and geospatial intelligence platform for daily <b>wildfire risk prediction</b> and <b>preliminary landslide hydrometeorological trigger evaluation</b> across the 7 Sister States of Northeast India (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura) spanning <b>253,412 km&sup2;</b>.
</p>
<ul>
    <li><b>Analytical Unit:</b> <b>253,408</b> projected 1 km &times; 1 km fishnet grid cells in metric projected CRS <b>EPSG:32646</b> (UTM Zone 46N).</li>
    <li><b>Temporal Window:</b> 2021&ndash;2024 daily resolution (4 complete years). Train: 2021&ndash;2023 (717,324 cell-days). Test: 2024 realistic holdout (1,000,000 cell-days, 348 fires, base rate 0.035%).</li>
    <li><b>Unified Execution:</b> Entire project launches via a single batch script: <code>.\run_hima.bat web</code> (frontend &amp; API), <code>.\run_hima.bat demo</code> (pipeline demo), and <code>.\run_hima.bat test</code> (9 automated unit tests).</li>
</ul>

<h2>2. 4-Member Team Breakdown: Specializations, Contributions &amp; Viva Guide</h2>
<p>
    The project is architected across four distinct engineering disciplines. Each member has defined code ownership, mathematical concepts to explain, and dedicated viva answers:
</p>

<!-- MEMBER 1 -->
<div class="member-card" style="border-top-color: #f97316;">
    <div class="member-title">MEMBER 1: FULL STACK DEVELOPER</div>
    <div class="member-role" style="color: #ea580c;">System Architecture, Interactive Frontend &amp; Prediction REST API</div>
    
    <p><b>1. Codebase Ownership:</b></p>
    <ul>
        <li><code>frontend/index.html</code>: 5-tab Single Page Application (SPA) structure (Overview, Simulator, Models, Gallery, Audit).</li>
        <li><code>frontend/styles.css</code>: Dark glassmorphism design system, responsive grids, animated gauge styling, and risk bands.</li>
        <li><code>frontend/app.js</code>: Client-side engine, canvas particle animation, SVG choropleth projection, dynamic slider binding, and modal lightbox.</li>
        <li><code>src/api/predict.py</code>: Multi-threaded Python HTTP REST API server (<code>ThreadingHTTPServer</code>) handling live inference and metadata caching.</li>
        <li><code>run_hima.bat</code>: Automated Windows batch launcher consolidating all execution modes (<code>web</code>, <code>demo</code>, <code>test</code>, <code>fast</code>).</li>
    </ul>

    <p><b>2. Detailed Technical Contribution &amp; Concept Explanation:</b></p>
    <ul>
        <li><b>High-Performance REST Backend:</b> Built a zero-dependency REST server using Python's standard <code>http.server.ThreadingHTTPServer</code> that loads the trained scikit-learn model bundles (<code>models/*.joblib</code>) into RAM on startup. Predictions execute with sub-50ms latency.</li>
        <li><b>Client-Side SVG Choropleth Map:</b> Rather than using heavy external mapping libraries requiring online tiles or API keys, engineered a pure client-side SVG renderer. Simplified GeoJSON coordinates from <code>study_states.gpkg</code> are projected dynamically using an equirectangular transformation ($X = \text{PAD} + \Delta\lambda \cdot W \cdot 0.9, Y = \text{PAD} + \Delta\phi \cdot H$) with dynamic 3-stop color interpolation across fire counts, landslide occurrences, and test ROC-AUC.</li>
        <li><b>Live Risk Simulator &amp; Animated Gauge:</b> Connected 14 environmental controls to an interactive SVG needle gauge. The gauge path dynamically transitions its <code>stroke-dashoffset</code> (0&ndash;346px) and color based on the predicted probability, assigning provisional risk categories: LOW (&lt;30%), MODERATE (30&ndash;60%), HIGH (60&ndash;80%), and CRITICAL (&gt;80%).</li>
    </ul>

    <p><b>3. Speech Script for Member 1:</b></p>
    <div class="callout">
        <i>"Sir/Ma'am, I owned the Full Stack Development of HIMA. I built our lightweight, multi-threaded REST API server in Python that loads our best ML pipelines and serves predictions live. On the frontend, I engineered a responsive single-page dashboard featuring an interactive SVG choropleth map of Northeast India, an animated risk gauge, real-world scenario presets, and a model comparison viewer, runnable completely offline."</i>
    </div>

    <p><b>4. Member 1 Viva Questions &amp; Answers:</b></p>
    <div class="qa-box">
        <div class="qa-q">Q: How does data flow from the web sliders to the machine learning model?</div>
        <div class="qa-a"><b>A:</b> When the user clicks 'Run Model', JavaScript serializes the 14 form inputs into a JSON payload and makes an asynchronous <code>POST</code> request to <code>/api/predict/wildfire</code>. The Python backend validates the payload, transforms it into a pandas DataFrame matching the 33-feature training schema, feeds it through the scikit-learn pipeline, and returns the raw score, calibrated probability, and risk band in JSON.</div>
    </div>
    <div class="qa-box">
        <div class="qa-q">Q: Why did you build a custom SVG map instead of using Leaflet or Google Maps?</div>
        <div class="qa-a"><b>A:</b> Using standard external map tiles requires an active internet connection, external API keys, and heavy JavaScript dependencies. Our custom SVG parser renders simplified GeoJSON polygons directly from Python outputs, making the entire platform 100% offline-ready, ultra-fast, and reproducible on any machine.</div>
    </div>
</div>

<!-- MEMBER 2 -->
<div class="member-card" style="border-top-color: #0284c7;">
    <div class="member-title">MEMBER 2: DATA SCIENCE SPECIALIST 1</div>
    <div class="member-role" style="color: #0369a1;">Geospatial Engineering, Coordinate Systems &amp; Multimodal Data Ingestion</div>
    
    <p><b>1. Codebase Ownership:</b></p>
    <ul>
        <li><code>src/audit/inventory.py</code>: Automated recursive audit and integrity scanner of 184 raw files (2.898 GB).</li>
        <li><code>src/geospatial/boundaries.py</code>: Extraction of the 7 Sister States from NWIC shapefiles, topological repair, and CRS transformation.</li>
        <li><code>src/geospatial/grid.py</code>: Construction of the 253,408 projected 1 km &times; 1 km fishnet grid cells.</li>
        <li><code>src/ingestion/firms.py</code>: Ingestion, multi-year archive discovery, spatial filtering, and exact deduplication of NASA VIIRS fires.</li>
        <li><code>src/ingestion/imd.py</code> &amp; <code>src/ingestion/era5.py</code>: NetCDF rainfall extraction (CF TIME units) and ERA5 reanalysis KD-Tree coupling.</li>
    </ul>

    <p><b>2. Detailed Technical Contribution &amp; Concept Explanation:</b></p>
    <ul>
        <li><b>Metric Projection (EPSG:32646):</b> Solved spatial distortion across the Himalayas. In geographic coordinates (EPSG:4326), a 0.01&deg; &times; 0.01&deg; cell shrinks significantly as latitude increases from 21&deg;N to 29&deg;N. Projected the study area into UTM Zone 46N (EPSG:32646) centered at 93&deg;E, ensuring every single grid cell is exactly 1,000,000 m&sup2; (1 km&sup2;).</li>
        <li><b>Spatial Nearest-Neighbor KD-Trees:</b> Coupled coarse atmospheric data to fine 1 km grid cells using <code>scipy.spatial.cKDTree</code>: mapped 415 IMD 0.25&deg; grid points (median distance 10.57 km) and 2,491 ERA5 0.1&deg; grid points (median distance 4.21 km) to all 253,408 cells in under 2 seconds.</li>
        <li><b>Multi-Year Archive Discovery:</b> During raw FIRMS audit, discovered that archive zip <code>DL_FIRE_SV-C2_816518.zip</code> spanned 2022&ndash;2023 rather than a single year, enabling complete 2021&ndash;2024 ground truth coverage (219,928 vegetation fires of type=0).</li>
        <li><b>Sikkim Spatial Boundary Defense:</b> Identified that local ERA5 NetCDF grids begin at 89.8&deg;E, while Sikkim lies between 88.0&deg;E and 88.9&deg;E. Enforced zero data fabrication by defining the analytical grid strictly across the contiguous 7 Sister States.</li>
    </ul>

    <p><b>3. Speech Script for Member 2:</b></p>
    <div class="callout">
        <i>"Sir/Ma'am, I led the Geospatial Engineering and raw data ingestion pipeline. I audited 2.9 GB of raw spatial archives and created a metric 1 km fishnet analytical grid of 253,408 cells in EPSG:32646 UTM Zone 46N. I extracted boundary geometries for the 7 Sister States, ingested over 219,000 NASA VIIRS active fires, and linked IMD 0.25-degree rainfall grids and ERA5 reanalysis rasters to every cell using KD-Tree spatial indexing."</i>
    </div>

    <p><b>4. Member 2 Viva Questions &amp; Answers:</b></p>
    <div class="qa-box">
        <div class="qa-q">Q: Why did you convert the coordinate system from EPSG:4326 to EPSG:32646?</div>
        <div class="qa-a"><b>A:</b> In EPSG:4326, coordinates are spherical degrees. Because meridians converge near the poles, a degree of longitude in southern Mizoram (22&deg;N) represents significantly more ground distance than in northern Arunachal Pradesh (29&deg;N). Reprojecting to UTM Zone 46N (EPSG:32646) provides a Cartesian metric coordinate system where distances and areas are preserved in meters.</div>
    </div>
    <div class="qa-box">
        <div class="qa-q">Q: How did you link 415 IMD rain points to 253,408 grid cells efficiently?</div>
        <div class="qa-a"><b>A:</b> Instead of performing heavy spatial polygon intersections for every day across 4 years, I computed spatial nearest-neighbors once using a <code>cKDTree</code> in 2D projected space. Each 1 km cell centroid was assigned the ID of the nearest IMD grid centroid (median distance 10.57 km) and nearest ERA5 centroid (median 4.21 km), allowing instantaneous dictionary-based feature lookups.</div>
    </div>
</div>

<!-- MEMBER 3 -->
<div class="member-card" style="border-top-color: #10b981;">
    <div class="member-title">MEMBER 3: DATA SCIENCE SPECIALIST 2</div>
    <div class="member-role" style="color: #059669;">Feature Engineering, Class Imbalance &amp; Wildfire ML Modeling Lead</div>
    
    <p><b>1. Codebase Ownership:</b></p>
    <ul>
        <li><code>src/features/weather.py</code>: Rolling window feature engineering (3d, 7d, 15d), antecedent rainfall sums, and dry spell tracking.</li>
        <li><code>src/labels/wildfire.py</code>: Wildfire positive labeling, spatial block grouping, and balanced negative subsampling.</li>
        <li><code>src/training/pipelines.py</code>: Implementation and cross-validation of 6 classifiers and hyperparameter tuning.</li>
        <li><code>models/wildfire_best_model.joblib</code>: Validated production model pipeline and model card.</li>
    </ul>

    <p><b>2. Detailed Technical Contribution &amp; Concept Explanation:</b></p>
    <ul>
        <li><b>33 Predictive Physical Features:</b> Formulated atmospheric drying features: afternoon relative humidity minimum (<code>relative_humidity_min</code>), dewpoint depression ($T - T_d$), topsoil volumetric moisture, and rolling antecedent dry days.</li>
        <li><b>Cyclical Seasonal Representation:</b> Replaced linear Day of Year (1&ndash;365) with trigonometric transformations:
            <br/><span class="formula">\sin(\text{doy}) = \sin(2\pi \cdot \text{DOY} / 365), \quad \cos(\text{doy}) = \cos(2\pi \cdot \text{DOY} / 365)</span>
            <br/>This eliminates the artificial numerical discontinuity between December 31 ($\text{DOY}=365$) and January 1 ($\text{DOY}=1$), which was ranked as the #1 most powerful feature in permutation importance.</li>
        <li><b>Spatial Stratified Group Cross-Validation:</b> Partitioned training data using 50 km spatial block IDs as groups. This prevents random K-Fold data leakage where adjacent 1 km cells on the same day end up in both train and validation folds.</li>
        <li><b>Trained &amp; Compared 6 Syllabus Classifiers:</b> Evaluated DummyClassifier, Logistic Regression, Gaussian Naive Bayes, Decision Tree, Random Forest, and HistGradientBoosting. Selected HistGradientBoosting for its superior CV PR-AUC (<b>0.7817</b>) and 2024 Test ROC-AUC (<b>0.9358</b>).</li>
        <li><b>Threshold Optimization:</b> Swept 100 decision thresholds across cross-validation probabilities to find the optimal F1 threshold ($0.7118$), achieving a <b>68.4% detection recall</b> at a <b>6.1% false alarm rate</b>.</li>
    </ul>

    <p><b>3. Speech Script for Member 3:</b></p>
    <div class="callout">
        <i>"Sir/Ma'am, I led Feature Engineering and Wildfire Machine Learning. I engineered 33 atmospheric, drought, and cyclical seasonal features. I trained and compared 6 classifiers using 5-fold Spatial Group Cross-Validation to eliminate spatial autocorrelation leakage. Our best model, HistGradientBoosting, achieved a 0.9358 ROC-AUC and 0.7817 PR-AUC on an unseen 1,000,000 cell-day realistic holdout, correctly identifying 68.4% of fires with only a 6.1% false alarm rate."</i>
    </div>

    <p><b>4. Member 3 Viva Questions &amp; Answers:</b></p>
    <div class="qa-box">
        <div class="qa-q">Q: Why did you use cyclical Day-of-Year instead of just passing the month or integer day?</div>
        <div class="qa-a"><b>A:</b> Time is cyclical, not linear. If we pass DOY as an integer (1 to 365), a decision tree treats Day 1 (Jan 1) and Day 365 (Dec 31) as maximally distant, even though they are consecutive days in the winter climate. Transforming into sine and cosine preserves continuous seasonal periodicity.</div>
    </div>
    <div class="qa-box">
        <div class="qa-q">Q: Why is HistGradientBoosting better than Random Forest in this application?</div>
        <div class="qa-a"><b>A:</b> Random Forest builds trees independently in parallel, averaging predictions to reduce variance. HistGradientBoosting builds trees sequentially, where each successive tree explicitly fits the gradient residuals (errors) of prior trees. It captures complex feature interactions (such as heat + low humidity + high wind) with higher precision and uses 256-bin histogram discretization, training in seconds with native handling of missing values.</div>
    </div>
</div>

<!-- MEMBER 4 -->
<div class="member-card" style="border-top-color: #a855f7;">
    <div class="member-title">MEMBER 4: DATA SCIENCE SPECIALIST 3</div>
    <div class="member-role" style="color: #7e22ce;">Landslide Modeling, Statistical Calibration &amp; Test Quality Assurance</div>
    
    <p><b>1. Codebase Ownership:</b></p>
    <ul>
        <li><code>src/ingestion/gsi_pdf.py</code>: Unstructured PDF table extraction for GSI landslide compendium using <code>pymupdf</code>.</li>
        <li><code>src/ingestion/coolr.py</code>: Verification and spatial intersection of NASA Global Landslide Catalog.</li>
        <li><code>src/labels/landslide.py</code> &amp; <code>src/training/landslide_pipelines.py</code>: Landslide labeling and preliminary trigger modeling.</li>
        <li><code>src/evaluation/metrics.py</code>: Bayesian odds-ratio prior adjustment, Brier score calibration, and performance metrics.</li>
        <li><code>src/evaluation/eda.py</code>: Generation of 19 publication-grade exploratory figures and maps.</li>
        <li><code>tests/test_hima_pipeline.py</code>: Authoring the 9 automated pytest unit and data-integrity test suites.</li>
    </ul>

    <p><b>2. Detailed Technical Contribution &amp; Concept Explanation:</b></p>
    <ul>
        <li><b>PDF Table Layout Mining:</b> The GSI landslide compendium was an unstructured multi-page PDF where standard table-detection libraries failed. Developed a word-coordinate parser using <code>pymupdf</code> based on horizontal $X$-boundaries, extracting <b>10,731 national records</b> and <b>9,970 validated events within the 7 Sister States</b> (463 unique dated cell-days).</li>
        <li><b>Survey Bias Discovery &amp; Mitigation:</b> Discovered that <b>78.6% (529/673)</b> of dated GSI events came from a single post-monsoon 2024 field survey in Mizoram. Proved that including <code>state_name</code> in landslide features caused models to overfit to Mizoram's geographical boundary rather than learning actual rainfall physics. Successfully neutralized this bias by <b>excluding <code>state_name</code> from landslide features</b>.</li>
        <li><b>Bayesian Odds-Ratio Calibration:</b> Because negative subsampling was used during training (effective prior ~16.7%), raw model probabilities overestimated true daily risk. Implemented Bayes' Theorem odds-ratio adjustment:
            <br/><span class="formula">P_{\text{cal}} = \frac{P_{\text{raw}}}{P_{\text{raw}} + (1 - P_{\text{raw}}) \cdot \frac{\pi_{\text{train}}}{\pi_{\text{target}}} \cdot \frac{1 - \pi_{\text{target}}}{1 - \pi_{\text{train}}}}</span>
            <br/>Calibrated raw scores back to true population prevalence ($0.043\%$), lowering Brier score from 0.083 to 0.0005.</li>
        <li><b>Preliminary Weather-Only Landslide Model:</b> Developed the preliminary landslide classifier using antecedent IMD/ERA5 rainfall (1d, 3d, 7d, 15d) and soil water saturation, achieving <b>0.9367 ROC-AUC</b> on the 2024 holdout.</li>
        <li><b>Automated Testing Suite:</b> Built 9 comprehensive pytest test suites in <code>tests/test_hima_pipeline.py</code>, ensuring automated verification of data integrity, gap preservation, and zero feature leakage.</li>
    </ul>

    <p><b>3. Speech Script for Member 4:</b></p>
    <div class="callout">
        <i>"Sir/Ma'am, I led Landslide Modeling, Statistical Calibration, and Software Quality Assurance. I built the PDF mining parser to extract 9,970 GSI field landslide records, detected and resolved severe geographical survey bias by removing state identifiers from landslide features, and implemented Bayesian odds-ratio adjustment to calibrate probabilities back to real-world base rates. I also authored our 9 automated unit tests verifying zero data leakage, correct temporal handling, and deterministic inference."</i>
    </div>

    <p><b>4. Member 4 Viva Questions &amp; Answers:</b></p>
    <div class="qa-box">
        <div class="qa-q">Q: Why is your Landslide model called 'Preliminary Weather-Only'?</div>
        <div class="qa-a"><b>A:</b> Landslide susceptibility fundamentally depends on static terrain features: slope, aspect, curvature, bedrock geology, and soil thickness. These datasets were absent locally. Following strict research integrity, we did not fabricate synthetic topography. Our model strictly evaluates hydrometeorological triggering (rainfall accumulation and soil saturation).</div>
    </div>
    <div class="qa-box">
        <div class="qa-q">Q: What did the Bayesian Prior Adjustment achieve mathematically?</div>
        <div class="qa-a"><b>A:</b> Classifiers trained on subsampled data output probabilities reflecting the training ratio (~16.7%), not the real world (0.043%). Bayesian prior adjustment recalibrates the probability distribution without changing the monotonic rank order, ensuring predicted probabilities represent actual real-world single-cell daily occurrence rates.</div>
    </div>
</div>

<h2>3. Comprehensive Breakdown of the 9 Automated Test Cases</h2>
<p>
    The test suite in <code>tests/test_hima_pipeline.py</code> runs in <b>2.56 seconds</b> and verifies 9 mission-critical properties of the system:
</p>

<div class="test-box">
    <div class="test-title">1. test_config_loads_and_has_disclaimer()</div>
    <p><b>What it tests:</b> Verifies that <code>config/project.yaml</code> loads cleanly, contains the mandatory academic disclaimer string (<i>"not an official warning"</i>), defines grid cell size as 1000m, and specifies projected CRS as <code>EPSG:32646</code>.</p>
    <p><b>Why it matters:</b> Guarantees configuration reproducibility and legal compliance across the entire pipeline.</p>
</div>

<div class="test-box">
    <div class="test-title">2. test_days_since_rain_preserves_missing_gaps()</div>
    <p><b>What it tests:</b> Passes a synthetic rainfall array with missing days: <code>[5mm, 0mm, 0mm, NaN, 0mm, 3mm]</code>. Asserts that the missing day remains <code>NaN</code> (never filled with 0) and that the streak resets cleanly after the gap.</p>
    <p><b>Why it matters:</b> Proves that ERA5 reanalysis gaps (e.g., missing August 2023) do not fabricate artificial 30-day drought streaks across missing months.</p>
</div>

<div class="test-box">
    <div class="test-title">3. test_imd_season_mapping()</div>
    <p><b>What it tests:</b> Validates that calendar month integers (1, 3, 7, 10, 12) strictly map to official IMD seasons: <i>Winter, Pre-Monsoon, Monsoon, Post-Monsoon, Winter</i>.</p>
    <p><b>Why it matters:</b> Prevents seasonal classification errors when computing performance stratified by climate seasons.</p>
</div>

<div class="test-box">
    <div class="test-title">4. test_bayes_prior_adjustment_monotonic_and_bounded()</div>
    <p><b>What it tests:</b> Evaluates probability array $[0.01, 0.25, 0.50, 0.75, 0.99]$ under Bayesian prior adjustment. Asserts that outputs are bounded in $[0, 1]$, strictly monotonic ($P_1 < P_2$), and that at $P=0.50$ with $\pi_{\text{train}}=0.50$, the output exactly equals $\pi_{\text{target}}$.</p>
    <p><b>Why it matters:</b> Proves that probability calibration preserves the exact ROC ranking and obeys the mathematical laws of conditional probability.</p>
</div>

<div class="test-box">
    <div class="test-title">5. test_risk_band_boundaries()</div>
    <p><b>What it tests:</b> Passes boundary probabilities $[0.05, 0.30, 0.65, 0.90]$ and verifies exact mapping into the 4 standard categories: <i>LOW (0&ndash;30%), MODERATE (30&ndash;60%), HIGH (60&ndash;80%), and CRITICAL (80&ndash;100%)</i>.</p>
    <p><b>Why it matters:</b> Guarantees consistent color coding and operational categorization between the backend API and frontend gauge.</p>
</div>

<div class="test-box">
    <div class="test-title">6. test_no_post_event_leakage_in_features()</div>
    <p><b>What it tests:</b> Compares the 33 training features against a forbidden set of post-event columns: <code>fire_detected</code>, <code>detection_count</code>, <code>frp_sum</code>, <code>frp_mean</code>, <code>brightness_mean</code>, etc., asserting zero intersection.</p>
    <p><b>Why it matters:</b> <b>The most critical test for academic defense.</b> Proves that satellite fire metrics that only exist after ignition were never leaked into the training features.</p>
</div>

<div class="test-box">
    <div class="test-title">7. test_grid_and_boundaries_artifacts_if_built()</div>
    <p><b>What it tests:</b> Inspects <code>grid_metadata.json</code> to confirm that exactly 0 cells lie outside the 7-state boundary, total cell count exceeds 200,000, and metric cell width is 1000m.</p>
    <p><b>Why it matters:</b> Verifies the integrity of the spatial analytical fishnet grid without spatial clipping or leakage outside Northeast India.</p>
</div>

<div class="test-box">
    <div class="test-title">8. test_validated_wildfire_predictor_inference()</div>
    <p><b>What it tests:</b> Runs end-to-end model inference on two contrasting test inputs: a dry Pre-Monsoon Mizoram cell vs. a flooded Monsoon Assam cell. Asserts that the dry cell scores strictly higher in both raw score and calibrated probability.</p>
    <p><b>Why it matters:</b> Proves that the trained model bundle loaded in production makes physically realistic decisions on unseen meteorological inputs.</p>
</div>

<div class="test-box">
    <div class="test-title">9. test_required_deliverables_exist()</div>
    <p><b>What it tests:</b> Asserts the physical existence of all 23 core deliverables: model cards, saved joblib pipelines, CSV comparison tables, figures, maps, audit summaries, README, and requirements.</p>
    <p><b>Why it matters:</b> Ensures that any evaluator cloning the repository has all artifacts required for verification.</p>
</div>

<h2>4. Dependent vs. Independent Variables (Model Specifications)</h2>
<p>
    The modeling pipeline formulates two distinct binary classification tasks:
</p>
<ul>
    <li><b>Wildfire Target ($Y_{\text{fire}} \in \{0, 1\}$):</b> 1 if at least one VIIRS vegetation fire detected in cell $c$ on date $t$; 0 otherwise.</li>
    <li><b>Landslide Target ($Y_{\text{slide}} \in \{0, 1\}$):</b> 1 if a GSI field landslide occurred in cell $c$ on date $t$; 0 otherwise.</li>
    <li><b>Independent Features ($X \in \mathbb{R}^{33}$):</b>
        Thermal drying (temperature, dewpoint depression, min/mean humidity), hydrological (soil moisture layer 1, 7d rolling moisture), precipitation history (same-day rain, 3d, 7d, 15d sums, consecutive dry days), wind speed, and spatiotemporal features ($\sin(\text{doy})$, $\cos(\text{doy})$, latitude, longitude, state, season).
    </li>
</ul>

<h2>5. Guide to All Website Sliders &amp; Physical Interactions</h2>
<table>
    <tr>
        <th>Slider / Factor</th>
        <th>Range / Units</th>
        <th>Physical Meaning &amp; Modeling Role</th>
    </tr>
    <tr>
        <td><b>State</b></td>
        <td>7 Sister States</td>
        <td>Regional baseline fire frequency based on vegetation density and shifting cultivation practices.</td>
    </tr>
    <tr>
        <td><b>IMD Season</b></td>
        <td>Pre-Monsoon, Monsoon, Post-Monsoon, Winter</td>
        <td>Seasonal macro-climate. Wildfires strictly concentrate in Pre-Monsoon (March&ndash;April); Monsoon brings near-total suppression.</td>
    </tr>
    <tr>
        <td><b>Latitude &amp; Longitude</b></td>
        <td>21.9&deg;&ndash;29.3&deg;N, 89.8&deg;&ndash;97.3&deg;E</td>
        <td>Geographic coordinates. Southern ridges (Mizoram) warm earlier in spring than northern alpine Arunachal Pradesh.</td>
    </tr>
    <tr>
        <td><b>Day of Year (DOY)</b></td>
        <td>1 to 365 (e.g., 90 = Mar 31)</td>
        <td><b>#1 Top Permutation Feature!</b> Converted to continuous sine and cosine angles. Captures the spring dry season timing.</td>
    </tr>
    <tr>
        <td><b>ERA5 Temperature</b></td>
        <td>0&deg;C to 37&deg;C</td>
        <td>Daily mean ambient temperature driving transpiration and forest litter desiccation.</td>
    </tr>
    <tr>
        <td><b>Min Relative Humidity (RH)</b></td>
        <td>5% to 100%</td>
        <td><b>#1 Weather Factor!</b> Afternoon minimum humidity. Values &lt;25% dramatically increase flammability; values &gt;75% suppress fires.</td>
    </tr>
    <tr>
        <td><b>Soil Moisture (Layer 1)</b></td>
        <td>0.05 to 0.50 m&sup3;/m&sup3;</td>
        <td>Volumetric water content in the top 0&ndash;7 cm of soil. Moisture &lt;0.15 indicates extreme ground fuel dryness.</td>
    </tr>
    <tr>
        <td><b>Wind Speed</b></td>
        <td>0.1 to 12.0 m/s</td>
        <td>Surface wind providing oxygen and accelerating fire propagation.</td>
    </tr>
    <tr>
        <td><b>Same-Day Rain (1d)</b></td>
        <td>0 to 250 mm</td>
        <td>IMD precipitation on the prediction day, causing immediate physical suppression of ignitions.</td>
    </tr>
    <tr>
        <td><b>Antecedent Rain (3d, 7d, 15d)</b></td>
        <td>0 to 1200 mm</td>
        <td>Cumulative historical rainfall over prior weeks. Primary driver for <b>landslide trigger threshold</b>.</td>
    </tr>
    <tr>
        <td><b>Consecutive Dry Days</b></td>
        <td>0 to 60 days</td>
        <td>Uninterrupted dry spell count (&lt;2.5 mm rain). High values indicate prolonged biomass drying.</td>
    </tr>
</table>

<h2>6. All 6 Classifiers &amp; Why HistGradientBoosting Won</h2>
<ol>
    <li><b>DummyClassifier (Baseline):</b> Predicts training label distribution. Yields exactly <b>0.5000 ROC-AUC</b>, confirming all models learn real patterns.</li>
    <li><b>Logistic Regression:</b> Computes weighted linear log-odds: <span class="formula">P(Y=1|X) = \sigma(w^T X + b)</span>. Achieved <b>0.9040 ROC-AUC</b>, but cannot model nonlinear meteorological synergies.</li>
    <li><b>Gaussian Naive Bayes:</b> Assumes feature independence: <span class="formula">P(Y|X) \propto P(Y) \prod P(X_i|Y)</span>. Achieved <b>0.8621 ROC-AUC</b>, heavily penalized by high correlation among weather features.</li>
    <li><b>Decision Tree (CART):</b> Orthogonal binary splits maximizing Gini reduction. Achieved <b>0.9049 ROC-AUC</b>; provides complete visual interpretability.</li>
    <li><b>Random Forest:</b> Bagging ensemble of 100 decorrelated trees with random subspace sampling. Achieved <b>0.9260 ROC-AUC</b> and <b>0.7761 CV PR-AUC</b>.</li>
    <li><b>HistGradientBoosting (Best Model):</b> Sequential boosting algorithm with 256-bin histogram discretization fitting gradient residuals:
        <br/><span class="formula">F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)</span>
        <br/><b>Why it won:</b> Achieved <b>0.9358 Test ROC-AUC</b>, <b>0.7817 CV PR-AUC</b>, <b>68.4% fire recall</b>, and only <b>6.1% false alarm rate</b>, with native handling of missing reanalysis values.
    </li>
</ol>

<h2>7. Comprehensive Viva Question Bank</h2>
<div class="qa-box">
    <div class="qa-q">Q1: Why is test precision small (~0.4%) when ROC-AUC is 93.6%?</div>
    <div class="qa-a"><b>A:</b> This is the <b>Base Rate Fallacy</b> in rare-event modeling. The 2024 test set contains only 348 fire days across 1,000,000 cell-days (0.035% prevalence). Even with a 94% accurate model with a 6% false alarm rate, false positives numerically outnumber true positives. ROC-AUC and PR-AUC are the primary metrics used in literature.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q2: How did you ensure zero data leakage?</div>
    <div class="qa-a"><b>A:</b> Strict forward temporal split (train 2021&ndash;2023, test 2024), Spatial Group K-Fold cross-validation on 50 km geographic blocks, and complete exclusion of post-event satellite readings (FRP, brightness).</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q3: Why was Sikkim excluded from the ERA5 grid?</div>
    <div class="qa-a"><b>A:</b> ERA5 reanalysis starts at 89.8&deg;E, while Sikkim is located at 88.0&deg;&ndash;88.9&deg;E. To maintain zero data fabrication, the analytical grid was constrained to the 7 Sister States.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q4: Why is the Landslide model 'Preliminary Weather-Only'?</div>
    <div class="qa-a"><b>A:</b> Static terrain layers (DEM/slope, geology, SoilGrids) were unavailable locally. Adhering to zero fabrication, the model evaluates hydrometeorological triggering (antecedent rainfall and soil saturation) only.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q5: Why was state_name excluded from Landslide features?</div>
    <div class="qa-a"><b>A:</b> 78.6% of dated GSI events came from a 2024 Mizoram field survey campaign. Excluding <code>state_name</code> prevented the model from memorizing geographical survey bias.</div>
</div>
"""

def generate_pdf():
    print(f"[PDF Gen] Compiling Complete HIMA Study Guide & Viva Prep to: {OUTPUT_PDF}")
    mediabox = pymupdf.paper_rect("a4")
    # Margins: 32pt top, 36pt left/right, 36pt bottom
    where = mediabox + (36, 32, -36, -36)

    writer = pymupdf.DocumentWriter(str(OUTPUT_PDF))
    story = pymupdf.Story(html=HTML_CONTENT, user_css=CSS)

    def rectfn(rect_num, filled):
        return mediabox, where, None

    story.write(writer, rectfn)
    writer.close()
    print(f"[PDF Gen] Successfully generated PDF! File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    generate_pdf()
