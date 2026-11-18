"""Shared configuration loading and path resolution utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "project.yaml"


def load_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load YAML project configuration."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def resolve_project_path(rel_or_abs: str | Path) -> Path:
    """Resolve a path relative to PROJECT_ROOT unless already absolute."""
    p = Path(rel_or_abs)
    return p if p.is_absolute() else (PROJECT_ROOT / p)


def ensure_project_dirs(cfg: dict[str, Any]) -> dict[str, Path]:
    """Create workspace interim, processed, reports, models, and outputs subdirectories."""
    paths_cfg = cfg["paths"]
    interim = resolve_project_path(paths_cfg["interim_dir"])
    processed = resolve_project_path(paths_cfg["processed_dir"])
    reports = resolve_project_path(paths_cfg["reports_dir"])
    models = resolve_project_path(paths_cfg["models_dir"])
    outputs = resolve_project_path(paths_cfg["outputs_dir"])

    dirs = {
        "raw_data_root": Path(paths_cfg["raw_data_root"]),
        "interim_boundaries": interim / "boundaries",
        "interim_firms": interim / "firms_extracted",
        "interim_events": interim / "events_validated",
        "interim_weather": interim / "weather_daily",
        "processed_boundaries": processed / "boundaries",
        "processed_grid": processed / "grid",
        "processed_labels": processed / "labels",
        "processed_features": processed / "features",
        "processed_weather": processed / "weather",
        "reports": reports,
        "models": models,
        "outputs_maps": outputs / "maps",
        "outputs_figures": outputs / "figures",
        "outputs_tables": outputs / "tables",
    }
    for key, path in dirs.items():
        if key != "raw_data_root":
            path.mkdir(parents=True, exist_ok=True)
    return dirs

