"""Exploratory Data Analysis (EDA) maps & figures for Wildfire, Weather, and Landslides.

Generates all required visual deliverables (Section 12 of HIMA handoff):
  - outputs/maps/wildfire_hotspot_map.png
  - outputs/figures/wildfire_seasonal_trends.png
  - outputs/figures/weather_rainfall_eda.png
  - outputs/figures/wildfire_correlation_heatmap.png
  - outputs/maps/landslide_inventory_map.png
  - outputs/figures/landslide_gsi_coolr_eda.png
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import ensure_project_dirs, load_config
from src.evaluation.metrics import DISCLAIMER


def run_all_eda(config_path: str | Path | None = None) -> dict[str, str]:
    """Generate all EDA figures and maps from validated processed datasets."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    outputs: dict[str, str] = {}

    states_4326 = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")
    firms = pd.read_parquet(dirs["interim_firms"] / "firms_ne_india_detections.parquet")
    firms_veg = firms[firms["is_vegetation_fire"]].copy()
    imd = pd.read_parquet(dirs["interim_weather"] / "imd_daily_ne.parquet")
    wf = pd.read_parquet(dirs["processed_labels"].parent / "wildfire.parquet")

    # 1. Wildfire Hotspot Map
    out_wf_map = dirs["outputs_maps"] / "wildfire_hotspot_map.png"
    fig, ax = plt.subplots(figsize=(11, 9), dpi=150)
    states_4326.plot(ax=ax, color="#f4f4f0", edgecolor="#333333", linewidth=0.9)
    hb = ax.hexbin(
        firms_veg["longitude"],
        firms_veg["latitude"],
        gridsize=75,
        cmap="YlOrRd",
        mincnt=1,
        bins="log",
        alpha=0.88,
    )
    cbar = fig.colorbar(hb, ax=ax, shrink=0.72, pad=0.02)
    cbar.set_label("Log10(VIIRS Vegetation Fire Detections, 2021–2024)")
    for _, row in states_4326.iterrows():
        c = row.geometry.representative_point()
        ax.annotate(
            row["state_name"],
            xy=(c.x, c.y),
            fontsize=8,
            fontweight="bold",
            ha="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65),
        )
    ax.set_title(
        f"Northeast India Wildfire Hotspot Density (NASA FIRMS VIIRS S-NPP C2, type=0)\n"
        f"2021–2024 ({len(firms_veg):,} detections across 7 states) | {DISCLAIMER}",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    fig.savefig(out_wf_map, bbox_inches="tight")
    plt.close(fig)
    outputs["wildfire_hotspot_map"] = str(out_wf_map)

    # 2. Wildfire Monthly/Yearly Trends, State Breakdown, FRP & Confidence Distributions
    out_wf_trends = dirs["outputs_figures"] / "wildfire_seasonal_trends.png"
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), dpi=150)

    # Panel A: Monthly seasonal cycle by year
    monthly = firms_veg.groupby(["year", "month"]).size().unstack(fill_value=0)
    for yr in sorted(monthly.index):
        axes[0, 0].plot(monthly.columns, monthly.loc[yr], marker="o", lw=2, label=str(yr))
    axes[0, 0].set_xticks(range(1, 13))
    axes[0, 0].set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    axes[0, 0].set_ylabel("Vegetation Fire Detections")
    axes[0, 0].set_title("Monthly Wildfire Seasonality by Year (2021–2024)", fontweight="bold")
    axes[0, 0].legend(title="Year")
    axes[0, 0].grid(True, alpha=0.3)

    # Panel B: Detections by State
    st_counts = firms_veg["state_name"].value_counts().sort_values()
    axes[0, 1].barh(st_counts.index, st_counts.values, color="#d95f02", alpha=0.88)
    axes[0, 1].set_xlabel("Total Vegetation Fire Detections (2021–2024)")
    axes[0, 1].set_title("Wildfire Detections by State", fontweight="bold")
    axes[0, 1].grid(axis="x", alpha=0.3)

    # Panel C: FRP log distribution (positive values)
    frp_pos = firms_veg.loc[firms_veg["frp"] > 0, "frp"]
    axes[1, 0].hist(np.log10(frp_pos), bins=50, color="#e34a33", alpha=0.85, edgecolor="white")
    axes[1, 0].set_xlabel("Log10(Fire Radiative Power [MW])")
    axes[1, 0].set_ylabel("Detection Count")
    axes[1, 0].set_title(
        f"Fire Radiative Power (FRP) Distribution\nMedian={frp_pos.median():.1f} MW, P95={frp_pos.quantile(0.95):.1f} MW",
        fontweight="bold",
    )
    axes[1, 0].grid(True, alpha=0.3)

    # Panel D: Confidence & Day/Night breakdown
    conf_dn = pd.crosstab(firms_veg["confidence"], firms_veg["daynight"])
    conf_labels = {"l": "Low (l)", "n": "Nominal (n)", "h": "High (h)"}
    conf_dn.index = [conf_labels.get(str(v), str(v)) for v in conf_dn.index]
    conf_dn.plot(kind="bar", ax=axes[1, 1], color=["#fc8d62", "#386cb0"], alpha=0.9)
    axes[1, 1].set_xlabel("VIIRS Confidence Category")
    axes[1, 1].set_ylabel("Detection Count")
    axes[1, 1].set_title("Detection Confidence vs Day/Night Overpass", fontweight="bold")
    axes[1, 1].tick_params(axis="x", rotation=0)
    axes[1, 1].legend(title="Overpass", labels=["Day (D)", "Night (N)"])
    axes[1, 1].grid(axis="y", alpha=0.3)

    fig.suptitle(f"HIMA Wildfire Exploratory Data Analysis (2021–2024) | {DISCLAIMER}", fontsize=12, y=1.01)
    plt.tight_layout()
    fig.savefig(out_wf_trends, bbox_inches="tight")
    plt.close(fig)
    outputs["wildfire_seasonal_trends"] = str(out_wf_trends)

    # 3. IMD Rainfall & ERA5 Weather vs Fire EDA
    out_weather = dirs["outputs_figures"] / "weather_rainfall_eda.png"
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), dpi=150)

    # Panel A: IMD regional daily mean rainfall time series
    imd["date"] = pd.to_datetime(imd["date"])
    imd_daily_mean = imd.groupby("date")["imd_rainfall_mm"].mean()
    imd_monthly = imd_daily_mean.resample("ME").sum()
    axes[0, 0].bar(imd_monthly.index, imd_monthly.values, width=22, color="#2b8cbe", alpha=0.85)
    axes[0, 0].set_ylabel("Regional Mean Monthly Rainfall (mm)")
    axes[0, 0].set_title("IMD 0.25° Monthly Rainfall Time Series (NE India, 2021–2024)", fontweight="bold")
    axes[0, 0].grid(axis="y", alpha=0.3)

    # Panel B-D: Weather distributions by Wildfire Label (Train 2021-2023)
    wf_tr = wf[wf["split"] == "train"].dropna(subset=["relative_humidity_min", "soil_water_layer1", "temperature_c"])
    sample_tr = wf_tr.sample(min(120_000, len(wf_tr)), random_state=42)

    sns.kdeplot(
        data=sample_tr, x="relative_humidity_min", hue="fire_detected", common_norm=False, fill=True, ax=axes[0, 1]
    )
    axes[0, 1].set_title("ERA5 Daily Min Relative Humidity (%) by Fire Label", fontweight="bold")
    axes[0, 1].set_xlabel("Daily Min Relative Humidity (%)")
    axes[0, 1].grid(True, alpha=0.3)

    sns.kdeplot(
        data=sample_tr, x="soil_water_layer1", hue="fire_detected", common_norm=False, fill=True, ax=axes[1, 0]
    )
    axes[1, 0].set_title("ERA5 Soil Moisture Layer 1 (m³/m³) by Fire Label", fontweight="bold")
    axes[1, 0].set_xlabel("Volumetric Soil Water (m³/m³)")
    axes[1, 0].grid(True, alpha=0.3)

    sns.kdeplot(
        data=sample_tr, x="dewpoint_depression_c", hue="fire_detected", common_norm=False, fill=True, ax=axes[1, 1]
    )
    axes[1, 1].set_title("ERA5 Dewpoint Depression (T - Td, °C) by Fire Label", fontweight="bold")
    axes[1, 1].set_xlabel("Dewpoint Depression (°C) — Higher = Drier Air")
    axes[1, 1].grid(True, alpha=0.3)

    fig.suptitle(f"HIMA Weather & Fire-Environment EDA (ERA5 44/48 months; IMD 48/48) | {DISCLAIMER}", fontsize=12, y=1.01)
    plt.tight_layout()
    fig.savefig(out_weather, bbox_inches="tight")
    plt.close(fig)
    outputs["weather_rainfall_eda"] = str(out_weather)

    # 4. Feature Correlation Heatmap
    out_corr = dirs["outputs_figures"] / "wildfire_correlation_heatmap.png"
    corr_cols = [
        "fire_detected",
        "temperature_c",
        "dewpoint_depression_c",
        "relative_humidity_min",
        "soil_water_layer1",
        "wind_speed_ms",
        "era5_rain_sum_7d",
        "era5_days_since_rain",
        "imd_rain_sum_7d",
        "imd_rain_sum_15d",
        "imd_days_since_rain",
        "era5_temp_mean_7d",
        "era5_rh_min_7d",
    ]
    corr_mat = sample_tr[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(11, 9), dpi=150)
    sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax, annot_kws={"size": 8})
    ax.set_title(f"Wildfire Target & Weather Feature Correlation Matrix (2021–2023 Train)\n{DISCLAIMER}", fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_corr, bbox_inches="tight")
    plt.close(fig)
    outputs["wildfire_correlation_heatmap"] = str(out_corr)

    # 5 & 6. Landslide Spatial Map (colored by date-quality category) & Antecedent Rainfall EDA
    ls_inv_path = dirs["processed_labels"].parent / "landslide.parquet"
    ls_mod_path = dirs["processed_labels"].parent / "landslide_modeling.parquet"
    if ls_inv_path.exists():
        ls_df = pd.read_parquet(ls_inv_path)

        out_ls_map = dirs["outputs_maps"] / "landslide_inventory_map.png"
        fig, ax = plt.subplots(figsize=(11, 9), dpi=150)
        states_4326.plot(ax=ax, color="#f6f6f2", edgecolor="#333333", linewidth=0.9)
        dq_styles = [
            ("undated_field_validated_location", "#756bb1", 5, 0.35, "Undated GSI Field Slide"),
            ("dated_outside_target_window", "#3182bd", 10, 0.65, "Dated GSI Slide (Pre-2021)"),
            ("dated_in_target_2021_2024", "#e31a1c", 16, 0.85, "Dated GSI Slide (2021–2024)"),
        ]
        for dq_key, col, sz, alp, lbl in dq_styles:
            sub = ls_df[ls_df["date_quality"] == dq_key]
            if len(sub) > 0:
                ax.scatter(sub["longitude"], sub["latitude"], s=sz, c=col, alpha=alp, label=f"{lbl} (n={len(sub):,})")
        ax.legend(title="Date Quality Category", loc="lower right", fontsize=8.5, markerscale=1.6)
        for _, row in states_4326.iterrows():
            c = row.geometry.representative_point()
            ax.annotate(
                row["state_name"],
                xy=(c.x, c.y),
                fontsize=8,
                fontweight="bold",
                ha="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65),
            )
        ax.set_title(
            f"GSI Field-Validated Landslide Inventory — Northeast India ({len(ls_df):,} records)\n"
            f"Note: 0/176 NASA COOLR events fell in NE India | {DISCLAIMER}",
            fontsize=10.5,
            fontweight="bold",
        )
        ax.set_xlabel("Longitude (°E)")
        ax.set_ylabel("Latitude (°N)")
        ax.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        fig.savefig(out_ls_map, bbox_inches="tight")
        plt.close(fig)
        outputs["landslide_inventory_map"] = str(out_ls_map)

        # Panel EDA for GSI Landslide inventory
        out_ls_eda = dirs["outputs_figures"] / "landslide_gsi_coolr_eda.png"
        fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), dpi=150)

        st_ls = ls_df["state_name"].value_counts().sort_values()
        axes[0].barh(st_ls.index, st_ls.values, color="#6a51a3", alpha=0.88)
        axes[0].set_title("GSI Field-Validated Slides by State\n(Inside 7-State Study Boundary)", fontweight="bold")
        axes[0].set_xlabel("Field-Validated Slide Count")
        axes[0].grid(axis="x", alpha=0.3)

        mv = ls_df["movement_type"].replace("", "Unspecified").value_counts().head(8).iloc[::-1]
        axes[1].barh(mv.index, mv.values, color="#238b45", alpha=0.88)
        axes[1].set_title("Top GSI Movement Types", fontweight="bold")
        axes[1].set_xlabel("Slide Count")
        axes[1].grid(axis="x", alpha=0.3)

        dated_21_24 = ls_df[ls_df["date_quality"] == "dated_in_target_2021_2024"].copy()
        mo_counts = dated_21_24["event_date"].dt.month.value_counts().reindex(range(1, 13), fill_value=0)
        axes[2].bar(
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            mo_counts.values,
            color="#e31a1c",
            alpha=0.85,
        )
        axes[2].set_title(f"Dated 2021–2024 Landslides by Month (n={len(dated_21_24)})\n(Peak: May Cyclone Remal + SW Monsoon)", fontweight="bold")
        axes[2].set_ylabel("Dated Event Count")
        axes[2].tick_params(axis="x", rotation=35)
        axes[2].grid(axis="y", alpha=0.3)

        fig.suptitle(f"HIMA Landslide Inventory EDA (COOLR NE=0; GSI Field-Validated n={len(ls_df):,}) | {DISCLAIMER}", fontsize=11, y=1.02)
        plt.tight_layout()
        fig.savefig(out_ls_eda, bbox_inches="tight")
        plt.close(fig)
        outputs["landslide_gsi_coolr_eda"] = str(out_ls_eda)

    if ls_mod_path.exists():
        ls_mod = pd.read_parquet(ls_mod_path)
        out_ls_rain = dirs["outputs_figures"] / "landslide_rainfall_eda.png"
        fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), dpi=150)

        rain_cols = [("imd_rain_sum_3d", "IMD 3-Day Antecedent Rainfall (mm)"),
                     ("imd_rain_sum_7d", "IMD 7-Day Antecedent Rainfall (mm)"),
                     ("soil_water_layer1", "ERA5 Top-Layer Soil Moisture (m³/m³)")]
        for ax, (col, title) in zip(axes, rain_cols):
            sub_plot = ls_mod[[col, "landslide_detected"]].dropna()
            pos_vals = sub_plot.loc[sub_plot["landslide_detected"] == 1, col]
            neg_vals = sub_plot.loc[sub_plot["landslide_detected"] == 0, col]
            if col != "soil_water_layer1":
                pos_plot = np.log1p(np.maximum(pos_vals, 0))
                neg_plot = np.log1p(np.maximum(neg_vals, 0))
                sns.kdeplot(neg_plot, fill=True, label=f"Background (med={neg_vals.median():.1f} mm)", ax=ax)
                sns.kdeplot(pos_plot, fill=True, label=f"Dated Landslide (med={pos_vals.median():.1f} mm)", ax=ax)
                ax.set_xlabel(f"log1p({col})")
            else:
                sns.kdeplot(neg_vals, fill=True, label=f"Background (med={neg_vals.median():.3f})", ax=ax)
                sns.kdeplot(pos_vals, fill=True, label=f"Dated Landslide (med={pos_vals.median():.3f})", ax=ax)
                ax.set_xlabel("Volumetric Soil Water (m³/m³)")
            ax.set_title(title, fontweight="bold")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

        fig.suptitle(f"Antecedent Rainfall & Soil Moisture on Dated 2021–2024 Landslides vs Background | {DISCLAIMER}", fontsize=11, y=1.02)
        plt.tight_layout()
        fig.savefig(out_ls_rain, bbox_inches="tight")
        plt.close(fig)
        outputs["landslide_rainfall_eda"] = str(out_ls_rain)

    return outputs


if __name__ == "__main__":
    out_map = run_all_eda()
    print("EDA visualisations generated:")
    for k, v in out_map.items():
        print(f"  {k}: {v}")

