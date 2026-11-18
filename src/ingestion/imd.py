"""Step 3/6a: IMD daily 0.25-degree gridded rainfall NetCDF validation and ingestion."""

from __future__ import annotations

import calendar
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

from src.config import ensure_project_dirs, load_config


def resolve_imd_time_axis(ds_raw: xr.Dataset, year: int, path: Path) -> tuple[pd.DatetimeIndex, dict[str, Any]]:
    """Inspect and validate the TIME axis of an IMD annual NetCDF file.

    Verifies:
      1. Whether xarray can decode TIME directly via CF units/calendar.
      2. Exact day count (366 for leap year, 365 for non-leap year).
      3. Raw TIME values and attributes so no silent assumption is made.
    """
    expected_days = 366 if calendar.isleap(year) else 365
    time_dim = "TIME" if "TIME" in ds_raw.dims else next(d for d in ds_raw.dims if "time" in d.lower())
    n_steps = int(ds_raw.sizes[time_dim])

    raw_attrs = {k: str(v) for k, v in ds_raw[time_dim].attrs.items()} if time_dim in ds_raw.coords else {}
    raw_vals = ds_raw[time_dim].values if time_dim in ds_raw.coords else np.arange(n_steps)

    # Try CF-compliant decoding first
    decoded_method = ""
    dates: pd.DatetimeIndex | None = None
    try:
        with xr.open_dataset(path, decode_times=True) as ds_dec:
            t_dec = pd.to_datetime(ds_dec[time_dim].values)
            if len(t_dec) == n_steps and int(t_dec[0].year) == year and int(t_dec[-1].year) == year:
                dates = pd.DatetimeIndex(t_dec.normalize())
                decoded_method = "cf_decoded_directly"
    except Exception:
        dates = None

    # Fallback: verify units or exact calendar-year day count if CF metadata was non-standard
    if dates is None:
        units = raw_attrs.get("units", "")
        if n_steps == expected_days:
            # Verify raw values are strictly monotonically increasing by 1 day
            diffs = np.diff(raw_vals.astype(float))
            if len(diffs) > 0 and np.allclose(diffs, 1.0):
                dates = pd.date_range(start=f"{year}-01-01", periods=n_steps, freq="D")
                decoded_method = f"verified_daily_sequence_{expected_days}d (units='{units}')"
            else:
                raise ValueError(f"IMD {path.name}: TIME step increments are not uniform daily: {diffs[:5]}")
        else:
            raise ValueError(
                f"IMD {path.name}: TIME length {n_steps} != expected {expected_days} days for year {year} "
                f"(raw_attrs={raw_attrs}). Manual verification required."
            )

    info = {
        "file": path.name,
        "year": year,
        "time_dim": time_dim,
        "n_steps": n_steps,
        "expected_days_for_year": expected_days,
        "raw_time_attrs": raw_attrs,
        "raw_first_3": [float(x) for x in raw_vals[:3]],
        "raw_last_3": [float(x) for x in raw_vals[-3:]],
        "decoded_method": decoded_method,
        "date_start": str(dates[0].date()),
        "date_end": str(dates[-1].date()),
    }
    return dates, info


