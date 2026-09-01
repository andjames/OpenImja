"""Pure policy for a small, human review queue; never changes lifecycle state."""
from __future__ import annotations
from collections import defaultdict
from statistics import median

def ranked_candidates(records: list[dict], limit_per_group: int = 3) -> list[dict]:
    """Rank processed scenes by representative area, then envelope coverage.

    A rank is a review aid, not a quality score or publication decision.
    """
    groups = defaultdict(list)
    for record in records:
        if record.get("observation_state") != "processed" or record.get("value") is None:
            continue
        provenance = record.get("provenance", {})
        key = (record.get("measurement_family"), provenance.get("sensor", record.get("source")), record["observed_at"][:4])
        groups[key].append(record)
    results = []
    for group in groups.values():
        areas = [item["value"] for item in group]
        middle = median(areas)
        ordered = sorted(group, key=lambda item: (abs(item["value"] - middle), -(item.get("qa", {}).get("lake_envelope_valid_fraction") or 0), item["observed_at"]))
        for rank, item in enumerate(ordered, 1):
            results.append({**item, "review_rank": rank, "review_recommended": rank <= limit_per_group, "season_group_median_area_km2": round(middle, 6), "season_group_candidate_count": len(group)})
    return sorted(results, key=lambda item: (not item["review_recommended"], item["observed_at"]))
