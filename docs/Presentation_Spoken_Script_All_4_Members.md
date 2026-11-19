# HIMA Complete Viva & Presentation Spoken Script
## Word-for-Word Delivery Guide for All 4 Members
**Slide Deck:** `HIMA_Project_Presentation.pptx` (31 Slides)  
**Total Estimated Time:** 12–15 Minutes (approx. 3–4 minutes per member)

---

## 🎬 STAGE 1: OPENING & TEAM INTRODUCTION
### 👤 Speaker: Member 1 (Lead Presenter)

#### 🖥️ Slide 1: Cover Slide — HIMA
> **[Member 1 Speaks]:**  
> *"Respected teachers, external examiners, and dear colleagues, good morning.  
> Today, our team is proud to present project **HIMA**, which stands for **Hazard Intelligence, Monitoring & Assessment**.  
> 
> HIMA is an end-to-end, machine-learning-driven early-warning framework engineered to predict two of the most devastating natural hazards in Northeast India: **Wildfires** and **Landslides**.  
> 
> Before we begin, we state our project's ethical and scientific baseline: this system produces research risk estimates to aid planning and is not a substitute for official government disaster bulletins."*

---

#### 🖥️ Slide 2: Table of Contents
> **[Member 1 Speaks]:**  
> *"Our presentation today is organized into four distinct technical divisions, each engineered by one of our team members:
> - **Member 1 (Myself):** Full Stack Development, REST API Architecture, and Real-Time Interactive Dashboard.
> - **Member 2:** Geospatial Engineering, 253,408-Cell Grid Construction, and Multi-Source Satellite Ingestion.
> - **Member 3:** Feature Engineering (33 variables), Temporal Cyclical Encodings, and Wildfire Machine Learning.
> - **Member 4:** Landslide Machine Learning, GSI PDF Mining, Bayesian Prior Calibration, and the 9 Automated Unit Tests.
> - Finally, we will jointly present our Exploratory Data Analysis gallery, project metrics, and future roadmap."*

---

#### 🖥️ Slide 3: Project Overview — Why HIMA?
> **[Member 1 Speaks]:**  
> *"To understand why HIMA is necessary, consider the geography of Northeast India. The region experiences extreme monsoons triggering severe landslides, followed immediately by arid, hot pre-monsoon dry spells that ignite catastrophic forest fires.
> 
> Until now, disaster management has relied on siloed, delayed reports. HIMA bridges this gap by unifying four national and international datasets: NASA FIRMS fire points, IMD gridded rainfall, ECMWF ERA5-Land reanalysis, and Geological Survey of India landslide inventories.
> 
> We model these hazards across **253,408 unique one-square-kilometer grid cells**, evaluating six competitive machine learning classifiers per hazard under strict temporal hold-out validation."*

---

#### 🖥️ Slide 4: Study Area — Seven Sister States
> **[Member 1 Speaks]:**  
> *"As shown on the map on the left, our study area spans the complete Seven Sister States: Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, and Tripura — encompassing over 253,000 square kilometers.
> 
> To couple continuous meteorological grids with discrete point events like satellite fire pixels, we established two synchronized coordinate reference systems: EPSG:4326 for geographic coordinates and EPSG:32646 (UTM Zone 46N) for metric distance calculations.
> 
> You will notice Sikkim was omitted after careful data auditing revealed zero historical VIIRS vegetation fire detections. Including it would have injected unlabelled noise into our training pipeline."*

---

#### 🖥️ Slide 5: Team Structure Matrix
> **[Member 1 Speaks]:**  
> *"Here is the architectural division of our team. Each member took complete end-to-end ownership of their codebase, directories, and theoretical validations.
> 
> I will now present the first technical module: the Full Stack & Integration Architecture."*

---

## 💻 STAGE 2: MEMBER 1 — FULL STACK & SYSTEM INTEGRATION
### 👤 Speaker: Member 1

#### 🖥️ Slide 6: Section Header — Member 1
> **[Member 1 Speaks]:**  
> *"I will now present Member 1's domain: Full Stack Engineering, REST API design, and the operational dashboard."*

---

#### 🖥️ Slide 7: Member 1 — Role & File Ownership
> **[Member 1 Speaks]:**  
> *"As the Full Stack engineer, my primary goal was transforming complex, serialized machine learning models into an instantaneous, accessible decision-support system.
> 
> In terms of code ownership:
> - I authored `frontend/index.html`, `styles.css`, and `app.js` for our client-side user experience.
> - I engineered `src/api/predict.py`, the core Flask backend REST API.
> - And I developed `run_hima.bat`, our master automation script that lets any operator launch the system in demo, web, test, or data modes with one command.
> 
> My core design philosophy was **Offline-First**. Disaster relief officers in the hills of Northeast India frequently lose internet access. Therefore, our web client contains zero external CDN dependencies and zero cloud tile-server dependencies."*