def ingest_imd(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate and clip IMD annual NetCDF rainfall files (2021-2024) to Northeast India bbox."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    raw_root = dirs["raw_data_root"]
    target_years = cfg["scope"]["target_years"]

    study_states = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")
    minx, miny, maxx, maxy = study_states.total_bounds
    # 0.5-degree buffer guarantees nearest IMD cell (0.25 deg spacing) exists for every NE India 1 km cell
    lon_min, lon_max = minx - 0.5, maxx + 0.5
    lat_min, lat_max = miny - 0.5, maxy + 0.5

    records_list: list[pd.DataFrame] = []
    file_reports: list[dict[str, Any]] = []
    missing_years: list[int] = []

    for yr in target_years:
        nc_path = raw_root / "data" / "raw" / f"RF25_ind{yr}_rfp25.nc"
        if not nc_path.exists():
            missing_years.append(yr)
            continue

        with xr.open_dataset(nc_path, decode_times=False) as ds:
            dates, time_info = resolve_imd_time_axis(ds, yr, nc_path)

            var_name = "RAINFALL" if "RAINFALL" in ds.data_vars else list(ds.data_vars)[0]
            lat_name = "LATITUDE" if "LATITUDE" in ds.coords else next(c for c in ds.coords if "lat" in c.lower())
            lon_name = "LONGITUDE" if "LONGITUDE" in ds.coords else next(c for c in ds.coords if "lon" in c.lower())

            var_attrs = {k: str(v) for k, v in ds[var_name].attrs.items()}
            lats = ds[lat_name].values.astype(np.float64)
            lons = ds[lon_name].values.astype(np.float64)

            lat_idx = np.where((lats >= lat_min) & (lats <= lat_max))[0]
            lon_idx = np.where((lons >= lon_min) & (lons <= lon_max))[0]

            sub_vals = ds[var_name].isel({lat_name: lat_idx, lon_name: lon_idx}).values.astype(np.float32)

            # Identify and mask IMD missing/fill values (typically -999.0 or _FillValue)
            fill_val = ds[var_name].attrs.get("_FillValue", ds[var_name].attrs.get("missing_value", -999.0))
            try:
                fill_float = float(fill_val)
            except Exception:
                fill_float = -999.0

            nodata_mask = np.isclose(sub_vals, fill_float) | (sub_vals < 0.0)
            nodata_count = int(nodata_mask.sum())
            sub_vals = np.where(nodata_mask, np.nan, sub_vals)

            sub_lats = lats[lat_idx]
            sub_lons = lons[lon_idx]

            # Flatten to tidy daily table: (date, imd_lat, imd_lon, imd_rainfall_mm)
            t_grid, la_grid, lo_grid = np.meshgrid(
                np.arange(len(dates)), np.arange(len(sub_lats)), np.arange(len(sub_lons)), indexing="ij"
            )
            df_yr = pd.DataFrame(
                {
                    "date": dates.values[t_grid.ravel()],
                    "imd_lat": np.round(sub_lats[la_grid.ravel()], 4),
                    "imd_lon": np.round(sub_lons[lo_grid.ravel()], 4),
                    "imd_rainfall_mm": sub_vals.ravel(),
                }
            )
            # Drop grid points that are permanently NaN (outside India land mask in IMD RF25)
            valid_pt = df_yr.groupby(["imd_lat", "imd_lon"])["imd_rainfall_mm"].transform(lambda s: s.notna().any())
            df_yr = df_yr.loc[valid_pt].copy()
            records_list.append(df_yr)

            file_reports.append(
                {
                    **time_info,
                    "variable": var_name,
                    "var_attrs": var_attrs,
                    "fill_value_detected": fill_float,
                    "lat_step_deg": float(np.median(np.abs(np.diff(lats)))),
                    "lon_step_deg": float(np.median(np.abs(np.diff(lons)))),
                    "clipped_lat_count": int(len(sub_lats)),
                    "clipped_lon_count": int(len(sub_lons)),
                    "nodata_cells_masked_in_bbox": nodata_count,
                    "valid_land_grid_points": int(df_yr[["imd_lat", "imd_lon"]].drop_duplicates().shape[0]),
                    "rainfall_min_mm": float(np.nanmin(df_yr["imd_rainfall_mm"])),
                    "rainfall_max_mm": float(np.nanmax(df_yr["imd_rainfall_mm"])),
                    "rainfall_mean_mm": round(float(np.nanmean(df_yr["imd_rainfall_mm"])), 3),
                }
            )

    imd_df = pd.concat(records_list, ignore_index=True)
    imd_df = imd_df.sort_values(["imd_lat", "imd_lon", "date"]).reset_index(drop=True)

    # Assign stable imd_grid_id
    pts = imd_df[["imd_lat", "imd_lon"]].drop_duplicates().sort_values(["imd_lat", "imd_lon"]).reset_index(drop=True)
    pts["imd_grid_id"] = [f"IMD_{i:04d}" for i in range(len(pts))]
    imd_df = imd_df.merge(pts, on=["imd_lat", "imd_lon"], how="left")

    out_parquet = dirs["interim_weather"] / "imd_daily_ne.parquet"
    pts_parquet = dirs["interim_weather"] / "imd_grid_points_ne.parquet"
    imd_df.to_parquet(out_parquet, index=False)
    pts.to_parquet(pts_parquet, index=False)

    metadata = {
        "source_dataset": "IMD_RF25_0.25deg_Daily_Rainfall",
        "units": "mm/day",
        "target_years": target_years,
        "missing_years": missing_years,
        "total_rows": int(len(imd_df)),
        "unique_valid_grid_points": int(len(pts)),
        "date_min": str(imd_df["date"].min().date()),
        "date_max": str(imd_df["date"].max().date()),
        "missing_rainfall_values": int(imd_df["imd_rainfall_mm"].isna().sum()),
        "files": file_reports,
        "outputs": {"daily_parquet": str(out_parquet), "grid_points_parquet": str(pts_parquet)},
    }
    with (dirs["reports"] / "imd_ingestion_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return imd_df, metadata


if __name__ == "__main__":
    df_out, meta = ingest_imd()
    print("IMD ingestion complete.")
    print("Rows:", meta["total_rows"], "| Grid pts:", meta["unique_valid_grid_points"])
    print("Date range:", meta["date_min"], "to", meta["date_max"])
    for f in meta["files"]:
        print(f"  {f['file']}: {f['decoded_method']} | min={f['rainfall_min_mm']} max={f['rainfall_max_mm']} mean={f['rainfall_mean_mm']}")

