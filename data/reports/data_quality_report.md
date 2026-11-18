# HIMA Data Audit & Quality Report

- **Audit Timestamp (UTC):** `2026-11-18T04:09:10.727767+00:00`
- **Raw Data Root (read-only):** `C:\Users\lenovo\Downloads\hima`
- **Total Files Scanned:** `184` (2.898 GB)
- **Target Window:** `2021–2024`

## Target-Window Coverage Summary (2021–2024)

| Dataset | Available in Target Window | Missing / Gaps |
|---|---|---|
| NASA FIRMS (Wildfire ZIPs) | [2021, 2022, 2023, 2024] (all years: 2012–2026, excl. missing) | Missing: `[]` (2025 archive outside window) |
| IMD Daily Rainfall (NetCDF) | [2021, 2022, 2023, 2024] (all years: 2012–2024) | Missing: `[]` |
| ERA5-Land Processed Weather (NetCDF) | 44 / 48 months | Missing: `['2023-08', '2023-09', '2023-11', '2023-12']` |
| ERA5-Land Raw GRIB | 0 / 48 months (only [2012, 2013]) | Outside 2021–2024 target window |
| Boundaries ZIP | Present (`boundaries.zip`) | Requires extraction of `.shp/.shx/.dbf/.prj` |
| NASA COOLR JSON | 176 India candidate events | Requires spatial & date-precision filtering |
| GSI Landslide PDF | 904 pages (300.95 MB) | Unstructured PDF; requires extraction validation |

## Planned Static Datasets Status

| Planned Layer | Status |
|---|---|
| SRTM / Copernicus DEM | `NOT_FOUND` |
| ESA WorldCover | `NOT_FOUND` |
| MODIS MOD13Q1 NDVI | `NOT_FOUND` |
| SoilGrids | `NOT_FOUND` |
| Geology / Lithology | `NOT_FOUND` |
| ISRO NRSC Landslide Atlas | `NOT_FOUND` |

## Key Data Quality Rules Enforced
- Raw files in `C:\Users\lenovo\Downloads\hima` are never modified or overwritten.
- Missing periods (2023 FIRMS; 2023-08/09/11/12 ERA5) are explicitly excluded or flagged, **never** replaced with zeros.
- Missing static layers (DEM, WorldCover, MODIS NDVI, SoilGrids, Geology, ISRO Atlas) are **never** fabricated.
