#!/usr/bin/env python3
"""Discover and assess every Landsat C2 L2 scene in a date window; never publishes."""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone
from pathlib import Path
import ee, google.auth
from freshness import classify
from geometry import load_config, geometry_provenance
from landsat import SENSORS, slc_off_reasons, qa_mask_description

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/archive/scenes/landsat"; REPORTS = ROOT / "data/archive/reports"; BOUNDARIES = ROOT / "data/archive/boundaries"

def z(d): return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
def safe(v): return v.replace("/", "_").replace(":", "_")
def mask(image, green, nir):
    qa=image.select("QA_PIXEL")
    clear=qa.bitwiseAnd(1).eq(0).And(qa.bitwiseAnd(1<<1).eq(0)).And(qa.bitwiseAnd(1<<2).eq(0)).And(qa.bitwiseAnd(1<<3).eq(0)).And(qa.bitwiseAnd(1<<4).eq(0)).And(qa.bitwiseAnd(1<<5).eq(0))
    return image.select([green,nir],["green","nir"]).multiply(.0000275).add(-.2).updateMask(clear)
def fraction(image, geometry):
    value=image.select("green").mask().reduceRegion(ee.Reducer.mean(),geometry,30,maxPixels=10_000_000).get("green").getInfo()
    return float(value) if value is not None else None
def process(image, collection, spec, config, envelope):
    aoi=ee.Geometry(config["geometry"]); seed=ee.Geometry(config["seed_point"]); props=image.toDictionary(["system:index","system:time_start","CLOUD_COVER","SPACECRAFT_ID"]).getInfo(); observed=datetime.fromtimestamp(props["system:time_start"]/1000,timezone.utc)
    scaled=mask(image,spec["green"],spec["nir"]); aoi_fraction=fraction(scaled,aoi); envelope_fraction=fraction(scaled,envelope)
    water=scaled.normalizedDifference(["green","nir"]).gte(.10).selfMask().clip(aoi); components=water.reduceToVectors(geometry=aoi,scale=30,geometryType="polygon",eightConnected=True,labelProperty="water",reducer=ee.Reducer.countEvery(),maxPixels=100_000_000).filterBounds(seed).map(lambda f:f.set("area_m2",f.geometry().area(1))).sort("area_m2",False)
    area=None; boundary=None
    if components.size().getInfo():
        selected=ee.Feature(components.first()); area=round(selected.geometry().area(1).getInfo()/1e6,6); boundary=selected.getInfo()
    reasons=slc_off_reasons(spec["platform"],observed)
    if envelope_fraction is None or envelope_fraction < config["sentinel2_qa"]["minimum_lake_envelope_valid_fraction"]: reasons.append("LOW_LAKE_ENVELOPE_OBSERVABILITY")
    if area is None: reasons.append("NO_LAKE_COMPONENT_AT_SEED")
    state="rejected" if reasons else "processed"; processed=datetime.now(timezone.utc); product=f"{collection}/{props['system:index']}"
    record={"lake_id":config["id"],"variable":"lake_area","measurement_family":"optical","value":area,"unit":"km2","observed_at":z(observed),"processed_at":z(processed),"source":"Landsat","source_product":product,"source_url":"https://developers.google.com/earth-engine/datasets/catalog/landsat","method":"landsat_c2_l2_ndwi_connected_component","method_version":"0.2.0-archive","parameters":{"index":"NDWI=(green-NIR)/(green+NIR)","ndwi_threshold":.10,"cloud_mask":qa_mask_description(),"historical_outlier_policy":config["optical_archive"]["historical_outlier_policy"]},"confidence":None,"quality_flags":reasons or ["QA_PASSED_PENDING_REVIEW"],"observation_state":state,"rejection_reasons":reasons,"state_history":[{"state":"discovered","at":z(processed)},{"state":state,"at":z(processed)}],"freshness":classify(observed,processed),"boundary_geojson_url":None,"qa":{"aoi_valid_fraction":aoi_fraction,"lake_envelope_valid_fraction":envelope_fraction,"reference_lake_envelope_path":config["reviewed_reference_lake_envelope"]["path"],"outlier_reference_observation":None,"relative_area_change":None},"provenance":{"code_version":"scan_landsat_v0_2","config_path":"config/lakes/imja-tsho.json","image_id":product,"earth_engine_collection":collection,"scene_cloud_cover_percent":props.get("CLOUD_COVER"),"sensor_family":"Landsat","sensor":spec["sensor"],"platform":spec["platform"],"collection":collection,"spatial_resolution_m":spec["resolution_m"],**geometry_provenance(config)}}
    path=OUT/f"{safe(product)}.json"
    if boundary:
        BOUNDARIES.joinpath(str(observed.year)).mkdir(parents=True,exist_ok=True)
        bpath=BOUNDARIES/str(observed.year)/f"Landsat-{observed.date().isoformat()}-{safe(props['system:index'])}.geojson"; bpath.write_text(json.dumps({"type":"FeatureCollection","features":[boundary]},indent=2)+"\n"); record["boundary_geojson_url"]=str(bpath.relative_to(ROOT))
    path.write_text(json.dumps(record,indent=2)+"\n"); return record
def main():
    p=argparse.ArgumentParser(); p.add_argument("--start",required=True);p.add_argument("--end",required=True);p.add_argument("--project",default=os.environ.get("OPENIMJA_EE_PROJECT"),required=os.environ.get("OPENIMJA_EE_PROJECT") is None);a=p.parse_args()
    creds,_=google.auth.default(scopes=["https://www.googleapis.com/auth/earthengine","https://www.googleapis.com/auth/cloud-platform"]);ee.Initialize(credentials=creds,project=a.project);config=load_config(); envelope=ee.Geometry(json.loads((ROOT/config["reviewed_reference_lake_envelope"]["path"]).read_text())["features"][0]["geometry"]);aoi=ee.Geometry(config["geometry"]);OUT.mkdir(parents=True,exist_ok=True); records=[]
    for collection,spec in SENSORS.items():
        ids=ee.ImageCollection(collection).filterBounds(aoi).filterDate(a.start,a.end).aggregate_array("system:index").getInfo()
        for image_id in ids: records.append(process(ee.Image(f"{collection}/{image_id}"),collection,spec,config,envelope))
    report={"sensor_family":"Landsat","start":a.start,"end":a.end,"available_scenes":len(records),"usable":sum(r["observation_state"]=="processed" for r in records),"generated_at":z(datetime.now(timezone.utc))}
    REPORTS.mkdir(parents=True,exist_ok=True)
    report_path=REPORTS/f"landsat_{a.start}_{a.end}.json"
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({**report,"report":str(report_path.relative_to(ROOT))},indent=2))
if __name__=="__main__":main()
