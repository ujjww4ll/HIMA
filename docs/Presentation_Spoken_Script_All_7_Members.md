# Flood Prediction and Early Warning System
## Word-for-Word Viva & Spoken Presentation Delivery Guide for All 7 Members
**Presentation File:** `Flood_Prediction_and_Early_Warning_System.pptx` (33 Slides)  
**Total Estimated Presentation Time:** 14–18 Minutes (~2–2.5 minutes per member)  
**Course:** Application of Artificial Intelligence (AI-ML / CSET312)  

---

## 👥 Team Breakdown & Slide Allocations

| Member | Name / Designation | Slides Owned | Core Focus & Presentation Topic |
| :---: | :--- | :---: | :--- |
| **M1** | **Ujjwal (Team Lead)** | Slides 1–8 | Opening, Problem Statement, Full-Stack Architecture, REST API, Web UI & Risk Simulator |
| **M2** | **Member 2 (Geospatial Lead)** | Slides 9–11 | 253,408 Metric Grid (EPSG:32646), FIRMS Fire Ingestion, IMD Rain & ERA5 Reanalysis |
| **M3** | **Member 3 (Wildfire ML Lead)** | Slides 12–15 | 33 Features, Cyclical Sine/Cosine DOY, 6-Model Benchmark (HistGradientBoosting 0.9358) |
| **M4** | **Member 4 (Landslide & QA Lead)** | Slides 16–19 | GSI PDF Mining, Landslide Trigger Models, Bayesian Calibration, 9 Pytest Integrity Tests |
| **M5** | **Malvika (Flood Ingestion Lead)** | Slides 20–22 | INDOFLOODS (4,548 river events), CHIRPS Multi-Day Rain Lags ($T_{1d}–T_{10d}$), Parquet Sync |
| **M6** | **Shubhangi (Flood ML Lead)** | Slides 23–26 | Flood 6-Classifier Benchmark, GBDT Tuning (0.9557 Test AUC, 98.56% Recall, FAR Control) |
| **M7** | **Sonam (Domain Transfer Lead)** | Slides 27–30 | Solving Spatial Domain Shift (The 1.7% Bug Fix), Catchment Scaling, Cascading Risk Chains |
| **ALL** | **All 7 Members Jointly** | Slides 31–33 | Comparative Master Benchmark Table, Honest Limitations, Conclusion & Future Roadmap |

---

## 🎬 STAGE 1: OPENING & FULL-STACK ARCHITECTURE
### 👤 Speaker: Ujjwal (Team Lead & Full-Stack AI Engineer)
**Slide Coverage:** Slides 1 to 8

#### 🖥️ Slide 1: Cover Slide
> **[Ujjwal Speaks]:**  
> *"Respected external examiners, faculty members, and fellow classmates, a very warm good morning.  
> Today, our team is privileged to present our Application of AI Capstone Project: **Flood Prediction and Early Warning System**, augmented with **Multi-Hazard Landslide and Wildfire Intelligence**.  
> 
> Our team consists of seven members: myself, **Ujjwal**, serving as Team Lead and Full-Stack Architect, alongside **Member 2** for Geospatial Ingestion, **Member 3** for Wildfire ML, **Member 4** for Landslide & QA, **Malvika** for Flood Hydrology & Ingestion, **Shubhangi** for Flood Machine Learning, and **Sonam** for Domain Generalization and Multi-Hazard Integration.  
> 
> As an ethical baseline, our platform produces research risk estimates to aid proactive civil defense planning and does not substitute for official government disaster bulletins."*

#### 🖥️ Slide 2: Executive Summary & The Multi-Hazard Challenge
> **[Ujjwal Speaks]:**  
> *"Why did we build this system? Across India, disasters are rarely isolated. Severe pre-monsoon heatwaves ignite catastrophic forest fires. When torrential monsoons strike, fire-denuded hillslopes give way to landslides. As runoff gathers across thousands of square kilometers, river stages surge past danger marks, submerging fertile floodplains.  
> Traditional early warning systems operate in silos. Our platform couples five authoritative datasets into a single machine-learning framework, predicting hazard severity days in advance."*

#### 🖥️ Slide 3: 7-Member Responsibility Matrix
> **[Ujjwal Speaks]:**  
> *"To ensure industrial engineering rigor, each of our seven members took end-to-end ownership over their codebase and theoretical proofs. Each member here today will present their own data pipelines, mathematical validations, and experimental findings."*

