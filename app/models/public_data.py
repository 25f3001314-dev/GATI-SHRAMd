"""Typed records returned by public contextual data adapters."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicIndicatorRecord:
    """Non-PII public indicator observation with provenance."""

    dataset_id: str
    geography: str
    period: str
    indicator: str
    value: float | None
    source: str
    access_date: str
    data_mode: str = "public"
