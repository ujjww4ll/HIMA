"""Step 11: HIMA Research Web Dashboard & Prediction API (Wildfire + Preliminary Landslide).

Serves:
  - Static frontend dashboard from `frontend/` (`GET /`)
  - Generated maps & figures from `outputs/` (`GET /outputs/...`)
  - Live metadata, model comparison tables & simplified state GeoJSON (`GET /api/overview`)
  - Validated Wildfire inference (`POST /predict` and `POST /api/predict/wildfire`)
  - Preliminary Weather-Only Landslide inference (`POST /api/predict/landslide`)

Never fabricates live weather, missing terrain layers, or official alerts.
"""

from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd

from src.config import PROJECT_ROOT
from src.evaluation.metrics import DISCLAIMER, assign_risk_band, bayes_prior_adjust


DEFAULT_WILDFIRE_MODEL = PROJECT_ROOT / "models" / "wildfire_best_model.joblib"
DEFAULT_LANDSLIDE_MODEL = PROJECT_ROOT / "models" / "landslide_preliminary_model.joblib"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


class WildfireRiskPredictor:
    """Loads saved wildfire preprocessing + model pipeline bundle for deterministic inference."""

    def __init__(self, model_path: str | Path = DEFAULT_WILDFIRE_MODEL) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Validated wildfire model artifact not found: {self.model_path}. Run training first."
            )
        bundle = joblib.load(self.model_path)
        self.model_name: str = bundle["model_name"]
        self.pipeline = bundle["pipeline"]
        self.features: list[str] = bundle["features"]
        self.operating_threshold: float = float(bundle["operating_threshold"])
        self.effective_train_prior: float = float(bundle["effective_train_prior"])
        self.population_prior: float = float(bundle["population_prior_2021_2023"])
        self.trained_timestamp_utc: str = bundle.get("trained_timestamp_utc", "")
        self.disclaimer: str = bundle.get("disclaimer", DISCLAIMER)

    def predict(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Predict wildfire risk probabilities and provisional bands for input feature dicts."""
        df = pd.DataFrame(records)
        for col in self.features:
            if col not in df.columns:
                df[col] = np.nan
        X = df[self.features]

        raw_probs = self.pipeline.predict_proba(X)[:, 1]
        cal_probs = bayes_prior_adjust(raw_probs, self.effective_train_prior, self.population_prior)
        # Risk band on raw relative score vs calibrated daily probability (both returned transparently!)
        bands_raw = assign_risk_band(raw_probs)
        bands_cal = assign_risk_band(cal_probs)
        alerts_at_thr = (raw_probs >= self.operating_threshold).astype(int)

        predictions = []
        for i in range(len(df)):
            predictions.append(
                {
                    "index": i,
                    "raw_score": round(float(raw_probs[i]), 5),
                    "calibrated_daily_probability": round(float(cal_probs[i]), 6),
                    "provisional_risk_band": str(bands_cal[i]),
                    "relative_score_band": str(bands_raw[i]),
                    "above_cv_f1_threshold": bool(alerts_at_thr[i]),
                }
            )

        return {
            "hazard": "wildfire",
            "model_name": self.model_name,
            "trained_timestamp_utc": self.trained_timestamp_utc,
            "operating_threshold_raw_score": self.operating_threshold,
            "population_prior_2021_2023": self.population_prior,
            "disclaimer": self.disclaimer,
            "note": (
                "Provisional risk bands are research display categories, not validated operational thresholds. "
                "Single-cell daily calibrated probabilities are naturally small (~0.03%-5%) because NE India has 253,408 1 km cells."
            ),
            "predictions": predictions,
        }


class LandslideRiskPredictor:
    """Loads preliminary weather-only landslide trigger model bundle."""

    def __init__(self, model_path: str | Path = DEFAULT_LANDSLIDE_MODEL) -> None:
        self.model_path = Path(model_path)
        self.available = self.model_path.exists()
        if not self.available:
            return
        bundle = joblib.load(self.model_path)
        self.model_name: str = bundle["model_name"]
        self.pipeline = bundle["pipeline"]
        self.features: list[str] = bundle["features"]
        self.operating_threshold: float = float(bundle["operating_threshold"])
        self.preliminary_warning: str = bundle.get(
            "preliminary_warning",
            "Weather-trigger only; static terrain layers (DEM/slope/soil/geology) absent.",
        )
        self.trained_timestamp_utc: str = bundle.get("trained_timestamp_utc", "")
        self.disclaimer: str = bundle.get("disclaimer", DISCLAIMER)

    def predict(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        if not self.available:
            raise FileNotFoundError("Preliminary landslide model artifact not found.")
        df = pd.DataFrame(records)
        for col in self.features:
            if col not in df.columns:
                df[col] = np.nan
        X = df[self.features]
        raw_probs = self.pipeline.predict_proba(X)[:, 1]
        bands = assign_risk_band(raw_probs)
        alerts = (raw_probs >= self.operating_threshold).astype(int)

        predictions = [
            {
                "index": i,
                "raw_score": round(float(raw_probs[i]), 5),
                "relative_score_band": str(bands[i]),
                "above_cv_f1_threshold": bool(alerts[i]),
            }
            for i in range(len(df))
        ]
        return {
            "hazard": "landslide_preliminary",
            "model_name": self.model_name,
            "trained_timestamp_utc": self.trained_timestamp_utc,
            "operating_threshold_raw_score": self.operating_threshold,
            "preliminary_warning": self.preliminary_warning,
            "disclaimer": self.disclaimer,
            "predictions": predictions,
        }


def _read_json_if_exists(path: Path) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _read_csv_records_if_exists(path: Path) -> list[dict[str, Any]]:
    if path.exists():
        df = pd.read_csv(path)
        return json.loads(df.to_json(orient="records"))
    return []


def build_dashboard_overview() -> dict[str, Any]:
    """Assemble real verified reports, tables, and simplified NE India GeoJSON for the web UI."""
    reports = PROJECT_ROOT / "data" / "reports"
    tables = PROJECT_ROOT / "outputs" / "tables"
    models = PROJECT_ROOT / "models"

    # Load simplified study-state polygons for fast offline SVG map rendering
    boundaries_geojson: dict[str, Any] = {"type": "FeatureCollection", "features": []}
    gpkg = PROJECT_ROOT / "data" / "processed" / "boundaries" / "study_states.gpkg"
    if gpkg.exists():
        gdf = gpd.read_file(gpkg).to_crs("EPSG:4326")
        gdf["geometry"] = gdf.geometry.simplify(0.025, preserve_topology=True)
        cents = gdf.geometry.representative_point()
        gdf["rep_lon"] = np.round(cents.x, 4)
        gdf["rep_lat"] = np.round(cents.y, 4)
        if "area_km2" not in gdf.columns:
            if "shape_area" in gdf.columns:
                gdf["area_km2"] = (gdf["shape_area"] / 1e6).round(2)
            else:
                gdf["area_km2"] = None
        boundaries_geojson = json.loads(gdf[["state_name", "area_km2", "rep_lon", "rep_lat", "geometry"]].to_json())

    return {
        "disclaimer": DISCLAIMER,
        "audit": _read_json_if_exists(reports / "data_audit_summary.json"),
        "boundaries_meta": _read_json_if_exists(reports / "boundaries_metadata.json"),
        "grid_meta": _read_json_if_exists(reports / "grid_metadata.json"),
        "firms_meta": _read_json_if_exists(reports / "firms_ingestion_metadata.json"),
        "weather_meta": _read_json_if_exists(reports / "weather_features_metadata.json"),
        "landslide_feasibility": _read_json_if_exists(reports / "landslide_feasibility.json"),
        "gsi_meta": _read_json_if_exists(reports / "gsi_pdf_inspection.json"),
        "wildfire_card": _read_json_if_exists(models / "wildfire_model_card.json"),
        "landslide_card": _read_json_if_exists(models / "landslide_model_card.json"),
        "tables": {
            "wildfire_models": _read_csv_records_if_exists(tables / "wildfire_model_comparison.csv"),
            "wildfire_per_state": _read_csv_records_if_exists(tables / "wildfire_test2024_per_state.csv"),
            "wildfire_per_season": _read_csv_records_if_exists(tables / "wildfire_test2024_per_season.csv"),
            "wildfire_importance": _read_csv_records_if_exists(tables / "wildfire_feature_importance.csv")[:12],
            "landslide_models": _read_csv_records_if_exists(tables / "landslide_model_comparison.csv"),
            "landslide_importance": _read_csv_records_if_exists(tables / "landslide_feature_importance.csv")[:12],
        },
        "boundaries_geojson": boundaries_geojson,
    }


def serve_http(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the HIMA Research Dashboard & Prediction API server."""
    wf_predictor = WildfireRiskPredictor()
    ls_predictor = LandslideRiskPredictor()
    overview_cache = build_dashboard_overview()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            print(f"[HIMA Web] {self.address_string()} - {format % args}")

        def _send_json(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, file_path: Path) -> None:
            if not file_path.exists() or not file_path.is_file():
                self._send_json(404, {"error": f"File not found: {file_path.name}"})
                return
            mime, _ = mimetypes.guess_type(str(file_path))
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            parsed = urlparse(self.path).path

            if parsed == "/health":
                self._send_json(
                    200,
                    {
                        "status": "ok",
                        "wildfire_model": wf_predictor.model_name,
                        "landslide_model": ls_predictor.model_name if ls_predictor.available else None,
                        "disclaimer": wf_predictor.disclaimer,
                    },
                )
                return

            if parsed == "/api/overview":
                self._send_json(200, overview_cache)
                return

            # Serve generated PNG maps & figures securely from outputs/
            if parsed.startswith("/outputs/"):
                rel = parsed.removeprefix("/outputs/").lstrip("/")
                target = (OUTPUTS_DIR / rel).resolve()
                if OUTPUTS_DIR.resolve() in target.parents:
                    self._send_file(target)
                else:
                    self._send_json(403, {"error": "Forbidden path"})
                return

            # Serve frontend static files
            if parsed in {"/", "/index.html"}:
                self._send_file(FRONTEND_DIR / "index.html")
                return

            rel_fe = parsed.lstrip("/")
            fe_target = (FRONTEND_DIR / rel_fe).resolve()
            if FRONTEND_DIR.resolve() in fe_target.parents and fe_target.is_file():
                self._send_file(fe_target)
                return

            self._send_json(404, {"error": f"Route not found: {parsed}"})

        def do_POST(self) -> None:
            parsed = urlparse(self.path).path
            if parsed not in {"/predict", "/api/predict/wildfire", "/api/predict/landslide"}:
                self._send_json(404, {"error": f"Endpoint not found: {parsed}"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
                records = payload if isinstance(payload, list) else payload.get("records", [payload])
                if parsed == "/api/predict/landslide":
                    result = ls_predictor.predict(records)
                else:
                    result = wf_predictor.predict(records)
                self._send_json(200, result)
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})

    server = ThreadingHTTPServer((host, port), Handler)
    print("===================================================================")
    print(f"HIMA Research Dashboard & API running at: http://{host}:{port}")
    print(f"Wildfire Model:  {wf_predictor.model_name}")
    if ls_predictor.available:
        print(f"Landslide Model: {ls_predictor.model_name} (Preliminary Weather-Only)")
    print(f"Disclaimer:      {wf_predictor.disclaimer}")
    print("Press Ctrl+C to stop.")
    print("===================================================================")
    server.serve_forever()


if __name__ == "__main__":
    serve_http()