#### 🖥️ Slide 4: Multi-Hazard System Architecture
> **[Ujjwal Speaks]:**  
> *"Our architecture flows from raw satellite archives to an interactive browser interface. Raw data is ingested, projected into metric space, transformed through feature pipelines, evaluated across 6 standard scikit-learn models per hazard, and served live via a multi-threaded Python REST API."*

#### 🖥️ Slide 6–7: Web Dashboard & Interactive Simulator
> **[Ujjwal Speaks]:**  
> *"I will now present the Full-Stack and Serving Architecture that I engineered.  
> To guarantee zero-friction deployment, I built the frontend as a native Single Page Application using modern HTML5, CSS3, and ES6 JavaScript — with zero bulky frameworks or external CDN dependencies.  
> Key components include:
> 1. An offline-first interactive SVG map of Northeast India rendered from GeoJSON polygons.
> 2. An animated SVG Risk Gauge using CSS arc offset interpolation (`stroke-dashoffset`) that smoothly animates across Low, Moderate, High, and Critical risk bands.
> 3. A multi-threaded REST API server in `src/api/predict.py` serving real-time predictions for all three hazards at sub-50ms latency.
> 4. Automatic form filtering: when switching to Flood mode, 14 non-pertinent weather fields are hidden, exposing only the 5 active hydrological drivers."*

#### 🖥️ Slide 8: Ujjwal's Viva Defense Bank
> **Examiner Question:** *"Why use Python's built-in `ThreadingHTTPServer` instead of Flask or FastAPI?"*  
> **Ujjwal's Answer:** *"To eliminate deployment overhead and external server binaries. The university demo requires instant 1-click startup via `run_hima.bat` on any standard machine. The multi-threaded standard library server handles concurrent requests reliably without external WSGI containers."*  
> 
> **Examiner Question:** *"How did you prevent CORS preflight errors?"*  
> **Ujjwal's Answer:** *"The server serves both the static web frontend and the JSON REST endpoints on the exact same origin (`http://localhost:8000`). All client requests use relative paths (`/api/*`), completely avoiding CORS restrictions."*

---

## 🎬 STAGE 2: GEOSPATIAL ENGINEERING & DATA PIPELINE
### 👤 Speaker: Member 2 (Geospatial & Ingestion Lead)
**Slide Coverage:** Slides 9 to 11

#### 🖥️ Slide 9–10: 1 km² Metric Fishnet Grid & Ingestion
> **[Member 2 Speaks]:**  
> *"Thank you, Ujjwal. Respected examiners, I owned the Geospatial Engineering and Ingestion architecture.  
> 
> To couple continuous atmospheric grids with discrete point hazard events, I established a dual coordinate system: EPSG:4326 for unprojected geographic coordinates and **EPSG:32646 (UTM Zone 46N)** for metric distance calculations.  
> In UTM Zone 46N, coordinates are measured in metres. Across the Seven Sister States (253,412 km²), I constructed an exact fishnet grid of **253,408 unique 1 km × 1 km grid cells**.  
> 
> I then ingested and harmonized three massive archives:
> 1. **NASA FIRMS VIIRS (S-NPP C2):** 219,928 confirmed vegetation fires (Type=0), spatially deduplicated.
> 2. **IMD 0.25° Gridded Daily Rainfall:** 48 complete calendar months (2021–2024), 415 grid points mapped with a median distance of 10.57 km.
> 3. **ECMWF ERA5-Land Reanalysis:** 0.1° resolution, 2,491 grid points. Four missing months were strictly preserved as NaN rather than corrupted with artificial zeros."*

#### 🖥️ Slide 11: Member 2's Viva Defense Bank
> **Examiner Question:** *"Why not create 1 km cells directly in degrees (EPSG:4326)?"*  
> **Member 2's Answer:** *"One degree of longitude shrinks significantly as latitude increases toward the Himalayas (28°N). Generating cells in degrees creates deformed trapezoids. UTM Zone 46N measures distance in exact metres, guaranteeing precise 1,000m × 1,000m squares."*  
> 
> **Examiner Question:** *"How did you link fire points to 1 km cells without running out of RAM?"*  
> **Member 2's Answer:** *"I mapped grid cell centroids into a Scipy KD-Tree structure and performed nearest-neighbor lookups in Euclidean space, reducing spatial join complexity from O(N × M) to O(N log M), running in under 4 seconds."*

