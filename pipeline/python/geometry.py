"""Canonical Imja geometry/config loading and provenance."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config/lakes/imja-tsho.json"

def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())

def geometry_provenance(config: dict) -> dict:
    return {"geometry_version": config["geometry_version"], "geometry_config_path": "config/lakes/imja-tsho.json", "reference_lake_envelope_path": config["reviewed_reference_lake_envelope"]["path"]}
