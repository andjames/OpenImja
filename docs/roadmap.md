# OpenImja technical and scientific roadmap

OpenImja is evolving from a lake-area experiment into an open, reproducible observatory of Imja Tsho and the surrounding glacier–lake system. It remains **not** an operational early-warning system, flood-warning service, hazard score, evacuation tool, or substitute for Nepal DHM and local authorities.

Its role is to make heterogeneous observations discoverable, reproducible, temporally explicit, and honest about their quality, freshness, and uncertainty.

## Guiding questions

1. How has Imja Tsho changed over time?
2. How well can the lake actually be observed at a given time?
3. What is happening to the glacier and terrain around the lake?
4. What field measurements and monitoring infrastructure exist, how old are they, and where did they come from?

No answer is to be collapsed into a synthetic risk value.

## Observation ontology

The current lake-area schema suits repeated EO-derived area observations; it is not a universal container. Future records will share carefully chosen provenance while retaining family-specific schemas.

| Concept | Examples | Epistemic status |
| --- | --- | --- |
| `satellite_observation` | Landsat, Sentinel-2, Sentinel-1 scene | satellite-derived |
| `field_measurement` | GPR, lake/stream level, weather gauge | measured/authoritative |
| `terrain_model` | DEM, elevation-change, velocity product | derived reference product |
| `bathymetric_survey` | manual sounding, sonar tracks, bathymetric raster | field/reference data |
| `derived_measurement` | lake area, shoreline, terminus position | method-derived |
| `model_output` | published flood or geomorphic model | modelled |
| `infrastructure_record` | gauge, sensor, siren, communications link | status must be evidenced |
| `contextual_dataset` | rivers, terrain, settlements, bridges | source-specific context |

Temporal status is independent: `historical`, `latest_authoritative`, `near_real_time`, `satellite_derived`, `modelled`, `stale`, and `unknown`. A model is not an observation, and a field datum is not automatically current.

### Shared provenance direction

Where meaningful, future schemas should support source, product, URL, DOI, observation/processing/retrieval times, method/version, sensor, institution, spatial resolution, uncertainty, quality flags, licence, citation, and geometry version. OpenImja will not add meaningless null-heavy fields merely to force a universal shape.

Every record should answer: what it is; when it was observed and processed; who/what produced it; how it was measured; whether it is measured, derived, or modelled; its uncertainty/freshness; and how it can be reproduced or traced.

## Data layers

### Lake surface and observability

Lake area, shoreline geometry, and eventually terminus position are repeated remote-sensing observations. Landsat supplies long optical history, Sentinel-2 modern optical observations, and Sentinel-1 an independent SAR family. Sensors remain separate until validated.

Observability is data in its own right: every acquisition is `AVAILABLE`, then may be `USABLE`, `REJECTED`, `REVIEWED`, or `PUBLISHED`. Cloud, snow, shadow, coverage, Landsat artifacts, radar geometry, and classification uncertainty are retained. This reports monitoring coverage, never safety.

### Bathymetry, glacier, terrain, and ground data

Bathymetry is field/reference data rather than a frequently updated feed. Prior to ingest, identify original points/tracks/raster, survey date, authors/institution, method/instrument/frequency, positioning, uncertainty, publication/DOI/URL, and licence. Sparse manual soundings, sonar, interpolated bathymetry, and model outputs remain distinguishable.

The parent glacier will be represented separately through terminus, surface elevation/change, velocity, debris-covered ice extent, and measured versus modelled ice thickness. High-resolution terrain products are historical references with actual acquisition dates, not current monitoring.

Future DHM/authoritative sources require stable permitted access plus station metadata, timestamp semantics, units, latency, QA, and licence. Infrastructure uses only `confirmed_operational`, `confirmed_offline`, `status_unknown`, or `historical_decommissioned`; installation alone is not evidence of operation.

Later downstream context may include Imja Khola, Dudh Koshi, terrain, trails, bridges, settlements, facilities, hydropower, and published flood models. Modelled products remain distinct from observations; OpenImja will not build an independent evacuation/inundation model.

## Deliberate sequence

### Phase A — historical lake reconstruction *(active priority)*

Build the longest defensible Landsat/Sentinel-2 reconstruction (approximately 1985–2026), preserving gaps, rejections, provenance, and reviewed shoreline boundaries. Do not interpolate.

**Result:** surface-area and shoreline history with provenance.

### Phase B — modern observability *(active priority; parallel with A)*

Build acquisition-level records for Landsat, Sentinel-2, and Sentinel-1, retaining `AVAILABLE`/`USABLE` status, rejection reasons, and coverage summaries.

**Result:** a measurable history of how often Imja could be observed.

### Phase C — SAR validation *(ongoing)*

Validate Sentinel-1 independently against high-quality optical observations using corrected geometry. Evaluate pass direction, area difference, overlap, omission/commission, terrain geometry, and season. Do not merge SAR with optical until empirical validation supports it.

### Phase D — bathymetric archive

Research and catalogue the 1992, 2002, 2009, 2012, 2014, and 2016 leads. Prefer original points/tracks/raster to values copied from publications. Ingest only where access and licensing permit.

**Result:** versioned historical depth/volume observations with provenance, not a continuous volume estimate.

### Phase E — high-resolution glacier/terrain reference

Evaluate NASA High Mountain Asia products, beginning with HMA2_DCG_SMB where coverage is relevant. Investigate DEM, elevation change, velocity, and surface mass balance; use broader HMA 8 m DEMs only where they add context without duplication.

**Result:** historical high-resolution glacier–lake context.

### Phase F — glacier/lake physical history

After validation, explore descriptive relationships among lake-area growth, shoreline migration, terminus retreat, velocity, elevation change, and measured bathymetry. Correlation does not justify prediction.

### Phase G — authoritative ground observations

Investigate reliable DHM/field data access, station metadata, freshness, sensor status, and provenance. Present ground and satellite data together without conflating them.

### Phase H — downstream context

Only after upstream architecture matures, evaluate authoritative terrain/context sources, NASA HMA Flood Geomorphic Potential, published GLOF models, and mapped infrastructure. Keep all model output distinct.

## Scientific boundary: volume reconstruction

Bathymetry plus lake area does **not** justify a continuous historical lake-volume record. A future reconstruction would be a separate derived/modelled product requiring explicit assumptions about changing lake-bottom geometry, glacier retreat, dead ice, lake level, uncertainty propagation, and scientific review.

## Planning registry

The machine-readable [source registry](../config/source-registry.json) records implemented sources and planned leads. `requires_verification` means dates, methods, access, licence, values, and suitability must be confirmed from original sources before use.

```text
SATELLITES      What could we see?
LAKE            How did its surface and shoreline change?
DEPTH           What did field surveys measure beneath the surface?
GLACIER         How did the ice retreat, thin, and move?
TERRAIN         What geometry surrounds the lake?
GROUND SENSORS  What did authoritative instruments observe?
INFRASTRUCTURE  What monitoring systems exist and are they functioning?
DOWNSTREAM      What physical and human systems lie below the lake?
```

The governing rule remains: **do not make data look more certain, current, or operational than it is.**
