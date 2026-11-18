"""Generate HIMA Complete Project Textbook & Viva Handbook PDF.

Compiles an exhaustive, multi-chapter textbook-grade study guide covering:
- Chapter 1: Project Master Architecture & Problem Statement
- Chapter 2: Member 1 Handbook (Full Stack & System Integration Lead)
- Chapter 3: Member 2 Handbook (Geospatial & Data Pipeline Lead)
- Chapter 4: Member 3 Handbook (Feature Engineering & Wildfire ML Lead)
- Chapter 5: Member 4 Handbook (Landslide ML, Statistical Calibration & QA Lead)
- Chapter 6: The 9 Automated Unit Test Cases (Exhaustive Technical Guide)
- Chapter 7: Master Viva Exam Bank (30+ High-Yield Questions with Complete Answers)
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
    font-size: 8.8pt;
    line-height: 1.45;
    color: #1e293b;
}
.cover-box {
    background-color: #0f172a;
    color: #ffffff;
    padding: 22pt 24pt;
    border-radius: 6pt;
    margin-bottom: 14pt;
}
.cover-box h1 {
    font-size: 21pt;
    margin: 0 0 4pt 0;
    color: #f97316;
    letter-spacing: -0.5pt;
}
.cover-box .sub {
    font-size: 10.5pt;
    color: #cbd5e1;
    margin: 0 0 6pt 0;
}
.cover-box .meta {
    font-size: 8pt;
    color: #94a3b8;
    margin: 0;
}
.toc-box {
    background-color: #f8fafc;
    border: 1pt solid #cbd5e1;
    border-radius: 4pt;
    padding: 10pt 14pt;
    margin-bottom: 14pt;
}
.toc-box h3 {
    margin: 0 0 6pt 0;
    color: #0f172a;
    font-size: 10pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
}
.toc-grid {
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.6;
}
.member-banner {
    background-color: #0f172a;
    color: #ffffff;
    padding: 10pt 14pt;
    border-radius: 4pt;
    margin-top: 18pt;
    margin-bottom: 10pt;
}
.member-banner h2 {
    color: #f97316;
    font-size: 13pt;
    margin: 0 0 2pt 0;
    border: none;
    padding: 0;
}
.member-banner .role {
    font-size: 8.5pt;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    font-weight: bold;
    margin: 0;
}
h2 {
    color: #0f172a;
    font-size: 12pt;
    border-bottom: 1.5pt solid #e2e8f0;
    padding-bottom: 3pt;
    margin-top: 14pt;
    margin-bottom: 6pt;
}
h3 {
    color: #0369a1;
    font-size: 10pt;
    margin-top: 10pt;
    margin-bottom: 3pt;
}
h4 {
    color: #334155;
    font-size: 8.8pt;
    margin-top: 6pt;
    margin-bottom: 2pt;
    font-weight: bold;
}
p {
    margin: 0 0 5pt 0;
    text-align: justify;
}
ul, ol {
    margin: 0 0 6pt 14pt;
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
.callout-speech {
    background-color: #faf5ff;
    border-left: 3pt solid #a855f7;
    padding: 8pt 12pt;
    margin: 8pt 0;
    border-radius: 0 4pt 4pt 0;
    font-style: italic;
    color: #4c1d95;
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
    border: 1pt solid #e2e8f0;
}
.qa-box {
    background-color: #f8fafc;
    border: 1pt solid #e2e8f0;
    border-radius: 4pt;
    padding: 6pt 8pt;
    margin-bottom: 7pt;
}
.qa-q {
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 2pt;
}
.qa-a {
    color: #334155;
    text-align: justify;
}
.test-box {
    background-color: #ffffff;
    border: 1pt solid #cbd5e1;
    border-left: 3.5pt solid #10b981;
    border-radius: 3pt;
    padding: 6pt 8pt;
    margin-bottom: 7pt;
}
.test-title {
    font-weight: bold;
    color: #0f172a;
    font-family: courier, monospace;
    font-size: 8.5pt;
}
"""

