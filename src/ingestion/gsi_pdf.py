"""Step 8b: GSI Field-Validated Landslide PDF structured table extraction.

Uses PyMuPDF word-coordinate layout parsing (fast, preserves exact decimal coordinates and
multi-line cell wrapping cleanly without breaking decimals).

Columns in GSI_Landslide_Inventory_Field_Validated.pdf:
  Sl.No., Slide_No, State, District, Slide_Name, NH_SH_Location,
  Latitude, Longitude, Material Involved, Movement Type, History

Extracts ONLY verifiable Northeast India records with exact source_page traceability.
Never invents missing dates or coordinates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pymupdf
import shapely

from src.config import ensure_project_dirs, load_config


NE_STATES_CANONICAL = {
    "arunachal pradesh": "Arunachal Pradesh",
    "arunanchal pradesh": "Arunachal Pradesh",
    "arunachal": "Arunachal Pradesh",
    "assam": "Assam",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "tripura": "Tripura",
    "sikkim": "Sikkim",
}

# Match numeric dates (DD/MM/YYYY, YYYY-MM-DD) AND named-month dates (e.g. '17 May 2016', '02nd June 2020')
MONTH_NAMES = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
DATE_PATTERNS = [
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?[\s./-]+{MONTH_NAMES}[\s.,/-]+(?:19|20)\d{{2}}\b", re.IGNORECASE),
    re.compile(rf"\b{MONTH_NAMES}[\s.-]+\d{{1,2}}(?:st|nd|rd|th)?[\s,.-]+(?:19|20)\d{{2}}\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}[-/.]\d{1,2}[-/.](?:19|20)\d{2}\b"),
    re.compile(r"\b(?:19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}\b"),
]
SLIDE_YEAR_PATTERN = re.compile(r"/(19\d{2}|20\d{2})(?:-\d{2})?/")

# Default column left-edge cutoffs (calibrated from verified PDF layout; dynamically refined per page header)
DEFAULT_COL_EDGES = [0.0, 44.0, 131.0, 204.0, 280.0, 383.0, 470.0, 516.0, 563.0, 622.0, 666.0]
HEADER_ANCHORS = [
    "sl.no",
    "slide_no",
    "state",
    "district",
    "slide_name",
    "nh_sh",
    "latitude",
    "longitude",
    "material",
    "movement",
    "history",
]


def extract_exact_date(history: str) -> str | None:
    """Extract an exact day-precision date string from History text if present."""
    if not history or history.strip().upper() in {"NA", "N/A", "NIL", "-", "NONE"}:
        return None
    for pat in DATE_PATTERNS:
        m = pat.search(history)
        if m:
            # Strip ordinal suffixes (02nd -> 02) for clean pandas parsing
            return re.sub(r"(\d+)(?:st|nd|rd|th)\b", r"\1", m.group(0), flags=re.IGNORECASE)
    return None


def parse_float_safe(val: str) -> float:
    s = str(val).replace("°", "").replace("N", "").replace("E", "").replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return float("nan")


def detect_column_edges(words: list[tuple[Any, ...]]) -> tuple[list[float], float]:
    """Detect column x-boundaries and header bottom y from the page header words."""
    header_words = [w for w in words if w[1] < 95.0]
    found_x: dict[int, float] = {}
    header_bottom = 80.0

    for w in header_words:
        tok = w[4].lower().strip()
        for idx, anchor in enumerate(HEADER_ANCHORS):
            if tok.startswith(anchor) and idx not in found_x:
                found_x[idx] = float(w[0]) - 2.0
                header_bottom = max(header_bottom, float(w[3]) + 1.0)
                break

    if len(found_x) >= 9:
        edges = [0.0]
        for i in range(1, 11):
            edges.append(found_x.get(i, DEFAULT_COL_EDGES[i]))
        return edges, header_bottom
    return list(DEFAULT_COL_EDGES), 80.0


def col_index_for_x(x0: float, edges: list[float]) -> int:
    for i in range(len(edges) - 1, -1, -1):
        if x0 >= edges[i]:
            return i
    return 0


def parse_page_records(page: pymupdf.Page, page_num_1based: int) -> list[dict[str, Any]]:
    """Parse all table rows on a single GSI PDF page using word coordinates."""
    words = page.get_text("words")
    if not words:
        return []

    edges, header_y_end = detect_column_edges(words)

    # Filter out title & header words
    body_words = [w for w in words if w[1] >= header_y_end - 1.0]
    if not body_words:
        return []

    # Identify row start y-coordinates from integer Sl.No. tokens in column 0
    row_anchors: list[tuple[float, str]] = []
    for w in body_words:
        if w[0] < edges[1] and w[4].isdigit():
            row_anchors.append((float(w[1]), w[4]))
    row_anchors.sort(key=lambda t: t[0])

    if not row_anchors:
        return []

    # Assign each body word to its row band [anchor_y - 2.5, next_anchor_y - 2.5)
    n_rows = len(row_anchors)
    row_buckets: list[list[list[tuple[float, float, str]]]] = [
        [[] for _ in range(11)] for _ in range(n_rows)
    ]

    anchor_ys = [a[0] for a in row_anchors]
    for w in body_words:
        wy = float(w[1])
        wx = float(w[0])
        # Find last anchor with anchor_y <= wy + 2.5
        r_idx = -1
        for i in range(n_rows):
            if anchor_ys[i] <= wy + 2.5:
                r_idx = i
            else:
                break
        if r_idx < 0:
            continue
        c_idx = col_index_for_x(wx, edges)
        row_buckets[r_idx][c_idx].append((wy, wx, w[4]))

    records: list[dict[str, Any]] = []
    for r_idx in range(n_rows):
        cells = []
        for c_idx in range(11):
            toks = sorted(row_buckets[r_idx][c_idx], key=lambda t: (round(t[0], 1), t[1]))
            cells.append(" ".join(t[2] for t in toks).strip())

        sl_no, slide_no, state_raw, district, slide_name, location, lat_s, lon_s, material, move_type, history = cells
        state_norm = NE_STATES_CANONICAL.get(state_raw.lower().strip())
        if not state_norm:
            continue

        lat = parse_float_safe(lat_s)
        lon = parse_float_safe(lon_s)
        exact_date_str = extract_exact_date(history)
        yr_match = SLIDE_YEAR_PATTERN.search(slide_no)
        survey_year = int(yr_match.group(1)) if yr_match else None

        records.append(
            {
                "source_page": page_num_1based,
                "sl_no": sl_no,
                "source_event_id": slide_no if slide_no else f"GSI_P{page_num_1based}_{sl_no}",
                "state_name_raw": state_raw,
                "state_name": state_norm,
                "district": district,
                "slide_name": slide_name,
                "nh_sh_location": location,
                "latitude": lat,
                "longitude": lon,
                "material_involved": material,
                "movement_type": move_type,
                "history": history,
                "survey_year_from_id": survey_year,
                "exact_date_in_history": exact_date_str,
                "has_exact_event_date": exact_date_str is not None,
                "source_dataset": "GSI_FIELD_VALIDATED_PDF",
            }
        )
    return records


def inspect_and_extract_gsi_pdf(config_path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Scan all pages of GSI PDF, extract structured table rows for NE India states with provenance."""
    cfg = load_config(config_path)
    dirs = ensure_project_dirs(cfg)

    pdf_path = dirs["raw_data_root"] / "GSI_Landslide_Inventory_Field_Validated.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"GSI PDF not found: {pdf_path}")

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    pages_with_text = 0
    ne_candidate_pages = 0
    extracted_rows: list[dict[str, Any]] = []

    ne_keywords = list(NE_STATES_CANONICAL.keys())

    for page_idx in range(total_pages):
        page = doc[page_idx]
        txt = page.get_text("text")
        if len(txt.strip()) >= 30:
            pages_with_text += 1
        txt_lower = txt.lower()
        if not any(kw in txt_lower for kw in ne_keywords):
            continue

        ne_candidate_pages += 1
        extracted_rows.extend(parse_page_records(page, page_idx + 1))

    doc.close()

    df = pd.DataFrame(extracted_rows)
    if len(df) > 0:
        df["has_valid_coords"] = (
            df["latitude"].notna()
            & df["longitude"].notna()
            & df["latitude"].between(21.0, 30.5)
            & df["longitude"].between(87.5, 98.5)
        )
        # Validate spatial containment against study states (7 Sisters)
        study_states = gpd.read_file(dirs["processed_boundaries"] / "study_states.gpkg")[["state_name", "geometry"]]
        valid_sub = df.loc[df["has_valid_coords"]].copy()
        if len(valid_sub) > 0:
            pts = shapely.points(valid_sub["longitude"].to_numpy(), valid_sub["latitude"].to_numpy())
            pts_gdf = gpd.GeoDataFrame(valid_sub[["source_event_id"]], geometry=pts, crs="EPSG:4326")
            inside = gpd.sjoin(pts_gdf, study_states, how="inner", predicate="within")
            inside_idx = set(inside.index.tolist())
            df["within_study_boundary"] = df.index.isin(inside_idx)
        else:
            df["within_study_boundary"] = False

        # Parse extracted history dates strictly
        parsed_dt = pd.to_datetime(df["exact_date_in_history"], dayfirst=True, format="mixed", errors="coerce")
        df["parsed_event_date"] = parsed_dt
        d_start = pd.Timestamp(cfg["scope"]["date_start"])
        d_end = pd.Timestamp(cfg["scope"]["date_end"])
        df["dated_in_target_2021_2024"] = (
            df["within_study_boundary"]
            & parsed_dt.notna()
            & (parsed_dt >= d_start)
            & (parsed_dt <= d_end)
        )
    else:
        df["has_valid_coords"] = False
        df["within_study_boundary"] = False
        df["parsed_event_date"] = pd.NaT
        df["dated_in_target_2021_2024"] = False

    out_csv = dirs["interim_events"] / "gsi_ne_india_extracted.csv"
    out_parquet = dirs["interim_events"] / "gsi_ne_india_extracted.parquet"
    df.to_csv(out_csv, index=False)
    df.to_parquet(out_parquet, index=False)

    non_na_history = (
        df["history"].replace({"": np.nan, "NA": np.nan, "N/A": np.nan, "na": np.nan, "Nil": np.nan, "NIL": np.nan}).dropna()
        if len(df) > 0
        else pd.Series(dtype=str)
    )

    report = {
        "source_file": str(pdf_path),
        "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
        "total_pages": total_pages,
        "pages_with_extractable_text": pages_with_text,
        "ne_candidate_pages_scanned": ne_candidate_pages,
        "total_ne_records_extracted": int(len(df)),
        "valid_coords_count": int(df["has_valid_coords"].sum()) if len(df) else 0,
        "within_7_sister_study_boundary_count": int(df["within_study_boundary"].sum()) if len(df) else 0,
        "records_with_non_na_history": int(len(non_na_history)),
        "records_with_exact_event_date_any_year": int(df["parsed_event_date"].notna().sum()) if len(df) else 0,
        "records_dated_in_target_2021_2024_in_study": int(df["dated_in_target_2021_2024"].sum()) if len(df) else 0,
        "records_by_state": {k: int(v) for k, v in df["state_name"].value_counts().sort_index().items()} if len(df) else {},
        "movement_type_counts": {k: int(v) for k, v in df["movement_type"].value_counts().head(10).items()} if len(df) else {},
        "material_involved_counts": {k: int(v) for k, v in df["material_involved"].value_counts().head(10).items()} if len(df) else {},
        "sample_non_na_history_values": non_na_history.head(15).tolist(),
        "outputs": {"csv": str(out_csv), "parquet": str(out_parquet)},
        "validation_assessment": (
            "GSI PDF is a structured, text-extractable field-validated landslide inventory. "
            "Northeast India slide locations with exact coordinates, material, movement type, and "
            "history dates were extracted with page provenance via word-coordinate table parsing."
        ),
    }

    with (dirs["reports"] / "gsi_pdf_inspection.json").open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    return df, report


if __name__ == "__main__":
    df_gsi, rep = inspect_and_extract_gsi_pdf()
    print("GSI PDF extraction complete.")
    print(f"Total pages: {rep['total_pages']} | NE candidate pages: {rep['ne_candidate_pages_scanned']}")
    print(
        f"Extracted NE records: {rep['total_ne_records_extracted']:,} | "
        f"Valid coords: {rep['valid_coords_count']:,} | "
        f"Inside 7 Sisters: {rep['within_7_sister_study_boundary_count']:,}"
    )
    print(
        f"Exact event dates (any year): {rep['records_with_exact_event_date_any_year']:,} | "
        f"Dated in 2021-2024 inside 7 Sisters: {rep['records_dated_in_target_2021_2024_in_study']:,}"
    )
    print("By state:", rep["records_by_state"])
    print("Top movement types:", rep["movement_type_counts"])
