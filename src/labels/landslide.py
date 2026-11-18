"""Step 8c/9: Landslide inventory integration (COOLR + GSI PDF) & preliminary modeling dataset builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pyproj import Transformer

from src.config import ensure_project_dirs, load_config
from src.labels.wildfire import assign_imd_season, sample_uniform_celldays


def build_landslide_dataset(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Integrate COOLR & GSI NE India records, attach weather features, and build preliminary ML table.

    Strictly enforces:
      - Undated or outside-window records NEVER become 2021-2024 daily positive labels.
      - Clearly labels the daily modeling table as PRELIMINARY (weather-only, missing DEM/slope/soil/geology).
    """
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    rng = np.random.default_rng(int(cfg["project"]["random_state"]))

    coolr_ne_path = dirs["interim_events"] / "coolr_ne_india.parquet"
    coolr_all_path = dirs["interim_events"] / "coolr_all_india.parquet"
    gsi_path = dirs["interim_events"] / "gsi_ne_india_extracted.parquet"

    coolr_ne = pd.read_parquet(coolr_ne_path) if coolr_ne_path.exists() else pd.DataFrame()
    coolr_all_n = len(pd.read_parquet(coolr_all_path)) if coolr_all_path.exists() else 0
    gsi_ne = pd.read_parquet(gsi_path) if gsi_path.exists() else pd.DataFrame()

    grid_df = pd.read_parquet(dirs["processed_grid"] / "grid_1km_with_weather_keys.parquet")
    with (dirs["reports"] / "grid_metadata.json").open("r", encoding="utf-8") as fh:
        grid_meta = json.load(fh)
    era5_feat = pd.read_parquet(dirs["processed_weather"] / "era5_features_daily.parquet")
    imd_feat = pd.read_parquet(dirs["processed_weather"] / "imd_features_daily.parquet")

    parts: list[pd.DataFrame] = []

    if len(coolr_ne) > 0:
        c = pd.DataFrame(
            {
                "source_dataset": "NASA_COOLR",
                "source_event_id": coolr_ne["source_event_id"].astype(str),
                "source_page": np.nan,
                "state_name": coolr_ne.get("state_name"),
                "district": None,
                "location_name": coolr_ne.get("location_description"),
                "latitude": coolr_ne["latitude"],
                "longitude": coolr_ne["longitude"],
                "event_date": pd.to_datetime(coolr_ne["event_date"]),
                "date_quality": coolr_ne["date_quality"],
                "movement_type": coolr_ne.get("landslide_category"),
                "material_involved": None,
                "within_study_boundary": True,
                "is_eligible_daily_label": coolr_ne["date_quality"] == "dated_in_target_2021_2024",
            }
        )
        parts.append(c)

    if len(gsi_ne) > 0:
        gsi_in = gsi_ne[gsi_ne["within_study_boundary"]].copy()
        parsed_dt = pd.to_datetime(gsi_in["parsed_event_date"], errors="coerce").dt.normalize()
        d_start = pd.Timestamp(cfg["scope"]["date_start"])
        d_end = pd.Timestamp(cfg["scope"]["date_end"])

        def gsi_dq(dt: pd.Timestamp) -> str:
            if pd.isna(dt):
                return "undated_field_validated_location"
            if d_start <= dt <= d_end:
                return "dated_in_target_2021_2024"
            return "dated_outside_target_window"

        dq_series = parsed_dt.map(gsi_dq)
        g = pd.DataFrame(
            {
                "source_dataset": "GSI_FIELD_VALIDATED_PDF",
                "source_event_id": gsi_in["source_event_id"].astype(str),
                "source_page": gsi_in["source_page"],
                "state_name": gsi_in["state_name"],
                "district": gsi_in["district"],
                "location_name": gsi_in["slide_name"].where(gsi_in["slide_name"] != "", gsi_in["nh_sh_location"]),
                "latitude": gsi_in["latitude"],
                "longitude": gsi_in["longitude"],
                "event_date": parsed_dt,
                "date_quality": dq_series,
                "movement_type": gsi_in["movement_type"],
                "material_involved": gsi_in["material_involved"],
                "within_study_boundary": True,
                "is_eligible_daily_label": dq_series == "dated_in_target_2021_2024",
            }
        )
        parts.append(g)

    df = pd.concat(parts, ignore_index=True)

    # Map every NE India landslide point onto the 1 km projected fishnet grid
    transformer = Transformer.from_crs(grid_meta["geographic_crs"], grid_meta["projected_crs"], always_xy=True)
    xm, ym = transformer.transform(df["longitude"].to_numpy(), df["latitude"].to_numpy())
    df["grid_col"] = np.floor((xm - grid_meta["origin_x_m"]) / grid_meta["cell_size_m"]).astype(np.int32)
    df["grid_row"] = np.floor((ym - grid_meta["origin_y_m"]) / grid_meta["cell_size_m"]).astype(np.int32)
    df = df.merge(
        grid_df[["cell_id", "grid_col", "grid_row", "era5_grid_id", "imd_grid_id"]],
        on=["grid_col", "grid_row"],
        how="left",
    )

    # Attach weather context for dated 2021-2024 events
    df["date"] = df["event_date"]
    df = df.merge(imd_feat, on=["imd_grid_id", "date"], how="left")
    df = df.merge(era5_feat, on=["era5_grid_id", "date"], how="left")

    out_inv_parquet = dirs["processed_labels"].parent / "landslide.parquet"
    df.to_parquet(out_inv_parquet, index=False)

    # Deduplicate dated 2021-2024 events to unique (cell_id, date) positive cell-days
    dated_valid = df[df["is_eligible_daily_label"] & df["cell_id"].notna()].copy()
    pos_cd = (
        dated_valid.groupby(["cell_id", "date"], as_index=False)
        .agg(
            event_count=("source_event_id", "size"),
            source_event_id=("source_event_id", "first"),
            source_dataset=("source_dataset", "first"),
        )
    )
    pos_cd["landslide_detected"] = np.int8(1)
    pos_cd["label_source"] = "gsi_field_validated_dated_2021_2024"
    pos_cd["year"] = pos_cd["date"].dt.year.astype(np.int32)

    min_needed = int(cfg["landslide"]["min_dated_events_for_daily_model"])
    n_dated_rows = int(len(dated_valid))
    n_unique_pos_cd = int(len(pos_cd))

    modeling_meta: dict[str, Any] = {}
    if n_unique_pos_cd >= min_needed:
        cell_ids = grid_df["cell_id"].to_numpy()
        train_years = [2021, 2022, 2023]
        test_years = [2024]

        train_pos = pos_cd[pos_cd["year"].isin(train_years)].copy()
        test_pos = pos_cd[pos_cd["year"].isin(test_years)].copy()

        # Train negatives: 25:1 uniform random background across 2021-2023 NE India cell-days
        train_dates = pd.DatetimeIndex(
            np.concatenate([pd.date_range(f"{y}-01-01", f"{y}-12-31", freq="D").values for y in train_years])
        )
        train_pos_keys = set(zip(train_pos["cell_id"], train_pos["date"]))
        n_train_neg = max(len(train_pos) * 25, 10_000)
        train_neg = sample_uniform_celldays(cell_ids, train_dates, n_train_neg, rng, exclude_keys=train_pos_keys)
        train_neg["event_count"] = np.int32(0)
        train_neg["source_event_id"] = None
        train_neg["source_dataset"] = "HIMA_GRID_BACKGROUND"
        train_neg["landslide_detected"] = np.int8(0)
        train_neg["label_source"] = "observed_no_record_sampled"
        train_neg["year"] = train_neg["date"].dt.year.astype(np.int32)

        train_df = pd.concat([train_pos, train_neg], ignore_index=True)
        train_df["split"] = "train"

        # Test negatives: 100,000 uniform background 2024 cell-days + ALL 2024 positive cell-days
        test_dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
        test_pos_keys = set(zip(test_pos["cell_id"], test_pos["date"]))
        test_neg = sample_uniform_celldays(cell_ids, test_dates, 100_000, rng, exclude_keys=test_pos_keys)
        test_neg["event_count"] = np.int32(0)
        test_neg["source_event_id"] = None
        test_neg["source_dataset"] = "HIMA_GRID_BACKGROUND"
        test_neg["landslide_detected"] = np.int8(0)
        test_neg["label_source"] = "observed_no_record_background_test"
        test_neg["year"] = np.int32(2024)

        test_df = pd.concat([test_pos, test_neg], ignore_index=True)
        test_df["split"] = "test_2024"

        mod_df = pd.concat([train_df, test_df], ignore_index=True)
        mod_df = mod_df.merge(
            grid_df[["cell_id", "x_m", "y_m", "centroid_lat", "centroid_lon", "state_name", "era5_grid_id", "imd_grid_id"]],
            on="cell_id",
            how="left",
        )
        bx = np.floor(mod_df["x_m"].to_numpy() / 50_000.0).astype(np.int32)
        by = np.floor(mod_df["y_m"].to_numpy() / 50_000.0).astype(np.int32)
        mod_df["spatial_block_id"] = [f"B_{x}_{y}" for x, y in zip(bx, by)]
        mod_df["month"] = mod_df["date"].dt.month.astype(np.int8)
        mod_df["day_of_year"] = mod_df["date"].dt.day_of_year.astype(np.int16)
        mod_df["sin_doy"] = np.sin(2.0 * np.pi * mod_df["day_of_year"] / 365.25).astype(np.float32)
        mod_df["cos_doy"] = np.cos(2.0 * np.pi * mod_df["day_of_year"] / 365.25).astype(np.float32)
        mod_df["season"] = assign_imd_season(mod_df["month"])

        mod_df = mod_df.merge(imd_feat, on=["imd_grid_id", "date"], how="left")
        mod_df = mod_df.merge(era5_feat, on=["era5_grid_id", "date"], how="left")

        mod_out_path = dirs["processed_labels"].parent / "landslide_modeling.parquet"
        mod_df.to_parquet(mod_out_path, index=False)
        modeling_meta = {
            "modeling_parquet": str(mod_out_path),
            "train_rows": int(len(train_df)),
            "train_positives_celldays": int(len(train_pos)),
            "test_rows": int(len(test_df)),
            "test_positives_celldays": int(len(test_pos)),
            "positive_celldays_by_year": {int(k): int(v) for k, v in pos_cd["year"].value_counts().sort_index().items()},
        }

    missing_terrain = [
        "SRTM / Copernicus DEM (elevation, slope, aspect)",
        "ESA WorldCover (land cover)",
        "SoilGrids (soil properties)",
        "Geology / lithology",
    ]
    can_train = n_unique_pos_cd >= min_needed

    feasibility = {
        "inventory_parquet": str(out_inv_parquet),
        "coolr_india_candidates": int(coolr_all_n),
        "coolr_ne_india_events": int(len(coolr_ne)),
        "coolr_note": "All 176 COOLR India records lie in Uttarakhand & Himachal Pradesh; 0 in Northeast India.",
        "gsi_ne_india_within_study_boundary": int((df["source_dataset"] == "GSI_FIELD_VALIDATED_PDF").sum()),
        "date_quality_breakdown": {k: int(v) for k, v in df["date_quality"].value_counts().items()},
        "dated_events_2021_2024_raw": n_dated_rows,
        "dated_unique_celldays_2021_2024": n_unique_pos_cd,
        "min_dated_events_threshold": min_needed,
        "missing_static_terrain_layers": missing_terrain,
        "daily_classifier_defensible_preliminary": can_train,
        "decision": "TRAIN_PRELIMINARY_WEATHER_ONLY_WITH_TERRAIN_CAVEATS" if can_train else "EDA_ONLY",
        "caveats": [
            "Static terrain layers (DEM/slope/aspect, WorldCover, SoilGrids, geology) are missing locally; this is strictly a preliminary weather/antecedent-rainfall trigger classifier.",
            "Strong survey/reporting bias exists: 529/673 dated 2021-2024 records come from Mizoram's 2024 field surveys (e.g. Cyclone Remal), while 9,297 other GSI field slides have no exact occurrence date.",
            "Undated GSI slides are strictly excluded from daily labels and used only for spatial inventory mapping.",
        ],
        "modeling_dataset": modeling_meta,
    }
    with (dirs["reports"] / "landslide_feasibility.json").open("w", encoding="utf-8") as fh:
        json.dump(feasibility, fh, indent=2)

    return df, feasibility


if __name__ == "__main__":
    df_out, feas = build_landslide_dataset()
    print("Landslide dataset & feasibility assessment complete.")
    print(json.dumps(feas, indent=2))
