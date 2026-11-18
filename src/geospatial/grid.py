"""Step 4: Build a projected 1 km x 1 km fishnet grid over Northeast India."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import Transformer
import shapely

from src.config import ensure_project_dirs, load_config


def build_1km_grid(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build 1,000 m x 1,000 m fishnet grid in metric CRS, clipped to study boundaries.

    Edge policy ('centroid_within'): keep every 1 km square whose centroid lies inside a
    configured study state polygon. This guarantees every cell has a unique state assignment
    and no cell centroid falls outside the study boundaries.
    """
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    proj_crs = cfg["geospatial"]["projected_crs"]
    geo_crs = cfg["geospatial"]["geographic_crs"]
    cell_size = int(cfg["geospatial"]["grid_cell_size_m"])

    proj_boundary_path = dirs["processed_boundaries"] / "study_states_projected.gpkg"
    if not proj_boundary_path.exists():
        raise FileNotFoundError(
            f"Projected boundary file not found: {proj_boundary_path}. Run boundaries.py first."
        )

    states_proj = gpd.read_file(proj_boundary_path)[["state_name", "geometry"]]
    if str(states_proj.crs) != proj_crs:
        states_proj = states_proj.to_crs(proj_crs)

    minx, miny, maxx, maxy = states_proj.total_bounds
    origin_x = math.floor(minx / cell_size) * cell_size
    origin_y = math.floor(miny / cell_size) * cell_size
    end_x = math.ceil(maxx / cell_size) * cell_size
    end_y = math.ceil(maxy / cell_size) * cell_size

    xs = np.arange(origin_x + cell_size / 2.0, end_x, cell_size, dtype=np.float64)
    ys = np.arange(origin_y + cell_size / 2.0, end_y, cell_size, dtype=np.float64)
    ncols = len(xs)
    nrows = len(ys)

    xx, yy = np.meshgrid(xs, ys)
    cols_idx, rows_idx = np.meshgrid(np.arange(ncols, dtype=np.int32), np.arange(nrows, dtype=np.int32))

    flat_x = xx.ravel()
    flat_y = yy.ravel()
    flat_c = cols_idx.ravel()
    flat_r = rows_idx.ravel()

    # Vectorized point creation and spatial join to keep only cells inside study states
    pts = shapely.points(flat_x, flat_y)
    pts_gdf = gpd.GeoDataFrame(
        {"grid_col": flat_c, "grid_row": flat_r, "x_m": flat_x, "y_m": flat_y},
        geometry=pts,
        crs=proj_crs,
    )

    joined = gpd.sjoin(pts_gdf, states_proj, how="inner", predicate="within")
    joined = joined.drop(columns=["index_right"])
    # Deduplicate in rare case a centroid falls exactly on a shared state border
    joined = joined.drop_duplicates(subset=["grid_col", "grid_row"], keep="first").reset_index(drop=True)

    # Sort deterministically and assign stable cell_id
    joined = joined.sort_values(["grid_row", "grid_col"]).reset_index(drop=True)
    joined["cell_id"] = [
        f"NE_{c:04d}_{r:04d}" for c, r in zip(joined["grid_col"].to_numpy(), joined["grid_row"].to_numpy())
    ]

    # Compute WGS84 centroid coordinates
    transformer = Transformer.from_crs(proj_crs, geo_crs, always_xy=True)
    lon, lat = transformer.transform(joined["x_m"].to_numpy(), joined["y_m"].to_numpy())
    joined["centroid_lon"] = np.round(lon, 6)
    joined["centroid_lat"] = np.round(lat, 6)

    # Verify zero cells lie outside study boundary
    union_geom = states_proj.geometry.union_all()
    outside_count = int((~shapely.within(joined.geometry.to_numpy(), union_geom)).sum())
    if outside_count > 0:
        raise RuntimeError(f"Grid validation failed: {outside_count} cell centroids fall outside boundary.")

    # Save lightweight columnar attributes table (GeoParquet-style attributes)
    attr_cols = ["cell_id", "grid_col", "grid_row", "x_m", "y_m", "centroid_lon", "centroid_lat", "state_name"]
    attr_df = joined[attr_cols].copy()
    attr_parquet_path = dirs["processed_grid"] / "grid_1km_attributes.parquet"
    attr_df.to_parquet(attr_parquet_path, index=False)

    # Construct 1 km x 1 km polygons and save as GeoPackage
    half = cell_size / 2.0
    boxes = shapely.box(
        joined["x_m"].to_numpy() - half,
        joined["y_m"].to_numpy() - half,
        joined["x_m"].to_numpy() + half,
        joined["y_m"].to_numpy() + half,
    )
    grid_gdf = gpd.GeoDataFrame(attr_df, geometry=boxes, crs=proj_crs)
    grid_gpkg_path = dirs["processed_grid"] / "grid_1km.gpkg"
    grid_gdf.to_file(grid_gpkg_path, driver="GPKG")

    # Save metadata
    cells_per_state = attr_df["state_name"].value_counts().sort_index().to_dict()
    metadata = {
        "projected_crs": proj_crs,
        "geographic_crs": geo_crs,
        "cell_size_m": cell_size,
        "edge_cell_policy": cfg["geospatial"]["edge_cell_policy"],
        "origin_x_m": origin_x,
        "origin_y_m": origin_y,
        "bbox_cols": ncols,
        "bbox_rows": nrows,
        "total_cells": int(len(attr_df)),
        "cells_outside_boundary": outside_count,
        "cells_per_state": {k: int(v) for k, v in cells_per_state.items()},
        "resolution_limitation_note": (
            "1 km grid is the unified analytical frame; coarser ERA5 (~9-11 km) and IMD (~25 km) "
            "weather inputs do not gain 1 km physical resolution through spatial joining."
        ),
        "outputs": {
            "attributes_parquet": str(attr_parquet_path),
            "grid_gpkg": str(grid_gpkg_path),
        },
    }
    meta_path = dirs["reports"] / "grid_metadata.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    # Generate verification map (Northeast India boundaries + zoomed 1 km grid inset)
    plot_study_area_and_grid(states_proj, grid_gdf, dirs["outputs_maps"] / "study_area_and_grid.png", metadata)

    return attr_df, metadata


