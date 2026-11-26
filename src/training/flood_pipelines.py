"""Flood Risk Classifier — INDOFLOODS All-India Dataset (6 Classifiers, Syllabus-Aligned).

Target: predict whether a flood event EXCEEDS DANGER LEVEL (binary: 0/1)
        using antecedent rainfall lags (T1d–T10d) + catchment characteristics.

Train/Test split: 70/30 random stratified (event-level, not temporal)
since INDOFLOODS spans 1965–2020 without full NE India coverage.

Produces:
  - models/flood_model.joblib
  - models/flood_model_card.json
  - outputs/figures/flood_model_comparison.png
  - outputs/figures/flood_roc_pr_curves.png
  - outputs/figures/flood_confusion_matrices.png
  - outputs/figures/flood_feature_importance.png
  - outputs/tables/flood_model_comparison.csv
  - outputs/tables/flood_feature_importance.csv
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
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
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

# ── Feature definitions ────────────────────────────────────────────────────────
FLOOD_NUMERIC_FEATURES = [
    # Antecedent CHIRPS cumulative rainfall lags (primary flood triggers)
    "T1d", "T2d", "T3d", "T4d", "T5d", "T6d", "T7d", "T8d", "T9d", "T10d",
    # Catchment physical characteristics
    "catchment_area_km2",
    "stream_order",
    "population_density",
    "urban_pct",
    # Event context
    "Latitude",
    "Longitude",
]
FLOOD_CATEGORICAL_FEATURES = ["soil_type", "lithology_type", "land_cover"]
FLOOD_ALL_FEATURES = FLOOD_NUMERIC_FEATURES + FLOOD_CATEGORICAL_FEATURES
TARGET_COL = "exceeds_danger_level"


def build_flood_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    """Build sklearn ColumnTransformer for flood features."""
    num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    if scale_numeric:
        num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", num_pipe, FLOOD_NUMERIC_FEATURES),
        ("cat", cat_pipe, FLOOD_CATEGORICAL_FEATURES),
    ], remainder="drop")


def train_and_evaluate_flood(config_path: str | Path | None = None) -> dict[str, Any]:
    """Train & compare 6 syllabus-aligned flood risk classifiers."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    rs = int(cfg["project"]["random_state"])

    flood_path = dirs["processed_labels"].parent / "flood.parquet"
    if not flood_path.exists():
        raise FileNotFoundError(
            f"Flood processed data not found: {flood_path}. Run src.ingestion.flood first."
        )

    df = pd.read_parquet(flood_path)

    # Drop rows where target is undefined
    df = df[df[TARGET_COL].notna()].copy().reset_index(drop=True)

    # Keep features that exist in the dataframe
    avail_num = [f for f in FLOOD_NUMERIC_FEATURES if f in df.columns]
    avail_cat = [f for f in FLOOD_CATEGORICAL_FEATURES if f in df.columns]
    all_feats = avail_num + avail_cat

    X = df[all_feats]
    y = df[TARGET_COL].to_numpy(dtype=np.int32)

    pos_rate = y.mean()
    print(f"[Flood] Dataset: {len(df):,} events | Positive (exceeds danger): {y.sum():,} ({pos_rate:.1%})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=rs, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=rs)

    # Rebuild preprocessors using only available features
    def build_prep(scale: bool = True) -> ColumnTransformer:
        num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median"))])
        if scale:
            num_pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ])
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        transformers = []
        if avail_num:
            transformers.append(("num", num_pipe, avail_num))
        if avail_cat:
            transformers.append(("cat", cat_pipe, avail_cat))
        return ColumnTransformer(transformers, remainder="drop")

    model_specs: list[tuple[str, Pipeline, dict, str]] = [
        (
            "DummyClassifier (Prior)",
            Pipeline([("prep", build_prep(False)), ("clf", DummyClassifier(strategy="prior"))]),
            {},
            "Baseline utility",
        ),
        (
            "Logistic Regression",
            Pipeline([
                ("prep", build_prep(True)),
                ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=rs)),
            ]),
            {"clf__C": [0.05, 0.2, 1.0, 5.0]},
            "CSET312 Core",
        ),
        (
            "Gaussian Naive Bayes",
            Pipeline([("prep", build_prep(True)), ("clf", GaussianNB())]),
            {"clf__var_smoothing": [1e-9, 1e-6, 1e-3]},
            "CSET312 Core",
        ),
        (
            "Decision Tree",
            Pipeline([
                ("prep", build_prep(False)),
                ("clf", DecisionTreeClassifier(class_weight="balanced", random_state=rs)),
            ]),
            {"clf__max_depth": [3, 5, 8], "clf__min_samples_leaf": [10, 30]},
            "CSET312 Core",
        ),
        (
            "Random Forest",
            Pipeline([
                ("prep", build_prep(False)),
                ("clf", RandomForestClassifier(
                    n_estimators=200, class_weight="balanced_subsample",
                    random_state=rs, n_jobs=-1
                )),
            ]),
            {"clf__max_depth": [6, 12], "clf__min_samples_leaf": [5, 15]},
            "Practical Tabular Extension",
        ),
        (
            "HistGradientBoosting",
            Pipeline([
                ("prep", build_prep(False)),
                ("clf", HistGradientBoostingClassifier(class_weight="balanced", random_state=rs)),
            ]),
            {"clf__max_depth": [4, 6], "clf__learning_rate": [0.03, 0.08], "clf__max_iter": [150]},
            "Advanced GBDT Extension",
        ),
    ]

    comparison_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}
    test_probs: dict[str, np.ndarray] = {}
    model_thresholds: dict[str, float] = {}

    for name, pipe, param_grid, syllabus_tag in model_specs:
        print(f"[Flood] Training: {name} ...")
        if param_grid:
            gs = GridSearchCV(pipe, param_grid=param_grid, scoring="average_precision",
                              cv=cv, n_jobs=-1, refit=False)
            gs.fit(X_train, y_train)
            pipe.set_params(**gs.best_params_)
            best_params = gs.best_params_
        else:
            best_params = {}

        oof_probs = cross_val_predict(pipe, X_train, y_train, cv=cv,
                                      method="predict_proba", n_jobs=-1)[:, 1]
        cv_m = compute_classification_metrics(y_train, oof_probs, threshold=0.5)
        opt_thr = find_best_f1_threshold(y_train, oof_probs) if name != "DummyClassifier (Prior)" else 0.5
        model_thresholds[name] = opt_thr

        pipe.fit(X_train, y_train)
        fitted_models[name] = pipe

        p_test = pipe.predict_proba(X_test)[:, 1]
        test_probs[name] = p_test
        tm = compute_classification_metrics(y_test, p_test, threshold=opt_thr)

        comparison_rows.append({
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
        })

    comp_df = pd.DataFrame(comparison_rows)
    comp_csv = dirs["outputs_tables"] / "flood_model_comparison.csv"
    comp_df.to_csv(comp_csv, index=False)

    non_dummy = comp_df[comp_df["model"] != "DummyClassifier (Prior)"]
    best_row = non_dummy.sort_values("cv_pr_auc", ascending=False).iloc[0]
    best_model_name = str(best_row["model"])
    best_pipeline = fitted_models[best_model_name]

    best_path = dirs["models"] / "flood_model.joblib"
    joblib.dump({
        "model_name": best_model_name,
        "pipeline": best_pipeline,
        "features": all_feats,
        "operating_threshold": float(best_row["operating_threshold"]),
        "disclaimer": DISCLAIMER,
        "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
        "note": "Trained on INDOFLOODS all-India gauged river events 1965–2020.",
    }, best_path)
    print(f"[Flood] Best model ({best_model_name}) saved → {best_path}")

    # ── Plots ──────────────────────────────────────────────────────────────────
    plot_roc_pr_curves(
        y_test, test_probs,
        dirs["outputs_figures"] / "flood_roc_pr_curves.png",
        title_prefix="Flood Risk — Test Set (30% Hold-Out)",
    )
    plot_model_comparison_bar(comp_df, dirs["outputs_figures"] / "flood_model_comparison.png")
    plot_confusion_matrices(
        y_test,
        {m: (test_probs[m], model_thresholds[m]) for m in test_probs},
        dirs["outputs_figures"] / "flood_confusion_matrices.png",
    )
    dt_pipe = fitted_models["Decision Tree"]
    dt_names = list(dt_pipe.named_steps["prep"].get_feature_names_out())
    plot_decision_tree_diagram(
        dt_pipe, dt_names,
        dirs["outputs_figures"] / "flood_decision_tree.png",
        max_depth=3,
    )

    imp_df = plot_permutation_importance(
        best_pipeline, X_test, y_test,
        dirs["outputs_figures"] / "flood_feature_importance.png",
        model_name=f"{best_model_name} (Flood Risk)",
        random_state=rs,
    )
    imp_df.to_csv(dirs["outputs_tables"] / "flood_feature_importance.csv", index=False)

    model_card: dict[str, Any] = {
        "project": cfg["project"]["name"],
        "hazard": "Flood (Exceeds Danger Level — INDOFLOODS)",
        "disclaimer": DISCLAIMER,
        "selected_best_model": best_model_name,
        "selection_criterion": "Highest 5-fold StratifiedKFold PR-AUC",
        "dataset": "INDOFLOODS All-India Gauged River Events 1965–2020",
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "train_positives": int(y_train.sum()),
        "test_positives": int(y_test.sum()),
        "features_count": len(all_feats),
        "features": all_feats,
        "note": (
            "NE India has limited gauging stations in INDOFLOODS. "
            "Model is trained all-India and applicable for regional risk estimation. "
            "Antecedent CHIRPS rainfall (T1d–T10d) are primary flood triggers."
        ),
        "top_10_features_permutation_importance": imp_df.head(10).to_dict(orient="records"),
        "all_models_summary": comparison_rows,
        "saved_artifacts": {
            "best_model_joblib": str(best_path),
            "comparison_csv": str(comp_csv),
        },
        "trained_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    with (dirs["models"] / "flood_model_card.json").open("w", encoding="utf-8") as fh:
        json.dump(model_card, fh, indent=2)

    return model_card


if __name__ == "__main__":
    card = train_and_evaluate_flood()
    print("\n=== FLOOD MODEL COMPARISON (Test Set — 30% Hold-Out) ===")
    print("Best model (by CV PR-AUC):", card["selected_best_model"])
    df_c = pd.DataFrame(card["all_models_summary"])
    print(df_c[[
        "model", "cv_roc_auc", "cv_pr_auc", "test_roc_auc",
        "test_pr_auc", "test_recall", "test_precision", "test_false_alarm_rate"
    ]].to_string(index=False))
