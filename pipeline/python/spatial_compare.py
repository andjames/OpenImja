"""GeoJSON polygon comparison for audit, not sensor harmonization."""
from __future__ import annotations
from shapely.geometry import shape
def compare_geojson(a: dict,b: dict)->dict:
    ga=shape(a["features"][0]["geometry"]);gb=shape(b["features"][0]["geometry"]);inter=ga.intersection(gb);union=ga.union(gb)
    return {"iou":None if union.area==0 else inter.area/union.area,"optical_omission_fraction":None if ga.area==0 else ga.difference(gb).area/ga.area,"sar_commission_fraction":None if gb.area==0 else gb.difference(ga).area/gb.area,"centroid_displacement_degrees":ga.centroid.distance(gb.centroid)}