---

## 🎬 STAGE 3: WILDFIRE MACHINE LEARNING & FEATURE ENGINEERING
### 👤 Speaker: Member 3 (Feature Engineering & Wildfire ML Lead)
**Slide Coverage:** Slides 12 to 15

#### 🖥️ Slide 12–14: 33 Features & Wildfire Classifiers
> **[Member 3 Speaks]:**  
> *"Thank you, Member 2. Respected examiners, I engineered the 33 spatiotemporal weather features and the wildfire machine learning pipelines.  
> 
> Forest fires in Northeast India are hyper-seasonal, peaking strictly between February and April during pre-monsoon slash-and-burn cycles. To capture this without boundary distortion, I encoded the day-of-year into continuous periodic wavefunctions: $\sin(2\pi \cdot \text{doy} / 365)$ and $\cos(2\pi \cdot \text{doy} / 365)$.  
> I also engineered atmospheric moisture deficit indicators including Dewpoint Depression ($T_{air} - T_{dew}$), soil water saturation, and consecutive dry days.  
> 
> I benchmarked six classifiers under spatial 5-fold cross-validation and evaluated them on a **1,000,000 cell-day 2024 hold-out test set** under realistic 0.035% prevalence.  
> **HistGradientBoosting** achieved the top score with a **2024 Test ROC-AUC of 0.9358** and **85.20% Recall**."*

#### 🖥️ Slide 15: Member 3's Viva Defense Bank
> **Examiner Question:** *"Why did HistGradientBoosting beat Random Forest and Decision Trees?"*  
> **Member 3's Answer:** *"HistGradientBoosting bins continuous variables into 256 integer buckets, dramatically accelerating tree split searches and natively handling missing ERA5 months without synthetic imputation. Its boosting mechanism sequentially penalizes hard false alarms."*  
> 
> **Examiner Question:** *"Why evaluate on a 0.035% prevalence test set instead of a 50-50 balanced set?"*  
> **Member 3's Answer:** *"Wildfires occur in less than 0.04% of daily cells in reality. A 50-50 artificial test set inflates precision and gives false confidence. Testing on 1,000,000 realistic cell-days proves true operational reliability."*

---

## 🎬 STAGE 4: LANDSLIDE MODELING, CALIBRATION & QA
### 👤 Speaker: Member 4 (Landslide ML & QA Lead)
**Slide Coverage:** Slides 16 to 19

#### 🖥️ Slide 16–18: GSI Mining, Bayesian Calibration & 9 Tests
> **[Member 4 Speaks]:**  
> *"Thank you, Member 3. Respected examiners, I was responsible for Landslide Feasibility Modeling, Bayesian Odds Calibration, and the Automated Quality Assurance Test Suite.  
> 
> Using `pdfplumber`, I extracted **9,970 landslide event records** from scanned Geological Survey of India (GSI) multi-page bulletins. Filtering for valid calendar dates within our 2021–2024 window identified 463 unique dated cell-days.  
> Because static high-resolution DEM slope layers were unavailable offline, I strictly modeled this as a **Hydrometeorological Weather-Trigger Pipeline** (rainfall + soil water), refusing to fabricate synthetic terrain data.  
> 
> To solve the severe class-imbalance problem, I implemented **Bayesian Prior Odds Calibration**:  
> $$\text{Odds}_{true} = \text{Odds}_{sample} \times \left( \frac{\pi_{true}}{1 - \pi_{true}} \Big/ \frac{\pi_{sample}}{1 - \pi_{sample}} \right)$$  
> This dropped the Brier score from 0.083 to **0.0005**, aligning probabilities with true real-world event frequencies.  
> Finally, I authored **9 automated pytest unit tests** verifying non-negativity, mathematical monotonicity, and zero post-event data leakage. All 9 tests pass in 2.85s."*

#### 🖥️ Slide 19: Member 4's Viva Defense Bank
> **Examiner Question:** *"Why did you exclude 'state_name' from landslide model features?"*  
> **Member 4's Answer:** *"In the GSI records, 78% of dated entries originated from specific road-clearing survey teams in Mizoram. Including `state_name` would cause the model to memorize survey team bias rather than learning physical precipitation-trigger thresholds."*  
> 
> **Examiner Question:** *"What does `test_no_post_event_leakage_in_features` verify?"*  
> **Member 4's Answer:** *"It mathematically guarantees that no rolling feature uses information from day $t+1$ or later. Any future leakage invalidates an operational early warning system."*

