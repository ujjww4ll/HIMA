"""Generate the 6 structured Jupyter notebooks in notebooks/ for interactive B.Tech Data Science review."""

from __future__ import annotations

from pathlib import Path
import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NB_DIR = PROJECT_ROOT / "notebooks"


def make_nb(title: str, intro_md: str, cells: list[tuple[str, str]]) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(f"# {title}\n\n{intro_md}")]
    for ctype, content in cells:
        if ctype == "md":
            nb.cells.append(nbf.v4.new_markdown_cell(content))
        else:
            nb.cells.append(nbf.v4.new_code_cell(content))
    return nb


def generate_all() -> None:
    NB_DIR.mkdir(parents=True, exist_ok=True)

    notebooks = {
        "01_data_audit.ipynb": (
            "01 — HIMA Recursive Data Audit & Quality Report",
            "Read-only audit of `C:\\Users\\lenovo\\Downloads\\hima`. Inspects file inventory, schemas, "
            "date coverage for 2021–2024, IMD CF time decoding, ERA5 missing months, FIRMS multi-year "
            "archives, COOLR fields, GSI PDF structure, and absent static datasets.",
            [
                ("code", "import json, pandas as pd\nfrom pathlib import Path\n\nROOT = Path('..')\ninv = pd.read_csv(ROOT / 'data/reports/data_inventory.csv')\ninv.groupby('category')[['size_mb']].agg(['count', 'sum'])"),
                ("code", "summary = json.loads((ROOT / 'data/reports/data_audit_summary.json').read_text(encoding='utf-8'))\nprint('Total files:', summary['total_files_scanned'], '| Total GB:', summary['total_size_gb'])\nprint('FIRMS years:', summary['coverage']['firms_years_all'])\nprint('IMD missing 2021-2024:', summary['coverage']['imd_missing_in_target'])\nprint('ERA5 missing 2021-2024:', summary['coverage']['era5_processed_missing_in_target'])\nprint('Planned static layers:', summary['planned_static_datasets'])"),
            ],
        ),
        "02_boundaries_grid.ipynb": (
            "02 — Northeast India State Boundaries & Projected 1 km Grid",
            "Validates `state_NWIC.shp` (repaired 1 invalid geometry), documents the 7 Sister States "
            "matching the local ERA5 extent (`89.8°E–97.4°E`, noting why Sikkim lies west of `89.8°E`), "
            "and inspects the metric `EPSG:32646` 1 km × 1 km fishnet grid.",
            [
                ("code", "import json, pandas as pd\nfrom pathlib import Path\nfrom IPython.display import Image, display\n\nROOT = Path('..')\nb_meta = json.loads((ROOT / 'data/reports/boundaries_metadata.json').read_text(encoding='utf-8'))\ng_meta = json.loads((ROOT / 'data/reports/grid_metadata.json').read_text(encoding='utf-8'))\npd.DataFrame({'area_km2': b_meta['state_areas_km2'], 'cells_1km': g_meta['cells_per_state']})"),
                ("code", "display(Image(filename=str(ROOT / 'outputs/maps/study_area_and_grid.png')))"),
            ],
        ),
        "03_wildfire_eda.ipynb": (
            "03 — Wildfire Exploratory Data Analysis (NASA FIRMS 2021–2024)",
            "Explores VIIRS S-NPP Collection 2 active-fire detections across Northeast India (2021–2024), "
            "validating `type == 0` vegetation fire filtering vs industrial flares (`type == 2`), monthly "
            "seasonality, FRP distributions, and hotspot maps.",
            [
                ("code", "import json, pandas as pd\nfrom pathlib import Path\nfrom IPython.display import Image, display\n\nROOT = Path('..')\nf_meta = json.loads((ROOT / 'data/reports/firms_ingestion_metadata.json').read_text(encoding='utf-8'))\nprint('Years ingested:', f_meta['years_ingested'])\nprint('Type counts:', f_meta['type_value_counts'])\nprint('Confidence counts:', f_meta['confidence_value_counts'])\npd.Series(f_meta['detections_by_state'], name='detections')"),
                ("code", "display(Image(filename=str(ROOT / 'outputs/maps/wildfire_hotspot_map.png')))\ndisplay(Image(filename=str(ROOT / 'outputs/figures/wildfire_seasonal_trends.png')))"),
            ],
        ),
        "04_landslide_eda.ipynb": (
            "04 — Landslide Inventory Validation, Antecedent Rainfall EDA & Preliminary Weather Model",
            "Audits NASA COOLR (0/176 in NE India — all in Uttarakhand/HP) and extracts 10,731 "
            "field-validated NE India records from the 904-page GSI PDF (9,970 inside 7-state study "
            "boundary, including 673 dated 2021–2024 events -> 463 unique cell-days). Documents "
            "antecedent rainfall triggers and preliminary weather-only landslide classifiers.",
            [
                ("code", "import json, pandas as pd\nfrom pathlib import Path\nfrom IPython.display import Image, display\n\nROOT = Path('..')\nfeas = json.loads((ROOT / 'data/reports/landslide_feasibility.json').read_text(encoding='utf-8'))\nprint(json.dumps(feas, indent=2))"),
                ("code", "pd.read_csv(ROOT / 'outputs/tables/landslide_model_comparison.csv')[['model', 'cv_roc_auc', 'cv_pr_auc', 'test_roc_auc', 'test_pr_auc', 'test_recall', 'test_precision', 'test_f1', 'test_false_alarm_rate']]"),
                ("code", "for img in ['maps/landslide_inventory_map.png', 'figures/landslide_gsi_coolr_eda.png', 'figures/landslide_rainfall_eda.png', 'figures/landslide_roc_pr_curves.png', 'figures/landslide_feature_importance.png', 'figures/landslide_decision_tree.png']:\n    display(Image(filename=str(ROOT / 'outputs' / img)))"),
            ],
        ),
        "05_feature_engineering.ipynb": (
            "05 — Leakage-Safe Weather & Antecedent Rainfall Feature Engineering",
            "Inspects ERA5-Land daily & 7/15-day rolling weather features (with missing 2023-08/09/11/12 "
            "preserved as `NaN`), separate IMD 0.25° daily & antecedent rainfall lags (`1/3/7/15` days), "
            "and feature correlations with wildfire presence.",
            [
                ("code", "import json, pandas as pd\nfrom pathlib import Path\nfrom IPython.display import Image, display\n\nROOT = Path('..')\nw_meta = json.loads((ROOT / 'data/reports/weather_features_metadata.json').read_text(encoding='utf-8'))\nprint('ERA5 grid pts:', w_meta['used_era5_grid_points'], '| IMD grid pts:', w_meta['used_imd_grid_points'])\nprint('ERA5 missing rows flagged:', w_meta['era5_missing_rows_flagged'])\nwf = pd.read_parquet(ROOT / 'data/processed/wildfire.parquet')\nwf.groupby('split')['fire_detected'].agg(['count', 'sum', 'mean'])"),
                ("code", "display(Image(filename=str(ROOT / 'outputs/figures/weather_rainfall_eda.png')))\ndisplay(Image(filename=str(ROOT / 'outputs/figures/wildfire_correlation_heatmap.png')))"),
            ],
        ),
        "06_model_comparison.ipynb": (
            "06 — Syllabus-Aligned Wildfire Classifier Comparison & Explainability",
            "Compares `DummyClassifier`, `LogisticRegression`, `GaussianNB`, `DecisionTreeClassifier`, "
            "`RandomForestClassifier`, and `HistGradientBoostingClassifier` using 5-fold spatial "
            "`StratifiedGroupKFold` on 2021–2023 and held-out realistic-prevalence evaluation on 2024. "
            "**Disclaimer:** Research risk estimate only — not an official warning.",
            [
                ("code", "import pandas as pd\nfrom pathlib import Path\nfrom IPython.display import Image, display\n\nROOT = Path('..')\ncomp = pd.read_csv(ROOT / 'outputs/tables/wildfire_model_comparison.csv')\ncomp[['model', 'syllabus_role', 'cv_roc_auc', 'cv_pr_auc', 'test_roc_auc', 'test_pr_auc', 'test_recall', 'test_precision', 'test_f1', 'test_false_alarm_rate']]"),
                ("code", "pd.read_csv(ROOT / 'outputs/tables/wildfire_test2024_per_state.csv')"),
                ("code", "pd.read_csv(ROOT / 'outputs/tables/wildfire_test2024_per_season.csv')"),
                ("code", "for img in ['wildfire_model_comparison.png', 'wildfire_roc_pr_curves.png', 'wildfire_confusion_matrices.png', 'wildfire_decision_tree.png', 'wildfire_feature_importance.png', 'wildfire_calibration.png']:\n    display(Image(filename=str(ROOT / 'outputs/figures' / img)))"),
            ],
        ),
    }

    for fname, (title, intro, cells) in notebooks.items():
        nb = make_nb(title, intro, cells)
        with (NB_DIR / fname).open("w", encoding="utf-8") as fh:
            nbf.write(nb, fh)
    print(f"Generated {len(notebooks)} notebooks in {NB_DIR}")


if __name__ == "__main__":
    generate_all()

