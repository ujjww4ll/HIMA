"""Step 3/6b: ERA5-Land processed daily weather NetCDF validation and ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

from src.config import ensure_project_dirs, load_config


def ingest_era5_processed(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load available ERA5-Land daily NetCDF files for 2021-2024, validate units, clip to NE India.

    Explicitly records missing months (never fills missing months with zeros).
    Keeps ERA5 precipitation separate from IMD rainfall (`era5_rainfall_mm`).
    """
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    raw_root = dirs["raw_data_root"]
    target_years = cfg["scope"]["target_years"]

    study_states = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")
    minx, miny, maxx, maxy = study_states.total_bounds
    lon_min, lon_max = minx - 0.25, maxx + 0.25
    lat_min, lat_max = miny - 0.25, maxy + 0.25

    era5_dir = raw_root / "data" / "processed" / "weather"
    present_months: list[str] = []
    missing_months: list[str] = []
    monthly_frames: list[pd.DataFrame] = []
    sample_var_attrs: dict[str, Any] = {}
    rh_out_of_range_count = 0

    for yr in target_years:
        for mo in range(1, 13):
            ym = f"{yr:04d}-{mo:02d}"
            nc_path = era5_dir / f"ERA5_Land_daily_{yr:04d}_{mo:02d}.nc"
            if not nc_path.exists():
                missing_months.append(ym)
                continue

            present_months.append(ym)
            with xr.open_dataset(nc_path) as ds:
                if not sample_var_attrs:
                    sample_var_attrs = {
                        v: {ak: str(av) for ak, av in ds[v].attrs.items()} for v in ds.data_vars
                    }

                lats = ds["latitude"].values.astype(np.float64)
                lons = ds["longitude"].values.astype(np.float64)
                lat_idx = np.where((lats >= lat_min) & (lats <= lat_max))[0]
                lon_idx = np.where((lons >= lon_min) & (lons <= lon_max))[0]
                sub = ds.isel(latitude=lat_idx, longitude=lon_idx)

                dates = pd.to_datetime(sub["time"].values).normalize()
                sub_lats = lats[lat_idx]
                sub_lons = lons[lon_idx]

                t_g, la_g, lo_g = np.meshgrid(
                    np.arange(len(dates)), np.arange(len(sub_lats)), np.arange(len(sub_lons)), indexing="ij"
                )

                data_dict: dict[str, Any] = {
                    "date": dates.values[t_g.ravel()],
                    "era5_lat": np.round(sub_lats[la_g.ravel()], 4),
                    "era5_lon": np.round(sub_lons[lo_g.ravel()], 4),
                }

                # Extract expected ERA5 variables cleanly
                for col in [
                    "temperature_c",
                    "dewpoint_c",
                    "u_wind",
                    "v_wind",
                    "soil_water_layer1",
                    "rainfall_m",
                    "relative_humidity_mean",
                    "relative_humidity_min",
                ]:
                    if col in sub.data_vars:
                        data_dict[col] = sub[col].values.astype(np.float32).ravel()

                df_mo = pd.DataFrame(data_dict)
                monthly_frames.append(df_mo)

    era5_df = pd.concat(monthly_frames, ignore_index=True)

    # Drop ocean/invalid grid points that are always NaN for temperature_c
    valid_pt = era5_df.groupby(["era5_lat", "era5_lon"])["temperature_c"].transform(lambda s: s.notna().any())
    era5_df = era5_df.loc[valid_pt].copy()

    # Unit conversion & derived variables (documented)
    if "rainfall_m" in era5_df.columns:
        # Clamp tiny negative numerical noise from reanalysis accumulation (< 0) to 0 while preserving NaNs
        rain_m = era5_df["rainfall_m"].to_numpy(dtype=np.float32)
        era5_df["era5_rainfall_mm"] = np.where(np.isnan(rain_m), np.nan, np.maximum(rain_m, 0.0) * 1000.0).astype(np.float32)

    if "u_wind" in era5_df.columns and "v_wind" in era5_df.columns:
        era5_df["wind_speed_ms"] = np.sqrt(
            np.square(era5_df["u_wind"].to_numpy(dtype=np.float32))
            + np.square(era5_df["v_wind"].to_numpy(dtype=np.float32))
        ).astype(np.float32)

    # Validate relative humidity range [0, 100]
    for rh_col in ["relative_humidity_mean", "relative_humidity_min"]:
        if rh_col in era5_df.columns:
            vals = era5_df[rh_col]
            out_mask = vals.notna() & ((vals < 0.0) | (vals > 100.0))
            rh_out_of_range_count += int(out_mask.sum())
            if out_mask.any():
                era5_df[rh_col] = vals.clip(0.0, 100.0).astype(np.float32)

    # Dewpoint depression (temperature - dewpoint): physically meaningful dryness indicator for wildfire
    if "temperature_c" in era5_df.columns and "dewpoint_c" in era5_df.columns:
        era5_df["dewpoint_depression_c"] = (era5_df["temperature_c"] - era5_df["dewpoint_c"]).astype(np.float32)

    # Assign stable era5_grid_id
    pts = era5_df[["era5_lat", "era5_lon"]].drop_duplicates().sort_values(["era5_lat", "era5_lon"]).reset_index(drop=True)
    pts["era5_grid_id"] = [f"ERA5_{i:04d}" for i in range(len(pts))]
    era5_df = era5_df.merge(pts, on=["era5_lat", "era5_lon"], how="left")
    era5_df = era5_df.sort_values(["era5_grid_id", "date"]).reset_index(drop=True)

    out_parquet = dirs["interim_weather"] / "era5_daily_ne.parquet"
    pts_parquet = dirs["interim_weather"] / "era5_grid_points_ne.parquet"
    era5_df.to_parquet(out_parquet, index=False)
    pts.to_parquet(pts_parquet, index=False)

    summary_stats = {}
    for col in [
        "temperature_c",
        "dewpoint_c",
        "dewpoint_depression_c",
        "wind_speed_ms",
        "soil_water_layer1",
        "era5_rainfall_mm",
        "relative_humidity_mean",
        "relative_humidity_min",
    ]:
        if col in era5_df.columns:
            s = era5_df[col]
            summary_stats[col] = {
                "min": round(float(s.min()), 4),
                "median": round(float(s.median()), 4),
                "max": round(float(s.max()), 4),
                "missing_count": int(s.isna().sum()),
            }

    metadata = {
        "source_dataset": "ERA5_Land_Processed_Daily_NetCDF",
        "target_years": target_years,
        "months_present_count": len(present_months),
        "months_expected_count": len(target_years) * 12,
        "months_missing": missing_months,
        "missing_months_policy": "Explicitly absent/NaN — never replaced with zeros.",
        "total_rows": int(len(era5_df)),
        "unique_valid_grid_points": int(len(pts)),
        "date_min": str(era5_df["date"].min().date()),
        "date_max": str(era5_df["date"].max().date()),
        "rh_values_clipped_to_0_100": rh_out_of_range_count,
        "sample_var_attrs": sample_var_attrs,
        "summary_stats": summary_stats,
        "outputs": {"daily_parquet": str(out_parquet), "grid_points_parquet": str(pts_parquet)},
    }
    with (dirs["reports"] / "era5_ingestion_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return era5_df, metadata


if __name__ == "__main__":
    df_out, meta = ingest_era5_processed()
    print("ERA5 processed ingestion complete.")
    print(f"Months present: {meta['months_present_count']}/{meta['months_expected_count']} | Missing: {meta['months_missing']}")
    print("Total rows:", meta["total_rows"], "| Grid pts:", meta["unique_valid_grid_points"])
    print("Summary stats:", json.dumps(meta["summary_stats"], indent=2))