---

#### 🖥️ Slide 8: How the Web Dashboard Works (Data Flow)
> **[Member 1 Speaks]:**  
> *"On this slide, you can see how data flows when an operator interacts with HIMA:
> 
> 1. The user adjusts environmental parameters using input sliders: 2-meter air temperature, relative humidity, wind speed, and cumulative rainfall.
> 2. `app.js` captures these inputs asynchronously and packages them into a clean JSON payload.
> 3. It fires a `POST` request to our Flask `/predict` endpoint.
> 4. The backend loads our pre-trained scikit-learn pipelines via `joblib`, performs feature scaling, evaluates the 33 decision features, applies Member 4's Bayesian calibration, and returns the calibrated probability in under 50 milliseconds.
> 5. As seen in the graphic, the client-side JavaScript receives this response and immediately animates our custom SVG semi-circular gauge to the exact risk percentage, categorizing it as Low, Moderate, High, or Critical.
> 6. Simultaneously, our custom inline SVG map updates the state polygons with color-coded alerts — all without a single page reload."*

---

#### 🖥️ Slide 9: Member 1 — Viva Defense Points
> **[Member 1 Speaks]:**  
> *"If asked about my architectural choices during viva:
> - **Why Flask over Django or FastAPI?** Flask provides the exact lightweight micro-framework needed for machine learning inference without the redundant database ORM overhead of Django. It starts up in under one second.
> - **Why custom SVG instead of Leaflet or Google Maps?** Standard map libraries require external web servers to fetch map tiles. If cell towers go down during a monsoon disaster, Leaflet breaks. Our inline SVG choropleth is self-contained, weighs less than 50 kilobytes, and works 100% offline.
> - **How is the threshold 0.7118 operationalized?** When probability exceeds 0.7118, the dashboard triggers an active red alert banner, warning operators of an imminent high-probability fire event.
> 
> I now invite **Member 2** to present our Geospatial and Data Ingestion Pipeline."*

---

## 🗺️ STAGE 3: MEMBER 2 — GEOSPATIAL & DATA INGESTION
### 👤 Speaker: Member 2

#### 🖥️ Slide 10: Section Header — Member 2
> **[Member 2 Speaks]:**  
> *"Thank you, Member 1. Respected examiners, I am Member 2, and I lead the Geospatial Engineering and Data Ingestion Architecture for HIMA."*

---

#### 🖥️ Slide 11: Member 2 — Role & File Ownership
> **[Member 2 Speaks]:**  
> *"My responsibility was building the absolute spatial and temporal backbone upon which all feature engineering and modeling depends.
> 
> I owned and developed:
> - `src/geospatial/grid.py`: The algorithmic generator for our 253,408 reference grid cells.
> - `src/geospatial/spatial.py`: High-speed $O(\log n)$ spatial nearest-neighbor search routines.
> - `src/ingestion/firms.py`: Ingestion, filtering, and temporal deduplication of NASA VIIRS satellite fires.
> - `src/ingestion/imd.py`: Gridded NetCDF daily precipitation extraction routines.
> - `src/ingestion/era5.py`: ECMWF Copernicus reanalysis weather pipelines.
> - `src/audit/`: Complete data integrity and geographic completeness auditing scripts.
> 
> In total, I ingested and cleaned **219,928 satellite fire detections**, 4 years of daily IMD 0.25-degree rainfall grids, and multi-gigabyte ERA5 climate data."*

---

#### 🖥️ Slide 12: The 253,408-Cell Grid & Spatial Joins
> **[Member 2 Speaks]:**  
> *"Building an AI model across an entire geographic region requires solving a fundamental spatial problem: satellite fires are discrete latitude-longitude points, rainfall is a coarse 0.25-degree grid, and topography varies continuously.
> 
> To unify them:
> 1. I generated a regular 0.01-degree mesh across Northeast India's bounding box and clipped it against the official state boundary geometries stored in `study_states.gpkg`. This produced exactly **253,408 valid onshore land cells**, each representing approximately 1 km².
> 2. To link fire events to cells, a naive brute-force search would require calculating 219,000 points against 253,000 centroids — over **55 billion distance calculations**, which would take hours.
> 3. Instead, I reprojected the coordinates from angular degrees (EPSG:4326) into metric coordinates (EPSG:32646 - UTM Zone 46N) and indexed all 253,408 centroids into a **`scipy.spatial.cKDTree`**.
> 4. This reduced the lookup time to $O(\log n)$. All 219,928 fires were snapped to their nearest cell centroid in **less than 12 seconds**.
> 5. Furthermore, I applied strict domain filtering to the FIRMS dataset: only `type == 0` (presumed vegetation fires) were retained, automatically eliminating false alarms caused by industrial flares or oil refineries."*

