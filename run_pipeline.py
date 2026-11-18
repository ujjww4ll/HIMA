"""Master single-command runner for the HIMA project.

Usage:
    python run_pipeline.py                 # Full end-to-end run + notebooks + tests + demo prediction
    python run_pipeline.py --skip-ingest   # Fast re-run (reuse data/interim, retrain & plot + tests)
    python run_pipeline.py --demo          # Instant demo: print saved metrics, run tests & sample prediction
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

import pandas as pd

from scripts.generate_notebooks import generate_all as generate_notebooks
from src.api.predict import WildfireRiskPredictor
from src.audit.inventory import run_audit
from src.config import PROJECT_ROOT
from src.evaluation.eda import run_all_eda
from src.features.weather import build_all_weather_features
from src.geospatial.boundaries import build_study_boundaries
from src.geospatial.grid import build_1km_grid
from src.ingestion.coolr import ingest_coolr
from src.ingestion.era5 import ingest_era5_processed
from src.ingestion.firms import ingest_firms
from src.ingestion.gsi_pdf import inspect_and_extract_gsi_pdf
from src.ingestion.imd import ingest_imd
from src.labels.landslide import build_landslide_dataset
from src.labels.wildfire import build_wildfire_dataset
from src.training.landslide_pipelines import train_and_evaluate_landslide
from src.training.pipelines import train_and_evaluate_wildfire


def print_summary_and_demo() -> None:
    """Print model comparison tables, run pytest, and run a sample wildfire inference demo."""
    wf_csv = PROJECT_ROOT / "outputs" / "tables" / "wildfire_model_comparison.csv"
    ls_csv = PROJECT_ROOT / "outputs" / "tables" / "landslide_model_comparison.csv"

    if wf_csv.exists():
        print("\n=== WILDFIRE MODEL COMPARISON (Train 2021-2023 -> Realistic 2024 Test) ===")
        df = pd.read_csv(wf_csv)
        cols = ["model", "cv_roc_auc", "cv_pr_auc", "test_roc_auc", "test_pr_auc", "test_recall", "test_precision", "test_false_alarm_rate"]
        print(df[cols].to_string(index=False))

    if ls_csv.exists():
        print("\n=== PRELIMINARY LANDSLIDE MODEL COMPARISON (Weather-Only, Train 2021-2023 -> 2024 Test) ===")
        df = pd.read_csv(ls_csv)
        cols = ["model", "cv_roc_auc", "cv_pr_auc", "test_roc_auc", "test_pr_auc", "test_recall", "test_precision", "test_false_alarm_rate"]
        print(df[cols].to_string(index=False))

    print("\n=== SAMPLE WILDFIRE RISK PREDICTION DEMO ===")
    predictor = WildfireRiskPredictor()
    demo_records = [
        {
            "temperature_c": 31.0, "dewpoint_c": 10.0, "dewpoint_depression_c": 21.0,
            "wind_speed_ms": 2.5, "soil_water_layer1": 0.14, "era5_rainfall_mm": 0.0,
            "relative_humidity_mean": 32.0, "relative_humidity_min": 18.0,
            "era5_temp_mean_7d": 29.5, "era5_temp_max_7d": 32.0, "era5_rh_min_7d": 16.0,
            "era5_rh_mean_7d": 35.0, "era5_soil_water_mean_7d": 0.15, "era5_wind_mean_7d": 2.2,
            "era5_rain_sum_3d": 0.0, "era5_rain_sum_7d": 0.0, "era5_rain_sum_15d": 1.0,
            "era5_days_since_rain": 20.0, "imd_rain_1d": 0.0, "imd_rain_lag1d": 0.0,
            "imd_rain_sum_3d": 0.0, "imd_rain_sum_7d": 0.0, "imd_rain_sum_15d": 0.0,
            "imd_rain_max_7d": 0.0, "imd_rainy_days_7d": 0.0, "imd_rainy_days_15d": 0.0,
            "imd_days_since_rain": 25.0, "centroid_lat": 23.5, "centroid_lon": 92.8,
            "sin_doy": 0.99, "cos_doy": 0.05, "state_name": "Mizoram", "season": "Pre-Monsoon",
        },
        {
            "temperature_c": 24.0, "dewpoint_c": 23.0, "dewpoint_depression_c": 1.0,
            "wind_speed_ms": 1.0, "soil_water_layer1": 0.48, "era5_rainfall_mm": 65.0,
            "relative_humidity_mean": 96.0, "relative_humidity_min": 90.0,
            "era5_temp_mean_7d": 24.5, "era5_temp_max_7d": 26.0, "era5_rh_min_7d": 85.0,
            "era5_rh_mean_7d": 94.0, "era5_soil_water_mean_7d": 0.47, "era5_wind_mean_7d": 1.2,
            "era5_rain_sum_3d": 140.0, "era5_rain_sum_7d": 280.0, "era5_rain_sum_15d": 550.0,
            "era5_days_since_rain": 0.0, "imd_rain_1d": 70.0, "imd_rain_lag1d": 45.0,
            "imd_rain_sum_3d": 160.0, "imd_rain_sum_7d": 320.0, "imd_rain_sum_15d": 600.0,
            "imd_rain_max_7d": 95.0, "imd_rainy_days_7d": 7.0, "imd_rainy_days_15d": 14.0,
            "imd_days_since_rain": 0.0, "centroid_lat": 26.1, "centroid_lon": 91.7,
            "sin_doy": -0.25, "cos_doy": -0.96, "state_name": "Assam", "season": "Monsoon",
        },
    ]
    res = predictor.predict(demo_records)
    print(f"Model: {res['model_name']} | {res['disclaimer']}")
    print("  Case 0 (Dry Pre-Monsoon Mizoram):", json.dumps(res["predictions"][0]))
    print("  Case 1 (Wet Monsoon Assam):      ", json.dumps(res["predictions"][1]))

    print("\n=== RUNNING UNIT & INTEGRITY TESTS (pytest) ===")
    subprocess.run([sys.executable, "-m", "pytest", "-v"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HIMA Hazard Intelligence & ML Pipeline.")
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip raw-data audit and ingestion steps (reuse existing files in data/interim).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Instant verification & presentation demo using already trained models and tables.",
    )
    args = parser.parse_args()

    if args.demo:
        print_summary_and_demo()
        return

    if not args.skip_ingest:
        print("[1/11] Running fresh read-only data audit...")
        run_audit()
        print("[2/11] Extracting and validating state boundaries...")
        build_study_boundaries()
        print("[3/11] Building projected 1 km x 1 km fishnet grid...")
        build_1km_grid()
        print("[4/11] Ingesting NASA FIRMS wildfire archives...")
        ingest_firms()
        print("[5/11] Ingesting IMD daily rainfall NetCDFs...")
        ingest_imd()
        print("[6/11] Ingesting ERA5-Land processed daily weather NetCDFs...")
        ingest_era5_processed()
        print("[7/11] Ingesting NASA COOLR & GSI field-validated landslide records...")
        ingest_coolr()
        inspect_and_extract_gsi_pdf()

    print("[8/11] Engineering leakage-safe daily weather features...")
    build_all_weather_features()

    print("[9/11] Building wildfire modeling dataset & landslide inventory/modeling dataset...")
    build_wildfire_dataset()
    build_landslide_dataset()

    print("[10/11] Training syllabus-aligned wildfire & preliminary landslide classifiers + EDA plots...")
    train_and_evaluate_wildfire()
    train_and_evaluate_landslide()
    run_all_eda()

    print("[11/11] Refreshing Jupyter notebooks, printing results, and running tests...")
    generate_notebooks()
    print_summary_and_demo()

    print("\nHIMA pipeline completed successfully.")


if __name__ == "__main__":
    main()
