"""Strict adapter for a manually downloaded public mobility CSV."""

import csv
from pathlib import Path

from app.models.signals import RawRecord

REQUIRED_COLUMNS = {
    "source",
    "state",
    "district",
    "origin",
    "destination",
    "timestamp",
    "signal_type",
    "volume",
}
NON_EMPTY_COLUMNS = REQUIRED_COLUMNS - {"district"}


class PublicDataError(ValueError):
    """Raised when a public file cannot be safely interpreted."""


class CSVMobilityAdapter:
    """Load public mobility observations without contacting a remote service."""

    name = "public mobility CSV"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def fetch_records(self) -> list[RawRecord]:
        """Parse required fields and reject malformed rows explicitly."""
        if not self.path.exists():
            raise PublicDataError(f"Public mobility CSV does not exist: {self.path}")
        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing_columns = REQUIRED_COLUMNS - columns
            if missing_columns:
                raise PublicDataError(
                    f"Missing required columns: {sorted(missing_columns)}"
                )
            records: list[RawRecord] = []
            for row_number, row in enumerate(reader, start=2):
                try:
                    volume = int(row["volume"] or "")
                    if volume < 0:
                        raise ValueError("volume must not be negative")
                    required_values = [row[column].strip() for column in NON_EMPTY_COLUMNS]
                    if any(not value for value in required_values):
                        raise ValueError("required value is empty")
                    records.append(
                        RawRecord(
                            source=row["source"].strip(),
                            state=row["state"].strip(),
                            district=row["district"].strip() or None,
                            origin=row["origin"].strip(),
                            destination=row["destination"].strip(),
                            timestamp=row["timestamp"].strip(),
                            signal_type=row["signal_type"].strip(),
                            volume=volume,
                            metadata={
                                "synthetic": "false",
                                "dataset_id": "public_mobility_csv_template",
                            },
                        )
                    )
                except (KeyError, ValueError) as error:
                    raise PublicDataError(
                        f"Malformed public mobility row {row_number}: {error}"
                    ) from error
        return records
