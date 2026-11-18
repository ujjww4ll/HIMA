"""Step 2: Extract, inspect, validate, and filter Northeast India state boundaries."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd

from src.config import ensure_project_dirs, load_config


def extract_boundaries(raw_data_root: Path, interim_boundaries_dir: Path) -> Path:
    """Extract all shapefile components together from boundaries.zip into interim folder."""
    zip_path = raw_data_root / "data" / "raw" / "boundaries.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Boundary archive not found: {zip_path}")

    interim_boundaries_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(interim_boundaries_dir)

    shp_files = list(interim_boundaries_dir.rglob("*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No .shp file found after extracting {zip_path}")

    shp_path = shp_files[0]
    required_exts = [".shp", ".shx", ".dbf", ".prj"]
    missing = [ext for ext in required_exts if not shp_path.with_suffix(ext).exists()]
    if missing:
        raise FileNotFoundError(f"Missing shapefile sidecar files for {shp_path.name}: {missing}")
    return shp_path


# Verified shapefile spelling aliases (state_NWIC.shp spells Arunachal Pradesh as 'Arunanchal Pradesh')
STATE_SPELLING_ALIASES = {
    "arunanchal pradesh": "arunachal pradesh",
}


def find_state_column(gdf: gpd.GeoDataFrame) -> str:
    """Identify the state-name attribute column by inspecting actual columns and values."""
    if "state_name" in gdf.columns:
        return "state_name"
    for col in gdf.columns:
        if col == "geometry":
            continue
        vals = gdf[col].dropna().astype(str).str.lower()
        if vals.str.contains("assam").any() and vals.str.contains("meghalaya").any():
            return col
    raise ValueError(f"Could not detect state name column among columns: {list(gdf.columns)}")


def normalize_name(name: str) -> str:
    norm = " ".join(str(name).strip().lower().split())
    return STATE_SPELLING_ALIASES.get(norm, norm)


def build_study_boundaries(config_path: str | Path | None = None) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    """Extract, validate, filter configured study states, and save GeoPackage + GeoJSON."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    shp_path = extract_boundaries(dirs["raw_data_root"], dirs["interim_boundaries"])
    gdf = gpd.read_file(shp_path)

    original_crs = str(gdf.crs)
    geom_types = gdf.geometry.geom_type.value_counts().to_dict()
    invalid_before = int((~gdf.geometry.is_valid).sum())
    repaired_geoms = False
    if invalid_before > 0:
        gdf["geometry"] = gdf.geometry.make_valid()
        repaired_geoms = True
    invalid_after = int((~gdf.geometry.is_valid).sum())

    state_col = find_state_column(gdf)
    available_states = sorted(gdf[state_col].dropna().astype(str).unique().tolist())

    # Match configured study states cleanly (case/whitespace normalized)
    target_norm = {normalize_name(s): s for s in cfg["scope"]["study_states"]}
    gdf["_norm_state"] = gdf[state_col].astype(str).map(normalize_name)

    matched_mask = gdf["_norm_state"].isin(target_norm.keys())
    study_gdf = gdf.loc[matched_mask].copy()
    matched_norm = set(study_gdf["_norm_state"].unique())
    missing_states = [orig for norm, orig in target_norm.items() if norm not in matched_norm]
    if missing_states:
        raise ValueError(
            f"Configured study states not found in {shp_path.name} ({state_col}): {missing_states}. "
            f"Available states: {available_states}"
        )

    # Standardize state_name column and dissolve multi-part state rows if any
    study_gdf["state_name"] = study_gdf["_norm_state"].map(target_norm)
    study_gdf = study_gdf.drop(columns=["_norm_state"])
    if study_gdf["state_name"].duplicated().any():
        study_gdf = study_gdf.dissolve(by="state_name", as_index=False)

    # Ensure geographic EPSG:4326 for canonical boundary storage
    geo_crs = cfg["geospatial"]["geographic_crs"]
    if str(study_gdf.crs) != geo_crs:
        study_gdf = study_gdf.to_crs(geo_crs)

    # Compute metric areas in projected CRS for documentation
    proj_crs = cfg["geospatial"]["projected_crs"]
    proj_gdf = study_gdf.to_crs(proj_crs)
    study_gdf["area_km2"] = (proj_gdf.geometry.area / 1e6).round(2).values

    # Save processed outputs
    gpkg_path = dirs["processed_boundaries"] / "study_states.gpkg"
    geojson_path = dirs["processed_boundaries"] / "study_states.geojson"
    proj_gpkg_path = dirs["processed_boundaries"] / "study_states_projected.gpkg"

    study_gdf.to_file(gpkg_path, driver="GPKG")
    study_gdf.to_file(geojson_path, driver="GeoJSON")
    proj_gdf.assign(area_km2=study_gdf["area_km2"].values).to_file(proj_gpkg_path, driver="GPKG")

    bounds_4326 = [round(float(x), 5) for x in study_gdf.total_bounds]
    bounds_proj = [round(float(x), 2) for x in proj_gdf.total_bounds]

    metadata = {
        "source_zip": str(dirs["raw_data_root"] / "data" / "raw" / "boundaries.zip"),
        "extracted_shp": str(shp_path),
        "all_columns": [c for c in gdf.columns if c not in {"geometry", "_norm_state"}],
        "detected_state_column": state_col,
        "available_states_count": len(available_states),
        "available_states": available_states,
        "selected_states": sorted(study_gdf["state_name"].tolist()),
        "state_areas_km2": dict(zip(study_gdf["state_name"], study_gdf["area_km2"])),
        "total_area_km2": round(float(study_gdf["area_km2"].sum()), 2),
        "original_crs": original_crs,
        "saved_geographic_crs": str(study_gdf.crs),
        "projected_crs": proj_crs,
        "projected_crs_reason": cfg["geospatial"]["projected_crs_reason"],
        "geometry_types_raw": geom_types,
        "invalid_geometries_before": invalid_before,
        "geometries_repaired": repaired_geoms,
        "invalid_geometries_after": invalid_after,
        "bounds_epsg4326_minx_miny_maxx_maxy": bounds_4326,
        "bounds_projected_m": bounds_proj,
        "outputs": {
            "gpkg": str(gpkg_path),
            "geojson": str(geojson_path),
            "projected_gpkg": str(proj_gpkg_path),
        },
    }

    meta_path = dirs["reports"] / "boundaries_metadata.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return study_gdf, metadata


if __name__ == "__main__":
    gdf_out, meta = build_study_boundaries()
    print("Boundaries validated and saved.")
    print("Detected state column:", meta["detected_state_column"])
    print("Original CRS:", meta["original_crs"])
    print("Selected states:", meta["selected_states"])
    print("Total area (km2):", meta["total_area_km2"])
    print("Invalid geometries repaired:", meta["invalid_geometries_before"], "->", meta["invalid_geometries_after"])
