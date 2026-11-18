# HIMA — Hazard Intelligence, Monitoring & Assessment (Northeast India)

> **Disclaimer:** *Research risk estimate only — not an official warning.* All probabilities, maps, and provisional risk bands produced by this academic B.Tech Data Science / CSET312 AI-ML project are research demonstrations and must **not** be treated as official government alerts or operational forecasts.

## 1. Project Overview
HIMA is a reproducible geospatial hazard-risk assessment and machine-learning pipeline for **Northeast India** (`2021–2024`) built on a metric **1 km × 1 km × 1 day** analytical frame (`EPSG:32646`, WGS 84 / UTM Zone 46N).

- **Workspace (code, interim/processed outputs, models, figures, notebooks):** `c:\Users\lenovo\Desktop\aiml project`
- **Raw Data Root (strictly read-only, never modified):** `C:\Users\lenovo\Downloads\hima`
- **Study Region (configurable in `config/project.yaml`):** All 7 Northeast India Sister States (`Arunachal Pradesh`, `Assam`, `Manipur`, `Meghalaya`, `Mizoram`, `Nagaland`, `Tripura`) — `253,412 km²` (`253,408` 1 km grid cells, `0` outside boundary).
  - *Sikkim exclusion note:* Sikkim (`88.0°E–88.9°E`) lies ~100 km west of the local processed ERA5 longitude cutoff (`89.8°E–97.4°E`) and is excluded from the ERA5-coupled grid to prevent 100+ km spatial mismatch.

---

## 2. Verified Data Audit & Real-Data Discoveries (2021–2024)

| Dataset | Source Location (Read-Only) | Verified Coverage & Key Audit Findings |
|---|---|---|
| **State Boundaries** | `data\raw\boundaries.zip` | `state_NWIC.shp` (`EPSG:7755`, 36 states). Repaired `1` invalid polygon; canonicalized `"Arunanchal Pradesh"` → `"Arunachal Pradesh"`. |
| **NASA FIRMS (Wildfire)** | `DL_FIRE_SV-C2_*.zip` | Row-level audit revealed `DL_FIRE_SV-C2_816518.zip` spans **2022–2023** (`579,733` national rows in 2023), yielding **complete 2021–2024 coverage** after deduplicating overlapping 2022 records. Total NE India detections: **`223,904`** (`219,928` vegetation fires `type == 0`; `3,908` static industrial/oil flares `type == 2` filtered out). |
| **IMD Daily Rainfall** | `data\raw\RF25_ind2021..2024_rfp25.nc` | **48 / 48 months complete.** CF `TIME` coordinate (`days since 1900-12-31`) decoded cleanly; units `mm/day`; `415` active 0.25° grid points (median distance to 1 km cells: `10.57 km`). |
| **ERA5-Land Daily Weather** | `data\processed\weather\ERA5_Land_daily_*.nc` | **44 / 48 months present.** Missing `2023-08`, `2023-09`, `2023-11`, `2023-12` (`303,902` missing grid-days preserved as `NaN` with `era5_missing_flag = 1`, **never** replaced with `0`). Verified Celsius values (`temperature_c`, `dewpoint_c`), converted `rainfall_m × 1000` → `era5_rainfall_mm` (kept separate from IMD), `2,491` active 0.1° grid points (median distance: `4.21 km`). |
| **NASA COOLR (Landslide)** | `COOLR_India_Events.json` | `176` candidate India events — **0 in Northeast India** (all `176` lie in Uttarakhand & Himachal Pradesh, `76.79–77.25°E, 30.82–31.35°N`). |
| **GSI Field-Validated PDF** | `GSI_Landslide_Inventory_Field_Validated.pdf` | Structured 904-page text-extractable tabular PDF. Word-coordinate parsing extracted **`10,731`** NE India records (`10,730` valid coordinates; **`9,970`** inside the 7-state study boundary: `8,601` undated spatial slides, `696` pre-2021 dated slides, and **`673` exact-day 2021–2024 slides → `463` unique cell-days**). |
| **Planned Static Layers** | DEM, WorldCover, MODIS NDVI, SoilGrids, Geology, ISRO Atlas | **Not present locally.** Never fabricated; documented as explicit limitations. |

---

## 3. Model Results (Syllabus-Aligned CSET312 Comparison)

