"""Contracts shared by every data source adapter."""

from typing import Protocol

from app.models.signals import RawRecord


class DataSourceAdapter(Protocol):
    """Replaceable boundary for an API, file, database, or government feed."""

    name: str

    def fetch_records(self) -> list[RawRecord]:
        """Fetch records into the local State Node only."""
