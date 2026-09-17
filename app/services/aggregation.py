"""Aggregation of state-local sanitized records."""

from collections import defaultdict
from typing import Iterable

from app.models.signals import SanitizedRecord


def aggregate_records(records: Iterable[SanitizedRecord]) -> list[SanitizedRecord]:
    """Aggregate by route, district, time window, and source."""
    grouped: dict[tuple[str, str, str, str | None, str, str, str], int] = defaultdict(int)
    for record in records:
        key = (
            record.state,
            record.origin,
            record.destination,
            record.district,
            record.time_window,
            record.source,
            record.signal_type,
        )
        grouped[key] += record.signal_count

    return [
        SanitizedRecord(
            state=state,
            origin=origin,
            destination=destination,
            district=district,
            time_window=time_window,
            source=source,
            signal_type=signal_type,
            signal_count=signal_count,
        )
        for (state, origin, destination, district, time_window, source, signal_type), signal_count in grouped.items()
    ]
