# Data sources

OpenImja uses a source only when its observation type, time, method, quality, licence, and traceability are clear. A source catalogue is not a claim that every listed dataset has been ingested, is current, covers Imja, or is suitable for publication.

The machine-readable planning inventory is [config/source-registry.json](../config/source-registry.json). Entries marked `requires_verification` are research leads, not evidence in the public series.

## Implemented observation families

| Family | Source | Current use | Important boundary |
| --- | --- | --- | --- |
| Optical EO | Sentinel-2 Level-2A | modern lake area, boundary, observability | cloud, snow, shadow, terrain, and threshold limitations remain explicit |
| Optical EO | Landsat Collection 2 Level-2 | historical scene archive and candidates | generations/bands differ; Landsat 7 post-2003 SLC-off is retained and rejected |
| SAR EO | Sentinel-1 GRD | experimental independent candidate/pair archive | not an optical substitute or gap-fill; no automatic publication |

## Planned source families

### Bathymetry and field depth

The registry records leads for 1992, 2002, 2009, 2012, 2014, and 2016 Imja surveys. All are presently `requires_verification` for ingestion. The 2012 BioSonics, 2014 SyQwest HydroBox, 2016 Garmin echoMAP, 2012 GPR, and 2016 modelling-supplement references must be evaluated against original survey/data documentation. No large external archive is automatically downloaded.

For each potential survey, OpenImja will seek original survey dates, authors/institutions, method, number/distribution of measurements, instrument/frequency, positional method, depth/volume values and uncertainty, tracks/points/raster availability, publication/DOI/URL, and licence. Manual line soundings, sonar observations, interpolated bathymetry, and model outputs are separate evidence types.

The published 2012 study is a useful lead for tracing earlier surveys, but does not establish redistribution rights for raw data: [Somos-Valenzuela et al. (2014)](https://tc.copernicus.org/articles/8/1661/2014/). The [Zenodo modelling supplement](https://zenodo.org/records/1307619) is a lead for inspecting model inputs, not a basis for automatic model ingestion.

### NASA High Mountain Asia terrain and glacier products

NASA/NSIDC’s [HMA2_DCG_SMB.001](https://nsidc.org/data/hma2_dcg_smb/versions/1) is a planned historical reference source. NSIDC describes 2 m DEMs, surface velocities, Lagrangian SMB rates, and SMB uncertainties for select debris-covered glaciers in Nepal, with 2012–2017 temporal coverage. OpenImja must confirm Imja coverage and individual acquisition dates before use; it is not current monitoring. DOI: `10.5067/DARPX4AR2OYO`.

For broader terrain coverage, the registry includes [HMA 8 m along-track DEMs](https://nsidc.org/data/hma_dem8m_at/versions/1), DOI `10.5067/GSACB044M4PK`. These are historical VHR optical-derived DEMs with varying dates, not a generic current terrain layer. Products will be evaluated for coverage, coregistration, uncertainty, licensing/access, and redundancy before ingestion.

NASA’s [HMA Flood Geomorphic Potential](https://nsidc.org/data/hma2_fgp/versions/1), DOI `10.5067/WS83XMWHGEM9`, is registered only as possible future `model_output` for downstream physical context. It is not an OpenImja warning, evacuation, or inundation product.

### Ground observations and infrastructure

Nepal DHM and other authoritative providers are placeholders until a stable permitted access method, station metadata, timestamp semantics, units, latency, quality control, and licence are confirmed. No brittle scraping is permitted merely to populate the repository.

Future infrastructure records may describe sensors, gauges, weather stations, links, and sirens. Equipment installation does not establish operation; use only `confirmed_operational`, `confirmed_offline`, `status_unknown`, or `historical_decommissioned` with an evidence source and date.

## Source admission checklist

Before a source becomes an OpenImja data product, record:

1. ontology and measured/derived/modelled status;
2. spatial/temporal coverage and actual observation date;
3. producer, method, version, uncertainty, and QA;
4. access path, licence, citation, and retention permissions;
5. source-specific schema/adapter and reproducible transformation; and
6. an explicit decision about publication and freshness semantics.

No source is treated as an emergency alert by default.
