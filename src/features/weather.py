"""Step 6: Leakage-safe daily weather feature engineering & 1 km grid spatial lookup."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from src.config import ensure_project_dirs, load_config


def map_grid_to_weather_points(
    grid_df: pd.DataFrame,
    era5_pts: pd.DataFrame,
    imd_pts: pd.DataFrame,
) -> pd.DataFrame:
    """Attach nearest ERA5 and IMD weather grid IDs and distances (km) to every 1 km cell."""
    out = grid_df.copy()

    # Use approximate local equirectangular scaling (cos(26 deg) for NE India) for accurate nearest-neighbor lookup
    lat_scale = 111.32
    lon_scale = 111.32 * np.cos(np.deg2rad(26.0))

    grid_xy = np.column_stack([out["centroid_lon"].to_numpy() * lon_scale, out["centroid_lat"].to_numpy() * lat_scale])

    era5_xy = np.column_stack([era5_pts["era5_lon"].to_numpy() * lon_scale, era5_pts["era5_lat"].to_numpy() * lat_scale])
    era5_tree = cKDTree(era5_xy)
    e_dist, e_idx = era5_tree.query(grid_xy, k=1)
    out["era5_grid_id"] = era5_pts["era5_grid_id"].to_numpy()[e_idx]
    out["era5_dist_km"] = np.round(e_dist, 2).astype(np.float32)

    imd_xy = np.column_stack([imd_pts["imd_lon"].to_numpy() * lon_scale, imd_pts["imd_lat"].to_numpy() * lat_scale])
    imd_tree = cKDTree(imd_xy)
    i_dist, i_idx = imd_tree.query(grid_xy, k=1)
    out["imd_grid_id"] = imd_pts["imd_grid_id"].to_numpy()[i_idx]
    out["imd_dist_km"] = np.round(i_dist, 2).astype(np.float32)

    return out


def compute_days_since_rain_array(rain_mm: np.ndarray, threshold_mm: float = 1.0, cap: int = 60) -> np.ndarray:
    """Compute consecutive dry days ending at each day on a contiguous daily series.

    NaN inputs break continuity (output becomes NaN until rain resumes or valid values restart cleanly).
    """
    n = len(rain_mm)
    out = np.full(n, np.nan, dtype=np.float32)
    dry_streak = np.nan
    for i in range(n):
        val = rain_mm[i]
        if np.isnan(val):
            dry_streak = np.nan
            out[i] = np.nan
        elif val >= threshold_mm:
            dry_streak = 0.0
            out[i] = 0.0
        else:
            if np.isnan(dry_streak):
                # Start counting cautiously from 1 after an unknown gap? No — stay NaN until a known rain event
                # or cap? Wait: at start of Jan 2021 (dry winter), keeping NaN until first rain would drop Jan-Feb!
                # Instead, count observed consecutive dry days since series start / gap reset only if within valid run.
                dry_streak = 1.0
            else:
                dry_streak = min(dry_streak + 1.0, float(cap))
            out[i] = dry_streak
    return out


def build_imd_features(imd_df: pd.DataFrame, date_start: str, date_end: str) -> pd.DataFrame:
    """Compute leakage-safe antecedent IMD rainfall features on a complete daily calendar."""
    full_dates = pd.date_range(date_start, date_end, freq="D")
    grid_ids = imd_df["imd_grid_id"].unique()

    # Complete (imd_grid_id, date) index so rolling windows strictly represent calendar days
    full_idx = pd.MultiIndex.from_product([grid_ids, full_dates], names=["imd_grid_id", "date"])
    base = (
        imd_df[["imd_grid_id", "date", "imd_rainfall_mm"]]
        .drop_duplicates(subset=["imd_grid_id", "date"])
        .set_index(["imd_grid_id", "date"])
        .reindex(full_idx)
        .reset_index()
    )

    g = base.groupby("imd_grid_id", sort=False)["imd_rainfall_mm"]

    base["imd_rain_1d"] = base["imd_rainfall_mm"].astype(np.float32)
    base["imd_rain_lag1d"] = g.shift(1).astype(np.float32)
    base["imd_rain_sum_3d"] = g.transform(lambda s: s.rolling(3, min_periods=3).sum()).astype(np.float32)
    base["imd_rain_sum_7d"] = g.transform(lambda s: s.rolling(7, min_periods=6).sum()).astype(np.float32)
    base["imd_rain_sum_15d"] = g.transform(lambda s: s.rolling(15, min_periods=12).sum()).astype(np.float32)
    base["imd_rain_max_7d"] = g.transform(lambda s: s.rolling(7, min_periods=6).max()).astype(np.float32)
    # IMD rainy-day definition: >= 2.5 mm/day
    base["imd_is_rainy"] = (base["imd_rainfall_mm"] >= 2.5).astype(np.float32)
    base.loc[base["imd_rainfall_mm"].isna(), "imd_is_rainy"] = np.nan
    gr = base.groupby("imd_grid_id", sort=False)["imd_is_rainy"]
    base["imd_rainy_days_7d"] = gr.transform(lambda s: s.rolling(7, min_periods=6).sum()).astype(np.float32)
    base["imd_rainy_days_15d"] = gr.transform(lambda s: s.rolling(15, min_periods=12).sum()).astype(np.float32)

    dsr_list = []
    for _, grp in base.groupby("imd_grid_id", sort=False):
        dsr_list.append(compute_days_since_rain_array(grp["imd_rainfall_mm"].to_numpy(), threshold_mm=2.5, cap=60))
    base["imd_days_since_rain"] = np.concatenate(dsr_list)
    base = base.drop(columns=["imd_rainfall_mm", "imd_is_rainy"])
    return base


def build_era5_features(era5_df: pd.DataFrame, date_start: str, date_end: str) -> pd.DataFrame:
    """Compute leakage-safe ERA5 daily & rolling features on a complete calendar (gaps remain NaN)."""
    full_dates = pd.date_range(date_start, date_end, freq="D")
    grid_ids = era5_df["era5_grid_id"].unique()
    keep_cols = [
        "era5_grid_id",
        "date",
        "temperature_c",
        "dewpoint_c",
        "dewpoint_depression_c",
        "wind_speed_ms",
        "soil_water_layer1",
        "era5_rainfall_mm",
        "relative_humidity_mean",
        "relative_humidity_min",
    ]
    avail_cols = [c for c in keep_cols if c in era5_df.columns]

    full_idx = pd.MultiIndex.from_product([grid_ids, full_dates], names=["era5_grid_id", "date"])
    base = (
        era5_df[avail_cols]
        .drop_duplicates(subset=["era5_grid_id", "date"])
        .set_index(["era5_grid_id", "date"])
        .reindex(full_idx)
        .reset_index()
    )

    grp = base.groupby("era5_grid_id", sort=False)

    base["era5_temp_mean_7d"] = grp["temperature_c"].transform(lambda s: s.rolling(7, min_periods=6).mean()).astype(np.float32)
    base["era5_temp_max_7d"] = grp["temperature_c"].transform(lambda s: s.rolling(7, min_periods=6).max()).astype(np.float32)
    base["era5_rh_min_7d"] = grp["relative_humidity_min"].transform(lambda s: s.rolling(7, min_periods=6).min()).astype(np.float32)
    base["era5_rh_mean_7d"] = grp["relative_humidity_mean"].transform(lambda s: s.rolling(7, min_periods=6).mean()).astype(np.float32)
    base["era5_soil_water_mean_7d"] = grp["soil_water_layer1"].transform(lambda s: s.rolling(7, min_periods=6).mean()).astype(np.float32)
    base["era5_wind_mean_7d"] = grp["wind_speed_ms"].transform(lambda s: s.rolling(7, min_periods=6).mean()).astype(np.float32)
    base["era5_rain_sum_3d"] = grp["era5_rainfall_mm"].transform(lambda s: s.rolling(3, min_periods=3).sum()).astype(np.float32)
    base["era5_rain_sum_7d"] = grp["era5_rainfall_mm"].transform(lambda s: s.rolling(7, min_periods=6).sum()).astype(np.float32)
    base["era5_rain_sum_15d"] = grp["era5_rainfall_mm"].transform(lambda s: s.rolling(15, min_periods=12).sum()).astype(np.float32)

    dsr_list = []
    for _, sub in base.groupby("era5_grid_id", sort=False):
        dsr_list.append(compute_days_since_rain_array(sub["era5_rainfall_mm"].to_numpy(), threshold_mm=1.0, cap=60))
    base["era5_days_since_rain"] = np.concatenate(dsr_list)

    # Flag missing ERA5 days explicitly so downstream models/EDA know when weather was absent
    base["era5_missing_flag"] = base["temperature_c"].isna().astype(np.int8)
    return base


def build_all_weather_features(config_path: str | Path | None = None) -> dict[str, Any]:
    """Run full weather feature pipeline and save processed tables + grid weather keys."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    grid_df = pd.read_parquet(dirs["processed_grid"] / "grid_1km_attributes.parquet")
    era5_pts = pd.read_parquet(dirs["interim_weather"] / "era5_grid_points_ne.parquet")
    imd_pts = pd.read_parquet(dirs["interim_weather"] / "imd_grid_points_ne.parquet")

    grid_linked = map_grid_to_weather_points(grid_df, era5_pts, imd_pts)
    grid_linked_path = dirs["processed_grid"] / "grid_1km_with_weather_keys.parquet"
    grid_linked.to_parquet(grid_linked_path, index=False)

    # Filter weather points strictly to those actually referenced by NE India 1 km cells (saves RAM/disk!)
    used_era5_ids = set(grid_linked["era5_grid_id"].unique())
    used_imd_ids = set(grid_linked["imd_grid_id"].unique())

    era5_raw = pd.read_parquet(dirs["interim_weather"] / "era5_daily_ne.parquet")
    era5_raw = era5_raw[era5_raw["era5_grid_id"].isin(used_era5_ids)].copy()

    imd_raw = pd.read_parquet(dirs["interim_weather"] / "imd_daily_ne.parquet")
    imd_raw = imd_raw[imd_raw["imd_grid_id"].isin(used_imd_ids)].copy()

    d_start = cfg["scope"]["date_start"]
    d_end = cfg["scope"]["date_end"]

    imd_feat = build_imd_features(imd_raw, d_start, d_end)
    era5_feat = build_era5_features(era5_raw, d_start, d_end)

    imd_feat_path = dirs["processed_weather"] / "imd_features_daily.parquet"
    era5_feat_path = dirs["processed_weather"] / "era5_features_daily.parquet"
    imd_feat.to_parquet(imd_feat_path, index=False)
    era5_feat.to_parquet(era5_feat_path, index=False)

    meta = {
        "date_start": d_start,
        "date_end": d_end,
        "prediction_cutoff": cfg["weather"]["prediction_cutoff"],
        "ne_cells_count": int(len(grid_linked)),
        "used_era5_grid_points": int(len(used_era5_ids)),
        "used_imd_grid_points": int(len(used_imd_ids)),
        "era5_nearest_dist_km_median": round(float(grid_linked["era5_dist_km"].median()), 2),
        "era5_nearest_dist_km_max": round(float(grid_linked["era5_dist_km"].max()), 2),
        "imd_nearest_dist_km_median": round(float(grid_linked["imd_dist_km"].median()), 2),
        "imd_nearest_dist_km_max": round(float(grid_linked["imd_dist_km"].max()), 2),
        "imd_feature_rows": int(len(imd_feat)),
        "era5_feature_rows": int(len(era5_feat)),
        "era5_missing_rows_flagged": int(era5_feat["era5_missing_flag"].sum()),
        "imd_feature_columns": [c for c in imd_feat.columns if c not in {"imd_grid_id", "date"}],
        "era5_feature_columns": [c for c in era5_feat.columns if c not in {"era5_grid_id", "date"}],
        "outputs": {
            "grid_linked": str(grid_linked_path),
            "imd_features": str(imd_feat_path),
            "era5_features": str(era5_feat_path),
        },
    }
    with (dirs["reports"] / "weather_features_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    return meta


if __name__ == "__main__":
    m = build_all_weather_features()
    print("Weather features built successfully.")
    print(f"Used ERA5 grid pts: {m['used_era5_grid_points']} (median dist {m['era5_nearest_dist_km_median']} km)")
    print(f"Used IMD grid pts:  {m['used_imd_grid_points']} (median dist {m['imd_nearest_dist_km_median']} km)")
    print(f"ERA5 feature rows:  {m['era5_feature_rows']:,} (missing flagged: {m['era5_missing_rows_flagged']:,})")
    print(f"IMD feature rows:   {m['imd_feature_rows']:,}")

