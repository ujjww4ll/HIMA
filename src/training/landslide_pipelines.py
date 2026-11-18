"""Step 10: Preliminary Weather-Only Landslide Classifier Suite (Syllabus-Aligned).

Trained strictly on validated dated GSI 2021-2023 cell-days and tested on unseen 2024 dated
GSI landslide cell-days + 100,000 uniform 2024 background cell-days.

IMPORTANT LIMITATION DOCUMENTED IN ALL OUTPUTS:
  Static terrain layers (DEM, slope, aspect, WorldCover, SoilGrids, geology) are NOT present in
  local downloads. Therefore this model evaluates ONLY hydrometeorological triggering (antecedent
  IMD/ERA5 rainfall, soil moisture, seasonality, location) and is NOT a complete susceptibility model.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_predict
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.config import ensure_project_dirs, load_config
from src.evaluation.metrics import (
    DISCLAIMER,
    compute_classification_metrics,
    find_best_f1_threshold,
    plot_confusion_matrices,
    plot_decision_tree_diagram,
    plot_model_comparison_bar,
    plot_permutation_importance,
    plot_roc_pr_curves,
)


LANDSLIDE_NUMERIC_FEATURES = [
    # IMD antecedent rainfall (primary rainfall-trigger predictors)
    "imd_rain_1d",
    "imd_rain_lag1d",
    "imd_rain_sum_3d",
    "imd_rain_sum_7d",
    "imd_rain_sum_15d",
    "imd_rain_max_7d",
    "imd_rainy_days_7d",
    "imd_rainy_days_15d",
    "imd_days_since_rain",
    # ERA5 rainfall, soil saturation, and weather
    "era5_rainfall_mm",
    "era5_rain_sum_3d",
    "era5_rain_sum_7d",
    "era5_rain_sum_15d",
    "soil_water_layer1",
    "era5_soil_water_mean_7d",
    "temperature_c",
    "relative_humidity_mean",
    "wind_speed_ms",
    # Spatial & seasonal context (note: DEM/slope/geology absent!)
    "centroid_lat",
    "centroid_lon",
    "sin_doy",
    "cos_doy",
]

LANDSLIDE_CATEGORICAL_FEATURES = ["season"]
# Note: state_name is deliberately EXCLUDED from landslide features to prevent the model from
# exploiting campaign reporting bias (529/673 dated records in Mizoram) rather than physical rainfall!
LANDSLIDE_ALL_FEATURES = LANDSLIDE_NUMERIC_FEATURES + LANDSLIDE_CATEGORICAL_FEATURES


def build_ls_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    if scale_numeric:
        num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    else:
        num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [("num", num_pipe, LANDSLIDE_NUMERIC_FEATURES), ("cat", cat_pipe, LANDSLIDE_CATEGORICAL_FEATURES)],
        remainder="drop",
    )


def train_and_evaluate_landslide(config_path: str | Path | None = None) -> dict[str, Any]:
    """Train & compare 6 syllabus-aligned preliminary weather-only landslide classifiers."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    rs = int(cfg["project"]["random_state"])

    mod_path = dirs["processed_labels"].parent / "landslide_modeling.parquet"
    if not mod_path.exists():
        raise FileNotFoundError(f"Landslide modeling table not found: {mod_path}. Run src.labels.landslide first.")

    df = pd.read_parquet(mod_path)
    train_df = df[df["split"] == "train"].copy().reset_index(drop=True)
    test_df = df[df["split"] == "test_2024"].copy().reset_index(drop=True)

    X_train = train_df[LANDSLIDE_ALL_FEATURES]
    y_train = train_df["landslide_detected"].to_numpy(dtype=np.int32)
    groups_train = train_df["spatial_block_id"].to_numpy()

    X_test = test_df[LANDSLIDE_ALL_FEATURES]
    y_test = test_df["landslide_detected"].to_numpy(dtype=np.int32)

    cv = StratifiedGroupKFold(n_splits=5)

    model_specs: list[tuple[str, Pipeline, dict[str, list[Any]], str]] = [
        (
            "DummyClassifier (Prior)",
            Pipeline([("prep", build_ls_preprocessor(False)), ("clf", DummyClassifier(strategy="prior"))]),
            {},
            "Baseline utility",
        ),
        (
            "Logistic Regression",
            Pipeline(
                [
                    ("prep", build_ls_preprocessor(True)),
                    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=rs)),
                ]
            ),
            {"clf__C": [0.05, 0.2, 1.0]},
            "CSET312 Core (Titanic lab)",
        ),
        (
            "Gaussian Naive Bayes",
            Pipeline([("prep", build_ls_preprocessor(True)), ("clf", GaussianNB())]),
            {"clf__var_smoothing": [1e-6, 1e-3, 1e-1]},
            "CSET312 Core (Raisin lab)",
        ),
        (
            "Decision Tree",
            Pipeline(
                [
                    ("prep", build_ls_preprocessor(False)),
                    ("clf", DecisionTreeClassifier(class_weight="balanced", random_state=rs)),
                ]
            ),
            {"clf__max_depth": [3, 5, 7], "clf__min_samples_leaf": [15, 40]},
            "CSET312 Core (Raisin lab)",
        ),
        (
            "Random Forest",
            Pipeline(
                [
                    ("prep", build_ls_preprocessor(False)),
                    (
                        "clf",
                        RandomForestClassifier(
                            n_estimators=150, class_weight="balanced_subsample", random_state=rs, n_jobs=-1
                        ),
                    ),
                ]
            ),
            {"clf__max_depth": [6, 10], "clf__min_samples_leaf": [10, 25]},
            "Practical Tabular Extension",
        ),
        (
            "HistGradientBoosting",
            Pipeline(
                [
                    ("prep", build_ls_preprocessor(False)),
                    ("clf", HistGradientBoostingClassifier(class_weight="balanced", random_state=rs)),
                ]
            ),
            {"clf__max_depth": [4, 6], "clf__learning_rate": [0.03, 0.08], "clf__max_iter": [120]},
            "Advanced GBDT Extension",
        ),
    ]

    comparison_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}
    test_probs: dict[str, np.ndarray] = {}
    model_thresholds: dict[str, float] = {}

    for name, pipe, param_grid, syllabus_tag in model_specs:
        print(f"[Landslide] Training & validating: {name} ...")
        if param_grid:
            gs = GridSearchCV(pipe, param_grid=param_grid, scoring="average_precision", cv=cv, n_jobs=-1, refit=False)
            gs.fit(X_train, y_train, groups=groups_train)
            best_params = gs.best_params_
            pipe.set_params(**best_params)
        else:
            best_params = {}

        oof_probs = cross_val_predict(
            pipe, X_train, y_train, cv=cv, groups=groups_train, method="predict_proba", n_jobs=-1
        )[:, 1]
        cv_m = compute_classification_metrics(y_train, oof_probs, threshold=0.5)
        opt_thr = find_best_f1_threshold(y_train, oof_probs) if name != "DummyClassifier (Prior)" else 0.5
        model_thresholds[name] = opt_thr

        pipe.fit(X_train, y_train)
        fitted_models[name] = pipe

        p_test = pipe.predict_proba(X_test)[:, 1]
        test_probs[name] = p_test
        tm = compute_classification_metrics(y_test, p_test, threshold=opt_thr)

        comparison_rows.append(
            {
                "model": name,
                "syllabus_role": syllabus_tag,
                "best_params": json.dumps(best_params),
                "cv_roc_auc": cv_m["roc_auc"],
                "cv_pr_auc": cv_m["pr_auc"],
                "operating_threshold": round(opt_thr, 4),
                "test_roc_auc": tm["roc_auc"],
                "test_pr_auc": tm["pr_auc"],
                "test_accuracy": tm["accuracy"],
                "test_precision": tm["precision"],
                "test_recall": tm["recall"],
                "test_f1": tm["f1"],
                "test_false_alarm_rate": tm["false_alarm_rate"],
                "test_tp": tm["tp"],
                "test_fp": tm["fp"],
                "test_fn": tm["fn"],
                "test_tn": tm["tn"],
            }
        )

    comp_df = pd.DataFrame(comparison_rows)
    comp_csv = dirs["outputs_tables"] / "landslide_model_comparison.csv"
    comp_df.to_csv(comp_csv, index=False)

    non_dummy = comp_df[comp_df["model"] != "DummyClassifier (Prior)"]
    best_row = non_dummy.sort_values("cv_pr_auc", ascending=False).iloc[0]
    best_model_name = str(best_row["model"])
    best_pipeline = fitted_models[best_model_name]

    best_path = dirs["models"] / "landslide_preliminary_model.joblib"
    joblib.dump(
        {
            "model_name": best_model_name,
            "pipeline": best_pipeline,
            "features": LANDSLIDE_ALL_FEATURES,
            "operating_threshold": float(best_row["operating_threshold"]),
            "preliminary_warning": "Weather-trigger only; static terrain layers (DEM/slope/soil/geology) absent.",
            "disclaimer": DISCLAIMER,
            "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sklearn_version": sklearn.__version__,
        },
        best_path,
    )

    # Plots
    plot_roc_pr_curves(
        y_test,
        test_probs,
        dirs["outputs_figures"] / "landslide_roc_pr_curves.png",
        title_prefix="Preliminary Landslide 2024 Test (Weather-Only)",
    )
    plot_model_comparison_bar(comp_df, dirs["outputs_figures"] / "landslide_model_comparison.png")
    plot_confusion_matrices(
        y_test,
        {m: (test_probs[m], model_thresholds[m]) for m in test_probs},
        dirs["outputs_figures"] / "landslide_confusion_matrices.png",
    )
    dt_pipe = fitted_models["Decision Tree"]
    dt_names = list(dt_pipe.named_steps["prep"].get_feature_names_out())
    plot_decision_tree_diagram(
        dt_pipe, dt_names, dirs["outputs_figures"] / "landslide_decision_tree.png", max_depth=3
    )

    # Permutation importance on 2024 test (all positives + 20k background)
    pos_idx = np.where(y_test == 1)[0]
    neg_idx = np.where(y_test == 0)[0]
    rng = np.random.default_rng(rs)
    neg_sub = rng.choice(neg_idx, size=min(20_000, len(neg_idx)), replace=False)
    perm_idx = np.concatenate([pos_idx, neg_sub])
    imp_df = plot_permutation_importance(
        best_pipeline,
        X_test.iloc[perm_idx],
        y_test[perm_idx],
        dirs["outputs_figures"] / "landslide_feature_importance.png",
        model_name=f"{best_model_name} (Preliminary Landslide)",
        random_state=rs,
    )
    imp_df.to_csv(dirs["outputs_tables"] / "landslide_feature_importance.csv", index=False)

    model_card = {
        "project": cfg["project"]["name"],
        "hazard": "Landslide (Preliminary Weather-Only Daily Trigger Model)",
        "disclaimer": DISCLAIMER,
        "selected_best_model": best_model_name,
        "selection_criterion": "Highest 5-fold Spatial StratifiedGroupKFold PR-AUC on 2021-2023 training data",
        "train_period": [2021, 2022, 2023],
        "test_period": [2024],
        "train_rows": int(len(train_df)),
        "train_positive_celldays": int(y_train.sum()),
        "test_rows": int(len(test_df)),
        "test_positive_celldays": int(y_test.sum()),
        "features_count": len(LANDSLIDE_ALL_FEATURES),
        "features": LANDSLIDE_ALL_FEATURES,
        "state_feature_excluded_reason": "Excluded state_name intentionally to avoid exploiting Mizoram 2024 survey campaign bias.",
        "critical_limitations": [
            "Missing DEM/slope/aspect, WorldCover, SoilGrids, and geology static layers.",
            "Training uses dated GSI PDF field records (117 raw -> unique cell-days in 2021-2023) and tests on 2024 dated GSI records (predominantly Cyclone Remal in Mizoram).",
            "NOT a full landslide susceptibility model or operational warning system.",
        ],
        "top_10_features_permutation_importance": imp_df.head(10).to_dict(orient="records"),
        "all_models_summary": comparison_rows,
        "saved_artifacts": {"best_model_joblib": str(best_path), "comparison_csv": str(comp_csv)},
        "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with (dirs["models"] / "landslide_model_card.json").open("w", encoding="utf-8") as fh:
        json.dump(model_card, fh, indent=2)

    return model_card


if __name__ == "__main__":
    card = train_and_evaluate_landslide()
    print("\n=== PRELIMINARY LANDSLIDE MODEL COMPARISON COMPLETE ===")
    print("Best model (by spatial CV PR-AUC):", card["selected_best_model"])
    df_c = pd.DataFrame(card["all_models_summary"])
    print(
        df_c[
            ["model", "cv_roc_auc", "cv_pr_auc", "test_roc_auc", "test_pr_auc", "test_recall", "test_precision", "test_f1", "test_false_alarm_rate"]
        ].to_string(index=False)
    )

