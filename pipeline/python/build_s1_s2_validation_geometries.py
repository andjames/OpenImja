#!/usr/bin/env python3
"""Build static spatial-comparison layers for the Sentinel-1 / Sentinel-2 audit view."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from shapely.geometry import mapping, shape

ROOT = Path(__file__).resolve().parents[2]
PAIRS = ROOT / "data/validation/s1-s2-pairs.csv"
OUTPUT = ROOT / "data/validation/s1-s2-pair-geometries.geojson"


def pair_key(row: dict) -> str:
    return f"{row['sentinel2_product_id']}|{row['sentinel1_product_id']}"


def read_geometry(relative_path: str):
    if not relative_path:
        return None
    feature_collection = json.loads((ROOT / relative_path).read_text())
    features = feature_collection.get("features", [])
    return shape(features[0]["geometry"]) if features else None


def comparison_features(pair_id: str, optical, sar) -> list[dict]:
    """Return labelled, non-harmonized geometry layers for one pair."""
    if optical is None:
        return []
    layers = [("optical", optical)]
    if sar is not None:
        layers.extend([
            ("sar", sar),
            ("intersection", optical.intersection(sar)),
            ("optical_omission", optical.difference(sar)),
            ("sar_commission", sar.difference(optical)),
        ])
    return [
        {"type": "Feature", "properties": {"pair_id": pair_id, "layer": layer}, "geometry": mapping(geometry)}
        for layer, geometry in layers if not geometry.is_empty
    ]


def main() -> None:
    with PAIRS.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    features = []
    for row in rows:
        features.extend(comparison_features(pair_key(row), read_geometry(row["sentinel2_boundary"]), read_geometry(row["sentinel1_boundary"])))
    OUTPUT.write_text(json.dumps({"type": "FeatureCollection", "features": features}, indent=2) + "\n")
    print(json.dumps({"pairs": len(rows), "layers": len(features), "output": str(OUTPUT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
