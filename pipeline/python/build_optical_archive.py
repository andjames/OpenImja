#!/usr/bin/env python3
"""Build static optical scene/measurement archive tables; preserves gaps and rejections."""
from __future__ import annotations
import argparse,csv,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from archive_policy import season_window,select_yearly_candidates
from geometry import load_config

ROOT=Path(__file__).resolve().parents[2]; ARCHIVE=ROOT/"data/archive"
def records(path): return [json.loads(p.read_text()) for p in path.glob("*.json")]
def scan_years():
    """Years with a completed Landsat scan, including legacy scan records."""
    years=set()
    for report in records(ARCHIVE/"reports"):
        if report.get("sensor_family")=="Landsat" and report.get("start"):
            years.add(int(report["start"][:4]))
    for record in records(ARCHIVE/"scenes/landsat"):
        years.add(int(record["observed_at"][:4]))
    return years
def main():
    p=argparse.ArgumentParser();p.add_argument("--start-year",type=int,default=1985);p.add_argument("--end-year",type=int,default=2026);p.add_argument("--execute",action="store_true");p.add_argument("--project");p.add_argument("--season-start");p.add_argument("--season-end");a=p.parse_args(); cfg=load_config();startmd=a.season_start or cfg["optical_archive"]["season_start_month_day"];endmd=a.season_end or cfg["optical_archive"]["season_end_month_day"]
    if a.execute and not a.project:p.error("--project required with --execute")
    for year in range(a.start_year,a.end_year+1):
        start,end=season_window(year,startmd,endmd)
        if a.execute: subprocess.run(["python","pipeline/python/scan_landsat.py","--start",start,"--end",end,"--project",a.project],cwd=ROOT,check=True)
    # Historical records made before the canonical expanded AOI are retained on
    # disk for audit but cannot be mixed into this corrected-geometry archive.
    scene_records=[r for r in records(ROOT/"data/archive/scenes/landsat")+records(ROOT/"data/processed/imja-tsho/scenes") if r.get("provenance",{}).get("geometry_version")==cfg["geometry_version"]]
    rows=[]
    for r in scene_records:
        if r.get("measurement_family")!="optical":continue
        d=r["observed_at"][:10]; rows.append({"observed_at":r["observed_at"],"year":d[:4],"sensor":r.get("provenance",{}).get("sensor",r["source"]),"source_product":r["source_product"],"boundary_geojson_url":r.get("boundary_geojson_url"),"available":True,"usable":r["observation_state"] in {"processed","reviewed","published"},"observation_state":r["observation_state"],"lake_area_km2":r.get("value"),"aoi_valid_fraction":r.get("qa",{}).get("aoi_valid_fraction"),"lake_envelope_valid_fraction":r.get("qa",{}).get("lake_envelope_valid_fraction"),"cloud_shadow_metrics":r.get("provenance",{}).get("scene_cloud_cover_percent"),"method":r["method"],"method_version":r["method_version"],"rejection_reasons":";".join(r.get("rejection_reasons",[])),"quality_flags":";".join(r.get("quality_flags",[])),"geometry_version":r.get("provenance",{}).get("geometry_version",cfg["geometry_version"])})
    present={int(x["year"]) for x in rows}; scanned=scan_years()
    for year in range(a.start_year,a.end_year+1):
        if year not in present:
            start,_=season_window(year,startmd,endmd); is_future=start>datetime.now(timezone.utc).date().isoformat()
            is_scanned=year in scanned
            state="future_window" if is_future else "unavailable" if is_scanned else "not_scanned"
            reason="FUTURE_SEASONAL_WINDOW" if is_future else "NO_ACQUISITION_IN_CONFIGURED_SEASON" if is_scanned else "NOT_YET_SCANNED"
            rows.append({"observed_at":f"{year}-{startmd}T00:00:00Z","year":year,"sensor":None,"source_product":None,"boundary_geojson_url":None,"available":False,"usable":False,"observation_state":state,"lake_area_km2":None,"aoi_valid_fraction":None,"lake_envelope_valid_fraction":None,"cloud_shadow_metrics":None,"method":None,"method_version":None,"rejection_reasons":reason,"quality_flags":"","geometry_version":cfg["geometry_version"]})
    fields=list(rows[0]);ARCHIVE.mkdir(parents=True,exist_ok=True)
    with (ARCHIVE/"optical-scenes.csv").open("w",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(sorted(rows,key=lambda x:x["observed_at"]))
    measurements=sorted([x for x in rows if x["observation_state"] in {"reviewed","published"}],key=lambda x:x["observed_at"])
    with (ARCHIVE/"lake-area-optical.csv").open("w",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(measurements)
    print(json.dumps({"scene_rows":len(rows),"published_or_reviewed_measurements":len(measurements),"season":{"start":startmd,"end":endmd}},indent=2))
if __name__=="__main__":main()
