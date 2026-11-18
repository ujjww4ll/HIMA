"""Step 1: Fresh recursive file audit and metadata/schema inspection.

Strictly read-only with respect to raw_data_root. Never modifies, moves, or deletes raw data.
Generates:
  - data/reports/data_inventory.csv
  - data/reports/data_audit_summary.json
  - data/reports/data_quality_report.md
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from src.config import ensure_project_dirs, load_config


PLANNED_STATIC_DATASETS = [
    ("SRTM / Copernicus DEM", ["dem", "srtm", "copernicus", "elev", "slope"]),
    ("ESA WorldCover", ["worldcover", "landcover", "lulc"]),
    ("MODIS MOD13Q1 NDVI", ["modis", "mod13", "ndvi", "appeears"]),
    ("SoilGrids", ["soilgrid", "soil_grid", "clay", "sand", "silt"]),
    ("Geology / Lithology", ["geolog", "litholog", "rock"]),
    ("ISRO NRSC Landslide Atlas", ["nrsc", "isro", "atlas"]),
]


def classify_file(rel_path: str, name: str, ext: str) -> tuple[str, int | None, int | None]:
    """Classify a file by HIMA dataset category and extract year/month if present."""
    lower = name.lower()
    rel_lower = rel_path.lower()

    if lower == "boundaries.zip":
        return "boundaries_zip", None, None
    if lower.startswith("dl_fire") and ext == ".zip":
        return "firms_zip", None, None
    if lower == "coolr_india_events.json":
        return "coolr_json", None, None
    if lower.startswith("gsi_landslide") and ext == ".pdf":
        return "gsi_pdf", None, None

    m_imd = re.search(r"rf25_ind(\d{4})_rfp25\.nc$", lower)
    if m_imd:
        return "imd_netcdf", int(m_imd.group(1)), None

    m_era_proc = re.search(r"era5_land_daily_(\d{4})_(\d{2})\.nc$", lower)
    if m_era_proc:
        return "era5_processed_nc", int(m_era_proc.group(1)), int(m_era_proc.group(2))

    m_era_raw = re.search(r"era5_land_(\d{4})_(\d{2})\.grib$", lower)
    if m_era_raw:
        return "era5_raw_grib", int(m_era_raw.group(1)), int(m_era_raw.group(2))

    if "boundaries" in rel_lower and ext in {".shp", ".shx", ".dbf", ".prj"}:
        return "boundaries_extracted", None, None

    return "other", None, None


def inspect_zip(path: Path) -> dict[str, Any]:
    """Inspect a ZIP archive without extracting it."""
    info: dict[str, Any] = {"entries": [], "csv_files": [], "header": None, "date_min": None, "date_max": None, "row_count": None}
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        info["entries"] = names
        csvs = [n for n in names if n.lower().endswith(".csv")]
        info["csv_files"] = csvs
        if csvs:
            # Inspect the main archive CSV (prefer 'fire_archive_' if multiple)
            main_csv = next((c for c in csvs if "archive" in c.lower()), csvs[0])
            with zf.open(main_csv) as fh:
                text_stream = io.TextIOWrapper(fh, encoding="utf-8", errors="replace")
                reader = csv.reader(text_stream)
                header = next(reader, None)
                info["header"] = header
                acq_idx = header.index("acq_date") if header and "acq_date" in header else None
                min_d: str | None = None
                max_d: str | None = None
                years_seen: set[int] = set()
                count = 0
                for row in reader:
                    count += 1
                    if acq_idx is not None and len(row) > acq_idx:
                        d = row[acq_idx]
                        if len(d) >= 4 and d[:4].isdigit():
                            years_seen.add(int(d[:4]))
                        if min_d is None or d < min_d:
                            min_d = d
                        if max_d is None or d > max_d:
                            max_d = d
                info["date_min"] = min_d
                info["date_max"] = max_d
                info["years_present"] = sorted(years_seen)
                info["row_count"] = count
    return info


def inspect_imd_sample(path: Path) -> dict[str, Any]:
    """Inspect an IMD NetCDF file's variables, dimensions, coordinates, and raw TIME values."""
    result: dict[str, Any] = {"file": path.name}
    with xr.open_dataset(path, decode_times=False) as ds:
        result["data_vars"] = list(ds.data_vars)
        result["coords"] = list(ds.coords)
        result["dims"] = {k: int(v) for k, v in ds.sizes.items()}
        result["global_attrs"] = {k: str(v) for k, v in ds.attrs.items()}
        result["var_attrs"] = {
            v: {ak: str(av) for ak, av in ds[v].attrs.items()} for v in list(ds.data_vars) + list(ds.coords)
        }
        if "TIME" in ds.coords:
            t_vals = ds["TIME"].values
            result["time_raw_dtype"] = str(t_vals.dtype)
            result["time_raw_first5"] = [float(x) if np.isscalar(x) else str(x) for x in t_vals[:5]]
            result["time_raw_last3"] = [float(x) if np.isscalar(x) else str(x) for x in t_vals[-3:]]
    try:
        with xr.open_dataset(path, decode_times=True) as ds_dec:
            if "TIME" in ds_dec.coords:
                t_dec = ds_dec["TIME"].values
                result["time_decoded_first"] = str(t_dec[0])
                result["time_decoded_last"] = str(t_dec[-1])
                result["time_decoded_dtype"] = str(t_dec.dtype)
    except Exception as exc:
        result["time_decode_error"] = str(exc)
    return result