All models use identical features, training-only imputation/encoding/scaling inside `scikit-learn` `Pipeline`s, `GridSearchCV` inside **5-fold spatial `StratifiedGroupKFold`** (50 km × 50 km spatial blocks) on **2021–2023**, and unseen future-year evaluation on **2024**.

### 3.1 Wildfire Classification (Primary Model)
- **Train (`2021–2023`):** `717,324` rows (`119,554` positive 1 km cell-days + 5:1 uniform background negatives).
- **Realistic-Prevalence Test (`2024`):** `1,000,000` uniformly sampled 1 km cell-days (`348` true positives; realistic base rate = **`0.000348`**).

| Model | Syllabus Role | Spatial CV ROC-AUC | Spatial CV PR-AUC | 2024 Test ROC-AUC | 2024 Test PR-AUC | 2024 Recall | 2024 Precision | 2024 FAR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `DummyClassifier (Prior)` | Baseline utility | 0.4962 | 0.1651 | 0.5000 | 0.0003 | 0.0000 | 0.0000 | 0.0000 |
| `Gaussian Naive Bayes` | CSET312 Core | 0.8913 | 0.5877 | 0.8621 | 0.0025 | 0.5833 | 0.0021 | 0.0951 |
| `Logistic Regression` | CSET312 Core | 0.9216 | 0.6802 | 0.9040 | 0.0045 | 0.6494 | 0.0028 | 0.0812 |
| `Decision Tree` | CSET312 Core | 0.9259 | 0.7223 | 0.9049 | 0.0046 | 0.5920 | 0.0033 | 0.0619 |
| `Random Forest` | Tabular Extension | 0.9434 | 0.7761 | 0.9260 | **0.0067** | 0.6322 | **0.0044** | **0.0501** |
| **`HistGradientBoosting`** *(Selected by CV PR-AUC)* | GBDT Extension | **0.9470** | **0.7817** | **0.9358** | 0.0061 | **0.6839** | 0.0039 | 0.0612 |

- **Per-state 2024 ROC-AUC (`HistGradientBoosting`):** Ranges from **`0.8997`** (Assam) to **`0.9689`** (Tripura) across all 7 states.
- **Calibration:** Analytical Bayes prior-odds adjustment (using strictly 2021–2023 population prevalence `0.000431`) improves 2024 Brier score from `0.07–0.21` raw down to **`0.0002–0.0011`**.
- **Top Physical Drivers (Permutation Importance):** Seasonal cycle (`sin_doy`, `cos_doy`), location (`centroid_lat/lon`), `relative_humidity_min`, `era5_soil_water_mean_7d`, `dewpoint_depression_c`, `era5_temp_max_7d`, `era5_rain_sum_3d`, and `imd_rain_sum_3d`.

### 3.2 Preliminary Landslide Classification (Weather-Trigger Only)
- **Train (`2021–2023`):** `10,097` rows (`97` unique dated GSI positive cell-days + uniform background negatives; `state_name` intentionally excluded to prevent exploiting 2024 Mizoram survey bias).
- **Test (`2024`):** `100,366` rows (`366` unseen 2024 dated GSI positive cell-days + `100,000` uniform 2024 background cell-days; test prevalence = `0.00365`).

| Model | Spatial CV ROC-AUC | Spatial CV PR-AUC | 2024 Test ROC-AUC | 2024 Test PR-AUC | 2024 Recall | 2024 Precision | 2024 FAR |
|---|---:|---:|---:|---:|---:|---:|---:|
| `DummyClassifier (Prior)` | 0.3493 | 0.0074 | 0.5000 | 0.0036 | 0.0000 | 0.0000 | 0.0000 |
| `Gaussian Naive Bayes` | 0.8134 | 0.0859 | 0.8957 | 0.0297 | 0.2377 | 0.0377 | 0.0222 |
| `Decision Tree` | 0.7033 | 0.2416 | 0.8214 | 0.0933 | 0.0000 | 0.0000 | 0.0000 |
| `Logistic Regression` | **0.8637** | 0.1003 | 0.9375 | 0.1160 | **0.4863** | 0.1529 | 0.0099 |
| `Random Forest` | 0.8561 | 0.2081 | **0.9502** | 0.1366 | 0.1967 | 0.1920 | **0.0030** |
| **`HistGradientBoosting`** *(Selected by CV PR-AUC)* | 0.8483 | **0.3528** | 0.9367 | **0.2187** | 0.4290 | **0.2163** | 0.0057 |