---

#### 🖥️ Slide 13: Member 2 — Viva Defense Points
> **[Member 2 Speaks]:**  
> *"Anticipating key viva questions:
> - **Why UTM Zone 46N projection?** Latitude and longitude degrees do not have constant metric distances on the curved surface of the Earth. A degree of longitude at 22°N is not equal to a degree at 29°N. UTM Zone 46N projects the region onto a Cartesian plane in true meters, ensuring spatial nearest-neighbor queries are physically accurate.
> - **Can we inspect the NetCDF data?** Absolutely. IMD rainfall is stored in binary NetCDF4 (`.nc`) files. Using Python's `xarray` library, we open the multi-dimensional dataset, inspect coordinate dimensions (Latitude, Longitude, Time), and extract point-slice time series using nearest-neighbor interpolation.
> 
> I now hand the presentation over to **Member 3** to explain our Feature Engineering and Wildfire Machine Learning Models."*

---

## 🔥 STAGE 4: MEMBER 3 — FEATURE ENGINEERING & WILDFIRE ML
### 👤 Speaker: Member 3

#### 🖥️ Slide 14: Section Header — Member 3
> **[Member 3 Speaks]:**  
> *"Thank you, Member 2. Respected examiners, I am Member 3, responsible for Feature Engineering and Wildfire Machine Learning Pipelines."*

---

#### 🖥️ Slide 15: 33 Engineered Features for Wildfire Prediction
> **[Member 3 Speaks]:**  
> *"Machine learning models are only as effective as the domain signals provided to them. I engineered a comprehensive feature matrix of **33 predictive indicators** categorized into four groups:
> 
> 1. **Atmospheric Stress Features:** Daily maximum temperature, minimum relative humidity, mean wind speed, and Vapour Pressure Deficit (VPD). When relative humidity drops below 30% and VPD spikes, fuel flammability reaches critical levels.
> 2. **Antecedent Moisture Depletion:** 1-day, 3-day, and 7-day cumulative rainfall lags, surface soil moisture (0–7 cm depth), and our custom **Consecutive Dry Days counter**.
> 3. **Cyclical Temporal Encoding:** Day-of-year has circular continuity — December 31 is directly adjacent to January 1. If fed as a raw integer from 1 to 365, tree algorithms see a massive numerical split. I encoded seasonality using sine and cosine transformations:
>    $$\text{doy\_sin} = \sin\left(\frac{2\pi \cdot \text{DOY}}{365}\right), \quad \text{doy\_cos} = \cos\left(\frac{2\pi \cdot \text{DOY}}{365}\right)$$
>    This allows our models to learn smooth, circular seasonal patterns.
> 4. **Strict Leakage Prevention:** Post-ignition satellite attributes like Fire Radiative Power (`frp_sum`), brightness temperature, and scan angle were aggressively purged. Using them would constitute target leakage because they only exist after a fire has already ignited."*

---

#### 🖥️ Slide 16: Wildfire — 6 Classifiers Compared (The Benchmark Table)
> **[Member 3 Speaks]:**  
> *"On this slide, you see our comprehensive model benchmark table. We did not simply train one algorithm; we rigorously tested six distinct classifiers using a strict temporal split: **2021 to 2023 for training, and unseen 2024 data as the test holdout**:
> 
> - A baseline **DummyClassifier** confirmed the severe class imbalance (positive base rate ~0.2%).
> - **Logistic Regression** achieved an initial ROC-AUC of 0.9040 but suffered from linear boundary limitations.
> - **Gaussian Naive Bayes** achieved 58.3% recall but produced a high false alarm rate of 9.51%.
> - **Decision Trees** showed clear overfitting, dropping from 0.91 CV to 0.72 on the test set.
> - **Random Forest** performed strongly with a 0.9260 Test ROC-AUC.
> - **HistGradientBoosting emerged as our clear champion:**
>   - **Test ROC-AUC: 0.9358** (Cross-validated: 0.9470).
>   - **Highest Test Recall: 68.39%** (catching over two-thirds of all wildland fires).
>   - **False Alarm Rate constrained to just 6.12%**."*