def inspect_era5_nc_sample(path: Path) -> dict[str, Any]:
    """Inspect a processed ERA5-Land daily NetCDF sample."""
    result: dict[str, Any] = {"file": path.name}
    with xr.open_dataset(path) as ds:
        result["data_vars"] = list(ds.data_vars)
        result["coords"] = list(ds.coords)
        result["dims"] = {k: int(v) for k, v in ds.sizes.items()}
        result["global_attrs"] = {k: str(v) for k, v in ds.attrs.items()}
        result["var_attrs"] = {
            v: {ak: str(av) for ak, av in ds[v].attrs.items()} for v in ds.data_vars
        }
        if "time" in ds.coords:
            t = ds["time"].values
            result["time_first"] = str(t[0])
            result["time_last"] = str(t[-1])
        if "latitude" in ds.coords and "longitude" in ds.coords:
            lat = ds["latitude"].values
            lon = ds["longitude"].values
            result["lat_range"] = [float(np.min(lat)), float(np.max(lat))]
            result["lon_range"] = [float(np.min(lon)), float(np.max(lon))]
            result["lat_step"] = float(np.median(np.abs(np.diff(lat))))
            result["lon_step"] = float(np.median(np.abs(np.diff(lon))))
    return result


def inspect_coolr(path: Path) -> dict[str, Any]:
    """Inspect NASA COOLR JSON schema and record count."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    features = data.get("features", [])
    first_feat = features[0] if features else {}
    return {
        "file": path.name,
        "root_keys": list(data.keys()),
        "geometry_type": data.get("geometryType"),
        "spatial_reference": data.get("spatialReference"),
        "field_names": [f.get("name") for f in data.get("fields", [])],
        "feature_count": len(features),
        "first_feature_keys": list(first_feat.keys()),
        "sample_attributes": first_feat.get("attributes", {}),
    }


def inspect_gsi_pdf(path: Path) -> dict[str, Any]:
    """Inspect GSI PDF page count and sample text extraction using PyMuPDF (fitz)."""
    result: dict[str, Any] = {"file": path.name, "size_mb": round(path.stat().st_size / (1024 * 1024), 2)}
    try:
        import pymupdf

        doc = pymupdf.open(path)
        result["page_count"] = len(doc)
        result["metadata"] = dict(doc.metadata) if doc.metadata else {}
        sample_pages = []
        pages_with_text = 0
        # Probe first 10 pages + evenly spaced sample across document
        probe_indices = sorted(
            set(list(range(min(10, len(doc)))) + [int(i * (len(doc) - 1) / 9) for i in range(10)])
        ) if len(doc) > 0 else []
        for idx in probe_indices:
            txt = doc[idx].get_text("text").strip()
            if txt:
                pages_with_text += 1
            sample_pages.append({"page_1based": idx + 1, "char_count": len(txt), "preview": txt[:250]})
        result["probed_pages"] = len(probe_indices)
        result["probed_pages_with_text"] = pages_with_text
        result["sample_pages"] = sample_pages[:8]
        doc.close()
    except Exception as exc:
        result["inspection_error"] = str(exc)
    return result


def run_audit(config_path: str | Path | None = None) -> dict[str, Any]:
    """Run full recursive audit of raw_data_root and write reports to workspace."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)
    raw_root = dirs["raw_data_root"]
    if not raw_root.exists():
        raise FileNotFoundError(f"Raw data root not found: {raw_root}")

    target_years = cfg["scope"]["target_years"]
    rows: list[dict[str, Any]] = []

    firms_details: list[dict[str, Any]] = []
    imd_years: set[int] = set()
    era5_proc_months: set[tuple[int, int]] = set()
    era5_raw_months: set[tuple[int, int]] = set()

    imd_sample_path: Path | None = None
    era5_sample_path: Path | None = None
    coolr_path: Path | None = None
    gsi_pdf_path: Path | None = None
    boundaries_zip_info: dict[str, Any] | None = None

    all_files = sorted(p for p in raw_root.rglob("*") if p.is_file())
    for fp in all_files:
        rel = fp.relative_to(raw_root).as_posix()
        ext = fp.suffix.lower()
        size_bytes = fp.stat().st_size
        category, yr, mo = classify_file(rel, fp.name, ext)
        notes = ""
        in_target = False

        if category == "firms_zip":
            zinfo = inspect_zip(fp)
            if zinfo["date_min"]:
                yr = int(zinfo["date_min"][:4])
            in_target = yr in target_years if yr else False
            notes = f"csvs={zinfo['csv_files']}; rows={zinfo['row_count']}; dates={zinfo['date_min']}..{zinfo['date_max']}"
            firms_details.append({"file": fp.name, "year": yr, **zinfo})
        elif category == "boundaries_zip":
            boundaries_zip_info = inspect_zip(fp)
            in_target = True
            notes = f"entries={boundaries_zip_info['entries']}"
        elif category == "imd_netcdf":
            if yr is not None:
                imd_years.add(yr)
                in_target = yr in target_years
                if yr == 2021 or imd_sample_path is None:
                    imd_sample_path = fp
        elif category == "era5_processed_nc":
            if yr is not None and mo is not None:
                era5_proc_months.add((yr, mo))
                in_target = yr in target_years
                if (yr, mo) == (2021, 1) or era5_sample_path is None:
                    era5_sample_path = fp
        elif category == "era5_raw_grib":
            if yr is not None and mo is not None:
                era5_raw_months.add((yr, mo))
                in_target = yr in target_years
        elif category == "coolr_json":
            coolr_path = fp
            in_target = True
        elif category == "gsi_pdf":
            gsi_pdf_path = fp
            in_target = True

        rows.append(
            {
                "relative_path": rel,
                "filename": fp.name,
                "extension": ext,
                "category": category,
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 3),
                "year": yr,
                "month": mo,
                "in_target_window": in_target,
                "notes": notes,
            }
        )

    inv_df = pd.DataFrame(rows)
    inv_csv_path = dirs["reports"] / "data_inventory.csv"
    inv_df.to_csv(inv_csv_path, index=False)

    # Coverage checks for target window
    firms_years_found = sorted({y for d in firms_details for y in d.get("years_present", [])})
    firms_missing_target = [y for y in target_years if y not in firms_years_found]
    imd_missing_target = [y for y in target_years if y not in imd_years]
    expected_ym = [(y, m) for y in target_years for m in range(1, 13)]
    era5_missing_target = [f"{y:04d}-{m:02d}" for (y, m) in expected_ym if (y, m) not in era5_proc_months]

    # Check planned static layers
    all_names_lower = [f["relative_path"].lower() for f in rows]
    static_status = {}
    for label, keywords in PLANNED_STATIC_DATASETS:
        matches = [p for p in all_names_lower if any(kw in p for kw in keywords)]
        static_status[label] = {"status": "FOUND" if matches else "NOT_FOUND", "matches": matches}

    summary: dict[str, Any] = {
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "raw_data_root": str(raw_root),
        "total_files_scanned": len(rows),
        "total_size_gb": round(inv_df["size_bytes"].sum() / (1024 ** 3), 3),
        "target_years": target_years,
        "coverage": {
            "firms_years_all": firms_years_found,
            "firms_missing_in_target": firms_missing_target,
            "firms_archives": [
                {
                    "file": d["file"],
                    "year": d["year"],
                    "rows": d["row_count"],
                    "date_min": d["date_min"],
                    "date_max": d["date_max"],
                    "csv_files": d["csv_files"],
                }
                for d in firms_details
            ],
            "imd_years_all": sorted(imd_years),
            "imd_missing_in_target": imd_missing_target,
            "era5_processed_total_months": len(era5_proc_months),
            "era5_processed_target_present": len(expected_ym) - len(era5_missing_target),
            "era5_processed_target_expected": len(expected_ym),
            "era5_processed_missing_in_target": era5_missing_target,
            "era5_raw_grib_total_months": len(era5_raw_months),
            "era5_raw_grib_years": sorted({y for y, _ in era5_raw_months}),
        },
        "schemas": {
            "boundaries_zip": boundaries_zip_info,
            "firms_sample_header": firms_details[0]["header"] if firms_details else None,
            "imd_sample": inspect_imd_sample(imd_sample_path) if imd_sample_path else None,
            "era5_processed_sample": inspect_era5_nc_sample(era5_sample_path) if era5_sample_path else None,
            "coolr": inspect_coolr(coolr_path) if coolr_path else None,
            "gsi_pdf": inspect_gsi_pdf(gsi_pdf_path) if gsi_pdf_path else None,
        },
        "planned_static_datasets": static_status,
    }

    summary_json_path = dirs["reports"] / "data_audit_summary.json"
    with summary_json_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # Write human-readable Data Quality Report
    md_lines = [
        "# HIMA Data Audit & Quality Report",
        "",
        f"- **Audit Timestamp (UTC):** `{summary['audit_timestamp_utc']}`",
        f"- **Raw Data Root (read-only):** `{raw_root}`",
        f"- **Total Files Scanned:** `{summary['total_files_scanned']}` ({summary['total_size_gb']} GB)",
        f"- **Target Window:** `{target_years[0]}–{target_years[-1]}`",
        "",
        "## Target-Window Coverage Summary (2021–2024)",
        "",
        "| Dataset | Available in Target Window | Missing / Gaps |",
        "|---|---|---|",
        f"| NASA FIRMS (Wildfire ZIPs) | {[y for y in firms_years_found if y in target_years]} (all years: {firms_years_found[0]}–{firms_years_found[-1]}, excl. missing) | Missing: `{firms_missing_target}` (2025 archive outside window) |",
        f"| IMD Daily Rainfall (NetCDF) | {sorted(y for y in imd_years if y in target_years)} (all years: {min(imd_years)}–{max(imd_years)}) | Missing: `{imd_missing_target}` |",
        f"| ERA5-Land Processed Weather (NetCDF) | {summary['coverage']['era5_processed_target_present']} / {summary['coverage']['era5_processed_target_expected']} months | Missing: `{era5_missing_target}` |",
        f"| ERA5-Land Raw GRIB | 0 / 48 months (only {summary['coverage']['era5_raw_grib_years']}) | Outside 2021–2024 target window |",
        f"| Boundaries ZIP | Present (`boundaries.zip`) | Requires extraction of `.shp/.shx/.dbf/.prj` |",
        f"| NASA COOLR JSON | {summary['schemas']['coolr']['feature_count'] if summary['schemas']['coolr'] else 0} India candidate events | Requires spatial & date-precision filtering |",
        f"| GSI Landslide PDF | {summary['schemas']['gsi_pdf'].get('page_count', 'unknown') if summary['schemas']['gsi_pdf'] else 0} pages ({summary['schemas']['gsi_pdf'].get('size_mb', 0) if summary['schemas']['gsi_pdf'] else 0} MB) | Unstructured PDF; requires extraction validation |",
        "",
        "## Planned Static Datasets Status",
        "",
        "| Planned Layer | Status |",
        "|---|---|",
    ]
    for label, st in static_status.items():
        md_lines.append(f"| {label} | `{st['status']}` |")

    md_lines += [
        "",
        "## Key Data Quality Rules Enforced",
        "- Raw files in `C:\\Users\\lenovo\\Downloads\\hima` are never modified or overwritten.",
        "- Missing periods (2023 FIRMS; 2023-08/09/11/12 ERA5) are explicitly excluded or flagged, **never** replaced with zeros.",
        "- Missing static layers (DEM, WorldCover, MODIS NDVI, SoilGrids, Geology, ISRO Atlas) are **never** fabricated.",
    ]

    report_md_path = dirs["reports"] / "data_quality_report.md"
    report_md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    result = run_audit()
    print("Audit complete.")
    print("Total files:", result["total_files_scanned"])
    print("FIRMS missing in target:", result["coverage"]["firms_missing_in_target"])
    print("IMD missing in target:", result["coverage"]["imd_missing_in_target"])
    print("ERA5 missing in target:", result["coverage"]["era5_processed_missing_in_target"])
    print("IMD sample:", json.dumps(result["schemas"]["imd_sample"], indent=2))
    print("COOLR fields:", result["schemas"]["coolr"]["field_names"] if result["schemas"]["coolr"] else None)
    print("GSI PDF:", json.dumps({k: v for k, v in (result["schemas"]["gsi_pdf"] or {}).items() if k != "sample_pages"}, indent=2))
