"""Step 8a: NASA COOLR landslide candidate JSON ingestion and spatial/temporal validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
import shapely

from src.config import ensure_project_dirs, load_config


def parse_coolr_timestamp(val: Any) -> pd.Timestamp:
    """Parse ArcGIS epoch milliseconds or ISO date strings safely into UTC-naive Timestamp."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return pd.NaT
    if isinstance(val, (int, float)):
        # ArcGIS FeatureServer timestamps are typically epoch milliseconds
        if abs(val) > 1e11:
            return pd.to_datetime(val, unit="ms", errors="coerce", utc=True).tz_localize(None)
        if abs(val) > 1e8:
            return pd.to_datetime(val, unit="s", errors="coerce", utc=True).tz_localize(None)
        return pd.NaT
    ts = pd.to_datetime(str(val), errors="coerce", utc=True)
    return ts.tz_localize(None) if pd.notna(ts) else pd.NaT


def ingest_coolr(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load COOLR JSON, inspect schema, validate coordinates & dates, filter to NE India."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    json_path = dirs["raw_data_root"] / "COOLR_India_Events.json"
    if not json_path.exists():
        raise FileNotFoundError(f"COOLR JSON not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    features = raw.get("features", [])
    rows: list[dict[str, Any]] = []
    for feat in features:
        attrs = dict(feat.get("attributes", {}))
        geom = feat.get("geometry") or {}
        if "x" in geom and "y" in geom:
            attrs["_geom_x"] = geom["x"]
            attrs["_geom_y"] = geom["y"]
        rows.append(attrs)

    df = pd.DataFrame(rows)
    all_columns = list(df.columns)

    # Detect coordinate columns
    lat_col = next((c for c in df.columns if c.lower() in {"latitude", "lat", "_geom_y"}), None)
    lon_col = next((c for c in df.columns if c.lower() in {"longitude", "lon", "lng", "_geom_x"}), None)
    date_col = next((c for c in df.columns if "event_date" in c.lower() or c.lower() == "date"), None)
    id_col = next((c for c in df.columns if c.lower() in {"event_id", "objectid", "globalid", "id"}), None)

    df["source_event_id"] = df[id_col].astype(str) if id_col else df.index.astype(str)
    df["source_dataset"] = "NASA_COOLR"
    df["latitude"] = pd.to_numeric(df[lat_col], errors="coerce") if lat_col else np.nan
    df["longitude"] = pd.to_numeric(df[lon_col], errors="coerce") if lon_col else np.nan

    # Parse dates cleanly
    if date_col:
        parsed_dt = df[date_col].map(parse_coolr_timestamp)
    else:
        parsed_dt = pd.Series(pd.NaT, index=df.index)
    df["event_datetime"] = parsed_dt
    df["event_date"] = parsed_dt.dt.normalize()
    df["event_year"] = parsed_dt.dt.year

    # Date quality classification
    d_start = pd.Timestamp(cfg["scope"]["date_start"])
    d_end = pd.Timestamp(cfg["scope"]["date_end"])

    def classify_date(dt: pd.Timestamp) -> str:
        if pd.isna(dt):
            return "undated_or_unparseable"
        if d_start <= dt <= d_end:
            return "dated_in_target_2021_2024"
        return "dated_outside_target_window"

    df["date_quality"] = df["event_date"].map(classify_date)
    df["has_valid_coords"] = (
        df["latitude"].notna()
        & df["longitude"].notna()
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    )

    # Save national candidate table
    all_out = dirs["interim_events"] / "coolr_all_india.parquet"
    df.to_parquet(all_out, index=False)

    # Spatial join valid coordinates against NE India study boundaries
    study_states = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")[["state_name", "geometry"]]
    valid_df = df.loc[df["has_valid_coords"]].copy()
    pts = shapely.points(valid_df["longitude"].to_numpy(), valid_df["latitude"].to_numpy())
    pts_gdf = gpd.GeoDataFrame(valid_df, geometry=pts, crs="EPSG:4326")

    ne_gdf = gpd.sjoin(pts_gdf, study_states, how="inner", predicate="within").drop(columns=["index_right"])

    # Assign 1 km grid cell_id if grid exists
    grid_attr_path = dirs["processed_grid"] / "grid_1km_attributes.parquet"
    grid_meta_path = dirs["reports"] / "grid_metadata.json"
    if grid_attr_path.exists() and grid_meta_path.exists() and len(ne_gdf) > 0:
        grid_attr = pd.read_parquet(grid_attr_path)
        with grid_meta_path.open("r", encoding="utf-8") as fh:
            grid_meta = json.load(fh)
        transformer = Transformer.from_crs("EPSG:4326", grid_meta["projected_crs"], always_xy=True)
        xm, ym = transformer.transform(ne_gdf["longitude"].to_numpy(), ne_gdf["latitude"].to_numpy())
        ne_gdf["grid_col"] = np.floor((xm - grid_meta["origin_x_m"]) / grid_meta["cell_size_m"]).astype(np.int32)
        ne_gdf["grid_row"] = np.floor((ym - grid_meta["origin_y_m"]) / grid_meta["cell_size_m"]).astype(np.int32)
        ne_df = pd.DataFrame(ne_gdf.drop(columns=["geometry"])).merge(
            grid_attr[["cell_id", "grid_col", "grid_row"]],
            on=["grid_col", "grid_row"],
            how="left",
        )
    else:
        ne_df = pd.DataFrame(ne_gdf.drop(columns=["geometry"]))
        ne_df["cell_id"] = None

    dup_ids_all = int(df["source_event_id"].duplicated().sum())
    dup_ids_ne = int(ne_df["source_event_id"].duplicated().sum()) if len(ne_df) else 0

    ne_out = dirs["interim_events"] / "coolr_ne_india.parquet"
    ne_csv = dirs["interim_events"] / "coolr_ne_india.csv"
    ne_df.to_parquet(ne_out, index=False)
    ne_df.to_csv(ne_csv, index=False)

    metadata = {
        "source_file": str(json_path),
        "all_columns": all_columns,
        "detected_columns": {"lat": lat_col, "lon": lon_col, "date": date_col, "id": id_col},
        "total_india_candidates": int(len(df)),
        "valid_coord_india_candidates": int(df["has_valid_coords"].sum()),
        "duplicate_source_ids_india": dup_ids_all,
        "date_quality_india": {k: int(v) for k, v in df["date_quality"].value_counts().items()},
        "ne_india_total_events": int(len(ne_df)),
        "duplicate_source_ids_ne": dup_ids_ne,
        "ne_india_by_state": {k: int(v) for k, v in ne_df["state_name"].value_counts().sort_index().items()} if len(ne_df) else {},
        "ne_india_by_date_quality": {k: int(v) for k, v in ne_df["date_quality"].value_counts().items()} if len(ne_df) else {},
        "ne_india_by_year": {int(k): int(v) for k, v in ne_df["event_year"].dropna().value_counts().sort_index().items()} if len(ne_df) else {},
        "ne_india_date_min": str(ne_df["event_date"].min().date()) if len(ne_df) and ne_df["event_date"].notna().any() else None,
        "ne_india_date_max": str(ne_df["event_date"].max().date()) if len(ne_df) and ne_df["event_date"].notna().any() else None,
        "outputs": {"all_india_parquet": str(all_out), "ne_india_parquet": str(ne_out), "ne_india_csv": str(ne_csv)},
    }
    with (dirs["reports"] / "coolr_ingestion_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return ne_df, metadata


if __name__ == "__main__":
    ne_events, meta = ingest_coolr()
    print("COOLR ingestion complete.")
    print("India candidates:", meta["total_india_candidates"], "| NE India events:", meta["ne_india_total_events"])
    print("NE India date quality:", meta["ne_india_by_date_quality"])
    print("NE India by state:", meta["ne_india_by_state"])
    print("NE India by year:", meta["ne_india_by_year"])

