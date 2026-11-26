# Flood Prediction and Early Warning System
## with Multi-Hazard Landslide and Wildfire Intelligence
**Course:** Application of Artificial Intelligence (AI-ML / CSET312)  
**Academic Capstone Project Report**  
**Team Members:** Sachin (Lead), Anshul, Ujjwal, Aadi, Malvika, Shubhangi, Sonam  

---

## Executive Abstract
Natural hazards across India exhibit intense seasonal coupling. Pre-monsoon aridity triggers forest fires, followed by monsoon rainfalls that destabilize slopes into landslides and inundate river basins into catastrophic floods. 
This project presents an end-to-end Machine Learning Framework for Flood Prediction and Early Warning, augmented with multi-hazard intelligence for landslides and wildfires. 
Coupling NASA FIRMS VIIRS (219,928 fires), IMD 0.25° Gridded Daily Rainfall (48 months), ECMWF ERA5-Land Reanalysis (44 months), GSI Landslide Inventories (9,970 records), and INDOFLOODS (4,548 river flood events), we construct a 253,408-cell metric grid in EPSG:32646 (UTM Zone 46N) and benchmark 6 classifiers per hazard. HistGradientBoosting won all categories (Flood ROC-AUC: 0.9557, Recall: 98.56%; Wildfire ROC-AUC: 0.9358; Landslide ROC-AUC: 0.9367). We diagnosed and solved a critical spatial coordinate domain-shift bug, enabling universal hydrological generalization across Indian river basins. The platform is served live via a multi-threaded Python REST API and an interactive web dashboard.

---

## 1. 7-Member Responsibility Matrix

| Member | Role Title | Codebase Ownership | Core Technical Contribution |
| :--- | :--- | :--- | :--- |
| **Sachin (Lead)** | Full-Stack AI Engineer | `frontend/`, `src/api/predict.py`, `run_hima.bat` | Web dashboard, REST API server, SVG map, live gauge, pipeline launcher. |
| **Anshul** | Geospatial Data Lead | `src/geospatial/`, `src/audit/`, `src/ingestion/` | 253,408 1 km² grid (EPSG:32646), FIRMS fires, IMD/ERA5 KD-Tree joins. |
| **Ujjwal** | Wildfire ML Lead | `src/features/`, `src/training/wildfire_pipelines.py` | 33 features, cyclical DOY transformations, 6-classifier wildfire benchmark. |
| **Aadi** | Landslide & QA Lead | `src/ingestion/gsi.py`, `src/training/landslide_pipelines.py`, `tests/` | GSI PDF mining via pdfplumber, Bayesian prior odds calibration, 9 pytest test cases. |
| **Malvika** | Flood Ingestion Lead | `src/ingestion/flood.py`, `data/raw/flood/` | INDOFLOODS ingestion (4,548 events), CHIRPS antecedent lags (T1d–T10d), Parquet sync. |
| **Shubhangi** | Flood ML Lead | `src/training/flood_pipelines.py`, `models/flood_model.joblib` | 6 flood classifiers benchmark, GBDT tuning (0.9557 Test ROC-AUC, 98.56% Recall). |
| **Sonam** | Domain Transfer Lead | `src/api/predict.py`, `frontend/app.js` | Solved spatial coordinate domain shift (1.7% bug), catchment scaling (100–50k km²), flood presets. |
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
- **Solution:** Removed `Latitude` and `Longitude` from features to create a pure physical hydrological model based strictly on antecedent rainfall lags ($T_{1d}$–$T_{10d}$) and catchment scale ($km^2$). Expanded the catchment slider to 50,000 km².
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
