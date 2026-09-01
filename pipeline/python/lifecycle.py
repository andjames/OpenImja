"""Pure lifecycle rules shared by optical and SAR scene records."""
from __future__ import annotations


ALLOWED_TRANSITIONS = {("processed", "rejected"), ("processed", "reviewed"), ("reviewed", "published")}


def can_transition(current: str, target: str, rejection_reasons: list[str]) -> bool:
    return not rejection_reasons and (current, target) in ALLOWED_TRANSITIONS


def should_update_latest(existing_latest: dict | None, candidate: dict) -> bool:
    """Only a later published observation can replace the latest public record."""
    if candidate.get("observation_state") != "published":
        return False
    if not existing_latest:
        return True
    existing = existing_latest.get("latest_observation") or {}
    if not existing:
        return True
    if existing.get("observation_state") != "published":
        return True
    if candidate["observed_at"] > existing.get("observed_at", ""):
        return True
    # A corrected-geometry or method reprocessing of the *same acquisition*
    # may replace a legacy representation. This does not permit a different,
    # older historical acquisition to regress the public latest record.
    return candidate.get("observed_at") == existing.get("observed_at") and candidate.get("source_product") == existing.get("source_product")