> **Important Landslide Caveat:** Because static terrain layers (DEM/slope/aspect, WorldCover, SoilGrids, geology) are absent locally and 529/673 dated 2021–2024 GSI slides reflect Mizoram's 2024 field surveys (e.g., Cyclone Remal), this landslide classifier is strictly a **preliminary rainfall/weather-trigger demonstration**, not a complete slope-susceptibility model.

---

## 4. Project Structure
```text
aiml project/
├── config/
│   ├── project.yaml                # Paths, study states, CRS, years, split & risk band config
│   └── feature_schema.json         # Feature definitions & excluded post-event leakage columns
├── data/
│   ├── interim/                    # Extracted boundaries, FIRMS CSVs, COOLR/GSI, daily weather
│   ├── processed/                  # 1 km grid, weather features, wildfire.parquet, landslide*.parquet
│   └── reports/                    # Inventory CSV, audit JSON, data dictionary, feasibility reports
├── models/                         # Saved .joblib pipelines & model cards (wildfire & landslide)
├── notebooks/                      # 01_data_audit.ipynb .. 06_model_comparison.ipynb
├── outputs/
│   ├── maps/                       # Study area & 1 km grid, wildfire hotspots, landslide inventory
│   ├── figures/                    # EDA, ROC/PR, confusion matrices, plot_tree, importance, calibration
│   └── tables/                     # Model comparison, per-state, per-season, feature importance CSVs
├── scripts/
│   └── generate_notebooks.py       # Regenerates the 6 interactive notebooks
├── src/
│   ├── config.py
│   ├── audit/inventory.py
│   ├── geospatial/{boundaries.py, grid.py}
│   ├── ingestion/{firms.py, imd.py, era5.py, coolr.py, gsi_pdf.py}
│   ├── features/weather.py
│   ├── labels/{wildfire.py, landslide.py}
│   ├── training/{pipelines.py, landslide_pipelines.py}
│   ├── evaluation/{metrics.py, eda.py}
│   └── api/predict.py              # Validated wildfire research inference API (GET /health, POST /predict)
├── tests/test_hima_pipeline.py     # Unit & data-integrity test suite
├── run_pipeline.py                 # Single-command end-to-end runner
└── requirements.txt
```

---

## 5. Setup & Run Instructions

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Run the full reproducible pipeline (reads C:\Users\lenovo\Downloads\hima read-only)
python run_pipeline.py

# Or re-run features, labels, modeling, and EDA using existing interim files:
python run_pipeline.py --skip-ingest

# 3. Run unit & data-integrity tests
pytest -v

# 4. (Optional) Start local research wildfire inference API (http://127.0.0.1:8000)
python -m src.api.predict
```

---

## 6. Key Limitations (Must Be Reported Alongside Results)
1. **Missing static environmental layers:** DEM/slope/aspect, ESA WorldCover, MODIS NDVI, SoilGrids, geology, and ISRO NRSC Landslide Atlas were not found locally and were never fabricated.
2. **ERA5 temporal & spatial gaps:** Four months are missing in 2023 (`2023-08`, `2023-09`, `2023-11`, `2023-12`) and were preserved as `NaN`; local ERA5 starts at `89.8°E`, excluding Sikkim (`88.0°E–88.9°E`).
3. **Coarse-to-fine resolution mismatch:** Spatial joining ERA5 (`~9–11 km`) and IMD (`~25 km`) onto the 1 km fishnet grid does not create true 1 km physical meteorological detail.
4. **Satellite & inventory label incompleteness:** FIRMS active-fire detections are affected by clouds, overpass timing, and agricultural/jhum burning; "no record" (`0`) does not guarantee zero hazard occurred.
5. **Landslide reporting bias:** `0/176` COOLR records fell in Northeast India, and `8,601/9,970` GSI Northeast India field slides lack exact daily occurrence dates; dated 2021–2024 GSI slides heavily reflect 2024 Mizoram surveys (`529/673`).
6. **Non-operational status:** Provisional UI risk bands (`LOW 0–30%`, `MODERATE 30–60%`, `HIGH 60–80%`, `CRITICAL 80–100%`) are display categories only, not validated operational warning thresholds.