---

#### 🖥️ Slide 17: Wildfire Model Comparison & ROC / PR Curves
> **[Member 3 Speaks]:**  
> *"The visual charts on Slide 17 substantiate these findings.
> - The left graph displays our model comparison bar chart across all metrics.
> - The right graph shows our **ROC curve** and **Precision-Recall curve**.
> 
> Examiners often ask: *Why is the PR-AUC value 0.0061 seemingly small?*  
> Because fire events represent only 0.2% of all daily cell observations. In extreme class imbalances (1 positive per 500 safe days), a standard 0.5 threshold yields high false alarms. By performing precision-recall threshold optimization, we proved our model provides a **30-fold enrichment over random chance**."*

---

#### 🖥️ Slide 18: Feature Importance & Decision Tree Logic
> **[Member 3 Speaks]:**  
> *"Slide 18 demonstrates the interpretability of our model:
> - The feature importance chart proves that **minimum relative humidity**, **cyclical day-of-year**, **soil moisture**, and **3-day antecedent rainfall** are the dominant drivers of fire ignition across Northeast India.
> - On the right, we extracted a shallow surrogate decision tree to illustrate decision boundaries: when relative humidity drops below 34% and consecutive dry days exceed 9, fire probability increases dramatically.
> 
> I now hand over to **Member 4** to cover Landslide Modeling, Statistical Calibration, and Quality Assurance."*

---

## 🌊 STAGE 5: MEMBER 4 — LANDSLIDE ML, CALIBRATION & QA
### 👤 Speaker: Member 4

#### 🖥️ Slide 19: Section Header — Member 4
> **[Member 4 Speaks]:**  
> *"Thank you, Member 3. Respected examiners, I am Member 4, and I oversee Landslide Machine Learning, Bayesian Probability Calibration, and System Quality Assurance."*

---

#### 🖥️ Slide 20: Member 4 — Role & File Ownership
> **[Member 4 Speaks]:**  
> *"My technical contributions span three critical engineering challenges:
> 1. Ingesting and sanitizing unstructured Geological Survey of India landslide records (`src/ingestion/gsi_pdf.py`).
> 2. Developing the Landslide ML pipeline and implementing Bayesian calibration (`src/training/landslide_pipelines.py`, `src/evaluation/metrics.py`).
> 3. Designing and verifying the complete test suite in `tests/test_hima_pipeline.py`.
> 
> When mining GSI landslide bulletins, standard table parsing tools failed due to complex, scanned layouts. I engineered a coordinate-based bounding-box extraction pipeline using `pdfplumber`, extracting **9,970 historical landslide events**.
> 
> Crucially, I uncovered a critical phenomenon: **Survey Bias**. In official records, landslides are documented predominantly near state highways and settlements in Assam. If we had included administrative attributes like `state_name` as features, the machine learning model would have simply memorized geography rather than physical slope physics. I actively purged all administrative spatial identifiers to force the model to rely purely on geophysical triggers: cumulative rainfall, soil saturation, and moisture retention."*

---

#### 🖥️ Slide 21: Landslide Model Comparison & ROC / PR Curves
> **[Member 4 Speaks]:**  
> *"Slide 21 illustrates our Landslide model benchmarks.
> Once again, **HistGradientBoosting outperformed all other algorithms**, achieving an outstanding **Test ROC-AUC of 0.9367** on unseen 2024 test events.
> 
> Because landslides in the Himalayas are triggered predominantly by continuous pore-water pressure spikes, our 3-day and 7-day antecedent rainfall features provided clear decision boundaries."*

---

#### 🖥️ Slide 22: Bayesian Prior Calibration of Probabilities
> **[Member 4 Speaks]:**  
> *"Slide 22 represents one of the most mathematically rigorous aspects of our project: **Bayesian Odds-Ratio Prior Calibration**.
> 
> Standard gradient-boosted trees output raw scores based on training distributions. Because we subsample non-event days during training to prevent class collapse, raw model outputs artificially inflate probabilities — predicting a 40% risk for days when the physical climatological base rate is only 0.2%.
> 
> To correct this, I implemented an analytical Bayesian transformation:
> $$\text{Odds}_{\text{calibrated}} = \text{Odds}_{\text{raw}} \times \left(\frac{\pi_{\text{true}}}{1 - \pi_{\text{true}}}\right) \times \left(\frac{1 - \pi_{\text{train}}}{\pi_{\text{train}}}\right)$$
> 
> As displayed on the calibration curve:
> - Our **Brier Score before calibration was 0.083** (indicating severe overconfidence).
> - After Bayesian calibration, our **Brier Score dropped to 0.0005 — an improvement of 99.4%**.
> Our dashboard now displays mathematically sound, true daily probabilities."*

