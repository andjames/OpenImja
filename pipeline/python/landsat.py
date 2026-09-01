"""Explicit Landsat Collection 2 Level-2 sensor specifications and QA policy."""
from __future__ import annotations
from datetime import datetime, timezone

SENSORS = {
    "LANDSAT/LT05/C02/T1_L2": {"sensor": "TM", "platform": "Landsat 5", "green": "SR_B2", "nir": "SR_B4", "resolution_m": 30},
    "LANDSAT/LE07/C02/T1_L2": {"sensor": "ETM+", "platform": "Landsat 7", "green": "SR_B2", "nir": "SR_B4", "resolution_m": 30},
    "LANDSAT/LC08/C02/T1_L2": {"sensor": "OLI", "platform": "Landsat 8", "green": "SR_B3", "nir": "SR_B5", "resolution_m": 30},
    "LANDSAT/LC09/C02/T1_L2": {"sensor": "OLI-2", "platform": "Landsat 9", "green": "SR_B3", "nir": "SR_B5", "resolution_m": 30},
}
SLC_OFF_START = datetime(2003, 5, 31, tzinfo=timezone.utc)

def slc_off_reasons(platform: str, observed_at: datetime) -> list[str]:
    return ["LANDSAT_7_SLC_OFF"] if platform == "Landsat 7" and observed_at >= SLC_OFF_START else []

def qa_mask_description() -> str:
    return "QA_PIXEL fill/dilated-cloud/cirrus/cloud/shadow/snow bits; Landsat 7 post-2003 SLC-off scenes rejected by archive policy"
