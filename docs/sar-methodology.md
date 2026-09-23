# Sentinel-1 SAR validation methodology

Sentinel-1 is being evaluated as a complementary observation source. It is **not** yet being used to fill missing Sentinel-2 observations in the official OpenImja lake-area series.

SAR is valuable because it senses microwave backscatter and can acquire imagery through cloud and without sunlight. This differs fundamentally from optical NDWI: smooth open water often returns low C-band backscatter, while surrounding terrain, rough water, ice, snow, debris, and sensor geometry can return very different values.

The experimental v0.1 scanner uses Earth Engine's `COPERNICUS/S1_GRD` calibrated, ortho-corrected dB product, filters to IW/VV acquisitions, removes very-low-backscatter edge pixels, applies a configurable VV threshold, and selects the thresholded component containing the Imja seed point. Earth Engine's GRD preparation does not remove the need for site-specific validation.

In steep Himalayan terrain, radar shadow, layover, foreshortening, incidence-angle effects, DEM/terrain-correction limitations, ice or wet snow, wind-roughened water, mixed shoreline pixels, and moraine/glacier geometry can all make a thresholded SAR outline misleading. Ascending and descending geometry may differ materially and are kept as provenance, not merged.

Each SAR scene is retained as processed or rejected. The archive retains SAR scenes within a configurable month-scale temporal context (currently ±31 days by default) around reviewed/published optical observations, allowing OpenImja to describe available SAR coverage instead of silently discarding it. Every record carries its actual temporal separation.

Pairs within a separately configurable ±3 day strict window are labelled `near_coincident`; only these support direct same-period validation. Wider records are labelled `contextual_month_scale`: they are useful for observability and method exploration, but are not evidence that the optical and SAR boundaries describe identical lake conditions. SAR and optical values remain separate measurement families until sufficient paired, reviewed evidence supports a documented cross-sensor interpretation.
