#!/usr/bin/env python3
"""Build a static, non-publishing candidate-review queue for Imja Tsho."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from geometry import load_config
from review_queue import ranked_candidates

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"data/review/imja-tsho.json"
def load(folder):
    return [(json.loads(path.read_text()), str(path.relative_to(ROOT))) for path in folder.glob("*.json")]
def public(record, path):
    provenance=record.get("provenance", {})
    return {"record_path":path,"observed_at":record["observed_at"],"measurement_family":record.get("measurement_family"),"source":record.get("source"),"sensor":provenance.get("sensor",record.get("source")),"source_product":record.get("source_product"),"source_url":record.get("source_url"),"value":record.get("value"),"unit":record.get("unit"),"boundary_geojson_url":record.get("boundary_geojson_url"),"qa":record.get("qa",{}),"quality_flags":record.get("quality_flags",[]),"season_group_median_area_km2":record["season_group_median_area_km2"],"season_group_candidate_count":record["season_group_candidate_count"],"review_rank":record["review_rank"],"review_recommended":record["review_recommended"]}
def main():
    config=load_config(); version=config["geometry_version"]
    pairs=load(ROOT/"data/processed/imja-tsho/scenes")+load(ROOT/"data/processed/imja-tsho/sar-scenes")+load(ROOT/"data/archive/scenes/landsat")
    canonical=[(record,path) for record,path in pairs if record.get("provenance",{}).get("geometry_version")==version]
    ranked=ranked_candidates([record for record,_ in canonical])
    paths={record["source_product"]:path for record,path in canonical}
    queue=[public(record,paths[record["source_product"]]) for record in ranked]
    states={state:sum(record.get("observation_state")==state for record,_ in canonical) for state in ["processed","rejected","reviewed","published"]}
    output={"lake_id":config["id"],"geometry_version":version,"generated_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"definitions":"Rank orders representative processed candidates within a sensor/year group by distance from that group’s median area, then envelope coverage. It is a review aid, not an automated quality or publication decision.","state_counts":states,"candidates":queue}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({"output":str(OUT.relative_to(ROOT)),"candidate_count":len(queue),"recommended":sum(x["review_recommended"] for x in queue)},indent=2))
if __name__=="__main__":main()
