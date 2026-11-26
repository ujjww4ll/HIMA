"""Flood data ingestion — INDOFLOODS dataset (IndoFloods Integrated + CHIRPS rainfall).

Reads from data/raw/flood/:
  - indofloods_integrated.csv  → 4,548 flood events with 148 features (master dataset)
  - precipitation_variables_indofloods.csv → T1d–T10d antecedent rainfall (already embedded)
  - chirps_rainfall_all.csv    → 1.3M daily gauge rainfall records 1998–2020 (time series)

Produces:
  - data/processed/labels/flood.parquet    → clean event table with NE India flag
  - data/reports/flood_ingestion_metadata.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import ensure_project_dirs, load_config

# Northeast India states (must match grid scope)
NE_INDIA_STATES = {
    "Arunachal Pradesh", "Assam", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Tripura", "Sikkim",
}

# Columns to keep from indofloods_integrated for ML
FLOOD_EVENT_COLS = [
    "EventID", "GaugeID", "Station", "State", "Latitude", "Longitude",
    "Start Date", "End Date", "Event Duration (days)", "Peak Flood Level (m)",
    "Peak Discharge Q (cumec)", "Flood Volume (cumec)", "Flood Type",
    "Warning Level", "Danger Level", "Time to Peak (days)",
    # Antecedent CHIRPS rainfall lags (T1d = cumulative rainfall 1 day before peak)
    "T1d", "T2d", "T3d", "T4d", "T5d", "T6d", "T7d", "T8d", "T9d", "T10d",
    # Catchment characteristics
    "Catchment Area", "Stream Order", "Soil type", "lithology type",
    "Land cover", "Population Density", "Urban percentage",
]


def ingest_flood_dataset(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and clean INDOFLOODS dataset; flag Northeast India records.

    Returns:
        (df_events, metadata_dict)
    """
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    flood_raw = Path("data/raw/flood")
    if not flood_raw.exists():
        flood_raw = dirs["raw_data_root"] / "data" / "raw" / "flood"

    integrated_path = flood_raw / "indofloods_integrated.csv"
    chirps_path = flood_raw / "chirps_rainfall_all.csv"

    if not integrated_path.exists():
        raise FileNotFoundError(
            f"INDOFLOODS master file not found: {integrated_path}. "
            "Copy it to data/raw/flood/indofloods_integrated.csv"
        )

    # ── Load master event table ────────────────────────────────────────────────
    print("[Flood Ingestion] Loading indofloods_integrated.csv ...")
    df_all = pd.read_csv(integrated_path, low_memory=False)
    print(f"  Loaded {len(df_all):,} flood events, {len(df_all.columns)} columns")

    # Keep only columns we need
    keep = [c for c in FLOOD_EVENT_COLS if c in df_all.columns]
    df = df_all[keep].copy()

    # Normalize column names for downstream use
    df.rename(columns={
        "Start Date":            "start_date",
        "End Date":              "end_date",
        "Event Duration (days)": "event_duration_days",
        "Peak Flood Level (m)":  "peak_flood_level_m",
        "Peak Discharge Q (cumec)": "peak_discharge_cumec",
        "Flood Volume (cumec)":  "flood_volume_cumec",
        "Flood Type":            "flood_type",
        "Warning Level":         "warning_level",
        "Danger Level":          "danger_level",
        "Time to Peak (days)":   "time_to_peak_days",
        "Catchment Area":        "catchment_area_km2",
        "Stream Order":          "stream_order",
        "Soil type":             "soil_type",
        "lithology type":        "lithology_type",
        "Land cover":            "land_cover",
        "Population Density":    "population_density",
        "Urban percentage":      "urban_pct",
    }, inplace=True)

    # Parse dates
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["peak_date"] = df["start_date"] + pd.to_timedelta(
        df["time_to_peak_days"].fillna(0).clip(lower=0), unit="D"
    )
    df["year"] = df["start_date"].dt.year.astype("Int32")

    # Flag NE India records
    df["in_ne_india"] = df["State"].isin(NE_INDIA_STATES)
    n_ne = int(df["in_ne_india"].sum())

    # Flood severity label: 1 if peak_discharge_cumec exceeds danger level
    # (safe proxy when both columns are available)
    df["exceeds_danger_level"] = (
        df["peak_discharge_cumec"].notna()
        & df["danger_level"].notna()
        & (df["peak_discharge_cumec"] >= df["danger_level"])
    ).astype(np.int8)

    # ── CHIRPS daily rainfall summary ─────────────────────────────────────────
    chirps_meta: dict[str, Any] = {}
    if chirps_path.exists():
        print("[Flood Ingestion] Scanning chirps_rainfall_all.csv ...")
        total_rows, unique_gauges = 0, set()
        d_min: str | None = None
        d_max: str | None = None
        for chunk in pd.read_csv(chirps_path, chunksize=200_000):
            total_rows += len(chunk)
            unique_gauges.update(chunk["GaugeID"].unique())
            cmin = chunk["date"].min()
            cmax = chunk["date"].max()
            d_min = cmin if d_min is None else min(d_min, cmin)
            d_max = cmax if d_max is None else max(d_max, cmax)
        chirps_meta = {
            "total_rows": total_rows,
            "unique_gauges": len(unique_gauges),
            "date_range": [d_min, d_max],
        }
        print(f"  CHIRPS: {total_rows:,} rows · {len(unique_gauges)} gauges · {d_min} → {d_max}")

    # ── Save processed table ───────────────────────────────────────────────────
    out_path = dirs["processed_labels"].parent / "flood.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[Flood Ingestion] Saved → {out_path}")

    # ── Metadata report ────────────────────────────────────────────────────────
    state_counts = df["State"].value_counts().head(15).to_dict()
    ne_state_counts = df[df["in_ne_india"]]["State"].value_counts().to_dict()

    metadata: dict[str, Any] = {
        "source_file": str(integrated_path),
        "total_events": int(len(df)),
        "ne_india_events": n_ne,
        "all_india_events": int(len(df)),
        "date_range": {
            "earliest": str(df["start_date"].min().date()) if df["start_date"].notna().any() else None,
            "latest":   str(df["start_date"].max().date()) if df["start_date"].notna().any() else None,
        },
        "top_15_states_by_events": state_counts,
        "ne_india_state_breakdown": ne_state_counts,
        "exceeds_danger_level_all_india": int(df["exceeds_danger_level"].sum()),
        "exceeds_danger_level_ne_india":  int(df[df["in_ne_india"]]["exceeds_danger_level"].sum()),
        "flood_types": df["flood_type"].value_counts().to_dict() if "flood_type" in df.columns else {},
        "features_kept": keep,
        "chirps_summary": chirps_meta,
        "output_parquet": str(out_path),
        "note": (
            "IndoFloods covers all-India gauged rivers 1965–2020. "
            "NE India records are limited (Assam/Manipur) due to sparse gauge networks. "
            "CHIRPS satellite rainfall fills spatial gaps for antecedent rainfall features."
        ),
    }

    report_path = dirs["reports"] / "flood_ingestion_metadata.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, default=str)
    print(f"[Flood Ingestion] Metadata report → {report_path}")

    return df, metadata


if __name__ == "__main__":
    df_out, meta = ingest_flood_dataset()
    print(f"\nFlood ingestion complete: {len(df_out):,} events saved.")
    print(f"NE India events: {meta['ne_india_events']} | Total India: {meta['total_events']}")
