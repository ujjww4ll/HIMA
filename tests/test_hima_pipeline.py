"""Unit and data-integrity tests for the HIMA project."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PROJECT_ROOT, load_config
from src.evaluation.metrics import assign_risk_band, bayes_prior_adjust
from src.features.weather import compute_days_since_rain_array
from src.labels.wildfire import assign_imd_season
from src.training.pipelines import ALL_FEATURES


def test_config_loads_and_has_disclaimer():
    cfg = load_config()
    assert "disclaimer" in cfg["project"]
    assert "not an official warning" in cfg["project"]["disclaimer"].lower()
    assert cfg["geospatial"]["grid_cell_size_m"] == 1000
    assert cfg["geospatial"]["projected_crs"] == "EPSG:32646"


def test_days_since_rain_preserves_missing_gaps():
    # Days 0: rain (5mm), Day 1: dry (0mm), Day 2: dry (0mm), Day 3: missing (NaN), Day 4: dry (0mm), Day 5: rain (3mm)
    rain = np.array([5.0, 0.0, 0.0, np.nan, 0.0, 3.0], dtype=np.float32)
    dsr = compute_days_since_rain_array(rain, threshold_mm=1.0, cap=60)
    assert dsr[0] == 0.0
    assert dsr[1] == 1.0
    assert dsr[2] == 2.0
    assert np.isnan(dsr[3]), "Missing weather day must remain NaN, never 0"
    assert dsr[4] == 1.0, "Streak must reset cleanly after NaN gap instead of bridging across missing months"
    assert dsr[5] == 0.0


def test_imd_season_mapping():
    months = pd.Series([1, 3, 7, 10, 12])
    seasons = assign_imd_season(months).tolist()
    assert seasons == ["Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon", "Winter"]


def test_bayes_prior_adjustment_monotonic_and_bounded():
    probs = np.array([0.01, 0.25, 0.50, 0.75, 0.99])
    adj = bayes_prior_adjust(probs, pi_train=0.5, pi_target=0.001)
    assert np.all(adj >= 0.0) and np.all(adj <= 1.0)
    assert np.all(np.diff(adj) > 0), "Prior adjustment must be strictly monotonic"
    # At p=0.5 with pi_train=0.5, adjusted prob must equal pi_target
    assert np.isclose(adj[2], 0.001, atol=1e-6)


def test_risk_band_boundaries():
    bands = assign_risk_band(np.array([0.05, 0.30, 0.65, 0.90]))
    assert list(bands) == [
        "LOW (0-30%)",
        "MODERATE (30-60%)",
        "HIGH (60-80%)",
        "CRITICAL (80-100%)",
    ]


def test_no_post_event_leakage_in_features():
    forbidden = {
        "fire_detected",
        "detection_count",
        "frp_sum",
        "frp_mean",
        "frp_max",
        "brightness_mean",
        "brightness_max",
        "day_detections",
        "night_detections",
        "high_conf_count",
        "nominal_conf_count",
        "low_conf_count",
    }
    overlap = forbidden.intersection(ALL_FEATURES)
    assert not overlap, f"Post-event leakage columns found in ALL_FEATURES: {overlap}"


def test_grid_and_boundaries_artifacts_if_built():
    grid_meta_path = PROJECT_ROOT / "data" / "reports" / "grid_metadata.json"
    if grid_meta_path.exists():
        meta = json.loads(grid_meta_path.read_text(encoding="utf-8"))
        assert meta["cells_outside_boundary"] == 0
        assert meta["total_cells"] > 200_000
        assert meta["cell_size_m"] == 1000


def test_validated_wildfire_predictor_inference():
    from src.api.predict import WildfireRiskPredictor

    model_path = PROJECT_ROOT / "models" / "wildfire_best_model.joblib"
    assert model_path.exists(), "Trained wildfire_best_model.joblib must exist"
    predictor = WildfireRiskPredictor(model_path)
    sample = [
        {
            "temperature_c": 31.0,
            "dewpoint_c": 10.0,
            "dewpoint_depression_c": 21.0,
            "wind_speed_ms": 2.5,
            "soil_water_layer1": 0.14,
            "era5_rainfall_mm": 0.0,
            "relative_humidity_mean": 32.0,
            "relative_humidity_min": 18.0,
            "era5_temp_mean_7d": 29.5,
            "era5_temp_max_7d": 32.0,
            "era5_rh_min_7d": 16.0,
            "era5_rh_mean_7d": 35.0,
            "era5_soil_water_mean_7d": 0.15,
            "era5_wind_mean_7d": 2.2,
            "era5_rain_sum_3d": 0.0,
            "era5_rain_sum_7d": 0.0,
            "era5_rain_sum_15d": 1.0,
            "era5_days_since_rain": 20.0,
            "imd_rain_1d": 0.0,
            "imd_rain_lag1d": 0.0,
            "imd_rain_sum_3d": 0.0,
            "imd_rain_sum_7d": 0.0,
            "imd_rain_sum_15d": 0.0,
            "imd_rain_max_7d": 0.0,
            "imd_rainy_days_7d": 0.0,
            "imd_rainy_days_15d": 0.0,
            "imd_days_since_rain": 25.0,
            "centroid_lat": 23.5,
            "centroid_lon": 92.8,
            "sin_doy": 0.99,
            "cos_doy": 0.05,
            "state_name": "Mizoram",
            "season": "Pre-Monsoon",
        },
        {
            "temperature_c": 24.0,
            "dewpoint_c": 23.0,
            "dewpoint_depression_c": 1.0,
            "wind_speed_ms": 1.0,
            "soil_water_layer1": 0.48,
            "era5_rainfall_mm": 65.0,
            "relative_humidity_mean": 96.0,
            "relative_humidity_min": 90.0,
            "era5_temp_mean_7d": 24.5,
            "era5_temp_max_7d": 26.0,
            "era5_rh_min_7d": 85.0,
            "era5_rh_mean_7d": 94.0,
            "era5_soil_water_mean_7d": 0.47,
            "era5_wind_mean_7d": 1.2,
            "era5_rain_sum_3d": 140.0,
            "era5_rain_sum_7d": 280.0,
            "era5_rain_sum_15d": 550.0,
            "era5_days_since_rain": 0.0,
            "imd_rain_1d": 70.0,
            "imd_rain_lag1d": 45.0,
            "imd_rain_sum_3d": 160.0,
            "imd_rain_sum_7d": 320.0,
            "imd_rain_sum_15d": 600.0,
            "imd_rain_max_7d": 95.0,
            "imd_rainy_days_7d": 7.0,
            "imd_rainy_days_15d": 14.0,
            "imd_days_since_rain": 0.0,
            "centroid_lat": 26.1,
            "centroid_lon": 91.7,
            "sin_doy": -0.25,
            "cos_doy": -0.96,
            "state_name": "Assam",
            "season": "Monsoon",
        },
    ]
    out = predictor.predict(sample)
    assert "not an official warning" in out["disclaimer"].lower()
    preds = out["predictions"]
    assert len(preds) == 2
    # Dry pre-monsoon Mizoram cell must score strictly higher than flooded monsoon Assam cell
    assert preds[0]["raw_score"] > preds[1]["raw_score"]
    assert preds[0]["calibrated_daily_probability"] > preds[1]["calibrated_daily_probability"]


def test_required_deliverables_exist():
    expected = [
        "data/reports/data_inventory.csv",
        "data/reports/data_audit_summary.json",
        "data/reports/data_quality_report.md",
        "data/reports/data_dictionary.md",
        "data/reports/landslide_feasibility.json",
        "models/wildfire_best_model.joblib",
        "models/wildfire_model_card.json",
        "models/landslide_preliminary_model.joblib",
        "models/landslide_model_card.json",
        "outputs/maps/study_area_and_grid.png",
        "outputs/maps/wildfire_hotspot_map.png",
        "outputs/maps/landslide_inventory_map.png",
        "outputs/figures/wildfire_model_comparison.png",
        "outputs/figures/wildfire_roc_pr_curves.png",
        "outputs/figures/wildfire_decision_tree.png",
        "outputs/figures/wildfire_feature_importance.png",
        "outputs/figures/wildfire_calibration.png",
        "outputs/figures/landslide_rainfall_eda.png",
        "outputs/figures/landslide_roc_pr_curves.png",
        "outputs/tables/wildfire_model_comparison.csv",
        "outputs/tables/landslide_model_comparison.csv",
        "README.md",
        "requirements.txt",
    ]
    missing = [p for p in expected if not (PROJECT_ROOT / p).exists()]
    assert not missing, f"Missing expected deliverables: {missing}"