def plot_study_area_and_grid(
    states_proj: gpd.GeoDataFrame,
    grid_gdf: gpd.GeoDataFrame,
    out_path: Path,
    metadata: dict[str, Any],
) -> None:
    """Plot study-area states map alongside a 20 km x 20 km zoomed 1 km fishnet grid check."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), dpi=150)

    # Panel 1: All 8 Northeast India states in projected CRS
    states_proj.plot(
        column="state_name",
        ax=ax1,
        cmap="Set3",
        edgecolor="#222222",
        linewidth=0.9,
        legend=True,
        legend_kwds={"loc": "lower left", "fontsize": 8, "framealpha": 0.9},
    )
    ax1.set_title(
        f"HIMA Study Region: Northeast India ({metadata['total_cells']:,} × 1 km cells)\n"
        f"CRS: {metadata['projected_crs']} (metres)",
        fontsize=11,
        fontweight="bold",
    )
    ax1.set_xlabel("Easting (m)")
    ax1.set_ylabel("Northing (m)")
    ax1.grid(True, linestyle="--", alpha=0.35)

    # Pick a representative 20 km x 20 km window around Guwahati / central Assam for zoomed grid check
    assam = states_proj[states_proj["state_name"] == "Assam"]
    center_pt = assam.geometry.centroid.iloc[0] if len(assam) else states_proj.geometry.centroid.iloc[0]
    cx, cy = center_pt.x, center_pt.y
    half_win = 10_000  # 20 km x 20 km box

    # Highlight zoom window on Panel 1
    zoom_box = shapely.box(cx - half_win, cy - half_win, cx + half_win, cy + half_win)
    gpd.GeoSeries([zoom_box], crs=states_proj.crs).boundary.plot(ax=ax1, color="red", linewidth=1.8)

    # Panel 2: Zoomed 1 km fishnet grid cells
    zoom_cells = grid_gdf.cx[cx - half_win : cx + half_win, cy - half_win : cy + half_win]
    zoom_cells.plot(ax=ax2, facecolor="#d9edf7", edgecolor="#2b5c8f", linewidth=0.5, alpha=0.8)
    states_proj.boundary.plot(ax=ax2, color="#111111", linewidth=1.2)
    ax2.set_xlim(cx - half_win, cx + half_win)
    ax2.set_ylim(cy - half_win, cy + half_win)
    ax2.set_title(
        f"Zoomed 20 km × 20 km Fishnet Check ({len(zoom_cells)} cells shown)\n"
        f"Cell size: 1,000 m × 1,000 m | Edge policy: {metadata['edge_cell_policy']}",
        fontsize=11,
        fontweight="bold",
    )
    ax2.set_xlabel("Easting (m)")
    ax2.set_ylabel("Northing (m)")
    ax2.grid(True, linestyle=":", alpha=0.4)

    fig.suptitle(
        "HIMA Geospatial Frame Verification — Research Demo Only",
        fontsize=12,
        y=0.99,
    )
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    df, meta = build_1km_grid()
    print(f"Grid generated: {meta['total_cells']:,} cells across {len(meta['cells_per_state'])} states.")
    for st, cnt in meta["cells_per_state"].items():
        print(f"  {st}: {cnt:,} cells")

