"""Step 5b/7a: Wildfire cell-day positive aggregation and leakage-safe modeling dataset builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import ensure_project_dirs, load_config


def assign_imd_season(month: pd.Series) -> pd.Series:
    """Map calendar month (1-12) to official IMD Indian meteorological seasons."""
    return month.map(
        {
            12: "Winter",
            1: "Winter",
            2: "Winter",
            3: "Pre-Monsoon",
            4: "Pre-Monsoon",
            5: "Pre-Monsoon",
            6: "Monsoon",
            7: "Monsoon",
            8: "Monsoon",
            9: "Monsoon",
            10: "Post-Monsoon",
            11: "Post-Monsoon",
        }
    )


def aggregate_firms_to_celldays(firms_df: pd.DataFrame, vegetation_only: bool = True) -> pd.DataFrame:
    """Aggregate point FIRMS detections to unique (cell_id, date) wildfire positive records."""
    df = firms_df.copy()
    if vegetation_only and "is_vegetation_fire" in df.columns:
        df = df.loc[df["is_vegetation_fire"]].copy()

    df["date"] = pd.to_datetime(df["acq_date"]).dt.normalize()
    df["is_day"] = (df["daynight"].astype(str).str.upper() == "D").astype(np.int32)
    df["is_night"] = (df["daynight"].astype(str).str.upper() == "N").astype(np.int32)
    df["is_high_conf"] = (df["confidence"].astype(str).str.lower() == "h").astype(np.int32)
    df["is_nom_conf"] = (df["confidence"].astype(str).str.lower() == "n").astype(np.int32)
    df["is_low_conf"] = (df["confidence"].astype(str).str.lower() == "l").astype(np.int32)

    agg = (
        df.groupby(["cell_id", "date"], as_index=False)
        .agg(
            detection_count=("frp", "size"),
            frp_sum=("frp", "sum"),
            frp_mean=("frp", "mean"),
            frp_max=("frp", "max"),
            brightness_mean=("brightness", "mean"),
            brightness_max=("brightness", "max"),
            day_detections=("is_day", "sum"),
            night_detections=("is_night", "sum"),
            high_conf_count=("is_high_conf", "sum"),
            nominal_conf_count=("is_nom_conf", "sum"),
            low_conf_count=("is_low_conf", "sum"),
            source_file=("source_file", "first"),
        )
    )
    agg["fire_detected"] = np.int8(1)
    agg["source_dataset"] = "NASA_FIRMS_VIIRS_SNPP_C2"
    agg["label_source"] = "firms_vegetation_fire_type0" if vegetation_only else "firms_all_detections"
    return agg


def sample_uniform_celldays(
    cell_ids: np.ndarray,
    dates: pd.DatetimeIndex,
    n_samples: int,
    rng: np.random.Generator,
    exclude_keys: set[tuple[str, pd.Timestamp]] | None = None,
) -> pd.DataFrame:
    """Uniformly sample unique (cell_id, date) pairs without replacement across cells x dates."""
    n_cells = len(cell_ids)
    n_days = len(dates)
    total_space = n_cells * n_days
    target = min(n_samples, total_space)

    collected_cells: list[np.ndarray] = []
    collected_dates: list[np.ndarray] = []
    seen: set[int] = set()
    # Oversample slightly to account for collisions or excluded positives
    batch_size = int(target * 1.15) + 1000

    while len(seen) < target:
        flat_idx = rng.integers(0, total_space, size=batch_size, dtype=np.int64)
        flat_idx = np.unique(flat_idx)
        c_idx = flat_idx // n_days
        d_idx = flat_idx % n_days

        keep_c = []
        keep_d = []
        for fi, ci, di in zip(flat_idx, c_idx, d_idx):
            fi_int = int(fi)
            if fi_int in seen:
                continue
            if exclude_keys is not None and (cell_ids[ci], dates[di]) in exclude_keys:
                continue
            seen.add(fi_int)
            keep_c.append(cell_ids[ci])
            keep_d.append(dates[di])
            if len(seen) >= target:
                break
        if keep_c:
            collected_cells.append(np.array(keep_c, dtype=object))
            collected_dates.append(np.array(keep_d, dtype="datetime64[ns]"))

    return pd.DataFrame(
        {
            "cell_id": np.concatenate(collected_cells),
            "date": pd.to_datetime(np.concatenate(collected_dates)),
        }
    )


def build_wildfire_dataset(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build leakage-safe wildfire modeling dataset (train: 2021-2022, realistic test: 2024).

    Explicitly excludes 2023 because FIRMS 2023 archive is missing (never replaced with zeros).
    """
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    rng = np.random.default_rng(int(cfg["project"]["random_state"]))
    train_years = cfg["wildfire"]["temporal_train_years"]
    test_years = cfg["wildfire"]["temporal_test_years"]
    neg_ratio = int(cfg["wildfire"]["negative_sampling_ratio"])

    firms_df = pd.read_parquet(dirs["interim_firms"] / "firms_ne_india_detections.parquet")
    grid_df = pd.read_parquet(dirs["processed_grid"] / "grid_1km_with_weather_keys.parquet")
    era5_feat = pd.read_parquet(dirs["processed_weather"] / "era5_features_daily.parquet")
    imd_feat = pd.read_parquet(dirs["processed_weather"] / "imd_features_daily.parquet")

    # 1. Aggregate positives to unique (cell_id, date)
    pos_df = aggregate_firms_to_celldays(firms_df, vegetation_only=True)
    pos_df["year"] = pos_df["date"].dt.year.astype(np.int32)
    pos_out_path = dirs["processed_labels"] / "wildfire_positive_celldays.parquet"
    pos_df.to_parquet(pos_out_path, index=False)

    cell_ids = grid_df["cell_id"].to_numpy()

    # 2. Build Training split (2021-2022): all positives + uniform negative sample (neg_ratio : 1)
    train_pos = pos_df[pos_df["year"].isin(train_years)].copy()
    train_dates = pd.DatetimeIndex(
        np.concatenate([pd.date_range(f"{y}-01-01", f"{y}-12-31", freq="D").values for y in train_years])
    )
    train_pos_keys = set(zip(train_pos["cell_id"], train_pos["date"]))
    n_train_neg = len(train_pos) * neg_ratio

    train_neg = sample_uniform_celldays(cell_ids, train_dates, n_train_neg, rng, exclude_keys=train_pos_keys)
    train_neg["fire_detected"] = np.int8(0)
    train_neg["detection_count"] = np.int32(0)
    train_neg["frp_sum"] = np.float32(0.0)
    train_neg["frp_mean"] = np.float32(0.0)
    train_neg["frp_max"] = np.float32(0.0)
    train_neg["brightness_mean"] = np.float32(np.nan)
    train_neg["brightness_max"] = np.float32(np.nan)
    train_neg["day_detections"] = np.int32(0)
    train_neg["night_detections"] = np.int32(0)
    train_neg["high_conf_count"] = np.int32(0)
    train_neg["nominal_conf_count"] = np.int32(0)
    train_neg["low_conf_count"] = np.int32(0)
    train_neg["source_file"] = "uniform_background_sample"
    train_neg["source_dataset"] = "HIMA_GRID_BACKGROUND"
    train_neg["label_source"] = "observed_no_record_sampled"
    train_neg["year"] = train_neg["date"].dt.year.astype(np.int32)

    train_df = pd.concat([train_pos, train_neg], ignore_index=True)
    train_df["split"] = "train"

    # 3. Build Realistic-Prevalence Test split (2024): uniform random sample of 1,000,000 cell-days
    # Preserves true 2024 NE India wildfire base rate without artificial oversampling.
    test_dates = pd.DatetimeIndex(
        np.concatenate([pd.date_range(f"{y}-01-01", f"{y}-12-31", freq="D").values for y in test_years])
    )
    test_pos = pos_df[pos_df["year"].isin(test_years)].copy()
    test_total_space = len(cell_ids) * len(test_dates)
    true_test_prevalence = len(test_pos) / test_total_space

    test_sample_size = min(1_000_000, test_total_space)
    test_base = sample_uniform_celldays(cell_ids, test_dates, test_sample_size, rng, exclude_keys=None)
    test_df = test_base.merge(
        test_pos.drop(columns=["year"]),
        on=["cell_id", "date"],
        how="left",
    )
    test_df["fire_detected"] = test_df["fire_detected"].fillna(0).astype(np.int8)
    for zcol in ["detection_count", "day_detections", "night_detections", "high_conf_count", "nominal_conf_count", "low_conf_count"]:
        test_df[zcol] = test_df[zcol].fillna(0).astype(np.int32)
    for fcol in ["frp_sum", "frp_mean", "frp_max"]:
        test_df[fcol] = test_df[fcol].fillna(0.0).astype(np.float32)
    test_df["source_file"] = test_df["source_file"].fillna("uniform_realistic_test_sample")
    test_df["source_dataset"] = test_df["source_dataset"].fillna("HIMA_GRID_BACKGROUND")
    test_df["label_source"] = test_df["label_source"].fillna("observed_no_record_realistic_test")
    test_df["year"] = test_df["date"].dt.year.astype(np.int32)
    test_df["split"] = "test_realistic"

    # Combine and attach grid attributes + spatial block IDs + weather features + seasonality
    full_df = pd.concat([train_df, test_df], ignore_index=True)

    # Spatial block (50 km x 50 km) for leakage-safe StratifiedGroupKFold inside training data
    grid_join_cols = [
        "cell_id",
        "x_m",
        "y_m",
        "centroid_lat",
        "centroid_lon",
        "state_name",
        "era5_grid_id",
        "imd_grid_id",
    ]
    full_df = full_df.merge(grid_df[grid_join_cols], on="cell_id", how="left")
    bx = np.floor(full_df["x_m"].to_numpy() / 50_000.0).astype(np.int32)
    by = np.floor(full_df["y_m"].to_numpy() / 50_000.0).astype(np.int32)
    full_df["spatial_block_id"] = [f"B_{x}_{y}" for x, y in zip(bx, by)]

    # Calendar / seasonal features
    full_df["month"] = full_df["date"].dt.month.astype(np.int8)
    full_df["day_of_year"] = full_df["date"].dt.day_of_year.astype(np.int16)
    full_df["sin_doy"] = np.sin(2.0 * np.pi * full_df["day_of_year"] / 365.25).astype(np.float32)
    full_df["cos_doy"] = np.cos(2.0 * np.pi * full_df["day_of_year"] / 365.25).astype(np.float32)
    full_df["season"] = assign_imd_season(full_df["month"])

    # Join daily ERA5 & IMD features cleanly
    full_df = full_df.merge(era5_feat, on=["era5_grid_id", "date"], how="left")
    full_df = full_df.merge(imd_feat, on=["imd_grid_id", "date"], how="left")

    out_path = dirs["processed_dir"] if "processed_dir" in dirs else Path("data/processed")
    wildfire_parquet = dirs["processed_labels"].parent / "wildfire.parquet"
    full_df.to_parquet(wildfire_parquet, index=False)

    n_test_pos_real = int((test_df["fire_detected"] == 1).sum())
    meta = {
        "output_parquet": str(wildfire_parquet),
        "positive_celldays_parquet": str(pos_out_path),
        "train_years": train_years,
        "test_years": test_years,
        "excluded_years": cfg["wildfire"]["missing_years_in_window"],
        "excluded_years_reason": "FIRMS 2023 archive missing; 4 ERA5 months missing in 2023. Never filled with zeros.",
        "total_positive_celldays_all_valid_years": int(len(pos_df)),
        "positive_celldays_by_year": {int(k): int(v) for k, v in pos_df["year"].value_counts().sort_index().items()},
        "train_rows": int(len(train_df)),
        "train_positives": int(len(train_pos)),
        "train_negatives": int(len(train_neg)),
        "train_positive_rate": round(float(len(train_pos) / len(train_df)), 5),
        "test_realistic_rows": int(len(test_df)),
        "test_realistic_positives": n_test_pos_real,
        "test_realistic_positive_rate": round(float(n_test_pos_real / len(test_df)), 6),
        "test_true_population_positives_2024": int(len(test_pos)),
        "test_true_population_celldays_2024": int(test_total_space),
        "test_true_population_prevalence_2024": round(float(true_test_prevalence), 6),
        "unique_spatial_blocks_train": int(full_df.loc[full_df["split"] == "train", "spatial_block_id"].nunique()),
        "era5_missing_in_train": int(full_df.loc[full_df["split"] == "train", "era5_missing_flag"].sum()),
        "era5_missing_in_test": int(full_df.loc[full_df["split"] == "test_realistic", "era5_missing_flag"].sum()),
    }

    with (dirs["reports"] / "wildfire_dataset_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    return full_df, meta


if __name__ == "__main__":
    df_out, meta = build_wildfire_dataset()
    print("Wildfire dataset built.")
    print(f"Train ({meta['train_years']}): {meta['train_rows']:,} rows ({meta['train_positives']:,} pos, rate={meta['train_positive_rate']:.4f})")
    print(
        f"Test realistic (2024): {meta['test_realistic_rows']:,} rows "
        f"({meta['test_realistic_positives']:,} pos, rate={meta['test_realistic_positive_rate']:.6f}, "
        f"true 2024 rate={meta['test_true_population_prevalence_2024']:.6f})"
    )
