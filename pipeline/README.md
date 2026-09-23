# Processing pipeline

The v0.1 pipeline is intentionally a command-line workflow that produces plain JSON, CSV, and GeoJSON files. It uses Google Earth Engine only as a reproducible catalogue and compute backend; credentials are supplied by the operator and never stored in this repository.

## Setup

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r pipeline/python/requirements.txt
export OPENIMJA_EE_PROJECT="your-earth-engine-enabled-cloud-project"
earthengine authenticate --auth_mode=gcloud --scopes=https://www.googleapis.com/auth/earthengine,https://www.googleapis.com/auth/cloud-platform --force
earthengine set_project "$OPENIMJA_EE_PROJECT"
```

Before authenticating, register the project through `https://code.earthengine.google.com/register?project=YOUR_PROJECT_ID`; this enables/ registers Earth Engine access for the selected commercial or noncommercial use. Authenticate with an account that is permitted to use that project. `gcloud` mode uses Google's supported command-line OAuth flow, and the explicit scopes above omit Drive because this pipeline does not export to Drive. If Google blocks a consent screen, do not bypass it or paste credentials anywhere: confirm the account/project has Earth Engine access, use `gcloud` mode, and ask the Workspace administrator to allow Google Cloud/Earth Engine if the account is managed. Then process a date; the script searches a configurable surrounding window and chooses the least-cloudy candidate that clears the configured AOI validity threshold.

If you authenticated with `gcloud auth application-default login` instead, pass `--auth-source application-default` to a processor. This uses the current Google application-default credential when an old Earth Engine credential file is unusable.

```sh
python pipeline/python/process_sentinel2.py --date 2025-10-15
```

It writes an observation JSON, a GeoJSON boundary, and a CSV row. It does **not** update `data/latest/imja-tsho.json` unless `--promote-latest` is supplied after visual review of the candidate boundary. A result is an EO-derived estimate, not an official lake measurement or warning.

Historical backfills are idempotent by source product: the CSV replaces a matching product row and remains date-sorted. An older acquisition cannot displace a newer `data/latest` observation.

## Validate before a first publication

Open `earth_engine/imja_sentinel2_inspect.js` in the Earth Engine Code Editor and select the configured Cloud project. It renders the raw RGB image, SCL classes, raw NDWI, masked probable water, draft AOI, and draft seed point. Adjusting the configuration or threshold requires recording why and visually reviewing the resulting boundary; do not lower criteria simply to fill a data gap.

After an AOI change, generate a non-publishing candidate reference boundary with `generate_reference_envelope.py`, review it, then update the configured reference-envelope path and status before resuming QA scans.

## Scene QA and review states

Use `scan_sentinel2.py` to inspect **every** Sentinel-2 scene in a bounded date range. It writes per-scene records to `data/processed/imja-tsho/scenes/` and a compact report to `data/processed/imja-tsho/reports/`. A scene progresses from `discovered` to either `processed` or `rejected`; rejected records are retained with machine-readable reasons. The scan never updates the public latest record.

```sh
python pipeline/python/scan_sentinel2.py --start 2026-08-01 --end 2026-08-28 --project "$OPENIMJA_EE_PROJECT"
```

`aoi_valid_fraction` describes clear coverage across the broad processing AOI. `lake_envelope_valid_fraction` separately measures clear coverage within the reviewed November 2025 lake envelope and is the publication gate. The configurable policy also flags implausibly large area changes against a reviewed/published reference. These are QA rules, not hazard thresholds.

Only a human can advance a QA-passing scene from `processed` to `reviewed`, then to `published`; both transitions require a retained note:

```sh
python pipeline/python/review_observation.py data/processed/imja-tsho/scenes/SCENE.json --to reviewed --note "Boundary follows shoreline in RGB review."
python pipeline/python/review_observation.py data/processed/imja-tsho/scenes/SCENE.json --to published --note "Second review complete."
```

Run regression checks with `PYTHONPATH=pipeline/python python -m unittest discover -s pipeline/python/tests`.

## Static review queue

Generate a local review queue after collecting candidate scenes:

```sh
python pipeline/python/build_review_queue.py
```

Open `web/review.html` through a static server. It shows retained boundaries and QA context, recommends a small representative subset per sensor/year, and copies lifecycle commands. It cannot mutate records from the browser. A human rejection uses a controlled machine-readable reason; review and publication still require a retained note.

## Experimental Sentinel-1 validation

`scan_sentinel1.py` scans IW/VV GRD scenes using configurable dB thresholds and the same lifecycle, reference-envelope, and provenance architecture. It creates SAR candidates/rejections only; it never publishes or substitutes for optical observations.

```sh
python pipeline/python/scan_sentinel1.py --start 2025-11-14 --end 2025-11-21 --project "$OPENIMJA_EE_PROJECT"
python pipeline/python/pair_s1_s2.py --window-days 31 --strict-window-days 3
python pipeline/python/build_s1_s2_validation_geometries.py
python pipeline/python/summarize_s1_s2_pairs.py
```

Open `web/validation.html` through a static server to inspect one pair at a time: shared-extent optical and SAR maps, a precomputed overlap/omission/commission map, and the retained QA state. The pairing CSV retains all SAR records in the configured contextual window, including rejected scenes. It labels strict near-coincident pairs separately from month-scale contextual records, so coverage can be studied without overstating temporal comparability.

See [SAR methodology](../docs/sar-methodology.md). The spatial layers are an audit aid, not a sensor-harmonization product or a publication mechanism.

## Historical optical archive and observability

`build_optical_archive.py` is intentionally scene-first. It writes `data/archive/optical-scenes.csv` with every discovered Landsat/Sentinel-2 record, including rejections, then writes the much smaller reviewed/published measurement series separately. It does not force annual values or interpolate gaps.

```sh
python pipeline/python/build_optical_archive.py --start-year 1985 --end-year 2026 --execute --project "$OPENIMJA_EE_PROJECT"
python pipeline/python/build_optical_archive.py --start-year 1985 --end-year 2026
python pipeline/python/pair_optical_sensors.py --window-days 7
python pipeline/python/pair_s1_s2.py --window-days 31 --strict-window-days 3
python pipeline/python/build_observability.py
```

Without `--execute`, an unsearched year is explicitly `not_scanned`; it is not reported as a missing acquisition. See [archive methodology](../docs/archive-methodology.md). Landsat's 30 m observations need independent review and are not merged with Sentinel-2.
