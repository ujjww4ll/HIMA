# HIMA Data Dictionary

All raw datasets live read-only under `C:\Users\lenovo\Downloads\hima` and are never modified. All derived tables live in this project workspace under `data/interim/` and `data/processed/`.

## 1. Study Boundaries (`data/processed/boundaries/`)
- `study_states.gpkg` / `study_states.geojson`: Validated 7 Northeast India state polygons (`Arunachal Pradesh`, `Assam`, `Manipur`, `Meghalaya`, `Mizoram`, `Nagaland`, `Tripura`) in `EPSG:4326` (repaired 1 invalid geometry from raw `state_NWIC.shp`, canonicalized shapefile spelling `"Arunanchal Pradesh"` → `"Arunachal Pradesh"`).
- `study_states_projected.gpkg`: Identical boundaries reprojected to `EPSG:32646` (WGS 84 / UTM Zone 46N, metres).

## 2. Projected 1 km Grid (`data/processed/grid/`)
- `grid_1km.gpkg`: 253,408 polygons of 1,000 m × 1,000 m in `EPSG:32646` (`edge_cell_policy = centroid_within`, 0 cells outside boundary).
- `grid_1km_with_weather_keys.parquet`:

| Column | Type | Units / Description |
|---|---|---|
| `cell_id` | string | Stable fishnet identifier `NE_<col>_<row>` |
| `grid_col`, `grid_row` | int32 | Fishnet column & row indices in `EPSG:32646` |
| `x_m`, `y_m` | float64 | Cell centroid Easting & Northing (metres, `EPSG:32646`) |
| `centroid_lon`, `centroid_lat` | float64 | Cell centroid WGS84 coordinates (degrees, `EPSG:4326`) |
| `state_name` | string | Canonical Northeast India state name |
| `era5_grid_id`, `era5_dist_km` | string / float32 | Nearest ERA5-Land 0.1° grid point ID & distance (km) |
| `imd_grid_id`, `imd_dist_km` | string / float32 | Nearest IMD RF25 0.25° grid point ID & distance (km) |

## 3. Daily Weather Feature Tables (`data/processed/weather/`)
All rolling windows end at or before day $t$ on a contiguous daily calendar (`2021-01-01`..`2024-12-31`). Missing ERA5 months (`2023-08`, `2023-09`, `2023-11`, `2023-12`) remain `NaN` with `era5_missing_flag = 1`.

### `era5_features_daily.parquet` (Source: `ERA5_Land_daily_YYYY_MM.nc`, 44/48 months)
| Column | Units | Description |
|---|---|---|
| `temperature_c`, `dewpoint_c` | °C | Daily 2 m air & dewpoint temperature |
| `dewpoint_depression_c` | °C | `temperature_c - dewpoint_c` (atmospheric dryness) |
| `wind_speed_ms` | m/s | $\sqrt{u^2 + v^2}$ 10 m wind speed |
| `soil_water_layer1` | m³/m³ | Top-layer volumetric soil moisture (0–7 cm) |
| `era5_rainfall_mm` | mm/day | Total precipitation converted from `rainfall_m × 1000` (separate from IMD) |
| `relative_humidity_mean`, `relative_humidity_min` | % (0–100) | Daily mean & minimum relative humidity |
| `era5_temp_mean_7d`, `era5_temp_max_7d` | °C | 7-day rolling mean / max temperature |
| `era5_rh_min_7d`, `era5_rh_mean_7d` | % | 7-day rolling min / mean relative humidity |
| `era5_soil_water_mean_7d` | m³/m³ | 7-day rolling mean soil moisture |
| `era5_wind_mean_7d` | m/s | 7-day rolling mean wind speed |
| `era5_rain_sum_3d`, `_7d`, `_15d` | mm | 3-, 7-, and 15-day antecedent ERA5 rainfall totals |
| `era5_days_since_rain` | days | Consecutive dry days (`< 1.0 mm/day`, capped at 60, reset on NaN gaps) |
| `era5_missing_flag` | int8 | `1` when ERA5 month is missing, `0` otherwise |

### `imd_features_daily.parquet` (Source: `RF25_ind2021..2024_rfp25.nc`, 48/48 months)
| Column | Units | Description |
|---|---|---|
| `imd_rain_1d`, `imd_rain_lag1d` | mm/day | Same-day and previous-day IMD gridded rainfall |
| `imd_rain_sum_3d`, `_7d`, `_15d` | mm | 3-, 7-, and 15-day antecedent IMD rainfall totals |
| `imd_rain_max_7d` | mm/day | 7-day rolling maximum daily rainfall |
| `imd_rainy_days_7d`, `_15d` | days | Count of IMD rainy days (`>= 2.5 mm/day`) in prior 7 / 15 days |
| `imd_days_since_rain` | days | Consecutive days with `< 2.5 mm/day` (capped at 60) |

## 4. Wildfire Modeling Table (`data/processed/wildfire.parquet`)
- `split`: `'train'` (`2021–2023`, all positive cell-days + 5:1 uniform background negatives) or `'test_realistic'` (`2024`, 1,000,000 uniform cell-days preserving real-world base rate).
- `fire_detected`: Binary target (`1` = $\ge 1$ NASA FIRMS VIIRS S-NPP C2 `type == 0` vegetation fire in cell-day; `0` = observed no-record).
- `spatial_block_id`: 50 km × 50 km block identifier used for leakage-safe `StratifiedGroupKFold`.
- `sin_doy`, `cos_doy`, `season`: Cyclic day-of-year and official IMD meteorological season (`Winter`, `Pre-Monsoon`, `Monsoon`, `Post-Monsoon`).
- Provenance & post-event audit columns (strictly excluded from model features): `detection_count`, `frp_sum`, `frp_mean`, `frp_max`, `brightness_mean`, `brightness_max`, `day_detections`, `night_detections`, `high_conf_count`, `nominal_conf_count`, `low_conf_count`, `source_dataset`, `source_file`, `label_source`.

## 5. Landslide Inventory Table (`data/processed/landslide.parquet`)
- Integrates validated Northeast India landslide records with `source_dataset`, `source_event_id`, `source_page`, `state_name`, `district`, `location_name`, `latitude`, `longitude`, `event_date`, `date_quality`, `movement_type`, `material_involved`, `within_study_boundary`, and `is_eligible_daily_label`.