---

## 🎬 STAGE 5: FLOOD DATA INGESTION & CHIRPS HYDROLOGY
### 👤 Speaker: Malvika (Flood Data Ingestion & CHIRPS Hydrology Lead)
**Slide Coverage:** Slides 20 to 22

#### 🖥️ Slide 20–21: INDOFLOODS Ingestion & Multi-Day Rain Lags
> **[Malvika Speaks]:**  
> *"Thank you, Member 4. Respected examiners, I spearheaded the Flood Data Ingestion and Hydrological Precipitation Processing architecture.  
> 
> Floods are the deadliest hydrometeorological disaster in India. To build an AI model capable of predicting river flooding, I ingested the **INDOFLOODS benchmark dataset**, comprising **4,548 all-India gauged river flood events** from 1965 to 2020 monitored by the Central Water Commission (CWC).  
> The target variable is `exceeds_danger_level`: 1 if peak river discharge reached or exceeded the official CWC danger level, and 0 otherwise (3,481 positive events, 76.5%).  
> 
> Crucially, river flooding does not happen from same-day rain alone. I integrated multi-temporal CHIRPS precipitation accumulation vectors across 155 river gauges and 1.3 million daily observations:
> - $T_{1d}$: 24-hour flash precipitation.
> - $T_{2d}, T_{3d}$: Channel runoff accumulation.
> - $T_{4d} \dots T_{7d}$: Catchment-wide soil saturation.
> - $T_{8d} \dots T_{10d}$: Basin peak inundation volume.  
> Supporting variables include catchment area ($km^2$), stream order, population density, urban percentage, and lithology."*

#### 🖥️ Slide 22: Malvika's Viva Defense Bank
> **Examiner Question:** *"Why use CHIRPS satellite rainfall instead of local rain gauges?"*  
> **Malvika's Answer:** *"Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) merges 0.05° infrared satellite precipitation with ground gauge measurements, providing continuous, gap-free precipitation across entire river catchments where physical gauges are sparse."*  
> 
> **Examiner Question:** *"What is the physical significance of the 10-day rainfall lag ($T_{10d}$)?"*  
> **Malvika's Answer:** *"In large river catchments, the time of concentration — the time required for water from the most remote point in the watershed to reach the river outlet — can be several days. $T_{10d}$ captures the antecedent baseflow that primes the river channel for flooding."*

---

## 🎬 STAGE 6: FLOOD MACHINE LEARNING ARCHITECTURE
### 👤 Speaker: Shubhangi (Flood ML Architecture & Benchmarking Lead)
**Slide Coverage:** Slides 23 to 26

#### 🖥️ Slide 23–25: 6-Classifier Benchmark & GBDT Optimization
> **[Shubhangi Speaks]:**  
> *"Thank you, Malvika. Respected examiners, I designed and trained the machine learning architecture for river flood prediction.  
> 
> Following our CSET312 syllabus, I benchmarked six diverse algorithms under a strict 70/30 stratified train/test split (3,183 train / 1,365 test) and 5-fold cross-validation:
> 1. **Dummy Baseline:** CV PR-AUC 0.7649, Test ROC-AUC 0.5000.
> 2. **Logistic Regression:** Regularized linear baseline, Test ROC-AUC 0.8017.
> 3. **Gaussian Naive Bayes:** Probabilistic baseline, Test ROC-AUC 0.7386.
> 4. **Decision Tree (Cost-Complexity Pruned):** Interpretable tree, Test ROC-AUC 0.9251.
> 5. **Random Forest:** Ensemble of 200 trees, Test ROC-AUC 0.9557.
> 6. **HistGradientBoosting (Winner):** **Test ROC-AUC: 0.9557**, **Test PR-AUC: 0.9825**, and **Test Recall: 98.56%**.  
> 
> At our optimized F1 operating threshold of 0.2849, HistGradientBoosting successfully captured **1,030 out of 1,045 flood disaster events** in the test set, while maintaining a low False Alarm Rate of 16.56%."*

