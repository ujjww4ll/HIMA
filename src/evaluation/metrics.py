"""Evaluation metrics, calibration, risk bands, and visualization helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.tree import plot_tree


DISCLAIMER = "Research risk estimate only — not an official warning."


def bayes_prior_adjust(probs: np.ndarray, pi_train: float, pi_target: float) -> np.ndarray:
    """Analytical Bayes prior-odds adjustment from subsampled training prior to population prior.

    Uses strictly training-period population prevalence (no test data leakage).
    """
    eps = 1e-7
    p = np.clip(np.asarray(probs, dtype=np.float64), eps, 1.0 - eps)
    odds_ratio = (pi_target / (1.0 - pi_target)) / (pi_train / (1.0 - pi_train))
    adj = (p * odds_ratio) / (p * odds_ratio + (1.0 - p))
    return np.clip(adj, 0.0, 1.0)


def assign_risk_band(probs: np.ndarray) -> np.ndarray:
    """Map calibrated probability [0, 1] to provisional HIMA UI risk bands."""
    p = np.asarray(probs, dtype=np.float64)
    return np.select(
        [p < 0.30, p < 0.60, p < 0.80],
        ["LOW (0-30%)", "MODERATE (30-60%)", "HIGH (60-80%)"],
        default="CRITICAL (80-100%)",
    )


def find_best_f1_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Find probability threshold maximizing F1 on validation/CV predictions (never fit on test)."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    if len(thresholds) == 0:
        return 0.5
    f1s = 2 * (precision[:-1] * recall[:-1]) / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    best_idx = int(np.argmax(f1s))
    return float(thresholds[best_idx])


def compute_classification_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    y_prob_calibrated: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compute comprehensive binary classification metrics including PR-AUC and FAR."""
    y_true = np.asarray(y_true, dtype=np.int32)
    y_prob = np.asarray(y_prob, dtype=np.float64)
    y_pred = (y_prob >= threshold).astype(np.int32)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = float(fp / max(fp + tn, 1))
    has_both_classes = len(np.unique(y_true)) == 2

    metrics: dict[str, Any] = {
        "n_samples": int(len(y_true)),
        "n_positives": int(y_true.sum()),
        "prevalence": round(float(y_true.mean()), 6),
        "threshold": round(float(threshold), 4),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4) if has_both_classes else None,
        "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4) if has_both_classes else None,
        "false_alarm_rate": round(fpr, 4),
        "brier_raw": round(float(brier_score_loss(y_true, np.clip(y_prob, 0, 1))), 5),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
    if y_prob_calibrated is not None:
        metrics["brier_calibrated"] = round(
            float(brier_score_loss(y_true, np.clip(y_prob_calibrated, 0, 1))), 5
        )
    return metrics


