"""Generate HIMA Complete Project Study Guide and Viva Preparation PDF.

Creates a publication-quality study guide PDF covering:
- Project architecture, study area, and objective
- Dependent vs Independent variables
- Deep-dive into every single factor and slider in the dashboard
- All 6 ML classifiers explained + why HistGradientBoosting won
- Comprehensive viva / exam / teacher question bank with model answers
"""

from pathlib import Path
import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "HIMA_Project_Study_Guide_and_Viva_Prep.pdf"

CSS = """
@page {
    margin: 36pt 40pt 40pt 40pt;
}
body {
    font-family: helvetica, sans-serif;
    font-size: 9.5pt;
    line-height: 1.45;
    color: #1e293b;
}
.header-box {
    background-color: #0f172a;
    color: #ffffff;
    padding: 16pt 20pt;
    border-radius: 6pt;
    margin-bottom: 16pt;
}
.header-box h1 {
    font-size: 20pt;
    margin: 0 0 4pt 0;
    color: #f97316;
    letter-spacing: -0.5pt;
}
.header-box .sub {
    font-size: 10pt;
    color: #94a3b8;
    margin: 0;
}
.badge {
    background-color: #ea580c;
    color: #ffffff;
    padding: 2pt 6pt;
    border-radius: 3pt;
    font-size: 8pt;
    font-weight: bold;
    display: inline-block;
}
h2 {
    color: #0f172a;
    font-size: 13pt;
    border-bottom: 2pt solid #e2e8f0;
    padding-bottom: 4pt;
    margin-top: 18pt;
    margin-bottom: 8pt;
}
h3 {
    color: #0369a1;
    font-size: 10.5pt;
    margin-top: 12pt;
    margin-bottom: 4pt;
}
h4 {
    color: #334155;
    font-size: 9.5pt;
    margin-top: 8pt;
    margin-bottom: 2pt;
}
p {
    margin: 0 0 6pt 0;
}
ul, ol {
    margin: 0 0 8pt 18pt;
    padding: 0;
}
li {
    margin-bottom: 3pt;
}
.callout {
    background-color: #f8fafc;
    border-left: 3pt solid #3b82f6;
    padding: 8pt 12pt;
    margin: 8pt 0;
    border-radius: 0 4pt 4pt 0;
}
.callout-warn {
    background-color: #fffbeb;
    border-left: 3pt solid #f59e0b;
    padding: 8pt 12pt;
    margin: 8pt 0;
    border-radius: 0 4pt 4pt 0;
}
.callout-success {
    background-color: #f0fdf4;
    border-left: 3pt solid #22c55e;
    padding: 8pt 12pt;
    margin: 8pt 0;
    border-radius: 0 4pt 4pt 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 12pt 0;
    font-size: 8.5pt;
}
th, td {
    border: 1pt solid #cbd5e1;
    padding: 4.5pt 6pt;
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
    padding: 4pt 8pt;
    border-radius: 3pt;
    font-family: courier, monospace;
    font-size: 8.5pt;
    color: #0f172a;
    display: inline-block;
    margin: 2pt 0;
}
.qa-box {
    background-color: #f8fafc;
    border: 1pt solid #e2e8f0;
    border-radius: 4pt;
    padding: 8pt 10pt;
    margin-bottom: 10pt;
}
.qa-q {
    font-weight: bold;
    color: #0f172a;
    margin-bottom: 4pt;
}
.qa-a {
    color: #334155;
}
.code-tag {
    background-color: #e2e8f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
    font-family: courier, monospace;
    font-size: 8pt;
}
"""

