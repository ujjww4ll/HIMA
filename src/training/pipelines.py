"""Step 7b: Syllabus-aligned wildfire ML training, spatial CV, hyperparameter tuning, and evaluation.

Models compared on identical features and temporal split (Train: 2021-2023, Test: 2024 realistic prevalence):
  1. DummyClassifier (prior baseline)
  2. LogisticRegression (StandardScaler + OneHotEncoder, GridSearchCV in spatial StratifiedGroupKFold)
  3. GaussianNB (StandardScaler + OneHotEncoder, GridSearchCV in spatial StratifiedGroupKFold)
  4. DecisionTreeClassifier (interpretable rules + plot_tree, GridSearchCV in spatial StratifiedGroupKFold)
  5. RandomForestClassifier (practical ensemble extension)
  6. HistGradientBoostingClassifier (advanced gradient boosting extension)
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
    assign_risk_band,
    bayes_prior_adjust,
    compute_classification_metrics,
    find_best_f1_threshold,
    plot_calibration_and_risk_bands,
    plot_confusion_matrices,
    plot_decision_tree_diagram,
    plot_model_comparison_bar,
    plot_permutation_importance,
    plot_roc_pr_curves,
)


NUMERIC_FEATURES = [
    # ERA5 daily weather
    "temperature_c",
    "dewpoint_c",
    "dewpoint_depression_c",
    "wind_speed_ms",
    "soil_water_layer1",
    "era5_rainfall_mm",
    "relative_humidity_mean",
    "relative_humidity_min",
    # ERA5 leakage-safe rolling windows
    "era5_temp_mean_7d",
    "era5_temp_max_7d",
    "era5_rh_min_7d",
    "era5_rh_mean_7d",
    "era5_soil_water_mean_7d",
    "era5_wind_mean_7d",
    "era5_rain_sum_3d",
    "era5_rain_sum_7d",
    "era5_rain_sum_15d",
    "era5_days_since_rain",
    # IMD daily & antecedent rainfall (kept separate from ERA5)
    "imd_rain_1d",
    "imd_rain_lag1d",
    "imd_rain_sum_3d",
    "imd_rain_sum_7d",
    "imd_rain_sum_15d",
    "imd_rain_max_7d",
    "imd_rainy_days_7d",
    "imd_rainy_days_15d",
    "imd_days_since_rain",
    # Spatial & seasonal context
    "centroid_lat",
    "centroid_lon",
    "sin_doy",
    "cos_doy",
]

CATEGORICAL_FEATURES = ["state_name", "season"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    """Build leakage-safe scikit-learn ColumnTransformer (fit strictly inside training folds)."""
    if scale_numeric:
        num_pipe = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
    else:
        num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])

    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", num_pipe, NUMERIC_FEATURES),
            ("cat", cat_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def save_feature_schema(project_root: Path) -> Path:
    """Write config/feature_schema.json documenting exact features, types, units, and leakage exclusions."""
    schema = {
        "target": "fire_detected",
        "target_definition": "Binary (1 = >=1 validated FIRMS VIIRS SNPP C2 type=0 vegetation fire in 1 km cell on date; 0 = observed no-record)",
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "excluded_post_event_columns": [
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
        ],
        "missing_planned_predictors": [
            "MODIS MOD13Q1 NDVI",
            "ESA WorldCover land cover",
            "SRTM/Copernicus DEM (elevation, slope, aspect)",
        ],
    }
    schema_path = project_root / "config" / "feature_schema.json"
    with schema_path.open("w", encoding="utf-8") as fh:
        json.dump(schema, fh, indent=2)
    return schema_path


def train_and_evaluate_wildfire(config_path: str | Path | None = None) -> dict[str, Any]:
    """Train all syllabus-aligned wildfire classifiers with spatial CV and evaluate on 2024 realistic test set."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    rs = int(cfg["project"]["random_state"])

    save_feature_schema(dirs["models"].parent)

    wf_path = dirs["processed_labels"].parent / "wildfire.parquet"
    df = pd.read_parquet(wf_path)
    with (dirs["reports"] / "wildfire_dataset_metadata.json").open("r", encoding="utf-8") as fh:
        ds_meta = json.load(fh)
    with (dirs["reports"] / "grid_metadata.json").open("r", encoding="utf-8") as fh:
        grid_meta = json.load(fh)

    train_df = df[df["split"] == "train"].copy().reset_index(drop=True)
    test_df = df[df["split"] == "test_realistic"].copy().reset_index(drop=True)

    X_train = train_df[ALL_FEATURES]
    y_train = train_df["fire_detected"].to_numpy(dtype=np.int32)
    groups_train = train_df["spatial_block_id"].to_numpy()

    X_test = test_df[ALL_FEATURES]
    y_test = test_df["fire_detected"].to_numpy(dtype=np.int32)

    # Compute true TRAINING-period population prevalence (2021-2023) strictly without peeking at 2024 test!
    n_cells = int(grid_meta["total_cells"])
    train_years = cfg["wildfire"]["temporal_train_years"]
    n_train_days = sum(366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365 for y in train_years)
    pi_train_subsampled = float(y_train.mean())
    pi_train_population = float(ds_meta["train_positives"] / (n_cells * n_train_days))

    cv = StratifiedGroupKFold(n_splits=5)

    # Subsample CV tuning cap if training rows are huge so GridSearchCV stays fast (<2 min) while final fit uses 100% of train!
    if len(train_df) > 180_000:
        rng = np.random.default_rng(rs)
        tune_idx = rng.choice(len(train_df), size=150_000, replace=False)
        X_tune = X_train.iloc[tune_idx].reset_index(drop=True)
        y_tune = y_train[tune_idx]
        g_tune = groups_train[tune_idx]
    else:
        X_tune, y_tune, g_tune = X_train, y_train, groups_train

    model_specs: list[tuple[str, Pipeline, dict[str, list[Any]], str]] = [
        (
            "DummyClassifier (Prior)",
            Pipeline([("prep", build_preprocessor(False)), ("clf", DummyClassifier(strategy="prior"))]),
            {},
            "Baseline utility",
        ),
        (
            "Logistic Regression",
            Pipeline(
                [
                    ("prep", build_preprocessor(scale_numeric=True)),
                    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=rs)),
                ]
            ),
            {"clf__C": [0.1, 1.0, 5.0]},
            "CSET312 Core (Titanic lab)",
        ),
        (
            "Gaussian Naive Bayes",
            Pipeline(
                [
                    ("prep", build_preprocessor(scale_numeric=True)),
                    ("clf", GaussianNB()),
                ]
            ),
            {"clf__var_smoothing": [1e-9, 1e-6, 1e-3]},
            "CSET312 Core (Raisin lab)",
        ),
        (
            "Decision Tree",
            Pipeline(
                [
                    ("prep", build_preprocessor(scale_numeric=False)),
                    ("clf", DecisionTreeClassifier(class_weight="balanced", random_state=rs)),
                ]
            ),
            {"clf__max_depth": [5, 8, 12], "clf__min_samples_leaf": [50, 200]},
            "CSET312 Core (Raisin lab)",
        ),
        (
            "Random Forest",
            Pipeline(
                [
                    ("prep", build_preprocessor(scale_numeric=False)),
                    (
                        "clf",
                        RandomForestClassifier(
                            n_estimators=120,
                            class_weight="balanced_subsample",
                            random_state=rs,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            {"clf__max_depth": [12, 18], "clf__min_samples_leaf": [25, 100]},
            "Practical Tabular Extension",
        ),
        (
            "HistGradientBoosting",
            Pipeline(
                [
                    ("prep", build_preprocessor(scale_numeric=False)),
                    (
                        "clf",
                        HistGradientBoostingClassifier(
                            class_weight="balanced",
                            random_state=rs,
                        ),
                    ),
                ]
            ),
            {"clf__max_depth": [6, 10], "clf__learning_rate": [0.05, 0.1], "clf__max_iter": [150]},
            "Advanced GBDT Extension",
        ),
    ]

    comparison_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}
    test_probs_raw: dict[str, np.ndarray] = {}
    test_probs_cal: dict[str, np.ndarray] = {}
    model_thresholds: dict[str, float] = {}
    best_params_log: dict[str, Any] = {}

    for name, pipe, param_grid, syllabus_tag in model_specs:
        print(f"Training & validating: {name} ...")
        if param_grid:
            gs = GridSearchCV(
                pipe,
                param_grid=param_grid,
                scoring="average_precision",
                cv=cv,
                n_jobs=-1,
                refit=False,
            )
            gs.fit(X_tune, y_tune, groups=g_tune)
            best_params = gs.best_params_
            pipe.set_params(**best_params)
        else:
            best_params = {}
        best_params_log[name] = best_params

        # Out-of-fold predictions on spatial StratifiedGroupKFold (training data only!)
        oof_probs = cross_val_predict(
            pipe, X_tune, y_tune, cv=cv, groups=g_tune, method="predict_proba", n_jobs=-1
        )[:, 1]
        cv_metrics = compute_classification_metrics(y_tune, oof_probs, threshold=0.5)
        opt_thresh = find_best_f1_threshold(y_tune, oof_probs) if name != "DummyClassifier (Prior)" else 0.5
        model_thresholds[name] = opt_thresh

        # Final refit on 100% of 2021-2023 training data
        pipe.fit(X_train, y_train)
        fitted_models[name] = pipe

        # Evaluate on realistic-prevalence 2024 held-out test set
        p_raw = pipe.predict_proba(X_test)[:, 1]
        # Analytical Bayes prior adjustment using strictly training-period prevalence
        # For balanced-weight models effective training prior is 0.5; for unweighted (Dummy, GNB) it is pi_train_subsampled
        eff_train_prior = 0.5 if name not in {"DummyClassifier (Prior)", "Gaussian Naive Bayes"} else pi_train_subsampled
        p_cal = (
            np.full_like(p_raw, pi_train_population)
            if name == "DummyClassifier (Prior)"
            else bayes_prior_adjust(p_raw, eff_train_prior, pi_train_population)
        )

        test_probs_raw[name] = p_raw
        test_probs_cal[name] = p_cal

        test_metrics = compute_classification_metrics(y_test, p_raw, threshold=opt_thresh, y_prob_calibrated=p_cal)

        comparison_rows.append(
            {
                "model": name,
                "syllabus_role": syllabus_tag,
                "best_params": json.dumps(best_params),
                "cv_roc_auc": cv_metrics["roc_auc"],
                "cv_pr_auc": cv_metrics["pr_auc"],
                "cv_f1_at_0.5": cv_metrics["f1"],
                "operating_threshold": round(opt_thresh, 4),
                "test_roc_auc": test_metrics["roc_auc"],
                "test_pr_auc": test_metrics["pr_auc"],
                "test_accuracy": test_metrics["accuracy"],
                "test_precision": test_metrics["precision"],
                "test_recall": test_metrics["recall"],
                "test_f1": test_metrics["f1"],
                "test_false_alarm_rate": test_metrics["false_alarm_rate"],
                "test_brier_raw": test_metrics["brier_raw"],
                "test_brier_calibrated": test_metrics.get("brier_calibrated"),
                "test_tp": test_metrics["tp"],
                "test_fp": test_metrics["fp"],
                "test_fn": test_metrics["fn"],
                "test_tn": test_metrics["tn"],
            }
        )

    comp_df = pd.DataFrame(comparison_rows)
    comp_csv = dirs["outputs_tables"] / "wildfire_model_comparison.csv"
    comp_df.to_csv(comp_csv, index=False)

    # Select best model strictly by Spatial CV PR-AUC (never select hyperparameters/models using test!)
    non_dummy = comp_df[comp_df["model"] != "DummyClassifier (Prior)"]
    best_row = non_dummy.sort_values("cv_pr_auc", ascending=False).iloc[0]
    best_model_name = str(best_row["model"])
    best_pipeline = fitted_models[best_model_name]

    # Save full pipelines + metadata
    best_model_path = dirs["models"] / "wildfire_best_model.joblib"
    dt_model_path = dirs["models"] / "wildfire_decision_tree.joblib"
    lr_model_path = dirs["models"] / "wildfire_logistic_regression.joblib"
    joblib.dump(
        {
            "model_name": best_model_name,
            "pipeline": best_pipeline,
            "features": ALL_FEATURES,
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
            "operating_threshold": float(best_row["operating_threshold"]),
            "effective_train_prior": 0.5 if best_model_name != "Gaussian Naive Bayes" else pi_train_subsampled,
            "population_prior_2021_2023": pi_train_population,
            "disclaimer": DISCLAIMER,
            "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sklearn_version": sklearn.__version__,
        },
        best_model_path,
    )
    joblib.dump(fitted_models["Decision Tree"], dt_model_path)
    joblib.dump(fitted_models["Logistic Regression"], lr_model_path)

    # Per-state and per-season breakdown for best model on 2024 realistic test set
    eval_df = test_df[["state_name", "season", "fire_detected"]].copy()
    eval_df["prob_raw"] = test_probs_raw[best_model_name]
    eval_df["prob_cal"] = test_probs_cal[best_model_name]
    eval_df["risk_band"] = assign_risk_band(eval_df["prob_cal"].to_numpy())
    best_thr = float(best_row["operating_threshold"])

    state_rows = []
    for st, sub in eval_df.groupby("state_name", sort=True):
        m = compute_classification_metrics(
            sub["fire_detected"].to_numpy(), sub["prob_raw"].to_numpy(), threshold=best_thr, y_prob_calibrated=sub["prob_cal"].to_numpy()
        )
        state_rows.append({"state_name": st, **m})
    state_metrics_df = pd.DataFrame(state_rows)
    state_metrics_df.to_csv(dirs["outputs_tables"] / "wildfire_test2024_per_state.csv", index=False)

    season_rows = []
    for sea, sub in eval_df.groupby("season", sort=True):
        m = compute_classification_metrics(
            sub["fire_detected"].to_numpy(), sub["prob_raw"].to_numpy(), threshold=best_thr, y_prob_calibrated=sub["prob_cal"].to_numpy()
        )
        season_rows.append({"season": sea, **m})
    season_metrics_df = pd.DataFrame(season_rows)
    season_metrics_df.to_csv(dirs["outputs_tables"] / "wildfire_test2024_per_season.csv", index=False)

    # Generate evaluation & explainability figures
    plot_roc_pr_curves(y_test, test_probs_raw, dirs["outputs_figures"] / "wildfire_roc_pr_curves.png")
    plot_model_comparison_bar(comp_df, dirs["outputs_figures"] / "wildfire_model_comparison.png")
    plot_confusion_matrices(
        y_test,
        {m: (test_probs_raw[m], model_thresholds[m]) for m in test_probs_raw},
        dirs["outputs_figures"] / "wildfire_confusion_matrices.png",
    )

    # Decision tree diagram (extract post-OHE feature names cleanly)
    dt_pipe = fitted_models["Decision Tree"]
    dt_feat_names = list(dt_pipe.named_steps["prep"].get_feature_names_out())
    plot_decision_tree_diagram(
        dt_pipe, dt_feat_names, dirs["outputs_figures"] / "wildfire_decision_tree.png", max_depth=3
    )

    # Permutation importance on stratified 100k subset of 2024 test (keeps all positives + random negatives for speed)
    pos_idx = np.where(y_test == 1)[0]
    neg_idx = np.where(y_test == 0)[0]
    rng_perm = np.random.default_rng(rs)
    neg_sub = rng_perm.choice(neg_idx, size=min(80_000, len(neg_idx)), replace=False)
    perm_idx = np.concatenate([pos_idx, neg_sub])
    imp_df = plot_permutation_importance(
        best_pipeline,
        X_test.iloc[perm_idx],
        y_test[perm_idx],
        dirs["outputs_figures"] / "wildfire_feature_importance.png",
        model_name=best_model_name,
        random_state=rs,
    )
    imp_df.to_csv(dirs["outputs_tables"] / "wildfire_feature_importance.csv", index=False)

    # Calibration & lift plot
    plot_calibration_and_risk_bands(
        y_test,
        test_probs_raw[best_model_name],
        test_probs_cal[best_model_name],
        best_model_name,
        dirs["outputs_figures"] / "wildfire_calibration.png",
    )

    # Save structured Model Card JSON
    model_card = {
        "project": cfg["project"]["name"],
        "hazard": "Wildfire (1 km cell x 1 day)",
        "disclaimer": DISCLAIMER,
        "selected_best_model": best_model_name,
        "selection_criterion": "Highest 5-fold Spatial StratifiedGroupKFold PR-AUC on 2021-2023 training data",
        "train_period": train_years,
        "test_period": cfg["wildfire"]["temporal_test_years"],
        "train_rows": int(len(train_df)),
        "train_positives": int(y_train.sum()),
        "test_realistic_rows": int(len(test_df)),
        "test_realistic_positives": int(y_test.sum()),
        "test_realistic_prevalence": round(float(y_test.mean()), 6),
        "population_prior_2021_2023": round(pi_train_population, 6),
        "features_count": len(ALL_FEATURES),
        "features": ALL_FEATURES,
        "best_model_test_metrics": comp_df[comp_df["model"] == best_model_name].iloc[0].to_dict(),
        "top_10_features_permutation_importance": imp_df.head(10).to_dict(orient="records"),
        "all_models_summary": comparison_rows,
        "saved_artifacts": {
            "best_model_joblib": str(best_model_path),
            "decision_tree_joblib": str(dt_model_path),
            "logistic_regression_joblib": str(lr_model_path),
            "comparison_csv": str(comp_csv),
        },
        "package_versions": {
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with (dirs["models"] / "wildfire_model_card.json").open("w", encoding="utf-8") as fh:
        json.dump(model_card, fh, indent=2)

    return model_card


if __name__ == "__main__":
    card = train_and_evaluate_wildfire()
    print("\n=== WILDFIRE MODEL COMPARISON COMPLETE ===")
    print("Best model (by spatial CV PR-AUC):", card["selected_best_model"])
    df_c = pd.DataFrame(card["all_models_summary"])
    print(
        df_c[
            ["model", "cv_roc_auc", "cv_pr_auc", "test_roc_auc", "test_pr_auc", "test_recall", "test_precision", "test_f1", "test_false_alarm_rate"]
        ].to_string(index=False)
    )