def plot_roc_pr_curves(
    y_true: np.ndarray,
    model_probs: dict[str, np.ndarray],
    out_path: Path,
    title_prefix: str = "Wildfire 2024 Realistic-Prevalence Test",
) -> None:
    """Plot side-by-side ROC and Precision-Recall curves for all compared models."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=150)

    for name, probs in model_probs.items():
        fpr, tpr, _ = roc_curve(y_true, probs)
        roc_val = roc_auc_score(y_true, probs)
        ax1.plot(fpr, tpr, lw=2, label=f"{name} (AUC={roc_val:.3f})")

        prec, rec, _ = precision_recall_curve(y_true, probs)
        pr_val = average_precision_score(y_true, probs)
        ax2.plot(rec, prec, lw=2, label=f"{name} (AP={pr_val:.4f})")

    ax1.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6, label="Chance")
    ax1.set_title(f"{title_prefix} — ROC Curve", fontweight="bold")
    ax1.set_xlabel("False Positive Rate (False Alarm Rate)")
    ax1.set_ylabel("True Positive Rate (Recall)")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.grid(True, alpha=0.3)

    base_rate = float(np.mean(y_true))
    ax2.axhline(base_rate, color="k", linestyle="--", lw=1, alpha=0.6, label=f"Baseline ({base_rate:.5f})")
    ax2.set_title(f"{title_prefix} — Precision-Recall Curve", fontweight="bold")
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.suptitle(f"HIMA Model Discrimination | {DISCLAIMER}", fontsize=11, y=0.99)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def plot_model_comparison_bar(comp_df: pd.DataFrame, out_path: Path) -> None:
    """Plot bar comparison of CV and 2024 Test ROC-AUC and PR-AUC across all models."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)

    models = comp_df["model"].tolist()
    x = np.arange(len(models))
    w = 0.36

    ax1.bar(x - w / 2, comp_df["cv_roc_auc"], width=w, label="Spatial CV (2021–2022)", color="#4c78a8")
    ax1.bar(x + w / 2, comp_df["test_roc_auc"], width=w, label="Realistic Test (2024)", color="#f58518")
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=20, ha="right", fontsize=9)
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("ROC-AUC")
    ax1.set_title("ROC-AUC Comparison (Higher = Better)", fontweight="bold")
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.3)

    ax2.bar(x - w / 2, comp_df["cv_pr_auc"], width=w, label="Spatial CV (5:1 train ratio)", color="#54a24b")
    ax2.bar(x + w / 2, comp_df["test_pr_auc"], width=w, label="Realistic Test (true 2024 base rate)", color="#e45756")
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=20, ha="right", fontsize=9)
    ax2.set_ylabel("PR-AUC (Average Precision)")
    ax2.set_title("PR-AUC Comparison (Note Different Class Base Rates)", fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle(f"HIMA Wildfire Classifier Comparison | {DISCLAIMER}", fontsize=11, y=0.99)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def plot_confusion_matrices(
    y_true: np.ndarray,
    model_preds: dict[str, tuple[np.ndarray, float]],
    out_path: Path,
) -> None:
    """Plot confusion matrices grid for all evaluated models on 2024 realistic test set."""
    n = len(model_preds)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.2 * nrows), dpi=150)
    axes_flat = np.atleast_1d(axes).ravel()

    for ax, (name, (probs, thresh)) in zip(axes_flat, model_preds.items()):
        preds = (probs >= thresh).astype(int)
        cm = confusion_matrix(y_true, preds, labels=[0, 1])
        sns.heatmap(
            cm,
            annot=True,
            fmt=",d",
            cmap="Blues",
            cbar=False,
            ax=ax,
            xticklabels=["Pred 0 (No Fire)", "Pred 1 (Fire)"],
            yticklabels=["True 0 (No Fire)", "True 1 (Fire)"],
        )
        rec = recall_score(y_true, preds, zero_division=0)
        prec = precision_score(y_true, preds, zero_division=0)
        ax.set_title(f"{name}\nthr={thresh:.2f} | Rec={rec:.2f} | Prec={prec:.4f}", fontsize=9, fontweight="bold")

    for ax in axes_flat[n:]:
        ax.axis("off")

    fig.suptitle(f"Wildfire 2024 Test Confusion Matrices | {DISCLAIMER}", fontsize=11, y=1.01)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def plot_decision_tree_diagram(tree_pipeline: Any, feature_names: list[str], out_path: Path, max_depth: int = 3) -> None:
    """Visualize top levels of the fitted DecisionTreeClassifier using sklearn.tree.plot_tree."""
    clf = tree_pipeline.named_steps["clf"]
    fig, ax = plt.subplots(figsize=(20, 10), dpi=150)
    plot_tree(
        clf,
        feature_names=feature_names,
        class_names=["No Fire (0)", "Fire (1)"],
        filled=True,
        rounded=True,
        max_depth=max_depth,
        fontsize=8,
        ax=ax,
    )
    ax.set_title(
        f"HIMA Interpretable Decision Tree (Top {max_depth} Levels) | {DISCLAIMER}",
        fontsize=13,
        fontweight="bold",
    )
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def plot_permutation_importance(
    pipeline: Any,
    X_eval: pd.DataFrame,
    y_eval: np.ndarray,
    out_path: Path,
    model_name: str,
    random_state: int = 42,
) -> pd.DataFrame:
    """Compute and plot permutation feature importance (ROC-AUC drop) on held-out 2024 sample."""
    res = permutation_importance(
        pipeline,
        X_eval,
        y_eval,
        scoring="roc_auc",
        n_repeats=5,
        random_state=random_state,
        n_jobs=-1,
    )
    imp_df = (
        pd.DataFrame(
            {
                "feature": X_eval.columns,
                "importance_mean": res.importances_mean,
                "importance_std": res.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )

    top = imp_df.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=150)
    ax.barh(top["feature"], top["importance_mean"], xerr=top["importance_std"], color="#2b7bba", alpha=0.9)
    ax.set_xlabel("Mean Decrease in ROC-AUC when Feature Permuted")
    ax.set_title(f"Top 15 Feature Drivers — {model_name} (2024 Held-Out Test)\n{DISCLAIMER}", fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return imp_df


def plot_calibration_and_risk_bands(
    y_true: np.ndarray,
    raw_probs: np.ndarray,
    cal_probs: np.ndarray,
    model_name: str,
    out_path: Path,
) -> None:
    """Plot reliability/calibration curve (before vs after Bayes prior adjustment) & risk distribution."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)

    # Reliability diagram using quantile bins (critical for rare events!)
    frac_pos_raw, mean_pred_raw = calibration_curve(y_true, np.clip(raw_probs, 0, 1), n_bins=10, strategy="quantile")
    frac_pos_cal, mean_pred_cal = calibration_curve(y_true, np.clip(cal_probs, 0, 1), n_bins=10, strategy="quantile")

    ax1.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
    ax1.plot(mean_pred_raw, frac_pos_raw, "o-", label=f"Raw subsampled prob (Brier={brier_score_loss(y_true, np.clip(raw_probs,0,1)):.4f})")
    ax1.plot(mean_pred_cal, frac_pos_cal, "s-", label=f"Prior-adjusted prob (Brier={brier_score_loss(y_true, np.clip(cal_probs,0,1)):.5f})")
    ax1.set_title(f"Probability Calibration ({model_name}, 2024 Realistic Test)", fontweight="bold")
    ax1.set_xlabel("Mean Predicted Probability")
    ax1.set_ylabel("Observed Event Frequency")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Observed fire rate by decile of predicted risk score (lift chart)
    deciles = pd.qcut(pd.Series(raw_probs).rank(method="first"), 10, labels=[f"D{i}" for i in range(1, 11)])
    lift_df = pd.DataFrame({"decile": deciles, "y": y_true}).groupby("decile", observed=False)["y"].agg(["mean", "sum"])
    ax2.bar(lift_df.index, lift_df["mean"] * 1000, color="#d95f02", alpha=0.85)
    ax2.set_title("Observed 2024 Fire Rate by Predicted Risk Decile (Lift Check)", fontweight="bold")
    ax2.set_xlabel("Model Risk Decile (D1=Lowest, D10=Highest)")
    ax2.set_ylabel("Observed Fires per 1,000 Cell-Days")
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle(f"HIMA Calibration & Risk Lift Analysis | {DISCLAIMER}", fontsize=11, y=0.99)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

