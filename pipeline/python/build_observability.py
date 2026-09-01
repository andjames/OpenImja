#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
from observability import summary
from geometry import load_config
ROOT=Path(__file__).resolve().parents[2]
def load(path):return [json.loads(p.read_text()) for p in path.glob("*.json")]
def main():
 cfg=load_config(); version=cfg["geometry_version"]
 records=[r for r in load(ROOT/"data/processed/imja-tsho/scenes")+load(ROOT/"data/processed/imja-tsho/sar-scenes")+load(ROOT/"data/archive/scenes/landsat") if r.get("provenance",{}).get("geometry_version")==version]
 latest=json.loads((ROOT/"data/latest/imja-tsho.json").read_text()).get("latest_observation")
 if latest and latest.get("provenance",{}).get("geometry_version")!=version: latest=None
 now=datetime.now(timezone.utc); out={"lake_id":"imja-tsho","geometry_version":version,"as_of":now.isoformat().replace("+00:00","Z"),"definitions":"Acquisition counts are canonical-geometry archived scene records; usable means processed/reviewed/published, not a hazard signal.","periods":[summary(records,latest,now,d) for d in [30,90,365]]};p=ROOT/"data/observability/imja-tsho.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