#### 🖥️ Slide 26: Shubhangi's Viva Defense Bank
> **Examiner Question:** *"Why is Recall prioritized over overall Accuracy in flood prediction?"*  
> **Shubhangi's Answer:** *"In disaster early warning, a False Negative (missing an actual catastrophic flood) costs human lives. A False Positive (a precautionary alert that stays below danger level) incurs minimal logistical cost. HistGradientBoosting maximized Recall to 98.56%."*  
> 
> **Examiner Question:** *"Why did Gaussian Naive Bayes suffer from a high False Alarm Rate (77.19%)?"*  
> **Shubhangi's Answer:** *"Naive Bayes strictly assumes feature independence. Antecedent rainfall variables ($T_{1d}$ through $T_{10d}$) exhibit high multicollinearity ($r > 0.85$). Correlated inputs multiply the likelihood ratios, artificially driving extreme over-prediction."*

---

## 🎬 STAGE 7: DOMAIN TRANSFER & MULTI-HAZARD GENERALIZATION
### 👤 Speaker: Sonam (Domain Transfer & Multi-Hazard Integration Lead)
**Slide Coverage:** Slides 27 to 30

#### 🖥️ Slide 27–29: Solving Domain Shift (The 1.7% Bug) & Cascading Risks
> **[Sonam Speaks]:**  
> *"Thank you, Shubhangi. Respected examiners, I owned Multi-Hazard Integration and Domain Generalization.  
> 
> During user testing of our prototype, we encountered a critical anomaly: the flood risk gauge refused to exceed 1.7%, even when rainfall was dialed up to an extreme 500mm!  
> I conducted a rigorous forensic audit and identified a **Spatial Confounder Domain Shift**:
> - INDOFLOODS gauges are located in Central and Western India between **72.8°E and 91.6°E**.
> - Northeast India is located between **92.8°E and 97.3°E**.
> - Because `Latitude` and `Longitude` were included in training, HistGradientBoosting split on Longitude: any coordinate $> 91.6°E$ was routed to an empty leaf with zero training samples, capping predictions at **0.017 (1.7%)**!  
> 
> **My Solution:** I eliminated `Latitude` and `Longitude` from flood training. River flood physics is governed by **antecedent rainfall volume and catchment area**, not arbitrary GPS numbers!  
> I retrained the pipeline on pure hydrological variables and expanded catchment scaling to **50,000 km²**.  
> **The Result:** The model now operates dynamically across the full 0% to 100% scale (Low: 18.6%, Moderate: 86.8%, Extreme: 92.4%) with identical cross-validation performance."*

#### 🖥️ Slide 30: Sonam's Viva Defense Bank
> **Examiner Question:** *"Did removing Latitude and Longitude hurt cross-validation performance?"*  
> **Sonam's Answer:** *"Not at all. Cross-validation proved CV PR-AUC remained identical at 0.9886, and CV ROC-AUC held at 0.9696. Removing spatial coordinates eliminated geographic memorization, allowing true physical transfer to Northeast India."*  
> 
> **Examiner Question:** *"Why is catchment area the single most important flood feature?"*  
> **Sonam's Answer:** *"According to hydrological runoff equations ($Q = C \cdot I \cdot A$), peak discharge scales directly with basin area. A 100mm storm over a 20,000 km² basin generates hundreds of millions of cubic metres of runoff, whereas the same storm over a small 100 km² headwater stream drains safely."*

---

## 🎬 STAGE 8: JOINT CONCLUSION & ROADMAP
### 👤 Speakers: Joint Delivery (All 7 Members)
**Slide Coverage:** Slides 31 to 33

#### 🖥️ Slide 31: Cross-Hazard Benchmark Table
> **[Ujjwal Speaks]:**  
> *"In summary, HistGradientBoosting proved to be the universal champion across all three disaster modalities: Wildfire ROC-AUC 0.9358, Landslide ROC-AUC 0.9367, and Flood ROC-AUC 0.9557."*

#### 🖥️ Slide 32: Honest Academic Limitations
> **[Member 4 / Sonam Speaks]:**  
> *"We emphasize academic integrity: high-resolution DEM slope layers, Sentinel-2 NDVI, and 4 missing ERA5 months were absent locally. We refused to fabricate synthetic data, delivering verified results on real ground-truth inputs."*

#### 🖥️ Slide 33: Conclusion & Future Roadmap
> **[Ujjwal Concludes]:**  
> *"In the future, our platform will integrate Sentinel-1 InSAR radar for millimeter-level hillslope deformation tracking, real-time IoT bridge ultrasonic river gauges, and automated Common Alerting Protocol (CAP) SMS alerts.  
> We now invite the esteemed examiners for questions. Thank you very much."*