HTML_CONTENT = r"""
<div class="header-box">
    <h1>HIMA Project Study Guide &amp; Viva Exam Prep</h1>
    <p class="sub"><b>Hazard Intelligence, Monitoring &amp; Assessment (Northeast India)</b> &bull; B.Tech AI-ML / Data Science Capstone (CSET312)</p>
    <p style="margin-top: 6pt; font-size: 8.5pt; color: #cbd5e1;">Author: Ujjwal &bull; Repository: https://github.com/ujjww4ll/HIMA &bull; Framework: Python, scikit-learn, GeoPandas</p>
</div>

<div class="callout-warn">
    <b>Official Academic Disclaimer:</b> Research risk estimate only &mdash; not an official operational warning. All predictions are spatial-probabilistic estimates for academic evaluation.
</div>

<h2>1. Executive Summary &amp; Project Overview</h2>
<p>
    <b>What is HIMA?</b> HIMA is an end-to-end Machine Learning and Geospatial Intelligence platform built to predict and evaluate daily <b>wildfire risk</b> and <b>preliminary landslide hydrometeorological triggering</b> across the 7 Sister States of Northeast India.
</p>
<ul>
    <li><b>Study Area:</b> 7 Sister States (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Tripura) spanning <b>253,412 km&sup2;</b>.</li>
    <li><b>Analytical Grid:</b> <b>253,408</b> contiguous 1 km &times; 1 km fishnet grid cells projected in metric CRS <b>EPSG:32646</b> (UTM Zone 46N).</li>
    <li><b>Temporal Horizon:</b> 2021&ndash;2024 daily resolution (4 full calendar years).
        <ul>
            <li><b>Training Set:</b> 2021&ndash;2023 (717,324 cell-days; 119,554 wildfire positive samples).</li>
            <li><b>Test Set:</b> 2024 Unseen Realistic Holdout (1,000,000 cell-days; 348 positives; natural prevalence ~0.035%).</li>
        </ul>
    </li>
    <li><b>Core Datasets Ingested:</b>
        <ul>
            <li><b>Wildfire ground truth:</b> NASA FIRMS VIIRS S-NPP Collection 2 (375 m resolution, 219,928 vegetation fires of type=0).</li>
            <li><b>Landslide ground truth:</b> Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) Compendium (9,970 field-validated records in study area; 463 unique dated cell-days).</li>
            <li><b>Atmospheric reanalysis:</b> ECMWF ERA5-Land daily reanalysis (2m temperature, dewpoint, min/mean relative humidity, 10m wind speed, volumetric soil moisture layer 1, runoff).</li>
            <li><b>Precipitation observations:</b> IMD 0.25&deg; gridded daily rainfall (same-day, 3d, 7d, 15d rolling antecedent totals, dry spell counters).</li>
        </ul>
    </li>
</ul>

<h2>2. Dependent vs. Independent Variables (The Core Machine Learning Setup)</h2>
<p>
    When your teacher asks: <i>"What are you predicting, and what inputs are you feeding into the algorithm?"</i>, use these exact definitions:
</p>

<h3>A. Dependent Variables (Targets / What We Predict)</h3>
<p>The model solves a binary classification task on each spatial 1 km cell $c$ on day $t$:</p>
<ol>
    <li><b>Wildfire Target (<code>fire_detected</code> &isin; {0, 1}):</b>
        <ul>
            <li><b>1 (Positive):</b> At least one active VIIRS S-NPP C2 vegetation fire (type=0) was detected within cell $c$ on date $t$.</li>
            <li><b>0 (Negative):</b> No fire detected in cell $c$ on date $t$.</li>
        </ul>
    </li>
    <li><b>Landslide Target (<code>landslide_detected</code> &isin; {0, 1}):</b>
        <ul>
            <li><b>1 (Positive):</b> GSI field-validated landslide occurred in cell $c$ on date $t$.</li>
            <li><b>0 (Negative):</b> Background non-event cell-day.</li>
        </ul>
    </li>
</ol>

<h3>B. Independent Variables (Features / What We Use to Predict)</h3>
<p>The wildfire pipeline uses <b>33 engineered features</b> belonging to four distinct physical categories:</p>

<table>
    <tr>
        <th>Category</th>
        <th>Features</th>
        <th>Physical &amp; Statistical Justification</th>
    </tr>
    <tr>
        <td><b>Thermal &amp; Moisture (ERA5)</b></td>
        <td><code>temperature_c</code>, <code>dewpoint_c</code>, <code>dewpoint_depression_c</code>, <code>relative_humidity_min</code>, <code>relative_humidity_mean</code>, 7-day rolling means/extremes</td>
        <td>Wildfires cannot propagate when fine forest fuel moisture is high. Relative humidity minimum (daily afternoon trough) and dewpoint depression ($T - T_d$) measure the atmosphere's drying power on forest biomass.</td>
    </tr>
    <tr>
        <td><b>Precipitation &amp; Drought (IMD + ERA5)</b></td>
        <td><code>imd_rain_1d</code>, <code>imd_rain_sum_3d</code>, <code>imd_rain_sum_7d</code>, <code>imd_rain_sum_15d</code>, <code>imd_days_since_rain</code>, <code>era5_rainfall_mm</code></td>
        <td>Antecedent rainfall dictates sub-surface and topsoil moisture. <code>days_since_rain</code> tracks continuous dry spells where leaf litter becomes dry tinder.</td>
    </tr>
    <tr>
        <td><b>Hydrology &amp; Wind</b></td>
        <td><code>soil_water_layer1</code> (0&ndash;7 cm volumetric water content), <code>era5_soil_water_mean_7d</code>, <code>wind_speed_ms</code>, <code>era5_wind_mean_7d</code></td>
        <td>Topsoil dryness mirrors organic layer desiccating. Wind speed supplies oxygen and drives fire rate of spread (ROS).</td>
    </tr>
    <tr>
        <td><b>Spatiotemporal &amp; Geography</b></td>
        <td><code>centroid_lat</code>, <code>centroid_lon</code>, <code>sin_doy</code>, <code>cos_doy</code>, <code>state_name</code>, <code>season</code></td>
        <td>Northeast India has distinct climate zones (Assam valley vs. Mizoram ridges). Cyclical transformation of Day-of-Year ($\sin, \cos(2\pi \cdot \text{DOY}/365)$) captures seasonal dry period (March&ndash;April) without discontinuity between Dec 31 and Jan 1.</td>
    </tr>
</table>

<div class="callout-success">
    <b>Data Leakage Prevention:</b> Post-event features such as Fire Radiative Power (<code>frp_sum</code>, <code>frp_mean</code>), fire brightness (<code>brightness_mean</code>), and detection counts are <b>strictly excluded</b> from features. They only exist <i>after</i> a fire ignites!
</div>

<h2>3. Detailed Breakdown of Every Factor &amp; Slider in the Web Simulator</h2>
<p>
    When presenting the Live Risk Simulator on the website, here is what each control represents and how they interact:
</p>

<table>
    <tr>
        <th>Website Parameter</th>
        <th>Range / Units</th>
        <th>What It Represents &amp; How the Model Uses It</th>
    </tr>
    <tr>
        <td><b>State</b></td>
        <td>7 Sister States</td>
        <td>Encodes regional baseline fire frequency. Mizoram, Assam, and Manipur have higher historical jhum (slash-and-burn) clearing and fire counts than Tripura or Nagaland.</td>
    </tr>
    <tr>
        <td><b>IMD Season</b></td>
        <td>Pre-Monsoon, Monsoon, Post-Monsoon, Winter</td>
        <td>Categorical meteorological period. Northeast India fire season peaks strictly in <b>Pre-Monsoon</b> (March&ndash;April). During <b>Monsoon</b>, heavy rainfall completely suppresses natural wildfires.</td>
    </tr>
    <tr>
        <td><b>Latitude &amp; Longitude</b></td>
        <td>21.9&deg;&ndash;29.3&deg;N, 89.8&deg;&ndash;97.3&deg;E</td>
        <td>Geographic position. Lower latitudes (Mizoram 23&deg;N) dry out earlier in spring than northern alpine Arunachal Pradesh (28&deg;N).</td>
    </tr>
    <tr>
        <td><b>Day of Year (DOY)</b></td>
        <td>1 to 365 (e.g., 90 = Mar 31)</td>
        <td><b>#1 Top Permutation Feature!</b> Converted to $\sin(\text{doy})$ and $\cos(\text{doy})$. The tree splits heavily on DOY 60&ndash;120 (March&ndash;April), which is the primary wildfire window.</td>
    </tr>
    <tr>
        <td><b>ERA5 Temperature</b></td>
        <td>0&deg;C to 37&deg;C</td>
        <td>Daily mean air temperature. Higher temperatures accelerate fuel evapotranspiration and lower relative humidity.</td>
    </tr>
    <tr>
        <td><b>Min Relative Humidity (RH min)</b></td>
        <td>5% to 100%</td>
        <td><b>Most Critical Meteorological Factor!</b> Afternoon minimum humidity. When RH drops below 25%, fire probability shoots up. If RH is &gt;75%, fire probability drops to near zero regardless of heat.</td>
    </tr>
    <tr>
        <td><b>Soil Moisture (Layer 1)</b></td>
        <td>0.05 to 0.50 m&sup3;/m&sup3;</td>
        <td>Volumetric water content in the top 0&ndash;7 cm. Values below 0.18 indicate desiccated ground litter susceptible to ignition.</td>
    </tr>
    <tr>
        <td><b>Wind Speed</b></td>
        <td>0.1 to 12.0 m/s</td>
        <td>Surface wind speed. High winds (&gt;4 m/s) fan flames and accelerate fire propagation.</td>
    </tr>
    <tr>
        <td><b>Same-Day Rainfall (1d)</b></td>
        <td>0 to 250 mm</td>
        <td>IMD precipitation on the prediction day. Immediate direct suppression of fire ignitions.</td>
    </tr>
    <tr>
        <td><b>Antecedent Rain (3d, 7d, 15d)</b></td>
        <td>0 to 1200 mm</td>
        <td>Cumulative historical rainfall over prior 3, 7, and 15 days. Crucial for both wildfire suppression and <b>landslide trigger threshold</b> (deep saturation).</td>
    </tr>
    <tr>
        <td><b>Consecutive Dry Days</b></td>
        <td>0 to 60 days</td>
        <td>Number of uninterrupted days with rainfall &lt; 2.5 mm. High dry days (&gt;20) indicate cumulative drought and extreme fire susceptibility.</td>
    </tr>
</table>

<div class="callout-warn">
    <b>Key Teacher Demonstration Tip (Physical Coherence):</b><br/>
    If your teacher asks: <i>"Why did risk stay high when I only moved rainfall to 200 mm?"</i><br/>
    <b>Answer:</b> <i>"Because in nature, 200 mm of rain never happens inside 18% desert humidity and 22 consecutive dry days! The tree model splits on humidity and Day of Year first. To test monsoon suppression properly, we either click the <b>Peak Monsoon</b> preset or slide humidity up to 80% and dry days to 0. The risk score immediately drops to 0.05%."</i>
</div>

<h2>4. All 6 Machine Learning Classifiers Explained</h2>
<p>We trained and systematically compared 6 syllabus-aligned classifiers under identical 5-fold Spatial Group Cross-Validation:</p>

<h3>1. DummyClassifier (Prior Baseline)</h3>
<ul>
    <li><b>How it works:</b> Predicts the class distribution based purely on training label frequency (prevalence) without using any features.</li>
    <li><b>Role in project:</b> Sanity baseline. Confirms that an uninformed guess yields exactly <b>0.5000 ROC-AUC</b>, proving all other models learn genuine physical signal.</li>
</ul>

<h3>2. Logistic Regression (Linear Probabilistic Baseline)</h3>
<ul>
    <li><b>How it works:</b> Models the log-odds of fire as a linear combination of normalized inputs:
        <br/><span class="formula">P(Y=1|X) = &sigma;(w&supT;X + b) = 1 / (1 + e^{-(w&supT;X + b)})</span>
    </li>
    <li><b>Evaluation:</b> Achieved <b>0.9040 Test ROC-AUC</b>, but struggles with complex nonlinear weather interactions (e.g., wind only amplifies fire if humidity is already low).</li>
</ul>

<h3>3. Gaussian Naive Bayes (Generative Bayesian Classifier)</h3>
<ul>
    <li><b>How it works:</b> Applies Bayes' Theorem assuming conditional independence between features:
        <br/><span class="formula">P(Y=1|X) &prop; P(Y=1) &prod; P(x_i | Y=1)</span>, where each feature distribution is modeled as a 1D Gaussian.
    </li>
    <li><b>Evaluation:</b> Fast, but severely penalized (0.8621 ROC-AUC) because weather features violate the independence assumption (temperature, humidity, and rainfall are heavily correlated).</li>
</ul>

<h3>4. Decision Tree (CART &mdash; Interpretable White-Box)</h3>
<ul>
    <li><b>How it works:</b> Recursively partitions feature space using binary orthogonal splits that maximize Gini Impurity reduction (<span class="formula">Gini = 1 - &sum; p_i&sup2;</span>). Constrained to <code>max_depth=12</code> and <code>min_samples_leaf=200</code>.</li>
    <li><b>Evaluation:</b> Achieved <b>0.9049 Test ROC-AUC</b>. Offers complete visual interpretability (generated in <code>outputs/figures/wildfire_decision_tree.png</code>).</li>
</ul>

<h3>5. Random Forest (Bagging Ensemble)</h3>
<ul>
    <li><b>How it works:</b> Builds 100 decorrelated decision trees using bootstrap aggregation (bagging) with random feature subspace sampling at each split ($m = \sqrt{p}$). Final prediction is the unweighted average of all trees.</li>
    <li><b>Evaluation:</b> Drastically reduced single-tree variance, achieving <b>0.9260 Test ROC-AUC</b> and <b>0.7761 CV PR-AUC</b>.</li>
</ul>

<h3>6. HistGradientBoosting (Histogram GBDT &mdash; Selected Best Model)</h3>
<ul>
    <li><b>How it works:</b> A modern Gradient Boosted Decision Tree (GBDT) algorithm based on LightGBM. Instead of sorting continuous feature values, it discretizes them into <b>256 integer bins</b>. Trees are built sequentially, with each new tree fitting the <i>negative gradient (residuals)</i> of the loss function:
        <br/><span class="formula">F_m(x) = F_{m-1}(x) + &gamma;_m h_m(x)</span>
    </li>
    <li><b>Why it won (Best Model Justification):</b>
        <ol>
            <li><b>Highest Test ROC-AUC:</b> <b>0.9358</b> on realistic 2024 holdout.</li>
            <li><b>Highest Cross-Validation PR-AUC:</b> <b>0.7817</b> (the metric that matters most for class imbalance).</li>
            <li><b>Best Recall / False Alarm Trade-off:</b> Catches <b>68.4%</b> of all fires while triggering alarms on only <b>6.1%</b> of non-fire days.</li>
            <li><b>Native Missing Value Handling:</b> Naturally routes missing ERA5 reanalysis values (NaN) to the best branch without needing artificial zero-filling.</li>
            <li><b>Captures Nonlinear Synergies:</b> High heat + low humidity + high wind is modeled as deep interactive tree pathways.</li>
        </ol>
    </li>
</ul>

<h2>5. Comprehensive Viva / Teacher Question Bank &amp; Model Answers</h2>

<div class="qa-box">
    <div class="qa-q">Q1: Why is your test precision so small (~0.4%) even though your ROC-AUC is 93.6%? Did your model fail?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"No, Sir/Ma'am! This is the classic <b>Base Rate Fallacy</b> in extreme class imbalance. In our 2024 test set, there are only 348 fire days across 1,000,000 cell-days (a natural prevalence of 0.035%, or 1 fire in 2,870 cell-days). Even with a model that correctly filters out 94% of false alarms, false positives will still numerically exceed true positives. That is why precision alone is misleading for rare hazards, and why ROC-AUC (0.9358) and PR-AUC are the primary metrics used in remote sensing and hazard assessment literature."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q2: How did you ensure there is NO data leakage between train and test?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"We implemented a strict two-tier isolation protocol:
        <br/>1. <b>Temporal Split:</b> Models were trained strictly on 2021&ndash;2023 data and tested on the forward 2024 calendar year (simulating real operational deployment).
        <br/>2. <b>Spatial Block Cross-Validation:</b> Inside the training set, we used Spatial Stratified Group K-Fold on 50 km geographic blocks to prevent spatial autocorrelation leakage.
        <br/>3. <b>Feature Sanitization:</b> All post-ignition sensor readings (FRP, fire brightness) were stripped before modeling."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q3: What is Bayesian Prior Adjustment, and why did you use it?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"Because our training set used balanced negative subsampling (effective prior ~16.7%), the raw model probabilities overestimate real-world daily likelihood. We apply Bayes' Theorem odds-ratio adjustment:
        <br/><span class="formula">P_cal = P_raw / [P_raw + (1 - P_raw) &times; (P_train / P_pop) &times; ((1 - P_pop) / (1 - P_train))]</span>
        <br/>This maps raw classifier scores back to true real-world Northeast India daily fire prevalence (~0.043%), yielding well-calibrated probabilities without altering ROC ranking."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q4: Why was Sikkim excluded from the ERA5-coupled spatial grid?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"Because of raw data spatial extent constraints. Local processed ERA5 NetCDF reanalysis rasters begin at longitude <b>89.8&deg;E</b>, whereas Sikkim lies between <b>88.0&deg;E and 88.9&deg;E</b>. Rather than faking or fabricating proxy weather for Sikkim, we adhered strictly to academic data integrity and constrained the coupled analytical grid to the 7 contiguous Sister States."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q5: Why do you label the Landslide model 'Preliminary Weather-Only'?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"A complete landslide susceptibility model requires static geo-environmental layers: Digital Elevation Models (slope, aspect, curvature), geological lithology, SoilGrids, and land-use (WorldCover). These datasets were not locally present in the downloads directory. Adhering to zero fabrication of missing data, our model evaluates <b>hydrometeorological triggering</b> (antecedent rainfall &amp; soil saturation) only."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q6: Why did you exclude <code>state_name</code> from the Landslide feature set?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"Data audit revealed strong geographical sampling bias: <b>529 out of 673 (78.6%)</b> dated GSI landslide events came from a single post-monsoon field survey campaign in Mizoram in 2024. If <code>state_name</code> were included, the tree would memorize 'Mizoram = Landslide', creating severe survey-bias artifact rather than learning true rainfall triggers."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q7: How did you handle the 4 missing ERA5 months in 2023?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"ERA5 reanalysis was missing months 2023-08, 09, 11, and 12 in the local archive. We <b>preserved them as NaN</b> and used HistGradientBoosting's native NaN routing. We strictly forbade imputing zeros, because filling zero rainfall during August (peak monsoon) would artificially fabricate severe drought conditions that never existed."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q8: How did you choose the operating alert threshold?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"Instead of defaulting to 0.5, we performed threshold tuning across 100 cutoffs on out-of-fold spatial cross-validation. The optimal threshold of <b>0.7118</b> was chosen to maximize the F1-score, establishing the operational decision boundary between routine background noise and high-confidence hazard alert."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q9: What is the difference between Bagging and Boosting in your models?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"In <b>Random Forest (Bagging)</b>, 100 trees are trained independently in parallel on bootstrap samples, reducing variance by averaging. In <b>HistGradientBoosting (Boosting)</b>, trees are trained sequentially in series, where each tree fits the residual errors of prior trees, reducing both bias and variance."</i>
    </div>
</div>

<div class="qa-box">
    <div class="qa-q">Q10: What software engineering practices did you follow?</div>
    <div class="qa-a">
        <b>Answer:</b> <i>"We implemented a production-style architecture: a centralized <code>config/project.yaml</code>, modular Python packages (<code>src/audit</code>, <code>src/geospatial</code>, <code>src/ingestion</code>, <code>src/features</code>, <code>src/training</code>, <code>src/api</code>), a single-command batch launcher (<code>run_hima.bat</code>), full git version control, and a <b>9/9 passing pytest test suite</b> covering data integrity, monotonicity, and inference."</i>
    </div>
</div>
"""

def generate_pdf():
    print(f"[PDF Gen] Compiling HIMA Study Guide & Viva Prep to: {OUTPUT_PDF}")
    mediabox = pymupdf.paper_rect("a4")
    # 36pt margins = 0.5 inch margins
    where = mediabox + (36, 36, -36, -36)

    writer = pymupdf.DocumentWriter(str(OUTPUT_PDF))
    story = pymupdf.Story(html=HTML_CONTENT, user_css=CSS)

    def rectfn(rect_num, filled):
        return mediabox, where, None

    story.write(writer, rectfn)
    writer.close()
    print(f"[PDF Gen] Successfully generated PDF! File size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    generate_pdf()
