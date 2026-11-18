"""Step 5a: NASA FIRMS wildfire ingestion, schema validation, and spatial filtering."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer

from src.config import ensure_project_dirs, load_config


# VIIRS S-NPP C2 standard product definitions (NASA FIRMS documentation)
VIIRS_TYPE_MEANINGS = {
    0: "presumed_vegetation_fire",
    1: "active_volcano",
    2: "other_static_land_source",
    3: "offshore",
}
VIIRS_CONFIDENCE_MEANINGS = {
    "l": "low",
    "n": "nominal",
    "h": "high",
}


def find_target_firms_zips(
    raw_data_root: Path, target_years: list[int]
) -> tuple[list[tuple[Path, list[int]]], list[int], list[str]]:
    """Locate all FIRMS ZIP archives that overlap target_years by checking every acq_date year inside each CSV."""
    target_set = set(target_years)
    matched_zips: list[tuple[Path, list[int]]] = []
    covered_years: set[int] = set()
    outside_window: list[str] = []

    for zp in sorted(raw_data_root.rglob("DL_FIRE*.zip")):
        with zipfile.ZipFile(zp, "r") as zf:
            csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csvs:
                continue
            main_csv = next((c for c in csvs if "archive" in c.lower()), csvs[0])
            with zf.open(main_csv) as fh:
                dates_col = pd.read_csv(fh, usecols=["acq_date"])["acq_date"]
            years_in_zip = sorted(int(y) for y in dates_col.dropna().astype(str).str[:4].unique() if y.isdigit())
            overlap = sorted(y for y in years_in_zip if y in target_set)
            if overlap:
                # Only include archive if it contributes at least one new target year (avoids redundant 2021 copy from 816516)
                new_years = [y for y in overlap if y not in covered_years]
                if new_years:
                    matched_zips.append((zp, years_in_zip))
                    covered_years.update(overlap)
                else:
                    outside_window.append(f"{zp.name} (years={years_in_zip}, already covered)")
            else:
                outside_window.append(f"{zp.name} (years={years_in_zip})")

    missing = [y for y in target_years if y not in covered_years]
    return matched_zips, missing, outside_window


def ingest_firms(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Extract target-year FIRMS ZIPs to interim, validate schema, filter to NE India, assign 1 km cell_id."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    target_years = cfg["scope"]["target_years"]
    d_start = pd.Timestamp(cfg["scope"]["date_start"])
    d_end = pd.Timestamp(cfg["scope"]["date_end"])

    matched_zips, missing_years, outside_zips = find_target_firms_zips(dirs["raw_data_root"], target_years)
    if not matched_zips:
        raise FileNotFoundError(f"No FIRMS archives found for target years {target_years}")

    # Load study boundaries and 1 km grid metadata + attributes
    study_states = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")
    grid_attr = pd.read_parquet(dirs["processed_grid"] / "grid_1km_attributes.parquet")
    with (dirs["reports"] / "grid_metadata.json").open("r", encoding="utf-8") as fh:
        grid_meta = json.load(fh)

    minx, miny, maxx, maxy = study_states.total_bounds
    proj_crs = grid_meta["projected_crs"]
    geo_crs = grid_meta["geographic_crs"]
    origin_x = float(grid_meta["origin_x_m"])
    origin_y = float(grid_meta["origin_y_m"])
    cell_size = float(grid_meta["cell_size_m"])
    transformer = Transformer.from_crs(geo_crs, proj_crs, always_xy=True)

    frames: list[pd.DataFrame] = []
    archive_stats: list[dict[str, Any]] = []

    for zp, years_in_zip in matched_zips:
        extract_dir = dirs["interim_firms"] / zp.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zp, "r") as zf:
            csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            main_csv = next((c for c in csvs if "archive" in c.lower()), csvs[0])
            out_csv = extract_dir / Path(main_csv).name
            if not out_csv.exists():
                with zf.open(main_csv) as src_fh, out_csv.open("wb") as dst_fh:
                    dst_fh.write(src_fh.read())

        df = pd.read_csv(out_csv, low_memory=False)
        total_national = len(df)

        # Parse numeric coordinates and dates
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        df["acq_date"] = pd.to_datetime(df["acq_date"], errors="coerce")
        df["acq_time"] = df["acq_time"].astype(str).str.zfill(4)
        for num_col in ["brightness", "scan", "track", "bright_t31", "frp", "type"]:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

        # Strict date-window & bounding-box pre-filter before exact projected grid assignment
        bbox_mask = (
            (df["longitude"] >= minx - 0.1)
            & (df["longitude"] <= maxx + 0.1)
            & (df["latitude"] >= miny - 0.1)
            & (df["latitude"] <= maxy + 0.1)
            & (df["acq_date"] >= d_start)
            & (df["acq_date"] <= d_end)
        )
        df_sub = df.loc[bbox_mask].copy()

        # Reproject to metric CRS and map directly to fishnet (grid_col, grid_row)
        x_m, y_m = transformer.transform(df_sub["longitude"].to_numpy(), df_sub["latitude"].to_numpy())
        df_sub["x_m"] = x_m
        df_sub["y_m"] = y_m
        df_sub["grid_col"] = np.floor((x_m - origin_x) / cell_size).astype(np.int32)
        df_sub["grid_row"] = np.floor((y_m - origin_y) / cell_size).astype(np.int32)

        # Inner join with validated NE India 1 km grid (keeps strictly detections inside NE India cells)
        df_ne = df_sub.merge(
            grid_attr[["cell_id", "grid_col", "grid_row", "state_name", "centroid_lat", "centroid_lon"]],
            on=["grid_col", "grid_row"],
            how="inner",
        )
        df_ne["year"] = df_ne["acq_date"].dt.year.astype(np.int32)
        df_ne["month"] = df_ne["acq_date"].dt.month.astype(np.int32)
        df_ne["source_dataset"] = "NASA_FIRMS_VIIRS_SNPP_C2"
        df_ne["source_file"] = zp.name

        archive_stats.append(
            {
                "zip_file": zp.name,
                "years_in_archive": years_in_zip,
                "extracted_csv": str(out_csv),
                "national_rows": int(total_national),
                "ne_india_target_window_rows": int(len(df_ne)),
                "date_min": str(df_ne["acq_date"].min().date()) if len(df_ne) else None,
                "date_max": str(df_ne["acq_date"].max().date()) if len(df_ne) else None,
            }
        )
        frames.append(df_ne)

    combined = pd.concat(frames, ignore_index=True)

    # Deduplicate overlapping year records across multi-year ZIP archives (e.g. 2022 in 816517 & 816518)
    dup_subset = ["latitude", "longitude", "acq_date", "acq_time", "satellite"]
    exact_duplicates = int(combined.duplicated(subset=dup_subset).sum())
    if exact_duplicates > 0:
        combined = combined.drop_duplicates(subset=dup_subset, keep="first").reset_index(drop=True)

    # Inspect type and confidence distributions BEFORE any filtering
    type_counts = combined["type"].value_counts(dropna=False).to_dict() if "type" in combined.columns else {}
    conf_counts = combined["confidence"].value_counts(dropna=False).to_dict() if "confidence" in combined.columns else {}
    daynight_counts = combined["daynight"].value_counts(dropna=False).to_dict() if "daynight" in combined.columns else {}
    sat_counts = combined["satellite"].value_counts(dropna=False).to_dict() if "satellite" in combined.columns else {}

    # Flag presumed vegetation fires (type == 0) per VIIRS C2 documentation, while retaining all rows in interim
    combined["is_vegetation_fire"] = combined["type"] == 0

    out_all_path = dirs["interim_firms"] / "firms_ne_india_detections.parquet"
    combined.to_parquet(out_all_path, index=False)

    years_ingested = sorted(int(y) for y in combined["year"].unique())
    metadata = {
        "target_years_requested": target_years,
        "years_ingested": years_ingested,
        "years_missing_in_window": [y for y in target_years if y not in years_ingested],
        "archives_skipped_or_outside": outside_zips,
        "archive_stats": archive_stats,
        "total_ne_detections_after_exact_dedup": int(len(combined)),
        "exact_duplicates_removed_from_overlapping_archives": exact_duplicates,
        "vegetation_fire_count_type_0": int(combined["is_vegetation_fire"].sum()),
        "non_vegetation_fire_count": int((~combined["is_vegetation_fire"]).sum()),
        "type_value_counts": {str(k): int(v) for k, v in type_counts.items()},
        "type_definitions_viirs_c2": VIIRS_TYPE_MEANINGS,
        "confidence_value_counts": {str(k): int(v) for k, v in conf_counts.items()},
        "confidence_definitions_viirs_c2": VIIRS_CONFIDENCE_MEANINGS,
        "daynight_value_counts": {str(k): int(v) for k, v in daynight_counts.items()},
        "satellite_value_counts": {str(k): int(v) for k, v in sat_counts.items()},
        "detections_by_state": {k: int(v) for k, v in combined["state_name"].value_counts().sort_index().items()},
        "detections_by_year": {int(k): int(v) for k, v in combined["year"].value_counts().sort_index().items()},
        "output_parquet": str(out_all_path),
    }

    with (dirs["reports"] / "firms_ingestion_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return combined, metadata


if __name__ == "__main__":
    df_out, meta = ingest_firms()
    print("FIRMS ingestion complete.")
    print("Years ingested:", meta["years_ingested"], "| Missing:", meta["years_missing_in_window"])
    print("Total NE India detections:", meta["total_ne_detections_after_exact_dedup"])
    print("Type counts:", meta["type_value_counts"])
    print("Confidence counts:", meta["confidence_value_counts"])
    print("By state:", meta["detections_by_state"])
