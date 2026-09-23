#!/usr/bin/env python3
"""Pair reviewed/published optical records with all nearby SAR candidates."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from pairing import observation_pairs
from spatial_compare import compare_geojson

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/validation/s1-s2-pairs.csv"

def records(folder: Path) -> list[dict]:
    return [json.loads(path.read_text()) for path in folder.glob("*.json")]

def spatial_metrics(row: dict) -> dict:
    """Return geometry disagreement metrics when both retained boundaries exist."""
    left, right = row.get("sentinel2_boundary"), row.get("sentinel1_boundary")
    if not left or not right:
        return {"iou":None,"optical_omission_fraction":None,"sar_commission_fraction":None,"centroid_displacement_degrees":None}
    try:
        return compare_geojson(json.loads((ROOT/left).read_text()),json.loads((ROOT/right).read_text()))
    except (OSError, ValueError, KeyError, IndexError):
        return {"iou":None,"optical_omission_fraction":None,"sar_commission_fraction":None,"centroid_displacement_degrees":None}

def main() -> None:
    parser = argparse.ArgumentParser(description="Pair all retained SAR scenes with published optical references in an explicit temporal context.")
    parser.add_argument("--window-days", type=float, default=31, help="Maximum absolute separation retained in the contextual archive (default: 31).")
    parser.add_argument("--strict-window-days", type=float, default=3, help="Maximum separation labelled near_coincident for direct validation (default: 3).")
    args = parser.parse_args()
    optical = records(ROOT / "data/processed/imja-tsho/scenes") + records(ROOT / "data/processed/imja-tsho")
    sar = records(ROOT / "data/processed/imja-tsho/sar-scenes")
    rows = [{**row,**spatial_metrics(row)} for row in observation_pairs(optical, sar, args.window_days, args.strict_window_days)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["sentinel2_observed_at", "sentinel2_area_km2", "sentinel2_product_id", "sentinel2_boundary", "sentinel1_observed_at", "sentinel1_area_km2", "sentinel1_product_id", "sentinel1_boundary", "temporal_separation_hours", "temporal_separation_days", "pairing_window_days", "strict_window_days", "pairing_class", "absolute_area_difference_km2", "percentage_area_difference", "signed_area_difference_km2", "sentinel1_orbit_pass", "sentinel1_polarization", "sentinel1_incidence_metadata", "sentinel1_parameters", "sentinel2_quality_flags", "sentinel1_quality_flags", "sentinel1_state", "iou", "optical_omission_fraction", "sar_commission_fraction", "centroid_displacement_degrees"]
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"pairs": len(rows), "window_days": args.window_days, "strict_window_days": args.strict_window_days, "output": str(OUT.relative_to(ROOT))}, indent=2))

if __name__ == "__main__": main()
