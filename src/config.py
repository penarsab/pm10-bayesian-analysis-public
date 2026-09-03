"""Configuration helpers for the public PM10 replication package."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIGS_DIR = PROJECT_ROOT / "configs"
CONFIG_PATH = CONFIGS_DIR / "reproduction.yaml"
FROZEN_RESULTS_DIR = PROJECT_ROOT / "data" / "frozen_results"
FIGURE_SOURCES_DIR = FROZEN_RESULTS_DIR / "figure_sources"
TABLE_SOURCES_DIR = FROZEN_RESULTS_DIR / "table_sources"
MODEL_METADATA_DIR = FROZEN_RESULTS_DIR / "model_metadata"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def load_analysis_config() -> dict[str, Any]:
    return load_yaml(CONFIG_PATH)


def config_section(name: str) -> dict[str, Any]:
    return load_analysis_config()[name]


def project_path(relative_path: str | Path) -> Path:
    path = Path(relative_path)
    return path if path.is_absolute() else PROJECT_ROOT / path
