#!/usr/bin/env python3
"""Describe near-coincident reviewed/published Landsat and Sentinel-2 observations.

This is comparison evidence only. It does not harmonize or merge sensor series.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from pairing import parse_time
from spatial_compare import compare_geojson

ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"data/validation/optical-cross-sensor-pairs.csv"
def records(path): return [json.loads(p.read_text()) for p in path.glob("*.json")]
def metrics(a,b):
    if not a.get("boundary_geojson_url") or not b.get("boundary_geojson_url"): return {"iou":None,"landat_omission_fraction":None,"sentinel2_commission_fraction":None,"centroid_displacement_degrees":None}
    try:
        raw=compare_geojson(json.loads((ROOT/a["boundary_geojson_url"]).read_text()),json.loads((ROOT/b["boundary_geojson_url"]).read_text()))
        return {"iou":raw["iou"],"landsat_omission_fraction":raw["optical_omission_fraction"],"sentinel2_commission_fraction":raw["sar_commission_fraction"],"centroid_displacement_degrees":raw["centroid_displacement_degrees"]}
    except (OSError,ValueError,KeyError,IndexError): return {"iou":None,"landat_omission_fraction":None,"sentinel2_commission_fraction":None,"centroid_displacement_degrees":None}
def main():
    p=argparse.ArgumentParser();p.add_argument("--window-days",type=float,default=7);a=p.parse_args()
    landsat=[r for r in records(ROOT/"data/archive/scenes/landsat") if r.get("observation_state") in {"reviewed","published"}]
    s2=[r for r in records(ROOT/"data/processed/imja-tsho/scenes") if r.get("measurement_family")=="optical" and r.get("source")=="Sentinel-2" and r.get("observation_state") in {"reviewed","published"}]
    rows=[]
    for left in landsat:
        for right in s2:
            hours=(parse_time(right["observed_at"])-parse_time(left["observed_at"])).total_seconds()/3600
            if abs(hours)>a.window_days*24: continue
            diff=right.get("value")-left.get("value") if right.get("value") is not None and left.get("value") is not None else None
            rows.append({"landsat_observed_at":left["observed_at"],"landsat_sensor":left["provenance"].get("sensor"),"landsat_product_id":left["source_product"],"landsat_area_km2":left.get("value"),"sentinel2_observed_at":right["observed_at"],"sentinel2_product_id":right["source_product"],"sentinel2_area_km2":right.get("value"),"temporal_separation_hours":hours,"absolute_area_difference_km2":None if diff is None else abs(diff),"percentage_area_difference":None if diff is None or not left.get("value") else abs(diff)/left["value"]*100,**metrics(left,right)})
    OUT.parent.mkdir(parents=True,exist_ok=True); fields=list(rows[0]) if rows else ["landsat_observed_at","landsat_sensor","landsat_product_id","landsat_area_km2","sentinel2_observed_at","sentinel2_product_id","sentinel2_area_km2","temporal_separation_hours","absolute_area_difference_km2","percentage_area_difference","iou","landat_omission_fraction","sentinel2_commission_fraction","centroid_displacement_degrees"]
    with OUT.open("w",newline="") as h: w=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
    print(json.dumps({"pairs":len(rows),"output":str(OUT.relative_to(ROOT)),"note":"No sensor harmonization or merge is performed."},indent=2))
if __name__=="__main__":main()