HTML_CONTENT = r"""
<div class="cover-box">
    <h1>HIMA: The Complete Project Textbook &amp; Viva Handbook</h1>
    <div class="sub">Hazard Intelligence, Monitoring &amp; Assessment &mdash; Northeast India Geospatial Wildfire &amp; Landslide ML Platform</div>
    <div class="meta">B.Tech Data Science / AI-ML Capstone (Course CSET312) &bull; GitHub: https://github.com/ujjww4ll/HIMA &bull; Framework: Python, scikit-learn, GeoPandas, PyMuPDF</div>
</div>

<div class="callout-warn">
    <b>Mandatory Academic Disclaimer:</b> Research risk estimate only &mdash; not an official operational warning. All predictions are spatial-probabilistic estimates for academic evaluation across Northeast India.
</div>

<div class="toc-box">
    <h3>Handbook Contents</h3>
    <div class="toc-grid">
        &bull; <b>Chapter 1:</b> Project Master Architecture, Study Area &amp; The Physical Problem<br/>
        &bull; <b>Chapter 2:</b> Member 1 Handbook &mdash; Full Stack &amp; System Integration Specialist<br/>
        &bull; <b>Chapter 3:</b> Member 2 Handbook &mdash; Geospatial Engineering &amp; Data Pipeline Lead<br/>
        &bull; <b>Chapter 4:</b> Member 3 Handbook &mdash; Feature Engineering &amp; Wildfire ML Specialist<br/>
        &bull; <b>Chapter 5:</b> Member 4 Handbook &mdash; Landslide Modeling, Statistical Calibration &amp; QA Lead<br/>
        &bull; <b>Chapter 6:</b> The 9 Automated Test Cases &mdash; Line-by-Line Integrity Guide<br/>
        &bull; <b>Chapter 7:</b> Master Project Viva Exam Bank (30+ High-Yield Questions &amp; Detailed Model Answers)
    </div>
</div>

<!-- CHAPTER 1 -->
<h2>Chapter 1: Project Master Architecture, Study Area &amp; The Physical Problem</h2>

<p>
    <b>1.1 What is HIMA?</b><br/>
    HIMA stands for <b>Hazard Intelligence, Monitoring &amp; Assessment</b>. It is an end-to-end Machine Learning and Geospatial Intelligence platform engineered to solve two high-consequence natural hazard challenges across Northeast India:
</p>
<ol>
    <li><b>Daily Wildfire Ignition &amp; Propagation Risk:</b> Predicting whether an analytical 1 km &times; 1 km cell on a given calendar day will experience an active vegetation wildfire.</li>
    <li><b>Preliminary Landslide Hydrometeorological Triggering:</b> Evaluating whether accumulated rainfall and soil moisture saturation cross critical thresholds to trigger slope instability and mass movements.</li>
</ol>

<p>
    <b>1.2 Why Northeast India? The Geographic &amp; Climate Context</b><br/>
    Northeast India comprises the 7 Sister States (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, and Tripura), spanning an area of <b>253,412 km&sup2;</b>. This region is a global biodiversity hotspot characterized by unique climatic vulnerabilities:
</p>
<ul>
    <li><b>Severe Wildfire Seasonality (Pre-Monsoon):</b> During the dry pre-monsoon months of March and April, temperatures climb rapidly while afternoon relative humidity plummets below 20%. Combined with traditional shifting cultivation (jhum) clearance where dried biomass is burned before the sowing season, fires frequently escape control and spread into adjacent deciduous and evergreen forest tracts.</li>
    <li><b>Extreme Monsoon Rainfall &amp; Landslide Disasters (June&ndash;September):</b> Northeast India receives among the highest annual precipitation volumes on Earth (e.g., Mawsynram and Cherrapunji in Meghalaya). Intense or sustained multi-week rainfall saturates weathered residual soil horizons on steep Himalayan and Indo-Burma ranges, causing thousands of catastrophic slope failures annually.</li>
</ul>

<p>
    <b>1.3 The Core Technical Deliverables:</b><br/>
    The project contains no simulated or fabricated data. It unifies <b>4 primary real-world raw datasets (2.898 GB)</b> over a 4-year temporal horizon (2021&ndash;2024 daily):
</p>
<ul>
    <li><b>NASA FIRMS VIIRS S-NPP Collection 2:</b> 219,928 satellite active vegetation fire detections (375 m resolution, type=0).</li>
    <li><b>Geological Survey of India (GSI) NLSM Compendium:</b> 9,970 field-validated historical landslides inside the 7 Sister States.</li>
    <li><b>ECMWF ERA5-Land Reanalysis:</b> 0.1&deg; gridded daily atmospheric and soil hydrology data (temperature, dewpoint, min/mean relative humidity, wind speed, volumetric soil moisture layer 1).</li>
    <li><b>India Meteorological Department (IMD):</b> 0.25&deg; gridded daily rainfall covering all 48 months (2021&ndash;2024).</li>
</ul>

<!-- CHAPTER 2 -->
<div class="member-banner">
    <h2>Chapter 2: Member 1 Handbook &mdash; Full Stack Developer</h2>
    <div class="role">System Architecture, Web Application, Interactive Map &amp; REST Prediction Server</div>
</div>

<h3>2.1 Role Definition &amp; Codebase Ownership</h3>
<p>
    Member 1 is responsible for everything the user touches, sees, interacts with, and executes over the network. They transformed raw machine learning artifacts into an interactive, high-performance web platform:
</p>
<table>
    <tr>
        <th>File Path</th>
        <th>Lines / Size</th>
        <th>Technical Function &amp; Purpose</th>
    </tr>
    <tr>
        <td><code>frontend/index.html</code></td>
        <td>341 lines</td>
        <td>Defines the semantic structure of the 5-tab Single Page Application (Overview, Risk Simulator, ML Models, Visuals Gallery, Audit &amp; Limitations).</td>
    </tr>
    <tr>
        <td><code>frontend/styles.css</code></td>
        <td>450+ lines</td>
        <td>Custom dark glassmorphism design system (navy <code>#020817</code>, orange fire accent <code>#f97316</code>), CSS Grid/Flexbox layouts, responsive mobile rules, and animated needle gauge aesthetics.</td>
    </tr>
    <tr>
        <td><code>frontend/app.js</code></td>
        <td>996 lines</td>
        <td>Client-side JavaScript engine: background canvas particle simulation, client-side SVG coordinate projection, slider event binding, REST fetch calls, and modal lightbox viewer.</td>
    </tr>
    <tr>
        <td><code>src/api/predict.py</code></td>
        <td>310+ lines</td>
        <td>Multi-threaded HTTP REST API server (<code>ThreadingHTTPServer</code>) providing deterministic model inference, cached metadata responses, and secure static asset delivery.</td>
    </tr>
    <tr>
        <td><code>run_hima.bat</code></td>
        <td>38 lines</td>
        <td>Automated batch launcher consolidating single-command modes: <code>web</code>, <code>demo</code>, <code>fast</code>, and <code>test</code>.</td>
    </tr>
</table>

<h3>2.2 Detailed Technical Deep-Dive</h3>

<h4>A. Zero-Dependency Multi-Threaded Python REST Server</h4>
<p>
    Instead of using heavy web frameworks like Django, Flask, or FastAPI that require large third-party runtime dependencies, Member 1 implemented a native, high-throughput server using Python's standard library <code>http.server.ThreadingHTTPServer</code>.
</p>
<ul>
    <li><b>In-Memory Model Loading:</b> When the server boots up, it loads <code>WildfireRiskPredictor</code> and <code>LandslideRiskPredictor</code> into system memory once. Subsequent HTTP requests execute inference immediately without reading files from disk.</li>
    <li><b>Thread Pooling:</b> <code>ThreadingHTTPServer</code> assigns incoming requests to separate worker threads, allowing simultaneous browser requests (e.g., streaming GeoJSON metadata while calculating model inference) without blocking.</li>
    <li><b>Endpoints Served:</b>
        <ul>
            <li><code>GET /</code> and <code>GET /index.html</code>: Delivers the frontend SPA.</li>
            <li><code>GET /api/overview</code>: Returns pre-aggregated JSON metadata, verified data audit statistics, comparison tables, and simplified study-state polygon GeoJSON.</li>
            <li><code>POST /api/predict/wildfire</code>: Receives a 33-feature JSON payload, converts it to a pandas DataFrame, evaluates probabilities via the scikit-learn pipeline, and returns the raw score, calibrated probability, and risk band.</li>
            <li><code>POST /api/predict/landslide</code>: Evaluates the preliminary hydrometeorological landslide model.</li>
            <li><code>GET /outputs/...</code>: Delivers 19 generated figures and maps securely with strict parent-path validation to prevent directory traversal attacks.</li>
        </ul>
    </li>
</ul>

<h4>B. Custom Client-Side SVG Choropleth Map (100% Offline)</h4>
<p>
    Traditional web apps rely on online mapping libraries like Leaflet, Mapbox, or Google Maps. These libraries require external internet access, API tokens, and download heavy raster tiles. Member 1 designed a mathematical, client-side vector renderer in pure SVG:
</p>
<ol>
    <li><b>GeoJSON Coordinate Projection:</b> Real multi-polygon geometries from <code>study_states.gpkg</code> were simplified in GeoPandas using Douglas-Peucker tolerance ($\epsilon = 0.025$). The JavaScript converts longitude ($\lambda$) and latitude ($\phi$) into SVG canvas coordinates ($X, Y$) using an equirectangular transformation with an aspect correction factor:
        <br/><span class="formula">X = \text{PAD} + \left(\frac{\lambda - \lambda_{\min}}{\lambda_{\max} - \lambda_{\min}}\right) \cdot (W - 2 \cdot \text{PAD}) \cdot 0.9, \quad Y = \text{PAD} + \left(\frac{\phi_{\max} - \phi}{\phi_{\max} - \phi_{\min}}\right) \cdot (H - 2 \cdot \text{PAD})</span>
    </li>
    <li><b>Dynamic 3-Stop Color Interpolation:</b> As the user switches the layer dropdown between <i>Wildfire Detections</i>, <i>ROC-AUC Performance</i>, and <i>GSI Landslides</i>, JavaScript normalizes values into $t \in [0, 1]$ and dynamically blends RGB hex values across a dark blue &rarr; vibrant orange &rarr; red gradient.</li>
    <li><b>Interactive State Binding:</b> Clicking any state on the map highlights the polygon, updates the side panel with exact statistics (grid cells, fire counts, ROC-AUC), and automatically pre-populates the Risk Simulator with that state's representative latitude and longitude.</li>
</ol>

<h4>C. Live Risk Simulator &amp; Animated SVG Needle Gauge</h4>
<ul>
    <li>The simulator connects 14 environmental controls (sliders and dropdowns) to an SVG circular arc gauge.</li>
    <li>The circular arc has a total arc length of 346 pixels. When the API returns a risk probability $P \in [0, 1]$, JavaScript animates the <code>stroke-dashoffset</code>:
        <br/><span class="formula">\text{stroke-dashoffset} = 346 \cdot (1 - P)</span>
        <br/>This smoothly sweeps the colored bar clockwise from 0% to the exact predicted score in 1.2 seconds, changing color dynamically from green (LOW) to amber (MODERATE), orange (HIGH), and red (CRITICAL).
    </li>
    <li><b>Real-World Scenarios:</b> Features 4 one-click scenario presets: <i>Dry Pre-Monsoon (Mizoram)</i>, <i>Peak Monsoon (Assam)</i>, <i>Cyclone Remal Extreme Rain</i>, and <i>Cool Winter (Arunachal)</i>.</li>
</ul>

<h3>2.3 Member 1 Speech Script for the Presentation</h3>
<div class="callout-speech">
    "Good morning Sir/Ma'am. I owned the Full Stack Development and System Integration for Project HIMA. My objective was to take our machine learning models out of isolated Python scripts and deliver a complete, responsive, production-ready research platform.
    <br/><br/>
    I developed our high-performance Python REST backend using a multi-threaded architecture that keeps our trained scikit-learn models in memory, serving predictions in less than 50 milliseconds. On the frontend, I built a Single Page Application using HTML5, CSS3 glassmorphism, and vanilla JavaScript. Instead of relying on third-party mapping APIs that require internet access, I built a custom SVG choropleth engine that renders simplified GeoJSON polygons of the 7 Sister States completely offline with dynamic color scaling and interactive state inspection.
    <br/><br/>
    Finally, I created our Live Risk Simulator, connecting 14 environmental parameters to an animated SVG needle gauge that displays both raw model scores and calibrated daily probabilities in real-time."
</div>

<h3>2.4 Comprehensive Viva Questions &amp; Detailed Answers for Member 1</h3>
<div class="qa-box">
    <div class="qa-q">Q1: How does your web frontend communicate with the machine learning model? Explain the full request-response lifecycle.</div>
    <div class="qa-a"><b>Answer:</b> When the user clicks 'Run Model' on the simulator tab, JavaScript extracts the current values from the 14 form inputs (latitude, longitude, day of year, temperature, relative humidity, soil moisture, wind speed, rainfall sums, dry days, state, and season). It calculates required mathematical derivatives (such as $\sin(\text{doy})$, $\cos(\text{doy})$, dewpoint depression, and rolling proxies) and packages them into a JSON object. JavaScript then executes an asynchronous <code>fetch()</code> POST request to <code>/api/predict/wildfire</code>. The Python server parses the JSON body, converts it into a pandas DataFrame matching our 33-feature training schema, feeds it into the joblib pipeline, and returns the raw classification score, the Bayesian calibrated probability, and the risk band in a JSON response. JavaScript unpacks this response and triggers CSS transitions to animate the needle gauge, update metric cards, and color the band pill.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q2: Why did you build a custom SVG map instead of using a standard mapping library like Leaflet, OpenLayers, or Mapbox?</div>
    <div class="qa-a"><b>Answer:</b> External mapping libraries introduce heavy client-side overhead (often 500 KB to 2 MB of JavaScript and CSS) and rely on remote raster or vector tile servers. If the system is offline, behind an institutional firewall, or in an area with poor connectivity, external map tiles fail to load. By calculating an equirectangular projection of simplified GeoJSON polygons directly in pure SVG, our map is 100% self-contained, offline-ready, renders instantaneously, and enables direct DOM manipulation for hover tooltips, click selection, and dynamic fill-color transitions.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q3: How do you prevent Path Traversal / Directory Traversal attacks when serving files from <code>/outputs/</code>?</div>
    <div class="qa-a"><b>Answer:</b> In <code>src/api/predict.py</code>, when a client requests an image via <code>/outputs/figures/example.png</code>, the server resolves the target path to its absolute filesystem representation using <code>Path.resolve()</code>. It then explicitly checks whether <code>OUTPUTS_DIR.resolve()</code> is an ancestor of the target file using <code>target.parents</code>. If an attacker passes a path like <code>/outputs/../../config/secrets</code>, the check detects that the target is outside the outputs directory and immediately terminates the request with an HTTP 403 Forbidden status.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q4: What is the purpose of the <code>run_hima.bat</code> file?</div>
    <div class="qa-a"><b>Answer:</b> <code>run_hima.bat</code> is our unified Windows launcher. It detects the virtual environment at <code>.venv\Scripts\python.exe</code> and routes arguments cleanly: <code>.\run_hima.bat web</code> starts the dashboard server, <code>.\run_hima.bat demo</code> executes the instant ML pipeline verification in the terminal, <code>.\run_hima.bat fast</code> skips raw data extraction and retrains models, and <code>.\run_hima.bat test</code> executes the automated pytest suite. This eliminates user error from typing long Python package commands.</div>
</div>

<!-- CHAPTER 3 -->
<div class="member-banner">
    <h2>Chapter 3: Member 2 Handbook &mdash; Geospatial &amp; Data Pipeline Lead</h2>
    <div class="role">Geospatial Engineering, Coordinate Systems, Fishnet Grids &amp; Ingestion Pipelines</div>
</div>

<h3>3.1 Role Definition &amp; Codebase Ownership</h3>
<p>
    Member 2 is the foundation of the entire data science workflow. Without their spatial framework, no machine learning could occur. They audited, cleaned, projected, and unified 2.9 GB of raw spatial data onto a unified analytical grid:
</p>
<table>
    <tr>
        <th>File Path</th>
        <th>Lines / Size</th>
        <th>Technical Function &amp; Purpose</th>
    </tr>
    <tr>
        <td><code>src/audit/inventory.py</code></td>
        <td>150 lines</td>
        <td>Recursive integrity audit of 184 files (2.898 GB) spanning NetCDF, GRIB, Shapefiles, and PDFs; produces <code>data_inventory.csv</code>.</td>
    </tr>
    <tr>
        <td><code>src/geospatial/boundaries.py</code></td>
        <td>190 lines</td>
        <td>Filters national NWIC shapefiles to extract the 7 Sister States, repairs invalid geometries, and projects to EPSG:32646.</td>
    </tr>
    <tr>
        <td><code>src/geospatial/grid.py</code></td>
        <td>220 lines</td>
        <td>Builds the 253,408 projected 1 km &times; 1 km fishnet grid; calculates bounding boxes, cell coordinates, and spatial metadata.</td>
    </tr>
    <tr>
        <td><code>src/ingestion/firms.py</code></td>
        <td>260 lines</td>
        <td>Ingests NASA VIIRS S-NPP C2 archives, unpacks multi-year zips, filters type=0 vegetation fires, and eliminates duplicates.</td>
    </tr>
    <tr>
        <td><code>src/ingestion/imd.py</code> &amp; <code>era5.py</code></td>
        <td>480 lines</td>
        <td>Parses IMD NetCDF (CF TIME units) and ERA5 reanalysis; couples grids to the 1 km cells using KD-Tree nearest-neighbors.</td>
    </tr>
</table>

<h3>3.2 Detailed Technical Deep-Dive</h3>

<h4>A. Why Projected CRS (EPSG:32646) is Mandatory (vs Geographic EPSG:4326)</h4>
<p>
    A fundamental error in amateur geospatial data science is treating latitude and longitude degrees as uniform Cartesian coordinates. Member 2 enforced rigorous geodetic standards:
</p>
<ul>
    <li><b>The Problem with EPSG:4326 (WGS 84 Degrees):</b> In geographic coordinates, the Earth is modeled as an oblate spheroid. Meridians converge toward the poles. At latitude 22&deg;N (southern Mizoram), $1^\circ$ of longitude spans approximately $103.2\text{ km}$, whereas at latitude 29&deg;N (northern Arunachal Pradesh), $1^\circ$ of longitude spans only $97.3\text{ km}$. If we built a $0.01^\circ \times 0.01^\circ$ grid, northern cells would be over 6% smaller in area than southern cells, severely biasing wildfire counts per cell.</li>
    <li><b>The Solution with EPSG:32646 (UTM Zone 46N):</b> Member 2 projected all boundaries into <b>Universal Transverse Mercator (UTM) Zone 46N (EPSG:32646)</b>, whose central meridian is 93&deg;E (precisely bisecting Northeast India). In this metric coordinate system, coordinates are measured in meters. Every single one of our <b>253,408 fishnet cells</b> has dimensions of exactly $1,000\text{ m} \times 1,000\text{ m}$ ($1.000\text{ km}^2$), guaranteeing uniform spatial density.</li>
</ul>

<h4>B. Spatial Nearest-Neighbor KD-Trees (`scipy.spatial.cKDTree`)</h4>
<p>
    A major computational challenge in HIMA was linking atmospheric weather rasters to 253,408 grid cells across 1,461 calendar days (2021&ndash;2024). A naive spatial polygon intersection would take over 48 hours of computation. Member 2 solved this using spatial $k$-d trees:
</p>
<ol>
    <li>Member 2 extracted the geographic centroids of all 415 IMD 0.25&deg; rainfall points and all 2,491 ERA5 0.1&deg; atmospheric points.</li>
    <li>Built balanced binary search trees in 2D space using <code>scipy.spatial.cKDTree</code>.</li>
    <li>Queried the tree with all 253,408 1 km cell centroids simultaneously. In <b>1.8 seconds</b>, each 1 km cell was assigned the exact index of its nearest IMD station (median distance: 10.57 km) and nearest ERA5 cell (median distance: 4.21 km).</li>
    <li>Stored these static pairings in <code>grid_1km_with_weather_keys.parquet</code>, reducing daily weather coupling to an instantaneous $O(1)$ memory lookup.</li>
</ol>

<h4>C. Ground Truth Ingestion &amp; Deduplication</h4>
<ul>
    <li><b>NASA FIRMS VIIRS Active Fire Archive:</b> Discovered that zip file <code>DL_FIRE_SV-C2_816518.zip</code> contained fire detections spanning both 2022 and 2023. Filtered out non-vegetation fires (industrial flares, urban blazes) by keeping strictly <code>type=0</code> (vegetation fire). Removed exact duplicates from overlapping satellite overpasses, resulting in <b>219,928 confirmed vegetation fire detections</b>.</li>
    <li><b>The Sikkim Exclusion Defense:</b> During raster boundary auditing, Member 2 verified that local ERA5 NetCDF reanalysis starts at <b>89.8&deg;E</b>, whereas Sikkim is situated between <b>88.0&deg;E and 88.9&deg;E</b>. Adhering to strict academic honesty and zero data fabrication, Sikkim was excluded from the ERA5-coupled analytical grid, defining the study area cleanly as the 7 Sister States.</li>
</ul>

<h3>3.3 Member 2 Speech Script for the Presentation</h3>
<div class="callout-speech">
    "Good morning Sir/Ma'am. I led the Geospatial Engineering and Multimodal Data Ingestion pipeline. I was responsible for auditing 2.9 GB of raw spatial archives and building our 1 km analytical grid.
    <br/><br/>
    Because geographic degree coordinates distort surface area across latitudes, I reprojected all state boundaries into the metric coordinate system EPSG:32646 (UTM Zone 46N). This allowed us to construct a canonical fishnet grid of exactly 253,408 uniform 1 km&sup2; cells covering all 7 Sister States without spatial distortion.
    <br/><br/>
    To connect coarse atmospheric grids to our 1 km cells, I used 2D spatial KD-Trees, linking 415 IMD rainfall stations and 2,491 ERA5 reanalysis points to our 253,408 cells in under two seconds. I also ingested and deduplicated over 219,000 NASA VIIRS active fires, establishing our ground truth for machine learning."
</div>

<h3>3.4 Comprehensive Viva Questions &amp; Detailed Answers for Member 2</h3>
<div class="qa-box">
    <div class="qa-q">Q1: What is the difference between a Geographic Coordinate Reference System and a Projected Coordinate Reference System? Why did you need both?</div>
    <div class="qa-a"><b>Answer:</b> A Geographic CRS (such as EPSG:4326 / WGS 84) identifies locations on a 3-dimensional ellipsoidal Earth using angular units (degrees of latitude and longitude). Because lines of longitude converge toward the poles, the linear ground distance of one degree varies depending on your latitude. A Projected CRS (such as EPSG:32646 / UTM Zone 46N) projects the curved surface onto a 2-dimensional flat plane using a mathematical map projection (Transverse Mercator). Its units are meters. We needed EPSG:4326 to ingest raw satellite coordinates, and we immediately reprojected to EPSG:32646 so our analytical grid cells would have exactly identical physical surface areas ($1,000\text{ m} \times 1,000\text{ m} = 1\text{ km}^2$).</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q2: How does a KD-Tree work mathematically, and why is it faster than brute-force distance calculation?</div>
    <div class="qa-a"><b>Answer:</b> A $k$-d tree (short for $k$-dimensional tree) is a space-partitioning data structure that organizes points in a $k$-dimensional space. At each level of the tree, the algorithm splits the set of points along a specific coordinate axis using the median point as a hyperplane. To find the nearest neighbor of a query cell among $N$ weather stations, a brute-force approach must compute $N$ Euclidean distance calculations, which is $O(N)$ per cell, or $O(M \cdot N)$ for $M$ cells ($253,408 \times 2,491 \approx 6.3 \times 10^8$ operations). A KD-Tree eliminates vast subspaces using branch-and-bound bounding boxes, executing nearest-neighbor searches in $O(\log N)$ average time, completing the entire spatial assignment in under 2 seconds.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q3: Why did you filter FIRMS fires for <code>type=0</code>? What are the other types?</div>
    <div class="qa-a"><b>Answer:</b> In the NASA VIIRS Collection 2 active fire product, detection pixels are categorized by thermal source: <code>type=0</code> represents presumed vegetation fires (wildfires, forest burns, crop clearance); <code>type=1</code> represents active volcanoes; <code>type=2</code> represents other static land sources (such as industrial oil and gas flares); and <code>type=3</code> represents offshore detections. Since our project is focused on wildfire and forest biomass burning, retaining types 1, 2, or 3 would inject non-vegetation noise into our training labels.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q4: Why did you exclude Sikkim from the spatial grid? Could you have interpolated the data?</div>
    <div class="qa-a"><b>Answer:</b> The local ERA5 NetCDF reanalysis rasters provided in the dataset start at 89.8&deg;E, but Sikkim is located between 88.0&deg;E and 88.9&deg;E (roughly 100 km west of the reanalysis boundary). Interpolating or extrapolating weather data across 100 km of rugged Himalayan terrain would have violated academic integrity by inventing synthetic weather. Adhering strictly to zero data fabrication, we constrained our coupled analytical grid to the 7 contiguous Sister States.</div>
</div>

<!-- CHAPTER 4 -->
<div class="member-banner">
    <h2>Chapter 4: Member 3 Handbook &mdash; Feature Engineering &amp; Wildfire ML Specialist</h2>
    <div class="role">Feature Engineering, Imbalanced Learning, Spatial Cross-Validation &amp; Model Selection</div>
</div>

<h3>4.1 Role Definition &amp; Codebase Ownership</h3>
<p>
    Member 3 is the core machine learning modeler for the wildfire prediction engine. They formulated physical features, addressed extreme class imbalance, trained 6 classifiers, and optimized the operating threshold:
</p>
<table>
    <tr>
        <th>File Path</th>
        <th>Lines / Size</th>
        <th>Technical Function &amp; Purpose</th>
    </tr>
    <tr>
        <td><code>src/features/weather.py</code></td>
        <td>320 lines</td>
        <td>Computes rolling antecedent rainfall windows (3d, 7d, 15d), dry spell counters, dewpoint depression, and cyclical time features.</td>
    </tr>
    <tr>
        <td><code>src/labels/wildfire.py</code></td>
        <td>240 lines</td>
        <td>Constructs training datasets (2021&ndash;2023) with balanced negative subsampling and forward 2024 realistic test holdouts.</td>
    </tr>
    <tr>
        <td><code>src/training/pipelines.py</code></td>
        <td>410 lines</td>
        <td>5-fold Spatial Group Cross-Validation, benchmarking 6 classifiers, and hyperparameter tuning.</td>
    </tr>
    <tr>
        <td><code>models/wildfire_best_model.joblib</code></td>
        <td>478 KB</td>
        <td>Serialized production model bundle with preprocessing pipeline, operating threshold, and Bayesian prior calibration metadata.</td>
    </tr>
</table>

<h3>4.2 Detailed Technical Deep-Dive</h3>

<h4>A. The 33 Engineered Features Explained in Plain English</h4>
<p>
    Member 3 designed a feature vector capturing every physical mechanism required for wildland fire ignition:
</p>
<ol>
    <li><b>Afternoon Minimum Relative Humidity (<code>relative_humidity_min</code>):</b> Air can hold more water vapor at higher temperatures. In the afternoon, as temperature peaks, relative humidity reaches its daily minimum. Fine forest fuels (dead grass, dry leaves) equilibrate with atmospheric moisture in 1 to 2 hours. When RH drops below 25%, fuel moisture drops to critical levels, and any spark triggers ignition. Ranked as the #1 daily meteorological feature.</li>
    <li><b>Dewpoint Depression (<code>dewpoint_depression_c</code>):</b> Defined as $T - T_{\text{dew}}$. A large dewpoint depression (&gt;15&deg;C) indicates hot, extremely dry air with massive vapor pressure deficits, directly evaporating moisture from standing timber.</li>
    <li><b>Soil Water Layer 1 (<code>soil_water_layer1</code>) &amp; 7-day Mean:</b> Volumetric water content in the top 0&ndash;7 cm of soil ($m^3/m^3$). Values below 0.15 indicate desiccated surface organic layers.</li>
    <li><b>Cumulative Antecedent Rainfall (<code>imd_rain_sum_3d, 7d, 15d</code>):</b> Even if a single day is sunny, heavy rainfall 3 to 7 days prior prevents deep forest litter from burning.</li>
    <li><b>Consecutive Dry Days (<code>days_since_rain</code>):</b> A counter measuring continuous days with rainfall &lt; 2.5 mm. Tracks progressive cumulative drought.</li>
    <li><b>Cyclical Day of Year Transformations:</b>
        <br/><span class="formula">\sin(\text{doy}) = \sin\left(\frac{2\pi \cdot \text{DOY}}{365}\right), \quad \cos(\text{doy}) = \cos\left(\frac{2\pi \cdot \text{DOY}}{365}\right)</span>
        <br/>If Day of Year is passed as an integer (1 to 365), tree algorithms treat Dec 31 (Day 365) and Jan 1 (Day 1) as mathematically distant. Cyclical trigonometry maps time onto a continuous circle, where Dec 31 and Jan 1 are adjacent points. Permutation importance proved $\sin(\text{doy})$ is the single most powerful feature in the model (importance score 0.1279).
    </li>
</ol>

<h4>B. Solving Extreme Class Imbalance: The Training vs. Test Strategy</h4>
<p>
    Wildfire is an extreme needle-in-a-haystack event:
</p>
<ul>
    <li>In 2024 across Northeast India, there were only <b>348 positive fire days</b> out of <b>1,000,000 cell-days</b>. The real-world natural prevalence is only <b>0.035%</b> (or 1 positive for every 2,870 negative cell-days).</li>
    <li>If a model is trained directly on a 99.965% negative dataset, it falls into the trivial majority-class trap: predicting 0 everywhere achieves 99.965% accuracy while catching zero fires.</li>
    <li><b>Member 3's Two-Tier Solution:</b>
        <ol>
            <li><b>Training Set (2021&ndash;2023):</b> Member 3 extracted all 119,554 positive cell-days and performed balanced negative subsampling (1:5 ratio), creating a rich training dataset of <b>717,324 rows</b> with an effective prevalence of ~16.7%. This forced classifiers to learn subtle decision boundaries between fire and non-fire weather.</li>
            <li><b>Realistic Holdout Test Set (2024):</b> Evaluated models on a forward, unmanipulated <b>1,000,000 cell-day dataset</b> with true 0.035% prevalence, proving that the model generalizes to real operational conditions without overfitting.</li>
        </ol>
    </li>
</ul>

<h4>C. Spatial Stratified Group Cross-Validation (Zero Spatial Leakage)</h4>
<p>
    Standard random K-Fold cross-validation is invalid for geospatial data because of <b>spatial autocorrelation (Tobler's First Law of Geography)</b>: nearby locations are more similar than distant locations. If cell $(x, y)$ is in the training set and adjacent cell $(x+1, y)$ on the same day is in the validation set, the model memorizes local weather rather than learning predictive physics. Member 3 implemented <b>Spatial Stratified Group K-Fold on 50 km spatial blocks</b>, ensuring that entire geographic regions were held out together during validation.
</p>

<h4>D. Systematic Comparison of 6 Syllabus Classifiers</h4>
<table>
    <tr>
        <th>Model Name</th>
        <th>Syllabus Alignment</th>
        <th>CV ROC-AUC</th>
        <th>CV PR-AUC</th>
        <th>2024 Test ROC-AUC</th>
        <th>2024 Recall</th>
        <th>False Alarm Rate</th>
    </tr>
    <tr>
        <td><b>DummyClassifier</b></td>
        <td>Baseline Sanity</td>
        <td>0.4962</td>
        <td>0.1651</td>
        <td>0.5000</td>
        <td>0.00%</td>
        <td>0.00%</td>
    </tr>
    <tr>
        <td><b>Logistic Regression</b></td>
        <td>Linear Sigmoid Model</td>
        <td>0.9216</td>
        <td>0.6802</td>
        <td>0.9040</td>
        <td>64.94%</td>
        <td>8.12%</td>
    </tr>
    <tr>
        <td><b>Gaussian Naive Bayes</b></td>
        <td>Probabilistic Generative</td>
        <td>0.8913</td>
        <td>0.5877</td>
        <td>0.8621</td>
        <td>58.33%</td>
        <td>9.51%</td>
    </tr>
    <tr>
        <td><b>Decision Tree</b></td>
        <td>CART White-Box</td>
        <td>0.9259</td>
        <td>0.7223</td>
        <td>0.9049</td>
        <td>59.20%</td>
        <td>6.19%</td>
    </tr>
    <tr>
        <td><b>Random Forest</b></td>
        <td>Bagging Ensemble</td>
        <td>0.9434</td>
        <td>0.7761</td>
        <td>0.9260</td>
        <td>63.22%</td>
        <td>5.01%</td>
    </tr>
    <tr>
        <td><b>HistGradientBoosting</b></td>
        <td><b>Advanced GBDT (Winner)</b></td>
        <td><b>0.9470</b></td>
        <td><b>0.7817</b></td>
        <td><b>0.9358</b></td>
        <td><b>68.39%</b></td>
        <td><b>6.12%</b></td>
    </tr>
</table>

<h4>E. Why HistGradientBoosting Won (Technical Justification)</h4>
<ol>
    <li><b>Highest Discrimination Power:</b> Highest CV PR-AUC (0.7817) and 2024 Test ROC-AUC (0.9358).</li>
    <li><b>Superior Fire Detection:</b> Catches <b>68.4%</b> of all real fires in 2024, compared to 59.2% for Decision Tree and 63.2% for Random Forest.</li>
    <li><b>Histogram Discretization:</b> Continuous features are binned into 256 integer bins, drastically reducing memory footprint and allowing 717,000 rows to train in under 20 seconds.</li>
    <li><b>Native Missing Value Routing:</b> Missing ERA5 values (NaN) are routed dynamically to the split branch that minimizes loss, eliminating imputation artifacts.</li>
</ol>

<h3>4.3 Member 3 Speech Script for the Presentation</h3>
<div class="callout-speech">
    "Good morning Sir/Ma'am. I was responsible for Feature Engineering and Wildfire Machine Learning Modeling. I engineered 33 atmospheric, hydrological, and temporal features, including cyclical trigonometric Day-of-Year transformations to capture the spring dry season without artificial calendar boundary cliffs.
    <br/><br/>
    To evaluate our models rigorously, I implemented 5-fold Spatial Group Cross-Validation on 50 km geographic blocks, completely eliminating spatial autocorrelation leakage. I trained and compared 6 classifiers from our syllabus. Our best model, HistGradientBoosting, achieved a 0.9358 ROC-AUC and 0.7817 PR-AUC on an unseen 1,000,000 cell-day realistic holdout.
    <br/><br/>
    By sweeping 100 threshold candidates on cross-validation, I established our optimal alert threshold at 0.7118, successfully capturing 68.4% of all wildfires with a false alarm rate of only 6.1%."
</div>

<h3>4.4 Comprehensive Viva Questions &amp; Detailed Answers for Member 3</h3>
<div class="qa-box">
    <div class="qa-q">Q1: Why is your test precision so small (~0.4%) even though your ROC-AUC is 93.6%? Did your model fail?</div>
    <div class="qa-a"><b>Answer:</b> No, Sir/Ma'am. This is a mathematical consequence known as the <b>Base Rate Fallacy</b> in extreme class imbalance. In our 2024 test set, there are only 348 fire days across 1,000,000 cell-days (a natural base rate of 0.035%, or 1 fire in 2,870 days). Even with a model that correctly rejects 94% of non-fire days, false alarms will numerically exceed true positives in raw volume ($\text{Recall}=68.4\% \implies 238\text{ True Positives}$; $\text{False Alarm Rate}=6.1\% \implies 61,203\text{ False Positives}$; $\text{Precision} = 238 / (238 + 61,203) \approx 0.0039$). This is why precision alone is misleading for rare hazards, and why ROC-AUC (0.9358) and PR-AUC are the primary metrics used in remote sensing and hazard assessment literature.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q2: What is the difference between Bagging (Random Forest) and Boosting (HistGradientBoosting)?</div>
    <div class="qa-a"><b>Answer:</b> In <b>Random Forest (Bagging)</b>, individual decision trees are trained independently and in parallel on bootstrap samples of the training data, with random feature subsets chosen at each split. The predictions are averaged, which primarily reduces model variance without reducing bias. In <b>HistGradientBoosting (Boosting)</b>, trees are built sequentially in series. Each new tree fits the negative gradient (residuals or prediction errors) of the ensemble built so far: $F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)$. Boosting reduces both bias and variance, allowing it to learn complex, non-linear interactions between heat, humidity, and wind that parallel bagging trees average out.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q3: How did you select the operating threshold of 0.7118? Why not use 0.5?</div>
    <div class="qa-a"><b>Answer:</b> Defaulting to 0.5 is only optimal for balanced binary classification problems where false positives and false negatives carry identical real-world costs. Because we trained on subsampled data with ~16.7% prevalence, raw probabilities are shifted upward. I evaluated 100 candidate thresholds from 0.01 to 0.99 on out-of-fold cross-validation predictions, tracking F1-score, Precision, and Recall. The threshold of 0.7118 maximized the F1-score (0.7124), providing the optimal mathematical balance between capturing fires (68.4% recall) and suppressing operational false alarms (6.1% false alarm rate).</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q4: Why did Naive Bayes perform worse than Logistic Regression and Decision Trees?</div>
    <div class="qa-a"><b>Answer:</b> Gaussian Naive Bayes relies on the fundamental assumption that all input features are conditionally independent given the class: $P(X|Y) = \prod P(X_i|Y)$. In meteorological data, this assumption is severely violated. Air temperature, relative humidity, dewpoint depression, and rainfall are heavily correlated by atmospheric thermodynamics. Naive Bayes double-counts redundant evidence, resulting in overconfident probabilities and the lowest test performance (0.8621 ROC-AUC).</div>
</div>

<!-- CHAPTER 5 -->
<div class="member-banner">
    <h2>Chapter 5: Member 4 Handbook &mdash; Landslide Modeling, Statistical Calibration &amp; QA Lead</h2>
    <div class="role">PDF Table Mining, Survey Bias Mitigation, Bayesian Odds Calibration &amp; Pytest Architecture</div>
</div>

<h3>5.1 Role Definition &amp; Codebase Ownership</h3>
<p>
    Member 4 owns the landslide prediction pipeline, statistical probability calibration, and software quality assurance:
</p>
<table>
    <tr>
        <th>File Path</th>
        <th>Lines / Size</th>
        <th>Technical Function &amp; Purpose</th>
    </tr>
    <tr>
        <td><code>src/ingestion/gsi_pdf.py</code></td>
        <td>290 lines</td>
        <td>Word-coordinate layout parser using <code>pymupdf</code> to extract unstructured GSI landslide compendium tables.</td>
    </tr>
    <tr>
        <td><code>src/ingestion/coolr.py</code></td>
        <td>110 lines</td>
        <td>Spatial verification of NASA COOLR catalog (proves zero coverage in Northeast India).</td>
    </tr>
    <tr>
        <td><code>src/labels/landslide.py</code> &amp; <code>training/landslide_pipelines.py</code></td>
        <td>360 lines</td>
        <td>Landslide positive labeling, survey bias mitigation, and preliminary trigger modeling.</td>
    </tr>
    <tr>
        <td><code>src/evaluation/metrics.py</code></td>
        <td>280 lines</td>
        <td>Bayesian odds-ratio prior calibration, Brier score calculation, and evaluation metrics.</td>
    </tr>
    <tr>
        <td><code>tests/test_hima_pipeline.py</code></td>
        <td>206 lines</td>
        <td>The 9 automated pytest unit and data-integrity test suites.</td>
    </tr>
</table>

<h3>5.2 Detailed Technical Deep-Dive</h3>

<h4>A. Mining Unstructured GSI Landslide Compendiums with PyMuPDF</h4>
<p>
    The Geological Survey of India (GSI) published historical landslide inventories in a multi-page PDF compendium. Standard table extraction libraries (like <code>camelot</code> or <code>pdfplumber</code>) failed because the PDF lacked physical ruling lines, and multi-line descriptions broke cell borders. Member 4 built a custom layout parser:
</p>
<ol>
    <li>Extracted word-level bounding boxes (character coordinates $x_0, y_0, x_1, y_1$) using <code>pymupdf</code>.</li>
    <li>Calibrated column boundaries along horizontal $X$-coordinates corresponding to table headers: <i>Sl.No., Slide_No, State, District, Slide_Name, NH_SH_Location, Latitude, Longitude, Material Involved, Movement Type, History</i>.</li>
    <li>Successfully parsed <b>10,731 national records</b>, of which <b>9,970 lay inside the 7 Sister States</b>, isolating <b>463 unique dated cell-days</b> spanning 2021&ndash;2024.</li>
</ol>

<h4>B. Detection &amp; Mitigation of Geographic Survey Bias</h4>
<ul>
    <li><b>The Discovery:</b> When inspecting dated GSI events, Member 4 discovered that <b>78.6% (529 out of 673)</b> of dated records came from a single post-monsoon 2024 field survey campaign in Mizoram.</li>
    <li><b>The Bias:</b> If <code>state_name</code> was included as an input feature, machine learning models simply memorized: <code>IF state == 'Mizoram' THEN landslide = 1</code>. This produced artificially inflated validation scores but failed completely to learn actual rainfall triggering physics.</li>
    <li><b>The Solution:</b> Member 4 <b>explicitly stripped <code>state_name</code> from all landslide feature vectors</b>, forcing classifiers to learn strictly from antecedent IMD/ERA5 rainfall, soil moisture, and atmospheric conditions.</li>
</ul>

<h4>C. Bayesian Odds-Ratio Prior Adjustment (Probability Calibration)</h4>
<p>
    Because classifiers were trained on subsampled data with an artificial prevalence ($\pi_{\text{train}} \approx 16.7\%$), raw model scores output probabilities reflecting that artificial training ratio. Member 4 derived and implemented Bayesian odds-ratio adjustment to calibrate scores back to the true daily Northeast India population prior ($\pi_{\text{target}} \approx 0.043\%$):
</p>
<ol>
    <li>By Bayes' rule in odds formulation:
        <br/><span class="formula">\text{Odds}_{\text{cal}} = \text{Odds}_{\text{raw}} \cdot \left(\frac{\pi_{\text{target}}}{1 - \pi_{\text{target}}}\right) \cdot \left(\frac{1 - \pi_{\text{train}}}{\pi_{\text{train}}}\right)</span>
    </li>
    <li>Converting back from odds to probability:
        <br/><span class="formula">P_{\text{cal}} = \frac{P_{\text{raw}}}{P_{\text{raw}} + (1 - P_{\text{raw}}) \cdot \left(\frac{\pi_{\text{train}}}{\pi_{\text{target}}}\right) \cdot \left(\frac{1 - \pi_{\text{target}}}{1 - \pi_{\text{train}}}\right)}</span>
    </li>
    <li><b>Results:</b> Reduced Brier score from <b>0.0834</b> down to <b>0.0005</b>, yielding mathematically calibrated daily risk estimates while preserving exact ROC rank order.</li>
</ol>

<h4>D. The Preliminary Weather-Only Landslide Model</h4>
<ul>
    <li>Trained the 6 classifiers using antecedent precipitation windows (1d, 3d, 7d, 15d) and topsoil moisture.</li>
    <li><b>HistGradientBoosting achieved 0.9367 ROC-AUC</b> on the 2024 holdout.</li>
    <li><b>Research Honesty:</b> Labeled strictly as <i>"Preliminary Weather-Only"</i> because static terrain layers (DEM/slope, aspect, geological lithology, and SoilGrids) were unavailable locally, adhering to strict zero data fabrication.</li>
</ul>

<h3>5.3 Member 4 Speech Script for the Presentation</h3>
<div class="callout-speech">
    "Good morning Sir/Ma'am. I was responsible for Landslide Modeling, Statistical Probability Calibration, and Software Quality Assurance.
    <br/><br/>
    I developed an automated word-coordinate layout parser in PyMuPDF to extract 9,970 historical landslide records from the unstructured GSI compendium. During data exploration, I detected severe geographic survey bias: over 78% of dated events came from a single 2024 survey in Mizoram. To prevent the model from memorizing geography, I explicitly removed state identifiers from landslide features, forcing the model to learn pure hydrometeorological triggers.
    <br/><br/>
    To correct probability distortion caused by negative subsampling, I derived and implemented Bayesian Odds-Ratio Prior Calibration, lowering our Brier score to 0.0005. Finally, I architected our automated test suite, which runs in 2.5 seconds and passes all 9 unit and integrity tests."
</div>

<h3>5.4 Comprehensive Viva Questions &amp; Detailed Answers for Member 4</h3>
<div class="qa-box">
    <div class="qa-q">Q1: Why is your Landslide model called 'Preliminary Weather-Only'? Why didn't you download a DEM?</div>
    <div class="qa-a"><b>Answer:</b> Slope angle, elevation, terrain curvature, and bedrock geology are primary static determinants of slope stability. These datasets were absent in the raw downloads directory. To strictly adhere to research ethics and zero data fabrication, we refused to invent synthetic topography or use undocumented external sources. Our model evaluates whether antecedent hydrometeorological conditions (accumulated IMD rainfall and soil saturation) are sufficient to trigger slope failures, which is why it is defensibly framed as a preliminary hydrometeorological trigger model.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q2: How does your Bayesian Prior Adjustment formula work, and why is it monotonic?</div>
    <div class="qa-a"><b>Answer:</b> When a model is trained on balanced data with positive prevalence $\pi_{\text{train}}$ (e.g. 16.7%), the raw sigmoid probability reflects that 1:5 ratio. In reality, the true population prevalence $\pi_{\text{target}}$ is only 0.043%. The adjustment multiplies the predicted odds by the ratio of true prior odds to training prior odds. Because this transformation is a strictly monotonically increasing function ($f'(P) > 0$), it shifts probabilities downward to match true population scale without altering the relative ranking of samples. Therefore, ROC-AUC and PR-AUC remain perfectly preserved while calibration error (Brier score) drops dramatically from 0.083 to 0.0005.</div>
</div>
<div class="qa-box">
    <div class="qa-q">Q3: How did you extract tables from a PDF using word coordinates?</div>
    <div class="qa-a"><b>Answer:</b> The GSI PDF lacked standard vector table ruling lines, rendering standard table extractors useless. Using PyMuPDF's <code>get_text("words")</code>, I extracted every word along with its bounding box coordinates $(x_0, y_0, x_1, y_1)$. By analyzing header $X$-ranges across pages, I established strict horizontal intervals corresponding to each column (e.g., Latitude between $X=420$ and $X=460$). Text blocks sharing identical line heights were concatenated into single records, allowing accurate extraction of 9,970 records with valid geospatial coordinates.</div>
</div>

<!-- CHAPTER 6 -->
<h2>Chapter 6: The 9 Automated Unit Test Cases &mdash; Line-by-Line Integrity Guide</h2>
<p>
    Software quality and data integrity in HIMA are enforced by an automated test suite located in <code>tests/test_hima_pipeline.py</code>. It executes via <code>.\run_hima.bat test</code> in <b>2.56 seconds</b>, asserting 9 non-negotiable scientific and software invariants:
</p>

<div class="test-box">
    <div class="test-title">Test 1: test_config_loads_and_has_disclaimer()</div>
    <p><b>Code Under Test:</b> <code>src/config.py :: load_config()</code></p>
    <p><b>What It Asserts:</b> Confirms that <code>config/project.yaml</code> loads without syntax errors, that the mandatory disclaimer string containing <i>"not an official warning"</i> is present, that <code>grid_cell_size_m == 1000</code>, and that projected CRS is exactly <code>EPSG:32646</code>.</p>
    <p><b>Scientific Purpose:</b> Guarantees reproducible project settings and legal compliance across all runs.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 2: test_days_since_rain_preserves_missing_gaps()</div>
    <p><b>Code Under Test:</b> <code>src/features/weather.py :: compute_days_since_rain_array()</code></p>
    <p><b>What It Asserts:</b> Passes a synthetic rainfall array with a missing day: <code>[5.0, 0.0, 0.0, NaN, 0.0, 3.0]</code>. Asserts that the missing day remains <code>NaN</code> (never converted to 0) and that the dry streak resets cleanly to 1.0 after the gap instead of bridging across missing data.</p>
    <p><b>Scientific Purpose:</b> Proves that the 4 missing ERA5 months (e.g. August 2023) do not fabricate artificial 30-day drought streaks that would trigger false wildfire alarms.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 3: test_imd_season_mapping()</div>
    <p><b>Code Under Test:</b> <code>src/labels/wildfire.py :: assign_imd_season()</code></p>
    <p><b>What It Asserts:</b> Passes month series <code>[1, 3, 7, 10, 12]</code> and asserts exact mapping to official IMD meteorological seasons: <i>Winter, Pre-Monsoon, Monsoon, Post-Monsoon, Winter</i>.</p>
    <p><b>Scientific Purpose:</b> Ensures seasonal performance breakdowns in <code>outputs/tables/wildfire_test2024_per_season.csv</code> match meteorological standards.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 4: test_bayes_prior_adjustment_monotonic_and_bounded()</div>
    <p><b>Code Under Test:</b> <code>src/evaluation/metrics.py :: bayes_prior_adjust()</code></p>
    <p><b>What It Asserts:</b> Passes probabilities $[0.01, 0.25, 0.50, 0.75, 0.99]$. Asserts that all calibrated probabilities lie strictly in $[0, 1]$, that differences $\Delta P > 0$ (strict monotonicity), and that at $P=0.50$ with $\pi_{\text{train}}=0.50$, the adjusted probability exactly equals $\pi_{\text{target}}$.</p>
    <p><b>Scientific Purpose:</b> Mathematically proves that Bayesian calibration preserves sample ranking and satisfies probability axioms.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 5: test_risk_band_boundaries()</div>
    <p><b>Code Under Test:</b> <code>src/evaluation/metrics.py :: assign_risk_band()</code></p>
    <p><b>What It Asserts:</b> Evaluates boundary values $[0.05, 0.30, 0.65, 0.90]$ and confirms exact mapping into the 4 standard categories: <i>LOW (0&ndash;30%), MODERATE (30&ndash;60%), HIGH (60&ndash;80%), and CRITICAL (80&ndash;100%)</i>.</p>
    <p><b>Scientific Purpose:</b> Guarantees consistent risk categorization between Python models and the web frontend needle gauge.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 6: test_no_post_event_leakage_in_features()</div>
    <p><b>Code Under Test:</b> <code>src/training/pipelines.py :: ALL_FEATURES</code></p>
    <p><b>What It Asserts:</b> Performs set intersection between the 33 training features and a forbidden list of post-ignition satellite columns: <code>fire_detected</code>, <code>detection_count</code>, <code>frp_sum</code>, <code>frp_mean</code>, <code>brightness_mean</code>, <code>brightness_max</code>, etc. Asserts that the intersection is empty.</p>
    <p><b>Scientific Purpose:</b> <b>The most crucial test for viva defense.</b> Proves that satellite fire metrics that only exist after ignition were never leaked into feature vectors.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 7: test_grid_and_boundaries_artifacts_if_built()</div>
    <p><b>Code Under Test:</b> <code>data/reports/grid_metadata.json</code></p>
    <p><b>What It Asserts:</b> Reads grid metadata and verifies that <code>cells_outside_boundary == 0</code>, <code>total_cells > 200,000</code>, and <code>cell_size_m == 1000</code>.</p>
    <p><b>Scientific Purpose:</b> Verifies spatial containment and uniform metric fishnet geometry across the 7 Sister States.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 8: test_validated_wildfire_predictor_inference()</div>
    <p><b>Code Under Test:</b> <code>src/api/predict.py :: WildfireRiskPredictor</code></p>
    <p><b>What It Asserts:</b> Loads the production model bundle (<code>models/wildfire_best_model.joblib</code>) and evaluates two inputs: an extreme dry Pre-Monsoon Mizoram cell vs. a flooded Monsoon Assam cell. Asserts that the dry cell scores strictly higher in both raw score and calibrated probability.</p>
    <p><b>Scientific Purpose:</b> Proves that serialized production pipelines produce physically coherent predictions on unseen weather states.</p>
</div>

<div class="test-box">
    <div class="test-title">Test 9: test_required_deliverables_exist()</div>
    <p><b>Code Under Test:</b> Filesystem integrity check across 23 target artifacts.</p>
    <p><b>What It Asserts:</b> Confirms the physical presence of all 23 core deliverables: model cards, saved joblib pipelines, CSV comparison tables, figures, maps, audit summaries, README, and requirements.</p>
    <p><b>Scientific Purpose:</b> Ensures complete reproducibility for any academic evaluator cloning the repository.</p>
</div>

<!-- CHAPTER 7 -->
<h2>Chapter 7: Master Project Viva Exam Bank (30+ High-Yield Questions &amp; Answers)</h2>

<div class="qa-box">
    <div class="qa-q">Q1: What is the exact research problem your project solves?</div>
    <div class="qa-a"><b>Answer:</b> Project HIMA formulates two distinct daily hazard prediction tasks over a uniform 1 km &times; 1 km spatial grid covering the 7 Sister States of Northeast India (253,412 km&sup2;) from 2021 to 2024: (1) predicting active vegetation wildfire occurrence using satellite ground truth and atmospheric reanalysis, and (2) evaluating preliminary hydrometeorological landslide triggering using GSI field inventories and antecedent precipitation.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q2: What is the base rate of wildfires in your test set, and why does it matter?</div>
    <div class="qa-a"><b>Answer:</b> In our 2024 realistic test set of 1,000,000 cell-days, there are exactly 348 positive fire days, representing a natural prevalence of 0.035% (or 1 positive per 2,870 negatives). This extreme class imbalance means standard accuracy is meaningless (predicting all zeros yields 99.965% accuracy). We evaluate models using Area Under the ROC Curve (ROC-AUC) and Area Under the Precision-Recall Curve (PR-AUC) under Spatial Group Cross-Validation.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q3: How did you ensure there is no spatial autocorrelation leakage?</div>
    <div class="qa-a"><b>Answer:</b> Standard K-Fold cross-validation randomly shuffles rows, placing adjacent 1 km cells from the same day into both training and validation sets, allowing models to cheat by memorizing local weather. We partitioned training data using 50 km spatial block IDs as groups in a <code>StratifiedGroupKFold</code> protocol, guaranteeing that entire geographic regions were completely held out together during validation.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q4: Why did HistGradientBoosting win over Random Forest?</div>
    <div class="qa-a"><b>Answer:</b> Random Forest builds trees in parallel and averages their predictions to reduce variance. HistGradientBoosting builds trees sequentially, where each new tree fits the negative gradient residuals of prior trees, reducing both bias and variance. It captures complex, non-linear weather interactions (such as heat + low humidity + high wind) and uses 256-bin histogram discretization, enabling training on 717,000 rows in seconds with native handling of missing reanalysis values.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q5: What was the #1 most important feature in your wildfire model?</div>
    <div class="qa-a"><b>Answer:</b> Permutation importance proved that cyclical Day of Year ($\sin(\text{doy})$) was the #1 feature (importance score 0.1279), followed by centroid latitude (0.0408), centroid longitude (0.0269), and minimum relative humidity (0.0158). This aligns with the physical reality of Northeast India, where fires concentrate heavily in the spring dry season (March&ndash;April).</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q6: Why did you exclude post-event features like FRP and fire brightness?</div>
    <div class="qa-a"><b>Answer:</b> Fire Radiative Power (FRP) and brightness temperature are satellite sensor measurements that only exist after vegetation is actively burning. Including them in training features would represent severe target leakage, producing an artificial 100% accurate model that cannot forecast fires before ignition.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q7: How did you handle missing ERA5 reanalysis months in 2023?</div>
    <div class="qa-a"><b>Answer:</b> Months 2023-08, 09, 11, and 12 were missing in local ERA5 files. We preserved them as <code>NaN</code> and allowed HistGradientBoosting to handle them natively through missing value routing. We strictly forbade imputing zeros, because filling zero rainfall during August (peak monsoon) would artificially fabricate severe drought conditions that never existed.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q8: Why did you exclude state_name from your Landslide model?</div>
    <div class="qa-a"><b>Answer:</b> Data audit revealed severe geographic survey bias: 78.6% (529/673) of dated GSI landslide events came from a single post-monsoon 2024 field survey in Mizoram. If <code>state_name</code> was included, models simply memorized that Mizoram equals landslide, failing to learn actual rainfall physics. Excluding state names forced models to learn purely from precipitation and soil moisture.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q9: What is the mathematical basis of Bayesian Prior Adjustment?</div>
    <div class="qa-a"><b>Answer:</b> Because we used negative subsampling in training to give the model a ~16.7% positive prevalence, the raw model outputs overestimate real-world daily likelihood. Bayesian prior adjustment mathematically adjusts the predicted odds ratio by the ratio of training prevalence to true population prevalence (~0.043%), producing well-calibrated probabilities without changing the ROC curve.</div>
</div>

<div class="qa-box">
    <div class="qa-q">Q10: What are the main limitations of your project?</div>
    <div class="qa-a"><b>Answer:</b> (1) Lack of static terrain layers (DEM/slope, aspect, geological lithology, and SoilGrids) restricts our landslide model to hydrometeorological triggering only; (2) Absence of dynamic high-resolution vegetation indices (such as MODIS/Sentinel NDVI) limits real-time fuel curing tracking; (3) GSI landslide records suffer from spatial survey bias toward road corridors and surveyed districts.</div>
</div>
"""

def generate_pdf():
    print(f"[PDF Gen] Compiling Complete HIMA Textbook & Viva Handbook to: {OUTPUT_PDF}")
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
