"""Data-quality profiling for ingested mobility records."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Iterable

from app.models.signals import RawRecord


@dataclass(frozen=True)
class DataQualityReport:
    """Observable quality facts; missing values are never hidden."""

    row_count: int
    date_coverage: dict[str, str | None]
    geographic_coverage: dict[str, int]
    missing_values: dict[str, int]
    duplicate_records: int
    source: str
    freshness_access_date: str
    data_mode: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def profile_records(
    records: Iterable[RawRecord],
    source: str,
    access_date: str,
    data_mode: str,
) -> DataQualityReport:
    """Profile row count, coverage, missing values, and duplicate rows."""
    record_list = list(records)
    timestamps = sorted(record.timestamp for record in record_list if record.timestamp)
    missing_fields = {
        field: sum(getattr(record, field) in (None, "") for record in record_list)
        for field in ("state", "district", "origin", "destination", "timestamp", "volume")
    }
    keys = [
        (record.source, record.origin, record.destination, record.timestamp, record.volume)
        for record in record_list
    ]
    duplicate_records = len(keys) - len(set(keys))
    return DataQualityReport(
        row_count=len(record_list),
        date_coverage={
            "start": timestamps[0] if timestamps else None,
            "end": timestamps[-1] if timestamps else None,
        },
        geographic_coverage={
            "states": len({record.state for record in record_list if record.state}),
            "districts": len({record.district for record in record_list if record.district}),
            "origins": len({record.origin for record in record_list if record.origin}),
            "destinations": len({record.destination for record in record_list if record.destination}),
        },
        missing_values=missing_fields,
        duplicate_records=duplicate_records,
        source=source,
        freshness_access_date=access_date,
        data_mode=data_mode,
    )
