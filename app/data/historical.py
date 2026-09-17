"""Reader for documented historical observed-flow CSV files."""

import csv
from pathlib import Path

from app.analytics.validation import HistoricalObservation


class HistoricalDataError(ValueError):
    """Raised when historical validation data is missing or malformed."""


def load_observations(path: str | Path, dataset_id: str) -> list[HistoricalObservation]:
    """Read origin,destination,time_window,observed_flow from a local CSV."""
    source_path = Path(path)
    if not source_path.exists():
        raise HistoricalDataError(f"Historical observations do not exist: {source_path}")
    with source_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"origin", "destination", "time_window", "observed_flow"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise HistoricalDataError(f"Missing historical columns: {sorted(missing)}")
        observations: list[HistoricalObservation] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                observations.append(
                    HistoricalObservation(
                        origin=row["origin"].strip(),
                        destination=row["destination"].strip(),
                        time_window=row["time_window"].strip(),
                        observed_flow=float(row["observed_flow"]),
                        dataset_id=dataset_id,
                    )
                )
            except (KeyError, ValueError) as error:
                raise HistoricalDataError(f"Malformed historical row {row_number}") from error
    return observations