---

#### 🖥️ Slide 23: The 9 Automated Unit & Integrity Tests (All PASSED)
> **[Member 4 Speaks]:**  
> *"In software engineering, reproducibility is paramount. To ensure HIMA's robustness, I authored a comprehensive test suite of **9 automated pytest unit tests**.
> 
> As shown on Slide 23, all 9 tests pass in **2.56 seconds**:
> 1. `test_config_loads_and_has_disclaimer`: Validates that system configuration and scientific disclaimers are present.
> 2. `test_days_since_rain_preserves_missing_gaps`: Confirms missing ERA5 months are kept as `NaN` and not corrupted into zeroes.
> 3. `test_ind_season_mapping`: Validates that all calendar days correctly map to IMD meteorological seasons.
> 4. `test_bayes_prior_adjustment_monotonic_and_bounded`: Verifies mathematically that calibrated probabilities remain bounded within $[0, 1]$ and strictly monotonic.
> 5. `test_risk_band_boundaries`: Checks that Low, Moderate, High, and Critical risk bins do not overlap.
> 6. `test_no_post_event_leakage_in_features`: Confirms no post-fire satellite indicators exist in the feature matrix.
> 7. `test_grid_boundaries_facts_if_built`: Checks the geometric bounds of our 253,408 grid cells.
> 8. `test_validated_wildfire_predictor_inference`: Verifies end-to-end forward-pass inference on sample vectors.
> 9. `test_required_deliverables_exist`: Validates that all maps, joblib models, and figure artifacts exist on disk.
> 
> I now hand back to **Member 1** to lead our final summary and conclusions."*

---

## 📊 STAGE 6: JOINT WRAP-UP & CONCLUSION
### 👤 Speaker: Member 1 (Lead Presenter)

#### 🖥️ Slides 24–27: EDA Gallery (Correlation, Trends & Confusions)
> **[Member 1 Speaks]:**  
> *"Slides 24 through 27 showcase our Exploratory Data Analysis:
> - **Slide 24:** Our Correlation Heatmap reveals strong inverse correlation between relative humidity and fire ignition, while the seasonal plot confirms our March–April fire peak.
> - **Slide 25:** Displays our full Confusion Matrix grids for both hazards across all 6 classifiers.
> - **Slide 26:** Confirms the heavy right-skewed rainfall distribution triggering slope failures."*

---

#### 🖥️ Slide 28: Master Results Summary Table
> **[Member 1 Speaks]:**  
> *"Slide 28 consolidates our entire project's experimental findings:
> - Both Wildfire and Landslide models achieved greater than **0.93 ROC-AUC**.
> - Wildfire caught **68.4% of real events** with only a **6.1% false alarm rate**.
> - Bayesian calibration delivered a **99.4% Brier Score optimization**.
> - Over **253,408 grid cells** are modeled seamlessly."*

---

#### 🖥️ Slide 29: Limitations & Planned Future Work
> **[Member 1 Speaks]:**  
> *"We maintain complete academic honesty regarding our current limitations:
> - ERA5 reanalysis data carries a multi-week publication lag, making our current system ideal for post-event analysis and seasonal risk modeling rather than same-hour alerts.
> - In our next phase, we plan to integrate ISRO MOSDAC numerical weather forecasts for 6-hour real-time predictions, incorporate 10-meter Sentinel-2 NDVI vegetative fuel layers, and add SMS alerts for forest rangers."*

---

#### 🖥️ Slide 30: Thank You & Viva Defense Opening
> **[Member 1 Speaks]:**  
> *"In conclusion, Project HIMA successfully demonstrates how multi-hazard machine learning, rigorous geospatial engineering, and responsive offline-first software can work together to protect Northeast India.
> 
> Our complete source code, documentation, and models are available openly on GitHub at `github.com/ujjww4ll/HIMA`.
> 
> We thank our professors and evaluators for their time and guidance. We are now open for questions."*

---

## 🏆 Summary Checklist for Your Team
| Step | Action | Completed? |
|:---:|:---|:---:|
| 1 | Double-click `HIMA_Project_Presentation.pptx` to open slides | ✅ |
| 2 | Member 1 starts speech on Slide 1 | ✅ |
| 3 | Hand over smoothly at Slide 10 (Member 2), Slide 14 (Member 3), Slide 19 (Member 4) | ✅ |
| 4 | Conclude jointly on Slide 28–30 | ✅ |
