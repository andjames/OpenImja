# Historical archive and observability

OpenImja separates a satellite acquisition from a defensible measurement. **Available** means an archive search found a scene covering the processing AOI. **Usable** means that scene passed the sensor-specific masking, reference-envelope observability, component, and policy checks. A scene can then be **rejected**, or a usable candidate can be human-advanced through **reviewed** and **published**. These labels describe data handling only; they are not hazard indicators.

`data/archive/optical-scenes.csv` is the scene-level record. It retains rejected scenes and their machine-readable reasons. `data/archive/lake-area-optical.csv` contains only reviewed or published optical measurements. A date with `not_scanned` means no archive search has yet been completed for that seasonal window; it must never be read as “no acquisition.” A scanned window with no matching scenes is recorded as unavailable; a seasonal window that has not occurred is `future_window`. No gaps are interpolated.

## Historical optical approach

The initial seasonal window is configurable in `config/lakes/imja-tsho.json` and currently explores post-monsoon dates. This is a practical starting point, not a claim of universal scientific optimality. The archive scans all candidate scenes in the window, evaluates each, and selects nothing unless candidates have passed QA and received human review. The historical temporal-change policy is deliberately `record_only`: an apparent change is retained for review rather than silently applying modern change limits to earlier lake growth.

Landsat Collection 2 Level-2 records retain the collection, platform, sensor, band mapping, 30 m resolution, mask policy, threshold, method version, and canonical geometry provenance. TM, ETM+, OLI, and OLI-2 band mappings are explicit. Landsat 7 scenes after 31 May 2003 receive the `LANDSAT_7_SLC_OFF` rejection reason, because the scan-line corrector failure can compromise this small, terrain-confined target. Sentinel-2 remains a separate optical stream with its existing finer-resolution QA policy.

## Comparisons and observability

`pair_optical_sensors.py` records near-coincident reviewed/published Landsat and Sentinel-2 measurements, with temporal and area differences and boundary overlap where both boundaries exist. It does not correct, merge, or treat instruments as interchangeable.

`pair_s1_s2.py` similarly retains paired optical/SAR records separately, adding intersection-over-union, optical omission, SAR commission, and centroid displacement when both saved boundaries are available. Orbit direction, polarization, timing, parameters, and QA flags remain in the pair record. These are validation data, not an optical gap-fill.

`data/observability/imja-tsho.json` reports local archive coverage for the last 30, 90, and 365 days. Its acquisition, usable, rejected, and freshness counts describe how much of the satellite archive OpenImja assessed. They do not measure lake danger, warning coverage, or safety.
