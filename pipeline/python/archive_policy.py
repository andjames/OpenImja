"""Pure archive/observability policy; no Earth Engine dependency."""
from __future__ import annotations
from datetime import datetime

def scene_state(*, available: bool, rejection_reasons: list[str]) -> tuple[str, bool]:
    if not available: return "unavailable", False
    if rejection_reasons: return "rejected", False
    return "processed", True

def select_yearly_candidates(records: list[dict]) -> list[dict]:
    """Quality-first: retain all usable candidates, never invent a yearly measurement."""
    return sorted([r for r in records if r.get("available") and r.get("usable")], key=lambda r: r["observed_at"])

def season_window(year: int, start_month_day: str, end_month_day: str) -> tuple[str, str]:
    start = f"{year}-{start_month_day}"; end = f"{year}-{end_month_day}"
    if end_month_day <= start_month_day: end = f"{year + 1}-{end_month_day}"
    return start, end

def days_since(as_of: datetime, observed_at: datetime | None) -> int | None:
    return None if observed_at is None else max(0, int((as_of - observed_at).total_seconds() // 86400))
